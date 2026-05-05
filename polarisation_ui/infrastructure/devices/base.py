"""Abstract interface for encoder devices, plus a simple in-process mock."""

from abc import ABC, abstractmethod
from typing import Optional


class EncoderAdapter(ABC):
    """Abstract base class for angle encoder devices."""

    @abstractmethod
    def read(self) -> float:
        """Read current angle in degrees."""

    @abstractmethod
    def reset(self) -> None:
        """Reset encoder to zero position."""

    @abstractmethod
    def is_connected(self) -> bool:
        """Return True if device is accessible."""

    @abstractmethod
    def connect(self) -> None:
        """Establish connection to encoder device."""

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from encoder device."""

    @abstractmethod
    def get_raw_value(self) -> Optional[int]:
        """Return raw encoder count, or None if not available."""


class EncoderMock(EncoderAdapter):
    """In-process encoder mock for unit tests — angle is set programmatically."""

    def __init__(self, start_angle: float = 0.0, name: str = "MockEncoder") -> None:
        self.current_angle = start_angle
        self.name = name
        self._connected = True

    def read(self) -> float:
        if not self._connected:
            raise RuntimeError(f"{self.name} is not connected")
        return self.current_angle

    def reset(self) -> None:
        if not self._connected:
            raise RuntimeError(f"{self.name} is not connected")
        self.current_angle = 0.0

    def is_connected(self) -> bool:
        return self._connected

    def connect(self) -> None:
        self._connected = True

    def disconnect(self) -> None:
        self._connected = False

    def get_raw_value(self) -> Optional[int]:
        return int(self.current_angle)

    def set_angle(self, angle: float) -> None:
        self.current_angle = angle
