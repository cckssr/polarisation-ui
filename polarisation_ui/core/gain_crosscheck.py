"""Post-calibration gain-switch consistency verification.

Once every PD-TIA gain stage has its own (voltage, power) calibration, this
module checks that they agree: at a handful of fixed optical-power levels
inside the overlap of adjacent gain windows, every stage should report
(after applying its own calibration) close to the same watts. Large spread
means the per-gain calibrations disagree with each other even though each
one individually looks fine in isolation.

Pure Python — no PySide6, no Qt, no hardware I/O.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GainCrossCheckLevel:
    """One test level: a fixed actuator position, measured through every stage."""

    level: float
    """Actuator position (mm for the ND stage, degrees for the polariser) at
    which this level was measured."""
    pm_power_W: float
    """Reference PM400 reading at this level."""
    per_gain: dict[int, tuple[float, float]]
    """gain_stage -> (voltage_V, power_W), where power_W is that stage's own
    calibration applied to its own voltage reading. A stage that saturated or
    was skipped at this level is simply absent from this dict."""


@dataclass(frozen=True)
class GainCrossCheckResult:
    """Aggregate statistics for a gain-switch consistency run."""

    levels: tuple[GainCrossCheckLevel, ...]
    worst_spread_pct: float
    """Largest ``(max_W - min_W) / mean_W * 100`` across gains, over all levels."""
    worst_pm_deviation_pct: float
    """Largest single-stage deviation from the reference PM400 reading, over all levels."""
    tolerance_pct: float
    passed: bool

    def to_json_dict(self) -> dict:
        """Return a JSON-serialisable summary for embedding in the profile JSON."""
        return {
            "worst_spread_pct": self.worst_spread_pct,
            "worst_pm_deviation_pct": self.worst_pm_deviation_pct,
            "tolerance_pct": self.tolerance_pct,
            "passed": self.passed,
            "levels": [
                {
                    "level": lvl.level,
                    "pm_power_W": lvl.pm_power_W,
                    "per_gain": {
                        str(stage): {"voltage_V": v, "power_W": w}
                        for stage, (v, w) in lvl.per_gain.items()
                    },
                }
                for lvl in self.levels
            ],
        }


def evaluate_gain_crosscheck(
    levels: list[GainCrossCheckLevel],
    tolerance_pct: float = 5.0,
) -> GainCrossCheckResult:
    """Compute cross-gain agreement statistics from a set of measured levels.

    Args:
        levels: one entry per tested actuator position, each carrying every
            gain stage's own-calibration power reading at that position.
        tolerance_pct: maximum allowed spread (between gains) and deviation
            (from the PM400 reference) for the run to pass.

    Returns:
        GainCrossCheckResult with worst-case spread, worst-case PM400
        deviation, and a pass/fail verdict.

    Raises:
        ValueError: *levels* is empty, or no level has at least 2 gain readings.
    """
    if not levels:
        raise ValueError("evaluate_gain_crosscheck requires at least one level")

    worst_spread_pct = 0.0
    worst_pm_deviation_pct = 0.0
    any_comparable = False

    for lvl in levels:
        powers = [w for _, w in lvl.per_gain.values()]
        if len(powers) >= 2:
            any_comparable = True
            mean_w = sum(powers) / len(powers)
            if mean_w != 0:
                spread_pct = (max(powers) - min(powers)) / mean_w * 100.0
                worst_spread_pct = max(worst_spread_pct, spread_pct)

        if lvl.pm_power_W != 0:
            for _, power_w in lvl.per_gain.values():
                dev_pct = abs(power_w - lvl.pm_power_W) / lvl.pm_power_W * 100.0
                worst_pm_deviation_pct = max(worst_pm_deviation_pct, dev_pct)

    if not any_comparable:
        raise ValueError(
            "evaluate_gain_crosscheck requires at least one level with 2+ gain readings"
        )

    passed = worst_spread_pct <= tolerance_pct and worst_pm_deviation_pct <= tolerance_pct

    return GainCrossCheckResult(
        levels=tuple(levels),
        worst_spread_pct=worst_spread_pct,
        worst_pm_deviation_pct=worst_pm_deviation_pct,
        tolerance_pct=tolerance_pct,
        passed=passed,
    )
