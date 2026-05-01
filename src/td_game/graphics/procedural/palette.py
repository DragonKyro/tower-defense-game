"""Medieval fantasy palette used by all procedural generators.

Centralized so color tweaks (or a seasonal reskin) are one-file changes.
Values are RGBA tuples.
"""
from __future__ import annotations

# Terrain
GRASS = (92, 148, 78, 255)
GRASS_DARK = (64, 112, 58, 255)
PATH = (158, 124, 82, 255)
PATH_DARK = (118, 92, 62, 255)
WATER = (72, 128, 180, 255)
CLIFF = (112, 104, 96, 255)
BUILD_SPOT = (222, 198, 128, 255)
BUILD_SPOT_RING = (90, 70, 30, 255)

# Generic
OUTLINE = (24, 20, 16, 255)
SHADOW = (0, 0, 0, 90)
TRANSPARENT = (0, 0, 0, 0)

# Factions
KNIGHT_STEEL = (190, 196, 208, 255)
KNIGHT_BLUE = (58, 92, 172, 255)
KNIGHT_GOLD = (226, 188, 82, 255)

ARCHER_GREEN = (72, 132, 76, 255)
ARCHER_LEATHER = (128, 86, 50, 255)

MAGE_PURPLE = (116, 78, 172, 255)
MAGE_ROBE = (78, 52, 118, 255)

ARTILLERY_BRONZE = (156, 96, 48, 255)
ARTILLERY_IRON = (72, 72, 80, 255)

# Enemies
ORC_SKIN = (104, 148, 84, 255)
ORC_DARK = (66, 98, 58, 255)

GOBLIN_SKIN = (148, 164, 96, 255)
TROLL_SKIN = (140, 118, 88, 255)
WRAITH = (72, 60, 96, 255)
DRAGON = (176, 60, 60, 255)

# Projectiles
ARROW = (208, 184, 124, 255)
CANNONBALL = (48, 48, 56, 255)
MAGIC_BOLT = (196, 132, 220, 255)
METEOR_CORE = (240, 112, 48, 255)
METEOR_RING = (248, 204, 96, 255)

# Effects
POISON = (112, 196, 92, 200)
BURN = (236, 128, 40, 220)
STUN = (240, 228, 96, 220)
SLOW = (140, 200, 232, 200)

# Health bar
HP_GREEN = (92, 196, 92, 255)
HP_RED = (212, 72, 72, 255)
HP_BG = (30, 30, 30, 220)
