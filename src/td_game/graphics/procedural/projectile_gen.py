"""Projectile sprite generator with gradient shading + glow."""
from __future__ import annotations

from PIL import Image, ImageDraw

from . import palette as P
from ._util import finalize, new_canvas, shaded_circle, soft_shadow, glow


SIZE = 28
METEOR_SIZE = 56


def generate(name: str) -> Image.Image:
    kind = name.split("_", 1)[0]
    if kind == "arrow":
        return _arrow()
    if kind == "cannonball":
        return _cannonball()
    if kind == "bolt":
        return _magic_bolt()
    if kind == "meteor":
        return _meteor()
    return _arrow()


def _arrow() -> Image.Image:
    img, d, s = new_canvas(SIZE)
    cy = SIZE // 2
    # Shaft with gradient from base to tip
    d.rectangle(((2) * s, (cy - 1) * s, (SIZE - 8) * s, (cy + 1) * s), fill=P.ARROW)
    d.line(((2) * s, (cy - 1) * s, (SIZE - 8) * s, (cy - 1) * s), fill=(240, 220, 180, 255), width=1 * s)
    d.line(((2) * s, (cy + 1) * s, (SIZE - 8) * s, (cy + 1) * s), fill=(160, 130, 80, 255), width=1 * s)
    # Tip (metallic triangle)
    pts = [((SIZE - 8) * s, (cy - 3) * s), ((SIZE - 1) * s, cy * s), ((SIZE - 8) * s, (cy + 3) * s)]
    d.polygon(pts, fill=P.ARROW_TIP)
    d.polygon([((SIZE - 8) * s, (cy - 3) * s), ((SIZE - 3) * s, cy * s), ((SIZE - 8) * s, (cy - 1) * s)],
              fill=(255, 255, 255, 255))
    # Fletching
    d.polygon([(2 * s, (cy - 2) * s), (6 * s, cy * s), (2 * s, (cy + 2) * s)], fill=P.BANNER_RED)
    d.polygon([(2 * s, (cy - 1) * s), (5 * s, cy * s), (2 * s, (cy + 1) * s)], fill=(255, 255, 255, 255))
    return finalize(img, SIZE)


def _cannonball() -> Image.Image:
    img, d, s = new_canvas(SIZE)
    cx = cy = SIZE // 2
    soft_shadow(img, cx, cy + 6, 8, 2, scale=s, alpha=120)
    shaded_circle(d, cx, cy, 8, P.CANNONBALL, scale=s,
                  shadow_tint=(20, 20, 24, 255), highlight_tint=P.CANNONBALL_HI)
    # Specular highlight
    d.ellipse(((cx - 4) * s, (cy - 5) * s, (cx - 2) * s, (cy - 3) * s), fill=(220, 220, 230, 255))
    return finalize(img, SIZE)


def _magic_bolt() -> Image.Image:
    img, d, s = new_canvas(SIZE)
    cx = cy = SIZE // 2
    glow(img, cx, cy, 10, P.MAGIC_BOLT, scale=s, alpha=180)
    shaded_circle(d, cx, cy, 6, P.MAGIC_BOLT, scale=s,
                  shadow_tint=(80, 40, 140, 255), highlight_tint=P.MAGIC_BOLT_CORE)
    d.ellipse(((cx - 2) * s, (cy - 3) * s, (cx + 2) * s, (cy + 1) * s), fill=P.MAGIC_BOLT_CORE)
    # Sparkles
    for (sx, sy) in [(-8, -4), (7, 5), (-6, 6)]:
        d.ellipse(((cx + sx) * s, (cy + sy) * s, (cx + sx + 1) * s, (cy + sy + 1) * s),
                  fill=(255, 255, 255, 200))
    return finalize(img, SIZE)


def _meteor() -> Image.Image:
    img, d, s = new_canvas(METEOR_SIZE)
    cx = cy = METEOR_SIZE // 2
    glow(img, cx, cy, 22, P.METEOR_RING, scale=s, alpha=180)
    glow(img, cx, cy, 14, P.METEOR_CORE, scale=s, alpha=220)
    shaded_circle(d, cx, cy, 12, P.METEOR_CORE, scale=s,
                  shadow_tint=(160, 60, 20, 255), highlight_tint=(255, 240, 180, 255))
    shaded_circle(d, cx - 2, cy - 2, 5, (255, 240, 200, 255), scale=s,
                  shadow_tint=(220, 180, 100, 255), highlight_tint=(255, 255, 255, 255))
    # Trailing fire tail
    for i, (tx, ty, r) in enumerate([(-10, -10, 3), (-16, -14, 2), (-20, -16, 1)]):
        d.ellipse(((cx + tx - r) * s, (cy + ty - r) * s, (cx + tx + r) * s, (cy + ty + r) * s),
                  fill=(*P.METEOR_RING[:3], 200 - i * 50))
    return finalize(img, METEOR_SIZE)
