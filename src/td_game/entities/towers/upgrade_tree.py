"""Tower upgrade trees.

Shape:
    Tier 1 (base build) -> Tier 2 -> Tier 3 -> then a branching step to one
    of four Tier-4 specializations.

Represented as a linear list for the shared tiers plus a dict of
specializations keyed by a short id. The game never cares about the
shape beyond "given the current node, what are the next options?"
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class TowerStatsRow:
    """Data-only stat block for one tier / specialization of a tower."""
    display_name: str
    cost: int                # gold to build, or cost to upgrade TO this row
    damage: float
    range: float
    attack_interval: float   # seconds
    projectile: str = ""     # sprite key in 'projectiles' category (if ranged)
    sprite: str = ""         # tower sprite
    description: str = ""    # one-liner flavor; shown in tooltips
    # Optional bonuses per row (structured as key->value so data can grow
    # without widening this dataclass every time).
    extras: dict = field(default_factory=dict)


@dataclass
class UpgradeTree:
    family: str                          # 'archer' | 'barracks' | 'mage' | 'artillery'
    tiers: list[TowerStatsRow]           # tiers[0] is the base build; tiers[-1] is the last shared tier
    specializations: dict[str, TowerStatsRow]  # 4 entries by spec id

    def next_upgrades(self, current_tier_index: int, current_spec: str | None) -> list[tuple[str, TowerStatsRow]]:
        """Return choices from the current node.

        Returns a list of (node_id, row). node_id is either the index of
        the next shared tier as a string, or a specialization id.
        """
        if current_spec is not None:
            return []  # spec is terminal
        next_tier = current_tier_index + 1
        if next_tier < len(self.tiers):
            return [(str(next_tier), self.tiers[next_tier])]
        # Reached top of shared tree — offer all specializations.
        return [(spec_id, row) for spec_id, row in self.specializations.items()]
