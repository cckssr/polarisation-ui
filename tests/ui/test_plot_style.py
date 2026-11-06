"""Plots follow the application palette and take their colours from ``plot_colors``."""

from __future__ import annotations

import pyqtgraph as pg
import pytest
from PySide6.QtGui import QColor, QGuiApplication, QPalette
from PySide6.QtWidgets import QApplication

from polarisation_ui.infrastructure.config import AppConfig, load_config
from polarisation_ui.infrastructure.logging import Debug
from polarisation_ui.ui.plot_style import (
    PlotColors,
    plot_colors,
    set_plot_colors,
    style_plot,
)
from polarisation_ui.ui.widgets.brewster_curve_plot import BrewsterCurvePlot
from polarisation_ui.ui.widgets.ellipsometry_fit_plot import EllipsometryFitPlot
from polarisation_ui.ui.widgets.malus_curve_plot import MalusCurvePlot
from polarisation_ui.ui.widgets.nd_linearity_plot import NDLinearityPlot

DARK_WINDOW = QColor(32, 33, 36)
LIGHT_TEXT = QColor(235, 235, 235)
LIGHT_WINDOW = QColor(250, 250, 250)
DARK_TEXT = QColor(20, 20, 20)


def _palette(window: QColor, text: QColor) -> QPalette:
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, window)
    palette.setColor(QPalette.ColorRole.WindowText, text)
    return palette


@pytest.fixture
def app_palette(qapp):
    """Switch the application palette inside a test and restore it afterwards."""
    original = QGuiApplication.palette()

    def switch(window: QColor, text: QColor) -> None:
        QApplication.setPalette(_palette(window, text))

    yield switch
    QApplication.setPalette(original)


@pytest.fixture
def warnings(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    messages: list[str] = []
    monkeypatch.setattr(Debug, "warning", classmethod(lambda cls, msg: messages.append(msg)))
    return messages


def _background(widget: pg.PlotWidget) -> QColor:
    return widget.backgroundBrush().color()


def _axis_pen_color(widget: pg.PlotWidget, name: str) -> QColor:
    return widget.getPlotItem().getAxis(name).pen().color()


def test_a_plot_gets_the_dark_background_and_light_axes_of_a_dark_palette(qtbot, app_palette):
    app_palette(DARK_WINDOW, LIGHT_TEXT)
    plot = pg.PlotWidget()
    qtbot.addWidget(plot)
    style_plot(plot)
    assert _background(plot) == DARK_WINDOW
    for axis in ("left", "bottom"):
        assert _axis_pen_color(plot, axis) == LIGHT_TEXT
        assert plot.getPlotItem().getAxis(axis).textPen().color() == LIGHT_TEXT


def test_a_plot_gets_the_light_background_and_dark_axes_of_a_light_palette(qtbot, app_palette):
    app_palette(LIGHT_WINDOW, DARK_TEXT)
    plot = pg.PlotWidget()
    qtbot.addWidget(plot)
    style_plot(plot)
    assert _background(plot) == LIGHT_WINDOW
    assert _axis_pen_color(plot, "left") == DARK_TEXT


def test_the_plot_follows_a_palette_change(qtbot, app_palette):
    app_palette(LIGHT_WINDOW, DARK_TEXT)
    plot = pg.PlotWidget()
    qtbot.addWidget(plot)
    plot.show()
    style_plot(plot)
    app_palette(DARK_WINDOW, LIGHT_TEXT)
    qtbot.waitUntil(lambda: _background(plot) == DARK_WINDOW)
    assert _axis_pen_color(plot, "bottom") == LIGHT_TEXT
    app_palette(LIGHT_WINDOW, DARK_TEXT)
    qtbot.waitUntil(lambda: _background(plot) == LIGHT_WINDOW)
    assert _axis_pen_color(plot, "bottom") == DARK_TEXT


def test_styling_twice_installs_a_single_palette_watcher(qtbot, app_palette):
    plot = pg.PlotWidget()
    qtbot.addWidget(plot)
    style_plot(plot)
    style_plot(plot)
    watchers = [c for c in plot.children() if type(c).__name__ == "_PaletteWatcher"]
    assert len(watchers) == 1


def test_a_graphics_layout_widget_is_styled_too(qtbot, app_palette):
    app_palette(DARK_WINDOW, LIGHT_TEXT)
    layout = pg.GraphicsLayoutWidget()
    qtbot.addWidget(layout)
    inner = layout.addPlot()
    style_plot(layout)
    assert layout.backgroundBrush().color() == DARK_WINDOW
    assert inner.getAxis("left").pen().color() == LIGHT_TEXT


def test_a_legend_follows_the_palette(qtbot, app_palette):
    app_palette(DARK_WINDOW, LIGHT_TEXT)
    plot = pg.PlotWidget()
    qtbot.addWidget(plot)
    plot.addLegend()
    plot.plot([0, 1], [0, 1], name="Kurve")
    style_plot(plot)
    assert plot.getPlotItem().legend.opts["labelTextColor"] == LIGHT_TEXT


@pytest.mark.parametrize(
    "factory, attribute",
    [
        (MalusCurvePlot, "_plot_widget"),
        (BrewsterCurvePlot, "_plot_widget"),
        (EllipsometryFitPlot, "_residual_widget"),
        (NDLinearityPlot, "_resid_plot"),
    ],
)
def test_the_application_plots_follow_the_palette(qtbot, app_palette, factory, attribute):
    app_palette(DARK_WINDOW, LIGHT_TEXT)
    widget = factory()
    qtbot.addWidget(widget)
    plot = getattr(widget, attribute)
    assert _background(plot) == DARK_WINDOW
    assert _axis_pen_color(plot, "left") == LIGHT_TEXT


def test_the_packaged_config_defines_every_colour_role(warnings):
    colors = PlotColors.from_config(load_config())
    assert warnings == []
    assert len(colors.series) == 10
    assert colors.series[0] == (31, 119, 180)  # tab:blue
    assert colors.fit == (214, 39, 40)  # tab:red
    assert colors.reference == (127, 127, 127)  # tab:gray
    assert 0 <= colors.band_alpha <= 255 and 0 <= colors.point_alpha <= 255


def test_plot_colors_resolves_the_default_config_and_is_cached():
    assert plot_colors() is plot_colors()
    assert plot_colors().series_color(0) == plot_colors().series[0]


def test_colors_accept_rgb_lists_hex_strings_and_cycle_names(warnings):
    config = load_config(
        overrides={
            "plot_colors": {
                "series": [[1, 2, 3], "#0a0b0c", "C3"],
                "fit": "tab:green",
                "marker": [255, 0, 0],
            }
        }
    )
    colors = PlotColors.from_config(config)
    assert warnings == []
    assert colors.series == ((1, 2, 3), (10, 11, 12), (214, 39, 40))
    assert colors.fit == (44, 160, 44)
    assert colors.marker == (255, 0, 0)


def test_the_series_colours_cycle():
    colors = PlotColors.from_config(
        load_config(overrides={"plot_colors": {"series": ["C0", "C1"]}})
    )
    assert colors.series_color(2) == colors.series_color(0)
    assert colors.series_color(3) == colors.series_color(1)


def test_malformed_entries_fall_back_to_grey_and_are_logged(warnings):
    config: AppConfig = load_config(
        overrides={
            "plot_colors": {
                "series": "tab:blue",  # not a list
                "fit": "not-a-colour",
                "reference": [1, 2],
                "marker": [0, 0, 300],
                "band_alpha": "much",
                "point_alpha": 999,
            }
        }
    )
    colors = PlotColors.from_config(config)
    grey = (160, 160, 160)
    assert colors.series == (grey,)
    assert colors.fit == colors.reference == colors.marker == grey
    assert colors.band_alpha == colors.point_alpha == 255
    logged = " ".join(warnings)
    for key in ("series", "fit", "reference", "marker", "band_alpha", "point_alpha"):
        assert f"plot_colors.{key}" in logged


def test_a_missing_section_falls_back_to_grey_and_is_logged(warnings):
    colors = PlotColors.from_config(AppConfig({}))
    assert colors.fit == (160, 160, 160)
    assert warnings


def test_set_plot_colors_changes_the_colours_of_plots_created_afterwards(qtbot):
    set_plot_colors(
        PlotColors.from_config(load_config(overrides={"plot_colors": {"marker": [7, 8, 9]}}))
    )
    plot = MalusCurvePlot()
    qtbot.addWidget(plot)
    assert plot._last_marker.opts["symbolPen"].color().getRgb()[:3] == (7, 8, 9)
    set_plot_colors(None)
    assert plot_colors().marker == (255, 127, 14)  # tab:orange of the packaged config
