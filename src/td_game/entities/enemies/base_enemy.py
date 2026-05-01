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
    melee_damage: float = 6.0            # dmg/hit when fighting a blocking unit
    melee_interval: float = 1.1          # seconds between melee hits
    flying: bool = False
    immunities: frozenset[EffectTag] = field(default_factory=frozenset)
    sprite_base: str = "orc"             # short id; animations derived from it
    description: str = ""                # shown in tooltips / info panels
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
        # Melee engagement: set by a BaseUnit when it blocks us.
        self.engaged_by: "object | None" = None
        self._attack_cd: float = 0.0

    @property
    def speed(self) -> float:
        return 0.0 if self.stunned else self.base_speed * self.speed_multiplier

    def on_update(self, dt: float) -> None:
        # Disengage if our melee target died.
        if self.engaged_by is not None and not getattr(self.engaged_by, "alive", False):
            self.engaged_by = None

        # Melee attack a blocking unit.
        if self.engaged_by is not None and self.alive and not self.stunned:
            self._attack_cd -= dt
            if self._attack_cd <= 0:
                from td_game.core.constants import DamageType
                from td_game.core.damage import DamagePacket
                self.engaged_by.take_damage(
                    DamagePacket(self.stats.melee_damage, DamageType.PHYSICAL, source=self)
                )
                self._attack_cd = self.stats.melee_interval
                # Face the target smoothly.
                if self.engaged_by.center_x < self.center_x - 0.1:
                    self.face(-1)
                elif self.engaged_by.center_x > self.center_x + 0.1:
                    self.face(1)

        # Pick walking vs idle state each frame so stuns/slows/engagements are visible.
        if self.anim is not None and self.alive:
            from td_game.graphics.anim_controller import AnimState
            if self.stunned or self.engaged_by is not None:
                self.anim.set_state(AnimState.IDLE)
            else:
                self.anim.set_state(AnimState.WALK)
        super().on_update(dt)

    @property
    def is_flying(self) -> bool:
        return self.stats.flying

    def on_death(self) -> None:
        super().on_death()
        # Trigger death animation if present.
        if self.anim is not None:
            from td_game.graphics.anim_controller import AnimState
            self.anim.set_state(AnimState.DEATH)
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
