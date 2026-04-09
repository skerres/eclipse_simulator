from domain.models import ShipConfig, WeaponGroup
from simulation.runner import run_simulation

ION_CANNON = WeaponGroup(dice_count=1, damage=1)


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


class TestSimulationRunner:
    def test_returns_correct_totals(self):
        result = run_simulation(
            [_make_interceptor(2)],
            [_make_interceptor(2)],
            n=100,
            seed=42,
        )
        assert result.num_simulations == 100
        assert result.attacker_wins + result.defender_wins + result.draws == 100

    def test_percentages_sum_to_100(self):
        result = run_simulation(
            [_make_interceptor(3)],
            [_make_interceptor(1)],
            n=500,
            seed=7,
        )
        total = result.attacker_win_pct + result.defender_win_pct + result.draw_pct
        assert abs(total - 100.0) < 0.01

    def test_deterministic_with_seed(self):
        args = ([_make_interceptor(3)], [_make_interceptor(2)])
        r1 = run_simulation(*args, n=200, seed=99)
        r2 = run_simulation(*args, n=200, seed=99)
        assert r1.attacker_wins == r2.attacker_wins
        assert r1.defender_wins == r2.defender_wins
        assert r1.draws == r2.draws

    def test_asymmetric_matchup_converges(self):
        """GCDS vs 1 interceptor: GCDS should win overwhelmingly."""
        result = run_simulation(
            [_make_interceptor(1)],
            [_make_gcds()],
            n=1000,
            seed=42,
        )
        assert result.defender_win_pct > 90.0

    def test_large_fleet_advantage_shows(self):
        """8 interceptors vs 1 should show strong attacker advantage."""
        result = run_simulation(
            [_make_interceptor(8)],
            [_make_interceptor(1)],
            n=1000,
            seed=42,
        )
        assert result.attacker_win_pct > 90.0

    def test_avg_rounds_positive(self):
        result = run_simulation(
            [_make_interceptor(2)],
            [_make_interceptor(2)],
            n=100,
            seed=0,
        )
        assert result.avg_rounds > 0

    def test_avg_survivors_in_range(self):
        result = run_simulation(
            [_make_interceptor(4)],
            [_make_interceptor(2)],
            n=500,
            seed=12,
        )
        assert 0 <= result.avg_attacker_survivors <= 4
        assert 0 <= result.avg_defender_survivors <= 2
