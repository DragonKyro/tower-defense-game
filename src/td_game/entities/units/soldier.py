"""Barracks soldier: animated, auto-engages nearby enemies, respawns on death."""
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
                 armor: float = 0.0) -> None:
        # Seed texture with the first walk frame so the sprite is valid
        # before on_update runs.
        tex = load_texture("heroes", "knight_idle_0")
        super().__init__(
            tex, x, y,
            max_hp=max_hp,
            damage=damage,
            attack_interval=attack_interval,
            engage_radius=72,       # generous — reliably catches enemies on the lane
            aggression_radius=120,  # chase enemies approaching rally
        )
        self.barracks = barracks
        self.armor = armor
        self.speed = 110.0  # snappier than the default 80 so they reach the path fast
        self._respawn_delay = 8.0
        self.respawn_timer = 0.0

        idle = Animation(
            frames=load_animation_frames("heroes", "knight_idle", 2),
            frame_duration=0.5, loop=LoopMode.PING_PONG,
        )
        walk = Animation(
            frames=load_animation_frames("heroes", "knight_walk", 6),
            frame_duration=0.09, loop=LoopMode.LOOP,
        )
        attack = Animation(
            frames=load_animation_frames("heroes", "knight_attack", 3),
            frame_duration=0.07, loop=LoopMode.ONCE,
        )
        death = Animation(
            frames=load_animation_frames("heroes", "knight_death", 4),
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
        self.respawn_timer = self._respawn_delay
