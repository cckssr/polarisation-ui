"""Dual-power-meter cross-check scatter plot.

Shows power meter B vs. power meter A across the scanned ND range, with a
unity (B = A) reference line — points hugging the line mean the two meters
agree.

This is a pyqtgraph custom widget — constructing Qt objects in Python is an
explicit exception per CLAUDE.md for pyqtgraph widgets.
"""

import pyqtgraph as pg
from PySide6.QtWidgets import QVBoxLayout, QWidget


class DetectorComparisonPlot(QWidget):
    """Live scatter plot for the dual-power-meter cross-check.

    X = reference meter A (W), Y = meter under test B (W), both log scale,
    with a unity reference line. Call ``add_point()`` as each paired reading
    arrives.
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
        self._plot_widget.setLabel("bottom", "PM400 A (Referenz)", units="W")
        self._plot_widget.setLabel("left", "PM400 B (Prüfling)", units="W")
        self._plot_widget.setLogMode(x=True, y=True)

        self._unity_line = self._plot_widget.plot(
            [1e-12, 1.0], [1e-12, 1.0], pen=pg.mkPen((150, 150, 150), width=1)
        )
        self._series = self._plot_widget.plot(
            [],
            [],
            pen=None,
            symbol="o",
            symbolSize=7,
            symbolBrush=pg.mkBrush(210, 100, 30, 200),
            symbolPen=pg.mkPen(None),
        )

        layout.addWidget(self._plot_widget)

    # ── Public API ────────────────────────────────────────────────────────────

    def add_point(self, power_a_W: float, power_b_W: float) -> None:
        """Append a paired reading and refresh the series."""
        self._xs.append(power_a_W)
        self._ys.append(power_b_W)
        self._series.setData(self._xs, self._ys)

    def clear(self) -> None:
        """Remove all points."""
        self._xs = []
        self._ys = []
        self._series.setData([], [])
