"""Armor shred: reduces target armor for a duration."""
from __future__ import annotations

from td_game.core.constants import EffectTag

from .base_effect import BaseEffect


class ArmorShred(BaseEffect):
    tag = EffectTag.ARMOR_SHRED

    def __init__(self, amount: float = 5.0, duration: float = 4.0) -> None:
        super().__init__(duration)
        self.amount = amount

    def on_apply(self, target) -> None:
        target.armor = max(0.0, target.armor - self.amount)
        self._applied = self.amount

    def on_remove(self, target) -> None:
        target.armor = target.armor + getattr(self, "_applied", 0.0)
