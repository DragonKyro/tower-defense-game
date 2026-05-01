"""Spatial queries: range / AoE checks.

For the framework scaffold these are O(n) brute force; good enough for
hundreds of entities. Swap in a spatial hash later if needed.
"""
from __future__ import annotations

from typing import Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from td_game.entities.entity import Entity


def in_radius(cx: float, cy: float, radius: float, entities: Iterable["Entity"]) -> list["Entity"]:
    r2 = radius * radius
    out: list["Entity"] = []
    for e in entities:
        if not e.alive:
            continue
        dx = e.center_x - cx
        dy = e.center_y - cy
        if dx * dx + dy * dy <= r2:
            out.append(e)
    return out


def nearest(cx: float, cy: float, entities: Iterable["Entity"]):
    best = None
    best_d2 = float("inf")
    for e in entities:
        if not e.alive:
            continue
        dx = e.center_x - cx
        dy = e.center_y - cy
        d2 = dx * dx + dy * dy
        if d2 < best_d2:
            best = e
            best_d2 = d2
    return best
