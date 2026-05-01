"""Tower sprite generator with distinct per-tier silhouettes.

Sprite name format:
  '<family>_<tier>'                 static preview for menus
  '<family>_<tier>_<state>_<frame>' animated (state: idle / attack)

Per-tier design intent (stacked deltas so tier N includes N-1's extras):
  Tier 1 — plain structure, modest base platform.
  Tier 2 — reinforced silhouette: taller, extra plank/window detail,
           small banner, slightly richer palette.
  Tier 3 — ornate & tall: battlements or wider stone work, clear gold
           trim, secondary spire or larger wheels, braziers glowing.
  Tier 4 — specialization color: roof / barrel / robe painted in the
           spec accent so all four specs are visually distinct.
"""
from __future__ import annotations

import math

from PIL import Image, ImageDraw

from td_game.core.constants import TILE_SIZE

from . import palette as P
from ._util import (
    finalize,
    glow,
    new_canvas,
    outline_polygon,
    shaded_circle,
    shaded_rect,
    soft_shadow,
)


_STATES = {"idle", "attack"}


def _parse(name: str) -> tuple[str, int, str | None, str, int]:
    """Return (family, tier, spec, state, frame) from a sprite key.

    Accepts any of:
      'archer_2'                          (tier 2, no spec, idle, frame 0)
      'archer_2_idle_1'                   (tier 2, idle frame 1)
      'archer_4_sharpshooter'             (tier-4 spec)
      'archer_4_sharpshooter_attack_2'    (tier-4 spec + animated)
    """
    parts = name.split("_")
    family = parts[0]
    tier = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 1
    spec: str | None = None
    state = "idle"
    frame = 0
    # Parse middle tokens — could be spec or state.
    i = 2
    if i < len(parts) and parts[i] not in _STATES and not parts[i].isdigit():
        spec = parts[i]
        i += 1
    if i < len(parts) and parts[i] in _STATES:
        state = parts[i]
        i += 1
    if i < len(parts) and parts[i].isdigit():
        frame = int(parts[i])
    return family, tier, spec, state, frame


def generate(name: str) -> Image.Image:
    family, tier, spec, state, frame = _parse(name)
    img, d, s = new_canvas(TILE_SIZE)

    if family == "archer":
        _archer(img, d, s, tier, state, frame, spec)
    elif family == "barracks":
        _barracks(img, d, s, tier, state, frame, spec)
    elif family == "mage":
        _mage(img, d, s, tier, state, frame, spec)
    elif family == "artillery":
        _artillery(img, d, s, tier, state, frame, spec)
    else:
        _archer(img, d, s, tier, state, frame, spec)
    return finalize(img, TILE_SIZE)


# ------------------------------------------------------------- Platform

def _stone_base(img, d, s, tier: int) -> tuple[int, int, int]:
    cx = cy = TILE_SIZE // 2
    # Base platform grows with tier.
    platform_r = 16 + tier * 2
    soft_shadow(img, cx, cy + 14, platform_r + 2, 6, scale=s, alpha=130)
    # Outer dark ring.
    d.ellipse(((cx - platform_r - 1) * s, (cy + 8) * s,
               (cx + platform_r + 1) * s, (cy + 16) * s), fill=P.STONE_DARK)
    # Top stone slab.
    d.ellipse(((cx - platform_r) * s, (cy + 4) * s,
               (cx + platform_r) * s, (cy + 14) * s), fill=P.STONE)
    # Highlight.
    d.ellipse(((cx - platform_r + 2) * s, (cy + 5) * s,
               (cx + platform_r - 2) * s, (cy + 9) * s), fill=(*P.STONE_LIGHT[:3], 160))
    # Brick marks — more at higher tiers.
    step = 10 - tier
    for bx_off in range(-platform_r + 4, platform_r - 3, max(4, step)):
        d.line(((cx + bx_off) * s, (cy + 8) * s, (cx + bx_off) * s, (cy + 14) * s),
               fill=P.STONE_DARK, width=1 * s)
    # Gold trim ring at tier 3+.
    if tier >= 3:
        d.ellipse(((cx - platform_r) * s, (cy + 3) * s,
                   (cx + platform_r) * s, (cy + 6) * s),
                  outline=P.KNIGHT_GOLD, width=1 * s)
    return cx, cy, platform_r


# ------------------------------------------------------------- Archer

def _archer(img, d, s, tier: int, state: str, frame: int, spec: str | None = None) -> None:
    cx, cy, _ = _stone_base(img, d, s, tier)
    recoil = [-1, -2, 0][frame % 3] if state == "attack" else 0
    body_top = cy - (18 + tier * 3)
    body_bot = cy + 4
    # Per-spec overrides on tier 4 change the whole silhouette palette.
    archer_spec_body = {
        "sharpshooter": (60, 72, 96, 255),      # slate blue — marksman lodge
        "rapidfire": (140, 84, 40, 255),        # bright oak
        "ranger": (60, 92, 60, 255),            # forest green
        "crossbow": (88, 68, 52, 255),          # dark wood crossbow tower
    }
    body_color = P.WOOD
    if tier == 2:
        body_color = (156, 108, 66, 255)
    elif tier == 3:
        body_color = (168, 124, 76, 255)
    elif tier == 4:
        body_color = archer_spec_body.get(spec or "", (84, 52, 28, 255))
    shaded_rect(d, cx - 11, body_top, 22, body_bot - body_top, body_color, scale=s)

    # Horizontal planks every 5px (more per tier makes it read as sturdier).
    for py in range(body_top + 4, body_bot - 2, 5):
        d.line(((cx - 10) * s, py * s, (cx + 10) * s, py * s), fill=P.WOOD_DARK, width=1 * s)

    # Windows: more windows with higher tier.
    if tier == 1:
        d.rectangle(((cx - 2) * s, (body_top + 6) * s, (cx + 2) * s, (body_top + 12) * s), fill=(0, 0, 0, 255))
    elif tier == 2:
        d.rectangle(((cx - 7) * s, (body_top + 6) * s, (cx - 3) * s, (body_top + 11) * s), fill=(0, 0, 0, 255))
        d.rectangle(((cx + 3) * s, (body_top + 6) * s, (cx + 7) * s, (body_top + 11) * s), fill=(0, 0, 0, 255))
    elif tier >= 3:
        for ox in (-7, 0, 7):
            d.rectangle(((cx + ox - 2) * s, (body_top + 8) * s, (cx + ox + 2) * s, (body_top + 14) * s),
                        fill=(0, 0, 0, 255))

    # Roof (layered at higher tiers).
    roof_color = P.ARCHER_GREEN
    if tier == 4:
        roof_color = (186, 72, 60, 255)  # crimson spec roof
    roof_h = 8 + tier * 4
    roof_top = body_top - roof_h
    outline_polygon(d, [(cx - 14, body_top), (cx + 14, body_top), (cx, roof_top)], roof_color, scale=s)
    if tier >= 2:
        # Second layered roof peak behind — creates a more ornate profile.
        outline_polygon(d, [(cx - 10, body_top - roof_h // 2),
                            (cx + 10, body_top - roof_h // 2),
                            (cx, body_top - roof_h - 4)], roof_color, scale=s)
    # Flag with colour per tier.
    flag_color = P.BANNER_RED if tier < 4 else P.KNIGHT_GOLD
    d.rectangle(((cx) * s, (roof_top - 6) * s, (cx + 1) * s, roof_top * s), fill=P.WOOD_DARK)
    d.polygon([((cx + 1) * s, (roof_top - 6) * s), ((cx + 7) * s, (roof_top - 4) * s),
               ((cx + 1) * s, (roof_top - 2) * s)], fill=flag_color)

    # Archer head in the window (tier 2+ shows a crossbowman chest strap too).
    head_cx = cx + recoil
    shaded_circle(d, head_cx, body_top + 9, 3, (220, 190, 150, 255), scale=s,
                  shadow_tint=(160, 120, 90, 255), highlight_tint=(240, 215, 180, 255))

    # Gold trim band at tier 3+.
    if tier >= 3:
        d.line(((cx - 12) * s, (body_top + 2) * s, (cx + 12) * s, (body_top + 2) * s),
               fill=P.KNIGHT_GOLD, width=2 * s)
        d.line(((cx - 12) * s, (body_top + roof_h + 6) * s, (cx + 12) * s, (body_top + roof_h + 6) * s),
               fill=P.KNIGHT_GOLD, width=1 * s)
    # Tier-4 spec accents.
    if tier == 4:
        if spec == "sharpshooter":
            # Big scope/lens glow on the window.
            glow(img, cx, body_top + 10, 8, (210, 230, 255, 255), scale=s, alpha=220)
            d.ellipse(((cx - 3) * s, (body_top + 7) * s, (cx + 3) * s, (body_top + 13) * s),
                      fill=(20, 20, 30, 255))
            d.ellipse(((cx - 2) * s, (body_top + 8) * s, (cx + 2) * s, (body_top + 12) * s),
                      fill=(180, 220, 255, 255))
        elif spec == "rapidfire":
            # A fan of 3 ready arrows sticking out of the top.
            for ox in (-4, 0, 4):
                d.line(((cx + ox) * s, (body_top - 2) * s,
                        (cx + ox) * s, (body_top - 10) * s),
                       fill=P.ARROW, width=1 * s)
                d.polygon([((cx + ox - 2) * s, (body_top - 8) * s),
                           ((cx + ox + 2) * s, (body_top - 8) * s),
                           ((cx + ox) * s, (body_top - 12) * s)],
                          fill=P.ARROW_TIP)
        elif spec == "ranger":
            # Leafy canopy around the tower.
            for (ox, oy) in [(-12, -4), (12, -4), (0, -8), (-8, 2), (8, 2)]:
                shaded_circle(d, cx + ox, body_top + oy, 4, P.TREE_LEAVES, scale=s,
                              shadow_tint=P.TREE_LEAVES_DARK,
                              highlight_tint=P.TREE_LEAVES_LIGHT)
        elif spec == "crossbow":
            # Heavy crossbow mounted on the roof.
            d.rectangle(((cx - 10) * s, (body_top - 4) * s,
                         (cx + 10) * s, (body_top - 2) * s),
                        fill=P.WOOD_DARK)
            d.arc(((cx - 10) * s, (body_top - 10) * s,
                   (cx + 10) * s, (body_top + 2) * s),
                  start=180, end=0, fill=P.WOOD_DARK, width=2 * s)
            d.line(((cx - 8) * s, (body_top - 6) * s, (cx + 8) * s, (body_top - 6) * s),
                   fill=(220, 220, 220, 255), width=1 * s)
        # Fallback/shared: braziers.
        glow(img, cx - 12, cy + 2, 4, (255, 180, 60, 255), scale=s, alpha=180)
        glow(img, cx + 12, cy + 2, 4, (255, 180, 60, 255), scale=s, alpha=180)


# ----------------------------------------------------------- Barracks

def _barracks(img, d, s, tier: int, state: str, frame: int, spec: str | None = None) -> None:
    cx, cy, _ = _stone_base(img, d, s, tier)
    body_top = cy - (16 + tier * 4)
    body_bot = cy + 4
    wall_color = P.STONE
    if tier == 2:
        wall_color = (172, 168, 162, 255)
    elif tier >= 3:
        wall_color = (190, 184, 178, 255)
    shaded_rect(d, cx - 16, body_top, 32, body_bot - body_top, wall_color, scale=s,
                outline=(40, 38, 36, 255), top_light=True)
    # Battlements — more teeth with higher tier.
    teeth_step = 8 if tier < 3 else 6
    for bx in range(-14, 15, teeth_step):
        d.rectangle(((cx + bx) * s, (body_top - 4) * s,
                     (cx + bx + 4) * s, body_top * s), fill=wall_color)
        d.rectangle(((cx + bx) * s, (body_top - 4) * s,
                     (cx + bx + 4) * s, (body_top - 3) * s), fill=P.STONE_LIGHT)
    # Gate.
    d.rectangle(((cx - 5) * s, (body_top + 8) * s, (cx + 5) * s, body_bot * s), fill=(40, 30, 20, 255))
    d.polygon([((cx - 5) * s, (body_top + 8) * s), ((cx + 5) * s, (body_top + 8) * s),
               (cx * s, (body_top + 4) * s)], fill=(40, 30, 20, 255))
    # Central banner color per tier (visual read of upgrade path).
    banner_color = {1: P.KNIGHT_BLUE, 2: P.BANNER_RED, 3: (80, 160, 80, 255), 4: P.KNIGHT_GOLD}[tier]
    d.rectangle(((cx - 2) * s, (body_top + 10) * s, (cx + 2) * s, (body_top + 18) * s), fill=banner_color)
    # Corner turrets at tier 3+.
    if tier >= 3:
        for sx in (-16, 14):
            d.rectangle(((cx + sx) * s, (body_top - 8) * s,
                         (cx + sx + 2) * s, body_top * s), fill=wall_color)
            d.polygon([((cx + sx - 1) * s, (body_top - 8) * s),
                       ((cx + sx + 3) * s, (body_top - 8) * s),
                       ((cx + sx + 1) * s, (body_top - 14) * s)],
                      fill=P.BANNER_RED if tier < 4 else P.KNIGHT_GOLD)
    # Gold trim.
    if tier >= 3:
        d.line(((cx - 16) * s, (body_top + 2) * s, (cx + 16) * s, (body_top + 2) * s),
               fill=P.KNIGHT_GOLD, width=2 * s)
    # Tier-4 spec emblem on the gate face.
    if tier >= 4:
        shaded_circle(d, cx, body_top + 14, 5, P.KNIGHT_GOLD, scale=s,
                      shadow_tint=P.KNIGHT_GOLD_DARK, highlight_tint=(255, 240, 180, 255))
        if spec == "paladins":
            # Radiant halo behind the keep.
            glow(img, cx, body_top + 2, 14, (255, 240, 160, 255), scale=s, alpha=160)
        elif spec == "knights":
            # Crossed lances over the gate.
            d.line(((cx - 10) * s, (body_top + 4) * s, (cx + 10) * s, (body_top + 22) * s),
                   fill=P.KNIGHT_STEEL_LIGHT, width=2 * s)
            d.line(((cx + 10) * s, (body_top + 4) * s, (cx - 10) * s, (body_top + 22) * s),
                   fill=P.KNIGHT_STEEL_LIGHT, width=2 * s)
        elif spec == "assassins":
            # Dark-banner overlay, covered windows.
            arcade_black = (22, 22, 28, 180)
            d.rectangle(((cx - 16) * s, body_top * s,
                         (cx + 16) * s, (body_top + 6) * s), fill=arcade_black)
            d.polygon([((cx - 4) * s, (body_top + 14) * s),
                       ((cx + 4) * s, (body_top + 14) * s),
                       (cx * s, (body_top + 18) * s)], fill=(60, 20, 20, 255))
        elif spec == "pikemen":
            # Pikes sticking up above the battlements.
            for ox in (-10, -4, 4, 10):
                d.rectangle(((cx + ox) * s, (body_top - 12) * s,
                             (cx + ox + 1) * s, (body_top - 4) * s),
                            fill=P.WOOD_DARK)
                d.polygon([((cx + ox - 1) * s, (body_top - 12) * s),
                           ((cx + ox + 2) * s, (body_top - 12) * s),
                           ((cx + ox) * s, (body_top - 17) * s)],
                          fill=P.KNIGHT_STEEL_LIGHT)


# ------------------------------------------------------------- Mage

def _mage(img, d, s, tier: int, state: str, frame: int, spec: str | None = None) -> None:
    cx, cy, _ = _stone_base(img, d, s, tier)
    body_top = cy - (20 + tier * 3)
    body_bot = cy + 4
    robe_color = P.MAGE_ROBE
    if tier == 2:
        robe_color = (90, 60, 140, 255)
    elif tier == 3:
        robe_color = (108, 72, 164, 255)
    elif tier == 4:
        robe_color = (46, 30, 80, 255)  # arcane deep purple
    shaded_rect(d, cx - 10, body_top, 20, body_bot - body_top, robe_color, scale=s)
    for off in (-6, 0, 6):
        d.line(((cx + off) * s, body_top * s, (cx + off) * s, body_bot * s),
               fill=(*P.MAGE_PURPLE_DARK[:3], 220), width=1 * s)
    # Cone height / style scales with tier.
    cone_h = 10 + tier * 4
    cone_top = body_top - cone_h
    cone_color = P.MAGE_PURPLE if tier < 4 else (180, 60, 180, 255)
    outline_polygon(d, [(cx - 12, body_top), (cx + 12, body_top), (cx, cone_top)], cone_color, scale=s)
    if tier >= 2:
        # Stars on the spire.
        for (ox, oy) in [(-4, -cone_h + 14), (4, -cone_h + 10), (0, -cone_h + 6)]:
            d.ellipse(((cx + ox - 1) * s, (body_top + oy - 1) * s,
                       (cx + ox + 1) * s, (body_top + oy + 1) * s),
                      fill=(255, 240, 200, 230))
    if tier >= 3:
        # Secondary spires left & right.
        for sx in (-10, 10):
            outline_polygon(d,
                [(cx + sx - 4, body_top),
                 (cx + sx + 4, body_top),
                 (cx + sx, body_top - cone_h // 2)],
                cone_color, scale=s)
    # Orb + glow grow with tier.
    orb_r = 3 + tier
    orb_pulse = 0 if state != "idle" else frame
    glow(img, cx, cone_top - 2, 6 + tier + orb_pulse, P.MAGE_PURPLE_LIGHT, scale=s, alpha=180)
    shaded_circle(d, cx, cone_top - 2, orb_r, P.MAGE_PURPLE_LIGHT, scale=s,
                  shadow_tint=P.MAGE_PURPLE_DARK, highlight_tint=(255, 255, 255, 255))
    # Window.
    win_cx, win_cy = cx, body_top + 10
    win_color = (240, 220, 140, 255) if tier < 4 else (210, 160, 255, 255)
    d.ellipse(((win_cx - 4) * s, (win_cy - 4) * s, (win_cx + 4) * s, (win_cy + 4) * s), fill=win_color)
    d.rectangle(((win_cx - 4) * s, win_cy * s, (win_cx + 4) * s, (win_cy + 4) * s), fill=win_color)
    glow(img, win_cx, win_cy, 4, win_color, scale=s, alpha=160)
    if state == "attack":
        glow(img, cx, cone_top - 2, 8 + frame * 2, (255, 240, 220, 255), scale=s, alpha=220)
    if tier >= 3:
        d.line(((cx - 12) * s, (body_top + 2) * s, (cx + 12) * s, (body_top + 2) * s),
               fill=P.KNIGHT_GOLD, width=2 * s)
    # Mage tier-4 spec accents.
    if tier == 4:
        if spec == "arcane":
            # Swirling arcane runes + bright white core.
            glow(img, cx, cone_top - 2, 14, (255, 255, 255, 255), scale=s, alpha=220)
            for (ox, oy) in [(-10, -cone_h - 6), (10, -cone_h - 6), (0, -cone_h - 10)]:
                d.point(((cx + ox) * s, (body_top + oy) * s), fill=(255, 255, 255, 255))
        elif spec == "necromancer":
            # Skull above the spire + green aura.
            glow(img, cx, cone_top - 8, 10, (120, 220, 160, 255), scale=s, alpha=180)
            shaded_circle(d, cx, cone_top - 10, 4, P.BONE, scale=s,
                          shadow_tint=(180, 170, 140, 255),
                          highlight_tint=(255, 250, 230, 255))
            d.ellipse(((cx - 2) * s, (cone_top - 11) * s,
                       (cx - 1) * s, (cone_top - 9) * s), fill=(0, 0, 0, 255))
            d.ellipse(((cx + 1) * s, (cone_top - 11) * s,
                       (cx + 2) * s, (cone_top - 9) * s), fill=(0, 0, 0, 255))
        elif spec == "pyromancer":
            # Flames climbing the spire.
            for (ox, oy, r, c) in [(-6, 4, 5, (255, 120, 40, 255)),
                                   (6, 2, 5, (255, 160, 60, 255)),
                                   (0, -4, 6, (255, 200, 80, 255))]:
                glow(img, cx + ox, cone_top + oy, r, c, scale=s, alpha=200)
        elif spec == "druid":
            # Leafy vines wrapping the tower.
            for (ox, oy) in [(-10, -4), (8, -6), (-4, -12), (6, -14), (0, 2)]:
                shaded_circle(d, cx + ox, body_top + oy, 3, P.TREE_LEAVES, scale=s,
                              shadow_tint=P.TREE_LEAVES_DARK,
                              highlight_tint=P.TREE_LEAVES_LIGHT)


# ---------------------------------------------------------- Artillery

def _artillery(img, d, s, tier: int, state: str, frame: int, spec: str | None = None) -> None:
    cx, cy, _ = _stone_base(img, d, s, tier)
    body_top = cy - 8
    # Carriage grows darker/sturdier per tier.
    carriage_color = P.WOOD
    if tier == 2:
        carriage_color = (122, 78, 46, 255)
    elif tier == 3:
        carriage_color = (82, 52, 32, 255)
    elif tier == 4:
        carriage_color = (48, 32, 20, 255)
    shaded_rect(d, cx - 16, body_top, 32, 14, carriage_color, scale=s)
    d.rectangle(((cx - 16) * s, (body_top + 6) * s, (cx + 16) * s, (body_top + 8) * s), fill=P.ARTILLERY_IRON_DARK)
    # Wheels grow in size with tier.
    wheel_r = 5 + (tier - 1)
    for wx in (cx - 14, cx + 14):
        shaded_circle(d, wx, cy + 6, wheel_r, P.WOOD_DARK, scale=s,
                      shadow_tint=(40, 25, 15, 255), highlight_tint=P.WOOD)
        d.line(((wx - wheel_r) * s, (cy + 6) * s, (wx + wheel_r) * s, (cy + 6) * s),
               fill=P.ARTILLERY_IRON_DARK, width=1 * s)
        d.line((wx * s, (cy + 6 - wheel_r) * s, wx * s, (cy + 6 + wheel_r) * s),
               fill=P.ARTILLERY_IRON_DARK, width=1 * s)
    # Barrel dims scale with tier.
    recoil = [0, 3, 1][frame % 3] if state == "attack" else 0
    barrel_len = 16 + tier * 3
    barrel_w = 6 + (tier - 1)
    angle = math.radians(-35)
    bx = cx - 4 + recoil
    by = cy - 4
    ex = bx + barrel_len * math.cos(angle)
    ey = by + barrel_len * math.sin(angle)
    nx = -math.sin(angle)
    ny = math.cos(angle)
    barrel_color = P.ARTILLERY_BRONZE
    if tier == 4:
        barrel_color = (156, 156, 180, 255)  # silvered/iron spec barrel
    pts = [
        (bx + nx * barrel_w / 2, by + ny * barrel_w / 2),
        (bx - nx * barrel_w / 2, by - ny * barrel_w / 2),
        (ex - nx * barrel_w / 2, ey - ny * barrel_w / 2),
        (ex + nx * barrel_w / 2, ey + ny * barrel_w / 2),
    ]
    outline_polygon(d, [(int(p[0]), int(p[1])) for p in pts], barrel_color, scale=s)
    # Banded reinforcement rings along the barrel at tier 2+.
    if tier >= 2:
        for t in (0.35, 0.7):
            mx = bx + (ex - bx) * t
            my = by + (ey - by) * t
            d.line(((mx + nx * (barrel_w / 2 + 1)) * s, (my + ny * (barrel_w / 2 + 1)) * s,
                    (mx - nx * (barrel_w / 2 + 1)) * s, (my - ny * (barrel_w / 2 + 1)) * s),
                   fill=P.ARTILLERY_IRON_DARK, width=2 * s)
    # Muzzle.
    d.ellipse(((int(ex) - 3) * s, (int(ey) - 3) * s, (int(ex) + 3) * s, (int(ey) + 3) * s),
              fill=(20, 20, 20, 255))
    if state == "attack" and frame == 1:
        glow(img, int(ex), int(ey), 8 + tier * 2, (255, 200, 80, 255), scale=s, alpha=230)
    # Gold plate at tier 3+.
    if tier >= 3:
        d.rectangle(((cx - 16) * s, body_top * s, (cx + 16) * s, (body_top + 2) * s), fill=P.KNIGHT_GOLD)
    # Tier-4 spec accents.
    if tier == 4:
        if spec == "mortar":
            # Oversized muzzle mouth.
            d.ellipse(((int(ex) - 6) * s, (int(ey) - 6) * s,
                       (int(ex) + 6) * s, (int(ey) + 6) * s),
                      fill=(20, 20, 20, 255))
            # Pile of ammo.
            for (ox, oy) in [(12, 6), (10, 6), (11, 3)]:
                shaded_circle(d, cx - ox, cy + oy, 3, P.CANNONBALL, scale=s,
                              shadow_tint=(20, 20, 24, 255), highlight_tint=P.CANNONBALL_HI)
        elif spec == "tesla":
            # Tall lightning rod + arcing sparks.
            d.rectangle(((cx - 1) * s, (cy - 30) * s, (cx + 1) * s, (cy - 4) * s),
                        fill=P.KNIGHT_STEEL_LIGHT)
            d.ellipse(((cx - 3) * s, (cy - 34) * s, (cx + 3) * s, (cy - 28) * s),
                      fill=(180, 220, 255, 255))
            glow(img, cx, cy - 30, 6, (160, 210, 255, 255), scale=s, alpha=200)
            for (x1, y1, x2, y2) in [(-6, -24, 6, -18), (8, -12, -4, -8)]:
                d.line(((cx + x1) * s, (cy + y1) * s, (cx + x2) * s, (cy + y2) * s),
                       fill=(210, 240, 255, 255), width=1 * s)
        elif spec == "flamethrower":
            # Flared nozzle + jet of flame.
            d.polygon([((int(ex) - 2) * s, (int(ey) - 4) * s),
                       ((int(ex) + 8) * s, (int(ey) - 8) * s),
                       ((int(ex) + 8) * s, (int(ey) + 8) * s),
                       ((int(ex) - 2) * s, (int(ey) + 4) * s)],
                      fill=P.ARTILLERY_BRONZE_DARK)
            glow(img, int(ex) + 12, int(ey), 8, (255, 140, 50, 255), scale=s, alpha=200)
            glow(img, int(ex) + 20, int(ey) - 2, 6, (255, 200, 80, 255), scale=s, alpha=180)
        elif spec == "rocket":
            # Four-barrel rocket rack replaces the single barrel.
            for (ox, oy) in [(-4, -2), (-4, 2), (2, -2), (2, 2)]:
                d.rectangle(((cx - 6 + ox) * s, (cy - 8 + oy) * s,
                             (cx + 10 + ox) * s, (cy - 6 + oy) * s),
                            fill=P.ARTILLERY_BRONZE)
            for (ox, oy) in [(10, -2), (10, 2)]:
                d.ellipse(((cx + ox - 2) * s, (cy - 9 + oy) * s,
                           (cx + ox + 2) * s, (cy - 5 + oy) * s),
                          fill=(40, 40, 40, 255))
        else:
            for (ox, oy) in [(12, 6), (10, 6), (11, 3)]:
                shaded_circle(d, cx - ox, cy + oy, 2, P.CANNONBALL, scale=s,
                              shadow_tint=(20, 20, 24, 255), highlight_tint=P.CANNONBALL_HI)
