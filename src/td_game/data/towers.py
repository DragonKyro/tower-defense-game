"""Tower stat tables + upgrade trees.

Editing numbers here tunes the game. Adding a 5th specialization =
adding an entry to a `specializations` dict below. No class changes.
"""
from __future__ import annotations

from td_game.entities.towers.upgrade_tree import TowerStatsRow, UpgradeTree


# ---------------------------------------------------------------- Archer

ARCHER_TREE = UpgradeTree(
    family="archer",
    tiers=[
        TowerStatsRow("Archer Tower I", cost=75, damage=10, range=180, attack_interval=1.0,
                      projectile="arrow_0", sprite="archer_1"),
        TowerStatsRow("Archer Tower II", cost=90, damage=16, range=195, attack_interval=0.9,
                      projectile="arrow_0", sprite="archer_2"),
        TowerStatsRow("Archer Tower III", cost=130, damage=26, range=210, attack_interval=0.8,
                      projectile="arrow_0", sprite="archer_3"),
    ],
    specializations={
        "sharpshooter": TowerStatsRow("Sharpshooter", cost=400, damage=70, range=260,
                                      attack_interval=0.7, projectile="arrow_0", sprite="archer_4",
                                      extras={"pierce_armor": 15.0}),
        "rapidfire": TowerStatsRow("Rapid-Fire", cost=380, damage=22, range=200,
                                   attack_interval=0.25, projectile="arrow_0", sprite="archer_4"),
        "ranger": TowerStatsRow("Ranger's Hideout", cost=420, damage=30, range=220,
                                attack_interval=0.6, projectile="arrow_0", sprite="archer_4",
                                extras={"multishot": 2}),
        "crossbow": TowerStatsRow("Crossbow Fort", cost=450, damage=45, range=240,
                                  attack_interval=0.9, projectile="arrow_0", sprite="archer_4",
                                  extras={"aoe_radius": 30}),
    },
)


# -------------------------------------------------------------- Barracks

BARRACKS_TREE = UpgradeTree(
    family="barracks",
    tiers=[
        TowerStatsRow("Barracks I", cost=70, damage=4, range=120, attack_interval=1.2,
                      sprite="barracks_1", extras={"unit_hp": 40, "unit_count": 3}),
        TowerStatsRow("Barracks II", cost=90, damage=6, range=130, attack_interval=1.1,
                      sprite="barracks_2", extras={"unit_hp": 60, "unit_count": 3}),
        TowerStatsRow("Barracks III", cost=130, damage=9, range=140, attack_interval=1.0,
                      sprite="barracks_3", extras={"unit_hp": 90, "unit_count": 3}),
    ],
    specializations={
        "paladins": TowerStatsRow("Paladins", cost=420, damage=14, range=150, attack_interval=1.0,
                                  sprite="barracks_4", extras={"unit_hp": 180, "unit_count": 3, "heal": 4.0}),
        "knights": TowerStatsRow("Knights", cost=400, damage=20, range=150, attack_interval=1.0,
                                 sprite="barracks_4", extras={"unit_hp": 140, "unit_count": 3, "armor": 6}),
        "assassins": TowerStatsRow("Assassins", cost=380, damage=12, range=160, attack_interval=0.6,
                                   sprite="barracks_4", extras={"unit_hp": 80, "unit_count": 3, "crit": 0.25}),
        "pikemen": TowerStatsRow("Pikemen", cost=400, damage=18, range=140, attack_interval=1.0,
                                 sprite="barracks_4", extras={"unit_hp": 110, "unit_count": 4, "armor_shred": 3}),
    },
)


# ------------------------------------------------------------------ Mage

MAGE_TREE = UpgradeTree(
    family="mage",
    tiers=[
        TowerStatsRow("Mage Tower I", cost=95, damage=18, range=170, attack_interval=1.4,
                      projectile="bolt_0", sprite="mage_1"),
        TowerStatsRow("Mage Tower II", cost=120, damage=28, range=180, attack_interval=1.3,
                      projectile="bolt_0", sprite="mage_2"),
        TowerStatsRow("Mage Tower III", cost=160, damage=42, range=190, attack_interval=1.2,
                      projectile="bolt_0", sprite="mage_3"),
    ],
    specializations={
        "arcane": TowerStatsRow("Arcane Wizard", cost=500, damage=110, range=230, attack_interval=1.1,
                                projectile="bolt_0", sprite="mage_4", extras={"true_damage": True}),
        "necromancer": TowerStatsRow("Necromancer", cost=480, damage=60, range=210, attack_interval=1.1,
                                     projectile="bolt_0", sprite="mage_4", extras={"summon_skeleton": True}),
        "pyromancer": TowerStatsRow("Pyromancer", cost=460, damage=55, range=200, attack_interval=1.0,
                                    projectile="bolt_0", sprite="mage_4", extras={"burn_dps": 10, "burn_time": 3}),
        "druid": TowerStatsRow("Druid", cost=440, damage=45, range=200, attack_interval=1.1,
                               projectile="bolt_0", sprite="mage_4", extras={"poison_dps": 8, "poison_time": 4}),
    },
)


# ------------------------------------------------------------- Artillery

ARTILLERY_TREE = UpgradeTree(
    family="artillery",
    tiers=[
        TowerStatsRow("Bombard I", cost=110, damage=28, range=160, attack_interval=1.8,
                      projectile="cannonball_0", sprite="artillery_1",
                      extras={"aoe_radius": 45, "ground_only": True}),
        TowerStatsRow("Bombard II", cost=140, damage=46, range=170, attack_interval=1.7,
                      projectile="cannonball_0", sprite="artillery_2",
                      extras={"aoe_radius": 50, "ground_only": True}),
        TowerStatsRow("Bombard III", cost=180, damage=72, range=180, attack_interval=1.6,
                      projectile="cannonball_0", sprite="artillery_3",
                      extras={"aoe_radius": 55, "ground_only": True}),
    ],
    specializations={
        "mortar": TowerStatsRow("Big Bertha", cost=550, damage=160, range=230, attack_interval=2.0,
                                projectile="cannonball_0", sprite="artillery_4",
                                extras={"aoe_radius": 75, "ground_only": True}),
        "tesla": TowerStatsRow("Tesla", cost=520, damage=50, range=180, attack_interval=0.7,
                               projectile="bolt_0", sprite="artillery_4",
                               extras={"chain_jumps": 3, "ground_only": False}),
        "flamethrower": TowerStatsRow("Flamethrower", cost=500, damage=20, range=140, attack_interval=0.2,
                                      projectile="", sprite="artillery_4",
                                      extras={"cone_damage": True, "burn_dps": 12, "burn_time": 2}),
        "rocket": TowerStatsRow("Rocket Battery", cost=540, damage=90, range=220, attack_interval=1.4,
                                projectile="cannonball_0", sprite="artillery_4",
                                extras={"aoe_radius": 50, "rockets": 3, "ground_only": False}),
    },
)


TOWER_TREES: dict[str, UpgradeTree] = {
    "archer": ARCHER_TREE,
    "barracks": BARRACKS_TREE,
    "mage": MAGE_TREE,
    "artillery": ARTILLERY_TREE,
}
