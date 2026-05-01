"""Projectile sprite generator."""
from __future__ import annotations

from PIL import Image, ImageDraw

from . import palette as P


SIZE = 24  # projectiles are smaller than tiles


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
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.line((2, SIZE // 2, SIZE - 6, SIZE // 2), fill=P.ARROW, width=2)
    d.polygon([(SIZE - 6, SIZE // 2 - 3), (SIZE - 6, SIZE // 2 + 3), (SIZE - 1, SIZE // 2)], fill=(220, 220, 220, 255))
    d.line((2, SIZE // 2 - 2, 5, SIZE // 2 + 2), fill=(240, 240, 240, 255), width=1)
    return img


def _cannonball() -> Image.Image:
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cy = SIZE // 2
    d.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill=P.CANNONBALL, outline=P.OUTLINE)
    d.ellipse((cx - 3, cy - 3, cx - 1, cy - 1), fill=(200, 200, 200, 255))  # highlight
    return img


def _magic_bolt() -> Image.Image:
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cy = SIZE // 2
    d.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=P.MAGIC_BOLT)
    d.ellipse((cx - 3, cy - 3, cx + 3, cy + 3), fill=(240, 220, 255, 255))
    return img


def _meteor() -> Image.Image:
    size = 48
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cy = size // 2
    d.ellipse((cx - 18, cy - 18, cx + 18, cy + 18), fill=P.METEOR_RING)
    d.ellipse((cx - 12, cy - 12, cx + 12, cy + 12), fill=P.METEOR_CORE)
    d.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=(255, 240, 180, 255))
    return img
