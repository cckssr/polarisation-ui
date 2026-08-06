"""Central display and export formatting policy.

All numeric-to-string conversions for the UI go through this module so that
decimal places and units are consistent everywhere.  Defaults are read from
config.json under the "display_format" / "export_format" keys and can be
overridden there without touching code.

Usage:
    from polarisation_ui.core.formatting import fmt_angle, fmt_voltage, fmt_intensity
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class DisplayFormat:
    """Decimal-place and unit policy for on-screen (live) readouts."""

    angle_dp: int = 2
    voltage_dp: int = 4
    intensity_dp: int = 4
    stats_dp: int = 2
    angle_unit: str = "°"
    voltage_unit: str = "V"
    intensity_unit: str = "a.u."


@dataclass(frozen=True)
class ExportFormat:
    """Decimal-place policy for CSV/file export."""

    angle_dp: int = 4
    voltage_dp: int = 6
    intensity_dp: int = 6


# Module-level singletons — replaced by init_from_config() at app startup.
_display = DisplayFormat()
_export = ExportFormat()

_PLACEHOLDER = "–"


def init_from_config(config: dict) -> None:
    """Apply display/export format overrides from config dict ("display_format" key)."""
    global _display, _export
    df = config.get("display_format", {})
    ef = config.get("export_format", {})
    _display = DisplayFormat(
        angle_dp=int(df.get("angle_dp", _display.angle_dp)),
        voltage_dp=int(df.get("voltage_dp", _display.voltage_dp)),
        intensity_dp=int(df.get("intensity_dp", _display.intensity_dp)),
        stats_dp=int(df.get("stats_dp", _display.stats_dp)),
        angle_unit=str(df.get("angle_unit", _display.angle_unit)),
        voltage_unit=str(df.get("voltage_unit", _display.voltage_unit)),
        intensity_unit=str(df.get("intensity_unit", _display.intensity_unit)),
    )
    _export = ExportFormat(
        angle_dp=int(ef.get("angle_dp", _export.angle_dp)),
        voltage_dp=int(ef.get("voltage_dp", _export.voltage_dp)),
        intensity_dp=int(ef.get("intensity_dp", _export.intensity_dp)),
    )


def fmt_angle(value: float | None) -> str:
    """Format angle for display (default 2 dp). Returns '–' for None."""
    if value is None:
        return _PLACEHOLDER
    return f"{value:.{_display.angle_dp}f}"


def fmt_voltage(value: float | None) -> str:
    """Format voltage for display (default 4 dp). Returns '–' for None."""
    if value is None:
        return _PLACEHOLDER
    return f"{value:.{_display.voltage_dp}f}"


def fmt_intensity(value: float | None) -> str:
    """Format intensity/ADC reading for display (default 4 dp). Returns '–' for None."""
    if value is None:
        return _PLACEHOLDER
    return f"{value:.{_display.intensity_dp}f}"


def fmt_stat(value: float | None) -> str:
    """Format a statistics value for display (default 2 dp). Returns '–' for None."""
    if value is None:
        return _PLACEHOLDER
    return f"{value:.{_display.stats_dp}f}"


def export_angle(value: float) -> str:
    """Format angle for CSV export (default 4 dp)."""
    return f"{value:.{_export.angle_dp}f}"


def export_voltage(value: float) -> str:
    """Format voltage for CSV export (default 6 dp)."""
    return f"{value:.{_export.voltage_dp}f}"


def export_intensity(value: float) -> str:
    """Format intensity for CSV export (default 6 dp)."""
    return f"{value:.{_export.intensity_dp}f}"


def get_display_format() -> DisplayFormat:
    """Return the currently active DisplayFormat."""
    return _display


def get_export_format() -> ExportFormat:
    """Return the currently active ExportFormat."""
    return _export
