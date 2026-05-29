"""Host-side module registry.

Defines the ``HostModule`` protocol and the ``ModuleRegistry`` singleton.
Tabs query ``ModuleRegistry.get(id)`` so they can request actions on
host-side peripherals (e.g. the Thorlabs KDC101 rotation stage).

The protocol is intentionally minimal — add methods only when a real tab
needs them, so the tab code does not have to change when the real driver
replaces a stub.

Usage::

    from polarisation_ui.infrastructure.modules import ModuleRegistry, HostModule
    from polarisation_ui.infrastructure.modules.kdc101_stub import Kdc101Stub

    ModuleRegistry.register(Kdc101Stub())

    kdc = ModuleRegistry.get("kdc101")
    if kdc is not None and kdc.is_connected():
        print(kdc.describe())

Thread-safety: all calls are expected from the Qt main thread; no locking.
"""

from typing import Optional, Protocol, runtime_checkable

from polarisation_ui.infrastructure.logging import Debug


@runtime_checkable
class HostModule(Protocol):
    """Minimal protocol every host-side peripheral module must satisfy."""

    @property
    def id(self) -> str:
        """Unique module identifier, e.g. ``'kdc101'``."""
        ...

    def connect(self) -> bool:
        """Open the connection to the peripheral; return True on success."""
        ...

    def disconnect(self) -> None:
        """Close the connection gracefully."""
        ...

    def is_connected(self) -> bool:
        """Return True when the peripheral is reachable."""
        ...

    def describe(self) -> str:
        """Human-readable one-line description for diagnostics / log output."""
        ...


class ModuleRegistry:
    """Registry for host-side peripheral modules.

    Class-level dict — one registry per process.  Tabs receive the registry
    contents via ``PlotTabBase.inject_modules()`` so they remain decoupled from
    this class.

    ``clear()`` is provided for unit tests that need a clean slate.
    """

    _registry: dict[str, HostModule] = {}

    @classmethod
    def register(cls, module: HostModule) -> None:
        """Register *module*; overwrites any previous entry with the same id."""
        cls._registry[module.id] = module
        Debug.info(f"ModuleRegistry: registered '{module.id}' — {module.describe()}")

    @classmethod
    def unregister(cls, module_id: str) -> None:
        """Remove the module for *module_id*; no-op if not registered."""
        if module_id in cls._registry:
            del cls._registry[module_id]
            Debug.info(f"ModuleRegistry: unregistered '{module_id}'")

    @classmethod
    def get(cls, module_id: str) -> Optional[HostModule]:
        """Return the module for *module_id*, or ``None`` if not registered."""
        return cls._registry.get(module_id)

    @classmethod
    def all(cls) -> dict[str, HostModule]:
        """Return a shallow copy of the full registry."""
        return dict(cls._registry)

    @classmethod
    def clear(cls) -> None:
        """Remove all registered modules.  Primarily for unit tests."""
        cls._registry.clear()
