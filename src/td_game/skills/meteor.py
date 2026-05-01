"""Global Meteor skill: AoE damage at a point."""
from __future__ import annotations

from td_game.core.constants import DamageType
from td_game.core.damage import DamagePacket
from td_game.core.events import SKILL_USED

from .base_skill import BaseSkill, SkillContext, TargetKind


class Meteor(BaseSkill):
    id = "meteor"
    display_name = "Meteor"
    target_kind = TargetKind.AREA

    def __init__(self, cooldown: float = 25.0, cost: int = 0, damage: float = 220.0, radius: float = 90.0) -> None:
        super().__init__(cooldown, cost)
        self.damage = damage
        self.radius = radius

    def on_activate(self, ctx: SkillContext, target) -> None:
        x, y = target
        packet = DamagePacket(self.damage, DamageType.FIRE, source=self)
        # Apply to all enemies in radius. Skill bypasses projectile travel
        # by design (Kingdom Rush meteor is effectively instant).
        r2 = self.radius * self.radius
        for enemy in list(ctx.scene.enemies):
            if not enemy.alive:
                continue
            dx = enemy.center_x - x
            dy = enemy.center_y - y
            if dx * dx + dy * dy <= r2:
                enemy.take_damage(packet)
        ctx.scene.spawn_fx("explosion_0", x, y, lifetime=0.5)
        ctx.state.bus.publish(SKILL_USED, skill=self, target=target)
