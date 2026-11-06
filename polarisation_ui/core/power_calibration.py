"""Power calibration profiles for the PD-TIA detector.

Each detector requires its own calibration because the TIA gain resistors vary.
A profile stores (voltage_V, power_W) measurement pairs for each of the four
discrete PDTIA gain stages, plus a derived W/V conversion factor and zero-light
voltage offset (weighted least-squares fit, see GainCalibration.fit) used to
convert live ADC readings to optical power in real time.

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

"intensity_control" and "gain_crosscheck" are optional metadata blocks added
for the ND-filter intensity source (see infrastructure/devices/intensity_actuator.py
and core/gain_crosscheck.py) — purely informational, read via .get() with an
empty-dict default, so older files without them load unchanged and older
readers of new files simply ignore them. Neither is consulted by
watts_from_voltage() or conversion_factor().
"""

from __future__ import annotations

import json
import math
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

    def fit(self) -> tuple[float, float] | None:
        """Fit ``P = slope * (V - V0)`` to the calibration points.

        The fit is a weighted least-squares line ``P = slope * V + b`` with
        weights ``1 / P**2`` (i.e. it minimises the *relative* power error, so
        the low-power end is not drowned out by the high-power points). ``V0 =
        -b / slope`` is the voltage the PD-TIA reads at zero light (dark
        offset); it is typically a few mV and differs per gain stage.

        A plain mean of the per-point ratios ``P / V`` must not be used here:
        points with a tiny ``V`` have a hugely inflated ratio, which biased the
        factor up by up to 2x for the low-voltage gain stages.

        Returns:
            ``(slope_W_per_V, zero_offset_V)`` or None if no usable fit exists.
            With a single usable point (or points that all share one voltage)
            the fit falls back to a line through the origin (``V0 = 0``).
        """
        pts = [(v, p) for v, p in self.points if math.isfinite(v) and math.isfinite(p) and p > 0]
        if not pts:
            return None

        weights = [1.0 / (p * p) for _, p in pts]
        sw = sum(weights)
        sv = sum(w * v for w, (v, _) in zip(weights, pts, strict=True))
        sp = sum(w * p for w, (_, p) in zip(weights, pts, strict=True))
        svv = sum(w * v * v for w, (v, _) in zip(weights, pts, strict=True))
        svp = sum(w * v * p for w, (v, p) in zip(weights, pts, strict=True))

        denom = sw * svv - sv * sv
        slope: float | None = None
        offset_V = 0.0
        # Relative tolerance: denom is a difference of nearly equal products
        # when every point shares the same voltage.
        if len(pts) >= 2 and denom > 1e-12 * sw * svv:
            slope = (sw * svp - sv * sp) / denom
            if slope > 0.0:
                intercept = (sp - slope * sv) / sw
                offset_V = -intercept / slope
        if slope is None or slope <= 0.0:
            # Degenerate data: line through the origin, weighted LS slope.
            if svv <= 0.0:
                return None
            slope = svp / svv
            offset_V = 0.0
            if slope <= 0.0:
                return None
        return slope, offset_V

    def conversion_factor_W_per_V(self) -> float | None:
        """Slope of the fitted voltage→power line in W/V (see :meth:`fit`).

        Returns:
            float or None: The conversion factor in W/V. None if no valid fit is available.
        """
        fitted = self.fit()
        return None if fitted is None else fitted[0]

    def zero_offset_V(self) -> float:
        """Zero-light PD-TIA voltage ``V0`` of the fit (see :meth:`fit`); 0.0 if unavailable."""
        fitted = self.fit()
        return 0.0 if fitted is None else fitted[1]

    def watts_from_voltage(self, voltage_V: float) -> float | None:
        """Convert a raw voltage reading to power using the fitted calibration.

        Args:
            voltage_V: The raw (not dark-tared) ADC voltage to convert (V)

        Returns:
            float or None: ``slope * (V - V0)`` in W. None if no fit is available.
        """
        fitted = self.fit()
        if fitted is None:
            return None
        slope, offset_V = fitted
        return slope * (voltage_V - offset_V)


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
    # Provenance of the intensity actuator used for this run — see
    # infrastructure/devices/intensity_actuator.py. Purely informational;
    # never read back by watts_from_voltage() or conversion_factor().
    intensity_control: dict = field(default_factory=dict)
    # Post-calibration gain-switch consistency check — see
    # core/gain_crosscheck.py. Purely informational.
    gain_crosscheck: dict = field(default_factory=dict)

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

    def zero_offset_V(self, gain_stage: int) -> float:
        """Return the zero-light voltage ``V0`` for *gain_stage* (0.0 if uncalibrated)."""
        cal = self.gains.get(gain_stage)
        return 0.0 if cal is None else cal.zero_offset_V()

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
            "intensity_control": self.intensity_control,
            "gain_crosscheck": self.gain_crosscheck,
            "gains": {
                str(stage): {
                    "points": list(cal.points),
                    "n_points": len(cal.points),
                    "n_saturated_skipped": cal.n_saturated_skipped,
                    "conversion_factor_W_per_V": cal.conversion_factor_W_per_V(),
                    "zero_offset_V": cal.zero_offset_V(),
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
            intensity_control=data.get("intensity_control", {}),
            gain_crosscheck=data.get("gain_crosscheck", {}),
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
            "wavelength_nm": self.wavelength_nm,
            "gain_conversion_factors": {
                str(stage): cal.conversion_factor_W_per_V()
                for stage, cal in self.gains.items()
                if cal.conversion_factor_W_per_V() is not None
            },
            "gain_zero_offsets_V": {
                str(stage): cal.zero_offset_V()
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


def select_gain_for_power(
    power_W: float,
    limits: dict[int, tuple[float, float]],
    current_stage: int | None = None,
) -> int | None:
    """Pick the PDTIA gain stage whose configured power window covers *power_W*.

    *limits* maps gain stage to an inclusive ``(min_W, max_W)`` window — see
    ``pdtia.gain_auto_switch_power_W`` in config.json. Returns None if *limits*
    is empty.

    *current_stage* is kept whenever its own window still covers *power_W*,
    so a reading that sits in the overlap of two adjacent windows doesn't
    flap the gain back and forth. When several other windows match, the
    lowest gain stage (least amplification, least saturation risk) wins.
    When no window contains *power_W*, the stage whose window is nearest is
    chosen.
    """
    if not limits:
        return None
    if current_stage is not None and current_stage in limits:
        lo, hi = limits[current_stage]
        if lo <= power_W <= hi:
            return current_stage

    matches = [stage for stage, (lo, hi) in limits.items() if lo <= power_W <= hi]
    if matches:
        return min(matches)

    def _distance(stage: int) -> float:
        lo, hi = limits[stage]
        return lo - power_W if power_W < lo else power_W - hi

    return min(limits, key=_distance)


def load_gain_power_limits(config: dict) -> dict[int, tuple[float, float]]:
    """Parse ``pdtia.gain_auto_switch_power_W`` out of an already-loaded config dict.

    Expected shape: ``{"pdtia": {"gain_auto_switch_power_W": {"1": {"min": .., "max": ..}, ...}}}``.
    Malformed entries (bad stage key, missing/non-numeric min or max) are skipped.
    Takes the config dict rather than reading config.json itself, keeping this
    module free of file I/O.
    """
    raw = config.get("pdtia", {}).get("gain_auto_switch_power_W", {})
    limits: dict[int, tuple[float, float]] = {}
    for key, bounds in raw.items():
        try:
            limits[int(key)] = (float(bounds["min"]), float(bounds["max"]))
        except (KeyError, TypeError, ValueError):
            continue
    return limits


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
