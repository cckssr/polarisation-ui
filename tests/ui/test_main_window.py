"""MainWindow on the simulated bench: wiring of the controllers to the Designer form."""

from __future__ import annotations

import ast
import re
import sys
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import pytest
from PySide6.QtWidgets import QDialog, QFileDialog, QMessageBox

from polarisation_ui.core.models import AcquisitionSettings, TabExport
from polarisation_ui.core.power_calibration import PowerCalibrationProfile
from polarisation_ui.infrastructure import session_journal
from polarisation_ui.infrastructure.modules import ModuleRegistry
from polarisation_ui.infrastructure.session_state import SessionState, save_session_state
from polarisation_ui.ui import context as context_module
from polarisation_ui.ui.common.status_led import LED_GREEN, LED_RED, LED_YELLOW
from polarisation_ui.ui.windows import mainwindow as mainwindow_module
from polarisation_ui.ui.windows.mainwindow import MainWindow

pytestmark = pytest.mark.skipif(sys.platform == "win32", reason="PTY not available on Windows")

UI_DIR = Path(__file__).resolve().parents[2] / "polarisation_ui" / "ui"
KDC_ID = "mock://kdc101"
PM400_RESOURCE = "USB0::0x1313::0x8078::MOCK00001::INSTR"


def _text(window: MainWindow, key: str, **fmt: object) -> str:
    return window.config.text(f"mainwindow.{key}", **fmt)


def _tab_titles(window: MainWindow) -> list[str]:
    tabs = window.ui.tabWidget
    return [tabs.tabText(i) for i in range(tabs.count()) if tabs.isTabVisible(i)]


def _led_style(window: MainWindow, name: str) -> str:
    return getattr(window.ui, name).styleSheet()


# ---- construction -----------------------------------------------------------------------------


def test_the_window_constructs_on_the_simulated_bench_in_the_disconnected_state(window) -> None:
    ui = window.ui
    assert window.ctx.simulation is not None
    assert ui.cbArduinoPort.count() == 1
    assert ui.cbArduinoPort.itemText(0) == window.ctx.simulation.port
    assert ui.btnArduinoConnect.text() == _text(window, "button_connect")
    assert ui.lblArduinoStatusValue.text() == _text(window, "status_arduino_idle")
    assert _led_style(window, "ledArduinoStatus") == LED_RED
    for widget in (ui.gbSampleStage, ui.gbDetectorStage, ui.tabDetector):
        assert not widget.isEnabled()
    for button in (ui.btnStartMeasurement, ui.btnStopMeasurement, ui.btnResetMeasurement):
        assert not button.isEnabled()
    assert not ui.btnSave.isEnabled()
    assert ui.cbKDCDevice.count() == 1
    assert ui.cbKDCDevice.itemData(0) == KDC_ID
    assert ui.comboPM400.currentText() == PM400_RESOURCE
    assert ui.lblKDCStatusValue.text() == _text(window, "status_not_connected")
    assert ui.lblKDCPositionValue.text() == _text(window, "value_none")
    assert not ui.btnKDCHome.isEnabled()
    assert ui.btnKDCConnect.isEnabled()
    assert ui.cbPdtiaID.count() >= 1
    assert ui.cbGroupLetter.currentIndex() == -1


def test_the_experiment_tabs_are_locked_until_a_group_is_chosen(window) -> None:
    tabs = window.ui.tabWidget
    assert tabs.count() == 1 + len(window.tabs.tabs)
    assert "waveplate" not in {t.tab_id for t in window.tabs.tabs}  # needs the KDC101
    for i in range(1, tabs.count()):
        assert not tabs.isTabEnabled(i)
        assert tabs.tabToolTip(i) == _text(window, "tab_group_required")

    window.ui.cbGroupLetter.setCurrentIndex(0)
    for i in range(1, tabs.count()):
        assert tabs.isTabEnabled(i)
        assert tabs.tabToolTip(i) == ""

    window.ui.cbGroupLetter.setCurrentIndex(-1)
    assert not tabs.isTabEnabled(1)


def test_clearing_the_group_while_on_an_experiment_tab_returns_to_the_configuration(window) -> None:
    window.ui.cbGroupLetter.setCurrentIndex(0)
    window.ui.tabWidget.setCurrentIndex(1)
    window.ui.cbGroupLetter.setCurrentIndex(-1)
    assert window.ui.tabWidget.currentIndex() == 0


def test_the_inline_averaging_controls_start_from_the_config_defaults(window) -> None:
    acq = window.ctx.measurement.acq_settings
    assert window.ui.spbSampleAverages.value() == acq.samp_averages
    assert window.ui.cbDetectorAverageOn.isChecked() == acq.det_average_on
    assert window.ui.spbPdtiaAverages.isEnabledTo(window.ui.tabDetector) == acq.pdtia_average_on


def test_no_session_files_are_touched_without_persistence(
    qtbot, config, tmp_path, monkeypatch
) -> None:
    state_path = tmp_path / "last_session.json"
    monkeypatch.setattr(context_module, "SESSION_STATE_PATH", state_path)
    ModuleRegistry.clear()
    win = MainWindow(config, simulate=True, persist=False)
    qtbot.addWidget(win)
    win.show()
    win.ui.cbGroupLetter.setCurrentIndex(1)
    win.ui.leSuffix.setText("x")
    qtbot.wait(700)
    win.close()
    assert not state_path.exists()


# ---- connection and live displays -------------------------------------------------------------


def test_connecting_enables_the_stage_groups_and_streams_into_the_displays(
    qtbot, connected: MainWindow
) -> None:
    ui = connected.ui
    assert ui.btnArduinoConnect.text() == _text(connected, "button_disconnect")
    assert ui.lblArduinoStatusValue.text() == _text(connected, "status_connected")
    assert _led_style(connected, "ledArduinoStatus") == LED_GREEN
    assert _led_style(connected, "ledSampleStatus") == LED_GREEN
    for widget in (ui.gbSampleStage, ui.gbDetectorStage, ui.tabDetector):
        assert widget.isEnabled()
    assert ui.btnStartMeasurement.isEnabled()
    assert not ui.cbArduinoPort.isEnabled()
    assert not ui.btnRefreshPorts.isEnabled()

    qtbot.waitUntil(lambda: ui.lcdDetectorVoltage_mV.value() != 0.0, timeout=5000)
    qtbot.waitUntil(lambda: ui.lcdSampleAngle.value() != 0.0, timeout=5000)
    assert ui.lcdSampleAngle_2.value() == pytest.approx(ui.lcdSampleAngle.value(), abs=1.0)
    assert ui.lcdDetectorVoltage_2.value() == pytest.approx(ui.lcdDetectorVoltage_mV.value())
    assert connected.statusBar().currentMessage()


def test_the_pdtia_gain_is_active_after_connecting_and_shown_on_both_button_groups(
    connected,
) -> None:
    stage = connected.ctx.data.pdtia_gain
    assert 1 <= stage <= 4
    assert getattr(connected.ui, f"btnGain{stage}").isChecked()
    assert getattr(connected.ui, f"btnGain{stage}_2").isChecked()


def test_the_detector_row_asks_for_a_calibration_while_none_is_loaded(connected) -> None:
    assert connected.ctx.detector.calibration_profile is None
    connected.ctx.detector.update_calibration_status()
    assert connected.ui.lblDetectorStatusValue.text() == _text(
        connected, "status_select_calibration"
    )
    assert _led_style(connected, "ledDetectorStatus") == LED_YELLOW


def test_the_connect_button_disconnects_again_and_resets_the_panel(connected) -> None:
    ui = connected.ui
    ui.btnArduinoConnect.click()
    assert not connected.ctx.connection.is_connected
    assert ui.btnArduinoConnect.text() == _text(connected, "button_connect")
    assert ui.lblArduinoStatusValue.text() == _text(connected, "status_disconnected")
    assert _led_style(connected, "ledArduinoStatus") == LED_RED
    assert ui.lblSampleStatusValue.text() == _text(connected, "status_no_signal")
    assert not ui.gbSampleStage.isEnabled()
    assert not ui.btnStartMeasurement.isEnabled()
    assert ui.cbArduinoPort.isEnabled()
    assert ui.btnRefreshPorts.isEnabled()


def test_a_failing_connect_keeps_the_port_selection_usable(window) -> None:
    window.ui.cbArduinoPort.clear()
    window.ui.cbArduinoPort.addItem("/dev/does-not-exist")
    window.ui.btnArduinoConnect.click()
    assert not window.ctx.connection.is_connected
    assert _led_style(window, "ledArduinoStatus") == LED_RED
    assert window.ui.cbArduinoPort.isEnabled()
    assert window.ui.btnArduinoConnect.text() == _text(window, "button_connect")


def test_the_refresh_button_rescans_the_ports(window) -> None:
    window.ui.cbArduinoPort.clear()
    window.ui.btnRefreshPorts.click()
    assert window.ui.cbArduinoPort.count() == 1


def test_a_lost_link_resets_the_panel_and_offers_the_partial_export(
    qtbot, connected, monkeypatch
) -> None:
    asked: list[str] = []

    def fake_question(parent, title, text, *args):
        asked.append(title)
        return QMessageBox.StandardButton.No

    monkeypatch.setattr(QMessageBox, "question", staticmethod(fake_question))
    connected.ctx.measurement.start()
    journal = connected.ctx.data.current_journal
    assert journal is not None
    qtbot.waitUntil(lambda: journal.row_count > 0, timeout=5000)

    connected.ctx.simulation.arduino.kill_pty()
    qtbot.waitUntil(lambda: not connected.ctx.connection.is_connected, timeout=10000)

    assert asked == [connected.config.message("session.lost_title")]
    assert connected.ui.lblArduinoStatusValue.text() == _text(connected, "status_disconnected")
    assert not connected.ui.gbSampleStage.isEnabled()


# ---- encoder zeroing --------------------------------------------------------------------------


def test_the_zero_buttons_drive_the_encoders(connected, monkeypatch) -> None:
    ui = connected.ui
    ui.btnSampleZero.click()
    ui.btnDetectorStage180.click()
    assert connected.ctx.data.detector_offset_deg == 180.0
    ui.btnDetectorStageZero.click()
    assert connected.ctx.data.detector_offset_deg == 0.0


def test_a_failed_zeroing_shows_an_error_dialog(connected, monkeypatch) -> None:
    shown: list[tuple[str, str]] = []
    monkeypatch.setattr(
        mainwindow_module, "show_error", lambda parent, title, text: shown.append((title, text))
    )
    connected.ctx.connection.device_manager.zero_sample_encoder = lambda: False
    connected.ui.btnSampleZero.click()
    assert shown == [
        (
            connected.config.message("connection.zero_failed_title"),
            connected.config.message("connection.zero_sample_failed_text"),
        )
    ]


# ---- measurement ------------------------------------------------------------------------------


def test_start_stop_and_reset_drive_the_measurement_buttons(connected) -> None:
    ui = connected.ui
    ui.btnStartMeasurement.click()
    assert connected.ctx.measurement.is_measuring
    assert not ui.btnStartMeasurement.isEnabled()
    assert ui.btnStopMeasurement.isEnabled()
    assert not ui.btnResetMeasurement.isEnabled()
    assert not ui.btnSave.isEnabled()
    for button in (ui.btnSampleZero, ui.btnDetectorStageZero, ui.btnDetectorStage180):
        assert not button.isEnabled()
    assert not ui.tabWidget.tabBar().isEnabled()

    ui.btnStopMeasurement.click()
    assert not connected.ctx.measurement.is_measuring
    assert ui.btnStartMeasurement.isEnabled()
    assert not ui.btnStopMeasurement.isEnabled()
    assert ui.btnResetMeasurement.isEnabled()
    for button in (ui.btnSampleZero, ui.btnDetectorStageZero, ui.btnDetectorStage180):
        assert button.isEnabled()
    assert ui.tabWidget.tabBar().isEnabled()

    ui.btnResetMeasurement.click()
    assert not ui.btnResetMeasurement.isEnabled()


def test_the_tabs_hear_about_measurement_start_stop_and_reset(connected) -> None:
    events: list[str] = []
    tab = connected.tabs.tabs[0]
    tab.on_measurement_started = lambda: events.append("started")  # type: ignore[method-assign]
    tab.on_measurement_stopped = lambda: events.append("stopped")  # type: ignore[method-assign]
    tab.on_reset = lambda: events.append("reset")  # type: ignore[method-assign]

    connected.ui.btnStartMeasurement.click()
    connected.ui.btnStopMeasurement.click()
    connected.ui.btnResetMeasurement.click()

    assert events == ["started", "stopped", "reset"]


def test_the_tabs_hear_about_the_link_state(connected) -> None:
    states: list = []
    tab = connected.tabs.tabs[0]
    tab.on_connection_state = states.append  # type: ignore[method-assign]
    connected.ui.btnArduinoConnect.click()
    assert [s.value for s in states] == ["lost"]


def test_frames_reach_the_tabs(qtbot, connected) -> None:
    frames: list = []
    connected.tabs.tabs[0].on_frame = frames.append  # type: ignore[method-assign]
    qtbot.waitUntil(lambda: len(frames) >= 2, timeout=5000)


def test_the_stream_sources_follow_the_visible_tabs(connected) -> None:
    sources = connected.tabs.required_sources()
    assert {"ENC:BOTH", "ADC"} <= sources
    streamed = set(connected.ctx.simulation.arduino.get_state()["stream_sources"])
    assert {"ENC:A", "ENC:B", "ADC"} <= streamed  # the mock expands ENC:BOTH


# ---- group, filename, save --------------------------------------------------------------------


def test_the_filename_preview_follows_group_team_and_suffix(window) -> None:
    ui = window.ui
    assert ui.pteCurrentFilename.toPlainText() == ""
    ui.cbGroupLetter.setCurrentIndex(0)
    group = ui.cbGroupLetter.currentText()
    ui.leTeamName.setText("Team Rot")
    ui.leSuffix.setText("run1")
    text = ui.pteCurrentFilename.toPlainText()
    assert text.endswith(f"_{group}_run1.csv")
    assert "Team_Rot" in text
    ui.cbGroupLetter.setCurrentIndex(-1)
    assert ui.pteCurrentFilename.toPlainText() == ""


def test_typing_a_trailing_blank_in_the_team_name_is_not_swallowed(window) -> None:
    window.ui.leTeamName.setText("Team ")
    assert window.ui.leTeamName.text() == "Team "
    assert window.ctx.measurement.team_name == "Team"


def test_a_calibration_profile_adds_its_wavelength_to_the_filename_preview(
    window, tmp_path
) -> None:
    window.ui.cbGroupLetter.setCurrentIndex(0)
    path = tmp_path / "cal.json"
    PowerCalibrationProfile(name="cal", wavelength_nm=633.0).save(path)
    window.ctx.detector.select_profile(path)
    assert "633nm" in window.ui.pteCurrentFilename.toPlainText()


class _FakeTab:
    """A tab with one saved point and an export, standing in for a measurement tab."""

    def __init__(self) -> None:
        self.points = [object()]

    def get_saved_points(self) -> list:
        return self.points

    def build_export(self) -> TabExport:
        return TabExport(
            filename_hint="fake",
            columns=["a"],
            rows=[["1"], ["2"]],
            metadata={},
            filename_tokens=[],
        )


def test_saving_without_points_shows_the_no_points_error(window, monkeypatch) -> None:
    shown: list[str] = []
    monkeypatch.setattr(
        mainwindow_module, "show_error", lambda parent, title, text: shown.append(text)
    )
    window.ui.btnSave.setEnabled(True)
    window._save_data()
    assert shown == [window.config.message("save.no_points")]


def test_saving_exports_the_active_tab_and_locks_group_and_team(
    window, tmp_path, monkeypatch
) -> None:
    ui = window.ui
    ui.cbGroupLetter.setCurrentIndex(0)
    ui.leTeamName.setText("Team")
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    monkeypatch.setattr(window.tabs, "active_export_tab", lambda: _FakeTab())
    target = tmp_path / "saved.csv"
    proposals: list[str] = []

    def fake_dialog(parent, title, proposal, filters):
        proposals.append(proposal)
        return str(target), ""

    monkeypatch.setattr(QFileDialog, "getSaveFileName", staticmethod(fake_dialog))

    window._save_data()

    assert target.exists()
    assert proposals and proposals[0].startswith(str(tmp_path))
    assert proposals[0].endswith("messung_fake_A.csv")
    assert not ui.cbGroupLetter.isEnabled()
    assert not ui.leTeamName.isEnabled()
    assert str(target) in window.statusBar().currentMessage()


def test_cancelling_the_save_dialog_writes_nothing_and_keeps_the_prefix_editable(
    window, tmp_path, monkeypatch
) -> None:
    window.ui.cbGroupLetter.setCurrentIndex(0)
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    monkeypatch.setattr(window.tabs, "active_export_tab", lambda: _FakeTab())
    monkeypatch.setattr(QFileDialog, "getSaveFileName", staticmethod(lambda *a: ("", "")))
    window._save_data()
    assert window.ui.cbGroupLetter.isEnabled()


# ---- gain, auto gain, dark tare ---------------------------------------------------------------


def test_clicking_a_gain_button_sets_the_stage_and_checks_both_groups(connected) -> None:
    ui = connected.ui
    ui.btnGain3.click()
    assert connected.ctx.data.pdtia_gain == 3
    assert ui.btnGain3.isChecked() and ui.btnGain3_2.isChecked()
    ui.btnGain2_2.click()
    assert connected.ctx.data.pdtia_gain == 2
    assert ui.btnGain2.isChecked() and ui.btnGain2_2.isChecked()


def test_the_auto_gain_buttons_mirror_each_other_and_a_manual_click_turns_it_off(connected) -> None:
    ui = connected.ui
    ui.btnGainA.setChecked(True)
    assert ui.btnGainA_2.isChecked()
    assert connected.ctx.detector.gain_auto_enabled
    ui.btnGain4.click()
    assert not ui.btnGainA.isChecked()
    assert not ui.btnGainA_2.isChecked()
    assert not connected.ctx.detector.gain_auto_enabled


def test_the_dark_tare_asks_first_and_shows_the_measured_offset(
    qtbot, connected, monkeypatch
) -> None:
    ui = connected.ui
    monkeypatch.setattr(
        QMessageBox,
        "question",
        staticmethod(lambda *a, **k: QMessageBox.StandardButton.Cancel),
    )
    ui.btnDarkTare.click()
    assert ui.btnDarkTare.isEnabled()

    monkeypatch.setattr(
        QMessageBox, "question", staticmethod(lambda *a, **k: QMessageBox.StandardButton.Yes)
    )
    ui.btnDarkTare.click()
    assert not ui.btnDarkTare.isEnabled()
    assert not ui.btnDarkReset.isEnabled()
    qtbot.waitUntil(lambda: ui.btnDarkTare.isEnabled(), timeout=10000)
    assert ui.lblDarkOffsetValue.text().endswith(" mV")

    ui.btnDarkReset.click()
    assert ui.lblDarkOffsetValue.text() == _text(connected, "dark_offset_none")


def test_selecting_a_profile_in_the_combo_loads_it(window, tmp_path) -> None:
    path = tmp_path / "cal-x.json"
    PowerCalibrationProfile(name="cal-x").save(path)
    window.ctx.detector._profiles_dir = tmp_path
    window._reload_profiles()
    assert window.ui.cbProfile.count() == 1
    assert window.ctx.detector.profile_name == ""  # the selector shows its placeholder
    window.ui.cbProfile.setCurrentIndex(0)
    assert window.ctx.detector.profile_name == "cal-x"
    assert window.ctx.detector.calibration_profile is not None

    window._reload_profiles()  # a reload keeps the selection
    assert window.ui.cbProfile.currentText() == "cal-x"
    assert window.ctx.detector.profile_name == "cal-x"


def test_the_pdtia_id_selector_feeds_the_detector_controller(window) -> None:
    combo = window.ui.cbPdtiaID
    combo.setCurrentIndex(combo.count() - 1)
    assert window.ctx.detector.pdtia_id == combo.currentText()


# ---- inline acquisition settings --------------------------------------------------------------


def test_inline_averaging_edits_reach_the_data_controller(window) -> None:
    window.ui.spbSampleAverages.setValue(9)
    window.ui.cbDetectorAverageOn.setChecked(False)
    acq = window.ctx.measurement.acq_settings
    assert acq.samp_averages == 9
    assert not acq.det_average_on
    assert not window.ui.spbDetectorAverages.isEnabled()
    assert window.ctx.data._sample_buffer.maxlen == 9


def test_the_acquisition_dialog_result_updates_the_inline_controls(window, monkeypatch) -> None:
    new = replace(
        window.ctx.measurement.acq_settings,
        samp_averages=13,
        samp_average_on=True,
        spike_filter_enabled=False,
    )

    class FakeDialog:
        def __init__(self, settings, parent=None, config=None) -> None:
            self.settings = settings

        def setAttribute(self, *args) -> None:
            pass

        def exec(self) -> int:
            return QDialog.DialogCode.Accepted

        def get_settings(self) -> AcquisitionSettings:
            return new

    monkeypatch.setattr(mainwindow_module, "AcquisitionSettingsDialog", FakeDialog)
    window.ui.actionAcquisitionSettings.trigger()
    assert window.ui.spbSampleAverages.value() == 13
    assert not window.ctx.measurement.acq_settings.spike_filter_enabled
    assert window.ctx.data._sample_buffer.maxlen == 13


def test_a_rejected_acquisition_dialog_changes_nothing(window, monkeypatch) -> None:
    before = window.ctx.measurement.acq_settings

    class FakeDialog:
        def __init__(self, *args, **kwargs) -> None:
            pass

        def setAttribute(self, *args) -> None:
            pass

        def exec(self) -> int:
            return QDialog.DialogCode.Rejected

    monkeypatch.setattr(mainwindow_module, "AcquisitionSettingsDialog", FakeDialog)
    window.ui.actionAcquisitionSettings.trigger()
    assert window.ctx.measurement.acq_settings == before


# ---- KDC101 -----------------------------------------------------------------------------------


def test_connecting_the_kdc_adds_the_waveplate_tab_and_shows_the_position(qtbot, window) -> None:
    ui = window.ui
    before = _tab_titles(window)
    ui.btnKDCConnect.click()

    assert window.ctx.kdc.is_connected
    assert ui.btnKDCConnect.text() == _text(window, "button_disconnect")
    assert ui.lblKDCStatusValue.text() == _text(window, "status_connected_named", id=KDC_ID)
    assert ui.btnKDCHome.isEnabled() and ui.btnKDCZero.isEnabled()
    assert ui.btnKDCOffsetReset.isEnabled()
    assert len(_tab_titles(window)) == len(before) + 1
    waveplate = next(t for t in window.tabs.tabs if t.tab_id == "waveplate")
    assert not ui.tabWidget.isTabEnabled(ui.tabWidget.indexOf(waveplate))  # group gate applies

    window.ctx.kdc.kdc.move_to(30.0)
    window.ctx.kdc.poll_position()
    assert ui.lblKDCPositionValue.text().endswith("°")
    assert "30" in ui.lblKDCPositionValue.text()

    ui.btnKDCConnect.click()
    assert not window.ctx.kdc.is_connected
    assert _tab_titles(window) == before
    assert ui.btnKDCConnect.text() == _text(window, "button_connect")
    assert ui.lblKDCPositionValue.text() == _text(window, "value_none")
    assert not ui.btnKDCHome.isEnabled()


def test_the_kdc_buttons_home_and_reset_the_offset(qtbot, window) -> None:
    ui = window.ui
    ui.btnKDCConnect.click()
    window.ctx.kdc.set_zero_offset(25.0)
    assert ui.lblKDCOffsetValue.text().startswith("25")
    ui.btnKDCOffsetReset.click()
    assert ui.lblKDCOffsetValue.text() == _text(window, "value_none")

    ui.btnKDCHome.click()
    assert not ui.btnKDCHome.isEnabled()
    assert not ui.btnKDCConnect.isEnabled()
    qtbot.waitUntil(lambda: ui.btnKDCHome.isEnabled(), timeout=3000)
    assert ui.btnKDCConnect.isEnabled()


def test_connecting_the_kdc_without_a_device_warns(window, monkeypatch) -> None:
    warned: list[tuple[str, str]] = []
    monkeypatch.setattr(
        QMessageBox,
        "warning",
        staticmethod(lambda parent, title, text: warned.append((title, text))),
    )
    window.ui.cbKDCDevice.clear()
    window.ui.cbKDCDevice.addItem(_text(window, "kdc_none_found"))
    window.ui.btnKDCConnect.click()
    assert warned == [(window.config.message("kdc.title"), window.config.message("kdc.no_device"))]
    assert not window.ctx.kdc.is_connected


# ---- PM400 ------------------------------------------------------------------------------------


def test_connecting_the_pm400_makes_it_the_active_detector_in_the_panel(qtbot, connected) -> None:
    ui = connected.ui
    ui.btnConnectPM400.click()
    assert connected.ctx.pm400.is_connected
    assert ui.btnConnectPM400.text() == _text(connected, "button_disconnect")
    assert ui.btnZeroPM400.isEnabled()
    assert _led_style(connected, "ledPM400Status") == LED_GREEN
    assert "S120C" in ui.lblPM400Status.text()
    qtbot.waitUntil(lambda: not ui.btnGain1.isEnabled(), timeout=3000)
    for stage in (1, 2, 3, 4):
        assert not getattr(ui, f"btnGain{stage}_2").isEnabled()
    assert not ui.btnGainA.isEnabled()
    assert not ui.lcdDetectorPower_2.isEnabled()
    qtbot.waitUntil(lambda: ui.lcdDetectorPower.value() != 0.0, timeout=5000)

    ui.btnConnectPM400.click()
    assert not connected.ctx.pm400.is_connected
    qtbot.waitUntil(lambda: ui.btnGain1.isEnabled(), timeout=3000)
    assert ui.lcdDetectorPower_2.isEnabled()
    assert ui.btnConnectPM400.text() == _text(connected, "button_connect")
    assert not ui.btnZeroPM400.isEnabled()
    assert _led_style(connected, "ledPM400Status") == LED_RED


def test_the_wavelength_spin_box_drives_the_pm400_controller(window) -> None:
    window.ui.spbPM400Wavelength.setValue(532.0)
    assert window.ctx.pm400.wavelength_nm == 532.0


def test_connecting_the_pm400_without_a_resource_warns(connected, monkeypatch) -> None:
    window = connected
    warned: list[str] = []
    monkeypatch.setattr(
        QMessageBox, "warning", staticmethod(lambda parent, title, text: warned.append(text))
    )
    window.ui.comboPM400.clear()
    window.ui.btnConnectPM400.click()
    assert warned == [window.config.message("pm400.no_resource")]


# ---- auxiliary windows ------------------------------------------------------------------------


def _close_children(window: MainWindow, cls: type) -> None:
    for child in window.findChildren(cls):
        child.close()


def test_the_encoder_debug_dialog_receives_the_shared_devices(window, monkeypatch) -> None:
    from polarisation_ui.ui.windows.encoder_debug_window import EncoderDebugDialog

    seen: dict = {}
    real_init = EncoderDebugDialog.__init__

    def spy(self, *args, **kwargs):
        seen["args"], seen["kwargs"] = args, kwargs
        real_init(self, *args, **kwargs)

    monkeypatch.setattr(EncoderDebugDialog, "__init__", spy)
    window.ui.actionEncoderDebug.trigger()

    assert seen["args"] == (window.ctx.connection.device_manager,)
    assert seen["kwargs"]["pm400"] is window.ctx.pm400.pm400
    assert seen["kwargs"]["data_controller"] is window.ctx.data
    assert seen["kwargs"]["config"] is window.config
    dialogs = window.findChildren(EncoderDebugDialog)
    assert len(dialogs) == 1 and dialogs[0].isVisible()
    _close_children(window, EncoderDebugDialog)


def test_the_power_calibration_windows_open_and_reload_the_profiles_when_saved(
    window, tmp_path
) -> None:
    from polarisation_ui.ui.windows.auto_power_calibration_window import (
        AutoPowerCalibrationWindow,
    )
    from polarisation_ui.ui.windows.power_calibration_window import PowerCalibrationWindow

    window.ui.actionPowerCalibration.trigger()
    window.ui.actionAutoPowerCalibration.trigger()
    manual = window.findChildren(PowerCalibrationWindow)
    auto = window.findChildren(AutoPowerCalibrationWindow)
    assert len(manual) == 1 and manual[0].isVisible()
    assert len(auto) == 1 and auto[0].isVisible()

    window.ctx.detector._profiles_dir = tmp_path
    PowerCalibrationProfile(name="fresh").save(tmp_path / "fresh.json")
    manual[0].profile_saved.emit()
    assert window.ui.cbProfile.findText("fresh") >= 0

    _close_children(window, PowerCalibrationWindow)
    _close_children(window, AutoPowerCalibrationWindow)


def test_the_calibration_button_in_the_detector_tab_opens_the_power_calibration(connected) -> None:
    window = connected
    from polarisation_ui.ui.windows.power_calibration_window import PowerCalibrationWindow

    window.ui.btnOpenCalibration.click()
    assert len(window.findChildren(PowerCalibrationWindow)) == 1
    _close_children(window, PowerCalibrationWindow)


def test_the_log_window_is_created_once_and_reused(window) -> None:
    from polarisation_ui.ui.windows.log_window import LogWindow

    window.ui.actionLogWindow.trigger()
    window.ui.actionLogWindow.trigger()
    assert len(window.findChildren(LogWindow)) == 1
    _close_children(window, LogWindow)


def test_the_event_log_dock_follows_its_action(window) -> None:
    window.ui.actionEventLog.setChecked(False)
    assert not window.ui.dockEventLog.isVisible()
    window.ui.actionEventLog.setChecked(True)
    assert window.ui.dockEventLog.isVisible()


# ---- close ------------------------------------------------------------------------------------


def test_closing_stops_the_measurement_the_polling_and_every_device(qtbot, connected) -> None:
    ctx = connected.ctx
    ctx.kdc.connect_device(KDC_ID)
    ctx.pm400.connect_resource(PM400_RESOURCE)
    ctx.measurement.start()
    arduino = ctx.simulation.arduino

    connected.close()

    assert not ctx.measurement.is_measuring
    assert not ctx.data.is_reading()
    assert not ctx.connection.device_manager.is_encoder_connected()
    assert not ctx.kdc.is_connected
    assert not ctx.pm400.is_connected
    assert not ctx.kdc._position_timer.isActive()
    assert ctx.data._pm400_worker is None
    assert ModuleRegistry.all() == {}
    assert not arduino._running


def test_closing_a_window_that_never_connected_is_clean(window) -> None:
    window.close()
    assert not window.ctx.data.is_reading()


# ---- start-up checks (persistence on) ---------------------------------------------------------


@pytest.fixture
def persistent_env(tmp_path, monkeypatch):
    state = tmp_path / "state" / "last_session.json"
    journals = tmp_path / "journals"
    monkeypatch.setattr(context_module, "SESSION_STATE_PATH", state)
    monkeypatch.setattr(session_journal, "JOURNAL_BASE", journals)
    ModuleRegistry.clear()
    yield SimpleNamespace(state=state, journals=journals, home=tmp_path)
    ModuleRegistry.clear()


def _orphan(base: Path, name: str) -> Path:
    session_dir = base / name
    session_dir.mkdir(parents=True)
    (session_dir / "journal.csv").write_text(
        "ts_ms,sample_angle,detector_angle,intensity,gap\n1,1.0,2.0,0.5,\n", encoding="utf-8"
    )
    return session_dir


def _open(qtbot, config) -> MainWindow:
    win = MainWindow(config, simulate=True, persist=True)
    qtbot.addWidget(win)
    win.show()
    return win


def test_dismissed_orphans_are_deleted_and_a_matching_session_is_restored(
    qtbot, config, persistent_env, monkeypatch
) -> None:
    orphan = _orphan(persistent_env.journals, "20260101T000000_000001")
    now = datetime.now()
    save_session_state(
        SessionState(
            saved_date=now.date().isoformat(),
            saved_at=now.isoformat(),
            group_letter="C",
            team_name="Team Gruen",
            suffix="again",
        ),
        persistent_env.state,
    )
    answers = {
        config.message("session.orphans_title"): QMessageBox.StandardButton.No,
        config.message("session.restore_title"): QMessageBox.StandardButton.Yes,
    }
    asked: list[str] = []

    def fake_question(parent, title, text, *args):
        asked.append(title)
        return answers[title]

    monkeypatch.setattr(QMessageBox, "question", staticmethod(fake_question))
    win = _open(qtbot, config)

    qtbot.waitUntil(lambda: win.ctx.measurement.group_letter == "C", timeout=3000)
    assert asked == [
        config.message("session.orphans_title"),
        config.message("session.restore_title"),
    ]
    assert not orphan.exists()
    assert win.ui.cbGroupLetter.currentText() == "C"
    assert win.ui.leTeamName.text() == "Team Gruen"
    assert win.ui.leSuffix.text() == "again"
    assert win.ui.tabWidget.isTabEnabled(1)
    win.close()


def test_accepted_orphans_are_exported_and_a_declined_restore_keeps_the_state_idle(
    qtbot, config, persistent_env, monkeypatch
) -> None:
    orphan = _orphan(persistent_env.journals, "20260101T000000_000001")
    target = persistent_env.home / "recovered.csv"
    monkeypatch.setattr(
        QMessageBox, "question", staticmethod(lambda *a, **k: QMessageBox.StandardButton.Yes)
    )
    monkeypatch.setattr(
        QFileDialog, "getSaveFileName", staticmethod(lambda *a, **k: (str(target), ""))
    )
    win = _open(qtbot, config)

    qtbot.waitUntil(target.exists, timeout=3000)
    assert (orphan / "finalized").exists()
    assert win.ctx.measurement.group_letter == ""
    win.close()


def test_changes_are_persisted_after_the_start_up_checks(qtbot, config, persistent_env) -> None:
    win = _open(qtbot, config)
    qtbot.waitUntil(lambda: win.ctx.session._armed, timeout=3000)
    win.ui.cbGroupLetter.setCurrentIndex(2)
    qtbot.waitUntil(persistent_env.state.exists, timeout=3000)
    win.close()
    assert win.ctx.measurement.group_letter in persistent_env.state.read_text(encoding="utf-8")


# ---- source rules -----------------------------------------------------------------------------

GERMAN_CHARS = re.compile(r"[äöüÄÖÜß]")
GERMAN_WORDS = re.compile(
    r"\b(Verbinden|Verbunden|Trennen|Getrennt|Nicht|Bitte|Fehler|Messung|Keine?|Gerät|Sitzung)\b"
)
CHECKED_SOURCES = [
    UI_DIR / "windows" / "mainwindow.py",
    UI_DIR / "context.py",
    UI_DIR / "widgets" / "tab_host.py",
    *sorted((UI_DIR / "controllers").glob("*.py")),
]


def _string_literals(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    docstrings: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = node.body
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
                docstrings.add(id(body[0].value))
    return [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and id(node) not in docstrings
    ]


@pytest.mark.parametrize("path", CHECKED_SOURCES, ids=lambda p: p.name)
def test_no_german_string_literal_is_left_in_the_window_and_the_controllers(path: Path) -> None:
    for literal in _string_literals(path):
        assert not GERMAN_CHARS.search(literal), f"{path.name}: {literal!r}"
        assert not GERMAN_WORDS.search(literal), f"{path.name}: {literal!r}"


@pytest.mark.parametrize("path", CHECKED_SOURCES, ids=lambda p: p.name)
def test_the_window_and_the_controllers_read_the_injected_config_not_the_global(
    path: Path,
) -> None:
    source = path.read_text(encoding="utf-8")
    assert "import_config" not in source
    assert not re.search(r"^CONFIG\b", source, re.MULTILINE)


def test_data_controller_has_no_german_literal_left() -> None:
    path = UI_DIR / "controllers" / "data_controller.py"
    for literal in _string_literals(path):
        assert not GERMAN_CHARS.search(literal), literal


def test_the_main_window_stays_thin() -> None:
    lines = (UI_DIR / "windows" / "mainwindow.py").read_text(encoding="utf-8").count("\n")
    assert lines < 1000


def test_controllers_never_import_widgets() -> None:
    forbidden = ("PySide6.QtWidgets", "PySide6.QtGui", "polarisation_ui.pyqt", "ui.widgets")
    for path in sorted((UI_DIR / "controllers").glob("*.py")):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            module = ""
            if isinstance(node, ast.ImportFrom) and node.module:
                module = node.module
            elif isinstance(node, ast.Import):
                module = node.names[0].name
            assert not any(module.startswith(f) or f in module for f in forbidden), (
                f"{path.name} imports {module}"
            )
