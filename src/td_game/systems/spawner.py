"""Instantiates enemies onto paths.

Consumed by wave_manager which drives the spawn timing.
"""
from __future__ import annotations

import random
from typing import TYPE_CHECKING

from td_game.core.events import ENEMY_SPAWNED
from td_game.entities.enemies.enemies import create_enemy
from td_game.entities.enemies.path_follower import PathFollower

if TYPE_CHECKING:
    from td_game.world.path import PathRegistry


class Spawner:
    def __init__(self, registry: "PathRegistry", bus, rng: random.Random | None = None) -> None:
        self.registry = registry
        self.bus = bus
        self.follower = PathFollower(registry, rng or random.Random())

    def spawn(self, enemy_id: str, path_id: str, scene):
        enemy = create_enemy(enemy_id, bus=self.bus)
        self.follower.attach(enemy, path_id)
        scene.spawn_enemy(enemy)
        self.bus.publish(ENEMY_SPAWNED, enemy=enemy)
        return enemy

    def update_followers(self, enemies, dt: float) -> None:
        for e in enemies:
            if e.alive:
                self.follower.update(e, dt)
