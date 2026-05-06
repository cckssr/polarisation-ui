"""
Mock Arduino for testing — SCPI 2.0.0 (ADS1220 + PD-TIA gain).

Implements the full SCPI 2.0.0 command tree via a PTY pair so that
DualEncoderArduino and its tests can run without real hardware.

ADS1220 intensity is simulated via Malus's law:
    V = V_REF * cos²(sample_angle_rad)
so the detector plot shows a real polarisation curve when sample angle varies.
"""

import math
import os
import random
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from ..logging import Debug
from .mock_port_registry import register_mock_port, unregister_mock_port

# PTY is Unix-only (pty, tty, select on file descriptors are absent on Windows)
_PTY_AVAILABLE = sys.platform != "win32"
if _PTY_AVAILABLE:
    import pty
    import select
    import tty

# ── Simulation constants ─────────────────────────────────────────────────────

_V_REF = 2.048  # ADS1220 reference voltage (V)
_TEMP_NOMINAL = 25.0  # °C — approximate room temperature


@dataclass
class MockEncoderState:
    """State for one encoder simulation."""

    current_angle: float = 0.0
    zero_offset: float = 0.0
    base_angle: float = 0.0
    poll_count: int = 0

    def get_effective_angle(self) -> float:
        return self.current_angle - self.zero_offset

    def get_raw_value(self) -> int:
        return int((self.get_effective_angle() % 360.0) / 360.0 * 16384) % 65536


class MockArduino:
    """
    Simulated Arduino (SCPI 2.0.0) via PTY.

    Runs in a background daemon thread; callers interact through the PTY slave
    path returned by start().

    ADC intensity follows Malus's law on encoder-A effective angle so that
    tests and the UI get physically meaningful data without real hardware.
    """

    DEFAULT_POLL_INTERVAL_MS = 50
    ENCODER_A_BASE_SPEED = 0.5
    ENCODER_B_BASE_SPEED = 0.3

    def __init__(
        self,
        encoder_a_speed: float = ENCODER_A_BASE_SPEED,
        encoder_b_speed: float = ENCODER_B_BASE_SPEED,
        poll_interval_ms: int = DEFAULT_POLL_INTERVAL_MS,
        start_angle_a: float = 0.0,
        start_angle_b: float = 0.0,
    ):
        self.encoder_a_speed = encoder_a_speed
        self.encoder_b_speed = encoder_b_speed
        self.poll_interval_ms = poll_interval_ms

        self.encoder_a = MockEncoderState(
            current_angle=start_angle_a, base_angle=start_angle_a
        )
        self.encoder_b = MockEncoderState(
            current_angle=start_angle_b, base_angle=start_angle_b
        )

        # ADC config mirrors CONF:ADC:* commands
        self.adc_gain: int = 1
        self.adc_mux: str = "DIFF01"
        self.adc_rate: int = 20
        self.adc_mode: str = "NORM"
        self.adc_fir: str = "OFF"
        self.adc_vref: str = "EXT"
        self.adc_temp_enabled: bool = False

        # PD-TIA discrete gain stage (0 = lowest gain)
        self.pdtia_gain: int = 0

        # Streaming state — set by CONF:SRC and INIT:CONT.
        # Use expanded token form internally (ENC:BOTH is expanded on CONF:SRC write).
        self._stream_sources: set[str] = {"ENC:A", "ENC:B"}
        self.stream_rate_hz: int = 1000 // poll_interval_ms
        self.continuous_running: bool = False

        # Firmware version string — override in tests to check incompatibility
        self._firmware_version: str = "2.0.0"

        # Debug mode
        self._debug_mode: bool = False

        # Frame sequence counter (mirrors firmware s_frameSeq)
        self._frame_seq: int = 0

        # PTY pair
        self.pty_master: Optional[int] = None
        self.pty_slave: Optional[int] = None
        self.pty_slave_path: Optional[str] = None

        self._running = False
        self._stop_flag = False
        self._thread: Optional[threading.Thread] = None
        self._start_time = time.time()
        self._port_file: Optional[Path] = None

    # ── Public control ────────────────────────────────────────────────────────

    def start(self) -> str:
        """Start simulator; returns PTY slave path."""
        if not _PTY_AVAILABLE:
            raise NotImplementedError(
                "MockArduino requires PTY support (pty/tty/select) which is not "
                "available on Windows. Run PTY-based tests on Linux or macOS."
            )
        if self._running:
            Debug.warning("MockArduino already running")
            return self.pty_slave_path  # type: ignore[return-value]

        try:
            self.pty_master, self.pty_slave = pty.openpty()
            self.pty_slave_path = os.ttyname(self.pty_slave)
            tty.setraw(self.pty_master)
            self._port_file = register_mock_port(self.pty_slave_path)

            self._running = True
            self._stop_flag = False
            self._start_time = time.time()

            self._thread = threading.Thread(target=self._run_loop, daemon=False)
            self._thread.start()

            Debug.info(f"MockArduino PTY: {self.pty_slave_path}")
            return self.pty_slave_path  # type: ignore[return-value]

        except Exception as e:
            Debug.error(f"Failed to start MockArduino: {e}", exc_info=True)
            self._cleanup()
            raise RuntimeError(f"Failed to create PTY: {e}") from e

    def stop(self) -> None:
        """Stop the simulator."""
        if not self._running:
            unregister_mock_port(self._port_file)
            self._port_file = None
            return
        self._stop_flag = True
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)

    def set_encoder_a_angle(self, angle: float) -> None:
        self.encoder_a.current_angle = angle
        self.encoder_a.base_angle = angle
        self.encoder_a.poll_count = 0

    def set_encoder_b_angle(self, angle: float) -> None:
        self.encoder_b.current_angle = angle
        self.encoder_b.base_angle = angle
        self.encoder_b.poll_count = 0

    def set_firmware_version(self, version: str) -> None:
        """Override firmware version string — use in tests for mismatch testing."""
        self._firmware_version = version

    def get_state(self) -> dict:
        """Return a snapshot of current mock state (for test assertions)."""
        return {
            "continuous_running": self.continuous_running,
            "stream_sources": sorted(self._stream_sources),
            "stream_rate_hz": self.stream_rate_hz,
            "poll_interval_ms": self.poll_interval_ms,
            "pdtia_gain": self.pdtia_gain,
            "adc_gain": self.adc_gain,
            "encoder_a": {
                "current_angle": self.encoder_a.current_angle,
                "zero_offset": self.encoder_a.zero_offset,
                "effective_angle": self.encoder_a.get_effective_angle(),
                "raw_value": self.encoder_a.get_raw_value(),
                "poll_count": self.encoder_a.poll_count,
            },
            "encoder_b": {
                "current_angle": self.encoder_b.current_angle,
                "zero_offset": self.encoder_b.zero_offset,
                "effective_angle": self.encoder_b.get_effective_angle(),
                "raw_value": self.encoder_b.get_raw_value(),
                "poll_count": self.encoder_b.poll_count,
            },
        }

    # ── PTY loop ──────────────────────────────────────────────────────────────

    def _cleanup(self) -> None:
        unregister_mock_port(self._port_file)
        self._port_file = None
        for fd in (self.pty_master, self.pty_slave):
            if fd is not None:
                try:
                    os.close(fd)
                except OSError:
                    pass
        self.pty_master = self.pty_slave = None

    def _run_loop(self) -> None:
        try:

            last_poll = time.time()

            while not self._stop_flag:
                try:
                    readable, _, _ = select.select([self.pty_master], [], [], 0.01)
                except (OSError, ValueError):
                    break

                if readable:
                    self._process_incoming()

                now = time.time()
                interval_s = self.poll_interval_ms / 1000.0
                if now - last_poll >= interval_s:
                    if self.continuous_running:
                        self._emit_frame()
                    last_poll = now

        except (OSError, RuntimeError) as e:
            Debug.error(f"MockArduino loop error: {e}", exc_info=True)
        finally:
            self._cleanup()

    def _process_incoming(self) -> None:
        try:
            data = os.read(self.pty_master, 1024)  # type: ignore[arg-type]
        except OSError:
            return
        if not data:
            return
        text = data.decode("utf-8", errors="ignore")
        for raw in text.split("\n"):
            cmd = raw.strip()
            if not cmd:
                continue
            Debug.debug(f"MockArduino ← {cmd}")
            response = self._handle_command(cmd)
            if response is not None:
                Debug.debug(f"MockArduino → {response}")
                self._write_response(response + "\n")

    def _write_response(self, text: str) -> None:
        try:
            os.write(self.pty_master, text.encode("utf-8"))  # type: ignore[arg-type]
        except OSError as e:
            Debug.debug(f"PTY write error: {e}")

    # ── SCPI command dispatcher ───────────────────────────────────────────────

    def _handle_command(self, raw_cmd: str) -> Optional[str]:
        cmd = raw_cmd.upper().strip()

        # '?' may appear inside the command before a parameter
        # (e.g. 'MEAS:ENC:ANGL? BOTH') or at the very end (e.g. '*IDN?').
        # Detect it by presence, not by position.
        is_query = "?" in cmd

        # Split on first space; then strip '?' from the header mnemonic
        header, _, param = cmd.partition(" ")
        header = header.replace("?", "")
        param = param.strip()

        # ── IEEE 488.2 common ────────────────────────────────────────────────
        if header == "*IDN":
            if is_query:
                return f"Polarisation-UI,GoniometerBench,0,{self._firmware_version}"
            return None

        if header == "*RST":
            self._reset_state()
            return None

        if header == "*CLS":
            return None

        if header == "*TST":
            return "0" if is_query else None

        if header == "*OPC":
            return "1" if is_query else None

        if header == "*WAI":
            return None

        # ── MEAS subsystem ────────────────────────────────────────────────────
        if header == "MEAS:ENC:ANGL" and is_query:
            return self._cmd_meas_enc_angl(param)

        if header == "MEAS:ENC:MAGN" and is_query:
            return self._cmd_meas_enc_magn(param)

        if header == "MEAS:ADC:VOLT" and is_query:
            return f"{self._compute_adc_voltage():.6f}"

        if header == "MEAS:ADC:TEMP" and is_query:
            return f"{self._compute_adc_temperature():.2f}"

        if header == "MEAS:ALL" and is_query:
            ts = int((time.time() - self._start_time) * 1000)
            a = self.encoder_a.get_effective_angle()
            b = self.encoder_b.get_effective_angle()
            ma = self.encoder_a.get_raw_value()
            mb = self.encoder_b.get_raw_value()
            v = self._compute_adc_voltage()
            return f"{ts},{a:.2f},{b:.2f},{ma},{mb},{v:.6f}"

        # ── CONF subsystem ────────────────────────────────────────────────────
        if header == "CONF:ADC:MUX":
            if not is_query:
                self.adc_mux = param
                return None
            return self.adc_mux

        if header == "CONF:ADC:GAIN":
            if not is_query:
                try:
                    self.adc_gain = int(param)
                except ValueError:
                    pass
                return None
            return str(self.adc_gain)

        if header == "CONF:ADC:RATE":
            if not is_query:
                try:
                    self.adc_rate = int(param)
                except ValueError:
                    pass
                return None
            return str(self.adc_rate)

        if header == "CONF:ADC:MODE":
            if not is_query:
                self.adc_mode = param
                return None
            return self.adc_mode

        if header == "CONF:ADC:FIR":
            if not is_query:
                self.adc_fir = param
                return None
            return self.adc_fir

        if header == "CONF:ADC:VREF":
            if not is_query:
                self.adc_vref = param
                return None
            return self.adc_vref

        if header == "CONF:ADC:TEMP":
            if not is_query:
                self.adc_temp_enabled = param == "ON"
                return None
            return "ON" if self.adc_temp_enabled else "OFF"

        if header == "CONF:PDTIA:GAIN":
            if not is_query:
                try:
                    self.pdtia_gain = int(param)
                except ValueError:
                    pass
                return None
            bits = f"{self.pdtia_gain & 0xF:04b}"
            return f"{self.pdtia_gain},0b{bits}"

        if header == "CONF:ENC:ZERO":
            if param in ("A", ""):
                self.encoder_a.zero_offset = self.encoder_a.current_angle
            elif param == "B":
                self.encoder_b.zero_offset = self.encoder_b.current_angle
            elif param == "BOTH":
                self.encoder_a.zero_offset = self.encoder_a.current_angle
                self.encoder_b.zero_offset = self.encoder_b.current_angle
            return None

        if header == "CONF:ENC:ERR":
            return None  # no hardware error flag to clear in mock

        if header == "CONF:SRC":
            if not is_query:
                # Expand ENC:BOTH shorthand to both tokens for internal tracking
                tokens: set[str] = set()
                for s in param.split(","):
                    t = s.strip()
                    if t == "ENC:BOTH":
                        tokens.add("ENC:A")
                        tokens.add("ENC:B")
                    elif t:
                        tokens.add(t)
                self._stream_sources = tokens
                return None
            return ",".join(sorted(self._stream_sources))

        if header == "CONF:RATE":
            if not is_query:
                try:
                    hz = int(param)
                    if hz > 0:
                        self.stream_rate_hz = hz
                        self.poll_interval_ms = max(1, 1000 // hz)
                except ValueError:
                    pass
                return None
            return str(self.stream_rate_hz)

        # ── SENS subsystem ────────────────────────────────────────────────────
        if header == "SENS:ADC:MUX" and is_query:
            return self.adc_mux

        if header == "SENS:ADC:GAIN" and is_query:
            return str(self.adc_gain)

        if header == "SENS:ADC:RATE" and is_query:
            return str(self.adc_rate)

        if header == "SENS:ADC:MODE" and is_query:
            return self.adc_mode

        if header == "SENS:ADC:FIR" and is_query:
            return self.adc_fir

        if header == "SENS:ADC:VREF" and is_query:
            return self.adc_vref

        if header == "SENS:ADC:TEMP" and is_query:
            return "ON" if self.adc_temp_enabled else "OFF"

        if header == "SENS:PDTIA:GAIN" and is_query:
            return str(self.pdtia_gain)

        if header == "SENS:SRC" and is_query:
            return ",".join(sorted(self._stream_sources))

        if header == "SENS:RATE" and is_query:
            return str(self.stream_rate_hz)

        # ── INIT / FETC / ABOR ───────────────────────────────────────────────
        if header == "INIT:CONT":
            if is_query:
                return "1" if self.continuous_running else "0"
            if param == "ON":
                self.continuous_running = True
            elif param in ("OFF", "0"):
                self.continuous_running = False
            return None

        if header == "INIT":
            # Single-shot arm: emit one frame immediately
            self._emit_frame()
            return None

        if header == "ABOR":
            self.continuous_running = False
            return None

        if header == "FETC:ENC:ANGL" and is_query:
            return self._cmd_meas_enc_angl(param)

        if header == "FETC:ADC:VOLT" and is_query:
            return f"{self._compute_adc_voltage():.6f}"

        if header == "FETC:ALL" and is_query:
            ts = int((time.time() - self._start_time) * 1000)
            a = self.encoder_a.get_effective_angle()
            b = self.encoder_b.get_effective_angle()
            v = self._compute_adc_voltage()
            return f"{ts},{a:.2f},{b:.2f},{v:.6f}"

        # ── DIAG subsystem ───────────────────────────────────────────────────
        if header == "DIAG:ENC" and is_query:
            if param == "BOTH":
                return (
                    "compHA=0,compLA=0,cofA=0,ocfA=1,agcA=200,"
                    "compHB=0,compLB=0,cofB=0,ocfB=1,agcB=195"
                )
            agc = 195 if param == "B" else 200
            return f"compH=0,compL=0,cof=0,ocf=1,agc={agc}"

        if header == "DIAG:ADC" and is_query:
            return "reg0=0x00,reg1=0x04,reg2=0x00,reg3=0x00,drdy=1,last_raw=0x800000"

        if header == "DIAG:PDTIA" and is_query:
            bits = f"{self.pdtia_gain & 0xF:04b}"
            return f"stage={self.pdtia_gain},pattern=0b{bits}"

        if header == "DIAG:SELF" and is_query:
            return "ENC_A=PASS,ENC_B=PASS,ADC=PASS,PDTIA=PASS"

        # ── SYST subsystem ───────────────────────────────────────────────────
        if header == "SYST:ERR" and is_query:
            return '0,"No error"'

        if header == "SYST:VERS" and is_query:
            return self._firmware_version

        if header == "SYST:UPTIME" and is_query:
            return str(int((time.time() - self._start_time) * 1000))

        if header == "SYST:DEB":
            if is_query:
                return "1" if self._debug_mode else "0"
            self._debug_mode = param == "ON"
            return None

        if header == "SYST:HELP" and is_query:
            return (
                "SCPI 2.0.0: MEAS:ENC:ANGL?,MEAS:ADC:VOLT?,MEAS:ADC:TEMP?,"
                "CONF:ADC:*,CONF:PDTIA:GAIN,CONF:ENC:ZERO,CONF:SRC,CONF:RATE,"
                "DIAG:ENC?,DIAG:ADC?,DIAG:SELF?,INIT:CONT,ABOR,SYST:ERR?"
            )

        Debug.debug(f"MockArduino: unknown command '{raw_cmd}'")
        return None

    # ── Helper commands ───────────────────────────────────────────────────────

    def _cmd_meas_enc_angl(self, param: str) -> str:
        if param in ("A", ""):
            return f"{self.encoder_a.get_effective_angle():.2f}"
        if param == "B":
            return f"{self.encoder_b.get_effective_angle():.2f}"
        if param == "BOTH":
            a = self.encoder_a.get_effective_angle()
            b = self.encoder_b.get_effective_angle()
            return f"{a:.2f},{b:.2f}"
        return "ERROR"

    def _cmd_meas_enc_magn(self, param: str) -> str:
        if param in ("A", ""):
            return str(self.encoder_a.get_raw_value())
        if param == "B":
            return str(self.encoder_b.get_raw_value())
        if param == "BOTH":
            return f"{self.encoder_a.get_raw_value()},{self.encoder_b.get_raw_value()}"
        return "ERROR"

    # ── Simulation helpers ────────────────────────────────────────────────────

    def _compute_adc_voltage(self) -> float:
        """Malus's law: V = V_REF * cos²(sample_angle)."""
        angle_rad = math.radians(self.encoder_a.get_effective_angle())
        signal = _V_REF * (math.cos(angle_rad) ** 2)
        signal += random.gauss(0.0, 0.002)
        return round(max(0.0, min(_V_REF, signal)), 6)

    def _compute_adc_temperature(self) -> float:
        return round(_TEMP_NOMINAL + random.gauss(0.0, 0.1), 2)

    def _reset_state(self) -> None:
        self.continuous_running = False
        self._stream_sources = {"ENC:A", "ENC:B"}
        self.stream_rate_hz = 1000 // self.DEFAULT_POLL_INTERVAL_MS
        self.poll_interval_ms = self.DEFAULT_POLL_INTERVAL_MS
        self.adc_gain = 1
        self.adc_mux = "DIFF01"
        self.adc_rate = 20
        self.adc_mode = "NORM"
        self.adc_fir = "OFF"
        self.adc_vref = "EXT"
        self.adc_temp_enabled = True
        self.pdtia_gain = 0
        self._frame_seq = 0

    # ── Streaming ─────────────────────────────────────────────────────────────

    def _emit_frame(self) -> None:
        """Build and send a DATA:FRAME line based on configured sources."""
        # Advance encoder angles for simulation
        self.encoder_a.poll_count += 1
        self.encoder_b.poll_count += 1
        self.encoder_a.current_angle = (
            self.encoder_a.base_angle + self.encoder_a.poll_count * self.encoder_a_speed
        )
        self.encoder_b.current_angle = (
            self.encoder_b.base_angle + self.encoder_b.poll_count * self.encoder_b_speed
        )

        self._frame_seq += 1
        ts_ms = int((time.time() - self._start_time) * 1000)
        parts = [f"DATA:FRAME seq={self._frame_seq}", f"tsMs={ts_ms}"]

        srcs = self._stream_sources
        enc_a_active = "ENC:A" in srcs or "ENC:BOTH" in srcs
        enc_b_active = "ENC:B" in srcs or "ENC:BOTH" in srcs
        diag_active = "DIAG" in srcs

        if enc_a_active:
            parts.append(f"angA={self.encoder_a.get_effective_angle():.2f}")
            if diag_active:
                parts.append("agcA=200")
                parts.append("dstatA=1")  # ocf=1, all other flags clear
        if enc_b_active:
            parts.append(f"angB={self.encoder_b.get_effective_angle():.2f}")
            if diag_active:
                parts.append("agcB=195")
                parts.append("dstatB=1")

        if "ADC" in srcs:
            parts.append(f"adcV={self._compute_adc_voltage():.6f}")
        if "ADC:T" in srcs:
            parts.append(f"adcT={self._compute_adc_temperature():.2f}")

        if "PDTIA" in srcs:
            parts.append(f"pdGain={self.pdtia_gain}")
        parts.append("stat=0")

        self._write_response(",".join(parts) + "\n")


def main() -> int:
    """CLI entry point for manual testing."""
    import argparse
    import signal

    if not _PTY_AVAILABLE:
        print(
            "MockArduino cannot run on Windows because PTY support is unavailable.",
            file=sys.stderr,
        )
        return 1

    parser = argparse.ArgumentParser(description="MockArduino SCPI 2.0.0 via PTY")
    parser.add_argument(
        "--speed-a", type=float, default=MockArduino.ENCODER_A_BASE_SPEED
    )
    parser.add_argument(
        "--speed-b", type=float, default=MockArduino.ENCODER_B_BASE_SPEED
    )
    parser.add_argument(
        "--interval", type=int, default=MockArduino.DEFAULT_POLL_INTERVAL_MS
    )
    parser.add_argument("--start-a", type=float, default=0.0)
    parser.add_argument("--start-b", type=float, default=0.0)
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default=os.environ.get("MOCK_ARDUINO_LOG_LEVEL", "INFO"),
    )
    parser.add_argument("--no-startup-info", action="store_true")
    args = parser.parse_args()

    level_map = {
        "DEBUG": Debug.DEBUG_VERBOSE,
        "INFO": Debug.DEBUG_INFO,
        "WARNING": Debug.DEBUG_ERROR,
        "ERROR": Debug.DEBUG_ERROR,
    }
    Debug.init(
        debug_level=level_map.get(args.log_level, Debug.DEBUG_INFO),
        app_name="MockArduino",
    )

    mock = MockArduino(
        encoder_a_speed=args.speed_a,
        encoder_b_speed=args.speed_b,
        poll_interval_ms=args.interval,
        start_angle_a=args.start_a,
        start_angle_b=args.start_b,
    )

    if not args.no_startup_info:
        print("MockArduino SCPI 2.0.0 starting...")

    pty_path = mock.start()

    if not args.no_startup_info:
        print(f"PTY Slave Path: {pty_path}")
    else:
        print(pty_path)

    stop_requested = threading.Event()

    def _request_stop(_signum, _frame) -> None:
        stop_requested.set()

    signal.signal(signal.SIGINT, _request_stop)
    signal.signal(signal.SIGTERM, _request_stop)

    try:
        while not stop_requested.is_set():
            time.sleep(0.1)
    finally:
        mock.stop()

    return 0


if __name__ == "__main__":
    sys.exit(main())
