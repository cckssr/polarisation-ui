"""Live readout panel: sample / detector angle, voltage, power and the PD-TIA gain buttons."""

from __future__ import annotations

import math

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QGroupBox, QPushButton, QWidget

from polarisation_ui.core.formatting import fmt_angle, fmt_stat
from polarisation_ui.infrastructure.config import AppConfig
from polarisation_ui.pyqt.ui_readout_panel import Ui_ReadoutPanel
from polarisation_ui.ui.i18n import apply_strings

GAIN_STAGES = (1, 2, 3, 4)
_NO_VALUE = "----"


class ReadoutPanel(QGroupBox):
    """Big LCD readouts and the (single) gain-stage selector."""

    gain_selected = Signal(int)  # PD-TIA gain stage 1-4
    gain_auto_toggled = Signal(bool)

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build the form; the gain buttons use their stage number as button-group id."""
        super().__init__(parent)
        self.ui = Ui_ReadoutPanel()
        self.ui.setupUi(self)
        self._no_limits_tooltip = ""
        for stage in GAIN_STAGES:
            self.ui.buttonGroupGain.setId(self._gain_button(stage), stage)
        self.ui.buttonGroupGain.idClicked.connect(self.gain_selected)
        self.ui.buttonGainAuto.toggled.connect(self.gain_auto_toggled)

    def apply_config(self, config: AppConfig) -> None:
        """Apply the ``ui.readout_panel`` strings."""
        self._no_limits_tooltip = config.text("readout_panel.gain_auto_no_limits")
        apply_strings(self, config.section("ui").get("readout_panel", {}))

    def _gain_button(self, stage: int) -> QPushButton:
        return getattr(self.ui, f"buttonGain{stage}")

    # ---- displays -------------------------------------------------------------------------
    @Slot(float, float)
    def show_angles(self, sample_deg: float, detector_deg: float) -> None:
        """Show the (already averaged) sample and detector-arm angles."""
        self.ui.lcdSampleAngle.display(fmt_angle(sample_deg))
        self.ui.lcdDetectorAngle.display(fmt_angle(detector_deg))

    @Slot(float)
    def show_voltage(self, volts: float) -> None:
        """Show the detector voltage in mV (``----`` for NaN)."""
        self.ui.lcdVoltage.display(_NO_VALUE if math.isnan(volts) else fmt_stat(volts * 1000.0))

    @Slot(float)
    def show_power(self, watts: float) -> None:
        """Show the calibrated power in µW (``----`` for NaN)."""
        self.ui.lcdPower.display(_NO_VALUE if math.isnan(watts) else fmt_stat(watts * 1e6))

    def reset_displays(self) -> None:
        """Zero all four LCDs (a fresh connection)."""
        for lcd in (
            self.ui.lcdSampleAngle,
            self.ui.lcdDetectorAngle,
            self.ui.lcdVoltage,
            self.ui.lcdPower,
        ):
            lcd.display(0.00)

    # ---- gain buttons ---------------------------------------------------------------------
    @Slot(int)
    def set_gain(self, stage: int) -> None:
        """Check the button of ``stage`` without emitting :attr:`gain_selected`."""
        button = self.ui.buttonGroupGain.button(stage)
        if button is not None and not button.isChecked():
            button.blockSignals(True)
            button.setChecked(True)
            button.blockSignals(False)

    @Slot()
    def clear_gain(self) -> None:
        """No gain stage is active."""
        group = self.ui.buttonGroupGain
        checked = group.checkedButton()
        if checked is not None:
            group.setExclusive(False)
            checked.setChecked(False)
            group.setExclusive(True)

    @Slot(bool)
    def set_gain_auto(self, checked: bool) -> None:
        """Show the AUTO state without emitting :attr:`gain_auto_toggled`."""
        button = self.ui.buttonGainAuto
        if button.isChecked() != checked:
            button.blockSignals(True)
            button.setChecked(checked)
            button.blockSignals(False)

    def set_gain_enabled(self, manual: bool, auto: bool) -> None:
        """Enable the manual stage buttons and the AUTO button independently."""
        for stage in GAIN_STAGES:
            self._gain_button(stage).setEnabled(manual)
        self.ui.buttonGainAuto.setEnabled(auto)

    def set_gain_auto_unavailable(self) -> None:
        """AUTO needs power windows in the config: disable it and say why."""
        self.ui.buttonGainAuto.setEnabled(False)
        self.ui.buttonGainAuto.setToolTip(self._no_limits_tooltip)
