"""Tests for core/auto_calibration_settings.py — no Qt, no hardware."""

import math
import json
from pathlib import Path

import pytest

from polarisation_ui.core.auto_calibration_settings import (
    AutoCalibrationConnectionSettings,
    AutoCalibrationParams,
    build_angle_grid,
)

# ── AutoCalibrationConnectionSettings ────────────────────────────────────────


class TestAutoCalibrationConnectionSettings:
    def test_defaults(self):
        s = AutoCalibrationConnectionSettings()
        assert s.kdc101_conn_id == ""
        assert s.pm400_visa_resource == ""
        assert s.wavelength_nm == pytest.approx(633.0)
        assert s.beamsplitter_attenuation_dB == pytest.approx(0.0)
        assert s.angle_offset_deg == pytest.approx(0.0)

    def test_roundtrip_json(self, tmp_path):
        path = tmp_path / "settings.json"
        s = AutoCalibrationConnectionSettings(
            kdc101_conn_id="27266999",
            pm400_visa_resource="USB0::0x1313::0x8078::P0001::INSTR",
            beamsplitter_attenuation_dB=3.125,
            wavelength_nm=532.0,
            angle_offset_deg=23.75,
        )
        s.save(path)
        loaded = AutoCalibrationConnectionSettings.load(path)
        assert loaded.kdc101_conn_id == "27266999"
        assert loaded.pm400_visa_resource == "USB0::0x1313::0x8078::P0001::INSTR"
        assert loaded.beamsplitter_attenuation_dB == pytest.approx(3.125)
        assert loaded.wavelength_nm == pytest.approx(532.0)
        assert loaded.angle_offset_deg == pytest.approx(23.75)

    def test_angle_offset_defaults_to_zero_on_old_json(self, tmp_path):
        """JSON files that predate angle_offset_deg must load with 0.0."""
        path = tmp_path / "old.json"
        path.write_text(
            '{"kdc101_conn_id":"X","pm400_visa_resource":"Y",'
            '"beamsplitter_attenuation_dB":3.0,"wavelength_nm":633.0}',
            encoding="utf-8",
        )
        loaded = AutoCalibrationConnectionSettings.load(path)
        assert loaded.angle_offset_deg == pytest.approx(0.0)

    def test_load_missing_file_returns_defaults(self, tmp_path):
        s = AutoCalibrationConnectionSettings.load(tmp_path / "nonexistent.json")
        assert s.kdc101_conn_id == ""

    def test_load_corrupt_file_returns_defaults(self, tmp_path):
        path = tmp_path / "bad.json"
        path.write_text("not json", encoding="utf-8")
        s = AutoCalibrationConnectionSettings.load(path)
        assert s.kdc101_conn_id == ""


# ── build_angle_grid ──────────────────────────────────────────────────────────


def _make_params(mode: str, start=0.0, end=90.0, n=5) -> AutoCalibrationParams:
    return AutoCalibrationParams(
        selected_gains=(1, 2, 3, 4),
        angle_start_deg=start,
        angle_end_deg=end,
        n_points=n,
        grid_mode=mode,
        point_settle_s=0.1,
        gain_settle_s=0.2,
        detector_samples=3,
        pm_averaging=10,
        profile_name="test",
        wavelength_nm=633.0,
        beamsplitter_attenuation_dB=3.0,
    )


class TestBuildAngleGrid:
    def test_linear_angle_length(self):
        grid = build_angle_grid(_make_params("linear_angle", n=10))
        assert len(grid) == 10

    def test_linear_angle_endpoints(self):
        grid = build_angle_grid(_make_params("linear_angle", start=10.0, end=80.0, n=5))
        assert grid[0] == pytest.approx(10.0)
        assert grid[-1] == pytest.approx(80.0)

    def test_linear_angle_monotone(self):
        grid = build_angle_grid(_make_params("linear_angle", start=5.0, end=85.0, n=20))
        assert all(grid[i] <= grid[i + 1] for i in range(len(grid) - 1))

    def test_linear_cos2_length(self):
        grid = build_angle_grid(_make_params("linear_cos2", n=15))
        assert len(grid) == 15

    def test_linear_cos2_endpoints_within_range(self):
        grid = build_angle_grid(_make_params("linear_cos2", start=0.0, end=90.0, n=5))
        for angle in grid:
            assert 0.0 <= angle <= 90.0 + 1e-9

    def test_linear_cos2_intensity_steps_equal(self):
        grid = build_angle_grid(_make_params("linear_cos2", start=0.0, end=90.0, n=10))
        intensities = [math.cos(math.radians(a)) ** 2 for a in grid]
        diffs = [
            abs(intensities[i + 1] - intensities[i])
            for i in range(len(intensities) - 1)
        ]
        assert max(diffs) - min(diffs) < 1e-9

    def test_min_two_points_clamped(self):
        params = _make_params("linear_angle", n=1)
        grid = build_angle_grid(params)
        assert len(grid) == 2
