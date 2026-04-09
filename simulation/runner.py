"""Monte Carlo simulation runner for Eclipse battles."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from domain.combat import run_battle

if TYPE_CHECKING:
    from domain.models import BattleResult, DiceAssignmentStrategy, ShipConfig


@dataclass(frozen=True)
class SimulationResult:
    """Aggregated outcome of N independent battle simulations."""

    num_simulations: int
    attacker_wins: int
    defender_wins: int
    draws: int
    attacker_win_pct: float
    defender_win_pct: float
    draw_pct: float
    avg_rounds: float
    avg_attacker_survivors: float
    avg_defender_survivors: float
    results: tuple[BattleResult, ...] = field(repr=False, default=())


def run_simulation(
    attacker_configs: list[ShipConfig],
    defender_configs: list[ShipConfig],
    n: int = 10_000,
    seed: int | None = None,
    strategy: DiceAssignmentStrategy | None = None,
) -> SimulationResult:
    """Run *n* independent battles and return aggregated statistics."""
    attacker_wins = 0
    defender_wins = 0
    draws = 0
    total_rounds = 0
    total_attacker_survivors = 0
    total_defender_survivors = 0
    results: list[BattleResult] = []

    for i in range(n):
        run_seed = (seed + i) if seed is not None else None
        rng = random.Random(run_seed)

        result = run_battle(attacker_configs, defender_configs, rng, strategy)
        results.append(result)

        if result.winner == "attacker":
            attacker_wins += 1
        elif result.winner == "defender":
            defender_wins += 1
        else:
            draws += 1

        total_rounds += result.rounds
        total_attacker_survivors += sum(result.attacker_survivors.values())
        total_defender_survivors += sum(result.defender_survivors.values())

    return SimulationResult(
        num_simulations=n,
        attacker_wins=attacker_wins,
        defender_wins=defender_wins,
        draws=draws,
        attacker_win_pct=attacker_wins / n * 100 if n else 0,
        defender_win_pct=defender_wins / n * 100 if n else 0,
        draw_pct=draws / n * 100 if n else 0,
        avg_rounds=total_rounds / n if n else 0,
        avg_attacker_survivors=total_attacker_survivors / n if n else 0,
        avg_defender_survivors=total_defender_survivors / n if n else 0,
        results=tuple(results),
    )
