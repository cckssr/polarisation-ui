"""Multi-series calibration scatter plot.

Shows one colour-coded scatter series per PDTIA gain stage (1–4) with
X = detector voltage (V) and Y = optical power (W).  Designed to receive
live points during an automated power calibration sweep.

This is a pyqtgraph custom widget — constructing Qt objects in Python is an
explicit exception per CLAUDE.md for pyqtgraph widgets.
"""

from __future__ import annotations

import pyqtgraph as pg
from PySide6.QtWidgets import QVBoxLayout, QWidget

from polarisation_ui.infrastructure.config import AppConfig, default_config
from polarisation_ui.ui.plot_style import plot_colors, style_plot


class MultiGainCalibrationPlot(QWidget):
    """Live scatter plot for automated power calibration.

    One coloured series per gain stage; X = detector voltage (V),
    Y = calibrated optical power (W).  Call ``add_point()`` as each
    calibration point arrives from the worker thread.
    """

    def __init__(self, parent: QWidget | None = None, config: AppConfig | None = None) -> None:
        """Build the plot widget with empty per-gain-stage point buffers; texts from ``config``."""
        super().__init__(parent)
        self._config: AppConfig = config if config is not None else default_config()
        self._data: dict[int, tuple[list[float], list[float]]] = {g: ([], []) for g in range(1, 5)}
        self._setup_plot()

    def _setup_plot(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        colors = plot_colors()
        self._plot_widget = pg.PlotWidget()
        self._plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self._plot_widget.addLegend()

        self._series: dict[int, pg.PlotDataItem] = {}
        for gain in range(1, 5):
            colour = colors.series_color(gain - 1)
            series = self._plot_widget.plot(
                [],
                [],
                name=self._series_name(gain),
                pen=None,
                symbol="o",
                symbolSize=7,
                symbolBrush=pg.mkBrush(*colour, colors.point_alpha),
                symbolPen=pg.mkPen(None),
            )
            self._series[gain] = series

        style_plot(self._plot_widget)
        layout.addWidget(self._plot_widget)
        self._apply_labels()

    def _series_name(self, gain: int) -> str:
        return self._config.text("plots.multi_gain_series_name", gain=gain)

    def _apply_labels(self) -> None:
        self._plot_widget.setLabel(
            "bottom", self._config.text("plots.multi_gain_voltage_label"), units="V"
        )
        self._plot_widget.setLabel(
            "left", self._config.text("plots.multi_gain_power_label"), units="W"
        )

    def apply_config(self, config: AppConfig) -> None:
        """Use the axis and legend texts of ``config``."""
        self._config = config
        self._apply_labels()
        legend = self._plot_widget.plotItem.legend
        for gain, series in self._series.items():
            name = self._series_name(gain)
            series.opts["name"] = name
            if legend is not None:
                legend.getLabel(series).setText(name)

    # ── Public API ────────────────────────────────────────────────────────────

    def add_point(self, gain: int, voltage_V: float, power_W: float) -> None:
        """Append a calibration point for *gain* and refresh the series."""
        if gain not in self._data:
            return
        xs, ys = self._data[gain]
        xs.append(voltage_V)
        ys.append(power_W)
        self._series[gain].setData(xs, ys)

    def clear_gain(self, gain: int) -> None:
        """Remove all points for a single gain stage."""
        if gain not in self._data:
            return
        self._data[gain] = ([], [])
        self._series[gain].setData([], [])

    def clear(self) -> None:
        """Remove all points from all gain series."""
        for gain in list(self._data):
            self.clear_gain(gain)
