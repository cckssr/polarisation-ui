"""ND-filter transmission scatter plot.

Shows optical power (log scale) vs. ND-stage position during a range scan,
with markers for the calibrated clear/dark end positions once the scan has
been analysed.

This is a pyqtgraph custom widget — constructing Qt objects in Python is an
explicit exception per CLAUDE.md for pyqtgraph widgets.
"""

import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget


class NDTransmissionPlot(QWidget):
    """Live scatter plot for the ND-filter range scan.

    X = stage position (mm), Y = optical power (W, log scale). Call
    ``add_point()`` as each scan point arrives, then ``set_range_markers()``
    once ``core.nd_filter.analyse_nd_scan`` has picked the clear/dark ends.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build the pyqtgraph plot widget with an empty point buffer."""
        super().__init__(parent)
        self._xs: list[float] = []
        self._ys: list[float] = []
        self._setup_plot()

    def _setup_plot(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._plot_widget = pg.PlotWidget()
        self._plot_widget.setBackground("w")
        self._plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self._plot_widget.setLabel("bottom", "Position", units="mm")
        self._plot_widget.setLabel("left", "Optische Leistung", units="W")
        self._plot_widget.setLogMode(y=True)

        self._series = self._plot_widget.plot(
            [],
            [],
            pen=pg.mkPen((50, 120, 220), width=1),
            symbol="o",
            symbolSize=6,
            symbolBrush=pg.mkBrush(50, 120, 220, 200),
            symbolPen=pg.mkPen(None),
        )
        self._clear_marker = self._plot_widget.addLine(
            x=0, pen=pg.mkPen((30, 160, 50), width=2, style=Qt.PenStyle.DashLine)
        )
        self._clear_marker.setVisible(False)
        self._dark_marker = self._plot_widget.addLine(
            x=0, pen=pg.mkPen((180, 40, 40), width=2, style=Qt.PenStyle.DashLine)
        )
        self._dark_marker.setVisible(False)

        layout.addWidget(self._plot_widget)

    # ── Public API ────────────────────────────────────────────────────────────

    def add_point(self, position_mm: float, power_W: float) -> None:
        """Append a scan point and refresh the series."""
        self._xs.append(position_mm)
        self._ys.append(power_W)
        self._series.setData(self._xs, self._ys)

    def set_range_markers(self, pos_clear_mm: float, pos_dark_mm: float) -> None:
        """Show vertical markers at the calibrated clear/dark end positions."""
        self._clear_marker.setValue(pos_clear_mm)
        self._clear_marker.setVisible(True)
        self._dark_marker.setValue(pos_dark_mm)
        self._dark_marker.setVisible(True)

    def clear(self) -> None:
        """Remove all points and hide the range markers."""
        self._xs = []
        self._ys = []
        self._series.setData([], [])
        self._clear_marker.setVisible(False)
        self._dark_marker.setVisible(False)
