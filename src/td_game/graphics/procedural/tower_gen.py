"""Tower sprite generator.

Sprite name format: `<family>_<tier>[_frame]`, e.g. 'archer_1', 'mage_3',
'barracks_2_attack_0'. We keep it simple: one static icon per tier for
the framework scaffold; animation frames can be added later.
"""
from __future__ import annotations

from PIL import Image, ImageDraw

from td_game.core.constants import TILE_SIZE

from . import palette as P
from ._util import circle, new_canvas, rect


def generate(name: str) -> Image.Image:
    family, _, rest = name.partition("_")
    tier = int(rest.split("_", 1)[0]) if rest and rest[0].isdigit() else 1
    if family == "archer":
        return _archer(tier)
    if family == "barracks":
        return _barracks(tier)
    if family == "mage":
        return _mage(tier)
    if family == "artillery":
        return _artillery(tier)
    return _archer(tier)


def _base(tier: int) -> tuple[Image.Image, ImageDraw.ImageDraw, int, int]:
    img = new_canvas()
    d = ImageDraw.Draw(img)
    cx = cy = TILE_SIZE // 2
    # Stone platform grows with tier.
    r = 14 + tier * 2
    circle(d, cx, cy + 10, r + 2, fill=(60, 60, 70, 255))
    circle(d, cx, cy + 10, r, fill=(140, 140, 150, 255), outline=P.OUTLINE, width=1)
    return img, d, cx, cy


def _archer(tier: int) -> Image.Image:
    img, d, cx, cy = _base(tier)
    # Wooden tower body
    rect(d, cx - 10, cy - 18, 20, 26, fill=P.ARCHER_LEATHER, outline=P.OUTLINE)
    # Roof (taller with tier)
    top = cy - 18 - (4 + tier * 2)
    d.polygon([(cx - 14, cy - 18), (cx + 14, cy - 18), (cx, top)], fill=P.ARCHER_GREEN, outline=P.OUTLINE)
    # Archer silhouette
    circle(d, cx, cy - 8, 3, fill=(60, 40, 30, 255))
    return img


def _barracks(tier: int) -> Image.Image:
    img, d, cx, cy = _base(tier)
    rect(d, cx - 16, cy - 12, 32, 24, fill=P.KNIGHT_STEEL, outline=P.OUTLINE)
    # Banner
    rect(d, cx - 2, cy - 22, 4, 10, fill=P.KNIGHT_BLUE)
    if tier >= 2:
        rect(d, cx - 10, cy - 8, 20, 6, fill=P.KNIGHT_BLUE)
    if tier >= 3:
        rect(d, cx - 8, cy - 2, 16, 6, fill=P.KNIGHT_GOLD)
    return img


def _mage(tier: int) -> Image.Image:
    img, d, cx, cy = _base(tier)
    # Tower
    rect(d, cx - 9, cy - 20, 18, 28, fill=P.MAGE_ROBE, outline=P.OUTLINE)
    # Cap
    d.polygon([(cx - 12, cy - 20), (cx + 12, cy - 20), (cx, cy - 20 - (6 + tier * 2))], fill=P.MAGE_PURPLE, outline=P.OUTLINE)
    # Window glow
    circle(d, cx, cy - 10, 3, fill=(240, 220, 140, 255))
    return img


def _artillery(tier: int) -> Image.Image:
    img, d, cx, cy = _base(tier)
    # Base plate
    rect(d, cx - 16, cy - 8, 32, 14, fill=P.ARTILLERY_IRON, outline=P.OUTLINE)
    # Barrel
    rect(d, cx - 4, cy - 20 - tier * 2, 8, 16 + tier * 2, fill=P.ARTILLERY_BRONZE, outline=P.OUTLINE)
    # Wheel
    circle(d, cx - 14, cy + 6, 4, fill=P.OUTLINE)
    circle(d, cx + 14, cy + 6, 4, fill=P.OUTLINE)
    return img
