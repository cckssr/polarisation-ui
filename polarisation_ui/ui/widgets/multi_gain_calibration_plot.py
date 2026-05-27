"""
Multi-series calibration scatter plot.

Shows one colour-coded scatter series per PDTIA gain stage (1–4) with
X = detector voltage (V) and Y = optical power (W).  Designed to receive
live points during an automated power calibration sweep.

This is a pyqtgraph custom widget — constructing Qt objects in Python is an
explicit exception per CLAUDE.md for pyqtgraph widgets.
"""

from typing import Optional

import pyqtgraph as pg
from PySide6.QtWidgets import QVBoxLayout, QWidget

_GAIN_COLOURS: dict[int, tuple[int, int, int]] = {
    1: (30, 160, 50),  # green
    2: (50, 120, 220),  # blue
    3: (210, 100, 30),  # orange
    4: (180, 40, 180),  # purple
}


class MultiGainCalibrationPlot(QWidget):
    """
    Live scatter plot for automated power calibration.

    One coloured series per gain stage; X = detector voltage (V),
    Y = calibrated optical power (W).  Call ``add_point()`` as each
    calibration point arrives from the worker thread.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._data: dict[int, tuple[list[float], list[float]]] = {
            g: ([], []) for g in range(1, 5)
        }
        self._setup_plot()

    def _setup_plot(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._plot_widget = pg.PlotWidget()
        self._plot_widget.setBackground("w")
        self._plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self._plot_widget.setLabel("bottom", "Detektorspannung", units="V")
        self._plot_widget.setLabel("left", "Optische Leistung", units="W")
        self._plot_widget.addLegend()

        self._series: dict[int, pg.PlotDataItem] = {}
        for gain, (r, g_col, b) in _GAIN_COLOURS.items():
            series = self._plot_widget.plot(
                [],
                [],
                name=f"Gain {gain}",
                pen=None,
                symbol="o",
                symbolSize=7,
                symbolBrush=pg.mkBrush(r, g_col, b, 200),
                symbolPen=pg.mkPen(None),
            )
            self._series[gain] = series

        layout.addWidget(self._plot_widget)

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
