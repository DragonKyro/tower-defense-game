"""Enemy paths: ordered waypoints with optional branching."""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Sequence


@dataclass(frozen=True)
class Waypoint:
    x: float
    y: float


@dataclass
class Path:
    """An ordered list of waypoints forming one route from spawn to exit.

    Branching: a path may declare that at waypoint index `i`, enemies
    switch to a *different* path with some probability. This is how
    Kingdom Rush–style fork maps work.
    """
    id: str
    waypoints: list[Waypoint]
    branches: dict[int, dict[str, float]] = field(default_factory=dict)  # {wp_index: {path_id: weight}}

    def length(self) -> float:
        total = 0.0
        for a, b in zip(self.waypoints, self.waypoints[1:]):
            total += math.hypot(b.x - a.x, b.y - a.y)
        return total

    def branch_pick(self, index: int, rng: random.Random) -> str | None:
        options = self.branches.get(index)
        if not options:
            return None
        total = sum(options.values()) or 1.0
        r = rng.random() * total
        acc = 0.0
        for pid, w in options.items():
            acc += w
            if r <= acc:
                return pid
        return None


class PathRegistry:
    """Level-scoped lookup table used by path_follower for branch resolution."""

    def __init__(self, paths: Sequence[Path]) -> None:
        self._by_id: dict[str, Path] = {p.id: p for p in paths}

    def get(self, path_id: str) -> Path:
        return self._by_id[path_id]

    def __iter__(self):
        return iter(self._by_id.values())
