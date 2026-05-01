"""Burn: fire DoT."""
from __future__ import annotations

from td_game.core.constants import DamageType, EffectTag
from td_game.core.damage import DamagePacket

from .base_effect import BaseEffect


class Burn(BaseEffect):
    tag = EffectTag.BURN

    def __init__(self, dps: float = 10.0, duration: float = 3.0, tick_interval: float = 0.5) -> None:
        super().__init__(duration)
        self.dps = dps
        self.tick_interval = tick_interval

    def on_tick(self, target) -> None:
        target.take_damage(DamagePacket(self.dps * self.tick_interval, DamageType.FIRE))
