"""Poison: deals damage-over-time to a target."""
from __future__ import annotations

from td_game.core.constants import DamageType, EffectTag
from td_game.core.damage import DamagePacket

from .base_effect import BaseEffect


class Poison(BaseEffect):
    tag = EffectTag.POISON

    def __init__(self, dps: float = 8.0, duration: float = 4.0, tick_interval: float = 0.5) -> None:
        super().__init__(duration)
        self.dps = dps
        self.tick_interval = tick_interval

    def on_tick(self, target) -> None:
        target.take_damage(DamagePacket(self.dps * self.tick_interval, DamageType.POISON))
