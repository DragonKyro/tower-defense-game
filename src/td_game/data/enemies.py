"""Enemy stat table.

Keyed by string id so waves and level files reference enemies without
importing their classes. Adding a new enemy = adding a row here (and,
only if it needs unique behavior, a subclass in
`entities/enemies/enemies.py`).

`sprite_base` is the short name the animation controller expands into
`<base>_idle_0`, `<base>_walk_0..3`, `<base>_death_0`.
"""
from __future__ import annotations

from td_game.core.constants import EffectTag
from td_game.entities.enemies.base_enemy import EnemyStats


ENEMIES: dict[str, EnemyStats] = {
    "goblin": EnemyStats(
        id="goblin",
        display_name="Goblin Scout",
        description=(
            "Swift, lightly armored raiders. Dangerous in numbers; trivial "
            "in isolation. Archers make short work of them."
        ),
        max_hp=40,
        speed=90,
        armor=0,
        bounty=3,
        lives_cost=1,
        melee_damage=4,
        melee_interval=0.9,
        sprite_base="goblin",
    ),
    "orc": EnemyStats(
        id="orc",
        display_name="Orc Warrior",
        description=(
            "Tough front-line grunts with modest armor. Barracks soldiers "
            "can hold them while archers and mages whittle them down."
        ),
        max_hp=110,
        speed=55,
        armor=3,
        bounty=6,
        lives_cost=1,
        melee_damage=12,
        melee_interval=1.2,
        sprite_base="orc",
    ),
    "troll": EnemyStats(
        id="troll",
        display_name="Cave Troll",
        description=(
            "Massive, heavily armored. Cleaves lives fast if they leak. "
            "Artillery and armor-piercing specialists shine here."
        ),
        max_hp=320,
        speed=40,
        armor=8,
        bounty=15,
        lives_cost=2,
        melee_damage=28,
        melee_interval=1.4,
        sprite_base="troll",
    ),
    "wraith": EnemyStats(
        id="wraith",
        display_name="Wraith",
        description=(
            "Flying spirit, immune to poison and burn. Only flying-capable "
            "towers (archer/mage/tesla/rocket) can hit them."
        ),
        max_hp=140,
        speed=70,
        armor=0,
        magic_resist=0.4,
        bounty=10,
        lives_cost=1,
        melee_damage=9,
        melee_interval=1.1,
        flying=True,
        immunities=frozenset({EffectTag.POISON, EffectTag.BURN}),
        sprite_base="wraith",
    ),
    "dragon": EnemyStats(
        id="dragon",
        display_name="Red Dragon",
        description=(
            "Boss-tier flier. Extreme HP, burn and stun immune. Focus-fire "
            "with your strongest specializations and spend meteors freely."
        ),
        max_hp=900,
        speed=60,
        armor=6,
        magic_resist=0.3,
        bounty=60,
        lives_cost=5,
        melee_damage=50,
        melee_interval=1.5,
        flying=True,
        immunities=frozenset({EffectTag.BURN, EffectTag.STUN}),
        sprite_base="dragon",
    ),
}
