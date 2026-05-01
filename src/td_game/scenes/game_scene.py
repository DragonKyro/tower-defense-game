"""The gameplay view.

Owns all per-run sprite lists and drives the per-frame update cycle:
wave manager -> spawner followers -> tower attacks -> projectiles -> combat.
"""
from __future__ import annotations

import arcade

from td_game.core.constants import (
    HUD_HEIGHT,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TILE_SIZE,
    Layer,
    MAX_HEROES_PER_LEVEL,
)
from td_game.core.events import ENEMY_KILLED, LEVEL_LOST, LEVEL_WON
from td_game.core.game_state import GameState
from td_game.core.resources import load_texture
from td_game.data.heroes import HEROES
from td_game.skills.meteor import Meteor
from td_game.skills.reinforcements import Reinforcements
from td_game.systems.combat import CombatSystem
from td_game.systems.command import CommandSystem
from td_game.systems.economy import EconomySystem
from td_game.systems.spawner import Spawner
from td_game.systems.wave_manager import WaveManager
from td_game.ui.health_bar import draw_health_bar
from td_game.ui.hud import HUD
from td_game.ui.tower_menu import BuildMenu, UpgradeMenu
from td_game.world.level import LevelDef
from td_game.world.tile import TileType


class GameView(arcade.View):
    def __init__(self, level: LevelDef) -> None:
        super().__init__()
        self.level = level
        self.state = GameState(
            gold=level.starting_gold,
            lives=level.starting_lives,
            total_waves=len(level.waves),
        )
        # Sprite lists (one per layer so draw order is deterministic).
        self.tiles = arcade.SpriteList()
        self.build_spot_sprites = arcade.SpriteList()
        self.towers = arcade.SpriteList()
        self.enemies = arcade.SpriteList()
        self.units = arcade.SpriteList()
        self.projectiles = arcade.SpriteList()
        self.fx = arcade.SpriteList()

        self._spot_by_sprite: dict = {}
        self._fx_lifetimes: dict = {}
        self._selected_menu = None
        self._pending_skill = None   # skill awaiting a target

        self.spawner = Spawner(level.map.path_registry(), self.state.bus)
        self.wave_manager = WaveManager(level.waves, self.spawner, self.state)
        self.wave_manager.bind(self)
        self.combat = CombatSystem(self.state)
        self.economy = EconomySystem(self.state)
        self.command = CommandSystem(self, self.state)

        # Skills
        self.reinforcements = Reinforcements(cooldown=level.reinforcements_cooldown,
                                             cost=level.reinforcements_cost)
        self.meteor = Meteor(cooldown=level.meteor_cooldown, cost=level.meteor_cost)

        # Heroes
        self.heroes = []
        self._hero_slots_available = min(level.hero_slots, MAX_HEROES_PER_LEVEL)

        self.hud = HUD(self.state, [self.reinforcements, self.meteor], self._on_skill_button)

        # End-of-game routing.
        self.state.bus.subscribe(LEVEL_WON, lambda **_: self._route_to_end(True))
        self.state.bus.subscribe(LEVEL_LOST, lambda **_: self._route_to_end(False))

        self._build_tile_sprites()
        self._build_spot_sprites()
        self._place_default_hero()
        # Auto-start first wave after a short breather.
        self._first_wave_timer = 2.0

    # --- scaffolding ------------------------------------------------

    def _build_tile_sprites(self) -> None:
        grid = self.level.map.grid
        rows = len(grid)
        for r, row in enumerate(grid):
            for c, tile in enumerate(row):
                tex = load_texture("tiles", tile.sprite_name())
                sp = arcade.Sprite()
                sp.texture = tex
                sp.center_x = c * TILE_SIZE + TILE_SIZE / 2
                sp.center_y = SCREEN_HEIGHT - (r * TILE_SIZE + TILE_SIZE / 2)
                self.tiles.append(sp)

    def _build_spot_sprites(self) -> None:
        tex = load_texture("tiles", "build_spot_0")
        for spot in self.level.map.build_spots:
            sp = arcade.Sprite()
            sp.texture = tex
            sp.center_x = spot.x
            sp.center_y = spot.y
            self.build_spot_sprites.append(sp)
            self._spot_by_sprite[sp] = spot

    def _place_default_hero(self) -> None:
        if self._hero_slots_available <= 0:
            return
        # Place first hero near the first spawn point.
        for spawn_path_id, (sx, sy) in self.level.map.spawn_points.items():
            hero_id = "knight"  # default; level UI could let player pick
            hero = HEROES[hero_id](sx + 64, sy, bus=self.state.bus)
            self.heroes.append(hero)
            self.units.append(hero)
            break

    # --- scene API for systems --------------------------------------

    def spawn_enemy(self, enemy) -> None:
        self.enemies.append(enemy)

    def spawn_tower(self, tower, spot) -> None:
        self.towers.append(tower)

    def remove_tower(self, tower) -> None:
        tower.remove_from_sprite_lists()

    def spawn_unit(self, unit) -> None:
        self.units.append(unit)

    def spawn_projectile(self, proj) -> None:
        self.projectiles.append(proj)

    def spawn_fx(self, sprite_name: str, x: float, y: float, lifetime: float = 0.4) -> None:
        tex = load_texture("effects", sprite_name)
        sp = arcade.Sprite()
        sp.texture = tex
        sp.center_x = x
        sp.center_y = y
        self.fx.append(sp)
        self._fx_lifetimes[sp] = lifetime

    # --- input ------------------------------------------------------

    def on_mouse_press(self, x: float, y: float, button, modifiers) -> None:
        # HUD priority
        if y < HUD_HEIGHT and self.hud.handle_click(x, y):
            return
        y_world = y
        # If a menu is open, let it handle the click first.
        if self._selected_menu is not None:
            if self._selected_menu.handle_click(x, y_world):
                self._selected_menu = None
                return
            # Click elsewhere closes it.
            self._selected_menu = None

        # If a skill is pending a target, fulfill it.
        if self._pending_skill is not None:
            skill = self._pending_skill
            self._pending_skill = None
            self.command.cast_skill(skill, target=(x, y_world))
            return

        # Right-click on empty ground: rally first hero.
        if button == arcade.MOUSE_BUTTON_RIGHT and self.heroes:
            self.command.set_hero_rally(self.heroes[0], x, y_world)
            return

        # Click on an existing tower?
        for t in self.towers:
            dx = t.center_x - x
            dy = t.center_y - y_world
            if dx * dx + dy * dy <= (TILE_SIZE / 2) ** 2:
                self._selected_menu = UpgradeMenu(
                    t, t.center_x, t.center_y,
                    on_upgrade=self._on_upgrade_picked,
                    on_sell=self._on_sell,
                )
                return

        # Click on a build spot?
        for sp in self.build_spot_sprites:
            dx = sp.center_x - x
            dy = sp.center_y - y_world
            if dx * dx + dy * dy <= (TILE_SIZE / 2) ** 2:
                spot = self._spot_by_sprite[sp]
                self._selected_menu = BuildMenu(
                    spot, sp.center_x, sp.center_y,
                    allowed=self.level.allowed_towers,
                    on_pick=self._on_family_picked,
                )
                return

    # --- menu callbacks --------------------------------------------

    def _on_family_picked(self, family: str, spot) -> None:
        ok = self.command.build_tower(family, spot)
        if ok:
            # Remove the build-spot sprite so a tower can't be built twice here.
            for sp, s in list(self._spot_by_sprite.items()):
                if s is spot:
                    sp.remove_from_sprite_lists()
                    del self._spot_by_sprite[sp]
                    break

    def _on_upgrade_picked(self, tower, node_id: str) -> None:
        self.command.upgrade_tower(tower, node_id)

    def _on_sell(self, tower) -> None:
        self.command.sell_tower(tower)

    def _on_skill_button(self, skill) -> None:
        if not skill.ready:
            return
        if skill.target_kind.name == "SELF":
            self.command.cast_skill(skill)
        else:
            self._pending_skill = skill

    # --- per-frame --------------------------------------------------

    def on_update(self, delta_time: float) -> None:
        if self.state.paused:
            return
        dt = delta_time * self.state.game_speed

        # First-wave pre-delay.
        if self._first_wave_timer > 0:
            self._first_wave_timer -= dt
            if self._first_wave_timer <= 0:
                self.wave_manager.start_next_wave()

        # Enemies: move along paths
        self.spawner.update_followers([e for e in self.enemies if e.alive], dt)

        # Update entities
        for sprite_list in (self.enemies, self.units, self.towers, self.projectiles):
            for sp in sprite_list:
                sp.on_update(dt)

        # Engagement + combat
        self.combat.resolve_engagement(self.units, self.enemies)
        for t in self.towers:
            t.try_attack(self.enemies, self)
        self.combat.tick_projectiles(self.projectiles, self.enemies)

        # Cull dead
        for e in list(self.enemies):
            if not e.alive:
                e.remove_from_sprite_lists()
        for u in list(self.units):
            if not u.alive and getattr(u, "respawn_timer", 0.0) <= 0:
                # Heroes stay in the list so they can update_respawn; soldiers die.
                from td_game.entities.heroes.base_hero import BaseHero
                if not isinstance(u, BaseHero):
                    u.remove_from_sprite_lists()

        # FX lifetime
        for sp in list(self._fx_lifetimes.keys()):
            self._fx_lifetimes[sp] -= dt
            if self._fx_lifetimes[sp] <= 0:
                sp.remove_from_sprite_lists()
                del self._fx_lifetimes[sp]

        # Wave progression
        active_count = sum(1 for e in self.enemies if e.alive)
        self.wave_manager.update(dt, active_count)

        # Losing condition
        if self.state.lost:
            self.state.bus.publish(LEVEL_LOST)

    # --- drawing ----------------------------------------------------

    def on_draw(self) -> None:
        self.clear()
        self.tiles.draw()
        self.build_spot_sprites.draw()
        self.towers.draw()
        self.units.draw()
        self.enemies.draw()
        self.projectiles.draw()
        self.fx.draw()

        # Health bars
        for e in self.enemies:
            draw_health_bar(e)
        for u in self.units:
            if u.alive:
                draw_health_bar(u)

        # HUD
        self.hud.draw()
        if self._selected_menu is not None:
            self._selected_menu.draw()

        # Skill-targeting cursor
        if self._pending_skill is not None:
            arcade.draw_text(
                f"Click to target {self._pending_skill.display_name}",
                20, SCREEN_HEIGHT - 30, (255, 255, 255), 14,
            )

    # --- game-over routing -----------------------------------------

    def _route_to_end(self, won: bool) -> None:
        from .game_over import GameOverView
        self.window.show_view(GameOverView(self.level, won))
