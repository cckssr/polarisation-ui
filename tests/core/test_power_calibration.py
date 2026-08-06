"""Tests for core.power_calibration.select_best_profile_for_device_id.

Pure-function tests — no filesystem or Qt involved; profile lists are built
in-memory as Path objects (the function never touches disk itself).
"""

from pathlib import Path

from polarisation_ui.core.power_calibration import select_best_profile_for_device_id


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

    def test_only_matching_device_id_considered(self):
        profiles = _paths("20250101_DET-A", "20260101_DET-B")
        best = select_best_profile_for_device_id(profiles, "DET-A")
        assert best.stem == "20250101_DET-A"
