"""Standardised QMessageBox wrappers for the UI layer."""

from typing import Optional
from PySide6.QtWidgets import QMessageBox, QWidget


def show_error(
    parent: Optional[QWidget],
    title: str,
    message: str,
    detailed_text: Optional[str] = None,
) -> None:
    """Show a critical-error dialog.

    Args:
        parent (QWidget): The parent widget for the dialog.
        title (str): The title of the error dialog.
        message (str): The main error message to display.
        detailed_text (str, optional): Additional details about the error. Defaults to None.
    """
    dialog = QMessageBox(parent)
    dialog.setIcon(QMessageBox.Icon.Critical)
    dialog.setWindowTitle(title)
    dialog.setText(message)
    if detailed_text:
        dialog.setDetailedText(detailed_text)
    dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
    dialog.exec()
