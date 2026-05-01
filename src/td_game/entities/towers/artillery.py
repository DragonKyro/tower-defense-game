"""Artillery tower — lobbed AoE physical damage."""
from __future__ import annotations

from td_game.core.constants import DamageType
from td_game.core.damage import DamagePacket
from td_game.core.resources import load_texture

from .base_tower import BaseTower
from ..projectiles.base_projectile import ArcProjectile


class ArtilleryTower(BaseTower):
    family = "artillery"
    can_hit_ground = True
    can_hit_flying = False  # default; rocket/tesla specs flip this via row extras

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._sync_flight_capability()

    def _apply_row(self, row) -> None:
        super()._apply_row(row)
        self._sync_flight_capability()

    def _sync_flight_capability(self) -> None:
        self.can_hit_flying = not bool(self._row.extras.get("ground_only", True))

    def perform_attack(self, target, scene) -> None:
        extras = self._row.extras
        packet = DamagePacket(amount=self.damage, type=DamageType.SIEGE, source=self)
        tex = load_texture("projectiles", self._row.projectile or "cannonball_0")
        aoe = float(extras.get("aoe_radius", 45))
        scene.spawn_projectile(ArcProjectile(
            tex, self.center_x, self.center_y,
            target.center_x, target.center_y,
            speed=300, packet=packet, aoe_radius=aoe,
        ))
