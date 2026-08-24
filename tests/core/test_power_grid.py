"""Tests for interp_monotonic, build_power_grid, and positions_for_target_powers."""

import pytest

from polarisation_ui.core.auto_calibration_settings import (
    build_power_grid,
    positions_for_target_powers,
)
from polarisation_ui.core.utils import interp_monotonic


class TestInterpMonotonic:
    def test_interpolates_between_points(self):
        xs = [0.0, 1.0, 2.0]
        ys = [0.0, 10.0, 20.0]
        assert interp_monotonic(0.5, xs, ys) == pytest.approx(5.0)

    def test_clamps_below_range(self):
        xs = [1.0, 2.0, 3.0]
        ys = [10.0, 20.0, 30.0]
        assert interp_monotonic(-5.0, xs, ys) == pytest.approx(10.0)

    def test_clamps_above_range(self):
        xs = [1.0, 2.0, 3.0]
        ys = [10.0, 20.0, 30.0]
        assert interp_monotonic(99.0, xs, ys) == pytest.approx(30.0)

    def test_exact_match_returns_exact_y(self):
        xs = [0.0, 1.0, 2.0]
        ys = [0.0, 10.0, 20.0]
        assert interp_monotonic(1.0, xs, ys) == pytest.approx(10.0)

    def test_raises_on_empty(self):
        with pytest.raises(ValueError):
            interp_monotonic(1.0, [], [])

    def test_raises_on_length_mismatch(self):
        with pytest.raises(ValueError):
            interp_monotonic(1.0, [0.0, 1.0], [0.0])


class TestBuildPowerGrid:
    def test_log_power_length_and_endpoints(self):
        grid = build_power_grid(1e-3, 1e-7, 10, mode="log_power")
        assert len(grid) == 10
        assert grid[0] == pytest.approx(1e-3)
        assert grid[-1] == pytest.approx(1e-7)

    def test_log_power_equal_ratio_steps(self):
        grid = build_power_grid(1e-3, 1e-7, 9, mode="log_power")
        ratios = [grid[i] / grid[i + 1] for i in range(len(grid) - 1)]
        assert max(ratios) - min(ratios) < 1e-9

    def test_log_power_rejects_nonpositive(self):
        with pytest.raises(ValueError):
            build_power_grid(1e-3, 0.0, 5, mode="log_power")

    def test_linear_power_length_and_endpoints(self):
        grid = build_power_grid(1e-3, 1e-4, 10, mode="linear_power")
        assert len(grid) == 10
        assert grid[0] == pytest.approx(1e-3)
        assert grid[-1] == pytest.approx(1e-4)

    def test_linear_power_equal_absolute_steps(self):
        grid = build_power_grid(1.0, 0.0, 5, mode="linear_power")
        diffs = [grid[i] - grid[i + 1] for i in range(len(grid) - 1)]
        assert all(d == pytest.approx(0.25) for d in diffs)

    def test_n_clamped_to_minimum_two(self):
        grid = build_power_grid(1e-3, 1e-4, 1, mode="linear_power")
        assert len(grid) == 2


class TestPositionsForTargetPowers:
    def _scan(self):
        # Monotonic decay, position 0..50 mm, 3 decades.
        return [(x, 1e-3 * 10 ** (-3 * x / 50)) for x in range(0, 51, 5)]

    def test_maps_targets_to_positions_monotonically(self):
        scan = self._scan()
        targets = build_power_grid(1e-3, 1e-6, 5, mode="log_power")
        positions = positions_for_target_powers(targets, scan)
        assert len(positions) == 5
        assert all(positions[i] <= positions[i + 1] for i in range(len(positions) - 1))

    def test_endpoint_targets_map_to_endpoint_positions(self):
        scan = self._scan()
        positions = positions_for_target_powers([1e-3, 1e-6], scan)
        assert positions[0] == pytest.approx(0.0, abs=0.5)
        assert positions[-1] == pytest.approx(50.0, abs=0.5)

    def test_out_of_range_target_clamps(self):
        scan = self._scan()
        positions = positions_for_target_powers([1.0, 1e-12], scan)
        assert positions[0] == pytest.approx(0.0)
        assert positions[1] == pytest.approx(50.0)

    def test_raises_on_empty_scan(self):
        with pytest.raises(ValueError):
            positions_for_target_powers([1e-4], [])
