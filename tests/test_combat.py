import random

from domain.combat import run_battle
from domain.models import ShipConfig, WeaponGroup

ION_CANNON = WeaponGroup(dice_count=1, damage=1)
PLASMA_MISSILE = WeaponGroup(dice_count=2, damage=2, is_missile=True)


def _make_interceptor(count: int = 1) -> ShipConfig:
    return ShipConfig(
        name="Interceptor",
        weapons=(ION_CANNON,),
        computer=0,
        shield=0,
        hull=0,
        initiative=3,
        count=count,
    )


def _make_cruiser(count: int = 1) -> ShipConfig:
    return ShipConfig(
        name="Cruiser",
        weapons=(ION_CANNON,),
        computer=1,
        shield=0,
        hull=1,
        initiative=2,
        count=count,
    )


def _make_ancient(count: int = 1) -> ShipConfig:
    return ShipConfig(
        name="Ancient",
        weapons=(ION_CANNON, ION_CANNON),
        computer=1,
        shield=0,
        hull=1,
        initiative=2,
        count=count,
    )


def _make_gcds() -> ShipConfig:
    return ShipConfig(
        name="GCDS",
        weapons=(ION_CANNON, ION_CANNON, ION_CANNON, ION_CANNON),
        computer=1,
        shield=0,
        hull=7,
        initiative=0,
        count=1,
    )


class TestBattleBasics:
    def test_returns_a_winner(self):
        rng = random.Random(42)
        result = run_battle(
            [_make_interceptor(2)],
            [_make_interceptor(2)],
            rng,
        )
        assert result.winner in ("attacker", "defender", "draw")

    def test_deterministic_with_same_seed(self):
        cfg_a = [_make_interceptor(3)]
        cfg_d = [_make_ancient()]

        r1 = run_battle(cfg_a, cfg_d, random.Random(100))
        r2 = run_battle(cfg_a, cfg_d, random.Random(100))
        assert r1.winner == r2.winner
        assert r1.rounds == r2.rounds
        assert r1.attacker_survivors == r2.attacker_survivors
        assert r1.defender_survivors == r2.defender_survivors

    def test_heavily_favored_side_wins(self):
        """8 interceptors vs 1 interceptor should almost always win for attacker."""
        wins = 0
        for seed in range(200):
            result = run_battle(
                [_make_interceptor(8)],
                [_make_interceptor(1)],
                random.Random(seed),
            )
            if result.winner == "attacker":
                wins += 1
        assert wins > 180  # expect > 90%

    def test_rounds_are_positive(self):
        result = run_battle(
            [_make_cruiser(2)],
            [_make_ancient()],
            random.Random(7),
        )
        assert result.rounds >= 1


class TestMissiles:
    def test_missiles_fire_before_cannons(self):
        """A missile-armed ship with high initiative should deal damage
        before the engagement round starts."""
        missile_ship = ShipConfig(
            name="MissileBoat",
            weapons=(PLASMA_MISSILE,),
            computer=3,
            shield=0,
            hull=0,
            initiative=5,
            count=4,
        )
        target = _make_interceptor(1)

        wins = 0
        for seed in range(100):
            result = run_battle([missile_ship], [target], random.Random(seed))
            if result.winner == "attacker":
                wins += 1
        # 4 missile boats with +3 computer vs 1 interceptor: should win most
        assert wins > 80


class TestDamageAndHull:
    def test_hull_absorbs_damage(self):
        """GCDS with 7 hull should survive many rounds against a single interceptor."""
        result = run_battle(
            [_make_interceptor(1)],
            [_make_gcds()],
            random.Random(42),
        )
        # GCDS should win almost certainly
        assert result.winner == "defender"

    def test_no_survivors_for_loser(self):
        for seed in range(50):
            result = run_battle(
                [_make_interceptor(1)],
                [_make_interceptor(1)],
                random.Random(seed),
            )
            if result.winner == "attacker":
                assert result.defender_survivors == {}
            elif result.winner == "defender":
                assert result.attacker_survivors == {}


class TestInitiativeOrder:
    def test_higher_initiative_fires_first(self):
        """Interceptor (init 3) should fire before Cruiser (init 2).
        With matched stats, firing first gives an edge."""
        # Give both sides identical offense so the only difference is initiative
        fast = ShipConfig(
            name="Fast",
            weapons=(ION_CANNON,),
            computer=0, shield=0, hull=0,
            initiative=5,
            count=3,
        )
        slow = ShipConfig(
            name="Slow",
            weapons=(ION_CANNON,),
            computer=0, shield=0, hull=0,
            initiative=1,
            count=3,
        )

        fast_wins = 0
        for seed in range(500):
            result = run_battle([fast], [slow], random.Random(seed))
            if result.winner == "attacker":
                fast_wins += 1

        # Fast side (attacker) fires first and should win more often
        assert fast_wins > 250


class TestCruiserVsAncient:
    def test_cruiser_vs_ancient_reasonable_odds(self):
        """A single default cruiser vs a single ancient should be a close fight."""
        att_wins = 0
        for seed in range(1000):
            result = run_battle(
                [_make_cruiser(1)],
                [_make_ancient(1)],
                random.Random(seed),
            )
            if result.winner == "attacker":
                att_wins += 1

        # Cruiser has 1 cannon +1 comp, 1 hull.  Ancient has 2 cannons +1 comp, 1 hull.
        # Ancient has double firepower so should win more, but it's not a blowout.
        assert 100 < att_wins < 600
