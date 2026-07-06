"""Calibration Analysis Module.

Analyzes calibration data to determine:
- Error magnitude and direction
- Optimal magnet positioning offset
- Fourier components of the error
"""

import math
from dataclasses import dataclass

import numpy as np

from .measurement import CalibrationRun


@dataclass
class CalibrationResult:
    """Results of calibration analysis."""

    # Basic statistics
    mean_error: float  # Mean error in degrees
    std_error: float  # Standard deviation of error
    max_error: float  # Maximum absolute error
    min_error: float  # Minimum error

    # Sinusoidal fit (1x per revolution)
    amplitude_1x: float  # Amplitude of 1x component (degrees)
    phase_1x: float  # Phase of 1x component (degrees)

    # Sinusoidal fit (2x per revolution)
    amplitude_2x: float  # Amplitude of 2x component (degrees)
    phase_2x: float  # Phase of 2x component (degrees)

    # Offset recommendation
    offset_direction: float  # Direction to move magnet (degrees)
    offset_magnitude: str  # Qualitative assessment

    def summary(self) -> str:
        """Generate human-readable summary."""
        lines = [
            "=" * 60,
            "CALIBRATION ANALYSIS RESULTS",
            "=" * 60,
            "",
            "Error Statistics:",
            f"  Mean error:     {self.mean_error:+.3f}°",
            f"  Std deviation:  {self.std_error:.3f}°",
            f"  Max error:      {self.max_error:+.3f}°",
            f"  Min error:      {self.min_error:+.3f}°",
            "",
            "Harmonic Analysis:",
            f"  1x amplitude:   {self.amplitude_1x:.3f}° at phase {self.phase_1x:.1f}°",
            f"  2x amplitude:   {self.amplitude_2x:.3f}° at phase {self.phase_2x:.1f}°",
            "",
            "Magnet Alignment Recommendation:",
            f"  Move magnet towards {self.offset_direction:.1f}° direction",
            f"  Adjustment needed: {self.offset_magnitude}",
            "=" * 60,
        ]
        return "\n".join(lines)


class CalibrationAnalysis:
    """Analyzes calibration measurement data.

    The main sources of error in AS5048A encoders with off-center magnets:

    1. **1x per revolution (eccentricity)**:
       Magnet center offset from rotation axis.
       Shows as sin/cos error at 1x rotation frequency.

    2. **2x per revolution (ellipticity)**:
       Non-uniform magnetic field distribution.
       Shows as sin/cos error at 2x rotation frequency.

    The analysis extracts these components and recommends
    magnet positioning adjustments.
    """

    def __init__(self, run: CalibrationRun):
        """Initialize analysis with calibration run.

        Args:
            run: CalibrationRun with measurement data
        """
        self.run = run
        self._result: CalibrationResult | None = None

    def analyze(self) -> CalibrationResult:
        """Perform full analysis on the calibration data.

        Returns:
            CalibrationResult with analysis findings
        """
        if len(self.run.points) < 10:
            raise ValueError("Need at least 10 points for analysis")

        # Extract data arrays
        ref_angles = np.array(self.run.get_reference_angles())
        errors = np.array(self.run.get_errors())

        # Convert reference angles to radians
        ref_rad = np.deg2rad(ref_angles)

        # Basic statistics
        mean_error = np.mean(errors)
        std_error = np.std(errors)
        max_error = np.max(errors)
        min_error = np.min(errors)

        # Fourier analysis for 1x component
        amp_1x, phase_1x = self._fit_sinusoid(ref_rad, errors, harmonic=1)

        # Fourier analysis for 2x component
        amp_2x, phase_2x = self._fit_sinusoid(ref_rad, errors, harmonic=2)

        # Determine offset recommendation
        # The phase of the 1x component indicates where the error is maximum,
        # which is opposite to the direction the magnet should move
        offset_direction = (phase_1x + 180) % 360

        # Qualitative assessment based on amplitude
        if amp_1x < 0.1:
            offset_magnitude = "Excellent - no adjustment needed"
        elif amp_1x < 0.5:
            offset_magnitude = "Good - minor adjustment may help"
        elif amp_1x < 1.0:
            offset_magnitude = "Moderate - adjustment recommended"
        elif amp_1x < 2.0:
            offset_magnitude = "Significant - adjustment needed"
        else:
            offset_magnitude = "Large - major adjustment required"

        self._result = CalibrationResult(
            mean_error=mean_error,
            std_error=std_error,
            max_error=max_error,
            min_error=min_error,
            amplitude_1x=amp_1x,
            phase_1x=phase_1x,
            amplitude_2x=amp_2x,
            phase_2x=phase_2x,
            offset_direction=offset_direction,
            offset_magnitude=offset_magnitude,
        )

        return self._result

    def _fit_sinusoid(
        self, angles_rad: np.ndarray, errors: np.ndarray, harmonic: int = 1
    ) -> tuple[float, float]:
        """Fit a sinusoidal component to the error data.

        Uses least-squares fit: error = A*sin(n*theta + phi) + offset
        Which can be rewritten as: error = a*sin(n*theta) + b*cos(n*theta) + c

        Args:
            angles_rad: Reference angles in radians
            errors: Error values in degrees
            harmonic: Harmonic number (1 = 1x per rev, 2 = 2x per rev)

        Returns:
            Tuple of (amplitude, phase_degrees)
        """
        n = harmonic

        # Build design matrix for least squares
        # error = a*sin(n*theta) + b*cos(n*theta) + c
        sin_term = np.sin(n * angles_rad)
        cos_term = np.cos(n * angles_rad)
        ones = np.ones_like(angles_rad)

        A = np.column_stack([sin_term, cos_term, ones])

        # Solve least squares
        coeffs, residuals, rank, s = np.linalg.lstsq(A, errors, rcond=None)
        a, b, c = coeffs

        # Convert to amplitude and phase
        amplitude = np.sqrt(a**2 + b**2)
        phase_rad = np.arctan2(b, a)
        phase_deg = np.rad2deg(phase_rad)

        # Normalize phase to 0-360
        if phase_deg < 0:
            phase_deg += 360

        return amplitude, phase_deg

    def get_error_at_angle(self, angle_deg: float) -> float:
        """Predict error at a given angle using the fitted model.

        Args:
            angle_deg: Reference angle in degrees

        Returns:
            Predicted error in degrees
        """
        if self._result is None:
            self.analyze()

        r = self._result
        angle_rad = math.radians(angle_deg)

        # Reconstruct from harmonics
        error = r.mean_error
        error += r.amplitude_1x * math.sin(angle_rad + math.radians(r.phase_1x))
        error += r.amplitude_2x * math.sin(2 * angle_rad + math.radians(r.phase_2x))

        return error

    def get_polar_data(self) -> tuple[list[float], list[float]]:
        """Get data formatted for polar plot.

        Returns:
            Tuple of (angles_rad, errors_magnitude)
        """
        angles = [math.radians(a) for a in self.run.get_reference_angles()]
        # Use absolute error for radius (or signed for direction indication)
        errors = self.run.get_errors()

        return angles, errors

    def get_error_vs_angle_data(self) -> tuple[list[float], list[float]]:
        """Get data for Cartesian error vs angle plot.

        Returns:
            Tuple of (angles_deg, errors_deg)
        """
        return self.run.get_reference_angles(), self.run.get_errors()


# Simple test
if __name__ == "__main__":
    print("CalibrationAnalysis module - use with main.py")
