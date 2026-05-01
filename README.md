# Realmguard

A modular, Kingdom Rush–inspired tower defense built on **Python Arcade**. The framework is laid down first so new levels can be "pumped out" on top of it; art and audio are procedurally generated placeholders so the project runs end-to-end on a fresh clone.

## Features (framework)

- **4 tower families** (archer, barracks, mage, artillery), each with **3 shared tiers + 4 branching specializations** (tier-4 leaves) — defined as pure data in [src/td_game/data/towers.py](src/td_game/data/towers.py).
- **Up to 2 heroes** per level with unique skills (two samples included: Knight, Ranger).
- **Global skills**: Reinforcements and Meteor — both on per-level cooldowns.
- **Status effects**: poison, burn, slow, stun, armor shred — with per-enemy immunity lists.
- **Data-driven enemies and waves** — add rows to tables, not new classes.
- **Event bus** for decoupling achievements / UI / stats from gameplay.
- **Procedural sprite fallback**: drops real art into `assets/sprites/<category>/<name>.png` to override placeholders, no code changes required.
- **Scene graph**: main menu → level select → game → pause / game-over.

## Setup

```bash
python -m venv .venv
source .venv/Scripts/activate        # Windows bash; use .venv/bin/activate elsewhere
pip install -e .
python realmguard.py
```

Or, after `pip install -e .`, use the installed console script:

```bash
realmguard
```

Or without editable install:

```bash
pip install -r requirements.txt
python realmguard.py
```

Requires Python 3.11+.

## Project layout

```
src/td_game/
  core/         # constants, events, resources (asset loader), game_state, damage
  graphics/     # animation, anim_controller, procedural sprite generators
  entities/
    towers/     # base_tower, targeting, upgrade_tree, 4 tower families, factory
    enemies/    # base_enemy, path_follower, enemy factory
    units/      # base_unit, soldier (barracks), reinforcement
    heroes/     # base_hero + sample heroes (knight, ranger)
    projectiles/
  skills/       # base_skill, reinforcements, meteor, hero skills
  effects/      # poison, burn, slow, stun, armor_shred
  world/        # tile, path, map, wave, level
  systems/      # wave_manager, spawner, combat, economy, command, collision
  scenes/       # main_menu, level_select, game_scene, pause_menu, game_over
  ui/           # hud, tower_menu, button, health_bar
  data/         # towers.py, enemies.py, heroes.py, effects.py
    levels/     # Python modules, one per level, registered in __init__.py
assets/         # Drop-in art overrides (preferred when present)
generated_sprites/   # Procedural sprite cache (gitignored)
```

See [CLAUDE.md](CLAUDE.md) for an architecture contract geared at contributors and Claude-assisted sessions.

## Controls

- **Left-click** a build spot to open the tower build menu; click a family to build it.
- **Left-click** an existing tower to open its upgrade / sell menu.
- **Right-click** on the ground to rally your hero to that point.
- **Bottom HUD** shows gold, lives, current wave, and skill buttons (Reinforcements, Meteor).
- Skills that need a target (Reinforcements point, Meteor area) open a "click where to target" mode on button press.

## How to add a new level

The whole process lives under `src/td_game/data/levels/`.

1. Copy `level_01.py` to `level_02.py`.
2. Edit:
   - `id`, `display_name`, `description`
   - carve a new path via grid cells and call `_tile_center` for each
   - place `BuildSpot`s next to it
   - define waves with `SpawnOrder` entries (enemy id, count, interval, optional delay & path_id)
3. In `src/td_game/data/levels/__init__.py`, import your `LEVEL_02` and add it to the `LEVELS` dict.
4. Run — it'll show up in the Level Select view.

To add a **new enemy**, add a row to [src/td_game/data/enemies.py](src/td_game/data/enemies.py) (id, hp, speed, armor, immunities, sprite name). A matching `<sprite>.png` under `assets/sprites/enemies/` will be used if present; otherwise the procedural generator will handle it.

To add a **new tower specialization**, add an entry to the appropriate `UpgradeTree.specializations` dict in [src/td_game/data/towers.py](src/td_game/data/towers.py). No class changes needed for stat-only specs; for behavior differences, extend `perform_attack` on the tower subclass.

## Roadmap

Framework seams already in place, implementations stubbed or partial:
- Save / unlock persistence ([save_manager.py](src/td_game/core/save_manager.py))
- Heroic / Iron challenge modes (level tags)
- Boss mechanics (BaseEnemy subclass hook)
- Dual-faction towers (Alliance style) — fits the existing factory
- Encore mode, gem economy (Vengeance-style), random prizes

## License

MIT (see pyproject.toml).
