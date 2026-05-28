"""
ConnectionBanner — non-blocking reconnect status banner.

Three visible states:
  OK          — hidden.
  RECONNECTING — amber background, countdown to next attempt.
  LOST        — red background, offers "Exportieren…" action.
"""

from enum import Enum

from PySide6.QtCore import QTimer, Signal, Slot
from PySide6.QtWidgets import QFrame

from polarisation_ui.pyqt.ui_connection_banner import Ui_ConnectionBanner

_STYLE_RECONNECTING = (
    "QFrame { background-color: #FFA500; border: none; }"
    "QLabel { color: #000; font-weight: bold; }"
    "QPushButton { background-color: #CC8000; color: #FFF; }"
)
_STYLE_LOST = (
    "QFrame { background-color: #CC0000; border: none; }"
    "QLabel { color: #FFF; font-weight: bold; }"
    "QPushButton { background-color: #880000; color: #FFF; }"
)


class BannerState(Enum):
    OK = "ok"
    RECONNECTING = "reconnecting"
    LOST = "lost"


class ConnectionBanner(QFrame):
    """Persistent non-blocking reconnect status banner."""

    MAX_ATTEMPTS: int = 10

    export_requested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.ui = Ui_ConnectionBanner()
        self.ui.setupUi(self)

        self._state = BannerState.OK
        self._attempt: int = 0
        self._countdown_s: int = 0

        self._countdown_timer = QTimer(self)
        self._countdown_timer.setInterval(1000)
        self._countdown_timer.timeout.connect(self._tick_countdown)

        self.ui.btnBannerExport.clicked.connect(self.export_requested)
        self.setVisible(False)

    # ── Public API ────────────────────────────────────────────────────────────

    def set_reconnecting(self, attempt: int, delay_s: float) -> None:
        """Show RECONNECTING state with countdown to next attempt."""
        self._state = BannerState.RECONNECTING
        self._attempt = attempt
        self._countdown_s = max(1, int(delay_s))
        self.ui.btnBannerExport.setVisible(False)
        self.setStyleSheet(_STYLE_RECONNECTING)
        self._update_reconnecting_text()
        self.setVisible(True)
        self._countdown_timer.start()

    def set_lost(self) -> None:
        """Show LOST state with export button."""
        self._countdown_timer.stop()
        self._state = BannerState.LOST
        self.ui.lblBannerText.setText("Verbindung verloren – Daten exportieren?")
        self.ui.btnBannerExport.setVisible(True)
        self.setStyleSheet(_STYLE_LOST)
        self.setVisible(True)

    def set_ok(self) -> None:
        """Hide the banner (connection OK / reconnected)."""
        self._countdown_timer.stop()
        self._state = BannerState.OK
        self.setVisible(False)

    # ── Internal ──────────────────────────────────────────────────────────────

    @Slot()
    def _tick_countdown(self) -> None:
        if self._state != BannerState.RECONNECTING:
            self._countdown_timer.stop()
            return
        self._countdown_s = max(0, self._countdown_s - 1)
        self._update_reconnecting_text()

    def _update_reconnecting_text(self) -> None:
        self.ui.lblBannerText.setText(
            f"Verbindung wird wiederhergestellt – "
            f"nächster Versuch in {self._countdown_s}s "
            f"(Versuch {self._attempt}/{self.MAX_ATTEMPTS})"
        )
