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
    if kind == "hit":
        return _hit_flash()
    if kind == "slash":
        return _slash()
    return _aura_glow(P.POISON)


def _hit_flash() -> Image.Image:
    """Starburst-shaped impact flash, played briefly on every melee hit."""
    img, d, s = new_canvas(SIZE)
    cx = cy = SIZE // 2
    glow(img, cx, cy, 10, (255, 240, 160, 255), scale=s, alpha=220)
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        length = 14 if angle % 90 == 0 else 9
        ex = cx + int(length * math.cos(rad))
        ey = cy + int(length * math.sin(rad))
        d.line((cx * s, cy * s, ex * s, ey * s), fill=(255, 248, 200, 230), width=2 * s)
    shaded_circle(d, cx, cy, 4, (255, 252, 220, 255), scale=s,
                  shadow_tint=(220, 180, 100, 255), highlight_tint=(255, 255, 255, 255))
    return finalize(img, SIZE)


def _slash() -> Image.Image:
    """Quick diagonal slash arc, laid over a unit during a swing."""
    img, d, s = new_canvas(SIZE)
    cx = cy = SIZE // 2
    # Arc via a thick curved line (approximated with segments).
    for i, t in enumerate((0.0, 0.25, 0.5, 0.75, 1.0)):
        alpha = int(255 * (1.0 - t * 0.6))
        ang = math.radians(-40 + t * 90)
        r = 14
        x1 = cx + math.cos(ang) * r
        y1 = cy + math.sin(ang) * r
        ang2 = math.radians(-40 + (t + 0.2) * 90)
        x2 = cx + math.cos(ang2) * r
        y2 = cy + math.sin(ang2) * r
        d.line((x1 * s, y1 * s, x2 * s, y2 * s), fill=(255, 250, 210, alpha), width=3 * s)
    return finalize(img, SIZE)


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
