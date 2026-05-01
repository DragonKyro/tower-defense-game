"""Per-run game state shared across systems.

A single `GameState` is created when a level starts and destroyed when it
ends. Systems read and write it; the UI observes it via events.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .events import EventBus, GOLD_CHANGED, LIVES_CHANGED


@dataclass
class GameState:
    gold: int = 0
    lives: int = 0
    score: int = 0
    current_wave: int = 0   # 1-indexed once a wave starts; 0 means pre-game
    total_waves: int = 0
    game_speed: float = 1.0  # 1x / 2x toggle
    paused: bool = False
    won: bool = False
    lost: bool = False
    bus: EventBus = field(default_factory=EventBus)

    # --- gold --------------------------------------------------------

    def add_gold(self, amount: int, reason: str = "") -> None:
        self.gold += amount
        self.bus.publish(GOLD_CHANGED, gold=self.gold, delta=amount, reason=reason)

    def spend_gold(self, amount: int, reason: str = "") -> bool:
        if self.gold < amount:
            return False
        self.gold -= amount
        self.bus.publish(GOLD_CHANGED, gold=self.gold, delta=-amount, reason=reason)
        return True

    # --- lives -------------------------------------------------------

    def lose_life(self, amount: int = 1) -> None:
        self.lives = max(0, self.lives - amount)
        self.bus.publish(LIVES_CHANGED, lives=self.lives, delta=-amount)
        if self.lives == 0 and not self.won:
            self.lost = True
