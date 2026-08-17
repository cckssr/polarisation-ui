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
from PySide6.QtCore import QTimer, Signal, Slot
from PySide6.QtWidgets import (
    QAbstractItemView,
    QButtonGroup,
    QComboBox,
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

from polarisation_ui.core.auto_calibration_settings import AutoCalibrationConnectionSettings
from polarisation_ui.core.exceptions import PM400Error
from polarisation_ui.core.formatting import export_voltage
from polarisation_ui.core.power_calibration import (
    PROFILES_DIR,
    GainCalibration,
    PowerCalibrationProfile,
    select_gain_for_power,
)
from polarisation_ui.infrastructure.config import import_config
from polarisation_ui.infrastructure.devices.pm400 import PM400PowerMeter
from polarisation_ui.infrastructure.logging import Debug

_GAIN_STAGES = (1, 2, 3, 4)

# PM400 live-power poll period while connected.
_PM400_POLL_MS = 250


def _load_gain_power_limits() -> dict[int, tuple[float, float]]:
    """Parse pdtia.gain_auto_switch_power_W from config.json into {stage: (min_W, max_W)}."""
    raw = import_config().get("pdtia", {}).get("gain_auto_switch_power_W", {})
    limits: dict[int, tuple[float, float]] = {}
    for key, bounds in raw.items():
        try:
            limits[int(key)] = (float(bounds["min"]), float(bounds["max"]))
        except (KeyError, TypeError, ValueError):
            Debug.warning(f"Ignoring malformed pdtia.gain_auto_switch_power_W entry: {key!r}")
    return limits


_GAIN_POWER_LIMITS = _load_gain_power_limits()


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
        self._live_pm400_power_W: float | None = None
        self._pm = PM400PowerMeter()
        self._pm_poll_timer = QTimer(self)
        self._pm_poll_timer.timeout.connect(self._on_pm400_power_poll)
        self._setup_ui()
        self._connect_live_updates()
        if self._data_controller is not None:
            self._sync_gain_buttons()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        layout.addWidget(self._build_gain_group())

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

        self._spin_wavelength = QDoubleSpinBox()
        self._spin_wavelength.setRange(1.0, 10000.0)
        self._spin_wavelength.setDecimals(1)
        self._spin_wavelength.setSuffix(" nm")
        self._spin_wavelength.setValue(633.0)
        self._spin_wavelength.setToolTip(
            "Laserwellenlänge — die Responsivität des Detektors ist wellenlängenabhängig."
        )
        profile_form.addRow("Wellenlänge:", self._spin_wavelength)

        btn_row = QHBoxLayout()
        self._btn_save = QPushButton("Kalibrierung speichern")
        self._btn_save.clicked.connect(self._save_profile)
        btn_load = QPushButton("Kalibrierung laden…")
        btn_load.clicked.connect(self._load_profile)
        btn_row.addWidget(self._btn_save)
        btn_row.addWidget(btn_load)
        profile_form.addRow(btn_row)

        layout.addWidget(profile_group)

        layout.addWidget(self._build_pm400_group())
        layout.addWidget(self._build_live_values_group())

        # Close button
        close_btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close_btn_box.rejected.connect(self.close)
        layout.addWidget(close_btn_box)

    def _build_gain_group(self) -> QGroupBox:
        """PD-TIA gain control: manual per-stage buttons + an "Automatisch" toggle.

        Clicking a manual button also switches the active data-entry tab so the
        point table always matches whatever gain is physically engaged.
        """
        group = QGroupBox("PD-TIA Verstärkung")
        row = QHBoxLayout(group)
        row.setContentsMargins(8, 6, 8, 6)

        self._gain_buttons: dict[int, QPushButton] = {}
        self._gain_button_group = QButtonGroup(self)
        self._gain_button_group.setExclusive(True)
        for stage in _GAIN_STAGES:
            btn = QPushButton(f"Gain {stage}")
            btn.setCheckable(True)
            btn.clicked.connect(lambda _checked, s=stage: self._on_gain_button_clicked(s))
            row.addWidget(btn)
            self._gain_button_group.addButton(btn, stage)
            self._gain_buttons[stage] = btn

        self._btn_auto_gain = QPushButton("Automatisch")
        self._btn_auto_gain.setCheckable(True)
        self._btn_auto_gain.setToolTip(
            "Verstärkung automatisch anhand der PM400-Leistung wählen.\n"
            "Grenzwerte je Gain: config.json → pdtia.gain_auto_switch_power_W"
        )
        self._btn_auto_gain.toggled.connect(self._on_auto_gain_toggled)
        row.addWidget(self._btn_auto_gain)

        self._lbl_gain_status = QLabel("—")
        row.addWidget(self._lbl_gain_status, 1)

        if self._data_controller is None:
            group.setEnabled(False)
        if not _GAIN_POWER_LIMITS:
            self._btn_auto_gain.setEnabled(False)
            self._btn_auto_gain.setToolTip(
                "Keine Grenzwerte konfiguriert (pdtia.gain_auto_switch_power_W in config.json)."
            )
        return group

    def _build_pm400_group(self) -> QGroupBox:
        """PM400 connection + beamsplitter-attenuation control."""
        group = QGroupBox("PM400 Leistungsmesser")
        form = QFormLayout(group)
        form.setContentsMargins(8, 6, 8, 6)
        form.setVerticalSpacing(4)

        settings = AutoCalibrationConnectionSettings.load()

        self._cb_pm400 = QComboBox()
        self._cb_pm400.setEditable(True)
        if settings.pm400_visa_resource:
            self._cb_pm400.setEditText(settings.pm400_visa_resource)
        btn_refresh = QPushButton("Aktualisieren")
        btn_refresh.clicked.connect(self._refresh_pm400_list)
        self._btn_connect_pm400 = QPushButton("Verbinden")
        self._btn_connect_pm400.clicked.connect(self._toggle_pm400)

        conn_row = QHBoxLayout()
        conn_row.addWidget(self._cb_pm400, 1)
        conn_row.addWidget(btn_refresh)
        conn_row.addWidget(self._btn_connect_pm400)
        form.addRow("VISA-Ressource:", conn_row)

        self._lbl_pm400_status = QLabel("Nicht verbunden")
        form.addRow(self._lbl_pm400_status)

        self._spin_attenuation = QDoubleSpinBox()
        self._spin_attenuation.setRange(0.0, 60.0)
        self._spin_attenuation.setDecimals(2)
        self._spin_attenuation.setSuffix(" dB")
        self._spin_attenuation.setValue(settings.beamsplitter_attenuation_dB)

        self._btn_toggle_attenuation = QPushButton("Abschwächung setzen")
        self._btn_toggle_attenuation.setToolTip(
            "Setzt die PM400-Abschwächung auf den nebenstehenden Wert, "
            "bzw. schaltet sie aus, falls bereits aktiv."
        )
        self._btn_toggle_attenuation.setEnabled(False)
        self._btn_toggle_attenuation.clicked.connect(self._toggle_attenuation)

        att_row = QHBoxLayout()
        att_row.addWidget(self._spin_attenuation)
        att_row.addWidget(self._btn_toggle_attenuation)
        form.addRow("Abschwächung:", att_row)

        self._refresh_pm400_list()
        return group

    def _build_live_values_group(self) -> QGroupBox:
        group = QGroupBox("Live-Werte")
        form = QFormLayout(group)
        form.setContentsMargins(8, 6, 8, 6)
        form.setVerticalSpacing(4)
        self._lbl_live = QLabel("—")
        form.addRow("Detektorspannung:", self._lbl_live)
        self._lbl_live_power = QLabel("—")
        form.addRow("PM400-Leistung:", self._lbl_live_power)
        return group

    def _connect_live_updates(self) -> None:
        if self._data_controller is None:
            return
        self._data_controller.intensity_updated.connect(self._on_live_voltage)

    @Slot(float)
    def _on_live_voltage(self, voltage: float) -> None:
        self._live_voltage = voltage
        self._lbl_live.setText(f"{export_voltage(voltage)} V")
        for tab in self._gain_tabs.values():
            tab.set_live_voltage(voltage)

    # ==================== PD-TIA Gain Control ====================

    def _sync_gain_buttons(self) -> None:
        """Reflect the actually-active hardware gain in the button group (no hardware write)."""
        if self._data_controller is None:
            return
        current = self._data_controller.pdtia_gain
        if current in self._gain_buttons:
            self._gain_buttons[current].setChecked(True)
            self._update_gain_status(current, auto=self._btn_auto_gain.isChecked())

    def _update_gain_status(self, stage: int, auto: bool) -> None:
        mode = "automatisch" if auto else "manuell"
        self._lbl_gain_status.setText(f"Aktive Verstärkung: Gain {stage} ({mode})")

    def _on_gain_button_clicked(self, stage: int) -> None:
        if self._data_controller is None:
            return
        ok = self._data_controller.set_pdtia_gain(stage)
        if ok:
            self._tab_widget.setCurrentIndex(stage - 1)
            self._update_gain_status(stage, auto=False)
        else:
            QMessageBox.warning(self, "PD-TIA", f"Gain {stage} konnte nicht gesetzt werden.")
            self._sync_gain_buttons()

    @Slot(bool)
    def _on_auto_gain_toggled(self, checked: bool) -> None:
        for btn in self._gain_buttons.values():
            btn.setEnabled(not checked)
        if checked:
            self._maybe_auto_switch_gain()
        else:
            self._sync_gain_buttons()

    def _maybe_auto_switch_gain(self) -> None:
        if (
            self._data_controller is None
            or self._live_pm400_power_W is None
            or not _GAIN_POWER_LIMITS
        ):
            return
        current = self._data_controller.pdtia_gain or None
        target = select_gain_for_power(self._live_pm400_power_W, _GAIN_POWER_LIMITS, current)
        if target is None or target == current:
            return
        ok = self._data_controller.set_pdtia_gain(target)
        if ok:
            self._tab_widget.setCurrentIndex(target - 1)
            self._update_gain_status(target, auto=True)
            Debug.info(
                f"Auto-Gain: switched to stage {target} (P={self._live_pm400_power_W:.3e} W)"
            )
        if target in self._gain_buttons:
            self._gain_buttons[target].setChecked(True)

    # ==================== PM400 ====================

    @Slot()
    def _refresh_pm400_list(self) -> None:
        current = self._cb_pm400.currentText()
        resources = PM400PowerMeter.list_resources()
        self._cb_pm400.clear()
        for r in resources:
            self._cb_pm400.addItem(r)
        if current and self._cb_pm400.findText(current) < 0:
            self._cb_pm400.addItem(current)
        if current:
            idx = self._cb_pm400.findText(current)
            if idx >= 0:
                self._cb_pm400.setCurrentIndex(idx)

    @Slot()
    def _toggle_pm400(self) -> None:
        if self._pm.is_connected():
            self._pm_poll_timer.stop()
            self._pm.disconnect()
            self._lbl_pm400_status.setText("Nicht verbunden")
            self._btn_connect_pm400.setText("Verbinden")
            self._btn_toggle_attenuation.setEnabled(False)
            self._live_pm400_power_W = None
            self._lbl_live_power.setText("—")
            return

        resource = self._cb_pm400.currentText().strip()
        if not resource:
            QMessageBox.warning(self, "PM400", "Keine VISA-Ressource angegeben.")
            return
        try:
            self._pm.connect(resource)
            info = self._pm.sensor_info()
            sensor_str = " | ".join(str(x) for x in info[:3]) if info else "–"
            self._lbl_pm400_status.setText(f"Verbunden: {sensor_str}")
            self._btn_connect_pm400.setText("Trennen")
            self._btn_toggle_attenuation.setEnabled(True)
            try:
                att_dB = self._pm.get_attenuation_dB()
                self._btn_toggle_attenuation.setText(
                    "Abschwächung ausschalten" if att_dB > 0.0 else "Abschwächung setzen"
                )
            except PM400Error:
                pass
            self._pm_poll_timer.start(_PM400_POLL_MS)
        except PM400Error as exc:
            QMessageBox.critical(self, "PM400 Fehler", str(exc))

    @Slot()
    def _on_pm400_power_poll(self) -> None:
        if not self._pm.is_connected():
            return
        try:
            power_W = self._pm.read_power_W()
        except PM400Error as exc:
            Debug.warning(f"PM400 read failed: {exc}")
            return
        self._live_pm400_power_W = power_W
        self._lbl_live_power.setText(f"{power_W:.3e} W")
        if self._btn_auto_gain.isChecked():
            self._maybe_auto_switch_gain()

    @Slot()
    def _toggle_attenuation(self) -> None:
        if not self._pm.is_connected():
            return
        try:
            current_dB = self._pm.get_attenuation_dB()
            if current_dB > 0.0:
                self._pm.set_attenuation_dB(0.0)
                self._btn_toggle_attenuation.setText("Abschwächung setzen")
            else:
                self._pm.set_attenuation_dB(self._spin_attenuation.value())
                self._btn_toggle_attenuation.setText("Abschwächung ausschalten")
        except PM400Error as exc:
            QMessageBox.critical(self, "PM400 Fehler", str(exc))

    @Slot()
    def _save_profile(self) -> None:
        name = self._le_profile_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Kein Name", "Bitte einen Profilnamen eingeben.")
            return

        profile = PowerCalibrationProfile(name=name, wavelength_nm=self._spin_wavelength.value())
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
            self._spin_wavelength.setValue(
                profile.wavelength_nm if profile.wavelength_nm is not None else 633.0
            )
            for stage in _GAIN_STAGES:
                cal = profile.gains.get(stage)
                if cal is not None and stage in self._gain_tabs:
                    self._gain_tabs[stage].load_calibration(cal)
            Debug.info(f"Loaded calibration profile from {path_str}")
        except Exception as exc:
            Debug.error(f"Failed to load calibration profile: {exc}")
            QMessageBox.critical(self, "Fehler", f"Laden fehlgeschlagen:\n{exc}")

    def closeEvent(self, event) -> None:
        """Detach from DataController's live-voltage signal and disconnect the PM400."""
        if self._data_controller is not None:
            try:
                self._data_controller.intensity_updated.disconnect(self._on_live_voltage)
            except RuntimeError:
                pass
        self._pm_poll_timer.stop()
        if self._pm.is_connected():
            self._pm.disconnect()
        super().closeEvent(event)
