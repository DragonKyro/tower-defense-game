"""Floating health bar for enemies / units.

Uses arcade.draw_lrbt_rectangle_filled only (no text) so it's cheap
enough to call per-enemy per-frame.
"""
from __future__ import annotations

import arcade


def draw_health_bar(entity, width: float = 32, height: float = 5, y_offset: float = 22) -> None:
    if entity.hp >= entity.max_hp:
        return
    if entity.hp <= 0:
        return
    x = entity.center_x
    y = entity.center_y + y_offset
    frac = max(0.0, entity.hp / entity.max_hp)
    # Shadow
    arcade.draw_lrbt_rectangle_filled(
        x - width / 2 + 1, x + width / 2 + 1, y - height / 2 - 1, y + height / 2 - 1,
        (0, 0, 0, 170),
    )
    # Background
    arcade.draw_lrbt_rectangle_filled(
        x - width / 2, x + width / 2, y - height / 2, y + height / 2,
        (20, 20, 24, 220),
    )
    # Fill
    if frac > 0.6:
        color = (104, 208, 92)
    elif frac > 0.3:
        color = (228, 212, 82)
    else:
        color = (220, 80, 72)
    arcade.draw_lrbt_rectangle_filled(
        x - width / 2 + 1, x - width / 2 + 1 + (width - 2) * frac,
        y - height / 2 + 1, y + height / 2 - 1,
        color,
    )
    # Highlight band
    arcade.draw_lrbt_rectangle_filled(
        x - width / 2 + 1, x - width / 2 + 1 + (width - 2) * frac,
        y + height / 2 - 2, y + height / 2 - 1,
        (255, 255, 255, 120),
    )
    # Border
    arcade.draw_lrbt_rectangle_outline(
        x - width / 2, x + width / 2, y - height / 2, y + height / 2, (0, 0, 0, 200), 1,
    )
