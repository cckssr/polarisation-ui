"""Status-message hub and LED vocabulary shared by the controllers.

Controllers never touch widgets: they report progress through ``StatusHub`` (status bar and event
log) and through ``(led, text)`` signals whose ``led`` is one of the ``LED_*`` states below. The
main window maps both to widgets.
"""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal

# LED states carried by the controllers' ``*_state_changed`` signals.
LED_OFF = "off"  # not connected
LED_OK = "ok"  # connected / healthy
LED_BUSY = "busy"  # connecting
LED_WARN = "warn"  # degraded (sensor fault, saturation, calibration missing)
LED_ERROR = "error"  # failed / no signal

# Rows of the Arduino status panel (``ConnectionController.row_state_changed``).
ROW_ARDUINO = "arduino"
ROW_SAMPLE = "sample"
ROW_DETECTOR_STAGE = "detector_stage"
ROW_DETECTOR = "detector"

LEVELS = ("info", "success", "warning", "error")


class StatusHub(QObject):
    """Collects status messages from all controllers; the window shows them in the status bar."""

    message = Signal(str, str)  # level ("info"/"success"/"warning"/"error"), text

    def info(self, text: str) -> None:
        """Report a neutral message."""
        self.message.emit("info", text)

    def success(self, text: str) -> None:
        """Report a completed action."""
        self.message.emit("success", text)

    def warning(self, text: str) -> None:
        """Report something that needs attention."""
        self.message.emit("warning", text)

    def error(self, text: str) -> None:
        """Report a failure."""
        self.message.emit("error", text)
