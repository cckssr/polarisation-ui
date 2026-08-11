"""Waveplate (λ/4, λ/2) experiment tab.

Requires the KDC101 rotation stage (required_modules = {"kdc101"}).

Workflow:
  1. User selects waveplate type (λ/4 or λ/2) and checks the
     "Verzögerungsplatte eingesetzt" checkbox.
  2. On "Scan starten": KDC101 re-homes only if it isn't already homed, then
     sweeps from start to end (relative to the polariser zero offset found on
     the Configuration tab) in the configured step size.
  3. Each step records averaged intensity vs. waveplate angle, plus the
     PDTIA gain and power active at that point.
  4. Export: filename contains "qwp" or "hwp"; metadata carries waveplate_type
     and sweep parameters.
"""

from __future__ import annotations

import math
import time
from collections import deque
from typing import TYPE_CHECKING

from PySide6.QtCore import QMutex, QMutexLocker, Signal, Slot
from PySide6.QtWidgets import QHeaderView, QTableWidgetItem, QWidget

from polarisation_ui.core.formatting import (
    export_angle,
    export_intensity,
    fmt_angle,
    fmt_intensity,
    fmt_stat,
)
from polarisation_ui.core.models import Frame, MalusPoint, TabExport
from polarisation_ui.core.utils import windowed_average_intensity
from polarisation_ui.infrastructure.qt_threads import KDCSweepWorker
from polarisation_ui.pyqt.ui_waveplate_tab import Ui_WaveplateTab
from polarisation_ui.ui.widgets.plot_tab_base import ConnState, PlotTabBase

if TYPE_CHECKING:
    from polarisation_ui.infrastructure.devices.kdc101_polariser import KDC101Polariser

_BUFFER_MAXLEN = 20
_AVERAGE_WINDOW_MS = 500

_WAVEPLATE_TOKENS = ["qwp", "hwp"]
_WAVEPLATE_LABELS = ["lambda/4", "lambda/2"]


class WaveplateTab(PlotTabBase):
    """Wave plate (λ/4, λ/2) experiment tab: KDC101-driven automated angle sweep."""

    tab_id = "waveplate"
    tab_title = "Verzögerungsplatte"
    required_sources: set[str] = {"ADC"}
    required_modules: set[str] = {"kdc101"}

    points_changed = Signal(int)

    _KDC_POLL_INTERVAL_S: float = 0.5  # How often to refresh KDC position in the label

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialise empty buffers; build() constructs the widgets."""
        super().__init__(parent)
        self._buffer: deque[Frame] = deque(maxlen=_BUFFER_MAXLEN)
        self._buffer_mutex = QMutex()
        self._is_measuring: bool = False
        self._kdc: KDC101Polariser | None = None
        self._sweep_worker: KDCSweepWorker | None = None
        self._kdc_pos_cache: float | None = None
        self._kdc_last_poll_ts: float = 0.0

    def build(self) -> None:
        """Construct the tab's widgets and wire up signal connections."""
        self._ui = Ui_WaveplateTab()
        self._ui.setupUi(self)
        self._ui.pointsTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._ui.cbWaveplatePlaced.toggled.connect(self._update_sweep_button_state)
        self._ui.cmbWaveplateType.currentIndexChanged.connect(self._on_waveplate_type_changed)
        self._ui.btnStartSweep.clicked.connect(self._start_sweep)
        self._ui.btnAbortSweep.clicked.connect(self._abort_sweep)
        self._ui.btnDeleteLast.clicked.connect(self._delete_last_point)
        self._ui.btnDeleteSelected.clicked.connect(self._delete_selected_point)
        self._ui.btnClear.clicked.connect(self._clear_all_points)
        self._ui.pointsTable.itemSelectionChanged.connect(self._on_table_selection_changed)

    # ── PlotTabBase lifecycle ─────────────────────────────────────────────────

    def on_frame(self, frame: Frame) -> None:
        """Buffer the frame for averaging and refresh the live intensity/position labels."""
        with QMutexLocker(self._buffer_mutex):
            self._buffer.append(frame)
        self._update_live_labels(frame)

    def on_reset(self) -> None:
        """Clear the plot, buffer, and saved points."""
        self._ui.intensityCurvePlot.clear()
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
        """Enable point/sweep controls for the new measurement session."""
        self._is_measuring = True
        with QMutexLocker(self._buffer_mutex):
            self._buffer.clear()
        self._ui.btnDeleteLast.setEnabled(True)
        self._ui.btnClear.setEnabled(True)
        self._on_table_selection_changed()
        self._update_sweep_button_state()

    def on_measurement_stopped(self) -> None:
        """Abort any running sweep and disable point/sweep controls."""
        self._is_measuring = False
        if self._sweep_worker is not None:
            self._sweep_worker.abort()
        self._ui.btnDeleteLast.setEnabled(False)
        self._ui.btnDeleteSelected.setEnabled(False)
        self._ui.btnClear.setEnabled(False)
        self._update_sweep_button_state()

    def inject_modules(self, modules: dict[str, object]) -> None:
        """Store the injected kdc101 module (or clear it) and refresh sweep controls."""
        kdc = modules.get("kdc101")
        if kdc is not None:
            self._kdc = kdc  # type: ignore[assignment]
        else:
            self._kdc = None
        self._update_sweep_button_state()

    # ── Export contract ───────────────────────────────────────────────────────

    def get_saved_points(self) -> list[MalusPoint]:
        """Return all points saved to the intensity curve plot."""
        return self._ui.intensityCurvePlot.get_points()

    def build_export(self) -> TabExport:
        """Build the CSV-ready export of all saved wave-plate points."""
        points = self.get_saved_points()
        waveplate_idx = self._ui.cmbWaveplateType.currentIndex()
        waveplate_token = _WAVEPLATE_TOKENS[waveplate_idx]
        waveplate_label = _WAVEPLATE_LABELS[waveplate_idx]
        columns = [
            "waveplate_angle_deg",
            "intensity_V",
            "pdtia_gain",
            "power_W",
            "conv_factor_W_per_V",
        ]
        rows = [
            [
                export_angle(pt.analyser_angle),
                export_intensity(pt.intensity_V),
                str(pt.pdtia_gain) if pt.pdtia_gain else "",
                f"{pt.power_W:.6e}" if pt.power_W is not None else "",
                (f"{pt.conv_factor_W_per_V:.6e}" if pt.conv_factor_W_per_V is not None else ""),
            ]
            for pt in points
        ]
        metadata: dict = {
            "waveplate_type": waveplate_label,
            "sweep_start_deg": self._ui.spinSweepStart.value(),
            "sweep_end_deg": self._ui.spinSweepEnd.value(),
            "sweep_step_deg": self._ui.spinSweepStep.value(),
            "columns": columns,
            "units": {
                "waveplate_angle_deg": "degrees",
                "intensity_V": "volts",
                "power_W": "watts",
                "conv_factor_W_per_V": "watts_per_volt",
            },
        }
        return TabExport(
            filename_hint="waveplate",
            columns=columns,
            rows=rows,
            metadata=metadata,
            filename_tokens=[waveplate_token],
        )

    def restore_points(self, points: list[dict]) -> None:
        """Reload previously-saved points from a prior session."""
        for p in points:
            try:
                self._ui.intensityCurvePlot.add_point(
                    analyser_angle=float(p["analyser_angle"]),
                    polariser_angle=float(p.get("polariser_angle", 0.0)),
                    intensity_V=float(p["intensity_V"]),
                    pdtia_gain=int(p.get("pdtia_gain") or 0),
                    power_W=p.get("power_W"),
                    conv_factor_W_per_V=p.get("conv_factor_W_per_V"),
                )
            except (KeyError, TypeError, ValueError):
                pass
        self._refresh_table()
        self.points_changed.emit(len(self._ui.intensityCurvePlot.get_points()))

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _compute_average_safe(self) -> tuple[float, Frame | None]:
        with QMutexLocker(self._buffer_mutex):
            return windowed_average_intensity(self._buffer, _AVERAGE_WINDOW_MS)

    def _update_live_labels(self, frame: Frame | None) -> None:
        if frame is None or math.isnan(frame.intensity):
            self._ui.lblLiveIntensity.setText("—")
            self._ui.lblKDCPosition.setText("—")
            return
        self._ui.lblLiveIntensity.setText(f"{fmt_intensity(frame.intensity)} V")
        # Refresh the KDC position at most every _KDC_POLL_INTERVAL_S seconds to avoid
        # a blocking hardware read on every ~10 Hz frame.
        if self._kdc is not None and self._kdc.is_connected():
            now = time.monotonic()
            if now - self._kdc_last_poll_ts >= self._KDC_POLL_INTERVAL_S:
                try:
                    self._kdc_pos_cache = self._kdc.get_position_deg()
                    self._kdc_last_poll_ts = now
                except Exception as exc:  # noqa: BLE001
                    # Non-critical: keep showing the cached value on transient errors.
                    from polarisation_ui.infrastructure.logging import Debug

                    Debug.warning(f"WaveplateTab: KDC position read failed: {exc}")
            if self._kdc_pos_cache is not None:
                self._ui.lblKDCPosition.setText(f"{fmt_angle(self._kdc_pos_cache)}°")
            else:
                self._ui.lblKDCPosition.setText("—")

    def _update_sweep_button_state(self) -> None:
        can_start = (
            self._kdc is not None
            and self._kdc.is_connected()
            and self._ui.cbWaveplatePlaced.isChecked()
            and self._is_measuring
            and self._sweep_worker is None
        )
        self._ui.btnStartSweep.setEnabled(can_start)
        self._ui.btnAbortSweep.setEnabled(
            self._sweep_worker is not None and self._sweep_worker.isRunning()
        )

    @Slot(int)
    def _on_waveplate_type_changed(self, _index: int) -> None:
        self.filename_hint_changed.emit()

    @Slot()
    def _start_sweep(self) -> None:
        if self._kdc is None or not self._kdc.is_connected():
            return
        self._sweep_worker = KDCSweepWorker(
            kdc=self._kdc,
            read_average=self._compute_average_safe,
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
        self, angle: float, _kdc_pos: float, intensity_V: float, frame: Frame | None
    ) -> None:
        pdtia_gain = 0
        power_W: float | None = None
        conv_factor: float | None = None
        if frame is not None:
            pdtia_gain = frame.pdtia_gain
            conv_factor = frame.conv_factor_W_per_V
            if conv_factor is not None:
                power_W = intensity_V * conv_factor
        self._ui.intensityCurvePlot.add_point(
            analyser_angle=angle,
            polariser_angle=0.0,
            intensity_V=intensity_V,
            pdtia_gain=pdtia_gain,
            power_W=power_W,
            conv_factor_W_per_V=conv_factor,
        )
        self._refresh_table()
        self.points_changed.emit(len(self._ui.intensityCurvePlot.get_points()))

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

    @Slot()
    def _delete_last_point(self) -> None:
        if not self._ui.intensityCurvePlot.remove_last_point():
            self.status_message.emit("warning", "Keine Punkte zum Löschen")
        else:
            self._refresh_table()
            self.points_changed.emit(len(self._ui.intensityCurvePlot.get_points()))

    @Slot()
    def _delete_selected_point(self) -> None:
        selected = self._ui.pointsTable.selectedItems()
        if not selected:
            return
        row = self._ui.pointsTable.currentRow()
        if not self._ui.intensityCurvePlot.remove_point_at(row):
            self.status_message.emit("warning", "Punkt konnte nicht gelöscht werden")
        else:
            self._refresh_table()
            self.points_changed.emit(len(self._ui.intensityCurvePlot.get_points()))

    @Slot()
    def _clear_all_points(self) -> None:
        self._ui.intensityCurvePlot.clear()
        self._refresh_table()
        self.points_changed.emit(0)

    def _refresh_table(self) -> None:
        points = self._ui.intensityCurvePlot.get_points()
        self._ui.pointsTable.setRowCount(len(points))
        for row, pt in enumerate(points):
            # NOTE: analyser angle here uses 3 dp, which matches neither
            # DisplayFormat.angle_dp (2) nor ExportFormat.angle_dp (4) — left as a
            # hardcoded outlier rather than silently changing visible precision.
            self._ui.pointsTable.setItem(row, 0, QTableWidgetItem(f"{pt.analyser_angle:.3f}"))
            self._ui.pointsTable.setItem(row, 1, QTableWidgetItem(export_intensity(pt.intensity_V)))
            if pt.power_W is not None:
                self._ui.pointsTable.setItem(row, 2, QTableWidgetItem(fmt_stat(pt.power_W * 1e6)))
            else:
                self._ui.pointsTable.setItem(row, 2, QTableWidgetItem("—"))
            self._ui.pointsTable.setItem(
                row, 3, QTableWidgetItem(str(pt.pdtia_gain) if pt.pdtia_gain else "—")
            )
        self._on_table_selection_changed()

    @Slot()
    def _on_table_selection_changed(self) -> None:
        has_selection = bool(self._ui.pointsTable.selectedItems())
        self._ui.btnDeleteSelected.setEnabled(self._is_measuring and has_selection)
