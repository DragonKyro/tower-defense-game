"""Tower sprite generator with 3D shading + idle/attack frames.

Sprite name format: '<family>_<tier>' (static) OR '<family>_<tier>_<state>_<frame>'
e.g. 'archer_1', 'archer_1_idle_0', 'mage_2_attack_1'.
"""
from __future__ import annotations

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
    glow,
)


def generate(name: str) -> Image.Image:
    parts = name.split("_")
    family = parts[0]
    tier = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 1
    state = parts[2] if len(parts) > 2 else "idle"
    frame = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0

    img, d, s = new_canvas(TILE_SIZE)

    if family == "archer":
        _archer(img, d, s, tier, state, frame)
    elif family == "barracks":
        _barracks(img, d, s, tier, state, frame)
    elif family == "mage":
        _mage(img, d, s, tier, state, frame)
    elif family == "artillery":
        _artillery(img, d, s, tier, state, frame)
    else:
        _archer(img, d, s, tier, state, frame)

    return finalize(img, TILE_SIZE)


def _stone_base(img, d, s, tier: int) -> tuple[int, int, int]:
    """Circular stone platform all towers sit on. Returns (cx, cy, radius)."""
    cx = cy = TILE_SIZE // 2
    platform_r = 18 + tier
    soft_shadow(img, cx, cy + 14, platform_r + 2, 6, scale=s, alpha=130)
    # Outer dark ring
    d.ellipse(((cx - platform_r - 1) * s, (cy + 8) * s,
               (cx + platform_r + 1) * s, (cy + 16) * s), fill=P.STONE_DARK)
    # Top stone slab
    d.ellipse(((cx - platform_r) * s, (cy + 4) * s,
               (cx + platform_r) * s, (cy + 14) * s), fill=P.STONE)
    # Highlight
    d.ellipse(((cx - platform_r + 2) * s, (cy + 5) * s,
               (cx + platform_r - 2) * s, (cy + 9) * s), fill=(*P.STONE_LIGHT[:3], 160))
    # Brick marks.
    for bx_off in (-10, -2, 6):
        d.line(((cx + bx_off) * s, (cy + 8) * s, (cx + bx_off) * s, (cy + 14) * s),
               fill=P.STONE_DARK, width=1 * s)
    return cx, cy, platform_r


# ------------------------------------------------------------- Archer

def _archer(img, d, s, tier: int, state: str, frame: int) -> None:
    cx, cy, _ = _stone_base(img, d, s, tier)
    # Recoil offset on attack frames.
    recoil = 0
    if state == "attack":
        recoil = [-1, -2, 0][frame % 3]
    # Wooden tower body
    body_top = cy - 20 - (tier * 2)
    body_bot = cy + 4
    shaded_rect(d, cx - 11, body_top, 22, body_bot - body_top, P.WOOD, scale=s)
    # Planks
    for py in range(body_top + 4, body_bot - 2, 5):
        d.line(((cx - 10) * s, py * s, (cx + 10) * s, py * s), fill=P.WOOD_DARK, width=1 * s)
    # Window slit
    d.rectangle(((cx - 2) * s, (body_top + 6) * s, (cx + 2) * s, (body_top + 12) * s), fill=(0, 0, 0, 255))
    # Roof (taller w/ tier)
    roof_h = 8 + tier * 3
    roof_top = body_top - roof_h
    pts = [(cx - 14, body_top), (cx + 14, body_top), (cx, roof_top)]
    outline_polygon(d, pts, P.ARCHER_GREEN, scale=s)
    # Flag
    d.rectangle(((cx) * s, (roof_top - 6) * s, (cx + 1) * s, roof_top * s), fill=P.WOOD_DARK)
    d.polygon([((cx + 1) * s, (roof_top - 6) * s), ((cx + 7) * s, (roof_top - 4) * s),
               ((cx + 1) * s, (roof_top - 2) * s)], fill=P.BANNER_RED if tier < 4 else P.KNIGHT_GOLD)
    # Archer in the window (little circle for head, offset by recoil on attack)
    head_cx = cx + recoil
    shaded_circle(d, head_cx, body_top + 9, 3, (220, 190, 150, 255), scale=s,
                  shadow_tint=(160, 120, 90, 255), highlight_tint=(240, 215, 180, 255))
    # Tier decorations: gold trim at tier 3+
    if tier >= 3:
        d.line(((cx - 12) * s, (body_top + 2) * s, (cx + 12) * s, (body_top + 2) * s),
               fill=P.KNIGHT_GOLD, width=2 * s)


# ----------------------------------------------------------- Barracks

def _barracks(img, d, s, tier: int, state: str, frame: int) -> None:
    cx, cy, _ = _stone_base(img, d, s, tier)
    # Low stone keep
    body_top = cy - 18 - tier * 2
    body_bot = cy + 4
    shaded_rect(d, cx - 16, body_top, 32, body_bot - body_top, P.STONE, scale=s,
                outline=(40, 38, 36, 255), top_light=True)
    # Battlements
    for bx in range(-14, 15, 6):
        d.rectangle(((cx + bx) * s, (body_top - 4) * s,
                     (cx + bx + 4) * s, body_top * s), fill=P.STONE)
        d.rectangle(((cx + bx) * s, (body_top - 4) * s,
                     (cx + bx + 4) * s, (body_top - 3) * s), fill=P.STONE_LIGHT)
    # Door
    d.rectangle(((cx - 5) * s, (body_top + 8) * s, (cx + 5) * s, body_bot * s), fill=(40, 30, 20, 255))
    d.polygon([((cx - 5) * s, (body_top + 8) * s), ((cx + 5) * s, (body_top + 8) * s),
               (cx * s, (body_top + 4) * s)], fill=(40, 30, 20, 255))
    # Banner
    banner_color = P.KNIGHT_BLUE
    if tier >= 3:
        banner_color = P.BANNER_RED
    d.rectangle(((cx - 2) * s, (body_top + 10) * s, (cx + 2) * s, (body_top + 18) * s), fill=banner_color)
    # Gold trim at tier 3+
    if tier >= 3:
        d.line(((cx - 16) * s, (body_top + 2) * s, (cx + 16) * s, (body_top + 2) * s),
               fill=P.KNIGHT_GOLD, width=2 * s)
    # Spec: at tier 4 a bright golden shield on the face.
    if tier >= 4:
        shaded_circle(d, cx, body_top + 12, 5, P.KNIGHT_GOLD, scale=s,
                      shadow_tint=P.KNIGHT_GOLD_DARK, highlight_tint=(255, 240, 180, 255))


# --------------------------------------------------------------- Mage

def _mage(img, d, s, tier: int, state: str, frame: int) -> None:
    cx, cy, _ = _stone_base(img, d, s, tier)
    # Spire base
    body_top = cy - 22 - tier * 2
    body_bot = cy + 4
    shaded_rect(d, cx - 10, body_top, 20, body_bot - body_top, P.MAGE_ROBE, scale=s)
    # Vertical stripes
    for off in (-6, 0, 6):
        d.line(((cx + off) * s, body_top * s, (cx + off) * s, body_bot * s),
               fill=(*P.MAGE_PURPLE_DARK[:3], 220), width=1 * s)
    # Roof (tall cone)
    cone_h = 10 + tier * 3
    cone_top = body_top - cone_h
    pts = [(cx - 12, body_top), (cx + 12, body_top), (cx, cone_top)]
    outline_polygon(d, pts, P.MAGE_PURPLE, scale=s)
    # Orb at tip
    orb_pulse = 0 if state != "idle" else (frame * 1)
    orb_r = 3 + orb_pulse
    glow(img, cx, cone_top - 2, 6 + orb_pulse, P.MAGE_PURPLE_LIGHT, scale=s, alpha=180)
    shaded_circle(d, cx, cone_top - 2, orb_r, P.MAGE_PURPLE_LIGHT, scale=s,
                  shadow_tint=P.MAGE_PURPLE_DARK, highlight_tint=(255, 255, 255, 255))
    # Window (glowing arch)
    win_cx, win_cy = cx, body_top + 10
    d.ellipse(((win_cx - 4) * s, (win_cy - 4) * s, (win_cx + 4) * s, (win_cy + 4) * s),
              fill=(240, 220, 140, 255))
    d.rectangle(((win_cx - 4) * s, win_cy * s, (win_cx + 4) * s, (win_cy + 4) * s),
                fill=(240, 220, 140, 255))
    glow(img, win_cx, win_cy, 4, (255, 230, 150, 255), scale=s, alpha=160)
    # Attack flash
    if state == "attack":
        glow(img, cx, cone_top - 2, 8 + frame * 2, (255, 240, 220, 255), scale=s, alpha=220)
    # Gold trim at tier 3+
    if tier >= 3:
        d.line(((cx - 12) * s, (body_top + 2) * s, (cx + 12) * s, (body_top + 2) * s),
               fill=P.KNIGHT_GOLD, width=2 * s)


# ---------------------------------------------------------- Artillery

def _artillery(img, d, s, tier: int, state: str, frame: int) -> None:
    cx, cy, _ = _stone_base(img, d, s, tier)
    # Wheel + carriage
    body_top = cy - 8
    shaded_rect(d, cx - 16, body_top, 32, 14, P.WOOD, scale=s)
    # Iron reinforcement strap
    d.rectangle(((cx - 16) * s, (body_top + 6) * s, (cx + 16) * s, (body_top + 8) * s),
                fill=P.ARTILLERY_IRON_DARK)
    # Wheels
    for wx in (cx - 14, cx + 14):
        shaded_circle(d, wx, cy + 6, 5, P.WOOD_DARK, scale=s,
                      shadow_tint=(40, 25, 15, 255), highlight_tint=P.WOOD)
        # Spokes
        d.line(((wx - 4) * s, (cy + 6) * s, (wx + 4) * s, (cy + 6) * s),
               fill=P.ARTILLERY_IRON_DARK, width=1 * s)
        d.line((wx * s, (cy + 2) * s, wx * s, (cy + 10) * s),
               fill=P.ARTILLERY_IRON_DARK, width=1 * s)
    # Barrel (angled up)
    recoil = 0
    if state == "attack":
        recoil = [0, 3, 1][frame % 3]
    barrel_len = 18 + tier * 2
    barrel_w = 7
    # Draw tilted barrel using rotated rect via polygon.
    import math
    angle = math.radians(-35)
    bx = cx - 4 + recoil
    by = cy - 4
    # Build barrel polygon: base at (bx,by), extends toward angle.
    ex = bx + barrel_len * math.cos(angle)
    ey = by + barrel_len * math.sin(angle)
    nx = -math.sin(angle)
    ny = math.cos(angle)
    pts = [
        (bx + nx * barrel_w / 2, by + ny * barrel_w / 2),
        (bx - nx * barrel_w / 2, by - ny * barrel_w / 2),
        (ex - nx * barrel_w / 2, ey - ny * barrel_w / 2),
        (ex + nx * barrel_w / 2, ey + ny * barrel_w / 2),
    ]
    outline_polygon(d, [(int(p[0]), int(p[1])) for p in pts], P.ARTILLERY_BRONZE, scale=s)
    # Muzzle mouth
    d.ellipse(((int(ex) - 3) * s, (int(ey) - 3) * s, (int(ex) + 3) * s, (int(ey) + 3) * s),
              fill=(20, 20, 20, 255))
    # Muzzle flash on attack
    if state == "attack" and frame == 1:
        glow(img, int(ex), int(ey), 8, (255, 200, 80, 255), scale=s, alpha=230)
    # Tier decoration
    if tier >= 3:
        d.rectangle(((cx - 16) * s, (body_top) * s, (cx + 16) * s, (body_top + 2) * s), fill=P.KNIGHT_GOLD)
