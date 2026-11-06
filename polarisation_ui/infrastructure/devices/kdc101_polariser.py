"""KDC101 motorised polariser adapter using pylablib.

Wraps pylablib's KinesisMotor with a simple connect/home/move/read API.
Positions are always in degrees (PRM1-Z8 scale is applied automatically).

Do NOT use raw APT messages here — all communication goes through pylablib.
"""

from __future__ import annotations

from polarisation_ui.infrastructure.devices.kdc101_base import KDC101MotorBase

_PRM1_Z8_SCALE = "PRM1-Z8"  # built-in pylablib scale for the PRM1/MZ8 stage

_POSITION_STABLE_DEG = 0.05  # positions within this delta count as "the same"


class KDC101Polariser(KDC101MotorBase):
    """Drive a Thorlabs KDC101 + PRM1-Z8 rotation stage with a polariser mounted.

    All positions are expressed in degrees. The PRM1-Z8 encoder scale is
    applied automatically via pylablib so no manual counts-per-degree maths
    is needed here.

    Usage::

        kdc = KDC101Polariser()
        kdc.connect("27266999")  # serial-number string or full port path
        kdc.home()
        kdc.move_to(45.0)
        print(kdc.get_position_deg())
        kdc.disconnect()
    """

    _SCALE = _PRM1_Z8_SCALE
    _POSITION_STABLE_DELTA = _POSITION_STABLE_DEG

    def __init__(self) -> None:
        """Start disconnected; connect() opens the pylablib KinesisMotor session."""
        super().__init__()
        # Host-side logical-zero offset (degrees)
        self._zero_offset_deg: float = 0.0

    # ── Logical-zero offset ──────────────────────────────────────────────────

    @property
    def zero_offset_deg(self) -> float:
        """Host-side logical-zero offset in degrees (0.0 until a zero-find has run)."""
        return self._zero_offset_deg

    def set_zero_offset_deg(self, offset_deg: float) -> None:
        """Set the logical-zero offset, normalised to [0, 360)."""
        self._zero_offset_deg = offset_deg % 360.0

    def move_to_logical(self, angle_deg: float, wait: bool = True, timeout: float = 60.0) -> None:
        """Move to *angle_deg* relative to the current zero offset.

        Equivalent to ``move_to(zero_offset_deg + angle_deg, ...)``.

        Deliberately not wrapped to [0, 360) — the PRM1-Z8 is a continuous
        rotation mount, so a target past 360° (or below 0°) is a valid
        absolute position that keeps the stage turning the same direction.
        Wrapping here would snap the target back into [0, 360) mid-sweep and
        send the stage the long way round instead of continuing forward.
        """
        self.move_to(self._zero_offset_deg + angle_deg, wait=wait, timeout=timeout)

    # ── Motion ────────────────────────────────────────────────────────────────

    def move_to(self, angle_deg: float, wait: bool = True, timeout: float = 60.0) -> None:
        """Move to *angle_deg* (degrees). Blocks until the move completes when *wait* is True.

        Raises ``KDC101TimeoutError`` on timeout, ``KDC101Error`` on other errors.
        """
        self._move_to(angle_deg, wait=wait, timeout=timeout)

    def get_position_deg(self) -> float:
        """Return the current position in degrees."""
        return self._get_position()

    def get_position_deg_nowait(self) -> float | None:
        """Non-blocking position read for UI polling.

        Returns ``None`` instead of blocking when the stage is currently busy
        servicing another call (e.g. a sweep worker mid-move), so a Qt
        main-thread display timer never stalls the GUI waiting on serial I/O.
        """
        return self._get_position_nowait()
