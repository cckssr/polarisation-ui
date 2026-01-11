"""
Dual AS5048A Encoder Interface via Serial Communication.

This module provides a high-level interface for communicating with an Arduino
that controls two AS5048A magnetic encoders. It abstracts the serial protocol
and provides convenient methods for reading encoder values and setting zero positions.

The interface communicates with the Arduino via serial commands defined in main.cpp:
    - C_A1/C_A0: Start/stop continuous reading of encoder A
    - C_B1/C_B0: Start/stop continuous reading of encoder B
    - C_BOTH1/C_BOTH0: Start/stop continuous reading of both encoders
    - R_A/R_B: Single read from each encoder
    - R_BOTH: Single read of both encoders
    - Z_A/Z_B/Z_BOTH: Set zero position for encoder(s)

Architecture:
    - Pure Python, no PySide6 dependencies
    - Built on SerialDevice for low-level communication
    - Handles protocol parsing and error recovery
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

from polarisation_ui.infrastructure.serial_device import SerialDevice
from polarisation_ui.infrastructure.logging import Debug


class EncoderID(Enum):
    """Encoder identifier."""

    A = "A"
    B = "B"


@dataclass
class EncoderValue:
    """Single encoder reading."""

    encoder_id: EncoderID
    angle_deg: float
    angle_raw: Optional[int] = None

    def __repr__(self) -> str:
        """String representation."""
        raw_str = f", raw={self.angle_raw}" if self.angle_raw is not None else ""
        return f"EncoderValue({self.encoder_id.value}, {self.angle_deg}°{raw_str})"


@dataclass
class DualEncoderValue:
    """Reading from both encoders."""

    angle_a: float
    angle_b: float

    def __repr__(self) -> str:
        """String representation."""
        return f"DualEncoderValue(A={self.angle_a}°, B={self.angle_b}°)"


class DualEncoderArduino:
    """
    High-level interface for dual AS5048A encoders via Arduino.

    Manages serial communication with Arduino running the AS5048A control firmware.
    Provides methods to read encoder positions, set zero points, and manage
    continuous polling modes.

    Attributes:
        DEFAULT_TIMEOUT (float): Default timeout for serial read operations.
        DEFAULT_POLL_INTERVAL (int): Default continuous polling interval in ms.
    """

    DEFAULT_TIMEOUT = 1.0
    DEFAULT_POLL_INTERVAL = 50

    def __init__(
        self,
        port: str,
        baudrate: int = 115200,
        timeout: float = DEFAULT_TIMEOUT,
        encoder_b_present: bool = True,
    ):
        """
        Initialize dual encoder interface.

        Args:
            port (str): Serial port (e.g., '/dev/ttyUSB0', 'COM3').
            baudrate (int): Serial communication speed. Default 115200.
            timeout (float): Timeout for serial read operations. Default 1.0s.
            encoder_b_present (bool): Whether second encoder is present. Default True.
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.encoder_b_present = encoder_b_present

        self._device = SerialDevice(port, baudrate, timeout)
        self._config: Dict[str, Any] = {
            "encoder_b_present": encoder_b_present,
            "poll_interval": self.DEFAULT_POLL_INTERVAL,
        }

    def connect(self) -> bool:
        """
        Establish connection to Arduino.

        Returns:
            bool: True if connected successfully, False otherwise.
        """
        try:
            self._device.reconnect()
            Debug.info(f"DualEncoderArduino connected to {self.port}")
            return self._device.connected
        except Exception as e:
            Debug.error(f"Failed to connect to encoder Arduino: {e}")
            return False

    def disconnect(self) -> None:
        """Close serial connection."""
        self._device.close()
        Debug.info(f"DualEncoderArduino disconnected from {self.port}")

    def is_connected(self) -> bool:
        """
        Check if serial connection is active.

        Returns:
            bool: True if connected, False otherwise.
        """
        return self._device.connected and self._device.serial is not None

    def read_encoder_a(self) -> Optional[float]:
        """
        Read current angle from encoder A.

        Sends single read command to Arduino and parses response.

        Returns:
            float: Angle in degrees, or None on error.
        """
        value = self.read_single(EncoderID.A)
        return value.angle_deg if value else None

    def read_encoder_b(self) -> Optional[float]:
        """
        Read current angle from encoder B.

        Requires encoder B to be present.

        Returns:
            float: Angle in degrees, or None on error.
        """
        if not self.encoder_b_present:
            Debug.warning("Encoder B not present")
            return None
        value = self.read_single(EncoderID.B)
        return value.angle_deg if value else None

    def read_single(self, encoder_id: EncoderID) -> Optional[EncoderValue]:
        """
        Read single value from one encoder.

        Sends 'R_A' or 'R_B' command to Arduino.

        Args:
            encoder_id (EncoderID): Which encoder to read.

        Returns:
            EncoderValue: Parsed value with angle_deg and angle_raw, or None on error.
        """
        if encoder_id == EncoderID.B and not self.encoder_b_present:
            Debug.warning("Encoder B not available")
            return None

        command = f"R_{encoder_id.value}"
        if not self._device.send_command(command, add_newline=True):
            Debug.error(f"Failed to send command: {command}")
            return None

        response = self._device.read_value(timeout=self.timeout, return_type="str")
        if not response:
            Debug.error(f"No response from encoder {encoder_id.value}")
            return None

        return self._parse_single_response(response, encoder_id)

    def read_both(self) -> Optional[DualEncoderValue]:
        """
        Read values from both encoders simultaneously.

        Sends 'R_BOTH' command to Arduino. More efficient than reading separately.

        Returns:
            DualEncoderValue: Both angles, or None on error.
        """
        if not self.encoder_b_present:
            Debug.warning("Encoder B not present")
            return None

        command = "R_BOTH"
        if not self._device.send_command(command, add_newline=True):
            Debug.error(f"Failed to send command: {command}")
            return None

        response = self._device.read_value(timeout=self.timeout, return_type="str")
        if not response:
            Debug.error("No response for R_BOTH command")
            return None

        return self._parse_both_response(response)

    def start_continuous_a(self) -> bool:
        """
        Start continuous polling of encoder A.

        Arduino will send readings at configured poll interval.

        Returns:
            bool: True if command accepted, False otherwise.
        """
        return self._send_mode_command("C_A1")

    def stop_continuous_a(self) -> bool:
        """Stop continuous polling of encoder A."""
        return self._send_mode_command("C_A0")

    def start_continuous_b(self) -> bool:
        """
        Start continuous polling of encoder B.

        Requires encoder B to be present.

        Returns:
            bool: True if command accepted, False otherwise.
        """
        if not self.encoder_b_present:
            Debug.warning("Encoder B not present")
            return False
        return self._send_mode_command("C_B1")

    def stop_continuous_b(self) -> bool:
        """Stop continuous polling of encoder B."""
        return self._send_mode_command("C_B0")

    def start_continuous_both(self) -> bool:
        """
        Start continuous polling of both encoders.

        Requires encoder B to be present.

        Returns:
            bool: True if command accepted, False otherwise.
        """
        if not self.encoder_b_present:
            Debug.warning("Encoder B not present")
            return False
        return self._send_mode_command("C_BOTH1")

    def stop_continuous_both(self) -> bool:
        """Stop continuous polling of both encoders."""
        return self._send_mode_command("C_BOTH0")

    def reset_zero_a(self) -> bool:
        """
        Set zero position for encoder A.

        Current position becomes new 0°.

        Returns:
            bool: True if successful, False otherwise.
        """
        return self._send_zero_command("Z_A")

    def reset_zero_b(self) -> bool:
        """
        Set zero position for encoder B.

        Requires encoder B to be present.

        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.encoder_b_present:
            Debug.warning("Encoder B not present")
            return False
        return self._send_zero_command("Z_B")

    def reset_zero_both(self) -> bool:
        """
        Set zero position for both encoders.

        Current positions become new 0°.

        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.encoder_b_present:
            Debug.warning("Encoder B not present")
            return False
        return self._send_zero_command("Z_BOTH")

    def set_poll_interval(self, interval_ms: int) -> bool:
        """
        Set continuous polling interval.

        Args:
            interval_ms (int): Poll interval in milliseconds (1-10000).

        Returns:
            bool: True if successful, False otherwise.
        """
        if not (1 <= interval_ms <= 10000):
            Debug.error(f"Invalid poll interval: {interval_ms} ms")
            return False

        command = f"P:{interval_ms}"
        if not self._device.send_command(command, add_newline=True):
            Debug.error(f"Failed to set poll interval: {command}")
            return False

        response = self._device.read_value(timeout=self.timeout, return_type="str")
        if response and "OK" in response:
            self._config["poll_interval"] = interval_ms
            Debug.info(f"Poll interval set to {interval_ms} ms")
            return True

        Debug.error(f"Failed to set poll interval: {response}")
        return False

    def get_diagnostics_a(self) -> Optional[Dict[str, bool]]:
        """
        Read diagnostics from encoder A.

        Returns diagnostic flags from the AS5048A chip.

        Returns:
            Dict with diagnostic flags, or None on error.
        """
        return self.get_diagnostics(EncoderID.A)

    def get_diagnostics_b(self) -> Optional[Dict[str, bool]]:
        """
        Read diagnostics from encoder B.

        Returns diagnostic flags from the AS5048A chip.

        Returns:
            Dict with diagnostic flags, or None on error.
        """
        if not self.encoder_b_present:
            Debug.warning("Encoder B not present")
            return None
        return self.get_diagnostics(EncoderID.B)

    def get_diagnostics(self, encoder_id: EncoderID) -> Optional[Dict[str, bool]]:
        """
        Read diagnostics from one encoder.

        Args:
            encoder_id (EncoderID): Which encoder to read diagnostics from.

        Returns:
            Dict with keys: compHigh, compLow, cof, ocf, agc (all bool).
            Returns None on error.
        """
        if encoder_id == EncoderID.B and not self.encoder_b_present:
            Debug.warning("Encoder B not present")
            return None

        command = f"DIAG_{encoder_id.value}"
        if not self._device.send_command(command, add_newline=True):
            Debug.error(f"Failed to send command: {command}")
            return None

        response = self._device.read_value(timeout=self.timeout, return_type="str")
        if not response:
            Debug.error(f"No response for diagnostics command")
            return None

        return self._parse_diagnostics_response(response, encoder_id)

    def flush_buffer(self) -> bool:
        """Clear input buffer (removes stale data)."""
        return self._device.flush_input_buffer()

    def _send_mode_command(self, command: str) -> bool:
        """
        Send mode control command and verify response.

        Args:
            command (str): Mode command (C_A1, C_B1, etc.)

        Returns:
            bool: True if 'OK' received, False otherwise.
        """
        if not self._device.send_command(command, add_newline=True):
            return False

        response = self._device.read_value(timeout=self.timeout, return_type="str")
        success = response is not None and "OK" in response
        if success:
            Debug.debug(f"Mode command accepted: {command}")
        else:
            Debug.error(f"Mode command failed: {command} -> {response}")
        return success

    def _send_zero_command(self, command: str) -> bool:
        """
        Send zero-set command and verify response.

        Args:
            command (str): Zero command (Z_A, Z_B, Z_BOTH)

        Returns:
            bool: True if 'OK' received, False otherwise.
        """
        if not self._device.send_command(command, add_newline=True):
            return False

        response = self._device.read_value(timeout=self.timeout, return_type="str")
        success = response is not None and "OK" in response
        if success:
            Debug.debug(f"Zero command accepted: {command}")
        else:
            Debug.error(f"Zero command failed: {command} -> {response}")
        return success

    def _parse_single_response(
        self, response: str, encoder_id: EncoderID
    ) -> Optional[EncoderValue]:
        """
        Parse single encoder response: 'DATA,A,angle_deg,angle_raw'

        Args:
            response (str): Response string from Arduino.
            encoder_id (EncoderID): Expected encoder ID.

        Returns:
            EncoderValue or None if parsing failed.
        """
        try:
            parts = response.split(",")
            if len(parts) < 4 or parts[0] != "DATA":
                Debug.error(f"Invalid response format: {response}")
                return None

            resp_id = parts[1].strip()
            if resp_id != encoder_id.value:
                Debug.warning(
                    f"Encoder ID mismatch: expected {encoder_id.value}, got {resp_id}"
                )

            angle_deg = float(parts[2])
            angle_raw = int(float(parts[3]))

            Debug.debug(
                f"Parsed encoder {encoder_id.value}: {angle_deg}° (raw: {angle_raw})"
            )
            return EncoderValue(encoder_id, angle_deg, angle_raw)

        except (IndexError, ValueError) as e:
            Debug.error(f"Failed to parse encoder response: {response} ({e})")
            return None

    def _parse_both_response(self, response: str) -> Optional[DualEncoderValue]:
        """
        Parse dual encoder response: 'DATA_BOTH,angle_a,angle_b'

        Args:
            response (str): Response string from Arduino.

        Returns:
            DualEncoderValue or None if parsing failed.
        """
        try:
            parts = response.split(",")
            if len(parts) < 3 or parts[0] != "DATA_BOTH":
                Debug.error(f"Invalid response format: {response}")
                return None

            angle_a = float(parts[1])
            angle_b = float(parts[2])

            Debug.debug(f"Parsed both encoders: A={angle_a}°, B={angle_b}°")
            return DualEncoderValue(angle_a, angle_b)

        except (IndexError, ValueError) as e:
            Debug.error(f"Failed to parse dual encoder response: {response} ({e})")
            return None

    def _parse_diagnostics_response(
        self, response: str, encoder_id: EncoderID
    ) -> Optional[Dict[str, bool]]:
        """
        Parse diagnostics response: 'DIAG_A,compHigh:0,compLow:0,cof:0,ocf:0,agc:200'

        Args:
            response (str): Response string from Arduino.
            encoder_id (EncoderID): Expected encoder ID.

        Returns:
            Dict with diagnostic flags or None if parsing failed.
        """
        try:
            parts = response.split(",")
            if len(parts) < 6 or not parts[0].startswith("DIAG_"):
                Debug.error(f"Invalid diagnostics format: {response}")
                return None

            diag_dict = {}
            for part in parts[1:]:
                if ":" in part:
                    key, value = part.split(":")
                    # Convert to bool (0=False, anything else=True)
                    diag_dict[key.strip()] = bool(int(value.strip()))

            Debug.debug(f"Parsed diagnostics for {encoder_id.value}: {diag_dict}")
            return diag_dict

        except (IndexError, ValueError) as e:
            Debug.error(f"Failed to parse diagnostics response: {response} ({e})")
            return None
