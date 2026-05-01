"""Wires gold earning + life loss into the EventBus.

Attach once at scene start; unsubscribe at teardown.
"""
from __future__ import annotations

from td_game.core.events import ENEMY_KILLED, ENEMY_LEAKED


class EconomySystem:
    def __init__(self, state) -> None:
        self.state = state
        state.bus.subscribe(ENEMY_KILLED, self._on_kill)
        state.bus.subscribe(ENEMY_LEAKED, self._on_leak)

    def _on_kill(self, enemy, bounty: int = 0, **_) -> None:
        if bounty:
            self.state.add_gold(bounty, reason="kill")

    def _on_leak(self, enemy, lives_cost: int = 1, **_) -> None:
        self.state.lose_life(lives_cost)
