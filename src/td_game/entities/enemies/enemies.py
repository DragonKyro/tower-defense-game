"""Concrete enemy factory.

All enemy *behavior* differences funnel through `EnemyStats`; if you
need a new behavior (e.g., a boss that spawns adds on death), subclass
`BaseEnemy` here and register it in `create_enemy`.
"""
from __future__ import annotations

from td_game.core.resources import load_texture
from td_game.data.enemies import ENEMIES

from .base_enemy import BaseEnemy, EnemyStats


def create_enemy(enemy_id: str, bus=None) -> BaseEnemy:
    stats: EnemyStats = ENEMIES[enemy_id]
    texture = load_texture("enemies", stats.sprite)
    return BaseEnemy(stats, texture, bus=bus)
