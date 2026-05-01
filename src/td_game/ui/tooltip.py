"""Floating info panels for hovered units, towers, build spots, and skills.

Text objects are created on-demand and cached on the InfoPanel instance,
so the panel can be redrawn every frame without triggering the slow
`arcade.draw_text` path.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import arcade

from td_game.core.constants import SCREEN_HEIGHT, SCREEN_WIDTH


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


@dataclass
class InfoPanel:
    """A bordered panel with a title + body lines. Call draw(x, y)."""
    title: str
    body: tuple[str, ...]
    width: float = 280
    accent: tuple[int, int, int] = (232, 192, 84)

    _title_text: Optional[arcade.Text] = field(default=None, init=False, repr=False)
    _lines: list[arcade.Text] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        self._title_text = arcade.Text(
            self.title, 0, 0,
            color=self.accent, font_size=14, bold=True,
            anchor_x="left", anchor_y="top",
        )
        self._lines = [
            arcade.Text(
                line, 0, 0, color=(230, 228, 220), font_size=11,
                anchor_x="left", anchor_y="top",
                multiline=True, width=int(self.width - 20),
            )
            for line in self.body
        ]

    def _height(self) -> float:
        # Rough: title + wrap count per line.
        h = 26
        for line in self._lines:
            # Each line is multiline-wrapped; approximate via content_height if available.
            height = getattr(line, "content_height", None)
            if height is None or height <= 0:
                height = 14 * max(1, (len(line.text) // 40) + 1)
            h += int(height) + 4
        return h

    def draw(self, anchor_x: float, anchor_y: float, align: str = "above") -> None:
        w = self.width
        h = self._height()
        # Prefer to draw above the anchor; fall back to below if too close to the top.
        if align == "above":
            x = _clamp(anchor_x - w / 2, 8, SCREEN_WIDTH - w - 8)
            y = anchor_y + 20
            if y + h > SCREEN_HEIGHT - 8:
                y = anchor_y - h - 20
        else:
            x = _clamp(anchor_x - w / 2, 8, SCREEN_WIDTH - w - 8)
            y = anchor_y - h - 20
        y = _clamp(y, 8, SCREEN_HEIGHT - h - 8)

        # Shadow.
        arcade.draw_lrbt_rectangle_filled(x + 3, x + w + 3, y - 3, y + h - 3, (0, 0, 0, 150))
        # Body.
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, (28, 30, 40, 235))
        # Top accent bar.
        arcade.draw_lrbt_rectangle_filled(x, x + w, y + h - 3, y + h, self.accent)
        # Border.
        arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, (*self.accent, 255), 1)

        tx = x + 10
        ty = y + h - 6
        if self._title_text is not None:
            self._title_text.x = tx
            self._title_text.y = ty
            self._title_text.draw()
            ty -= 22
        for line in self._lines:
            line.x = tx
            line.y = ty
            line.draw()
            height = getattr(line, "content_height", None)
            if height is None or height <= 0:
                height = 14 * max(1, (len(line.text) // 40) + 1)
            ty -= int(height) + 4


# Factories so scenes can get a panel for a thing without plumbing fields.

def enemy_panel(stats) -> InfoPanel:
    body = [
        f"HP {int(stats.max_hp)}   Speed {int(stats.speed)}   Armor {int(stats.armor)}",
        f"Bounty {stats.bounty}g   Leaks for {stats.lives_cost} life" + ("s" if stats.lives_cost != 1 else ""),
        ("Flying — only air-capable towers can hit it." if stats.flying else ""),
        stats.description or "",
    ]
    return InfoPanel(
        title=stats.display_name,
        body=tuple(b for b in body if b),
        accent=(228, 120, 108) if stats.flying else (232, 192, 84),
    )


def tower_panel(family: str, row) -> InfoPanel:
    body = [
        f"Damage {int(row.damage)}   Range {int(row.range)}   Rate {row.attack_interval:.2f}s",
        f"Cost {row.cost}g",
        _describe_extras(row.extras),
        _describe_family(family),
    ]
    return InfoPanel(
        title=row.display_name,
        body=tuple(b for b in body if b),
        accent=(180, 220, 255),
    )


def skill_panel(skill) -> InfoPanel:
    body = [
        f"Cooldown {skill.cooldown:.0f}s" + (f"  •  Cost {skill.cost}g" if skill.cost else ""),
        getattr(skill, "description", "") or "",
    ]
    return InfoPanel(
        title=skill.display_name,
        body=tuple(b for b in body if b),
        accent=(168, 212, 232),
    )


def _describe_family(family: str) -> str:
    return {
        "archer": "Archer Tower — cheap physical single-target. Hits air and ground.",
        "barracks": "Barracks — spawns soldiers that block enemies on the path.",
        "mage": "Mage Tower — expensive magic damage. Great vs. armored foes.",
        "artillery": "Artillery — lobs AoE shots. Ground-only unless upgraded.",
    }.get(family, "")


def _describe_extras(extras: dict) -> str:
    bits: list[str] = []
    if "aoe_radius" in extras:
        bits.append(f"AoE r{int(extras['aoe_radius'])}")
    if "pierce_armor" in extras:
        bits.append(f"Armor pierce {int(extras['pierce_armor'])}")
    if "true_damage" in extras:
        bits.append("True damage")
    if "multishot" in extras:
        bits.append(f"{int(extras['multishot'])} shots per volley")
    if "burn_dps" in extras:
        bits.append(f"Burn {int(extras['burn_dps'])} dps")
    if "poison_dps" in extras:
        bits.append(f"Poison {int(extras['poison_dps'])} dps")
    if "chain_jumps" in extras:
        bits.append(f"Chains to {int(extras['chain_jumps'])} targets")
    if "unit_count" in extras:
        bits.append(f"{int(extras['unit_count'])} soldiers")
    if extras.get("ground_only"):
        bits.append("Ground only")
    return " • ".join(bits)
