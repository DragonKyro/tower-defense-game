"""Re-exports for level authors.

A level module imports from this one instead of reaching across the
project, so the public surface for authoring levels is tight.
"""
from __future__ import annotations

from td_game.world.level import LevelDef
from td_game.world.map import BuildSpot, DecorItem, Map
from td_game.world.path import Path, Waypoint
from td_game.world.tile import Tile, TileType
from td_game.world.wave import SpawnOrder, Wave

__all__ = [
    "LevelDef",
    "Map",
    "BuildSpot",
    "DecorItem",
    "Path",
    "Waypoint",
    "Tile",
    "TileType",
    "Wave",
    "SpawnOrder",
]
