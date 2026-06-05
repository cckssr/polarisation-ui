"""Base class for experiment tab widgets.

Each experiment tab (Malus, Ellipsometry, …) subclasses PlotTabBase,
declares its metadata, and implements the lifecycle hooks.  The
TabRegistry gates tabs whose required_modules are not currently injected.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from polarisation_ui.core.models import Frame


class ConnState(Enum):
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    LOST = "lost"


class PlotTabBase(QWidget):
    """Abstract base for all experiment tabs.

    Subclasses must define tab_id and tab_title and implement build().
    All other hooks have default no-op implementations.
    """

    tab_id: str = ""
    tab_title: str = ""
    required_sources: set[str] = set()
    required_modules: set[str] = set()

    # --- outbound signals ----------------------------------------------------
    status_message = Signal(str, str)  # (level, message) — "info"/"warning"/"error"
    filename_hint_changed = Signal()  # emitted when filename_hint or tokens change

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

    # --- lifecycle hooks (override in subclass) ------------------------------

    def build(self) -> None:
        """Construct layout, plots, and controls. Called once before the tab is shown."""

    def on_frame(self, frame: Frame) -> None:
        """Receive a new data frame at the polling rate (~10 Hz)."""

    def on_reset(self) -> None:
        """Clear all buffered data. Called when the user triggers a measurement reset."""

    def on_connection_state(self, state: ConnState) -> None:
        """React to changes in device connection state."""

    def on_activated(self) -> None:
        """Called when this tab becomes the visible/active tab."""

    def on_deactivated(self) -> None:
        """Called when this tab is hidden (another tab activated)."""

    def on_measurement_started(self) -> None:
        """Called when a measurement session starts (enable plot interaction buttons)."""

    def on_measurement_stopped(self) -> None:
        """Called when a measurement session stops (disable plot interaction buttons)."""

    # --- inbound injection ---------------------------------------------------

    def inject_modules(self, modules: dict[str, object]) -> None:
        """Receive host-side module references (e.g. {"kdc101": KdcController})."""

    def restore_points(self, points: list[dict]) -> None:
        """Reload saved points from a prior session. Override in subclasses."""
