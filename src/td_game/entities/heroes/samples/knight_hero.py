"""Sample hero: Knight (melee tank)."""
from __future__ import annotations

from td_game.core.resources import load_texture
from td_game.entities.heroes.base_hero import BaseHero, HeroStats
from td_game.skills.hero.knight_skills import Rally, ShieldBash


KNIGHT_STATS = HeroStats(
    id="knight",
    display_name="Sir Aric",
    max_hp=260,
    damage=28,
    attack_interval=0.9,
    speed=85,
    armor=5,
    magic_resist=0.1,
    sprite="knight",
)


def make_knight(x: float, y: float, bus=None) -> BaseHero:
    tex = load_texture("heroes", KNIGHT_STATS.sprite)
    skills = [ShieldBash(), Rally()]
    return BaseHero(KNIGHT_STATS, tex, skills, x, y, bus=bus)
