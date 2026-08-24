"""Tests for polarisation_ui.core.nd_filter.analyse_nd_scan."""

import pytest

from polarisation_ui.core.nd_filter import analyse_nd_scan


class TestBasicScan:
    def test_monotonic_decay_picks_ends_and_dynamic_range(self):
        # 3 decades of decay over 0..50 mm, clear end at 0, dark end at 50.
        points = [(x, 1e-3 * 10 ** (-3 * x / 50)) for x in range(0, 51, 5)]
        result = analyse_nd_scan(points)

        assert result.pos_clear_mm == pytest.approx(0.0)
        assert result.pos_dark_mm == pytest.approx(50.0)
        assert result.power_clear_W == pytest.approx(1e-3)
        assert result.power_dark_W == pytest.approx(1e-6, rel=1e-6)
        assert result.dynamic_range_dB == pytest.approx(30.0, abs=0.01)
        assert result.monotonic is True

    def test_scan_direction_reversed_gives_same_result(self):
        points = [(x, 1e-3 * 10 ** (-3 * x / 50)) for x in range(50, -1, -5)]
        result = analyse_nd_scan(points)

        assert result.pos_clear_mm == pytest.approx(0.0)
        assert result.pos_dark_mm == pytest.approx(50.0)
        assert result.monotonic is True

    def test_raises_on_fewer_than_two_points(self):
        with pytest.raises(ValueError):
            analyse_nd_scan([(0.0, 1e-3)])


class TestPlateauDetection:
    def test_clear_end_is_innermost_edge_of_plateau(self):
        # Flat clear-aperture region at 0 and 5 mm, then decaying.
        points = [
            (0, 1.0e-3),
            (5, 1.0e-3),
            (10, 9.0e-4),
            (15, 5.0e-4),
            (20, 1.0e-4),
        ]
        result = analyse_nd_scan(points, plateau_frac=0.01)

        # 5 mm still qualifies (>= 0.99 * 1e-3); 10 mm does not (9e-4 < 9.9e-4).
        assert result.pos_clear_mm == pytest.approx(5.0)

    def test_tighter_plateau_frac_shrinks_the_clear_region(self):
        points = [
            (0, 1.0e-3),
            (5, 1.0e-3),
            (10, 9.0e-4),
            (15, 5.0e-4),
            (20, 1.0e-4),
        ]
        result = analyse_nd_scan(points, plateau_frac=0.0001)
        assert result.pos_clear_mm == pytest.approx(5.0)  # still exactly equal to peak


class TestDarkFloor:
    def test_dark_floor_stops_before_raw_minimum(self):
        points = [
            (0, 1.0e-3),
            (10, 1.0e-4),
            (20, 1.0e-6),
            (30, 5.0e-9),  # at/below floor — should become the dark end
            (40, 3.0e-9),  # noise below floor, but further out
            (50, 4.0e-9),
        ]
        result = analyse_nd_scan(points, dark_floor_W=5e-9)
        assert result.pos_dark_mm == pytest.approx(30.0)
        assert result.power_dark_W == pytest.approx(5e-9)

    def test_no_floor_uses_raw_minimum(self):
        points = [
            (0, 1.0e-3),
            (10, 1.0e-4),
            (20, 1.0e-6),
            (30, 5.0e-9),
            (40, 3.0e-9),  # global min
            (50, 4.0e-9),
        ]
        result = analyse_nd_scan(points)
        assert result.pos_dark_mm == pytest.approx(40.0)
        assert result.power_dark_W == pytest.approx(3.0e-9)


class TestMonotonicDetection:
    def test_flags_non_monotonic_scan(self):
        points = [
            (0, 1.0e-3),
            (10, 5.0e-4),
            (20, 8.0e-4),  # bump — non-monotonic
            (30, 1.0e-4),
            (40, 1.0e-5),
        ]
        result = analyse_nd_scan(points)
        assert result.monotonic is False

    def test_tolerates_small_measurement_noise(self):
        points = [
            (0, 1.0e-3),
            (10, 5.0e-4),
            (20, 5.02e-4),  # within 2% noise tolerance
            (30, 1.0e-4),
            (40, 1.0e-5),
        ]
        result = analyse_nd_scan(points)
        assert result.monotonic is True


class TestJsonRoundTrip:
    def test_to_json_dict_has_expected_keys(self):
        points = [(x, 1e-3 * 10 ** (-3 * x / 50)) for x in range(0, 51, 5)]
        result = analyse_nd_scan(points)
        d = result.to_json_dict()
        assert set(d) == {
            "pos_clear_mm",
            "pos_dark_mm",
            "power_clear_W",
            "power_dark_W",
            "dynamic_range_dB",
            "monotonic",
        }
