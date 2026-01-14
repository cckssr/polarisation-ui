"""
Common dialog utilities for the UI layer.

Provides standardized PySide6 dialogs for info, warnings, errors, and confirmations.
Centralizes dialog styling and behavior across the application.
"""

from PySide6.QtWidgets import QMessageBox, QWidget
from typing import Optional


def show_info(
    parent: Optional[QWidget],
    title: str,
    message: str,
    detailed_text: Optional[str] = None,
) -> None:
    """
    Show information dialog.

    Args:
        parent: Parent widget
        title: Dialog title
        message: Main message text
        detailed_text: Optional detailed information
    """
    dialog = QMessageBox(parent)
    dialog.setIcon(QMessageBox.Icon.Information)
    dialog.setWindowTitle(title)
    dialog.setText(message)

    if detailed_text:
        dialog.setDetailedText(detailed_text)

    dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
    dialog.exec()


def show_warning(
    parent: Optional[QWidget],
    title: str,
    message: str,
    detailed_text: Optional[str] = None,
) -> None:
    """
    Show warning dialog.

    Args:
        parent: Parent widget
        title: Dialog title
        message: Main message text
        detailed_text: Optional detailed information
    """
    dialog = QMessageBox(parent)
    dialog.setIcon(QMessageBox.Icon.Warning)
    dialog.setWindowTitle(title)
    dialog.setText(message)

    if detailed_text:
        dialog.setDetailedText(detailed_text)

    dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
    dialog.exec()


def show_error(
    parent: Optional[QWidget],
    title: str,
    message: str,
    detailed_text: Optional[str] = None,
) -> None:
    """
    Show error dialog.

    Args:
        parent: Parent widget
        title: Dialog title
        message: Main message text (primary error info)
        detailed_text: Optional detailed technical information
    """
    dialog = QMessageBox(parent)
    dialog.setIcon(QMessageBox.Icon.Critical)
    dialog.setWindowTitle(title)
    dialog.setText(message)

    if detailed_text:
        dialog.setDetailedText(detailed_text)

    dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
    dialog.exec()


def ask_confirmation(
    parent: Optional[QWidget],
    title: str,
    message: str,
    detailed_text: Optional[str] = None,
) -> bool:
    """
    Show confirmation dialog with Yes/No buttons.

    Args:
        parent: Parent widget
        title: Dialog title
        message: Question to ask user
        detailed_text: Optional detailed information

    Returns:
        bool: True if user clicked Yes, False if No
    """
    dialog = QMessageBox(parent)
    dialog.setIcon(QMessageBox.Icon.Question)
    dialog.setWindowTitle(title)
    dialog.setText(message)

    if detailed_text:
        dialog.setDetailedText(detailed_text)

    dialog.setStandardButtons(
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    dialog.setDefaultButton(QMessageBox.StandardButton.No)

    result = dialog.exec()
    return result == QMessageBox.StandardButton.Yes


def show_critical_error(
    parent: Optional[QWidget], message: str, exception: Optional[Exception] = None
) -> None:
    """
    Show critical error dialog, typically for unrecoverable errors.

    Args:
        parent: Parent widget
        message: User-friendly error message
        exception: Optional exception with technical details
    """
    detailed = None
    if exception:
        detailed = f"{type(exception).__name__}: {str(exception)}"

    show_error(
        parent=parent, title="Critical Error", message=message, detailed_text=detailed
    )


def show_connection_error(
    parent: Optional[QWidget], device_name: str, error_details: Optional[str] = None
) -> None:
    """
    Show device connection error dialog.

    Args:
        parent: Parent widget
        device_name: Name of the device that failed to connect
        error_details: Optional technical error details
    """
    message = f"Failed to connect to {device_name}."

    show_error(
        parent=parent,
        title="Connection Error",
        message=message,
        detailed_text=error_details,
    )
