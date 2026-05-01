"""Geometric helpers for drawing paths as smooth ribbons.

Used by the game scene to replace the old grid-aligned path tiles with
a continuous curved polygon that looks hand-drawn.
"""
from __future__ import annotations

import math
from typing import Iterable, Sequence


Point = tuple[float, float]


def smooth_waypoints(waypoints: Sequence, iterations: int = 3) -> list[Point]:
    """Corner-cutting (Chaikin) subdivision.

    Produces a list of (x, y) points that round out right-angle grid
    corners while still passing near the original waypoints.
    """
    pts: list[Point] = [(w.x, w.y) for w in waypoints]
    for _ in range(iterations):
        if len(pts) < 3:
            break
        new_pts: list[Point] = [pts[0]]
        for i in range(len(pts) - 1):
            ax, ay = pts[i]
            bx, by = pts[i + 1]
            # Two inner points at 25% and 75%.
            new_pts.append((ax * 0.75 + bx * 0.25, ay * 0.75 + by * 0.25))
            new_pts.append((ax * 0.25 + bx * 0.75, ay * 0.25 + by * 0.75))
        new_pts.append(pts[-1])
        pts = new_pts
    return pts


def nearest_point_on_curves(curves: Sequence[Sequence[Point]], x: float, y: float) -> Point:
    """Return the closest (x, y) on any of the supplied smoothed curves.

    Used to auto-place a barracks rally on the path the enemies take.
    """
    best: Point = (x, y)
    best_d2 = float("inf")
    for curve in curves:
        for px, py in curve:
            dx = px - x
            dy = py - y
            d2 = dx * dx + dy * dy
            if d2 < best_d2:
                best = (px, py)
                best_d2 = d2
    return best


def path_ribbon(points: Sequence[Point], half_width: float) -> list[Point]:
    """Build a closed polygon (left edge + right edge reversed) around a polyline.

    At each point we offset perpendicular to the averaged direction of the
    adjacent segments, which gives smooth joints without overshoot.
    """
    n = len(points)
    if n < 2:
        return []
    left: list[Point] = []
    right: list[Point] = []
    for i in range(n):
        if i == 0:
            dx = points[1][0] - points[0][0]
            dy = points[1][1] - points[0][1]
        elif i == n - 1:
            dx = points[i][0] - points[i - 1][0]
            dy = points[i][1] - points[i - 1][1]
        else:
            dx = points[i + 1][0] - points[i - 1][0]
            dy = points[i + 1][1] - points[i - 1][1]
        mag = math.hypot(dx, dy) or 1.0
        nx = -dy / mag
        ny = dx / mag
        px, py = points[i]
        left.append((px + nx * half_width, py + ny * half_width))
        right.append((px - nx * half_width, py - ny * half_width))
    return left + list(reversed(right))
