"""Bottom HUD strip: gold, lives, wave, skill buttons, pause.

Layout right-to-left: pause, speed, [global skills], [selected-hero skills].

Skill buttons show a rising dark overlay for cooldown and a centered
seconds-remaining number. Disabled (can't afford) buttons are darkened
uniformly by the Button class.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

import arcade

from td_game.core.constants import HUD_HEIGHT, SCREEN_WIDTH
from td_game.core.resources import load_texture
from td_game.graphics.procedural import palette as P

from .button import Button


@dataclass
class _SkillButton:
    btn: Button
    skill: object
    cooldown_text: arcade.Text


class HUD:
    def __init__(
        self,
        state,
        skills: list,
        on_cast: Callable,
        on_pause: Callable,
        on_speed_toggle: Callable,
        on_cast_hero: Callable | None = None,
    ) -> None:
        self.state = state
        self.global_skills = list(skills)
        self.on_cast = on_cast
        self.on_cast_hero = on_cast_hero or on_cast
        self.on_pause = on_pause
        self.on_speed_toggle = on_speed_toggle

        self._gold_text = arcade.Text("Gold: 0", 18, HUD_HEIGHT - 24,
                                      color=(248, 220, 120), font_size=16, bold=True)
        self._lives_text = arcade.Text("Lives: 0", 160, HUD_HEIGHT - 24,
                                       color=(240, 108, 100), font_size=16, bold=True)
        self._wave_text = arcade.Text("Wave: 0/0", 310, HUD_HEIGHT - 24,
                                      color=(200, 220, 244), font_size=16, bold=True)
        self._hint_text = arcade.Text(
            "L-click build / select  •  R-click: move hero or rally barracks  •  1/2: pick hero  •  SPACE: next wave  •  P: pause",
            18, 16, color=(180, 180, 192), font_size=10,
        )
        self._hero_label = arcade.Text(
            "", 0, 0, color=(240, 228, 180), font_size=11, bold=True,
            anchor_x="center", anchor_y="center",
        )

        self.buttons: list[Button] = []
        self.skill_buttons: list[_SkillButton] = []
        # Hero skill buttons rebuild when selection changes.
        self._hero_skill_buttons: list[_SkillButton] = []
        self._selected_hero = None
        self._build_static_buttons()
        self._build_global_skill_buttons()

    # --- layout constants ------------------------------------------

    ICON_W = 56
    ICON_H = 56
    SPACING = 10

    def _right_cluster_left(self) -> float:
        """x-coord of the left edge of the pause/speed cluster."""
        right_edge = SCREEN_WIDTH - 16
        return right_edge - 32 - 60 - self.SPACING - 60

    # --- construction ----------------------------------------------

    def _build_static_buttons(self) -> None:
        y = HUD_HEIGHT / 2
        right_edge = SCREEN_WIDTH - 16
        self._pause_btn = Button(right_edge - 32, y, 60, 44, "II",
                                 self.on_pause, hotkey="P")
        self._speed_btn = Button(right_edge - 32 - 60 - self.SPACING, y, 60, 44, "1x",
                                 self.on_speed_toggle, hotkey="F")
        self.buttons.append(self._pause_btn)
        self.buttons.append(self._speed_btn)

    def _build_global_skill_buttons(self) -> None:
        y = HUD_HEIGHT / 2
        # Right cluster takes ~140px; global skills start to its left.
        start_x = self._right_cluster_left() - self.SPACING - self.ICON_W / 2
        hotkeys = ("Q", "W")
        for idx, skill in enumerate(self.global_skills):
            bx = start_x - idx * (self.ICON_W + self.SPACING)
            self._append_skill_button(skill, bx, y, hotkey=hotkeys[idx] if idx < 2 else None)

    def _append_skill_button(self, skill, x: float, y: float, hotkey: str | None) -> None:
        tex = load_texture("skills", skill.icon) if skill.icon else None
        b = Button(
            x, y, self.ICON_W, self.ICON_H, skill.display_name,
            on_click=(lambda s=skill: self._dispatch_cast(s)),
            icon=tex,
            hotkey=hotkey,
        )
        cdt = arcade.Text(
            "", x, y, color=(255, 255, 255), font_size=18, bold=True,
            anchor_x="center", anchor_y="center",
        )
        self.buttons.append(b)
        sb = _SkillButton(b, skill, cdt)
        return sb

    def _dispatch_cast(self, skill) -> None:
        # Global skills (Reinforcements/Meteor) go to on_cast; hero skills
        # need their owning hero threaded through.
        if skill in self.global_skills:
            self.on_cast(skill)
        else:
            self.on_cast_hero(skill, self._selected_hero)

    def _rebuild_global_skill_buttons(self) -> None:
        # Re-layout the global skill buttons with cached textures.
        self.skill_buttons = []
        y = HUD_HEIGHT / 2
        start_x = self._right_cluster_left() - self.SPACING - self.ICON_W / 2
        # Hero cluster, if any, shifts global skills further left.
        hero_count = len(self._hero_skill_buttons)
        hero_cluster_w = hero_count * (self.ICON_W + self.SPACING) if hero_count else 0
        start_x -= hero_cluster_w
        hotkeys = ("Q", "W")
        for idx, skill in enumerate(self.global_skills):
            bx = start_x - idx * (self.ICON_W + self.SPACING)
            tex = load_texture("skills", skill.icon) if skill.icon else None
            b = Button(
                bx, y, self.ICON_W, self.ICON_H, skill.display_name,
                on_click=(lambda s=skill: self._dispatch_cast(s)),
                icon=tex,
                hotkey=hotkeys[idx] if idx < 2 else None,
            )
            cdt = arcade.Text(
                "", bx, y, color=(255, 255, 255), font_size=18, bold=True,
                anchor_x="center", anchor_y="center",
            )
            self.skill_buttons.append(_SkillButton(b, skill, cdt))

    # --- hero selection --------------------------------------------

    def set_selected_hero(self, hero) -> None:
        if hero is self._selected_hero:
            return
        self._selected_hero = hero
        # Wipe any prior hero buttons out of the master click list.
        self.buttons = [b for b in self.buttons
                        if not any(b is hsb.btn for hsb in self._hero_skill_buttons)]
        self._hero_skill_buttons = []
        if hero is not None:
            y = HUD_HEIGHT / 2
            # Hero cluster sits directly left of the global cluster.
            right_edge = self._right_cluster_left() - self.SPACING - self.ICON_W / 2
            global_count = len(self.global_skills)
            right_edge -= global_count * (self.ICON_W + self.SPACING)
            hotkeys = ("1", "2", "3")
            for idx, skill in enumerate(hero.skills):
                bx = right_edge - idx * (self.ICON_W + self.SPACING)
                tex = load_texture("skills", skill.icon) if skill.icon else None
                b = Button(
                    bx, y, self.ICON_W, self.ICON_H, skill.display_name,
                    on_click=(lambda s=skill: self.on_cast_hero(s, hero)),
                    icon=tex,
                    hotkey=hotkeys[idx] if idx < 3 else None,
                )
                cdt = arcade.Text(
                    "", bx, y, color=(255, 255, 255), font_size=18, bold=True,
                    anchor_x="center", anchor_y="center",
                )
                self.buttons.append(b)
                self._hero_skill_buttons.append(_SkillButton(b, skill, cdt))
            self._hero_label.text = hero.stats.display_name
        else:
            self._hero_label.text = ""

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

        # Every skill button (global + hero) gets its cooldown + enabled
        # state refreshed here.
        all_sbs = self._all_skill_buttons()
        for sb in all_sbs:
            skill = sb.skill
            cd_left = getattr(skill, "_cooldown_left", 0.0)
            frac = 0.0
            if skill.cooldown > 0:
                frac = max(0.0, min(1.0, cd_left / skill.cooldown))
            sb.btn.cooldown_fraction = frac
            affordable = self.state.gold >= skill.cost
            # Hero skills also require a live hero.
            live = True
            if self._selected_hero is not None and sb in self._hero_skill_buttons:
                live = self._selected_hero.alive
            sb.btn.set_enabled(skill.ready and affordable and live)
            sb.cooldown_text.text = f"{cd_left:.0f}s" if cd_left > 0.05 else ""

    def _all_skill_buttons(self) -> list[_SkillButton]:
        # Static global skills live in self.skill_buttons *after* rebuild;
        # until first rebuild they live in whatever the constructor added.
        if not self.skill_buttons:
            self._rebuild_global_skill_buttons()
            # Merge the freshly-built global cluster into the master click list.
            self.buttons = [b for b in self.buttons
                            if not any(b is sb.btn for sb in self.skill_buttons)]
            for sb in self.skill_buttons:
                self.buttons.append(sb.btn)
        return self.skill_buttons + self._hero_skill_buttons

    def update_hover(self, x: float, y: float) -> None:
        for b in self.buttons:
            b.update_hover(x, y)

    # --- rendering --------------------------------------------------

    def draw(self) -> None:
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, HUD_HEIGHT, (22, 24, 32))
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, HUD_HEIGHT - 3, HUD_HEIGHT, P.KNIGHT_GOLD_DARK)
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, HUD_HEIGHT - 2, HUD_HEIGHT - 1, P.KNIGHT_GOLD)
        arcade.draw_lrbt_rectangle_outline(0, SCREEN_WIDTH, 0, HUD_HEIGHT, (100, 90, 70), 1)

        self._draw_stat_chip(6, HUD_HEIGHT - 36, 148, 28, (40, 30, 12), (180, 140, 60))
        self._draw_stat_chip(156, HUD_HEIGHT - 36, 144, 28, (40, 20, 20), (180, 80, 80))
        self._draw_stat_chip(306, HUD_HEIGHT - 36, 160, 28, (20, 30, 48), (100, 130, 180))
        self._gold_text.draw()
        self._lives_text.draw()
        self._wave_text.draw()
        self._hint_text.draw()

        for b in self.buttons:
            b.draw()

        # Cooldown seconds, drawn last so they sit on top of the dark mask.
        for sb in self._all_skill_buttons():
            if sb.cooldown_text.text:
                sb.cooldown_text.draw()

        # Hero portrait label.
        if self._selected_hero is not None and self._hero_skill_buttons:
            bx = self._hero_skill_buttons[-1].btn.x
            self._hero_label.x = bx
            self._hero_label.y = HUD_HEIGHT - 8
            self._hero_label.draw()

    def _draw_stat_chip(self, x: float, y: float, w: float, h: float, fill, border) -> None:
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, fill)
        arcade.draw_lrbt_rectangle_filled(x, x + w, y + h - 2, y + h, (*border, 200))
        arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, border, 1)

    def handle_click(self, x: float, y: float) -> bool:
        for b in self.buttons:
            if b.click(x, y):
                return True
        return False
