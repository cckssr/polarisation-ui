"""
Core domain models for goniometer control system.

This module contains pure Python dataclasses representing the
goniometer state without any Qt or UI dependencies.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class GoniometerState:
    """
    Represents the state of a dual-stage goniometer.

    The goniometer follows a specific mechanical relationship:
    detector_angle = 2 * sample_angle

    This ensures the detector always reflects back to the sample
    at the correct geometry for reflection measurements.
    """

    sample_angle: float  # Upper stage angle (degrees) - sample position
    detector_angle: float  # Lower stage angle (degrees) - detector arm position
    timestamp: datetime = None

    def __post_init__(self) -> None:
        """Initialize timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def validate(self) -> bool:
        """
        Validate goniometer state against physical constraints.

        Returns:
            bool: True if state is valid, False otherwise.
        """
        # Check if detector angle follows 2x relationship
        expected_detector = 2.0 * self.sample_angle
        tolerance = 0.1  # degrees

        is_valid = abs(self.detector_angle - expected_detector) <= tolerance
        return is_valid

    def get_validation_error(self) -> Optional[str]:
        """
        Get human-readable validation error if state is invalid.

        Returns:
            str or None: Error message if invalid, None if valid.
        """
        expected = 2.0 * self.sample_angle
        difference = abs(self.detector_angle - expected)

        if difference > 0.1:
            return (
                f"Detector angle deviation detected. "
                f"Expected {expected:.2f}°, got {self.detector_angle:.2f}° "
                f"(difference: {difference:.2f}°)"
            )
        return None


@dataclass
class EncoderReading:
    """
    Represents a single reading from an encoder device.

    Encoders provide electronic feedback of the manual stage position.
    """

    stage: str  # 'sample' or 'detector'
    angle_degrees: float
    raw_value: Optional[int] = None  # Raw encoder count if available


@dataclass
class PhotodiodeReading:
    """Represents a single photodiode measurement."""

    voltage: float  # Measured voltage in volts


@dataclass
class MeasurementPoint:
    """A single measurement point with goniometer stages and photodiode data."""

    sample_stage_reading: EncoderReading  # Sample stage angle
    detector_stage_reading: EncoderReading  # Detector stage angle
    photodiode_reading: PhotodiodeReading
    timestamp: datetime = None

    def __post_init__(self) -> None:
        """Initialize timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class MeasurementSession:
    """Complete measurement session with metadata."""

    points: List[MeasurementPoint] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    subterm: str = ""
    group: str = ""

    @property
    def duration_seconds(self) -> float:
        """Calculate duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

    @property
    def count(self) -> int:
        """Number of data points."""
        return len(self.points)


@dataclass
class AcquisitionSettings:
    """
    Acquisition settings for the current session.

    Loaded from config at startup; changes made in the settings dialog
    are kept in memory only and are never written back to config.json.
    """

    det_average_on: bool = True
    det_averages: int = 5
    samp_average_on: bool = True
    samp_averages: int = 5


@dataclass
class DeviceInfo:
    """Arduino device information and status."""

    port: str
    baudrate: int = 115200
    connected: bool = False
    firmware_version: str = ""
    hardware_version: str = ""
