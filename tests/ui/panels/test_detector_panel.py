"""DetectorPanel: PD-TIA page (id, profile, averaging, dark current) and PM400 page."""

from __future__ import annotations

from pathlib import Path

from polarisation_ui.ui.common.status_led import LED_YELLOW


def test_the_inner_tabs_have_the_configured_titles(detector, config) -> None:
    strings = config.section("ui")["detector_panel"]
    tabs = detector.ui.tabDetector
    assert [tabs.tabText(i) for i in range(tabs.count())] == [
        strings["tabPdtia@tab"],
        strings["tabPm400@tab"],
    ]
    assert detector.title() == strings["self"]


def test_the_photodetector_selector_emits_only_for_user_changes(qtbot, detector) -> None:
    with qtbot.assertNotEmitted(detector.pdtia_id_selected):
        detector.set_pdtia_ids(["PD-1", "PD-2"])
        detector.select_pdtia_id("PD-2")
    assert detector.current_pdtia_id() == "PD-2"
    with qtbot.waitSignal(detector.pdtia_id_selected) as blocker:
        detector.ui.comboPdtiaId.setCurrentIndex(0)
    assert blocker.args == ["PD-1"]


def test_the_profile_selector_lists_stems_and_emits_the_path(qtbot, detector, tmp_path) -> None:
    paths = [tmp_path / "cal-a.json", tmp_path / "cal-b.json"]
    with qtbot.assertNotEmitted(detector.profile_selected):
        detector.set_profiles(paths, "")
    assert [detector.ui.comboProfile.itemText(i) for i in range(2)] == ["cal-a", "cal-b"]
    assert detector.current_profile() is None  # the placeholder is shown
    with qtbot.waitSignal(detector.profile_selected) as blocker:
        detector.ui.comboProfile.setCurrentIndex(1)
    assert blocker.args == [Path(paths[1])]
    detector.set_profiles(paths, "cal-a")
    assert detector.current_profile() == paths[0]
    with qtbot.assertNotEmitted(detector.profile_selected):
        detector.select_profile_name("cal-b")
        detector.select_profile_name("")
    assert detector.current_profile() is None


def test_the_reload_and_calibration_buttons_emit_their_signals(qtbot, detector) -> None:
    with qtbot.waitSignal(detector.profile_reload_requested):
        detector.ui.buttonReloadProfiles.click()
    with qtbot.waitSignal(detector.calibration_requested):
        detector.ui.buttonOpenCalibration.click()


def test_the_pdtia_averaging_controls_emit_and_set_silently(qtbot, detector) -> None:
    with qtbot.assertNotEmitted(detector.averaging_changed):
        detector.set_averaging(True, 7)
    assert detector.averaging() == (True, 7)
    with qtbot.waitSignal(detector.averaging_changed) as blocker:
        detector.ui.checkPdtiaAverage.setChecked(False)
    assert blocker.args == [False, 7]
    assert not detector.ui.spinPdtiaAverages.isEnabled()


def test_the_dark_current_controls_lock_while_busy_and_show_the_offset(
    qtbot, detector, config
) -> None:
    with qtbot.waitSignal(detector.dark_tare_requested):
        detector.ui.buttonDarkTare.click()
    with qtbot.waitSignal(detector.dark_reset_requested):
        detector.ui.buttonDarkReset.click()
    detector.set_dark_busy(True)
    assert not detector.ui.buttonDarkTare.isEnabled()
    assert not detector.ui.buttonDarkReset.isEnabled()
    detector.set_dark_busy(False)
    assert detector.ui.buttonDarkTare.isEnabled()
    assert detector.ui.valueDarkOffset.text() == config.text("detector_panel.dark_offset_none")
    detector.set_dark_offset(0.0125)
    assert detector.ui.valueDarkOffset.text().endswith(" mV")
    assert "12.500" in detector.ui.valueDarkOffset.text()


def test_the_status_row_shows_text_and_led(detector) -> None:
    detector.set_state("warn", "Sättigung")
    assert detector.ui.valuePdtiaStatus.text() == "Sättigung"
    assert detector.ui.ledPdtiaStatus.styleSheet() == LED_YELLOW


def test_the_pm400_resource_list_prefers_the_current_then_the_remembered_entry(detector) -> None:
    detector.set_pm400_resources(["R1", "R2"], preferred="R2")
    assert detector.current_pm400_resource() == "R2"
    detector.ui.comboPm400Resource.setCurrentIndex(0)
    detector.set_pm400_resources(["R1", "R2"], preferred="R2")
    assert detector.current_pm400_resource() == "R1"
    detector.select_pm400_resource("R2")
    assert detector.current_pm400_resource() == "R2"
    detector.set_pm400_resources([])
    assert detector.ui.comboPm400Resource.count() == 0


def test_the_pm400_connect_button_requests_connect_or_disconnect(qtbot, detector, config) -> None:
    detector.set_pm400_resources(["R1"])
    assert not detector.ui.buttonPm400Zero.isEnabled()
    with qtbot.waitSignal(detector.pm400_connect_requested) as blocker:
        detector.ui.buttonPm400Connect.click()
    assert blocker.args == ["R1"]
    detector.set_pm400_connected(True)
    assert detector.ui.buttonPm400Connect.text() == config.text("detector_panel.text_disconnect")
    assert detector.ui.buttonPm400Zero.isEnabled()
    with qtbot.waitSignal(detector.pm400_disconnect_requested):
        detector.ui.buttonPm400Connect.click()
    with qtbot.waitSignal(detector.pm400_zero_requested):
        detector.ui.buttonPm400Zero.click()


def test_the_pm400_wavelength_emits_only_for_user_changes(qtbot, detector) -> None:
    with qtbot.assertNotEmitted(detector.pm400_wavelength_changed):
        detector.set_pm400_wavelength(532.0)
    assert detector.ui.spinWavelength.value() == 532.0
    with qtbot.waitSignal(detector.pm400_wavelength_changed) as blocker:
        detector.ui.spinWavelength.setValue(800.0)
    assert blocker.args == [800.0]


def test_the_pm400_refresh_button_and_resource_change_emit_signals(qtbot, detector) -> None:
    with qtbot.waitSignal(detector.pm400_refresh_requested):
        detector.ui.buttonPm400Refresh.click()
    detector.set_pm400_resources(["R1", "R2"])
    with qtbot.waitSignal(detector.pm400_resource_changed) as blocker:
        detector.ui.comboPm400Resource.setCurrentIndex(1)
    assert blocker.args == ["R2"]
