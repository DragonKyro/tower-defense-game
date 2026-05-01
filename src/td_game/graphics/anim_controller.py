"""State-machine wrapper that picks the right Animation per entity state."""
from __future__ import annotations

from enum import Enum, auto
from typing import Mapping

from .animation import Animation, AnimationPlayer, LoopMode


class AnimState(Enum):
    IDLE = auto()
    WALK = auto()
    ATTACK = auto()
    CAST = auto()
    DEATH = auto()
    SPAWN = auto()


class AnimationController:
    """Holds an AnimState -> Animation map and the active player.

    Entities just call `controller.set_state(...)` when their logical
    state changes, then `controller.update(dt)` each frame and assign
    the returned texture to their sprite.
    """
    def __init__(self, states: Mapping[AnimState, Animation], initial: AnimState = AnimState.IDLE) -> None:
        self.states = dict(states)
        self.current: AnimState = initial
        self.player = AnimationPlayer(self.states[initial])

    def set_state(self, state: AnimState, force: bool = False) -> None:
        if state == self.current and not force:
            return
        if state not in self.states:
            return  # silently ignore — lets us share controllers across sprite sets
        self.current = state
        self.player.reset(self.states[state])

    def update(self, dt: float):
        return self.player.advance(dt)

    @property
    def finished(self) -> bool:
        return self.player.finished
