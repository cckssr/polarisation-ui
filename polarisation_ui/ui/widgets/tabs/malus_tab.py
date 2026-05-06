"""
Malus-law experiment tab.

Owns both plots (live detector scan + manually saved Malus curve) and the
Save / Delete-point controls.  Data arrives via on_frame(); the tab stores
the latest frame so the Save button can snapshot current values on demand.
"""

from __future__ import annotations

import math
from typing import Optional

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
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
        self._btn_delete_selected: Optional[QPushButton] = None
        self._btn_clear_detector: Optional[QPushButton] = None
        self._lbl_max_intensity: Optional[QLabel] = None
        self._lbl_max_angle: Optional[QLabel] = None
        self._points_table: Optional[QTableWidget] = None

    def build(self) -> None:
        layout = QGridLayout(self)
        layout.setContentsMargins(5, 10, 10, 5)
        layout.setRowStretch(0, 3)
        layout.setRowStretch(1, 2)
        layout.setColumnStretch(0, 1)

        self._detector_plot = MalusDetectorPlot()
        layout.addWidget(self._detector_plot, 0, 0)

        self._curve_plot = MalusCurvePlot()
        layout.addWidget(self._curve_plot, 1, 0, 3, 1)

        # --- Right panel (spans all rows in column 1) ---
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(4, 0, 0, 0)
        right_layout.setSpacing(6)

        self._btn_clear_detector = QPushButton("Detektorgraph\nlöschen")
        self._btn_clear_detector.setToolTip(
            "Löscht alle Punkte im oberen Detektorwinkel-Intensitäts-Graphen"
        )
        self._btn_clear_detector.setEnabled(False)
        self._btn_clear_detector.clicked.connect(self._clear_detector_plot)
        right_layout.addWidget(self._btn_clear_detector)

        # Max-intensity readout
        max_group = QGroupBox("Maximum")
        max_form = QFormLayout(max_group)
        max_form.setContentsMargins(6, 4, 6, 4)
        max_form.setVerticalSpacing(2)
        self._lbl_max_intensity = QLabel("—")
        self._lbl_max_angle = QLabel("—")
        max_form.addRow("I:", self._lbl_max_intensity)
        max_form.addRow("θ:", self._lbl_max_angle)
        right_layout.addWidget(max_group)

        right_layout.addStretch(1)

        # Saved-points table
        self._points_table = QTableWidget(0, 3)
        self._points_table.setHorizontalHeaderLabels(["θ_S (°)", "θ_D (°)", "I (V)"])
        self._points_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self._points_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self._points_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._points_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._points_table.setMinimumHeight(80)
        self._points_table.setMaximumHeight(200)
        self._points_table.verticalHeader().setVisible(False)
        self._points_table.itemSelectionChanged.connect(
            self._on_table_selection_changed
        )
        right_layout.addWidget(self._points_table)

        self._btn_delete_selected = QPushButton("Ausgewählten\nlöschen")
        self._btn_delete_selected.setToolTip("Markierten Punkt aus der Kurve löschen")
        self._btn_delete_selected.setEnabled(False)
        self._btn_delete_selected.clicked.connect(self._delete_selected_point)
        right_layout.addWidget(self._btn_delete_selected)

        self._btn_delete = QPushButton("Letzten Punkt\nlöschen")
        self._btn_delete.setEnabled(False)
        self._btn_delete.clicked.connect(self._delete_last_point)
        right_layout.addWidget(self._btn_delete)

        self._btn_save = QPushButton("Punkt\nspeichern")
        self._btn_save.setEnabled(False)
        self._btn_save.clicked.connect(self._save_point)
        right_layout.addWidget(self._btn_save)

        layout.addWidget(right_panel, 0, 1, 4, 1)

        # Wire peak signal → labels
        self._detector_plot.peak_changed.connect(self._update_max_labels)

    def on_frame(self, frame: Frame) -> None:
        self._latest_frame = frame
        if self._detector_plot is not None:
            self._detector_plot.update_data(frame.detector_angle, frame.intensity)

    def on_reset(self) -> None:
        if self._detector_plot is not None:
            self._detector_plot.clear()
        if self._curve_plot is not None:
            self._curve_plot.clear()
        self._refresh_table()
        self.points_changed.emit(0)

    def on_connection_state(self, state: ConnState) -> None:
        pass

    def on_activated(self) -> None:
        pass

    def on_deactivated(self) -> None:
        pass

    def on_measurement_started(self) -> None:
        for btn in (
            self._btn_clear_detector,
            self._btn_delete,
            self._btn_save,
        ):
            if btn is not None:
                btn.setEnabled(True)
        # delete-selected stays gated on table selection
        self._on_table_selection_changed()

    def on_measurement_stopped(self) -> None:
        for btn in (
            self._btn_clear_detector,
            self._btn_delete,
            self._btn_delete_selected,
            self._btn_save,
        ):
            if btn is not None:
                btn.setEnabled(False)

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
            self._refresh_table()
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
            self._refresh_table()
            self.points_changed.emit(len(self._curve_plot.get_points()))

    @Slot()
    def _delete_selected_point(self) -> None:
        if self._curve_plot is None or self._points_table is None:
            return
        selected = self._points_table.selectedItems()
        if not selected:
            return
        row = self._points_table.currentRow()
        if not self._curve_plot.remove_point_at(row):
            self.status_message.emit("warning", "Punkt konnte nicht gelöscht werden")
        else:
            self._refresh_table()
            self.points_changed.emit(len(self._curve_plot.get_points()))

    @Slot(float, float)
    def _update_max_labels(self, intensity: float, angle: float) -> None:
        if self._lbl_max_intensity is None or self._lbl_max_angle is None:
            return
        if math.isnan(intensity):
            self._lbl_max_intensity.setText("—")
            self._lbl_max_angle.setText("—")
        else:
            self._lbl_max_intensity.setText(f"{intensity:.4f} V")
            self._lbl_max_angle.setText(f"{angle:.2f}°")

    def _refresh_table(self) -> None:
        if self._points_table is None or self._curve_plot is None:
            return
        points = self._curve_plot.get_points()
        self._points_table.setRowCount(len(points))
        for row, (sa, da, intensity) in enumerate(points):
            self._points_table.setItem(row, 0, QTableWidgetItem(f"{sa:.3f}"))
            self._points_table.setItem(row, 1, QTableWidgetItem(f"{da:.3f}"))
            self._points_table.setItem(row, 2, QTableWidgetItem(f"{intensity:.6f}"))
        self._on_table_selection_changed()

    @Slot()
    def _on_table_selection_changed(self) -> None:
        if self._btn_delete_selected is None or self._points_table is None:
            return
        # Only enable if measurement is running (btn_save is a proxy for that state)
        measuring = self._btn_save is not None and self._btn_save.isEnabled()
        has_selection = bool(self._points_table.selectedItems())
        self._btn_delete_selected.setEnabled(measuring and has_selection)
