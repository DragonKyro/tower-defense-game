"""Audio manager — SFX + looping music.

Uses arcade's pyglet-based sound API. First launch generates all WAV
files into `generated_audio/` via `graphics.procedural.audio_gen`; later
launches just load from cache.

Prefer shipping real audio by dropping a file into `assets/audio/<name>.wav`
(or .ogg/.mp3) — `resolve_audio_path` falls back to the generated cache.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import arcade

from td_game.graphics.procedural.audio_gen import generate_to

from .constants import AUDIO_DIR, GENERATED_AUDIO_DIR


class AudioManager:
    """Loads + plays audio. Safe to call even if audio hardware is missing —
    exceptions from the underlying stack are swallowed so the game never
    crashes because of audio.
    """
    def __init__(self, music_volume: float = 0.35, sfx_volume: float = 0.55) -> None:
        self.music_volume = music_volume
        self.sfx_volume = sfx_volume
        self._sounds: dict[str, arcade.Sound] = {}
        self._music_player = None
        self._ready = False
        self._warmed = False

    def warmup(self) -> None:
        """Generate any missing WAV files. Call once at app startup."""
        if self._warmed:
            return
        self._warmed = True
        try:
            generate_to(GENERATED_AUDIO_DIR)
            self._ready = True
        except Exception as exc:  # pragma: no cover — audio init failures shouldn't crash
            print(f"[audio] warmup failed: {exc}")
            self._ready = False

    # --- path resolution --------------------------------------------

    def _resolve(self, name: str) -> Optional[Path]:
        # Prefer hand-authored assets under assets/audio, then the cache.
        for ext in (".wav", ".ogg", ".mp3"):
            p = AUDIO_DIR / f"{name}{ext}"
            if p.is_file():
                return p
        cached = GENERATED_AUDIO_DIR / f"{name}.wav"
        if cached.is_file():
            return cached
        return None

    def _load(self, name: str) -> Optional[arcade.Sound]:
        if not self._ready:
            return None
        snd = self._sounds.get(name)
        if snd is not None:
            return snd
        path = self._resolve(name)
        if path is None:
            return None
        try:
            snd = arcade.Sound(str(path))
            self._sounds[name] = snd
            return snd
        except Exception as exc:  # pragma: no cover
            print(f"[audio] load failed for {name}: {exc}")
            return None

    # --- playback ---------------------------------------------------

    def play_sfx(self, name: str, volume_mult: float = 1.0) -> None:
        snd = self._load(name)
        if snd is None:
            return
        try:
            snd.play(volume=self.sfx_volume * volume_mult)
        except Exception:  # pragma: no cover
            pass

    def play_music(self, name: str) -> None:
        self.stop_music()
        snd = self._load(name)
        if snd is None:
            return
        try:
            self._music_player = snd.play(volume=self.music_volume, loop=True)
        except Exception:  # pragma: no cover
            self._music_player = None

    def stop_music(self) -> None:
        if self._music_player is None:
            return
        try:
            self._music_player.pause()
            self._music_player = None
        except Exception:  # pragma: no cover
            self._music_player = None

    def set_music_volume(self, vol: float) -> None:
        self.music_volume = max(0.0, min(1.0, vol))
        if self._music_player is not None:
            try:
                self._music_player.volume = self.music_volume
            except Exception:  # pragma: no cover
                pass


# Module-level singleton — cheap enough, avoids plumbing through every
# view. Scenes import `audio` and call methods directly.
audio = AudioManager()
