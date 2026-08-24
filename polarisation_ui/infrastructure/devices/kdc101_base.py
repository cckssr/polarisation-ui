"""Shared KDC101 transport layer for rotation and linear stage adapters.

Both ``KDC101Polariser`` (PRM1-Z8 rotation stage) and ``KDC101NDStage``
(MTS50/M-Z8 linear stage) talk to the same Thorlabs KDC101 controller over
pylablib's ``KinesisMotor``. This module holds the pylablib import bootstrap,
connection lifecycle, homing, and the position-poll-until-stable move logic
shared by both — only the position unit and pylablib scale name differ.

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

# pylablib (and its hard dependency PyQt5) is imported lazily on first use and
# cached in these module globals.
_Thorlabs = None
_ThorlabsError: type = Exception  # falls back to bare Exception until loaded
_ThorlabsTimeoutError: type = Exception
_PYLABLIB_AVAILABLE: bool | None = None
_PYLABLIB_IMPORT_ERROR: str = ""

# wait_until_stopped() polling parameters.
_POSITION_POLL_INTERVAL_S = 0.2
_POSITION_STABLE_READS = 3  # consecutive stable reads before declaring "stopped"


def _ensure_pylablib() -> bool:
    """Import pylablib on first call; cache the result in the module globals above."""
    global \
        _Thorlabs, \
        _ThorlabsError, \
        _ThorlabsTimeoutError, \
        _PYLABLIB_AVAILABLE, \
        _PYLABLIB_IMPORT_ERROR
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


class KDC101MotorBase:
    """Transport-level KDC101 driver shared by rotation and linear stage adapters.

    Subclasses set ``_SCALE`` (a pylablib named scale string, e.g.
    ``"PRM1-Z8"`` or ``"MTS50-Z8"``) and ``_POSITION_STABLE_DELTA`` (position
    units within which two consecutive reads count as "the same" while
    polling for move completion) and expose unit-named public wrappers
    (``move_to``/``get_position_deg`` or ``move_to_mm``/``get_position_mm``)
    around the protected ``_move_to`` / ``_get_position`` / ``_get_position_nowait``
    methods here.
    """

    _SCALE: str = ""
    _POSITION_STABLE_DELTA: float = 0.05

    def __init__(self) -> None:
        """Start disconnected; connect() opens the pylablib KinesisMotor session."""
        self._motor: KinesisMotor | None = None
        # Serialises every call that touches the stage.
        self._lock = threading.Lock()

    # ── Connection ────────────────────────────────────────────────────────────

    def connect(self, conn_id: str) -> None:
        """Open connection to the KDC101 identified by *conn_id*.

        *conn_id* is either a serial-number string (e.g. ``"27266999"``) or a
        full port path (e.g. ``"/dev/cu.usbserial-27266999"``). Both forms are
        accepted by pylablib's ``KinesisMotor``.

        Raises ``KDC101Error`` on failure.
        """
        if not _ensure_pylablib():
            raise KDC101Error(
                f"pylablib is not installed; cannot connect to KDC101 ({_PYLABLIB_IMPORT_ERROR})"
            )
        try:
            motor = _Thorlabs.KinesisMotor(conn_id, scale=self._SCALE)
            motor.open()
            # Discard any unsolicited status frames that arrive on open.
            motor.flush_comm()
            self._motor = motor
            Debug.info(f"{type(self).__name__}: connected to {conn_id}")
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
                Debug.warning(f"{type(self).__name__}: error during disconnect: {exc}")
            finally:
                self._motor = None
        Debug.info(f"{type(self).__name__}: disconnected")

    def is_connected(self) -> bool:
        """Return whether the motor session is currently open."""
        return self._motor is not None

    # ── Motion ────────────────────────────────────────────────────────────────

    def home(self, wait: bool = True, timeout: float = 120.0) -> None:
        """Home the stage. Blocks until homing is complete when *wait* is True.

        Raises ``KDC101TimeoutError`` if homing does not complete within
        *timeout* seconds.
        """
        self._require_connected()
        try:
            with self._lock:
                self._motor.flush_comm()
                self._motor.home(sync=wait, timeout=timeout if wait else None)
            Debug.info(f"{type(self).__name__}: homed")
        except _ThorlabsTimeoutError as exc:
            raise KDC101TimeoutError(f"KDC101 home timed out: {exc}") from exc
        except _ThorlabsError as exc:
            raise KDC101Error(f"KDC101 home failed: {exc}") from exc

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
            Debug.warning(f"{type(self).__name__}: is_homed() failed: {exc}")
            return False

    def stop(self, immediate: bool = True) -> None:
        """Stop any in-progress move (e.g. to abort a continuous scan mid-travel)."""
        self._require_connected()
        try:
            with self._lock:
                self._motor.stop(immediate=immediate, sync=False)
        except _ThorlabsError as exc:
            raise KDC101Error(f"KDC101 stop failed: {exc}") from exc

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

    # ── Raw position access (subclasses expose unit-named wrappers) ────────────

    def _move_to(self, value: float, wait: bool = True, timeout: float = 60.0) -> None:
        """Move to *value* in the subclass's native position unit.

        Completion is detected by polling ``_get_position()`` rather than
        pylablib's ``wait_move()`` — APT status queries race with the
        KDC101's unsolicited background frames and intermittently fail.

        Raises ``KDC101TimeoutError`` on timeout, ``KDC101Error`` on other errors.
        """
        self._require_connected()
        try:
            with self._lock:
                self._motor.flush_comm()
                self._motor.move_to(value)
        except _ThorlabsError as exc:
            raise KDC101Error(f"KDC101 move_to({value:.4f}) failed: {exc}") from exc
        if wait and not self._wait_until_stopped(timeout):
            raise KDC101TimeoutError(f"KDC101 move_to({value:.4f}) timed out after {timeout}s")

    def _wait_until_stopped(self, timeout: float) -> bool:
        """Poll position until stable for consecutive reads, tolerating transient errors.

        Avoids ``wait_move()``/``is_moving()`` entirely, and silently retries
        past transient framing errors instead of failing the whole move on one
        bad read.
        """
        deadline = time.time() + timeout
        prev_pos: float | None = None
        stable_count = 0
        while time.time() < deadline:
            time.sleep(_POSITION_POLL_INTERVAL_S)
            try:
                pos = self._get_position()
            except KDC101Error:
                continue  # transient read error — keep waiting
            if prev_pos is not None and abs(pos - prev_pos) < self._POSITION_STABLE_DELTA:
                stable_count += 1
                if stable_count >= _POSITION_STABLE_READS:
                    return True
            else:
                stable_count = 0
            prev_pos = pos
        return False

    def _get_position(self) -> float:
        """Return the current position in the subclass's native unit."""
        self._require_connected()
        try:
            with self._lock:
                self._motor.flush_comm()
                return float(self._motor.get_position())
        except _ThorlabsError as exc:
            raise KDC101Error(f"KDC101 get_position failed: {exc}") from exc

    def _get_position_nowait(self) -> float | None:
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

    # ── Discovery ─────────────────────────────────────────────────────────────

    @staticmethod
    def list_devices() -> list[tuple[str, str]]:
        """Return ``[(conn_id, description), ...]`` for all connected KDC101s.

        When the ft232 backend is available pylablib returns
        ``[(serial_number, description), ...]``. Without it (macOS fallback)
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
            Debug.warning(f"KDC101MotorBase.list_devices: {exc}")
            return []

    # ── Internal ──────────────────────────────────────────────────────────────

    def _require_connected(self) -> None:
        if self._motor is None:
            raise KDC101Error("KDC101 is not connected")
