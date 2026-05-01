"""Sample hero: Knight (melee tank)."""
from __future__ import annotations

from td_game.core.resources import load_animation_frames, load_texture
from td_game.entities.heroes.base_hero import BaseHero, HeroStats
from td_game.graphics.animation import Animation, LoopMode
from td_game.graphics.anim_controller import AnimationController, AnimState
from td_game.skills.hero.knight_skills import Rally, ShieldBash


KNIGHT_STATS = HeroStats(
    id="knight",
    display_name="Sir Aric",
    description="Stalwart defender. Shield Bash stuns blocked enemies; Rally heals and armors him up.",
    max_hp=260,
    damage=28,
    attack_interval=0.9,
    speed=85,
    armor=5,
    magic_resist=0.1,
    sprite_base="knight",
)


def make_knight(x: float, y: float, bus=None) -> BaseHero:
    tex = load_texture("heroes", f"{KNIGHT_STATS.sprite_base}_idle_0")
    skills = [ShieldBash(), Rally()]
    hero = BaseHero(KNIGHT_STATS, tex, skills, x, y, bus=bus)
    idle = Animation(frames=load_animation_frames("heroes", f"{KNIGHT_STATS.sprite_base}_idle", 2),
                     frame_duration=0.5, loop=LoopMode.PING_PONG)
    walk = Animation(frames=load_animation_frames("heroes", f"{KNIGHT_STATS.sprite_base}_walk", 6),
                     frame_duration=0.09, loop=LoopMode.LOOP)
    attack = Animation(frames=load_animation_frames("heroes", f"{KNIGHT_STATS.sprite_base}_attack", 3),
                       frame_duration=0.07, loop=LoopMode.ONCE)
    death = Animation(frames=load_animation_frames("heroes", f"{KNIGHT_STATS.sprite_base}_death", 4),
                      frame_duration=0.14, loop=LoopMode.ONCE)
    hero.anim = AnimationController(
        states={AnimState.IDLE: idle, AnimState.WALK: walk,
                AnimState.ATTACK: attack, AnimState.DEATH: death},
        initial=AnimState.IDLE,
    )
    return hero
