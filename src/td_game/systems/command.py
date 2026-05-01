"""Player command layer.

Translates UI intents (build, upgrade, sell, cast skill, rally hero) into
side-effects on the scene + game state. Keeps UI code thin.
"""
from __future__ import annotations

from td_game.entities.towers import factory as tower_factory
from td_game.skills.base_skill import SkillContext


class CommandSystem:
    def __init__(self, scene, state) -> None:
        self.scene = scene
        self.state = state

    # --- towers -----------------------------------------------------

    def build_tower(self, family: str, spot) -> bool:
        cost = tower_factory.base_cost(family)
        if not self.state.spend_gold(cost, reason=f"build:{family}"):
            return False
        tower = tower_factory.build_tower(family, spot.x, spot.y, bus=self.state.bus)
        self.scene.spawn_tower(tower, spot)
        return True

    def upgrade_tower(self, tower, node_id: str) -> bool:
        upgrades = {nid: row for nid, row in tower.next_upgrades()}
        if node_id not in upgrades:
            return False
        if not self.state.spend_gold(upgrades[node_id].cost, reason=f"upgrade:{tower.family}"):
            return False
        return tower.upgrade_to(node_id)

    def sell_tower(self, tower) -> bool:
        refund = tower.sell()
        self.state.add_gold(refund, reason=f"sell:{tower.family}")
        self.scene.remove_tower(tower)
        return True

    # --- heroes & skills --------------------------------------------

    def set_hero_rally(self, hero, x: float, y: float) -> None:
        if hero.alive:
            hero.set_rally(x, y)

    def cast_skill(self, skill, target=None, hero=None) -> bool:
        ctx = SkillContext(scene=self.scene, state=self.state, hero=hero)
        return skill.activate(ctx, target)
