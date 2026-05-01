"""Frame-based animation primitives."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Sequence

import arcade


class LoopMode(Enum):
    LOOP = auto()
    ONCE = auto()
    PING_PONG = auto()


@dataclass
class Animation:
    frames: Sequence[arcade.Texture]
    frame_duration: float = 0.1
    loop: LoopMode = LoopMode.LOOP

    def total_duration(self) -> float:
        return len(self.frames) * self.frame_duration


@dataclass
class AnimationPlayer:
    """Stateful cursor over an Animation. Cheap to allocate per-entity."""
    animation: Animation
    elapsed: float = 0.0
    finished: bool = False

    def reset(self, animation: Animation | None = None) -> None:
        if animation is not None:
            self.animation = animation
        self.elapsed = 0.0
        self.finished = False

    def advance(self, dt: float) -> arcade.Texture:
        if self.finished:
            return self.animation.frames[-1]
        self.elapsed += dt
        n = len(self.animation.frames)
        total = self.animation.total_duration()
        mode = self.animation.loop
        if mode is LoopMode.LOOP:
            idx = int((self.elapsed / self.animation.frame_duration)) % n
        elif mode is LoopMode.ONCE:
            if self.elapsed >= total:
                self.finished = True
                return self.animation.frames[-1]
            idx = int(self.elapsed / self.animation.frame_duration)
        else:  # PING_PONG
            cycle = (n - 1) * 2 or 1
            t = int(self.elapsed / self.animation.frame_duration) % cycle
            idx = t if t < n else cycle - t
        return self.animation.frames[max(0, min(idx, n - 1))]
