"""Shared display-formatting helpers for angles, voltages, and intensity values.

All functions return formatted strings ready for display. They live in core
so that UI widgets and export code use identical representations.
"""


def fmt_angle(value: float) -> str:
    """Format an encoder angle to 2 decimal places with degree symbol."""
    return f"{value:.2f}°"


def fmt_voltage(value: float) -> str:
    """Format an ADC voltage to 4 decimal places with unit."""
    return f"{value:.4f} V"


def fmt_intensity(value: float) -> str:
    """Format a normalised intensity value to 4 decimal places."""
    return f"{value:.4f}"
