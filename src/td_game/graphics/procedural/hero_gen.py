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
    if state == "death":
        bob = (2, 5, 9, 12)[min(frame, 3)]
        lean = 0
        arm = 0

    if kind == "knight":
        _knight(img, d, s, bob, lean, arm, state, frame)
    elif kind == "ranger":
        _ranger(img, d, s, bob, lean, arm, state, frame)
    else:
        _knight(img, d, s, bob, lean, arm, state, frame)

    if state == "death" and frame >= 2:
        alpha = (0.85, 0.55, 0.25)[min(frame - 1, 2)]
        r, g, b, a = img.split()
        a = a.point(lambda v: int(v * alpha))
        img.putalpha(a)

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
    # Sword: dramatic overhead swing during attack frames.
    # Frame 0 = wind-up (raised high behind), 1 = down-strike across,
    # 2 = follow-through (extended forward). Gives a readable arc.
    if state == "attack":
        import math as _m
        # Angle measured from vertical (up). Positive rotates clockwise.
        sword_angle = (-110, 20, 75)[frame % 3]
        sword_len = 24
        rad = _m.radians(sword_angle)
        # Hand pivot roughly at shoulder height.
        hx = cx + 3
        hy = cy - 6
        tip_x = hx + _m.sin(rad) * sword_len
        tip_y = hy - _m.cos(rad) * sword_len
        # Blade polygon (tapered: wider at hilt, thinner at tip).
        nx = _m.cos(rad)
        ny = _m.sin(rad)
        w0, w1 = 3, 1
        blade = [
            (hx + nx * w0, hy + ny * w0),
            (hx - nx * w0, hy - ny * w0),
            (tip_x - nx * w1, tip_y - ny * w1),
            (tip_x + nx * w1, tip_y + ny * w1),
        ]
        d.polygon([(p[0] * s, p[1] * s) for p in blade], fill=P.KNIGHT_STEEL_LIGHT)
        d.line(((hx - nx * w0) * s, (hy - ny * w0) * s,
                (tip_x - nx * w1) * s, (tip_y - ny * w1) * s),
               fill=P.KNIGHT_STEEL, width=1 * s)
        # Guard.
        d.rectangle(((hx - 4) * s, (hy - 1) * s, (hx + 4) * s, (hy + 2) * s), fill=P.KNIGHT_GOLD)
        # Speed streak on the strike frame.
        if frame == 1:
            from ._util import glow as _glow
            _glow(img, int((hx + tip_x) / 2), int((hy + tip_y) / 2), 10,
                  (255, 255, 220, 255), scale=s, alpha=140)
    else:
        sword_x = cx + 12 + arm
        sword_top = cy - 16
        d.rectangle(((sword_x) * s, sword_top * s, (sword_x + 2) * s, (cy + 4) * s),
                    fill=P.KNIGHT_STEEL_LIGHT)
        d.rectangle(((sword_x - 3) * s, (cy + 2) * s, (sword_x + 5) * s, (cy + 4) * s),
                    fill=P.KNIGHT_GOLD)
        d.rectangle(((sword_x) * s, (cy + 4) * s, (sword_x + 2) * s, (cy + 8) * s),
                    fill=P.WOOD_DARK)
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
