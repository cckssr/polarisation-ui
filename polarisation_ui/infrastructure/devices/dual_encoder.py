"""
Dual AS5048A Encoder Interface via Serial Communication (SCPI Protocol).

This module provides a high-level interface for communicating with an Arduino
that controls two AS5048A magnetic encoders. It abstracts the SCPI serial
protocol and provides convenient methods for reading encoder values and
setting zero positions.

The interface communicates with the Arduino via SCPI commands defined in main.cpp:
    - MEAS:ANGL? A/B/BOTH   Read angle(s) in degrees
    - MEAS:MAGN? A/B/BOTH   Read raw magnitude(s)
    - INIT ON,A/B/BOTH      Start continuous angle streaming
    - INIT ON,MAG           Start continuous magnitude streaming
    - ABOR                  Stop continuous streaming
    - CONF:ZERO A/B/BOTH    Set zero position
    - SENS:INT <ms>         Set poll interval
    - SYST:DIAG? A/B        Read encoder diagnostics
    - *IDN?                 Identification
    - *RST                  Reset
    - SYST:ERR?             Query error queue

Architecture:
    - Pure Python, no PySide6 dependencies
    - Built on SerialDevice for low-level communication
    - Handles protocol parsing and error recovery
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

import serial

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
    High-level interface for dual AS5048A encoders via Arduino (SCPI protocol).

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
        except serial.SerialException as e:
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

        Returns:
            float: Angle in degrees, or None on error.
        """
        value = self.read_single(EncoderID.A)
        return value.angle_deg if value else None

    def read_encoder_b(self) -> Optional[float]:
        """
        Read current angle from encoder B.

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

        Sends 'MEAS:ANGL? A' or 'MEAS:ANGL? B' command to Arduino.

        Args:
            encoder_id (EncoderID): Which encoder to read.

        Returns:
            EncoderValue: Parsed value with angle_deg, or None on error.
        """
        if encoder_id == EncoderID.B and not self.encoder_b_present:
            Debug.warning("Encoder B not available")
            return None

        command = f"MEAS:ANGL? {encoder_id.value}"
        if not self._device.send_command(command, add_newline=True):
            Debug.error(f"Failed to send command: {command}")
            return None

        response = self._device.read_value(timeout=self.timeout, return_type="str")
        if not response:
            Debug.error(f"No response from encoder {encoder_id.value}")
            self._query_and_log_error()
            return None

        return self._parse_single_response(response, encoder_id)

    def read_both(self) -> Optional[DualEncoderValue]:
        """
        Read values from both encoders simultaneously.

        Sends 'MEAS:ANGL? BOTH' command to Arduino.

        Returns:
            DualEncoderValue: Both angles, or None on error.
        """
        if not self.encoder_b_present:
            Debug.warning("Encoder B not present")
            return None

        command = "MEAS:ANGL? BOTH"
        if not self._device.send_command(command, add_newline=True):
            Debug.error(f"Failed to send command: {command}")
            return None

        response = self._device.read_value(timeout=self.timeout, return_type="str")
        if not response:
            Debug.error("No response for MEAS:ANGL? BOTH command")
            self._query_and_log_error()
            return None

        return self._parse_both_response(response)

    def start_continuous_a(self) -> bool:
        """Start continuous angle streaming for encoder A."""
        return self._send_command_no_response("INIT ON,A")

    def stop_continuous_a(self) -> bool:
        """Stop continuous streaming."""
        return self._send_command_no_response("ABOR")

    def start_continuous_b(self) -> bool:
        """Start continuous angle streaming for encoder B."""
        if not self.encoder_b_present:
            Debug.warning("Encoder B not present")
            return False
        return self._send_command_no_response("INIT ON,B")

    def stop_continuous_b(self) -> bool:
        """Stop continuous streaming."""
        return self._send_command_no_response("ABOR")

    def start_continuous_both(self) -> bool:
        """Start continuous angle streaming for both encoders."""
        if not self.encoder_b_present:
            Debug.warning("Encoder B not present")
            return False
        return self._send_command_no_response("INIT ON,BOTH")

    def stop_continuous_both(self) -> bool:
        """Stop continuous streaming."""
        return self._send_command_no_response("ABOR")

    def abort(self) -> bool:
        """Stop any active continuous streaming."""
        return self._send_command_no_response("ABOR")

    def reset_zero_a(self) -> bool:
        """Set zero position for encoder A."""
        return self._send_command_no_response("CONF:ZERO A")

    def reset_zero_b(self) -> bool:
        """Set zero position for encoder B."""
        if not self.encoder_b_present:
            Debug.warning("Encoder B not present")
            return False
        return self._send_command_no_response("CONF:ZERO B")

    def reset_zero_both(self) -> bool:
        """Set zero position for both encoders."""
        if not self.encoder_b_present:
            Debug.warning("Encoder B not present")
            return False
        return self._send_command_no_response("CONF:ZERO BOTH")

    def set_poll_interval(self, interval_ms: int) -> bool:
        """
        Set continuous polling interval.

        Args:
            interval_ms (int): Poll interval in milliseconds (1-9999).

        Returns:
            bool: True if command sent successfully, False otherwise.
        """
        if interval_ms < 1 or interval_ms > 9999:
            Debug.error(f"Invalid poll interval: {interval_ms} ms")
            return False

        if self._send_command_no_response(f"SENS:INT {interval_ms}"):
            self._config["poll_interval"] = interval_ms
            Debug.info(f"Poll interval set to {interval_ms} ms")
            return True
        return False

    def get_diagnostics_a(self) -> Optional[Dict[str, bool]]:
        """Read diagnostics from encoder A."""
        return self.get_diagnostics(EncoderID.A)

    def get_diagnostics_b(self) -> Optional[Dict[str, bool]]:
        """Read diagnostics from encoder B."""
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
            Dict with keys: compHigh, compLow, cof, ocf, agc.
            Returns None on error.
        """
        if encoder_id == EncoderID.B and not self.encoder_b_present:
            Debug.warning("Encoder B not present")
            return None

        command = f"SYST:DIAG? {encoder_id.value}"
        if not self._device.send_command(command, add_newline=True):
            Debug.error(f"Failed to send command: {command}")
            return None

        response = self._device.read_value(timeout=self.timeout, return_type="str")
        if not response:
            Debug.error("No response for diagnostics command")
            return None

        return self._parse_diagnostics_response(response, encoder_id)

    def query_error(self) -> Optional[str]:
        """
        Query next error from error queue (SYST:ERR?).

        Returns:
            Error string (e.g. '0,"No error"') or None on comm failure.
        """
        command = "SYST:ERR?"
        if not self._device.send_command(command, add_newline=True):
            return None
        return self._device.read_value(timeout=self.timeout, return_type="str")

    def identify(self) -> Optional[str]:
        """
        Query device identification (*IDN?).

        Returns:
            Identification string or None on error.
        """
        if not self._device.send_command("*IDN?", add_newline=True):
            return None
        return self._device.read_value(timeout=self.timeout, return_type="str")

    def reset(self) -> bool:
        """Reset device to defaults (*RST)."""
        return self._send_command_no_response("*RST")

    def flush_buffer(self) -> bool:
        """Clear input buffer (removes stale data)."""
        return self._device.flush_input_buffer()

    def _query_and_log_error(self) -> None:
        """
        Query the device error queue and log the result.

        Called after a read timeout so the caller knows whether the Arduino
        reported an error (e.g. unknown command, hardware fault) or simply
        had no data to send.  Flushes stale bytes first so the SYST:ERR?
        response is not contaminated by the previous timed-out command.
        """
        self._device.flush_input_buffer()
        error = self.query_error()
        if error is None:
            Debug.error("SYST:ERR? query failed (no response)")
        elif error.startswith("0,"):
            Debug.debug(f"SYST:ERR? → {error} (no device error)")
        else:
            Debug.error(f"SYST:ERR? → {error}")

    def _send_command_no_response(self, command: str) -> bool:
        """
        Send a SCPI command that does not produce a response.

        Args:
            command (str): SCPI command string.

        Returns:
            bool: True if sent successfully, False otherwise.
        """
        if not self._device.send_command(command, add_newline=True):
            Debug.error(f"Failed to send command: {command}")
            return False
        Debug.debug(f"Command sent: {command}")
        return True

    def _parse_single_response(
        self, response: str, encoder_id: EncoderID
    ) -> Optional[EncoderValue]:
        """
        Parse single encoder query response.

        MEAS:ANGL? A  →  '45.23'

        Args:
            response (str): Response string from Arduino.
            encoder_id (EncoderID): Expected encoder ID.

        Returns:
            EncoderValue or None if parsing failed.
        """
        try:
            angle_deg = float(response.strip())
            Debug.debug(f"Parsed encoder {encoder_id.value}: {angle_deg}°")
            return EncoderValue(encoder_id, angle_deg)
        except ValueError as e:
            Debug.error(f"Failed to parse encoder response: '{response}' ({e})")
            return None

    def _parse_both_response(self, response: str) -> Optional[DualEncoderValue]:
        """
        Parse dual encoder query response.

        MEAS:ANGL? BOTH  →  '45.23,12.67'

        Args:
            response (str): Response string from Arduino.

        Returns:
            DualEncoderValue or None if parsing failed.
        """
        try:
            parts = response.strip().split(",")
            if len(parts) < 2:
                Debug.error(f"Invalid dual encoder response: '{response}'")
                return None
            angle_a = float(parts[0])
            angle_b = float(parts[1])
            Debug.debug(f"Parsed both encoders: A={angle_a}°, B={angle_b}°")
            return DualEncoderValue(angle_a, angle_b)
        except (IndexError, ValueError) as e:
            Debug.error(f"Failed to parse dual encoder response: '{response}' ({e})")
            return None

    def _parse_diagnostics_response(
        self, response: str, encoder_id: EncoderID
    ) -> Optional[Dict[str, bool]]:
        """
        Parse diagnostics query response.

        SYST:DIAG? A  →  '0,0,0,1,200'  (compHigh,compLow,cof,ocf,agc)

        Args:
            response (str): Response string from Arduino.
            encoder_id (EncoderID): Expected encoder ID.

        Returns:
            Dict with diagnostic flags or None if parsing failed.
        """
        try:
            parts = response.strip().split(",")
            if len(parts) < 5:
                Debug.error(f"Invalid diagnostics response: '{response}'")
                return None

            keys = ["compHigh", "compLow", "cof", "ocf", "agc"]
            diag_dict = {key: bool(int(val.strip())) for key, val in zip(keys, parts)}
            Debug.debug(f"Parsed diagnostics for {encoder_id.value}: {diag_dict}")
            return diag_dict

        except (IndexError, ValueError) as e:
            Debug.error(f"Failed to parse diagnostics response: '{response}' ({e})")
            return None
