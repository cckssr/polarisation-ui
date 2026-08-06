"""Smoke tests for PowerDriftTab (Laser-Drift warm-up monitoring)."""

import pytest

from polarisation_ui.core.models import Frame
from polarisation_ui.ui.widgets.tabs.power_drift_tab import (
    _MAX_DURATION_S,
    _MAX_POINTS,
    PowerDriftTab,
)


def _make_frame(
    ts_ms: int = 1000,
    sample_angle: float = 10.0,
    detector_angle: float = 20.0,
    intensity: float = 0.5,
) -> Frame:
    return Frame(
        ts_ms=ts_ms,
        sample_angle=sample_angle,
        detector_angle=detector_angle,
        intensity=intensity,
    )


@pytest.fixture()
def tab(qtbot):
    t = PowerDriftTab()
    t.build()
    qtbot.addWidget(t)
    return t


# ---------------------------------------------------------------------------
# Metadata / build
# ---------------------------------------------------------------------------


def test_tab_metadata():
    assert PowerDriftTab.tab_id == "power_drift"
    assert PowerDriftTab.tab_title == "Laser-Drift"
    assert PowerDriftTab.required_sources == {"ENC:BOTH", "ADC"}
    assert PowerDriftTab.required_modules == set()


def test_build_creates_widgets(tab):
    assert tab._ui.intensityPlot is not None
    assert tab._ui.anglesPlot is not None
    assert tab._ui.progressBar is not None
    assert tab._ui.btnClear is not None


def test_clear_button_disabled_before_measurement(tab):
    assert not tab._ui.btnClear.isEnabled()


def test_clear_button_enabled_after_start(tab):
    tab.on_measurement_started()
    assert tab._ui.btnClear.isEnabled()


def test_clear_button_disabled_after_stop(tab):
    tab.on_measurement_started()
    tab.on_measurement_stopped()
    assert not tab._ui.btnClear.isEnabled()


# ---------------------------------------------------------------------------
# on_frame / ring buffers
# ---------------------------------------------------------------------------


def test_on_frame_ignored_without_measurement(tab):
    tab.on_frame(_make_frame())
    assert len(tab._times_s) == 0


def test_on_frame_latches_t0_on_first_frame(tab):
    tab.on_measurement_started()
    tab.on_frame(_make_frame(ts_ms=5000, intensity=0.3))
    assert len(tab._times_s) == 1
    assert tab._times_s[0] == 0.0
    assert tab._intensity[0] == 0.3


def test_on_frame_accumulates_elapsed_time(tab):
    tab.on_measurement_started()
    tab.on_frame(_make_frame(ts_ms=1000))
    tab.on_frame(_make_frame(ts_ms=1500))
    tab.on_frame(_make_frame(ts_ms=2000))
    assert list(tab._times_s) == pytest.approx([0.0, 0.5, 1.0])


def test_on_frame_past_one_hour_cap_is_dropped(tab):
    tab.on_measurement_started()
    tab.on_frame(_make_frame(ts_ms=0))
    over_cap_ms = (_MAX_DURATION_S + 10) * 1000
    tab.on_frame(_make_frame(ts_ms=over_cap_ms))
    assert len(tab._times_s) == 1


def test_first_angle_reference_latched_once(tab):
    tab.on_measurement_started()
    tab.on_frame(_make_frame(ts_ms=1000, sample_angle=10.0, detector_angle=20.0))
    tab.on_frame(_make_frame(ts_ms=1500, sample_angle=15.0, detector_angle=25.0))
    assert tab._first_sample_angle == 10.0
    assert tab._first_detector_angle == 20.0


def test_max_points_cap_evicts_oldest(tab):
    tab.on_measurement_started()
    # Push more than _MAX_POINTS frames spaced 1ms apart (well under the
    # 1-hour wall-clock cap, but exceeding the ring-buffer maxlen) so every
    # frame is accepted and the deque eviction itself is exercised.
    n = _MAX_POINTS + 50
    for i in range(n):
        tab.on_frame(_make_frame(ts_ms=i, intensity=float(i)))
    assert len(tab._times_s) == _MAX_POINTS
    assert len(tab._intensity) == _MAX_POINTS
    # Oldest samples were evicted; the buffer should hold the most recent ones.
    assert tab._intensity[-1] == float(n - 1)


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------


def test_intensity_stats_labels_updated(tab):
    tab.on_measurement_started()
    tab.on_frame(_make_frame(ts_ms=1000, intensity=0.2))
    tab.on_frame(_make_frame(ts_ms=1100, intensity=0.4))
    tab.on_frame(_make_frame(ts_ms=1200, intensity=0.6))
    assert tab._ui.lblICurrent.text() == "0.60000 V"
    assert tab._ui.lblIMin.text() == "0.20000 V"
    assert tab._ui.lblIMax.text() == "0.60000 V"
    assert tab._ui.lblIMean.text() == "0.40000 V"


def test_angle_delta_labels_updated(tab):
    tab.on_measurement_started()
    tab.on_frame(_make_frame(ts_ms=1000, sample_angle=10.0, detector_angle=20.0))
    tab.on_frame(_make_frame(ts_ms=1100, sample_angle=10.5, detector_angle=19.5))
    assert tab._ui.lblDeltaSample.text() == "+0.500°"
    assert tab._ui.lblDeltaDetector.text() == "-0.500°"


def test_elapsed_label_and_progress_bar_updated(tab):
    tab.on_measurement_started()
    tab.on_frame(_make_frame(ts_ms=0))
    tab.on_frame(_make_frame(ts_ms=65_000))
    assert tab._ui.lblElapsed.text() == "00:01:05"
    assert tab._ui.progressBar.value() == 65


# ---------------------------------------------------------------------------
# Reset / clear
# ---------------------------------------------------------------------------


def test_on_reset_clears_buffers_and_labels(tab):
    tab.on_measurement_started()
    tab.on_frame(_make_frame(ts_ms=1000, intensity=0.5))
    tab.on_frame(_make_frame(ts_ms=1100, intensity=0.6))
    assert len(tab._times_s) == 2

    tab.on_reset()

    assert len(tab._times_s) == 0
    assert len(tab._intensity) == 0
    assert len(tab._sample_angle) == 0
    assert len(tab._detector_angle) == 0
    assert tab._first_sample_angle is None
    assert tab._first_detector_angle is None
    assert tab._ui.lblICurrent.text() == "—"
    assert tab._ui.lblDeltaSample.text() == "—"
    assert tab._ui.lblElapsed.text() == "00:00:00"
    assert tab._ui.progressBar.value() == 0


def test_reset_while_measuring_restarts_clock_from_next_frame(tab):
    tab.on_measurement_started()
    tab.on_frame(_make_frame(ts_ms=1000))
    tab.on_reset()
    # A fresh clock reference should be latched from the next incoming frame.
    tab.on_frame(_make_frame(ts_ms=50_000, intensity=0.9))
    assert len(tab._times_s) == 1
    assert tab._times_s[0] == 0.0


def test_clear_data_without_active_measurement_leaves_t0_none(tab):
    tab._clear_data()
    assert tab._t0_ms is None
    # Frames should still be ignored since no measurement was started.
    tab.on_frame(_make_frame(ts_ms=1000))
    assert len(tab._times_s) == 0
