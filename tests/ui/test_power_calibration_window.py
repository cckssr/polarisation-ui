"""Tests for PowerCalibrationWindow and its per-gain tabs (Designer forms, strings, PM400 flows).

No hardware: the PM400 is ``MockPM400`` (or absent), the data controller is a tiny fake that
only carries the ``intensity_updated`` signal, and the user settings file is never read.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QDialogButtonBox, QMessageBox, QWidget

import polarisation_ui.ui.windows.power_calibration_window as pcw
from polarisation_ui.core.auto_calibration_settings import AutoCalibrationConnectionSettings
from polarisation_ui.core.power_calibration import (
    GainCalibration,
    PowerCalibrationProfile,
)
from polarisation_ui.infrastructure.config import AppConfig
from polarisation_ui.infrastructure.devices.pm400 import PM400PowerMeter
from polarisation_ui.infrastructure.mocks.mock_pm400 import MockPM400
from polarisation_ui.ui.windows.power_calibration_window import (
    GainCalibrationTab,
    PowerCalibrationWindow,
)

MODULE_PATH = Path(pcw.__file__)
RESOURCE = "USB0::0x1313::0x8078::MOCK00001::INSTR"


class FakeDataController(QObject):
    """Stands in for DataController: only the live-voltage signal."""

    intensity_updated = Signal(float)


class DialogRecorder:
    """Replaces the QMessageBox static helpers and records (kind, title, text)."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str, str]] = []

    def install(self, monkeypatch: pytest.MonkeyPatch) -> None:
        for kind in ("warning", "critical", "information"):
            monkeypatch.setattr(
                QMessageBox,
                kind,
                staticmethod(
                    lambda parent, title, text, _kind=kind: self.calls.append((_kind, title, text))
                ),
            )


@pytest.fixture(autouse=True)
def isolated_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """No user settings file, no VISA scan."""
    monkeypatch.setattr(
        AutoCalibrationConnectionSettings,
        "load",
        classmethod(lambda cls, path=None: cls(beamsplitter_attenuation_dB=3.0)),
    )
    monkeypatch.setattr(PM400PowerMeter, "list_resources", staticmethod(lambda: [RESOURCE]))


@pytest.fixture
def dialogs(monkeypatch: pytest.MonkeyPatch) -> DialogRecorder:
    recorder = DialogRecorder()
    recorder.install(monkeypatch)
    return recorder


@pytest.fixture
def controller() -> FakeDataController:
    return FakeDataController()


@pytest.fixture
def window(qtbot, controller: FakeDataController, config: AppConfig) -> PowerCalibrationWindow:
    win = PowerCalibrationWindow(data_controller=controller, config=config)
    qtbot.addWidget(win)
    return win


@pytest.fixture
def shared_window(qtbot, config: AppConfig) -> PowerCalibrationWindow:
    pm = MockPM400()
    pm.connect(RESOURCE)
    win = PowerCalibrationWindow(pm400=pm, config=config)
    qtbot.addWidget(win)
    return win


def _add_point(tab: GainCalibrationTab, voltage: float, power: float) -> None:
    tab.ui.spinVoltage.setValue(voltage)
    tab.ui.spinPower.setValue(power)
    tab.ui.buttonAdd.click()


# ── construction and strings ────────────────────────────────────────────────


def test_the_window_builds_without_pm400_hardware_and_without_a_data_controller(
    qtbot, config: AppConfig
) -> None:
    win = PowerCalibrationWindow(config=config)
    qtbot.addWidget(win)
    assert win.ui.comboPm400.count() == 1
    assert win.ui.buttonConnect.isEnabled()
    assert not win.ui.buttonToggleAttenuation.isEnabled()


def test_the_window_shows_one_gain_tab_per_stage(window: PowerCalibrationWindow) -> None:
    tabs = window.ui.tabGains
    assert tabs.count() == 4
    assert [tabs.tabText(i) for i in range(4)] == ["Gain 1", "Gain 2", "Gain 3", "Gain 4"]
    assert all(isinstance(tabs.widget(i), GainCalibrationTab) for i in range(4))


def test_the_window_shows_the_german_strings(window: PowerCalibrationWindow) -> None:
    ui = window.ui
    assert window.windowTitle() == "Leistungskalibrierung — PD-TIA Detektor"
    assert ui.groupProfile.title() == "Profil"
    assert ui.buttonSave.text() == "Kalibrierung speichern"
    assert ui.buttonLoad.text() == "Kalibrierung laden…"
    assert ui.groupPm400.title() == "PM400 Leistungsmesser"
    assert ui.labelResource.text() == "VISA-Ressource:"
    assert ui.spinAttenuation.suffix() == " dB"
    assert ui.spinWavelength.suffix() == " nm"
    assert ui.editProfileName.placeholderText() == "z.B. Det-A"
    assert ui.valuePm400Status.text() == "Nicht verbunden"
    assert ui.buttonBox.button(QDialogButtonBox.StandardButton.Close).text() == "Schließen"
    assert ui.spinAttenuation.value() == pytest.approx(3.0)


def test_the_gain_tab_shows_the_german_strings_for_its_stage(
    window: PowerCalibrationWindow,
) -> None:
    tab = window.ui.tabGains.widget(1)
    assert isinstance(tab, GainCalibrationTab)
    assert tab.ui.groupEntry.title() == "Messpunkt hinzufügen — Gain 2"
    assert tab.ui.buttonAdd.text() == "Punkt hinzufügen"
    assert tab.ui.buttonRemove.text() == "Ausgewählten Punkt löschen"
    assert tab.ui.valueFactor.text() == "Konversionsfaktor: —"
    headers = [
        tab.ui.tablePoints.horizontalHeaderItem(i).text()
        for i in range(tab.ui.tablePoints.columnCount())
    ]
    assert headers == ["Spannung (V)", "Leistung (W)", "W/V"]
    assert tab.ui.calibrationPlot.getAxis("bottom").labelText == "Spannung"
    assert tab.ui.calibrationPlot.getAxis("left").labelUnits == "W"


def test_a_config_override_changes_the_shown_text(qtbot, config: AppConfig) -> None:
    custom = config.with_overrides(
        {"ui": {"power_calibration": {"groupProfile": "Profile X", "text_gain_tab": "G{stage}"}}}
    )
    win = PowerCalibrationWindow(config=custom)
    qtbot.addWidget(win)
    assert win.ui.groupProfile.title() == "Profile X"
    assert win.ui.tabGains.tabText(0) == "G1"


def test_the_scroll_area_hosts_the_content_and_the_close_button_stays_outside(
    window: PowerCalibrationWindow,
) -> None:
    assert window.ui.scrollMain.widget() is window.ui.contentMain
    assert not window.ui.contentMain.isAncestorOf(window.ui.buttonBox)
    assert window.ui.contentMain.isAncestorOf(window.ui.tabGains)


# ── config keys ──────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("section", "form_widget"),
    [
        ("power_calibration", "window"),
        ("power_calibration_gain_tab", "tab"),
    ],
)
def test_every_designer_key_resolves_to_a_child_widget(
    window: PowerCalibrationWindow, config: AppConfig, section: str, form_widget: str
) -> None:
    root: QWidget = window if form_widget == "window" else window.ui.tabGains.widget(0)
    for key in config.section("ui")[section]:
        name = key.partition("@")[0]
        if "_" in name:
            continue
        assert name == "self" or root.findChild(QObject, name) is not None, key


def _called_keys(function_names: set[str]) -> set[str]:
    keys: set[str] = set()
    for node in ast.walk(ast.parse(MODULE_PATH.read_text(encoding="utf-8"))):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr in function_names
        ):
            keys.update(
                sub.value
                for sub in ast.walk(node.args[0])
                if isinstance(sub, ast.Constant) and isinstance(sub.value, str)
            )
    return keys


def test_every_key_the_code_looks_up_exists_in_the_config(config: AppConfig) -> None:
    ui = config.section("ui")
    messages = config.section("messages")["power_calibration"]
    text_keys = _called_keys({"_text"})
    assert text_keys
    for key in text_keys:
        assert key in ui["power_calibration"] or key in ui["power_calibration_gain_tab"], key
    message_keys = _called_keys({"_message"})
    assert message_keys
    for key in message_keys:
        assert key in messages, key
    for path in _called_keys({"message"}) - {"power_calibration."}:  # helper prefix
        assert config.message(path) != path, path


def test_every_code_key_of_the_config_is_used_by_the_module(config: AppConfig) -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    ui = config.section("ui")
    code_keys = (
        {k for k in ui["power_calibration"] if "_" in k}
        | {k for k in ui["power_calibration_gain_tab"] if "_" in k}
        | set(config.section("messages")["power_calibration"])
    )
    unused = {key for key in code_keys if not re.search(rf'[".]{key}"', source)}
    assert not unused, unused


# ── no widget construction left ──────────────────────────────────────────────

_ALLOWED_QTWIDGETS = {
    "QDialog",
    "QDialogButtonBox",
    "QFileDialog",
    "QHeaderView",
    "QMessageBox",
    "QTableWidgetItem",
    "QWidget",
}


def test_the_module_imports_no_widget_or_layout_classes() -> None:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    imported = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module == "PySide6.QtWidgets"
        for alias in node.names
    }
    assert imported <= _ALLOWED_QTWIDGETS, imported - _ALLOWED_QTWIDGETS
    forbidden = {"QLabel", "QPushButton", "QGroupBox", "QVBoxLayout", "QHBoxLayout", "QFormLayout"}
    forbidden |= {"QLineEdit", "QComboBox", "QDoubleSpinBox", "QTableWidget", "QScrollArea"}
    forbidden |= {"QTabWidget", "QFrame"}
    assert not forbidden & imported


def test_the_module_does_not_construct_a_plot_widget() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "PlotWidget(" not in source
    assert not re.search(r"[\"'][^\"'\n]*[äöüÄÖÜß][^\"'\n]*[\"']", source)


# ── gain tab behaviour ───────────────────────────────────────────────────────


def test_adding_a_point_updates_the_table_the_factor_and_emits_points_changed(
    qtbot, window: PowerCalibrationWindow
) -> None:
    tab = window.ui.tabGains.widget(0)
    assert isinstance(tab, GainCalibrationTab)
    with qtbot.waitSignal(tab.points_changed):
        _add_point(tab, 0.5, 1e-3)
    assert tab.ui.tablePoints.rowCount() == 1
    assert tab.ui.tablePoints.item(0, 0).text() == "0.500000"
    assert tab.ui.tablePoints.item(0, 1).text() == "0.001000000"
    assert tab.ui.tablePoints.item(0, 2).text() == "2.0000e-03"
    assert tab.ui.valueFactor.text() == "Konversionsfaktor: 2.0000e-03 W/V  (Gain 1)"
    assert tab.get_calibration().points == [(0.5, 1e-3)]


def test_the_factor_is_the_mean_of_the_ratios(window: PowerCalibrationWindow) -> None:
    tab = window.ui.tabGains.widget(2)
    assert isinstance(tab, GainCalibrationTab)
    _add_point(tab, 1.0, 1e-3)
    _add_point(tab, 2.0, 6e-3)
    assert tab.ui.tablePoints.rowCount() == 2
    assert tab.ui.valueFactor.text() == "Konversionsfaktor: 2.0000e-03 W/V  (Gain 3)".replace(
        "2.0000e-03", f"{(1e-3 + 3e-3) / 2:.4e}"
    )


def test_removing_the_selected_point_updates_table_and_factor(
    qtbot, window: PowerCalibrationWindow
) -> None:
    tab = window.ui.tabGains.widget(0)
    assert isinstance(tab, GainCalibrationTab)
    _add_point(tab, 0.5, 1e-3)
    tab.ui.tablePoints.selectRow(0)
    with qtbot.waitSignal(tab.points_changed):
        tab.ui.buttonRemove.click()
    assert tab.ui.tablePoints.rowCount() == 0
    assert tab.ui.valueFactor.text() == "Konversionsfaktor: —"
    assert tab.get_calibration().points == []


def test_removing_without_a_selection_does_nothing(window: PowerCalibrationWindow) -> None:
    tab = window.ui.tabGains.widget(0)
    assert isinstance(tab, GainCalibrationTab)
    _add_point(tab, 0.5, 1e-3)
    tab.ui.tablePoints.setCurrentCell(-1, -1)
    tab.ui.buttonRemove.click()
    assert tab.ui.tablePoints.rowCount() == 1


def test_an_invalid_point_is_rejected_with_a_german_warning(
    window: PowerCalibrationWindow, dialogs: DialogRecorder
) -> None:
    tab = window.ui.tabGains.widget(0)
    assert isinstance(tab, GainCalibrationTab)
    _add_point(tab, 0.0, 1e-3)
    _add_point(tab, 0.5, 0.0)
    assert dialogs.calls == [
        ("warning", "Ungültige Eingabe", "Spannung muss größer als 0 sein."),
        ("warning", "Ungültige Eingabe", "Leistung muss größer als 0 sein."),
    ]
    assert tab.ui.tablePoints.rowCount() == 0


def test_the_gain_tabs_keep_separate_calibrations(window: PowerCalibrationWindow) -> None:
    first, second = window.ui.tabGains.widget(0), window.ui.tabGains.widget(1)
    assert isinstance(first, GainCalibrationTab) and isinstance(second, GainCalibrationTab)
    _add_point(first, 0.5, 1e-3)
    assert second.ui.tablePoints.rowCount() == 0
    assert second.get_calibration().gain_stage == 2


def test_the_live_button_copies_the_live_voltage(
    window: PowerCalibrationWindow, controller: FakeDataController
) -> None:
    tab = window.ui.tabGains.widget(0)
    assert isinstance(tab, GainCalibrationTab)
    assert not tab.ui.buttonLive.isEnabled()
    tab.ui.buttonLive.setEnabled(True)
    tab.ui.buttonLive.click()
    assert tab.ui.spinVoltage.value() == 0.0  # nothing cached yet
    controller.intensity_updated.emit(1.234)
    assert tab.ui.buttonLive.isEnabled()
    tab.ui.buttonLive.click()
    assert tab.ui.spinVoltage.value() == pytest.approx(1.234)


def test_loading_a_calibration_refreshes_the_tab(window: PowerCalibrationWindow) -> None:
    tab = window.ui.tabGains.widget(3)
    assert isinstance(tab, GainCalibrationTab)
    cal = GainCalibration(gain_stage=4)
    cal.add_point(1.0, 2e-3)
    tab.load_calibration(cal)
    assert tab.ui.tablePoints.rowCount() == 1
    assert "Gain 4" in tab.ui.valueFactor.text()


# ── live values and data controller ──────────────────────────────────────────


def test_the_live_voltage_signal_updates_the_label_and_every_tab(
    window: PowerCalibrationWindow, controller: FakeDataController
) -> None:
    controller.intensity_updated.emit(2.5)
    assert window.ui.valueDetectorVoltage.text() == "2.500000 V"
    for i in range(4):
        assert window.ui.tabGains.widget(i).ui.buttonLive.isEnabled()


def test_closing_the_window_detaches_from_the_data_controller(
    window: PowerCalibrationWindow, controller: FakeDataController
) -> None:
    window.close()
    controller.intensity_updated.emit(9.0)
    assert window.ui.valueDetectorVoltage.text() == "—"


# ── PM400 ────────────────────────────────────────────────────────────────────


def test_a_shared_connected_pm400_is_used_without_a_second_session(
    shared_window: PowerCalibrationWindow,
) -> None:
    ui = shared_window.ui
    assert ui.valuePm400Status.text() == "Verbunden (Hauptfenster): S120C | MOCK0001 | Mock sensor"
    assert not ui.comboPm400.isEnabled()
    assert not ui.buttonConnect.isEnabled()
    assert ui.buttonToggleAttenuation.isEnabled()
    assert shared_window._pm_poll_timer.isActive()


def test_a_shared_pm400_that_is_not_connected_points_to_the_main_window(
    qtbot, config: AppConfig
) -> None:
    win = PowerCalibrationWindow(pm400=MockPM400(), config=config)
    qtbot.addWidget(win)
    assert win.ui.valuePm400Status.text() == "Nicht verbunden — PM400 im Hauptfenster verbinden"
    assert not win._pm_poll_timer.isActive()
    assert not win.ui.buttonToggleAttenuation.isEnabled()


def test_the_power_poll_fills_the_live_power_label(shared_window: PowerCalibrationWindow) -> None:
    shared_window._on_pm400_power_poll()
    text = shared_window.ui.valuePm400Power.text()
    assert text.endswith(" W")
    assert text != "— W"
    assert shared_window._live_pm400_power_W is not None


def test_the_attenuation_button_toggles_the_pm400_attenuation(
    shared_window: PowerCalibrationWindow,
) -> None:
    ui = shared_window.ui
    pm = shared_window._pm
    ui.buttonToggleAttenuation.click()
    assert pm.get_attenuation_dB() == pytest.approx(3.0)
    assert ui.buttonToggleAttenuation.text() == "Abschwächung ausschalten"
    ui.buttonToggleAttenuation.click()
    assert pm.get_attenuation_dB() == 0.0
    assert ui.buttonToggleAttenuation.text() == "Abschwächung setzen"


def test_closing_keeps_a_shared_pm400_connected_and_stops_the_poll(
    shared_window: PowerCalibrationWindow,
) -> None:
    shared_window.close()
    assert shared_window._pm.is_connected()
    assert not shared_window._pm_poll_timer.isActive()


def test_connecting_and_disconnecting_an_own_pm400(window: PowerCalibrationWindow) -> None:
    ui = window.ui
    window._pm = MockPM400()
    ui.comboPm400.setCurrentText(RESOURCE)
    ui.buttonConnect.click()
    assert window._pm.is_connected()
    assert ui.valuePm400Status.text().startswith("Verbunden: S120C")
    assert ui.buttonConnect.text() == "Trennen"
    assert ui.buttonToggleAttenuation.isEnabled()
    assert window._pm_poll_timer.isActive()

    ui.buttonConnect.click()
    assert not window._pm.is_connected()
    assert ui.valuePm400Status.text() == "Nicht verbunden"
    assert ui.buttonConnect.text() == "Verbinden"
    assert not ui.buttonToggleAttenuation.isEnabled()
    assert not window._pm_poll_timer.isActive()
    assert ui.valuePm400Power.text() == "—"


def test_connecting_without_a_resource_warns(
    qtbot, config: AppConfig, dialogs: DialogRecorder, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(PM400PowerMeter, "list_resources", staticmethod(lambda: []))
    win = PowerCalibrationWindow(config=config)
    qtbot.addWidget(win)
    win.ui.buttonConnect.click()
    assert dialogs.calls == [("warning", "PM400", "Keine VISA-Ressource angegeben.")]


def test_a_failing_pm400_connect_shows_the_error_dialog(
    window: PowerCalibrationWindow, dialogs: DialogRecorder
) -> None:
    from polarisation_ui.core.exceptions import PM400Error

    class Failing(MockPM400):
        def connect(self, visa_resource: str) -> None:
            raise PM400Error("boom")

    window._pm = Failing()
    window.ui.buttonConnect.click()
    assert dialogs.calls == [("critical", "PM400 Fehler", "boom")]
    assert window.ui.valuePm400Status.text() == "Nicht verbunden"


def test_closing_disconnects_an_own_pm400(window: PowerCalibrationWindow) -> None:
    window._pm = MockPM400()
    window._pm.connect(RESOURCE)
    window.close()
    assert not window._pm.is_connected()


# ── profile save and load ────────────────────────────────────────────────────


def test_saving_without_a_name_warns(
    window: PowerCalibrationWindow, dialogs: DialogRecorder
) -> None:
    window.ui.buttonSave.click()
    assert dialogs.calls == [("warning", "Kein Name", "Bitte einen Profilnamen eingeben.")]


def test_saving_writes_the_profile_and_emits_profile_saved(
    qtbot,
    window: PowerCalibrationWindow,
    dialogs: DialogRecorder,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    target = tmp_path / "Det-A.json"
    monkeypatch.setattr(PowerCalibrationProfile, "default_path", staticmethod(lambda name: target))
    tab = window.ui.tabGains.widget(0)
    assert isinstance(tab, GainCalibrationTab)
    _add_point(tab, 0.5, 1e-3)
    window.ui.editProfileName.setText("Det-A")
    window.ui.spinWavelength.setValue(532.0)
    with qtbot.waitSignal(window.profile_saved):
        window.ui.buttonSave.click()
    assert target.exists()
    saved = PowerCalibrationProfile.load(target)
    assert saved.name == "Det-A"
    assert saved.wavelength_nm == pytest.approx(532.0)
    assert saved.gains[1].points == [(0.5, 1e-3)]
    kind, title, text = dialogs.calls[-1]
    assert (kind, title) == ("information", "Gespeichert")
    assert text.startswith("Kalibrierungsprofil 'Det-A' wurde gespeichert:")


def test_a_failing_save_shows_the_error_dialog(
    window: PowerCalibrationWindow, dialogs: DialogRecorder, monkeypatch: pytest.MonkeyPatch
) -> None:
    def broken(self: PowerCalibrationProfile, path: Path) -> None:
        raise OSError("disk full")

    monkeypatch.setattr(PowerCalibrationProfile, "save", broken)
    window.ui.editProfileName.setText("X")
    window.ui.buttonSave.click()
    assert dialogs.calls[-1] == ("critical", "Fehler", "Speichern fehlgeschlagen:\ndisk full")


def test_loading_a_profile_fills_name_wavelength_and_tabs(
    qtbot,
    config: AppConfig,
    window: PowerCalibrationWindow,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    profile = PowerCalibrationProfile(name="Loaded", wavelength_nm=780.0)
    cal = GainCalibration(gain_stage=2)
    cal.add_point(1.0, 4e-3)
    profile.gains[2] = cal
    path = tmp_path / "Loaded.json"
    profile.save(path)

    captured: dict[str, str] = {}

    def fake_dialog(parent, caption, directory, file_filter):
        captured.update(caption=caption, file_filter=file_filter)
        return str(path), ""

    monkeypatch.setattr(pcw.QFileDialog, "getOpenFileName", staticmethod(fake_dialog))
    window.ui.buttonLoad.click()
    assert captured == {
        "caption": "Kalibrierungsprofil laden",
        "file_filter": "JSON-Dateien (*.json);;Alle Dateien (*)",
    }
    assert window.ui.editProfileName.text() == "Loaded"
    assert window.ui.spinWavelength.value() == pytest.approx(780.0)
    tab = window.ui.tabGains.widget(1)
    assert isinstance(tab, GainCalibrationTab)
    assert tab.ui.tablePoints.rowCount() == 1


def test_cancelling_the_load_dialog_changes_nothing(
    window: PowerCalibrationWindow, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        pcw.QFileDialog, "getOpenFileName", staticmethod(lambda *args, **kwargs: ("", ""))
    )
    window.ui.editProfileName.setText("Keep")
    window.ui.buttonLoad.click()
    assert window.ui.editProfileName.text() == "Keep"


def test_a_broken_profile_file_shows_the_error_dialog(
    window: PowerCalibrationWindow,
    dialogs: DialogRecorder,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    broken = tmp_path / "broken.json"
    broken.write_text("{not json", encoding="utf-8")
    monkeypatch.setattr(
        pcw.QFileDialog, "getOpenFileName", staticmethod(lambda *a, **k: (str(broken), ""))
    )
    window.ui.buttonLoad.click()
    kind, title, text = dialogs.calls[-1]
    assert (kind, title) == ("critical", "Fehler")
    assert text.startswith("Laden fehlgeschlagen:\n")
