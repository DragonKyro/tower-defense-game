"""Map tile types."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class TileType(Enum):
    GRASS = auto()
    PATH = auto()
    WATER = auto()
    CLIFF = auto()
    BUILD_GROUND = auto()  # towers that need flat ground (archer/mage/artillery)
    BUILD_FOREST = auto()  # variant build spot (tree stump style)
    DECOR = auto()


WALKABLE_FOR_ENEMIES = {TileType.PATH}
BLOCKED = {TileType.WATER, TileType.CLIFF}


@dataclass(frozen=True)
class Tile:
    type: TileType
    sprite: str = ""  # override sprite name, else derived from type

    def sprite_name(self) -> str:
        if self.sprite:
            return self.sprite
        return {
            TileType.GRASS: "grass_0",
            TileType.PATH: "path_0",
            TileType.WATER: "water_0",
            TileType.CLIFF: "cliff_0",
            TileType.BUILD_GROUND: "grass_0",
            TileType.BUILD_FOREST: "grass_0",
            TileType.DECOR: "grass_0",
        }[self.type]
