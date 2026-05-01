"""Asset loader / cache.

Load order for a sprite key `<category>/<name>.png`:
    1. assets/sprites/<category>/<name>.png  (shipped art; preferred)
    2. generated_sprites/<category>/<name>.png  (procedural cache)
    3. Generate via the appropriate procedural generator and cache it.

Game code should never read files directly — call `load_texture(...)` or
`load_animation(...)` here so real art can replace placeholders without
touching gameplay code.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Callable, Optional

import arcade
from PIL import Image

from .constants import GENERATED_SPRITES_DIR, SPRITES_DIR

ProceduralGenerator = Callable[[str], Image.Image]


_generators: dict[str, ProceduralGenerator] = {}


def register_generator(category: str, gen: ProceduralGenerator) -> None:
    """Register a procedural generator for a sprite category.

    The generator takes a bare name (e.g. 'orc_walk_0') and returns a PIL
    Image. Called when no file exists under either sprite root.
    """
    _generators[category] = gen


def _resolve_or_generate(category: str, name: str) -> Path:
    shipped = SPRITES_DIR / category / f"{name}.png"
    if shipped.is_file():
        return shipped
    cache = GENERATED_SPRITES_DIR / category / f"{name}.png"
    if cache.is_file():
        return cache
    gen = _generators.get(category)
    if gen is None:
        raise FileNotFoundError(
            f"No sprite {category}/{name}.png and no generator registered for '{category}'."
        )
    cache.parent.mkdir(parents=True, exist_ok=True)
    img = gen(name)
    img.save(cache)
    return cache


@lru_cache(maxsize=1024)
def load_texture(category: str, name: str) -> arcade.Texture:
    path = _resolve_or_generate(category, name)
    return arcade.load_texture(str(path))


def load_animation_frames(category: str, base_name: str, frame_count: int) -> list[arcade.Texture]:
    """Convenience: load `<base>_0`..`<base>_{n-1}`."""
    return [load_texture(category, f"{base_name}_{i}") for i in range(frame_count)]


def clear_cache() -> None:
    load_texture.cache_clear()
