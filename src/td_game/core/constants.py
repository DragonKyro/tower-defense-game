"""Global constants: window, grid, colors, layers, damage types.

Tuning numeric balance lives in `td_game.data.*`. Values here define the
shape of the world, not the feel of the game.
"""
from __future__ import annotations

from enum import Enum, IntEnum, auto
from pathlib import Path

# --- Window --------------------------------------------------------------

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Realmguard"
TARGET_FPS = 60

# --- Grid ----------------------------------------------------------------

TILE_SIZE = 64
GRID_COLS = SCREEN_WIDTH // TILE_SIZE          # 20
GRID_ROWS = (SCREEN_HEIGHT - 80) // TILE_SIZE  # 10 gameplay rows, 80px HUD strip
HUD_HEIGHT = SCREEN_HEIGHT - GRID_ROWS * TILE_SIZE

# --- Paths (filesystem) --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]
ASSETS_DIR = PROJECT_ROOT / "assets"
SPRITES_DIR = ASSETS_DIR / "sprites"
AUDIO_DIR = ASSETS_DIR / "audio"
FONTS_DIR = ASSETS_DIR / "fonts"
GENERATED_SPRITES_DIR = PROJECT_ROOT / "generated_sprites"

# --- Z-order layers ------------------------------------------------------

class Layer(IntEnum):
    BACKGROUND = 0
    TILES = 10
    DECOR = 20
    BUILD_SPOTS = 30
    PATH_OVERLAY = 40
    TOWERS = 50
    UNITS = 60
    ENEMIES = 70
    PROJECTILES = 80
    FX = 90
    UI = 100


# --- Game economy defaults (overridable per-level) -----------------------

DEFAULT_STARTING_GOLD = 200
DEFAULT_STARTING_LIVES = 20
SELL_REFUND_RATIO = 0.7  # fraction of total invested

# --- Skill defaults ------------------------------------------------------

REINFORCEMENTS_DEFAULT_COOLDOWN = 15.0
METEOR_DEFAULT_COOLDOWN = 25.0
HERO_DEFAULT_RESPAWN = 25.0
MAX_HEROES_PER_LEVEL = 2

# --- Damage types --------------------------------------------------------

class DamageType(Enum):
    PHYSICAL = auto()  # mitigated by armor
    MAGIC = auto()     # mitigated by magic_resist
    TRUE = auto()      # ignores both
    FIRE = auto()      # physical + may apply Burn
    POISON = auto()    # magic + may apply Poison
    SIEGE = auto()     # aoe physical, ignores armor on structures


# --- Effect tags (used for enemy immunity lists in data tables) ---------

class EffectTag(Enum):
    POISON = auto()
    SLOW = auto()
    STUN = auto()
    BURN = auto()
    ARMOR_SHRED = auto()
    KNOCKBACK = auto()
