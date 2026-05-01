"""Lightweight pub/sub event bus.

Subsystems publish events; observers subscribe. Keeps gameplay code from
having to know about UI, achievements, or statistics.

Usage:
    bus = EventBus()
    bus.subscribe("enemy_killed", my_handler)
    bus.publish("enemy_killed", enemy=enemy, by=tower)
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any, Callable

Handler = Callable[..., None]


class EventBus:
    def __init__(self) -> None:
        self._subs: dict[str, list[Handler]] = defaultdict(list)

    def subscribe(self, event: str, handler: Handler) -> None:
        self._subs[event].append(handler)

    def unsubscribe(self, event: str, handler: Handler) -> None:
        if handler in self._subs.get(event, ()):
            self._subs[event].remove(handler)

    def publish(self, event: str, **payload: Any) -> None:
        for handler in list(self._subs.get(event, ())):
            handler(**payload)

    def clear(self) -> None:
        self._subs.clear()


# Canonical event names (not enforced, but grep-friendly).
ENEMY_SPAWNED = "enemy_spawned"
ENEMY_KILLED = "enemy_killed"
ENEMY_LEAKED = "enemy_leaked"
WAVE_STARTED = "wave_started"
WAVE_CLEARED = "wave_cleared"
LEVEL_WON = "level_won"
LEVEL_LOST = "level_lost"
TOWER_BUILT = "tower_built"
TOWER_UPGRADED = "tower_upgraded"
TOWER_SOLD = "tower_sold"
HERO_DIED = "hero_died"
HERO_RESPAWNED = "hero_respawned"
SKILL_USED = "skill_used"
GOLD_CHANGED = "gold_changed"
LIVES_CHANGED = "lives_changed"
