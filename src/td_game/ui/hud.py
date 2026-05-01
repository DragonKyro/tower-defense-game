"""Bottom HUD strip: gold, lives, wave, skill buttons."""
from __future__ import annotations

import arcade

from td_game.core.constants import HUD_HEIGHT, SCREEN_HEIGHT, SCREEN_WIDTH

from .button import Button


class HUD:
    def __init__(self, state, skills: list, on_cast) -> None:
        self.state = state
        self.skills = skills
        self.on_cast = on_cast
        self.buttons: list[Button] = []
        self._build_buttons()

    def _build_buttons(self) -> None:
        y = HUD_HEIGHT / 2
        btn_w = 120
        spacing = 12
        right_edge = SCREEN_WIDTH - 16
        # Lay out skill buttons right-to-left so rightmost is first skill.
        for idx, skill in enumerate(self.skills):
            bx = right_edge - btn_w / 2 - idx * (btn_w + spacing)
            self.buttons.append(Button(
                x=bx,
                y=y,
                width=btn_w,
                height=40,
                label=skill.display_name,
                on_click=(lambda s=skill: self.on_cast(s)),
            ))

    def draw(self) -> None:
        # HUD background
        arcade.draw_lrbt_rectangle_filled(
            0, SCREEN_WIDTH, 0, HUD_HEIGHT, (24, 24, 32),
        )
        arcade.draw_lrbt_rectangle_outline(
            0, SCREEN_WIDTH, 0, HUD_HEIGHT, (80, 80, 100), 1,
        )
        # Text
        arcade.draw_text(f"Gold: {self.state.gold}", 16, HUD_HEIGHT - 22,
                         (240, 210, 110), 16)
        arcade.draw_text(f"Lives: {self.state.lives}", 160, HUD_HEIGHT - 22,
                         (240, 90, 90), 16)
        arcade.draw_text(
            f"Wave: {self.state.current_wave}/{self.state.total_waves}",
            320, HUD_HEIGHT - 22, (200, 220, 240), 16,
        )
        for b in self.buttons:
            b.draw()

    def handle_click(self, x: float, y: float) -> bool:
        for b in self.buttons:
            if b.click(x, y):
                return True
        return False
