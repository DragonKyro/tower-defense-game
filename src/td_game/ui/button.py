"""Clickable button with hover state and cached text.

Uses `arcade.Text` (not `draw_text`) for GPU-cached rendering.
Hover state is driven by `update_hover(x, y)` called from the scene's
`on_mouse_motion` handler.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

import arcade


@dataclass(eq=False)
class Button:
    x: float
    y: float
    width: float
    height: float
    label: str
    on_click: Callable[[], None]
    enabled: bool = True
    hotkey: str | None = None
    icon: arcade.Texture | None = None   # if set, drawn centered (scaled to fit)
    subtitle: str | None = None          # optional small badge under the icon (e.g. cost)

    # internal
    hovered: bool = field(default=False, init=False)
    cooldown_fraction: float = field(default=0.0, init=False)  # 1.0 = just fired, 0.0 = ready
    _text: arcade.Text | None = field(default=None, init=False, repr=False)
    _hotkey_text: arcade.Text | None = field(default=None, init=False, repr=False)
    _subtitle_text: arcade.Text | None = field(default=None, init=False, repr=False)
    _icon_sprite: arcade.Sprite | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        if self.icon is not None:
            sp = arcade.Sprite()
            sp.texture = self.icon
            # Icon sits in the upper portion; subtitle (if any) goes below.
            subtitle_space = 14 if self.subtitle else 0
            pad = 8
            target = min(self.width - pad, self.height - pad - subtitle_space)
            scale = target / max(self.icon.width, self.icon.height)
            sp.scale = (scale, scale)
            sp.center_x = self.x
            sp.center_y = self.y + subtitle_space / 2
            self._icon_sprite = sp
            if self.subtitle:
                self._subtitle_text = arcade.Text(
                    self.subtitle,
                    self.x, self.y - self.height / 2 + 4,
                    color=(248, 220, 120), font_size=11, bold=True,
                    anchor_x="center", anchor_y="baseline",
                )
        else:
            self._text = arcade.Text(
                self.label, self.x, self.y,
                color=(240, 236, 228),
                font_size=14,
                anchor_x="center",
                anchor_y="center",
                multiline=False,
                align="center",
            )
        if self.hotkey:
            self._hotkey_text = arcade.Text(
                f"[{self.hotkey}]",
                self.x + self.width / 2 - 4, self.y - self.height / 2 + 4,
                color=(220, 210, 170), font_size=9, bold=True,
                anchor_x="right", anchor_y="baseline",
            )

    # ---- geometry ---------------------------------------------------

    def contains(self, px: float, py: float) -> bool:
        return (
            self.x - self.width / 2 <= px <= self.x + self.width / 2
            and self.y - self.height / 2 <= py <= self.y + self.height / 2
        )

    def update_hover(self, px: float, py: float) -> None:
        self.hovered = self.enabled and self.contains(px, py)

    def click(self, px: float, py: float) -> bool:
        if self.enabled and self.contains(px, py):
            self.on_click()
            return True
        return False

    def set_label(self, text: str) -> None:
        if text != self.label:
            self.label = text
            if self._text is not None:
                self._text.text = text

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = enabled
        if not enabled:
            self.hovered = False

    # ---- draw -------------------------------------------------------

    def draw(self) -> None:
        left = self.x - self.width / 2
        right = self.x + self.width / 2
        bottom = self.y - self.height / 2
        top = self.y + self.height / 2

        if not self.enabled:
            bg = (34, 34, 42)
            border = (80, 80, 90)
            text_color = (120, 116, 110)
        elif self.hovered:
            bg = (92, 102, 128)
            border = (240, 214, 136)
            text_color = (255, 250, 232)
        else:
            bg = (52, 56, 72)
            border = (160, 160, 180)
            text_color = (240, 236, 228)

        # Soft shadow beneath.
        arcade.draw_lrbt_rectangle_filled(left + 2, right + 2, bottom - 3, top - 3, (0, 0, 0, 120))
        # Body.
        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, bg)
        # Top highlight band.
        arcade.draw_lrbt_rectangle_filled(left, right, top - 4, top, (255, 255, 255, 30))
        # Border.
        arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, border, 2)

        if self._icon_sprite is not None:
            subtitle_space = 14 if self.subtitle else 0
            self._icon_sprite.center_x = self.x
            self._icon_sprite.center_y = self.y + subtitle_space / 2
            arcade.draw_sprite(self._icon_sprite)
            if self._subtitle_text is not None:
                self._subtitle_text.draw()
            # Cooldown mask: rising dark overlay from the bottom based on
            # `self.cooldown_fraction` (1.0 = full cover / just fired,
            # 0.0 = ready). Drawn last so it sits over the icon.
            cd_frac = getattr(self, "cooldown_fraction", 0.0)
            if cd_frac > 0.001:
                cover_h = (top - bottom) * min(1.0, cd_frac)
                arcade.draw_lrbt_rectangle_filled(
                    left, right, bottom, bottom + cover_h, (0, 0, 0, 175),
                )
            if not self.enabled and cd_frac <= 0.001:
                arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, (0, 0, 0, 140))
        elif self._text is not None:
            if self._text.color != text_color:
                self._text.color = text_color
            self._text.x = self.x
            self._text.y = self.y
            self._text.draw()
        if self._hotkey_text is not None:
            self._hotkey_text.draw()
