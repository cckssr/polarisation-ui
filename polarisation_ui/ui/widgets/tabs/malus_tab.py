"""
Malus-law experiment tab.

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
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from polarisation_ui.core.models import Frame, MalusPoint, TabExport
from polarisation_ui.ui.widgets.malus_curve_plot import MalusCurvePlot
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
        self._curve_plot: Optional[MalusCurvePlot] = None
        self._spin_polariser: Optional[QDoubleSpinBox] = None
        self._spin_analyser: Optional[QDoubleSpinBox] = None
        self._btn_add: Optional[QPushButton] = None
        self._btn_delete: Optional[QPushButton] = None
        self._btn_delete_selected: Optional[QPushButton] = None
        self._btn_clear: Optional[QPushButton] = None
        self._lbl_live_intensity: Optional[QLabel] = None
        self._lbl_live_power: Optional[QLabel] = None
        self._points_table: Optional[QTableWidget] = None
        self._buffer: deque[Frame] = deque(maxlen=_BUFFER_MAXLEN)
        self._is_measuring: bool = False

    def build(self) -> None:
        from PySide6.QtWidgets import QGridLayout

        layout = QGridLayout(self)
        layout.setContentsMargins(5, 10, 10, 5)
        layout.setRowStretch(0, 1)
        layout.setColumnStretch(0, 2)
        layout.setColumnStretch(1, 1)

        self._curve_plot = MalusCurvePlot()
        layout.addWidget(self._curve_plot, 0, 0)

        # --- Right panel ---
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(4, 0, 0, 0)
        right_layout.setSpacing(6)

        # Live intensity readout
        live_group = QGroupBox("Aktuell")
        live_form = QFormLayout(live_group)
        live_form.setContentsMargins(6, 4, 6, 4)
        live_form.setVerticalSpacing(2)
        self._lbl_live_intensity = QLabel("—")
        self._lbl_live_power = QLabel("—")
        live_form.addRow("I:", self._lbl_live_intensity)
        live_form.addRow("P:", self._lbl_live_power)
        right_layout.addWidget(live_group)

        # Angle input group
        entry_group = QGroupBox("Messpunkt")
        entry_form = QFormLayout(entry_group)
        entry_form.setContentsMargins(6, 6, 6, 6)
        entry_form.setVerticalSpacing(4)

        self._spin_polariser = QDoubleSpinBox()
        self._spin_polariser.setRange(-360.0, 360.0)
        self._spin_polariser.setDecimals(2)
        self._spin_polariser.setSuffix(" °")
        self._spin_polariser.setValue(0.0)
        self._spin_polariser.setToolTip(
            "Polarisatorwinkel (fest für die gesamte Messreihe)"
        )
        entry_form.addRow("Polarisator θ_P:", self._spin_polariser)

        self._spin_analyser = QDoubleSpinBox()
        self._spin_analyser.setRange(-360.0, 360.0)
        self._spin_analyser.setDecimals(2)
        self._spin_analyser.setSuffix(" °")
        self._spin_analyser.setValue(0.0)
        self._spin_analyser.setEnabled(False)
        self._spin_analyser.setToolTip("Analysatorwinkel für diesen Messpunkt")
        # ENTER in the spin box also adds a point
        self._spin_analyser.lineEdit().returnPressed.connect(self._add_point)
        entry_form.addRow("Analysator θ_A:", self._spin_analyser)

        self._btn_add = QPushButton("Punkt hinzufügen")
        self._btn_add.setToolTip(
            "Aktuellen Analysatorwinkel mit gemittelter Intensität speichern"
        )
        self._btn_add.setEnabled(False)
        self._btn_add.clicked.connect(self._add_point)
        entry_form.addRow(self._btn_add)

        right_layout.addWidget(entry_group)

        # Saved-points table — expands to fill remaining vertical space
        self._points_table = QTableWidget(0, 5)
        self._points_table.setHorizontalHeaderLabels(
            ["θ_A (°)", "θ_P (°)", "I (V)", "Gain", "P (W)"]
        )
        self._points_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self._points_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self._points_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._points_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._points_table.setMinimumHeight(120)
        self._points_table.verticalHeader().setVisible(False)
        self._points_table.itemSelectionChanged.connect(
            self._on_table_selection_changed
        )
        right_layout.addWidget(self._points_table, stretch=1)

        self._btn_delete_selected = QPushButton("Ausgewählten\nlöschen")
        self._btn_delete_selected.setToolTip("Markierten Punkt aus der Kurve löschen")
        self._btn_delete_selected.setEnabled(False)
        self._btn_delete_selected.clicked.connect(self._delete_selected_point)
        right_layout.addWidget(self._btn_delete_selected)

        self._btn_delete = QPushButton("Letzten Punkt\nlöschen")
        self._btn_delete.setEnabled(False)
        self._btn_delete.clicked.connect(self._delete_last_point)
        right_layout.addWidget(self._btn_delete)

        self._btn_clear = QPushButton("Alle löschen")
        self._btn_clear.setEnabled(False)
        self._btn_clear.clicked.connect(self._clear_all_points)
        right_layout.addWidget(self._btn_clear)

        layout.addWidget(right_panel, 0, 1)

    # ── PlotTabBase lifecycle ─────────────────────────────────────────────────

    def on_frame(self, frame: Frame) -> None:
        self._buffer.append(frame)
        self._update_live_labels(frame)

    def on_reset(self) -> None:
        if self._curve_plot is not None:
            self._curve_plot.clear()
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
        if self._spin_polariser is not None:
            self._spin_polariser.setEnabled(False)
        for w in (
            self._spin_analyser,
            self._btn_add,
            self._btn_delete,
            self._btn_clear,
        ):
            if w is not None:
                w.setEnabled(True)
        self._on_table_selection_changed()

    def on_measurement_stopped(self) -> None:
        self._is_measuring = False
        for w in (
            self._spin_analyser,
            self._btn_add,
            self._btn_delete,
            self._btn_delete_selected,
            self._btn_clear,
        ):
            if w is not None:
                w.setEnabled(False)
        if self._spin_polariser is not None:
            self._spin_polariser.setEnabled(True)

    def inject_modules(self, modules: dict[str, object]) -> None:
        pass

    # ── Export contract ───────────────────────────────────────────────────────

    def get_saved_points(self) -> list[MalusPoint]:
        """Return all saved MalusPoint entries for export."""
        if self._curve_plot is None:
            return []
        return self._curve_plot.get_points()

    def build_export(self) -> TabExport:
        """Return a schema-agnostic export bundle for the global Save action."""
        points = self.get_saved_points()
        polariser_angle = (
            self._spin_polariser.value()
            if self._spin_polariser is not None
            else float("nan")
        )
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
        """Average buffered intensity and save a new point at the entered angle."""
        if self._curve_plot is None or self._spin_analyser is None:
            return

        avg_intensity, latest_frame = self._compute_average()
        if math.isnan(avg_intensity):
            self.status_message.emit("warning", "Keine gültige Intensität im Puffer")
            return

        analyser_angle = self._spin_analyser.value()
        polariser_angle = (
            self._spin_polariser.value() if self._spin_polariser is not None else 0.0
        )

        power_W: Optional[float] = None
        conv_factor: Optional[float] = None
        pdtia_gain = 0
        if latest_frame is not None:
            pdtia_gain = latest_frame.pdtia_gain
            conv_factor = latest_frame.conv_factor_W_per_V
            if conv_factor is not None:
                power_W = avg_intensity * conv_factor

        self._curve_plot.add_point(
            analyser_angle=analyser_angle,
            polariser_angle=polariser_angle,
            intensity_V=avg_intensity,
            pdtia_gain=pdtia_gain,
            power_W=power_W,
            conv_factor_W_per_V=conv_factor,
        )
        self._refresh_table()
        self.points_changed.emit(len(self._curve_plot.get_points()))

    def _compute_average(self) -> tuple[float, Optional[Frame]]:
        """Return (averaged intensity, most-recent frame) from the buffer window."""
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

    @Slot()
    def _clear_all_points(self) -> None:
        if self._curve_plot is None:
            return
        self._curve_plot.clear()
        self._refresh_table()
        self.points_changed.emit(0)

    def _update_live_labels(self, frame: Optional[Frame]) -> None:
        if self._lbl_live_intensity is None:
            return
        if frame is None or math.isnan(frame.intensity):
            self._lbl_live_intensity.setText("—")
            if self._lbl_live_power is not None:
                self._lbl_live_power.setText("—")
            return
        self._lbl_live_intensity.setText(f"{frame.intensity:.4f} V")
        if self._lbl_live_power is not None:
            if frame.power_W is not None:
                self._lbl_live_power.setText(f"{frame.power_W * 1e3:.3f} mW")
            else:
                self._lbl_live_power.setText("—")

    def _refresh_table(self) -> None:
        if self._points_table is None or self._curve_plot is None:
            return
        points = self._curve_plot.get_points()
        self._points_table.setRowCount(len(points))
        for row, pt in enumerate(points):
            self._points_table.setItem(
                row, 0, QTableWidgetItem(f"{pt.analyser_angle:.3f}")
            )
            self._points_table.setItem(
                row, 1, QTableWidgetItem(f"{pt.polariser_angle:.3f}")
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
        has_selection = bool(self._points_table.selectedItems())
        self._btn_delete_selected.setEnabled(self._is_measuring and has_selection)
