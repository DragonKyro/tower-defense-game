"""Wave manager state-machine smoke test."""
from __future__ import annotations

from unittest.mock import MagicMock

from td_game.core.game_state import GameState
from td_game.systems.wave_manager import WaveManager, WaveState
from td_game.world.wave import SpawnOrder, Wave


def test_wave_manager_progresses_through_waves():
    waves = (
        Wave(name="A", spawns=(SpawnOrder("goblin", count=1, interval=0.1),), reward_gold=10, inter_wave_delay=0.1),
        Wave(name="B", spawns=(SpawnOrder("goblin", count=1, interval=0.1),), reward_gold=20, inter_wave_delay=0.1),
    )
    state = GameState()
    spawner = MagicMock()
    wm = WaveManager(waves, spawner, state)
    wm.bind(MagicMock())

    wm.start_next_wave()
    assert wm.phase is WaveState.IN_WAVE
    # Tick until the one spawn has fired.
    for _ in range(5):
        wm.update(0.1, active_enemy_count=1)
    # Pretend that enemy died — update with 0 active.
    wm.update(0.1, active_enemy_count=0)
    assert wm.phase is WaveState.BETWEEN

    # Let the inter-wave delay tick down.
    for _ in range(3):
        wm.update(0.1, active_enemy_count=0)
    assert wm.phase is WaveState.IN_WAVE
    assert state.current_wave == 2
