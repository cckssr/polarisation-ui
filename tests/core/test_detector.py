"""Tests for core.detector.point_power — the shared per-point power derivation."""

from polarisation_ui.core.detector import DETECTOR_PDTIA, DETECTOR_PM400, point_power
from polarisation_ui.core.models import Frame


def _frame(**overrides) -> Frame:
    defaults = dict(
        ts_ms=0,
        sample_angle=0.0,
        detector_angle=0.0,
        intensity=0.5,
        pdtia_gain=2,
        power_W=None,
        conv_factor_W_per_V=None,
        detector=DETECTOR_PDTIA,
    )
    defaults.update(overrides)
    return Frame(**defaults)


def test_no_frame_returns_none_none():
    assert point_power(None, 0.5) == (None, None)


def test_pdtia_without_calibration_returns_none_none():
    frame = _frame(detector=DETECTOR_PDTIA, conv_factor_W_per_V=None)
    assert point_power(frame, 0.5) == (None, None)


def test_pdtia_with_calibration_multiplies_intensity_by_conv_factor():
    frame = _frame(detector=DETECTOR_PDTIA, conv_factor_W_per_V=2.0e-6)
    power_W, conv_factor = point_power(frame, 0.5)
    assert power_W == 0.5 * 2.0e-6
    assert conv_factor == 2.0e-6


def test_pm400_returns_frame_power_ignoring_intensity_arg():
    """PM400 measures power directly — the passed intensity_V must be ignored."""
    frame = _frame(detector=DETECTOR_PM400, power_W=1.23e-6, conv_factor_W_per_V=None)
    power_W, conv_factor = point_power(frame, 999.0)
    assert power_W == 1.23e-6
    assert conv_factor is None


def test_pm400_with_no_power_reading_yet_returns_none():
    frame = _frame(detector=DETECTOR_PM400, power_W=None)
    power_W, conv_factor = point_power(frame, 0.5)
    assert power_W is None
    assert conv_factor is None
