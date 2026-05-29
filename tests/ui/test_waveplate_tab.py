"""Smoke tests for WaveplateTab."""

import pytest

from polarisation_ui.core.models import Frame
from polarisation_ui.infrastructure.mocks.mock_kdc101_polariser import (
    MockKDC101Polariser,
)
from polarisation_ui.ui.widgets.tabs.waveplate_tab import WaveplateTab


def _make_frame(ts_ms: int = 1000, intensity: float = 0.5) -> Frame:
    return Frame(ts_ms=ts_ms, sample_angle=0.0, detector_angle=0.0, intensity=intensity)


@pytest.fixture()
def tab(qtbot):
    t = WaveplateTab()
    t.build()
    qtbot.addWidget(t)
    return t


@pytest.fixture()
def tab_with_kdc(tab):
    kdc = MockKDC101Polariser()
    kdc.connect("mock://kdc101")
    tab.inject_modules({"kdc101": kdc})
    return tab, kdc


def test_metadata():
    assert WaveplateTab.tab_id == "waveplate"
    assert "kdc101" in WaveplateTab.required_modules


def test_sweep_button_disabled_without_kdc(tab):
    assert not tab._ui.btnStartSweep.isEnabled()


def test_sweep_button_disabled_without_waveplate_placed(tab_with_kdc):
    tab, _ = tab_with_kdc
    tab.on_measurement_started()
    tab._ui.cbWaveplatePlaced.setChecked(False)
    assert not tab._ui.btnStartSweep.isEnabled()


def test_sweep_button_enabled_when_ready(tab_with_kdc):
    tab, _ = tab_with_kdc
    tab.on_measurement_started()
    tab._ui.cbWaveplatePlaced.setChecked(True)
    assert tab._ui.btnStartSweep.isEnabled()


def test_on_frame_populates_buffer(tab):
    tab.on_frame(_make_frame(1000, 0.4))
    assert len(tab._buffer) == 1


def test_build_export_qwp_filename_tokens(tab):
    tab._ui.cmbWaveplateType.setCurrentIndex(0)  # λ/4
    exp = tab.build_export()
    assert exp.filename_tokens == ["qwp"]
    assert exp.metadata["waveplate_type"] == "lambda/4"


def test_build_export_hwp_filename_tokens(tab):
    tab._ui.cmbWaveplateType.setCurrentIndex(1)  # λ/2
    exp = tab.build_export()
    assert exp.filename_tokens == ["hwp"]
    assert exp.metadata["waveplate_type"] == "lambda/2"


def test_inject_modules_enables_sweep_group(tab):
    kdc = MockKDC101Polariser()
    kdc.connect("mock://kdc101")
    tab.inject_modules({"kdc101": kdc})
    assert tab._kdc is kdc


def test_inject_modules_with_empty_dict_clears_kdc(tab):
    kdc = MockKDC101Polariser()
    kdc.connect("mock://kdc101")
    tab.inject_modules({"kdc101": kdc})
    tab.inject_modules({})
    assert tab._kdc is None
