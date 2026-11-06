"""Live plots for the Laser-Drift (power drift) tab.

Two independent pyqtgraph widgets — one for intensity, one for both encoder
angles — plotted against elapsed time in minutes.  Each carries a fixed
60-minute ``InfiniteLine`` marker so students can see at a glance when the
standard 1-hour warm-up/observation window elapses.
"""

from __future__ import annotations

import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget

from polarisation_ui.ui.plot_style import plot_colors, style_plot

_ONE_HOUR_MIN: float = 60.0


def _hour_marker() -> pg.InfiniteLine:
    """Build a vertical dashed reference line at the 60-minute mark."""
    colour = plot_colors().reference
    return pg.InfiniteLine(
        pos=_ONE_HOUR_MIN,
        angle=90,
        movable=False,
        pen=pg.mkPen(color=colour, width=1, style=Qt.PenStyle.DashLine),
        label="1 h",
        labelOpts={"color": colour, "position": 0.97},
    )


class PowerDriftIntensityPlot(QWidget):
    """Rolling intensity-vs-elapsed-time plot with a 60 min reference marker."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build the pyqtgraph plot widget with an empty intensity curve."""
        super().__init__(parent)
        self._setup_plot()

    def _setup_plot(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        colors = plot_colors()
        self._plot_widget = pg.PlotWidget()
        self._plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self._plot_widget.setLabel("bottom", "Zeit", units="min")
        self._plot_widget.setLabel("left", "Intensität", units="V")
        self._plot_widget.addLegend(offset=(-10, 10))

        self._curve = self._plot_widget.plot(
            [],
            [],
            pen=pg.mkPen(color=colors.series_color(0), width=2),
            name="Intensität",
        )
        self._plot_widget.addItem(_hour_marker())

        style_plot(self._plot_widget)
        layout.addWidget(self._plot_widget)

    def set_data(self, t_min: list[float], intensity: list[float]) -> None:
        """Replace the plotted intensity curve with new (time, intensity) samples."""
        self._curve.setData(t_min, intensity)

    def clear(self) -> None:
        """Remove all plotted data."""
        self._curve.setData([], [])


class PowerDriftAnglesPlot(QWidget):
    """Rolling sample/detector-angle-vs-elapsed-time plot with a 60 min marker."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build the pyqtgraph plot widget with empty angle curves."""
        super().__init__(parent)
        self._setup_plot()

    def _setup_plot(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        colors = plot_colors()
        self._plot_widget = pg.PlotWidget()
        self._plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self._plot_widget.setLabel("bottom", "Zeit", units="min")
        self._plot_widget.setLabel("left", "Winkel", units="°")
        self._plot_widget.addLegend(offset=(-10, 10))

        self._curve_sample = self._plot_widget.plot(
            [],
            [],
            pen=pg.mkPen(color=colors.series_color(1), width=1.5, style=Qt.PenStyle.DashLine),
            name="Probenwinkel (θS)",
        )
        self._curve_detector = self._plot_widget.plot(
            [],
            [],
            pen=pg.mkPen(color=colors.series_color(2), width=1.5, style=Qt.PenStyle.DotLine),
            name="Detektorwinkel (θD)",
        )
        self._plot_widget.addItem(_hour_marker())

        style_plot(self._plot_widget)
        layout.addWidget(self._plot_widget)

    def set_data(
        self,
        t_min: list[float],
        sample_angle: list[float],
        detector_angle: list[float],
    ) -> None:
        """Replace the plotted angle curves with new (time, angle) samples."""
        self._curve_sample.setData(t_min, sample_angle)
        self._curve_detector.setData(t_min, detector_angle)

    def clear(self) -> None:
        """Remove all plotted data."""
        self._curve_sample.setData([], [])
        self._curve_detector.setData([], [])
