"""Live log output window.

Displays the application log in a non-modal dialog. Log records are forwarded
from Python's logging system via a thread-safe Qt signal, so it works correctly
even when records originate from worker threads (e.g. ReconnectWorker).
"""

import logging

from PySide6.QtCore import QObject, Qt, Signal, Slot
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QDialog

from polarisation_ui.infrastructure.logging import Debug
from polarisation_ui.pyqt.ui_log_window import Ui_LogWindow


class _SignalEmitter(QObject):
    """Minimal QObject used solely to own a Qt signal for cross-thread delivery."""

    message = Signal(str)


class _LogWindowHandler(logging.Handler):
    """Thread-safe bridge between Python's logging system and a Qt signal.

    ``emit()`` is called by the logging framework from any thread.  Emitting
    a Qt signal is safe from any thread — Qt queues delivery to the main thread
    when the signal is connected with QueuedConnection.
    """

    def __init__(self) -> None:
        super().__init__()
        self._emitter = _SignalEmitter()
        self.setFormatter(
            logging.Formatter("%(asctime)s  %(levelname)-8s  %(message)s")
        )

    def connect(self, slot) -> None:
        self._emitter.message.connect(slot, Qt.ConnectionType.QueuedConnection)

    def emit(self, record: logging.LogRecord) -> None:
        try:
            self._emitter.message.emit(self.format(record))
        except Exception:
            self.handleError(record)


class LogWindow(QDialog):
    """Non-modal dialog that shows the live application log."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.ui = Ui_LogWindow()
        self.ui.setupUi(self)
        self.ui.buttonBox.rejected.connect(self.hide)

        self._handler = _LogWindowHandler()
        self._handler.connect(self._append_line)
        Debug.add_handler(self._handler)

    @Slot(str)
    def _append_line(self, text: str) -> None:
        self.ui.textLog.appendPlainText(text)
        cursor = self.ui.textLog.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.ui.textLog.setTextCursor(cursor)

    def closeEvent(self, event) -> None:
        Debug.remove_handler(self._handler)
        event.accept()
