"""Shared Pillow helpers for procedural generators.

Quality knobs:
  - SUPERSAMPLE: render at 2x and downsample with LANCZOS for smooth edges.
  - shaded_circle / shaded_ellipse: base + shadow crescent + highlight for volume.
  - soft_shadow: Gaussian-blurred ellipse beneath entities for grounding.
  - outline_shape: draws a dark shape 1-2px larger than the fill for crisp edges.
"""
from __future__ import annotations

from typing import Tuple

from PIL import Image, ImageDraw, ImageFilter

from td_game.core.constants import TILE_SIZE

SUPERSAMPLE = 2  # render at 2x, downsample for anti-aliased look


def new_canvas(size: int = TILE_SIZE, supersample: bool = True) -> Tuple[Image.Image, ImageDraw.ImageDraw, int]:
    """Return (img, draw, scale) where scale is the multiplier for all coordinates.

    When supersample=True we render at `size * SUPERSAMPLE` and the caller
    should `finalize(img, size)` to downsample. Draw helpers all accept
    `scale` and multiply coordinates internally.
    """
    if supersample:
        s = SUPERSAMPLE
        img = Image.new("RGBA", (size * s, size * s), (0, 0, 0, 0))
    else:
        s = 1
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img, "RGBA"), s


def finalize(img: Image.Image, target_size: int) -> Image.Image:
    """Downsample supersampled images; no-op if already target size."""
    if img.size == (target_size, target_size):
        return img
    return img.resize((target_size, target_size), Image.LANCZOS)


# --- shape helpers (coords/sizes are in source space; multiply by scale) ---


def shaded_circle(
    draw: ImageDraw.ImageDraw,
    cx: int,
    cy: int,
    r: int,
    base,
    scale: int = 1,
    shadow_tint: Tuple[int, int, int] | None = None,
    highlight_tint: Tuple[int, int, int] | None = None,
    outline=(20, 16, 12, 255),
) -> None:
    """A ball-like circle: outline + base + shadow crescent + highlight dot."""
    cx, cy, r = cx * scale, cy * scale, r * scale
    if outline:
        draw.ellipse((cx - r - scale, cy - r - scale, cx + r + scale, cy + r + scale), fill=outline)
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=base)
    if shadow_tint is None:
        shadow_tint = _darken(base, 0.55)
    # Shadow crescent: darker ellipse offset down-right.
    sh_r = int(r * 0.82)
    draw.ellipse((cx - sh_r + int(r * 0.25), cy - sh_r + int(r * 0.3),
                  cx + sh_r + int(r * 0.25), cy + sh_r + int(r * 0.3)),
                 fill=(*shadow_tint[:3], shadow_tint[3] if len(shadow_tint) > 3 else 110))
    # Base again on top to reveal only the crescent below.
    draw.ellipse((cx - r + scale, cy - r + scale, cx + r - scale, cy + r - scale), fill=base)
    # Highlight: small ellipse up-left.
    if highlight_tint is None:
        highlight_tint = _lighten(base, 0.55)
    hi_r = max(1, int(r * 0.35))
    hx = cx - int(r * 0.3)
    hy = cy - int(r * 0.35)
    draw.ellipse((hx - hi_r, hy - hi_r, hx + hi_r, hy + hi_r), fill=(*highlight_tint[:3], 200))


def shaded_rect(
    draw: ImageDraw.ImageDraw,
    x: int, y: int, w: int, h: int,
    base,
    scale: int = 1,
    outline=(20, 16, 12, 255),
    top_light: bool = True,
) -> None:
    """Rectangle with outline, darker band on the bottom, lighter band on top."""
    x, y, w, h = x * scale, y * scale, w * scale, h * scale
    if outline:
        draw.rectangle((x - scale, y - scale, x + w + scale, y + h + scale), fill=outline)
    draw.rectangle((x, y, x + w, y + h), fill=base)
    # Bottom shadow band.
    shadow = _darken(base, 0.7)
    band_h = max(2, h // 4)
    draw.rectangle((x, y + h - band_h, x + w, y + h), fill=(*shadow[:3], 180))
    # Top highlight band.
    if top_light:
        light = _lighten(base, 0.25)
        draw.rectangle((x, y, x + w, y + max(1, h // 6)), fill=(*light[:3], 180))


def outline_polygon(
    draw: ImageDraw.ImageDraw,
    points: list[tuple[int, int]],
    base,
    scale: int = 1,
    outline=(20, 16, 12, 255),
    shadow: bool = True,
) -> None:
    pts = [(p[0] * scale, p[1] * scale) for p in points]
    if outline:
        # Expand polygon a touch by drawing the same polygon as outlined path.
        draw.polygon(pts, fill=outline)
        # Inset fill.
        inset = _inset_polygon(pts, scale)
        if len(inset) >= 3:
            draw.polygon(inset, fill=base)
        else:
            draw.polygon(pts, fill=base)
    else:
        draw.polygon(pts, fill=base)
    if shadow:
        # Simple bottom-half darker overlay via a clipped polygon (approximate).
        sh = _darken(base, 0.6)
        # Split at vertical midpoint: overlay bottom 40%.
        ys = [p[1] for p in pts]
        ymin, ymax = min(ys), max(ys)
        mid = ymin + (ymax - ymin) * 0.55
        lower = [p for p in pts if p[1] >= mid]
        if len(lower) >= 3:
            draw.polygon(lower, fill=(*sh[:3], 110))


def _inset_polygon(points: list[tuple[int, int]], inset: int) -> list[tuple[int, int]]:
    """Naive inset: pull each point toward centroid by `inset` pixels."""
    if not points:
        return points
    cx = sum(p[0] for p in points) / len(points)
    cy = sum(p[1] for p in points) / len(points)
    out: list[tuple[int, int]] = []
    for px, py in points:
        dx = cx - px
        dy = cy - py
        d = (dx * dx + dy * dy) ** 0.5 or 1
        out.append((int(px + dx / d * inset), int(py + dy / d * inset)))
    return out


def soft_shadow(
    canvas: Image.Image,
    cx: int,
    cy: int,
    rx: int,
    ry: int,
    scale: int = 1,
    alpha: int = 110,
) -> None:
    """Paint a blurred ellipse onto canvas (used for ground shadows).

    Because PIL can't blur part of an image cheaply, we composite a
    separate blurred layer.
    """
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy, rx, ry = cx * scale, cy * scale, rx * scale, ry * scale
    d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=(0, 0, 0, alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(radius=max(1, 2 * scale)))
    canvas.alpha_composite(layer)


def glow(
    canvas: Image.Image,
    cx: int,
    cy: int,
    r: int,
    color,
    scale: int = 1,
    alpha: int = 160,
) -> None:
    """Soft radial glow (blurred circle) for magic / fire effects."""
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy, r = cx * scale, cy * scale, r * scale
    c = (*color[:3], alpha)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=c)
    layer = layer.filter(ImageFilter.GaussianBlur(radius=max(1, 3 * scale)))
    canvas.alpha_composite(layer)


def _darken(color, amount: float) -> tuple:
    r, g, b = color[:3]
    a = color[3] if len(color) > 3 else 255
    return (int(r * amount), int(g * amount), int(b * amount), a)


def _lighten(color, amount: float) -> tuple:
    r, g, b = color[:3]
    a = color[3] if len(color) > 3 else 255
    return (min(255, int(r + (255 - r) * amount)),
            min(255, int(g + (255 - g) * amount)),
            min(255, int(b + (255 - b) * amount)),
            a)


# Backwards-compat single-pixel helpers (still used by tile_gen for speckle).

def circle(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int, fill, outline=None, width: int = 1) -> None:
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill, outline=outline, width=width)


def rect(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, fill, outline=None, width: int = 1) -> None:
    draw.rectangle((x, y, x + w, y + h), fill=fill, outline=outline, width=width)


def drop_shadow(draw: ImageDraw.ImageDraw, cx: int, cy: int, rx: int, ry: int, color=(0, 0, 0, 90)) -> None:
    draw.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=color)


def parse_sprite_name(name: str) -> tuple[str, str, int]:
    """Parse '<kind>_<state>_<frame>' with sensible defaults.

    Accepts 'orc', 'orc_walk', 'orc_walk_2' — fills missing parts.
    """
    parts = name.split("_")
    kind = parts[0]
    state = "idle"
    frame = 0
    if len(parts) >= 2:
        state = parts[1]
    if len(parts) >= 3 and parts[2].isdigit():
        frame = int(parts[2])
    return kind, state, frame


# --- walk-cycle motion curves ---------------------------------------
# 6 frames per walk cycle so the character traverses body/leg positions
# in smaller, more continuous steps (vs. the old chunky 4-frame hop).
# Values are chosen so the body bobs by at most 1 source-pixel; legs swing
# by 1 source-pixel on each side. After 2x supersampling + LANCZOS
# downsample, motion reads as sub-pixel and smooths nicely.

WALK_FRAMES = 6

# Body vertical bob per frame (pre-supersample pixels).
_BODY_BOB = (0, 0, -1, -1, -1, 0)

# Front-leg horizontal offset (one leg forward, the other equal-and-opposite).
_LEG_STRIDE = (-1, 0, 1, 1, 0, -1)

# Arm swing — opposite phase to legs so the silhouette feels balanced.
_ARM_SWING = (1, 0, -1, -1, 0, 1)


def walk_bob(state: str, frame: int) -> int:
    if state == "walk":
        return _BODY_BOB[frame % WALK_FRAMES]
    if state == "idle":
        # Gentle breath: 2-frame ping-pong, very subtle.
        return 0 if frame % 2 == 0 else -1
    return 0


def walk_lean(state: str, frame: int) -> int:
    """Front-leg horizontal offset. Back leg is the negative."""
    if state == "walk":
        return _LEG_STRIDE[frame % WALK_FRAMES]
    return 0


def walk_arm(state: str, frame: int) -> int:
    if state == "walk":
        return _ARM_SWING[frame % WALK_FRAMES]
    return 0
