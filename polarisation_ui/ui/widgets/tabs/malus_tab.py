"""Malus-law experiment tab.

Manual-entry workflow: the optical sample is removed.  The user sets a
session-fixed polariser angle once, then enters an analyser angle per point
and confirms with ENTER or the "Punkt hinzufügen" button.  Each confirmed point
captures the live intensity averaged over the last ~0.5 s (up to 5 recent
non-NaN frames at a 10 Hz poll rate) and plots it on an analyser-angle-vs-
intensity scatter.

Controls are enabled only while a measurement session is running so the
behaviour is consistent with the Brewster tab.  The polariser spinbox is
editable before start and locked during a run, ensuring all points within
one session share the same reference angle.
"""

from __future__ import annotations

import math
from collections import deque
from typing import Optional

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QHeaderView, QTableWidgetItem, QWidget

from polarisation_ui.core.models import Frame, MalusPoint, TabExport
from polarisation_ui.pyqt.ui_malus_tab import Ui_MalusTab
from polarisation_ui.ui.widgets.plot_tab_base import ConnState, PlotTabBase

_BUFFER_MAXLEN = 20
_AVERAGE_WINDOW_MS = 500


class MalusTab(PlotTabBase):
    tab_id = "malus"
    tab_title = "Malus"
    required_sources: set[str] = {"ADC"}
    required_modules: set[str] = set()

    points_changed = Signal(
        int
    )  # emits current point count after every add/remove/clear

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._buffer: deque[Frame] = deque(maxlen=_BUFFER_MAXLEN)
        self._is_measuring: bool = False

    def build(self) -> None:
        self._ui = Ui_MalusTab()
        self._ui.setupUi(self)
        self._ui.pointsTable.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self._ui.spinAnalyser.lineEdit().returnPressed.connect(self._add_point)
        self._ui.btnAdd.clicked.connect(self._add_point)
        self._ui.btnDeleteLast.clicked.connect(self._delete_last_point)
        self._ui.btnDeleteSelected.clicked.connect(self._delete_selected_point)
        self._ui.btnClear.clicked.connect(self._clear_all_points)
        self._ui.pointsTable.itemSelectionChanged.connect(
            self._on_table_selection_changed
        )

    # ── PlotTabBase lifecycle ─────────────────────────────────────────────────

    def on_frame(self, frame: Frame) -> None:
        self._buffer.append(frame)
        self._update_live_labels(frame)

    def on_reset(self) -> None:
        self._ui.malusCurvePlot.clear()
        self._buffer.clear()
        self._refresh_table()
        self.points_changed.emit(0)
        self._update_live_labels(None)

    def on_connection_state(self, state: ConnState) -> None:
        pass

    def on_activated(self) -> None:
        pass

    def on_deactivated(self) -> None:
        pass

    def on_measurement_started(self) -> None:
        self._is_measuring = True
        self._buffer.clear()
        self._ui.spinPolariser.setEnabled(False)
        self._ui.spinAnalyser.setEnabled(True)
        self._ui.btnAdd.setEnabled(True)
        self._ui.btnDeleteLast.setEnabled(True)
        self._ui.btnClear.setEnabled(True)
        self._on_table_selection_changed()

    def on_measurement_stopped(self) -> None:
        self._is_measuring = False
        self._ui.spinAnalyser.setEnabled(False)
        self._ui.btnAdd.setEnabled(False)
        self._ui.btnDeleteLast.setEnabled(False)
        self._ui.btnDeleteSelected.setEnabled(False)
        self._ui.btnClear.setEnabled(False)
        self._ui.spinPolariser.setEnabled(True)

    def inject_modules(self, modules: dict[str, object]) -> None:
        pass

    # ── Export contract ───────────────────────────────────────────────────────

    def get_saved_points(self) -> list[MalusPoint]:
        return self._ui.malusCurvePlot.get_points()

    def build_export(self) -> TabExport:
        points = self.get_saved_points()
        polariser_angle = self._ui.spinPolariser.value()
        columns = [
            "analyser_angle_deg",
            "polariser_angle_deg",
            "intensity_V",
            "pdtia_gain",
            "power_W",
            "conv_factor_W_per_V",
        ]
        rows = [
            [
                f"{pt.analyser_angle:.4f}",
                f"{pt.polariser_angle:.4f}",
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
            "polariser_angle_deg": polariser_angle,
            "columns": columns,
            "units": {
                "analyser_angle_deg": "degrees",
                "polariser_angle_deg": "degrees",
                "intensity_V": "volts",
                "power_W": "watts",
                "conv_factor_W_per_V": "watts_per_volt",
            },
        }
        return TabExport(
            filename_hint="malus", columns=columns, rows=rows, metadata=metadata
        )

    # ── Internal helpers ──────────────────────────────────────────────────────

    @Slot()
    def _add_point(self) -> None:
        avg_intensity, latest_frame = self._compute_average()
        if math.isnan(avg_intensity):
            self.status_message.emit("warning", "Keine gültige Intensität im Puffer")
            return

        analyser_angle = self._ui.spinAnalyser.value()
        polariser_angle = self._ui.spinPolariser.value()

        power_W: Optional[float] = None
        conv_factor: Optional[float] = None
        pdtia_gain = 0
        if latest_frame is not None:
            pdtia_gain = latest_frame.pdtia_gain
            conv_factor = latest_frame.conv_factor_W_per_V
            if conv_factor is not None:
                power_W = avg_intensity * conv_factor

        self._ui.malusCurvePlot.add_point(
            analyser_angle=analyser_angle,
            polariser_angle=polariser_angle,
            intensity_V=avg_intensity,
            pdtia_gain=pdtia_gain,
            power_W=power_W,
            conv_factor_W_per_V=conv_factor,
        )
        self._refresh_table()
        self.points_changed.emit(len(self._ui.malusCurvePlot.get_points()))

    def _compute_average(self) -> tuple[float, Optional[Frame]]:
        if not self._buffer:
            return float("nan"), None

        latest = self._buffer[-1]
        cutoff_ms = latest.ts_ms - _AVERAGE_WINDOW_MS

        valid = [
            f.intensity
            for f in self._buffer
            if f.ts_ms >= cutoff_ms and not math.isnan(f.intensity)
        ]
        if not valid:
            return float("nan"), latest

        return sum(valid) / len(valid), latest

    @Slot()
    def _delete_last_point(self) -> None:
        if not self._ui.malusCurvePlot.remove_last_point():
            self.status_message.emit("warning", "Keine Punkte zum Löschen")
        else:
            self._refresh_table()
            self.points_changed.emit(len(self._ui.malusCurvePlot.get_points()))

    @Slot()
    def _delete_selected_point(self) -> None:
        selected = self._ui.pointsTable.selectedItems()
        if not selected:
            return
        row = self._ui.pointsTable.currentRow()
        if not self._ui.malusCurvePlot.remove_point_at(row):
            self.status_message.emit("warning", "Punkt konnte nicht gelöscht werden")
        else:
            self._refresh_table()
            self.points_changed.emit(len(self._ui.malusCurvePlot.get_points()))

    @Slot()
    def _clear_all_points(self) -> None:
        self._ui.malusCurvePlot.clear()
        self._refresh_table()
        self.points_changed.emit(0)

    def _update_live_labels(self, frame: Optional[Frame]) -> None:
        if frame is None or math.isnan(frame.intensity):
            self._ui.lblLiveIntensity.setText("—")
            self._ui.lblLivePower.setText("—")
            return
        self._ui.lblLiveIntensity.setText(f"{frame.intensity:.4f} V")
        if frame.power_W is not None:
            self._ui.lblLivePower.setText(f"{frame.power_W * 1e3:.3f} mW")
        else:
            self._ui.lblLivePower.setText("—")

    def _refresh_table(self) -> None:
        points = self._ui.malusCurvePlot.get_points()
        self._ui.pointsTable.setRowCount(len(points))
        for row, pt in enumerate(points):
            self._ui.pointsTable.setItem(
                row, 0, QTableWidgetItem(f"{pt.analyser_angle:.3f}")
            )
            self._ui.pointsTable.setItem(
                row, 1, QTableWidgetItem(f"{pt.polariser_angle:.3f}")
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
        has_selection = bool(self._ui.pointsTable.selectedItems())
        self._ui.btnDeleteSelected.setEnabled(self._is_measuring and has_selection)
