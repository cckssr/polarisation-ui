"""
KDC101 stub — placeholder host-side module.

Satisfies the ``HostModule`` protocol without importing any Thorlabs SDK.
Swap this for the real driver when hardware integration is implemented;
the real driver should be modelled on ``calibration_tool/devices/kdc101_stage.py``.

The stub exists so:
- ``ModuleRegistry`` can be wired up and queried from day one.
- ``PlotTabBase`` subclasses with ``required_modules={"kdc101"}`` are shown /
  hidden correctly without any hardware present (stub reports is_connected=True).
- Tests can exercise the registry without a real KDC101 device.
"""

from polarisation_ui.infrastructure.logging import Debug
from polarisation_ui.infrastructure.modules import HostModule


class Kdc101Stub:
    """
    Stub implementation of ``HostModule`` for the Thorlabs KDC101 stepper controller.

    All methods are no-ops that log at DEBUG level.  ``is_connected()`` always
    returns ``True`` so that tabs with ``required_modules={"kdc101"}`` become
    visible when the stub is registered, allowing UI development without hardware.
    """

    # ── HostModule protocol ───────────────────────────────────────────────────

    @property
    def id(self) -> str:
        return "kdc101"

    def connect(self) -> bool:
        Debug.info("Kdc101Stub.connect() — stub, no hardware action")
        return True

    def disconnect(self) -> None:
        Debug.info("Kdc101Stub.disconnect() — stub, no hardware action")

    def is_connected(self) -> bool:
        """Stub always reports connected so tabs become visible."""
        return True

    def describe(self) -> str:
        return "Thorlabs KDC101 (stub — no hardware)"

    # ── Type-check that the stub satisfies the protocol ───────────────────────

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)

    def __class_getitem__(cls, item: object) -> object:  # type: ignore[override]
        return cls


# Runtime assertion — caught at import time during tests.
assert isinstance(Kdc101Stub(), HostModule), (
    "Kdc101Stub does not satisfy the HostModule protocol"
)
