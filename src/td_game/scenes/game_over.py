"""Game-over screen (win or lose)."""
from __future__ import annotations

import arcade

from td_game.core.constants import SCREEN_HEIGHT, SCREEN_WIDTH
from td_game.ui.button import Button


class GameOverView(arcade.View):
    def __init__(self, level, won: bool) -> None:
        super().__init__()
        self.level = level
        self.won = won
        self.buttons: list[Button] = []

    def on_show_view(self) -> None:
        self.window.background_color = (10, 18, 28) if self.won else (30, 12, 12)
        cx = SCREEN_WIDTH / 2
        self.buttons = [
            Button(cx, SCREEN_HEIGHT / 2 - 40, 220, 44, "Replay", self._replay),
            Button(cx, SCREEN_HEIGHT / 2 - 100, 220, 44, "Main Menu", self._to_menu),
        ]

    def _replay(self) -> None:
        from .game_scene import GameView
        self.window.show_view(GameView(self.level))

    def _to_menu(self) -> None:
        from .main_menu import MainMenuView
        self.window.show_view(MainMenuView())

    def on_draw(self) -> None:
        self.clear()
        title = "Victory!" if self.won else "Defeat"
        color = (220, 230, 120) if self.won else (220, 90, 90)
        arcade.draw_text(title, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.7,
                         color, 64, anchor_x="center")
        arcade.draw_text(self.level.display_name, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.6,
                         (230, 230, 230), 22, anchor_x="center")
        for b in self.buttons:
            b.draw()

    def on_mouse_press(self, x, y, button, modifiers) -> None:
        for b in self.buttons:
            if b.click(x, y):
                return
