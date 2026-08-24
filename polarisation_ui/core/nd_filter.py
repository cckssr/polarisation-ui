"""Gradient ND-filter range calibration.

A gradient neutral-density filter mounted on a linear stage varies beam
intensity by position rather than by polarisation angle. Before it can be
used as an intensity actuator, its usable travel must be calibrated from a
power-meter scan: the "clear" end (maximum transmission) and the "dark" end
(minimum transmission, or the point where transmission drops into sensor
noise).

Pure Python — no PySide6, no Qt, no hardware I/O.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class NDFilterRange:
    """Calibrated usable travel of a gradient ND filter."""

    pos_clear_mm: float
    """Position of maximum transmission (innermost edge of the clear plateau)."""
    pos_dark_mm: float
    """Position of minimum transmission."""
    power_clear_W: float
    power_dark_W: float
    dynamic_range_dB: float
    monotonic: bool
    """False when the scan is not monotonic between the two ends — a sign of
    a misaligned wedge, beam clipping, or a filter mounted the wrong way
    round. Callers should warn the user rather than trust the range."""
    scan_points: tuple[tuple[float, float], ...]
    """The raw (position_mm, power_W) scan, in scan order."""

    def to_json_dict(self) -> dict:
        """Return a JSON-serialisable summary (not the raw scan — see scan_points)."""
        return {
            "pos_clear_mm": self.pos_clear_mm,
            "pos_dark_mm": self.pos_dark_mm,
            "power_clear_W": self.power_clear_W,
            "power_dark_W": self.power_dark_W,
            "dynamic_range_dB": self.dynamic_range_dB,
            "monotonic": self.monotonic,
        }


def analyse_nd_scan(
    points: list[tuple[float, float]],
    plateau_frac: float = 0.01,
    dark_floor_W: float | None = None,
) -> NDFilterRange:
    """Derive the usable ND-filter range from a raw position/power scan.

    Args:
        points: ``(position_mm, power_W)`` pairs in scan order (either
            travel direction; at least 2 points required).
        plateau_frac: fraction of peak power that defines the "clear"
            plateau. ``pos_clear_mm`` is the position closest to the dark end
            that still has power >= ``(1 - plateau_frac) * power_max`` — the
            *innermost* edge of the plateau, so a flat clear-aperture region
            doesn't push the end stop out into unused travel.
        dark_floor_W: if given, ``pos_dark_mm`` is the first scan position
            (walking from the clear end towards the dark end) whose power is
            at or below this floor, rather than the position of the raw
            minimum — avoids parking the stage in sensor noise where the
            "minimum" reading is meaningless.

    Returns:
        NDFilterRange summarising the calibrated ends and dynamic range.

    Raises:
        ValueError: fewer than 2 points given.
    """
    if len(points) < 2:
        raise ValueError("analyse_nd_scan requires at least 2 scan points")

    powers = [p for _, p in points]
    power_max = max(powers)
    power_min = min(powers)
    max_idx = powers.index(power_max)
    pos_at_max = points[max_idx][0]

    # Walk outward from the peak towards increasing distance, in scan order,
    # to find the innermost edge of the clear plateau.
    threshold = (1.0 - plateau_frac) * power_max
    pos_clear_mm = pos_at_max
    # Order points by distance from the peak position so "walking outward"
    # is well defined regardless of scan direction.
    ordered = sorted(points, key=lambda pt: abs(pt[0] - pos_at_max))
    for pos, power in ordered:
        if power >= threshold:
            pos_clear_mm = pos
        else:
            break

    # Dark end: walk from the clear end towards the far end of the scan,
    # in the position order the scan was actually taken in.
    sorted_by_pos = sorted(points, key=lambda pt: pt[0])
    if pos_clear_mm == sorted_by_pos[0][0]:
        walk = sorted_by_pos
    else:
        walk = list(reversed(sorted_by_pos))

    pos_dark_mm = walk[-1][0]
    power_dark_W = walk[-1][1]
    if dark_floor_W is not None:
        for pos, power in walk:
            if power <= dark_floor_W:
                pos_dark_mm = pos
                power_dark_W = power
                break
    else:
        power_dark_W = power_min
        pos_dark_mm = points[powers.index(power_min)][0]

    power_clear_W = power_max

    dynamic_range_dB = (
        10.0 * math.log10(power_clear_W / power_dark_W)
        if power_dark_W > 0 and power_clear_W > 0
        else float("inf")
    )

    monotonic = _is_monotonic_between(points, pos_clear_mm, pos_dark_mm)

    return NDFilterRange(
        pos_clear_mm=pos_clear_mm,
        pos_dark_mm=pos_dark_mm,
        power_clear_W=power_clear_W,
        power_dark_W=power_dark_W,
        dynamic_range_dB=dynamic_range_dB,
        monotonic=monotonic,
        scan_points=tuple(points),
    )


def _is_monotonic_between(points: list[tuple[float, float]], pos_a: float, pos_b: float) -> bool:
    """Return whether power is non-increasing when walking from *pos_a* to *pos_b*."""
    lo, hi = sorted((pos_a, pos_b))
    segment = sorted((p for p in points if lo <= p[0] <= hi), key=lambda pt: pt[0])
    if len(segment) < 2:
        return True
    if pos_a > pos_b:
        segment = list(reversed(segment))
    powers = [p for _, p in segment]
    # Allow small non-monotonic wiggle from measurement noise.
    tolerance = 0.02 * max(powers)
    for prev, cur in zip(powers, powers[1:], strict=False):
        if cur > prev + tolerance:
            return False
    return True
