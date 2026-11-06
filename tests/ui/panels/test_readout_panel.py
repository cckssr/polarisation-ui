"""ReadoutPanel: LCD readouts and the single gain selector."""

from __future__ import annotations

import math

import pytest


def test_the_four_displays_show_the_values(readout) -> None:
    readout.show_angles(123.45, 6.5)
    readout.show_voltage(2.5)
    readout.show_power(3.0e-5)
    assert readout.ui.lcdSampleAngle.value() == pytest.approx(123.45)
    assert readout.ui.lcdDetectorAngle.value() == pytest.approx(6.5)
    assert readout.ui.lcdVoltage.value() == pytest.approx(2500.0)  # mV
    assert readout.ui.lcdPower.value() == pytest.approx(30.0)  # µW


def test_a_missing_value_shows_dashes_instead_of_a_number(readout) -> None:
    readout.show_voltage(2.5)
    readout.show_voltage(math.nan)
    readout.show_power(math.nan)
    assert readout.ui.lcdVoltage.value() == 0.0 and readout.ui.lcdPower.value() == 0.0


def test_reset_zeroes_all_displays(readout) -> None:
    readout.show_angles(10.0, 20.0)
    readout.show_voltage(1.0)
    readout.reset_displays()
    for lcd in (readout.ui.lcdSampleAngle, readout.ui.lcdDetectorAngle, readout.ui.lcdVoltage):
        assert lcd.value() == 0.0


def test_the_gain_buttons_use_their_stage_as_id_and_emit_the_clicked_stage(qtbot, readout) -> None:
    for stage in (1, 2, 3, 4):
        assert readout.ui.buttonGroupGain.id(getattr(readout.ui, f"buttonGain{stage}")) == stage
    with qtbot.waitSignal(readout.gain_selected) as blocker:
        readout.ui.buttonGain3.click()
    assert blocker.args == [3]
    assert readout.ui.buttonGain3.isChecked()


def test_set_gain_checks_a_button_without_emitting_and_clear_gain_unchecks_all(
    qtbot, readout
) -> None:
    with qtbot.assertNotEmitted(readout.gain_selected):
        readout.set_gain(2)
    assert readout.ui.buttonGain2.isChecked()
    readout.clear_gain()
    assert not any(getattr(readout.ui, f"buttonGain{s}").isChecked() for s in (1, 2, 3, 4))
    readout.set_gain(4)
    assert readout.ui.buttonGain4.isChecked() and not readout.ui.buttonGain2.isChecked()


def test_auto_emits_for_the_user_and_is_set_silently_from_outside(qtbot, readout) -> None:
    with qtbot.waitSignal(readout.gain_auto_toggled) as blocker:
        readout.ui.buttonGainAuto.setChecked(True)
    assert blocker.args == [True]
    with qtbot.assertNotEmitted(readout.gain_auto_toggled):
        readout.set_gain_auto(False)
    assert not readout.ui.buttonGainAuto.isChecked()


def test_manual_and_auto_gain_buttons_are_enabled_independently(readout) -> None:
    readout.set_gain_enabled(manual=False, auto=True)
    assert not readout.ui.buttonGain1.isEnabled() and readout.ui.buttonGainAuto.isEnabled()
    readout.set_gain_enabled(manual=True, auto=False)
    assert readout.ui.buttonGain4.isEnabled() and not readout.ui.buttonGainAuto.isEnabled()


def test_auto_without_power_windows_is_disabled_with_an_explanation(readout, config) -> None:
    readout.set_gain_auto_unavailable()
    assert not readout.ui.buttonGainAuto.isEnabled()
    assert readout.ui.buttonGainAuto.toolTip() == config.text("readout_panel.gain_auto_no_limits")
