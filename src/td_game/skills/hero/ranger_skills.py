"""Ranger hero skills: ranged / DoT / mobility."""
from __future__ import annotations

from td_game.core.constants import DamageType
from td_game.core.damage import DamagePacket

from ..base_skill import BaseSkill, SkillContext, TargetKind


class PoisonArrow(BaseSkill):
    id = "poison_arrow"
    display_name = "Poison Arrow"
    description = "1.5x damage to one enemy and poisons them for 5 seconds."
    icon = "poisonarrow_0"
    target_kind = TargetKind.ENEMY

    def __init__(self) -> None:
        super().__init__(cooldown=6.0)

    def on_activate(self, ctx: SkillContext, target) -> None:
        from td_game.effects.poison import Poison
        hero = ctx.hero
        if hero is None or target is None:
            return
        target.take_damage(DamagePacket(hero.damage * 1.5, DamageType.PHYSICAL, source=hero))
        target.apply_effect(Poison(dps=12, duration=5.0))


class Volley(BaseSkill):
    id = "volley"
    display_name = "Volley"
    description = "Rain arrows over an area. 1.2x damage to every enemy in radius."
    icon = "volley_0"
    target_kind = TargetKind.AREA

    def __init__(self) -> None:
        super().__init__(cooldown=14.0)
        self.radius = 80.0
        self.damage_mult = 1.2

    def on_activate(self, ctx: SkillContext, target) -> None:
        hero = ctx.hero
        if hero is None:
            return
        x, y = (target if target else (hero.center_x, hero.center_y))
        r2 = self.radius * self.radius
        for enemy in list(ctx.scene.enemies):
            if not enemy.alive:
                continue
            dx = enemy.center_x - x
            dy = enemy.center_y - y
            if dx * dx + dy * dy <= r2:
                enemy.take_damage(DamagePacket(hero.damage * self.damage_mult, DamageType.PHYSICAL, source=hero))
