"""Tower build / upgrade popup menus with iconic buttons and hover info."""
from __future__ import annotations

import arcade

from td_game.core.resources import load_texture
from td_game.data.towers import TOWER_TREES

from .button import Button
from .tooltip import tower_panel


class BuildMenu:
    """Menu for an empty BuildSpot: lets the player pick a tower family."""
    def __init__(self, spot, x: float, y: float, allowed: tuple[str, ...], on_pick) -> None:
        self.spot = spot
        self.anchor_x = x
        self.anchor_y = y
        self.buttons: list[Button] = []
        self._family_by_btn: dict[Button, str] = {}
        btn_w = 68
        spacing = 6
        dx = -((btn_w + spacing) * (len(allowed) - 1)) / 2
        for family in allowed:
            cost = TOWER_TREES[family].tiers[0].cost
            tex = load_texture("towers", f"{family}_1")
            b = Button(
                x=x + dx, y=y + 86,
                width=btn_w, height=btn_w,
                label=_family_short(family),
                on_click=(lambda f=family: on_pick(f, spot)),
                icon=tex,
                subtitle=f"{cost}g",
            )
            self.buttons.append(b)
            self._family_by_btn[b] = family
            dx += btn_w + spacing

    @property
    def hovered_family(self) -> str | None:
        for b, family in self._family_by_btn.items():
            if b.hovered:
                return family
        return None

    def update_affordability(self, gold: int) -> None:
        for b, family in self._family_by_btn.items():
            b.set_enabled(gold >= TOWER_TREES[family].tiers[0].cost)

    def update_hover(self, x: float, y: float) -> None:
        for b in self.buttons:
            b.update_hover(x, y)

    def draw_preview(self, affordable_check) -> None:
        """Draw the range circle for the currently hovered tower family.

        Called from the scene *before* the menu buttons are drawn so the
        range ring sits on the map, beneath the popup. `affordable_check`
        is a callable family -> bool for colouring the ring.
        """
        family = self.hovered_family
        if family is None:
            return
        row = TOWER_TREES[family].tiers[0]
        affordable = affordable_check(family)
        ring = (120, 220, 140, 200) if affordable else (220, 100, 100, 200)
        fill = (120, 220, 140, 40) if affordable else (220, 100, 100, 40)
        arcade.draw_circle_filled(self.anchor_x, self.anchor_y, row.range, fill)
        arcade.draw_circle_outline(self.anchor_x, self.anchor_y, row.range, ring, 2)

    def draw(self) -> None:
        for b in self.buttons:
            b.draw()
        family = self.hovered_family
        if family is not None:
            btn = next(b for b, f in self._family_by_btn.items() if f == family)
            row = TOWER_TREES[family].tiers[0]
            tower_panel(family, row).draw(btn.x, btn.y + 32, align="above")

    def handle_click(self, x: float, y: float) -> bool:
        for b in self.buttons:
            if b.click(x, y):
                return True
        return False


class UpgradeMenu:
    """Menu for an existing tower: shows next upgrade options + sell.

    For a barracks, rally is not set from this menu — right-click on the
    map while the barracks is selected to move its rally.
    """
    def __init__(self, tower, x: float, y: float, on_upgrade, on_sell) -> None:
        self.tower = tower
        self.anchor_x = x
        self.anchor_y = y
        upgrades = tower.next_upgrades()
        self.buttons: list[Button] = []
        self._node_by_btn: dict[Button, str] = {}
        self._cost_by_btn: dict[Button, int] = {}
        btn_w = 68
        spacing = 6
        dx = -((btn_w + spacing) * (len(upgrades) - 1)) / 2 if upgrades else 0
        for node_id, row in upgrades:
            # Show the next-tier sprite as the upgrade icon.
            if node_id.isdigit():
                tier_num = int(node_id) + 1  # 0-indexed; file names are 1-indexed
            else:
                tier_num = 4
            tex = load_texture("towers", f"{tower.family}_{tier_num}")
            b = Button(
                x=x + dx, y=y + 86,
                width=btn_w, height=btn_w,
                label=_short_label(row.display_name),
                on_click=(lambda nid=node_id: on_upgrade(tower, nid)),
                icon=tex,
                subtitle=f"{row.cost}g",
            )
            self.buttons.append(b)
            self._node_by_btn[b] = node_id
            self._cost_by_btn[b] = row.cost
            dx += btn_w + spacing
        self._sell_btn = Button(
            x=x, y=y - 56,
            width=140, height=34,
            label=f"Sell {tower.sell_value()}g",
            on_click=(lambda: on_sell(tower)),
        )
        self.buttons.append(self._sell_btn)

    def update_affordability(self, gold: int) -> None:
        for b, cost in self._cost_by_btn.items():
            b.set_enabled(gold >= cost)

    def update_hover(self, x: float, y: float) -> None:
        for b in self.buttons:
            b.update_hover(x, y)

    def draw(self) -> None:
        # Range circle for context.
        arcade.draw_circle_outline(self.tower.center_x, self.tower.center_y,
                                   self.tower.range, (252, 240, 180, 130), 2)
        arcade.draw_circle_outline(self.tower.center_x, self.tower.center_y,
                                   self.tower.range + 2, (252, 240, 180, 50), 2)
        for b in self.buttons:
            b.draw()
        # Tooltip for hovered upgrade option.
        for b, node_id in self._node_by_btn.items():
            if b.hovered:
                for nid, row in self.tower.next_upgrades():
                    if nid == node_id:
                        tower_panel(self.tower.family, row).draw(b.x, b.y + 32, align="above")
                        break
                break

    def handle_click(self, x: float, y: float) -> bool:
        for b in self.buttons:
            if b.click(x, y):
                return True
        return False


def _family_short(family: str) -> str:
    return {"archer": "Archer", "barracks": "Barracks", "mage": "Mage", "artillery": "Cannon"}.get(family, family.title())


def _short_label(name: str) -> str:
    # Fit into a 60px button; cap at 2 lines of ~8 chars.
    parts = name.split()
    if len(parts) == 1:
        return parts[0][:10]
    return parts[0][:10] + "\n" + " ".join(parts[1:])[:10]
