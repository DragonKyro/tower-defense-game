"""Projectile base.

Subclasses (Arrow, Cannonball, MagicBolt, Meteor) differ in motion and
impact. They all ultimately deliver a DamagePacket to one or more enemies
and then expire.
"""
from __future__ import annotations

import math
from typing import TYPE_CHECKING

import arcade

from td_game.core.damage import DamagePacket
from td_game.entities.entity import Entity

if TYPE_CHECKING:
    from td_game.entities.enemies.base_enemy import BaseEnemy


class BaseProjectile(Entity):
    def __init__(
        self,
        texture: arcade.Texture,
        x: float,
        y: float,
        speed: float,
        packet: DamagePacket,
    ) -> None:
        super().__init__(texture, x, y, max_hp=1)
        self.speed = speed
        self.packet = packet
        self.dead = False

    def on_impact(self, target: "BaseEnemy", scene) -> None:
        target.take_damage(self.packet)
        for factory in self.packet.on_hit_effects:
            target.apply_effect(factory())
        self.dead = True


class HomingProjectile(BaseProjectile):
    """Seeks a target until it hits or target dies."""

    def __init__(self, texture: arcade.Texture, x: float, y: float, speed: float,
                 packet: DamagePacket, target: "BaseEnemy") -> None:
        super().__init__(texture, x, y, speed, packet)
        self.target = target

    def on_update(self, dt: float) -> None:
        super().on_update(dt)
        if self.dead:
            return
        if not self.target.alive:
            self.dead = True
            return
        dx = self.target.center_x - self.center_x
        dy = self.target.center_y - self.center_y
        dist = math.hypot(dx, dy)
        step = self.speed * dt
        if dist <= step or dist < 6:
            self.center_x = self.target.center_x
            self.center_y = self.target.center_y
            self.on_impact(self.target, None)
            return
        self.center_x += dx / dist * step
        self.center_y += dy / dist * step
        self.angle = math.degrees(math.atan2(dy, dx))


class ArcProjectile(BaseProjectile):
    """Lobs toward a target point; on landing, deals AoE damage."""

    def __init__(self, texture: arcade.Texture, x: float, y: float,
                 target_x: float, target_y: float, speed: float,
                 packet: DamagePacket, aoe_radius: float) -> None:
        super().__init__(texture, x, y, speed, packet)
        self.target_x = target_x
        self.target_y = target_y
        self.aoe_radius = aoe_radius
        self._elapsed = 0.0
        self._start_x = x
        self._start_y = y
        self._total_time = math.hypot(target_x - x, target_y - y) / speed or 0.01

    def on_update(self, dt: float) -> None:
        super().on_update(dt)
        if self.dead:
            return
        self._elapsed += dt
        t = min(1.0, self._elapsed / self._total_time)
        # Arc via parabolic y-offset.
        self.center_x = self._start_x + (self.target_x - self._start_x) * t
        base_y = self._start_y + (self.target_y - self._start_y) * t
        arc = 40 * math.sin(math.pi * t)
        self.center_y = base_y + arc
        if t >= 1.0:
            # AoE resolved by the combat system, which reads `aoe_radius`.
            self.dead = True


class StraightProjectile(BaseProjectile):
    """Flies in a straight line toward a point, pierces or dies on first hit."""

    def __init__(self, texture: arcade.Texture, x: float, y: float,
                 dir_x: float, dir_y: float, speed: float,
                 packet: DamagePacket, max_range: float) -> None:
        super().__init__(texture, x, y, speed, packet)
        norm = math.hypot(dir_x, dir_y) or 1.0
        self.vx = dir_x / norm * speed
        self.vy = dir_y / norm * speed
        self.angle = math.degrees(math.atan2(dir_y, dir_x))
        self._distance_left = max_range

    def on_update(self, dt: float) -> None:
        super().on_update(dt)
        if self.dead:
            return
        self.center_x += self.vx * dt
        self.center_y += self.vy * dt
        self._distance_left -= self.speed * dt
        if self._distance_left <= 0:
            self.dead = True
