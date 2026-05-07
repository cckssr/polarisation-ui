"""
Power calibration profiles for the PD-TIA detector.

Each detector requires its own calibration because the TIA gain resistors vary.
A profile stores (voltage_V, power_W) measurement pairs for each of the four
discrete PDTIA gain stages, plus a derived W/V conversion factor used to convert
live ADC readings to optical power in real time.

Profiles are stored as JSON files in PROFILES_DIR.  The application loads a
user-selected profile and pushes it to the Malus tab and the power LCD.

File format example:
    {
      "name": "Det-A",
      "calibrated_at": "2025-01-15",
      "gains": {
        "1": {"points": [[0.234, 1.0e-6], [0.468, 2.0e-6]]},
        "2": {"points": [[0.112, 1.0e-6], [0.225, 2.0e-6]]},
        "3": {"points": [[0.056, 1.0e-6]]},
        "4": {"points": []}
      }
    }
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Optional

PROFILES_DIR: Path = Path.home() / ".config" / "polarisation-ui" / "detector_profiles"

VALID_GAIN_STAGES: tuple[int, ...] = (1, 2, 3, 4)


@dataclass
class GainCalibration:
    """Measurement points for a single PDTIA gain stage."""

    gain_stage: int
    points: list[tuple[float, float]] = field(default_factory=list)

    def add_point(self, voltage_V: float, power_W: float) -> None:
        self.points.append((voltage_V, power_W))

    def remove_point(self, index: int) -> bool:
        if 0 <= index < len(self.points):
            del self.points[index]
            return True
        return False

    def conversion_factor_W_per_V(self) -> Optional[float]:
        """Mean W/V ratio across all calibration points. None if no points."""
        if not self.points:
            return None
        valid = [p_w / v_v for v_v, p_w in self.points if v_v > 0]
        if not valid:
            return None
        return sum(valid) / len(valid)

    def watts_from_voltage(self, voltage_V: float) -> Optional[float]:
        factor = self.conversion_factor_W_per_V()
        if factor is None:
            return None
        return voltage_V * factor


@dataclass
class PowerCalibrationProfile:
    """Full detector calibration across all four PDTIA gain stages."""

    name: str
    calibrated_at: str = field(default_factory=lambda: date.today().isoformat())
    gains: dict[int, GainCalibration] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for stage in VALID_GAIN_STAGES:
            if stage not in self.gains:
                self.gains[stage] = GainCalibration(gain_stage=stage)

    def gain_cal(self, stage: int) -> GainCalibration:
        return self.gains.setdefault(stage, GainCalibration(gain_stage=stage))

    def watts_from_voltage(self, voltage_V: float, gain_stage: int) -> Optional[float]:
        cal = self.gains.get(gain_stage)
        if cal is None:
            return None
        return cal.watts_from_voltage(voltage_V)

    def conversion_factor(self, gain_stage: int) -> Optional[float]:
        cal = self.gains.get(gain_stage)
        if cal is None:
            return None
        return cal.conversion_factor_W_per_V()

    # ── Persistence ──────────────────────────────────────────────────────────

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "name": self.name,
            "calibrated_at": self.calibrated_at,
            "gains": {
                str(stage): {"points": list(cal.points)}
                for stage, cal in self.gains.items()
            },
        }
        with path.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)

    @classmethod
    def load(cls, path: Path) -> "PowerCalibrationProfile":
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        profile = cls(
            name=data.get("name", path.stem),
            calibrated_at=data.get("calibrated_at", ""),
        )
        for stage_str, cal_data in data.get("gains", {}).items():
            stage = int(stage_str)
            raw_points = cal_data.get("points", [])
            profile.gains[stage] = GainCalibration(
                gain_stage=stage,
                points=[(float(v), float(p)) for v, p in raw_points],
            )
        return profile

    # ── Directory helpers ────────────────────────────────────────────────────

    @staticmethod
    def list_profiles(directory: Path = PROFILES_DIR) -> list[Path]:
        """Return sorted list of .json profile files in *directory*."""
        if not directory.exists():
            return []
        return sorted(directory.glob("*.json"))

    @staticmethod
    def default_path(name: str, directory: Path = PROFILES_DIR) -> Path:
        safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
        return directory / f"{safe}.json"
