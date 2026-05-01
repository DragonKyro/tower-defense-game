"""Barracks tower: stationary, spawns melee soldiers on a rally point."""
from __future__ import annotations

import math

from td_game.core.resources import load_texture

from ..units.soldier import Soldier
from .base_tower import BaseTower


class Barracks(BaseTower):
    family = "barracks"
    can_hit_ground = False
    can_hit_flying = False  # Barracks don't attack directly — their soldiers do

    def __init__(self, tree, x, y, bus=None) -> None:
        super().__init__(tree, x, y, bus=bus)
        self.soldiers: list[Soldier] = []
        self.rally_x: float = x + 40  # default rally in front of the tower
        self.rally_y: float = y
        self._respawn_tex = load_texture("heroes", "knight")  # reuse knight art for now

    def try_attack(self, enemies, scene) -> bool:
        # Barracks don't shoot. Instead, ensure soldier count matches tier.
        desired = int(self._row.extras.get("unit_count", 3))
        # Drop corpses; scene culls their sprites.
        self.soldiers = [s for s in self.soldiers if s.alive]
        if len(self.soldiers) < desired and self._cooldown <= 0:
            self._spawn_soldier(scene)
            # Respawn cadence uses the tower's attack_interval field as a proxy.
            self._cooldown = max(3.0, self.attack_interval * 4)
        return False

    def perform_attack(self, target, scene) -> None:
        # Never called — try_attack is overridden.
        return

    def _spawn_soldier(self, scene) -> None:
        row = self._row
        extras = row.extras
        # Ring out soldiers around the rally point.
        count = int(extras.get("unit_count", 3))
        idx = len(self.soldiers)
        angle = (idx / max(1, count)) * math.tau
        offset_x = math.cos(angle) * 18
        offset_y = math.sin(angle) * 18
        tex = self._respawn_tex
        soldier = Soldier(
            tex,
            self.rally_x + offset_x,
            self.rally_y + offset_y,
            barracks=self,
            max_hp=float(extras.get("unit_hp", 60)),
            damage=row.damage,
            attack_interval=row.attack_interval,
            armor=float(extras.get("armor", 0.0)),
        )
        soldier.set_rally(self.rally_x + offset_x, self.rally_y + offset_y)
        self.soldiers.append(soldier)
        scene.spawn_unit(soldier)

    def set_rally(self, x: float, y: float) -> None:
        self.rally_x = x
        self.rally_y = y
        count = max(1, int(self._row.extras.get("unit_count", 3)))
        for i, s in enumerate(self.soldiers):
            angle = (i / count) * math.tau
            s.set_rally(x + math.cos(angle) * 18, y + math.sin(angle) * 18)
