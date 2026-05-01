"""FX / status overlay generator with glow + shaded cores."""
from __future__ import annotations

import math

from PIL import Image, ImageDraw

from . import palette as P
from ._util import finalize, new_canvas, glow, shaded_circle


SIZE = 40
BIG = 80


def generate(name: str) -> Image.Image:
    kind = name.split("_", 1)[0]
    if kind == "poison":
        return _aura_glow(P.POISON)
    if kind == "burn":
        return _aura_glow(P.BURN)
    if kind == "slow":
        return _aura_glow(P.SLOW)
    if kind == "stun":
        return _stun()
    if kind == "explosion":
        return _explosion()
    return _aura_glow(P.POISON)


def _aura_glow(color) -> Image.Image:
    img, d, s = new_canvas(SIZE)
    cx = cy = SIZE // 2
    glow(img, cx, cy, 14, color, scale=s, alpha=200)
    # Inner core
    d.ellipse(((cx - 6) * s, (cy - 6) * s, (cx + 6) * s, (cy + 6) * s),
              fill=(*color[:3], 180))
    d.ellipse(((cx - 3) * s, (cy - 3) * s, (cx + 3) * s, (cy + 3) * s),
              fill=(255, 255, 255, 180))
    return finalize(img, SIZE)


def _stun() -> Image.Image:
    img, d, s = new_canvas(SIZE)
    cx = cy = SIZE // 2
    glow(img, cx, cy, 10, P.STUN, scale=s, alpha=180)
    for angle in range(0, 360, 60):
        rad = math.radians(angle)
        x = cx + int(12 * math.cos(rad))
        y = cy + int(12 * math.sin(rad))
        d.ellipse(((x - 3) * s, (y - 3) * s, (x + 3) * s, (y + 3) * s),
                  fill=(255, 240, 120, 255))
        d.ellipse(((x - 1) * s, (y - 1) * s, (x + 1) * s, (y + 1) * s),
                  fill=(255, 255, 255, 255))
    return finalize(img, SIZE)


def _explosion() -> Image.Image:
    img, d, s = new_canvas(BIG)
    cx = cy = BIG // 2
    glow(img, cx, cy, 32, (255, 180, 60, 255), scale=s, alpha=220)
    glow(img, cx, cy, 22, (255, 220, 120, 255), scale=s, alpha=230)
    shaded_circle(d, cx, cy, 18, (255, 200, 80, 255), scale=s,
                  shadow_tint=(200, 80, 40, 255), highlight_tint=(255, 255, 200, 255))
    shaded_circle(d, cx, cy, 10, (255, 240, 180, 255), scale=s,
                  shadow_tint=(240, 180, 100, 255), highlight_tint=(255, 255, 255, 255))
    # Spark streaks
    for angle in (30, 90, 150, 210, 270, 330):
        rad = math.radians(angle)
        ex = cx + int(28 * math.cos(rad))
        ey = cy + int(28 * math.sin(rad))
        d.line((cx * s, cy * s, ex * s, ey * s), fill=(255, 230, 140, 200), width=2 * s)
    return finalize(img, BIG)
