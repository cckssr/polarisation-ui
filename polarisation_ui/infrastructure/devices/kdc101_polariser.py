"""KDC101 motorised polariser adapter using pylablib.

Wraps pylablib's KinesisMotor with a simple connect/home/move/read API.
Positions are always in degrees (PRM1-Z8 scale is applied automatically).

Do NOT use raw APT messages here — all communication goes through pylablib.
"""

from __future__ import annotations

import threading
import time
from typing import TYPE_CHECKING

from polarisation_ui.core.exceptions import KDC101Error, KDC101TimeoutError
from polarisation_ui.infrastructure.logging import Debug

if TYPE_CHECKING:
    from pylablib.devices.Thorlabs import KinesisMotor

# pylablib (and its hard dependency PyQt5) is imported lazily on first
_Thorlabs = None
_ThorlabsError: type = Exception  # falls back to bare Exception until loaded
_ThorlabsTimeoutError: type = Exception

_PRM1_Z8_SCALE = "PRM1-Z8"  # built-in pylablib scale for the PRM1/MZ8 stage

# wait_until_stopped() polling parameters — see module docstring.
_POSITION_STABLE_DEG = 0.05  # positions within this delta count as "the same"
_POSITION_POLL_INTERVAL_S = 0.2
_POSITION_STABLE_READS = 3  # consecutive stable reads before declaring "stopped"


def _ensure_pylablib() -> bool:
    """Import pylablib on first call; cache the result. Thread-safe for reads."""
    global _Thorlabs, _ThorlabsError, _ThorlabsTimeoutError
    _pylablib_available: bool | None = None
    _pylablib_import_error: str
    if _pylablib_available is not None:
        return _pylablib_available
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
        _pylablib_available = True
    except ImportError as exc:
        _pylablib_import_error = str(exc)
        _pylablib_available = False
    return _pylablib_available


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
        self._motor: KinesisMotor | None = None
        # Serialises every call that touches the stage — see module docstring.
        self._lock = threading.Lock()
        # Host-side logical-zero offset (degrees)
        self._zero_offset_deg: float = 0.0

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
            # Discard any unsolicited status frames that arrive on open, same
            # as calibration_tool's KDC101Stage.connect().
            motor.flush_comm()
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
                with self._lock:
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
            with self._lock:
                self._motor.flush_comm()
                self._motor.home(sync=wait, timeout=timeout if wait else None)
            Debug.info("KDC101Polariser: homed")
        except _ThorlabsTimeoutError as exc:
            raise KDC101TimeoutError(f"KDC101 home timed out: {exc}") from exc
        except _ThorlabsError as exc:
            raise KDC101Error(f"KDC101 home failed: {exc}") from exc

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

    def is_homed(self) -> bool:
        """Return whether the stage has completed a homing sequence since power-up.

        Returns False (rather than raising) on a transient read error, so
        callers can safely use this to decide whether a re-home is needed.
        """
        self._require_connected()
        try:
            with self._lock:
                return bool(self._motor.is_homed())
        except _ThorlabsError as exc:
            Debug.warning(f"KDC101Polariser: is_homed() failed: {exc}")
            return False

    def stop(self, immediate: bool = True) -> None:
        """Stop any in-progress move (e.g. to abort a continuous scan mid-travel)."""
        self._require_connected()
        try:
            with self._lock:
                self._motor.stop(immediate=immediate, sync=False)
        except _ThorlabsError as exc:
            raise KDC101Error(f"KDC101 stop failed: {exc}") from exc

    def move_to(self, angle_deg: float, wait: bool = True, timeout: float = 60.0) -> None:
        """Move to *angle_deg* (degrees).  Blocks until the move completes when *wait* is True.

        Completion is detected by polling ``get_position_deg()`` rather than
        pylablib's ``wait_move()`` — see the module docstring for why.

        Raises ``KDC101TimeoutError`` on timeout, ``KDC101Error`` on other errors.
        """
        self._require_connected()
        try:
            with self._lock:
                self._motor.flush_comm()
                self._motor.move_to(angle_deg)
        except _ThorlabsError as exc:
            raise KDC101Error(f"KDC101 move_to({angle_deg:.2f}°) failed: {exc}") from exc
        if wait and not self._wait_until_stopped(timeout):
            raise KDC101TimeoutError(f"KDC101 move_to({angle_deg:.2f}°) timed out after {timeout}s")

    def _wait_until_stopped(self, timeout: float) -> bool:
        """Poll position until stable for consecutive reads, tolerating transient errors.

        Mirrors ``calibration_tool``'s ``wait_until_stopped()``: avoids
        ``wait_move()``/``is_moving()`` entirely, and silently retries past
        transient framing errors instead of failing the whole move on one bad read.
        """
        deadline = time.time() + timeout
        prev_pos: float | None = None
        stable_count = 0
        while time.time() < deadline:
            time.sleep(_POSITION_POLL_INTERVAL_S)
            try:
                pos = self.get_position_deg()
            except KDC101Error:
                continue  # transient read error — keep waiting
            if prev_pos is not None and abs(pos - prev_pos) < _POSITION_STABLE_DEG:
                stable_count += 1
                if stable_count >= _POSITION_STABLE_READS:
                    return True
            else:
                stable_count = 0
            prev_pos = pos
        return False

    def get_position_deg(self) -> float:
        """Return the current position in degrees."""
        self._require_connected()
        try:
            with self._lock:
                self._motor.flush_comm()
                return float(self._motor.get_position())
        except _ThorlabsError as exc:
            raise KDC101Error(f"KDC101 get_position failed: {exc}") from exc

    def get_position_deg_nowait(self) -> float | None:
        """Non-blocking position read for UI polling.

        Returns ``None`` instead of blocking when the stage is currently busy
        servicing another call (e.g. a sweep worker mid-move), so a Qt
        main-thread display timer never stalls the GUI waiting on serial I/O.
        """
        self._require_connected()
        if not self._lock.acquire(blocking=False):
            return None
        try:
            self._motor.flush_comm()
            return float(self._motor.get_position())
        except _ThorlabsError as exc:
            raise KDC101Error(f"KDC101 get_position failed: {exc}") from exc
        finally:
            self._lock.release()

    def enable(self, state: bool) -> None:
        """Enable or disable the motor channel."""
        self._require_connected()
        try:
            with self._lock:
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
