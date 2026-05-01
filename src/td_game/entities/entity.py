"""Base Entity: an Arcade Sprite plus hp, effects, and update hook.

All gameplay actors (enemies, units, heroes, towers, projectiles) extend
Entity so the scene can manage them uniformly. Towers override hp
semantics (indestructible by default) — see BaseTower.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import arcade

from td_game.core.damage import DamagePacket

if TYPE_CHECKING:
    from td_game.effects.base_effect import BaseEffect
    from td_game.graphics.anim_controller import AnimationController


class Entity(arcade.Sprite):
    # Seconds to complete a full left<->right flip. Smaller = snappier.
    FACING_FLIP_DURATION = 0.12

    def __init__(self, texture: arcade.Texture, x: float, y: float, max_hp: float = 1.0) -> None:
        super().__init__()
        self.texture = texture
        self.center_x = x
        self.center_y = y
        self.max_hp = float(max_hp)
        self.hp = float(max_hp)
        self.armor: float = 0.0
        self.magic_resist: float = 0.0  # 0..1
        self.effects: list["BaseEffect"] = []
        self.anim: "AnimationController | None" = None
        self.alive = True
        # Smooth facing: sprite scales from +1 -> -1 over FACING_FLIP_DURATION.
        self._facing_x: float = 1.0
        self._target_facing_x: float = 1.0

    # --- facing ------------------------------------------------------

    def face(self, direction: float) -> None:
        """Request the sprite face +X (direction >= 0) or -X.

        Called from movement / combat code. The actual mirror interpolates
        smoothly in `on_update` so the turn reads as a pivot rather than a
        teleport.
        """
        if direction >= 0:
            self._target_facing_x = 1.0
        else:
            self._target_facing_x = -1.0

    def _tick_facing(self, dt: float) -> None:
        if self._facing_x == self._target_facing_x:
            return
        rate = 2.0 / max(1e-3, self.FACING_FLIP_DURATION)  # full 2.0 swing per duration
        if self._target_facing_x > self._facing_x:
            self._facing_x = min(self._target_facing_x, self._facing_x + rate * dt)
        else:
            self._facing_x = max(self._target_facing_x, self._facing_x - rate * dt)
        # Avoid exact 0 (invisible frame) — nudge to a tiny value so the sprite stays rendered.
        fx = self._facing_x if abs(self._facing_x) > 0.05 else (0.05 if self._target_facing_x > 0 else -0.05)
        self.scale = (fx, 1.0)

    # --- lifecycle ---------------------------------------------------

    def on_update(self, dt: float) -> None:
        # Animation always ticks (even during death so the death clip plays).
        if self.anim is not None:
            self.texture = self.anim.update(dt)
        self._tick_facing(dt)
        if not self.alive:
            return
        # Tick status effects (list copy because they may remove themselves)
        for eff in list(self.effects):
            eff.tick(self, dt)

    def update(self, delta_time: float = 1 / 60) -> None:  # Arcade hook
        self.on_update(delta_time)

    # --- damage & effects -------------------------------------------

    def take_damage(self, packet: DamagePacket) -> float:
        if not self.alive:
            return 0.0
        applied = packet.compute_applied(self.armor, self.magic_resist)
        self.hp -= applied
        if self.hp <= 0:
            self.hp = 0
            self.on_death()
        return applied

    def on_death(self) -> None:
        self.alive = False
        # Remove effects so their on_remove hooks can run.
        for eff in list(self.effects):
            eff.remove(self)
        # Subclass hooks typically publish events and schedule a death anim.

    def apply_effect(self, effect: "BaseEffect") -> None:
        if not self.alive:
            return
        if not effect.can_apply(self):
            return
        # Stack handling: if not stackable and one already active, refresh.
        if not effect.stackable:
            for existing in self.effects:
                if type(existing) is type(effect):
                    existing.refresh(self, effect)
                    return
        self.effects.append(effect)
        effect.on_apply(self)
