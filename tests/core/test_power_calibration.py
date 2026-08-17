"""Tests for core.power_calibration.select_best_profile_for_device_id.

Pure-function tests — no filesystem or Qt involved; profile lists are built
in-memory as Path objects (the function never touches disk itself).
"""

from pathlib import Path

from polarisation_ui.core.power_calibration import (
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
