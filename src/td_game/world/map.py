"""Map: grid of Tiles + paths + build spots + decor + metadata.

A Map is pure data. It does not own sprites, entities, or game state.
Scenes consume a Map to initialize a gameplay session.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from td_game.core.constants import GRID_COLS, GRID_ROWS, TILE_SIZE

from .path import Path, PathRegistry
from .tile import Tile, TileType


@dataclass(frozen=True)
class BuildSpot:
    """An anchored position where towers can be built.

    `kind` lets levels restrict certain spots to specific tower families
    (e.g., a forest spot that only accepts archer/ranger towers). Empty
    set means 'any'.
    """
    x: float
    y: float
    allowed_families: frozenset[str] = frozenset()


@dataclass(frozen=True)
class DecorItem:
    """A purely decorative sprite placed on the map.

    `sprite` is a key in the 'decor' resource category (e.g. 'tree_oak').
    `scale` optionally overrides the rendered size. Decor is non-interactive.
    """
    x: float
    y: float
    sprite: str
    scale: float = 1.0


@dataclass
class Map:
    name: str
    grid: list[list[Tile]]  # [row][col] — row 0 is the top
    paths: list[Path] = field(default_factory=list)
    build_spots: list[BuildSpot] = field(default_factory=list)
    spawn_points: dict[str, tuple[float, float]] = field(default_factory=dict)  # path_id -> (x,y)
    exit_points: dict[str, tuple[float, float]] = field(default_factory=dict)
    decor: list[DecorItem] = field(default_factory=list)
    background: str | None = None  # optional pre-rendered background sprite name

    def in_bounds(self, col: int, row: int) -> bool:
        return 0 <= row < len(self.grid) and 0 <= col < len(self.grid[0])

    def tile_at_pixel(self, x: float, y: float) -> Tile | None:
        col = int(x // TILE_SIZE)
        row = int(y // TILE_SIZE)
        if not self.in_bounds(col, row):
            return None
        return self.grid[row][col]

    def path_registry(self) -> PathRegistry:
        return PathRegistry(self.paths)

    @classmethod
    def uniform(cls, name: str, tile_type: TileType = TileType.GRASS) -> "Map":
        grid = [[Tile(tile_type) for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        return cls(name=name, grid=grid)
