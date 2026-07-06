"""HostModule adapter wrapping KDC101Polariser for the ModuleRegistry.

This thin adapter exists solely to satisfy the ``HostModule`` protocol so
``TabRegistry.available(modules)`` can gate tabs that declare
``required_modules = {"kdc101"}``.  Motion calls (home, move_to,
get_position_deg) are made directly on the ``KDC101Polariser`` instance
injected via ``PlotTabBase.inject_modules()``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from polarisation_ui.infrastructure.devices.kdc101_polariser import KDC101Polariser


class KDC101ModuleAdapter:
    """Wraps ``KDC101Polariser`` as a ``HostModule`` for registry/gating."""

    id: str = "kdc101"

    def __init__(self, kdc: KDC101Polariser) -> None:
        """Wrap an already-constructed KDC101Polariser instance."""
        self._kdc = kdc

    def connect(self) -> bool:
        """Return whether the wrapped stage is connected (connection is managed elsewhere)."""
        return self._kdc.is_connected()

    def disconnect(self) -> None:
        """Disconnect the wrapped stage."""
        self._kdc.disconnect()

    def is_connected(self) -> bool:
        """Return whether the wrapped stage is currently connected."""
        return self._kdc.is_connected()

    def describe(self) -> str:
        """Return a human-readable label including current connection state."""
        return f"KDC101 polariser stage (connected={self._kdc.is_connected()})"
