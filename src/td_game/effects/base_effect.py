"""Status effects applied to Entities."""
from __future__ import annotations

from typing import TYPE_CHECKING

from td_game.core.constants import EffectTag

if TYPE_CHECKING:
    from td_game.entities.entity import Entity


class BaseEffect:
    """One status effect instance. Instances are not shared between targets.

    Contract:
      - `tag` classifies the effect for enemy immunity checks.
      - `duration` counts down in `tick`. When <= 0, the effect removes itself.
      - `stackable=False` (default) means re-apply refreshes duration;
        True means stacks add independent instances.
    """
    tag: EffectTag
    duration: float = 3.0
    tick_interval: float = 0.5
    stackable: bool = False

    def __init__(self, duration: float | None = None) -> None:
        if duration is not None:
            self.duration = duration
        self._remaining = self.duration
        self._since_tick = 0.0

    # Lifecycle hooks — subclasses override as needed.

    def can_apply(self, target: "Entity") -> bool:
        # Enemies declare a set of EffectTag immunities on their data row.
        immunities = getattr(target, "immunities", frozenset())
        return self.tag not in immunities

    def on_apply(self, target: "Entity") -> None: ...
    def on_tick(self, target: "Entity") -> None: ...
    def on_remove(self, target: "Entity") -> None: ...

    def refresh(self, target: "Entity", incoming: "BaseEffect") -> None:
        self._remaining = max(self._remaining, incoming._remaining)

    def tick(self, target: "Entity", dt: float) -> None:
        self._remaining -= dt
        self._since_tick += dt
        if self._since_tick >= self.tick_interval:
            self._since_tick = 0.0
            self.on_tick(target)
        if self._remaining <= 0:
            self.remove(target)

    def remove(self, target: "Entity") -> None:
        if self in target.effects:
            target.effects.remove(self)
        self.on_remove(target)
