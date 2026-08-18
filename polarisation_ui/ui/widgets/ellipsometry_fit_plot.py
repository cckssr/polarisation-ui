"""Analyser-sweep fit plot for the Ellipsometry tab.

Accumulates the raw EllipsometryPoint samples of the *current* (still being
measured) angle-of-incidence sweep, shows them as a scatter of power vs.
analyser azimuth, and overlays the fitted harmonic
``I(A) = I0*(1 + alpha*cos(2A) + beta*sin(2A))`` once set_fit() is called
with a RaeFit — this is the tab's live fit-quality feedback.  A small linked
residual strip below the main plot shows point-by-point deviation from the
fit.
"""

import numpy as np
import pyqtgraph as pg
from PySide6.QtWidgets import QVBoxLayout, QWidget

from polarisation_ui.core.ellipsometry import RaeFit
from polarisation_ui.core.models import EllipsometryPoint


class EllipsometryFitPlot(QWidget):
    """Scatter of the current analyser sweep + fitted harmonic overlay + residual strip.

    X axis: analyser azimuth (degrees, offset-corrected relative to the plane
    of incidence). Y axis: detector power (mW).

    All saved points are shown as green circles.  The most recently saved
    point is additionally outlined with a red ring.  The fitted harmonic is
    drawn as a blue curve once set_fit() is called with a valid RaeFit.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build the pyqtgraph plot widgets with an empty point buffer."""
        super().__init__(parent)
        self._points: list[EllipsometryPoint] = []
        self._fit: RaeFit | None = None
        self._setup_plot()

    def _setup_plot(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self._plot_widget = pg.PlotWidget()
        self._plot_widget.setBackground("w")
        self._plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self._plot_widget.setLabel("bottom", "Analysatorazimut", units="°")
        self._plot_widget.setLabel("left", "Leistung", units="mW")

        # All saved points: filled green circles
        self._scatter = self._plot_widget.plot(
            [],
            [],
            pen=None,
            symbol="o",
            symbolSize=7,
            symbolBrush=pg.mkBrush(30, 160, 50, 200),
            symbolPen=pg.mkPen(None),
        )
        # Last saved point: red outline ring (no fill) drawn on top
        self._last_marker = self._plot_widget.plot(
            [],
            [],
            pen=None,
            symbol="o",
            symbolSize=13,
            symbolBrush=pg.mkBrush(0, 0, 0, 0),
            symbolPen=pg.mkPen("r", width=2),
        )
        self._fit_curve = self._plot_widget.plot([], [], pen=pg.mkPen("b", width=2))

        self._residual_widget = pg.PlotWidget()
        self._residual_widget.setBackground("w")
        self._residual_widget.showGrid(x=True, y=True, alpha=0.3)
        self._residual_widget.setLabel("bottom", "Analysatorazimut", units="°")
        self._residual_widget.setLabel("left", "Residuum", units="mW")
        self._residual_widget.setMaximumHeight(90)
        self._residual_widget.setXLink(self._plot_widget)
        self._residual_scatter = self._residual_widget.plot(
            [],
            [],
            pen=None,
            symbol="o",
            symbolSize=5,
            symbolBrush=pg.mkBrush(200, 60, 60, 180),
            symbolPen=pg.mkPen(None),
        )

        layout.addWidget(self._plot_widget, 3)
        layout.addWidget(self._residual_widget, 1)

    def add_point(
        self,
        analyser_angle: float,
        azimuth_deg: float,
        intensity_V: float,
        power_W: float | None = None,
        pdtia_gain: int = 0,
        conv_factor_W_per_V: float | None = None,
        aoi_deg: float = float("nan"),
        detector_angle: float = float("nan"),
    ) -> None:
        """Append a new sweep sample and refresh the plot (fit overlay is unchanged)."""
        self._points.append(
            EllipsometryPoint(
                analyser_angle=analyser_angle,
                azimuth_deg=azimuth_deg,
                intensity_V=intensity_V,
                power_W=power_W,
                pdtia_gain=pdtia_gain,
                conv_factor_W_per_V=conv_factor_W_per_V,
                aoi_deg=aoi_deg,
                detector_angle=detector_angle,
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

    def get_points(self) -> list[EllipsometryPoint]:
        """Return all buffered EllipsometryPoint samples of the current sweep."""
        return list(self._points)

    def clear(self) -> None:
        """Remove all buffered samples and the fit overlay; clear the plot."""
        self._points.clear()
        self._fit = None
        self._refresh()

    def set_fit(self, fit: RaeFit | None) -> None:
        """Set (or clear, with None) the fitted-harmonic overlay and residual strip."""
        self._fit = fit
        self._refresh()

    def _refresh(self) -> None:
        if not self._points:
            self._scatter.setVisible(False)
            self._last_marker.setVisible(False)
            self._fit_curve.setData([], [])
            self._residual_scatter.setData([], [])
            return

        xs = [p.azimuth_deg for p in self._points]
        ys_mw = [p.power_W * 1e3 if p.power_W is not None else float("nan") for p in self._points]
        self._scatter.setData(xs, ys_mw)
        self._scatter.setVisible(True)
        self._last_marker.setData([xs[-1]], [ys_mw[-1]])
        self._last_marker.setVisible(True)

        if self._fit is None or not self._fit.valid:
            self._fit_curve.setData([], [])
            self._residual_scatter.setData([], [])
            return

        fit = self._fit
        az_fit = np.linspace(min(xs) - 2.0, max(xs) + 2.0, 200)
        az_fit_rad = np.radians(az_fit)
        i_fit_mw = fit.i0 * self._harmonic(az_fit_rad, fit.alpha, fit.beta) * 1e3
        self._fit_curve.setData(az_fit.tolist(), i_fit_mw.tolist())

        xs_rad = np.radians(xs)
        model_at_points_mw = fit.i0 * self._harmonic(xs_rad, fit.alpha, fit.beta) * 1e3
        residuals = np.array(ys_mw) - model_at_points_mw
        self._residual_scatter.setData(xs, residuals.tolist())

    @staticmethod
    def _harmonic(azimuth_rad: np.ndarray, alpha: float, beta: float) -> np.ndarray:
        """1 + alpha*cos(2A) + beta*sin(2A), the normalised RAE harmonic shape."""
        return 1 + alpha * np.cos(2 * azimuth_rad) + beta * np.sin(2 * azimuth_rad)
