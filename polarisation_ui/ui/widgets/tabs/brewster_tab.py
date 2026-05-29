"""Brewster-angle experiment tab.

Owns both plots (live detector scan + manually saved Brewster curve) and the
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
from typing import Literal, Optional

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QButtonGroup, QHeaderView, QTableWidgetItem, QWidget

from polarisation_ui.core.models import BrewsterPoint, Frame, TabExport
from polarisation_ui.pyqt.ui_brewster_tab import Ui_BrewsterTab
from polarisation_ui.ui.widgets.plot_tab_base import ConnState, PlotTabBase


class BrewsterTab(PlotTabBase):
    tab_id = "brewster"
    tab_title = "Brewster"
    required_sources: set[str] = {"ENC:BOTH", "ADC"}
    required_modules: set[str] = set()

    points_changed = Signal(
        int
    )  # emits current point count after every add/remove/clear

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._latest_frame: Optional[Frame] = None
        self._peak_intensity: float = float("nan")
        self._peak_angle: float = float("nan")
        self._polarisation: Literal["p", "s"] = "p"

    def build(self) -> None:
        self._ui = Ui_BrewsterTab()
        self._ui.setupUi(self)
        self._ui.pointsTable.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self._ui.btnClearDetector.clicked.connect(self._clear_detector_plot)
        self._ui.btnDeleteLast.clicked.connect(self._delete_last_point)
        self._ui.btnDeleteSelected.clicked.connect(self._delete_selected_point)
        self._ui.btnSaveCurrent.clicked.connect(self._save_point_current)
        self._ui.btnSaveMax.clicked.connect(self._save_point_max)
        self._ui.pointsTable.itemSelectionChanged.connect(
            self._on_table_selection_changed
        )
        self._ui.detectorPlot.peak_changed.connect(self._update_max_labels)

        # p/s polarisation selection — QButtonGroup is a non-visual logical helper
        self._pol_group = QButtonGroup(self)
        self._pol_group.addButton(self._ui.rbPolP, 0)
        self._pol_group.addButton(self._ui.rbPolS, 1)
        self._pol_group.idToggled.connect(self._on_polarisation_toggled)

    # ── PlotTabBase lifecycle ─────────────────────────────────────────────────

    def on_frame(self, frame: Frame) -> None:
        self._latest_frame = frame
        self._ui.detectorPlot.update_data(frame.detector_angle, frame.intensity)

    def on_reset(self) -> None:
        self._ui.detectorPlot.clear()
        self._ui.brewsterCurvePlot.clear()
        self._refresh_table()
        self.points_changed.emit(0)

    def on_connection_state(self, state: ConnState) -> None:
        pass

    def on_activated(self) -> None:
        pass

    def on_deactivated(self) -> None:
        pass

    def on_measurement_started(self) -> None:
        self._ui.btnClearDetector.setEnabled(True)
        self._ui.btnDeleteLast.setEnabled(True)
        self._ui.btnSaveCurrent.setEnabled(True)
        self._ui.btnSaveMax.setEnabled(True)
        self._on_table_selection_changed()

    def on_measurement_stopped(self) -> None:
        self._ui.btnClearDetector.setEnabled(False)
        self._ui.btnDeleteLast.setEnabled(False)
        self._ui.btnDeleteSelected.setEnabled(False)
        self._ui.btnSaveCurrent.setEnabled(False)
        self._ui.btnSaveMax.setEnabled(False)

    def inject_modules(self, modules: dict[str, object]) -> None:
        pass

    @Slot(int, bool)
    def _on_polarisation_toggled(self, btn_id: int, checked: bool) -> None:
        if checked:
            self._polarisation = "p" if btn_id == 0 else "s"
            self.filename_hint_changed.emit()

    # ── Export contract ───────────────────────────────────────────────────────

    def get_saved_points(self) -> list[BrewsterPoint]:
        return self._ui.brewsterCurvePlot.get_points()

    def build_export(self) -> TabExport:
        points = self.get_saved_points()
        columns = [
            "sample_angle_deg",
            "detector_angle_deg",
            "intensity_V",
            "pdtia_gain",
            "power_W",
            "conv_factor_W_per_V",
        ]
        rows = [
            [
                f"{pt.sample_angle:.4f}",
                f"{pt.detector_angle:.4f}",
                f"{pt.intensity_V:.6f}",
                str(pt.pdtia_gain) if pt.pdtia_gain else "",
                f"{pt.power_W:.6e}" if pt.power_W is not None else "",
                (
                    f"{pt.conv_factor_W_per_V:.6e}"
                    if pt.conv_factor_W_per_V is not None
                    else ""
                ),
            ]
            for pt in points
        ]
        metadata: dict = {
            "columns": columns,
            "units": {
                "sample_angle_deg": "degrees",
                "detector_angle_deg": "degrees",
                "intensity_V": "volts",
                "power_W": "watts",
                "conv_factor_W_per_V": "watts_per_volt",
            },
            "polarisation": self._polarisation,
        }
        return TabExport(
            filename_hint="brewster",
            columns=columns,
            rows=rows,
            metadata=metadata,
            filename_tokens=[self._polarisation],
        )

    # ── Save helpers ──────────────────────────────────────────────────────────

    @Slot()
    def _save_point_current(self) -> None:
        if self._latest_frame is None:
            return
        frame = self._latest_frame
        self._ui.brewsterCurvePlot.add_point(
            sample_angle=frame.sample_angle,
            detector_angle=frame.detector_angle,
            intensity_V=frame.intensity,
            pdtia_gain=frame.pdtia_gain,
            power_W=frame.power_W,
            conv_factor_W_per_V=frame.conv_factor_W_per_V,
        )
        self._clear_detector_plot()
        self._refresh_table()
        self.points_changed.emit(len(self._ui.brewsterCurvePlot.get_points()))

    @Slot()
    def _save_point_max(self) -> None:
        if self._latest_frame is None:
            return
        if math.isnan(self._peak_intensity):
            self.status_message.emit("warning", "Kein Maximum verfügbar")
            return
        frame = self._latest_frame
        peak_power_W = (
            self._peak_intensity * frame.conv_factor_W_per_V
            if frame.conv_factor_W_per_V is not None
            else None
        )
        self._ui.brewsterCurvePlot.add_point(
            sample_angle=frame.sample_angle,
            detector_angle=self._peak_angle,
            intensity_V=self._peak_intensity,
            pdtia_gain=frame.pdtia_gain,
            power_W=peak_power_W,
            conv_factor_W_per_V=frame.conv_factor_W_per_V,
        )
        self._clear_detector_plot()
        self._refresh_table()
        self.points_changed.emit(len(self._ui.brewsterCurvePlot.get_points()))

    @Slot()
    def _clear_detector_plot(self) -> None:
        self._ui.detectorPlot.clear()

    @Slot()
    def _delete_last_point(self) -> None:
        if not self._ui.brewsterCurvePlot.remove_last_point():
            self.status_message.emit("warning", "Keine Punkte zum Löschen")
        else:
            self._refresh_table()
            self.points_changed.emit(len(self._ui.brewsterCurvePlot.get_points()))

    @Slot()
    def _delete_selected_point(self) -> None:
        selected = self._ui.pointsTable.selectedItems()
        if not selected:
            return
        row = self._ui.pointsTable.currentRow()
        if not self._ui.brewsterCurvePlot.remove_point_at(row):
            self.status_message.emit("warning", "Punkt konnte nicht gelöscht werden")
        else:
            self._refresh_table()
            self.points_changed.emit(len(self._ui.brewsterCurvePlot.get_points()))

    @Slot(float, float)
    def _update_max_labels(self, intensity: float, angle: float) -> None:
        self._peak_intensity = intensity
        self._peak_angle = angle
        if math.isnan(intensity):
            self._ui.lblMaxIntensity.setText("—")
            self._ui.lblMaxAngle.setText("—")
        else:
            self._ui.lblMaxIntensity.setText(f"{intensity:.4f} V")
            self._ui.lblMaxAngle.setText(f"{angle:.2f}°")

    def _refresh_table(self) -> None:
        points = self._ui.brewsterCurvePlot.get_points()
        self._ui.pointsTable.setRowCount(len(points))
        for row, pt in enumerate(points):
            self._ui.pointsTable.setItem(
                row, 0, QTableWidgetItem(f"{pt.sample_angle:.3f}")
            )
            self._ui.pointsTable.setItem(
                row, 1, QTableWidgetItem(f"{pt.detector_angle:.3f}")
            )
            self._ui.pointsTable.setItem(
                row, 2, QTableWidgetItem(f"{pt.intensity_V:.6f}")
            )
            self._ui.pointsTable.setItem(
                row, 3, QTableWidgetItem(str(pt.pdtia_gain) if pt.pdtia_gain else "—")
            )
            if pt.power_W is not None:
                self._ui.pointsTable.setItem(
                    row, 4, QTableWidgetItem(f"{pt.power_W:.3e}")
                )
            else:
                self._ui.pointsTable.setItem(row, 4, QTableWidgetItem("—"))
        self._on_table_selection_changed()

    @Slot()
    def _on_table_selection_changed(self) -> None:
        measuring = self._ui.btnSaveCurrent.isEnabled()
        has_selection = bool(self._ui.pointsTable.selectedItems())
        self._ui.btnDeleteSelected.setEnabled(measuring and has_selection)
