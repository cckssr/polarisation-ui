"""MeasurementPanel and SavePanel."""

from __future__ import annotations


def test_every_measurement_button_starts_disabled(measurement) -> None:
    for button in (
        measurement.ui.buttonStart,
        measurement.ui.buttonStop,
        measurement.ui.buttonReset,
    ):
        assert not button.isEnabled()


def test_the_measurement_buttons_emit_their_intent_signals(qtbot, measurement) -> None:
    for button in (
        measurement.ui.buttonStart,
        measurement.ui.buttonStop,
        measurement.ui.buttonReset,
    ):
        button.setEnabled(True)
    with qtbot.waitSignal(measurement.start_requested):
        measurement.ui.buttonStart.click()
    with qtbot.waitSignal(measurement.stop_requested):
        measurement.ui.buttonStop.click()
    with qtbot.waitSignal(measurement.reset_requested):
        measurement.ui.buttonReset.click()


def test_running_leaves_only_stop_enabled(measurement) -> None:
    measurement.set_running(True)
    ui = measurement.ui
    assert [b.isEnabled() for b in (ui.buttonStart, ui.buttonStop, ui.buttonReset)] == [
        False,
        True,
        False,
    ]
    measurement.set_running(False)
    assert [b.isEnabled() for b in (ui.buttonStart, ui.buttonStop, ui.buttonReset)] == [
        True,
        False,
        True,
    ]
    measurement.set_reset_enabled(False)
    assert not ui.buttonReset.isEnabled()
    measurement.set_start_enabled(False)
    assert not ui.buttonStart.isEnabled()


def test_the_measurement_panel_has_its_configured_texts(measurement, config) -> None:
    strings = config.section("ui")["measurement_panel"]
    assert measurement.title() == strings["self"]
    assert measurement.ui.buttonStart.text() == strings["buttonStart"]


def test_the_group_selector_offers_the_letters_and_starts_empty(save) -> None:
    combo = save.ui.comboGroup
    assert combo.count() == 24 and combo.itemText(0) == "A"
    assert combo.currentIndex() == -1
    assert not save.ui.buttonSave.isEnabled()


def test_choosing_a_group_emits_the_letter_and_clearing_emits_an_empty_string(qtbot, save) -> None:
    with qtbot.waitSignal(save.group_changed) as blocker:
        save.ui.comboGroup.setCurrentIndex(2)
    assert blocker.args == ["C"]
    with qtbot.waitSignal(save.group_changed) as blocker:
        save.ui.comboGroup.setCurrentIndex(-1)
    assert blocker.args == [""]


def test_set_group_team_and_suffix_show_values_without_emitting(qtbot, save) -> None:
    with qtbot.assertNotEmitted(save.group_changed), qtbot.assertNotEmitted(save.team_changed):
        save.set_group("D")
        save.set_team("Team Rot")
    assert save.ui.comboGroup.currentText() == "D" and save.ui.editTeam.text() == "Team Rot"
    save.set_group("")
    assert save.ui.comboGroup.currentIndex() == -1


def test_typed_team_and_suffix_are_emitted_and_a_trailing_blank_is_kept(qtbot, save) -> None:
    with qtbot.waitSignal(save.team_changed) as blocker:
        save.ui.editTeam.setText("Team ")
    assert blocker.args == ["Team "]
    save.set_team("Team")  # the controller reports the stripped name back
    assert save.ui.editTeam.text() == "Team "
    with qtbot.waitSignal(save.suffix_changed) as blocker:
        save.ui.editSuffix.setText("run1")
    assert blocker.args == ["run1"]


def test_the_save_button_and_the_file_name_and_the_lock(qtbot, save) -> None:
    save.set_save_enabled(True)
    with qtbot.waitSignal(save.save_requested):
        save.ui.buttonSave.click()
    save.set_filename("/tmp/messung.csv")
    assert save.ui.valueFilename.text() == "/tmp/messung.csv"
    save.set_prefix_locked(True)
    assert not save.ui.comboGroup.isEnabled() and not save.ui.editTeam.isEnabled()
    save.set_prefix_locked(False)
    assert save.ui.comboGroup.isEnabled() and save.ui.editTeam.isEnabled()


def test_the_suffix_input_can_be_hidden(save) -> None:
    save.set_suffix_visible(False)
    assert save.ui.editSuffix.isHidden() and save.ui.labelSuffix.isHidden()
    save.set_suffix_visible(True)
    assert not save.ui.editSuffix.isHidden()


def test_the_dropbox_link_opens_externally_and_the_hint_is_configured(save, config) -> None:
    assert save.ui.labelDropbox.openExternalLinks()
    assert "href" in save.ui.labelDropbox.text()
    assert save.ui.labelHint.text() == config.text("save_panel.labelHint")
