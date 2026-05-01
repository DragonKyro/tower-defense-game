"""Sample hero: Ranger (ranged / DoT / mobile)."""
from __future__ import annotations

from td_game.core.resources import load_texture
from td_game.entities.heroes.base_hero import BaseHero, HeroStats
from td_game.skills.hero.ranger_skills import PoisonArrow, Volley


RANGER_STATS = HeroStats(
    id="ranger",
    display_name="Elyse",
    max_hp=180,
    damage=22,
    attack_interval=0.7,
    speed=110,
    armor=1,
    magic_resist=0.05,
    engage_radius=48,
    sprite="ranger",
)


def make_ranger(x: float, y: float, bus=None) -> BaseHero:
    tex = load_texture("heroes", RANGER_STATS.sprite)
    skills = [PoisonArrow(), Volley()]
    return BaseHero(RANGER_STATS, tex, skills, x, y, bus=bus)
