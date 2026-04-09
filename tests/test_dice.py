import random

from domain.dice import is_hit, roll_die, roll_weapons
from domain.models import WeaponGroup


class TestIsHit:
    def test_roll_1_always_misses(self):
        assert is_hit(1, computer=10, shield=0) is False

    def test_roll_6_always_hits(self):
        assert is_hit(6, computer=0, shield=10) is True

    def test_exact_threshold_hits(self):
        # roll 5 + computer 1 - shield 0 = 6 -> hit
        assert is_hit(5, computer=1, shield=0) is True

    def test_below_threshold_misses(self):
        # roll 4 + computer 1 - shield 0 = 5 -> miss
        assert is_hit(4, computer=1, shield=0) is False

    def test_shields_subtract_from_roll(self):
        # roll 5 + computer 2 - shield 2 = 5 -> miss
        assert is_hit(5, computer=2, shield=2) is False

    def test_high_computer_makes_low_roll_hit(self):
        # roll 2 + computer 4 - shield 0 = 6 -> hit
        assert is_hit(2, computer=4, shield=0) is True

    def test_shields_cannot_prevent_natural_6(self):
        assert is_hit(6, computer=0, shield=5) is True

    def test_computers_cannot_save_natural_1(self):
        assert is_hit(1, computer=5, shield=0) is False

    def test_no_bonuses_only_6_hits(self):
        for roll in range(2, 6):
            assert is_hit(roll, computer=0, shield=0) is False
        assert is_hit(6, computer=0, shield=0) is True


class TestRollDie:
    def test_seeded_determinism(self):
        rng1 = random.Random(42)
        rng2 = random.Random(42)
        results1 = [roll_die(rng1) for _ in range(100)]
        results2 = [roll_die(rng2) for _ in range(100)]
        assert results1 == results2

    def test_range(self):
        rng = random.Random(123)
        results = {roll_die(rng) for _ in range(1000)}
        assert results == {1, 2, 3, 4, 5, 6}


class TestRollWeapons:
    def test_correct_dice_count(self):
        weapon = WeaponGroup(dice_count=2, damage=2)
        rng = random.Random(0)
        rolls = roll_weapons(weapon, ship_count=3, rng=rng)
        assert len(rolls) == 6  # 2 dice * 3 ships

    def test_missile_same_as_cannon_for_rolling(self):
        missile = WeaponGroup(dice_count=2, damage=2, is_missile=True)
        rng = random.Random(99)
        rolls = roll_weapons(missile, ship_count=2, rng=rng)
        assert len(rolls) == 4
        assert all(1 <= r <= 6 for r in rolls)

    def test_single_ship_single_die(self):
        weapon = WeaponGroup(dice_count=1, damage=1)
        rng = random.Random(7)
        rolls = roll_weapons(weapon, ship_count=1, rng=rng)
        assert len(rolls) == 1
