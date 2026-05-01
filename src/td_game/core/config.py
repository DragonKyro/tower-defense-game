"""User-visible settings (volume, keybinds).

Thin wrapper over the profile's `settings` dict. Kept separate from
profile so gameplay/unlocks code doesn't reach into audio/input concerns.
"""
from __future__ import annotations

from . import save_manager

_profile = save_manager.load()


def get(key: str, default: float = 0.0) -> float:
    return _profile.settings.get(key, default)


def set_(key: str, value: float) -> None:
    _profile.settings[key] = value
    save_manager.save(_profile)
