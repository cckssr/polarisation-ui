"""Intensity-actuator abstraction for the automated power-calibration sweep.

AutoPowerCalibrationWorker varies beam intensity by moving one of two
possible actuators: the rotating polariser (Malus's law) or the axial
gradient ND-filter wheel driven by the ESP32/DRV8825 stepper controller.
Both expose the same tiny surface so the sweep loop doesn't need to know
which one it's driving.
"""

from __future__ import annotations

from typing import Protocol

from polarisation_ui.infrastructure.devices.kdc101_polariser import KDC101Polariser
from polarisation_ui.infrastructure.devices.nd_stepper import NDStepperStage


class IntensityActuator(Protocol):
    """Common surface for whatever device varies beam intensity during a sweep."""

    unit: str
    """Native unit of *level* in ``move_to`` — always ``"deg"`` (both actuators rotate)."""
    label: str
    """Human-readable name for logs and profile metadata."""

    def home(self) -> None:
        """Home the underlying stage."""
        ...

    def move_to(self, level: float) -> None:
        """Move to *level*, blocking until the move completes."""
        ...

    def metadata(self) -> dict:
        """Return a JSON-serialisable description for the profile's intensity_control field."""
        ...


class PolariserActuator:
    """Drives beam intensity by rotating a polariser (Malus's law)."""

    unit = "deg"
    label = "Polarisator"

    def __init__(self, kdc: KDC101Polariser, angle_offset_deg: float = 0.0) -> None:
        """Wrap *kdc*; *angle_offset_deg* is the physical angle of maximum transmission."""
        self._kdc = kdc
        self._angle_offset_deg = angle_offset_deg

    def home(self) -> None:
        """Home the KDC101 + PRM1-Z8 stage."""
        self._kdc.home()

    def move_to(self, level: float) -> None:
        """Move to logical angle *level* (degrees), offset by the max-transmission angle."""
        self._kdc.move_to(level + self._angle_offset_deg)

    def metadata(self) -> dict:
        """Describe this run's polariser configuration for the profile JSON."""
        return {
            "kind": "polariser",
            "stage": "PRM1-Z8",
            "scale": "PRM1-Z8",
            "unit": self.unit,
            "angle_offset_deg": self._angle_offset_deg,
        }


class NDFilterActuator:
    """Drives beam intensity by rotating an axial gradient ND filter."""

    unit = "deg"
    label = "ND-Filter"

    def __init__(self, nd: NDStepperStage, nd_range: object | None = None) -> None:
        """Wrap *nd*; *nd_range* (an ``NDFilterRange``, optional) is recorded as provenance."""
        self._nd = nd
        self._nd_range = nd_range

    def home(self) -> None:
        """Deliberately do nothing: the sweep must not re-reference the ND wheel.

        Without a home switch ``NDStepperStage.home()`` redefines the *current*
        position as 0°. The sweep inverts the position/power curve of the range
        scan, which is expressed in the wheel frame that existed when that scan
        ran — zeroing here (typically at the scan's end position) would shift
        every target angle and drive the wheel to the wrong place. The
        reference is set by the user ("Nullpunkt setzen" / "Referenzfahrt")
        before the range scan and stays untouched afterwards.
        """

    def move_to(self, level: float) -> None:
        """Move to wheel angle *level* (degrees)."""
        self._nd.move_to_deg(level)

    def metadata(self) -> dict:
        """Describe this run's ND-stage configuration and calibrated range for the profile JSON."""
        meta: dict = {
            "kind": "nd_filter",
            "stage": "ESP32+DRV8825 stepper",
            "unit": self.unit,
        }
        if self._nd_range is not None:
            meta["range"] = [self._nd_range.pos_clear_deg, self._nd_range.pos_dark_deg]
            meta["power_range_W"] = [self._nd_range.power_clear_W, self._nd_range.power_dark_W]
            meta["dynamic_range_dB"] = self._nd_range.dynamic_range_dB
        return meta
