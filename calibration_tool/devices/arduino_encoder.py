"""
Arduino Encoder Communication for AS5048A.

Communicates with the Arduino running the AS5048A firmware.
Sends commands like R_A to read angle and parses responses.
"""

import serial
import time
import re
from typing import Optional, Tuple


class ArduinoEncoder:
    """
    Interface to AS5048A encoder via Arduino.

    Protocol:
        Send: R_A (read angle encoder A)
        Receive: DATA,A,<angle_deg>

    Example:
        >>> encoder = ArduinoEncoder("/dev/cu.usbmodem1101")
        >>> encoder.connect()
        >>> angle = encoder.read_angle()
        >>> print(f"Angle: {angle:.2f}°")
        >>> encoder.disconnect()
    """

    # Regex patterns for parsing responses
    DATA_PATTERN = re.compile(r"DATA,([AB]),(-?\d+\.?\d*)")
    ERROR_PATTERN = re.compile(r"ERRO,([AB]),(.+)")
    OK_PATTERN = re.compile(r"OK:(.+)")

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
        Open serial connection to Arduino.

        Returns:
            True if connection successful, False otherwise
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
            # Wait for Arduino to reset after connection
            time.sleep(2.0)
            # Flush any startup messages
            self._serial.reset_input_buffer()
            self._serial.reset_output_buffer()
            self._connected = True
            print(f"[ArduinoEncoder] Connected to {self.port}")
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
        """Send command to Arduino."""
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

        Args:
            encoder_id: 'A' or 'B'

        Returns:
            Angle in degrees (0-360) or None if error
        """
        if not self.connected:
            print("[ArduinoEncoder] Not connected")
            return None

        # Send read command
        cmd = f"R_{encoder_id}"
        self._send_command(cmd)

        # Read response
        response = self._read_line(timeout=1.0)
        if not response:
            print("[ArduinoEncoder] No response")
            return None

        # Parse DATA response
        match = self.DATA_PATTERN.match(response)
        if match:
            enc_id = match.group(1)
            angle = float(match.group(2))
            return angle

        # Check for error
        error_match = self.ERROR_PATTERN.match(response)
        if error_match:
            print(f"[ArduinoEncoder] Error: {error_match.group(2)}")
            return None

        print(f"[ArduinoEncoder] Unexpected response: {response}")
        return None

    def set_zero(self, encoder_id: str = "A") -> bool:
        """
        Set current position as zero for encoder.

        Args:
            encoder_id: 'A' or 'B'

        Returns:
            True if successful
        """
        if not self.connected:
            return False

        cmd = f"Z_{encoder_id}"
        self._send_command(cmd)

        response = self._read_line(timeout=1.0)
        if response and response.startswith("OK:"):
            print(f"[ArduinoEncoder] Zero set for encoder {encoder_id}")
            return True
        return False

    def read_both_angles(self) -> Optional[Tuple[float, float]]:
        """
        Read angles from both encoders.

        Returns:
            Tuple (angle_a, angle_b) or None if error
        """
        if not self.connected:
            return None

        self._send_command("R_BOTH")
        response = self._read_line(timeout=1.0)

        if response and response.startswith("DATA_BOTH,"):
            parts = response.split(",")
            if len(parts) >= 3:
                try:
                    angle_a = float(parts[1])
                    angle_b = float(parts[2])
                    return (angle_a, angle_b)
                except ValueError:
                    pass
        return None


# Simple test
if __name__ == "__main__":
    from config import ARDUINO_PORT, ARDUINO_BAUDRATE

    encoder = ArduinoEncoder(ARDUINO_PORT, ARDUINO_BAUDRATE)

    if encoder.connect():
        print("\nReading 5 samples...")
        for i in range(5):
            angle = encoder.read_angle("A")
            if angle is not None:
                print(f"  Sample {i+1}: {angle:.2f}°")
            time.sleep(0.5)

        encoder.disconnect()
    else:
        print("Failed to connect. Check port in config.py")
