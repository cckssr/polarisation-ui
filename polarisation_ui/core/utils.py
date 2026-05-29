"""Core utilities — pure Python, no Qt or I/O dependencies."""

import math
from collections.abc import Sequence


def circular_mean_deg(angles: Sequence[float]) -> float:
    """Calculate circular mean for a sequence of angles in degrees.

    Arithmetic mean is wrong near the 0°/360° wrap (e.g. mean([359°, 1°])
    gives 180° instead of 0°). Uses atan2 of the mean sin/cos components.

    Args:
        angles: Non-empty sequence of angles in degrees.

    Returns:
        Mean angle in [0°, 360°).
    """
    n = len(angles)
    sin_sum = sum(math.sin(math.radians(a)) for a in angles)
    cos_sum = sum(math.cos(math.radians(a)) for a in angles)
    return math.degrees(math.atan2(sin_sum / n, cos_sum / n)) % 360
