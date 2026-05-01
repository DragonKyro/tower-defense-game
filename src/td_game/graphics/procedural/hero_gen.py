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
    elif kind == "footman":
        _footman(img, d, s, bob, lean, arm, state, frame)
    elif kind == "soldier":
        _soldier(img, d, s, bob, lean, arm, state, frame)
    elif kind == "peasant":
        _peasant(img, d, s, bob, lean, arm, state, frame)
    else:
        _knight(img, d, s, bob, lean, arm, state, frame)

    if state == "death" and frame >= 2:
        alpha = (0.85, 0.55, 0.25)[min(frame - 1, 2)]
        r, g, b, a = img.split()
        a = a.point(lambda v: int(v * alpha))
        img.putalpha(a)

    return finalize(img, TILE_SIZE)


def _knight(img, d, s, bob, lean, arm, state, frame) -> None:
    """Hero knight — iconic: crimson cape, tall gold-tipped plume, gold pauldrons."""
    cx = cy = TILE_SIZE // 2
    soft_shadow(img, cx, cy + 17, 15, 6, scale=s, alpha=140)
    # Cape flowing behind (under the body so shoulders clip it).
    cape_pts = [
        (cx - 11, cy - 8 + bob),
        (cx + 11, cy - 8 + bob),
        (cx + 9, cy + 12),
        (cx + 2, cy + 18),
        (cx - 2, cy + 18),
        (cx - 9, cy + 12),
    ]
    outline_polygon(d, cape_pts, P.BANNER_RED, scale=s, shadow=True)
    # Legs with light armor.
    leg_y = cy + 6
    shaded_rect(d, cx - 6 + lean, leg_y, 4, 8, P.KNIGHT_STEEL_DARK, scale=s)
    shaded_rect(d, cx + 2 - lean, leg_y, 4, 8, P.KNIGHT_STEEL_DARK, scale=s)
    # Torso — highlighted plate with royal blue tabard + gold emblem.
    body_y = cy - 8 + bob
    shaded_rect(d, cx - 9, body_y, 18, 16, P.KNIGHT_STEEL, scale=s)
    d.rectangle(((cx - 4) * s, body_y * s, (cx + 4) * s, (body_y + 16) * s), fill=P.KNIGHT_BLUE)
    d.polygon([((cx - 4) * s, (body_y + 16) * s), ((cx + 4) * s, (body_y + 16) * s),
               (cx * s, (body_y + 20) * s)], fill=P.KNIGHT_BLUE_DARK)
    # Bigger gold crest on tabard.
    d.ellipse(((cx - 3) * s, (body_y + 3) * s, (cx + 3) * s, (body_y + 9) * s), fill=P.KNIGHT_GOLD)
    d.line(((cx - 3) * s, (body_y + 6) * s, (cx + 3) * s, (body_y + 6) * s),
           fill=P.KNIGHT_GOLD_DARK, width=1 * s)
    # Gold pauldrons — bigger + gold-tinted.
    shaded_circle(d, cx - 10, body_y + 1, 5, P.KNIGHT_GOLD, scale=s,
                  shadow_tint=P.KNIGHT_GOLD_DARK, highlight_tint=(255, 240, 180, 255))
    shaded_circle(d, cx + 10, body_y + 1, 5, P.KNIGHT_GOLD, scale=s,
                  shadow_tint=P.KNIGHT_GOLD_DARK, highlight_tint=(255, 240, 180, 255))
    # Head / helmet.
    head_cy = cy - 16 + bob
    shaded_circle(d, cx, head_cy, 7, P.KNIGHT_STEEL, scale=s,
                  shadow_tint=P.KNIGHT_STEEL_DARK, highlight_tint=P.KNIGHT_STEEL_LIGHT)
    # Visor slit.
    d.rectangle(((cx - 4) * s, (head_cy - 1) * s, (cx + 4) * s, (head_cy + 1) * s),
                fill=(20, 20, 24, 255))
    # TALL plume — 3 colors stacked: gold tip, red body, white base flourish.
    plume_a = [(cx - 1, head_cy - 4), (cx + 7, head_cy - 12), (cx + 3, head_cy - 6)]
    outline_polygon(d, plume_a, P.BANNER_RED, scale=s, shadow=False)
    plume_b = [(cx + 4, head_cy - 10), (cx + 10, head_cy - 18), (cx + 6, head_cy - 12)]
    outline_polygon(d, plume_b, P.BANNER_RED, scale=s, shadow=False)
    plume_tip = [(cx + 8, head_cy - 16), (cx + 11, head_cy - 20), (cx + 9, head_cy - 16)]
    d.polygon([(p[0] * s, p[1] * s) for p in plume_tip], fill=P.KNIGHT_GOLD)
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


def _footman(img, d, s, bob, lean, arm, state, frame) -> None:
    """Tier-1/2 barracks soldier — padded cloth + red tabard, no helmet plume.

    Simpler than the hero knight: no cape, iron cap instead of plated helm,
    plain round shield. Reads as 'conscript' vs. the hero's 'royal knight'.
    """
    cx = cy = TILE_SIZE // 2
    soft_shadow(img, cx, cy + 16, 11, 4, scale=s, alpha=120)
    # Legs — plain leather.
    leg_y = cy + 6
    shaded_rect(d, cx - 5 + lean, leg_y, 4, 7, P.LEATHER_DARK, scale=s)
    shaded_rect(d, cx + 1 - lean, leg_y, 4, 7, P.LEATHER_DARK, scale=s)
    # Padded gambeson body with a small red tabard strip.
    body_y = cy - 7 + bob
    shaded_rect(d, cx - 8, body_y, 16, 14, (206, 188, 148, 255), scale=s)
    d.rectangle(((cx - 3) * s, body_y * s, (cx + 3) * s, (body_y + 14) * s), fill=P.BANNER_RED)
    # Leather belt + round metal boss.
    d.rectangle(((cx - 8) * s, (body_y + 10) * s, (cx + 8) * s, (body_y + 12) * s),
                fill=P.LEATHER_DARK)
    d.ellipse(((cx - 1) * s, (body_y + 9) * s, (cx + 2) * s, (body_y + 12) * s),
              fill=P.KNIGHT_STEEL_LIGHT)
    # Arms bare / leather-sleeved.
    shaded_rect(d, cx - 10 + arm, body_y + 1, 3, 10, (200, 170, 130, 255), scale=s)
    shaded_rect(d, cx + 7 - arm, body_y + 1, 3, 10, (200, 170, 130, 255), scale=s)
    # Iron cap (no visor, no plume).
    head_cy = cy - 13 + bob
    shaded_circle(d, cx, head_cy, 6, (220, 200, 168, 255), scale=s,
                  shadow_tint=(160, 140, 110, 255), highlight_tint=(240, 228, 200, 255))
    # Bowl cap on top.
    d.polygon([((cx - 7) * s, (head_cy - 2) * s),
               ((cx + 7) * s, (head_cy - 2) * s),
               ((cx + 5) * s, (head_cy - 7) * s),
               ((cx - 5) * s, (head_cy - 7) * s)],
              fill=P.KNIGHT_STEEL)
    d.line(((cx - 7) * s, (head_cy - 2) * s, (cx + 7) * s, (head_cy - 2) * s),
           fill=(20, 20, 24, 255), width=1 * s)
    # Eyes.
    d.point((cx - 2, head_cy + 1), fill=(20, 20, 24))
    d.point((cx + 2, head_cy + 1), fill=(20, 20, 24))
    # Round wooden shield.
    shield_x = cx - 12 - arm
    shaded_circle(d, shield_x, body_y + 4, 5, P.WOOD, scale=s,
                  shadow_tint=P.WOOD_DARK, highlight_tint=(180, 130, 88, 255))
    d.ellipse(((shield_x - 2) * s, (body_y + 2) * s,
               (shield_x + 2) * s, (body_y + 6) * s),
              fill=P.KNIGHT_STEEL_LIGHT)
    # Short sword at the hip.
    if state == "attack":
        import math as _m
        ang = _m.radians((-95, 15, 55)[frame % 3])
        hx = cx + 3
        hy = cy - 5
        tip_x = hx + _m.sin(ang) * 18
        tip_y = hy - _m.cos(ang) * 18
        nx = _m.cos(ang)
        ny = _m.sin(ang)
        blade = [
            (hx + nx * 2, hy + ny * 2),
            (hx - nx * 2, hy - ny * 2),
            (tip_x - nx, tip_y - ny),
            (tip_x + nx, tip_y + ny),
        ]
        d.polygon([(p[0] * s, p[1] * s) for p in blade], fill=P.KNIGHT_STEEL_LIGHT)
    else:
        d.rectangle(((cx + 10) * s, (cy - 6) * s, (cx + 12) * s, (cy + 4) * s),
                    fill=P.KNIGHT_STEEL_LIGHT)
        d.rectangle(((cx + 9) * s, (cy - 6) * s, (cx + 13) * s, (cy - 5) * s),
                    fill=P.KNIGHT_GOLD_DARK)


def _soldier(img, d, s, bob, lean, arm, state, frame) -> None:
    """Tier-3/4 barracks soldier — plated armor, steel helm with visor, kite shield."""
    cx = cy = TILE_SIZE // 2
    soft_shadow(img, cx, cy + 16, 13, 5, scale=s, alpha=130)
    leg_y = cy + 6
    shaded_rect(d, cx - 6 + lean, leg_y, 4, 8, P.KNIGHT_STEEL_DARK, scale=s)
    shaded_rect(d, cx + 2 - lean, leg_y, 4, 8, P.KNIGHT_STEEL_DARK, scale=s)
    # Steel chestplate.
    body_y = cy - 8 + bob
    shaded_rect(d, cx - 9, body_y, 18, 15, P.KNIGHT_STEEL, scale=s)
    # Green tabard stripe (so not identical to blue-tabard hero).
    d.rectangle(((cx - 3) * s, body_y * s, (cx + 3) * s, (body_y + 15) * s),
                fill=(80, 140, 80, 255))
    d.ellipse(((cx - 2) * s, (body_y + 4) * s, (cx + 2) * s, (body_y + 8) * s),
              fill=P.KNIGHT_STEEL_LIGHT)
    # Steel pauldrons (no gold).
    shaded_circle(d, cx - 10, body_y + 1, 4, P.KNIGHT_STEEL_DARK, scale=s,
                  shadow_tint=(80, 88, 108, 255), highlight_tint=P.KNIGHT_STEEL)
    shaded_circle(d, cx + 10, body_y + 1, 4, P.KNIGHT_STEEL_DARK, scale=s,
                  shadow_tint=(80, 88, 108, 255), highlight_tint=P.KNIGHT_STEEL)
    # Great helm with slit.
    head_cy = cy - 15 + bob
    shaded_circle(d, cx, head_cy, 7, P.KNIGHT_STEEL, scale=s,
                  shadow_tint=P.KNIGHT_STEEL_DARK, highlight_tint=P.KNIGHT_STEEL_LIGHT)
    d.rectangle(((cx - 4) * s, (head_cy - 1) * s, (cx + 4) * s, (head_cy + 1) * s),
                fill=(20, 20, 24, 255))
    # Short black plume (distinct from hero's tall red plume).
    d.polygon([((cx - 1) * s, (head_cy - 6) * s),
               ((cx + 3) * s, (head_cy - 10) * s),
               ((cx + 1) * s, (head_cy - 5) * s)], fill=(40, 40, 50, 255))
    # Kite shield on left, sword or nothing on right.
    shield_x = cx - 12 - arm
    shaded_rect(d, shield_x - 3, body_y, 6, 10, (80, 140, 80, 255), scale=s,
                outline=(30, 60, 30, 255))
    d.polygon([((shield_x - 3) * s, (body_y + 10) * s),
               ((shield_x + 3) * s, (body_y + 10) * s),
               (shield_x * s, (body_y + 14) * s)], fill=(80, 140, 80, 255))
    # Mace head on right (distinct weapon — not a longsword).
    if state == "attack":
        import math as _m
        ang = _m.radians((-90, 30, 60)[frame % 3])
        hx = cx + 4
        hy = cy - 4
        tip_x = hx + _m.sin(ang) * 16
        tip_y = hy - _m.cos(ang) * 16
        d.line((hx * s, hy * s, tip_x * s, tip_y * s), fill=P.WOOD_DARK, width=2 * s)
        d.ellipse(((tip_x - 4) * s, (tip_y - 4) * s, (tip_x + 4) * s, (tip_y + 4) * s),
                  fill=P.KNIGHT_STEEL)
    else:
        d.line(((cx + 10) * s, (cy - 10) * s, (cx + 10) * s, (cy + 6) * s),
               fill=P.WOOD_DARK, width=2 * s)
        d.ellipse(((cx + 7) * s, (cy - 14) * s, (cx + 13) * s, (cy - 8) * s),
                  fill=P.KNIGHT_STEEL)


def _peasant(img, d, s, bob, lean, arm, state, frame) -> None:
    """Reinforcement — conscripted peasant with a brown tunic and pitchfork."""
    cx = cy = TILE_SIZE // 2
    soft_shadow(img, cx, cy + 16, 10, 4, scale=s, alpha=110)
    # Bare legs / trousers.
    leg_y = cy + 6
    shaded_rect(d, cx - 5 + lean, leg_y, 4, 7, (124, 96, 72, 255), scale=s)
    shaded_rect(d, cx + 1 - lean, leg_y, 4, 7, (124, 96, 72, 255), scale=s)
    # Brown tunic, rope belt.
    body_y = cy - 7 + bob
    shaded_rect(d, cx - 7, body_y, 14, 13, (160, 120, 84, 255), scale=s,
                outline=(82, 58, 36, 255))
    d.rectangle(((cx - 7) * s, (body_y + 9) * s, (cx + 7) * s, (body_y + 10) * s),
                fill=(96, 72, 48, 255))
    # Arms in rolled-up sleeves.
    shaded_rect(d, cx - 9 + arm, body_y + 1, 3, 9, (215, 188, 150, 255), scale=s)
    shaded_rect(d, cx + 6 - arm, body_y + 1, 3, 9, (215, 188, 150, 255), scale=s)
    # Straw hat.
    head_cy = cy - 13 + bob
    shaded_circle(d, cx, head_cy, 5, (215, 188, 150, 255), scale=s,
                  shadow_tint=(160, 128, 90, 255), highlight_tint=(240, 220, 185, 255))
    # Hat brim.
    d.ellipse(((cx - 9) * s, (head_cy - 5) * s, (cx + 9) * s, (head_cy - 2) * s),
              fill=(212, 180, 100, 255))
    d.polygon([((cx - 6) * s, (head_cy - 5) * s),
               ((cx + 6) * s, (head_cy - 5) * s),
               ((cx + 3) * s, (head_cy - 10) * s),
               ((cx - 3) * s, (head_cy - 10) * s)],
              fill=(228, 200, 120, 255))
    d.point((cx - 2, head_cy + 1), fill=(20, 20, 24))
    d.point((cx + 2, head_cy + 1), fill=(20, 20, 24))
    # Pitchfork held upright on the right.
    fork_x = cx + 10 - arm
    d.rectangle((fork_x * s, (cy - 16) * s, (fork_x + 2) * s, (cy + 8) * s),
                fill=P.WOOD_DARK)
    for tine in (-3, 0, 3):
        d.rectangle(((fork_x + tine) * s, (cy - 22) * s,
                     (fork_x + tine + 1) * s, (cy - 14) * s),
                    fill=P.KNIGHT_STEEL_LIGHT)


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
