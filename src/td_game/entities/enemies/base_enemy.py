"""Base enemy.

Stats are typically set from `td_game.data.enemies.ENEMIES`, not in
subclass code. That keeps enemy tuning in a single table.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import arcade

from td_game.core.constants import EffectTag
from td_game.core.events import ENEMY_KILLED, ENEMY_LEAKED
from td_game.entities.entity import Entity

if TYPE_CHECKING:
    from td_game.world.path import Path, PathRegistry


@dataclass
class EnemyStats:
    id: str
    display_name: str
    max_hp: float
    speed: float                         # px/sec
    armor: float = 0.0
    magic_resist: float = 0.0            # 0..1
    bounty: int = 5                      # gold on kill
    lives_cost: int = 1                  # lives lost if it reaches exit
    flying: bool = False
    immunities: frozenset[EffectTag] = field(default_factory=frozenset)
    sprite: str = "orc_idle"             # resources key under 'enemies'
    # Optional: reward XP to heroes on kill, aura effects, death effects —
    # add fields here as features land.


class BaseEnemy(Entity):
    def __init__(self, stats: EnemyStats, texture: arcade.Texture, bus=None) -> None:
        super().__init__(texture, x=0, y=0, max_hp=stats.max_hp)
        self.stats = stats
        self.armor = stats.armor
        self.magic_resist = stats.magic_resist
        self.immunities = stats.immunities
        self.base_speed = stats.speed
        self.speed_multiplier: float = 1.0
        self.stunned: bool = False
        self.bus = bus  # EventBus
        # Pathing state — filled in by wave_manager / spawner:
        self.current_path: "Path | None" = None
        self.wp_index: int = 0
        self.leaked: bool = False

    @property
    def speed(self) -> float:
        return 0.0 if self.stunned else self.base_speed * self.speed_multiplier

    @property
    def is_flying(self) -> bool:
        return self.stats.flying

    def on_death(self) -> None:
        super().on_death()
        if self.bus is not None and not self.leaked:
            self.bus.publish(ENEMY_KILLED, enemy=self, bounty=self.stats.bounty)

    def on_leak(self) -> None:
        """Called by path_follower when the enemy reaches the exit."""
        self.leaked = True
        self.alive = False
        for eff in list(self.effects):
            eff.remove(self)
        if self.bus is not None:
            self.bus.publish(ENEMY_LEAKED, enemy=self, lives_cost=self.stats.lives_cost)
