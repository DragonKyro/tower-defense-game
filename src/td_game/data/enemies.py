"""Enemy stat table.

Keyed by string id so waves and level files reference enemies without
importing their classes. Adding a new enemy = adding a row here (and,
only if it needs unique behavior, a subclass in
`entities/enemies/enemies.py`).
"""
from __future__ import annotations

from td_game.core.constants import EffectTag
from td_game.entities.enemies.base_enemy import EnemyStats


ENEMIES: dict[str, EnemyStats] = {
    "goblin": EnemyStats(
        id="goblin",
        display_name="Goblin Scout",
        max_hp=40,
        speed=90,
        armor=0,
        bounty=3,
        lives_cost=1,
        sprite="goblin_idle",
    ),
    "orc": EnemyStats(
        id="orc",
        display_name="Orc Warrior",
        max_hp=110,
        speed=55,
        armor=3,
        bounty=6,
        lives_cost=1,
        sprite="orc_idle",
    ),
    "troll": EnemyStats(
        id="troll",
        display_name="Troll",
        max_hp=320,
        speed=40,
        armor=8,
        bounty=15,
        lives_cost=2,
        sprite="troll_idle",
    ),
    "wraith": EnemyStats(
        id="wraith",
        display_name="Wraith",
        max_hp=140,
        speed=70,
        armor=0,
        magic_resist=0.4,
        bounty=10,
        lives_cost=1,
        flying=True,
        immunities=frozenset({EffectTag.POISON, EffectTag.BURN}),
        sprite="wraith_idle",
    ),
    "dragon": EnemyStats(
        id="dragon",
        display_name="Dragon",
        max_hp=900,
        speed=60,
        armor=6,
        magic_resist=0.3,
        bounty=60,
        lives_cost=5,
        flying=True,
        immunities=frozenset({EffectTag.BURN, EffectTag.STUN}),
        sprite="dragon_idle",
    ),
}
