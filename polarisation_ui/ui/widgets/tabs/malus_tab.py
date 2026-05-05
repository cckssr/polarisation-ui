"""
Malus-law experiment tab.

Owns both plots (live detector scan + manually saved Malus curve) and the
Save / Delete-point controls.  Data arrives via on_frame(); the tab stores
the latest frame so the Save button can snapshot current values on demand.
"""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QGridLayout,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QWidget,
)

from polarisation_ui.core.models import Frame
from polarisation_ui.ui.widgets.malus_curve_plot import MalusCurvePlot
from polarisation_ui.ui.widgets.malus_detector_plot import MalusDetectorPlot
from polarisation_ui.ui.widgets.plot_tab_base import ConnState, PlotTabBase


class MalusTab(PlotTabBase):
    tab_id = "malus"
    tab_title = "Malus"
    required_sources: set[str] = {"ENC:BOTH", "ADC"}
    required_modules: set[str] = set()

    points_changed = Signal(
        int
    )  # emits current point count after every add/remove/clear

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._latest_frame: Optional[Frame] = None
        self._detector_plot: Optional[MalusDetectorPlot] = None
        self._curve_plot: Optional[MalusCurvePlot] = None
        self._btn_save: Optional[QPushButton] = None
        self._btn_delete: Optional[QPushButton] = None
        self._btn_clear_detector: Optional[QPushButton] = None

    def build(self) -> None:
        layout = QGridLayout(self)
        layout.setContentsMargins(5, 10, 10, 5)
        layout.setRowStretch(0, 3)
        layout.setRowStretch(1, 2)
        layout.setColumnStretch(0, 1)

        self._detector_plot = MalusDetectorPlot()
        layout.addWidget(self._detector_plot, 0, 0)

        self._btn_clear_detector = QPushButton("Detektorgraph\nlöschen")
        self._btn_clear_detector.setToolTip(
            "Löscht alle Punkte im oberen Detektorwinkel-Intensitäts-Graphen"
        )
        layout.addWidget(self._btn_clear_detector, 0, 1, Qt.AlignmentFlag.AlignTop)
        self._btn_clear_detector.clicked.connect(self._clear_detector_plot)

        self._curve_plot = MalusCurvePlot()
        layout.addWidget(self._curve_plot, 1, 0, 3, 1)

        layout.addItem(
            QSpacerItem(
                20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
            ),
            1,
            1,
        )

        self._btn_delete = QPushButton("Letzten Punkt\nlöschen")
        layout.addWidget(self._btn_delete, 2, 1)
        self._btn_delete.clicked.connect(self._delete_last_point)

        self._btn_save = QPushButton("Punkt\nspeichern")
        layout.addWidget(self._btn_save, 3, 1)
        self._btn_save.clicked.connect(self._save_point)

    def on_frame(self, frame: Frame) -> None:
        self._latest_frame = frame
        if self._detector_plot is not None:
            self._detector_plot.update_data(frame.detector_angle, frame.intensity)

    def on_reset(self) -> None:
        if self._detector_plot is not None:
            self._detector_plot.clear()
        if self._curve_plot is not None:
            self._curve_plot.clear()
        self.points_changed.emit(0)

    def on_connection_state(self, state: ConnState) -> None:
        pass

    def on_activated(self) -> None:
        pass

    def on_deactivated(self) -> None:
        pass

    def inject_modules(self, modules: dict[str, object]) -> None:
        pass

    def get_malus_points(self) -> list[tuple[float, float, float]]:
        """Return all saved (sample_angle, detector_angle, intensity) triples for export."""
        if self._curve_plot is None:
            return []
        return self._curve_plot.get_points()

    @Slot()
    def _save_point(self) -> None:
        if self._latest_frame is not None and self._curve_plot is not None:
            self._curve_plot.add_point(
                self._latest_frame.sample_angle,
                self._latest_frame.detector_angle,
                self._latest_frame.intensity,
            )
            self.points_changed.emit(len(self._curve_plot.get_points()))

    @Slot()
    def _clear_detector_plot(self) -> None:
        if self._detector_plot is not None:
            self._detector_plot.clear()

    @Slot()
    def _delete_last_point(self) -> None:
        if self._curve_plot is None:
            return
        if not self._curve_plot.remove_last_point():
            self.status_message.emit("warning", "Keine Punkte zum Löschen")
        else:
            self.points_changed.emit(len(self._curve_plot.get_points()))
