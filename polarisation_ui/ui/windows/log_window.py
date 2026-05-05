"""
Live log output window.

Displays the application log in a non-modal dialog. Log records are forwarded
from Python's logging system via a thread-safe Qt signal, so it works correctly
even when records originate from worker threads (e.g. ReconnectWorker).
"""

import logging

from PySide6.QtCore import QObject, Qt, Signal, Slot
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QPlainTextEdit,
    QVBoxLayout,
)

from polarisation_ui.infrastructure.logging import Debug


class _SignalEmitter(QObject):
    """Minimal QObject used solely to own a Qt signal for cross-thread delivery."""

    message = Signal(str)


class _LogWindowHandler(logging.Handler):
    """
    Thread-safe bridge between Python's logging system and a Qt signal.

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

    MAX_LINES = 2000

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Log-Ausgabe")
        self.resize(820, 480)

        self._text = QPlainTextEdit(self)
        self._text.setReadOnly(True)
        mono = QFont()
        mono.setStyleHint(QFont.StyleHint.Monospace)
        mono.setFamily("Menlo")
        mono.setPointSize(11)
        self._text.setFont(mono)
        self._text.setMaximumBlockCount(self.MAX_LINES)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close, self)
        buttons.rejected.connect(self.hide)

        layout = QVBoxLayout(self)
        layout.addWidget(self._text)
        layout.addWidget(buttons)

        self._handler = _LogWindowHandler()
        self._handler.connect(self._append_line)
        Debug.add_handler(self._handler)

    @Slot(str)
    def _append_line(self, text: str) -> None:
        self._text.appendPlainText(text)
        cursor = self._text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self._text.setTextCursor(cursor)

    def closeEvent(self, event) -> None:
        Debug.remove_handler(self._handler)
        event.accept()
