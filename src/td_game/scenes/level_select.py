"""Level select: pick an unlocked level."""
from __future__ import annotations

import arcade

from td_game.core.constants import SCREEN_HEIGHT, SCREEN_WIDTH
from td_game.ui.button import Button


class LevelSelectView(arcade.View):
    def __init__(self) -> None:
        super().__init__()
        self.buttons: list[Button] = []
        self._heading = arcade.Text(
            "Select a Level", SCREEN_WIDTH / 2, SCREEN_HEIGHT - 60,
            color=(235, 220, 180), font_size=32, anchor_x="center", bold=True,
        )
        self._descriptions: list[arcade.Text] = []

    def on_show_view(self) -> None:
        from td_game.data.levels import LEVELS
        self.window.background_color = (10, 16, 28)
        y = SCREEN_HEIGHT - 140
        self.buttons = []
        self._descriptions = []
        for lid, level in LEVELS.items():
            self.buttons.append(Button(
                SCREEN_WIDTH / 2, y, 320, 48,
                label=f"{level.display_name}",
                on_click=(lambda lvl=level: self._play(lvl)),
            ))
            self._descriptions.append(arcade.Text(
                level.description, SCREEN_WIDTH / 2, y - 30,
                color=(170, 176, 190), font_size=11, anchor_x="center",
            ))
            y -= 72
        self.buttons.append(Button(80, 40, 140, 36, "Back", on_click=self._back))

    def _play(self, level) -> None:
        from .game_scene import GameView
        self.window.show_view(GameView(level))

    def _back(self) -> None:
        from .main_menu import MainMenuView
        self.window.show_view(MainMenuView())

    def on_draw(self) -> None:
        self.clear()
        self._heading.draw()
        for desc in self._descriptions:
            desc.draw()
        for b in self.buttons:
            b.draw()

    def on_mouse_motion(self, x, y, dx, dy) -> None:
        for b in self.buttons:
            b.update_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers) -> None:
        for b in self.buttons:
            if b.click(x, y):
                return
