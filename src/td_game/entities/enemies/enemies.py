"""Concrete enemy factory.

All enemy *behavior* differences funnel through `EnemyStats`; if you
need a new behavior (e.g., a boss that spawns adds on death), subclass
`BaseEnemy` here and register it in `create_enemy`.
"""
from __future__ import annotations

from td_game.core.resources import load_animation_frames, load_texture
from td_game.data.enemies import ENEMIES
from td_game.graphics.animation import Animation, LoopMode
from td_game.graphics.anim_controller import AnimationController, AnimState

from .base_enemy import BaseEnemy, EnemyStats


def _build_anim_controller(base: str) -> AnimationController:
    idle = Animation(frames=load_animation_frames("enemies", f"{base}_idle", 2),
                     frame_duration=0.45, loop=LoopMode.PING_PONG)
    walk = Animation(frames=load_animation_frames("enemies", f"{base}_walk", 6),
                     frame_duration=0.09, loop=LoopMode.LOOP)
    death = Animation(frames=[load_texture("enemies", f"{base}_death_0")],
                      frame_duration=0.5, loop=LoopMode.ONCE)
    return AnimationController(
        states={AnimState.IDLE: idle, AnimState.WALK: walk, AnimState.DEATH: death},
        initial=AnimState.WALK,
    )


def create_enemy(enemy_id: str, bus=None) -> BaseEnemy:
    stats: EnemyStats = ENEMIES[enemy_id]
    ctrl = _build_anim_controller(stats.sprite_base)
    # Seed texture with the first walk frame.
    initial_tex = ctrl.states[AnimState.WALK].frames[0]
    enemy = BaseEnemy(stats, initial_tex, bus=bus)
    enemy.anim = ctrl
    return enemy
