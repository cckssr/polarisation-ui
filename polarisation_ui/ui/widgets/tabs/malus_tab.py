"""
Malus-law experiment tab.

Owns both plots (live detector scan + manually saved Malus curve) and the
Save / Delete-point controls.  Data arrives via on_frame(); the tab stores
the latest frame so the Save buttons can snapshot values on demand.

Two save modes:
  - "Aktuell speichern": snapshot the *current* live ADC reading.
  - "Maximum speichern": snapshot the *peak* intensity found in the detector
    scan above and clear the detector curve afterwards.

Both modes reset the detector scan after saving so the next sweep starts clean.
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

from polarisation_ui.core.models import Frame, MalusPoint
from polarisation_ui.core.power_calibration import PowerCalibrationProfile
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
        self._calibration_profile: Optional[PowerCalibrationProfile] = None
        self._detector_plot: Optional[MalusDetectorPlot] = None
        self._curve_plot: Optional[MalusCurvePlot] = None
        self._btn_save_current: Optional[QPushButton] = None
        self._btn_save_max: Optional[QPushButton] = None
        self._btn_delete: Optional[QPushButton] = None
        self._btn_delete_selected: Optional[QPushButton] = None
        self._btn_clear_detector: Optional[QPushButton] = None
        self._lbl_max_intensity: Optional[QLabel] = None
        self._lbl_max_angle: Optional[QLabel] = None
        self._points_table: Optional[QTableWidget] = None
        # cached peak from detector plot (intensity, angle)
        self._peak_intensity: float = float("nan")
        self._peak_angle: float = float("nan")

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
        self._points_table = QTableWidget(0, 5)
        self._points_table.setHorizontalHeaderLabels(
            ["θ_S (°)", "θ_D (°)", "I (V)", "Gain", "P (W)"]
        )
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

        self._btn_save_current = QPushButton("Aktuell\nspeichern")
        self._btn_save_current.setToolTip(
            "Aktuellen Messwert (live) als Punkt in der Malus-Kurve speichern"
        )
        self._btn_save_current.setEnabled(False)
        self._btn_save_current.clicked.connect(self._save_point_current)
        right_layout.addWidget(self._btn_save_current)

        self._btn_save_max = QPushButton("Maximum\nspeichern")
        self._btn_save_max.setToolTip(
            "Maximum des Detektorscans als Punkt speichern und Scan zurücksetzen"
        )
        self._btn_save_max.setEnabled(False)
        self._btn_save_max.clicked.connect(self._save_point_max)
        right_layout.addWidget(self._btn_save_max)

        layout.addWidget(right_panel, 0, 1, 4, 1)

        # Wire peak signal → labels and cached peak
        self._detector_plot.peak_changed.connect(self._update_max_labels)

    def set_calibration_profile(
        self, profile: Optional[PowerCalibrationProfile]
    ) -> None:
        """Inject the active detector calibration profile (called from MainWindow)."""
        self._calibration_profile = profile

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
            self._btn_save_current,
            self._btn_save_max,
        ):
            if btn is not None:
                btn.setEnabled(True)
        self._on_table_selection_changed()

    def on_measurement_stopped(self) -> None:
        for btn in (
            self._btn_clear_detector,
            self._btn_delete,
            self._btn_delete_selected,
            self._btn_save_current,
            self._btn_save_max,
        ):
            if btn is not None:
                btn.setEnabled(False)

    def inject_modules(self, modules: dict[str, object]) -> None:
        pass

    def get_malus_points(self) -> list[MalusPoint]:
        """Return all saved MalusPoint entries for export."""
        if self._curve_plot is None:
            return []
        return self._curve_plot.get_points()

    # ── Save helpers ──────────────────────────────────────────────────────────

    def _compute_power(
        self, voltage_V: float, gain: int
    ) -> tuple[Optional[float], Optional[float]]:
        """Return (power_W, conv_factor) for the given voltage and gain, or (None, None)."""
        if self._calibration_profile is None:
            return None, None
        factor = self._calibration_profile.conversion_factor(gain)
        if factor is None:
            return None, None
        return voltage_V * factor, factor

    @Slot()
    def _save_point_current(self) -> None:
        """Save the current live ADC reading and reset the detector scan."""
        if self._latest_frame is None or self._curve_plot is None:
            return
        frame = self._latest_frame
        power_W, conv = self._compute_power(frame.intensity, frame.pdtia_gain)
        self._curve_plot.add_point(
            sample_angle=frame.sample_angle,
            detector_angle=frame.detector_angle,
            intensity_V=frame.intensity,
            pdtia_gain=frame.pdtia_gain,
            power_W=power_W,
            conv_factor_W_per_V=conv,
        )
        self._clear_detector_plot()
        self._refresh_table()
        self.points_changed.emit(len(self._curve_plot.get_points()))

    @Slot()
    def _save_point_max(self) -> None:
        """Save the peak of the detector scan and reset the detector scan."""
        if self._latest_frame is None or self._curve_plot is None:
            return
        if math.isnan(self._peak_intensity):
            self.status_message.emit("warning", "Kein Maximum verfügbar")
            return
        frame = self._latest_frame
        power_W, conv = self._compute_power(self._peak_intensity, frame.pdtia_gain)
        self._curve_plot.add_point(
            sample_angle=frame.sample_angle,
            detector_angle=self._peak_angle,
            intensity_V=self._peak_intensity,
            pdtia_gain=frame.pdtia_gain,
            power_W=power_W,
            conv_factor_W_per_V=conv,
        )
        self._clear_detector_plot()
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
        self._peak_intensity = intensity
        self._peak_angle = angle
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
        for row, pt in enumerate(points):
            self._points_table.setItem(
                row, 0, QTableWidgetItem(f"{pt.sample_angle:.3f}")
            )
            self._points_table.setItem(
                row, 1, QTableWidgetItem(f"{pt.detector_angle:.3f}")
            )
            self._points_table.setItem(
                row, 2, QTableWidgetItem(f"{pt.intensity_V:.6f}")
            )
            self._points_table.setItem(
                row, 3, QTableWidgetItem(str(pt.pdtia_gain) if pt.pdtia_gain else "—")
            )
            if pt.power_W is not None:
                self._points_table.setItem(
                    row, 4, QTableWidgetItem(f"{pt.power_W:.3e}")
                )
            else:
                self._points_table.setItem(row, 4, QTableWidgetItem("—"))
        self._on_table_selection_changed()

    @Slot()
    def _on_table_selection_changed(self) -> None:
        if self._btn_delete_selected is None or self._points_table is None:
            return
        measuring = (
            self._btn_save_current is not None and self._btn_save_current.isEnabled()
        )
        has_selection = bool(self._points_table.selectedItems())
        self._btn_delete_selected.setEnabled(measuring and has_selection)
