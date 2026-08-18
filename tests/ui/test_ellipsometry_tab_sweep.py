"""Tests for the KDC101 sweep integration and gating in EllipsometryTab."""

import pytest

from polarisation_ui.core.models import Frame
from polarisation_ui.infrastructure.mocks.mock_kdc101_polariser import (
    MockKDC101Polariser,
)
from polarisation_ui.ui.widgets.tabs.ellipsometry_tab import EllipsometryTab


def _make_frame(
    ts_ms: int = 1000,
    intensity: float = 0.5,
    pdtia_gain: int = 1,
    power_W: float | None = None,
    conv_factor_W_per_V: float | None = None,
) -> Frame:
    return Frame(
        ts_ms=ts_ms,
        sample_angle=65.0,
        detector_angle=130.0,
        intensity=intensity,
        pdtia_gain=pdtia_gain,
        power_W=power_W,
        conv_factor_W_per_V=conv_factor_W_per_V,
    )


@pytest.fixture()
def tab(qtbot):
    t = EllipsometryTab()
    t.build()
    qtbot.addWidget(t)
    return t


@pytest.fixture()
def tab_with_kdc(tab):
    kdc = MockKDC101Polariser()
    kdc.connect("mock://kdc101")
    tab.inject_modules({"kdc101": kdc})
    return tab, kdc


def _make_ready(tab) -> None:
    """Satisfy every gate for btnStartSweep except the one under test."""
    tab.on_measurement_started()
    tab.on_frame(_make_frame(1000, power_W=1e-6, conv_factor_W_per_V=2e-6))
    tab._ui.cbAnalyserPlaced.setChecked(True)


def test_sweep_group_disabled_without_kdc(tab):
    assert not tab._ui.gbSweep.isEnabled()


def test_sweep_group_enabled_after_kdc_inject(tab_with_kdc):
    tab, _ = tab_with_kdc
    assert tab._ui.gbSweep.isEnabled()


def test_inject_empty_modules_disables_sweep_group(tab_with_kdc):
    tab, _ = tab_with_kdc
    tab.inject_modules({})
    assert not tab._ui.gbSweep.isEnabled()
    assert tab._kdc is None


def test_start_sweep_button_disabled_without_measurement(tab_with_kdc):
    tab, _ = tab_with_kdc
    tab._ui.cbAnalyserPlaced.setChecked(True)
    assert not tab._ui.btnStartSweep.isEnabled()


def test_start_sweep_button_disabled_without_power_calibration(tab_with_kdc):
    tab, _ = tab_with_kdc
    tab.on_measurement_started()
    tab._ui.cbAnalyserPlaced.setChecked(True)
    tab.on_frame(_make_frame(1000, conv_factor_W_per_V=None))
    assert not tab._ui.btnStartSweep.isEnabled()


def test_start_sweep_button_disabled_without_analyser_placed(tab_with_kdc):
    tab, _ = tab_with_kdc
    _make_ready(tab)
    tab._ui.cbAnalyserPlaced.setChecked(False)
    assert not tab._ui.btnStartSweep.isEnabled()


def test_start_sweep_button_enabled_when_ready(tab_with_kdc):
    tab, _ = tab_with_kdc
    _make_ready(tab)
    assert tab._ui.btnStartSweep.isEnabled()


def test_start_sweep_tooltip_explains_missing_gates(tab_with_kdc):
    tab, _ = tab_with_kdc
    assert tab._ui.btnStartSweep.toolTip() != "Scan starten"
    tooltip = tab._ui.btnStartSweep.toolTip()
    assert "Messung" in tooltip or "kalibrierung" in tooltip


def test_measurement_stop_disables_sweep_controls(tab_with_kdc):
    tab, _ = tab_with_kdc
    _make_ready(tab)
    assert tab._ui.btnStartSweep.isEnabled()
    tab.on_measurement_stopped()
    assert not tab._ui.btnStartSweep.isEnabled()


def test_sweep_point_carries_gain_and_power(tab_with_kdc):
    tab, _ = tab_with_kdc
    tab._aoi_zero_sample = 0.0
    frame = _make_frame(pdtia_gain=3, intensity=0.5, conv_factor_W_per_V=2e-6)
    tab._on_sweep_point(10.0, 10.0, 0.5, frame)
    points = tab._ui.fitPlot.get_points()
    assert len(points) == 1
    assert points[0].pdtia_gain == 3
    assert points[0].power_W == pytest.approx(0.5 * 2e-6)
    assert points[0].conv_factor_W_per_V == 2e-6
    assert points[0].azimuth_deg == pytest.approx(10.0 + tab._ui.spinAnalyserOffset.value())
    assert points[0].aoi_deg == pytest.approx(65.0)


def test_sweep_point_without_frame_leaves_gain_and_power_unset(tab_with_kdc):
    tab, _ = tab_with_kdc
    tab._on_sweep_point(10.0, 10.0, 0.5, None)
    points = tab._ui.fitPlot.get_points()
    assert len(points) == 1
    assert points[0].pdtia_gain == 0
    assert points[0].power_W is None


def test_sweep_points_feed_live_fit(tab_with_kdc):
    tab, _ = tab_with_kdc
    tab._aoi_zero_sample = 0.0
    offset = tab._ui.spinAnalyserOffset.value()
    import math

    for i in range(19):
        a = i * (180.0 / 19)
        az = math.radians(a + offset)
        intensity = 1.0 + 0.3 * math.cos(2 * az) + 0.2 * math.sin(2 * az)
        frame = _make_frame(intensity=intensity, power_W=intensity * 2e-6, conv_factor_W_per_V=2e-6)
        tab._on_sweep_point(a, a, intensity, frame)

    assert tab._last_fit is not None
    assert tab._last_fit.valid
    assert tab._last_fit.alpha == pytest.approx(0.3, abs=0.01)
    assert tab._last_fit.beta == pytest.approx(0.2, abs=0.01)


def test_abort_sweep_without_worker_is_noop(tab_with_kdc):
    tab, _ = tab_with_kdc
    tab._abort_sweep()  # must not raise
