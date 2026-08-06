"""Power calibration profiles for the PD-TIA detector.

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
from datetime import datetime
from pathlib import Path

PROFILES_DIR: Path = Path.home() / ".config" / "polarisation-ui" / "detector_profiles"

VALID_GAIN_STAGES: tuple[int, ...] = (1, 2, 3, 4)


@dataclass
class GainCalibration:
    """Measurement points for a single PDTIA gain stage."""

    gain_stage: int
    points: list[tuple[float, float]] = field(default_factory=list)
    n_saturated_skipped: int = 0

    def add_point(self, voltage_V: float, power_W: float) -> None:
        """Add a new calibration point (voltage, power) to this gain stage.

        Args:
            voltage_V: Measured voltage from the ADC (V)
            power_W: Corresponding optical power measured by the PM400 (W)
        """
        self.points.append((voltage_V, power_W))

    def remove_point(self, index: int) -> bool:
        """Remove a calibration point by index.

        Args:
            index: The index of the point to remove in the points list.

        Returns:
            bool: True if the point was successfully removed, False if index was out of range.
        """
        if 0 <= index < len(self.points):
            del self.points[index]
            return True
        return False

    def conversion_factor_W_per_V(self) -> float | None:
        """Mean W/V ratio across all calibration points.

        Returns:
            float or None: The average conversion factor in W/V. None if no valid points available.
        """
        if not self.points:
            return None
        valid = [p_w / v_v for v_v, p_w in self.points if v_v > 0]
        if not valid:
            return None
        return sum(valid) / len(valid)

    def watts_from_voltage(self, voltage_V: float) -> float | None:
        """Convert a voltage reading to power using the calibration points.

        Args:
            voltage_V: The voltage reading to convert (V)

        Returns:
            float or None: The corresponding power in W. None if conversion factor is unavailable.
        """
        factor = self.conversion_factor_W_per_V()
        if factor is None:
            return None
        return voltage_V * factor


@dataclass
class PowerCalibrationProfile:
    """Full detector calibration across all four PDTIA gain stages."""

    name: str
    # Full ISO-8601 datetime string, e.g. "2025-06-01T14:30:00.123456"
    calibrated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    # Instrument / beam metadata — populated by the auto-calibration worker
    wavelength_nm: float | None = None
    beamsplitter_attenuation_dB: float | None = None
    adc_saturation_threshold_V: float | None = None
    # PM400 sensor identification (name, serial, calibration_message, type, subtype, flags)
    sensor: dict = field(default_factory=dict)
    units: dict = field(default_factory=lambda: {"voltage": "V", "power": "W"})
    gains: dict[int, GainCalibration] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Ensure every valid gain stage has a (possibly empty) GainCalibration."""
        for stage in VALID_GAIN_STAGES:
            if stage not in self.gains:
                self.gains[stage] = GainCalibration(gain_stage=stage)

    def gain_cal(self, stage: int) -> GainCalibration:
        """Return the GainCalibration for *stage*, creating an empty one if absent."""
        return self.gains.setdefault(stage, GainCalibration(gain_stage=stage))

    def watts_from_voltage(self, voltage_V: float, gain_stage: int) -> float | None:
        """Convert a voltage reading to power using the calibration for *gain_stage*."""
        cal = self.gains.get(gain_stage)
        if cal is None:
            return None
        return cal.watts_from_voltage(voltage_V)

    def conversion_factor(self, gain_stage: int) -> float | None:
        """Return the W/V conversion factor for *gain_stage*, or None if uncalibrated."""
        cal = self.gains.get(gain_stage)
        if cal is None:
            return None
        return cal.conversion_factor_W_per_V()

    # ── Persistence ──────────────────────────────────────────────────────────

    def save(self, path: Path) -> None:
        """Write this profile to *path* as JSON, creating parent directories as needed."""
        path.parent.mkdir(parents=True, exist_ok=True)
        data: dict = {
            "name": self.name,
            "calibrated_at": self.calibrated_at,
            "wavelength_nm": self.wavelength_nm,
            "beamsplitter_attenuation_dB": self.beamsplitter_attenuation_dB,
            "adc_saturation_threshold_V": self.adc_saturation_threshold_V,
            "sensor": self.sensor,
            "units": self.units,
            "gains": {
                str(stage): {
                    "points": list(cal.points),
                    "n_points": len(cal.points),
                    "n_saturated_skipped": cal.n_saturated_skipped,
                    "conversion_factor_W_per_V": cal.conversion_factor_W_per_V(),
                }
                for stage, cal in self.gains.items()
            },
        }
        with path.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)

    @classmethod
    def load(cls, path: Path) -> PowerCalibrationProfile:
        """Load a profile previously written by save() from *path*."""
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        profile = cls(
            name=data.get("name", path.stem),
            calibrated_at=data.get("calibrated_at", ""),
            wavelength_nm=data.get("wavelength_nm"),
            beamsplitter_attenuation_dB=data.get("beamsplitter_attenuation_dB"),
            adc_saturation_threshold_V=data.get("adc_saturation_threshold_V"),
            sensor=data.get("sensor", {}),
            units=data.get("units", {"voltage": "V", "power": "W"}),
        )
        for stage_str, cal_data in data.get("gains", {}).items():
            stage = int(stage_str)
            raw_points = cal_data.get("points", [])
            profile.gains[stage] = GainCalibration(
                gain_stage=stage,
                points=[(float(v), float(p)) for v, p in raw_points],
                n_saturated_skipped=int(cal_data.get("n_saturated_skipped", 0)),
            )
        return profile

    # ── Directory helpers ────────────────────────────────────────────────────

    def to_save_metadata(self) -> dict:
        """Return a metadata dict suitable for embedding in a saved CSV."""
        return {
            "profile_name": self.name,
            "calibrated_at": self.calibrated_at,
            "gain_conversion_factors": {
                str(stage): cal.conversion_factor_W_per_V()
                for stage, cal in self.gains.items()
                if cal.conversion_factor_W_per_V() is not None
            },
        }

    @staticmethod
    def list_profiles(directory: Path = PROFILES_DIR) -> list[Path]:
        """Return sorted list of .json profile files in *directory*."""
        if not directory.exists():
            return []
        return sorted(directory.glob("*.json"))

    @staticmethod
    def default_path(name: str, directory: Path = PROFILES_DIR) -> Path:
        """Return the default .json path for a profile named *name* in *directory*."""
        safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
        return directory / f"{safe}.json"


def select_best_profile_for_device_id(profiles: list[Path], device_id: str) -> Path | None:
    """Pick the newest calibration profile whose filename contains *device_id*.

    Filenames that start with an 8-digit date (yyyymmdd) are considered newer
    than undated ones; among dated files the lexicographically greatest date
    wins. Returns None if *device_id* is empty or no profile matches.
    """
    if not device_id:
        return None

    matching = [p for p in profiles if device_id in p.stem]
    if not matching:
        return None

    def _sort_key(path: Path) -> tuple:
        stem = path.stem
        if len(stem) >= 8 and stem[:8].isdigit():
            return (1, stem[:8])
        return (0, "")

    return sorted(matching, key=_sort_key, reverse=True)[0]
