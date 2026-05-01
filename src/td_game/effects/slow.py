"""Slow: reduces enemy movement speed while active."""
from __future__ import annotations

from td_game.core.constants import EffectTag

from .base_effect import BaseEffect


class Slow(BaseEffect):
    tag = EffectTag.SLOW

    def __init__(self, factor: float = 0.5, duration: float = 2.0) -> None:
        super().__init__(duration)
        self.factor = factor  # multiplier applied to speed (e.g. 0.5 = half speed)

    def on_apply(self, target) -> None:
        target.speed_multiplier = min(getattr(target, "speed_multiplier", 1.0), self.factor)

    def on_remove(self, target) -> None:
        # Recalculate: slowest remaining slow wins; if none, reset to 1.0.
        remaining = [e.factor for e in target.effects if isinstance(e, Slow)]
        target.speed_multiplier = min(remaining) if remaining else 1.0
