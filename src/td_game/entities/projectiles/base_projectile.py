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
    """Lobs toward a target point; on landing, deals AoE damage.

    Height of the arc scales with throw distance so a far cannon shot
    visibly lofts higher than a near one — gives the cannons real
    weight. Sprite rotates with the tangent direction of the arc so
    the cannonball looks like it's traveling correctly.
    """

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
        distance = math.hypot(target_x - x, target_y - y)
        self._total_time = distance / speed if speed > 0 else 0.01
        # Arc height scales with distance — 60-160 px is readable without
        # leaving the play area.
        self.arc_height = max(60.0, min(160.0, distance * 0.55))

    def on_update(self, dt: float) -> None:
        super().on_update(dt)
        if self.dead:
            return
        self._elapsed += dt
        t = min(1.0, self._elapsed / self._total_time)
        dx = self.target_x - self._start_x
        dy_base = self.target_y - self._start_y
        self.center_x = self._start_x + dx * t
        arc = self.arc_height * math.sin(math.pi * t)
        self.center_y = self._start_y + dy_base * t + arc
        # Rotate to tangent direction (derivative of the parabolic path).
        dxdt = dx
        dydt = dy_base + self.arc_height * math.pi * math.cos(math.pi * t)
        self.angle = math.degrees(math.atan2(dydt, dxdt))
        if t >= 1.0:
            # AoE resolved by the combat system, which reads `aoe_radius`.
            self.dead = True


class ArcToTargetProjectile(BaseProjectile):
    """Ballistic projectile that arcs toward an enemy and hits them on landing.

    Unlike a HomingProjectile it doesn't track sharply — it follows a
    parabola computed from start→target and only drifts its endpoint
    toward the target's current position each frame. Gives KR-style
    arrow flight: visible arc, rotation along the path, minor tracking
    so a moving enemy still gets hit.
    """

    def __init__(self, texture: arcade.Texture, x: float, y: float, target,
                 speed: float, packet: DamagePacket, arc_height: float | None = None) -> None:
        super().__init__(texture, x, y, speed, packet)
        self.target = target
        self._start_x = x
        self._start_y = y
        self._elapsed = 0.0
        initial_dist = math.hypot(target.center_x - x, target.center_y - y)
        self._total_time = max(0.2, initial_dist / speed) if speed > 0 else 0.5
        if arc_height is None:
            arc_height = max(45.0, min(110.0, initial_dist * 0.45))
        self.arc_height = arc_height

    def on_update(self, dt: float) -> None:
        super().on_update(dt)
        if self.dead:
            return
        if not self.target.alive:
            # Target died mid-flight — let the arrow complete the arc to
            # its last known position, then disappear without damage.
            self.dead = True
            return
        self._elapsed += dt
        t = min(1.0, self._elapsed / self._total_time)
        tx = self.target.center_x
        ty = self.target.center_y
        dx = tx - self._start_x
        dy_base = ty - self._start_y
        self.center_x = self._start_x + dx * t
        arc = self.arc_height * math.sin(math.pi * t)
        self.center_y = self._start_y + dy_base * t + arc
        # Tangent rotation so the arrow visually banks up then down.
        dxdt = dx
        dydt = dy_base + self.arc_height * math.pi * math.cos(math.pi * t)
        self.angle = math.degrees(math.atan2(dydt, dxdt))
        if t >= 1.0:
            self.on_impact(self.target, None)


class FallingProjectile(BaseProjectile):
    """Falls straight down from spawn to a target point, dealing AoE on landing.

    Used by the Meteor skill's rain — each meteor is spawned above the
    play area with a short pre-delay, then drops onto its slightly
    randomized landing point. AoE resolves via the combat system which
    reads `aoe_radius`.
    """

    def __init__(self, texture: arcade.Texture, target_x: float, target_y: float,
                 spawn_y: float, speed: float, packet: DamagePacket,
                 aoe_radius: float, fall_delay: float = 0.0) -> None:
        super().__init__(texture, target_x, spawn_y, speed, packet)
        self.target_x = target_x
        self.target_y = target_y
        self.aoe_radius = aoe_radius
        self.fall_delay = fall_delay
        self.alpha = 0 if fall_delay > 0 else 255

    def on_update(self, dt: float) -> None:
        super().on_update(dt)
        if self.dead:
            return
        if self.fall_delay > 0:
            self.fall_delay -= dt
            if self.fall_delay <= 0:
                self.alpha = 255
            return
        dy = self.target_y - self.center_y
        step = self.speed * dt
        if abs(dy) <= step:
            self.center_y = self.target_y
            self.dead = True
            return
        # Always moving downward.
        self.center_y += -step if dy < 0 else step
        # Slight wobble for visual interest.
        self.angle = (self.angle + 360 * dt) % 360


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
