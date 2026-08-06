"""EventLogPanel — timestamped scrollback panel for application events.

Mirrors every message written to StatusBarManager so the user has
persistent scrollback beyond the status bar's 1-line display.
Hosted as a QDockWidget; toggle via the Einstellungen menu action.
"""

from datetime import datetime

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget

from polarisation_ui.pyqt.ui_event_log_panel import Ui_EventLogPanel


class EventLogPanel(QWidget):
    """Timestamped event log with fixed scrollback (500 lines)."""

    def __init__(self, parent=None) -> None:
        """Build the panel UI (empty scrollback until append() is called)."""
        super().__init__(parent)
        self.ui = Ui_EventLogPanel()
        self.ui.setupUi(self)

    @Slot(str)
    def append(self, message: str) -> None:
        """Append a timestamped line to the log."""
        ts = datetime.now().strftime("%H:%M:%S")
        self.ui.textLog.appendPlainText(f"[{ts}] {message}")
