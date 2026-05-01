"""Bottom HUD strip: gold, lives, wave, skill buttons, pause.

All text uses cached `arcade.Text` objects. `update(dt)` refreshes text
contents only when the underlying state changes — `draw()` is the fast
path.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import arcade

from td_game.core.constants import HUD_HEIGHT, SCREEN_HEIGHT, SCREEN_WIDTH
from td_game.core.resources import load_texture
from td_game.graphics.procedural import palette as P

from .button import Button


@dataclass
class _SkillButton:
    """A skill button with a cooldown overlay + icon slot."""
    btn: Button
    skill: object
    cooldown_text: arcade.Text


class HUD:
    def __init__(self, state, skills: list, on_cast: Callable, on_pause: Callable,
                 on_speed_toggle: Callable) -> None:
        self.state = state
        self.skills = skills
        self.on_cast = on_cast
        self.on_pause = on_pause
        self.on_speed_toggle = on_speed_toggle

        # Stat labels
        self._gold_text = arcade.Text("Gold: 0", 18, HUD_HEIGHT - 24,
                                      color=(248, 220, 120), font_size=16, bold=True)
        self._lives_text = arcade.Text("Lives: 0", 160, HUD_HEIGHT - 24,
                                       color=(240, 108, 100), font_size=16, bold=True)
        self._wave_text = arcade.Text("Wave: 0/0", 310, HUD_HEIGHT - 24,
                                      color=(200, 220, 244), font_size=16, bold=True)
        self._hint_text = arcade.Text(
            "Left-click to build or upgrade  •  Right-click to move hero  •  P to pause",
            18, 16, color=(180, 180, 192), font_size=11,
        )

        self.buttons: list[Button] = []
        self.skill_buttons: list[_SkillButton] = []
        self._build_buttons()

    def _build_buttons(self) -> None:
        y = HUD_HEIGHT / 2
        icon_w = 56
        icon_h = 56
        spacing = 10
        right_edge = SCREEN_WIDTH - 16

        # Right cluster: pause + speed.
        pause_btn = Button(right_edge - 32, y, 60, 44, "II",
                           self.on_pause, hotkey="P")
        speed_btn = Button(right_edge - 32 - 60 - spacing, y, 60, 44, "1x",
                           self.on_speed_toggle, hotkey="F")
        self.buttons.append(pause_btn)
        self.buttons.append(speed_btn)
        self._pause_btn = pause_btn
        self._speed_btn = speed_btn

        # Skill buttons — icon-based, right-to-left.
        cluster_right = right_edge - 32 - 60 - spacing - 60 - spacing - icon_w / 2
        hotkeys = ("Q", "W", "E", "R")
        for idx, skill in enumerate(self.skills):
            bx = cluster_right - idx * (icon_w + spacing)
            tex = load_texture("skills", skill.icon) if skill.icon else None
            hotkey = hotkeys[idx] if idx < len(hotkeys) else None
            b = Button(
                bx, y, icon_w, icon_h, skill.display_name,
                on_click=(lambda s=skill: self.on_cast(s)),
                icon=tex,
                hotkey=hotkey,
            )
            cdt = arcade.Text(
                "", bx, y, color=(255, 255, 255), font_size=18, bold=True,
                anchor_x="center", anchor_y="center",
            )
            self.buttons.append(b)
            self.skill_buttons.append(_SkillButton(b, skill, cdt))

    # --- dynamic updates -------------------------------------------

    def update(self, dt: float) -> None:
        gold = f"Gold: {self.state.gold}"
        if self._gold_text.text != gold:
            self._gold_text.text = gold
        lives = f"Lives: {self.state.lives}"
        if self._lives_text.text != lives:
            self._lives_text.text = lives
        wave = f"Wave: {self.state.current_wave}/{self.state.total_waves}"
        if self._wave_text.text != wave:
            self._wave_text.text = wave

        speed_label = f"{self.state.game_speed:g}x"
        if self._speed_btn.label != speed_label:
            self._speed_btn.set_label(speed_label)
        pause_label = "▶" if self.state.paused else "II"
        if self._pause_btn.label != pause_label:
            self._pause_btn.set_label(pause_label)

        # Skill CD text + enabled.
        for sb in self.skill_buttons:
            ready = sb.skill.ready
            sb.btn.set_enabled(ready and self.state.gold >= sb.skill.cost)
            if ready:
                sb.cooldown_text.text = ""
            else:
                cd_left = getattr(sb.skill, "_cooldown_left", 0.0)
                sb.cooldown_text.text = f"{cd_left:.0f}s"

    def update_hover(self, x: float, y: float) -> None:
        for b in self.buttons:
            b.update_hover(x, y)

    # --- rendering --------------------------------------------------

    def draw(self) -> None:
        # HUD strip background with gradient.
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, HUD_HEIGHT, (22, 24, 32))
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, HUD_HEIGHT - 3, HUD_HEIGHT, P.KNIGHT_GOLD_DARK)
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, HUD_HEIGHT - 2, HUD_HEIGHT - 1, P.KNIGHT_GOLD)
        arcade.draw_lrbt_rectangle_outline(0, SCREEN_WIDTH, 0, HUD_HEIGHT, (100, 90, 70), 1)

        # Stats panels
        self._draw_stat_chip(6, HUD_HEIGHT - 36, 148, 28, (40, 30, 12), (180, 140, 60))
        self._draw_stat_chip(156, HUD_HEIGHT - 36, 144, 28, (40, 20, 20), (180, 80, 80))
        self._draw_stat_chip(306, HUD_HEIGHT - 36, 160, 28, (20, 30, 48), (100, 130, 180))
        self._gold_text.draw()
        self._lives_text.draw()
        self._wave_text.draw()
        self._hint_text.draw()

        for b in self.buttons:
            b.draw()
        for sb in self.skill_buttons:
            if sb.cooldown_text.text:
                sb.cooldown_text.draw()

    def _draw_stat_chip(self, x: float, y: float, w: float, h: float, fill, border) -> None:
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, fill)
        arcade.draw_lrbt_rectangle_filled(x, x + w, y + h - 2, y + h, (*border, 200))
        arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, border, 1)

    def handle_click(self, x: float, y: float) -> bool:
        for b in self.buttons:
            if b.click(x, y):
                return True
        return False
