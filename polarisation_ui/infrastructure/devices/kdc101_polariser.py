"""
KDC101 motorised polariser adapter using pylablib.

Wraps pylablib's KinesisMotor with a simple connect/home/move/read API.
Positions are always in degrees (PRM1-Z8 scale is applied automatically).

Do NOT use raw APT messages here — all communication goes through pylablib.
"""

from typing import Optional

from polarisation_ui.core.exceptions import KDC101Error, KDC101TimeoutError
from polarisation_ui.infrastructure.logging import Debug

try:
    from pylablib.devices import Thorlabs as _Thorlabs
    from pylablib.devices.Thorlabs import ThorlabsError, ThorlabsTimeoutError

    _PYLABLIB_AVAILABLE = True
except ImportError:
    _PYLABLIB_AVAILABLE = False
    ThorlabsError = Exception
    ThorlabsTimeoutError = Exception


_PRM1_Z8_SCALE = "PRM1-Z8"  # built-in pylablib scale for the PRM1/MZ8 stage


class KDC101Polariser:
    """
    Drive a Thorlabs KDC101 + PRM1-Z8 rotation stage with a polariser mounted.

    All positions are expressed in degrees.  The PRM1-Z8 encoder scale is
    applied automatically via pylablib so no manual counts-per-degree maths
    is needed here.

    Usage::

        kdc = KDC101Polariser()
        kdc.connect("27266999")   # serial-number string or full port path
        kdc.home()
        kdc.move_to(45.0)
        print(kdc.get_position_deg())
        kdc.disconnect()
    """

    def __init__(self) -> None:
        self._motor: Optional[object] = None

    # ── Connection ────────────────────────────────────────────────────────────

    def connect(self, conn_id: str) -> None:
        """Open connection to the KDC101 identified by *conn_id*.

        *conn_id* is either a serial-number string (e.g. ``"27266999"``) or a
        full port path (e.g. ``"/dev/cu.usbserial-27266999"``).  Both forms are
        accepted by pylablib's ``KinesisMotor``.

        Raises ``KDC101Error`` on failure.
        """
        if not _PYLABLIB_AVAILABLE:
            raise KDC101Error("pylablib is not installed; cannot connect to KDC101")
        try:
            motor = _Thorlabs.KinesisMotor(conn_id, scale=_PRM1_Z8_SCALE)
            motor.open()
            self._motor = motor
            Debug.info(f"KDC101Polariser: connected to {conn_id}")
        except ThorlabsError as exc:
            raise KDC101Error(f"KDC101 connect failed: {exc}") from exc

    def disconnect(self) -> None:
        if self._motor is not None:
            try:
                self._motor.close()
            except Exception as exc:
                Debug.warning(f"KDC101Polariser: error during disconnect: {exc}")
            finally:
                self._motor = None
        Debug.info("KDC101Polariser: disconnected")

    def is_connected(self) -> bool:
        return self._motor is not None

    # ── Motion ────────────────────────────────────────────────────────────────

    def home(self, wait: bool = True, timeout: float = 120.0) -> None:
        """Home the stage.  Blocks until homing is complete when *wait* is True.

        Raises ``KDC101TimeoutError`` if homing does not complete within
        *timeout* seconds.
        """
        self._require_connected()
        try:
            self._motor.home(sync=wait, timeout=timeout if wait else None)
            Debug.info("KDC101Polariser: homed")
        except ThorlabsTimeoutError as exc:
            raise KDC101TimeoutError(f"KDC101 home timed out: {exc}") from exc
        except ThorlabsError as exc:
            raise KDC101Error(f"KDC101 home failed: {exc}") from exc

    def move_to(
        self, angle_deg: float, wait: bool = True, timeout: float = 60.0
    ) -> None:
        """Move to *angle_deg* (degrees).  Blocks until the move completes
        when *wait* is True.

        Raises ``KDC101TimeoutError`` on timeout, ``KDC101Error`` on other errors.
        """
        self._require_connected()
        try:
            self._motor.move_to(angle_deg)
            if wait:
                self._motor.wait_move(timeout=timeout)
        except ThorlabsTimeoutError as exc:
            raise KDC101TimeoutError(
                f"KDC101 move_to({angle_deg:.2f}°) timed out: {exc}"
            ) from exc
        except ThorlabsError as exc:
            raise KDC101Error(
                f"KDC101 move_to({angle_deg:.2f}°) failed: {exc}"
            ) from exc

    def get_position_deg(self) -> float:
        """Return the current position in degrees."""
        self._require_connected()
        try:
            return float(self._motor.get_position())
        except ThorlabsError as exc:
            raise KDC101Error(f"KDC101 get_position failed: {exc}") from exc

    def enable(self, state: bool) -> None:
        """Enable or disable the motor channel."""
        self._require_connected()
        try:
            if state:
                self._motor.enable_channel()
            else:
                self._motor.disable_channel()
        except ThorlabsError as exc:
            raise KDC101Error(f"KDC101 enable({state}) failed: {exc}") from exc

    # ── Discovery ─────────────────────────────────────────────────────────────

    @staticmethod
    def list_devices() -> list[tuple[str, str]]:
        """Return ``[(conn_id, description), ...]`` for all connected KDC101s.

        Returns an empty list if pylablib is not installed or no devices are
        found.
        """
        if not _PYLABLIB_AVAILABLE:
            return []
        try:
            return list(_Thorlabs.list_kinesis_devices())
        except Exception as exc:
            Debug.warning(f"KDC101Polariser.list_devices: {exc}")
            return []

    # ── Internal ──────────────────────────────────────────────────────────────

    def _require_connected(self) -> None:
        if self._motor is None:
            raise KDC101Error("KDC101 is not connected")
