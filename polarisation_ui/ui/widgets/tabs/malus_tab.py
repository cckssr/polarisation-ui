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
from typing import TYPE_CHECKING

from PySide6.QtCore import QMutex, QMutexLocker, Signal, Slot
from PySide6.QtWidgets import QHeaderView, QTableWidgetItem, QWidget

from polarisation_ui.core.formatting import (
    export_angle,
    export_intensity,
    fmt_intensity,
    fmt_stat,
)
from polarisation_ui.core.models import Frame, MalusPoint, TabExport
from polarisation_ui.core.utils import windowed_average_intensity
from polarisation_ui.infrastructure.qt_threads import KDCSweepWorker
from polarisation_ui.pyqt.ui_malus_tab import Ui_MalusTab
from polarisation_ui.ui.widgets.plot_tab_base import ConnState, PlotTabBase

if TYPE_CHECKING:
    from polarisation_ui.infrastructure.devices.kdc101_polariser import KDC101Polariser

_BUFFER_MAXLEN = 20
_AVERAGE_WINDOW_MS = 500


class MalusTab(PlotTabBase):
    """Malus-law experiment tab: manual analyser-angle entry + averaged intensity."""

    tab_id = "malus"
    tab_title = "Malus"
    required_sources: set[str] = {"ADC"}
    required_modules: set[str] = set()

    points_changed = Signal(int)  # emits current point count after every add/remove/clear

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialise empty buffers; build() constructs the widgets."""
        super().__init__(parent)
        self._buffer: deque[Frame] = deque(maxlen=_BUFFER_MAXLEN)
        self._buffer_mutex = QMutex()
        self._is_measuring: bool = False
        self._kdc: KDC101Polariser | None = None
        self._sweep_worker: KDCSweepWorker | None = None

    def build(self) -> None:
        """Construct the tab's widgets and wire up signal connections."""
        self._ui = Ui_MalusTab()
        self._ui.setupUi(self)
        self._ui.pointsTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._ui.spinAnalyser.lineEdit().returnPressed.connect(self._add_point)
        self._ui.btnAdd.clicked.connect(self._add_point)
        self._ui.btnDeleteLast.clicked.connect(self._delete_last_point)
        self._ui.btnDeleteSelected.clicked.connect(self._delete_selected_point)
        self._ui.btnClear.clicked.connect(self._clear_all_points)
        self._ui.pointsTable.itemSelectionChanged.connect(self._on_table_selection_changed)
        self._ui.cbPolariserPlaced.toggled.connect(self._on_polariser_placed_changed)
        self._ui.btnStartSweep.clicked.connect(self._start_sweep)
        self._ui.btnAbortSweep.clicked.connect(self._abort_sweep)

    # ── PlotTabBase lifecycle ─────────────────────────────────────────────────

    def on_frame(self, frame: Frame) -> None:
        """Buffer the frame for averaging and refresh the live intensity label."""
        with QMutexLocker(self._buffer_mutex):
            self._buffer.append(frame)
        self._update_live_labels(frame)

    def on_reset(self) -> None:
        """Clear the plot, buffer, and saved points."""
        self._ui.malusCurvePlot.clear()
        with QMutexLocker(self._buffer_mutex):
            self._buffer.clear()
        self._refresh_table()
        self.points_changed.emit(0)
        self._update_live_labels(None)

    def on_connection_state(self, state: ConnState) -> None:
        """No-op — this tab has no connection-state-dependent UI."""

    def on_activated(self) -> None:
        """No-op — this tab has no activation-dependent UI."""

    def on_deactivated(self) -> None:
        """No-op — this tab has no deactivation-dependent UI."""

    def on_measurement_started(self) -> None:
        """Enable manual-entry and sweep controls for the new measurement session."""
        self._is_measuring = True
        with QMutexLocker(self._buffer_mutex):
            self._buffer.clear()
        self._ui.spinPolariser.setEnabled(False)
        self._ui.spinAnalyser.setEnabled(True)
        self._ui.btnAdd.setEnabled(True)
        self._ui.btnDeleteLast.setEnabled(True)
        self._ui.btnClear.setEnabled(True)
        self._on_table_selection_changed()
        self._update_sweep_button_state()

    def on_measurement_stopped(self) -> None:
        """Disable manual-entry and sweep controls until the next session."""
        self._is_measuring = False
        if self._sweep_worker is not None:
            self._sweep_worker.abort()
        self._ui.spinAnalyser.setEnabled(False)
        self._ui.btnAdd.setEnabled(False)
        self._ui.btnDeleteLast.setEnabled(False)
        self._ui.btnDeleteSelected.setEnabled(False)
        self._ui.btnClear.setEnabled(False)
        self._ui.spinPolariser.setEnabled(True)
        self._update_sweep_button_state()

    def inject_modules(self, modules: dict[str, object]) -> None:
        """Enable the sweep group when a kdc101 module is available."""
        kdc = modules.get("kdc101")
        if kdc is not None:
            self._kdc = kdc  # type: ignore[assignment]
            self._ui.gbSweep.setEnabled(True)
        else:
            self._kdc = None
            self._ui.gbSweep.setEnabled(False)
        self._update_sweep_button_state()

    # ── Export contract ───────────────────────────────────────────────────────

    def get_saved_points(self) -> list[MalusPoint]:
        """Return all points saved to the Malus curve plot."""
        return self._ui.malusCurvePlot.get_points()

    def build_export(self) -> TabExport:
        """Build the CSV-ready export of all saved Malus points."""
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
                export_angle(pt.analyser_angle),
                export_angle(pt.polariser_angle),
                export_intensity(pt.intensity_V),
                str(pt.pdtia_gain) if pt.pdtia_gain else "",
                f"{pt.power_W:.6e}" if pt.power_W is not None else "",
                (f"{pt.conv_factor_W_per_V:.6e}" if pt.conv_factor_W_per_V is not None else ""),
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
        kdc_offset = self._kdc.zero_offset_deg if self._kdc is not None else 0.0
        if kdc_offset != 0.0:
            metadata["kdc_zero_offset_deg"] = kdc_offset
            metadata["sweep_start_deg"] = self._ui.spinSweepStart.value()
            metadata["sweep_end_deg"] = self._ui.spinSweepEnd.value()
            metadata["sweep_step_deg"] = self._ui.spinSweepStep.value()
        return TabExport(filename_hint="malus", columns=columns, rows=rows, metadata=metadata)

    def restore_points(self, points: list[dict]) -> None:
        """Reload previously-saved points from a prior session."""
        for p in points:
            try:
                self._ui.malusCurvePlot.add_point(
                    analyser_angle=float(p["analyser_angle"]),
                    polariser_angle=float(p["polariser_angle"]),
                    intensity_V=float(p["intensity_V"]),
                    pdtia_gain=int(p.get("pdtia_gain") or 0),
                    power_W=p.get("power_W"),
                    conv_factor_W_per_V=p.get("conv_factor_W_per_V"),
                )
            except (KeyError, TypeError, ValueError):
                pass
        self._refresh_table()
        self.points_changed.emit(len(self._ui.malusCurvePlot.get_points()))

    # ── Internal helpers ──────────────────────────────────────────────────────

    @Slot()
    def _add_point(self) -> None:
        avg_intensity, latest_frame = self._compute_average()
        if math.isnan(avg_intensity):
            self.status_message.emit("warning", "Keine gültige Intensität im Puffer")
            return

        analyser_angle = self._ui.spinAnalyser.value()
        polariser_angle = self._ui.spinPolariser.value()

        power_W: float | None = None
        conv_factor: float | None = None
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

    def _compute_average(self) -> tuple[float, Frame | None]:
        """Compute average intensity over last _AVERAGE_WINDOW_MS.

        Acquires the buffer mutex — safe to call from both the main thread
        and worker threads (e.g. via the KDCSweepWorker callback).
        """
        with QMutexLocker(self._buffer_mutex):
            return self._compute_average_locked()

    def _compute_average_locked(self) -> tuple[float, Frame | None]:
        """Must be called with _buffer_mutex held."""
        return windowed_average_intensity(self._buffer, _AVERAGE_WINDOW_MS)

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

    def _update_live_labels(self, frame: Frame | None) -> None:
        if frame is None or math.isnan(frame.intensity):
            self._ui.lblLiveIntensity.setText("—")
            self._ui.lblLivePower.setText("—")
            return
        self._ui.lblLiveIntensity.setText(f"{fmt_intensity(frame.intensity)} V")
        if frame.power_W is not None:
            # NOTE: power (mW) has no formatting bucket (no fmt_power/export_power
            # helper) and 3 dp doesn't match fmt_stat's 2 dp — left hardcoded.
            self._ui.lblLivePower.setText(f"{frame.power_W * 1e3:.3f} mW")
        else:
            self._ui.lblLivePower.setText("—")

    def _refresh_table(self) -> None:
        points = self._ui.malusCurvePlot.get_points()
        self._ui.pointsTable.setRowCount(len(points))
        for row, pt in enumerate(points):
            # NOTE: analyser/polariser angle here use 3 dp, which matches neither
            # DisplayFormat.angle_dp (2) nor ExportFormat.angle_dp (4) — left as a
            # hardcoded outlier rather than silently changing visible precision.
            self._ui.pointsTable.setItem(row, 0, QTableWidgetItem(f"{pt.analyser_angle:.3f}"))
            self._ui.pointsTable.setItem(row, 1, QTableWidgetItem(f"{pt.polariser_angle:.3f}"))
            self._ui.pointsTable.setItem(row, 2, QTableWidgetItem(export_intensity(pt.intensity_V)))
            # Columns are "P (µW)" then "Gain" (see malus_tab.ui) — keep the two
            # in that order here too.
            if pt.power_W is not None:
                self._ui.pointsTable.setItem(row, 3, QTableWidgetItem(fmt_stat(pt.power_W * 1e6)))
            else:
                self._ui.pointsTable.setItem(row, 3, QTableWidgetItem("—"))
            self._ui.pointsTable.setItem(
                row, 4, QTableWidgetItem(str(pt.pdtia_gain) if pt.pdtia_gain else "—")
            )
        self._on_table_selection_changed()

    @Slot()
    def _on_table_selection_changed(self) -> None:
        has_selection = bool(self._ui.pointsTable.selectedItems())
        self._ui.btnDeleteSelected.setEnabled(self._is_measuring and has_selection)

    # ── KDC101 sweep ──────────────────────────────────────────────────────────

    @Slot(bool)
    def _on_polariser_placed_changed(self, checked: bool) -> None:
        self._update_sweep_button_state()

    def _update_sweep_button_state(self) -> None:
        can_start = (
            self._kdc is not None
            and self._kdc.is_connected()
            and self._ui.cbPolariserPlaced.isChecked()
            and self._is_measuring
            and self._sweep_worker is None
        )
        self._ui.btnStartSweep.setEnabled(can_start)
        self._ui.btnAbortSweep.setEnabled(
            self._sweep_worker is not None and self._sweep_worker.isRunning()
        )

    @Slot()
    def _start_sweep(self) -> None:
        if self._kdc is None or not self._kdc.is_connected():
            return
        self._sweep_worker = KDCSweepWorker(
            kdc=self._kdc,
            read_average=self._compute_average,
            start_deg=self._ui.spinSweepStart.value(),
            end_deg=self._ui.spinSweepEnd.value(),
            step_deg=self._ui.spinSweepStep.value(),
            parent=self,
        )
        self._sweep_worker.point_scanned.connect(self._on_sweep_point)
        self._sweep_worker.progress.connect(self._on_sweep_progress)
        self._sweep_worker.finished.connect(self._on_sweep_finished)
        self._sweep_worker.failed.connect(self._on_sweep_failed)
        self._sweep_worker.log.connect(lambda msg: self.status_message.emit("info", msg))
        self._ui.btnStartSweep.setEnabled(False)
        self._ui.btnAbortSweep.setEnabled(True)
        self._sweep_worker.start()

    @Slot()
    def _abort_sweep(self) -> None:
        if self._sweep_worker is not None:
            self._sweep_worker.abort()

    @Slot(float, float, float, object)
    def _on_sweep_point(
        self,
        analyser_angle: float,
        kdc_pos: float,
        intensity_V: float,
        frame: Frame | None,
    ) -> None:
        polariser_angle = self._ui.spinPolariser.value()
        pdtia_gain = 0
        power_W: float | None = None
        conv_factor: float | None = None
        if frame is not None:
            pdtia_gain = frame.pdtia_gain
            conv_factor = frame.conv_factor_W_per_V
            if conv_factor is not None:
                power_W = intensity_V * conv_factor
        self._ui.malusCurvePlot.add_point(
            analyser_angle=analyser_angle,
            polariser_angle=polariser_angle,
            intensity_V=intensity_V,
            pdtia_gain=pdtia_gain,
            power_W=power_W,
            conv_factor_W_per_V=conv_factor,
        )
        self._refresh_table()
        self.points_changed.emit(len(self._ui.malusCurvePlot.get_points()))

    @Slot(int, int)
    def _on_sweep_progress(self, current: int, total: int) -> None:
        self.status_message.emit("info", f"Scan: {current}/{total}")

    @Slot()
    def _on_sweep_finished(self) -> None:
        self._sweep_worker = None
        self._update_sweep_button_state()
        self.status_message.emit("info", "Scan abgeschlossen")

    @Slot(str)
    def _on_sweep_failed(self, msg: str) -> None:
        self._sweep_worker = None
        self._update_sweep_button_state()
        self.status_message.emit("error", f"Scan fehlgeschlagen: {msg}")
