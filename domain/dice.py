"""Pure functions for die rolling and hit resolution."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import random

    from domain.models import WeaponGroup


def roll_die(rng: random.Random) -> int:
    """Roll a single d6."""
    return rng.randint(1, 6)


def is_hit(roll: int, computer: int, shield: int) -> bool:
    """Determine whether a die roll is a hit per Eclipse combat rules.

    Args:
        roll: The raw d6 result (1-6).
        computer: Attacker's total computer bonus.
        shield: Target's total shield value.

    Returns:
        True if the roll is a hit.
    """
    if roll == 1:
        return False
    if roll == 6:
        return True
    return (roll + computer - shield) >= 6


def roll_weapons(
    weapon: WeaponGroup,
    ship_count: int,
    rng: random.Random,
) -> list[int]:
    """Roll all dice for a weapon group across *ship_count* ships.

    Returns the raw die results (list of ints 1-6).
    Total dice = weapon.dice_count * ship_count.
    """
    total_dice = weapon.dice_count * ship_count
    return [roll_die(rng) for _ in range(total_dice)]
