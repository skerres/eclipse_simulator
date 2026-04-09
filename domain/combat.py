"""Single-battle engine: missile phase, engagement rounds, pluggable dice assignment."""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

from domain.dice import roll_weapons
from domain.models import BattleResult, ShipInstance
from domain.strategy import GreedySmallestFirst

if TYPE_CHECKING:
    import random

    from domain.models import DiceAssignmentStrategy, ShipConfig, WeaponGroup

MAX_ROUNDS = 50


def run_battle(
    attacker_configs: list[ShipConfig],
    defender_configs: list[ShipConfig],
    rng: random.Random,
    strategy: DiceAssignmentStrategy | None = None,
) -> BattleResult:
    """Simulate a single battle between two fleets and return the outcome."""
    if strategy is None:
        strategy = GreedySmallestFirst()

    attackers = _expand_fleet(attacker_configs)
    defenders = _expand_fleet(defender_configs)

    _resolve_missiles(attackers, defenders, rng, strategy, defender_wins_ties=True)

    rounds = 0
    while _has_survivors(attackers) and _has_survivors(defenders):
        rounds += 1
        if rounds > MAX_ROUNDS:
            break

        activation_order = _build_activation_order(
            attackers, defenders, defender_wins_ties=True
        )

        for side, ship_type_name in activation_order:
            firing_ships, targets = _select_firing_and_targets(
                side, ship_type_name, attackers, defenders,
            )
            if firing_ships:
                _fire_cannons(firing_ships, targets, rng, strategy)

        _remove_destroyed(attackers)
        _remove_destroyed(defenders)

    return _build_result(attackers, defenders, rounds)


# ---------------------------------------------------------------------------
# Fleet expansion
# ---------------------------------------------------------------------------


def _expand_fleet(configs: list[ShipConfig]) -> list[ShipInstance]:
    instances: list[ShipInstance] = []
    for cfg in configs:
        for _ in range(cfg.count):
            instances.append(ShipInstance(config=cfg))
    return instances


# ---------------------------------------------------------------------------
# Activation ordering
# ---------------------------------------------------------------------------


def _build_activation_order(
    attackers: list[ShipInstance],
    defenders: list[ShipInstance],
    *,
    defender_wins_ties: bool,
) -> list[tuple[str, str]]:
    """Return (side, ship_type_name) tuples sorted by initiative descending.

    Defender wins ties when defender_wins_ties is True (the standard rule).
    """
    entries: list[tuple[int, int, str, str]] = []

    seen_attacker: set[str] = set()
    for ship in attackers:
        if ship.is_destroyed or ship.config.name in seen_attacker:
            continue
        seen_attacker.add(ship.config.name)
        tie_breaker = 1 if defender_wins_ties else 0
        entries.append((ship.config.initiative, tie_breaker, "attacker", ship.config.name))

    seen_defender: set[str] = set()
    for ship in defenders:
        if ship.is_destroyed or ship.config.name in seen_defender:
            continue
        seen_defender.add(ship.config.name)
        tie_breaker = 0 if defender_wins_ties else 1
        entries.append((ship.config.initiative, tie_breaker, "defender", ship.config.name))

    entries.sort(key=lambda e: (-e[0], e[1]))
    return [(side, name) for _, _, side, name in entries]


def _select_firing_and_targets(
    side: str,
    ship_type_name: str,
    attackers: list[ShipInstance],
    defenders: list[ShipInstance],
) -> tuple[list[ShipInstance], list[ShipInstance]]:
    if side == "attacker":
        firing = [
            s for s in attackers
            if s.config.name == ship_type_name and not s.is_destroyed
        ]
        return firing, defenders
    firing = [
        s for s in defenders
        if s.config.name == ship_type_name and not s.is_destroyed
    ]
    return firing, attackers


# ---------------------------------------------------------------------------
# Missile phase
# ---------------------------------------------------------------------------


def _resolve_missiles(
    attackers: list[ShipInstance],
    defenders: list[ShipInstance],
    rng: random.Random,
    strategy: DiceAssignmentStrategy,
    *,
    defender_wins_ties: bool,
) -> None:
    activation_order = _build_activation_order(
        attackers, defenders, defender_wins_ties=defender_wins_ties,
    )

    for side, ship_type_name in activation_order:
        firing_ships, targets = _select_firing_and_targets(
            side, ship_type_name, attackers, defenders,
        )
        if not firing_ships:
            continue

        missile_weapons = [w for w in firing_ships[0].config.weapons if w.is_missile]
        if not missile_weapons:
            continue

        ship_count = len(firing_ships)
        computer = firing_ships[0].config.computer

        for weapon in missile_weapons:
            rolls = roll_weapons(weapon, ship_count, rng)
            _apply_strategy(strategy, rolls, weapon, computer, targets)

    _remove_destroyed(attackers)
    _remove_destroyed(defenders)


# ---------------------------------------------------------------------------
# Cannon fire
# ---------------------------------------------------------------------------


def _fire_cannons(
    firing_ships: list[ShipInstance],
    targets: list[ShipInstance],
    rng: random.Random,
    strategy: DiceAssignmentStrategy,
) -> None:
    if not firing_ships or not targets:
        return

    cannon_weapons = [w for w in firing_ships[0].config.weapons if not w.is_missile]
    if not cannon_weapons:
        return

    ship_count = len(firing_ships)
    computer = firing_ships[0].config.computer

    for weapon in cannon_weapons:
        rolls = roll_weapons(weapon, ship_count, rng)
        _apply_strategy(strategy, rolls, weapon, computer, targets)


# ---------------------------------------------------------------------------
# Dice assignment dispatch
# ---------------------------------------------------------------------------


def _apply_strategy(
    strategy: DiceAssignmentStrategy,
    rolls: list[int],
    weapon: WeaponGroup,
    computer: int,
    targets: list[ShipInstance],
) -> None:
    """Delegate dice assignment to the strategy, then apply the resulting damage."""
    live_targets = [t for t in targets if not t.is_destroyed]
    if not live_targets:
        return

    damage_map = strategy.assign(rolls, weapon.damage, computer, live_targets)
    for idx, dmg in damage_map.items():
        live_targets[idx].damage_taken += dmg


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _has_survivors(fleet: list[ShipInstance]) -> bool:
    return any(not s.is_destroyed for s in fleet)


def _remove_destroyed(fleet: list[ShipInstance]) -> None:
    fleet[:] = [s for s in fleet if not s.is_destroyed]


def _build_result(
    attackers: list[ShipInstance],
    defenders: list[ShipInstance],
    rounds: int,
) -> BattleResult:
    att_alive = _has_survivors(attackers)
    def_alive = _has_survivors(defenders)

    if att_alive and not def_alive:
        winner = "attacker"
    elif def_alive and not att_alive:
        winner = "defender"
    else:
        winner = "draw"

    return BattleResult(
        winner=winner,
        attacker_survivors=_count_survivors(attackers),
        defender_survivors=_count_survivors(defenders),
        rounds=rounds,
    )


def _count_survivors(fleet: list[ShipInstance]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for ship in fleet:
        if not ship.is_destroyed:
            counts[ship.config.name] += 1
    return dict(counts)
