"""Persistent profile stub.

Seam for future unlocks, star counts per level, encore mode flags, etc.
Right now just reads/writes a JSON file so the rest of the game can
assume the seam exists.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .constants import PROJECT_ROOT


SAVE_PATH = PROJECT_ROOT / "save.json"


@dataclass
class Profile:
    stars_by_level: dict[str, int] = field(default_factory=dict)
    unlocked_levels: list[str] = field(default_factory=lambda: ["level_01"])
    settings: dict[str, float] = field(default_factory=lambda: {"music": 0.6, "sfx": 0.8})


def load() -> Profile:
    if not SAVE_PATH.is_file():
        return Profile()
    try:
        raw = json.loads(SAVE_PATH.read_text())
        return Profile(
            stars_by_level=raw.get("stars_by_level", {}),
            unlocked_levels=raw.get("unlocked_levels", ["level_01"]),
            settings=raw.get("settings", {"music": 0.6, "sfx": 0.8}),
        )
    except (json.JSONDecodeError, OSError):
        return Profile()


def save(profile: Profile) -> None:
    SAVE_PATH.write_text(json.dumps(asdict(profile), indent=2))
