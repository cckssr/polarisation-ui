"""Smoke tests for BrewsterTab (Brewster-angle sample scan + peak finding).

Verifies build, measurement lifecycle, save-current, and build_export schema.
"""

import pytest

from polarisation_ui.core.models import Frame
from polarisation_ui.ui.widgets.tabs.brewster_tab import BrewsterTab


def _make_frame(
    sample_angle: float = 30.0,
    detector_angle: float = 60.0,
    intensity: float = 0.75,
) -> Frame:
    return Frame(
        ts_ms=1000,
        sample_angle=sample_angle,
        detector_angle=detector_angle,
        intensity=intensity,
    )


@pytest.fixture()
def tab(qtbot):
    t = BrewsterTab()
    t.build()
    qtbot.addWidget(t)
    return t


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------


def test_build_creates_plots(tab):
    assert tab._ui.detectorPlot is not None
    assert tab._ui.brewsterCurvePlot is not None


def test_tab_metadata():
    assert BrewsterTab.tab_id == "brewster"
    assert BrewsterTab.tab_title == "Brewster"
    assert BrewsterTab.required_modules == set()


# ---------------------------------------------------------------------------
# Measurement lifecycle
# ---------------------------------------------------------------------------


def test_save_buttons_disabled_before_measurement(tab):
    assert not tab._ui.btnSaveCurrent.isEnabled()
    assert not tab._ui.btnSaveMax.isEnabled()


def test_save_buttons_enabled_after_start(tab):
    tab.on_measurement_started()
    assert tab._ui.btnSaveCurrent.isEnabled()
    assert tab._ui.btnSaveMax.isEnabled()


# ---------------------------------------------------------------------------
# Save + export
# ---------------------------------------------------------------------------


def test_save_current_adds_point(qtbot, tab):
    tab.on_measurement_started()
    frame = _make_frame(sample_angle=25.0, detector_angle=50.0, intensity=0.9)
    tab.on_frame(frame)

    with qtbot.waitSignal(tab.points_changed, timeout=500) as blocker:
        tab._save_point_current()

    assert blocker.args == [1]
    points = tab.get_saved_points()
    assert len(points) == 1
    assert points[0].sample_angle == pytest.approx(25.0)
    assert points[0].intensity_V == pytest.approx(0.9)


def test_build_export_schema(qtbot, tab):
    tab.on_measurement_started()
    tab.on_frame(_make_frame(30.0, 60.0, 0.5))
    tab._save_point_current()

    exp = tab.build_export()
    assert exp.filename_hint == "brewster"
    assert "sample_angle_deg" in exp.columns
    assert "detector_angle_deg" in exp.columns
    assert "intensity_V" in exp.columns
    assert len(exp.rows) == 1


def test_build_export_empty(tab):
    exp = tab.build_export()
    assert exp.filename_hint == "brewster"
    assert exp.rows == []


# ---------------------------------------------------------------------------
# get_saved_points / on_reset
# ---------------------------------------------------------------------------


def test_get_saved_points_initially_empty(tab):
    assert tab.get_saved_points() == []


def test_reset_clears_points(qtbot, tab):
    tab.on_measurement_started()
    tab.on_frame(_make_frame())
    tab._save_point_current()
    assert len(tab.get_saved_points()) == 1

    with qtbot.waitSignal(tab.points_changed, timeout=500):
        tab.on_reset()

    assert tab.get_saved_points() == []
