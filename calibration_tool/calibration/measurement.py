"""Calibration Measurement Module.

Handles synchronized data acquisition from both encoders:
- KDC101 (reference stage via motorized Thorlabs)
- Arduino AS5048A (encoder under test)
"""

import csv
import os
import time
from dataclasses import dataclass, field
from datetime import datetime

from devices.arduino_encoder import ArduinoEncoder
from devices.kdc101_stage import KDC101Stage


@dataclass
class MeasurementPoint:
    """Single measurement point with timestamp."""

    timestamp: float  # Unix timestamp
    reference_deg: float  # KDC101 position in degrees
    measured_deg: float  # AS5048A position in degrees
    reference_counts: int = 0  # Raw encoder counts (KDC101)

    @property
    def error_deg(self) -> float:
        """Calculate angular error (measured - reference)."""
        error = self.measured_deg - self.reference_deg
        # Normalize to -180 to +180
        while error > 180:
            error -= 360
        while error < -180:
            error += 360
        return error


@dataclass
class CalibrationRun:
    """Complete calibration run with metadata."""

    name: str
    start_time: datetime
    points: list[MeasurementPoint] = field(default_factory=list)
    notes: str = ""

    def add_point(self, point: MeasurementPoint) -> None:
        """Add a measurement point."""
        self.points.append(point)

    @property
    def duration_sec(self) -> float:
        """Total duration of measurement run."""
        if len(self.points) < 2:
            return 0.0
        return self.points[-1].timestamp - self.points[0].timestamp

    @property
    def num_points(self) -> int:
        """Number of measurement points."""
        return len(self.points)

    def get_errors(self) -> list[float]:
        """Get list of all error values."""
        return [p.error_deg for p in self.points]

    def get_reference_angles(self) -> list[float]:
        """Get list of all reference angles."""
        return [p.reference_deg for p in self.points]

    def get_measured_angles(self) -> list[float]:
        """Get list of all measured angles."""
        return [p.measured_deg for p in self.points]


class CalibrationMeasurement:
    """Manages calibration measurement session.

    Workflow:
        1. Connect to both devices
        2. Start measurement (manual rotation at controller)
        3. Continuously read both positions
        4. Stop measurement
        5. Save and analyze data
    """

    def __init__(
        self,
        arduino: ArduinoEncoder,
        kdc101: KDC101Stage,
        encoder_id: str = "A",
    ):
        """Initialize measurement session.

        Args:
            arduino: ArduinoEncoder instance
            kdc101: KDC101Stage instance
            encoder_id: Which AS5048A to read — "A" (sample) or "B" (detector)
        """
        self.arduino = arduino
        self.kdc101 = kdc101
        self.encoder_id = encoder_id
        self.current_run: CalibrationRun | None = None
        self._running = False

    @property
    def is_running(self) -> bool:
        """Check if measurement is currently running."""
        return self._running

    def start_run(self, name: str = "") -> CalibrationRun:
        """Start a new calibration run.

        Args:
            name: Optional name for the run

        Returns:
            New CalibrationRun instance
        """
        if not name:
            name = datetime.now().strftime("calibration_%Y%m%d_%H%M%S")

        self.current_run = CalibrationRun(name=name, start_time=datetime.now())
        self._running = True
        print(f"[Measurement] Started run: {name}")
        return self.current_run

    def stop_run(self) -> CalibrationRun | None:
        """Stop the current calibration run.

        Returns:
            Completed CalibrationRun or None
        """
        self._running = False
        run = self.current_run
        if run:
            print(f"[Measurement] Stopped run: {run.name}")
            print(f"  Points collected: {run.num_points}")
            print(f"  Duration: {run.duration_sec:.1f}s")
        return run

    def take_single_measurement(self) -> MeasurementPoint | None:
        """Take a single synchronized measurement from both encoders.

        Returns:
            MeasurementPoint or None if error
        """
        # Single round-trip: compute degrees from the same counts read
        ref_counts = self.kdc101.get_position_counts()
        ref_deg = (
            ref_counts / self.kdc101.ENCODER_COUNTS_PER_DEG if ref_counts is not None else None
        )

        # Read the chosen AS5048A encoder (no ADC read — intensity is irrelevant here)
        measured_deg = self.arduino.read_angle(self.encoder_id)

        # Encoder A (sample stage): magnet placement reverses the count direction.
        if measured_deg is not None and self.encoder_id == "A":
            measured_deg = (360.0 - measured_deg) % 360.0

        if ref_deg is None or measured_deg is None:
            return None

        point = MeasurementPoint(
            timestamp=time.time(),
            reference_deg=ref_deg,
            measured_deg=measured_deg,
            reference_counts=ref_counts or 0,
        )

        # Add to current run if active
        if self.current_run and self._running:
            self.current_run.add_point(point)

        return point

    def continuous_measurement(self, interval_sec: float = 0.1, callback=None) -> None:
        """Run continuous measurement until stopped.

        Args:
            interval_sec: Time between measurements
            callback: Optional callback(point) for each measurement
        """
        if not self._running:
            print("[Measurement] Start a run first!")
            return

        print(f"[Measurement] Continuous mode started (interval: {interval_sec}s)")
        print("  Press Ctrl+C to stop")

        try:
            while self._running:
                point = self.take_single_measurement()

                if point and callback:
                    callback(point)

                time.sleep(interval_sec)

        except KeyboardInterrupt:
            print("\n[Measurement] Interrupted by user")
            self.stop_run()

    def save_to_csv(self, filepath: str | None = None) -> str:
        """Save current run to CSV file.

        Args:
            filepath: Optional file path (auto-generated if None)

        Returns:
            Path to saved file
        """
        if not self.current_run or not self.current_run.points:
            raise ValueError("No data to save")

        if filepath is None:
            # Create data directory if needed
            data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
            os.makedirs(data_dir, exist_ok=True)
            filepath = os.path.join(data_dir, f"{self.current_run.name}.csv")

        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)

            # Header
            writer.writerow(
                [
                    "timestamp",
                    "reference_deg",
                    "measured_deg",
                    "error_deg",
                    "reference_counts",
                ]
            )

            # Data
            for point in self.current_run.points:
                writer.writerow(
                    [
                        point.timestamp,
                        f"{point.reference_deg:.4f}",
                        f"{point.measured_deg:.4f}",
                        f"{point.error_deg:.4f}",
                        point.reference_counts,
                    ]
                )

        print(f"[Measurement] Saved to: {filepath}")
        return filepath

    @staticmethod
    def load_from_csv(filepath: str) -> CalibrationRun:
        """Load calibration run from CSV file.

        Args:
            filepath: Path to CSV file

        Returns:
            CalibrationRun with loaded data
        """
        name = os.path.splitext(os.path.basename(filepath))[0]
        run = CalibrationRun(name=name, start_time=datetime.now())

        with open(filepath) as f:
            reader = csv.DictReader(f)
            for row in reader:
                point = MeasurementPoint(
                    timestamp=float(row["timestamp"]),
                    reference_deg=float(row["reference_deg"]),
                    measured_deg=float(row["measured_deg"]),
                    reference_counts=int(row.get("reference_counts", 0)),
                )
                run.add_point(point)

        print(f"[Measurement] Loaded {run.num_points} points from {filepath}")
        return run


# Simple test
if __name__ == "__main__":
    print("CalibrationMeasurement module - use with main.py")
