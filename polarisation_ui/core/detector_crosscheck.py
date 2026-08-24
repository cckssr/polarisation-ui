"""Dual-power-meter cross-check.

Before trusting a PM400 as the detector-arm reference for PD-TIA calibration,
swap in a second identical PM400 and confirm both meters agree across the
full ND-filter range. This module evaluates that comparison; the sweep that
produces the raw points lives in
``polarisation_ui.infrastructure.qt_threads.DetectorCrossCheckWorker``.

Pure Python — no PySide6, no Qt, no hardware I/O.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DetectorComparisonPoint:
    """One simultaneous reading from both power meters at a given ND position."""

    position: float
    """Actuator level (mm for the ND stage) at which both readings were taken."""
    power_a_W: float
    """Reference meter (behind the beamsplitter, unchanged)."""
    power_b_W: float
    """Meter under test (temporarily replacing the PD-TIA detector)."""

    @property
    def ratio_b_over_a(self) -> float | None:
        """Return power_b / power_a, or None if power_a is zero."""
        if self.power_a_W == 0:
            return None
        return self.power_b_W / self.power_a_W


@dataclass(frozen=True)
class DetectorComparisonResult:
    """Aggregate statistics for a dual-power-meter cross-check run."""

    points: tuple[DetectorComparisonPoint, ...]
    mean_ratio: float
    ratio_spread_pct: float
    """``(max_ratio - min_ratio) / mean_ratio * 100`` across all valid points."""
    slope_W_per_W: float
    """Zero-intercept least-squares slope of power_b vs power_a."""
    r_squared: float
    worst_deviation_pct: float
    """Largest |ratio - mean_ratio| / mean_ratio * 100 across all valid points."""
    tolerance_pct: float
    passed: bool

    def to_json_dict(self) -> dict:
        """Return a JSON-serialisable summary (aggregate stats, not the raw points)."""
        return {
            "mean_ratio": self.mean_ratio,
            "ratio_spread_pct": self.ratio_spread_pct,
            "slope_W_per_W": self.slope_W_per_W,
            "r_squared": self.r_squared,
            "worst_deviation_pct": self.worst_deviation_pct,
            "tolerance_pct": self.tolerance_pct,
            "passed": self.passed,
            "points": [
                {"position": p.position, "power_a_W": p.power_a_W, "power_b_W": p.power_b_W}
                for p in self.points
            ],
        }


def evaluate_detector_comparison(
    points: list[DetectorComparisonPoint],
    tolerance_pct: float = 5.0,
) -> DetectorComparisonResult:
    """Compute agreement statistics between two power meters from paired readings.

    Args:
        points: simultaneous (power_a, power_b) readings across the scanned range.
        tolerance_pct: maximum allowed ratio deviation from the mean for the
            run to be considered a pass.

    Returns:
        DetectorComparisonResult with mean ratio, spread, a zero-intercept
        linear fit of B vs A, and a pass/fail verdict.

    Raises:
        ValueError: fewer than 2 points, or no point has a nonzero power_a_W.
    """
    if len(points) < 2:
        raise ValueError("evaluate_detector_comparison requires at least 2 points")

    ratios = [p.ratio_b_over_a for p in points]
    valid_ratios = [r for r in ratios if r is not None]
    if not valid_ratios:
        raise ValueError("no point has a nonzero power_a_W reading")

    mean_ratio = sum(valid_ratios) / len(valid_ratios)
    max_ratio = max(valid_ratios)
    min_ratio = min(valid_ratios)
    ratio_spread_pct = (
        (max_ratio - min_ratio) / mean_ratio * 100.0 if mean_ratio != 0 else float("inf")
    )
    worst_deviation_pct = (
        max(abs(r - mean_ratio) / mean_ratio * 100.0 for r in valid_ratios)
        if mean_ratio != 0
        else float("inf")
    )

    slope, r_squared = _zero_intercept_fit(points)

    passed = worst_deviation_pct <= tolerance_pct

    return DetectorComparisonResult(
        points=tuple(points),
        mean_ratio=mean_ratio,
        ratio_spread_pct=ratio_spread_pct,
        slope_W_per_W=slope,
        r_squared=r_squared,
        worst_deviation_pct=worst_deviation_pct,
        tolerance_pct=tolerance_pct,
        passed=passed,
    )


def _zero_intercept_fit(points: list[DetectorComparisonPoint]) -> tuple[float, float]:
    """Zero-intercept least-squares slope (B = slope * A) and its R².

    R² here is computed against the zero-intercept model, not the usual
    mean-centred model — the natural choice when the fit itself has no
    intercept term.
    """
    xs = [p.power_a_W for p in points]
    ys = [p.power_b_W for p in points]
    sum_xx = sum(x * x for x in xs)
    if sum_xx == 0:
        return 0.0, 0.0
    slope = sum(x * y for x, y in zip(xs, ys, strict=True)) / sum_xx

    ss_res = sum((y - slope * x) ** 2 for x, y in zip(xs, ys, strict=True))
    ss_tot = sum(y * y for y in ys)
    r_squared = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0

    return slope, r_squared
