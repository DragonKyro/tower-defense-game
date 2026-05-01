"""Temporary summoned soldiers via the global Reinforcements skill.

Die permanently (no respawn) and despawn after `lifetime` seconds.
"""
from __future__ import annotations

import arcade

from .base_unit import BaseUnit


class Reinforcement(BaseUnit):
    def __init__(self, texture: arcade.Texture, x: float, y: float,
                 max_hp: float = 60, damage: float = 8, lifetime: float = 12.0) -> None:
        super().__init__(texture, x, y, max_hp=max_hp, damage=damage, attack_interval=1.0)
        self.lifetime = lifetime

    def on_update(self, dt: float) -> None:
        super().on_update(dt)
        self.lifetime -= dt
        if self.lifetime <= 0 and self.alive:
            self.hp = 0
            self.on_death()
