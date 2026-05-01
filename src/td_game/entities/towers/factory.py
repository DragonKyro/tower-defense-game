"""Factory for building towers by family id.

The command/UI layer calls `build_tower('archer', spot, bus)` instead of
importing concrete subclasses directly. This is what keeps `allowed_towers`
on a Level as a list of strings.
"""
from __future__ import annotations

from td_game.data.towers import TOWER_TREES

from .archer_tower import ArcherTower
from .artillery import ArtilleryTower
from .barracks import Barracks
from .base_tower import BaseTower
from .mage_tower import MageTower


_FAMILY_TO_CLASS: dict[str, type[BaseTower]] = {
    "archer": ArcherTower,
    "barracks": Barracks,
    "mage": MageTower,
    "artillery": ArtilleryTower,
}


def build_tower(family: str, x: float, y: float, bus=None) -> BaseTower:
    cls = _FAMILY_TO_CLASS[family]
    tree = TOWER_TREES[family]
    return cls(tree, x, y, bus=bus)


def base_cost(family: str) -> int:
    return TOWER_TREES[family].tiers[0].cost
