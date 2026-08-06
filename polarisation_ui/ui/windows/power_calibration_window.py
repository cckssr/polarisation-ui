"""Power-calibration tool for PD-TIA detector.

Usage workflow:
  1. Set up the bench: calibrated power meter + constant laser + ND filters.
  2. Select a PDTIA gain stage (1–4) in the tab bar.
  3. Read the optical power from your meter → enter it in the "Leistung" field.
  4. Read the sensor voltage (live button fills it automatically) → enter in "Spannung".
  5. Click "Punkt hinzufügen" to add the (voltage, power) pair.
  6. Repeat with different ND filters / power levels for this gain.
  7. Switch to the next gain stage and repeat.
  8. Enter a profile name and click "Kalibrierung speichern".

The computed W/V conversion factor (mean of P/V across all points per stage) is
shown in real time and is used by the main window for the live wattage display.
"""

from __future__ import annotations

import math
from pathlib import Path

import pyqtgraph as pg
from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from polarisation_ui.core.formatting import export_voltage
from polarisation_ui.core.power_calibration import (
    PROFILES_DIR,
    GainCalibration,
    PowerCalibrationProfile,
)
from polarisation_ui.infrastructure.logging import Debug

_GAIN_STAGES = (1, 2, 3, 4)


class _GainCalTab(QWidget):
    """One tab per PDTIA gain stage — shows the (V, W) point table and a plot."""

    points_changed = Signal()

    def __init__(self, gain_stage: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._gain_stage = gain_stage
        self._cal = GainCalibration(gain_stage=gain_stage)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        # Entry row
        entry_group = QGroupBox(f"Messpunkt hinzufügen — Gain {self._gain_stage}")
        entry_form = QFormLayout(entry_group)
        entry_form.setContentsMargins(8, 6, 8, 6)
        entry_form.setVerticalSpacing(4)

        self._spin_voltage = QDoubleSpinBox()
        self._spin_voltage.setRange(0.0, 10.0)
        self._spin_voltage.setDecimals(6)
        self._spin_voltage.setSuffix(" V")
        self._spin_voltage.setSingleStep(0.001)

        self._btn_live = QPushButton("Live")
        self._btn_live.setToolTip("Aktuelle Sensorspannung übernehmen")
        self._btn_live.setMaximumWidth(55)
        self._btn_live.setEnabled(False)

        v_row = QHBoxLayout()
        v_row.addWidget(self._spin_voltage)
        v_row.addWidget(self._btn_live)
        entry_form.addRow("Spannung (V):", v_row)

        self._spin_power = QDoubleSpinBox()
        self._spin_power.setRange(0.0, 1.0)
        self._spin_power.setDecimals(9)
        self._spin_power.setSuffix(" W")
        self._spin_power.setSingleStep(1e-7)
        entry_form.addRow("Leistung (W):", self._spin_power)

        btn_add = QPushButton("Punkt hinzufügen")
        btn_add.clicked.connect(self._add_point)
        entry_form.addRow(btn_add)

        layout.addWidget(entry_group)

        # Conversion factor readout
        self._lbl_factor = QLabel("Konversionsfaktor: —")
        layout.addWidget(self._lbl_factor)

        # Point table
        self._table = QTableWidget(0, 3)
        self._table.setHorizontalHeaderLabels(["Spannung (V)", "Leistung (W)", "W/V"])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setMinimumHeight(100)
        self._table.setMaximumHeight(180)
        self._table.verticalHeader().setVisible(False)
        layout.addWidget(self._table)

        btn_remove = QPushButton("Ausgewählten Punkt löschen")
        btn_remove.clicked.connect(self._remove_selected)
        layout.addWidget(btn_remove)

        # Plot: voltage vs power
        self._plot = pg.PlotWidget()
        self._plot.setBackground("w")
        self._plot.showGrid(x=True, y=True, alpha=0.3)
        self._plot.setLabel("bottom", "Spannung", units="V")
        self._plot.setLabel("left", "Leistung", units="W")
        self._scatter = self._plot.plot(
            [],
            [],
            pen=None,
            symbol="o",
            symbolSize=8,
            symbolBrush=pg.mkBrush(0, 100, 200, 200),
            symbolPen=pg.mkPen(None),
        )
        self._fit_line = self._plot.plot([], [], pen=pg.mkPen("r", width=1.5))
        layout.addWidget(self._plot, 1)

        self._btn_live.clicked.connect(self._fill_live_voltage)

    def set_live_voltage(self, voltage: float) -> None:
        """Called by parent to update the cached live voltage for the "Live" button."""
        self._live_voltage = voltage
        self._btn_live.setEnabled(True)

    def _fill_live_voltage(self) -> None:
        if hasattr(self, "_live_voltage"):
            self._spin_voltage.setValue(self._live_voltage)

    @Slot()
    def _add_point(self) -> None:
        v = self._spin_voltage.value()
        p = self._spin_power.value()
        if v <= 0.0:
            QMessageBox.warning(self, "Ungültige Eingabe", "Spannung muss größer als 0 sein.")
            return
        if p <= 0.0:
            QMessageBox.warning(self, "Ungültige Eingabe", "Leistung muss größer als 0 sein.")
            return
        self._cal.add_point(v, p)
        self._refresh()
        self.points_changed.emit()

    @Slot()
    def _remove_selected(self) -> None:
        row = self._table.currentRow()
        if row < 0:
            return
        self._cal.remove_point(row)
        self._refresh()
        self.points_changed.emit()

    def _refresh(self) -> None:
        pts = self._cal.points
        self._table.setRowCount(len(pts))
        for i, (v, p) in enumerate(pts):
            ratio = p / v if v > 0 else float("nan")
            self._table.setItem(i, 0, QTableWidgetItem(export_voltage(v)))
            # NOTE: power (p) here uses 9 dp — no power_dp bucket exists in
            # DisplayFormat/ExportFormat, so this stays a hardcoded outlier
            # rather than changing visible precision.
            self._table.setItem(i, 1, QTableWidgetItem(f"{p:.9f}"))
            self._table.setItem(
                i, 2, QTableWidgetItem(f"{ratio:.4e}" if not math.isnan(ratio) else "—")
            )

        factor = self._cal.conversion_factor_W_per_V()
        if factor is None:
            self._lbl_factor.setText("Konversionsfaktor: —")
        else:
            self._lbl_factor.setText(
                f"Konversionsfaktor: {factor:.4e} W/V  (Gain {self._gain_stage})"
            )

        # Update scatter plot
        if pts:
            vs = [v for v, _ in pts]
            ps = [p for _, p in pts]
            self._scatter.setData(vs, ps)
            # Fit line: y = factor * x
            if factor is not None and len(vs) >= 1:
                x_min, x_max = min(vs), max(vs)
                self._fit_line.setData([x_min, x_max], [factor * x_min, factor * x_max])
            else:
                self._fit_line.setData([], [])
        else:
            self._scatter.setData([], [])
            self._fit_line.setData([], [])

    def get_calibration(self) -> GainCalibration:
        return self._cal

    def load_calibration(self, cal: GainCalibration) -> None:
        self._cal = cal
        self._refresh()


class PowerCalibrationWindow(QDialog):
    """Standalone calibration dialog.

    Emits `profile_saved` (no args) whenever a profile is successfully saved
    so that MainWindow can reload the profile combobox.
    """

    profile_saved = Signal()

    def __init__(
        self,
        data_controller=None,
        parent: QWidget | None = None,
    ) -> None:
        """Build the dialog's widgets in Python (no .ui counterpart by design)."""
        super().__init__(parent)
        self.setWindowTitle("Leistungskalibrierung — PD-TIA Detektor")
        self.resize(700, 620)
        self._data_controller = data_controller
        self._gain_tabs: dict[int, _GainCalTab] = {}
        self._live_voltage: float = 0.0
        self._setup_ui()
        self._connect_live_updates()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Gain stage tabs
        self._tab_widget = QTabWidget()
        for stage in _GAIN_STAGES:
            tab = _GainCalTab(gain_stage=stage)
            self._tab_widget.addTab(tab, f"Gain {stage}")
            self._gain_tabs[stage] = tab
        layout.addWidget(self._tab_widget, 1)

        # Profile name + save/load row
        profile_group = QGroupBox("Profil")
        profile_form = QFormLayout(profile_group)
        profile_form.setContentsMargins(8, 6, 8, 6)
        profile_form.setVerticalSpacing(4)

        self._le_profile_name = QLineEdit()
        self._le_profile_name.setPlaceholderText("z.B. Det-A")
        profile_form.addRow("Profilname:", self._le_profile_name)

        btn_row = QHBoxLayout()
        self._btn_save = QPushButton("Kalibrierung speichern")
        self._btn_save.clicked.connect(self._save_profile)
        btn_load = QPushButton("Kalibrierung laden…")
        btn_load.clicked.connect(self._load_profile)
        btn_row.addWidget(self._btn_save)
        btn_row.addWidget(btn_load)
        profile_form.addRow(btn_row)

        layout.addWidget(profile_group)

        # Current live voltage display (read-only info)
        self._lbl_live = QLabel("Live-Spannung: —")
        layout.addWidget(self._lbl_live)

        # Close button
        close_btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close_btn_box.rejected.connect(self.close)
        layout.addWidget(close_btn_box)

    def _connect_live_updates(self) -> None:
        if self._data_controller is None:
            return
        self._data_controller.intensity_updated.connect(self._on_live_voltage)

    @Slot(float)
    def _on_live_voltage(self, voltage: float) -> None:
        self._live_voltage = voltage
        self._lbl_live.setText(f"Live-Spannung: {export_voltage(voltage)} V")
        for tab in self._gain_tabs.values():
            tab.set_live_voltage(voltage)

    @Slot()
    def _save_profile(self) -> None:
        name = self._le_profile_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Kein Name", "Bitte einen Profilnamen eingeben.")
            return

        profile = PowerCalibrationProfile(name=name)
        for stage, tab in self._gain_tabs.items():
            profile.gains[stage] = tab.get_calibration()

        path = PowerCalibrationProfile.default_path(name)
        try:
            profile.save(path)
            Debug.info(f"Power calibration profile saved: {path}")
            QMessageBox.information(
                self,
                "Gespeichert",
                f"Kalibrierungsprofil '{name}' wurde gespeichert:\n{path}",
            )
            self.profile_saved.emit()
        except Exception as exc:
            Debug.error(f"Failed to save calibration profile: {exc}")
            QMessageBox.critical(self, "Fehler", f"Speichern fehlgeschlagen:\n{exc}")

    @Slot()
    def _load_profile(self) -> None:
        from PySide6.QtWidgets import QFileDialog

        profiles = PowerCalibrationProfile.list_profiles()
        if profiles:
            start_dir = str(PROFILES_DIR)
        else:
            start_dir = str(Path.home())

        path_str, _ = QFileDialog.getOpenFileName(
            self,
            "Kalibrierungsprofil laden",
            start_dir,
            "JSON-Dateien (*.json);;Alle Dateien (*)",
        )
        if not path_str:
            return
        try:
            profile = PowerCalibrationProfile.load(Path(path_str))
            self._le_profile_name.setText(profile.name)
            for stage in _GAIN_STAGES:
                cal = profile.gains.get(stage)
                if cal is not None and stage in self._gain_tabs:
                    self._gain_tabs[stage].load_calibration(cal)
            Debug.info(f"Loaded calibration profile from {path_str}")
        except Exception as exc:
            Debug.error(f"Failed to load calibration profile: {exc}")
            QMessageBox.critical(self, "Fehler", f"Laden fehlgeschlagen:\n{exc}")

    def closeEvent(self, event) -> None:
        """Detach from the shared DataController's live-voltage signal before closing."""
        if self._data_controller is not None:
            try:
                self._data_controller.intensity_updated.disconnect(self._on_live_voltage)
            except RuntimeError:
                pass
        super().closeEvent(event)
