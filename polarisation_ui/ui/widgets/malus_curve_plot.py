"""
Malus-law curve plot for Malus tab.

Accumulates manually saved (sample angle, intensity) pairs and displays them
as a scatter plot.  Points are added via add_point() (Save button) and removed
one at a time via remove_last_point() (Delete button).
"""

from typing import Optional

import pyqtgraph as pg
from PySide6.QtWidgets import QVBoxLayout, QWidget


class MalusCurvePlot(QWidget):
    """
    Scatter plot of saved Malus-law measurement points.

    X axis: sample stage angle (degrees)
    Y axis: detector intensity (a.u.)

    All saved points are shown as green circles.  The most recently saved point
    is additionally outlined with a red ring so the user can see the last entry.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._sample_angles: list[float] = []
        self._detector_angles: list[float] = []
        self._intensities: list[float] = []
        self._setup_plot()

    def _setup_plot(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._plot_widget = pg.PlotWidget()
        self._plot_widget.setBackground("w")
        self._plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self._plot_widget.setLabel("bottom", "Probenwinkel", units="°")
        self._plot_widget.setLabel("left", "Intensität", units="a.u.")

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

    def add_point(self, sample_angle: float, detector_angle: float, intensity: float) -> None:
        """Append a new measurement point and refresh the plot."""
        self._sample_angles.append(sample_angle)
        self._detector_angles.append(detector_angle)
        self._intensities.append(intensity)
        self._refresh()

    def remove_last_point(self) -> bool:
        """
        Remove the most recently added point.

        Returns:
            True if a point was removed, False if the list was already empty.
        """
        if not self._sample_angles:
            return False
        self._sample_angles.pop()
        self._detector_angles.pop()
        self._intensities.pop()
        self._refresh()
        return True

    def get_points(self) -> list[tuple[float, float, float]]:
        """Return all saved (sample_angle, detector_angle, intensity) triples."""
        return list(zip(self._sample_angles, self._detector_angles, self._intensities))

    def clear(self) -> None:
        """Remove all saved points and clear the plot."""
        self._sample_angles.clear()
        self._detector_angles.clear()
        self._intensities.clear()
        self._refresh()

    def _refresh(self) -> None:
        if not self._sample_angles:
            self._scatter.setData([], [])
            self._last_marker.setData([], [])
            return

        self._scatter.setData(self._sample_angles, self._intensities)
        self._last_marker.setData([self._sample_angles[-1]], [self._intensities[-1]])
