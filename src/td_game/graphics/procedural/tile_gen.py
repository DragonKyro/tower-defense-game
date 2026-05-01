"""Tile generators: grass, path, water, cliff, build spot."""
from __future__ import annotations

import random

from PIL import Image, ImageDraw

from td_game.core.constants import TILE_SIZE

from . import palette as P
from ._util import circle, new_canvas, rect


def generate(name: str) -> Image.Image:
    """Entry point registered with resources. `name` selects the variant."""
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


def _grass(name: str) -> Image.Image:
    img = new_canvas()
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, TILE_SIZE, TILE_SIZE), fill=P.GRASS)
    rng = random.Random(hash(name) & 0xFFFF)
    for _ in range(10):
        x = rng.randint(0, TILE_SIZE - 1)
        y = rng.randint(0, TILE_SIZE - 1)
        d.point((x, y), fill=P.GRASS_DARK)
    return img


def _path(name: str) -> Image.Image:
    img = new_canvas()
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, TILE_SIZE, TILE_SIZE), fill=P.PATH)
    rng = random.Random(hash(name) & 0xFFFF)
    for _ in range(14):
        x = rng.randint(0, TILE_SIZE - 1)
        y = rng.randint(0, TILE_SIZE - 1)
        d.point((x, y), fill=P.PATH_DARK)
    return img


def _water(name: str) -> Image.Image:
    img = new_canvas()
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, TILE_SIZE, TILE_SIZE), fill=P.WATER)
    for y in range(6, TILE_SIZE, 12):
        d.line((4, y, TILE_SIZE - 4, y), fill=(200, 230, 255, 140), width=1)
    return img


def _cliff(name: str) -> Image.Image:
    img = new_canvas()
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, TILE_SIZE, TILE_SIZE), fill=P.CLIFF)
    d.line((0, 0, TILE_SIZE, TILE_SIZE), fill=(80, 72, 64, 255), width=2)
    return img


def _build_spot(name: str) -> Image.Image:
    img = new_canvas()
    d = ImageDraw.Draw(img)
    # Transparent base so the underlying grass tile shows through.
    cx = cy = TILE_SIZE // 2
    r = TILE_SIZE // 2 - 4
    circle(d, cx, cy, r, fill=P.BUILD_SPOT, outline=P.BUILD_SPOT_RING, width=3)
    # "+" icon
    d.line((cx - 10, cy, cx + 10, cy), fill=P.BUILD_SPOT_RING, width=3)
    d.line((cx, cy - 10, cx, cy + 10), fill=P.BUILD_SPOT_RING, width=3)
    return img
