"""PTY-based simulator of the ND-stepper firmware (``src_nd_stepper/``).

Speaks the same SCPI-style protocol as the ESP32 + DRV8825 controller so
``NDStepperStage`` can be tested end to end without hardware. Motion is
simulated in wall-clock time at ``speed_dps`` (fast by default so tests stay
quick); there is no acceleration ramp.
"""

from __future__ import annotations

import os
import sys
import threading
import time

from ..logging import Debug

_PTY_AVAILABLE = sys.platform != "win32"
if _PTY_AVAILABLE:
    import pty
    import select
    import tty

_MODEL = "ND-Stepper-DRV8825"
_FW_VERSION = "1.0.0"
_ERR_QUEUE_SIZE = 8


class MockNDStepperFirmware:
    """Simulated ND-stepper controller served over a PTY pair."""

    def __init__(
        self,
        speed_dps: float = 7200.0,
        has_home_switch: bool = True,
        has_fault_pin: bool = True,
        has_reset_pin: bool = True,
    ) -> None:
        """Configure simulated speed, home switch and DRV8825 /FAULT wiring."""
        self.speed_dps = speed_dps
        self.has_home_switch = has_home_switch
        self.has_fault_pin = has_fault_pin
        self.has_reset_pin = has_reset_pin
        self.idle_disable_ms = 0
        """Release the motor this long after a move; 0 = hold (firmware default is 2000)."""
        self._last_active = time.monotonic()
        self.fault = False
        """Set True to simulate the driver pulling /FAULT low; latched until *CLS."""
        self._fault_latched = False
        self.limits = (-360.0, 360.0)
        self.homed = False
        self.enabled = True
        self.errors: list[str] = []
        self.commands: list[str] = []
        """Every command line received, uppercased — for test assertions."""

        self._pos_from = 0.0
        self._pos_to = 0.0
        self._t_start = 0.0
        self._t_end = 0.0
        self._homing_until = 0.0

        self.pty_master: int | None = None
        self.pty_slave: int | None = None
        self.pty_slave_path: str | None = None
        self._running = False
        self._stop_flag = False
        self._thread: threading.Thread | None = None
        self._pty_lock = threading.Lock()
        self._rx = ""

    # ── Public control ────────────────────────────────────────────────────────

    def start(self) -> str:
        """Start the simulator and return the PTY slave path."""
        if not _PTY_AVAILABLE:
            raise NotImplementedError("MockNDStepperFirmware requires PTY support (Linux/macOS)")
        self.pty_master, self.pty_slave = pty.openpty()
        self.pty_slave_path = os.ttyname(self.pty_slave)
        tty.setraw(self.pty_master)
        self._running = True
        self._stop_flag = False
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        Debug.info(f"MockNDStepperFirmware PTY: {self.pty_slave_path}")
        return self.pty_slave_path

    def stop(self) -> None:
        """Stop the simulator and release the PTY."""
        self._stop_flag = True
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)

    def kill_pty(self) -> None:
        """Close the PTY master mid-session, simulating a USB unplug."""
        self._stop_flag = True
        self._running = False
        with self._pty_lock:
            fd, self.pty_master = self.pty_master, None
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                pass

    @property
    def position_deg(self) -> float:
        """Current simulated wheel angle."""
        now = time.monotonic()
        if now >= self._t_end:
            return self._pos_to
        frac = (now - self._t_start) / (self._t_end - self._t_start)
        return self._pos_from + (self._pos_to - self._pos_from) * frac

    # ── Simulation ────────────────────────────────────────────────────────────

    def _busy(self) -> bool:
        now = time.monotonic()
        return now < self._t_end or now < self._homing_until

    def _move(self, target: float) -> None:
        start = self.position_deg
        duration = abs(target - start) / self.speed_dps
        self._pos_from, self._pos_to = start, target
        self._t_start = time.monotonic()
        self._t_end = self._t_start + duration

    def _set_position(self, deg: float) -> None:
        self._pos_from = self._pos_to = deg
        self._t_start = self._t_end = time.monotonic()

    def _queue_error(self, text: str) -> None:
        if len(self.errors) < _ERR_QUEUE_SIZE:
            self.errors.append(text)

    def _number(self, param: str) -> float | None:
        try:
            value = float(param)
        except ValueError:
            self._queue_error('-104,"Data type error"')
            return None
        if value != value or value in (float("inf"), float("-inf")):
            self._queue_error('-104,"Data type error"')
            return None
        return value

    def _service_idle(self) -> None:
        now = time.monotonic()
        if self.enabled and self.idle_disable_ms > 0:
            if self._busy():
                self._last_active = now
            elif (now - self._last_active) * 1000.0 >= self.idle_disable_ms:
                self.enabled = False

    def _fault_active(self) -> bool:
        if self.has_fault_pin and self.fault:
            self._fault_latched = True
        return self._fault_latched

    def _move_abs(self, deg: float) -> None:
        if self._fault_active():
            self._queue_error('-200,"Execution error; DRV8825 fault"')
        elif self._busy() and time.monotonic() < self._homing_until:
            self._queue_error('-200,"Execution error; homing in progress"')
        elif not self.limits[0] - 1e-3 <= deg <= self.limits[1] + 1e-3:
            self._queue_error('-222,"Data out of range; target outside travel limits"')
        else:
            self.enabled = True
            self._last_active = time.monotonic()
            self._move(deg)

    def _handle(self, line: str) -> str | None:  # noqa: C901 — flat protocol table
        """Return the reply for *line* (None for reply-less commands)."""
        line = line.strip().upper()
        if not line:
            return None
        self._service_idle()
        self.commands.append(line)
        header, _, param = line.partition(" ")
        param = param.strip()
        query = header.endswith("?")
        header = header.rstrip("?")

        if header == "*IDN" and query:
            return f"Custom ESP32,{_MODEL},0,{_FW_VERSION}"
        if header == "*RST":
            self._set_position(self.position_deg)
            self.limits = (-360.0, 360.0)
        elif header == "*CLS":
            self.errors.clear()
            if not self.fault:
                self._fault_latched = False
        elif header == "DIAG:DRV" and query:
            if not self.has_fault_pin:
                return "NA"
            return "FAULT" if self._fault_active() else "OK"
        elif header == "DIAG:DRV:RES" and not query:
            if not self.has_reset_pin:
                self._queue_error('-241,"Hardware missing; PIN_RESET not configured"')
            else:
                self._set_position(self.position_deg)
                if not self.fault:
                    self._fault_latched = False
        elif header == "DIAG:SELF" and query:
            if self._busy():
                return "FAIL,BUSY"
            if self._fault_active():
                return "FAIL,FAULT_ACTIVE"
            return "PASS" if self.has_fault_pin else "NA,NO_FAULT_PIN"
        elif header == "*OPC" and query:
            return "0" if self._busy() else "1"
        elif header == "SYST:ERR" and query:
            return self.errors.pop(0) if self.errors else '0,"No error"'
        elif header == "SYST:VERS" and query:
            return _FW_VERSION
        elif header == "MOT:HOME" and not query:
            if self.has_home_switch:
                self._homing_until = time.monotonic() + abs(self.position_deg) / self.speed_dps
                self._set_position(0.0)
            else:
                self._set_position(0.0)
            self.homed = True
        elif header == "MOT:HOMED" and query:
            return "1" if self.homed else "0"
        elif header == "MOT:MOVE:ABS" and not query:
            value = self._number(param)
            if value is not None:
                self._move_abs(value)
        elif header == "MOT:MOVE:REL" and not query:
            value = self._number(param)
            if value is not None:
                self._move_abs(self._pos_to + value)
        elif header == "MOT:STOP" and not query:
            self._set_position(self.position_deg)
        elif header == "MOT:ZERO" and not query:
            if self._busy():
                self._queue_error('-200,"Execution error; motor is moving"')
            else:
                self._set_position(0.0)
                self.homed = True
        elif header == "MOT:POS" and query:
            return f"{self.position_deg:.3f}"
        elif header == "MOT:BUSY" and query:
            return "1" if self._busy() else "0"
        elif header == "MOT:ENAB":
            if query:
                return "1" if self.enabled else "0"
            if param in ("ON", "1"):
                self.enabled = True
                self._last_active = time.monotonic()
            elif param in ("OFF", "0"):
                self.enabled = False
            else:
                self._queue_error('-224,"Illegal parameter value"')
        elif header == "CONF:MOT:SPEED":
            return f"{self.speed_dps:.2f}" if query else self._accept_speed(param)
        elif header == "CONF:MOT:IDLE":
            if query:
                return str(self.idle_disable_ms)
            value = self._number(param)
            if value is not None:
                if 0.0 <= value <= 600000.0:
                    self.idle_disable_ms = int(value)
                    self._last_active = time.monotonic()
                else:
                    self._queue_error('-222,"Data out of range; idle time"')
        elif header == "CONF:MOT:ACCEL":
            return "180.00" if query else None
        elif header == "CONF:MOT:LIM":
            if query:
                return f"{self.limits[0]:.2f},{self.limits[1]:.2f}"
            lo_s, _, hi_s = param.partition(",")
            lo, hi = self._number(lo_s), self._number(hi_s)
            if lo is not None and hi is not None:
                self.limits = (lo, hi)
        else:
            self._queue_error(f'-113,"Undefined header; {header}"')
        return None

    def _accept_speed(self, param: str) -> None:
        value = self._number(param)
        if value is not None and (value <= 0.0 or value > 360.0):
            self._queue_error('-222,"Data out of range; speed"')
        return None

    # ── PTY loop ──────────────────────────────────────────────────────────────

    def _run_loop(self) -> None:
        try:
            while not self._stop_flag:
                with self._pty_lock:
                    fd = self.pty_master
                if fd is None:
                    break
                try:
                    readable, _, _ = select.select([fd], [], [], 0.01)
                except (OSError, ValueError, TypeError):
                    break
                if not readable:
                    continue
                try:
                    data = os.read(fd, 1024)
                except OSError:
                    break
                self._rx += data.decode("utf-8", errors="ignore")
                while "\n" in self._rx:
                    raw, self._rx = self._rx.split("\n", 1)
                    reply = self._handle(raw)
                    if reply is not None:
                        try:
                            os.write(fd, (reply + "\n").encode())
                        except OSError:
                            return
        finally:
            self._cleanup()

    def _cleanup(self) -> None:
        with self._pty_lock:
            master, self.pty_master = self.pty_master, None
        for fd in (master, self.pty_slave):
            if fd is not None:
                try:
                    os.close(fd)
                except OSError:
                    pass
        self.pty_slave = None
