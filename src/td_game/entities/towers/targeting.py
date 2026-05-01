"""Targeting strategies.

A tower owns a TargetingStrategy. Strategies are stateless and pure.
Called with `(tower, enemies)` and must return the chosen enemy or None.
"""
from __future__ import annotations

import math
from enum import Enum, auto
from typing import TYPE_CHECKING, Callable, Iterable, Optional

if TYPE_CHECKING:
    from td_game.entities.enemies.base_enemy import BaseEnemy
    from .base_tower import BaseTower


class TargetMode(Enum):
    FIRST = auto()      # furthest along its path
    LAST = auto()       # least far along its path
    STRONGEST = auto()  # highest max_hp
    WEAKEST = auto()    # lowest current hp
    CLOSEST = auto()


def _in_range(tower: "BaseTower", enemy: "BaseEnemy") -> bool:
    dx = enemy.center_x - tower.center_x
    dy = enemy.center_y - tower.center_y
    return dx * dx + dy * dy <= tower.range * tower.range


def _valid(tower: "BaseTower", enemy: "BaseEnemy") -> bool:
    if not enemy.alive:
        return False
    if enemy.is_flying and not tower.can_hit_flying:
        return False
    if (not enemy.is_flying) and (not tower.can_hit_ground):
        return False
    return _in_range(tower, enemy)


def pick(tower: "BaseTower", enemies: Iterable["BaseEnemy"]) -> "Optional[BaseEnemy]":
    candidates = [e for e in enemies if _valid(tower, e)]
    if not candidates:
        return None
    mode = tower.target_mode
    if mode is TargetMode.FIRST:
        return max(candidates, key=_progress)
    if mode is TargetMode.LAST:
        return min(candidates, key=_progress)
    if mode is TargetMode.STRONGEST:
        return max(candidates, key=lambda e: e.max_hp)
    if mode is TargetMode.WEAKEST:
        return min(candidates, key=lambda e: e.hp)
    if mode is TargetMode.CLOSEST:
        return min(candidates, key=lambda e: (e.center_x - tower.center_x) ** 2 + (e.center_y - tower.center_y) ** 2)
    return candidates[0]


def _progress(enemy: "BaseEnemy") -> float:
    """Rough along-path progress: waypoint index + fractional distance to next."""
    path = enemy.current_path
    if path is None:
        return 0.0
    idx = enemy.wp_index
    if idx + 1 >= len(path.waypoints):
        return float(idx)
    a = path.waypoints[idx]
    b = path.waypoints[idx + 1]
    seg = math.hypot(b.x - a.x, b.y - a.y) or 1.0
    done = math.hypot(enemy.center_x - a.x, enemy.center_y - a.y)
    return idx + done / seg
