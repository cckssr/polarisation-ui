"""
Arduino Encoder Communication for AS5048A (SCPI protocol, firmware 2.0.0).

Communicates with the Arduino running the AS5048A firmware.
Uses SCPI commands: MEAS:ENC:ANGL? A to read angle, CONF:ENC:ZERO A to set zero, etc.
"""

import re
import time
from typing import Optional, Tuple

import serial


class ArduinoEncoder:
    """
    Interface to AS5048A encoder via Arduino (SCPI protocol).

    Protocol:
        Send: MEAS:ENC:ANGL? A   (read angle encoder A)
        Receive: 45.23           (bare float in degrees)

    Example:
        >>> encoder = ArduinoEncoder("/dev/cu.usbmodem1101")
        >>> encoder.connect()
        >>> angle = encoder.read_angle()
        >>> print(f"Angle: {angle:.2f}°")
        >>> encoder.disconnect()
    """

    # Streaming data pattern: DATA:ANGL A,45.23
    STREAM_ANGLE_PATTERN = re.compile(
        r"DATA:ANGL\s+([AB]|BOTH),(-?\d+\.?\d*)(?:,(-?\d+\.?\d*))?"
    )

    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 1.0):
        """
        Initialize encoder connection.

        Args:
            port: Serial port (e.g., /dev/cu.usbmodem1101)
            baudrate: Baud rate (default 115200)
            timeout: Read timeout in seconds
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self._serial: Optional[serial.Serial] = None
        self._connected = False

    @property
    def connected(self) -> bool:
        """Check if connected to Arduino."""
        return self._connected and self._serial is not None and self._serial.is_open

    def connect(self) -> bool:
        """
        Open serial connection to Arduino and verify it responds.

        Sends *IDN? after reset; requires a non-empty response to confirm
        the device is alive and speaking SCPI. Does not check firmware version
        (caller's responsibility if needed).

        Returns:
            True if connection successful and device responds, False otherwise
        """
        try:
            self._serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
            )
            # Wait for Arduino to reset after USB enumeration
            time.sleep(2.0)
            self._serial.reset_input_buffer()
            self._serial.reset_output_buffer()

            # Verify the device responds to SCPI identification
            self._serial.write(b"*IDN?\n")
            self._serial.flush()
            idn = self._serial.readline().decode("utf-8", errors="replace").strip()
            if not idn:
                print(f"[ArduinoEncoder] No IDN response on {self.port}")
                self._serial.close()
                return False

            self._connected = True
            print(f"[ArduinoEncoder] Connected to {self.port}: {idn}")
            return True
        except serial.SerialException as e:
            print(f"[ArduinoEncoder] Failed to connect: {e}")
            self._connected = False
            return False

    def disconnect(self) -> None:
        """Close serial connection."""
        if self._serial and self._serial.is_open:
            self._serial.close()
        self._connected = False
        print("[ArduinoEncoder] Disconnected")

    def _send_command(self, cmd: str) -> None:
        """Send SCPI command to Arduino."""
        if not self.connected:
            raise RuntimeError("Not connected to Arduino")
        self._serial.write(f"{cmd}\n".encode("utf-8"))
        self._serial.flush()

    def _read_line(self, timeout: Optional[float] = None) -> Optional[str]:
        """
        Read a line from Arduino.

        Args:
            timeout: Optional override for read timeout

        Returns:
            Line string (without newline) or None if timeout
        """
        if not self.connected:
            return None

        old_timeout = self._serial.timeout
        if timeout is not None:
            self._serial.timeout = timeout

        try:
            line = self._serial.readline().decode("utf-8").strip()
            return line if line else None
        finally:
            self._serial.timeout = old_timeout

    def read_angle(self, encoder_id: str = "A") -> Optional[float]:
        """
        Read angle from encoder.

        Sends MEAS:ENC:ANGL? <id> and parses the bare float response.

        Args:
            encoder_id: 'A' or 'B'

        Returns:
            Angle in degrees (0-360) or None if error
        """
        if not self.connected:
            print("[ArduinoEncoder] Not connected")
            return None

        self._send_command(f"MEAS:ENC:ANGL? {encoder_id}")

        response = self._read_line(timeout=1.0)
        if not response:
            print("[ArduinoEncoder] No response")
            return None

        try:
            return float(response)
        except ValueError:
            print(f"[ArduinoEncoder] Unexpected response: {response}")
            return None

    def set_zero(self, encoder_id: str = "A") -> bool:
        """
        Set current position as zero for encoder.

        Sends CONF:ENC:ZERO <id> (no response expected).

        Args:
            encoder_id: 'A' or 'B'

        Returns:
            True if command sent successfully
        """
        if not self.connected:
            return False

        self._send_command(f"CONF:ENC:ZERO {encoder_id}")
        print(f"[ArduinoEncoder] Zero set for encoder {encoder_id}")
        return True

    def clear_error_flag(self, encoder_id: str = "A") -> bool:
        """
        Clear hardware Error Flag on encoder (CONF:ENC:ERR <id>).

        The AS5048A EF is self-latching. Call this if the sensor keeps
        returning NAN despite no ongoing hardware problem.

        Args:
            encoder_id: 'A', 'B', or 'BOTH'

        Returns:
            True if command sent successfully
        """
        if not self.connected:
            return False

        self._send_command(f"CONF:ENC:ERR {encoder_id}")
        print(f"[ArduinoEncoder] Error flag cleared for encoder {encoder_id}")
        return True

    def read_both_angles(self) -> Optional[Tuple[float, float]]:
        """
        Read angles from both encoders.

        Sends MEAS:ENC:ANGL? BOTH and parses the comma-separated response.

        Returns:
            Tuple (angle_a, angle_b) or None if error
        """
        if not self.connected:
            return None

        self._send_command("MEAS:ENC:ANGL? BOTH")
        response = self._read_line(timeout=1.0)

        if not response:
            return None

        try:
            parts = response.split(",")
            if len(parts) >= 2:
                return (float(parts[0]), float(parts[1]))
        except ValueError:
            print(f"[ArduinoEncoder] Unexpected response: {response}")
        return None


# Simple test
if __name__ == "__main__":
    from config import ARDUINO_PORT, ARDUINO_BAUDRATE

    encoder = ArduinoEncoder(ARDUINO_PORT, ARDUINO_BAUDRATE)

    if encoder.connect():
        print("\nReading 5 samples...")
        for i in range(5):
            sample = encoder.read_angle("A")
            if sample is not None:
                print(f"  Sample {i + 1}: {sample:.2f}°")
            time.sleep(0.5)

        encoder.disconnect()
    else:
        print("Failed to connect. Check port in config.py")
