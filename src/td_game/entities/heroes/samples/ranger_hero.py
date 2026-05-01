"""Sample hero: Ranger (ranged / DoT / mobile)."""
from __future__ import annotations

from td_game.core.resources import load_animation_frames, load_texture
from td_game.entities.heroes.base_hero import BaseHero, HeroStats
from td_game.graphics.animation import Animation, LoopMode
from td_game.graphics.anim_controller import AnimationController, AnimState
from td_game.skills.hero.ranger_skills import PoisonArrow, Volley


RANGER_STATS = HeroStats(
    id="ranger",
    display_name="Elyse of the Greenwood",
    description="Agile ranger. Poison Arrow rots a single target; Volley rains arrows over an area.",
    max_hp=180,
    damage=22,
    attack_interval=0.7,
    speed=110,
    armor=1,
    magic_resist=0.05,
    engage_radius=48,
    sprite_base="ranger",
)


def make_ranger(x: float, y: float, bus=None) -> BaseHero:
    tex = load_texture("heroes", f"{RANGER_STATS.sprite_base}_idle_0")
    skills = [PoisonArrow(), Volley()]
    hero = BaseHero(RANGER_STATS, tex, skills, x, y, bus=bus)
    idle = Animation(frames=load_animation_frames("heroes", f"{RANGER_STATS.sprite_base}_idle", 2),
                     frame_duration=0.5, loop=LoopMode.PING_PONG)
    walk = Animation(frames=load_animation_frames("heroes", f"{RANGER_STATS.sprite_base}_walk", 6),
                     frame_duration=0.09, loop=LoopMode.LOOP)
    attack = Animation(frames=load_animation_frames("heroes", f"{RANGER_STATS.sprite_base}_attack", 3),
                       frame_duration=0.07, loop=LoopMode.ONCE)
    hero.anim = AnimationController(
        states={AnimState.IDLE: idle, AnimState.WALK: walk, AnimState.ATTACK: attack},
        initial=AnimState.IDLE,
    )
    return hero
