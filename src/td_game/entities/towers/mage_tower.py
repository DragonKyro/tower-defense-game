"""Mage tower — magic ranged damage, optional DoT."""
from __future__ import annotations

from td_game.core.constants import DamageType
from td_game.core.damage import DamagePacket
from td_game.core.resources import load_texture

from .base_tower import BaseTower
from ..projectiles.base_projectile import HomingProjectile


class MageTower(BaseTower):
    family = "mage"
    can_hit_ground = True
    can_hit_flying = True

    def perform_attack(self, target, scene) -> None:
        extras = self._row.extras
        dmg_type = DamageType.TRUE if extras.get("true_damage") else DamageType.MAGIC
        on_hit = []
        if "burn_dps" in extras:
            from td_game.effects.burn import Burn
            dps = float(extras["burn_dps"])
            dur = float(extras["burn_time"])
            on_hit.append(lambda dps=dps, dur=dur: Burn(dps=dps, duration=dur))
        if "poison_dps" in extras:
            from td_game.effects.poison import Poison
            dps = float(extras["poison_dps"])
            dur = float(extras["poison_time"])
            on_hit.append(lambda dps=dps, dur=dur: Poison(dps=dps, duration=dur))
        packet = DamagePacket(amount=self.damage, type=dmg_type, source=self, on_hit_effects=on_hit)
        tex = load_texture("projectiles", self._row.projectile or "bolt_0")
        scene.spawn_projectile(HomingProjectile(tex, self.center_x, self.center_y, 380, packet, target))
