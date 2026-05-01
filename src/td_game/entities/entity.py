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

    # --- lifecycle ---------------------------------------------------

    def on_update(self, dt: float) -> None:
        if not self.alive:
            return
        # Tick status effects (list copy because they may remove themselves)
        for eff in list(self.effects):
            eff.tick(self, dt)
        if self.anim is not None:
            self.texture = self.anim.update(dt)

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
