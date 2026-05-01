"""Knight hero skills: defensive-oriented."""
from __future__ import annotations

from td_game.core.constants import DamageType
from td_game.core.damage import DamagePacket

from ..base_skill import BaseSkill, SkillContext, TargetKind


class ShieldBash(BaseSkill):
    id = "shield_bash"
    display_name = "Shield Bash"
    target_kind = TargetKind.SELF

    def __init__(self) -> None:
        super().__init__(cooldown=8.0)

    def on_activate(self, ctx: SkillContext, target) -> None:
        from td_game.effects.stun import Stun
        hero = ctx.hero
        if hero is None:
            return
        for enemy in hero.blocking:
            enemy.take_damage(DamagePacket(hero.damage * 2, DamageType.PHYSICAL, source=hero))
            enemy.apply_effect(Stun(duration=1.5))


class Rally(BaseSkill):
    id = "rally"
    display_name = "Rally"
    target_kind = TargetKind.SELF

    def __init__(self) -> None:
        super().__init__(cooldown=18.0)

    def on_activate(self, ctx: SkillContext, target) -> None:
        hero = ctx.hero
        if hero is None:
            return
        hero.hp = min(hero.max_hp, hero.hp + hero.max_hp * 0.35)
        # Buff nearby units — placeholder: +armor for 5s (real effect could be a BuffEffect).
        hero.armor += 4
