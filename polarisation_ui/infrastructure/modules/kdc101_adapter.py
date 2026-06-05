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

    def __init__(self, kdc: "KDC101Polariser") -> None:
        self._kdc = kdc

    def connect(self) -> bool:
        return self._kdc.is_connected()

    def disconnect(self) -> None:
        self._kdc.disconnect()

    def is_connected(self) -> bool:
        return self._kdc.is_connected()

    def describe(self) -> str:
        return f"KDC101 polariser stage (connected={self._kdc.is_connected()})"
