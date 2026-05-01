"""Hero sprite generator (static placeholder)."""
from __future__ import annotations

from PIL import Image, ImageDraw

from td_game.core.constants import TILE_SIZE

from . import palette as P
from ._util import circle, new_canvas, rect


def generate(name: str) -> Image.Image:
    kind = name.split("_", 1)[0]
    if kind == "knight":
        return _knight()
    if kind == "ranger":
        return _ranger()
    return _knight()


def _knight() -> Image.Image:
    img = new_canvas()
    d = ImageDraw.Draw(img)
    cx = cy = TILE_SIZE // 2
    d.ellipse((cx - 12, cy + 14, cx + 12, cy + 20), fill=P.SHADOW)
    rect(d, cx - 9, cy - 8, 18, 22, fill=P.KNIGHT_STEEL, outline=P.OUTLINE)
    rect(d, cx - 3, cy - 8, 6, 22, fill=P.KNIGHT_BLUE)  # tabard
    circle(d, cx, cy - 14, 8, fill=P.KNIGHT_STEEL, outline=P.OUTLINE)  # helmet
    rect(d, cx - 2, cy - 18, 4, 2, fill=P.KNIGHT_GOLD)  # plume base
    # Sword
    rect(d, cx + 11, cy - 6, 2, 18, fill=P.KNIGHT_STEEL, outline=P.OUTLINE)
    rect(d, cx + 8, cy - 8, 8, 3, fill=P.KNIGHT_GOLD, outline=P.OUTLINE)
    return img


def _ranger() -> Image.Image:
    img = new_canvas()
    d = ImageDraw.Draw(img)
    cx = cy = TILE_SIZE // 2
    d.ellipse((cx - 12, cy + 14, cx + 12, cy + 20), fill=P.SHADOW)
    rect(d, cx - 8, cy - 8, 16, 22, fill=P.ARCHER_LEATHER, outline=P.OUTLINE)
    # Hooded head
    d.polygon([(cx - 10, cy - 6), (cx - 8, cy - 18), (cx + 8, cy - 18), (cx + 10, cy - 6)],
              fill=P.ARCHER_GREEN, outline=P.OUTLINE)
    circle(d, cx, cy - 12, 5, fill=(220, 190, 150, 255))  # face
    # Bow
    d.arc((cx + 10, cy - 12, cx + 22, cy + 12), start=270, end=90, fill=P.ARCHER_LEATHER, width=2)
    d.line((cx + 22, cy - 12, cx + 22, cy + 12), fill=(220, 220, 220, 255), width=1)
    return img
