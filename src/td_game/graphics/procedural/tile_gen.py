"""Tile generators: grass, path, water, cliff, build spot.

Tiles are rendered at target size (no supersample) to keep seams clean
when they tile side-by-side.
"""
from __future__ import annotations

import random

from PIL import Image, ImageDraw

from td_game.core.constants import TILE_SIZE

from . import palette as P
from ._util import soft_shadow, glow


def generate(name: str) -> Image.Image:
    if name.startswith("meadow_bg"):
        return _meadow_background(name)
    if name.startswith("grass"):
        return _grass(name)
    if name.startswith("path"):
        return _path(name)
    if name.startswith("water"):
        return _water(name)
    if name.startswith("cliff"):
        return _cliff(name)
    if name.startswith("build_spot"):
        return _build_spot(name)
    return _grass(name)


def _meadow_background(name: str) -> Image.Image:
    """A big seamless grass meadow for the whole play area.

    Generated once and cached. Avoids the tile-grid seams you get from
    rendering individual 64x64 grass tiles.
    """
    from td_game.core.constants import GRID_COLS, GRID_ROWS

    w = GRID_COLS * TILE_SIZE
    h = GRID_ROWS * TILE_SIZE
    img = Image.new("RGBA", (w, h), P.GRASS)
    d = ImageDraw.Draw(img)
    rng = random.Random(2027)

    # Subtle vertical gradient (top darker, bottom lighter) via alpha strips.
    for y in range(0, h, 4):
        t = y / h
        shade = int(26 * (0.5 - t) * 2)
        if shade > 0:
            color = (*(max(0, c - shade) for c in P.GRASS[:3]), 70)
        else:
            s = -shade
            color = (*(min(255, c + s) for c in P.GRASS[:3]), 70)
        d.rectangle((0, y, w, y + 4), fill=color)

    # Dapple patches (light + dark blobs).
    for _ in range(220):
        x = rng.randint(0, w - 1)
        y = rng.randint(0, h - 1)
        r = rng.randint(10, 38)
        tone = rng.choice((P.GRASS_LIGHT, P.GRASS_DARK))
        alpha = rng.randint(30, 70)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(*tone[:3], alpha))

    # Tiny grass blade tufts.
    for _ in range(1100):
        x = rng.randint(0, w - 1)
        y = rng.randint(0, h - 1)
        length = rng.randint(2, 4)
        tone = rng.choice((P.GRASS_DARK, P.GRASS_LIGHT, P.GRASS_LIGHT))
        d.line((x, y, x, y - length), fill=tone)

    # Soft outer vignette so screen edges feel hand-painted.
    for i in range(30):
        alpha = int(90 * (1 - i / 30) ** 2)
        d.rectangle((i, i, w - i, h - i), outline=(22, 34, 22, alpha), width=1)

    return img


def _grass(name: str) -> Image.Image:
    img = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), P.GRASS)
    d = ImageDraw.Draw(img)
    rng = random.Random(hash(name) & 0xFFFF)
    # Dappled shading — cluster of lighter patches.
    for _ in range(6):
        x = rng.randint(0, TILE_SIZE - 1)
        y = rng.randint(0, TILE_SIZE - 1)
        r = rng.randint(3, 6)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(*P.GRASS_LIGHT[:3], 90))
    # Darker speckles.
    for _ in range(14):
        x = rng.randint(0, TILE_SIZE - 1)
        y = rng.randint(0, TILE_SIZE - 1)
        d.point((x, y), fill=P.GRASS_DARK)
    # Individual grass blades
    for _ in range(8):
        x = rng.randint(2, TILE_SIZE - 3)
        y = rng.randint(4, TILE_SIZE - 4)
        d.line((x, y, x, y - 3), fill=P.GRASS_LIGHT)
        d.line((x + 1, y, x + 1, y - 2), fill=P.GRASS_DARK)
    return img


def _path(name: str) -> Image.Image:
    img = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), P.PATH)
    d = ImageDraw.Draw(img)
    rng = random.Random(hash(name) & 0xFFFF)
    # Darker edge hint.
    d.rectangle((0, 0, TILE_SIZE, 2), fill=P.PATH_DARK)
    d.rectangle((0, TILE_SIZE - 2, TILE_SIZE, TILE_SIZE), fill=P.PATH_DARK)
    # Variegated dirt tones.
    for _ in range(10):
        x = rng.randint(0, TILE_SIZE - 1)
        y = rng.randint(0, TILE_SIZE - 1)
        r = rng.randint(2, 5)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(*P.PATH_LIGHT[:3], 70))
    for _ in range(18):
        x = rng.randint(0, TILE_SIZE - 1)
        y = rng.randint(0, TILE_SIZE - 1)
        d.point((x, y), fill=P.PATH_DARK)
    # Pebbles
    for _ in range(3):
        x = rng.randint(4, TILE_SIZE - 6)
        y = rng.randint(4, TILE_SIZE - 6)
        r = rng.randint(1, 2)
        d.ellipse((x - r, y - r, x + r, y + r), fill=P.STONE)
        d.point((x - 1, y - 1), fill=P.STONE_LIGHT)
    return img


def _water(name: str) -> Image.Image:
    img = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), P.WATER)
    d = ImageDraw.Draw(img)
    for y in range(4, TILE_SIZE, 10):
        d.line((2, y, TILE_SIZE - 2, y), fill=(*P.WATER_LIGHT[:3], 160), width=2)
        d.line((6, y + 2, TILE_SIZE - 10, y + 2), fill=(*P.WATER_LIGHT[:3], 80), width=1)
    return img


def _cliff(name: str) -> Image.Image:
    img = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), P.CLIFF)
    d = ImageDraw.Draw(img)
    d.line((0, 0, TILE_SIZE, 0), fill=(80, 72, 64, 255), width=2)
    for i in range(3):
        d.line((0, 20 + i * 14, TILE_SIZE, 22 + i * 14), fill=(80, 72, 64, 255), width=1)
    return img


def _build_spot(name: str) -> Image.Image:
    img = Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cy = TILE_SIZE // 2
    r = TILE_SIZE // 2 - 4
    # Outer dark ring
    d.ellipse((cx - r - 1, cy - r - 1, cx + r + 1, cy + r + 1), fill=P.BUILD_SPOT_RING)
    # Stone disk
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=P.STONE)
    d.ellipse((cx - r + 2, cy - r + 2, cx + r - 2, cy + r - 2), fill=(*P.STONE_LIGHT[:3], 180))
    # Brick pattern
    for angle_deg in (0, 60, 120, 180, 240, 300):
        import math
        a = math.radians(angle_deg)
        x1 = int(cx + (r - 2) * 0.4 * math.cos(a))
        y1 = int(cy + (r - 2) * 0.4 * math.sin(a))
        x2 = int(cx + (r - 2) * math.cos(a))
        y2 = int(cy + (r - 2) * math.sin(a))
        d.line((x1, y1, x2, y2), fill=P.STONE_DARK, width=1)
    # Pulsing "+" to indicate buildable
    d.line((cx - 8, cy, cx + 8, cy), fill=P.KNIGHT_GOLD, width=3)
    d.line((cx, cy - 8, cx, cy + 8), fill=P.KNIGHT_GOLD, width=3)
    d.line((cx - 8, cy, cx + 8, cy), fill=(255, 240, 180, 255), width=1)
    d.line((cx, cy - 8, cx, cy + 8), fill=(255, 240, 180, 255), width=1)
    return img
