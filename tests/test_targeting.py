"""Targeting-strategy unit tests (no Arcade needed)."""
from __future__ import annotations

from dataclasses import dataclass

from td_game.entities.towers.targeting import TargetMode, pick
from td_game.world.path import Path, Waypoint


@dataclass
class FakeTower:
    center_x: float
    center_y: float
    range: float = 200
    target_mode: TargetMode = TargetMode.FIRST
    can_hit_flying: bool = True
    can_hit_ground: bool = True


@dataclass
class FakeEnemy:
    center_x: float
    center_y: float
    max_hp: float
    hp: float
    alive: bool = True
    is_flying: bool = False
    current_path: Path | None = None
    wp_index: int = 0


def _path():
    return Path(id="main", waypoints=[Waypoint(0, 0), Waypoint(200, 0)])


def test_pick_first_chooses_most_progressed():
    p = _path()
    t = FakeTower(center_x=100, center_y=0)
    ahead = FakeEnemy(center_x=150, center_y=0, max_hp=10, hp=10, current_path=p)
    behind = FakeEnemy(center_x=50, center_y=0, max_hp=10, hp=10, current_path=p)
    assert pick(t, [behind, ahead]) is ahead


def test_pick_strongest_chooses_highest_max_hp():
    p = _path()
    t = FakeTower(center_x=100, center_y=0, target_mode=TargetMode.STRONGEST)
    weak = FakeEnemy(center_x=80, center_y=0, max_hp=10, hp=10, current_path=p)
    strong = FakeEnemy(center_x=120, center_y=0, max_hp=100, hp=100, current_path=p)
    assert pick(t, [weak, strong]) is strong


def test_ground_only_skips_flyers():
    p = _path()
    t = FakeTower(center_x=100, center_y=0, can_hit_flying=False)
    flyer = FakeEnemy(center_x=110, center_y=0, max_hp=10, hp=10, is_flying=True, current_path=p)
    ground = FakeEnemy(center_x=90, center_y=0, max_hp=10, hp=10, current_path=p)
    assert pick(t, [flyer, ground]) is ground
