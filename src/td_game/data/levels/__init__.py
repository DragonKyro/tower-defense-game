"""Level registry.

To add a new level:
  1. Create `level_XX.py` in this folder and export a `LevelDef`.
  2. Import it here and add it to `LEVELS`.
"""
from __future__ import annotations

from td_game.world.level import LevelDef

from .level_01 import LEVEL_01


LEVELS: dict[str, LevelDef] = {
    LEVEL_01.id: LEVEL_01,
}
