"""Global Reinforcements skill: summons two temp soldiers at a point."""
from __future__ import annotations

from td_game.core.events import SKILL_USED
from td_game.core.resources import load_texture
from td_game.entities.units.reinforcement import Reinforcement

from .base_skill import BaseSkill, SkillContext, TargetKind


class Reinforcements(BaseSkill):
    id = "reinforcements"
    display_name = "Reinforcements"
    target_kind = TargetKind.POINT

    def __init__(self, cooldown: float = 15.0, cost: int = 0, count: int = 2) -> None:
        super().__init__(cooldown, cost)
        self.count = count

    def on_activate(self, ctx: SkillContext, target) -> None:
        x, y = target
        tex = load_texture("heroes", "knight")
        for i in range(self.count):
            offset = (i - (self.count - 1) / 2) * 16
            r = Reinforcement(tex, x + offset, y)
            ctx.scene.spawn_unit(r)
        ctx.state.bus.publish(SKILL_USED, skill=self, target=target)
