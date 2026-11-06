"""KdcPanel: device list, status, position and offset, buttons."""

from __future__ import annotations


def test_the_panel_shows_dashes_and_the_connect_text_initially(kdc, config) -> None:
    dash = config.text("kdc_panel.text_none")
    assert kdc.title() == config.text("kdc_panel.self")
    assert kdc.ui.valuePosition.text() == dash
    assert kdc.ui.valueOffset.text() == dash
    assert kdc.ui.buttonConnect.text() == config.text("kdc_panel.text_connect")


def test_the_device_list_keeps_the_selection_and_names_the_empty_case(kdc, config) -> None:
    kdc.set_devices([("A", "Mock A"), ("B", "Mock B")])
    kdc.ui.comboDevice.setCurrentIndex(1)
    kdc.set_devices([("A", "Mock A"), ("B", "Mock B")])
    assert kdc.ui.comboDevice.currentData() == "B"
    kdc.set_devices([])
    assert kdc.ui.comboDevice.count() == 1
    assert kdc.ui.comboDevice.currentText() == config.text("kdc_panel.text_no_device")
    assert kdc.ui.comboDevice.currentData() is None


def test_connect_requests_the_selected_connection_id_or_none(qtbot, kdc) -> None:
    kdc.set_devices([("ID-1", "Mock")])
    with qtbot.waitSignal(kdc.connect_requested) as blocker:
        kdc.ui.buttonConnect.click()
    assert blocker.args == ["ID-1"]
    kdc.set_devices([])
    with qtbot.waitSignal(kdc.connect_requested) as blocker:
        kdc.ui.buttonConnect.click()
    assert blocker.args == [None]


def test_the_button_disconnects_while_connected(qtbot, kdc, config) -> None:
    kdc.set_connected(True)
    assert kdc.ui.buttonConnect.text() == config.text("kdc_panel.text_disconnect")
    with qtbot.waitSignal(kdc.disconnect_requested):
        kdc.ui.buttonConnect.click()


def test_the_other_buttons_emit_their_intent_signals(qtbot, kdc) -> None:
    for signal, button in (
        (kdc.refresh_requested, kdc.ui.buttonRefresh),
        (kdc.home_requested, kdc.ui.buttonHome),
        (kdc.zero_requested, kdc.ui.buttonZero),
        (kdc.offset_reset_requested, kdc.ui.buttonOffsetReset),
    ):
        with qtbot.waitSignal(signal):
            button.click()


def test_the_controls_can_be_enabled_individually(kdc) -> None:
    kdc.set_controls(False, True, False, True)
    ui = kdc.ui
    assert [
        b.isEnabled()
        for b in (ui.buttonConnect, ui.buttonHome, ui.buttonZero, ui.buttonOffsetReset)
    ] == [
        False,
        True,
        False,
        True,
    ]


def test_position_and_offset_show_degrees_or_a_dash(kdc, config) -> None:
    kdc.set_position(30.0)
    assert kdc.ui.valuePosition.text().endswith("°") and "30" in kdc.ui.valuePosition.text()
    kdc.set_position(None)
    assert kdc.ui.valuePosition.text() == config.text("kdc_panel.text_none")
    kdc.set_offset(25.5)
    assert kdc.ui.valueOffset.text().startswith("25")
    kdc.set_offset(0.0)
    assert kdc.ui.valueOffset.text() == config.text("kdc_panel.text_none")
