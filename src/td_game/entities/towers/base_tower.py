"""Abstract tower.

A concrete Tower subclass is mostly glue: pick a targeting mode default,
tell us what projectile to fire (or which unit to spawn for barracks),
and how to react to an `on_attack` event.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Optional

import arcade

from td_game.core.constants import SELL_REFUND_RATIO
from td_game.core.events import TOWER_BUILT, TOWER_SOLD, TOWER_UPGRADED
from td_game.core.resources import load_texture
from td_game.entities.entity import Entity

from . import targeting
from .targeting import TargetMode
from .upgrade_tree import TowerStatsRow, UpgradeTree

if TYPE_CHECKING:
    from td_game.entities.enemies.base_enemy import BaseEnemy


class BaseTower(Entity):
    """Superclass for stationary towers.

    Most tower variety is data-driven via the UpgradeTree. Subclasses
    exist mainly to override `perform_attack` (how an attack resolves:
    spawn a projectile? pulse AoE? spawn a unit?).
    """
    family: str = "archer"                 # overridden by subclasses
    can_hit_ground: bool = True
    can_hit_flying: bool = True
    default_target_mode: TargetMode = TargetMode.FIRST

    def __init__(self, tree: UpgradeTree, x: float, y: float, bus=None) -> None:
        self.tree = tree
        self.current_tier_index = 0
        self.current_spec: Optional[str] = None
        row = tree.tiers[0]
        tex = load_texture("towers", row.sprite or f"{self.family}_1")
        super().__init__(tex, x, y, max_hp=1e9)  # effectively indestructible
        self.damage = row.damage
        self.range = row.range
        self.attack_interval = row.attack_interval
        self._cooldown = 0.0
        self.target_mode = self.default_target_mode
        self.total_invested: int = row.cost
        self.bus = bus
        self._row: TowerStatsRow = row
        if bus is not None:
            bus.publish(TOWER_BUILT, tower=self)

    # --- rows / upgrades ---------------------------------------------

    def _apply_row(self, row: TowerStatsRow) -> None:
        self._row = row
        self.damage = row.damage
        self.range = row.range
        self.attack_interval = row.attack_interval
        if row.sprite:
            self.texture = load_texture("towers", row.sprite)

    def next_upgrades(self) -> list[tuple[str, TowerStatsRow]]:
        return self.tree.next_upgrades(self.current_tier_index, self.current_spec)

    def upgrade_to(self, node_id: str) -> bool:
        for nid, row in self.next_upgrades():
            if nid == node_id:
                self.total_invested += row.cost
                if nid.isdigit():
                    self.current_tier_index = int(nid)
                else:
                    self.current_spec = nid
                self._apply_row(row)
                if self.bus is not None:
                    self.bus.publish(TOWER_UPGRADED, tower=self, row=row)
                return True
        return False

    def sell_value(self) -> int:
        return int(self.total_invested * SELL_REFUND_RATIO)

    def sell(self) -> int:
        refund = self.sell_value()
        self.alive = False
        if self.bus is not None:
            self.bus.publish(TOWER_SOLD, tower=self, refund=refund)
        return refund

    # --- per-frame --------------------------------------------------

    def on_update(self, dt: float) -> None:
        super().on_update(dt)
        if self._cooldown > 0:
            self._cooldown -= dt

    def try_attack(self, enemies, scene) -> bool:
        """Called every frame by the combat system.

        Returns True if an attack was performed this frame.
        """
        if self._cooldown > 0:
            return False
        target = targeting.pick(self, enemies)
        if target is None:
            return False
        self.perform_attack(target, scene)
        self._cooldown = self.attack_interval
        return True

    def perform_attack(self, target: "BaseEnemy", scene) -> None:
        """Subclass hook — defaults to no-op so subclass forgets are obvious."""
        raise NotImplementedError
