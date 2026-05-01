"""Shared Pillow helpers for procedural generators."""
from __future__ import annotations

from PIL import Image, ImageDraw

from td_game.core.constants import TILE_SIZE


def new_canvas(size: int = TILE_SIZE) -> Image.Image:
    return Image.new("RGBA", (size, size), (0, 0, 0, 0))


def circle(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int, fill, outline=None, width: int = 1) -> None:
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill, outline=outline, width=width)


def rect(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, fill, outline=None, width: int = 1) -> None:
    draw.rectangle((x, y, x + w, y + h), fill=fill, outline=outline, width=width)


def drop_shadow(draw: ImageDraw.ImageDraw, cx: int, cy: int, rx: int, ry: int, color=(0, 0, 0, 90)) -> None:
    draw.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=color)
