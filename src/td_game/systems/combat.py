"""Combat system: projectile impacts + engagement between units and enemies."""
from __future__ import annotations

from typing import TYPE_CHECKING

from td_game.entities.projectiles.base_projectile import (
    ArcProjectile,
    ArcToTargetProjectile,
    FallingProjectile,
    HomingProjectile,
    StraightProjectile,
)

from . import collision

if TYPE_CHECKING:
    pass


class CombatSystem:
    def __init__(self, state) -> None:
        self.state = state

    # --- engagement -------------------------------------------------

    def resolve_engagement(self, units, enemies) -> None:
        """Pair unengaged enemies with the nearest unit that has a free block slot.

        If the original blocker died, allow a new unit to pick up the enemy
        so it doesn't resume walking mid-brawl.
        """
        for enemy in enemies:
            if not enemy.alive or enemy.stunned:
                continue
            # If any *living* unit is blocking this enemy, leave it alone.
            already_live = any(enemy in u.blocking and u.alive for u in units)
            if already_live:
                continue
            # Clean stale references held by dead units.
            for u in units:
                if enemy in u.blocking and not u.alive:
                    u.blocking.remove(enemy)
            if enemy.engaged_by is not None and not enemy.engaged_by.alive:
                enemy.engaged_by = None
            # Find nearest unit in engage_radius with a slot.
            best = None
            best_d2 = float("inf")
            for u in units:
                if not u.alive or not u.has_free_slot():
                    continue
                dx = u.center_x - enemy.center_x
                dy = u.center_y - enemy.center_y
                d2 = dx * dx + dy * dy
                if d2 <= u.engage_radius * u.engage_radius and d2 < best_d2:
                    best = u
                    best_d2 = d2
            if best is not None:
                best.engage(enemy)

    # --- projectiles ------------------------------------------------

    def tick_projectiles(self, projectiles, enemies, scene) -> None:
        for p in list(projectiles):
            if p.dead:
                # Any projectile that carries an `aoe_radius` resolves a
                # splash on impact (cannons, meteors). Single-target
                # projectiles (arrows, magic bolts) already applied their
                # damage inside `on_impact` and just need culling.
                aoe = getattr(p, "aoe_radius", 0.0)
                if aoe > 0 and not getattr(p, "_aoe_resolved", False):
                    p._aoe_resolved = True
                    for e in collision.in_radius(p.center_x, p.center_y, aoe, enemies):
                        e.take_damage(p.packet)
                    if scene is not None and hasattr(scene, "spawn_explosion"):
                        scene.spawn_explosion(p.center_x, p.center_y, radius=aoe)
                p.remove_from_sprite_lists()
                continue
            # Straight & homing: hit test on overlap.
            if isinstance(p, (StraightProjectile, HomingProjectile)):
                for e in enemies:
                    if not e.alive:
                        continue
                    dx = e.center_x - p.center_x
                    dy = e.center_y - p.center_y
                    if dx * dx + dy * dy <= 16 * 16:  # ~hit radius
                        p.on_impact(e, None)
                        break
