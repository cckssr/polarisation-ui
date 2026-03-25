"""
Mock Arduino for testing dual encoder system via pseudo-terminal (PTY).

Based on gmcounter's proven PTY design pattern.
Uses select.select() for non-blocking I/O and synchronous command processing.

Features:
    - Creates a PTY pair for serial communication testing
    - Simulates two encoders with independently changing values
    - Supports all Arduino commands (R_A, R_B, Z_A, Z_B, continuous modes, etc.)
    - Handles zero position offsets correctly
    - Non-blocking I/O with select.select()
    - Graceful shutdown
"""

import os
import pty
import tty
import select
import time
import sys
import threading
from dataclasses import dataclass
from typing import Optional

from ..logging import Debug


@dataclass
class MockEncoderState:
    """State for one encoder simulation."""

    current_angle: float = 0.0
    zero_offset: float = 0.0
    base_angle: float = 0.0
    poll_count: int = 0

    def get_effective_angle(self) -> float:
        """Get angle accounting for zero offset."""
        return self.current_angle - self.zero_offset

    def get_raw_value(self) -> int:
        """Convert angle to raw encoder count (AS5048A: 14-bit = 16384 counts/rotation)."""
        return int((self.get_effective_angle() % 360.0) / 360.0 * 16384) % 65536


class MockArduino:
    """
    Simulated Arduino encoder system via PTY.

    Uses non-blocking I/O with select.select() for reliable communication.
    Runs in a background thread.
    """

    DEFAULT_POLL_INTERVAL = 50
    ENCODER_A_BASE_SPEED = 0.5
    ENCODER_B_BASE_SPEED = 0.3

    def __init__(
        self,
        encoder_a_speed: float = ENCODER_A_BASE_SPEED,
        encoder_b_speed: float = ENCODER_B_BASE_SPEED,
        poll_interval_ms: int = DEFAULT_POLL_INTERVAL,
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

        self.mode = "IDLE"
        self.continuous_running = False

        # PTY pair
        self.pty_master = None
        self.pty_slave = None
        self.pty_slave_path = None

        # Control
        self._running = False
        self._stop_flag = False
        self._thread = None

    def start(self) -> str:
        """
        Start the mock Arduino simulator in background thread.

        Returns:
            str: Path to the slave PTY (e.g., '/dev/pts/5').
        """
        if self._running:
            Debug.warning("MockArduino already running")
            return self.pty_slave_path

        try:
            # Create PTY pair
            self.pty_master, self.pty_slave = pty.openpty()
            self.pty_slave_path = os.ttyname(self.pty_slave)

            Debug.info(f"MockArduino PTY created: {self.pty_slave_path}")

            # Set raw mode for proper binary communication
            tty.setraw(self.pty_master)

            self._running = True
            self._stop_flag = False

            # Start loop in background thread (daemon=False for clean shutdown)
            self._thread = threading.Thread(target=self._run_loop, daemon=False)
            self._thread.start()

            return self.pty_slave_path

        except Exception as e:
            Debug.error(f"Failed to start MockArduino: {e}", exc_info=True)
            self._cleanup()
            raise RuntimeError(f"Failed to create PTY: {e}") from e

    def stop(self) -> None:
        """Stop the mock Arduino simulator."""
        if not self._running:
            return

        Debug.info("Stopping MockArduino simulator")
        self._stop_flag = True
        self._running = False

        # Wait for thread to finish
        if self._thread:
            self._thread.join(timeout=1.0)

    def _cleanup(self) -> None:
        """Close PTY file descriptors."""
        try:
            if self.pty_master is not None:
                os.close(self.pty_master)
        except OSError:
            pass
        finally:
            self.pty_master = None

        try:
            if self.pty_slave is not None:
                os.close(self.pty_slave)
        except OSError:
            pass
        finally:
            self.pty_slave = None

    def _run_loop(self) -> None:
        """
        Main loop of the mock Arduino simulator (blocking, runs in background thread).

        Uses select.select() for non-blocking reads with small timeout.
        """
        try:
            # Send startup info
            self._write_response("DATA:INFO AS5048A MockArduino SCPI Ready\n")
            self._write_response("DATA:INFO Send SYST:HELP? for command reference\n")

            last_poll_time = time.time()
            poll_interval_sec = self.poll_interval_ms / 1000.0

            while not self._stop_flag:
                # Non-blocking read with 10ms timeout
                try:
                    readable, _, _ = select.select([self.pty_master], [], [], 0.01)
                except (OSError, ValueError):
                    # PTY closed or error
                    break

                if readable:
                    self._process_incoming_data()

                # Update continuous mode periodically
                current_time = time.time()
                if current_time - last_poll_time >= poll_interval_sec:
                    if self.continuous_running:
                        self._send_continuous_data()
                    last_poll_time = current_time

        except (OSError, RuntimeError) as e:
            Debug.error(f"MockArduino loop error: {e}", exc_info=True)
        finally:
            self._cleanup()

    def _process_incoming_data(self) -> None:
        """Read and process incoming commands."""
        try:
            data = os.read(self.pty_master, 1024)
            if not data:
                return

            text = data.decode("utf-8", errors="ignore")
            commands = [cmd.strip() for cmd in text.split("\n") if cmd.strip()]

            for cmd in commands:
                Debug.debug(f"MockArduino received: {cmd}")
                response = self._handle_command(cmd)
                if response:
                    Debug.debug(f"MockArduino sending: {response}")
                    self._write_response(response + "\n")

        except OSError as e:
            Debug.debug(f"PTY read error: {e}")

    def _handle_command(self, cmd: str) -> Optional[str]:
        """Process a SCPI command and return response (None = no response)."""
        cmd = cmd.upper().strip()

        # Strip trailing '?' to detect queries
        is_query = cmd.endswith("?")
        if is_query:
            cmd = cmd[:-1].strip()

        # Split into header and parameter
        header, _, param = cmd.partition(" ")
        param = param.strip()

        # Common commands
        if header == "*IDN":
            return "Polarisation-UI,AS5048A-DualEncoder,0,1.0" if is_query else None

        if header == "*RST":
            self.mode = "IDLE"
            self.continuous_running = False
            self.poll_interval_ms = self.DEFAULT_POLL_INTERVAL
            return None

        if header == "*CLS":
            return None

        # MEAS:ANGL? A|B|BOTH
        if header == "MEAS:ANGL" and is_query:
            if param == "A" or param == "":
                return f"{self.encoder_a.get_effective_angle():.2f}"
            if param == "B":
                return f"{self.encoder_b.get_effective_angle():.2f}"
            if param == "BOTH":
                a = self.encoder_a.get_effective_angle()
                b = self.encoder_b.get_effective_angle()
                return f"{a:.2f},{b:.2f}"

        # MEAS:MAGN? A|B|BOTH
        if header == "MEAS:MAGN" and is_query:
            if param == "A" or param == "":
                return str(self.encoder_a.get_raw_value())
            if param == "B":
                return str(self.encoder_b.get_raw_value())
            if param == "BOTH":
                return f"{self.encoder_a.get_raw_value()},{self.encoder_b.get_raw_value()}"

        # CONF:ZERO A|B|BOTH
        if header == "CONF:ZERO":
            if param == "A" or param == "":
                self.encoder_a.zero_offset = self.encoder_a.current_angle
            elif param == "B":
                self.encoder_b.zero_offset = self.encoder_b.current_angle
            elif param == "BOTH":
                self.encoder_a.zero_offset = self.encoder_a.current_angle
                self.encoder_b.zero_offset = self.encoder_b.current_angle
            return None

        # CONF:ERR A|B|BOTH  — no-op in mock (no hardware EF to clear)
        if header == "CONF:ERR":
            return None

        # INIT ON,<target> | INIT OFF
        if header == "INIT":
            if param.startswith("ON"):
                target = param[2:].lstrip(",").strip() or "A"
                if target == "A":
                    self.mode = "CONTINUOUS_A"
                    self.encoder_a.poll_count = 0
                elif target == "B":
                    self.mode = "CONTINUOUS_B"
                    self.encoder_b.poll_count = 0
                elif target == "BOTH":
                    self.mode = "CONTINUOUS_BOTH"
                    self.encoder_a.poll_count = 0
                    self.encoder_b.poll_count = 0
                elif target == "MAG":
                    self.mode = "CONTINUOUS_MAG"
                elif target == "NOP":
                    self.mode = "CONTINUOUS_NOP"
                self.continuous_running = True
            elif param in ("OFF", "0"):
                self.mode = "IDLE"
                self.continuous_running = False
            return None

        # ABOR
        if header == "ABOR":
            self.mode = "IDLE"
            self.continuous_running = False
            return None

        # SENS:INT <ms> | SENS:INT?
        if header == "SENS:INT":
            if is_query:
                return str(self.poll_interval_ms)
            try:
                interval = int(param)
                if 1 <= interval <= 9999:
                    self.poll_interval_ms = interval
            except ValueError:
                pass
            return None

        # SYST:ERR?
        if header == "SYST:ERR" and is_query:
            return '0,"No error"'

        # SYST:DIAG? A|B
        if header == "SYST:DIAG" and is_query:
            if param == "B":
                return "0,0,0,1,195"
            return "0,0,0,1,200"

        # SYST:DEB ON|OFF | SYST:DEB?
        if header == "SYST:DEB":
            if is_query:
                return "0"
            return None

        # SYST:HELP?
        if header == "SYST:HELP" and is_query:
            return "INFO:AS5048A MockArduino SCPI interface"

        return None

    def _send_continuous_data(self) -> None:
        """Send streaming data in continuous mode."""
        if self.mode == "CONTINUOUS_A":
            self.encoder_a.poll_count += 1
            self.encoder_a.current_angle = (
                self.encoder_a.base_angle
                + self.encoder_a.poll_count * self.encoder_a_speed
            )
            response = self._format_encoder_a()
        elif self.mode == "CONTINUOUS_B":
            self.encoder_b.poll_count += 1
            self.encoder_b.current_angle = (
                self.encoder_b.base_angle
                + self.encoder_b.poll_count * self.encoder_b_speed
            )
            response = self._format_encoder_b()
        elif self.mode == "CONTINUOUS_BOTH":
            self.encoder_a.poll_count += 1
            self.encoder_b.poll_count += 1
            self.encoder_a.current_angle = (
                self.encoder_a.base_angle
                + self.encoder_a.poll_count * self.encoder_a_speed
            )
            self.encoder_b.current_angle = (
                self.encoder_b.base_angle
                + self.encoder_b.poll_count * self.encoder_b_speed
            )
            response = self._format_both_encoders()
        else:
            return

        if response:
            self._write_response(response + "\n")

    def _format_encoder_a(self) -> str:
        """Format streaming encoder A response: DATA:ANGL A,<deg>"""
        angle = self.encoder_a.get_effective_angle()
        return f"DATA:ANGL A,{angle:.2f}"

    def _format_encoder_b(self) -> str:
        """Format streaming encoder B response: DATA:ANGL B,<deg>"""
        angle = self.encoder_b.get_effective_angle()
        return f"DATA:ANGL B,{angle:.2f}"

    def _format_both_encoders(self) -> str:
        """Format streaming both-encoder response: DATA:ANGL BOTH,<a>,<b>"""
        angle_a = self.encoder_a.get_effective_angle()
        angle_b = self.encoder_b.get_effective_angle()
        return f"DATA:ANGL BOTH,{angle_a:.2f},{angle_b:.2f}"

    def _write_response(self, response: str) -> None:
        """Write response to the PTY master."""
        try:
            os.write(self.pty_master, response.encode("utf-8"))
        except OSError as e:
            Debug.debug(f"PTY write error: {e}")

    def get_state(self) -> dict:
        """Get current state of both encoders (for debugging)."""
        return {
            "mode": self.mode,
            "continuous_running": self.continuous_running,
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
            "poll_interval_ms": self.poll_interval_ms,
        }

    def set_encoder_a_angle(self, angle: float) -> None:
        """Manually set encoder A angle (for testing)."""
        self.encoder_a.current_angle = angle
        self.encoder_a.base_angle = angle
        self.encoder_a.poll_count = 0
        Debug.debug(f"MockArduino encoder A angle set to {angle}°")

    def set_encoder_b_angle(self, angle: float) -> None:
        """Manually set encoder B angle (for testing)."""
        self.encoder_b.current_angle = angle
        self.encoder_b.base_angle = angle
        self.encoder_b.poll_count = 0
        Debug.debug(f"MockArduino encoder B angle set to {angle}°")


def main() -> int:
    """CLI entry point for MockArduino."""
    import argparse
    import signal

    parser = argparse.ArgumentParser(
        description="MockArduino - Simulated Arduino Encoder System via PTY"
    )

    parser.add_argument(
        "--speed-a",
        type=float,
        default=MockArduino.ENCODER_A_BASE_SPEED,
        help="Encoder A speed in degrees per poll",
    )

    parser.add_argument(
        "--speed-b",
        type=float,
        default=MockArduino.ENCODER_B_BASE_SPEED,
        help="Encoder B speed in degrees per poll",
    )

    parser.add_argument(
        "--interval",
        type=int,
        default=MockArduino.DEFAULT_POLL_INTERVAL,
        help="Poll interval in milliseconds",
    )

    parser.add_argument(
        "--start-a",
        type=float,
        default=0.0,
        help="Starting angle for encoder A",
    )

    parser.add_argument(
        "--start-b",
        type=float,
        default=0.0,
        help="Starting angle for encoder B",
    )

    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default=os.environ.get("MOCK_ARDUINO_LOG_LEVEL", "INFO"),
        help="Logging level",
    )

    parser.add_argument(
        "--no-startup-info",
        action="store_true",
        help="Don't print startup information",
    )

    args = parser.parse_args()

    # Setup logging
    debug_level_map = {
        "DEBUG": Debug.DEBUG_VERBOSE,
        "INFO": Debug.DEBUG_INFO,
        "WARNING": Debug.DEBUG_ERROR,
        "ERROR": Debug.DEBUG_ERROR,
    }
    Debug.init(
        debug_level=debug_level_map.get(args.log_level, Debug.DEBUG_INFO),
        app_name="MockArduino",
    )

    try:
        mock = MockArduino(
            encoder_a_speed=args.speed_a,
            encoder_b_speed=args.speed_b,
            poll_interval_ms=args.interval,
            start_angle_a=args.start_a,
            start_angle_b=args.start_b,
        )

        if not args.no_startup_info:
            print("MockArduino starting...")

        pty_path = mock.start()

        if not args.no_startup_info:
            print(f"PTY Slave Path: {pty_path}")
        else:
            print(pty_path)

    except RuntimeError as e:
        Debug.error(f"Failed to start MockArduino: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
