"""Enemy sprite generator (static placeholder)."""
from __future__ import annotations

from PIL import Image, ImageDraw

from td_game.core.constants import TILE_SIZE

from . import palette as P
from ._util import circle, new_canvas, rect


def generate(name: str) -> Image.Image:
    kind = name.split("_", 1)[0]
    if kind == "orc":
        return _humanoid(P.ORC_SKIN, P.ORC_DARK)
    if kind == "goblin":
        return _humanoid(P.GOBLIN_SKIN, P.ORC_DARK, size=0.8)
    if kind == "troll":
        return _humanoid(P.TROLL_SKIN, P.ORC_DARK, size=1.15)
    if kind == "wraith":
        return _wraith()
    if kind == "dragon":
        return _dragon()
    return _humanoid(P.ORC_SKIN, P.ORC_DARK)


def _humanoid(skin, dark, size: float = 1.0) -> Image.Image:
    img = new_canvas()
    d = ImageDraw.Draw(img)
    cx = cy = TILE_SIZE // 2
    body_w = int(18 * size)
    body_h = int(20 * size)
    head_r = int(8 * size)
    # Shadow
    d.ellipse((cx - 12, cy + 14, cx + 12, cy + 20), fill=P.SHADOW)
    # Body
    rect(d, cx - body_w // 2, cy - body_h // 2, body_w, body_h, fill=dark, outline=P.OUTLINE)
    # Head
    circle(d, cx, cy - body_h // 2 - head_r + 2, head_r, fill=skin, outline=P.OUTLINE)
    # Eyes
    d.point((cx - 2, cy - body_h // 2 - head_r + 2), fill=(240, 40, 40))
    d.point((cx + 2, cy - body_h // 2 - head_r + 2), fill=(240, 40, 40))
    return img


def _wraith() -> Image.Image:
    img = new_canvas()
    d = ImageDraw.Draw(img)
    cx = cy = TILE_SIZE // 2
    d.ellipse((cx - 12, cy + 14, cx + 12, cy + 20), fill=P.SHADOW)
    # Tattered robe
    d.polygon(
        [(cx - 14, cy + 16), (cx - 10, cy - 14), (cx, cy - 20), (cx + 10, cy - 14), (cx + 14, cy + 16)],
        fill=P.WRAITH,
        outline=P.OUTLINE,
    )
    # Glowing eyes
    d.point((cx - 3, cy - 8), fill=(180, 220, 255))
    d.point((cx + 3, cy - 8), fill=(180, 220, 255))
    return img


def _dragon() -> Image.Image:
    img = new_canvas()
    d = ImageDraw.Draw(img)
    cx = cy = TILE_SIZE // 2
    # Body
    d.ellipse((cx - 18, cy - 8, cx + 18, cy + 14), fill=P.DRAGON, outline=P.OUTLINE)
    # Wings
    d.polygon([(cx - 18, cy), (cx - 28, cy - 10), (cx - 14, cy - 4)], fill=(140, 40, 40, 255), outline=P.OUTLINE)
    d.polygon([(cx + 18, cy), (cx + 28, cy - 10), (cx + 14, cy - 4)], fill=(140, 40, 40, 255), outline=P.OUTLINE)
    # Head
    circle(d, cx, cy - 14, 7, fill=P.DRAGON, outline=P.OUTLINE)
    d.point((cx - 2, cy - 15), fill=(255, 240, 80))
    d.point((cx + 2, cy - 15), fill=(255, 240, 80))
    return img
