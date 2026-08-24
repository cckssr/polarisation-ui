"""Automatic power calibration — settings and angle-grid builder.

Stores connection parameters (KDC101, PM400, beamsplitter attenuation) as a
JSON sidecar at ~/.config/polarisation-ui/auto_calibration_settings.json so
they survive application restarts.  Sweep parameters (AutoCalibrationParams)
are kept in memory only; they are filled from the dialog widgets each run.

No Qt, no hardware I/O.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

from .utils import interp_monotonic, linear_angle_grid

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
    nd_stage_conn_id: str = ""
    """KDC101 connection id for the ND-filter linear stage (MTS50/M-Z8)."""
    pm400_b_visa_resource: str = ""
    """VISA resource of the second PM400 used for the detector cross-check."""
    nd_pos_clear_mm: float | None = None
    """Calibrated ND-stage position of maximum transmission, from the range scan."""
    nd_pos_dark_mm: float | None = None
    """Calibrated ND-stage position of minimum transmission, from the range scan."""
    nd_power_clear_W: float | None = None
    nd_power_dark_W: float | None = None
    nd_calibrated_at: str = ""
    """ISO-8601 timestamp of the last successful ND-range scan, or "" if none yet."""

    def save(self, path: Path = _SETTINGS_PATH) -> None:
        """Write these settings to *path* as JSON, creating parent directories as needed."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as fh:
            json.dump(asdict(self), fh, indent=2)

    @classmethod
    def load(cls, path: Path = _SETTINGS_PATH) -> AutoCalibrationConnectionSettings:
        """Load settings from *path*, or return defaults if the file doesn't exist."""
        if not path.exists():
            return cls()
        try:
            with path.open("r", encoding="utf-8") as fh:
                data = json.load(fh)

            def _opt_float(key: str) -> float | None:
                value = data.get(key)
                return None if value is None else float(value)

            return cls(
                kdc101_conn_id=str(data.get("kdc101_conn_id", "")),
                pm400_visa_resource=str(data.get("pm400_visa_resource", "")),
                beamsplitter_attenuation_dB=float(data.get("beamsplitter_attenuation_dB", 0.0)),
                wavelength_nm=float(data.get("wavelength_nm", 633.0)),
                angle_offset_deg=float(data.get("angle_offset_deg", 0.0)),
                nd_stage_conn_id=str(data.get("nd_stage_conn_id", "")),
                pm400_b_visa_resource=str(data.get("pm400_b_visa_resource", "")),
                nd_pos_clear_mm=_opt_float("nd_pos_clear_mm"),
                nd_pos_dark_mm=_opt_float("nd_pos_dark_mm"),
                nd_power_clear_W=_opt_float("nd_power_clear_W"),
                nd_power_dark_W=_opt_float("nd_power_dark_W"),
                nd_calibrated_at=str(data.get("nd_calibrated_at", "")),
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
    margin below clipping.
    """
    intensity_source: Literal["polariser", "nd_filter"] = "polariser"
    """Which actuator the sweep drives — see infrastructure/devices/intensity_actuator.py."""
    power_grid_mode: Literal["log_power", "linear_power"] = "log_power"
    """Only used when intensity_source == "nd_filter" — see build_power_grid()."""
    nd_scan_points: tuple[tuple[float, float], ...] = ()
    """The calibrated ND range scan (position_mm, power_W), used to invert target
    powers to stage positions. Required when intensity_source == "nd_filter"."""
    power_tolerance_pct: float = 5.0
    """Max allowed |achieved - target| / target for an ND-mode sweep point before
    the worker bisects to refine the position (see max_refine_steps)."""
    max_refine_steps: int = 2
    """Max bisection refinement moves per ND-mode sweep point."""


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
        return linear_angle_grid(a0, a1, n)

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


def build_power_grid(
    p_hi_W: float,
    p_lo_W: float,
    n: int,
    mode: Literal["log_power", "linear_power"] = "log_power",
) -> list[float]:
    """Return *n* target powers from *p_hi_W* down to *p_lo_W*.

    ``log_power`` (default): geometric spacing — equal ratio between
    consecutive targets. The right choice for a gradient ND filter, whose
    transmission is exponential in position, so this gives roughly equal
    point density (in dB) across the whole dynamic range instead of
    clustering points near the bright end.

    ``linear_power``: equal absolute-power steps.

    Args:
        p_hi_W: First (highest) target power.
        p_lo_W: Last (lowest) target power.
        n: Number of points (clamped to >= 2).
        mode: Spacing mode.

    Returns:
        List of *n* target powers, descending (or ascending, if
        ``p_lo_W > p_hi_W``) from *p_hi_W* to *p_lo_W*.

    Raises:
        ValueError: ``mode == "log_power"`` and either power is <= 0.
    """
    n = max(n, 2)
    if mode == "linear_power":
        step = (p_lo_W - p_hi_W) / (n - 1)
        return [p_hi_W + i * step for i in range(n)]

    if p_hi_W <= 0 or p_lo_W <= 0:
        raise ValueError("build_power_grid(mode='log_power') requires positive powers")
    log_hi = math.log10(p_hi_W)
    log_lo = math.log10(p_lo_W)
    log_step = (log_lo - log_hi) / (n - 1)
    return [10 ** (log_hi + i * log_step) for i in range(n)]


def positions_for_target_powers(
    targets_W: list[float],
    scan_points: list[tuple[float, float]] | tuple[tuple[float, float], ...],
) -> list[float]:
    """Invert a calibrated ND-filter position/power scan to reach *targets_W*.

    *scan_points* is a raw ``(position_mm, power_W)`` scan — typically
    ``NDFilterRange.scan_points`` from ``core.nd_filter.analyse_nd_scan``.
    Interpolation is monotonic-in-power (the scan is sorted by power before
    inverting), so a non-monotonic scan gives an approximate but well-defined
    result rather than raising. Targets outside the scanned power range are
    clamped to the nearest end position.

    Raises:
        ValueError: *scan_points* is empty.
    """
    if not scan_points:
        raise ValueError("positions_for_target_powers requires a non-empty scan")
    ordered = sorted(scan_points, key=lambda pt: pt[1])
    powers = [p for _, p in ordered]
    positions = [x for x, _ in ordered]
    return [interp_monotonic(target, powers, positions) for target in targets_W]
