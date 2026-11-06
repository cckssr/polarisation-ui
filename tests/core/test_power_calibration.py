"""Tests for core.power_calibration.select_best_profile_for_device_id.

Pure-function tests — no filesystem or Qt involved; profile lists are built
in-memory as Path objects (the function never touches disk itself).
"""

import json
from pathlib import Path

import pytest

from polarisation_ui.core.power_calibration import (
    GainCalibration,
    PowerCalibrationProfile,
    load_gain_power_limits,
    select_best_profile_for_device_id,
    select_gain_for_power,
)


def _paths(*stems: str) -> list[Path]:
    return [Path(f"{stem}.json") for stem in stems]


class TestSelectBestProfileForDeviceId:
    def test_empty_device_id_returns_none(self):
        profiles = _paths("20250101_DET-A")
        assert select_best_profile_for_device_id(profiles, "") is None

    def test_no_match_returns_none(self):
        profiles = _paths("20250101_DET-A", "20250102_DET-B")
        assert select_best_profile_for_device_id(profiles, "DET-C") is None

    def test_single_match(self):
        profiles = _paths("20250101_DET-A")
        best = select_best_profile_for_device_id(profiles, "DET-A")
        assert best is not None
        assert best.stem == "20250101_DET-A"

    def test_dated_profile_preferred_over_undated(self):
        profiles = _paths("DET-A", "20250101_DET-A")
        best = select_best_profile_for_device_id(profiles, "DET-A")
        assert best.stem == "20250101_DET-A"

    def test_newest_date_wins_among_dated(self):
        profiles = _paths("20240101_DET-A", "20250601_DET-A", "20241231_DET-A")
        best = select_best_profile_for_device_id(profiles, "DET-A")
        assert best.stem == "20250601_DET-A"


class TestSelectGainForPower:
    _LIMITS = {
        1: (8.0e-5, 1.0),
        2: (8.0e-6, 1.2e-4),
        3: (8.0e-7, 1.2e-5),
        4: (0.0, 1.2e-6),
    }

    def test_empty_limits_returns_none(self):
        assert select_gain_for_power(1e-6, {}) is None

    def test_picks_matching_window(self):
        assert select_gain_for_power(5e-7, self._LIMITS) == 4
        assert select_gain_for_power(5e-3, self._LIMITS) == 1

    def test_prefers_lowest_gain_among_overlapping_matches(self):
        # 1e-4 falls in both gain 1's and gain 2's window.
        assert select_gain_for_power(1e-4, self._LIMITS) == 1

    def test_keeps_current_stage_within_overlap_to_avoid_flapping(self):
        # Still within gain 2's window even though gain 1 would also match.
        assert select_gain_for_power(1e-4, self._LIMITS, current_stage=2) == 2

    def test_switches_when_current_stage_no_longer_covers_power(self):
        assert select_gain_for_power(1e-6, self._LIMITS, current_stage=1) == 3

    def test_out_of_range_snaps_to_nearest(self):
        assert select_gain_for_power(10.0, self._LIMITS) == 1
        assert select_gain_for_power(-1.0, self._LIMITS) == 4

    def test_only_matching_device_id_considered(self):
        profiles = _paths("20250101_DET-A", "20260101_DET-B")
        best = select_best_profile_for_device_id(profiles, "DET-A")
        assert best.stem == "20250101_DET-A"


class TestPowerCalibrationProfileSaveLoad:
    """Backwards-compatibility contract: only `name` and `gains.<n>.points` are
    load-bearing — everything else must round-trip through .get() with a
    default, so both old files loading into new code and new files loading
    into old code stay correct."""

    _FIXED_POINTS = [(0.1, 1.0e-6), (0.2, 2.0e-6), (0.3, 3.0e-6)]

    def test_minimal_legacy_dict_loads(self, tmp_path):
        """A real in-the-wild profile carries only these three keys."""
        path = tmp_path / "DetRechts.json"
        path.write_text(
            json.dumps(
                {
                    "name": "DetRechts",
                    "calibrated_at": "2025-01-15",
                    "gains": {"1": {"points": [[0.1, 1.0e-6]]}},
                }
            ),
            encoding="utf-8",
        )
        profile = PowerCalibrationProfile.load(path)
        assert profile.name == "DetRechts"
        assert profile.gains[1].points == [(0.1, 1.0e-6)]
        assert profile.intensity_control == {}
        assert profile.gain_crosscheck == {}
        assert profile.wavelength_nm is None
        assert profile.sensor == {}

    def test_intensity_control_and_gain_crosscheck_roundtrip(self, tmp_path):
        path = tmp_path / "profile.json"
        profile = PowerCalibrationProfile(
            name="Det-A",
            intensity_control={"kind": "nd_filter", "unit": "deg", "range": [2.5, 47.5]},
            gain_crosscheck={"passed": True, "worst_spread_pct": 1.2},
        )
        profile.gains[1] = GainCalibration(gain_stage=1, points=list(self._FIXED_POINTS))
        profile.save(path)

        loaded = PowerCalibrationProfile.load(path)
        assert loaded.intensity_control == {
            "kind": "nd_filter",
            "unit": "deg",
            "range": [2.5, 47.5],
        }
        assert loaded.gain_crosscheck == {"passed": True, "worst_spread_pct": 1.2}

    def test_new_metadata_absent_from_legacy_reader_view(self, tmp_path):
        """A profile with the new keys still parses fine if a reader only looks
        at `gains` (mirrors calibration_tool/analyze_detector.py's `_load_points`)."""
        path = tmp_path / "profile.json"
        profile = PowerCalibrationProfile(name="Det-A", intensity_control={"kind": "nd_filter"})
        profile.gains[1] = GainCalibration(gain_stage=1, points=list(self._FIXED_POINTS))
        profile.save(path)

        with path.open() as fh:
            raw = json.load(fh)
        points = {gid: entry["points"] for gid, entry in raw["gains"].items() if entry["points"]}
        assert points == {"1": [[0.1, 1.0e-6], [0.2, 2.0e-6], [0.3, 3.0e-6]]}

    def test_conversion_factor_unaffected_by_new_fields(self):
        """conversion_factor_W_per_V() must be bit-identical regardless of the
        new metadata fields — it is computed purely from `points`."""
        plain = GainCalibration(gain_stage=1, points=list(self._FIXED_POINTS))
        with_meta_profile = PowerCalibrationProfile(
            name="X", intensity_control={"kind": "nd_filter"}, gain_crosscheck={"passed": True}
        )
        with_meta_profile.gains[1] = GainCalibration(gain_stage=1, points=list(self._FIXED_POINTS))

        assert plain.conversion_factor_W_per_V() == pytest.approx(1e-5)
        assert with_meta_profile.conversion_factor(1) == plain.conversion_factor_W_per_V()


class TestGainCalibrationFit:
    """The W/V factor is a weighted LS fit with zero-light offset, not a mean of P/V."""

    @staticmethod
    def _line(slope: float, v0: float, powers: list[float]) -> list[tuple[float, float]]:
        return [(p / slope + v0, p) for p in powers]

    def test_recovers_slope_and_offset(self):
        cal = GainCalibration(
            gain_stage=2, points=self._line(1.2e-4, -5.6e-3, [4e-7, 1e-6, 1e-5, 1e-4, 2.4e-4])
        )
        assert cal.conversion_factor_W_per_V() == pytest.approx(1.2e-4, rel=1e-9)
        assert cal.zero_offset_V() == pytest.approx(-5.6e-3, rel=1e-9)

    def test_regression_small_voltage_points_do_not_inflate_factor(self):
        """Mean of P/V gave ~2x the true slope when points sit near V=0 with an offset."""
        cal = GainCalibration(
            gain_stage=2, points=self._line(1.2e-4, -5.6e-3, [4e-7, 1e-6, 1e-5, 1e-4, 2.4e-4])
        )
        naive = sum(p / v for v, p in cal.points if v > 0) / sum(1 for v, _ in cal.points if v > 0)
        assert naive > 1.5 * 1.2e-4  # the old estimator is clearly biased on this data
        assert cal.conversion_factor_W_per_V() == pytest.approx(1.2e-4, rel=1e-6)

    def test_watts_from_voltage_applies_offset(self):
        cal = GainCalibration(gain_stage=1, points=self._line(1e-3, -6e-3, [4e-7, 1e-5, 1e-3]))
        # Zero-light reading maps to zero power, not to a negative one.
        assert cal.watts_from_voltage(-6e-3) == pytest.approx(0.0, abs=1e-15)
        assert cal.watts_from_voltage(0.5) == pytest.approx(1e-3 * (0.5 + 6e-3))

    def test_single_point_falls_back_to_origin_line(self):
        cal = GainCalibration(gain_stage=3, points=[(0.2, 2e-6)])
        assert cal.conversion_factor_W_per_V() == pytest.approx(1e-5)
        assert cal.zero_offset_V() == 0.0

    def test_identical_voltages_fall_back_to_origin_line(self):
        cal = GainCalibration(gain_stage=3, points=[(0.2, 2e-6), (0.2, 2e-6)])
        assert cal.conversion_factor_W_per_V() == pytest.approx(1e-5)
        assert cal.zero_offset_V() == 0.0

    def test_no_points_or_no_positive_power(self):
        assert GainCalibration(gain_stage=1).conversion_factor_W_per_V() is None
        assert GainCalibration(gain_stage=1).watts_from_voltage(0.1) is None
        assert GainCalibration(gain_stage=1).zero_offset_V() == 0.0
        assert GainCalibration(gain_stage=1, points=[(0.1, 0.0)]).fit() is None

    def test_offset_survives_save_and_load(self, tmp_path):
        profile = PowerCalibrationProfile(name="Det-A")
        profile.gains[2] = GainCalibration(
            gain_stage=2, points=self._line(1.2e-4, -5.6e-3, [4e-7, 1e-5, 2.4e-4])
        )
        path = tmp_path / "p.json"
        profile.save(path)
        loaded = PowerCalibrationProfile.load(path)
        assert loaded.zero_offset_V(2) == pytest.approx(-5.6e-3, rel=1e-6)
        assert loaded.watts_from_voltage(-5.6e-3, 2) == pytest.approx(0.0, abs=1e-12)
        assert loaded.zero_offset_V(4) == 0.0


class TestLoadGainPowerLimits:
    def test_parses_valid_entries(self):
        config = {"pdtia": {"gain_auto_switch_power_W": {"1": {"min": 1e-4, "max": 1.0}}}}
        assert load_gain_power_limits(config) == {1: (1e-4, 1.0)}

    def test_missing_section_returns_empty(self):
        assert load_gain_power_limits({}) == {}

    def test_skips_malformed_entries(self):
        config = {
            "pdtia": {
                "gain_auto_switch_power_W": {
                    "1": {"min": 1e-4, "max": 1.0},
                    "bad": {"min": "x", "max": 1.0},
                    "2": {"min": 1.0},
                }
            }
        }
        assert load_gain_power_limits(config) == {1: (1e-4, 1.0)}
