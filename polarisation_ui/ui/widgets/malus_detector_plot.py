"""
Live detector scan plot for Malus tab.

Shows detector arm angle (X) vs. intensity (Y) as the user sweeps the arm.
A rolling buffer of recent samples forms the curve; angle debouncing suppresses
duplicate readings when the detector is stationary.  The peak intensity sample
is highlighted with a red marker to assist in finding the optimal position.
"""

from collections import deque
from typing import Optional

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QVBoxLayout, QWidget


class MalusDetectorPlot(QWidget):
    """
    Live rolling scatter: detector angle vs. intensity.

    Accepts samples at the incoming poll rate but only appends a new point when
    the angle has moved by at least MIN_ANGLE_DELTA degrees, suppressing noise
    when the detector arm is stationary.  Keeps the last MAX_POINTS samples and
    highlights the maximum-intensity point with a red star.
    """

    MAX_POINTS: int = 300
    MIN_ANGLE_DELTA: float = 0.05  # degrees

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._angles: deque[float] = deque(maxlen=self.MAX_POINTS)
        self._intensities: deque[float] = deque(maxlen=self.MAX_POINTS)
        self._last_angle: Optional[float] = None
        self._setup_plot()

    def _setup_plot(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._plot_widget = pg.PlotWidget()
        self._plot_widget.setBackground("w")
        self._plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self._plot_widget.setLabel("bottom", "Detektorwinkel", units="°")
        self._plot_widget.setLabel("left", "Intensität", units="a.u.")

        # All buffered points: small blue dots
        self._curve = self._plot_widget.plot(
            [],
            [],
            pen=None,
            symbol="o",
            symbolSize=4,
            symbolBrush=pg.mkBrush(0, 100, 200, 180),
            symbolPen=pg.mkPen(None),
        )
        # Peak marker: red star
        self._peak = self._plot_widget.plot(
            [],
            [],
            pen=None,
            symbol="star",
            symbolSize=14,
            symbolBrush=pg.mkBrush(200, 30, 30, 220),
            symbolPen=pg.mkPen(None),
        )

        layout.addWidget(self._plot_widget)

    @Slot(float, float)
    def update_data(self, detector_angle: float, intensity: float) -> None:
        """
        Accept a new (angle, intensity) sample.

        A point is only appended when the detector angle has moved by at least
        MIN_ANGLE_DELTA degrees since the last accepted sample.
        """
        if (
            self._last_angle is None
            or abs(detector_angle - self._last_angle) >= self.MIN_ANGLE_DELTA
        ):
            self._angles.append(detector_angle)
            self._intensities.append(intensity)
            self._last_angle = detector_angle
            self._refresh()

    def clear(self) -> None:
        """Clear all buffered data and reset the plot."""
        self._angles.clear()
        self._intensities.clear()
        self._last_angle = None
        self._refresh()

    def _refresh(self) -> None:
        if not self._angles:
            self._curve.setData([], [])
            self._peak.setData([], [])
            return

        angles = list(self._angles)
        intensities = list(self._intensities)
        self._curve.setData(angles, intensities)

        peak_idx = int(np.argmax(intensities))
        self._peak.setData([angles[peak_idx]], [intensities[peak_idx]])
