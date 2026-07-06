"""Live detector scan plot for Brewster tab.

Shows detector arm angle (X) vs. intensity (Y) as the user sweeps the arm.
A rolling buffer of recent samples forms the curve; angle debouncing suppresses
duplicate readings when the detector is stationary.  The peak intensity sample
is highlighted with a red marker to assist in finding the optimal position.
"""

from collections import deque

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QVBoxLayout, QWidget


class BrewsterDetectorPlot(QWidget):
    """Live rolling scatter: detector angle vs. intensity.

    Accepts samples at the incoming poll rate but only appends a new point when
    the angle has moved by at least MIN_ANGLE_DELTA degrees, suppressing noise
    when the detector arm is stationary.  Keeps the last MAX_POINTS samples and
    highlights the maximum-intensity point with a red star and a vertical line.
    """

    MAX_POINTS: int = 300
    MIN_ANGLE_DELTA: float = 0.05  # degrees

    # Emitted on every refresh: (max_intensity, max_angle).  Both are nan when
    # the buffer is empty.
    peak_changed = Signal(float, float)

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build the pyqtgraph plot widget with empty rolling buffers."""
        super().__init__(parent)
        self._angles: deque[float] = deque(maxlen=self.MAX_POINTS)
        self._intensities: deque[float] = deque(maxlen=self.MAX_POINTS)
        self._last_angle: float | None = None
        self._setup_plot()

    def _setup_plot(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._plot_widget = pg.PlotWidget()
        self._plot_widget.setBackground("w")
        self._plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self._plot_widget.setLabel("bottom", "Detektorwinkel", units="°")
        self._plot_widget.setLabel("left", "Intensität", units="V")

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
        # Vertical line at peak angle
        self._peak_line = pg.InfiniteLine(
            angle=90,
            movable=False,
            pen=pg.mkPen(color=(200, 30, 30), width=1.5, style=Qt.PenStyle.DashLine),
        )
        self._peak_line.setVisible(False)
        self._plot_widget.addItem(self._peak_line)

        layout.addWidget(self._plot_widget)

    @Slot(float, float)
    def update_data(self, detector_angle: float, intensity: float) -> None:
        """Accept a new (angle, intensity) sample.

        A point is only appended when the detector angle has moved by at least
        MIN_ANGLE_DELTA degrees since the last accepted sample.  NaN intensity
        (no ADC reading) is silently dropped.
        """
        if np.isnan(intensity):
            return
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
            # Avoid setData([], []) on ScatterPlotItem — empty arrays trigger
            # np.nanmin on an all-NaN slice and produce a RuntimeWarning.
            self._curve.setVisible(False)
            self._peak.setVisible(False)
            self._peak_line.setVisible(False)
            self.peak_changed.emit(float("nan"), float("nan"))
            return

        angles = list(self._angles)
        intensities = list(self._intensities)
        self._curve.setData(angles, intensities)
        self._curve.setVisible(True)

        peak_idx = int(np.argmax(intensities))
        peak_angle = angles[peak_idx]
        peak_intensity = intensities[peak_idx]

        self._peak.setData([peak_angle], [peak_intensity])
        self._peak.setVisible(True)
        self._peak_line.setPos(peak_angle)
        self._peak_line.setVisible(True)
        self.peak_changed.emit(peak_intensity, peak_angle)
