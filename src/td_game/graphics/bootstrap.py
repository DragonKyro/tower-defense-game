"""Registers procedural sprite generators with the resource loader.

Called once at app startup. Kept separate from `resources.py` so that
module stays generator-agnostic.
"""
from __future__ import annotations

from td_game.core.resources import register_generator

from .procedural import (
    decor_gen,
    effect_gen,
    enemy_gen,
    hero_gen,
    projectile_gen,
    skill_gen,
    tile_gen,
    tower_gen,
)


def register_all() -> None:
    register_generator("tiles", tile_gen.generate)
    register_generator("towers", tower_gen.generate)
    register_generator("enemies", enemy_gen.generate)
    register_generator("heroes", hero_gen.generate)
    register_generator("projectiles", projectile_gen.generate)
    register_generator("effects", effect_gen.generate)
    register_generator("decor", decor_gen.generate)
    register_generator("skills", skill_gen.generate)
