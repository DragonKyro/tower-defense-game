"""Drives wave progression.

State machine:
  IDLE -> IN_WAVE (on start_wave) -> BETWEEN (all spawned and cleared)
  -> IN_WAVE (on next) -> ... -> DONE (last wave cleared)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING

from td_game.core.events import LEVEL_WON, WAVE_CLEARED, WAVE_STARTED

if TYPE_CHECKING:
    from td_game.core.game_state import GameState
    from td_game.world.wave import Wave

    from .spawner import Spawner


class WaveState(Enum):
    IDLE = auto()
    IN_WAVE = auto()
    BETWEEN = auto()
    DONE = auto()


@dataclass
class _GroupProgress:
    remaining: int
    since_last: float = 0.0
    delay_left: float = 0.0


class WaveManager:
    def __init__(self, waves: "tuple[Wave, ...]", spawner: "Spawner", state: "GameState") -> None:
        self.waves = waves
        self.spawner = spawner
        self.state = state
        self.state.total_waves = len(waves)
        self.phase: WaveState = WaveState.IDLE
        self._wave_index: int = -1
        self._groups: list[_GroupProgress] = []
        self._between_timer: float = 0.0
        self._spawned_total: int = 0
        self.scene = None

    def bind(self, scene) -> None:
        self.scene = scene

    # --- queries -----------------------------------------------------

    @property
    def current_wave_index(self) -> int:
        return self._wave_index

    def next_wave(self) -> "Wave | None":
        idx = self._wave_index + 1
        if idx < len(self.waves):
            return self.waves[idx]
        return None

    @property
    def between_timer(self) -> float:
        """Seconds remaining in the inter-wave breather (0 if not in BETWEEN)."""
        return max(0.0, self._between_timer) if self.phase is WaveState.BETWEEN else 0.0

    def can_call_next_early(self) -> bool:
        return self.phase is WaveState.BETWEEN and self.next_wave() is not None

    def call_next_wave_early(self) -> int:
        """Skip the inter-wave timer and start the next wave immediately.

        Returns a gold bonus proportional to the skipped time (KR-style).
        Caller is responsible for adding the gold to `state`.
        """
        if not self.can_call_next_early():
            return 0
        bonus = int(self._between_timer * 2) + 5  # flat + proportional
        self._between_timer = 0.0
        self.start_next_wave()
        return bonus

    # --- control -----------------------------------------------------

    def start_next_wave(self) -> None:
        if self.phase is WaveState.IN_WAVE or self.phase is WaveState.DONE:
            return
        self._wave_index += 1
        if self._wave_index >= len(self.waves):
            self.phase = WaveState.DONE
            self.state.won = True
            self.state.bus.publish(LEVEL_WON)
            return
        wave = self.waves[self._wave_index]
        self._groups = [_GroupProgress(remaining=o.count, delay_left=o.delay) for o in wave.spawns]
        self._spawned_total = 0
        self.phase = WaveState.IN_WAVE
        self.state.current_wave = self._wave_index + 1
        self.state.bus.publish(WAVE_STARTED, index=self._wave_index, wave=wave)

    # --- per-frame ---------------------------------------------------

    def update(self, dt: float, active_enemy_count: int) -> None:
        if self.phase is WaveState.IN_WAVE:
            self._tick_spawns(dt)
            if self._all_groups_done() and active_enemy_count == 0:
                self._on_wave_cleared()
        elif self.phase is WaveState.BETWEEN:
            self._between_timer -= dt
            if self._between_timer <= 0:
                self.start_next_wave()

    def _tick_spawns(self, dt: float) -> None:
        wave = self.waves[self._wave_index]
        for group, order in zip(self._groups, wave.spawns):
            if group.remaining <= 0:
                continue
            if group.delay_left > 0:
                group.delay_left -= dt
                continue
            group.since_last += dt
            while group.since_last >= order.interval and group.remaining > 0:
                group.since_last -= order.interval
                group.remaining -= 1
                self._spawned_total += 1
                if self.scene is not None:
                    self.spawner.spawn(order.enemy_id, order.path_id, self.scene)

    def _all_groups_done(self) -> bool:
        return all(g.remaining <= 0 for g in self._groups)

    def _on_wave_cleared(self) -> None:
        wave = self.waves[self._wave_index]
        self.state.add_gold(wave.reward_gold, reason="wave_bonus")
        self.state.bus.publish(WAVE_CLEARED, index=self._wave_index, wave=wave)
        if self._wave_index + 1 >= len(self.waves):
            self.phase = WaveState.DONE
            self.state.won = True
            self.state.bus.publish(LEVEL_WON)
        else:
            self.phase = WaveState.BETWEEN
            self._between_timer = wave.inter_wave_delay
