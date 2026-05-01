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
    if kind == "shieldbash":
        return _shieldbash()
    if kind == "rally":
        return _rally()
    if kind == "poisonarrow":
        return _poison_arrow()
    if kind == "volley":
        return _volley()
    return _meteor()


def _shieldbash() -> Image.Image:
    img, d, s = new_canvas(ICON_SIZE)
    _frame(img, d, s, P.KNIGHT_STEEL)
    cx = cy = ICON_SIZE // 2
    # Shield
    shield = [
        (cx - 13, cy - 10),
        (cx + 13, cy - 10),
        (cx + 13, cy + 2),
        (cx, cy + 14),
        (cx - 13, cy + 2),
    ]
    d.polygon([(p[0] * s, p[1] * s) for p in shield], fill=P.KNIGHT_BLUE)
    # Gold trim.
    trim = [
        (cx - 10, cy - 7),
        (cx + 10, cy - 7),
        (cx + 10, cy + 1),
        (cx, cy + 11),
        (cx - 10, cy + 1),
    ]
    d.polygon([(p[0] * s, p[1] * s) for p in trim], outline=P.KNIGHT_GOLD, width=1 * s)
    # Impact lines bursting out.
    for angle in range(30, 360, 60):
        rad = math.radians(angle)
        x1 = cx + int(14 * math.cos(rad))
        y1 = cy + int(14 * math.sin(rad))
        x2 = cx + int(20 * math.cos(rad))
        y2 = cy + int(20 * math.sin(rad))
        d.line((x1 * s, y1 * s, x2 * s, y2 * s), fill=(255, 240, 120, 255), width=2 * s)
    glow(img, cx, cy, 12, (255, 240, 180, 255), scale=s, alpha=120)
    return finalize(img, ICON_SIZE)


def _rally() -> Image.Image:
    img, d, s = new_canvas(ICON_SIZE)
    _frame(img, d, s, P.KNIGHT_GOLD)
    cx = cy = ICON_SIZE // 2
    # War horn outline
    horn_pts = [
        (cx - 14, cy + 6),
        (cx - 6, cy - 10),
        (cx + 14, cy - 4),
        (cx + 4, cy + 10),
    ]
    d.polygon([(p[0] * s, p[1] * s) for p in horn_pts], fill=P.KNIGHT_GOLD)
    d.polygon([(p[0] * s, p[1] * s) for p in horn_pts], outline=(80, 60, 20, 255), width=1 * s)
    # Mouthpiece glow (sound waves)
    for r, alpha in ((6, 120), (10, 80), (14, 50)):
        d.arc(((cx + 10 - r) * s, (cy - 4 - r) * s,
               (cx + 10 + r) * s, (cy - 4 + r) * s),
              start=300, end=60, fill=(255, 240, 180, alpha), width=2 * s)
    return finalize(img, ICON_SIZE)


def _poison_arrow() -> Image.Image:
    img, d, s = new_canvas(ICON_SIZE)
    _frame(img, d, s, P.POISON[:3] + (255,))
    cx = cy = ICON_SIZE // 2
    # Glow aura
    glow(img, cx, cy, 14, P.POISON, scale=s, alpha=200)
    # Arrow shaft (diagonal)
    import math as _m
    angle = _m.radians(-30)
    length = 24
    hx = cx - length / 2 * _m.cos(angle)
    hy = cy - length / 2 * _m.sin(angle)
    tx = cx + length / 2 * _m.cos(angle)
    ty = cy + length / 2 * _m.sin(angle)
    d.line((hx * s, hy * s, tx * s, ty * s), fill=P.ARROW, width=2 * s)
    # Tip (triangle)
    nx = -_m.sin(angle)
    ny = _m.cos(angle)
    tip = [
        (tx - _m.cos(angle) * 4 + nx * 3, ty - _m.sin(angle) * 4 + ny * 3),
        (tx - _m.cos(angle) * 4 - nx * 3, ty - _m.sin(angle) * 4 - ny * 3),
        (tx, ty),
    ]
    d.polygon([(int(p[0]) * s, int(p[1]) * s) for p in tip], fill=(200, 240, 140, 255))
    # Fletching
    feath = [
        (hx + _m.cos(angle) * 4 + nx * 3, hy + _m.sin(angle) * 4 + ny * 3),
        (hx + _m.cos(angle) * 4 - nx * 3, hy + _m.sin(angle) * 4 - ny * 3),
        (hx, hy),
    ]
    d.polygon([(int(p[0]) * s, int(p[1]) * s) for p in feath], fill=(92, 168, 72, 255))
    # Poison droplets
    for (dx_, dy_) in [(-4, 6), (2, 9), (-8, 10)]:
        d.ellipse(((cx + dx_ - 2) * s, (cy + dy_ - 2) * s,
                   (cx + dx_ + 2) * s, (cy + dy_ + 2) * s),
                  fill=(120, 220, 100, 230))
    return finalize(img, ICON_SIZE)


def _volley() -> Image.Image:
    img, d, s = new_canvas(ICON_SIZE)
    _frame(img, d, s, P.ARCHER_GREEN)
    cx = cy = ICON_SIZE // 2
    # Five arrows fanning outward, all pointing up.
    import math as _m
    for t in (-2, -1, 0, 1, 2):
        base_x = cx + t * 4
        # Tilt by small angle
        angle = _m.radians(t * 12 - 90)
        length = 22
        bx = base_x - _m.cos(angle) * length / 2
        by = cy - _m.sin(angle) * length / 2
        tx = base_x + _m.cos(angle) * length / 2
        ty = cy + _m.sin(angle) * length / 2
        d.line((bx * s, by * s, tx * s, ty * s), fill=P.ARROW, width=2 * s)
        # Tip
        nx = -_m.sin(angle)
        ny = _m.cos(angle)
        tip = [
            (tx - _m.cos(angle) * 3 + nx * 2, ty - _m.sin(angle) * 3 + ny * 2),
            (tx - _m.cos(angle) * 3 - nx * 2, ty - _m.sin(angle) * 3 - ny * 2),
            (tx, ty),
        ]
        d.polygon([(int(p[0]) * s, int(p[1]) * s) for p in tip], fill=(235, 235, 235, 255))
    return finalize(img, ICON_SIZE)


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
