"""ND-filter linearity plot.

Two stacked pyqtgraph plots sharing the angle axis:

* top — optical power (log scale) vs. wheel angle, one curve per scan, drawn
  live while the scans run;
* bottom — deviation of the optical density from the straight-line fit, one
  curve per scan, filled in as each scan completes, with the tolerance band.

Forward scans are drawn solid, backward scans dashed, so hysteresis is visible
at a glance.

This is a pyqtgraph custom widget — constructing Qt objects in Python is an
explicit exception per CLAUDE.md for pyqtgraph widgets.
"""

from collections.abc import Sequence

import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtGui import QPen
from PySide6.QtWidgets import QVBoxLayout, QWidget

from polarisation_ui.core.nd_linearity import BACKWARD

_PALETTE: tuple[tuple[int, int, int], ...] = (
    (31, 119, 180),
    (214, 39, 40),
    (44, 160, 44),
    (255, 127, 14),
    (148, 103, 189),
    (140, 86, 75),
    (227, 119, 194),
    (23, 190, 207),
)


class NDLinearityPlot(QWidget):
    """Live power curves plus residual curves for repeated ND-wheel scans."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build both plots with no data."""
        super().__init__(parent)
        self._power_curves: dict[int, pg.PlotDataItem] = {}
        self._power_data: dict[int, tuple[list[float], list[float]]] = {}
        self._resid_curves: dict[int, pg.PlotDataItem] = {}
        self._setup_plots()

    def _setup_plots(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._power_plot = pg.PlotWidget()
        self._power_plot.setBackground("w")
        self._power_plot.showGrid(x=True, y=True, alpha=0.3)
        self._power_plot.setLabel("left", "Optische Leistung", units="W")
        self._power_plot.setLogMode(y=True)
        self._power_plot.addLegend(offset=(-10, 10))

        self._resid_plot = pg.PlotWidget()
        self._resid_plot.setBackground("w")
        self._resid_plot.showGrid(x=True, y=True, alpha=0.3)
        self._resid_plot.setLabel("bottom", "Winkel", units="°")
        self._resid_plot.setLabel("left", "Abweichung vom linearen OD-Fit", units="OD")
        self._resid_plot.setXLink(self._power_plot)

        band_pen = pg.mkPen((120, 120, 120), width=1, style=Qt.PenStyle.DashLine)
        self._tol_upper = self._resid_plot.addLine(y=0.0, pen=band_pen)
        self._tol_lower = self._resid_plot.addLine(y=0.0, pen=band_pen)
        self._tol_upper.setVisible(False)
        self._tol_lower.setVisible(False)
        self._resid_plot.addLine(y=0.0, pen=pg.mkPen((0, 0, 0), width=1))

        layout.addWidget(self._power_plot, 3)
        layout.addWidget(self._resid_plot, 2)

    @staticmethod
    def _pen(index: int, direction: str) -> QPen:
        colour = _PALETTE[index % len(_PALETTE)]
        style = Qt.PenStyle.DashLine if direction == BACKWARD else Qt.PenStyle.SolidLine
        return pg.mkPen(colour, width=1.5, style=style)

    # ── Public API ────────────────────────────────────────────────────────────

    def begin_scan(self, index: int, direction: str) -> None:
        """Start a new power curve for scan *index* (zero-based)."""
        label = f"Scan {index + 1} ({'rückwärts' if direction == BACKWARD else 'vorwärts'})"
        colour = _PALETTE[index % len(_PALETTE)]
        self._power_data[index] = ([], [])
        self._power_curves[index] = self._power_plot.plot(
            [],
            [],
            pen=self._pen(index, direction),
            symbol="o",
            symbolSize=5,
            symbolBrush=pg.mkBrush(*colour, 200),
            symbolPen=pg.mkPen(None),
            name=label,
        )

    def add_point(self, index: int, position_deg: float, power_W: float) -> None:
        """Append a live point to scan *index*'s power curve."""
        if index not in self._power_curves:
            return
        xs, ys = self._power_data[index]
        xs.append(position_deg)
        ys.append(power_W)
        self._power_curves[index].setData(xs, ys)

    def set_residuals(
        self,
        index: int,
        direction: str,
        positions_deg: Sequence[float],
        residuals_od: Sequence[float],
    ) -> None:
        """Show (or replace) the OD-residual curve of scan *index*."""
        curve = self._resid_curves.get(index)
        if curve is None:
            curve = self._resid_plot.plot(
                [], [], pen=self._pen(index, direction), symbol="o", symbolSize=4
            )
            curve.setSymbolBrush(pg.mkBrush(*_PALETTE[index % len(_PALETTE)], 200))
            self._resid_curves[index] = curve
        curve.setData(list(positions_deg), list(residuals_od))

    def set_tolerance(self, tolerance_od: float | None) -> None:
        """Draw the ±tolerance band on the residual plot (``None`` hides it)."""
        visible = tolerance_od is not None and tolerance_od > 0.0
        self._tol_upper.setVisible(visible)
        self._tol_lower.setVisible(visible)
        if visible and tolerance_od is not None:
            self._tol_upper.setValue(tolerance_od)
            self._tol_lower.setValue(-tolerance_od)

    def clear(self) -> None:
        """Remove every curve."""
        for curve in self._power_curves.values():
            self._power_plot.removeItem(curve)
        for curve in self._resid_curves.values():
            self._resid_plot.removeItem(curve)
        self._power_curves.clear()
        self._power_data.clear()
        self._resid_curves.clear()
        legend = self._power_plot.plotItem.legend
        if legend is not None:
            legend.clear()
