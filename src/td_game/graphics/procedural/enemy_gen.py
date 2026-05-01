"""Enemy sprite generator with 3D shading + 6-frame walk cycles.

Name format: '<kind>_<state>_<frame>' (e.g. 'orc_walk_3').
States: idle (2 frames), walk (6 frames), death (1 frame).

Motion philosophy: the body largely holds still; legs swing and only the
torso gets a 1-pixel bob at the stride peak. This reads as smooth stride
instead of a chunky whole-body hop.
"""
from __future__ import annotations

from PIL import Image, ImageDraw

from td_game.core.constants import TILE_SIZE

from . import palette as P
from ._util import (
    finalize,
    glow,
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
    dying = state == "death"

    if kind == "orc":
        _orc(img, d, s, bob, lean, arm, dying)
    elif kind == "goblin":
        _goblin(img, d, s, bob, lean, arm, dying)
    elif kind == "troll":
        _troll(img, d, s, bob, lean, arm, dying)
    elif kind == "wraith":
        _wraith(img, d, s, frame, state)
    elif kind == "dragon":
        _dragon(img, d, s, frame, state)
    else:
        _orc(img, d, s, bob, lean, arm, dying)

    return finalize(img, TILE_SIZE)


# ----------------------------------------------------------------- Orc

def _orc(img, d, s, bob, lean, arm, dying: bool) -> None:
    cx = cy = TILE_SIZE // 2
    if dying:
        cy += 10
    soft_shadow(img, cx, cy + 16, 14, 5, scale=s, alpha=130)

    # Legs: feet stay on ground; front/back swing horizontally.
    leg_y = cy + 6
    shaded_rect(d, cx - 7 + lean, leg_y, 5, 8, P.ORC_CLOTH, scale=s)
    shaded_rect(d, cx + 2 - lean, leg_y, 5, 8, P.ORC_CLOTH, scale=s)

    # Body: only a 1px bob at the peak of the stride.
    body_y = cy - 8 + bob
    shaded_rect(d, cx - 10, body_y, 20, 16, P.ORC_CLOTH, scale=s)
    d.rectangle(((cx - 8) * s, (body_y + 2) * s, (cx + 8) * s, (body_y + 6) * s),
                fill=(160, 120, 78, 210))

    # Arms swing opposite to legs.
    arm_y = body_y + 2
    shaded_rect(d, cx - 13 + arm, arm_y, 5, 11, P.ORC_SKIN, scale=s)
    shaded_rect(d, cx + 8 - arm, arm_y, 5, 11, P.ORC_SKIN, scale=s)

    head_cy = cy - 14 + bob
    shaded_circle(d, cx, head_cy, 9, P.ORC_SKIN, scale=s,
                  shadow_tint=P.ORC_SKIN_DARK, highlight_tint=(170, 210, 140, 255))
    d.polygon([((cx - 3) * s, (head_cy + 6) * s), ((cx - 1) * s, (head_cy + 4) * s),
               ((cx - 2) * s, (head_cy + 9) * s)], fill=(240, 230, 200, 255))
    d.polygon([((cx + 3) * s, (head_cy + 6) * s), ((cx + 1) * s, (head_cy + 4) * s),
               ((cx + 2) * s, (head_cy + 9) * s)], fill=(240, 230, 200, 255))
    d.ellipse(((cx - 4) * s, (head_cy - 1) * s, (cx - 1) * s, (head_cy + 2) * s),
              fill=(240, 40, 40, 255))
    d.ellipse(((cx + 2) * s, (head_cy - 1) * s, (cx + 5) * s, (head_cy + 2) * s),
              fill=(240, 40, 40, 255))


# --------------------------------------------------------------- Goblin

def _goblin(img, d, s, bob, lean, arm, dying: bool) -> None:
    cx = cy = TILE_SIZE // 2
    if dying:
        cy += 12
    soft_shadow(img, cx, cy + 16, 11, 4, scale=s, alpha=120)

    leg_y = cy + 5
    shaded_rect(d, cx - 5 + lean, leg_y, 4, 7, P.LEATHER_DARK, scale=s)
    shaded_rect(d, cx + 1 - lean, leg_y, 4, 7, P.LEATHER_DARK, scale=s)

    body_y = cy - 6 + bob
    shaded_rect(d, cx - 8, body_y, 16, 12, P.LEATHER, scale=s)
    shaded_rect(d, cx - 10 + arm, body_y + 1, 4, 9, P.GOBLIN_SKIN, scale=s)
    shaded_rect(d, cx + 6 - arm, body_y + 1, 4, 9, P.GOBLIN_SKIN, scale=s)

    head_cy = cy - 12 + bob
    shaded_circle(d, cx, head_cy, 8, P.GOBLIN_SKIN, scale=s,
                  shadow_tint=P.GOBLIN_SKIN_DARK, highlight_tint=(200, 220, 140, 255))
    d.polygon([((cx - 1) * s, (head_cy + 2) * s), ((cx + 5) * s, (head_cy + 2) * s),
               ((cx + 1) * s, (head_cy + 5) * s)], fill=P.GOBLIN_SKIN_DARK)
    d.ellipse(((cx - 4) * s, (head_cy - 1) * s, (cx - 2) * s, (head_cy + 1) * s),
              fill=(255, 220, 80, 255))
    d.ellipse(((cx + 2) * s, (head_cy - 1) * s, (cx + 4) * s, (head_cy + 1) * s),
              fill=(255, 220, 80, 255))
    d.polygon([((cx - 8) * s, (head_cy - 2) * s), ((cx - 10) * s, (head_cy - 8) * s),
               ((cx - 6) * s, (head_cy - 5) * s)], fill=P.GOBLIN_SKIN_DARK)
    d.polygon([((cx + 8) * s, (head_cy - 2) * s), ((cx + 10) * s, (head_cy - 8) * s),
               ((cx + 6) * s, (head_cy - 5) * s)], fill=P.GOBLIN_SKIN_DARK)


# --------------------------------------------------------------- Troll

def _troll(img, d, s, bob, lean, arm, dying: bool) -> None:
    cx = cy = TILE_SIZE // 2
    if dying:
        cy += 8
    soft_shadow(img, cx, cy + 18, 18, 6, scale=s, alpha=140)

    leg_y = cy + 7
    shaded_rect(d, cx - 9 + lean, leg_y, 7, 9, P.LEATHER_DARK, scale=s)
    shaded_rect(d, cx + 2 - lean, leg_y, 7, 9, P.LEATHER_DARK, scale=s)

    body_y = cy - 10 + bob
    shaded_rect(d, cx - 14, body_y, 28, 18, P.TROLL_SKIN, scale=s)
    d.ellipse(((cx - 10) * s, (body_y + 8) * s, (cx + 10) * s, (body_y + 17) * s),
              fill=(*P.TROLL_SKIN_DARK[:3], 130))
    shaded_rect(d, cx - 18 + arm, body_y + 2, 6, 16, P.TROLL_SKIN, scale=s)
    shaded_rect(d, cx + 12 - arm, body_y + 2, 6, 16, P.TROLL_SKIN, scale=s)

    head_cy = cy - 16 + bob
    shaded_circle(d, cx, head_cy, 7, P.TROLL_SKIN, scale=s,
                  shadow_tint=P.TROLL_SKIN_DARK, highlight_tint=(190, 170, 140, 255))
    d.polygon([((cx - 5) * s, (head_cy - 5) * s), ((cx - 3) * s, (head_cy - 10) * s),
               ((cx - 1) * s, (head_cy - 5) * s)], fill=P.BONE)
    d.polygon([((cx + 5) * s, (head_cy - 5) * s), ((cx + 3) * s, (head_cy - 10) * s),
               ((cx + 1) * s, (head_cy - 5) * s)], fill=P.BONE)
    d.ellipse(((cx - 3) * s, head_cy * s, (cx - 1) * s, (head_cy + 2) * s),
              fill=(60, 20, 20, 255))
    d.ellipse(((cx + 1) * s, head_cy * s, (cx + 3) * s, (head_cy + 2) * s),
              fill=(60, 20, 20, 255))


# --------------------------------------------------------------- Wraith

def _wraith(img, d, s, frame: int, state: str) -> None:
    cx = cy = TILE_SIZE // 2
    soft_shadow(img, cx, cy + 18, 10, 3, scale=s, alpha=90)
    glow(img, cx, cy - 4, 16, P.WRAITH_LIGHT, scale=s, alpha=120)
    float_bob = [0, -1, -1, 0, -1, -1][frame % 6] if state == "walk" else 0
    wave = frame % 6
    pts = [
        (cx - 14, cy + 16 + float_bob),
        (cx - 12, cy - 6 + float_bob),
        (cx - 8, cy - 14 + float_bob),
        (cx, cy - 20 + float_bob),
        (cx + 8, cy - 14 + float_bob),
        (cx + 12, cy - 6 + float_bob),
        (cx + 14, cy + 16 + float_bob),
        (cx + 9, cy + 14 + float_bob + (1 if wave == 1 else 0)),
        (cx + 4, cy + 17 + float_bob),
        (cx - 4, cy + 17 + float_bob),
        (cx - 9, cy + 14 + float_bob + (1 if wave == 4 else 0)),
    ]
    outline_polygon(d, pts, P.WRAITH, scale=s, shadow=False)
    hd_hi = [(cx - 8, cy - 14 + float_bob), (cx, cy - 20 + float_bob),
             (cx + 2, cy - 16 + float_bob), (cx - 4, cy - 12 + float_bob)]
    d.polygon([(p[0] * s, p[1] * s) for p in hd_hi], fill=(*P.WRAITH_LIGHT[:3], 160))
    d.ellipse(((cx - 4) * s, (cy - 8 + float_bob) * s, (cx - 1) * s, (cy - 5 + float_bob) * s),
              fill=P.WRAITH_GLOW)
    d.ellipse(((cx + 1) * s, (cy - 8 + float_bob) * s, (cx + 4) * s, (cy - 5 + float_bob) * s),
              fill=P.WRAITH_GLOW)


# --------------------------------------------------------------- Dragon

def _dragon(img, d, s, frame: int, state: str) -> None:
    cx = cy = TILE_SIZE // 2
    soft_shadow(img, cx, cy + 20, 16, 4, scale=s, alpha=110)
    flap = [0, -2, -3, -2, 0, 2][frame % 6] if state == "walk" else 0
    body_bob = [0, -1, -2, -1, 0, 1][frame % 6] if state == "walk" else 0

    wing_l = [(cx - 6, cy - 2 + body_bob), (cx - 24, cy - 10 + flap),
              (cx - 22, cy + 2 + flap), (cx - 10, cy + 4 + body_bob)]
    outline_polygon(d, wing_l, P.DRAGON_WING, scale=s, shadow=True)
    wing_r = [(cx + 6, cy - 2 + body_bob), (cx + 24, cy - 10 + flap),
              (cx + 22, cy + 2 + flap), (cx + 10, cy + 4 + body_bob)]
    outline_polygon(d, wing_r, P.DRAGON_WING, scale=s, shadow=True)

    body_pts = [(cx - 12, cy - 2 + body_bob), (cx - 10, cy + 10 + body_bob),
                (cx + 10, cy + 12 + body_bob), (cx + 12, cy - 4 + body_bob),
                (cx + 8, cy - 8 + body_bob), (cx - 8, cy - 8 + body_bob)]
    outline_polygon(d, body_pts, P.DRAGON, scale=s, shadow=True)
    d.line([((cx - 8) * s, (cy + 5 + body_bob) * s), ((cx + 8) * s, (cy + 6 + body_bob) * s)],
           fill=(*P.DRAGON_LIGHT[:3], 180), width=2 * s)
    d.polygon([((cx + 6) * s, (cy + 10 + body_bob) * s),
               ((cx + 18) * s, (cy + 14 + body_bob) * s),
               ((cx + 8) * s, (cy + 14 + body_bob) * s)], fill=P.DRAGON_DARK)

    head_cx = cx
    head_cy = cy - 14 + body_bob
    shaded_circle(d, head_cx, head_cy, 7, P.DRAGON, scale=s,
                  shadow_tint=P.DRAGON_DARK, highlight_tint=P.DRAGON_LIGHT)
    d.polygon([((head_cx - 4) * s, (head_cy - 5) * s), ((head_cx - 6) * s, (head_cy - 12) * s),
               ((head_cx - 2) * s, (head_cy - 5) * s)], fill=P.BONE)
    d.polygon([((head_cx + 4) * s, (head_cy - 5) * s), ((head_cx + 6) * s, (head_cy - 12) * s),
               ((head_cx + 2) * s, (head_cy - 5) * s)], fill=P.BONE)
    d.ellipse(((head_cx - 2) * s, (head_cy + 3) * s, (head_cx + 8) * s, (head_cy + 8) * s),
              fill=P.DRAGON_DARK)
    if state == "idle" and frame == 1:
        glow(img, head_cx + 10, head_cy + 6, 4, (255, 180, 60, 255), scale=s, alpha=180)
    d.ellipse(((head_cx - 3) * s, (head_cy - 1) * s, (head_cx - 1) * s, (head_cy + 1) * s),
              fill=(255, 240, 80, 255))
    d.ellipse(((head_cx + 1) * s, (head_cy - 1) * s, (head_cx + 3) * s, (head_cy + 1) * s),
              fill=(255, 240, 80, 255))
