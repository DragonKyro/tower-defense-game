"""Bottom HUD: gold, lives, wave, hero portraits, hero skills, global skills, pause.

Layout (left-to-right on the right side of the strip):
    [hero portraits] [selected-hero skills] [global skills] [speed] [pause]

Skill buttons render a rising dark mask for cooldown and a centered
seconds-remaining number.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import arcade

from td_game.core.constants import HUD_HEIGHT, SCREEN_WIDTH
from td_game.core.resources import load_texture
from td_game.graphics.procedural import palette as P

from .button import Button
from .tooltip import skill_panel


@dataclass
class _SkillButton:
    btn: Button
    skill: object
    cooldown_text: arcade.Text


@dataclass
class _HeroPortrait:
    hero: object
    btn: Button
    respawn_text: arcade.Text


class HUD:
    ICON_W = 56
    ICON_H = 56
    SPACING = 10
    PORTRAIT_W = 56
    PORTRAIT_H = 56
    # Reserve enough space in the layout for these maxima so clusters never
    # overlap as the selection changes.
    MAX_HERO_SKILLS = 2
    MAX_HEROES = 2
    CLUSTER_GAP = 28   # extra padding between portrait cluster and hero skills

    def __init__(
        self,
        state,
        skills: list,
        on_cast: Callable,
        on_pause: Callable,
        on_speed_toggle: Callable,
        on_cast_hero: Callable | None = None,
        on_select_hero: Callable | None = None,
    ) -> None:
        self.state = state
        self.global_skills = list(skills)
        self.on_cast = on_cast
        self.on_cast_hero = on_cast_hero or (lambda s, h: on_cast(s))
        self.on_pause = on_pause
        self.on_speed_toggle = on_speed_toggle
        self.on_select_hero = on_select_hero or (lambda h: None)

        self._gold_text = arcade.Text("Gold: 0", 18, HUD_HEIGHT - 24,
                                      color=(248, 220, 120), font_size=16, bold=True)
        self._lives_text = arcade.Text("Lives: 0", 160, HUD_HEIGHT - 24,
                                       color=(240, 108, 100), font_size=16, bold=True)
        self._wave_text = arcade.Text("Wave: 0/0", 310, HUD_HEIGHT - 24,
                                      color=(200, 220, 244), font_size=16, bold=True)
        self._hint_text = arcade.Text(
            "L-click build / select  •  R-click: move hero / rally barracks  •  Hover any icon for details  •  1/2 pick hero  •  3/4 hero skills  •  SPACE next wave  •  P pause",
            18, 16, color=(180, 180, 192), font_size=10,
        )

        # Static buttons (pause + speed); populated immediately.
        self._pause_btn: Button | None = None
        self._speed_btn: Button | None = None

        # Skill clusters built once we know the heroes.
        self._global_skill_buttons: list[_SkillButton] = []
        self._hero_skill_buttons: list[_SkillButton] = []
        self._portraits: list[_HeroPortrait] = []
        self._selected_hero = None

        self._build_static()
        self._build_global_skills()

    # --- geometry --------------------------------------------------

    def _right_cluster_left(self) -> float:
        right_edge = SCREEN_WIDTH - 16
        # 60 pause + spacing + 60 speed
        return right_edge - 32 - 60 - self.SPACING - 60

    def _global_cluster_right(self) -> float:
        """Center-x of the rightmost global skill button."""
        return self._right_cluster_left() - self.SPACING - self.ICON_W / 2

    def _global_cluster_left_edge(self) -> float:
        """Left pixel edge of the global skill cluster."""
        n = len(self.global_skills)
        rightmost_center = self._global_cluster_right()
        return rightmost_center - self.ICON_W / 2 - (n - 1) * (self.ICON_W + self.SPACING)

    def _hero_cluster_right(self) -> float:
        """Center-x of the rightmost hero skill button."""
        return self._global_cluster_left_edge() - self.SPACING - self.ICON_W / 2

    def _hero_cluster_left_edge(self) -> float:
        """Left pixel edge reserved for hero skills (max slots, not current)."""
        return (self._hero_cluster_right() - self.ICON_W / 2
                - (self.MAX_HERO_SKILLS - 1) * (self.ICON_W + self.SPACING))

    def _portrait_cluster_right(self) -> float:
        """Center-x of the rightmost hero portrait. Fixed — doesn't shift."""
        return self._hero_cluster_left_edge() - self.CLUSTER_GAP - self.PORTRAIT_W / 2

    # --- construction ----------------------------------------------

    def _build_static(self) -> None:
        y = HUD_HEIGHT / 2
        right_edge = SCREEN_WIDTH - 16
        self._pause_btn = Button(right_edge - 32, y, 60, 44, "II",
                                 self.on_pause, hotkey="P")
        self._speed_btn = Button(right_edge - 32 - 60 - self.SPACING, y, 60, 44, "1x",
                                 self.on_speed_toggle, hotkey="F")

    def _build_global_skills(self) -> None:
        y = HUD_HEIGHT / 2
        hotkeys = ("Q", "W")
        start_x = self._global_cluster_right()
        self._global_skill_buttons = []
        for idx, skill in enumerate(self.global_skills):
            bx = start_x - idx * (self.ICON_W + self.SPACING)
            tex = load_texture("skills", skill.icon) if skill.icon else None
            b = Button(
                bx, y, self.ICON_W, self.ICON_H, skill.display_name,
                on_click=(lambda s=skill: self.on_cast(s)),
                icon=tex,
                hotkey=hotkeys[idx] if idx < len(hotkeys) else None,
            )
            cdt = arcade.Text("", bx, y, color=(255, 255, 255), font_size=18, bold=True,
                              anchor_x="center", anchor_y="center")
            self._global_skill_buttons.append(_SkillButton(b, skill, cdt))

    # --- hero portraits + skills -----------------------------------

    def set_heroes(self, heroes: list) -> None:
        """Register the level's heroes so we can draw portraits for them."""
        self._portraits = []
        if not heroes:
            return
        y = HUD_HEIGHT / 2
        start_x = self._portrait_cluster_right()
        for idx, hero in enumerate(heroes):
            bx = start_x - idx * (self.PORTRAIT_W + self.SPACING)
            # Use the hero's idle frame as the portrait icon.
            tex = load_texture("heroes", f"{hero.stats.sprite_base}_idle_0")
            hotkey = ("1", "2")[idx] if idx < 2 else None
            b = Button(
                bx, y, self.PORTRAIT_W, self.PORTRAIT_H, hero.stats.display_name,
                on_click=(lambda h=hero: self.on_select_hero(h)),
                icon=tex,
                hotkey=hotkey,
            )
            rt = arcade.Text(
                "", bx, y, color=(240, 240, 240), font_size=20, bold=True,
                anchor_x="center", anchor_y="center",
            )
            self._portraits.append(_HeroPortrait(hero, b, rt))

    def set_selected_hero(self, hero) -> None:
        if hero is self._selected_hero:
            # Still rebuild skill cluster so fresh hero rebuild if hotkeys changed.
            return
        self._selected_hero = hero
        self._rebuild_hero_skills()

    def _rebuild_hero_skills(self) -> None:
        hero = self._selected_hero
        self._hero_skill_buttons = []
        if hero is None:
            return
        y = HUD_HEIGHT / 2
        right_edge = self._global_cluster_right()
        right_edge -= len(self.global_skills) * (self.ICON_W + self.SPACING)
        hotkeys = ("3", "4", "5")
        for idx, skill in enumerate(hero.skills):
            bx = right_edge - idx * (self.ICON_W + self.SPACING)
            tex = load_texture("skills", skill.icon) if skill.icon else None
            b = Button(
                bx, y, self.ICON_W, self.ICON_H, skill.display_name,
                on_click=(lambda s=skill, h=hero: self.on_cast_hero(s, h)),
                icon=tex,
                hotkey=hotkeys[idx] if idx < len(hotkeys) else None,
            )
            cdt = arcade.Text("", bx, y, color=(255, 255, 255), font_size=18, bold=True,
                              anchor_x="center", anchor_y="center")
            self._hero_skill_buttons.append(_SkillButton(b, skill, cdt))

    # --- per-frame -------------------------------------------------

    def _iter_buttons(self):
        yield self._pause_btn
        yield self._speed_btn
        for sb in self._global_skill_buttons:
            yield sb.btn
        for sb in self._hero_skill_buttons:
            yield sb.btn
        for p in self._portraits:
            yield p.btn

    def _iter_skill_buttons(self):
        yield from self._global_skill_buttons
        yield from self._hero_skill_buttons

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

        # Skill cooldowns + enabled state.
        for sb in self._iter_skill_buttons():
            skill = sb.skill
            cd_left = max(0.0, getattr(skill, "_cooldown_left", 0.0))
            frac = 0.0
            if skill.cooldown > 0:
                frac = max(0.0, min(1.0, cd_left / skill.cooldown))
            sb.btn.cooldown_fraction = frac
            affordable = self.state.gold >= skill.cost
            live = True
            if any(sb is hs for hs in self._hero_skill_buttons):
                live = self._selected_hero is not None and self._selected_hero.alive
            sb.btn.set_enabled(skill.ready and affordable and live)
            sb.cooldown_text.text = f"{cd_left:.0f}s" if cd_left > 0.1 else ""

        # Portrait respawn timers.
        for p in self._portraits:
            if p.hero.alive:
                # Full-strength portrait; no cooldown mask; no respawn text.
                p.btn.cooldown_fraction = 0.0
                p.btn.set_enabled(True)
                p.respawn_text.text = ""
            else:
                # Respawn mask rising up in real time.
                rt = max(0.0, p.hero.respawn_timer)
                rd = p.hero.respawn_delay or 1.0
                p.btn.cooldown_fraction = max(0.0, min(1.0, rt / rd))
                p.btn.set_enabled(False)
                p.respawn_text.text = f"{rt:.0f}s" if rt > 0.1 else ""

    def update_hover(self, x: float, y: float) -> None:
        for b in self._iter_buttons():
            b.update_hover(x, y)

    # --- draw ------------------------------------------------------

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

        # Buttons.
        for b in self._iter_buttons():
            b.draw()

        # Selection highlight for the active hero portrait.
        for p in self._portraits:
            if p.hero is self._selected_hero:
                left = p.btn.x - p.btn.width / 2 - 2
                right = p.btn.x + p.btn.width / 2 + 2
                bottom = p.btn.y - p.btn.height / 2 - 2
                top = p.btn.y + p.btn.height / 2 + 2
                arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, P.KNIGHT_GOLD, 3)

        # Cooldown / respawn numbers last so they sit on the dark mask.
        for sb in self._iter_skill_buttons():
            if sb.cooldown_text.text:
                sb.cooldown_text.draw()
        for p in self._portraits:
            if p.respawn_text.text:
                p.respawn_text.draw()

        # Hover tooltip (skill descriptions). Drawn on top of the entire HUD.
        for sb in self._iter_skill_buttons():
            if sb.btn.hovered:
                skill_panel(sb.skill).draw(sb.btn.x, sb.btn.y + sb.btn.height / 2 + 6, align="above")
                break

    def _draw_stat_chip(self, x: float, y: float, w: float, h: float, fill, border) -> None:
        arcade.draw_lrbt_rectangle_filled(x, x + w, y, y + h, fill)
        arcade.draw_lrbt_rectangle_filled(x, x + w, y + h - 2, y + h, (*border, 200))
        arcade.draw_lrbt_rectangle_outline(x, x + w, y, y + h, border, 1)

    def handle_click(self, x: float, y: float) -> bool:
        for b in self._iter_buttons():
            if b.click(x, y):
                return True
        return False
