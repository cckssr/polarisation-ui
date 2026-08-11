"""HostModule adapter wrapping KDC101Polariser for the ModuleRegistry.

This adapter satisfies the ``HostModule`` protocol so
``TabRegistry.available(modules)`` can gate tabs that declare
``required_modules = {"kdc101"}``.  It is also the object tabs receive via
``PlotTabBase.inject_modules()`` (``ModuleRegistry.all()`` is the only source
of the ``"kdc101"`` entry), so motion calls (home, move_to, get_position_deg)
are exposed here as pass-throughs to the wrapped ``KDC101Polariser`` instance.
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

    # ── Motion pass-throughs ──────────────────────────────────────────────────
    # Tabs (malus_tab, waveplate_tab) and their qt_threads workers receive this
    # adapter as their "kdc" handle via inject_modules() and call these
    # directly, so they must be forwarded to the wrapped KDC101Polariser.

    def home(self, wait: bool = True, timeout: float = 120.0) -> None:
        """Home the wrapped stage; see ``KDC101Polariser.home``."""
        self._kdc.home(wait=wait, timeout=timeout)

    def move_to(self, angle_deg: float, wait: bool = True, timeout: float = 60.0) -> None:
        """Move the wrapped stage; see ``KDC101Polariser.move_to``."""
        self._kdc.move_to(angle_deg, wait=wait, timeout=timeout)

    def get_position_deg(self) -> float:
        """Return the wrapped stage's current position in degrees."""
        return self._kdc.get_position_deg()
