"""Barracks soldier — animated, auto-engages nearby enemies.

The owning Barracks controls respawn timing. Sprite set is chosen per
barracks tier so an upgraded barracks is visibly more powerful — tiers
1-2 spawn padded footmen, tiers 3-4 spawn plated soldiers.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from td_game.core.resources import load_animation_frames, load_texture
from td_game.graphics.animation import Animation, LoopMode
from td_game.graphics.anim_controller import AnimationController, AnimState

from .base_unit import BaseUnit

if TYPE_CHECKING:
    from td_game.entities.towers.barracks import Barracks


class Soldier(BaseUnit):
    def __init__(self, x: float, y: float, barracks: "Barracks",
                 max_hp: float, damage: float, attack_interval: float = 1.0,
                 armor: float = 0.0, sprite_base: str = "footman") -> None:
        tex = load_texture("heroes", f"{sprite_base}_idle_0")
        super().__init__(
            tex, x, y,
            max_hp=max_hp,
            damage=damage,
            attack_interval=attack_interval,
            engage_radius=72,
            aggression_radius=120,
        )
        self.barracks = barracks
        self.armor = armor
        self.speed = 110.0
        self.sprite_base = sprite_base

        idle = Animation(
            frames=load_animation_frames("heroes", f"{sprite_base}_idle", 2),
            frame_duration=0.5, loop=LoopMode.PING_PONG,
        )
        walk = Animation(
            frames=load_animation_frames("heroes", f"{sprite_base}_walk", 6),
            frame_duration=0.09, loop=LoopMode.LOOP,
        )
        attack = Animation(
            frames=load_animation_frames("heroes", f"{sprite_base}_attack", 3),
            frame_duration=0.07, loop=LoopMode.ONCE,
        )
        death = Animation(
            frames=load_animation_frames("heroes", f"{sprite_base}_death", 4),
            frame_duration=0.12, loop=LoopMode.ONCE,
        )
        self.anim = AnimationController(
            states={
                AnimState.IDLE: idle, AnimState.WALK: walk,
                AnimState.ATTACK: attack, AnimState.DEATH: death,
            },
            initial=AnimState.IDLE,
        )

    def on_death(self) -> None:
        super().on_death()
        if self.anim is not None:
            self.anim.set_state(AnimState.DEATH, force=True)
