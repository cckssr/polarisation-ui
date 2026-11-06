"""Tests for core.nd_linearity — pure analysis, no Qt or hardware."""

import math

import pytest

from polarisation_ui.core.nd_linearity import (
    BACKWARD,
    FORWARD,
    NDLinearityScan,
    analyse_linearity_set,
    fit_linearity,
)

P_MAX = 1e-6
SLOPE = 0.01  # OD per degree


def _scan(
    index: int,
    direction: str = FORWARD,
    *,
    offset_od: float = 0.0,
    ripple_od: float = 0.0,
    lo: float = 0.0,
    hi: float = 100.0,
    n: int = 11,
) -> NDLinearityScan:
    positions = [lo + (hi - lo) * i / (n - 1) for i in range(n)]
    if direction == BACKWARD:
        positions.reverse()
    points = tuple(
        (
            pos,
            P_MAX * 10.0 ** (-(SLOPE * pos + offset_od + ripple_od * (-1) ** round(pos / 10))),
        )
        for pos in positions
    )
    return NDLinearityScan(index=index, direction=direction, points=points)


class TestFitLinearity:
    def test_perfect_exponential_has_zero_residual(self):
        fit = fit_linearity(_scan(0), P_MAX)
        assert fit.slope_od_per_deg == pytest.approx(SLOPE)
        assert fit.intercept_od == pytest.approx(0.0, abs=1e-9)
        assert fit.max_residual_od == pytest.approx(0.0, abs=1e-9)
        assert fit.rms_residual_od == pytest.approx(0.0, abs=1e-9)

    def test_ripple_is_reported_as_residual(self):
        fit = fit_linearity(_scan(0, ripple_od=0.02), P_MAX)
        assert fit.max_residual_od == pytest.approx(0.02, rel=0.1)
        assert fit.max_residual_pct == pytest.approx((10**fit.max_residual_od - 1) * 100)

    def test_backward_scan_gives_same_fit_and_ascending_positions(self):
        fwd = fit_linearity(_scan(0, FORWARD), P_MAX)
        bwd = fit_linearity(_scan(1, BACKWARD), P_MAX)
        assert bwd.slope_od_per_deg == pytest.approx(fwd.slope_od_per_deg)
        assert list(bwd.positions_deg) == sorted(bwd.positions_deg)

    def test_negative_positions_are_supported(self):
        fit = fit_linearity(_scan(0, lo=-50.0, hi=50.0), P_MAX)
        assert fit.slope_od_per_deg == pytest.approx(SLOPE)

    def test_points_below_noise_floor_are_excluded(self):
        scan = _scan(0)
        noisy = NDLinearityScan(
            index=0,
            direction=FORWARD,
            points=(*scan.points[:-2], (90.0, 1e-12), (100.0, 0.0)),
        )
        fit = fit_linearity(noisy, P_MAX, noise_floor_W=1e-10)
        assert fit.n_used == len(scan.points) - 2
        assert fit.max_residual_od == pytest.approx(0.0, abs=1e-9)

    def test_too_few_usable_points_raises(self):
        scan = NDLinearityScan(0, FORWARD, ((0.0, 1e-6), (1.0, 5e-7)))
        with pytest.raises(ValueError, match="noise floor"):
            fit_linearity(scan, P_MAX)

    def test_non_positive_reference_raises(self):
        with pytest.raises(ValueError):
            fit_linearity(_scan(0), 0.0)


class TestLinearitySet:
    def test_empty_set_raises(self):
        with pytest.raises(ValueError):
            analyse_linearity_set([])

    def test_single_scan_has_no_cross_scan_metrics(self):
        report = analyse_linearity_set([_scan(0)])
        assert report.slope_std_od_per_deg == 0.0
        assert report.od_scatter_mean is None
        assert report.hysteresis_od is None

    def test_identical_scans_have_zero_scatter(self):
        report = analyse_linearity_set([_scan(0), _scan(1), _scan(2)])
        assert report.od_scatter_mean == pytest.approx(0.0, abs=1e-9)
        assert report.slope_std_od_per_deg == pytest.approx(0.0, abs=1e-12)
        assert report.hysteresis_od is None  # forward only

    def test_forward_backward_offset_is_reported_as_hysteresis(self):
        # The backward scan reads 0.03 OD darker everywhere → 0.03 / 0.01 = 3° of backlash.
        scans = [_scan(0, FORWARD), _scan(1, BACKWARD, offset_od=0.03)]
        report = analyse_linearity_set(scans)
        assert report.hysteresis_od == pytest.approx(0.03, abs=1e-6)
        assert report.hysteresis_deg == pytest.approx(3.0, abs=1e-3)

    def test_common_reference_exposes_drift_between_scans(self):
        report = analyse_linearity_set([_scan(0), _scan(1, offset_od=0.1)])
        assert report.od_scatter_mean == pytest.approx(0.1 / math.sqrt(2), abs=1e-6)
        # …while each scan on its own is still perfectly linear.
        assert all(f.max_residual_od < 1e-9 for f in report.fits)

    def test_scans_with_different_ranges_use_their_overlap(self):
        report = analyse_linearity_set([_scan(0, lo=0, hi=100), _scan(1, lo=20, hi=100)])
        assert report.od_scatter_max == pytest.approx(0.0, abs=1e-9)
