"""Base melee unit.

Units *block* enemies (Kingdom Rush rallying mechanic): while a unit has
a free block slot, an adjacent enemy stops and fights instead of walking
past. Heroes and barracks soldiers both inherit from BaseUnit.
"""
from __future__ import annotations

import math
from typing import TYPE_CHECKING

import arcade

from td_game.core.constants import DamageType
from td_game.core.damage import DamagePacket
from td_game.entities.entity import Entity

if TYPE_CHECKING:
    from td_game.entities.enemies.base_enemy import BaseEnemy


class BaseUnit(Entity):
    def __init__(
        self,
        texture: arcade.Texture,
        x: float,
        y: float,
        max_hp: float,
        damage: float,
        attack_interval: float = 1.0,
        block_slots: int = 1,
        engage_radius: float = 36.0,
    ) -> None:
        super().__init__(texture, x, y, max_hp=max_hp)
        self.damage = damage
        self.attack_interval = attack_interval
        self.block_slots = block_slots
        self.engage_radius = engage_radius
        self._cooldown = 0.0
        self.blocking: list["BaseEnemy"] = []
        # Rally point (where the unit tries to return when idle).
        self.rally_x: float = x
        self.rally_y: float = y
        self.speed: float = 80.0
        self.stunned: bool = False

    def has_free_slot(self) -> bool:
        self.blocking = [e for e in self.blocking if e.alive]
        return len(self.blocking) < self.block_slots

    def engage(self, enemy: "BaseEnemy") -> bool:
        if not self.has_free_slot():
            return False
        self.blocking.append(enemy)
        return True

    def on_update(self, dt: float) -> None:
        super().on_update(dt)
        if not self.alive or self.stunned:
            return
        if self._cooldown > 0:
            self._cooldown -= dt
        # Clean dead blocked enemies.
        self.blocking = [e for e in self.blocking if e.alive]
        if self.blocking:
            target = self.blocking[0]
            if self._cooldown <= 0:
                target.take_damage(DamagePacket(self.damage, DamageType.PHYSICAL, source=self))
                self._cooldown = self.attack_interval
        else:
            # Walk back to rally point.
            dx = self.rally_x - self.center_x
            dy = self.rally_y - self.center_y
            dist = math.hypot(dx, dy)
            if dist > 2:
                step = min(self.speed * dt, dist)
                self.center_x += dx / dist * step
                self.center_y += dy / dist * step

    def set_rally(self, x: float, y: float) -> None:
        self.rally_x = x
        self.rally_y = y
