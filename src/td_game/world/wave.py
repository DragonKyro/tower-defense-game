"""Wave definitions: spawn orders for a single wave."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SpawnOrder:
    enemy_id: str          # key into data.enemies.ENEMIES
    count: int
    interval: float        # seconds between spawns in this group
    delay: float = 0.0     # seconds before this group starts, relative to wave start
    path_id: str = "main"  # which path they spawn onto


@dataclass(frozen=True)
class Wave:
    name: str
    spawns: tuple[SpawnOrder, ...]
    reward_gold: int = 0           # bonus awarded on wave clear
    inter_wave_delay: float = 6.0  # time until next wave auto-starts (player can fast-call)

    def total_enemy_count(self) -> int:
        return sum(o.count for o in self.spawns)
