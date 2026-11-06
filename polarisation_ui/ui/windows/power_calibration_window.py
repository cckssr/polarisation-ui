"""Power-calibration tool for PD-TIA detector.

Usage workflow:
  1. Set up the bench: calibrated power meter + constant laser + ND filters.
  2. Select a PDTIA gain stage (1–4) in the tab bar.
  3. Read the optical power from your meter → enter it in the power field.
  4. Read the sensor voltage (live button fills it automatically) → enter it in the voltage field.
  5. Click the add button to add the (voltage, power) pair.
  6. Repeat with different ND filters / power levels for this gain.
  7. Switch to the next gain stage and repeat.
  8. Enter a profile name and click the save button.

The computed W/V conversion factor (mean of P/V across all points per stage) is
shown in real time and is used by the main window for the live wattage display.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import TYPE_CHECKING

import pyqtgraph as pg
from PySide6.QtCore import QTimer, Signal, Slot
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHeaderView,
    QMessageBox,
    QTableWidgetItem,
    QWidget,
)

from polarisation_ui.core.auto_calibration_settings import AutoCalibrationConnectionSettings
from polarisation_ui.core.exceptions import PM400Error
from polarisation_ui.core.formatting import export_voltage
from polarisation_ui.core.power_calibration import (
    PROFILES_DIR,
    GainCalibration,
    PowerCalibrationProfile,
)
from polarisation_ui.infrastructure.config import AppConfig, default_config
from polarisation_ui.infrastructure.devices.pm400 import PM400PowerMeter
from polarisation_ui.infrastructure.logging import Debug
from polarisation_ui.pyqt.ui_power_calibration import Ui_PowerCalibrationWindow
from polarisation_ui.pyqt.ui_power_calibration_gain_tab import Ui_PowerCalibrationGainTab
from polarisation_ui.ui.common.pm400_combo import populate_pm400_combo
from polarisation_ui.ui.i18n import apply_strings
from polarisation_ui.ui.plot_style import plot_colors, style_plot

if TYPE_CHECKING:
    from polarisation_ui.ui.controllers.data_controller import DataController

_GAIN_STAGES = (1, 2, 3, 4)

# PM400 live-power poll period while connected.
_PM400_POLL_MS = 250

_DEFAULT_WAVELENGTH_NM = 633.0


class GainCalibrationTab(QWidget):
    """One tab per PDTIA gain stage — shows the (V, W) point table and a plot."""

    points_changed = Signal()

    def __init__(
        self,
        gain_stage: int,
        parent: QWidget | None = None,
        config: AppConfig | None = None,
    ) -> None:
        """Load the Designer form for ``gain_stage`` and wire the point table and plot."""
        super().__init__(parent)
        self.config = config or default_config()
        self._gain_stage = gain_stage
        self._cal = GainCalibration(gain_stage=gain_stage)
        self._live_voltage: float | None = None

        self.ui = Ui_PowerCalibrationGainTab()
        self.ui.setupUi(self)
        apply_strings(self, self.config.section("ui").get("power_calibration_gain_tab", {}))
        self.ui.groupEntry.setTitle(self._text("text_entry_title", stage=gain_stage))
        self.ui.valueFactor.setText(self._text("text_factor_none"))

        self.ui.tablePoints.setHorizontalHeaderLabels(
            [
                self._text("header_voltage"),
                self._text("header_power"),
                self._text("header_ratio"),
            ]
        )
        self.ui.tablePoints.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._setup_plot()

        self.ui.buttonAdd.clicked.connect(self._add_point)
        self.ui.buttonRemove.clicked.connect(self._remove_selected)
        self.ui.buttonLive.clicked.connect(self._fill_live_voltage)

    def _text(self, key: str, **fmt: object) -> str:
        return self.config.text(f"power_calibration_gain_tab.{key}", **fmt)

    def _setup_plot(self) -> None:
        """Axis labels, grid and the data/fit curves of the promoted plot widget."""
        colors = plot_colors()
        plot = self.ui.calibrationPlot
        plot.showGrid(x=True, y=True, alpha=0.3)
        plot.setLabel("bottom", self._text("plot_x_label"), units=self._text("plot_x_units"))
        plot.setLabel("left", self._text("plot_y_label"), units=self._text("plot_y_units"))
        self._scatter = plot.plot(
            [],
            [],
            pen=None,
            symbol="o",
            symbolSize=8,
            symbolBrush=pg.mkBrush(*colors.series_color(0), colors.point_alpha),
            symbolPen=pg.mkPen(None),
        )
        self._fit_line = plot.plot([], [], pen=pg.mkPen(colors.fit, width=1.5))
        style_plot(plot)

    def set_live_voltage(self, voltage: float) -> None:
        """Called by parent to update the cached live voltage for the "Live" button."""
        self._live_voltage = voltage
        self.ui.buttonLive.setEnabled(True)

    def _fill_live_voltage(self) -> None:
        if self._live_voltage is not None:
            self.ui.spinVoltage.setValue(self._live_voltage)

    @Slot()
    def _add_point(self) -> None:
        v = self.ui.spinVoltage.value()
        p = self.ui.spinPower.value()
        title = self._text("title_invalid_input")
        if v <= 0.0:
            QMessageBox.warning(
                self, title, self.config.message("power_calibration.voltage_not_positive")
            )
            return
        if p <= 0.0:
            QMessageBox.warning(
                self, title, self.config.message("power_calibration.power_not_positive")
            )
            return
        self._cal.add_point(v, p)
        self._refresh()
        self.points_changed.emit()

    @Slot()
    def _remove_selected(self) -> None:
        row = self.ui.tablePoints.currentRow()
        if row < 0:
            return
        self._cal.remove_point(row)
        self._refresh()
        self.points_changed.emit()

    def _refresh(self) -> None:
        table = self.ui.tablePoints
        pts = self._cal.points
        table.setRowCount(len(pts))
        for i, (v, p) in enumerate(pts):
            ratio = p / v if v > 0 else float("nan")
            table.setItem(i, 0, QTableWidgetItem(export_voltage(v)))
            # NOTE: power (p) here uses 9 dp — no power_dp bucket exists in
            # DisplayFormat/ExportFormat, so this stays a hardcoded outlier
            # rather than changing visible precision.
            table.setItem(i, 1, QTableWidgetItem(f"{p:.9f}"))
            table.setItem(i, 2, QTableWidgetItem(f"{ratio:.4e}" if not math.isnan(ratio) else "—"))

        factor = self._cal.conversion_factor_W_per_V()
        if factor is None:
            self.ui.valueFactor.setText(self._text("text_factor_none"))
        else:
            self.ui.valueFactor.setText(
                self._text("text_factor", factor=f"{factor:.4e}", stage=self._gain_stage)
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
        """The calibration points entered so far for this gain stage."""
        return self._cal

    def load_calibration(self, cal: GainCalibration) -> None:
        """Replace the calibration shown by this tab (e.g. from a loaded profile)."""
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
        data_controller: DataController | None = None,
        pm400: PM400PowerMeter | None = None,
        parent: QWidget | None = None,
        config: AppConfig | None = None,
    ) -> None:
        """Load the Designer form, add one tab per gain stage and wire the signals."""
        super().__init__(parent)
        self.config = config or default_config()
        self._data_controller = data_controller
        self._gain_tabs: dict[int, GainCalibrationTab] = {}
        self._live_voltage: float = 0.0
        self._live_pm400_power_W: float | None = None
        # Reuse MainWindow's PM400 session when given (one VISA session only).
        self._pm_shared = pm400 is not None
        self._pm = pm400 if pm400 is not None else PM400PowerMeter()
        self._pm_poll_timer = QTimer(self)
        self._pm_poll_timer.timeout.connect(self._on_pm400_power_poll)

        self.ui = Ui_PowerCalibrationWindow()
        self.ui.setupUi(self)
        apply_strings(self, self.config.section("ui").get("power_calibration", {}))
        close_button = self.ui.buttonBox.button(QDialogButtonBox.StandardButton.Close)
        close_button.setText(self._text("text_close"))
        self.ui.valuePm400Status.setText(self._message("pm400_not_connected"))

        for stage in _GAIN_STAGES:
            tab = GainCalibrationTab(gain_stage=stage, config=self.config)
            self.ui.tabGains.addTab(tab, self._text("text_gain_tab", stage=stage))
            self._gain_tabs[stage] = tab

        settings = AutoCalibrationConnectionSettings.load()
        self._pm400_preferred = settings.pm400_visa_resource
        self.ui.spinAttenuation.setValue(settings.beamsplitter_attenuation_dB)

        self.ui.buttonSave.clicked.connect(self._save_profile)
        self.ui.buttonLoad.clicked.connect(self._load_profile)
        self.ui.buttonRefresh.clicked.connect(self._refresh_pm400_list)
        self.ui.buttonConnect.clicked.connect(self._toggle_pm400)
        self.ui.buttonToggleAttenuation.clicked.connect(self._toggle_attenuation)

        self._refresh_pm400_list()
        self._connect_live_updates()

    def _text(self, key: str, **fmt: object) -> str:
        return self.config.text(f"power_calibration.{key}", **fmt)

    def _message(self, key: str, **fmt: object) -> str:
        return self.config.message(f"power_calibration.{key}", **fmt)

    def _connect_live_updates(self) -> None:
        if self._data_controller is None:
            return
        self._data_controller.intensity_updated.connect(self._on_live_voltage)

    @Slot(float)
    def _on_live_voltage(self, voltage: float) -> None:
        self._live_voltage = voltage
        self.ui.valueDetectorVoltage.setText(
            self._text("text_voltage_value", voltage=export_voltage(voltage))
        )
        for tab in self._gain_tabs.values():
            tab.set_live_voltage(voltage)

    # ==================== PM400 ====================

    @Slot()
    def _refresh_pm400_list(self) -> None:
        if not self._pm_shared:
            populate_pm400_combo(self.ui.comboPm400, self._pm400_preferred)
            return
        # Shared session: connecting/disconnecting happens in MainWindow.
        self.ui.comboPm400.setEnabled(False)
        self.ui.buttonConnect.setEnabled(False)
        if self._pm.is_connected():
            info = self._pm.sensor_info()
            sensor_str = " | ".join(str(x) for x in info[:3]) if info else "–"
            self.ui.valuePm400Status.setText(
                self._message("pm400_connected_main", sensor=sensor_str)
            )
            self.ui.buttonToggleAttenuation.setEnabled(True)
            self._pm_poll_timer.start(_PM400_POLL_MS)
        else:
            self.ui.valuePm400Status.setText(self._message("pm400_not_connected_main"))

    @Slot()
    def _toggle_pm400(self) -> None:
        if self._pm.is_connected():
            self._pm_poll_timer.stop()
            self._pm.disconnect()
            self.ui.valuePm400Status.setText(self._message("pm400_not_connected"))
            self.ui.buttonConnect.setText(self._text("text_connect"))
            self.ui.buttonToggleAttenuation.setEnabled(False)
            self._live_pm400_power_W = None
            self.ui.valuePm400Power.setText("—")
            return

        resource = self.ui.comboPm400.currentText().strip()
        if not resource:
            QMessageBox.warning(self, self._text("title_pm400"), self._message("no_resource"))
            return
        try:
            self._pm.connect(resource)
            info = self._pm.sensor_info()
            sensor_str = " | ".join(str(x) for x in info[:3]) if info else "–"
            self.ui.valuePm400Status.setText(self._message("pm400_connected", sensor=sensor_str))
            self.ui.buttonConnect.setText(self._text("text_disconnect"))
            self.ui.buttonToggleAttenuation.setEnabled(True)
            try:
                att_dB = self._pm.get_attenuation_dB()
                self.ui.buttonToggleAttenuation.setText(
                    self._text("text_attenuation_off" if att_dB > 0.0 else "text_attenuation_set")
                )
            except PM400Error:
                pass
            self._pm_poll_timer.start(_PM400_POLL_MS)
        except PM400Error as exc:
            QMessageBox.critical(self, self._text("title_pm400_error"), str(exc))

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
        self.ui.valuePm400Power.setText(self._text("text_power_value", power=f"{power_W:.3e}"))

    @Slot()
    def _toggle_attenuation(self) -> None:
        if not self._pm.is_connected():
            return
        try:
            current_dB = self._pm.get_attenuation_dB()
            if current_dB > 0.0:
                self._pm.set_attenuation_dB(0.0)
                self.ui.buttonToggleAttenuation.setText(self._text("text_attenuation_set"))
            else:
                self._pm.set_attenuation_dB(self.ui.spinAttenuation.value())
                self.ui.buttonToggleAttenuation.setText(self._text("text_attenuation_off"))
        except PM400Error as exc:
            QMessageBox.critical(self, self._text("title_pm400_error"), str(exc))

    @Slot()
    def _save_profile(self) -> None:
        name = self.ui.editProfileName.text().strip()
        if not name:
            QMessageBox.warning(self, self._text("title_no_name"), self._message("no_profile_name"))
            return

        profile = PowerCalibrationProfile(name=name, wavelength_nm=self.ui.spinWavelength.value())
        for stage, tab in self._gain_tabs.items():
            profile.gains[stage] = tab.get_calibration()

        path = PowerCalibrationProfile.default_path(name)
        try:
            profile.save(path)
            Debug.info(f"Power calibration profile saved: {path}")
            QMessageBox.information(
                self,
                self._text("title_saved"),
                self._message("profile_saved", name=name, path=path),
            )
            self.profile_saved.emit()
        except Exception as exc:
            Debug.error(f"Failed to save calibration profile: {exc}")
            QMessageBox.critical(
                self, self._text("title_error"), self._message("save_failed", error=exc)
            )

    @Slot()
    def _load_profile(self) -> None:
        profiles = PowerCalibrationProfile.list_profiles()
        if profiles:
            start_dir = str(PROFILES_DIR)
        else:
            start_dir = str(Path.home())

        path_str, _ = QFileDialog.getOpenFileName(
            self,
            self._text("title_load_profile"),
            start_dir,
            self._text("file_filter_profile"),
        )
        if not path_str:
            return
        try:
            profile = PowerCalibrationProfile.load(Path(path_str))
            self.ui.editProfileName.setText(profile.name)
            self.ui.spinWavelength.setValue(
                profile.wavelength_nm
                if profile.wavelength_nm is not None
                else _DEFAULT_WAVELENGTH_NM
            )
            for stage in _GAIN_STAGES:
                cal = profile.gains.get(stage)
                if cal is not None and stage in self._gain_tabs:
                    self._gain_tabs[stage].load_calibration(cal)
            Debug.info(f"Loaded calibration profile from {path_str}")
        except Exception as exc:
            Debug.error(f"Failed to load calibration profile: {exc}")
            QMessageBox.critical(
                self, self._text("title_error"), self._message("load_failed", error=exc)
            )

    def closeEvent(self, event: QCloseEvent) -> None:
        """Detach from DataController's live-voltage signal and disconnect the PM400."""
        if self._data_controller is not None:
            try:
                self._data_controller.intensity_updated.disconnect(self._on_live_voltage)
            except RuntimeError:
                pass
        self._pm_poll_timer.stop()
        if self._pm.is_connected() and not self._pm_shared:
            self._pm.disconnect()
        super().closeEvent(event)
