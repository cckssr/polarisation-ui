"""Rotation-stage panel (one form, used for the sample and the detector encoder)."""

from __future__ import annotations

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QGroupBox, QWidget

from polarisation_ui.infrastructure.config import AppConfig
from polarisation_ui.pyqt.ui_stage_panel import Ui_StagePanel
from polarisation_ui.ui.common.status_led import set_led_state
from polarisation_ui.ui.i18n import apply_strings

ROLES = ("sample", "detector")


class StagePanel(QGroupBox):
    """Encoder status, moving average and zeroing of one rotation stage.

    ``role`` selects the title and tooltips from ``ui.stage_panel``; only the ``detector`` role
    shows the 180° calibration button.
    """

    zero_requested = Signal()
    zero_180_requested = Signal()
    averaging_changed = Signal(bool, int)  # moving average on, number of values

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build the form; call :meth:`apply_config` to choose the role."""
        super().__init__(parent)
        self.ui = Ui_StagePanel()
        self.ui.setupUi(self)
        self.role = ROLES[0]
        self.ui.buttonZero.clicked.connect(self.zero_requested)
        self.ui.button180.clicked.connect(self.zero_180_requested)
        self.ui.checkAverage.toggled.connect(self.ui.spinAverages.setEnabled)
        self.ui.checkAverage.toggled.connect(self._emit_averaging)
        self.ui.spinAverages.valueChanged.connect(self._emit_averaging)

    def apply_config(self, config: AppConfig, role: str = "sample") -> None:
        """Apply the ``ui.stage_panel`` strings for ``role`` (``sample`` or ``detector``)."""
        if role not in ROLES:
            raise ValueError(f"unknown stage role {role!r}")
        self.role = role
        strings = config.section("ui").get("stage_panel", {})
        apply_strings(self, strings)
        self.setTitle(config.text(f"stage_panel.title_{role}"))
        self.ui.checkAverage.setToolTip(config.text(f"stage_panel.tooltip_average_{role}"))
        self.ui.spinAverages.setToolTip(config.text("stage_panel.tooltip_averages"))
        self.ui.buttonZero.setToolTip(config.text(f"stage_panel.tooltip_zero_{role}"))
        self.ui.button180.setVisible(role == "detector")

    # ---- setters (driven by the controller) -----------------------------------------------
    def set_state(self, led: str, text: str) -> None:
        """Show the encoder status (``led`` is a controller LED state)."""
        set_led_state(self.ui.ledStatus, self.ui.valueStatus, text, led)

    def set_zeroing_enabled(self, enabled: bool) -> None:
        """No zeroing while a measurement runs."""
        self.ui.buttonZero.setEnabled(enabled)
        self.ui.button180.setEnabled(enabled)

    def set_averaging(self, on: bool, count: int) -> None:
        """Show the averaging settings without emitting :attr:`averaging_changed`."""
        for widget in (self.ui.checkAverage, self.ui.spinAverages):
            widget.blockSignals(True)
        self.ui.checkAverage.setChecked(on)
        self.ui.spinAverages.setValue(count)
        self.ui.spinAverages.setEnabled(on)
        for widget in (self.ui.checkAverage, self.ui.spinAverages):
            widget.blockSignals(False)

    def averaging(self) -> tuple[bool, int]:
        """The averaging settings as shown: ``(on, count)``."""
        return self.ui.checkAverage.isChecked(), self.ui.spinAverages.value()

    @Slot()
    def _emit_averaging(self) -> None:
        self.averaging_changed.emit(*self.averaging())
