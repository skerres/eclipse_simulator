# Eclipse Battle Simulator

## Purpose

Monte Carlo battle simulator for the board game **Eclipse: Second Dawn for the Galaxy**.
Given two opposing fleets with configured combat stats, the simulator runs thousands of
battles and reports win probabilities, average survivors, and round counts.

The authoritative reference for game rules is [BATTLE_RULES.md](BATTLE_RULES.md).

## Tech Stack

- **Python 3.11+** — core language
- **uv** — dependency management and virtual environment
- **Streamlit** — web UI (presentation layer)
- **pytest** — test framework (dev dependency)

### Common Commands

```bash
uv sync                              # install all dependencies
uv run python -m pytest tests/ -v    # run tests
uv run streamlit run presentation/app.py  # launch the web UI
```

## Architecture

Three layers with **strict one-way dependencies**:

```
presentation/ ──depends-on──▶ simulation/ ──depends-on──▶ domain/
```

### Domain Layer (`domain/`)

Pure Python, **zero external dependencies**. Contains all game logic:

- `models.py` — frozen dataclasses: `WeaponGroup`, `ShipConfig`, `ShipInstance`, `BattleResult`
- `dice.py` — pure functions for die rolling and hit resolution
- `combat.py` — single-battle engine (missile phase + engagement round loop)

### Simulation Layer (`simulation/`)

Depends only on `domain`. Orchestrates repeated battles:

- `runner.py` — Monte Carlo runner: runs N independent battles, aggregates into `SimulationResult`

### Presentation Layer (`presentation/`)

Depends on `domain` and `simulation`. User-facing:

- `app.py` — Streamlit web app (fleet config forms, run button, results display, simulation history)
- `presets.py` — preset ship configurations (Ancient, Terran defaults, GCDS)

### Tests (`tests/`)

- `test_dice.py` — unit tests for hit resolution edge cases
- `test_combat.py` — deterministic battle scenarios with seeded RNG
- `test_runner.py` — Monte Carlo convergence validation

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Simulation method | Monte Carlo (default 10,000 runs) | Gives win percentages rather than single outcomes |
| Dice assignment | Greedy (focus-fire smallest to largest) | Simple, deterministic, reasonable approximation of player behavior |
| Retreat | Not modeled (fight to the death) | Keeps v1 scope manageable; retreat adds significant decision complexity |
| Ship configuration | Raw stats (dice, computer, shield, hull, initiative) | Avoids needing the full ship-part/energy system in v1 |
| Missiles | Supported as separate weapon type | Fires once before engagement rounds, per the rules |
| Simulation history | In-session list in `st.session_state` | Each run appends fleet descriptions + results; survives reruns but resets on browser refresh |

## Dependency Rule

- `domain/` must **never** import from `simulation/` or `presentation/`
- `simulation/` must **never** import from `presentation/`
- All cross-layer communication happens through domain model types

## Randomness & Testability

All randomness flows through injectable `random.Random` instances. No module-level
RNG state. This allows tests to use seeded RNG for fully deterministic, repeatable results.

```python
def run_battle(attacker: list[ShipConfig], defender: list[ShipConfig], rng: random.Random) -> BattleResult
```

## Code Conventions

- **Type hints** on all function signatures and dataclass fields
- **Frozen dataclasses** for immutable value types (`WeaponGroup`, `ShipConfig`, `BattleResult`)
- **Mutable dataclass** only for `ShipInstance` (tracks damage during a battle)
- **No mutable global state** — all state is local or passed as arguments
- **No comments that merely narrate code** — comments only for non-obvious intent or trade-offs

## Future Expansion Ideas

- Configurable dice assignment strategies (optimal, random, NPC rules, user-interactive)
- Retreat modeling (threshold-based, per-ship-type conditions, two-phase mechanic)
- Full ship part builder with energy validation and slot limits
- Species support (all 7+ factions with unique blueprints and special rules)
- Advanced combat mechanics (Rift Cannon, Cloaking Device, Neutron Absorber, Antimatter Splitter)
- Simulation enhancements (sensitivity sweeps, expected VP, battle logs, CSV export)
- UI improvements (save/load fleets, matchup comparisons, survival histograms, persistent history via database or file export)
