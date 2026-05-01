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
        engage_radius: float = 48.0,
        aggression_radius: float = 0.0,
    ) -> None:
        super().__init__(texture, x, y, max_hp=max_hp)
        self.damage = damage
        self.attack_interval = attack_interval
        self.block_slots = block_slots
        self.engage_radius = engage_radius
        # When > 0, the unit auto-walks toward the nearest enemy in this
        # radius (around its current position) before the engage check.
        self.aggression_radius = aggression_radius
        self._cooldown = 0.0
        self.blocking: list["BaseEnemy"] = []
        # Rally point (where the unit tries to return when idle).
        self.rally_x: float = x
        self.rally_y: float = y
        self.speed: float = 80.0
        self.stunned: bool = False
        # Scene back-reference set by spawn_unit; enables pursuit to look up enemies.
        self._scene = None
        # HP regen per second when out of combat (no blocking, no recent damage).
        # Subclasses may override; heroes get a higher value.
        self.regen_rate: float = 6.0
        self._out_of_combat_time: float = 0.0
        self.REGEN_DELAY = 3.0  # seconds of peace before regen kicks in

    def has_free_slot(self) -> bool:
        self.blocking = [e for e in self.blocking if e.alive]
        return len(self.blocking) < self.block_slots

    def engage(self, enemy: "BaseEnemy") -> bool:
        if not self.has_free_slot():
            return False
        self.blocking.append(enemy)
        # Freeze the enemy on the path: it now fights instead of walking.
        enemy.engaged_by = self
        enemy._attack_cd = getattr(enemy.stats, "melee_interval", 1.0) * 0.5
        return True

    def on_death(self) -> None:
        super().on_death()
        if self.anim is not None:
            from td_game.graphics.anim_controller import AnimState
            self.anim.set_state(AnimState.DEATH, force=True)

    def disengage(self) -> None:
        """Drop current engagements.

        Used when the player explicitly rallies the hero elsewhere — the
        hero abandons the fight, enemies resume walking. Matches KR feel.
        """
        for e in self.blocking:
            if getattr(e, "engaged_by", None) is self:
                e.engaged_by = None
                e._attack_cd = 0.0
        self.blocking.clear()

    def take_damage(self, packet):
        applied = super().take_damage(packet)
        if applied:
            # Incoming damage resets the out-of-combat clock.
            self._out_of_combat_time = 0.0
        return applied

    def on_update(self, dt: float) -> None:
        super().on_update(dt)
        if not self.alive or self.stunned:
            return
        if self._cooldown > 0:
            self._cooldown -= dt
        # Clean dead blocked enemies.
        self.blocking = [e for e in self.blocking if e.alive]
        # Regen: tick only while nothing is being blocked.
        if not self.blocking:
            self._out_of_combat_time += dt
            if self._out_of_combat_time >= self.REGEN_DELAY and self.hp < self.max_hp:
                self.hp = min(self.max_hp, self.hp + self.regen_rate * dt)
        else:
            self._out_of_combat_time = 0.0
        from td_game.graphics.anim_controller import AnimState
        if self.blocking:
            target = self.blocking[0]
            # Face the target smoothly.
            if target.center_x < self.center_x - 0.1:
                self.face(-1)
            elif target.center_x > self.center_x + 0.1:
                self.face(1)
            if self._cooldown <= 0:
                if self.anim is not None:
                    self.anim.set_state(AnimState.ATTACK, force=True)
                target.take_damage(DamagePacket(self.damage, DamageType.PHYSICAL, source=self))
                if self._scene is not None:
                    self._scene.spawn_fx("hit_0", target.center_x, target.center_y + 4, lifetime=0.18)
                self._cooldown = self.attack_interval
            elif self.anim is not None and self.anim.finished:
                self.anim.set_state(AnimState.IDLE)
        else:
            # Look for a pursuit target before returning to rally.
            target = self._pursue_target() if self.aggression_radius > 0 else None
            if target is not None:
                goal_x, goal_y = target.center_x, target.center_y
            else:
                goal_x, goal_y = self.rally_x, self.rally_y
            dx = goal_x - self.center_x
            dy = goal_y - self.center_y
            dist = math.hypot(dx, dy)
            # Stop just shy of the target so engage_radius triggers.
            stop_dist = max(2.0, self.engage_radius * 0.7 if target is not None else 2.0)
            if dist > stop_dist:
                step = min(self.speed * dt, dist - stop_dist)
                self.center_x += dx / dist * step
                self.center_y += dy / dist * step
                if dx < -0.1:
                    self.face(-1)
                elif dx > 0.1:
                    self.face(1)
                if self.anim is not None:
                    self.anim.set_state(AnimState.WALK)
            else:
                if self.anim is not None:
                    self.anim.set_state(AnimState.IDLE)

    def _pursue_target(self):
        """Pick the nearest living enemy within aggression_radius of the *rally* point.

        Measuring from the rally (not the unit's current position) keeps the
        unit tethered — a hero you right-click to a new spot doesn't drift off
        chasing distant enemies; soldiers hold the path their barracks rallied
        on instead of wandering.
        """
        if self._scene is None:
            return None
        best = None
        best_d2 = self.aggression_radius * self.aggression_radius
        rx, ry = self.rally_x, self.rally_y
        for e in self._scene.enemies:
            if not e.alive or getattr(e, "is_flying", False):
                continue
            dx = e.center_x - rx
            dy = e.center_y - ry
            d2 = dx * dx + dy * dy
            if d2 <= best_d2:
                best = e
                best_d2 = d2
        return best

    def set_rally(self, x: float, y: float) -> None:
        self.rally_x = x
        self.rally_y = y
