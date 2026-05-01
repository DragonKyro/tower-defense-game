"""Pause overlay."""
from __future__ import annotations

import arcade

from td_game.core.constants import SCREEN_HEIGHT, SCREEN_WIDTH
from td_game.ui.button import Button


class PauseView(arcade.View):
    def __init__(self, underlying: arcade.View) -> None:
        super().__init__()
        self.underlying = underlying
        self.buttons: list[Button] = []

    def on_show_view(self) -> None:
        cx = SCREEN_WIDTH / 2
        self.buttons = [
            Button(cx, SCREEN_HEIGHT / 2 + 32, 220, 44, "Resume", self._resume),
            Button(cx, SCREEN_HEIGHT / 2 - 32, 220, 44, "Main Menu", self._to_menu),
        ]

    def _resume(self) -> None:
        self.window.show_view(self.underlying)

    def _to_menu(self) -> None:
        from .main_menu import MainMenuView
        self.window.show_view(MainMenuView())

    def on_draw(self) -> None:
        self.underlying.on_draw()
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, (0, 0, 0, 160))
        arcade.draw_text("Paused", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 120,
                         (235, 235, 235), 44, anchor_x="center")
        for b in self.buttons:
            b.draw()

    def on_mouse_press(self, x, y, button, modifiers) -> None:
        for b in self.buttons:
            if b.click(x, y):
                return
