"""Hero registry.

Heroes are constructed via factories (not plain dataclass rows) because
each hero has unique skills and potentially unique subclasses later.
Level files reference heroes by id; this module maps id -> factory.
"""
from __future__ import annotations

from typing import Callable

from td_game.entities.heroes.base_hero import BaseHero
from td_game.entities.heroes.samples.knight_hero import KNIGHT_STATS, make_knight
from td_game.entities.heroes.samples.ranger_hero import RANGER_STATS, make_ranger


HeroFactory = Callable[..., BaseHero]


HEROES: dict[str, HeroFactory] = {
    "knight": make_knight,
    "ranger": make_ranger,
}


HERO_STATS = {
    "knight": KNIGHT_STATS,
    "ranger": RANGER_STATS,
}
