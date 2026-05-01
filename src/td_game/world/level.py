"""Level aggregates everything a scene needs to play one stage.

Levels are declared as plain Python modules under
`td_game.data.levels.*` and registered in `td_game.data.levels.__init__`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from td_game.core.constants import (
    DEFAULT_STARTING_GOLD,
    DEFAULT_STARTING_LIVES,
    MAX_HEROES_PER_LEVEL,
    METEOR_DEFAULT_COOLDOWN,
    REINFORCEMENTS_DEFAULT_COOLDOWN,
)

from .map import Map
from .wave import Wave


@dataclass
class LevelDef:
    id: str
    display_name: str
    description: str
    map: Map
    waves: tuple[Wave, ...]
    starting_gold: int = DEFAULT_STARTING_GOLD
    starting_lives: int = DEFAULT_STARTING_LIVES
    allowed_towers: tuple[str, ...] = ("archer", "barracks", "mage", "artillery")
    hero_slots: int = 1  # up to MAX_HEROES_PER_LEVEL
    reinforcements_cooldown: float = REINFORCEMENTS_DEFAULT_COOLDOWN
    meteor_cooldown: float = METEOR_DEFAULT_COOLDOWN
    reinforcements_cost: int = 0
    meteor_cost: int = 0
    music: str | None = None
    tags: frozenset[str] = field(default_factory=frozenset)  # e.g. {"tutorial","heroic_available"}

    def __post_init__(self) -> None:
        if self.hero_slots > MAX_HEROES_PER_LEVEL:
            raise ValueError(f"hero_slots={self.hero_slots} exceeds MAX_HEROES_PER_LEVEL")
