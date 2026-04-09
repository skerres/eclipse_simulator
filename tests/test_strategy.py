"""Tests for dice assignment strategies."""

import random

from domain.combat import run_battle
from domain.models import ShipConfig, ShipInstance, WeaponGroup
from domain.strategy import (
    GreedyLargestFirst,
    GreedySmallestFirst,
    MaximizeKills,
    RandomAssignment,
)

ION_CANNON = WeaponGroup(dice_count=1, damage=1)
PLASMA_CANNON = WeaponGroup(dice_count=1, damage=2)


def _ship(hull: int, shield: int = 0, name: str = "Ship") -> ShipInstance:
    return ShipInstance(
        config=ShipConfig(
            name=name,
            weapons=(ION_CANNON,),
            computer=0,
            shield=shield,
            hull=hull,
        )
    )


class TestGreedySmallestFirst:
    def test_focuses_weakest_target(self):
        """First hits go to the weakest target to fill its HP allocation."""
        strategy = GreedySmallestFirst()
        targets = [_ship(hull=5, name="Big"), _ship(hull=1, name="Small")]
        # 3 guaranteed hits at dmg 1: Small gets 1 (fills hp_remaining=1), Big gets 2
        result = strategy.assign([6, 6, 6], weapon_damage=1, computer=0, targets=targets)
        assert result.get(1, 0) == 1  # Small filled first
        assert result.get(0, 0) == 2  # Big gets the rest

    def test_overflow_goes_to_smallest(self):
        """After all targets are filled, overflow dice go to the smallest target."""
        strategy = GreedySmallestFirst()
        targets = [_ship(hull=2, name="A"), _ship(hull=4, name="B")]
        # 10 hits at dmg 1: A gets 2 (fills hp), B gets 4 (fills hp), 4 overflow → A first
        result = strategy.assign([6] * 10, weapon_damage=1, computer=0, targets=targets)
        assert result.get(0, 0) == 2 + 4  # A's hp + 4 overflow
        assert result.get(1, 0) == 4  # B's hp filled


class TestGreedyLargestFirst:
    def test_focuses_strongest_target(self):
        """All hits should land on the largest target first."""
        strategy = GreedyLargestFirst()
        targets = [_ship(hull=0, name="Small"), _ship(hull=3, name="Big")]
        result = strategy.assign([6, 6], weapon_damage=1, computer=0, targets=targets)
        # Both hits should go to the big ship (index 1) since it has more HP
        assert result.get(1, 0) == 2

    def test_overflow_goes_to_largest(self):
        """After all targets are filled, overflow dice go to the largest target."""
        strategy = GreedyLargestFirst()
        targets = [_ship(hull=5, name="Big"), _ship(hull=1, name="Small")]
        # 10 hits at dmg 1: Big gets 5 (fills hp), Small gets 1 (fills hp), 4 overflow → Big
        rolls = [6] * 10
        result = strategy.assign(rolls, weapon_damage=1, computer=0, targets=targets)
        assert result.get(0, 0) == 5 + 4  # Big's hp + 4 overflow
        assert result.get(1, 0) == 1  # Small's hp filled


class TestRandomAssignment:
    def test_distributes_across_targets(self):
        """With many hits, random should distribute across all targets."""
        rng = random.Random(42)
        strategy = RandomAssignment(rng)
        targets = [_ship(hull=10, name="A"), _ship(hull=10, name="B")]
        rolls = [6] * 100
        result = strategy.assign(rolls, weapon_damage=1, computer=0, targets=targets)
        # Both targets should receive some damage
        assert result.get(0, 0) > 10
        assert result.get(1, 0) > 10

    def test_respects_hit_check(self):
        """Dice that can't hit (roll 1) should assign no damage."""
        rng = random.Random(0)
        strategy = RandomAssignment(rng)
        targets = [_ship(hull=5)]
        result = strategy.assign([1, 1, 1], weapon_damage=1, computer=0, targets=targets)
        assert result == {}


class TestMaximizeKills:
    def test_prefers_more_kills_over_fewer(self):
        """Given enough hits to kill two small ships OR damage one big ship,
        MaximizeKills should kill the two small ships."""
        strategy = MaximizeKills()
        # Big ship: hull 5, needs 6 hits to kill. Small ships: hull 0, need 1 hit each.
        targets = [
            _ship(hull=5, name="Big"),
            _ship(hull=0, name="Small1"),
            _ship(hull=0, name="Small2"),
        ]
        # 3 guaranteed hits at 1 damage each — can kill 2 smalls but not the big
        result = strategy.assign([6, 6, 6], weapon_damage=1, computer=0, targets=targets)
        assert result.get(1, 0) >= 1  # Small1 killed
        assert result.get(2, 0) >= 1  # Small2 killed

    def test_uniform_shield_fast_path(self):
        """When all targets have the same shield, maximizes kills greedily."""
        strategy = MaximizeKills()
        targets = [_ship(hull=1, name="A"), _ship(hull=0, name="B")]
        # 3 hits at dmg 1: can kill A (needs 2 hits) + B (needs 1 hit)
        result = strategy.assign([6, 6, 6], weapon_damage=1, computer=0, targets=targets)
        assert result.get(0, 0) >= 2  # A killed
        assert result.get(1, 0) >= 1  # B killed

    def test_mixed_shields_assigns_restricted_dice_wisely(self):
        """A die that rolled 3 with +3 computer can hit shield-0 but not shield-1.
        MaximizeKills should use the restricted die on the unshielded target and
        save the versatile die (roll 6) for the shielded target."""
        strategy = MaximizeKills()
        unshielded = _ship(hull=0, shield=0, name="Unshielded")
        shielded = _ship(hull=0, shield=1, name="Shielded")
        targets = [unshielded, shielded]
        # Roll 3 + computer 3 - shield 0 = 6 >= 6 → hits unshielded
        # Roll 3 + computer 3 - shield 1 = 5 < 6 → misses shielded
        # Roll 6 always hits both
        # Optimal: assign roll-3 to unshielded, roll-6 to shielded → 2 kills
        result = strategy.assign([3, 6], weapon_damage=1, computer=3, targets=targets)
        assert result.get(0, 0) >= 1
        assert result.get(1, 0) >= 1

    def test_softens_survivors(self):
        """After maximizing kills, remaining dice should damage surviving targets."""
        strategy = MaximizeKills()
        targets = [_ship(hull=10, name="Tank"), _ship(hull=0, name="Small")]
        # 2 hits: 1 kills Small, 1 left over → should soften Tank
        result = strategy.assign([6, 6], weapon_damage=1, computer=0, targets=targets)
        assert result.get(1, 0) >= 1  # Small killed
        assert result.get(0, 0) >= 1  # Tank softened


class TestStrategiesInBattle:
    """Integration: run full battles with each strategy and verify they produce
    valid results."""

    def _interceptor(self, count: int = 1) -> ShipConfig:
        return ShipConfig(
            name="Interceptor",
            weapons=(ION_CANNON,),
            computer=0, shield=0, hull=0,
            initiative=3, count=count,
        )

    def _ancient(self, count: int = 1) -> ShipConfig:
        return ShipConfig(
            name="Ancient",
            weapons=(ION_CANNON, ION_CANNON),
            computer=1, shield=0, hull=1,
            initiative=2, count=count,
        )

    def test_all_strategies_produce_valid_results(self):
        att = [self._interceptor(4)]
        dfd = [self._ancient(2)]
        strategies = [
            GreedySmallestFirst(),
            GreedyLargestFirst(),
            RandomAssignment(random.Random(42)),
            MaximizeKills(),
        ]
        for strategy in strategies:
            result = run_battle(att, dfd, random.Random(42), strategy)
            assert result.winner in ("attacker", "defender", "draw")
            assert result.rounds >= 1

    def test_greedy_smallest_is_default_when_none(self):
        """Passing strategy=None should use GreedySmallestFirst (backward compat)."""
        att = [self._interceptor(3)]
        dfd = [self._ancient(1)]
        r_none = run_battle(att, dfd, random.Random(99), strategy=None)
        r_explicit = run_battle(att, dfd, random.Random(99), GreedySmallestFirst())
        assert r_none.winner == r_explicit.winner
        assert r_none.rounds == r_explicit.rounds
        assert r_none.attacker_survivors == r_explicit.attacker_survivors
        assert r_none.defender_survivors == r_explicit.defender_survivors

    def test_maximize_kills_at_least_as_good_as_greedy(self):
        """Over many battles, MaximizeKills should win at least as often as greedy
        smallest-first (it can only do better or the same)."""
        att = [self._interceptor(4)]
        dfd = [self._ancient(2)]
        greedy_wins = 0
        optimal_wins = 0
        for seed in range(500):
            r_greedy = run_battle(att, dfd, random.Random(seed), GreedySmallestFirst())
            r_optimal = run_battle(att, dfd, random.Random(seed), MaximizeKills())
            if r_greedy.winner == "attacker":
                greedy_wins += 1
            if r_optimal.winner == "attacker":
                optimal_wins += 1
        assert optimal_wins >= greedy_wins - 5  # small tolerance for edge cases
