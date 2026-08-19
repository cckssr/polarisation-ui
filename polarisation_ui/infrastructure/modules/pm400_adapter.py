"""HostModule adapter wrapping PM400PowerMeter for the ModuleRegistry.

Named ``pm400_adapter.py`` rather than ``pm400.py`` because that filename is
already taken by the vendored PyMeasure ``ThorlabsPM400`` driver in this
package — see ``infrastructure/modules/pm400.py``.

Mirrors ``kdc101_adapter.py``: this is the object tabs receive via
``PlotTabBase.inject_modules()`` (``ModuleRegistry.all()`` is the only source
of the ``"pm400"`` entry), so anything not defined here (read_power_W,
set_wavelength_nm, ...) falls through ``__getattr__`` to the wrapped
``PM400PowerMeter``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from polarisation_ui.infrastructure.devices.pm400 import PM400PowerMeter


class PM400ModuleAdapter:
    """Wraps ``PM400PowerMeter`` as a ``HostModule`` for registry/gating."""

    id: str = "pm400"

    def __init__(self, pm: PM400PowerMeter) -> None:
        """Wrap an already-constructed PM400PowerMeter instance."""
        self._pm = pm

    def connect(self) -> bool:
        """Return whether the wrapped meter is connected (connection is managed elsewhere)."""
        return self._pm.is_connected()

    def disconnect(self) -> None:
        """Disconnect the wrapped meter."""
        self._pm.disconnect()

    def is_connected(self) -> bool:
        """Return whether the wrapped meter is currently connected."""
        return self._pm.is_connected()

    def describe(self) -> str:
        """Return a human-readable label including current connection state."""
        return f"PM400 power meter (connected={self._pm.is_connected()})"

    def __getattr__(self, name: str) -> Any:
        """Forward anything not defined above straight to the wrapped PM400PowerMeter."""
        return getattr(self._pm, name)
