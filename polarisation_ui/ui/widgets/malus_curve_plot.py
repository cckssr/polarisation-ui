"""Malus-law curve plot for Malus tab.

Accumulates manually saved MalusPoint entries (user-entered analyser angles)
and displays them as a scatter plot.  Points are added via add_point() and
removed via remove_last_point() or remove_point_at().
"""

import pyqtgraph as pg
from PySide6.QtWidgets import QVBoxLayout, QWidget

from polarisation_ui.core.models import MalusPoint


class MalusCurvePlot(QWidget):
    """Scatter plot of saved Malus-law measurement points.

    X axis: analyser angle (degrees, user-entered)
    Y axis: detector intensity (V, averaged over ~0.5 s window)

    All saved points are shown as green circles.  The most recently saved point
    is additionally outlined with a red ring so the user can see the last entry.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build the pyqtgraph plot widget with an empty point buffer."""
        super().__init__(parent)
        self._points: list[MalusPoint] = []
        self._setup_plot()

    def _setup_plot(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._plot_widget = pg.PlotWidget()
        self._plot_widget.setBackground("w")
        self._plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self._plot_widget.setLabel("bottom", "Analysatorwinkel", units="°")
        self._plot_widget.setLabel("left", "Intensität", units="V")

        # All saved points: filled green circles
        self._scatter = self._plot_widget.plot(
            [],
            [],
            pen=None,
            symbol="o",
            symbolSize=8,
            symbolBrush=pg.mkBrush(30, 160, 50, 200),
            symbolPen=pg.mkPen(None),
        )
        # Last saved point: red outline ring (no fill) drawn on top
        self._last_marker = self._plot_widget.plot(
            [],
            [],
            pen=None,
            symbol="o",
            symbolSize=14,
            symbolBrush=pg.mkBrush(0, 0, 0, 0),  # transparent fill
            symbolPen=pg.mkPen("r", width=2),
        )

        layout.addWidget(self._plot_widget)

    def add_point(
        self,
        analyser_angle: float,
        polariser_angle: float,
        intensity_V: float,
        pdtia_gain: int = 0,
        power_W: float | None = None,
        conv_factor_W_per_V: float | None = None,
        detector: str = "pdtia",
    ) -> None:
        """Append a new measurement point and refresh the plot."""
        self._points.append(
            MalusPoint(
                analyser_angle=analyser_angle,
                polariser_angle=polariser_angle,
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

    def get_points(self) -> list[MalusPoint]:
        """Return all saved MalusPoint entries."""
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

        xs = [p.analyser_angle for p in self._points]

        use_power = all(p.power_W is not None for p in self._points)
        if use_power:
            ys = [p.power_W * 1e3 for p in self._points]  # type: ignore[operator]
            self._plot_widget.setLabel("left", "Leistung", units="mW")
        else:
            ys = [p.intensity_V for p in self._points]
            self._plot_widget.setLabel("left", "Intensität", units="V")

        self._scatter.setData(xs, ys)
        self._scatter.setVisible(True)
        self._last_marker.setData([xs[-1]], [ys[-1]])
        self._last_marker.setVisible(True)
