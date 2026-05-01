"""Arcade Window + entry-point `run()`."""
from __future__ import annotations

import arcade

from .core.audio import audio
from .core.constants import SCREEN_HEIGHT, SCREEN_TITLE, SCREEN_WIDTH, TARGET_FPS
from .graphics.bootstrap import register_all


def run() -> None:
    register_all()
    audio.warmup()
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, update_rate=1 / TARGET_FPS)
    # Local import so procedural registration happens first.
    from .scenes.main_menu import MainMenuView
    window.show_view(MainMenuView())
    audio.play_music("music_meadow")
    arcade.run()
