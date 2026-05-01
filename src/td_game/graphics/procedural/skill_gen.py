"""Skill icon generator (square icons with a dark border + shaded motif)."""
from __future__ import annotations

import math

from PIL import Image, ImageDraw

from . import palette as P
from ._util import finalize, glow, new_canvas, shaded_circle


ICON_SIZE = 48


def generate(name: str) -> Image.Image:
    kind = name.split("_", 1)[0]
    if kind == "meteor":
        return _meteor()
    if kind == "reinforcements":
        return _reinforcements()
    return _meteor()


def _frame(img: Image.Image, d: ImageDraw.ImageDraw, s: int, accent) -> None:
    """Rounded dark frame with an accent inset — shared across all icons."""
    # Outer shadow
    d.rounded_rectangle((2 * s, 2 * s, (ICON_SIZE - 2) * s, (ICON_SIZE - 2) * s),
                        radius=6 * s, fill=(20, 18, 22, 255))
    # Inner background
    d.rounded_rectangle((4 * s, 4 * s, (ICON_SIZE - 4) * s, (ICON_SIZE - 4) * s),
                        radius=5 * s, fill=(46, 44, 58, 255))
    # Inner accent ring
    d.rounded_rectangle((5 * s, 5 * s, (ICON_SIZE - 5) * s, (ICON_SIZE - 5) * s),
                        radius=4 * s, outline=accent, width=1 * s)


def _meteor() -> Image.Image:
    img, d, s = new_canvas(ICON_SIZE)
    _frame(img, d, s, P.KNIGHT_GOLD_DARK)
    cx = cy = ICON_SIZE // 2
    # Fiery glow aura
    glow(img, cx, cy + 2, 14, (255, 150, 60, 255), scale=s, alpha=180)
    # Meteor body
    shaded_circle(d, cx, cy + 2, 9, (255, 140, 60, 255), scale=s,
                  shadow_tint=(170, 60, 30, 255), highlight_tint=(255, 240, 180, 255))
    # Hot core
    shaded_circle(d, cx - 2, cy, 3, (255, 240, 200, 255), scale=s,
                  shadow_tint=(240, 180, 90, 255), highlight_tint=(255, 255, 255, 255))
    # Streaks trailing up-left
    for (sx, sy, w) in [(-10, -8, 2), (-14, -11, 2), (-17, -13, 1)]:
        d.line(((cx + sx - w) * s, (cy + sy) * s, (cx + sx + w) * s, (cy + sy) * s),
               fill=(*P.METEOR_RING[:3], 230), width=2 * s)
    return finalize(img, ICON_SIZE)


def _reinforcements() -> Image.Image:
    img, d, s = new_canvas(ICON_SIZE)
    _frame(img, d, s, (120, 160, 230))
    cx = cy = ICON_SIZE // 2
    # Shield shape behind (blue with gold trim)
    shield = [
        (cx - 14, cy - 10),
        (cx + 14, cy - 10),
        (cx + 14, cy + 4),
        (cx, cy + 16),
        (cx - 14, cy + 4),
    ]
    d.polygon([(p[0] * s, p[1] * s) for p in shield], fill=(36, 60, 130, 255))
    # Gold trim (inset polygon).
    trim = [
        (cx - 11, cy - 7),
        (cx + 11, cy - 7),
        (cx + 11, cy + 3),
        (cx, cy + 13),
        (cx - 11, cy + 3),
    ]
    d.polygon([(p[0] * s, p[1] * s) for p in trim], outline=P.KNIGHT_GOLD, width=1 * s)
    # Two crossed swords in front.
    cx0, cy0 = cx, cy - 1
    for sign in (-1, 1):
        # Blade (diagonal rectangle via polygon).
        angle = math.radians(-35 * sign)
        length = 20
        bw = 2
        ex = cx0 + length * math.cos(angle)
        ey = cy0 + length * math.sin(angle)
        nx = -math.sin(angle)
        ny = math.cos(angle)
        pts = [
            (cx0 + nx * bw / 2, cy0 + ny * bw / 2),
            (cx0 - nx * bw / 2, cy0 - ny * bw / 2),
            (ex - nx * bw / 2, ey - ny * bw / 2),
            (ex + nx * bw / 2, ey + ny * bw / 2),
        ]
        d.polygon([(int(p[0]) * s, int(p[1]) * s) for p in pts], fill=P.KNIGHT_STEEL_LIGHT)
        # Guard.
        d.ellipse((int(cx0 - 4) * s, int(cy0 - 2) * s,
                   int(cx0 + 4) * s, int(cy0 + 2) * s), fill=P.KNIGHT_GOLD)
    # Pommel.
    d.ellipse(((cx - 2) * s, (cy0 - 1) * s, (cx + 2) * s, (cy0 + 3) * s), fill=P.KNIGHT_GOLD_DARK)
    return finalize(img, ICON_SIZE)
