"""Tests for the KDC101 sweep integration in MalusTab."""

import pytest

from polarisation_ui.core.models import Frame
from polarisation_ui.infrastructure.mocks.mock_kdc101_polariser import (
    MockKDC101Polariser,
)
from polarisation_ui.ui.widgets.tabs.malus_tab import MalusTab


def _make_frame(ts_ms: int = 1000, intensity: float = 0.5) -> Frame:
    return Frame(ts_ms=ts_ms, sample_angle=0.0, detector_angle=0.0, intensity=intensity)


@pytest.fixture()
def tab(qtbot):
    t = MalusTab()
    t.build()
    qtbot.addWidget(t)
    return t


@pytest.fixture()
def tab_with_kdc(tab):
    kdc = MockKDC101Polariser()
    kdc.connect("mock://kdc101")
    tab.inject_modules({"kdc101": kdc})
    return tab, kdc


def test_sweep_group_disabled_without_kdc(tab):
    assert not tab._ui.gbSweep.isEnabled()


def test_sweep_group_enabled_after_kdc_inject(tab_with_kdc):
    tab, _ = tab_with_kdc
    assert tab._ui.gbSweep.isEnabled()


def test_start_sweep_button_disabled_without_measurement(tab_with_kdc):
    tab, _ = tab_with_kdc
    tab._ui.cbPolariserPlaced.setChecked(True)
    # measurement not started → should not be enabled
    assert not tab._ui.btnStartSweep.isEnabled()


def test_start_sweep_button_enabled_when_ready(tab_with_kdc):
    tab, _ = tab_with_kdc
    tab.on_measurement_started()
    tab._ui.cbPolariserPlaced.setChecked(True)
    assert tab._ui.btnStartSweep.isEnabled()


def test_start_sweep_button_disabled_without_polariser_placed(tab_with_kdc):
    tab, _ = tab_with_kdc
    tab.on_measurement_started()
    tab._ui.cbPolariserPlaced.setChecked(False)
    assert not tab._ui.btnStartSweep.isEnabled()


def test_inject_empty_modules_disables_sweep_group(tab_with_kdc):
    tab, _ = tab_with_kdc
    tab.inject_modules({})
    assert not tab._ui.gbSweep.isEnabled()
    assert tab._kdc is None


def test_compute_average_thread_safe(tab):
    tab.on_frame(_make_frame(1000, 0.5))
    tab.on_frame(_make_frame(1100, 0.7))
    intensity, frame = tab._compute_average()
    assert not (intensity != intensity)  # not NaN
    assert abs(intensity - 0.6) < 0.01


def test_malus_export_contains_zero_offset_when_set(tab):
    tab._kdc_zero_offset = 45.0
    tab._ui.spinSweepStart.setValue(0.0)
    tab._ui.spinSweepEnd.setValue(180.0)
    tab._ui.spinSweepStep.setValue(5.0)
    exp = tab.build_export()
    assert exp.metadata["kdc_zero_offset_deg"] == 45.0
    assert exp.metadata["sweep_step_deg"] == 5.0
