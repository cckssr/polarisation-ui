"""KDC101 motorised polariser adapter using pylablib.

Wraps pylablib's KinesisMotor with a simple connect/home/move/read API.
Positions are always in degrees (PRM1-Z8 scale is applied automatically).

Do NOT use raw APT messages here — all communication goes through pylablib.
"""

from polarisation_ui.core.exceptions import KDC101Error, KDC101TimeoutError
from polarisation_ui.infrastructure.logging import Debug

# pylablib (and its hard dependency PyQt5) is imported lazily on first use so
# that it does not load PyQt5 into the process at startup alongside PySide6,
# which on macOS causes spurious ObjC class-duplication warnings.
_Thorlabs = None
_ThorlabsError: type = Exception  # falls back to bare Exception until loaded
_ThorlabsTimeoutError: type = Exception
_PYLABLIB_AVAILABLE: bool | None = None  # None = not yet probed
_PYLABLIB_IMPORT_ERROR: str = ""

_PRM1_Z8_SCALE = "PRM1-Z8"  # built-in pylablib scale for the PRM1/MZ8 stage


def _ensure_pylablib() -> bool:
    """Import pylablib on first call; cache the result. Thread-safe for reads."""
    global _Thorlabs, _ThorlabsError, _ThorlabsTimeoutError
    global _PYLABLIB_AVAILABLE, _PYLABLIB_IMPORT_ERROR
    if _PYLABLIB_AVAILABLE is not None:
        return _PYLABLIB_AVAILABLE
    try:
        from pylablib.devices import Thorlabs as _th
        from pylablib.devices.Thorlabs import (
            ThorlabsError as _te,
        )
        from pylablib.devices.Thorlabs import (
            ThorlabsTimeoutError as _tte,
        )

        _Thorlabs = _th
        _ThorlabsError = _te
        _ThorlabsTimeoutError = _tte
        _PYLABLIB_AVAILABLE = True
    except ImportError as exc:
        _PYLABLIB_IMPORT_ERROR = str(exc)
        _PYLABLIB_AVAILABLE = False
    return _PYLABLIB_AVAILABLE


class KDC101Polariser:
    """Drive a Thorlabs KDC101 + PRM1-Z8 rotation stage with a polariser mounted.

    All positions are expressed in degrees.  The PRM1-Z8 encoder scale is
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

    def __init__(self) -> None:
        """Start disconnected; connect() opens the pylablib KinesisMotor session."""
        self._motor: object | None = None

    # ── Connection ────────────────────────────────────────────────────────────

    def connect(self, conn_id: str) -> None:
        """Open connection to the KDC101 identified by *conn_id*.

        *conn_id* is either a serial-number string (e.g. ``"27266999"``) or a
        full port path (e.g. ``"/dev/cu.usbserial-27266999"``).  Both forms are
        accepted by pylablib's ``KinesisMotor``.

        Raises ``KDC101Error`` on failure.
        """
        if not _ensure_pylablib():
            raise KDC101Error(
                f"pylablib is not installed; cannot connect to KDC101 ({_PYLABLIB_IMPORT_ERROR})"
            )
        try:
            motor = _Thorlabs.KinesisMotor(conn_id, scale=_PRM1_Z8_SCALE)
            motor.open()
            self._motor = motor
            Debug.info(f"KDC101Polariser: connected to {conn_id}")
        except _ThorlabsError as exc:
            raise KDC101Error(f"KDC101 connect failed: {exc}") from exc
        except Exception as exc:
            # Catch backend/configuration errors (e.g. missing ft232 driver,
            # invalid port string format) and normalise them to KDC101Error so
            # callers never have to handle raw pylablib internals.
            raise KDC101Error(f"KDC101 connect failed: {exc}") from exc

    def disconnect(self) -> None:
        """Close the motor session, if any, ignoring errors during shutdown."""
        if self._motor is not None:
            try:
                self._motor.close()
            except Exception as exc:
                Debug.warning(f"KDC101Polariser: error during disconnect: {exc}")
            finally:
                self._motor = None
        Debug.info("KDC101Polariser: disconnected")

    def is_connected(self) -> bool:
        """Return whether the motor session is currently open."""
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
        except _ThorlabsTimeoutError as exc:
            raise KDC101TimeoutError(f"KDC101 home timed out: {exc}") from exc
        except _ThorlabsError as exc:
            raise KDC101Error(f"KDC101 home failed: {exc}") from exc

    def move_to(self, angle_deg: float, wait: bool = True, timeout: float = 60.0) -> None:
        """Move to *angle_deg* (degrees).  Blocks until the move completes when *wait* is True.

        Raises ``KDC101TimeoutError`` on timeout, ``KDC101Error`` on other errors.
        """
        self._require_connected()
        try:
            self._motor.move_to(angle_deg)
            if wait:
                self._motor.wait_move(timeout=timeout)
        except _ThorlabsTimeoutError as exc:
            raise KDC101TimeoutError(f"KDC101 move_to({angle_deg:.2f}°) timed out: {exc}") from exc
        except _ThorlabsError as exc:
            raise KDC101Error(f"KDC101 move_to({angle_deg:.2f}°) failed: {exc}") from exc

    def get_position_deg(self) -> float:
        """Return the current position in degrees."""
        self._require_connected()
        try:
            return float(self._motor.get_position())
        except _ThorlabsError as exc:
            raise KDC101Error(f"KDC101 get_position failed: {exc}") from exc

    def enable(self, state: bool) -> None:
        """Enable or disable the motor channel."""
        self._require_connected()
        try:
            if state:
                self._motor.enable_channel()
            else:
                self._motor.disable_channel()
        except _ThorlabsError as exc:
            raise KDC101Error(f"KDC101 enable({state}) failed: {exc}") from exc

    # ── Discovery ─────────────────────────────────────────────────────────────

    @staticmethod
    def list_devices() -> list[tuple[str, str]]:
        """Return ``[(conn_id, description), ...]`` for all connected KDC101s.

        When the ft232 backend is available pylablib returns
        ``[(serial_number, description), ...]``.  Without it (macOS fallback)
        it returns a flat list of port-path strings; those are normalised to
        ``(path, path)`` tuples so the caller always sees the same shape.

        Returns an empty list if pylablib is not installed or no devices are
        found.
        """
        if not _ensure_pylablib():
            return []
        try:
            devices = _Thorlabs.list_kinesis_devices()
            if not devices:
                return []
            result: list[tuple[str, str]] = []
            for d in devices:
                if isinstance(d, tuple) and len(d) >= 2:
                    result.append((str(d[0]), str(d[1])))
                elif isinstance(d, str):
                    result.append((d, d))
            return result
        except Exception as exc:
            Debug.warning(f"KDC101Polariser.list_devices: {exc}")
            return []

    # ── Internal ──────────────────────────────────────────────────────────────

    def _require_connected(self) -> None:
        if self._motor is None:
            raise KDC101Error("KDC101 is not connected")
