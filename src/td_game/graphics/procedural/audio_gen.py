"""Procedural WAV generator for music + SFX.

Renders tones via sine/square/noise waveforms into WAV files that Arcade
can load. Kept here (not `core/audio.py`) so it stays alongside the other
procedural generators that run on first launch.

Output: 44.1kHz, 16-bit, mono.
"""
from __future__ import annotations

import math
import random
import struct
import wave
from pathlib import Path
from typing import Iterable, Sequence

SAMPLE_RATE = 44100


# --- low-level wave synthesis -------------------------------------

def _write_wav(path: Path, samples: Sequence[float]) -> None:
    """Clip floats in [-1, 1] and write as a 16-bit mono WAV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SAMPLE_RATE)
        frames = bytearray()
        for v in samples:
            v = max(-1.0, min(1.0, v))
            frames += struct.pack("<h", int(v * 32767))
        f.writeframes(bytes(frames))


def _envelope(n: int, attack: float, release: float) -> list[float]:
    """Simple linear AR envelope. attack/release are fractions of n."""
    a = max(1, int(n * attack))
    r = max(1, int(n * release))
    out = []
    for i in range(n):
        if i < a:
            out.append(i / a)
        elif i > n - r:
            out.append(max(0.0, (n - i) / r))
        else:
            out.append(1.0)
    return out


def _sine(freq: float, n: int) -> list[float]:
    return [math.sin(2 * math.pi * freq * i / SAMPLE_RATE) for i in range(n)]


def _square(freq: float, n: int) -> list[float]:
    return [1.0 if math.sin(2 * math.pi * freq * i / SAMPLE_RATE) >= 0 else -1.0
            for i in range(n)]


def _noise(n: int) -> list[float]:
    rng = random.Random(1337)
    return [rng.uniform(-1.0, 1.0) for _ in range(n)]


def _tone(freq: float, duration: float, volume: float = 0.3,
          waveform: str = "sine",
          attack: float = 0.05, release: float = 0.2) -> list[float]:
    n = int(SAMPLE_RATE * duration)
    if waveform == "square":
        raw = _square(freq, n)
    elif waveform == "noise":
        raw = _noise(n)
    else:
        raw = _sine(freq, n)
    env = _envelope(n, attack, release)
    return [raw[i] * env[i] * volume for i in range(n)]


def _silence(duration: float) -> list[float]:
    return [0.0] * int(SAMPLE_RATE * duration)


def _mix(*tracks: Sequence[float]) -> list[float]:
    n = max(len(t) for t in tracks)
    out = [0.0] * n
    for t in tracks:
        for i, v in enumerate(t):
            out[i] += v
    # Gentle compression to prevent clipping.
    return [max(-1.0, min(1.0, v * 0.9)) for v in out]


def _concat(*tracks: Sequence[float]) -> list[float]:
    out: list[float] = []
    for t in tracks:
        out.extend(t)
    return out


# --- specific SFX -------------------------------------------------

def _sfx_hit() -> list[float]:
    # Short dull thud: a burst of filtered noise + low sine tail.
    n = int(SAMPLE_RATE * 0.12)
    env = _envelope(n, 0.02, 0.7)
    noise = _noise(n)
    low = _sine(120, n)
    return [(noise[i] * 0.6 + low[i] * 0.4) * env[i] * 0.35 for i in range(n)]


def _sfx_shoot() -> list[float]:
    # Quick high-to-mid swoop.
    n = int(SAMPLE_RATE * 0.12)
    env = _envelope(n, 0.02, 0.6)
    out = []
    for i in range(n):
        t = i / n
        freq = 1200 - 700 * t
        out.append(math.sin(2 * math.pi * freq * i / SAMPLE_RATE) * env[i] * 0.25)
    return out


def _sfx_cast() -> list[float]:
    # Rising arpeggio: C, E, G — quick.
    notes = (523.25, 659.25, 783.99)
    segments = []
    for f in notes:
        segments.append(_tone(f, 0.08, 0.3, "sine", 0.05, 0.3))
    return _concat(*segments)


def _sfx_explosion() -> list[float]:
    # Big boom: noise burst + low sine pulse.
    n = int(SAMPLE_RATE * 0.5)
    env = _envelope(n, 0.01, 0.85)
    noise = _noise(n)
    low = _sine(60, n)
    return [(noise[i] * 0.55 + low[i] * 0.45) * env[i] * 0.5 for i in range(n)]


def _sfx_wave_start() -> list[float]:
    # Horn call: low brass-like pulse.
    return _tone(146.83, 0.7, 0.35, "square", 0.08, 0.6)  # D3


def _sfx_build() -> list[float]:
    # Chime: double ding.
    return _concat(
        _tone(1046.5, 0.1, 0.25, "sine", 0.02, 0.4),  # C6
        _tone(1318.5, 0.18, 0.25, "sine", 0.02, 0.6),  # E6
    )


def _sfx_ui_click() -> list[float]:
    return _tone(880, 0.05, 0.2, "sine", 0.01, 0.5)


def _sfx_gold() -> list[float]:
    return _concat(
        _tone(1174.66, 0.06, 0.22, "sine", 0.01, 0.5),  # D6
        _tone(1567.98, 0.10, 0.22, "sine", 0.01, 0.6),  # G6
    )


def _sfx_hero_death() -> list[float]:
    # Descending minor.
    notes = (440, 392, 349.23, 293.66)  # A, G, F, D
    segments = [_tone(n, 0.18, 0.3, "sine", 0.04, 0.5) for n in notes]
    return _concat(*segments)


def _sfx_victory() -> list[float]:
    # Triumphant rising triad.
    notes = (523.25, 659.25, 783.99, 1046.5)
    segments = [_tone(n, 0.2, 0.32, "sine", 0.02, 0.5) for n in notes]
    return _concat(*segments)


# --- music: heroic march loop -------------------------------------

def _music_meadow() -> list[float]:
    """~16s looping heroic march in D minor at 120 BPM.

    Intent: Kingdom Rush archetype — brass-ish lead over an i–VI–III–VII
    chord progression, with a driving kick+snare backbeat and a warm
    triad pad. Not copying any specific KR track; just hitting the genre
    conventions that make it feel like a heroic tower-defense game:
    steady march tempo, a leap on the downbeat, dominant resolution
    back to the tonic at loop point.

    Voices (mixed together):
      - Lead: two detuned squares with light vibrato (≈ French horn).
      - Bass: sawtooth on the chord root, 2 bars per chord.
      - Pad: triad sines an octave above the bass for warmth.
      - Kick: pitch-bend sine on beats 1 & 3.
      - Snare: filtered noise + 200Hz body tone on beats 2 & 4.
      - Hi-hat: very quiet noise tick on every beat for forward motion.

    Loop-safe: the last melody note leads back to the tonic D, and every
    voice ends in its release tail so there's no click at wraparound.
    """
    bpm = 120
    beat = 60.0 / bpm           # 0.5s
    beats_per_bar = 4
    bars = 8
    total_beats = bars * beats_per_bar  # 32
    total_n = int(SAMPLE_RATE * beat * total_beats)

    # Chord progression: Dm – Bb – F – C (i – VI – III – VII), 2 bars each.
    progression = [
        (146.83, (146.83, 174.61, 220.00)),   # Dm: D3 F3 A3
        (116.54, (116.54, 146.83, 174.61)),   # Bb: Bb2 D3 F3
        (174.61, (174.61, 220.00, 261.63)),   # F:  F3 A3 C4
        (130.81, (130.81, 164.81, 196.00)),   # C:  C3 E3 G3
    ]

    # One melody note per beat (32 total), outlining each chord.
    D5, E5, F5, G5, A5, Bb5, C6, D6 = (
        587.33, 659.25, 698.46, 783.99, 880.00, 932.33, 1046.50, 1174.66,
    )
    melody_notes = [
        # Bar 1 (Dm): heroic opening — root then octave leap.
        D5, F5, A5, D6,
        # Bar 2 (Dm): descending resolution.
        C6, A5, F5, E5,
        # Bar 3 (Bb): restate phrase up.
        F5, D5, F5, A5,
        # Bar 4 (Bb): step down into the F chord.
        G5, F5, D5, F5,
        # Bar 5 (F): triumphant rise.
        A5, C6, A5, F5,
        # Bar 6 (F): step figure.
        G5, F5, E5, F5,
        # Bar 7 (C): lift.
        E5, G5, C6, Bb5,
        # Bar 8 (C): cadence down, leading tone D for loop back to Dm.
        A5, G5, F5, D5,
    ]

    # --- Lead (two detuned square waves ≈ brass) -----------------
    lead: list[float] = []
    for f in melody_notes:
        note_n = int(SAMPLE_RATE * beat * 0.92)
        rest_n = int(SAMPLE_RATE * beat) - note_n
        env = _envelope(note_n, 0.04, 0.35)
        for i in range(note_n):
            t = i / SAMPLE_RATE
            s1 = 1.0 if math.sin(2 * math.pi * f * t) >= 0 else -1.0
            s2 = 1.0 if math.sin(2 * math.pi * f * 1.004 * t) >= 0 else -1.0
            vib = 0.02 * math.sin(2 * math.pi * 5.5 * t)
            lead.append(((s1 + s2) * 0.5 + vib) * env[i] * 0.16)
        lead.extend([0.0] * rest_n)

    # --- Bass (sawtooth root, 2 bars per chord) ------------------
    bass: list[float] = []
    chord_n = int(SAMPLE_RATE * beat * beats_per_bar * 2)
    for root, _triad in progression:
        env = _envelope(chord_n, 0.02, 0.08)
        for i in range(chord_n):
            t = i / SAMPLE_RATE
            phase = (root * t) % 1.0
            saw = 2.0 * phase - 1.0
            bass.append(saw * env[i] * 0.14)

    # --- Pad (triad sines stacked an octave up) ------------------
    pad: list[float] = []
    for _root, triad in progression:
        env = _envelope(chord_n, 0.15, 0.25)
        for i in range(chord_n):
            t = i / SAMPLE_RATE
            v = sum(math.sin(2 * math.pi * f * 2 * t) for f in triad) / len(triad)
            trem = 0.9 + 0.1 * math.sin(2 * math.pi * 0.5 * t)
            pad.append(v * env[i] * 0.07 * trem)

    # --- Drums ---------------------------------------------------
    drums = [0.0] * total_n
    rng = random.Random(4242)
    # Kick on beats 1 & 3.
    kick_n = int(SAMPLE_RATE * 0.14)
    for bar in range(bars):
        for beat_in_bar in (0, 2):
            start = int(SAMPLE_RATE * beat * (bar * beats_per_bar + beat_in_bar))
            for i in range(kick_n):
                if start + i >= total_n:
                    break
                prog = i / kick_n
                freq = 140 - 95 * min(1.0, prog * 2.0)
                env = max(0.0, 1.0 - prog) ** 0.6
                drums[start + i] += math.sin(2 * math.pi * freq * i / SAMPLE_RATE) * env * 0.32
    # Snare on beats 2 & 4 (noise + 200Hz body).
    snare_n = int(SAMPLE_RATE * 0.08)
    for bar in range(bars):
        for beat_in_bar in (1, 3):
            start = int(SAMPLE_RATE * beat * (bar * beats_per_bar + beat_in_bar))
            for i in range(snare_n):
                if start + i >= total_n:
                    break
                prog = i / snare_n
                env = max(0.0, 1.0 - prog) ** 0.8
                noise = rng.uniform(-1.0, 1.0)
                body = math.sin(2 * math.pi * 200 * i / SAMPLE_RATE)
                drums[start + i] += (noise * 0.7 + body * 0.3) * env * 0.18
    # Hi-hat ticks on every beat — quiet, adds forward momentum.
    hat_n = int(SAMPLE_RATE * 0.03)
    for beat_idx in range(total_beats):
        start = int(SAMPLE_RATE * beat * beat_idx)
        for i in range(hat_n):
            if start + i >= total_n:
                break
            prog = i / hat_n
            env = max(0.0, 1.0 - prog) ** 1.2
            drums[start + i] += rng.uniform(-1.0, 1.0) * env * 0.045

    return _mix(lead, bass, pad, drums)


# --- public API ---------------------------------------------------

_GENERATORS: dict[str, callable] = {
    "music_meadow": _music_meadow,
    "sfx_hit": _sfx_hit,
    "sfx_shoot": _sfx_shoot,
    "sfx_cast": _sfx_cast,
    "sfx_explosion": _sfx_explosion,
    "sfx_wave_start": _sfx_wave_start,
    "sfx_build": _sfx_build,
    "sfx_ui_click": _sfx_ui_click,
    "sfx_gold": _sfx_gold,
    "sfx_hero_death": _sfx_hero_death,
    "sfx_victory": _sfx_victory,
}


def generate_to(cache_dir: Path) -> dict[str, Path]:
    """Render every known audio asset into `cache_dir`. Skip files already present."""
    out: dict[str, Path] = {}
    for name, fn in _GENERATORS.items():
        path = cache_dir / f"{name}.wav"
        if not path.is_file():
            _write_wav(path, fn())
        out[name] = path
    return out
