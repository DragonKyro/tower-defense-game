"""The gameplay view.

Owns all per-run sprite lists and drives the per-frame update cycle:
wave manager -> spawner followers -> tower attacks -> projectiles -> combat.
"""
from __future__ import annotations

import arcade

from td_game.core.constants import (
    HUD_HEIGHT,
    MAX_HEROES_PER_LEVEL,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TILE_SIZE,
)
from td_game.core.events import LEVEL_LOST, LEVEL_WON
from td_game.core.game_state import GameState
from td_game.core.resources import load_texture
from td_game.data.enemies import ENEMIES
from td_game.data.heroes import HEROES, HERO_STATS
from td_game.data.towers import TOWER_TREES
from td_game.skills.meteor import Meteor
from td_game.skills.reinforcements import Reinforcements
from td_game.systems.combat import CombatSystem
from td_game.systems.command import CommandSystem
from td_game.systems.economy import EconomySystem
from td_game.systems.spawner import Spawner
from td_game.systems.wave_manager import WaveManager
from td_game.ui.health_bar import draw_health_bar
from td_game.ui.hud import HUD
from td_game.ui.tooltip import InfoPanel, enemy_panel, tower_panel
from td_game.ui.tower_menu import BuildMenu, UpgradeMenu
from td_game.ui.wave_preview import WavePreview
from td_game.world.level import LevelDef
from td_game.world.path_geometry import smooth_waypoints


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
        self.background_sprite: arcade.Sprite | None = None
        self.decor_sprites = arcade.SpriteList(use_spatial_hash=False)
        self.build_spot_sprites = arcade.SpriteList()
        self.towers = arcade.SpriteList()
        self.enemies = arcade.SpriteList()
        self.units = arcade.SpriteList()
        self.projectiles = arcade.SpriteList()
        self.fx = arcade.SpriteList()

        # Pre-smoothed path vertex lists, drawn each frame as
        # circles-at-joints + thick lines between — yields a clean ribbon
        # without the self-intersection artifacts of a single polygon fill.
        self._path_curves: list[list[tuple[float, float]]] = []

        self._spot_by_sprite: dict = {}
        self._fx_lifetimes: dict = {}
        self._selected_menu = None
        self._pending_skill = None   # skill awaiting a target
        self._mouse_x = 0
        self._mouse_y = 0

        self.spawner = Spawner(level.map.path_registry(), self.state.bus)
        self.wave_manager = WaveManager(level.waves, self.spawner, self.state)
        self.wave_manager.bind(self)
        self.combat = CombatSystem(self.state)
        self.economy = EconomySystem(self.state)
        self.command = CommandSystem(self, self.state)

        self.reinforcements = Reinforcements(
            cooldown=level.reinforcements_cooldown, cost=level.reinforcements_cost,
        )
        self.meteor = Meteor(cooldown=level.meteor_cooldown, cost=level.meteor_cost)

        self.heroes = []
        self._hero_slots_available = min(level.hero_slots, MAX_HEROES_PER_LEVEL)

        self.hud = HUD(
            self.state, [self.reinforcements, self.meteor],
            on_cast=self._on_skill_button,
            on_pause=self._toggle_pause,
            on_speed_toggle=self._toggle_speed,
        )
        self.wave_preview = WavePreview(on_call_early=self._call_next_wave_early)

        # Cached text for hints and wave banners.
        self._target_prompt = arcade.Text(
            "", SCREEN_WIDTH / 2, SCREEN_HEIGHT - 24,
            color=(255, 250, 210), font_size=16, anchor_x="center", bold=True,
        )
        self._wave_banner: arcade.Text | None = None
        self._wave_banner_ttl = 0.0

        self.state.bus.subscribe(LEVEL_WON, lambda **_: self._route_to_end(True))
        self.state.bus.subscribe(LEVEL_LOST, lambda **_: self._route_to_end(False))
        self.state.bus.subscribe("wave_started", self._on_wave_started)

        self._build_background()
        self._build_paths()
        self._build_decor_sprites()
        self._build_spot_sprites()
        self._place_default_hero()
        self._first_wave_timer = 3.0

    # --- scaffolding ------------------------------------------------

    def _build_background(self) -> None:
        """One big meadow sprite spans the entire play area above the HUD."""
        tex = load_texture("tiles", "meadow_bg_0")
        sp = arcade.Sprite()
        sp.texture = tex
        sp.center_x = SCREEN_WIDTH / 2
        # Play area is the region above HUD_HEIGHT.
        sp.center_y = HUD_HEIGHT + (SCREEN_HEIGHT - HUD_HEIGHT) / 2
        self.background_sprite = sp

    def _draw_path_ribbon(self, points, width: float, color) -> None:
        """Draw a smooth thick ribbon through `points`.

        Each joint gets a filled disc (fills seam gaps between segments);
        each pair of consecutive points gets a thick line segment. Using
        two primitives here (instead of one polygon fill) avoids the
        self-intersection artifacts that a naive ribbon polygon
        produces at tight turns.
        """
        r = width / 2.0
        for px, py in points:
            arcade.draw_circle_filled(px, py, r, color)
        for i in range(len(points) - 1):
            x0, y0 = points[i]
            x1, y1 = points[i + 1]
            arcade.draw_line(x0, y0, x1, y1, color, line_width=width)

    def _build_paths(self) -> None:
        """Pre-compute smoothed vertex lists for each path.

        Rendering happens in on_draw as circles-at-joints + thick lines
        between, which produces a clean ribbon without polygon
        self-intersection at rounded corners.
        """
        self._path_curves = []
        for path in self.level.map.paths:
            smooth = smooth_waypoints(path.waypoints, iterations=2)
            self._path_curves.append(smooth)

    def _build_decor_sprites(self) -> None:
        # Sort by y descending so "further back" decor (higher y in screen
        # coords) draws before "closer" decor — gives a depth cue.
        for item in sorted(self.level.map.decor, key=lambda d: -d.y):
            tex = load_texture("decor", item.sprite)
            sp = arcade.Sprite()
            sp.texture = tex
            sp.center_x = item.x
            sp.center_y = item.y
            if item.scale != 1.0:
                sp.scale = (item.scale, item.scale)
            self.decor_sprites.append(sp)

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
        for _, (sx, sy) in self.level.map.spawn_points.items():
            hero = HEROES["knight"](sx + 128, sy, bus=self.state.bus)
            self.heroes.append(hero)
            hero._scene = self
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
        unit._scene = self
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

    # --- control ---------------------------------------------------

    def _toggle_pause(self) -> None:
        from .pause_menu import PauseView
        self.state.paused = True
        self.window.show_view(PauseView(self))

    def resume_from_pause(self) -> None:
        self.state.paused = False

    def _toggle_speed(self) -> None:
        self.state.game_speed = 2.0 if self.state.game_speed < 1.5 else 1.0

    def _call_next_wave_early(self) -> None:
        # Honors the breather before wave 1 as well as inter-wave breathers.
        if self._first_wave_timer > 0:
            # Flat bonus for skipping the initial grace period.
            bonus = int(self._first_wave_timer * 2) + 5
            self._first_wave_timer = 0.0
            self.state.add_gold(bonus, reason="wave_early")
            self.wave_manager.start_next_wave()
            return
        bonus = self.wave_manager.call_next_wave_early()
        if bonus:
            self.state.add_gold(bonus, reason="wave_early")

    def _can_afford_family(self, family: str) -> bool:
        return self.state.gold >= TOWER_TREES[family].tiers[0].cost

    def _call_early_bonus_preview(self) -> int:
        """Gold the player would get if they called the next wave *right now*."""
        if self._first_wave_timer > 0:
            return int(self._first_wave_timer * 2) + 5
        if self.wave_manager.can_call_next_early():
            return int(self.wave_manager.between_timer * 2) + 5
        return 0

    def _on_wave_started(self, index: int, wave, **_) -> None:
        self._wave_banner = arcade.Text(
            wave.name, SCREEN_WIDTH / 2, SCREEN_HEIGHT - 80,
            color=(250, 228, 160), font_size=24, anchor_x="center", bold=True,
        )
        self._wave_banner_ttl = 2.4

    # --- input -----------------------------------------------------

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float) -> None:
        self._mouse_x = x
        self._mouse_y = y
        self.hud.update_hover(x, y)
        self.wave_preview.update_hover(x, y)
        if self._selected_menu is not None and hasattr(self._selected_menu, "update_hover"):
            self._selected_menu.update_hover(x, y)

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        if symbol == arcade.key.ESCAPE:
            if self._pending_skill is not None:
                self._pending_skill = None
                self._target_prompt.text = ""
                return
            self._toggle_pause()
        elif symbol == arcade.key.P:
            self._toggle_pause()
        elif symbol == arcade.key.F:
            self._toggle_speed()
        elif symbol == arcade.key.SPACE:
            self._call_next_wave_early()
        elif symbol == arcade.key.Q:
            if self.reinforcements.ready:
                self._on_skill_button(self.reinforcements)
        elif symbol == arcade.key.W:
            if self.meteor.ready:
                self._on_skill_button(self.meteor)

    def on_mouse_press(self, x: float, y: float, button, modifiers) -> None:
        if y < HUD_HEIGHT and self.hud.handle_click(x, y):
            return
        if self.wave_preview.handle_click(x, y):
            return
        if self._selected_menu is not None:
            if self._selected_menu.handle_click(x, y):
                self._selected_menu = None
                return
            self._selected_menu = None

        if self._pending_skill is not None:
            skill = self._pending_skill
            self._pending_skill = None
            self._target_prompt.text = ""
            self.command.cast_skill(skill, target=(x, y))
            return

        if button == arcade.MOUSE_BUTTON_RIGHT and self.heroes:
            self.command.set_hero_rally(self.heroes[0], x, y)
            return

        # Tower?
        for t in self.towers:
            dx = t.center_x - x
            dy = t.center_y - y
            if dx * dx + dy * dy <= (TILE_SIZE / 2) ** 2:
                self._selected_menu = UpgradeMenu(
                    t, t.center_x, t.center_y,
                    on_upgrade=self._on_upgrade_picked,
                    on_sell=self._on_sell,
                )
                return

        # Build spot?
        for sp in self.build_spot_sprites:
            dx = sp.center_x - x
            dy = sp.center_y - y
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
        if self.command.build_tower(family, spot):
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
            self._target_prompt.text = f"Click to target {skill.display_name}  (esc to cancel)"

    # --- per-frame -------------------------------------------------

    # Upper bound on frame time we forward into the simulation. Prevents
    # enemies from teleporting across the map if the game stalls (e.g.
    # first-run sprite generation, GC pause, window drag).
    MAX_SIM_DT = 1.0 / 30.0

    def on_update(self, delta_time: float) -> None:
        if self.state.paused:
            return
        # Clamp the real-world delta *before* game_speed scaling so 2x mode
        # never lets one jumbo frame skip half a wave.
        clamped = min(delta_time, self.MAX_SIM_DT)
        dt = clamped * self.state.game_speed

        if self._first_wave_timer > 0:
            self._first_wave_timer -= dt
            if self._first_wave_timer <= 0:
                self.wave_manager.start_next_wave()

        self.spawner.update_followers([e for e in self.enemies if e.alive], dt)

        for sprite_list in (self.enemies, self.units, self.towers, self.projectiles):
            for sp in sprite_list:
                sp.on_update(dt)

        # Hero respawn / XP ticks
        for hero in self.heroes:
            if not hero.alive:
                continue

        self.combat.resolve_engagement(self.units, self.enemies)
        for t in self.towers:
            t.try_attack(self.enemies, self)
        self.combat.tick_projectiles(self.projectiles, self.enemies)

        for e in list(self.enemies):
            if not e.alive and (e.anim is None or e.anim.finished):
                e.remove_from_sprite_lists()
        for u in list(self.units):
            if not u.alive and getattr(u, "respawn_timer", 0.0) <= 0:
                from td_game.entities.heroes.base_hero import BaseHero
                if not isinstance(u, BaseHero):
                    u.remove_from_sprite_lists()

        for sp in list(self._fx_lifetimes.keys()):
            self._fx_lifetimes[sp] -= dt
            if self._fx_lifetimes[sp] <= 0:
                sp.remove_from_sprite_lists()
                del self._fx_lifetimes[sp]

        active_count = sum(1 for e in self.enemies if e.alive)
        self.wave_manager.update(dt, active_count)

        if self._wave_banner_ttl > 0:
            self._wave_banner_ttl -= dt

        # Wave preview: show during pre-wave grace or inter-wave breathers.
        from td_game.systems.wave_manager import WaveState
        if self._first_wave_timer > 0:
            self.wave_preview.set_wave(
                self.wave_manager.waves[0] if self.wave_manager.waves else None,
                self._first_wave_timer,
                self._call_early_bonus_preview(),
            )
        elif self.wave_manager.phase is WaveState.BETWEEN:
            nxt = self.wave_manager.next_wave()
            self.wave_preview.set_wave(
                nxt, self.wave_manager.between_timer, self._call_early_bonus_preview(),
            )
        else:
            self.wave_preview.hide()

        self.hud.update(dt)

        if self.state.lost:
            self.state.bus.publish(LEVEL_LOST)

    # --- rendering --------------------------------------------------

    def on_draw(self) -> None:
        self.clear()
        # Background meadow (single texture — no grid seams).
        if self.background_sprite is not None:
            arcade.draw_sprite(self.background_sprite)
        # Path: draw two passes (darker border + lighter dirt) as
        # circles-at-joints plus thick line segments between. Circles
        # fill joint gaps so the ribbon reads as one continuous track.
        from td_game.graphics.procedural import palette as P
        for curve in self._path_curves:
            self._draw_path_ribbon(curve, width=56, color=P.PATH_DARK)
            self._draw_path_ribbon(curve, width=44, color=P.PATH)
        self.decor_sprites.draw()
        self.build_spot_sprites.draw()
        self.towers.draw()
        self.units.draw()
        self.enemies.draw()
        self.projectiles.draw()
        self.fx.draw()

        for e in self.enemies:
            draw_health_bar(e)
        for u in self.units:
            if u.alive:
                draw_health_bar(u)

        # Range preview under open BuildMenu (drawn over the world but
        # under the menu popup + HUD).
        if isinstance(self._selected_menu, BuildMenu):
            self._selected_menu.draw_preview(self._can_afford_family)

        self.hud.draw()
        self.wave_preview.draw()

        if self._selected_menu is not None:
            self._selected_menu.draw()

        if self._pending_skill is not None:
            self._target_prompt.draw()
            if self._pending_skill.target_kind.name == "AREA":
                arcade.draw_circle_outline(
                    self._mouse_x, self._mouse_y,
                    getattr(self._pending_skill, "radius", 60),
                    (252, 160, 60, 180), 2,
                )
                arcade.draw_circle_filled(
                    self._mouse_x, self._mouse_y,
                    getattr(self._pending_skill, "radius", 60),
                    (252, 160, 60, 40),
                )

        if self._wave_banner is not None and self._wave_banner_ttl > 0:
            self._wave_banner.draw()

        self._draw_hover_tooltip()

    def _draw_hover_tooltip(self) -> None:
        if self._selected_menu is not None or self._pending_skill is not None:
            return
        if self._mouse_y < HUD_HEIGHT:
            return
        # Enemy under cursor?
        for e in self.enemies:
            if not e.alive:
                continue
            dx = e.center_x - self._mouse_x
            dy = e.center_y - self._mouse_y
            if dx * dx + dy * dy <= 20 * 20:
                panel = enemy_panel(e.stats)
                panel.draw(self._mouse_x, self._mouse_y + 24, align="above")
                return
        # Tower under cursor?
        for t in self.towers:
            dx = t.center_x - self._mouse_x
            dy = t.center_y - self._mouse_y
            if dx * dx + dy * dy <= 24 * 24:
                panel = tower_panel(t.family, t._row)
                panel.draw(self._mouse_x, self._mouse_y + 24, align="above")
                arcade.draw_circle_outline(t.center_x, t.center_y, t.range,
                                           (252, 240, 180, 120), 1)
                return
        # Build spot under cursor?
        for sp in self.build_spot_sprites:
            dx = sp.center_x - self._mouse_x
            dy = sp.center_y - self._mouse_y
            if dx * dx + dy * dy <= 20 * 20:
                panel = InfoPanel(
                    title="Build Spot",
                    body=("Click to construct a tower here.",
                          "4 families: Archer, Barracks, Mage, Artillery."),
                    accent=(232, 192, 84),
                )
                panel.draw(self._mouse_x, self._mouse_y + 24, align="above")
                return

    # --- game-over routing -----------------------------------------

    def _route_to_end(self, won: bool) -> None:
        from .game_over import GameOverView
        self.window.show_view(GameOverView(self.level, won))
