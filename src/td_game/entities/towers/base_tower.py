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
        tex = load_texture("towers", self._sprite_key_for(row, tier_index=0))
        super().__init__(tex, x, y, max_hp=1e9)  # effectively indestructible
        self.damage = row.damage
        self.range = row.range
        self.attack_interval = row.attack_interval
        self._cooldown = 0.0
        self.target_mode = self.default_target_mode
        self.total_invested: int = row.cost
        self.bus = bus
        self._row: TowerStatsRow = row
        self.anim = self._build_anim(tier_index=0)
        if bus is not None:
            bus.publish(TOWER_BUILT, tower=self)

    def _sprite_key_for(self, row: TowerStatsRow, tier_index: int) -> str:
        """Return a short key for the current look, e.g. 'archer_2'."""
        tier_num = (tier_index + 1) if self.current_spec is None else 4
        return f"{self.family}_{tier_num}"

    def _build_anim(self, tier_index: int):
        """Set up idle/attack animations for this tier. Subclasses may override."""
        from td_game.core.resources import load_animation_frames
        from td_game.graphics.animation import Animation, LoopMode
        from td_game.graphics.anim_controller import AnimationController, AnimState
        base = self._sprite_key_for(self._row, tier_index) if hasattr(self, "_row") else f"{self.family}_{tier_index+1}"
        idle = Animation(
            frames=load_animation_frames("towers", f"{base}_idle", 2),
            frame_duration=0.5, loop=LoopMode.PING_PONG,
        )
        attack = Animation(
            frames=load_animation_frames("towers", f"{base}_attack", 3),
            frame_duration=0.08, loop=LoopMode.ONCE,
        )
        return AnimationController(
            states={AnimState.IDLE: idle, AnimState.ATTACK: attack},
            initial=AnimState.IDLE,
        )

    # --- rows / upgrades ---------------------------------------------

    def _apply_row(self, row: TowerStatsRow) -> None:
        self._row = row
        self.damage = row.damage
        self.range = row.range
        self.attack_interval = row.attack_interval
        # Rebuild animation for the new tier's look.
        self.anim = self._build_anim(tier_index=self.current_tier_index)
        self.texture = load_texture("towers", self._sprite_key_for(row, self.current_tier_index))

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
        # Drop back to idle when an attack clip has played out.
        if self.anim is not None and self.anim.finished:
            from td_game.graphics.anim_controller import AnimState
            self.anim.set_state(AnimState.IDLE)
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
        if self.anim is not None:
            from td_game.graphics.anim_controller import AnimState
            self.anim.set_state(AnimState.ATTACK, force=True)
        return True

    def perform_attack(self, target: "BaseEnemy", scene) -> None:
        """Subclass hook — defaults to no-op so subclass forgets are obvious."""
        raise NotImplementedError
