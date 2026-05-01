"""Status-effect / FX icon generator."""
from __future__ import annotations

from PIL import Image, ImageDraw

from . import palette as P


SIZE = 32


def generate(name: str) -> Image.Image:
    kind = name.split("_", 1)[0]
    if kind == "poison":
        return _aura(P.POISON)
    if kind == "burn":
        return _aura(P.BURN)
    if kind == "slow":
        return _aura(P.SLOW)
    if kind == "stun":
        return _stun()
    if kind == "explosion":
        return _explosion()
    return _aura(P.POISON)


def _aura(color) -> Image.Image:
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((4, 4, SIZE - 4, SIZE - 4), fill=color)
    return img


def _stun() -> Image.Image:
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cy = SIZE // 2
    for angle in range(0, 360, 72):
        import math
        rad = math.radians(angle)
        x = cx + int(12 * math.cos(rad))
        y = cy + int(12 * math.sin(rad))
        d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=P.STUN)
    return img


def _explosion() -> Image.Image:
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cy = size // 2
    d.ellipse((cx - 30, cy - 30, cx + 30, cy + 30), fill=(240, 120, 40, 140))
    d.ellipse((cx - 22, cy - 22, cx + 22, cy + 22), fill=(248, 200, 80, 200))
    d.ellipse((cx - 12, cy - 12, cx + 12, cy + 12), fill=(255, 240, 180, 240))
    return img
