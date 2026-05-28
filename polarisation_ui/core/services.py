"""Core business logic services for goniometer control.

Services implement domain logic without any PySide6 or Qt dependencies.
They orchestrate operations on models and coordinate with infrastructure
adapters through dependency injection.
"""

from typing import Optional, List
from .models import GoniometerState, EncoderReading
from .exceptions import AngleLimitError, AngleMismatchError


class GoniometerService:
    """Service for managing goniometer state and operations.

    Responsibilities:
    - Maintain current goniometer state
    - Validate angle relationships
    - Process encoder readings
    - Apply angle constraints
    """

    # Physical constraints
    MIN_ANGLE = -180.0
    MAX_ANGLE = 180.0
    ANGLE_TOLERANCE = 0.5  # degrees

    def __init__(self) -> None:
        """Initialize goniometer service with default state."""
        self.current_state: Optional[GoniometerState] = None
        self.reading_history: List[EncoderReading] = []

    def initialize_state(self, sample_angle: float = 0.0) -> GoniometerState:
        """Initialize goniometer to a known state.

        Args:
            sample_angle: Initial sample stage angle in degrees.

        Returns:
            GoniometerState: The initialized state.

        Raises:
            AngleLimitError: If angle exceeds mechanical limits.
        """
        self._validate_angle_range(sample_angle)

        detector_angle = 2.0 * sample_angle
        self.current_state = GoniometerState(
            sample_angle=sample_angle, detector_angle=detector_angle
        )
        return self.current_state

    def update_sample_angle(self, angle: float) -> Optional[GoniometerState]:
        """Update sample stage angle (upper stage).

        The detector angle is automatically calculated to maintain
        the 2x relationship.

        Args:
            angle: New sample angle in degrees.

        Returns:
            Optional[GoniometerState]: Updated state.

        Raises:
            AngleLimitError: If angle exceeds limits.
        """
        if self.current_state is None:
            self.initialize_state(angle)
        else:
            self._validate_angle_range(angle)
            detector_angle = 2.0 * angle
            self.current_state = GoniometerState(
                sample_angle=angle, detector_angle=detector_angle
            )

        return self.current_state

    def process_encoder_reading(
        self, stage: str, angle: float
    ) -> Optional[GoniometerState]:
        """Process an encoder reading from hardware.

        Encoder readings are the electronic feedback of manual positions.
        If detector reading provided, it will be validated against sample angle.

        Args:
            stage: 'sample' or 'detector'
            angle: Measured angle in degrees.

        Returns:
            Optional[GoniometerState]: Updated state.

        Raises:
            AngleLimitError: If angle exceeds limits.
            AngleMismatchError: If detector angle doesn't follow 2x rule.
        """
        self._validate_angle_range(angle)
        reading = EncoderReading(stage=stage, angle_degrees=angle)
        self.reading_history.append(reading)

        if self.current_state is None:
            # First reading - assume it's sample
            if stage == "detector":
                sample_angle = angle / 2.0
            else:
                sample_angle = angle
            self.initialize_state(sample_angle)
        else:
            if stage == "sample":
                self.update_sample_angle(angle)
            elif stage == "detector":
                # Validate detector matches sample
                expected_detector = 2.0 * self.current_state.sample_angle
                if abs(angle - expected_detector) > self.ANGLE_TOLERANCE:
                    raise AngleMismatchError(
                        f"Detector angle {angle}° doesn't match expected "
                        f"{expected_detector}° (tolerance: {self.ANGLE_TOLERANCE}°)"
                    )
                self.current_state.detector_angle = angle

        return self.current_state

    def get_state(self) -> Optional[GoniometerState]:
        """Get current goniometer state."""
        return self.current_state

    def get_reading_history(self, limit: Optional[int] = None) -> List[EncoderReading]:
        """Get history of encoder readings.

        Args:
            limit: Maximum number of readings to return. None = all.

        Returns:
            List of encoder readings.
        """
        if limit is None:
            return self.reading_history
        return self.reading_history[-limit:]

    def reset(self) -> None:
        """Reset service to initial state."""
        self.current_state = None
        self.reading_history = []

    def _validate_angle_range(self, angle: float) -> None:
        """Validate angle is within mechanical limits.

        Args:
            angle: Angle to validate in degrees.

        Raises:
            AngleLimitError: If angle exceeds limits.
        """
        if not (self.MIN_ANGLE <= angle <= self.MAX_ANGLE):
            raise AngleLimitError(
                f"Angle {angle}° out of range [{self.MIN_ANGLE}, {self.MAX_ANGLE}]"
            )
