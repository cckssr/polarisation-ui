"""
Manual calibration controller.

Step-through calibration without a motorized reference stage: the user
physically sets each target angle and clicks Accept to record the encoder
reading at that position.  Produces the same CalibrationRun / MeasurementPoint
data model as the KDC101 path so the existing analysis and plotting code works
unchanged.
"""

import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from calibration.measurement import CalibrationRun, MeasurementPoint
from devices.arduino_encoder import ArduinoEncoder


@dataclass
class ManualCalibrationController:
    """
    Drives a manual, step-by-step calibration run.

    Usage::

        ctrl = ManualCalibrationController(arduino, step_size_deg=10.0)
        while not ctrl.is_complete:
            # show ctrl.current_target to the user
            point = ctrl.accept_current()   # or ctrl.skip_current()
        run = ctrl.get_run()
    """

    arduino: ArduinoEncoder
    step_size_deg: float
    run_name: str = ""

    def __post_init__(self) -> None:
        if not (0.1 <= self.step_size_deg <= 90.0):
            raise ValueError("step_size_deg must be between 0.1 and 90")
        if not self.run_name:
            self.run_name = datetime.now().strftime("manual_cal_%Y%m%d_%H%M%S")

        angle = 0.0
        targets: List[float] = []
        while angle < 360.0 - 1e-9:
            targets.append(round(angle, 6))
            angle += self.step_size_deg
        self._targets = targets
        self._current_index = 0
        self._run = CalibrationRun(name=self.run_name, start_time=datetime.now())

    # ------------------------------------------------------------------
    # Read-only state

    @property
    def current_target(self) -> Optional[float]:
        """Target angle the user should set, or None when complete."""
        if self._current_index >= len(self._targets):
            return None
        return self._targets[self._current_index]

    @property
    def step_index(self) -> int:
        """0-based index of the current step."""
        return self._current_index

    @property
    def total_steps(self) -> int:
        return len(self._targets)

    @property
    def is_complete(self) -> bool:
        return self._current_index >= len(self._targets)

    # ------------------------------------------------------------------
    # Actions

    def accept_current(self) -> MeasurementPoint:
        """
        Read the encoder and record a point for the current target angle.

        Raises RuntimeError if the encoder read fails or the run is already
        complete.
        """
        if self.is_complete:
            raise RuntimeError("Calibration run is already complete")

        measured = self.arduino.read_angle()
        if measured is None:
            raise RuntimeError("Encoder read returned None — check connection")

        point = MeasurementPoint(
            timestamp=time.time(),
            reference_deg=self._targets[self._current_index],
            measured_deg=measured,
        )
        self._run.add_point(point)
        self._current_index += 1
        return point

    def skip_current(self) -> None:
        """Advance past the current target without recording a point."""
        if not self.is_complete:
            self._current_index += 1

    def get_run(self) -> CalibrationRun:
        """Return the CalibrationRun accumulated so far."""
        return self._run
