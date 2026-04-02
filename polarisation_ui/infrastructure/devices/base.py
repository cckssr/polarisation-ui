"""
Abstract interfaces for encoder devices.

This module defines the contract that all encoder implementations must follow.
It allows the rest of the system to work with encoders without knowing
their underlying transport mechanism (serial, USB, mock, etc.).
"""

from abc import ABC, abstractmethod
from typing import Optional


class EncoderAdapter(ABC):
    """
    Abstract base class for angle encoder devices.

    Encoders read the current position of rotation stages.
    Different implementations can communicate via serial, USB, network, etc.
    """

    @abstractmethod
    def read(self) -> float:
        """
        Read current angle position.

        Returns:
            float: Current angle in degrees.

        Raises:
            Exception: If read operation fails.
        """
        pass

    @abstractmethod
    def reset(self) -> None:
        """
        Reset encoder to zero position.

        Raises:
            Exception: If reset operation fails.
        """
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """
        Check if encoder device is connected and responding.

        Returns:
            bool: True if device is accessible, False otherwise.
        """
        pass

    @abstractmethod
    def connect(self) -> None:
        """
        Establish connection to encoder device.

        Raises:
            Exception: If connection fails.
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from encoder device."""
        pass

    @abstractmethod
    def get_raw_value(self) -> Optional[int]:
        """
        Get raw encoder count if available.

        Some encoders provide raw counter values that can be converted
        to angles. This is device-specific.

        Returns:
            int: Raw encoder count, or None if not available.
        """
        pass


class EncoderMock(EncoderAdapter):
    """
    Mock encoder for testing and development.

    Simulates an encoder that can be controlled programmatically.
    Useful for testing the UI without hardware.
    """

    def __init__(self, start_angle: float = 0.0, name: str = "MockEncoder"):
        """
        Initialize mock encoder.

        Args:
            start_angle: Starting angle in degrees.
            name: Friendly name for this encoder.
        """
        self.current_angle = start_angle
        self.name = name
        self._connected = True

    def read(self) -> float:
        """Read current simulated angle."""
        if not self._connected:
            raise RuntimeError(f"{self.name} is not connected")
        return self.current_angle

    def reset(self) -> None:
        """Reset to zero."""
        if not self._connected:
            raise RuntimeError(f"{self.name} is not connected")
        self.current_angle = 0.0

    def is_connected(self) -> bool:
        """Mock always reports connected status."""
        return self._connected

    def connect(self) -> None:
        """Set connected state."""
        self._connected = True

    def disconnect(self) -> None:
        """Set disconnected state."""
        self._connected = False

    def get_raw_value(self) -> Optional[int]:
        """Return mock raw value (360 counts = 360 degrees)."""
        return int(self.current_angle)

    def set_angle(self, angle: float) -> None:
        """
        Programmatically set angle (for testing).

        Args:
            angle: New angle in degrees.
        """
        self.current_angle = angle


class EncoderSerial(EncoderAdapter):
    """
    Serial-based encoder implementation.

    Communicates with hardware encoder via serial port.
    Implementation placeholder - adapt to your hardware protocol.
    """

    def __init__(self, port: str, baudrate: int = 9600, name: str = "SerialEncoder"):
        """
        Initialize serial encoder.

        Args:
            port: Serial port (e.g., '/dev/ttyUSB0' or 'COM3').
            baudrate: Serial communication speed.
            name: Friendly name for logging.
        """
        self.port = port
        self.baudrate = baudrate
        self.name = name
        self.serial = None  # Will be initialized on connect()
        self._connected = False

    def read(self) -> float:
        """
        Read angle from serial device.

        TODO: Implement actual serial protocol for your encoder.
        """
        if not self._connected:
            raise RuntimeError(f"{self.name} ({self.port}) is not connected")

        # Placeholder: actual implementation depends on hardware protocol
        # Example:
        # self.serial.write(b'READ\n')
        # response = self.serial.readline().decode().strip()
        # angle = float(response)
        # return angle

        raise NotImplementedError(
            "Serial encoder implementation must be adapted to your hardware protocol"
        )

    def reset(self) -> None:
        """
        Reset encoder to zero.

        TODO: Implement actual serial protocol for your encoder.
        """
        if not self._connected:
            raise RuntimeError(f"{self.name} ({self.port}) is not connected")

        # Placeholder: actual implementation depends on hardware protocol
        # Example:
        # self.serial.write(b'RESET\n')
        # self.serial.readline()  # Wait for confirmation

        raise NotImplementedError(
            "Serial encoder implementation must be adapted to your hardware protocol"
        )

    def is_connected(self) -> bool:
        """Check if serial port is open."""
        return self._connected and self.serial is not None

    def connect(self) -> None:
        """
        Open serial connection.

        TODO: Implement actual serial connection setup.
        """
        try:
            import serial

            self.serial = serial.Serial(
                port=self.port, baudrate=self.baudrate, timeout=1.0
            )
            self._connected = True
        except ImportError:
            raise RuntimeError(
                "pyserial not installed. Install with: pip install pyserial"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to connect to {self.port}: {e}")

    def disconnect(self) -> None:
        """Close serial connection."""
        if self.serial and self.serial.is_open:
            self.serial.close()
        self._connected = False

    def get_raw_value(self) -> Optional[int]:
        """
        Get raw encoder count.

        TODO: Implement based on your hardware protocol.
        """
        return None
