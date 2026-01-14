"""
Status bar management utilities.

Provides helper functions for updating the status bar with
consistent formatting and behavior.
"""

from PySide6.QtWidgets import QStatusBar
from typing import Optional


class StatusBarManager:
    """
    Manager for application status bar.

    Provides methods to show different types of status messages
    with consistent formatting and timeout behavior.
    """

    DEFAULT_TIMEOUT = 3000  # 3 seconds

    def __init__(self, status_bar: QStatusBar):
        """
        Initialize status bar manager.

        Args:
            status_bar: QStatusBar instance to manage
        """
        self.status_bar = status_bar

    def show_message(self, message: str, timeout: Optional[int] = None) -> None:
        """
        Show a temporary message in the status bar.

        Args:
            message: Message text to display
            timeout: Time in milliseconds before clearing (None = permanent)
        """
        if timeout is None:
            timeout = self.DEFAULT_TIMEOUT

        self.status_bar.showMessage(message, timeout)

    def show_info(self, message: str, timeout: Optional[int] = None) -> None:
        """
        Show informational message.

        Args:
            message: Info message
            timeout: Display duration in milliseconds
        """
        self.show_message(f"ℹ️ {message}", timeout)

    def show_success(self, message: str, timeout: Optional[int] = None) -> None:
        """
        Show success message.

        Args:
            message: Success message
            timeout: Display duration in milliseconds
        """
        self.show_message(f"✓ {message}", timeout)

    def show_warning(self, message: str, timeout: Optional[int] = None) -> None:
        """
        Show warning message.

        Args:
            message: Warning message
            timeout: Display duration in milliseconds
        """
        if timeout is None:
            timeout = 5000  # Warnings stay longer
        self.show_message(f"⚠️ {message}", timeout)

    def show_error(self, message: str, timeout: Optional[int] = None) -> None:
        """
        Show error message.

        Args:
            message: Error message
            timeout: Display duration in milliseconds
        """
        if timeout is None:
            timeout = 8000  # Errors stay even longer
        self.show_message(f"❌ {message}", timeout)

    def show_connection_status(self, connected: bool, device_name: str) -> None:
        """
        Show device connection status.

        Args:
            connected: Whether device is connected
            device_name: Name of the device
        """
        if connected:
            self.show_success(f"{device_name} connected", timeout=2000)
        else:
            self.show_warning(f"{device_name} disconnected", timeout=None)

    def clear(self) -> None:
        """Clear status bar message."""
        self.status_bar.clearMessage()

    def set_permanent(self, message: str) -> None:
        """
        Set permanent status message.

        Args:
            message: Message to display permanently
        """
        self.status_bar.showMessage(message, 0)
