"""
Device Manager for Goniometer System.

Manages connections to encoder and photodetector hardware,
providing a centralized interface for device lifecycle management.
Implements the adapter pattern to abstract hardware details from UI.

Architecture:
    - Pure Python, no PySide6 dependencies
    - Uses dependency injection for adapters
    - Thread-safe connection handling
    - Automatic reconnection support
"""

from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from serial.tools import list_ports

from polarisation_ui.core.models import DualEncoderReading
from polarisation_ui.infrastructure.logging import Debug

try:
    from polarisation_ui.infrastructure.mocks.mock_port_registry import (
        discover_mock_ports as _discover_mock_ports,
    )

    _MOCK_REGISTRY_AVAILABLE = True
except ImportError:
    _MOCK_REGISTRY_AVAILABLE = False

from polarisation_ui.infrastructure.devices.dual_encoder import (
    DesiredState,
    DualEncoderArduino,
    EncoderID,
)


class DeviceState(Enum):
    """Device connection state."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


@dataclass
class DeviceStatus:
    """Status information for a device."""

    state: DeviceState
    port: Optional[str] = None
    baudrate: Optional[int] = None
    error_message: Optional[str] = None

    def is_ready(self) -> bool:
        """Check if device is ready for operations."""
        return self.state == DeviceState.CONNECTED


class GoniometerDeviceManager:
    """
    Manages all hardware devices for goniometer system.

    Responsibilities:
        - Initialize and connect to encoder Arduino
        - Manage device lifecycle (connect/disconnect)
        - Provide status information
        - Handle connection errors gracefully
        - Support mock devices for testing
    """

    def __init__(self, use_mock: bool = False):
        """
        Initialize device manager.

        Args:
            use_mock: If True, use mock devices for testing.
        """
        self.use_mock = use_mock

        # Device instances
        self._encoder_device: Optional[DualEncoderArduino] = None

        # Status tracking
        self._encoder_status = DeviceStatus(state=DeviceState.DISCONNECTED)

        # Last-known CONF:ADC:* / CONF:PDTIA:* state — reapplied after reconnect
        self._desired_state: DesiredState = DesiredState()

        Debug.info(f"Device manager initialized (mock={use_mock})")

    # ==================== Port Discovery ====================

    @staticmethod
    def list_available_ports() -> list[str]:
        """Return serial ports plus mock PTY ports registered in temp files."""
        ports = {p.device for p in list_ports.comports()}
        if _MOCK_REGISTRY_AVAILABLE:
            ports.update(_discover_mock_ports())
        return sorted(ports)

    # ==================== Connection Management ====================

    def connect_encoders(
        self, port: str, baudrate: int = 115200, timeout: float = 1.0
    ) -> bool:
        """
        Connect to encoder Arduino.

        Args:
            port: Serial port (e.g., '/dev/ttyUSB0', 'COM3')
            baudrate: Serial communication speed
            timeout: Read timeout in seconds

        Returns:
            bool: True if connection successful
        """
        try:
            self._encoder_status.state = DeviceState.CONNECTING

            Debug.info(f"Connecting to encoder Arduino at {port}...")

            # Initialize device
            self._encoder_device = DualEncoderArduino(
                port=port, baudrate=baudrate, timeout=timeout, encoder_b_present=True
            )

            # Attempt connection
            success = self._encoder_device.connect()

            if success:
                self._encoder_status = DeviceStatus(
                    state=DeviceState.CONNECTED, port=port, baudrate=baudrate
                )
                Debug.info("Encoder Arduino connected successfully")
                return True

            self._encoder_status = DeviceStatus(
                state=DeviceState.ERROR, error_message="Connection failed"
            )
            Debug.error("Failed to connect to encoder Arduino")
            return False

        except Exception as e:
            error_msg = f"Exception during encoder connection: {e}"
            Debug.error(error_msg)
            self._encoder_status = DeviceStatus(
                state=DeviceState.ERROR, error_message=str(e)
            )
            return False

    def reconnect_encoders(self) -> bool:
        """
        Re-establish the encoder connection using the last known port/baudrate.

        Cleanly disconnects first, then calls connect_encoders() with the
        stored parameters.  On success, reapplies the saved DesiredState so
        the Arduino's CONF:ADC:* / CONF:PDTIA:* config is restored.

        Returns False if no prior connection info exists.
        """
        port = self._encoder_status.port
        baudrate = self._encoder_status.baudrate or 115200
        if not port:
            Debug.warning("Cannot reconnect: no previous port stored")
            return False
        Debug.info(f"Reconnecting to {port} at {baudrate} baud...")
        self.disconnect_encoders()
        success = self.connect_encoders(port=port, baudrate=baudrate)
        if success and self._encoder_device is not None:
            self._encoder_device.reapply_desired_state(self._desired_state)
        return success

    def set_desired_state(self, state: DesiredState) -> None:
        """Update the desired-state snapshot used on reconnect."""
        self._desired_state = state

    def get_desired_state(self) -> DesiredState:
        """Get the last-known desired state for encoders."""
        return self._desired_state

    def get_firmware_version(self) -> str:
        """Return the firmware version reported by the connected device, or 'unknown'."""
        if self._encoder_device is None:
            return "unknown"
        return self._encoder_device.firmware_version

    def disconnect_encoders(self) -> None:
        """Disconnect from encoder Arduino."""
        if self._encoder_device is not None:
            try:
                self._encoder_device.disconnect()
                Debug.info("Encoder Arduino disconnected")
            except Exception as e:
                Debug.error(f"Error disconnecting encoder: {e}")
            finally:
                self._encoder_device = None
                self._encoder_status = DeviceStatus(state=DeviceState.DISCONNECTED)

    def disconnect_all(self) -> None:
        """Disconnect all devices."""
        Debug.info("Disconnecting all devices...")
        self.disconnect_encoders()

    # ==================== Status Queries ====================

    def is_encoder_connected(self) -> bool:
        """Check if encoder is connected."""
        return (
            self._encoder_device is not None
            and self._encoder_device.is_connected()
            and self._encoder_status.state == DeviceState.CONNECTED
        )

    def is_all_connected(self) -> bool:
        """Check if all devices are connected."""
        return self.is_encoder_connected()

    def get_encoder_status(self) -> DeviceStatus:
        """Get encoder connection status."""
        return self._encoder_status

    def get_connection_info(self) -> Dict[str, Any]:
        """
        Get detailed connection information for all devices.

        Returns:
            dict: Connection status for each device
        """
        return {
            "encoders": {
                "connected": self.is_encoder_connected(),
                "port": self._encoder_status.port,
                "baudrate": self._encoder_status.baudrate,
                "state": self._encoder_status.state.value,
                "error": self._encoder_status.error_message,
            },
            "all_ready": self.is_all_connected(),
        }

    # ==================== Device Access ====================

    def get_encoder_device(self) -> Optional[DualEncoderArduino]:
        """
        Get encoder device instance.

        Returns:
            DualEncoderArduino or None if not connected
        """
        if not self.is_encoder_connected():
            Debug.warning("Attempted to access encoder device while not connected")
            return None
        return self._encoder_device

    # ==================== Data Reading ====================

    def read_angles(self) -> Optional[DualEncoderReading]:
        """
        Read current angles from both encoders.

        Returns:
            DualEncoderReading(sample_angle, detector_angle) or None on error.
        """
        if not self.is_encoder_connected():
            return None

        try:
            device = self.get_encoder_device()
            if device is None:
                return None

            reading = device.read_angle("BOTH")
            if reading is None:
                return None

            return DualEncoderReading(
                sample_angle=reading.angle_a,
                detector_angle=reading.angle_b,
            )

        except Exception as e:
            Debug.error(f"Error reading angles: {e}")
            return None

    def read_sample_angle(self) -> Optional[float]:
        """Read sample stage angle (Encoder A)."""
        if not self.is_encoder_connected():
            return None

        try:
            device = self.get_encoder_device()
            if device is None:
                return None
            v = device.read_angle(EncoderID.A)
            return v.angle_deg if v is not None else None
        except Exception as e:
            Debug.error(f"Error reading sample angle: {e}")
            return None

    def read_detector_angle(self) -> Optional[float]:
        """Read detector stage angle (Encoder B)."""
        if not self.is_encoder_connected():
            return None

        try:
            device = self.get_encoder_device()
            if device is None:
                return None
            v = device.read_angle(EncoderID.B)
            return v.angle_deg if v is not None else None
        except Exception as e:
            Debug.error(f"Error reading detector angle: {e}")
            return None

    def read_adc_voltage(self) -> Optional[float]:
        """Read photodiode voltage via MEAS:ADC:VOLT? (requires firmware >= 2.0.0)."""
        device = self.get_encoder_device()
        if device is None:
            return None
        try:
            return device.adc.read_voltage()
        except Exception as e:
            Debug.error(f"Error reading ADC voltage: {e}")
            return None

    def read_adc_temperature(self) -> Optional[float]:
        """Read internal ADC temperature via MEAS:ADC:TEMP?."""
        device = self.get_encoder_device()
        if device is None:
            return None
        try:
            return device.adc.read_temperature()
        except Exception as e:
            Debug.error(f"Error reading ADC temperature: {e}")
            return None

    def read_diagnostics_both(
        self,
    ) -> Optional[tuple[Optional[dict], Optional[dict]]]:
        """
        Read SYST:DIAG? for both encoders.

        Returns:
            (diag_a, diag_b) where each entry is a dict with keys
            compHigh, compLow, cof, ocf, agc — or None if that encoder
            did not respond.  Returns None when not connected.
        """
        device = self.get_encoder_device()
        if device is None:
            return None
        return device.query_diagnostics("BOTH")

    # ==================== Device Control ====================

    def zero_encoder(self, target: EncoderID | str) -> bool:
        """Set current encoder position as zero. target: EncoderID.A, EncoderID.B, or 'BOTH'."""
        if not self.is_encoder_connected():
            return False
        try:
            device = self.get_encoder_device()
            if device is None:
                return False
            device.zero(target)
            label = target if isinstance(target, str) else target.value
            Debug.info(f"Encoder {label} zeroed")
            return True
        except Exception as e:
            Debug.error(f"Error zeroing encoder {target}: {e}")
            return False

    def zero_sample_encoder(self) -> bool:
        """Thin alias: zero sample stage encoder (A)."""
        return self.zero_encoder(EncoderID.A)

    def zero_detector_encoder(self) -> bool:
        """Thin alias: zero detector stage encoder (B)."""
        return self.zero_encoder(EncoderID.B)

    def set_pdtia_gain(self, stage: int) -> bool:
        """Set PDTIA discrete gain stage (1–4) via CONF:PDTIA:GAIN."""
        device = self.get_encoder_device()
        if device is None:
            return False
        try:
            ok = device.adc.set_pdtia_gain(stage)
            if ok:
                self._desired_state.pdtia_gain = stage
                Debug.info(f"PDTIA gain set to stage {stage}")
            return ok
        except Exception as e:
            Debug.error(f"Error setting PDTIA gain: {e}")
            return False

    def zero_both_encoders(self) -> bool:
        """Thin alias: zero both encoder stages."""
        return self.zero_encoder("BOTH")
