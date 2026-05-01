"""Background decor: trees, rocks, bushes, flowers, banners, stones, castle.

Sprite name format: '<kind>[_<variant>]'. Examples: 'tree_oak', 'tree_pine',
'rock_small', 'bush_0', 'flower_pink', 'banner_red', 'castle_keep'.
"""
from __future__ import annotations

import math
import random

from PIL import Image, ImageDraw

from td_game.core.constants import TILE_SIZE

from . import palette as P
from ._util import (
    finalize,
    new_canvas,
    outline_polygon,
    shaded_circle,
    shaded_rect,
    soft_shadow,
)


def generate(name: str) -> Image.Image:
    parts = name.split("_", 1)
    kind = parts[0]
    variant = parts[1] if len(parts) > 1 else "0"
    if kind == "tree":
        return _tree(variant)
    if kind == "rock":
        return _rock(variant)
    if kind == "bush":
        return _bush(variant)
    if kind == "flower":
        return _flower(variant)
    if kind == "banner":
        return _banner(variant)
    if kind == "rallyflag":
        return _rally_flag(variant)
    if kind == "stones":
        return _stones(variant)
    if kind == "castle":
        return _castle(variant)
    if kind == "mushroom":
        return _mushroom(variant)
    return _bush(variant)


def _rally_flag(variant: str) -> Image.Image:
    """Small pennant flag — gold = hero rally, red = barracks rally."""
    size = 32
    img, d, s = new_canvas(size)
    pole_x = size // 2 - 6
    # Pole
    d.rectangle((pole_x * s, 4 * s, (pole_x + 2) * s, (size - 2) * s), fill=P.BANNER_POLE)
    d.ellipse(((pole_x - 1) * s, 2 * s, (pole_x + 3) * s, 6 * s), fill=P.KNIGHT_GOLD)
    # Pennant
    color = P.KNIGHT_GOLD if variant == "hero" else P.BANNER_RED
    pts = [
        (pole_x + 2, 6),
        (pole_x + 16, 8),
        (pole_x + 12, 14),
        (pole_x + 16, 20),
        (pole_x + 2, 18),
    ]
    outline_polygon(d, pts, color, scale=s, shadow=False)
    return finalize(img, size)


# ------------------------------------------------------------- Trees

def _tree(variant: str) -> Image.Image:
    size = TILE_SIZE
    img, d, s = new_canvas(size)
    cx = size // 2
    cy = size - 10
    # Ground shadow
    soft_shadow(img, cx, cy + 8, 16, 5, scale=s, alpha=140)
    # Trunk
    shaded_rect(d, cx - 4, cy - 8, 8, 16, P.TREE_TRUNK, scale=s,
                outline=P.TREE_TRUNK_DARK, top_light=False)
    # Canopy
    if variant == "pine":
        # Layered triangles
        for layer, y_off in enumerate((0, -8, -16)):
            w = 22 - layer * 4
            outline_polygon(
                d,
                [(cx - w, cy - 10 + y_off), (cx + w, cy - 10 + y_off), (cx, cy - 22 + y_off - layer * 2)],
                P.TREE_LEAVES,
                scale=s,
                shadow=True,
            )
    else:
        # Oak: round canopy made of overlapping circles
        canopy_cy = cy - 18
        for (ox, oy, r) in [(-8, -2, 10), (9, -1, 9), (0, -8, 10), (-3, 3, 8), (5, 3, 8)]:
            shaded_circle(d, cx + ox, canopy_cy + oy, r, P.TREE_LEAVES, scale=s,
                          shadow_tint=P.TREE_LEAVES_DARK, highlight_tint=P.TREE_LEAVES_LIGHT)
    return finalize(img, size)


# ------------------------------------------------------------- Rocks

def _rock(variant: str) -> Image.Image:
    size = TILE_SIZE
    img, d, s = new_canvas(size)
    cx = size // 2
    cy = size - 16
    big = variant in ("large", "big")
    mid = variant in ("med", "medium")
    if big:
        soft_shadow(img, cx, cy + 10, 20, 5, scale=s, alpha=150)
        pts = [(cx - 18, cy + 6), (cx - 16, cy - 6), (cx - 6, cy - 14),
               (cx + 8, cy - 12), (cx + 18, cy - 2), (cx + 14, cy + 8)]
        outline_polygon(d, pts, P.ROCK, scale=s, shadow=True)
        # Lighter top facet.
        top = [(cx - 12, cy - 8), (cx - 2, cy - 14), (cx + 8, cy - 10), (cx - 6, cy - 4)]
        d.polygon([(p[0] * s, p[1] * s) for p in top], fill=(*P.STONE_LIGHT[:3], 200))
    elif mid:
        soft_shadow(img, cx, cy + 6, 12, 4, scale=s, alpha=140)
        pts = [(cx - 10, cy + 4), (cx - 8, cy - 4), (cx - 2, cy - 8),
               (cx + 6, cy - 6), (cx + 10, cy), (cx + 8, cy + 6)]
        outline_polygon(d, pts, P.ROCK, scale=s, shadow=True)
        d.polygon([((cx - 4) * s, (cy - 6) * s), ((cx + 4) * s, (cy - 4) * s),
                   (cx * s, (cy - 2) * s)], fill=(*P.STONE_LIGHT[:3], 200))
    else:
        soft_shadow(img, cx, cy + 4, 7, 2, scale=s, alpha=130)
        shaded_circle(d, cx, cy, 5, P.ROCK, scale=s, shadow_tint=P.ROCK_DARK,
                      highlight_tint=P.STONE_LIGHT)
    return finalize(img, size)


# -------------------------------------------------------------- Bush

def _bush(variant: str) -> Image.Image:
    size = TILE_SIZE
    img, d, s = new_canvas(size)
    cx = size // 2
    cy = size - 14
    soft_shadow(img, cx, cy + 8, 14, 4, scale=s, alpha=140)
    for (ox, oy, r) in [(-6, 0, 7), (4, 2, 6), (0, -4, 7), (-2, 4, 5)]:
        shaded_circle(d, cx + ox, cy + oy, r, P.BUSH, scale=s,
                      shadow_tint=P.BUSH_DARK,
                      highlight_tint=(130, 180, 96, 255))
    # Tiny berries on variant "berry"
    if variant == "berry":
        for (bx, by) in [(-5, -3), (3, -2), (-1, 1)]:
            d.ellipse(((cx + bx - 1) * s, (cy + by - 1) * s,
                       (cx + bx + 1) * s, (cy + by + 1) * s), fill=P.FLOWER_PINK)
    return finalize(img, size)


# ------------------------------------------------------------ Flower

def _flower(variant: str) -> Image.Image:
    size = TILE_SIZE // 2
    img, d, s = new_canvas(size)
    cx = cy = size // 2
    color_map = {"pink": P.FLOWER_PINK, "yellow": P.FLOWER_YELLOW, "blue": P.FLOWER_BLUE}
    color = color_map.get(variant, P.FLOWER_PINK)
    # Stem
    d.line((cx * s, (cy + 3) * s, cx * s, (size - 1) * s), fill=P.BUSH_DARK, width=1 * s)
    # Leaf
    d.ellipse(((cx - 3) * s, (cy + 4) * s, (cx + 1) * s, (cy + 7) * s), fill=P.BUSH)
    # Petals (5)
    for angle_deg in (0, 72, 144, 216, 288):
        rad = math.radians(angle_deg)
        px = cx + int(3 * math.cos(rad))
        py = cy + int(3 * math.sin(rad))
        d.ellipse(((px - 2) * s, (py - 2) * s, (px + 2) * s, (py + 2) * s), fill=color)
    # Center
    d.ellipse(((cx - 1) * s, (cy - 1) * s, (cx + 1) * s, (cy + 1) * s), fill=P.KNIGHT_GOLD)
    return finalize(img, size)


# ------------------------------------------------------------ Banner

def _banner(variant: str) -> Image.Image:
    size = TILE_SIZE
    img, d, s = new_canvas(size)
    cx = size // 2
    # Pole
    d.rectangle(((cx - 1) * s, 4 * s, (cx + 1) * s, (size - 4) * s), fill=P.BANNER_POLE)
    # Cloth
    colors = {"red": P.BANNER_RED, "blue": P.KNIGHT_BLUE}
    color = colors.get(variant, P.BANNER_RED)
    pts = [(cx + 1, 8), (cx + 16, 8), (cx + 14, 22), (cx + 16, 30), (cx + 1, 30)]
    outline_polygon(d, pts, color, scale=s, shadow=False)
    # Emblem
    d.ellipse(((cx + 5) * s, 14 * s, (cx + 11) * s, 20 * s), fill=P.KNIGHT_GOLD)
    # Pole cap
    d.ellipse(((cx - 2) * s, 2 * s, (cx + 2) * s, 6 * s), fill=P.KNIGHT_GOLD)
    return finalize(img, size)


# ------------------------------------------------------------- Stones

def _stones(variant: str) -> Image.Image:
    size = TILE_SIZE
    img, d, s = new_canvas(size)
    rng = random.Random(hash("stones" + variant) & 0xFFFF)
    soft_shadow(img, size // 2, size - 10, 18, 4, scale=s, alpha=120)
    for _ in range(5):
        x = rng.randint(8, size - 8)
        y = rng.randint(size - 20, size - 8)
        r = rng.randint(2, 4)
        shaded_circle(d, x, y, r, P.ROCK, scale=s,
                      shadow_tint=P.ROCK_DARK, highlight_tint=P.STONE_LIGHT)
    return finalize(img, size)


# ------------------------------------------------------------ Castle

def _castle(variant: str) -> Image.Image:
    size = TILE_SIZE * 2
    img, d, s = new_canvas(size)
    cx = size // 2
    cy = size - 12
    soft_shadow(img, cx, cy + 8, 50, 8, scale=s, alpha=160)
    # Main keep
    shaded_rect(d, cx - 32, cy - 56, 64, 60, P.STONE, scale=s,
                outline=(50, 46, 44, 255), top_light=True)
    # Central tower
    shaded_rect(d, cx - 14, cy - 80, 28, 28, P.STONE, scale=s,
                outline=(50, 46, 44, 255))
    # Battlements
    for bx in range(-30, 31, 8):
        d.rectangle(((cx + bx) * s, (cy - 64) * s, (cx + bx + 5) * s, (cy - 58) * s), fill=P.STONE)
    for bx in range(-12, 13, 8):
        d.rectangle(((cx + bx) * s, (cy - 88) * s, (cx + bx + 5) * s, (cy - 82) * s), fill=P.STONE)
    # Flags
    d.rectangle(((cx - 1) * s, (cy - 104) * s, (cx + 1) * s, (cy - 88) * s), fill=P.BANNER_POLE)
    d.polygon([((cx + 1) * s, (cy - 104) * s), ((cx + 10) * s, (cy - 100) * s),
               ((cx + 1) * s, (cy - 96) * s)], fill=P.BANNER_RED)
    # Gate
    d.rectangle(((cx - 6) * s, (cy - 18) * s, (cx + 6) * s, cy * s), fill=(40, 30, 20, 255))
    d.polygon([((cx - 6) * s, (cy - 18) * s), ((cx + 6) * s, (cy - 18) * s),
               (cx * s, (cy - 24) * s)], fill=(40, 30, 20, 255))
    # Windows (lit)
    for (wx, wy) in [(-20, -40), (0, -40), (20, -40), (-6, -70), (6, -70)]:
        d.rectangle(((cx + wx - 2) * s, (cy + wy) * s, (cx + wx + 2) * s, (cy + wy + 5) * s),
                    fill=(240, 220, 120, 255))
    return finalize(img, size)


# ------------------------------------------------------- Mushroom

def _mushroom(variant: str) -> Image.Image:
    size = TILE_SIZE // 2
    img, d, s = new_canvas(size)
    cx = size // 2
    cy = size - 6
    # Stem
    shaded_rect(d, cx - 2, cy - 6, 4, 6, (230, 218, 190, 255), scale=s,
                outline=(150, 134, 100, 255), top_light=False)
    # Cap
    shaded_circle(d, cx, cy - 7, 6, P.FLOWER_PINK, scale=s,
                  shadow_tint=(170, 72, 100, 255), highlight_tint=(255, 190, 210, 255))
    # Dots
    d.ellipse(((cx - 3) * s, (cy - 8) * s, (cx - 1) * s, (cy - 6) * s), fill=(255, 255, 255, 230))
    d.ellipse(((cx + 1) * s, (cy - 9) * s, (cx + 3) * s, (cy - 7) * s), fill=(255, 255, 255, 230))
    return finalize(img, size)
