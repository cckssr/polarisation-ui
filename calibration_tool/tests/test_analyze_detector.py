"""Round-trip test: PowerCalibrationProfile.save() -> analyze_detector fit."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from analyze_detector import _analyze_gain, _load_points  # noqa: E402

from polarisation_ui.core.power_calibration import PowerCalibrationProfile  # noqa: E402

KNOWN_SLOPE = 2.5  # W/V


def _build_profile_with_known_slope(gain_stage: int = 1) -> PowerCalibrationProfile:
    """Build a profile whose points fit power = KNOWN_SLOPE * voltage exactly."""
    profile = PowerCalibrationProfile(name="Det-Test")
    for voltage_v in (0.1, 0.2, 0.3, 0.4, 0.5):
        profile.gain_cal(gain_stage).add_point(voltage_v, KNOWN_SLOPE * voltage_v)
    return profile


def test_load_points_round_trips_saved_profile(tmp_path):
    profile = _build_profile_with_known_slope(gain_stage=1)
    path = tmp_path / "Det-Test.json"
    profile.save(path)

    gains_points = _load_points(path)

    assert set(gains_points) == {"1"}
    assert gains_points["1"] == [
        [0.1, 0.25],
        [0.2, 0.5],
        [0.3, 0.75],
        [0.4, 1.0],
        [0.5, 1.25],
    ]


def test_analyze_gain_recovers_known_slope_and_perfect_fit(tmp_path):
    profile = _build_profile_with_known_slope(gain_stage=2)
    path = tmp_path / "Det-B.json"
    profile.save(path)

    gains_points = _load_points(path)
    result = _analyze_gain("2", gains_points["2"])

    assert result.slope == pytest.approx(KNOWN_SLOPE, rel=1e-9)
    assert result.intercept == pytest.approx(0.0, abs=1e-12)
    assert result.r_squared == pytest.approx(1.0, rel=1e-9)
    assert result.rmse == pytest.approx(0.0, abs=1e-12)


def test_empty_gain_stages_are_excluded(tmp_path):
    # __post_init__ populates all four gain stages, but stages with no points
    # must not appear in _load_points()'s output.
    profile = _build_profile_with_known_slope(gain_stage=3)
    path = tmp_path / "Det-C.json"
    profile.save(path)

    gains_points = _load_points(path)

    assert list(gains_points) == ["3"]
