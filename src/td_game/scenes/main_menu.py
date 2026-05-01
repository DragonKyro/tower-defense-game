"""Main menu: start a level, pick one, or quit.

All title + tagline text lives in cached `arcade.Text` objects to avoid
the slow `draw_text` path.
"""
from __future__ import annotations

import arcade

from td_game.core.constants import SCREEN_HEIGHT, SCREEN_TITLE, SCREEN_WIDTH
from td_game.graphics.procedural import palette as P
from td_game.ui.button import Button


class MainMenuView(arcade.View):
    def __init__(self) -> None:
        super().__init__()
        self.buttons: list[Button] = []
        self._title = arcade.Text(
            SCREEN_TITLE, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.78,
            color=(240, 218, 152), font_size=72, anchor_x="center", bold=True,
        )
        self._title_shadow = arcade.Text(
            SCREEN_TITLE, SCREEN_WIDTH / 2 + 3, SCREEN_HEIGHT * 0.78 - 4,
            color=(0, 0, 0, 180), font_size=72, anchor_x="center", bold=True,
        )
        self._tagline = arcade.Text(
            "A modular, Kingdom Rush-inspired tower defense",
            SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.72,
            color=(190, 196, 210), font_size=16, anchor_x="center",
        )

    def on_show_view(self) -> None:
        self.window.background_color = (12, 18, 28)
        self._build_buttons()

    def _build_buttons(self) -> None:
        cx = SCREEN_WIDTH / 2
        self.buttons = [
            Button(cx, SCREEN_HEIGHT / 2, 240, 50, "Play", self._play),
            Button(cx, SCREEN_HEIGHT / 2 - 68, 240, 50, "Level Select", self._level_select),
            Button(cx, SCREEN_HEIGHT / 2 - 136, 240, 50, "Quit", arcade.exit),
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
        self._title_shadow.draw()
        self._title.draw()
        self._tagline.draw()
        for b in self.buttons:
            b.draw()

    def on_mouse_motion(self, x, y, dx, dy) -> None:
        for b in self.buttons:
            b.update_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers) -> None:
        for b in self.buttons:
            if b.click(x, y):
                return
