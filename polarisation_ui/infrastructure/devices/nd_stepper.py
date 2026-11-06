"""ND-filter stepper stage client (ESP32 + DRV8825, axial variable ND filter).

Talks the SCPI-style protocol of ``src_nd_stepper/`` over USB serial. The
filter wheel is rotary, so every position at this class's public API is an
angle in degrees. Unlike the continuous polariser rotation stage the wheel has
a usable range, so ``move_to_deg`` clamps its target to
``[min_angle_deg, max_angle_deg]``. The zero point is only a reference: the
wheel may travel to negative angles just as freely as to positive ones.

Commands used (the firmware replies only to queries; failures are queued and
read back with ``SYST:ERR?``, which this client does after every command):

    *IDN?                 Identification (checked on connect)
    SYST:ERR?             Pop one error from the device queue
    MOT:HOME              Start homing (or zero in place if no home switch)
    MOT:HOMED?            1 once a reference exists
    MOT:MOVE:ABS <deg>    Absolute move (non-blocking; client polls MOT:BUSY?)
    MOT:MOVE:REL <deg>    Relative move (used for manual jogging)
    MOT:STOP              Decelerate to a halt
    MOT:ZERO              Define the current position as 0 deg
    MOT:POS?              Position in degrees
    MOT:BUSY?             1 while moving or homing
    MOT:ENAB ON|OFF       Energise / release the motor
    DIAG:DRV?             OK | FAULT | NA — DRV8825 /FAULT pin
    DIAG:DRV:RES          Pulse DRV8825 /RESET to clear a latched fault (needs PIN_RESET)
    DIAG:SELF?            Short out-and-back move; PASS | FAIL,<reason> | NA,NO_FAULT_PIN
    CONF:MOT:IDLE <ms>    Release the motor this long after a move (0 = hold)
    CONF:MOT:SPEED <dps>  Max speed
    CONF:MOT:ACCEL <dps2> Acceleration

Pure device adapter — no Qt, no business logic.
"""

from __future__ import annotations

import threading
import time

import serial
from serial.tools import list_ports

from polarisation_ui.core.exceptions import NDStageError, NDStageTimeoutError
from polarisation_ui.infrastructure.logging import Debug
from polarisation_ui.infrastructure.serial_device import SerialDevice

MAX_ANGLE_DEG = 360.0  # default upper end of the usable range of the filter wheel
MIN_ANGLE_DEG = -360.0  # default lower end — zero is a reference, not a stop
_IDN_MARKER = "ND-Stepper"  # substring of the model field in *IDN?
_BUSY_POLL_S = 0.05
_REPLY_TIMEOUT_S = 2.0
_SELFTEST_TIMEOUT_S = 10.0


class NDStepperStage:
    """Drive a rotary variable ND filter via the ESP32/DRV8825 controller.

    Usage::

        nd = NDStepperStage()
        nd.connect("/dev/cu.usbserial-0001")
        nd.home()
        nd.move_to_deg(90.0)
        print(nd.get_position_deg())
        nd.disconnect()

    All serial transactions are serialised by a lock, so a UI timer calling
    ``get_position_deg_nowait()`` can safely run beside a sweep worker.
    """

    def __init__(
        self,
        max_angle_deg: float = MAX_ANGLE_DEG,
        baudrate: int = 115200,
        timeout: float = 1.0,
        min_angle_deg: float = MIN_ANGLE_DEG,
    ) -> None:
        """Create a disconnected client; *min_angle_deg*/*max_angle_deg* bound ``move_to_deg``."""
        self.min_angle_deg = min_angle_deg
        self.max_angle_deg = max_angle_deg
        self._baudrate = baudrate
        self._timeout = timeout
        self._dev: SerialDevice | None = None
        self._lock = threading.Lock()

    # ── Discovery ─────────────────────────────────────────────────────────────

    @staticmethod
    def list_devices() -> list[tuple[str, str]]:
        """Return ``[(port, description), ...]`` for all serial ports on this machine.

        The controller is a plain USB-serial ESP32, so it cannot be told
        apart from other ports before connecting; ``connect()`` verifies the
        identity.
        """
        return [(p.device, p.description or p.device) for p in list_ports.comports()]

    # ── Connection ────────────────────────────────────────────────────────────

    def connect(self, port: str) -> None:
        """Open *port* and verify the controller answers ``*IDN?`` as an ND stepper.

        Raises ``NDStageError`` if the port cannot be opened or the device is
        not the ND-stepper firmware.
        """
        if self.is_connected():
            self.disconnect()
        dev = SerialDevice(port=port, baudrate=self._baudrate, timeout=self._timeout)
        try:
            dev.reconnect()
        except serial.SerialException as exc:
            raise NDStageError(
                f"Cannot open {port}: {exc}. If the port is rejected with 'Invalid argument', "
                "unplug and replug the controller's USB cable and try again."
            ) from exc
        self._dev = dev
        try:
            idn = self._query("*IDN?")
        except NDStageError:
            self.disconnect()
            raise
        if _IDN_MARKER not in idn:
            self.disconnect()
            raise NDStageError(f"{port} is not an ND stepper controller (*IDN? → {idn!r})")
        Debug.info(f"NDStepperStage: connected to {port} ({idn})")

    def disconnect(self) -> None:
        """Close the serial port (safe to call when not connected)."""
        dev, self._dev = self._dev, None
        if dev is not None:
            dev.close()

    def is_connected(self) -> bool:
        """Return whether a serial connection is open."""
        return self._dev is not None and self._dev.connected

    # ── Motion ────────────────────────────────────────────────────────────────

    def home(self, wait: bool = True, timeout: float = 120.0) -> None:
        """Home the wheel; positions are relative to the reference afterwards.

        With a home switch fitted the controller seeks it; without one this
        zeroes the wheel where it currently is. Raises ``NDStageTimeoutError``
        on timeout and ``NDStageError`` if the controller reports a failure.
        """
        self._command("MOT:HOME")
        if wait:
            self._wait_idle(timeout)
            if self._query("MOT:HOMED?") != "1":
                self._check_errors()
                raise NDStageError("Homing finished without establishing a reference")

    def zero(self) -> None:
        """Define the current wheel position as 0° (no motion)."""
        self._command("MOT:ZERO")

    def move_to_deg(self, angle_deg: float, wait: bool = True, timeout: float = 60.0) -> None:
        """Move to *angle_deg*, clamped to ``[min_angle_deg, max_angle_deg]``.

        Raises ``NDStageTimeoutError`` on timeout, ``NDStageError`` otherwise.
        """
        clamped = max(self.min_angle_deg, min(self.max_angle_deg, angle_deg))
        if clamped != angle_deg:
            Debug.warning(
                f"NDStepperStage: move_to_deg({angle_deg:.3f}) clamped to {clamped:.3f} "
                f"(range is [{self.min_angle_deg}, {self.max_angle_deg}] deg)"
            )
        self._command(f"MOT:MOVE:ABS {clamped:.3f}")
        if wait:
            self._wait_idle(timeout)

    def jog_deg(self, delta_deg: float, wait: bool = True, timeout: float = 60.0) -> None:
        """Move by *delta_deg* relative to the current target (manual zero adjustment).

        Not clamped here: the firmware enforces its travel limits and rejects
        an out-of-range target, which surfaces as ``NDStageError``.
        """
        self._command(f"MOT:MOVE:REL {delta_deg:.3f}")
        if wait:
            self._wait_idle(timeout)

    def stop(self, immediate: bool = True) -> None:
        """Decelerate to a halt (*immediate* is accepted for KDC101 API parity)."""
        if self.is_connected():
            self._command("MOT:STOP")

    def enable(self, state: bool) -> None:
        """Energise (True) or release (False) the motor."""
        self._command(f"MOT:ENAB {'ON' if state else 'OFF'}")

    def set_idle_disable_ms(self, ms: int) -> None:
        """Release the motor *ms* after a move finishes (0 = hold forever).

        The driver otherwise holds at full current, which heats driver and
        motor. The next move re-energises the motor automatically.
        """
        self._command(f"CONF:MOT:IDLE {int(ms)}")

    def set_speed_dps(self, dps: float) -> None:
        """Set the maximum speed in degrees per second."""
        self._command(f"CONF:MOT:SPEED {dps:.3f}")

    def set_acceleration_dps2(self, dps2: float) -> None:
        """Set the acceleration in degrees per second squared."""
        self._command(f"CONF:MOT:ACCEL {dps2:.3f}")

    # ── State ─────────────────────────────────────────────────────────────────

    def get_position_deg(self) -> float:
        """Return the current wheel angle in degrees."""
        return self._parse_float(self._query("MOT:POS?"))

    def get_position_deg_nowait(self) -> float | None:
        """Non-blocking position read for UI polling.

        Returns ``None`` instead of blocking when the controller is busy
        servicing another call, so a Qt main-thread display timer never
        stalls the GUI waiting on serial I/O.
        """
        if not self.is_connected() or not self._lock.acquire(blocking=False):
            return None
        try:
            return self._parse_float(self._query_locked("MOT:POS?"))
        except NDStageError:
            return None
        finally:
            self._lock.release()

    def get_driver_status(self) -> str:
        """Return the DRV8825 /FAULT state: ``"OK"``, ``"FAULT"`` or ``"NA"`` (pin not wired).

        The DRV8825 has no status register — /FAULT (overcurrent or
        over-temperature) is its only feedback, and the firmware latches it.
        """
        return self._query("DIAG:DRV?")

    def reset_driver(self) -> str:
        """Pulse the DRV8825 /RESET line to clear a latched fault; return the new status.

        Needs ``PIN_RESET`` wired and configured in the firmware, otherwise
        ``NDStageError`` is raised. Stops any motion, and the coil phase is
        lost, so the wheel may shift by a few steps — re-home or re-zero if
        absolute accuracy matters.
        """
        self._command("DIAG:DRV:RES")
        self._command("*CLS")
        return self.get_driver_status()

    def self_test(self) -> tuple[bool, str]:
        """Run the controller's driver self-test (short move out and back).

        Returns ``(ok, detail)``. ``ok`` is True only for ``PASS``. Without a
        wired /FAULT pin the move still runs but the result is ``(False,
        "NA,NO_FAULT_PIN")`` — a move alone cannot prove the driver works, so
        check by eye or by hand that the shaft actually moved.
        """
        reply = self._query("DIAG:SELF?", timeout=_SELFTEST_TIMEOUT_S)
        return reply == "PASS", reply

    def is_homed(self) -> bool:
        """Return whether a home/zero reference exists."""
        return self._query("MOT:HOMED?") == "1"

    def is_busy(self) -> bool:
        """Return whether the wheel is moving or homing."""
        return self._query("MOT:BUSY?") == "1"

    # ── Transport ─────────────────────────────────────────────────────────────

    def _require_connected(self) -> SerialDevice:
        if self._dev is None or not self._dev.connected:
            raise NDStageError("ND stepper: not connected")
        return self._dev

    def _read_reply(self, dev: SerialDevice, timeout: float = _REPLY_TIMEOUT_S) -> str:
        """Read one reply line, skipping unsolicited ``DATA:`` lines (boot banner)."""
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise NDStageTimeoutError("ND stepper: no reply from controller")
            line = dev.read_value(timeout=remaining, return_type="str")
            if isinstance(line, str) and line and not line.startswith("DATA:"):
                return line

    def _send(self, dev: SerialDevice, command: str) -> None:
        if not dev.send_command(command):
            raise NDStageError(f"ND stepper: failed to send {command!r}")

    def _query_locked(self, command: str, timeout: float = _REPLY_TIMEOUT_S) -> str:
        dev = self._require_connected()
        self._send(dev, command)
        return self._read_reply(dev, timeout)

    def _query(self, command: str, timeout: float = _REPLY_TIMEOUT_S) -> str:
        with self._lock:
            return self._query_locked(command, timeout)

    def _command(self, command: str) -> None:
        """Send a reply-less command, then read ``SYST:ERR?`` to catch failures."""
        with self._lock:
            dev = self._require_connected()
            self._send(dev, command)
            self._check_errors_locked(dev, command)

    def _check_errors(self) -> None:
        with self._lock:
            self._check_errors_locked(self._require_connected(), None)

    def _check_errors_locked(self, dev: SerialDevice, command: str | None) -> None:
        errors: list[str] = []
        for _ in range(8):  # device queue holds 8
            self._send(dev, "SYST:ERR?")
            reply = self._read_reply(dev)
            if reply.startswith("0,"):
                break
            errors.append(reply)
        if errors:
            what = f" for {command!r}" if command else ""
            raise NDStageError(f"ND stepper rejected command{what}: {'; '.join(errors)}")

    def _wait_idle(self, timeout: float) -> None:
        deadline = time.monotonic() + timeout
        while True:
            if self._query("MOT:BUSY?") == "0":
                self._check_errors()
                return
            if time.monotonic() >= deadline:
                try:
                    self.stop()
                except NDStageError:
                    pass  # best effort — the timeout below is the real failure
                raise NDStageTimeoutError(f"ND stepper: motion did not finish in {timeout:.0f} s")
            time.sleep(_BUSY_POLL_S)

    @staticmethod
    def _parse_float(text: str) -> float:
        try:
            return float(text)
        except ValueError as exc:
            raise NDStageError(f"ND stepper: unexpected numeric reply {text!r}") from exc
