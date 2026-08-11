"""HostModule adapter wrapping KDC101Polariser for the ModuleRegistry.

This adapter satisfies the ``HostModule`` protocol so
``TabRegistry.available(modules)`` can gate tabs that declare
``required_modules = {"kdc101"}``.  It is also the object tabs receive via
``PlotTabBase.inject_modules()`` (``ModuleRegistry.all()`` is the only source
of the ``"kdc101"`` entry), so anything not defined here (home, move_to,
get_position_deg, ...) falls through ``__getattr__`` to the wrapped
``KDC101Polariser`` — new driver methods therefore work through the adapter
automatically, with nothing to keep in sync by hand.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

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

    def __getattr__(self, name: str) -> Any:
        """Forward anything not defined above straight to the wrapped KDC101Polariser."""
        return getattr(self._kdc, name)
