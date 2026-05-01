"""Realmguard — launch the game.

Works with or without `pip install -e .` — we put `src/` on sys.path
before importing the package so a plain `python realmguard.py` just runs.
"""
import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from td_game.app import run


if __name__ == "__main__":
    run()
