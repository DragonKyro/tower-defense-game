"""Combat system: projectile impacts + engagement between units and enemies."""
from __future__ import annotations

from typing import TYPE_CHECKING

from td_game.entities.projectiles.base_projectile import ArcProjectile, HomingProjectile, StraightProjectile

from . import collision

if TYPE_CHECKING:
    pass


class CombatSystem:
    def __init__(self, state) -> None:
        self.state = state

    # --- engagement -------------------------------------------------

    def resolve_engagement(self, units, enemies) -> None:
        """Pair unengaged enemies with the nearest unit that has a free block slot."""
        for enemy in enemies:
            if not enemy.alive or enemy.stunned:
                continue
            # If already being blocked, nothing to do.
            already = any(enemy in u.blocking for u in units)
            if already:
                continue
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

    def tick_projectiles(self, projectiles, enemies) -> None:
        for p in list(projectiles):
            if p.dead:
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
            elif isinstance(p, ArcProjectile) and p.dead and p.aoe_radius > 0:
                for e in collision.in_radius(p.center_x, p.center_y, p.aoe_radius, enemies):
                    e.take_damage(p.packet)
