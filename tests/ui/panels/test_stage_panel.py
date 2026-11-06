"""StagePanel: one form for the sample and the detector stage."""

from __future__ import annotations

import pytest

from polarisation_ui.ui.common.status_led import LED_GREEN
from polarisation_ui.ui.widgets.panels.stage_panel import StagePanel


def test_the_title_and_tooltips_follow_the_role(sample_stage, detector_stage, config) -> None:
    strings = config.section("ui")["stage_panel"]
    assert sample_stage.title() == strings["title_sample"]
    assert detector_stage.title() == strings["title_detector"]
    assert sample_stage.ui.buttonZero.toolTip() == strings["tooltip_zero_sample"]
    assert detector_stage.ui.buttonZero.toolTip() == strings["tooltip_zero_detector"]
    assert "Proben" in sample_stage.ui.checkAverage.toolTip()
    assert "Detektor" in detector_stage.ui.checkAverage.toolTip()


def test_only_the_detector_role_shows_the_180_degree_button(sample_stage, detector_stage) -> None:
    assert sample_stage.ui.button180.isHidden()
    assert not detector_stage.ui.button180.isHidden()


def test_an_unknown_role_is_rejected(qtbot, config) -> None:
    panel = StagePanel()
    qtbot.addWidget(panel)
    with pytest.raises(ValueError):
        panel.apply_config(config, "analyser")


def test_the_buttons_emit_their_intent_signals(qtbot, detector_stage) -> None:
    with qtbot.waitSignal(detector_stage.zero_requested):
        detector_stage.ui.buttonZero.click()
    with qtbot.waitSignal(detector_stage.zero_180_requested):
        detector_stage.ui.button180.click()


def test_the_averaging_controls_emit_the_settings_as_shown(qtbot, sample_stage) -> None:
    sample_stage.set_averaging(True, 5)
    with qtbot.waitSignal(sample_stage.averaging_changed) as blocker:
        sample_stage.ui.spinAverages.setValue(9)
    assert blocker.args == [True, 9]
    with qtbot.waitSignal(sample_stage.averaging_changed) as blocker:
        sample_stage.ui.checkAverage.setChecked(False)
    assert blocker.args == [False, 9]
    assert not sample_stage.ui.spinAverages.isEnabled()
    assert sample_stage.averaging() == (False, 9)


def test_set_averaging_shows_the_values_without_emitting(qtbot, sample_stage) -> None:
    with qtbot.assertNotEmitted(sample_stage.averaging_changed):
        sample_stage.set_averaging(False, 12)
    assert sample_stage.averaging() == (False, 12)
    assert not sample_stage.ui.spinAverages.isEnabled()


def test_zeroing_can_be_disabled_during_a_measurement(sample_stage, detector_stage) -> None:
    detector_stage.set_zeroing_enabled(False)
    assert not detector_stage.ui.buttonZero.isEnabled()
    assert not detector_stage.ui.button180.isEnabled()
    detector_stage.set_zeroing_enabled(True)
    assert detector_stage.ui.buttonZero.isEnabled() and detector_stage.ui.button180.isEnabled()


def test_the_status_shows_text_and_led(sample_stage) -> None:
    sample_stage.set_state("ok", "Encoder A")
    assert sample_stage.ui.valueStatus.text() == "Encoder A"
    assert sample_stage.ui.ledStatus.styleSheet() == LED_GREEN
