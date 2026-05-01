"""Minimal clickable button.

Arcade has its own GUI stack (`arcade.gui`) but its API drifted between
releases; we roll a tiny one here to avoid coupling to a specific arcade
minor version. Swap to arcade.gui later if desired.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

import arcade


@dataclass
class Button:
    x: float
    y: float
    width: float
    height: float
    label: str
    on_click: Callable[[], None]
    enabled: bool = True

    def contains(self, px: float, py: float) -> bool:
        return (
            self.x - self.width / 2 <= px <= self.x + self.width / 2
            and self.y - self.height / 2 <= py <= self.y + self.height / 2
        )

    def click(self, px: float, py: float) -> bool:
        if self.enabled and self.contains(px, py):
            self.on_click()
            return True
        return False

    def draw(self) -> None:
        bg = (60, 60, 72) if self.enabled else (40, 40, 48)
        arcade.draw_lrbt_rectangle_filled(
            self.x - self.width / 2, self.x + self.width / 2,
            self.y - self.height / 2, self.y + self.height / 2,
            bg,
        )
        arcade.draw_lrbt_rectangle_outline(
            self.x - self.width / 2, self.x + self.width / 2,
            self.y - self.height / 2, self.y + self.height / 2,
            (200, 200, 220), 2,
        )
        arcade.draw_text(
            self.label, self.x, self.y,
            (235, 235, 240), 14,
            anchor_x="center", anchor_y="center",
        )
