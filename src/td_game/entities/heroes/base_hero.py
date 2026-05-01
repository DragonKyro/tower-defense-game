"""Base hero.

A hero is a BaseUnit with XP/level, a set of Skills, and a respawn timer.
Click-to-move commands are issued via `set_rally`; the unit movement in
BaseUnit handles traversal.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import arcade

from td_game.core.constants import HERO_DEFAULT_RESPAWN
from td_game.core.events import HERO_DIED, HERO_RESPAWNED
from td_game.entities.units.base_unit import BaseUnit

if TYPE_CHECKING:
    from td_game.skills.base_skill import BaseSkill


@dataclass
class HeroStats:
    id: str
    display_name: str
    max_hp: float
    damage: float
    attack_interval: float
    speed: float = 120.0
    armor: float = 0.0
    magic_resist: float = 0.0
    engage_radius: float = 72.0
    aggression_radius: float = 160.0
    xp_curve: tuple[int, ...] = (50, 130, 240, 400, 620, 900, 1260, 1700, 2220)
    sprite_base: str = "knight"
    description: str = ""


class BaseHero(BaseUnit):
    def __init__(
        self,
        stats: HeroStats,
        texture: arcade.Texture,
        skills: list["BaseSkill"],
        x: float,
        y: float,
        bus=None,
    ) -> None:
        super().__init__(
            texture, x, y,
            max_hp=stats.max_hp,
            damage=stats.damage,
            attack_interval=stats.attack_interval,
            block_slots=1,
            engage_radius=stats.engage_radius,
            aggression_radius=stats.aggression_radius,
        )
        self.stats = stats
        self.speed = stats.speed
        self.armor = stats.armor
        self.magic_resist = stats.magic_resist
        self.skills = skills
        self.xp = 0
        self.level = 1
        self.bus = bus
        self.respawn_timer = 0.0
        self.respawn_delay = HERO_DEFAULT_RESPAWN
        self._home_x = x
        self._home_y = y

    # --- xp / level --------------------------------------------------

    def gain_xp(self, amount: int) -> None:
        self.xp += amount
        while self.level - 1 < len(self.stats.xp_curve) and self.xp >= self.stats.xp_curve[self.level - 1]:
            self.level += 1
            self.on_level_up()

    def on_level_up(self) -> None:
        # Small stat bump per level; specific heroes can customize.
        self.max_hp *= 1.1
        self.hp = self.max_hp
        self.damage *= 1.1

    # --- death / respawn ---------------------------------------------

    def on_death(self) -> None:
        super().on_death()
        self.respawn_timer = self.respawn_delay
        if self.bus is not None:
            self.bus.publish(HERO_DIED, hero=self)

    def update_respawn(self, dt: float) -> None:
        if self.alive or self.respawn_timer <= 0:
            return
        self.respawn_timer -= dt
        if self.respawn_timer <= 0:
            self.alive = True
            self.hp = self.max_hp
            self.center_x = self._home_x
            self.center_y = self._home_y
            self.rally_x = self._home_x
            self.rally_y = self._home_y
            if self.anim is not None:
                from td_game.graphics.anim_controller import AnimState
                self.anim.set_state(AnimState.IDLE, force=True)
            if self.bus is not None:
                self.bus.publish(HERO_RESPAWNED, hero=self)

    # --- per-frame ---------------------------------------------------

    def on_update(self, dt: float) -> None:
        if self.alive:
            super().on_update(dt)
            for s in self.skills:
                s.update(dt)
        else:
            self.update_respawn(dt)
