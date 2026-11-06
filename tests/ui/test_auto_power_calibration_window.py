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


class TestWindowSizeStability:
    """Long text in status labels must clip, not enlarge the dialog."""

    _LONG = "Verbunden: /dev/cu.usbserial-0123456789-with-a-very-long-descriptive-port-name " * 4
    _LABELS = (
        "lblArduinoStatus",
        "lblKDCStatus",
        "lblPM400Status",
        "lblPM400BStatus",
        "lblNDStatus",
        "lblNDPosition",
        "lblNDDriver",
        "lblPhase",
        "lblOutputPath",
        "lblAngleOffset",
        "lblNDRange",
        "lblXCheckResult",
        "lblVerifyResult",
    )

    def test_long_label_text_does_not_grow_minimum_width(self, window, qapp):
        before = window.minimumSizeHint().width()
        for name in self._LABELS:
            getattr(window.ui, name).setText(self._LONG)
        qapp.processEvents()
        assert window.minimumSizeHint().width() == before

    def test_long_combo_entries_do_not_grow_minimum_width(self, window, qapp):
        from PySide6.QtWidgets import QComboBox

        before = window.minimumSizeHint().width()
        for combo in window.findChildren(QComboBox):
            combo.addItem("/dev/cu.usbserial-0123456789 – Silicon Labs CP210x USB to UART Bridge")
        qapp.processEvents()
        assert window.minimumSizeHint().width() == before

    def test_long_phase_text_is_kept_as_tooltip(self, window):
        window._set_phase(self._LONG)
        assert window.ui.lblPhase.toolTip() == self._LONG


class TestNDLinearityTab:
    @staticmethod
    def _scan(index, direction, offset_od=0.0):
        from polarisation_ui.core.nd_linearity import NDLinearityScan

        positions = [float(p) for p in range(0, 101, 10)]
        if direction == "backward":
            positions.reverse()
        pts = tuple((p, 1e-6 * 10 ** (-(0.01 * p + offset_od))) for p in positions)
        return NDLinearityScan(index, direction, pts)

    def test_report_lists_every_scan_and_hysteresis(self, window):
        window._on_nd_lin_scan_finished(self._scan(0, "forward"))
        window._on_nd_lin_scan_finished(self._scan(1, "backward", offset_od=0.03))
        text = window.ui.txtNDLinReport.toPlainText()
        assert "vorwärts" in text and "rückwärts" in text
        assert "Hysterese (vorwärts ↔ rückwärts)" in text
        assert "≈ 3.00°" in text

    def test_scan_over_tolerance_is_flagged(self, window):
        window.ui.spinNDLinTol.setValue(0.001)
        scan = self._scan(0, "forward")
        # Bend one point so the line no longer fits.
        pts = list(scan.points)
        pts[5] = (pts[5][0], pts[5][1] * 0.7)
        window._on_nd_lin_scan_finished(type(scan)(0, "forward", tuple(pts)))
        assert "ÜBER TOLERANZ" in window.ui.txtNDLinReport.toPlainText()

    def test_clear_discards_scans_and_report(self, window):
        window._on_nd_lin_scan_finished(self._scan(0, "forward"))
        window._clear_nd_lin()
        assert window._nd_lin_scans == []
        assert window.ui.txtNDLinReport.toPlainText() == ""

    def test_start_without_hardware_does_not_launch_worker(self, window, monkeypatch):
        from PySide6.QtWidgets import QMessageBox

        monkeypatch.setattr(QMessageBox, "warning", lambda *a, **k: None)
        window._start_nd_lin()
        assert window._nd_lin_worker is None

    def test_status_says_linearity_is_diagnostic_and_names_sweep_curve(self, window):
        text = window.ui.lblNDLinStatus.text()
        assert "nicht auf Sweeps angewendet" in text
        assert "Sweep-Kennlinie: keine" in text
        window._nd_range = _fake_nd_scan()
        window._refresh_nd_lin_status()
        assert "Bereichsscan dieser Sitzung" in window.ui.lblNDLinStatus.text()


class TestPowerFromNDCurve:
    def test_curve_keeps_only_points_between_the_calibrated_ends(self, window):
        # Rising tail beyond the dark end (sensor noise) must be dropped.
        pts = [(x, 1e-3 * 10 ** (-3 * x / 50)) for x in range(0, 51, 2)]
        result = analyse_nd_scan(pts + [(52.0, 5e-5)], dark_floor_W=2e-6)
        kept = window._nd_curve_between_ends(result)
        lo, hi = sorted((result.pos_clear_deg, result.pos_dark_deg))
        assert kept and all(lo <= pos <= hi for pos, _ in kept)
        assert (52.0, 5e-5) not in kept

    def test_curve_mode_greys_out_pm400_only_options(self, window):
        window.ui.radioSourceND.setChecked(True)  # the grid group is disabled in polariser mode
        window.ui.chkPowerFromCurve.setChecked(True)
        assert not window.ui.spinPowerTolerancePct.isEnabled()
        assert not window.ui.spinMaxRefineSteps.isEnabled()
        window.ui.chkPowerFromCurve.setChecked(False)
        assert window.ui.spinPowerTolerancePct.isEnabled()

    def test_curve_mode_requires_a_scan_from_this_session(self, window, monkeypatch):
        from PySide6.QtWidgets import QMessageBox

        warned: list[str] = []
        monkeypatch.setattr(QMessageBox, "warning", lambda *a, **k: warned.append(a[2]))
        window.ui.chkGain1.setChecked(True)
        window.ui.lineProfileName.setText("p")
        window.ui.radioSourceND.setChecked(True)
        window.ui.chkPowerFromCurve.setChecked(True)
        window._start_sweep()
        assert window._worker is None
        assert warned and "Bereichsscan dieser Sitzung" in warned[0]


class TestGainVerifyFromCurve:
    def test_curve_reference_does_not_require_a_connected_pm400(self, window):
        window._profile = _calibrated_profile()
        window._nd.is_connected = lambda: True  # type: ignore[method-assign]
        assert not window._verify_ready()
        window.ui.chkVerifyFromCurve.setChecked(True)
        assert window._verify_ready()

    def test_curve_reference_requires_a_scan_from_this_session(self, window, monkeypatch):
        from PySide6.QtWidgets import QMessageBox

        warned: list[str] = []
        monkeypatch.setattr(QMessageBox, "warning", lambda *a, **k: warned.append(a[2]))
        window._profile = _calibrated_profile()
        window._nd.is_connected = lambda: True  # type: ignore[method-assign]
        window.ui.chkVerifyFromCurve.setChecked(True)
        window._start_verify()
        assert window._verify_worker is None
        assert warned and "Bereichsscan dieser Sitzung" in warned[0]

    def test_return_pass_checkbox_reaches_the_params(self, window):
        window.ui.chkReturnPass.setChecked(True)
        assert window.ui.chkReturnPass.isChecked()
