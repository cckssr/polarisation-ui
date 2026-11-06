"""Linearity analysis for a rotary variable ND filter.

An axial variable ND filter is specified to have an optical density that is
linear in the wheel angle, ``OD(θ) = -log10(P(θ) / P_ref) = a·θ + b``. This
module quantifies how well a measured filter follows that law and how
reproducible repeated scans are:

* **Linearity** of one scan — slope, RMS and maximum deviation of OD from the
  best straight line (in OD, and as the equivalent relative transmission error).
* **Repeatability** across several scans — per-position scatter of OD, spread
  of the slope, and the forward-vs-backward offset (hysteresis / backlash),
  also expressed as an angle error.

All scans of one report share a common reference power, so a source drift
between scans shows up as an OD offset rather than being fitted away.

Pure Python + numpy — no PySide6, no Qt, no hardware I/O.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

FORWARD = "forward"
BACKWARD = "backward"

_MIN_FIT_POINTS = 3


@dataclass(frozen=True)
class NDLinearityScan:
    """One raw scan of the ND wheel: ``(position_deg, power_W)`` in scan order."""

    index: int
    """Zero-based position of this scan within the measurement set."""
    direction: str
    """``FORWARD`` (start → end) or ``BACKWARD`` (end → start)."""
    points: tuple[tuple[float, float], ...]


@dataclass(frozen=True)
class NDLinearityFit:
    """Straight-line fit of OD vs. angle for one scan."""

    index: int
    direction: str
    n_used: int
    """Points that entered the fit (power above the noise floor)."""
    slope_od_per_deg: float
    intercept_od: float
    rms_residual_od: float
    max_residual_od: float
    """Largest ``|OD - fit|`` over the fitted points."""
    max_residual_pos_deg: float
    positions_deg: tuple[float, ...]
    """Fitted positions, ascending."""
    od: tuple[float, ...]
    residuals_od: tuple[float, ...]
    """``OD - fit`` for each fitted position (same order as ``positions_deg``)."""

    @property
    def max_residual_pct(self) -> float:
        """Largest transmission error relative to the fit, in percent."""
        return (10.0**self.max_residual_od - 1.0) * 100.0


@dataclass(frozen=True)
class NDLinearityReport:
    """Per-scan fits plus the cross-scan comparison."""

    reference_power_W: float
    fits: tuple[NDLinearityFit, ...]
    slope_mean_od_per_deg: float
    slope_std_od_per_deg: float
    """Sample std of the slope across scans; 0 for a single scan."""
    od_scatter_mean: float | None
    """Mean over positions of the across-scan OD std; ``None`` for one scan."""
    od_scatter_max: float | None
    hysteresis_od: float | None
    """Mean ``|OD_forward - OD_backward|`` over shared positions; ``None`` unless
    the set holds both directions."""
    hysteresis_deg: float | None
    """``hysteresis_od`` divided by ``|slope|`` — the equivalent angle error."""


def fit_linearity(
    scan: NDLinearityScan,
    reference_power_W: float,
    noise_floor_W: float = 0.0,
) -> NDLinearityFit:
    """Fit ``OD = a·θ + b`` to one scan.

    Args:
        scan: the raw scan.
        reference_power_W: power that defines OD = 0.
        noise_floor_W: points with power at or below this are ignored (they sit
            in sensor noise, where the logarithm is meaningless). Non-positive
            powers are always ignored.

    Raises:
        ValueError: fewer than 3 usable points, or a non-positive reference.
    """
    if reference_power_W <= 0.0:
        raise ValueError("reference power must be positive")
    floor = max(noise_floor_W, 0.0)
    used = sorted(
        (pos, power)
        for pos, power in scan.points
        if math.isfinite(power) and power > floor and power > 0.0
    )
    if len(used) < _MIN_FIT_POINTS:
        raise ValueError(
            f"scan {scan.index + 1}: only {len(used)} point(s) above the noise floor "
            f"(need {_MIN_FIT_POINTS})"
        )
    pos = np.array([u[0] for u in used], dtype=float)
    od = -np.log10(np.array([u[1] for u in used], dtype=float) / reference_power_W)
    slope, intercept = np.polyfit(pos, od, 1)
    resid = od - (slope * pos + intercept)
    worst = int(np.argmax(np.abs(resid)))
    return NDLinearityFit(
        index=scan.index,
        direction=scan.direction,
        n_used=len(used),
        slope_od_per_deg=float(slope),
        intercept_od=float(intercept),
        rms_residual_od=float(np.sqrt(np.mean(resid**2))),
        max_residual_od=float(abs(resid[worst])),
        max_residual_pos_deg=float(pos[worst]),
        positions_deg=tuple(float(x) for x in pos),
        od=tuple(float(x) for x in od),
        residuals_od=tuple(float(x) for x in resid),
    )


def analyse_linearity_set(
    scans: list[NDLinearityScan],
    noise_floor_W: float = 0.0,
) -> NDLinearityReport:
    """Fit every scan and compare them.

    The common reference power is the largest power above the noise floor in
    any scan. Scans that cannot be fitted (too few usable points) raise
    ``ValueError``.
    """
    if not scans:
        raise ValueError("analyse_linearity_set requires at least one scan")
    floor = max(noise_floor_W, 0.0)
    usable = [p for s in scans for _, p in s.points if math.isfinite(p) and p > floor and p > 0.0]
    if not usable:
        raise ValueError("no scan point is above the noise floor")
    ref = max(usable)
    fits = tuple(fit_linearity(s, ref, floor) for s in scans)

    slopes = np.array([f.slope_od_per_deg for f in fits])
    slope_std = float(np.std(slopes, ddof=1)) if len(fits) > 1 else 0.0

    scatter_mean: float | None = None
    scatter_max: float | None = None
    hyst_od: float | None = None
    hyst_deg: float | None = None
    if len(fits) > 1:
        grid, curves = _common_grid(fits)
        if grid.size:
            scatter = np.std(curves, axis=0, ddof=1)
            scatter_mean = float(np.mean(scatter))
            scatter_max = float(np.max(scatter))
            fwd = [c for c, f in zip(curves, fits, strict=True) if f.direction == FORWARD]
            bwd = [c for c, f in zip(curves, fits, strict=True) if f.direction == BACKWARD]
            if fwd and bwd:
                diff = np.mean(fwd, axis=0) - np.mean(bwd, axis=0)
                hyst_od = float(np.mean(np.abs(diff)))
                mean_slope = abs(float(np.mean(slopes)))
                hyst_deg = hyst_od / mean_slope if mean_slope > 0.0 else None

    return NDLinearityReport(
        reference_power_W=ref,
        fits=fits,
        slope_mean_od_per_deg=float(np.mean(slopes)),
        slope_std_od_per_deg=slope_std,
        od_scatter_mean=scatter_mean,
        od_scatter_max=scatter_max,
        hysteresis_od=hyst_od,
        hysteresis_deg=hyst_deg,
    )


def _common_grid(fits: tuple[NDLinearityFit, ...]) -> tuple[np.ndarray, np.ndarray]:
    """Resample every fit's OD onto the positions all scans cover.

    Returns ``(grid, curves)`` with ``curves`` shaped ``(n_scans, n_grid)``. The
    grid is the first scan's positions inside the overlap of all scans.
    """
    lo = max(f.positions_deg[0] for f in fits)
    hi = min(f.positions_deg[-1] for f in fits)
    grid = np.array([p for p in fits[0].positions_deg if lo <= p <= hi], dtype=float)
    if grid.size == 0:
        return grid, np.empty((len(fits), 0))
    curves = np.array([np.interp(grid, f.positions_deg, f.od) for f in fits])
    return grid, curves
