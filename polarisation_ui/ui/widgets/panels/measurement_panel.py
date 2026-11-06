"""Measurement panel: start, stop and reset of the data acquisition."""

from __future__ import annotations

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QGroupBox, QWidget

from polarisation_ui.infrastructure.config import AppConfig
from polarisation_ui.pyqt.ui_measurement_panel import Ui_MeasurementPanel
from polarisation_ui.ui.i18n import apply_strings


class MeasurementPanel(QGroupBox):
    """Three buttons; the owner decides when each is allowed."""

    start_requested = Signal()
    stop_requested = Signal()
    reset_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build the form; every button starts disabled (no device connected yet)."""
        super().__init__(parent)
        self.ui = Ui_MeasurementPanel()
        self.ui.setupUi(self)
        self.ui.buttonStart.clicked.connect(self.start_requested)
        self.ui.buttonStop.clicked.connect(self.stop_requested)
        self.ui.buttonReset.clicked.connect(self.reset_requested)
        for button in (self.ui.buttonStart, self.ui.buttonStop, self.ui.buttonReset):
            button.setEnabled(False)

    def apply_config(self, config: AppConfig) -> None:
        """Apply the ``ui.measurement_panel`` strings."""
        apply_strings(self, config.section("ui").get("measurement_panel", {}))

    @Slot(bool)
    def set_start_enabled(self, enabled: bool) -> None:
        """Start is possible once the Arduino is connected."""
        self.ui.buttonStart.setEnabled(enabled)

    @Slot(bool)
    def set_running(self, running: bool) -> None:
        """While running only Stop is available; afterwards Start and Reset are."""
        self.ui.buttonStart.setEnabled(not running)
        self.ui.buttonStop.setEnabled(running)
        self.ui.buttonReset.setEnabled(not running)

    @Slot(bool)
    def set_reset_enabled(self, enabled: bool) -> None:
        """Reset needs recorded data."""
        self.ui.buttonReset.setEnabled(enabled)
