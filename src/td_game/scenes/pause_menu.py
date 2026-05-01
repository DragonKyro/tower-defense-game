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
        self._title = arcade.Text("Paused", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 120,
                                  color=(240, 232, 210), font_size=48,
                                  anchor_x="center", bold=True)

    def on_show_view(self) -> None:
        cx = SCREEN_WIDTH / 2
        self.buttons = [
            Button(cx, SCREEN_HEIGHT / 2 + 32, 240, 48, "Resume", self._resume),
            Button(cx, SCREEN_HEIGHT / 2 - 36, 240, 48, "Main Menu", self._to_menu),
        ]

    def _resume(self) -> None:
        if hasattr(self.underlying, "resume_from_pause"):
            self.underlying.resume_from_pause()
        self.window.show_view(self.underlying)

    def _to_menu(self) -> None:
        from .main_menu import MainMenuView
        self.window.show_view(MainMenuView())

    def on_draw(self) -> None:
        self.underlying.on_draw()
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, (0, 0, 0, 170))
        self._title.draw()
        for b in self.buttons:
            b.draw()

    def on_mouse_motion(self, x, y, dx, dy) -> None:
        for b in self.buttons:
            b.update_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers) -> None:
        for b in self.buttons:
            if b.click(x, y):
                return

    def on_key_press(self, key, modifiers) -> None:
        if key == arcade.key.P or key == arcade.key.ESCAPE:
            self._resume()
