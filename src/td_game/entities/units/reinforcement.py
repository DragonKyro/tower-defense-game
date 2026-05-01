"""Temporary summoned peasants via the global Reinforcements skill.

Distinct sprite set from the barracks Soldier so the player can tell
"these two blockers I just placed" apart from "the soldiers guarding the
north barracks". Die permanently (no respawn) and despawn after
`lifetime` seconds.
"""
from __future__ import annotations

from td_game.core.resources import load_animation_frames, load_texture
from td_game.graphics.animation import Animation, LoopMode
from td_game.graphics.anim_controller import AnimationController, AnimState

from .base_unit import BaseUnit


class Reinforcement(BaseUnit):
    def __init__(self, x: float, y: float,
                 max_hp: float = 60, damage: float = 8, lifetime: float = 12.0) -> None:
        tex = load_texture("heroes", "peasant_idle_0")
        super().__init__(tex, x, y, max_hp=max_hp, damage=damage,
                         attack_interval=1.1, engage_radius=60, aggression_radius=80)
        self.lifetime = lifetime
        idle = Animation(
            frames=load_animation_frames("heroes", "peasant_idle", 2),
            frame_duration=0.55, loop=LoopMode.PING_PONG,
        )
        walk = Animation(
            frames=load_animation_frames("heroes", "peasant_walk", 6),
            frame_duration=0.09, loop=LoopMode.LOOP,
        )
        attack = Animation(
            frames=load_animation_frames("heroes", "peasant_attack", 3),
            frame_duration=0.09, loop=LoopMode.ONCE,
        )
        death = Animation(
            frames=load_animation_frames("heroes", "peasant_death", 4),
            frame_duration=0.12, loop=LoopMode.ONCE,
        )
        self.anim = AnimationController(
            states={
                AnimState.IDLE: idle, AnimState.WALK: walk,
                AnimState.ATTACK: attack, AnimState.DEATH: death,
            },
            initial=AnimState.IDLE,
        )

    def on_update(self, dt: float) -> None:
        super().on_update(dt)
        self.lifetime -= dt
        if self.lifetime <= 0 and self.alive:
            self.hp = 0
            self.on_death()
