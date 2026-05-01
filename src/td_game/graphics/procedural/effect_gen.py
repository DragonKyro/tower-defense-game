"""FX / status overlay generator with glow + shaded cores."""
from __future__ import annotations

import math

from PIL import Image, ImageDraw

from . import palette as P
from ._util import finalize, new_canvas, glow, shaded_circle


SIZE = 40
BIG = 80


def generate(name: str) -> Image.Image:
    parts = name.split("_")
    kind = parts[0]
    # Most effects have a trailing "_<frame>"; a few are multi-frame.
    frame = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
    if kind == "poison":
        return _aura_glow(P.POISON)
    if kind == "burn":
        return _aura_glow(P.BURN)
    if kind == "slow":
        return _aura_glow(P.SLOW)
    if kind == "stun":
        return _stun()
    if kind == "explosion":
        return _explosion(frame)
    if kind == "debris":
        return _debris()
    if kind == "smoke":
        return _smoke_puff(frame)
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


def _explosion(frame: int = 0) -> Image.Image:
    """5-frame evolving blast.

    Frame 0: bright white flash (ignition).
    Frame 1: peak fireball + expanding shockwave ring + sparks.
    Frame 2: wider, redder cloud + long debris rays.
    Frame 3: dissipating smoke clouds shifted off-center.
    Frame 4: last faint wisps.
    """
    img, d, s = new_canvas(BIG)
    cx = cy = BIG // 2
    frame = max(0, min(4, frame))

    if frame == 0:
        # Ignition flash.
        glow(img, cx, cy, 14, (255, 250, 220, 255), scale=s, alpha=240)
        shaded_circle(d, cx, cy, 8, (255, 255, 240, 255), scale=s,
                      shadow_tint=(250, 220, 150, 255), highlight_tint=(255, 255, 255, 255))
        shaded_circle(d, cx, cy, 4, (255, 255, 255, 255), scale=s,
                      shadow_tint=(250, 240, 200, 255), highlight_tint=(255, 255, 255, 255))
    elif frame == 1:
        # Peak fireball + shockwave ring.
        glow(img, cx, cy, 30, (255, 160, 60, 255), scale=s, alpha=220)
        glow(img, cx, cy, 22, (255, 210, 110, 255), scale=s, alpha=230)
        shaded_circle(d, cx, cy, 18, (255, 200, 90, 255), scale=s,
                      shadow_tint=(200, 90, 40, 255), highlight_tint=(255, 255, 210, 255))
        shaded_circle(d, cx, cy, 10, (255, 240, 180, 255), scale=s,
                      shadow_tint=(240, 180, 100, 255), highlight_tint=(255, 255, 255, 255))
        # Shockwave ring, expanding.
        d.ellipse(((cx - 28) * s, (cy - 28) * s, (cx + 28) * s, (cy + 28) * s),
                  outline=(255, 230, 170, 230), width=3 * s)
        # Sparks shooting out 12 directions.
        for deg in range(0, 360, 30):
            rad = math.radians(deg)
            r1 = 16
            r2 = 30
            x1 = cx + r1 * math.cos(rad)
            y1 = cy + r1 * math.sin(rad)
            x2 = cx + r2 * math.cos(rad)
            y2 = cy + r2 * math.sin(rad)
            d.line((x1 * s, y1 * s, x2 * s, y2 * s), fill=(255, 230, 150, 230), width=2 * s)
    elif frame == 2:
        # Wider cloud, redder + longer rays + outer shockwave fading.
        glow(img, cx, cy, 36, (200, 110, 60, 255), scale=s, alpha=200)
        glow(img, cx, cy, 28, (230, 160, 80, 255), scale=s, alpha=180)
        shaded_circle(d, cx, cy, 22, (200, 130, 70, 255), scale=s,
                      shadow_tint=(120, 60, 30, 255), highlight_tint=(240, 180, 110, 255))
        shaded_circle(d, cx - 4, cy + 2, 12, (240, 180, 110, 255), scale=s,
                      shadow_tint=(200, 120, 70, 255), highlight_tint=(255, 220, 160, 255))
        # Outer faded shockwave ring.
        d.ellipse(((cx - 36) * s, (cy - 36) * s, (cx + 36) * s, (cy + 36) * s),
                  outline=(255, 200, 140, 120), width=2 * s)
        # Long debris streaks (thicker, varied length).
        for i, deg in enumerate((15, 60, 105, 150, 195, 240, 285, 330)):
            rad = math.radians(deg)
            r1 = 14
            r2 = 36 + (i % 3) * 2
            x1 = cx + r1 * math.cos(rad)
            y1 = cy + r1 * math.sin(rad)
            x2 = cx + r2 * math.cos(rad)
            y2 = cy + r2 * math.sin(rad)
            d.line((x1 * s, y1 * s, x2 * s, y2 * s), fill=(255, 200, 120, 210), width=3 * s)
    elif frame == 3:
        # Dissipating smoke: two puffs offset up-and-away from center.
        glow(img, cx - 4, cy + 2, 26, (160, 130, 110, 255), scale=s, alpha=150)
        glow(img, cx + 8, cy - 4, 22, (170, 140, 120, 255), scale=s, alpha=130)
        shaded_circle(d, cx - 6, cy + 4, 14, (170, 150, 130, 255), scale=s,
                      shadow_tint=(100, 90, 80, 255), highlight_tint=(210, 190, 170, 255))
        shaded_circle(d, cx + 8, cy - 6, 10, (170, 150, 130, 255), scale=s,
                      shadow_tint=(100, 90, 80, 255), highlight_tint=(210, 190, 170, 255))
    else:  # frame 4
        # Last faint wisps drifting up.
        glow(img, cx - 10, cy - 6, 14, (170, 150, 130, 255), scale=s, alpha=90)
        glow(img, cx + 10, cy + 4, 10, (160, 140, 120, 255), scale=s, alpha=70)

    return finalize(img, BIG)


def _debris() -> Image.Image:
    """Tiny irregular chunk used as a flying particle after an explosion."""
    size = 12
    img, d, s = new_canvas(size)
    cx = cy = size // 2
    # Small irregular polygon with highlight dot.
    d.polygon([
        ((cx - 3) * s, (cy - 2) * s),
        ((cx + 2) * s, (cy - 3) * s),
        ((cx + 3) * s, (cy + 1) * s),
        ((cx + 1) * s, (cy + 3) * s),
        ((cx - 3) * s, (cy + 2) * s),
    ], fill=(80, 60, 40, 255))
    d.point(((cx - 1) * s, (cy - 1) * s), fill=(180, 150, 110, 255))
    return finalize(img, size)


def _smoke_puff(frame: int = 0) -> Image.Image:
    """Small smoke puff — used as trailing/residual FX."""
    size = 24
    img, d, s = new_canvas(size)
    cx = cy = size // 2
    alpha = (220, 170, 110, 60)[min(frame, 3)]
    glow(img, cx, cy, 8, (180, 160, 140, 255), scale=s, alpha=alpha)
    shaded_circle(d, cx, cy, 5, (180, 160, 140, 255), scale=s,
                  shadow_tint=(110, 100, 90, 255), highlight_tint=(220, 210, 200, 255))
    return finalize(img, size)
