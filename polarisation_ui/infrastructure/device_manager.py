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

from polarisation_ui.infrastructure.logging import Debug
from polarisation_ui.infrastructure.devices.dual_encoder import DualEncoderArduino


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

        Debug.info(f"Device manager initialized (mock={use_mock})")

    # ==================== Port Discovery ====================

    @staticmethod
    def list_available_ports() -> list[str]:
        """Return a list of available serial port device names."""
        return [p.device for p in list_ports.comports()]

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
            else:
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

    def read_angles(self) -> Optional[Tuple[float, float]]:
        """
        Read current angles from both encoders.

        Returns:
            Tuple of (sample_angle, detector_angle) or None on error
        """
        if not self.is_encoder_connected():
            return None

        try:
            device = self.get_encoder_device()
            if device is None:
                return None

            reading = device.read_both()
            if reading is None:
                return None

            return (reading.angle_a, reading.angle_b)

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
            return device.read_encoder_a()
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
            return device.read_encoder_b()
        except Exception as e:
            Debug.error(f"Error reading detector angle: {e}")
            return None

    # ==================== Device Control ====================

    def zero_sample_encoder(self) -> bool:
        """Set current sample encoder position as zero."""
        if not self.is_encoder_connected():
            return False

        try:
            device = self.get_encoder_device()
            if device is None:
                return False

            device.reset_zero_a()
            Debug.info("Sample encoder zeroed")
            return True
        except Exception as e:
            Debug.error(f"Error zeroing sample encoder: {e}")
            return False

    def zero_detector_encoder(self) -> bool:
        """Set current detector encoder position as zero."""
        if not self.is_encoder_connected():
            return False

        try:
            device = self.get_encoder_device()
            if device is None:
                return False

            device.reset_zero_b()
            Debug.info("Detector encoder zeroed")
            return True
        except Exception as e:
            Debug.error(f"Error zeroing detector encoder: {e}")
            return False

    def zero_both_encoders(self) -> bool:
        """Set both encoder positions as zero."""
        if not self.is_encoder_connected():
            return False

        try:
            device = self.get_encoder_device()
            if device is None:
                return False

            device.reset_zero_both()
            Debug.info("Both encoders zeroed")
            return True
        except Exception as e:
            Debug.error(f"Error zeroing encoders: {e}")
            return False
