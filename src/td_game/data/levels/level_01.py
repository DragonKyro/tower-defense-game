"""Level 01 — the proof-of-concept level.

Single winding path across a grass map with 6 build spots. Demonstrates
all 4 tower families, 1 hero slot, reinforcements + meteor.
"""
from __future__ import annotations

from td_game.core.constants import GRID_COLS, GRID_ROWS, SCREEN_HEIGHT, TILE_SIZE

from ._schema import BuildSpot, LevelDef, Map, Path, SpawnOrder, Tile, TileType, Wave, Waypoint


def _tile_center(col: int, row: int) -> tuple[float, float]:
    """Convert grid (col, row — row 0 at top) to world pixels (y up)."""
    x = col * TILE_SIZE + TILE_SIZE / 2
    y = SCREEN_HEIGHT - (row * TILE_SIZE + TILE_SIZE / 2)
    return x, y


def _build_map() -> Map:
    # Start with all grass.
    grid = [[Tile(TileType.GRASS) for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
    # Carve a path: enters at (0, 3), snakes to exit at (GRID_COLS-1, 7).
    path_cells = [
        (0, 3), (1, 3), (2, 3), (3, 3), (4, 3),
        (4, 4), (4, 5), (4, 6),
        (5, 6), (6, 6), (7, 6),
        (7, 5), (7, 4), (7, 3), (7, 2),
        (8, 2), (9, 2), (10, 2), (11, 2), (12, 2),
        (12, 3), (12, 4), (12, 5),
        (13, 5), (14, 5), (15, 5), (16, 5),
        (16, 6), (16, 7),
        (17, 7), (18, 7), (19, 7),
    ]
    for col, row in path_cells:
        grid[row][col] = Tile(TileType.PATH)

    waypoints = [Waypoint(*_tile_center(c, r)) for c, r in path_cells]

    # Build spots nestled next to the path.
    spot_cells = [(2, 4), (4, 2), (6, 5), (9, 3), (11, 4), (14, 6), (17, 6)]
    build_spots = [BuildSpot(*_tile_center(c, r)) for c, r in spot_cells]

    main_path = Path(id="main", waypoints=waypoints)
    spawn_xy = _tile_center(*path_cells[0])
    exit_xy = _tile_center(*path_cells[-1])

    return Map(
        name="Meadowkeep",
        grid=grid,
        paths=[main_path],
        build_spots=build_spots,
        spawn_points={"main": spawn_xy},
        exit_points={"main": exit_xy},
    )


def _build_waves() -> tuple[Wave, ...]:
    return (
        Wave(
            name="Wave 1 — Scouts",
            spawns=(
                SpawnOrder("goblin", count=8, interval=0.8),
            ),
            reward_gold=30,
        ),
        Wave(
            name="Wave 2 — Warband",
            spawns=(
                SpawnOrder("goblin", count=6, interval=0.7),
                SpawnOrder("orc", count=4, interval=1.2, delay=3.0),
            ),
            reward_gold=40,
        ),
        Wave(
            name="Wave 3 — Fliers",
            spawns=(
                SpawnOrder("wraith", count=5, interval=1.4),
                SpawnOrder("orc", count=4, interval=1.0, delay=4.0),
            ),
            reward_gold=50,
        ),
        Wave(
            name="Wave 4 — Assault",
            spawns=(
                SpawnOrder("orc", count=8, interval=0.8),
                SpawnOrder("troll", count=2, interval=4.0, delay=5.0),
            ),
            reward_gold=70,
        ),
        Wave(
            name="Wave 5 — Dragon",
            spawns=(
                SpawnOrder("wraith", count=4, interval=1.0),
                SpawnOrder("orc", count=6, interval=0.9, delay=3.0),
                SpawnOrder("dragon", count=1, interval=1.0, delay=10.0),
            ),
            reward_gold=120,
        ),
    )


LEVEL_01 = LevelDef(
    id="level_01",
    display_name="Meadowkeep",
    description="A quiet meadow under threat from the eastern woods.",
    map=_build_map(),
    waves=_build_waves(),
    starting_gold=220,
    starting_lives=20,
    hero_slots=1,
    tags=frozenset({"tutorial"}),
)
