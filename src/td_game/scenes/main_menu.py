"""Main menu: start a level or quit."""
from __future__ import annotations

import arcade

from td_game.core.constants import SCREEN_HEIGHT, SCREEN_TITLE, SCREEN_WIDTH
from td_game.ui.button import Button


class MainMenuView(arcade.View):
    def __init__(self) -> None:
        super().__init__()
        self.buttons: list[Button] = []

    def on_show_view(self) -> None:
        self.window.background_color = (12, 20, 32)
        self._build_buttons()

    def _build_buttons(self) -> None:
        cx = SCREEN_WIDTH / 2
        self.buttons = [
            Button(cx, SCREEN_HEIGHT / 2, 220, 48, "Play", self._play),
            Button(cx, SCREEN_HEIGHT / 2 - 64, 220, 48, "Level Select", self._level_select),
            Button(cx, SCREEN_HEIGHT / 2 - 128, 220, 48, "Quit", arcade.exit),
        ]

    def _play(self) -> None:
        from td_game.data.levels import LEVELS
        from .game_scene import GameView
        self.window.show_view(GameView(LEVELS["level_01"]))

    def _level_select(self) -> None:
        from .level_select import LevelSelectView
        self.window.show_view(LevelSelectView())

    def on_draw(self) -> None:
        self.clear()
        arcade.draw_text(SCREEN_TITLE, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.78,
                         (235, 220, 180), 56, anchor_x="center")
        arcade.draw_text("A modular, Kingdom Rush-inspired tower defense",
                         SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.72,
                         (170, 180, 200), 16, anchor_x="center")
        for b in self.buttons:
            b.draw()

    def on_mouse_press(self, x, y, button, modifiers) -> None:
        for b in self.buttons:
            if b.click(x, y):
                return
