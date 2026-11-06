"""EncoderDebugDialog: built entirely from encoder_debug.ui, strings from config.json."""

from __future__ import annotations

import re
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QLabel, QPushButton, QToolButton

from polarisation_ui.infrastructure.config import AppConfig
from polarisation_ui.infrastructure.device_manager import GoniometerDeviceManager
from polarisation_ui.infrastructure.devices.pm400 import PM400PowerMeter
from polarisation_ui.pyqt.sync_texts import PYQT_DIR
from polarisation_ui.ui.common.status_led import LED_GRAY, LED_GREEN, LED_RED
from polarisation_ui.ui.windows.encoder_debug_window import EncoderDebugDialog

WINDOW_SOURCE = (
    Path(__file__).resolve().parents[2] / "polarisation_ui" / "ui" / "windows"
) / "encoder_debug_window.py"

# Widgets that used to be built in Python and now come from the Designer form.
MOVED_WIDGETS = (
    "groupConnection",
    "labelPort",
    "comboPort",
    "buttonRefreshPorts",
    "buttonConnect",
    "valueConnectionStatus",
    "labelSampleInverted",
    "checkSampleInverted",
    "tabAds",
    "groupAdcLive",
    "ledAdcPresent",
    "lcdAdcVoltage",
    "ledAdcDrdy",
    "groupAdcRegisters",
    "editReg0",
    "editReg1",
    "editReg2",
    "editReg3",
    "editLastRaw",
    "groupAdcConfig",
    "editMux",
    "editGain",
    "editRate",
    "editMode",
    "editFir",
    "editVref",
    "buttonReadAdcConfig",
    "groupPdtia",
    "editPdtiaStage",
    "editPdtiaPattern",
    "tabRawStream",
    "labelRawStreamNotice",
    "editRawStream",
    "buttonClearRawStream",
    "tabSelfTest",
    "labelSelfTestInfo",
    "buttonRunSelfTest",
    "editSelfTest",
)


@pytest.fixture
def device_manager() -> GoniometerDeviceManager:
    return GoniometerDeviceManager()


@pytest.fixture
def dialog(qtbot, device_manager, config: AppConfig) -> EncoderDebugDialog:
    dlg = EncoderDebugDialog(device_manager, config=config)
    qtbot.addWidget(dlg)
    return dlg


@pytest.fixture
def standalone_dialog(qtbot, device_manager, config: AppConfig) -> EncoderDebugDialog:
    dlg = EncoderDebugDialog(device_manager, standalone=True, config=config)
    qtbot.addWidget(dlg)
    return dlg


@pytest.fixture
def mock_stack() -> Iterator[tuple[GoniometerDeviceManager, str]]:
    """A device manager connected to a PTY MockArduino."""
    if sys.platform == "win32":
        pytest.skip("PTY not available on Windows")
    from polarisation_ui.infrastructure.mocks import MockArduino

    mock = MockArduino(start_angle_a=10.0, start_angle_b=20.0)
    port = mock.start()
    dm = GoniometerDeviceManager()
    assert dm.connect_encoders(port=port)
    yield dm, port
    dm.disconnect_all()
    mock.stop()


# ── Construction in both modes ─────────────────────────────────────────────────


def test_the_embedded_dialog_hides_the_connection_group(dialog: EncoderDebugDialog) -> None:
    assert dialog.ui.groupConnection.isHidden()
    assert dialog.windowTitle() == "Encoder Debug"


def test_the_standalone_dialog_shows_the_connection_group(
    standalone_dialog: EncoderDebugDialog,
) -> None:
    dlg = standalone_dialog
    assert not dlg.ui.groupConnection.isHidden()
    assert dlg.windowTitle() == "Encoder Debug (Standalone)"
    assert dlg.ui.valueConnectionStatus.text() == "Nicht verbunden"
    assert dlg.ui.comboPort.count() >= 1
    # Nothing is connected: the diagnostic tabs stay disabled.
    assert not dlg.ui.tabWidget.isEnabled()


def test_the_standalone_dialog_connects_and_disconnects_through_the_form(
    qtbot, standalone_dialog: EncoderDebugDialog, mock_stack
) -> None:
    dm, port = mock_stack
    dm.disconnect_all()
    dlg = standalone_dialog
    dlg.ui.comboPort.clear()
    dlg.ui.comboPort.addItem(port)

    dlg.ui.buttonConnect.click()
    assert dlg.ui.valueConnectionStatus.text() == f"Verbunden: {port}"
    assert dlg.ui.buttonConnect.text() == "Trennen"
    assert dlg.ui.tabWidget.isEnabled()
    assert dlg.ui.editIdn.text() not in ("", "–")

    dlg.ui.buttonConnect.click()
    assert dlg.ui.valueConnectionStatus.text() == "Getrennt"
    assert dlg.ui.buttonConnect.text() == "Verbinden"
    assert not dlg.ui.tabWidget.isEnabled()


def test_a_failed_standalone_connection_is_reported(
    standalone_dialog: EncoderDebugDialog,
) -> None:
    dlg = standalone_dialog
    dlg.ui.comboPort.clear()
    dlg.ui.comboPort.addItem("/dev/does-not-exist")
    dlg.ui.buttonConnect.click()
    assert dlg.ui.valueConnectionStatus.text() == "Verbindung fehlgeschlagen"
    assert dlg.ui.buttonConnect.isEnabled()


def test_main_py_debug_only_path_constructs_the_dialog(qtbot, device_manager) -> None:
    """``main.py --debug-only`` builds the dialog exactly like this."""
    dlg = EncoderDebugDialog(device_manager, standalone=True)
    qtbot.addWidget(dlg)
    dlg.show()
    assert dlg.isVisible()
    assert not dlg.ui.groupConnection.isHidden()


# ── pm400 regression ───────────────────────────────────────────────────────────


def test_the_main_window_call_with_a_pm400_argument_constructs_the_dialog(
    qtbot, device_manager
) -> None:
    pm400 = PM400PowerMeter()
    dlg = EncoderDebugDialog(
        device_manager,
        sample_inverted=True,
        data_controller=None,
        pm400=pm400,
        parent=None,
    )
    qtbot.addWidget(dlg)
    assert dlg._pm400 is pm400


def test_the_pm400_argument_is_optional(dialog: EncoderDebugDialog) -> None:
    assert dialog._pm400 is None


# ── Everything comes from the Designer form ────────────────────────────────────


@pytest.mark.parametrize("name", MOVED_WIDGETS)
def test_the_formerly_programmatic_widgets_are_designer_children(
    dialog: EncoderDebugDialog, name: str
) -> None:
    found = dialog.findChild(QObject, name)
    assert found is not None, f"{name} is missing from encoder_debug.ui"
    assert getattr(dialog.ui, name) is found


def test_the_tabs_are_declared_in_the_form_in_order(dialog: EncoderDebugDialog) -> None:
    tabs = dialog.ui.tabWidget
    assert [tabs.tabText(i) for i in range(tabs.count())] == [
        "Messwerte",
        "System",
        "SCPI Terminal",
        "ADS1220",
        "Raw Stream",
        "Selbsttest",
    ]


def test_the_window_module_constructs_no_widgets() -> None:
    source = WINDOW_SOURCE.read_text(encoding="utf-8")
    constructed = re.findall(
        r"\bQ(?:Widget|Label|PushButton|GroupBox|LineEdit|Frame|LCDNumber|"
        r"ComboBox|ToolButton|CheckBox|PlainTextEdit|[HV]BoxLayout|"
        r"FormLayout|SpacerItem)\(",
        source,
    )
    assert constructed == []
    assert not re.search(r"[äöüÄÖÜß]", source), "German literal left in the window module"


def test_the_designer_names_use_the_oct_prefixes() -> None:
    names = re.findall(
        r'<widget class="(\w+)" name="(\w+)"', (PYQT_DIR / "encoder_debug.ui").read_text()
    )
    legacy = [n for _, n in names if re.match(r"(btn|lbl|gb|cb|spb|le|te|pbar)[A-Z]", n)]
    assert legacy == []


# ── Strings ────────────────────────────────────────────────────────────────────


def test_the_configured_german_strings_are_applied(dialog: EncoderDebugDialog) -> None:
    ui = dialog.ui
    assert ui.groupControl.title() == "Steuerung"
    assert ui.buttonRefresh.text() == "Aktualisieren"
    assert ui.checkAutoRefresh.text() == "Auto-Refresh"
    assert ui.spinRefreshInterval.suffix() == " ms"
    assert ui.groupAdcLive.title() == "Live-Messwerte"
    assert ui.labelAdcPresent.text() == "ADS1220 vorhanden:"
    assert ui.buttonReadAdcConfig.text() == "Konfiguration lesen"
    assert ui.buttonRunSelfTest.text() == "Selbsttest ausführen  (DIAG:SELF?)"
    assert ui.buttonClearRawStream.text() == "Löschen"
    assert ui.labelSampleInverted.text() == "Probe invertiert:"
    assert ui.editRawStream.placeholderText() == "Warte auf Frames …"
    assert ui.editSelfTest.placeholderText() == "Noch kein Test durchgeführt."
    assert ui.ledAdcDrdy.toolTip() == "Zeitbasierte Bereitschaft (DRDY-Pin nicht angeschlossen)"
    assert [ui.comboEncoderSelect.itemText(i) for i in range(3)] == [
        "A – Sample",
        "B – Detektor",
        "Beide",
    ]


def test_every_encoder_debug_key_resolves_to_a_widget(config: AppConfig) -> None:
    strings = config.section("ui").get("encoder_debug", {})
    assert strings, "ui.encoder_debug is empty"
    names = {
        key.partition("@")[0]
        for key in strings
        if "_" not in key.partition("@")[0] and key.partition("@")[0] != "self"
    }
    found = set(re.findall(r'name="(\w+)"', (PYQT_DIR / "encoder_debug.ui").read_text()))
    assert names <= found, f"keys without a widget: {sorted(names - found)}"


def test_every_code_looked_up_config_key_exists(config: AppConfig) -> None:
    source = WINDOW_SOURCE.read_text(encoding="utf-8")
    text_keys = set(re.findall(r'config\.text\(f?"encoder_debug\.(\w+)"', source))
    text_keys |= set(re.findall(r'config\.get\("ui\.encoder_debug\.(\w+)"', source))
    text_keys |= set(re.findall(r'"(tab_title_\w+)"', source))
    assert text_keys
    for key in text_keys:
        assert config.get(f"ui.encoder_debug.{key}") is not None, key
    message_keys = set(re.findall(r'_msg\(\s*f?"(\w+)"', source))
    message_keys |= set(re.findall(r"_msg\(\s*f?'(\w+)'", source))
    assert message_keys
    for key in message_keys:
        assert isinstance(config.get(f"messages.encoder_debug.{key}"), str), key


def test_every_visible_label_and_button_has_text(dialog: EncoderDebugDialog) -> None:
    for cls in (QLabel, QPushButton, QToolButton):
        for widget in dialog.findChildren(cls):
            name = widget.objectName()
            if not name.startswith(("label", "button")):
                continue  # live values are filled by code; the tab bar has internal buttons
            assert widget.text(), f"{name} has no text"
            assert widget.text() != name


# ── Behaviour of the moved widgets ─────────────────────────────────────────────


def test_the_sys_info_row_reflects_the_inverted_sample_setting(
    qtbot, device_manager, config: AppConfig
) -> None:
    dlg = EncoderDebugDialog(device_manager, sample_inverted=True, config=config)
    qtbot.addWidget(dlg)
    assert dlg.ui.checkSampleInverted.isChecked()
    assert not dlg.ui.checkSampleInverted.isEnabled()
    assert dlg.ui.formSysInfo.rowCount() == 4


def test_without_a_data_controller_the_raw_stream_tab_shows_the_notice(
    dialog: EncoderDebugDialog,
) -> None:
    assert not dialog.ui.labelRawStreamNotice.isHidden()
    assert dialog.ui.editRawStream.isHidden()
    assert dialog.ui.buttonClearRawStream.isHidden()
    assert "Strg+D" in dialog.ui.labelRawStreamNotice.text()


def test_with_a_data_controller_the_raw_stream_tab_logs_frames(
    qtbot, mock_stack, config: AppConfig
) -> None:
    from polarisation_ui.ui.controllers.data_controller import DataController

    dm, _port = mock_stack
    controller = DataController(dm, use_mock_intensity=True)
    dlg = EncoderDebugDialog(dm, data_controller=controller, config=config)
    qtbot.addWidget(dlg)
    try:
        assert dlg.ui.labelRawStreamNotice.isHidden()
        assert not dlg.ui.editRawStream.isHidden()

        controller.raw_frame.emit("DATA:FRAME seq=1")
        assert "DATA:FRAME seq=1" in dlg.ui.editRawStream.toPlainText()
        dlg.ui.buttonClearRawStream.click()
        assert dlg.ui.editRawStream.toPlainText() == ""
        dlg.close()
    finally:
        controller.cleanup()


def test_refresh_without_a_device_turns_all_leds_red_or_gray(
    dialog: EncoderDebugDialog,
) -> None:
    dialog._refresh()
    assert dialog.ui.ledConnA.styleSheet() == LED_RED
    assert dialog.ui.ledAdcPresent.styleSheet() == LED_RED
    assert dialog.ui.ledAdcDrdy.styleSheet() == LED_GRAY
    assert dialog.ui.ledErrorA.styleSheet() == LED_GRAY


def test_the_leds_start_gray(dialog: EncoderDebugDialog) -> None:
    for name in ("ledConnA", "ledCofB", "ledAdcPresent", "ledAdcDrdy"):
        assert getattr(dialog.ui, name).styleSheet() == LED_GRAY


def test_actions_without_a_device_report_the_configured_messages(
    dialog: EncoderDebugDialog,
) -> None:
    ui = dialog.ui
    dialog._set_tabs_enabled(True)
    ui.buttonRunSelfTest.click()
    assert ui.editSelfTest.toPlainText() == "Fehler: Gerät nicht verbunden."
    ui.buttonReadScpiErrors.click()
    assert ui.editScpiErrors.toPlainText() == "Nicht verbunden"
    ui.editCommandInput.setText("*IDN?")
    ui.buttonSendCommand.click()
    assert "[Nicht verbunden]" in ui.editTerminalLog.toPlainText()


def test_the_connected_dialog_fills_the_ads_tab_and_runs_the_self_test(
    qtbot, mock_stack, config: AppConfig
) -> None:
    dm, _port = mock_stack
    dlg = EncoderDebugDialog(dm, config=config)
    qtbot.addWidget(dlg)
    dlg._refresh_timer.stop()
    assert dlg.ui.tabWidget.isEnabled()

    dlg.ui.buttonRefresh.click()
    assert dlg.ui.ledAdcPresent.styleSheet() == LED_GREEN
    assert dlg.ui.editReg0.text().startswith("0x")
    assert dlg.ui.editLastRaw.text().startswith("0x")

    dlg.ui.buttonReadAdcConfig.click()
    assert dlg.ui.editMux.text() not in ("", "–") or dlg.ui.editGain.text() not in ("", "–")

    dlg.ui.buttonRunSelfTest.click()
    assert "DIAG:SELF?" in dlg.ui.editSelfTest.toPlainText()
