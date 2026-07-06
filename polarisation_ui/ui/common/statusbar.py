"""Status bar management utilities.

Provides helper functions for updating the status bar with
consistent formatting and behavior.
"""

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QStatusBar

if TYPE_CHECKING:
    from polarisation_ui.ui.widgets.event_log_panel import EventLogPanel


class StatusBarManager:
    """Manager for application status bar with optional EventLogPanel mirror."""

    DEFAULT_TIMEOUT = 3000  # 3 seconds

    def __init__(self, status_bar: QStatusBar) -> None:
        """Wrap the given QStatusBar; no EventLogPanel mirror until set_mirror()."""
        self.status_bar = status_bar
        self._mirror: EventLogPanel | None = None

    def set_mirror(self, panel: "EventLogPanel") -> None:
        """Attach an EventLogPanel that receives a copy of every message."""
        self._mirror = panel

    def show_message(self, message: str, timeout: int | None = None) -> None:
        """Show a message on the status bar and mirror it to the event log if attached."""
        if timeout is None:
            timeout = self.DEFAULT_TIMEOUT
        self.status_bar.showMessage(message, timeout)
        if self._mirror is not None:
            self._mirror.append(message)

    def show_info(self, message: str, timeout: int | None = None) -> None:
        """Show an info-styled message (ℹ️ prefix)."""
        self.show_message(f"ℹ️ {message}", timeout)

    def show_success(self, message: str, timeout: int | None = None) -> None:
        """Show a success-styled message (✓ prefix)."""
        self.show_message(f"✓ {message}", timeout)

    def show_warning(self, message: str, timeout: int | None = None) -> None:
        """Show a warning-styled message (⚠️ prefix), default 5 s timeout."""
        if timeout is None:
            timeout = 5000
        self.show_message(f"⚠️ {message}", timeout)

    def show_error(self, message: str, timeout: int | None = None) -> None:
        """Show an error-styled message (❌ prefix), default 8 s timeout."""
        if timeout is None:
            timeout = 8000
        self.show_message(f"❌ {message}", timeout)

    def clear(self) -> None:
        """Clear the current status bar message."""
        self.status_bar.clearMessage()
