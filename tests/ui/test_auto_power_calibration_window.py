"""Tests for AutoPowerCalibrationWindow's pure-logic helpers.

No hardware, no worker threads — just the QDialog construction (needed for
widget access) and _compute_verify_levels(), which had a bug where the
requested level count was silently capped at the number of adjacent-gain
overlap windows (at most 3 for 4 gain stages) regardless of what the user
asked for.

IMPORTANT: AutoCalibrationConnectionSettings.load()/.save() default to a
real path under the user's home directory
(~/.config/polarisation-ui/auto_calibration_settings.json), and
AutoPowerCalibrationWindow reads it in __init__ and writes it in
closeEvent(). The isolate_settings fixture below redirects that module-level
path to a tmp_path for every test in this file — never construct or close
this window in a test without it, or you will read/overwrite the real user
config file (this happened once during development).
"""

import pytest

from polarisation_ui.core.nd_filter import analyse_nd_scan
from polarisation_ui.core.power_calibration import GainCalibration, PowerCalibrationProfile


@pytest.fixture
def qapp():
    import sys

    from PySide6.QtWidgets import QApplication

    return QApplication.instance() or QApplication(sys.argv)


@pytest.fixture(autouse=True)
def isolate_settings(tmp_path, monkeypatch):
    """Redirect AutoCalibrationConnectionSettings' default path to tmp_path.

    load()/save() take ``path: Path = _SETTINGS_PATH`` — a default bound at
    function-definition time, so patching the module constant alone does
    nothing to already-compiled defaults. Wrapping both methods to force
    tmp_path is the only reliable way to keep every no-arg call (as
    AutoPowerCalibrationWindow makes) off the real ~/.config file.
    """
    import polarisation_ui.core.auto_calibration_settings as settings_mod

    fake_path = tmp_path / "auto_calibration_settings.json"
    cls = settings_mod.AutoCalibrationConnectionSettings
    original_load = cls.load.__func__
    original_save = cls.save

    monkeypatch.setattr(
        cls, "load", classmethod(lambda klass, path=fake_path: original_load(klass, path))
    )
    monkeypatch.setattr(cls, "save", lambda self, path=fake_path: original_save(self, path))


@pytest.fixture
def window(qapp):
    from polarisation_ui.ui.windows.auto_power_calibration_window import (
        AutoPowerCalibrationWindow,
    )

    w = AutoPowerCalibrationWindow()
    yield w
    w.close()


def _calibrated_profile(gains=(1, 2, 3, 4)) -> PowerCalibrationProfile:
    profile = PowerCalibrationProfile(name="test")
    for g in gains:
        profile.gains[g] = GainCalibration(gain_stage=g, points=[(2.5, 1.0e-6)])
    return profile


def _fake_nd_scan():
    points = [(x, 1e-3 * 10 ** (-3 * x / 50)) for x in range(0, 51, 2)]
    return analyse_nd_scan(points)


class TestComputeVerifyLevels:
    def test_level_count_matches_requested_above_overlap_count(self, window):
        """4 calibrated gains -> only 3 adjacent overlaps, but the level count
        must still track the spinbox value beyond 3 (the bug: it was capped)."""
        window._profile = _calibrated_profile()
        window._nd_range = _fake_nd_scan()

        assert len(window._compute_verify_levels(1)) == 1
        assert len(window._compute_verify_levels(3)) == 3
        assert len(window._compute_verify_levels(6)) == 6
        assert len(window._compute_verify_levels(10)) == 10
        assert len(window._compute_verify_levels(20)) == 20

    def test_level_count_below_overlap_count_is_a_subset(self, window):
        window._profile = _calibrated_profile()
        window._nd_range = _fake_nd_scan()

        assert len(window._compute_verify_levels(1)) == 1
        assert len(window._compute_verify_levels(2)) == 2

    def test_no_profile_returns_empty(self, window):
        window._nd_range = _fake_nd_scan()
        assert window._compute_verify_levels(3) == []

    def test_no_nd_scan_returns_empty(self, window):
        window._profile = _calibrated_profile()
        assert window._compute_verify_levels(3) == []

    def test_single_calibrated_gain_has_no_overlap(self, window):
        window._profile = _calibrated_profile(gains=(1,))
        window._nd_range = _fake_nd_scan()
        assert window._compute_verify_levels(3) == []

    def test_levels_stay_within_nd_travel(self, window):
        window._profile = _calibrated_profile()
        window._nd_range = _fake_nd_scan()
        for n in (1, 5, 10, 20):
            for level in window._compute_verify_levels(n):
                assert 0.0 <= level <= 50.0
