"""
Core domain models for goniometer control system.

This module contains pure Python dataclasses representing the
goniometer state without any Qt or UI dependencies.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


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
    adc_voltage: Optional[float] = None
    adc_temperature: Optional[float] = None

    def __post_init__(self) -> None:
        """Initialize timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now()


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
    # Hardware flag: the sample-stage magnet is mounted diametrically flipped,
    # so the raw angle increases in the wrong direction.  When True the
    # DataController applies  corrected = (360 - raw) % 360  before emitting.
    sample_stage_inverted: bool = True
    spike_filter_enabled: bool = True
    spike_max_delta_deg: float = 10.0  # 100 °/s at default 10 Hz — rejects glitches


@dataclass
class Frame:
    """Consolidated per-sample data frame emitted by DataController at the polling rate."""

    ts_ms: int
    sample_angle: float
    detector_angle: float
    intensity: float
