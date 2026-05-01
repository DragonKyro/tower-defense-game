"""Smoke test: an enemy walks a straight path from start to end."""
from __future__ import annotations

from unittest.mock import MagicMock

from td_game.core.events import EventBus
from td_game.entities.enemies.base_enemy import BaseEnemy, EnemyStats
from td_game.entities.enemies.path_follower import PathFollower
from td_game.world.path import Path, PathRegistry, Waypoint


def test_straight_path_leaks_on_reach():
    path = Path(id="main", waypoints=[Waypoint(0, 0), Waypoint(100, 0)])
    reg = PathRegistry([path])
    follower = PathFollower(reg)

    bus = EventBus()
    # Sub with spy.
    leaked = []
    bus.subscribe("enemy_leaked", lambda **p: leaked.append(p))

    stats = EnemyStats(id="test", display_name="t", max_hp=10, speed=100)
    # Texture is unused in this unit test; use a magic mock to skip Arcade.
    enemy = BaseEnemy.__new__(BaseEnemy)
    BaseEnemy.__init__(enemy, stats, MagicMock(), bus=bus)

    follower.attach(enemy, "main")
    assert enemy.center_x == 0 and enemy.center_y == 0

    # One full second at 100 px/s should land exactly on the exit.
    follower.update(enemy, 1.2)

    assert leaked, "enemy should have reached the exit and emitted enemy_leaked"
