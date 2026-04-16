"""!/usr/bin/env python
Core business logic utilities - NO Qt or I/O dependencies.

This module provides pure calculation and data transformation utilities for
core domain logic. All functions are side-effect free and work with standard
Python types only.

Functions:
    calculate_statistics: Compute mean, std, min, max from numeric values.

Dependencies:
    - statistics (standard library)
"""

import math
import statistics
from collections.abc import Sequence


def calculate_statistics(values: list[float]) -> dict:
    """
    Calculate statistical measures for a list of numeric values.

    Computes summary statistics useful for analyzing measurement data.
    Returns zero values for empty input.

    Args:
        values: List of numeric values.

    Returns:
        dict: Dictionary with keys:
              - mean: Arithmetic mean
              - std: Standard deviation (0 if fewer than 2 values)
              - min: Minimum value
              - max: Maximum value
              - count: Number of values

    Examples:
        >>> calculate_statistics([1.0, 2.0, 3.0])
        {'mean': 2.0, 'std': 1.0, 'min': 1.0, 'max': 3.0, 'count': 3}
        >>> calculate_statistics([])
        {'mean': 0.0, 'std': 0.0, 'min': 0.0, 'max': 0.0, 'count': 0}
    """
    if not values:
        return {"mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0, "count": 0}

    return {
        "mean": statistics.mean(values),
        "std": statistics.stdev(values) if len(values) > 1 else 0.0,
        "min": min(values),
        "max": max(values),
        "count": len(values),
    }


def circular_mean_deg(angles: Sequence[float]) -> float:
    """
    Circular mean for a sequence of angles in degrees.

    Arithmetic mean is wrong near the 0°/360° wrap (e.g. mean([359°, 1°])
    gives 180° instead of 0°). The circular mean uses atan2 of the mean
    sin/cos components and is always correct.

    Args:
        angles: Non-empty sequence of angles in degrees.

    Returns:
        Mean angle in [0°, 360°).
    """
    n = len(angles)
    sin_sum = sum(math.sin(math.radians(a)) for a in angles)
    cos_sum = sum(math.cos(math.radians(a)) for a in angles)
    return math.degrees(math.atan2(sin_sum / n, cos_sum / n)) % 360
