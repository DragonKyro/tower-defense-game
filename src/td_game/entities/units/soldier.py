"""Barracks soldier: spawned by a Barracks tower, respawns on death."""
from __future__ import annotations

from typing import TYPE_CHECKING

import arcade

from .base_unit import BaseUnit

if TYPE_CHECKING:
    from td_game.entities.towers.barracks import Barracks


class Soldier(BaseUnit):
    def __init__(self, texture: arcade.Texture, x: float, y: float, barracks: "Barracks",
                 max_hp: float, damage: float, attack_interval: float = 1.0,
                 armor: float = 0.0) -> None:
        super().__init__(texture, x, y, max_hp=max_hp, damage=damage,
                         attack_interval=attack_interval)
        self.barracks = barracks
        self.armor = armor
        self.respawn_timer = 0.0
        self._respawn_delay = 8.0

    def on_death(self) -> None:
        super().on_death()
        self.respawn_timer = self._respawn_delay
        # Scene will consult `.alive` to despawn; barracks sees `.respawn_timer`.
