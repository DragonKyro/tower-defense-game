"""Stun: target cannot move or act while active."""
from __future__ import annotations

from td_game.core.constants import EffectTag

from .base_effect import BaseEffect


class Stun(BaseEffect):
    tag = EffectTag.STUN

    def __init__(self, duration: float = 1.5) -> None:
        super().__init__(duration)

    def on_apply(self, target) -> None:
        target.stunned = True

    def on_remove(self, target) -> None:
        # Still stunned if another Stun is active.
        target.stunned = any(isinstance(e, Stun) for e in target.effects)
