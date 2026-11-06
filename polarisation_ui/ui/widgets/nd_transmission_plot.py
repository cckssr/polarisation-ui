"""ND-filter transmission scatter plot.

Shows optical power (log scale) vs. ND-stage position during a range scan,
with markers for the calibrated clear/dark end positions once the scan has
been analysed.

This is a pyqtgraph custom widget — constructing Qt objects in Python is an
explicit exception per CLAUDE.md for pyqtgraph widgets.
"""

from __future__ import annotations

import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget

from polarisation_ui.infrastructure.config import AppConfig, default_config
from polarisation_ui.ui.plot_style import plot_colors, style_plot


class NDTransmissionPlot(QWidget):
    """Live scatter plot for the ND-filter range scan.

    X = wheel angle (°), Y = optical power (W, log scale). Call
    ``add_point()`` as each scan point arrives, then ``set_range_markers()``
    once ``core.nd_filter.analyse_nd_scan`` has picked the clear/dark ends.
    """

    def __init__(self, parent: QWidget | None = None, config: AppConfig | None = None) -> None:
        """Build the pyqtgraph plot widget with an empty point buffer; texts from ``config``."""
        super().__init__(parent)
        self._config: AppConfig = config if config is not None else default_config()
        self._xs: list[float] = []
        self._ys: list[float] = []
        self._setup_plot()

    def _setup_plot(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        colors = plot_colors()
        self._plot_widget = pg.PlotWidget()
        self._plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self._plot_widget.setLogMode(y=True)

        self._series = self._plot_widget.plot(
            [],
            [],
            pen=pg.mkPen(colors.series_color(0), width=1),
            symbol="o",
            symbolSize=6,
            symbolBrush=pg.mkBrush(*colors.series_color(0), colors.point_alpha),
            symbolPen=pg.mkPen(None),
        )
        self._clear_marker = self._plot_widget.addLine(
            x=0, pen=pg.mkPen(colors.series_color(2), width=2, style=Qt.PenStyle.DashLine)
        )
        self._clear_marker.setVisible(False)
        self._dark_marker = self._plot_widget.addLine(
            x=0, pen=pg.mkPen(colors.fit, width=2, style=Qt.PenStyle.DashLine)
        )
        self._dark_marker.setVisible(False)

        style_plot(self._plot_widget)
        layout.addWidget(self._plot_widget)
        self._apply_labels()

    def _apply_labels(self) -> None:
        self._plot_widget.setLabel(
            "bottom", self._config.text("plots.nd_transmission_angle_label"), units="°"
        )
        self._plot_widget.setLabel(
            "left", self._config.text("plots.nd_transmission_power_label"), units="W"
        )

    def apply_config(self, config: AppConfig) -> None:
        """Use the axis texts of ``config``."""
        self._config = config
        self._apply_labels()

    # ── Public API ────────────────────────────────────────────────────────────

    def add_point(self, position_deg: float, power_W: float) -> None:
        """Append a scan point and refresh the series."""
        self._xs.append(position_deg)
        self._ys.append(power_W)
        self._series.setData(self._xs, self._ys)

    def set_range_markers(self, pos_clear_deg: float, pos_dark_deg: float) -> None:
        """Show vertical markers at the calibrated clear/dark end positions."""
        self._clear_marker.setValue(pos_clear_deg)
        self._clear_marker.setVisible(True)
        self._dark_marker.setValue(pos_dark_deg)
        self._dark_marker.setVisible(True)

    def clear(self) -> None:
        """Remove all points and hide the range markers."""
        self._xs = []
        self._ys = []
        self._series.setData([], [])
        self._clear_marker.setVisible(False)
        self._dark_marker.setVisible(False)
