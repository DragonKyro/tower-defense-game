"""Waypoint traversal with branching support.

Kept separate from `BaseEnemy` so non-enemy path-followers (e.g., a
scripted animation) can reuse the math.
"""
from __future__ import annotations

import math
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from td_game.world.path import PathRegistry
    from .base_enemy import BaseEnemy


class PathFollower:
    def __init__(self, registry: "PathRegistry", rng: random.Random | None = None) -> None:
        self.registry = registry
        self.rng = rng or random.Random()

    def attach(self, enemy: "BaseEnemy", path_id: str) -> None:
        path = self.registry.get(path_id)
        enemy.current_path = path
        enemy.wp_index = 0
        start = path.waypoints[0]
        enemy.center_x = start.x
        enemy.center_y = start.y

    def update(self, enemy: "BaseEnemy", dt: float) -> None:
        if not enemy.alive or enemy.current_path is None:
            return
        # Locked in melee — stand and fight instead of walking past.
        if enemy.engaged_by is not None and getattr(enemy.engaged_by, "alive", False):
            return
        path = enemy.current_path
        step = enemy.speed * dt
        if step <= 0:
            return
        remaining = step
        while remaining > 0 and enemy.alive:
            # Check branch at current wp first.
            new_path_id = path.branch_pick(enemy.wp_index, self.rng)
            if new_path_id is not None:
                path = self.registry.get(new_path_id)
                enemy.current_path = path
                enemy.wp_index = 0
            # Next waypoint.
            next_idx = enemy.wp_index + 1
            if next_idx >= len(path.waypoints):
                enemy.on_leak()
                return
            target = path.waypoints[next_idx]
            dx = target.x - enemy.center_x
            dy = target.y - enemy.center_y
            dist = math.hypot(dx, dy)
            if dist <= remaining:
                enemy.center_x = target.x
                enemy.center_y = target.y
                enemy.wp_index = next_idx
                remaining -= dist
            else:
                enemy.center_x += dx / dist * remaining
                enemy.center_y += dy / dist * remaining
                remaining = 0
            # Facing: request a horizontal flip; Entity smooths it over a few frames.
            if dx < -0.1:
                enemy.face(-1)
            elif dx > 0.1:
                enemy.face(1)
