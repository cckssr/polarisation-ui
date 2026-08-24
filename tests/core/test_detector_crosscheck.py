"""Tests for polarisation_ui.core.detector_crosscheck."""

import pytest

from polarisation_ui.core.detector_crosscheck import (
    DetectorComparisonPoint,
    evaluate_detector_comparison,
)


def _pt(position, a, b):
    return DetectorComparisonPoint(position=position, power_a_W=a, power_b_W=b)


class TestEvaluateDetectorComparison:
    def test_identical_meters_pass_with_zero_spread(self):
        points = [
            _pt(x, p, p) for x, p in zip(range(5), [1e-3, 1e-4, 1e-5, 1e-6, 1e-7], strict=True)
        ]
        result = evaluate_detector_comparison(points, tolerance_pct=1.0)

        assert result.mean_ratio == pytest.approx(1.0)
        assert result.ratio_spread_pct == pytest.approx(0.0)
        assert result.worst_deviation_pct == pytest.approx(0.0)
        assert result.slope_W_per_W == pytest.approx(1.0)
        assert result.r_squared == pytest.approx(1.0)
        assert result.passed is True

    def test_constant_offset_ratio_detected(self):
        # B reads consistently 10% low.
        points = [
            _pt(x, p, 0.9 * p)
            for x, p in zip(range(5), [1e-3, 1e-4, 1e-5, 1e-6, 1e-7], strict=True)
        ]
        result = evaluate_detector_comparison(points, tolerance_pct=5.0)

        assert result.mean_ratio == pytest.approx(0.9)
        assert result.worst_deviation_pct == pytest.approx(0.0, abs=1e-9)
        assert result.passed is True  # spread is zero even though ratio != 1

    def test_fails_when_deviation_exceeds_tolerance(self):
        points = [
            _pt(0, 1e-3, 1.00e-3),
            _pt(1, 1e-4, 1.00e-4),
            _pt(2, 1e-5, 1.20e-5),  # 20%-ish outlier
        ]
        result = evaluate_detector_comparison(points, tolerance_pct=5.0)
        assert result.passed is False
        assert result.worst_deviation_pct > 5.0

    def test_zero_power_a_point_excluded_from_ratio_but_not_fit(self):
        points = [
            _pt(0, 0.0, 0.0),
            _pt(1, 1e-4, 1e-4),
            _pt(2, 1e-5, 1e-5),
        ]
        result = evaluate_detector_comparison(points)
        assert result.mean_ratio == pytest.approx(1.0)

    def test_raises_on_fewer_than_two_points(self):
        with pytest.raises(ValueError):
            evaluate_detector_comparison([_pt(0, 1e-3, 1e-3)])

    def test_raises_when_all_power_a_zero(self):
        with pytest.raises(ValueError):
            evaluate_detector_comparison([_pt(0, 0.0, 0.0), _pt(1, 0.0, 0.0)])

    def test_to_json_dict_has_expected_keys(self):
        points = [_pt(x, p, p) for x, p in zip(range(3), [1e-3, 1e-4, 1e-5], strict=True)]
        result = evaluate_detector_comparison(points)
        d = result.to_json_dict()
        assert set(d) >= {
            "mean_ratio",
            "ratio_spread_pct",
            "slope_W_per_W",
            "r_squared",
            "worst_deviation_pct",
            "tolerance_pct",
            "passed",
            "points",
        }
        assert len(d["points"]) == 3
