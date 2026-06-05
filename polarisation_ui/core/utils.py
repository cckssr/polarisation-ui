"""Core utilities — pure Python, no Qt or I/O dependencies."""

import math
from collections.abc import Sequence


def linear_angle_grid(start: float, end: float, n: int) -> list[float]:
    """Return *n* evenly-spaced angles from *start* to *end* (inclusive).

    Args:
        start: First angle in degrees.
        end:   Last angle in degrees.
        n:     Number of points (must be >= 2).

    Returns:
        List of *n* angles.

    Raises:
        ValueError: if *n* < 2.
    """
    if n < 2:
        raise ValueError("linear_angle_grid requires n >= 2")
    step = (end - start) / (n - 1)
    return [start + i * step for i in range(n)]


def circular_mean_deg(angles: Sequence[float]) -> float:
    """Calculate circular mean for a sequence of angles in degrees.

    Arithmetic mean is wrong near the 0°/360° wrap (e.g. mean([359°, 1°])
    gives 180° instead of 0°). Uses atan2 of the mean sin/cos components.

    Args:
        angles: Non-empty sequence of angles in degrees.

    Returns:
        Mean angle in [0°, 360°).

    Raises:
        ValueError: if *angles* is empty.
    """
    n = len(angles)
    if n == 0:
        raise ValueError("circular_mean_deg requires a non-empty sequence")
    sin_sum = sum(math.sin(math.radians(a)) for a in angles)
    cos_sum = sum(math.cos(math.radians(a)) for a in angles)
    return math.degrees(math.atan2(sin_sum / n, cos_sum / n)) % 360
