"""Global Reinforcements skill: summons two temp soldiers at a point."""
from __future__ import annotations

from td_game.core.events import SKILL_USED
from td_game.entities.units.reinforcement import Reinforcement

from .base_skill import BaseSkill, SkillContext, TargetKind


class Reinforcements(BaseSkill):
    id = "reinforcements"
    display_name = "Reinforcements"
    description = "Summons two temporary peasants at the chosen point. They block enemies for about 12 seconds."
    icon = "reinforcements_0"
    target_kind = TargetKind.POINT

    def __init__(self, cooldown: float = 15.0, cost: int = 0, count: int = 2) -> None:
        super().__init__(cooldown, cost)
        self.count = count

    def on_activate(self, ctx: SkillContext, target) -> None:
        x, y = target
        for i in range(self.count):
            offset = (i - (self.count - 1) / 2) * 16
            r = Reinforcement(x + offset, y)
            ctx.scene.spawn_unit(r)
        ctx.state.bus.publish(SKILL_USED, skill=self, target=target)
