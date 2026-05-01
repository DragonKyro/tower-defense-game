"""Floating health bar for enemies / units."""
from __future__ import annotations

import arcade

from td_game.graphics.procedural import palette as P


def draw_health_bar(entity, width: float = 28, height: float = 4, y_offset: float = 22) -> None:
    if entity.hp >= entity.max_hp:
        return
    if entity.hp <= 0:
        return
    x = entity.center_x
    y = entity.center_y + y_offset
    frac = max(0.0, entity.hp / entity.max_hp)
    arcade.draw_lrbt_rectangle_filled(
        x - width / 2, x + width / 2, y - height / 2, y + height / 2,
        P.HP_BG[:3] + (180,),
    )
    arcade.draw_lrbt_rectangle_filled(
        x - width / 2, x - width / 2 + width * frac, y - height / 2, y + height / 2,
        P.HP_GREEN[:3] if frac > 0.35 else P.HP_RED[:3],
    )
