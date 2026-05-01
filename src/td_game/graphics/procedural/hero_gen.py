"""Hero sprite generator with 3D shading + 6-frame walk cycles.

Name: '<kind>_<state>_<frame>' — e.g. 'knight_walk_4', 'ranger_idle_0'.
"""
from __future__ import annotations

from PIL import Image, ImageDraw

from td_game.core.constants import TILE_SIZE

from . import palette as P
from ._util import (
    finalize,
    new_canvas,
    outline_polygon,
    parse_sprite_name,
    shaded_circle,
    shaded_rect,
    soft_shadow,
    walk_arm,
    walk_bob,
    walk_lean,
)


def generate(name: str) -> Image.Image:
    kind, state, frame = parse_sprite_name(name)
    img, d, s = new_canvas(TILE_SIZE)
    bob = walk_bob(state, frame)
    lean = walk_lean(state, frame)
    arm = walk_arm(state, frame)

    if kind == "knight":
        _knight(img, d, s, bob, lean, arm, state, frame)
    elif kind == "ranger":
        _ranger(img, d, s, bob, lean, arm, state, frame)
    else:
        _knight(img, d, s, bob, lean, arm, state, frame)
    return finalize(img, TILE_SIZE)


def _knight(img, d, s, bob, lean, arm, state, frame) -> None:
    cx = cy = TILE_SIZE // 2
    soft_shadow(img, cx, cy + 16, 13, 5, scale=s, alpha=130)
    # Legs (feet planted, stride by horizontal offset).
    leg_y = cy + 6
    shaded_rect(d, cx - 6 + lean, leg_y, 4, 8, P.KNIGHT_STEEL_DARK, scale=s)
    shaded_rect(d, cx + 2 - lean, leg_y, 4, 8, P.KNIGHT_STEEL_DARK, scale=s)
    # Torso (1px bob peak).
    body_y = cy - 8 + bob
    shaded_rect(d, cx - 9, body_y, 18, 16, P.KNIGHT_STEEL, scale=s)
    d.rectangle(((cx - 4) * s, body_y * s, (cx + 4) * s, (body_y + 16) * s), fill=P.KNIGHT_BLUE)
    d.polygon([((cx - 4) * s, (body_y + 16) * s), ((cx + 4) * s, (body_y + 16) * s),
               (cx * s, (body_y + 20) * s)], fill=P.KNIGHT_BLUE_DARK)
    d.ellipse(((cx - 2) * s, (body_y + 4) * s, (cx + 2) * s, (body_y + 8) * s), fill=P.KNIGHT_GOLD)
    # Shoulders (fixed).
    shaded_circle(d, cx - 10, body_y + 1, 4, P.KNIGHT_STEEL, scale=s,
                  shadow_tint=P.KNIGHT_STEEL_DARK, highlight_tint=P.KNIGHT_STEEL_LIGHT)
    shaded_circle(d, cx + 10, body_y + 1, 4, P.KNIGHT_STEEL, scale=s,
                  shadow_tint=P.KNIGHT_STEEL_DARK, highlight_tint=P.KNIGHT_STEEL_LIGHT)
    # Head.
    head_cy = cy - 15 + bob
    shaded_circle(d, cx, head_cy, 7, P.KNIGHT_STEEL, scale=s,
                  shadow_tint=P.KNIGHT_STEEL_DARK, highlight_tint=P.KNIGHT_STEEL_LIGHT)
    d.rectangle(((cx - 4) * s, (head_cy - 1) * s, (cx + 4) * s, (head_cy + 1) * s), fill=(20, 20, 24, 255))
    plume_pts = [(cx - 1, head_cy - 7), (cx + 6, head_cy - 12), (cx + 2, head_cy - 6)]
    outline_polygon(d, plume_pts, P.BANNER_RED, scale=s)
    # Sword swung on attack, held at side otherwise.
    sword_offset = 0
    if state == "attack":
        sword_offset = [0, -3, 0][frame % 3]
    sword_x = cx + 12 + sword_offset + arm
    sword_top = cy - 16 - sword_offset
    d.rectangle(((sword_x) * s, sword_top * s, (sword_x + 2) * s, (cy + 4) * s), fill=P.KNIGHT_STEEL_LIGHT)
    d.rectangle(((sword_x - 3) * s, (cy + 2) * s, (sword_x + 5) * s, (cy + 4) * s), fill=P.KNIGHT_GOLD)
    d.rectangle(((sword_x) * s, (cy + 4) * s, (sword_x + 2) * s, (cy + 8) * s), fill=P.WOOD_DARK)
    # Shield (opposite hand — moves with arm).
    shield_x = cx - 12 - arm
    shaded_circle(d, shield_x, body_y + 4, 5, P.KNIGHT_BLUE, scale=s,
                  shadow_tint=P.KNIGHT_BLUE_DARK, highlight_tint=(120, 160, 230, 255))
    d.line((shield_x * s, body_y * s, shield_x * s, (body_y + 9) * s), fill=P.KNIGHT_GOLD, width=1 * s)
    d.line(((shield_x - 4) * s, (body_y + 4) * s, (shield_x + 4) * s, (body_y + 4) * s),
           fill=P.KNIGHT_GOLD, width=1 * s)


def _ranger(img, d, s, bob, lean, arm, state, frame) -> None:
    cx = cy = TILE_SIZE // 2
    soft_shadow(img, cx, cy + 16, 11, 4, scale=s, alpha=120)
    leg_y = cy + 6
    shaded_rect(d, cx - 5 + lean, leg_y, 4, 8, P.LEATHER_DARK, scale=s)
    shaded_rect(d, cx + 1 - lean, leg_y, 4, 8, P.LEATHER_DARK, scale=s)
    body_y = cy - 8 + bob
    shaded_rect(d, cx - 8, body_y, 16, 14, P.ARCHER_LEATHER, scale=s)
    d.rectangle(((cx - 8) * s, (body_y + 10) * s, (cx + 8) * s, (body_y + 12) * s), fill=P.LEATHER_DARK)
    hood_pts = [(cx - 10, body_y + 6), (cx - 8, body_y - 8), (cx, body_y - 14),
                (cx + 8, body_y - 8), (cx + 10, body_y + 6)]
    outline_polygon(d, hood_pts, P.ARCHER_GREEN, scale=s)
    face_cy = body_y - 5 + bob
    shaded_circle(d, cx, face_cy, 4, (220, 190, 150, 255), scale=s,
                  shadow_tint=(160, 120, 90, 255), highlight_tint=(240, 215, 180, 255))
    bow_x = cx + 10 + arm
    bow_offset = 0
    if state == "attack":
        bow_offset = [0, -2, 0][frame % 3]
    d.arc(((bow_x - 2) * s, (cy - 14) * s, (bow_x + 8) * s, (cy + 12) * s),
          start=270, end=90, fill=P.WOOD_DARK, width=2 * s)
    d.line(((bow_x + 6) * s, (cy - 12) * s, (bow_x + 3 - bow_offset) * s, cy * s),
           fill=(240, 240, 240, 255), width=1 * s)
    d.line(((bow_x + 3 - bow_offset) * s, cy * s, (bow_x + 6) * s, (cy + 12) * s),
           fill=(240, 240, 240, 255), width=1 * s)
    if state == "attack":
        d.line(((bow_x + 3 - bow_offset) * s, cy * s, (bow_x + 10) * s, cy * s),
               fill=P.ARROW, width=1 * s)
    d.polygon([((cx + 8) * s, (body_y - 8) * s), ((cx + 14) * s, (body_y - 10) * s),
               ((cx + 9) * s, (body_y - 5) * s)], fill=P.ARCHER_GREEN_DARK)
