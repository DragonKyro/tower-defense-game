"""Level 01 — "Meadowkeep".

Single winding path across a grass meadow with 6 build spots, a castle
gate at the exit, and scattered decor (trees, rocks, bushes, flowers,
mushrooms, banners) for visual life.
"""
from __future__ import annotations

import random

from td_game.core.constants import GRID_COLS, GRID_ROWS, SCREEN_HEIGHT, TILE_SIZE

from ._schema import BuildSpot, DecorItem, LevelDef, Map, Path, SpawnOrder, Tile, TileType, Wave, Waypoint


def _tile_center(col: int, row: int) -> tuple[float, float]:
    """Grid (col, row — row 0 at top) to world pixels (y up)."""
    x = col * TILE_SIZE + TILE_SIZE / 2
    y = SCREEN_HEIGHT - (row * TILE_SIZE + TILE_SIZE / 2)
    return x, y


_PATH_CELLS: list[tuple[int, int]] = [
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

_SPOT_CELLS: list[tuple[int, int]] = [(2, 4), (4, 2), (6, 5), (9, 3), (11, 4), (14, 6), (17, 6)]


def _build_map() -> Map:
    grid = [[Tile(TileType.GRASS) for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
    path_set = set(_PATH_CELLS)
    for col, row in _PATH_CELLS:
        grid[row][col] = Tile(TileType.PATH)

    waypoints = [Waypoint(*_tile_center(c, r)) for c, r in _PATH_CELLS]
    build_spots = [BuildSpot(*_tile_center(c, r)) for c, r in _SPOT_CELLS]
    build_spot_set = set(_SPOT_CELLS)

    decor = _build_decor(path_set, build_spot_set)

    main_path = Path(id="main", waypoints=waypoints)
    spawn_xy = _tile_center(*_PATH_CELLS[0])
    exit_xy = _tile_center(*_PATH_CELLS[-1])

    return Map(
        name="Meadowkeep",
        grid=grid,
        paths=[main_path],
        build_spots=build_spots,
        spawn_points={"main": spawn_xy},
        exit_points={"main": exit_xy},
        decor=decor,
    )


def _build_decor(path_set: set, spot_set: set) -> list[DecorItem]:
    """Hand-placed anchors + randomized flowers / mushrooms on grass."""
    rng = random.Random(1337)
    items: list[DecorItem] = []

    # Castle at the far right (exit of the path).
    castle_x, castle_y = _tile_center(19, 7)
    items.append(DecorItem(castle_x + 20, castle_y + 28, "castle_keep"))

    # Banners flanking the spawn on the left.
    sx, sy = _tile_center(0, 3)
    items.append(DecorItem(sx + 10, sy + 48, "banner_red"))
    items.append(DecorItem(sx + 10, sy - 44, "banner_red"))

    # Large / medium rocks at the corners and edges.
    items.append(DecorItem(*_tile_center(2, 0), "rock_large"))
    items.append(DecorItem(*_tile_center(13, 0), "rock_large"))
    items.append(DecorItem(*_tile_center(6, 9), "rock_med"))
    items.append(DecorItem(*_tile_center(15, 8), "rock_med"))
    items.append(DecorItem(*_tile_center(0, 8), "rock_med"))

    # Trees along the top and bottom borders.
    trees = [
        (1, 0, "oak"), (3, 0, "pine"), (5, 0, "oak"), (9, 0, "pine"),
        (11, 0, "oak"), (15, 0, "pine"), (17, 1, "oak"),
        (0, 9, "oak"), (2, 9, "pine"), (4, 9, "oak"),
        (10, 9, "pine"), (12, 9, "oak"), (14, 9, "pine"),
        (18, 8, "oak"), (8, 8, "pine"), (3, 8, "oak"),
    ]
    for c, r, variant in trees:
        x, y = _tile_center(c, r)
        items.append(DecorItem(x + rng.randint(-6, 6), y + rng.randint(-6, 6), f"tree_{variant}"))

    # Bushes near path edges for softness.
    for c, r in [(5, 4), (3, 5), (6, 2), (10, 4), (13, 3), (15, 6), (8, 7)]:
        if (c, r) in path_set or (c, r) in spot_set:
            continue
        x, y = _tile_center(c, r)
        items.append(DecorItem(x + rng.randint(-8, 8), y + rng.randint(-8, 8),
                               "bush_berry" if rng.random() < 0.4 else "bush_0"))

    # Small stone clusters for texture.
    for c, r in [(1, 5), (6, 4), (11, 6), (14, 4), (18, 4), (2, 7), (5, 7)]:
        if (c, r) in path_set or (c, r) in spot_set:
            continue
        x, y = _tile_center(c, r)
        items.append(DecorItem(x + rng.randint(-10, 10), y + rng.randint(-10, 10), "stones_0"))

    # Flowers scattered on grass.
    flower_colors = ("pink", "yellow", "blue")
    for _ in range(40):
        c = rng.randint(0, GRID_COLS - 1)
        r = rng.randint(0, GRID_ROWS - 1)
        if (c, r) in path_set or (c, r) in spot_set:
            continue
        x, y = _tile_center(c, r)
        items.append(DecorItem(
            x + rng.randint(-20, 20),
            y + rng.randint(-20, 20),
            f"flower_{rng.choice(flower_colors)}",
        ))
    # Mushrooms.
    for _ in range(12):
        c = rng.randint(0, GRID_COLS - 1)
        r = rng.randint(0, GRID_ROWS - 1)
        if (c, r) in path_set or (c, r) in spot_set:
            continue
        x, y = _tile_center(c, r)
        items.append(DecorItem(
            x + rng.randint(-16, 16),
            y + rng.randint(-16, 16),
            "mushroom_0",
        ))

    return items


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
            name="Wave 3 — Shadows",
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
            name="Wave 5 — Red Wyrm",
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
    description="A quiet meadow under threat from the eastern woods. Defend the castle gate.",
    map=_build_map(),
    waves=_build_waves(),
    starting_gold=220,
    starting_lives=20,
    hero_slots=1,
    tags=frozenset({"tutorial"}),
)
