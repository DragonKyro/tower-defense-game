"""Top-of-screen banner showing the next wave + a 'call early' button.

Appears during the inter-wave breather and before the very first wave.
Click the banner (or press SPACE) to start the next wave immediately
and pocket a gold bonus proportional to the skipped time.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

import arcade

from td_game.core.constants import SCREEN_HEIGHT, SCREEN_WIDTH
from td_game.core.resources import load_texture
from td_game.data.enemies import ENEMIES
from td_game.graphics.procedural import palette as P


ICON_SIZE = 40
BAR_HEIGHT = 54
BAR_Y = SCREEN_HEIGHT - BAR_HEIGHT / 2 - 6


@dataclass
class _EnemyChip:
    sprite: arcade.Sprite
    count: int
    count_text: arcade.Text


class WavePreview:
    def __init__(self, on_call_early: Callable[[], None]) -> None:
        self.on_call_early = on_call_early
        self.visible = False
        self._wave = None
        self._timer = 0.0
        self._chips: list[_EnemyChip] = []

        # Cached label + countdown text.
        self._label = arcade.Text(
            "Next Wave", 0, 0, color=(252, 232, 168),
            font_size=13, bold=True, anchor_x="left", anchor_y="center",
        )
        self._countdown = arcade.Text(
            "", 0, 0, color=(220, 220, 232), font_size=12,
            anchor_x="left", anchor_y="center",
        )
        self._call_text = arcade.Text(
            "Send Now (+0g)   [SPACE]", 0, 0, color=(40, 30, 18),
            font_size=13, bold=True, anchor_x="center", anchor_y="center",
        )
        self._call_rect: tuple[float, float, float, float] | None = None
        self._call_hovered = False
        self._bonus = 0

    def set_wave(self, wave, timer: float, bonus: int) -> None:
        """Called each frame while inter-wave. `wave` is the upcoming Wave."""
        if wave is None:
            self.visible = False
            return
        self.visible = True
        self._timer = timer
        self._bonus = bonus

        if wave is not self._wave:
            self._wave = wave
            self._rebuild_chips(wave)

        mins = int(timer) // 60
        secs = int(timer) % 60
        self._countdown.text = f"{mins}:{secs:02d}"
        self._call_text.text = f"Send Now (+{bonus}g)   [SPACE]"

    def hide(self) -> None:
        self.visible = False

    def _rebuild_chips(self, wave) -> None:
        # Aggregate counts by enemy_id so we show one chip per type.
        counts: dict[str, int] = {}
        for order in wave.spawns:
            counts[order.enemy_id] = counts.get(order.enemy_id, 0) + order.count
        self._chips = []
        for enemy_id, count in counts.items():
            stats = ENEMIES[enemy_id]
            sp = arcade.Sprite()
            sp.texture = load_texture("enemies", f"{stats.sprite_base}_idle_0")
            sp.scale = (0.8, 0.8)
            sp.center_x = 0
            sp.center_y = BAR_Y
            self._chips.append(_EnemyChip(
                sprite=sp,
                count=count,
                count_text=arcade.Text(
                    f"×{count}", 0, 0, color=(250, 240, 220),
                    font_size=11, bold=True, anchor_x="center", anchor_y="center",
                ),
            ))

    # --- input ------------------------------------------------------

    def update_hover(self, x: float, y: float) -> None:
        if not self.visible or self._call_rect is None:
            self._call_hovered = False
            return
        l, r, b, t = self._call_rect
        self._call_hovered = l <= x <= r and b <= y <= t

    def handle_click(self, x: float, y: float) -> bool:
        if not self.visible or self._call_rect is None:
            return False
        l, r, b, t = self._call_rect
        if l <= x <= r and b <= y <= t:
            self.on_call_early()
            return True
        return False

    # --- draw -------------------------------------------------------

    def draw(self) -> None:
        if not self.visible or self._wave is None:
            return

        # Compute overall bar width based on chip count + button.
        chip_area_w = 10 + len(self._chips) * (ICON_SIZE + 28) + 10
        label_area_w = 90 + 48  # "Next Wave" + countdown
        button_w = 180
        total_w = label_area_w + chip_area_w + button_w + 40
        x_left = SCREEN_WIDTH / 2 - total_w / 2
        x_right = x_left + total_w
        y_top = BAR_Y + BAR_HEIGHT / 2
        y_bot = BAR_Y - BAR_HEIGHT / 2

        # Bar background + accent.
        arcade.draw_lrbt_rectangle_filled(x_left + 3, x_right + 3, y_bot - 3, y_top - 3, (0, 0, 0, 140))
        arcade.draw_lrbt_rectangle_filled(x_left, x_right, y_bot, y_top, (26, 28, 38, 235))
        arcade.draw_lrbt_rectangle_filled(x_left, x_right, y_top - 2, y_top, P.KNIGHT_GOLD)
        arcade.draw_lrbt_rectangle_outline(x_left, x_right, y_bot, y_top, P.KNIGHT_GOLD_DARK, 1)

        # Label + countdown.
        lx = x_left + 12
        self._label.x = lx
        self._label.y = BAR_Y + 3
        self._label.draw()
        cd_x = lx
        self._countdown.x = cd_x
        self._countdown.y = BAR_Y - 12
        self._countdown.draw()

        # Enemy chips (icons + ×count).
        cx = x_left + label_area_w + 10 + ICON_SIZE / 2
        for chip in self._chips:
            chip.sprite.center_x = cx
            chip.sprite.center_y = BAR_Y + 2
            # Little chip bg.
            arcade.draw_lrbt_rectangle_filled(
                cx - ICON_SIZE / 2 - 2, cx + ICON_SIZE / 2 + 2,
                y_bot + 6, y_top - 6, (40, 46, 60, 220),
            )
            arcade.draw_sprite(chip.sprite)
            chip.count_text.x = cx
            chip.count_text.y = y_bot + 10
            chip.count_text.draw()
            cx += ICON_SIZE + 28

        # Call-early button on the right.
        btn_right = x_right - 10
        btn_left = btn_right - button_w
        btn_bot = y_bot + 6
        btn_top = y_top - 6
        self._call_rect = (btn_left, btn_right, btn_bot, btn_top)

        if self._call_hovered:
            fill = (232, 192, 84)
            border = (255, 250, 220)
        else:
            fill = (172, 128, 40)
            border = (244, 212, 120)
        arcade.draw_lrbt_rectangle_filled(btn_left, btn_right, btn_bot, btn_top, fill)
        arcade.draw_lrbt_rectangle_filled(btn_left, btn_right, btn_top - 3, btn_top, (255, 255, 255, 120))
        arcade.draw_lrbt_rectangle_outline(btn_left, btn_right, btn_bot, btn_top, border, 2)
        self._call_text.x = (btn_left + btn_right) / 2
        self._call_text.y = (btn_bot + btn_top) / 2
        self._call_text.draw()
