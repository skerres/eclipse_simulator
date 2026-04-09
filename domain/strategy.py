"""Dice assignment strategies for Eclipse combat."""

from __future__ import annotations

from collections import defaultdict
from itertools import combinations
from typing import TYPE_CHECKING

from domain.dice import is_hit

if TYPE_CHECKING:
    import random

    from domain.models import ShipInstance


class GreedySmallestFirst:
    """Focus-fire on the weakest target first (fewest HP remaining).

    Optimal for maximizing kills per round when all targets share the same
    shield value.  This is the default / legacy behaviour.
    """

    def assign(
        self,
        rolls: list[int],
        weapon_damage: int,
        computer: int,
        targets: list[ShipInstance],
    ) -> dict[int, int]:
        pending: dict[int, int] = defaultdict(int)
        indexed = sorted(
            range(len(targets)), key=lambda i: targets[i].hp_remaining,
        )

        for roll in rolls:
            assigned = False
            for idx in indexed:
                if not is_hit(roll, computer, targets[idx].config.shield):
                    continue
                effective_hp = targets[idx].hp_remaining - pending[idx]
                if effective_hp > 0:
                    pending[idx] += weapon_damage
                    assigned = True
                    break

            if not assigned:
                for idx in indexed:
                    if is_hit(roll, computer, targets[idx].config.shield):
                        pending[idx] += weapon_damage
                        break

        return dict(pending)


class GreedyLargestFirst:
    """Focus-fire on the largest target first (most HP remaining).

    Matches the NPC dice assignment rules from the Eclipse rulebook:
    destroy the largest player ships first.
    """

    def assign(
        self,
        rolls: list[int],
        weapon_damage: int,
        computer: int,
        targets: list[ShipInstance],
    ) -> dict[int, int]:
        pending: dict[int, int] = defaultdict(int)
        indexed = sorted(
            range(len(targets)),
            key=lambda i: targets[i].hp_remaining,
            reverse=True,
        )

        for roll in rolls:
            assigned = False
            for idx in indexed:
                if not is_hit(roll, computer, targets[idx].config.shield):
                    continue
                effective_hp = targets[idx].hp_remaining - pending[idx]
                if effective_hp > 0:
                    pending[idx] += weapon_damage
                    assigned = True
                    break

            if not assigned:
                for idx in indexed:
                    if is_hit(roll, computer, targets[idx].config.shield):
                        pending[idx] += weapon_damage
                        break

        return dict(pending)


class RandomAssignment:
    """Assign each hitting die to a uniformly random live target."""

    def __init__(self, rng: random.Random) -> None:
        self._rng = rng

    def assign(
        self,
        rolls: list[int],
        weapon_damage: int,
        computer: int,
        targets: list[ShipInstance],
    ) -> dict[int, int]:
        pending: dict[int, int] = defaultdict(int)
        hittable_by_target: list[list[int]] = [[] for _ in targets]
        for idx in range(len(targets)):
            for roll in rolls:
                if is_hit(roll, computer, targets[idx].config.shield):
                    hittable_by_target[idx].append(roll)

        valid_indices = [i for i in range(len(targets)) if hittable_by_target[i]]
        if not valid_indices:
            return {}

        for roll in rolls:
            reachable = [
                i for i in valid_indices
                if is_hit(roll, computer, targets[i].config.shield)
            ]
            if reachable:
                idx = self._rng.choice(reachable)
                pending[idx] += weapon_damage

        return dict(pending)


class MaximizeKills:
    """Optimal single-round strategy: maximize the number of ships destroyed.

    Enumerates feasible kill-sets (affordable given the available hitting dice
    and per-target shield constraints) and picks the largest.  Ties are broken
    by total threat removed (sum of weapon dice counts on killed targets).

    Remaining dice after the chosen kill-set are distributed greedily to soften
    surviving targets (smallest HP first).
    """

    def assign(
        self,
        rolls: list[int],
        weapon_damage: int,
        computer: int,
        targets: list[ShipInstance],
    ) -> dict[int, int]:
        n = len(targets)
        if n == 0:
            return {}

        hits_for: list[list[int]] = [[] for _ in range(n)]
        for idx in range(n):
            for roll in rolls:
                if is_hit(roll, computer, targets[idx].config.shield):
                    hits_for[idx].append(roll)

        hits_needed: list[int] = []
        for idx in range(n):
            hp = targets[idx].hp_remaining
            hits_needed.append((hp // weapon_damage) + 1)

        total_hits = sum(1 for r in rolls for idx in range(n)
                         if is_hit(r, computer, targets[idx].config.shield))
        if total_hits == 0:
            return {}

        killable = [
            idx for idx in range(n) if len(hits_for[idx]) >= hits_needed[idx]
        ]

        best_set: tuple[int, ...] = ()
        best_threat = -1

        # Uniform-shield fast path: all targets reachable by all hitting dice.
        shields = {targets[idx].config.shield for idx in range(n)}
        if len(shields) == 1:
            total_hitting = len(hits_for[killable[0]]) if killable else 0
            sorted_killable = sorted(killable, key=lambda i: hits_needed[i])
            budget = total_hitting
            chosen: list[int] = []
            for idx in sorted_killable:
                if budget >= hits_needed[idx]:
                    budget -= hits_needed[idx]
                    chosen.append(idx)
            best_set = tuple(chosen)
        else:
            for size in range(len(killable), 0, -1):
                if best_set and len(best_set) >= size:
                    break
                for combo in combinations(killable, size):
                    cost = sum(hits_needed[i] for i in combo)
                    if cost > len(rolls):
                        continue
                    if not self._is_feasible(combo, hits_needed, hits_for, rolls,
                                             computer, targets, weapon_damage):
                        continue
                    threat = sum(
                        sum(w.dice_count for w in targets[i].config.weapons)
                        for i in combo
                    )
                    if len(combo) > len(best_set) or (
                        len(combo) == len(best_set) and threat > best_threat
                    ):
                        best_set = combo
                        best_threat = threat
                if best_set and len(best_set) == size:
                    break

        pending: dict[int, int] = defaultdict(int)
        used_rolls: list[bool] = [False] * len(rolls)

        for idx in sorted(best_set, key=lambda i: len(hits_for[i])):
            assigned = 0
            for ri, roll in enumerate(rolls):
                if used_rolls[ri]:
                    continue
                if is_hit(roll, computer, targets[idx].config.shield):
                    pending[idx] += weapon_damage
                    used_rolls[ri] = True
                    assigned += 1
                    if assigned >= hits_needed[idx]:
                        break

        survivors = sorted(
            [i for i in range(n) if i not in best_set],
            key=lambda i: targets[i].hp_remaining,
        )
        for ri, roll in enumerate(rolls):
            if used_rolls[ri]:
                continue
            for idx in survivors:
                if is_hit(roll, computer, targets[idx].config.shield):
                    pending[idx] += weapon_damage
                    used_rolls[ri] = True
                    break

        return dict(pending)

    @staticmethod
    def _is_feasible(
        combo: tuple[int, ...],
        hits_needed: list[int],
        hits_for: list[list[int]],
        rolls: list[int],
        computer: int,
        targets: list[ShipInstance],
        weapon_damage: int,
    ) -> bool:
        """Check whether the dice can be assigned to kill all targets in *combo*."""
        used: list[bool] = [False] * len(rolls)
        for idx in sorted(combo, key=lambda i: len(hits_for[i])):
            assigned = 0
            for ri, roll in enumerate(rolls):
                if used[ri]:
                    continue
                if is_hit(roll, computer, targets[idx].config.shield):
                    used[ri] = True
                    assigned += 1
                    if assigned >= hits_needed[idx]:
                        break
            if assigned < hits_needed[idx]:
                return False
        return True


STRATEGIES: dict[str, type] = {
    "Greedy (smallest first)": GreedySmallestFirst,
    "Greedy (largest first / NPC)": GreedyLargestFirst,
    "Random": RandomAssignment,
    "Maximize kills": MaximizeKills,
}

DEFAULT_STRATEGY_NAME = "Greedy (smallest first)"
