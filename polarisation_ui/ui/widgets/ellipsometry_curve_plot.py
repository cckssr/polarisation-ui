"""Psi(theta)/Delta(theta) series plot for the Ellipsometry tab.

The variable-angle-of-incidence series is the plot commercial ellipsometer
software leads with: Psi and Delta, each with its own AOI-dependent shape and
scale, sharing one angle-of-incidence X axis.  Displaying that requires two
independently-scaled Y axes on one plot — pyqtgraph has no built-in widget for
this, so it is built from the documented "MultiplePlotAxes" recipe: a second
``pg.ViewBox`` added to the same scene as the PlotWidget's own view, linked in
X only, with its own right-hand AxisItem.
"""

import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget

from polarisation_ui.core.models import EllipsometrySeriesPoint

_PSI_COLOR = (30, 100, 200)
_DELTA_COLOR = (200, 80, 30)


class EllipsometryCurvePlot(QWidget):
    """Psi(theta) / Delta(theta) series scatter with twin Y axes and an optional model overlay.

    X axis: angle of incidence (degrees). Left Y axis: Psi (blue, degrees).
    Right Y axis: Delta (orange, degrees). set_model() overlays a dashed
    curve pair from a fitted optical model; clear_model() removes it without
    touching the measured series.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build the twin-axis pyqtgraph plot with an empty point buffer."""
        super().__init__(parent)
        self._points: list[EllipsometrySeriesPoint] = []
        self._setup_plot()

    def _setup_plot(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._plot_widget = pg.PlotWidget()
        self._plot_widget.setBackground("w")
        self._plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self._plot_widget.setLabel("bottom", "Einfallswinkel θ", units="°")
        self._plot_widget.setLabel("left", "Ψ", units="°")

        self._plot_widget.showAxis("right")
        self._delta_viewbox = pg.ViewBox()
        self._plot_widget.scene().addItem(self._delta_viewbox)
        self._plot_widget.getAxis("right").linkToView(self._delta_viewbox)
        self._delta_viewbox.setXLink(self._plot_widget)
        self._plot_widget.getAxis("right").setLabel("Δ", units="°")

        def _sync_delta_view() -> None:
            main_vb = self._plot_widget.getViewBox()
            self._delta_viewbox.setGeometry(main_vb.sceneBoundingRect())
            self._delta_viewbox.linkedViewChanged(main_vb, self._delta_viewbox.XAxis)

        self._plot_widget.getViewBox().sigResized.connect(_sync_delta_view)
        _sync_delta_view()

        self._psi_scatter = self._plot_widget.plot(
            [],
            [],
            pen=None,
            symbol="o",
            symbolSize=8,
            symbolBrush=pg.mkBrush(*_PSI_COLOR, 200),
            symbolPen=pg.mkPen(None),
        )
        self._delta_scatter = pg.ScatterPlotItem(
            size=8, brush=pg.mkBrush(*_DELTA_COLOR, 200), pen=pg.mkPen(None)
        )
        self._delta_viewbox.addItem(self._delta_scatter)

        self._psi_model = self._plot_widget.plot(
            [], [], pen=pg.mkPen(_PSI_COLOR, width=2, style=Qt.PenStyle.DashLine)
        )
        self._delta_model = pg.PlotDataItem(
            [], [], pen=pg.mkPen(_DELTA_COLOR, width=2, style=Qt.PenStyle.DashLine)
        )
        self._delta_viewbox.addItem(self._delta_model)

        layout.addWidget(self._plot_widget)

    def set_series(self, points: list[EllipsometrySeriesPoint]) -> None:
        """Replace the displayed (theta, Psi, Delta) series and refresh both scatters."""
        self._points = list(points)
        self._refresh()

    def set_model(self, aoi_deg: list[float], psi_deg: list[float], delta_deg: list[float]) -> None:
        """Overlay a dashed (Psi, Delta) model curve, e.g. from a fitted FilmFit."""
        self._psi_model.setData(list(aoi_deg), list(psi_deg))
        self._delta_model.setData(list(aoi_deg), list(delta_deg))

    def clear_model(self) -> None:
        """Remove the model overlay, leaving the measured series untouched."""
        self._psi_model.setData([], [])
        self._delta_model.setData([], [])

    def clear(self) -> None:
        """Remove the measured series and the model overlay."""
        self._points = []
        self.clear_model()
        self._refresh()

    def _refresh(self) -> None:
        if not self._points:
            self._psi_scatter.setData([], [])
            self._delta_scatter.setData([], [])
            return
        xs = [p.aoi_deg for p in self._points]
        psi = [p.psi_deg for p in self._points]
        delta = [p.delta_deg for p in self._points]
        self._psi_scatter.setData(xs, psi)
        self._delta_scatter.setData(xs, delta)
