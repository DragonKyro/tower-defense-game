"""Generic sprite-sheet slicer.

For now the project ships only single-frame procedural PNGs, but real
artists typically deliver sheets. This keeps the seam ready.
"""
from __future__ import annotations

from pathlib import Path

import arcade


def slice_sheet(path: Path, frame_width: int, frame_height: int, count: int, margin: int = 0) -> list[arcade.Texture]:
    return arcade.load_spritesheet(
        str(path),
        sprite_width=frame_width,
        sprite_height=frame_height,
        columns=count,
        count=count,
        margin=margin,
    )
