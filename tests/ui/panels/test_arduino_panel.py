"""ArduinoPanel: port selection, connect button, status LED."""

from __future__ import annotations

from polarisation_ui.ui.common.status_led import LED_GREEN, LED_RED, LED_YELLOW


def test_the_panel_shows_the_configured_german_texts(arduino, config) -> None:
    strings = config.section("ui")["arduino_panel"]
    assert arduino.title() == strings["self"]
    assert arduino.ui.labelPort.text() == strings["labelPort"]
    assert arduino.ui.buttonConnect.text() == strings["text_connect"]
    assert arduino.ui.comboPort.toolTip() == strings["comboPort@tooltip"]


def test_the_connect_button_requests_the_selected_port(qtbot, arduino) -> None:
    arduino.set_ports(["/dev/a", "/dev/b"])
    arduino.ui.comboPort.setCurrentIndex(1)
    with qtbot.waitSignal(arduino.connect_requested) as blocker:
        arduino.ui.buttonConnect.click()
    assert blocker.args == ["/dev/b"]


def test_the_button_disconnects_while_connected_and_says_so(qtbot, arduino, config) -> None:
    arduino.set_connected(True)
    assert arduino.ui.buttonConnect.text() == config.text("arduino_panel.text_disconnect")
    with qtbot.waitSignal(arduino.disconnect_requested):
        arduino.ui.buttonConnect.click()
    arduino.set_connected(False)
    assert arduino.ui.buttonConnect.text() == config.text("arduino_panel.text_connect")


def test_the_refresh_button_asks_for_a_new_port_list(qtbot, arduino) -> None:
    with qtbot.waitSignal(arduino.refresh_requested):
        arduino.ui.buttonRefreshPorts.click()


def test_an_empty_port_list_shows_the_missing_text_as_the_only_entry(arduino) -> None:
    arduino.set_ports([], "Keine Ports")
    assert arduino.ui.comboPort.count() == 1
    assert arduino.current_port() == "Keine Ports"
    arduino.set_ports(["/dev/a"], "Keine Ports")
    assert arduino.ui.comboPort.count() == 1 and arduino.current_port() == "/dev/a"


def test_connecting_locks_the_port_selection(arduino) -> None:
    arduino.set_connecting(True)
    assert not arduino.ui.comboPort.isEnabled()
    assert not arduino.ui.buttonRefreshPorts.isEnabled()
    arduino.set_connecting(False)
    assert arduino.ui.comboPort.isEnabled() and arduino.ui.buttonRefreshPorts.isEnabled()


def test_the_status_shows_text_and_led_colour_for_every_state(arduino) -> None:
    for state, style in (
        ("ok", LED_GREEN),
        ("busy", LED_YELLOW),
        ("warn", LED_YELLOW),
        ("error", LED_RED),
        ("off", LED_RED),
        ("unknown", LED_RED),
    ):
        arduino.set_state(state, f"Text {state}")
        assert arduino.ui.valueStatus.text() == f"Text {state}"
        assert arduino.ui.ledStatus.styleSheet() == style
