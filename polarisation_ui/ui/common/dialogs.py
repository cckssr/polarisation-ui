"""Standardised QMessageBox wrappers for the UI layer."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox, QWidget


def show_error(
    parent: QWidget | None,
    title: str,
    message: str,
    detailed_text: str | None = None,
) -> None:
    """Show a critical-error dialog.

    Args:
        parent (QWidget): The parent widget for the dialog.
        title (str): The title of the error dialog.
        message (str): The main error message to display.
        detailed_text (str, optional): Additional details about the error. Defaults to None.
    """
    dialog = QMessageBox(parent)
    # Without this, the dialog's C++ object stays parented to `parent` forever
    # (Qt only auto-deletes it on close, not on Python GC), so repeated calls
    # leak one QMessageBox each.
    dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
    dialog.setIcon(QMessageBox.Icon.Critical)
    dialog.setWindowTitle(title)
    dialog.setText(message)
    if detailed_text:
        dialog.setDetailedText(detailed_text)
    dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
    dialog.exec()
