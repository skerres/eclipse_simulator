"""Domain data models for the Eclipse battle simulator."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class WeaponGroup:
    """A group of identical weapons on a ship blueprint.

    dice_count is per-ship (e.g. a Plasma Missile has dice_count=2).
    damage is per-hit (the burst count on the weapon's die symbol).
    """

    dice_count: int
    damage: int
    is_missile: bool = False


@dataclass(frozen=True)
class ShipConfig:
    """Immutable blueprint describing a type of ship and how many are in the fleet."""

    name: str
    weapons: tuple[WeaponGroup, ...] = ()
    computer: int = 0
    shield: int = 0
    hull: int = 0
    initiative: int = 0
    count: int = 1


@dataclass
class ShipInstance:
    """A single ship in an active battle, tracking accumulated damage."""

    config: ShipConfig
    damage_taken: int = 0

    @property
    def hp_remaining(self) -> int:
        """Remaining hit points before destruction."""
        return self.config.hull - self.damage_taken

    @property
    def is_destroyed(self) -> bool:
        """Whether accumulated damage exceeds the ship's hull value."""
        return self.damage_taken > self.config.hull


class DiceAssignmentStrategy(Protocol):
    """Strategy for assigning hitting dice to enemy targets."""

    def assign(
        self,
        rolls: list[int],
        weapon_damage: int,
        computer: int,
        targets: list[ShipInstance],
    ) -> dict[int, int]:
        """Return {target_index_in_live_targets: total_damage_to_apply}."""
        ...


@dataclass(frozen=True)
class BattleResult:
    """Outcome of a single battle."""

    winner: str  # "attacker", "defender", or "draw"
    attacker_survivors: dict[str, int] = field(default_factory=dict)
    defender_survivors: dict[str, int] = field(default_factory=dict)
    rounds: int = 0
