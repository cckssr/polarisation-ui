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
        "valueArduinoStatus",
        "valueKDCStatus",
        "valuePM400Status",
        "valuePM400BStatus",
        "valueNDStatus",
        "valueNDPosition",
        "valueNDDriver",
        "valuePhase",
        "valueOutputPath",
        "valueAngleOffset",
        "valueNDRange",
        "valueXCheckResult",
        "valueVerifyResult",
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
        assert window.ui.valuePhase.toolTip() == self._LONG


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
        text = window.ui.editNDLinReport.toPlainText()
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
        assert "ÜBER TOLERANZ" in window.ui.editNDLinReport.toPlainText()

    def test_clear_discards_scans_and_report(self, window):
        window._on_nd_lin_scan_finished(self._scan(0, "forward"))
        window._clear_nd_lin()
        assert window._nd_lin_scans == []
        assert window.ui.editNDLinReport.toPlainText() == ""

    def test_start_without_hardware_does_not_launch_worker(self, window, monkeypatch):
        from PySide6.QtWidgets import QMessageBox

        monkeypatch.setattr(QMessageBox, "warning", lambda *a, **k: None)
        window._start_nd_lin()
        assert window._nd_lin_worker is None

    def test_status_says_linearity_is_diagnostic_and_names_sweep_curve(self, window):
        text = window.ui.valueNDLinStatus.text()
        assert "nicht auf Sweeps angewendet" in text
        assert "Sweep-Kennlinie: keine" in text
        window._nd_range = _fake_nd_scan()
        window._refresh_nd_lin_status()
        assert "Bereichsscan dieser Sitzung" in window.ui.valueNDLinStatus.text()


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
        window.ui.checkPowerFromCurve.setChecked(True)
        assert not window.ui.spinPowerTolerancePct.isEnabled()
        assert not window.ui.spinMaxRefineSteps.isEnabled()
        window.ui.checkPowerFromCurve.setChecked(False)
        assert window.ui.spinPowerTolerancePct.isEnabled()

    def test_curve_mode_requires_a_scan_from_this_session(self, window, monkeypatch):
        from PySide6.QtWidgets import QMessageBox

        warned: list[str] = []
        monkeypatch.setattr(QMessageBox, "warning", lambda *a, **k: warned.append(a[2]))
        window.ui.checkGain1.setChecked(True)
        window.ui.editProfileName.setText("p")
        window.ui.radioSourceND.setChecked(True)
        window.ui.checkPowerFromCurve.setChecked(True)
        window._start_sweep()
        assert window._worker is None
        assert warned and "Bereichsscan dieser Sitzung" in warned[0]


# ── Configured strings ────────────────────────────────────────────────────────


def _config():
    from polarisation_ui.infrastructure.config import load_config

    return load_config()


class TestConfiguredStrings:
    def test_the_window_shows_the_german_texts_of_the_config(self, window):
        ui = window.ui
        assert window.windowTitle() == "Automatische Leistungskalibrierung"
        assert ui.buttonStart.text() == "Starten"
        assert ui.buttonConnectKDC.text() == "Verbinden"
        assert ui.valuePM400Status.text() == "Nicht verbunden"
        assert ui.valuePhase.text() == "Bereit"
        assert ui.groupAlignment.title() == "Polarisator-Ausrichtung"
        assert "Fährt den Referenzschalter an" in ui.buttonHomeNDStage.toolTip()
        assert ui.editProfileName.placeholderText() == "z.B. Det-A_auto"

    def test_tab_titles_and_table_headers_come_from_the_config(self, window):
        tabs = window.ui.tabMode
        titles = [tabs.tabText(i) for i in range(tabs.count())]
        assert titles == [
            "Kalibrierung",
            "ND-Bereich",
            "ND-Linearität",
            "Detektor-Vergleich",
            "Gain-Prüfung",
        ]
        table = window.ui.tableGainVerify
        headers = [table.horizontalHeaderItem(i).text() for i in range(table.columnCount())]
        assert headers == [
            "Pegel",
            "PM400 (W)",
            "Gain 1 (W)",
            "Gain 2 (W)",
            "Gain 3 (W)",
            "Gain 4 (W)",
        ]

    def test_every_ui_key_resolves_to_a_child_widget(self, window):
        from PySide6.QtCore import QObject

        strings = _config().section("ui")["auto_power_calibration"]
        missing = []
        for key in strings:
            name = key.partition("@")[0]
            if "_" in name:
                continue  # plain texts looked up by the code
            if name != "self" and window.findChild(QObject, name) is None:
                missing.append(key)
        assert not missing

    def test_no_label_button_or_check_is_empty_or_shows_a_raw_key(self, window):
        from PySide6.QtWidgets import QCheckBox, QLabel, QPushButton, QRadioButton

        for kind in (QLabel, QPushButton, QCheckBox, QRadioButton):
            for widget in window.findChildren(kind):
                name = widget.objectName()
                if name.startswith(("label", "button", "check", "radio")):
                    assert widget.text(), name
                    assert "auto_power_calibration" not in widget.text(), name

    def test_every_code_key_used_by_the_window_exists_in_the_config(self):
        import re
        from pathlib import Path

        import polarisation_ui.ui.windows.auto_power_calibration_window as module

        source = Path(module.__file__).read_text(encoding="utf-8")
        cfg = _config()
        texts = set(re.findall(r'\b_t\(\s*"(\w+)"', source)) | set(
            re.findall(r'\bt\(\s*"(\w+)"', source)
        )
        messages = set(re.findall(r'\b_m\(\s*"(\w+)"', source))
        messages |= set(re.findall(r'\b_m\(\s*"(\w+)"\s+if\s+\w', source))
        # _warn("title_key", "message_key") / _error("title_key", ...) / "verdict_ok" ternary
        for title, message in re.findall(r'\b_warn\(\s*"(\w+)",\s*"(\w+)"', source):
            texts.add(title)
            messages.add(message)
        texts |= set(re.findall(r'\b_error\(\s*"(\w+)"', source))
        texts |= set(re.findall(r'\b_apply_pm_settings\(\s*"(\w+)"', source))
        messages |= set(re.findall(r'"(verdict_ok|verdict_failed)"', source))
        assert texts and messages
        for key in texts:
            assert cfg.get(f"ui.auto_power_calibration.{key}") is not None, key
        for key in messages:
            assert cfg.get(f"messages.auto_power_calibration.{key}") is not None, key

    def test_a_config_override_changes_the_shown_texts(self, qapp):
        from polarisation_ui.ui.windows.auto_power_calibration_window import (
            AutoPowerCalibrationWindow,
        )

        config = _config().with_overrides(
            {"ui": {"auto_power_calibration": {"buttonStart": "Go", "button_connect": "Link"}}}
        )
        w = AutoPowerCalibrationWindow(config=config)
        try:
            assert w.ui.buttonStart.text() == "Go"
            assert w._t("button_connect") == "Link"
        finally:
            w.close()

    def test_a_warning_uses_the_configured_title_and_message(self, window, monkeypatch):
        from PySide6.QtWidgets import QMessageBox

        shown: list[tuple[str, str]] = []
        monkeypatch.setattr(QMessageBox, "warning", lambda *a, **k: shown.append((a[1], a[2])))
        for chk in (
            window.ui.checkGain1,
            window.ui.checkGain2,
            window.ui.checkGain3,
            window.ui.checkGain4,
        ):
            chk.setChecked(False)
        window._start_sweep()
        assert shown == [("Start", "Mindestens eine Gain-Stufe auswählen.")]

    def test_the_abort_marker_comes_from_the_config(self, window):
        assert window._is_abort_message("Scan abgebrochen")
        assert not window._is_abort_message("Timeout")

    def test_status_texts_use_named_placeholders(self, window):
        window._set_phase(window._m("gain_started", gain=3))
        assert window.ui.valuePhase.text() == "Gain 3 wird kalibriert…"
        window._show_nd_driver_status()  # not connected: must not raise
        window.ui.valueNDDriver.setText(window._t("nd_driver_other", status="X"))
        assert window.ui.valueNDDriver.text() == "Treiber: X"


class TestGainWindowsFromTheInjectedConfig:
    def test_the_gain_switch_windows_come_from_the_given_config(self, qapp):
        from polarisation_ui.ui.windows.auto_power_calibration_window import (
            AutoPowerCalibrationWindow,
        )

        # Disjoint windows: no overlap between neighbouring gain stages, so no verify level.
        windows = {
            "1": {"min": 1.0e-3, "max": 1.0},
            "2": {"min": 1.0e-4, "max": 5.0e-4},
            "3": {"min": 1.0e-5, "max": 5.0e-5},
            "4": {"min": 0.0, "max": 5.0e-6},
        }
        config = _config().with_overrides({"pdtia": {"gain_auto_switch_power_W": windows}})
        w = AutoPowerCalibrationWindow(config=config)
        try:
            w._profile = _calibrated_profile()
            w._nd_range = _fake_nd_scan()
            assert w._compute_verify_levels(3) == []
        finally:
            w.close()

    def test_the_default_config_has_overlapping_windows(self, window):
        window._profile = _calibrated_profile()
        window._nd_range = _fake_nd_scan()
        assert len(window._compute_verify_levels(3)) == 3


class TestReportFormatting:
    def test_the_report_labels_come_from_the_config(self):
        from polarisation_ui.core.nd_linearity import NDLinearityScan, analyse_linearity_set
        from polarisation_ui.ui.windows.auto_power_calibration_window import (
            format_nd_linearity_report,
        )

        positions = [float(p) for p in range(0, 101, 10)]
        pts = tuple((p, 1e-6 * 10 ** (-0.01 * p)) for p in positions)
        report = analyse_linearity_set([NDLinearityScan(0, "forward", pts)], noise_floor_W=0.0)
        text = format_nd_linearity_report(report, 0.05)
        assert text.splitlines()[0].startswith("Referenz OD=0:")
        assert "vorwärts" in text and "OK" in text
        custom = _config().with_overrides(
            {"ui": {"auto_power_calibration": {"report_header": "REF {power} / {tolerance}"}}}
        )
        assert format_nd_linearity_report(report, 0.05, config=custom).startswith("REF ")


class TestPlotTexts:
    def test_the_plots_label_their_axes_from_the_config(self, window):
        assert (
            window.ui.calibrationPlot._plot_widget.getAxis("bottom").labelText == "Detektorspannung"
        )
        assert window.ui.ndRangePlot._plot_widget.getAxis("bottom").labelText == "Winkel"
        assert window.ui.xCheckPlot._plot_widget.getAxis("left").labelText == "PM400 B (Prüfling)"
        assert (
            window.ui.ndLinearityPlot._resid_plot.getAxis("left").labelText
            == "Abweichung vom linearen OD-Fit"
        )

    def test_a_config_override_relabels_the_plots_and_the_legend(self, qapp):
        from polarisation_ui.ui.widgets.multi_gain_calibration_plot import MultiGainCalibrationPlot
        from polarisation_ui.ui.widgets.nd_linearity_plot import NDLinearityPlot

        config = _config().with_overrides(
            {
                "ui": {
                    "plots": {
                        "multi_gain_series_name": "G{gain}",
                        "multi_gain_voltage_label": "Voltage",
                        "nd_linearity_scan_backward": "Back {number}",
                    }
                }
            }
        )
        plot = MultiGainCalibrationPlot(config=config)
        assert plot._plot_widget.getAxis("bottom").labelText == "Voltage"
        assert plot._series[2].name() == "G2"
        plot.apply_config(_config())
        assert plot._series[2].name() == "Gain 2"
        assert plot._plot_widget.getAxis("bottom").labelText == "Detektorspannung"
        lin = NDLinearityPlot(config=config)
        lin.begin_scan(1, "backward")
        assert lin._power_curves[1].name() == "Back 2"


class TestPM400Combo:
    def test_the_empty_placeholder_comes_from_the_config(self, qapp, monkeypatch):
        from PySide6.QtWidgets import QComboBox

        from polarisation_ui.infrastructure.devices.pm400 import PM400PowerMeter
        from polarisation_ui.ui.common.pm400_combo import populate_pm400_combo

        monkeypatch.setattr(PM400PowerMeter, "list_resources", staticmethod(lambda: []))
        combo = QComboBox()
        assert populate_pm400_combo(combo, "x") == []
        assert combo.placeholderText() == "Kein PM400 gefunden"
        custom = _config().with_overrides({"ui": {"common": {"pm400_none_found": "none"}}})
        populate_pm400_combo(combo, config=custom)
        assert combo.placeholderText() == "none"
