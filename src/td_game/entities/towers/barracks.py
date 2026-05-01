"""Barracks tower: stationary, spawns melee soldiers that hold a rally point."""
from __future__ import annotations

import math

from ..units.soldier import Soldier
from .base_tower import BaseTower


class Barracks(BaseTower):
    family = "barracks"
    can_hit_ground = False
    can_hit_flying = False  # soldiers attack; the tower itself does not

    INITIAL_SPAWN_CD = 0.5   # fast fill on barracks construction
    RESPAWN_CD = 7.0         # slower replacement after a soldier dies

    def __init__(self, tree, x, y, bus=None) -> None:
        super().__init__(tree, x, y, bus=bus)
        self.soldiers: list[Soldier] = []
        # Rally defaults to tower position; scene overrides to the nearest
        # path point so soldiers spawn where they'll actually block enemies.
        self.rally_x: float = x
        self.rally_y: float = y
        self._respawn_cd: float = 0.0
        self._total_spawned: int = 0

    def try_attack(self, enemies, scene) -> bool:
        # Barracks don't shoot. Keep soldier count at the tier-desired value.
        desired = int(self._row.extras.get("unit_count", 3))
        self.soldiers = [s for s in self.soldiers if s.alive]
        if self._respawn_cd > 0:
            return False
        if len(self.soldiers) < desired:
            self._spawn_soldier(scene)
            self._total_spawned += 1
            # First batch (until all slots have been filled once) pops out
            # quickly so the barracks feels alive; replacement after deaths
            # uses the long cooldown so losses actually matter.
            if self._total_spawned <= desired:
                self._respawn_cd = self.INITIAL_SPAWN_CD
            else:
                self._respawn_cd = self.RESPAWN_CD
        return False

    def on_update(self, dt: float) -> None:
        super().on_update(dt)
        if self._respawn_cd > 0:
            self._respawn_cd -= dt

    def perform_attack(self, target, scene) -> None:
        return  # never called

    def _spawn_soldier(self, scene) -> None:
        row = self._row
        extras = row.extras
        count = max(1, int(extras.get("unit_count", 3)))
        idx = len(self.soldiers)
        angle = (idx / count) * math.tau
        offset_x = math.cos(angle) * 18
        offset_y = math.sin(angle) * 18
        # Tier -> sprite set: makes an upgraded barracks visibly stronger.
        # tier_index is 0 for tier 1, 1 for tier 2, 2 for tier 3. Spec is tier 4.
        if self.current_spec is not None:
            sprite_base = "soldier"   # tier-4 spec — same visual as tier 3 for now
        elif self.current_tier_index >= 2:
            sprite_base = "soldier"   # tier 3
        else:
            sprite_base = "footman"   # tier 1-2
        soldier = Soldier(
            self.center_x,
            self.center_y,
            barracks=self,
            max_hp=float(extras.get("unit_hp", 60)),
            damage=max(12.0, row.damage * 3.0),
            attack_interval=1.0,
            armor=float(extras.get("armor", 0.0)),
            sprite_base=sprite_base,
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

    def sell(self) -> int:
        # Also dispatch the soldiers so they don't linger after the barracks
        # is gone. Their death anim plays and they're culled by the scene.
        refund = super().sell()
        for s in self.soldiers:
            if s.alive:
                s.hp = 0
                s.on_death()
        self.soldiers.clear()
        return refund
