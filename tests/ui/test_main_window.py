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
from PySide6.QtCore import QObject
from PySide6.QtWidgets import (
    QAbstractButton,
    QDialog,
    QFileDialog,
    QGroupBox,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
)

from polarisation_ui.core.models import AcquisitionSettings, TabExport
from polarisation_ui.core.power_calibration import PowerCalibrationProfile
from polarisation_ui.infrastructure import session_journal
from polarisation_ui.infrastructure.config import load_config
from polarisation_ui.infrastructure.modules import ModuleRegistry
from polarisation_ui.infrastructure.session_state import SessionState, save_session_state
from polarisation_ui.ui import context as context_module
from polarisation_ui.ui.common.status_led import LED_GREEN, LED_RED, LED_YELLOW
from polarisation_ui.ui.windows import auxiliary_windows as auxiliary_windows_module
from polarisation_ui.ui.windows import main_window as main_window_module
from polarisation_ui.ui.windows.main_window import MainWindow

pytestmark = pytest.mark.skipif(sys.platform == "win32", reason="PTY not available on Windows")

UI_DIR = Path(__file__).resolve().parents[2] / "polarisation_ui" / "ui"
KDC_ID = "mock://kdc101"
PM400_RESOURCE = "USB0::0x1313::0x8078::MOCK00001::INSTR"


def _text(window: MainWindow, key: str, **fmt: object) -> str:
    """A configured text by its path below ``ui`` (e.g. ``main_window.status_connected``)."""
    return window.config.text(key, **fmt)


def _tab_titles(window: MainWindow) -> list[str]:
    tabs = window.ui.tabWidget
    return [tabs.tabText(i) for i in range(tabs.count()) if tabs.isTabVisible(i)]


def _led_style(led: QLabel) -> str:
    return led.styleSheet()


# ---- construction -----------------------------------------------------------------------------


def test_the_window_constructs_on_the_simulated_bench_in_the_disconnected_state(window) -> None:
    ui = window.ui
    assert window.ctx.simulation is not None
    assert ui.arduinoPanel.ui.comboPort.count() == 1
    assert ui.arduinoPanel.ui.comboPort.itemText(0) == window.ctx.simulation.port
    assert ui.arduinoPanel.ui.buttonConnect.text() == _text(window, "arduino_panel.text_connect")
    assert ui.arduinoPanel.ui.valueStatus.text() == _text(window, "main_window.status_arduino_idle")
    assert _led_style(window.ui.arduinoPanel.ui.ledStatus) == LED_RED
    for widget in (ui.sampleStagePanel, ui.detectorStagePanel, ui.detectorPanel):
        assert not widget.isEnabled()
    for button in (
        ui.measurementPanel.ui.buttonStart,
        ui.measurementPanel.ui.buttonStop,
        ui.measurementPanel.ui.buttonReset,
    ):
        assert not button.isEnabled()
    assert not ui.savePanel.ui.buttonSave.isEnabled()
    assert ui.kdcPanel.ui.comboDevice.count() == 1
    assert ui.kdcPanel.ui.comboDevice.itemData(0) == KDC_ID
    assert ui.detectorPanel.ui.comboPm400Resource.currentText() == PM400_RESOURCE
    assert ui.kdcPanel.ui.valueStatus.text() == _text(window, "main_window.status_not_connected")
    assert ui.kdcPanel.ui.valuePosition.text() == _text(window, "kdc_panel.text_none")
    assert not ui.kdcPanel.ui.buttonHome.isEnabled()
    assert ui.kdcPanel.ui.buttonConnect.isEnabled()
    assert ui.detectorPanel.ui.comboPdtiaId.count() >= 1
    assert ui.savePanel.ui.comboGroup.currentIndex() == -1


def test_the_experiment_tabs_are_locked_until_a_group_is_chosen(window) -> None:
    tabs = window.ui.tabWidget
    assert tabs.count() == len(window.tabs.tabs) > 0
    assert "waveplate" not in {t.tab_id for t in window.tabs.tabs}  # needs the KDC101
    for i in range(tabs.count()):
        assert not tabs.isTabEnabled(i)
        assert tabs.tabToolTip(i) == _text(window, "main_window.tab_group_required")

    window.ui.savePanel.ui.comboGroup.setCurrentIndex(0)
    for i in range(tabs.count()):
        assert tabs.isTabEnabled(i)
        assert tabs.tabToolTip(i) == ""

    window.ui.savePanel.ui.comboGroup.setCurrentIndex(-1)
    assert not tabs.isTabEnabled(0)


def test_clearing_the_group_while_on_an_experiment_tab_locks_it_in_place(window) -> None:
    window.ui.savePanel.ui.comboGroup.setCurrentIndex(0)
    window.ui.tabWidget.setCurrentIndex(1)
    window.ui.savePanel.ui.comboGroup.setCurrentIndex(-1)
    assert window.ui.tabWidget.currentIndex() == 1
    assert not window.ui.tabWidget.isTabEnabled(1)


def test_the_inline_averaging_controls_start_from_the_config_defaults(window) -> None:
    acq = window.ctx.measurement.acq_settings
    assert window.ui.sampleStagePanel.ui.spinAverages.value() == acq.samp_averages
    assert window.ui.detectorStagePanel.ui.checkAverage.isChecked() == acq.det_average_on
    assert (
        window.ui.detectorPanel.ui.spinPdtiaAverages.isEnabledTo(window.ui.detectorPanel)
        == acq.pdtia_average_on
    )


def test_no_session_files_are_touched_without_persistence(
    qtbot, config, tmp_path, monkeypatch
) -> None:
    state_path = tmp_path / "last_session.json"
    monkeypatch.setattr(context_module, "SESSION_STATE_PATH", state_path)
    ModuleRegistry.clear()
    win = MainWindow(config, simulate=True, persist=False)
    qtbot.addWidget(win)
    win.show()
    win.ui.savePanel.ui.comboGroup.setCurrentIndex(1)
    win.ui.savePanel.ui.editSuffix.setText("x")
    qtbot.wait(700)
    win.close()
    assert not state_path.exists()


# ---- connection and live displays -------------------------------------------------------------


def test_connecting_enables_the_stage_groups_and_streams_into_the_displays(
    qtbot, connected: MainWindow
) -> None:
    ui = connected.ui
    assert ui.arduinoPanel.ui.buttonConnect.text() == _text(
        connected, "arduino_panel.text_disconnect"
    )
    assert ui.arduinoPanel.ui.valueStatus.text() == _text(connected, "main_window.status_connected")
    assert _led_style(connected.ui.arduinoPanel.ui.ledStatus) == LED_GREEN
    assert _led_style(connected.ui.sampleStagePanel.ui.ledStatus) == LED_GREEN
    for widget in (ui.sampleStagePanel, ui.detectorStagePanel, ui.detectorPanel):
        assert widget.isEnabled()
    assert ui.measurementPanel.ui.buttonStart.isEnabled()
    assert not ui.arduinoPanel.ui.comboPort.isEnabled()
    assert not ui.arduinoPanel.ui.buttonRefreshPorts.isEnabled()

    qtbot.waitUntil(lambda: ui.readoutPanel.ui.lcdVoltage.value() != 0.0, timeout=5000)
    qtbot.waitUntil(lambda: ui.readoutPanel.ui.lcdSampleAngle.value() != 0.0, timeout=5000)
    assert connected.statusBar().currentMessage()


def test_the_pdtia_gain_is_active_after_connecting_and_shown_on_the_gain_buttons(
    connected,
) -> None:
    stage = connected.ctx.data.pdtia_gain
    assert 1 <= stage <= 4
    assert getattr(connected.ui.readoutPanel.ui, f"buttonGain{stage}").isChecked()


def test_the_detector_row_asks_for_a_calibration_while_none_is_loaded(connected) -> None:
    assert connected.ctx.detector.calibration_profile is None
    connected.ctx.detector.update_calibration_status()
    assert connected.ui.detectorPanel.ui.valuePdtiaStatus.text() == _text(
        connected, "main_window.status_select_calibration"
    )
    assert _led_style(connected.ui.detectorPanel.ui.ledPdtiaStatus) == LED_YELLOW


def test_the_connect_button_disconnects_again_and_resets_the_panel(connected) -> None:
    ui = connected.ui
    ui.arduinoPanel.ui.buttonConnect.click()
    assert not connected.ctx.connection.is_connected
    assert ui.arduinoPanel.ui.buttonConnect.text() == _text(connected, "arduino_panel.text_connect")
    assert ui.arduinoPanel.ui.valueStatus.text() == _text(
        connected, "main_window.status_disconnected"
    )
    assert _led_style(connected.ui.arduinoPanel.ui.ledStatus) == LED_RED
    assert ui.sampleStagePanel.ui.valueStatus.text() == _text(
        connected, "main_window.status_no_signal"
    )
    assert not ui.sampleStagePanel.isEnabled()
    assert not ui.measurementPanel.ui.buttonStart.isEnabled()
    assert ui.arduinoPanel.ui.comboPort.isEnabled()
    assert ui.arduinoPanel.ui.buttonRefreshPorts.isEnabled()


def test_a_failing_connect_keeps_the_port_selection_usable(window) -> None:
    window.ui.arduinoPanel.ui.comboPort.clear()
    window.ui.arduinoPanel.ui.comboPort.addItem("/dev/does-not-exist")
    window.ui.arduinoPanel.ui.buttonConnect.click()
    assert not window.ctx.connection.is_connected
    assert _led_style(window.ui.arduinoPanel.ui.ledStatus) == LED_RED
    assert window.ui.arduinoPanel.ui.comboPort.isEnabled()
    assert window.ui.arduinoPanel.ui.buttonConnect.text() == _text(
        window, "arduino_panel.text_connect"
    )


def test_the_refresh_button_rescans_the_ports(window) -> None:
    window.ui.arduinoPanel.ui.comboPort.clear()
    window.ui.arduinoPanel.ui.buttonRefreshPorts.click()
    assert window.ui.arduinoPanel.ui.comboPort.count() == 1


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
    assert connected.ui.arduinoPanel.ui.valueStatus.text() == _text(
        connected, "main_window.status_disconnected"
    )
    assert not connected.ui.sampleStagePanel.isEnabled()


# ---- encoder zeroing --------------------------------------------------------------------------


def test_the_zero_buttons_drive_the_encoders(connected, monkeypatch) -> None:
    ui = connected.ui
    ui.sampleStagePanel.ui.buttonZero.click()
    ui.detectorStagePanel.ui.button180.click()
    assert connected.ctx.data.detector_offset_deg == 180.0
    ui.detectorStagePanel.ui.buttonZero.click()
    assert connected.ctx.data.detector_offset_deg == 0.0


def test_a_failed_zeroing_shows_an_error_dialog(connected, monkeypatch) -> None:
    shown: list[tuple[str, str]] = []
    monkeypatch.setattr(
        main_window_module, "show_error", lambda parent, title, text: shown.append((title, text))
    )
    connected.ctx.connection.device_manager.zero_sample_encoder = lambda: False
    connected.ui.sampleStagePanel.ui.buttonZero.click()
    assert shown == [
        (
            connected.config.message("connection.zero_failed_title"),
            connected.config.message("connection.zero_sample_failed_text"),
        )
    ]


# ---- measurement ------------------------------------------------------------------------------


def test_start_stop_and_reset_drive_the_measurement_buttons(connected) -> None:
    ui = connected.ui
    ui.measurementPanel.ui.buttonStart.click()
    assert connected.ctx.measurement.is_measuring
    assert not ui.measurementPanel.ui.buttonStart.isEnabled()
    assert ui.measurementPanel.ui.buttonStop.isEnabled()
    assert not ui.measurementPanel.ui.buttonReset.isEnabled()
    assert not ui.savePanel.ui.buttonSave.isEnabled()
    for button in (
        ui.sampleStagePanel.ui.buttonZero,
        ui.detectorStagePanel.ui.buttonZero,
        ui.detectorStagePanel.ui.button180,
    ):
        assert not button.isEnabled()
    assert not ui.tabWidget.tabBar().isEnabled()

    ui.measurementPanel.ui.buttonStop.click()
    assert not connected.ctx.measurement.is_measuring
    assert ui.measurementPanel.ui.buttonStart.isEnabled()
    assert not ui.measurementPanel.ui.buttonStop.isEnabled()
    assert ui.measurementPanel.ui.buttonReset.isEnabled()
    for button in (
        ui.sampleStagePanel.ui.buttonZero,
        ui.detectorStagePanel.ui.buttonZero,
        ui.detectorStagePanel.ui.button180,
    ):
        assert button.isEnabled()
    assert ui.tabWidget.tabBar().isEnabled()

    ui.measurementPanel.ui.buttonReset.click()
    assert not ui.measurementPanel.ui.buttonReset.isEnabled()


def test_the_tabs_hear_about_measurement_start_stop_and_reset(connected) -> None:
    events: list[str] = []
    tab = connected.tabs.tabs[0]
    tab.on_measurement_started = lambda: events.append("started")  # type: ignore[method-assign]
    tab.on_measurement_stopped = lambda: events.append("stopped")  # type: ignore[method-assign]
    tab.on_reset = lambda: events.append("reset")  # type: ignore[method-assign]

    connected.ui.measurementPanel.ui.buttonStart.click()
    connected.ui.measurementPanel.ui.buttonStop.click()
    connected.ui.measurementPanel.ui.buttonReset.click()

    assert events == ["started", "stopped", "reset"]


def test_the_tabs_hear_about_the_link_state(connected) -> None:
    states: list = []
    tab = connected.tabs.tabs[0]
    tab.on_connection_state = states.append  # type: ignore[method-assign]
    connected.ui.arduinoPanel.ui.buttonConnect.click()
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
    assert ui.savePanel.ui.valueFilename.text() == ""
    ui.savePanel.ui.comboGroup.setCurrentIndex(0)
    group = ui.savePanel.ui.comboGroup.currentText()
    ui.savePanel.ui.editTeam.setText("Team Rot")
    ui.savePanel.ui.editSuffix.setText("run1")
    text = ui.savePanel.ui.valueFilename.text()
    assert text.endswith(f"_{group}_run1.csv")
    assert "Team_Rot" in text
    ui.savePanel.ui.comboGroup.setCurrentIndex(-1)
    assert ui.savePanel.ui.valueFilename.text() == ""


def test_typing_a_trailing_blank_in_the_team_name_is_not_swallowed(window) -> None:
    window.ui.savePanel.ui.editTeam.setText("Team ")
    assert window.ui.savePanel.ui.editTeam.text() == "Team "
    assert window.ctx.measurement.team_name == "Team"


def test_a_calibration_profile_adds_its_wavelength_to_the_filename_preview(
    window, tmp_path
) -> None:
    window.ui.savePanel.ui.comboGroup.setCurrentIndex(0)
    path = tmp_path / "cal.json"
    PowerCalibrationProfile(name="cal", wavelength_nm=633.0).save(path)
    window.ctx.detector.select_profile(path)
    assert "633nm" in window.ui.savePanel.ui.valueFilename.text()


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
        main_window_module, "show_error", lambda parent, title, text: shown.append(text)
    )
    window.ui.savePanel.ui.buttonSave.setEnabled(True)
    window._save_data()
    assert shown == [window.config.message("save.no_points")]


def test_saving_exports_the_active_tab_and_locks_group_and_team(
    window, tmp_path, monkeypatch
) -> None:
    ui = window.ui
    ui.savePanel.ui.comboGroup.setCurrentIndex(0)
    ui.savePanel.ui.editTeam.setText("Team")
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
    assert not ui.savePanel.ui.comboGroup.isEnabled()
    assert not ui.savePanel.ui.editTeam.isEnabled()
    assert str(target) in window.statusBar().currentMessage()


def test_cancelling_the_save_dialog_writes_nothing_and_keeps_the_prefix_editable(
    window, tmp_path, monkeypatch
) -> None:
    window.ui.savePanel.ui.comboGroup.setCurrentIndex(0)
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    monkeypatch.setattr(window.tabs, "active_export_tab", lambda: _FakeTab())
    monkeypatch.setattr(QFileDialog, "getSaveFileName", staticmethod(lambda *a: ("", "")))
    window._save_data()
    assert window.ui.savePanel.ui.comboGroup.isEnabled()


# ---- gain, auto gain, dark tare ---------------------------------------------------------------


def test_clicking_a_gain_button_sets_the_stage_and_checks_only_that_button(connected) -> None:
    ui = connected.ui.readoutPanel.ui
    ui.buttonGain3.click()
    assert connected.ctx.data.pdtia_gain == 3
    assert ui.buttonGain3.isChecked() and not ui.buttonGain2.isChecked()
    ui.buttonGain2.click()
    assert connected.ctx.data.pdtia_gain == 2
    assert ui.buttonGain2.isChecked() and not ui.buttonGain3.isChecked()


def test_the_gain_buttons_exist_once_in_the_window(window) -> None:
    for stage in (1, 2, 3, 4):
        assert len(window.findChildren(QPushButton, f"buttonGain{stage}")) == 1
        assert not window.findChildren(QPushButton, f"buttonGain{stage}_2")
    assert len(window.findChildren(QPushButton, "buttonGainAuto")) == 1


def test_a_manual_gain_click_turns_auto_off(connected) -> None:
    ui = connected.ui.readoutPanel.ui
    ui.buttonGainAuto.setChecked(True)
    assert connected.ctx.detector.gain_auto_enabled
    ui.buttonGain4.click()
    assert not ui.buttonGainAuto.isChecked()
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
    ui.detectorPanel.ui.buttonDarkTare.click()
    assert ui.detectorPanel.ui.buttonDarkTare.isEnabled()

    monkeypatch.setattr(
        QMessageBox, "question", staticmethod(lambda *a, **k: QMessageBox.StandardButton.Yes)
    )
    ui.detectorPanel.ui.buttonDarkTare.click()
    assert not ui.detectorPanel.ui.buttonDarkTare.isEnabled()
    assert not ui.detectorPanel.ui.buttonDarkReset.isEnabled()
    qtbot.waitUntil(lambda: ui.detectorPanel.ui.buttonDarkTare.isEnabled(), timeout=10000)
    assert ui.detectorPanel.ui.valueDarkOffset.text().endswith(" mV")

    ui.detectorPanel.ui.buttonDarkReset.click()
    assert ui.detectorPanel.ui.valueDarkOffset.text() == _text(
        connected, "detector_panel.dark_offset_none"
    )


def test_selecting_a_profile_in_the_combo_loads_it(window, tmp_path) -> None:
    path = tmp_path / "cal-x.json"
    PowerCalibrationProfile(name="cal-x").save(path)
    window.ctx.detector._profiles_dir = tmp_path
    window._reload_profiles()
    assert window.ui.detectorPanel.ui.comboProfile.count() == 1
    assert window.ctx.detector.profile_name == ""  # the selector shows its placeholder
    window.ui.detectorPanel.ui.comboProfile.setCurrentIndex(0)
    assert window.ctx.detector.profile_name == "cal-x"
    assert window.ctx.detector.calibration_profile is not None

    window._reload_profiles()  # a reload keeps the selection
    assert window.ui.detectorPanel.ui.comboProfile.currentText() == "cal-x"
    assert window.ctx.detector.profile_name == "cal-x"


def test_the_pdtia_id_selector_feeds_the_detector_controller(window) -> None:
    combo = window.ui.detectorPanel.ui.comboPdtiaId
    combo.setCurrentIndex(combo.count() - 1)
    assert window.ctx.detector.pdtia_id == combo.currentText()


# ---- inline acquisition settings --------------------------------------------------------------


def test_inline_averaging_edits_reach_the_data_controller(window) -> None:
    window.ui.sampleStagePanel.ui.spinAverages.setValue(9)
    window.ui.detectorStagePanel.ui.checkAverage.setChecked(False)
    acq = window.ctx.measurement.acq_settings
    assert acq.samp_averages == 9
    assert not acq.det_average_on
    assert not window.ui.detectorStagePanel.ui.spinAverages.isEnabled()
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

    monkeypatch.setattr(auxiliary_windows_module, "AcquisitionSettingsDialog", FakeDialog)
    window.ui.actionAcquisitionSettings.trigger()
    assert window.ui.sampleStagePanel.ui.spinAverages.value() == 13
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

    monkeypatch.setattr(auxiliary_windows_module, "AcquisitionSettingsDialog", FakeDialog)
    window.ui.actionAcquisitionSettings.trigger()
    assert window.ctx.measurement.acq_settings == before


# ---- KDC101 -----------------------------------------------------------------------------------


def test_connecting_the_kdc_adds_the_waveplate_tab_and_shows_the_position(qtbot, window) -> None:
    ui = window.ui
    before = _tab_titles(window)
    ui.kdcPanel.ui.buttonConnect.click()

    assert window.ctx.kdc.is_connected
    assert ui.kdcPanel.ui.buttonConnect.text() == _text(window, "kdc_panel.text_disconnect")
    assert ui.kdcPanel.ui.valueStatus.text() == _text(
        window, "main_window.status_connected_named", id=KDC_ID
    )
    assert ui.kdcPanel.ui.buttonHome.isEnabled() and ui.kdcPanel.ui.buttonZero.isEnabled()
    assert ui.kdcPanel.ui.buttonOffsetReset.isEnabled()
    assert len(_tab_titles(window)) == len(before) + 1
    waveplate = next(t for t in window.tabs.tabs if t.tab_id == "waveplate")
    assert not ui.tabWidget.isTabEnabled(ui.tabWidget.indexOf(waveplate))  # group gate applies

    window.ctx.kdc.kdc.move_to(30.0)
    window.ctx.kdc.poll_position()
    assert ui.kdcPanel.ui.valuePosition.text().endswith("°")
    assert "30" in ui.kdcPanel.ui.valuePosition.text()

    ui.kdcPanel.ui.buttonConnect.click()
    assert not window.ctx.kdc.is_connected
    assert _tab_titles(window) == before
    assert ui.kdcPanel.ui.buttonConnect.text() == _text(window, "kdc_panel.text_connect")
    assert ui.kdcPanel.ui.valuePosition.text() == _text(window, "kdc_panel.text_none")
    assert not ui.kdcPanel.ui.buttonHome.isEnabled()


def test_the_kdc_buttons_home_and_reset_the_offset(qtbot, window) -> None:
    ui = window.ui
    ui.kdcPanel.ui.buttonConnect.click()
    window.ctx.kdc.set_zero_offset(25.0)
    assert ui.kdcPanel.ui.valueOffset.text().startswith("25")
    ui.kdcPanel.ui.buttonOffsetReset.click()
    assert ui.kdcPanel.ui.valueOffset.text() == _text(window, "kdc_panel.text_none")

    ui.kdcPanel.ui.buttonHome.click()
    assert not ui.kdcPanel.ui.buttonHome.isEnabled()
    assert not ui.kdcPanel.ui.buttonConnect.isEnabled()
    qtbot.waitUntil(lambda: ui.kdcPanel.ui.buttonHome.isEnabled(), timeout=3000)
    assert ui.kdcPanel.ui.buttonConnect.isEnabled()


def test_connecting_the_kdc_without_a_device_warns(window, monkeypatch) -> None:
    warned: list[tuple[str, str]] = []
    monkeypatch.setattr(
        QMessageBox,
        "warning",
        staticmethod(lambda parent, title, text: warned.append((title, text))),
    )
    window.ui.kdcPanel.ui.comboDevice.clear()
    window.ui.kdcPanel.ui.comboDevice.addItem(_text(window, "kdc_panel.text_no_device"))
    window.ui.kdcPanel.ui.buttonConnect.click()
    assert warned == [(window.config.message("kdc.title"), window.config.message("kdc.no_device"))]
    assert not window.ctx.kdc.is_connected


# ---- PM400 ------------------------------------------------------------------------------------


def test_connecting_the_pm400_makes_it_the_active_detector_in_the_panel(qtbot, connected) -> None:
    ui = connected.ui
    ui.detectorPanel.ui.buttonPm400Connect.click()
    assert connected.ctx.pm400.is_connected
    assert ui.detectorPanel.ui.buttonPm400Connect.text() == _text(
        connected, "detector_panel.text_disconnect"
    )
    assert ui.detectorPanel.ui.buttonPm400Zero.isEnabled()
    assert _led_style(connected.ui.detectorPanel.ui.ledPm400Status) == LED_GREEN
    assert "S120C" in ui.detectorPanel.ui.valuePm400Status.text()
    qtbot.waitUntil(lambda: not ui.readoutPanel.ui.buttonGain1.isEnabled(), timeout=3000)
    for stage in (2, 3, 4):
        assert not getattr(ui.readoutPanel.ui, f"buttonGain{stage}").isEnabled()
    assert not ui.readoutPanel.ui.buttonGainAuto.isEnabled()
    qtbot.waitUntil(lambda: ui.readoutPanel.ui.lcdPower.value() != 0.0, timeout=5000)

    ui.detectorPanel.ui.buttonPm400Connect.click()
    assert not connected.ctx.pm400.is_connected
    qtbot.waitUntil(lambda: ui.readoutPanel.ui.buttonGain1.isEnabled(), timeout=3000)
    assert ui.detectorPanel.ui.buttonPm400Connect.text() == _text(
        connected, "detector_panel.text_connect"
    )
    assert not ui.detectorPanel.ui.buttonPm400Zero.isEnabled()
    assert _led_style(connected.ui.detectorPanel.ui.ledPm400Status) == LED_RED


def test_the_wavelength_spin_box_drives_the_pm400_controller(window) -> None:
    window.ui.detectorPanel.ui.spinWavelength.setValue(532.0)
    assert window.ctx.pm400.wavelength_nm == 532.0


def test_connecting_the_pm400_without_a_resource_warns(connected, monkeypatch) -> None:
    window = connected
    warned: list[str] = []
    monkeypatch.setattr(
        QMessageBox, "warning", staticmethod(lambda parent, title, text: warned.append(text))
    )
    window.ui.detectorPanel.ui.comboPm400Resource.clear()
    window.ui.detectorPanel.ui.buttonPm400Connect.click()
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
    assert window.ui.detectorPanel.ui.comboProfile.findText("fresh") >= 0

    _close_children(window, PowerCalibrationWindow)
    _close_children(window, AutoPowerCalibrationWindow)


def test_the_calibration_button_in_the_detector_tab_opens_the_power_calibration(connected) -> None:
    window = connected
    from polarisation_ui.ui.windows.power_calibration_window import PowerCalibrationWindow

    window.ui.detectorPanel.ui.buttonOpenCalibration.click()
    assert len(window.findChildren(PowerCalibrationWindow)) == 1
    _close_children(window, PowerCalibrationWindow)


def test_the_log_window_is_created_once_and_reused(window) -> None:
    from polarisation_ui.ui.windows.log_window import LogWindow

    window.ui.actionLogWindow.trigger()
    window.ui.actionLogWindow.trigger()
    assert len(window.findChildren(LogWindow)) == 1
    _close_children(window, LogWindow)


def test_the_event_log_dock_follows_its_action(window) -> None:
    window.ui.actionToggleEventLog.setChecked(False)
    assert not window.ui.dockEventLog.isVisible()
    window.ui.actionToggleEventLog.setChecked(True)
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
    assert win.ui.savePanel.ui.comboGroup.currentText() == "C"
    assert win.ui.savePanel.ui.editTeam.text() == "Team Gruen"
    assert win.ui.savePanel.ui.editSuffix.text() == "again"
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
    win.ui.savePanel.ui.comboGroup.setCurrentIndex(2)
    qtbot.waitUntil(persistent_env.state.exists, timeout=3000)
    win.close()
    assert win.ctx.measurement.group_letter in persistent_env.state.read_text(encoding="utf-8")


# ---- source rules -----------------------------------------------------------------------------

GERMAN_CHARS = re.compile(r"[äöüÄÖÜß]")
GERMAN_WORDS = re.compile(
    r"\b(Verbinden|Verbunden|Trennen|Getrennt|Nicht|Bitte|Fehler|Messung|Keine?|Gerät|Sitzung)\b"
)
PANEL_SOURCES = sorted((UI_DIR / "widgets" / "panels").glob("*_panel.py"))
CHECKED_SOURCES = [
    UI_DIR / "windows" / "main_window.py",
    UI_DIR / "windows" / "auxiliary_windows.py",
    UI_DIR / "common" / "session_prompts.py",
    UI_DIR / "context.py",
    UI_DIR / "widgets" / "tab_host.py",
    *PANEL_SOURCES,
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
    lines = (UI_DIR / "windows" / "main_window.py").read_text(encoding="utf-8").count("\n")
    assert lines < 600


# Qt classes that Python code may instantiate: non-visual helpers only (widgets live in the .ui).
_NON_VISUAL = {"QSettings", "QTimer", "QButtonGroup", "QSize", "QEvent"}


@pytest.mark.parametrize(
    "path", [UI_DIR / "windows" / "main_window.py", *PANEL_SOURCES], ids=lambda p: p.name
)
def test_the_window_and_the_panels_construct_no_widgets_in_python(path: Path) -> None:
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            name = node.func.id
            assert not (re.fullmatch(r"Q[A-Z]\w+", name) and name not in _NON_VISUAL), (
                f"{path.name} constructs {name}"
            )


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


# ---- strings, toolbar and structure -----------------------------------------------------------

FORM_ROOTS = {
    "main_window": lambda w: w,
    "arduino_panel": lambda w: w.ui.arduinoPanel,
    "stage_panel": lambda w: w.ui.sampleStagePanel,
    "kdc_panel": lambda w: w.ui.kdcPanel,
    "detector_panel": lambda w: w.ui.detectorPanel,
    "readout_panel": lambda w: w.ui.readoutPanel,
    "measurement_panel": lambda w: w.ui.measurementPanel,
    "save_panel": lambda w: w.ui.savePanel,
}
TOOLBAR_ACTIONS = (
    "actionAcquisitionSettings",
    "actionPowerCalibration",
    "actionAutoPowerCalibration",
    "actionEncoderDebug",
    "actionLogWindow",
    "actionAutoSaveEnabled",
    "actionToggleControls",
    "actionToggleMeasurement",
    "actionToggleEventLog",
    "actionFullScreen",
)


@pytest.mark.parametrize("form", sorted(FORM_ROOTS))
def test_every_configured_ui_key_of_the_window_and_its_panels_names_a_widget(window, form) -> None:
    root = FORM_ROOTS[form](window)
    strings = window.config.section("ui")[form]
    for key in strings:
        name = key.partition("@")[0]
        if "_" in name or name == "self":
            continue
        found = root.findChild(QObject, name) or getattr(window.ui, name, None)
        assert found is not None, f"ui.{form}.{key} names no widget"


def test_the_toolbar_shows_the_german_texts_from_the_config(window) -> None:
    strings = window.config.section("ui")["main_window"]
    toolbar_names = [a.objectName() for a in window.ui.toolBar.actions() if a.objectName()]
    assert set(TOOLBAR_ACTIONS) <= set(toolbar_names)
    for name in TOOLBAR_ACTIONS:
        action = getattr(window.ui, name)
        assert action.text() == strings[name] != ""
        assert action.toolTip() == strings[f"{name}@tooltip"]
    assert window.windowTitle() == strings["self@title"]
    assert window.ui.dockControls.windowTitle() == strings["dockControls"]
    assert window.ui.dockMeasurement.windowTitle() == strings["dockMeasurement"]
    assert window.ui.dockEventLog.windowTitle() == strings["dockEventLog"]


def test_the_old_menu_bar_and_configuration_tab_are_gone(window) -> None:
    assert window.menuBar().actions() == []
    assert {t.tab_id for t in window.tabs.tabs} == {
        window.ui.tabWidget.widget(i).tab_id for i in range(window.ui.tabWidget.count())
    }
    titles = [window.ui.tabWidget.tabText(i) for i in range(window.ui.tabWidget.count())]
    assert titles == [window.config.text(f"tabs.{t.tab_id}") for t in window.tabs.tabs]


def test_the_detector_panel_has_the_pdtia_and_pm400_pages_with_german_titles(window) -> None:
    tabs = window.ui.detectorPanel.ui.tabDetector
    strings = window.config.section("ui")["detector_panel"]
    assert [tabs.tabText(i) for i in range(tabs.count())] == [
        strings["tabPdtia@tab"],
        strings["tabPm400@tab"],
    ]


def test_no_button_check_radio_or_label_is_empty_and_every_group_box_has_a_title(window) -> None:
    for widget in window.findChildren(QAbstractButton):
        name = widget.objectName()
        if name.startswith(("button", "check", "radio")):
            assert widget.text().strip() != "", name
    for label in window.findChildren(QLabel):
        if label.objectName().startswith("label"):
            assert label.text().strip() != "", label.objectName()
    for group in window.findChildren(QGroupBox):
        assert group.title().strip() != "", group.objectName() or type(group).__name__
    for text in (w.text() for w in window.findChildren(QAbstractButton)):
        assert not re.fullmatch(r"\w+\.\w+", text), f"raw config key shown: {text!r}"


def test_the_stage_panels_get_their_titles_from_the_config_and_only_the_detector_has_180(
    window,
) -> None:
    strings = window.config.section("ui")["stage_panel"]
    sample, detector = window.ui.sampleStagePanel, window.ui.detectorStagePanel
    assert sample.title() == strings["title_sample"]
    assert detector.title() == strings["title_detector"]
    assert sample.ui.button180.isHidden()
    assert not detector.ui.button180.isHidden()


def test_each_side_dock_holds_a_scroll_area_with_the_panels(window) -> None:
    ui = window.ui
    for dock, scroll, panels in (
        (ui.dockControls, ui.scrollControls, ("arduinoPanel", "sampleStagePanel", "kdcPanel")),
        (
            ui.dockMeasurement,
            ui.scrollMeasurement,
            ("readoutPanel", "measurementPanel", "savePanel"),
        ),
    ):
        assert dock.findChild(QScrollArea) is scroll
        for name in panels:
            assert scroll.widget().findChild(QGroupBox, name) is not None
    assert ui.dockEventLog.findChild(QScrollArea) is None
    assert ui.dockEventLog.widget() is ui.eventLogPanel


def test_the_suffix_toolbar_action_shows_and_hides_the_suffix_input(window) -> None:
    ui = window.ui.savePanel.ui
    assert not ui.editSuffix.isHidden() and not ui.labelSuffix.isHidden()
    window.ui.actionAutoSaveEnabled.setChecked(False)
    assert ui.editSuffix.isHidden() and ui.labelSuffix.isHidden()
    window.ui.actionAutoSaveEnabled.setChecked(True)
    assert not ui.editSuffix.isHidden()


def test_the_suffix_toolbar_action_says_what_it_does(window) -> None:
    action = window.ui.actionAutoSaveEnabled
    assert action.text() == "Dateiname-Zusatz"
    assert "Suffix" in action.toolTip() and "Dateinamen" in action.toolTip()
    assert "Suffix-Feld" not in action.text()


# ---- docks, layout persistence, full screen ---------------------------------------------------

DOCKS = (
    ("dockControls", "actionToggleControls"),
    ("dockMeasurement", "actionToggleMeasurement"),
    ("dockEventLog", "actionToggleEventLog"),
)


@pytest.mark.parametrize(("dock", "action"), DOCKS)
def test_a_dock_collapses_and_returns_through_its_action_and_through_its_own_close_button(
    window, dock, action
) -> None:
    dock_widget, toggle = getattr(window.ui, dock), getattr(window.ui, action)
    assert dock_widget.isVisible() and toggle.isChecked()
    toggle.setChecked(False)
    assert dock_widget.isHidden()
    toggle.setChecked(True)
    assert dock_widget.isVisible()
    dock_widget.close()  # the dock's own close button
    assert not toggle.isChecked()
    dock_widget.show()
    assert toggle.isChecked()


def _stored(layout_file: Path, key: str):
    from PySide6.QtCore import QSettings

    return QSettings(str(layout_file), QSettings.Format.IniFormat).value(key)


def test_the_layout_is_saved_on_close_and_restored_on_the_next_start(
    qtbot, config, persistent_env, layout_file
) -> None:
    first = _open(qtbot, config)
    first.ui.actionToggleMeasurement.setChecked(False)
    height = first.minimumSizeHint().height() + 30  # just above the minimum, off the default
    first.resize(900, height)
    first.close()
    assert _stored(layout_file, "window/geometry") is not None
    assert _stored(layout_file, "window/state") is not None

    second = _open(qtbot, config)
    assert second.ui.dockMeasurement.isHidden()
    assert not second.ui.actionToggleMeasurement.isChecked()
    assert second.ui.dockControls.isVisible() and second.ui.actionToggleControls.isChecked()
    assert second.height() == height  # the default height differs
    second.close()


def test_a_window_without_persistence_never_touches_the_saved_layout(
    qtbot, config, layout_file, window
) -> None:
    window.ui.actionToggleMeasurement.setChecked(False)
    window.close()
    assert not layout_file.exists()


def test_each_profile_keeps_its_own_layout_keys(qtbot, persistent_env, layout_file) -> None:
    student = load_config(profile="student")
    win = _open(qtbot, student)
    assert win._layout_key("geometry") == "window/student/geometry"
    win.close()
    assert _stored(layout_file, "window/student/state") is not None
    assert _stored(layout_file, "window/state") is None

    expert = load_config()
    other = _open(qtbot, expert)
    assert other._layout_key("state") == "window/state"
    other.close()


def test_the_full_screen_action_and_f11_toggle_the_full_screen_state(qtbot, window) -> None:
    action = window.ui.actionFullScreen
    assert action.shortcut().toString() == "F11"
    assert not window.isFullScreen() and not action.isChecked()
    action.trigger()
    assert window.isFullScreen() and action.isChecked()
    action.trigger()
    assert not window.isFullScreen() and not action.isChecked()


def test_leaving_full_screen_returns_to_the_maximised_window(qtbot, window) -> None:
    window.showMaximized()
    window.set_fullscreen(True)
    assert window.isFullScreen()
    window.set_fullscreen(False)
    assert window.isMaximized() and not window.isFullScreen()


@pytest.mark.parametrize(
    ("mode", "full", "maximised"),
    [("fullscreen", True, False), ("maximized", False, True), ("normal", False, False)],
)
def test_show_initial_applies_the_window_mode(qtbot, config, mode, full, maximised) -> None:
    ModuleRegistry.clear()
    win = MainWindow(config, simulate=True, persist=False)
    qtbot.addWidget(win)
    win.show_initial(mode)
    assert win.isFullScreen() is full
    assert win.isMaximized() is maximised
    assert win.ui.actionFullScreen.isChecked() is full
    win.close()
    ModuleRegistry.clear()


def test_an_unknown_window_mode_falls_back_to_maximised(qtbot, config) -> None:
    ModuleRegistry.clear()
    win = MainWindow(config, simulate=True, persist=False)
    qtbot.addWidget(win)
    win.show_initial("sideways")
    assert win.isMaximized()
    win.close()
    ModuleRegistry.clear()


def test_the_configured_window_mode_is_a_known_mode(config) -> None:
    assert config.get("application.window_mode") in main_window_module.WINDOW_MODES
