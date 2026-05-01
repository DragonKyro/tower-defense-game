# CLAUDE.md — Architecture contract for this project

This file is the quick-briefing for any Claude-assisted session working in this repo. Keep it in sync with the code. If you change architecture, update here.

## What this project is

**Realmguard** — a modular tower defense inspired by Kingdom Rush / Frontiers / Origins / Vengeance / Alliance, built on Python Arcade 3.x. Target platform: desktop (Windows/Mac/Linux). Python 3.11+. The user-facing title is "Realmguard"; the internal Python package is still `td_game` because renaming it would touch every import for no functional gain.

## Design pillars

1. **Data-driven balance.** Tower stats, enemy stats, and level definitions live in `src/td_game/data/*`. Editing those files should not require code changes elsewhere.
2. **Framework first, content second.** Every subsystem ships with at least one example and an obvious extension point (a dict to add to, a subclass to override).
3. **Decoupled via events.** Gameplay publishes to an EventBus; UI / economy / stats subscribe. Never import UI from gameplay code.
4. **Placeholder art, real art later.** Resources are loaded via `core/resources.py`, which checks `assets/sprites/<cat>/<name>.png` first and falls back to procedural generation into `generated_sprites/`. Do not load files directly from gameplay code.

## Per-frame data flow (GameView)

```
GameView.on_update(dt)
├── spawner.update_followers(enemies, dt)       # move enemies along paths
├── entities.on_update(dt)                       # towers, units, projectiles, enemies
├── combat.resolve_engagement(units, enemies)    # assign enemies to blocking units
├── tower.try_attack(enemies, scene)             # each tower either fires or skips
├── combat.tick_projectiles(projectiles, enemies)# impact resolution + AoE
├── cull dead entities
├── update fx lifetimes
└── wave_manager.update(dt, active_enemy_count) # start next wave when cleared
```

Events propagate lives/gold changes; `GameView` subscribes to `LEVEL_WON`/`LEVEL_LOST` for scene transitions.

## Key subsystems and where they live

| Concern | Location |
|---|---|
| Window + entry point | [src/td_game/app.py](src/td_game/app.py) |
| Constants (grid, colors, damage types) | [src/td_game/core/constants.py](src/td_game/core/constants.py) |
| Event bus | [src/td_game/core/events.py](src/td_game/core/events.py) |
| Per-run state | [src/td_game/core/game_state.py](src/td_game/core/game_state.py) |
| Damage math | [src/td_game/core/damage.py](src/td_game/core/damage.py) |
| Save / profile stub | [src/td_game/core/save_manager.py](src/td_game/core/save_manager.py) |
| Asset loader | [src/td_game/core/resources.py](src/td_game/core/resources.py) |
| Procedural sprite generators | [src/td_game/graphics/procedural/](src/td_game/graphics/procedural/) |
| Animation state machine | [src/td_game/graphics/anim_controller.py](src/td_game/graphics/anim_controller.py) |
| Base entity | [src/td_game/entities/entity.py](src/td_game/entities/entity.py) |
| Tower base + targeting + trees | [src/td_game/entities/towers/](src/td_game/entities/towers/) |
| Enemy base + path follower | [src/td_game/entities/enemies/](src/td_game/entities/enemies/) |
| Unit base + soldier + reinforcement | [src/td_game/entities/units/](src/td_game/entities/units/) |
| Hero base + samples | [src/td_game/entities/heroes/](src/td_game/entities/heroes/) |
| Projectiles | [src/td_game/entities/projectiles/](src/td_game/entities/projectiles/) |
| Skill base + global + hero | [src/td_game/skills/](src/td_game/skills/) |
| Status effects | [src/td_game/effects/](src/td_game/effects/) |
| Map / path / wave / level | [src/td_game/world/](src/td_game/world/) |
| Per-frame systems | [src/td_game/systems/](src/td_game/systems/) |
| Scenes (arcade.View) | [src/td_game/scenes/](src/td_game/scenes/) |
| UI components | [src/td_game/ui/](src/td_game/ui/) |
| Data tables + levels | [src/td_game/data/](src/td_game/data/) |

## Extension points

- **New enemy** → row in [data/enemies.py](src/td_game/data/enemies.py). Subclass `BaseEnemy` only if unique behavior (e.g., boss spawns adds on death).
- **New tower specialization** → entry in the relevant `specializations` dict in [data/towers.py](src/td_game/data/towers.py). Subclass the tower only if the `perform_attack` logic differs.
- **New tower family** → new file under [entities/towers/](src/td_game/entities/towers/) + new `UpgradeTree` in `data/towers.py` + register in [entities/towers/factory.py](src/td_game/entities/towers/factory.py).
- **New hero** → new file under [entities/heroes/samples/](src/td_game/entities/heroes/samples/) + hero skills under [skills/hero/](src/td_game/skills/hero/) + register in [data/heroes.py](src/td_game/data/heroes.py).
- **New status effect** → new file under [effects/](src/td_game/effects/), extend `BaseEffect`, add a matching tag in `core/constants.EffectTag` if enemies should be able to be immune.
- **New level** → new `level_XX.py` under [data/levels/](src/td_game/data/levels/), register in `data/levels/__init__.py`.
- **New scene** → new `arcade.View` subclass under [scenes/](src/td_game/scenes/); route into it from an existing scene (no scene registry yet — intentional).

## Conventions

- Core modules do not import from `scenes/` or `ui/`. UI imports downward.
- Sprite lookups go through `resources.load_texture(category, name)`. Do not call `arcade.load_texture` directly from gameplay code.
- Systems are created per-game (inside `GameView.__init__`), not as singletons.
- Data tables are frozen/tuple-like where possible to discourage in-place mutation at runtime.
- Concrete tower subclasses exist only when `perform_attack` differs (archer vs mage differ only in packet type and projectile; we still have subclasses because Barracks completely overrides attack behavior and keeping all four in one file would be confusing).

## Things intentionally left as seams (not yet implemented)

- **Save / unlock** — `core/save_manager.py` exists but nothing writes to it yet. Wire in after first real progression loop.
- **Heroic / Iron challenge modes** — `LevelDef.tags` is the seam; scene can read tags and tweak economy/waves.
- **Encore mode** — pair with unlocks.
- **Dual-faction tower selection (Alliance)** — factory already takes a family string, so adding `"evil_archer"` is one entry.
- **Gem economy (Vengeance)** — add a parallel currency to `GameState`; events already route reasons.
- **Pathfinding** — paths are hand-authored in level files. If map size grows, swap in A* against `map.grid` walkability.
- **Spatial hash for range queries** — current combat system is O(n·m). Replace `systems/collision.py` when enemy counts get high.
- **Audio** — audio dirs exist; `resources.py` only loads images today. Add `load_sound` the same way.

## Running the game

```bash
pip install -e .
python realmguard.py
```

## Common tasks

- **Tweak tower balance**: edit rows in [data/towers.py](src/td_game/data/towers.py). `TowerStatsRow.extras` carries arbitrary kwargs; towers read from it in `perform_attack`.
- **Add a wave to level 01**: append a `Wave(...)` to `_build_waves()` in [data/levels/level_01.py](src/td_game/data/levels/level_01.py).
- **Skin the game**: drop PNGs into `assets/sprites/<category>/` matching the keys used by the generator (e.g. `assets/sprites/enemies/orc_idle.png`). They take precedence automatically.
