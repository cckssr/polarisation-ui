"""
Tests for MalusTab (manual analyser-angle entry, averaged intensity).

These tests call build() which constructs pyqtgraph widgets.  CI runs with
QT_QPA_PLATFORM=offscreen so no physical display is required.
"""

import math

import pytest

from polarisation_ui.core.models import Frame
from polarisation_ui.ui.widgets.tabs.malus_tab import MalusTab, _AVERAGE_WINDOW_MS

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_frame(ts_ms: int, intensity: float = 0.5, pdtia_gain: int = 0) -> Frame:
    return Frame(
        ts_ms=ts_ms,
        sample_angle=0.0,
        detector_angle=0.0,
        intensity=intensity,
        pdtia_gain=pdtia_gain,
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def tab(qtbot):
    t = MalusTab()
    t.build()
    qtbot.addWidget(t)
    return t


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------


def test_build_creates_plot_and_inputs(tab):
    assert tab._ui.malusCurvePlot is not None
    assert tab._ui.spinPolariser is not None
    assert tab._ui.spinAnalyser is not None
    assert tab._ui.btnAdd is not None


# ---------------------------------------------------------------------------
# on_frame / buffer
# ---------------------------------------------------------------------------


def test_on_frame_populates_buffer(tab):
    tab.on_frame(_make_frame(1000, 0.4))
    tab.on_frame(_make_frame(1100, 0.6))
    assert len(tab._buffer) == 2


def test_on_frame_updates_live_label(tab):
    tab.on_frame(_make_frame(1000, 1.2345))
    assert "1.2345" in tab._ui.lblLiveIntensity.text()


# ---------------------------------------------------------------------------
# _compute_average
# ---------------------------------------------------------------------------


def test_compute_average_empty_buffer_returns_nan(tab):
    avg, frame = tab._compute_average()
    assert math.isnan(avg)
    assert frame is None


def test_compute_average_uses_window(tab):
    # Only frames within _AVERAGE_WINDOW_MS of the latest ts_ms should count.
    old_ts = 0
    recent_ts = old_ts + _AVERAGE_WINDOW_MS + 1  # oldest recent frame exactly in window
    latest_ts = old_ts + _AVERAGE_WINDOW_MS + 200

    tab._buffer.append(_make_frame(old_ts, intensity=10.0))  # outside window
    tab._buffer.append(_make_frame(recent_ts, intensity=2.0))  # inside
    tab._buffer.append(_make_frame(latest_ts, intensity=4.0))  # inside (latest)

    # cutoff = latest_ts - _AVERAGE_WINDOW_MS = old_ts + 200 + 1
    # old_ts (0) < cutoff → excluded
    # recent_ts and latest_ts are >= cutoff → included
    avg, _ = tab._compute_average()
    assert avg == pytest.approx(3.0)  # mean(2.0, 4.0)


def test_compute_average_excludes_nan_frames(tab):
    tab._buffer.append(_make_frame(1000, intensity=float("nan")))
    tab._buffer.append(_make_frame(1100, intensity=0.8))
    tab._buffer.append(_make_frame(1200, intensity=0.6))

    avg, _ = tab._compute_average()
    assert avg == pytest.approx(0.7)  # mean(0.8, 0.6), NaN excluded


def test_compute_average_all_nan_returns_nan(tab):
    tab._buffer.append(_make_frame(1000, intensity=float("nan")))
    avg, _ = tab._compute_average()
    assert math.isnan(avg)


# ---------------------------------------------------------------------------
# Measurement lifecycle gating
# ---------------------------------------------------------------------------


def test_entry_disabled_before_measurement(tab):
    assert not tab._ui.spinAnalyser.isEnabled()
    assert not tab._ui.btnAdd.isEnabled()


def test_entry_enabled_after_measurement_start(tab):
    tab.on_measurement_started()
    assert tab._ui.spinAnalyser.isEnabled()
    assert tab._ui.btnAdd.isEnabled()


def test_polariser_locked_during_measurement(tab):
    tab.on_measurement_started()
    assert not tab._ui.spinPolariser.isEnabled()


def test_entry_disabled_after_measurement_stop(tab):
    tab.on_measurement_started()
    tab.on_measurement_stopped()
    assert not tab._ui.spinAnalyser.isEnabled()
    assert not tab._ui.btnAdd.isEnabled()


def test_polariser_re_enabled_after_measurement_stop(tab):
    tab.on_measurement_started()
    tab.on_measurement_stopped()
    assert tab._ui.spinPolariser.isEnabled()


# ---------------------------------------------------------------------------
# _add_point
# ---------------------------------------------------------------------------


def test_add_point_saves_with_averaged_intensity(qtbot, tab):
    tab.on_measurement_started()
    tab._ui.spinPolariser.setValue(30.0)
    tab._ui.spinAnalyser.setValue(45.0)
    # Feed frames all within the window
    base = 1000
    tab._buffer.append(_make_frame(base, 0.4))
    tab._buffer.append(_make_frame(base + 100, 0.6))

    with qtbot.waitSignal(tab.points_changed, timeout=500) as blocker:
        tab._add_point()

    assert blocker.args == [1]
    points = tab.get_saved_points()
    assert len(points) == 1
    assert points[0].analyser_angle == pytest.approx(45.0)
    assert points[0].polariser_angle == pytest.approx(30.0)
    assert points[0].intensity_V == pytest.approx(0.5)  # mean(0.4, 0.6)


def test_add_point_empty_buffer_emits_warning(qtbot, tab):
    tab.on_measurement_started()
    warnings: list[tuple[str, str]] = []
    tab.status_message.connect(lambda level, msg: warnings.append((level, msg)))

    tab._add_point()

    assert len(warnings) == 1
    assert warnings[0][0] == "warning"
    assert tab.get_saved_points() == []


def test_add_point_all_nan_buffer_emits_warning(qtbot, tab):
    tab.on_measurement_started()
    tab._buffer.append(_make_frame(1000, float("nan")))
    warnings: list[tuple[str, str]] = []
    tab.status_message.connect(lambda level, msg: warnings.append((level, msg)))

    tab._add_point()

    assert len(warnings) == 1
    assert tab.get_saved_points() == []


# ---------------------------------------------------------------------------
# get_saved_points / build_export
# ---------------------------------------------------------------------------


def test_get_saved_points_initially_empty(tab):
    assert tab.get_saved_points() == []


def test_build_export_schema(qtbot, tab):
    tab.on_measurement_started()
    tab._ui.spinPolariser.setValue(10.0)
    tab._ui.spinAnalyser.setValue(20.0)
    tab._buffer.append(_make_frame(1000, 0.3))
    tab._add_point()

    exp = tab.build_export()
    assert exp.filename_hint == "malus"
    assert "analyser_angle_deg" in exp.columns
    assert "polariser_angle_deg" in exp.columns
    assert "intensity_V" in exp.columns
    assert len(exp.rows) == 1
    assert exp.metadata["polariser_angle_deg"] == pytest.approx(10.0)


def test_build_export_empty_tab(tab):
    exp = tab.build_export()
    assert exp.filename_hint == "malus"
    assert exp.rows == []
    assert "analyser_angle_deg" in exp.columns


# ---------------------------------------------------------------------------
# on_reset
# ---------------------------------------------------------------------------


def test_reset_clears_points(qtbot, tab):
    tab.on_measurement_started()
    tab._buffer.append(_make_frame(1000, 0.5))
    tab._add_point()
    assert len(tab.get_saved_points()) == 1

    with qtbot.waitSignal(tab.points_changed, timeout=500):
        tab.on_reset()

    assert tab.get_saved_points() == []
    assert len(tab._buffer) == 0
