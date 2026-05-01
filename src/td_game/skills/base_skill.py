"""Base skill.

Skills have:
  - a cooldown that ticks in `update(dt)`
  - optional gold cost
  - a `target_kind` telling the UI what to prompt for
  - `activate(ctx, target)` that performs the effect

Both *global* skills (Reinforcements, Meteor) and *hero* skills share
this base. Hero skills additionally see `ctx.hero`.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any


class TargetKind(Enum):
    SELF = auto()       # no targeting: fires immediately
    POINT = auto()      # requires a map point
    ENEMY = auto()      # requires an enemy
    AREA = auto()       # point + radius telegraphed by UI


@dataclass
class SkillContext:
    """Passed to every skill activation.

    Carrying a reference to the scene + game_state keeps skill code free
    to read/write the world without each subclass plumbing both through.
    """
    scene: Any
    state: Any
    hero: Any = None


class BaseSkill:
    id: str = "skill"
    display_name: str = "Skill"
    target_kind: TargetKind = TargetKind.SELF

    def __init__(self, cooldown: float = 10.0, cost: int = 0) -> None:
        self.cooldown = cooldown
        self.cost = cost
        self._cooldown_left = 0.0

    @property
    def ready(self) -> bool:
        return self._cooldown_left <= 0

    def update(self, dt: float) -> None:
        if self._cooldown_left > 0:
            self._cooldown_left -= dt

    def can_activate(self, ctx: SkillContext) -> bool:
        if not self.ready:
            return False
        if self.cost > 0 and ctx.state.gold < self.cost:
            return False
        return True

    def activate(self, ctx: SkillContext, target: Any = None) -> bool:
        if not self.can_activate(ctx):
            return False
        if self.cost > 0:
            if not ctx.state.spend_gold(self.cost, reason=f"skill:{self.id}"):
                return False
        self.on_activate(ctx, target)
        self._cooldown_left = self.cooldown
        return True

    def on_activate(self, ctx: SkillContext, target: Any) -> None:
        raise NotImplementedError
