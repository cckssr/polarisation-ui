"""
Automatic power calibration — settings and angle-grid builder.

Stores connection parameters (KDC101, PM400, beamsplitter attenuation) as a
JSON sidecar at ~/.config/polarisation-ui/auto_calibration_settings.json so
they survive application restarts.  Sweep parameters (AutoCalibrationParams)
are kept in memory only; they are filled from the dialog widgets each run.

No Qt, no hardware I/O.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Literal

_SETTINGS_PATH: Path = (
    Path.home() / ".config" / "polarisation-ui" / "auto_calibration_settings.json"
)


@dataclass
class AutoCalibrationConnectionSettings:
    """Persisted connection and instrument configuration."""

    kdc101_conn_id: str = ""
    pm400_visa_resource: str = ""
    beamsplitter_attenuation_dB: float = 0.0
    wavelength_nm: float = 633.0
    angle_offset_deg: float = 0.0
    """Physical stage angle (°) that corresponds to maximum transmission.

    Determined by the polariser auto-alignment scan.  The calibration sweep
    drives the stage to ``logical_angle + angle_offset_deg`` so that logical
    0° always means maximum power regardless of how the polariser is mounted.
    """

    def save(self, path: Path = _SETTINGS_PATH) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as fh:
            json.dump(asdict(self), fh, indent=2)

    @classmethod
    def load(cls, path: Path = _SETTINGS_PATH) -> "AutoCalibrationConnectionSettings":
        if not path.exists():
            return cls()
        try:
            with path.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
            return cls(
                kdc101_conn_id=str(data.get("kdc101_conn_id", "")),
                pm400_visa_resource=str(data.get("pm400_visa_resource", "")),
                beamsplitter_attenuation_dB=float(
                    data.get("beamsplitter_attenuation_dB", 0.0)
                ),
                wavelength_nm=float(data.get("wavelength_nm", 633.0)),
                angle_offset_deg=float(data.get("angle_offset_deg", 0.0)),
            )
        except Exception:
            return cls()


@dataclass(frozen=True)
class AutoCalibrationParams:
    """Immutable sweep configuration passed to the calibration worker."""

    selected_gains: tuple[int, ...]
    angle_start_deg: float
    angle_end_deg: float
    n_points: int
    grid_mode: Literal["linear_angle", "linear_cos2"]
    point_settle_s: float
    gain_settle_s: float
    detector_samples: int
    pm_averaging: int
    profile_name: str
    wavelength_nm: float
    beamsplitter_attenuation_dB: float
    angle_offset_deg: float = 0.0
    adc_saturation_threshold_V: float = 2.35
    """ADC voltage above which a detector reading is treated as saturated.

    Points where the averaged detector voltage meets or exceeds this value are
    not recorded.  The PM400 read is also skipped for those points so that the
    sweep moves on immediately without spending measurement time in saturation.
    Typical ADS1220 full-scale is ~2.4 V; the default 2.35 V leaves a small
    margin below clipping."""
    """Physical stage angle at maximum transmission.  Added to every logical
    sweep angle before sending to the KDC so that sweep angles 0°…90° always
    map to max→min transmission regardless of how the polariser is mounted."""


def build_angle_grid(params: AutoCalibrationParams) -> list[float]:
    """Return a sorted list of *n_points* angles for the sweep.

    ``linear_angle``:  equal angular steps from *angle_start_deg* to
    *angle_end_deg* (inclusive).

    ``linear_cos2``:   steps are equal in cos²(θ) — useful because Malus'
    law means intensity is proportional to cos²(Δθ), so this grid gives
    equal intensity increments across the full range.  When angle_start is
    near 90° and angle_end near 0°, the grid is descending by angle but
    ascending by power.
    """
    n = max(params.n_points, 2)
    a0 = params.angle_start_deg
    a1 = params.angle_end_deg

    if params.grid_mode == "linear_angle":
        step = (a1 - a0) / (n - 1)
        return [a0 + i * step for i in range(n)]

    # linear_cos2: c²_i evenly spaced in [cos²(a0), cos²(a1)]
    c2_start = math.cos(math.radians(a0)) ** 2
    c2_end = math.cos(math.radians(a1)) ** 2
    c2_step = (c2_end - c2_start) / (n - 1)
    angles = []
    for i in range(n):
        c2 = c2_start + i * c2_step
        c2_clamped = max(0.0, min(1.0, c2))
        angles.append(math.degrees(math.acos(math.sqrt(c2_clamped))))
    return angles
