"""Archer tower — ranged single-target."""
from __future__ import annotations

from td_game.core.constants import DamageType
from td_game.core.damage import DamagePacket
from td_game.core.resources import load_texture

from .base_tower import BaseTower
from ..projectiles.base_projectile import ArcToTargetProjectile


class ArcherTower(BaseTower):
    family = "archer"
    can_hit_ground = True
    can_hit_flying = True

    def perform_attack(self, target, scene) -> None:
        extras = self._row.extras
        packet = DamagePacket(
            amount=self.damage,
            type=DamageType.PHYSICAL,
            source=self,
            pierce_armor=float(extras.get("pierce_armor", 0.0)),
        )
        proj_sprite = self._row.projectile or "arrow_0"
        tex = load_texture("projectiles", proj_sprite)
        shots = int(extras.get("multishot", 1))
        for i in range(shots):
            # Multishot: fire at up to N distinct targets if available.
            t = target if i == 0 else self._alt_target(scene, skip=target)
            if t is None:
                break
            # Arrows loft — parabolic flight that gently tracks the target,
            # like the archer towers in Kingdom Rush.
            scene.spawn_projectile(
                ArcToTargetProjectile(tex, self.center_x, self.center_y,
                                      target=t, speed=380, packet=packet)
            )

    def _alt_target(self, scene, skip) -> object | None:
        from . import targeting as tgt
        choices = [e for e in scene.enemies if e is not skip]
        return tgt.pick(self, choices)
