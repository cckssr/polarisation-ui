"""Brewster-angle curve plot for Brewster tab.

Accumulates manually saved BrewsterPoint entries and displays them as a scatter
plot.  Points are added via add_point() (Save button) and removed via
remove_last_point() or remove_point_at().
"""

from __future__ import annotations

import pyqtgraph as pg
from PySide6.QtWidgets import QVBoxLayout, QWidget

from polarisation_ui.core.models import BrewsterPoint
from polarisation_ui.infrastructure.config import AppConfig, default_config
from polarisation_ui.ui.plot_style import plot_colors, style_plot


class BrewsterCurvePlot(QWidget):
    """Scatter plot of saved Brewster-angle measurement points.

    X axis: sample stage angle (degrees)
    Y axis: detector intensity (V)

    All saved points are shown as filled circles.  The most recently saved point
    is additionally outlined with a marker-coloured ring so the user can see the last entry.
    """

    def __init__(self, parent: QWidget | None = None, config: AppConfig | None = None) -> None:
        """Build the pyqtgraph plot widget with an empty point buffer.

        The axis labels come from ``ui.plots`` in the configuration (default: ``default_config()``);
        an owning tab passes its own configuration through :meth:`apply_config`.
        """
        super().__init__(parent)
        self._points: list[BrewsterPoint] = []
        self._config: AppConfig = config if config is not None else default_config()
        self._y_is_power = False
        self._setup_plot()

    def _setup_plot(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        colors = plot_colors()
        self._plot_widget = pg.PlotWidget()
        self._plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self._apply_axis_labels()

        # All saved points: filled circles
        self._scatter = self._plot_widget.plot(
            [],
            [],
            pen=None,
            symbol="o",
            symbolSize=8,
            symbolBrush=pg.mkBrush(*colors.series_color(0), colors.point_alpha),
            symbolPen=pg.mkPen(None),
        )
        # Last saved point: marker-coloured outline ring (no fill) drawn on top
        self._last_marker = self._plot_widget.plot(
            [],
            [],
            pen=None,
            symbol="o",
            symbolSize=14,
            symbolBrush=pg.mkBrush(0, 0, 0, 0),  # transparent fill
            symbolPen=pg.mkPen(colors.marker, width=2),
        )

        style_plot(self._plot_widget)
        layout.addWidget(self._plot_widget)

    def apply_config(self, config: AppConfig) -> None:
        """Take the axis labels from ``config``."""
        self._config = config
        self._apply_axis_labels()

    def _apply_axis_labels(self) -> None:
        text = self._config.text
        self._plot_widget.setLabel(
            "bottom",
            text("plots.brewster_curve_x_label"),
            units=text("plots.brewster_curve_x_units"),
        )
        quantity = "power" if self._y_is_power else "intensity"
        self._plot_widget.setLabel(
            "left",
            text(f"plots.brewster_curve_{quantity}_label"),
            units=text(f"plots.brewster_curve_{quantity}_units"),
        )

    def add_point(
        self,
        sample_angle: float,
        detector_angle: float,
        intensity_V: float,
        pdtia_gain: int = 0,
        power_W: float | None = None,
        conv_factor_W_per_V: float | None = None,
        detector: str = "pdtia",
    ) -> None:
        """Append a new measurement point and refresh the plot."""
        self._points.append(
            BrewsterPoint(
                sample_angle=sample_angle,
                detector_angle=detector_angle,
                intensity_V=intensity_V,
                pdtia_gain=pdtia_gain,
                power_W=power_W,
                conv_factor_W_per_V=conv_factor_W_per_V,
                detector=detector,
            )
        )
        self._refresh()

    def remove_last_point(self) -> bool:
        """Remove the most recently added point. Returns False if already empty."""
        if not self._points:
            return False
        self._points.pop()
        self._refresh()
        return True

    def remove_point_at(self, index: int) -> bool:
        """Remove the point at *index*. Returns False if out of range."""
        if index < 0 or index >= len(self._points):
            return False
        del self._points[index]
        self._refresh()
        return True

    def get_points(self) -> list[BrewsterPoint]:
        """Return all saved BrewsterPoint entries."""
        return list(self._points)

    def clear(self) -> None:
        """Remove all saved points and clear the plot."""
        self._points.clear()
        self._refresh()

    def _refresh(self) -> None:
        if not self._points:
            self._scatter.setVisible(False)
            self._last_marker.setVisible(False)
            return

        xs = [p.sample_angle for p in self._points]

        use_power = all(p.power_W is not None for p in self._points)
        if use_power:
            ys = [p.power_W * 1e3 for p in self._points]  # type: ignore[operator]
        else:
            ys = [p.intensity_V for p in self._points]
        if use_power != self._y_is_power:
            self._y_is_power = use_power
            self._apply_axis_labels()

        self._scatter.setData(xs, ys)
        self._scatter.setVisible(True)
        self._last_marker.setData([xs[-1]], [ys[-1]])
        self._last_marker.setVisible(True)
