"""Tests for core.formatting — central display/export formatting policy.

Pure-function tests — no filesystem or Qt involved.  ``init_from_config``
mutates module-level singletons, so every test that touches it resets state
via the ``reset_formatting_state`` fixture to avoid leaking overrides across
tests.
"""

import pytest

from polarisation_ui.core import formatting
from polarisation_ui.core.formatting import (
    DisplayFormat,
    ExportFormat,
    export_angle,
    export_intensity,
    export_voltage,
    fmt_angle,
    fmt_intensity,
    fmt_stat,
    fmt_voltage,
    get_display_format,
    get_export_format,
    init_from_config,
)


@pytest.fixture(autouse=True)
def reset_formatting_state():
    """Restore module-level singletons to their defaults after each test."""
    yield
    formatting._display = DisplayFormat()
    formatting._export = ExportFormat()


class TestDefaults:
    def test_display_format_defaults(self):
        df = DisplayFormat()
        assert df.angle_dp == 2
        assert df.voltage_dp == 4
        assert df.intensity_dp == 4
        assert df.stats_dp == 2
        assert df.angle_unit == "°"
        assert df.voltage_unit == "V"
        assert df.intensity_unit == "a.u."

    def test_export_format_defaults(self):
        ef = ExportFormat()
        assert ef.angle_dp == 4
        assert ef.voltage_dp == 6
        assert ef.intensity_dp == 6

    def test_get_display_format_returns_current_singleton(self):
        assert get_display_format() == DisplayFormat()

    def test_get_export_format_returns_current_singleton(self):
        assert get_export_format() == ExportFormat()


class TestNonePlaceholder:
    def test_fmt_angle_none(self):
        assert fmt_angle(None) == "–"

    def test_fmt_voltage_none(self):
        assert fmt_voltage(None) == "–"

    def test_fmt_intensity_none(self):
        assert fmt_intensity(None) == "–"

    def test_fmt_stat_none(self):
        assert fmt_stat(None) == "–"


class TestExactOutput:
    def test_fmt_angle_known_value(self):
        assert fmt_angle(12.3456) == "12.35"

    def test_fmt_voltage_known_value(self):
        assert fmt_voltage(1.234567) == "1.2346"

    def test_fmt_intensity_known_value(self):
        assert fmt_intensity(0.98765) == "0.9877"

    def test_fmt_stat_known_value(self):
        assert fmt_stat(3.14159) == "3.14"

    def test_export_angle_known_value(self):
        assert export_angle(12.3456789) == "12.3457"

    def test_export_voltage_known_value(self):
        assert export_voltage(1.23456789) == "1.234568"

    def test_export_intensity_known_value(self):
        assert export_intensity(0.987654321) == "0.987654"

    def test_fmt_angle_negative_value(self):
        assert fmt_angle(-4.5) == "-4.50"

    def test_fmt_angle_zero(self):
        assert fmt_angle(0.0) == "0.00"


class TestInitFromConfig:
    def test_overrides_all_display_fields(self):
        init_from_config(
            {
                "display_format": {
                    "angle_dp": 1,
                    "voltage_dp": 3,
                    "intensity_dp": 5,
                    "stats_dp": 0,
                    "angle_unit": "deg",
                    "voltage_unit": "mV",
                    "intensity_unit": "counts",
                }
            }
        )
        df = get_display_format()
        assert df.angle_dp == 1
        assert df.voltage_dp == 3
        assert df.intensity_dp == 5
        assert df.stats_dp == 0
        assert df.angle_unit == "deg"
        assert df.voltage_unit == "mV"
        assert df.intensity_unit == "counts"

    def test_overrides_all_export_fields(self):
        init_from_config(
            {
                "export_format": {
                    "angle_dp": 8,
                    "voltage_dp": 1,
                    "intensity_dp": 2,
                }
            }
        )
        ef = get_export_format()
        assert ef.angle_dp == 8
        assert ef.voltage_dp == 1
        assert ef.intensity_dp == 2

    def test_partial_display_override_keeps_other_defaults(self):
        init_from_config({"display_format": {"angle_dp": 3}})
        df = get_display_format()
        assert df.angle_dp == 3
        # Untouched fields keep their dataclass defaults.
        assert df.voltage_dp == 4
        assert df.intensity_dp == 4
        assert df.stats_dp == 2
        assert df.angle_unit == "°"

    def test_partial_export_override_keeps_other_defaults(self):
        init_from_config({"export_format": {"voltage_dp": 2}})
        ef = get_export_format()
        assert ef.voltage_dp == 2
        assert ef.angle_dp == 4
        assert ef.intensity_dp == 6

    def test_empty_config_falls_back_to_defaults(self):
        init_from_config({})
        assert get_display_format() == DisplayFormat()
        assert get_export_format() == ExportFormat()

    def test_missing_keys_entirely_falls_back_to_defaults(self):
        init_from_config({"some_other_key": {"foo": "bar"}})
        assert get_display_format() == DisplayFormat()
        assert get_export_format() == ExportFormat()

    def test_override_affects_fmt_functions(self):
        init_from_config({"display_format": {"angle_dp": 0}})
        assert fmt_angle(12.6) == "13"

    def test_override_affects_export_functions(self):
        init_from_config({"export_format": {"angle_dp": 1}})
        assert export_angle(12.34) == "12.3"
