"""Damage primitives."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from .constants import DamageType

if TYPE_CHECKING:
    from td_game.effects.base_effect import BaseEffect


@dataclass
class DamagePacket:
    """Describes a single hit.

    `source` is an opaque reference (usually the tower/unit/hero that
    dealt the damage) kept around so kill attribution / on-kill effects
    can route back to it without tight coupling.
    """
    amount: float
    type: DamageType = DamageType.PHYSICAL
    source: object | None = None
    # Optional status effects applied on hit. Each entry is a factory so
    # fresh instances are produced per target (effects are stateful).
    on_hit_effects: list = field(default_factory=list)
    # True damage bypass (e.g., armor-piercing shots on physical damage).
    pierce_armor: float = 0.0      # flat armor reduction
    pierce_magic: float = 0.0      # flat magic_resist reduction

    def compute_applied(self, armor: float, magic_resist: float) -> float:
        """Apply target resistances and return final HP delta."""
        if self.type is DamageType.TRUE:
            return self.amount
        if self.type in (DamageType.PHYSICAL, DamageType.SIEGE, DamageType.FIRE):
            effective = max(0.0, armor - self.pierce_armor)
            if self.type is DamageType.SIEGE:
                effective *= 0.25  # siege largely ignores armor
            return max(1.0, self.amount - effective)
        if self.type in (DamageType.MAGIC, DamageType.POISON):
            effective = max(0.0, magic_resist - self.pierce_magic)
            # magic_resist is a percentage (0..1).
            return max(1.0, self.amount * (1.0 - min(0.9, effective)))
        return self.amount
