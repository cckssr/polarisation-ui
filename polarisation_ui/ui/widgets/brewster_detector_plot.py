"""Live detector scan plot for Brewster tab.

Shows detector arm angle (X) vs. intensity (Y) as the user sweeps the arm.
A rolling buffer of recent samples forms the curve; angle debouncing suppresses
duplicate readings when the detector is stationary.  The peak intensity sample
is highlighted with a marker to assist in finding the optimal position.
"""

from __future__ import annotations

from collections import deque

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import QVBoxLayout, QWidget

from polarisation_ui.infrastructure.config import AppConfig, default_config
from polarisation_ui.ui.plot_style import plot_colors, style_plot


class BrewsterDetectorPlot(QWidget):
    """Live rolling scatter: detector angle vs. intensity.

    Accepts samples at the incoming poll rate but only appends a new point when
    the angle has moved by at least MIN_ANGLE_DELTA degrees, suppressing noise
    when the detector arm is stationary.  Keeps the last MAX_POINTS samples and
    highlights the maximum-intensity point with a star and a vertical line.
    """

    MAX_POINTS: int = 300
    MIN_ANGLE_DELTA: float = 0.05  # degrees

    # Emitted on every refresh: (max_intensity, max_angle).  Both are nan when
    # the buffer is empty.
    peak_changed = Signal(float, float)

    def __init__(self, parent: QWidget | None = None, config: AppConfig | None = None) -> None:
        """Build the pyqtgraph plot widget with empty rolling buffers.

        The axis labels come from ``ui.plots`` in the configuration (default: ``default_config()``);
        an owning tab passes its own configuration through :meth:`apply_config`.
        """
        super().__init__(parent)
        self._config: AppConfig = config if config is not None else default_config()
        self._angles: deque[float] = deque(maxlen=self.MAX_POINTS)
        self._intensities: deque[float] = deque(maxlen=self.MAX_POINTS)
        self._last_angle: float | None = None
        self._power_mode: bool = False
        self._setup_plot()

    def set_power_mode(self, enabled: bool) -> None:
        """Switch the Y axis between PD-TIA intensity (V) and PM400 power (W).

        Call whenever the active detector changes (see ``core.detector``);
        does nothing but relabel the axis — the caller is responsible for
        feeding the matching quantity to ``update_data()``.
        """
        if enabled == self._power_mode:
            return
        self._power_mode = enabled
        self._apply_axis_labels()

    def apply_config(self, config: AppConfig) -> None:
        """Take the axis labels from ``config``."""
        self._config = config
        self._apply_axis_labels()

    def _apply_axis_labels(self) -> None:
        text = self._config.text
        self._plot_widget.setLabel(
            "bottom",
            text("plots.brewster_detector_x_label"),
            units=text("plots.brewster_detector_x_units"),
        )
        quantity = "power" if self._power_mode else "intensity"
        self._plot_widget.setLabel(
            "left",
            text(f"plots.brewster_detector_{quantity}_label"),
            units=text(f"plots.brewster_detector_{quantity}_units"),
        )

    def _setup_plot(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        colors = plot_colors()
        self._plot_widget = pg.PlotWidget()
        self._plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self._apply_axis_labels()

        # All buffered points: small dots
        self._curve = self._plot_widget.plot(
            [],
            [],
            pen=None,
            symbol="o",
            symbolSize=4,
            symbolBrush=pg.mkBrush(*colors.series_color(0), colors.point_alpha),
            symbolPen=pg.mkPen(None),
        )
        # Peak marker: star
        self._peak = self._plot_widget.plot(
            [],
            [],
            pen=None,
            symbol="star",
            symbolSize=14,
            symbolBrush=pg.mkBrush(*colors.marker, colors.point_alpha),
            symbolPen=pg.mkPen(None),
        )
        # Vertical line at peak angle
        self._peak_line = pg.InfiniteLine(
            angle=90,
            movable=False,
            pen=pg.mkPen(color=colors.marker, width=1.5, style=Qt.PenStyle.DashLine),
        )
        self._peak_line.setVisible(False)
        self._plot_widget.addItem(self._peak_line)

        style_plot(self._plot_widget)
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
