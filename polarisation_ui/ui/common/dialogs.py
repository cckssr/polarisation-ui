"""Standardised QMessageBox wrappers for the UI layer."""

from typing import Optional
from PySide6.QtWidgets import QMessageBox, QWidget


def show_error(
    parent: Optional[QWidget],
    title: str,
    message: str,
    detailed_text: Optional[str] = None,
) -> None:
    """Show a critical-error dialog."""
    dialog = QMessageBox(parent)
    dialog.setIcon(QMessageBox.Icon.Critical)
    dialog.setWindowTitle(title)
    dialog.setText(message)
    if detailed_text:
        dialog.setDetailedText(detailed_text)
    dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
    dialog.exec()
