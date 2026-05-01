"""Tower build / upgrade popup menu.

Shown when the player clicks a build spot or an existing tower. The menu
is logic-only here; the scene draws the options.
"""
from __future__ import annotations

import arcade

from td_game.data.towers import TOWER_TREES

from .button import Button


class BuildMenu:
    """Menu for an empty BuildSpot: lets the player pick a tower family."""
    def __init__(self, spot, x: float, y: float, allowed: tuple[str, ...], on_pick) -> None:
        self.spot = spot
        self.buttons: list[Button] = []
        dx = -60 * (len(allowed) - 1) / 2
        for family in allowed:
            cost = TOWER_TREES[family].tiers[0].cost
            self.buttons.append(Button(
                x=x + dx,
                y=y + 70,
                width=56,
                height=56,
                label=f"{family[:3]}\n{cost}g",
                on_click=(lambda f=family: on_pick(f, spot)),
            ))
            dx += 60

    def draw(self) -> None:
        for b in self.buttons:
            b.draw()

    def handle_click(self, x: float, y: float) -> bool:
        for b in self.buttons:
            if b.click(x, y):
                return True
        return False


class UpgradeMenu:
    """Menu for an existing tower: shows next upgrade options + sell."""
    def __init__(self, tower, x: float, y: float, on_upgrade, on_sell) -> None:
        self.tower = tower
        upgrades = tower.next_upgrades()
        self.buttons: list[Button] = []
        dx = -60 * (len(upgrades)) / 2
        for node_id, row in upgrades:
            self.buttons.append(Button(
                x=x + dx,
                y=y + 70,
                width=56,
                height=56,
                label=f"{row.display_name[:10]}\n{row.cost}g",
                on_click=(lambda nid=node_id: on_upgrade(tower, nid)),
            ))
            dx += 60
        self.buttons.append(Button(
            x=x,
            y=y - 70,
            width=100,
            height=32,
            label=f"Sell {tower.sell_value()}g",
            on_click=(lambda: on_sell(tower)),
        ))

    def draw(self) -> None:
        arcade.draw_circle_outline(self.tower.center_x, self.tower.center_y,
                                   self.tower.range, (250, 250, 250, 120), 2)
        for b in self.buttons:
            b.draw()

    def handle_click(self, x: float, y: float) -> bool:
        for b in self.buttons:
            if b.click(x, y):
                return True
        return False
