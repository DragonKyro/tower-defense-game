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
        title_color = (232, 228, 136) if won else (232, 96, 96)
        self._title = arcade.Text(
            "Victory!" if won else "Defeat",
            SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.7,
            color=title_color, font_size=72, anchor_x="center", bold=True,
        )
        self._subtitle = arcade.Text(
            level.display_name, SCREEN_WIDTH / 2, SCREEN_HEIGHT * 0.6,
            color=(230, 230, 230), font_size=22, anchor_x="center",
        )

    def on_show_view(self) -> None:
        self.window.background_color = (10, 18, 28) if self.won else (30, 12, 12)
        cx = SCREEN_WIDTH / 2
        self.buttons = [
            Button(cx, SCREEN_HEIGHT / 2 - 40, 240, 48, "Replay", self._replay),
            Button(cx, SCREEN_HEIGHT / 2 - 108, 240, 48, "Main Menu", self._to_menu),
        ]

    def _replay(self) -> None:
        from .game_scene import GameView
        self.window.show_view(GameView(self.level))

    def _to_menu(self) -> None:
        from .main_menu import MainMenuView
        self.window.show_view(MainMenuView())

    def on_draw(self) -> None:
        self.clear()
        self._title.draw()
        self._subtitle.draw()
        for b in self.buttons:
            b.draw()

    def on_mouse_motion(self, x, y, dx, dy) -> None:
        for b in self.buttons:
            b.update_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers) -> None:
        for b in self.buttons:
            if b.click(x, y):
                return
