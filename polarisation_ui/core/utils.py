"""Core utilities — pure Python, no Qt or I/O dependencies."""

import math
from collections.abc import Sequence

from polarisation_ui.core.models import Frame


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


def windowed_average_intensity(
    frames: Sequence[Frame], window_ms: int
) -> tuple[float, Frame | None]:
    """Average ``Frame.intensity`` over the trailing *window_ms* ending at the latest frame.

    Shared by tabs that support a manual "confirm point" workflow (Malus,
    Waveplate): a point's intensity is the mean of recent non-NaN readings
    rather than a single noisy sample. Frames are assumed to be already
    time-ordered (oldest first), as they are in each tab's ring buffer.

    Args:
        frames: Time-ordered frames (typically a small ring buffer); may be empty.
        window_ms: Trailing window width in milliseconds, measured back from
            the latest frame's ``ts_ms``.

    Returns:
        ``(nan, None)`` if *frames* is empty; ``(nan, latest)`` if every frame
        in the window has a NaN intensity; otherwise ``(mean, latest)``.
    """
    if not frames:
        return float("nan"), None
    latest = frames[-1]
    cutoff_ms = latest.ts_ms - window_ms
    valid = [f.intensity for f in frames if f.ts_ms >= cutoff_ms and not math.isnan(f.intensity)]
    if not valid:
        return float("nan"), latest
    return sum(valid) / len(valid), latest
