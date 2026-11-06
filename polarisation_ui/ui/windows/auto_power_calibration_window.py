"""Automatic power calibration dialog.

Drives an intensity actuator (rotating polariser or stepper-driven ND-filter wheel)
and a Thorlabs PM400 power meter to record (voltage, power) pairs for all
four PDTIA gain stages, then writes a PowerCalibrationProfile in the same
format used by the manual calibration window.

Also hosts four related workflows, each on its own tab: calibrating the
ND filter's usable travel from a power-meter scan (ND range), measuring how
linear its optical density is over several repeated scans (ND linearity), cross-
checking a second PM400 against the first across that range before trusting
it as the calibration reference (detector comparison), and verifying that all
PD-TIA gain stages agree after calibration (gain verification).

Standalone mode (data_controller=None): the dialog manages its own Arduino
connection and shows the groupArduino section.  The Arduino is needed for ADC
reads and PDTIA gain switching during the sweep.
"""

from __future__ import annotations

import json
from datetime import datetime
from functools import partial

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QDialog, QFileDialog, QMessageBox, QTableWidgetItem

from polarisation_ui.core.auto_calibration_settings import (
    AutoCalibrationConnectionSettings,
    AutoCalibrationParams,
)
from polarisation_ui.core.detector_crosscheck import DetectorComparisonResult
from polarisation_ui.core.exceptions import KDC101Error, NDStageError, PM400Error
from polarisation_ui.core.formatting import fmt_angle
from polarisation_ui.core.gain_crosscheck import GainCrossCheckLevel, GainCrossCheckResult
from polarisation_ui.core.nd_filter import NDFilterRange
from polarisation_ui.core.nd_linearity import (
    BACKWARD,
    NDLinearityReport,
    NDLinearityScan,
    analyse_linearity_set,
)
from polarisation_ui.core.power_calibration import (
    PowerCalibrationProfile,
    load_gain_power_limits,
)
from polarisation_ui.core.power_calibration import (
    PowerCalibrationProfile as _Profile,
)
from polarisation_ui.infrastructure.config import AppConfig, default_config
from polarisation_ui.infrastructure.device_manager import GoniometerDeviceManager
from polarisation_ui.infrastructure.devices.intensity_actuator import (
    NDFilterActuator,
    PolariserActuator,
)
from polarisation_ui.infrastructure.devices.kdc101_polariser import KDC101Polariser
from polarisation_ui.infrastructure.devices.nd_stepper import NDStepperStage
from polarisation_ui.infrastructure.devices.pm400 import PM400PowerMeter
from polarisation_ui.infrastructure.logging import Debug
from polarisation_ui.infrastructure.qt_threads import (
    AlignPolariserWorker,
    AutoPowerCalibrationWorker,
    DetectorCrossCheckWorker,
    GainCrossCheckWorker,
    KDC101HomeWorker,
    NDLinearityScanWorker,
    NDRangeScanWorker,
)
from polarisation_ui.pyqt.ui_auto_power_calibration import Ui_AutoPowerCalibrationDialog
from polarisation_ui.ui.common.pm400_combo import populate_pm400_combo
from polarisation_ui.ui.i18n import apply_strings

_GAIN_COLUMNS = {1: 2, 2: 3, 3: 4, 4: 5}  # gain stage -> tableGainVerify column index
_SECTION = "auto_power_calibration"  # key of this dialog in config.json (ui.* and messages.*)


class AutoPowerCalibrationWindow(QDialog):
    """Non-modal dialog for automated detector power calibration.

    When *data_controller* is provided the dialog is opened from MainWindow
    and the existing DataController supplies the Arduino device manager.
    When *data_controller* is None the dialog runs standalone: it shows the
    groupArduino section so the user can connect to the Arduino directly.
    """

    profile_saved = Signal()

    def __init__(
        self,
        data_controller=None,
        pm400: PM400PowerMeter | None = None,
        parent=None,
        config: AppConfig | None = None,
    ) -> None:
        """Build the dialog UI; standalone mode is enabled when data_controller is None.

        ``config`` provides the German texts and the gain power windows (default: the
        packaged ``default_config()``).
        """
        super().__init__(parent)
        self.config: AppConfig = config if config is not None else default_config()
        self.ui = Ui_AutoPowerCalibrationDialog()
        self.ui.setupUi(self)
        apply_strings(self, self.config.section("ui").get(_SECTION, {}))
        self._apply_code_strings()

        self._data_controller = data_controller
        self._standalone = data_controller is None
        # In standalone mode we own the device manager; otherwise we borrow it.
        self._device_manager: GoniometerDeviceManager | None = (
            GoniometerDeviceManager(use_mock=False) if self._standalone else None
        )

        self._kdc = KDC101Polariser()
        # A PM400 handed in by MainWindow is the one VISA session to the meter
        # (it is also the active detector there): reuse it, never open a second.
        self._pm_shared = pm400 is not None
        self._pm = pm400 if pm400 is not None else PM400PowerMeter()
        self._nd = NDStepperStage()
        self._pm_b = PM400PowerMeter()

        self._worker: AutoPowerCalibrationWorker | None = None
        self._align_worker: AlignPolariserWorker | None = None
        self._home_thread: KDC101HomeWorker | None = None
        self._nd_home_thread: KDC101HomeWorker | None = None
        self._nd_scan_worker: NDRangeScanWorker | None = None
        self._nd_lin_worker: NDLinearityScanWorker | None = None
        self._nd_range_active: bool = False
        self._nd_lin_active: bool = False
        # Linearity scans accumulate across runs so that repeated runs (e.g.
        # before/after remounting the filter) can be compared in one report.
        self._nd_lin_scans: list[NDLinearityScan] = []
        self._xcheck_worker: DetectorCrossCheckWorker | None = None
        self._verify_worker: GainCrossCheckWorker | None = None
        self._verify_from_curve = False  # reference of the running/last gain verification

        self._profile: PowerCalibrationProfile | None = None
        self._angle_offset_deg: float = 0.0
        # Fresh-this-session ND range scan (full curve). Falls back to the
        # 2-point summary persisted in settings when no fresh scan was run.
        self._nd_range: NDFilterRange | None = None
        self._xcheck_result: DetectorComparisonResult | None = None
        self._verify_result: GainCrossCheckResult | None = None

        self._settings = AutoCalibrationConnectionSettings.load()

        # The Arduino section is only relevant in standalone mode.
        self.ui.groupArduino.setVisible(self._standalone)

        self._apply_settings()
        self._connect_signals()
        self._refresh_kdc_list()
        self._refresh_nd_list()
        self._refresh_pm_list()
        self._refresh_pm_b_list()
        if self._standalone:
            self._refresh_arduino_list()
        self._on_intensity_source_changed()
        self._update_start_button_state()
        self._refresh_nd_lin_status()

    # ── Setup ─────────────────────────────────────────────────────────────────

    def _t(self, key: str, **fmt: object) -> str:
        """Text ``ui.auto_power_calibration.<key>`` of the configuration."""
        return self.config.text(f"{_SECTION}.{key}", **fmt)

    def _m(self, key: str, **fmt: object) -> str:
        """Message ``messages.auto_power_calibration.<key>`` of the configuration."""
        return self.config.message(f"{_SECTION}.{key}", **fmt)

    def _apply_code_strings(self) -> None:
        """Set the texts Designer cannot hold as plain widget text: tab titles and table headers."""
        pages = (
            (self.ui.tabCalibration, "tab_calibration"),
            (self.ui.tabNDRange, "tab_nd_range"),
            (self.ui.tabNDLinearity, "tab_nd_linearity"),
            (self.ui.tabDetectorCompare, "tab_detector_compare"),
            (self.ui.tabGainVerify, "tab_gain_verify"),
        )
        for page, key in pages:
            self.ui.tabMode.setTabText(self.ui.tabMode.indexOf(page), self._t(key))
        columns = self.config.get(f"ui.{_SECTION}.gain_verify_columns", [])
        if isinstance(columns, list) and columns:
            self.ui.tableGainVerify.setHorizontalHeaderLabels([str(c) for c in columns])
        for plot in (
            self.ui.calibrationPlot,
            self.ui.ndRangePlot,
            self.ui.ndLinearityPlot,
            self.ui.xCheckPlot,
        ):
            plot.apply_config(self.config)

    def _warn(self, title_key: str, message_key: str, **fmt: object) -> None:
        QMessageBox.warning(self, self._t(title_key), self._m(message_key, **fmt))

    def _error(self, title_key: str, text: str) -> None:
        QMessageBox.critical(self, self._t(title_key), text)

    def _is_abort_message(self, message: str) -> bool:
        """Whether a worker's failure message only reports a user abort."""
        return self._m("abort_marker") in message.lower()

    def _apply_settings(self) -> None:
        s = self._settings
        if s.kdc101_conn_id:
            self.ui.comboKDC.addItem(s.kdc101_conn_id)
        if s.nd_stage_conn_id:
            self.ui.comboNDStage.addItem(s.nd_stage_conn_id)
        if s.pm400_b_visa_resource:
            self.ui.comboPM400B.setEditText(s.pm400_b_visa_resource)
        self.ui.spinWavelength.setValue(s.wavelength_nm)
        self.ui.spinAttenuation.setValue(s.beamsplitter_attenuation_dB)
        if s.angle_offset_deg != 0.0:
            self._angle_offset_deg = s.angle_offset_deg
            self.ui.valueAngleOffset.setText(
                self._t("angle_offset_restored", angle=fmt_angle(s.angle_offset_deg))
            )
        if s.nd_pos_clear_deg is not None and s.nd_pos_dark_deg is not None:
            self.ui.valueNDRange.setText(
                self._t(
                    "nd_range_restored",
                    clear=f"{s.nd_pos_clear_deg:.2f}",
                    dark=f"{s.nd_pos_dark_deg:.2f}",
                )
            )

    def _set_phase(self, text: str) -> None:
        """Show *text* in the phase label; the full text stays available as tooltip.

        The label ignores its text width so a long message cannot enlarge the
        dialog — it is clipped instead.
        """
        self.ui.valuePhase.setText(text)
        self.ui.valuePhase.setToolTip(text)

    def _connect_signals(self) -> None:
        if self._standalone:
            self.ui.buttonRefreshArduino.clicked.connect(self._refresh_arduino_list)
            self.ui.buttonConnectArduino.clicked.connect(self._toggle_arduino)

        self.ui.buttonRefreshKDC.clicked.connect(self._refresh_kdc_list)
        self.ui.buttonConnectKDC.clicked.connect(self._toggle_kdc)
        self.ui.buttonHomeKDC.clicked.connect(self._home_kdc)

        self.ui.buttonRefreshNDStage.clicked.connect(self._refresh_nd_list)
        self.ui.buttonConnectNDStage.clicked.connect(self._toggle_nd)
        self.ui.buttonHomeNDStage.clicked.connect(self._home_nd)
        self.ui.buttonZeroNDStage.clicked.connect(self._zero_nd)
        self.ui.buttonSelfTestNDStage.clicked.connect(self._selftest_nd)
        self.ui.buttonNDMotorOff.clicked.connect(self._nd_motor_off)
        for button, delta in (
            (self.ui.buttonNDJogMinus5, -5.0),
            (self.ui.buttonNDJogMinus1, -1.0),
            (self.ui.buttonNDJogPlus1, 1.0),
            (self.ui.buttonNDJogPlus5, 5.0),
        ):
            button.clicked.connect(partial(self._jog_nd, delta))

        self.ui.buttonRefreshPM400.clicked.connect(self._refresh_pm_list)
        self.ui.buttonConnectPM400.clicked.connect(self._toggle_pm400)
        self.ui.buttonZeroPM400.clicked.connect(self._zero_pm400)

        self.ui.buttonRefreshPM400B.clicked.connect(self._refresh_pm_b_list)
        self.ui.buttonConnectPM400B.clicked.connect(self._toggle_pm400_b)
        self.ui.buttonZeroPM400B.clicked.connect(self._zero_pm400_b)

        self.ui.radioSourcePolariser.toggled.connect(self._on_intensity_source_changed)
        self.ui.radioSourceND.toggled.connect(self._on_intensity_source_changed)

        self.ui.buttonAlignPolariser.clicked.connect(self._start_align)
        self.ui.buttonAbortAlign.clicked.connect(self._abort_align)

        self.ui.editProfileName.textChanged.connect(self._update_output_path)
        self.ui.checkPowerFromCurve.toggled.connect(self._on_power_source_changed)
        self.ui.buttonStart.clicked.connect(self._start_sweep)
        self.ui.buttonAbort.clicked.connect(self._abort_sweep)
        self.ui.buttonSave.clicked.connect(self._save_profile)

        self.ui.buttonScanNDRange.clicked.connect(self._start_nd_scan)
        self.ui.buttonAbortNDScan.clicked.connect(self._abort_nd_scan)

        self.ui.buttonScanNDLin.clicked.connect(self._start_nd_lin)
        self.ui.buttonAbortNDLin.clicked.connect(self._abort_nd_lin)
        self.ui.buttonClearNDLin.clicked.connect(self._clear_nd_lin)
        self.ui.spinNDLinTol.valueChanged.connect(self._refresh_nd_lin_report)
        self.ui.spinNDLinFloorUW.valueChanged.connect(self._refresh_nd_lin_report)

        self.ui.buttonStartXCheck.clicked.connect(self._start_xcheck)
        self.ui.buttonAbortXCheck.clicked.connect(self._abort_xcheck)
        self.ui.buttonSaveXCheck.clicked.connect(self._save_xcheck)

        self.ui.checkVerifyFromCurve.toggled.connect(self._on_verify_source_changed)
        self.ui.buttonStartVerify.clicked.connect(self._start_verify)
        self.ui.buttonAbortVerify.clicked.connect(self._abort_verify)

    # ── Arduino (standalone mode) ─────────────────────────────────────────────

    @Slot()
    def _refresh_arduino_list(self) -> None:
        current = self.ui.comboArduinoPort.currentText()
        self.ui.comboArduinoPort.clear()
        ports = GoniometerDeviceManager.list_available_ports()
        for p in ports:
            self.ui.comboArduinoPort.addItem(p)
        if current and self.ui.comboArduinoPort.findText(current) < 0:
            self.ui.comboArduinoPort.addItem(current)
        if current:
            idx = self.ui.comboArduinoPort.findText(current)
            if idx >= 0:
                self.ui.comboArduinoPort.setCurrentIndex(idx)
        self._update_start_button_state()

    @Slot()
    def _toggle_arduino(self) -> None:
        assert self._device_manager is not None
        if self._device_manager.is_encoder_connected():
            self._device_manager.disconnect_encoders()
            self.ui.valueArduinoStatus.setText(self._t("status_not_connected"))
            self.ui.buttonConnectArduino.setText(self._t("button_connect"))
        else:
            port = self.ui.comboArduinoPort.currentText().strip()
            if not port:
                self._warn("title_arduino", "no_port")
                return
            ok = self._device_manager.connect_encoders(port)
            if ok:
                self.ui.valueArduinoStatus.setText(self._t("status_connected", name=port))
                self.ui.buttonConnectArduino.setText(self._t("button_disconnect"))
            else:
                status = self._device_manager.get_encoder_status()
                err = status.error_message or self._m("connection_failed_default")
                self._error(
                    "title_arduino_error", self._m("arduino_connect_failed", port=port, error=err)
                )
        self._update_start_button_state()

    # ── KDC101 (polariser) ───────────────────────────────────────────────────

    @Slot()
    def _refresh_kdc_list(self) -> None:
        current = self.ui.comboKDC.currentText()
        self.ui.comboKDC.clear()
        devices = KDC101Polariser.list_devices()
        for conn_id, desc in devices:
            self.ui.comboKDC.addItem(
                self._t("device_entry", conn_id=conn_id, description=desc), userData=conn_id
            )
        if not devices and current:
            self.ui.comboKDC.addItem(current, userData=current)
        self._update_start_button_state()

    @Slot()
    def _toggle_kdc(self) -> None:
        if self._kdc.is_connected():
            self._kdc.disconnect()
            self.ui.valueKDCStatus.setText(self._t("status_not_connected"))
            self.ui.buttonConnectKDC.setText(self._t("button_connect"))
            self.ui.buttonHomeKDC.setEnabled(False)
        else:
            conn_id = self.ui.comboKDC.currentData() or self.ui.comboKDC.currentText()
            if not conn_id:
                self._warn("title_kdc", "no_device")
                return
            try:
                self._kdc.connect(conn_id)
                self.ui.valueKDCStatus.setText(self._t("status_connected", name=conn_id))
                self.ui.buttonConnectKDC.setText(self._t("button_disconnect"))
                self.ui.buttonHomeKDC.setEnabled(True)
            except KDC101Error as exc:
                self._error("title_kdc_error", str(exc))
        self._update_start_button_state()

    @Slot()
    def _home_kdc(self) -> None:
        if not self._kdc.is_connected():
            return
        self.ui.buttonHomeKDC.setEnabled(False)
        self._set_phase(self._m("home_running"))
        self._home_thread = KDC101HomeWorker(self._kdc, parent=self)
        self._home_thread.done.connect(self._on_home_done)
        self._home_thread.error.connect(self._on_home_error)
        self._home_thread.start()

    @Slot()
    def _on_home_done(self) -> None:
        self.ui.buttonHomeKDC.setEnabled(True)
        self._set_phase(self._m("home_done"))

    @Slot(str)
    def _on_home_error(self, msg: str) -> None:
        self.ui.buttonHomeKDC.setEnabled(True)
        self._set_phase(self._m("home_failed"))
        self._error("title_kdc_error", msg)

    # ── KDC101 (ND-filter stage) ──────────────────────────────────────────────

    @Slot()
    def _refresh_nd_list(self) -> None:
        current = self.ui.comboNDStage.currentData() or self.ui.comboNDStage.currentText()
        self.ui.comboNDStage.clear()
        devices = NDStepperStage.list_devices()
        for conn_id, desc in devices:
            self.ui.comboNDStage.addItem(
                self._t("device_entry", conn_id=conn_id, description=desc), userData=conn_id
            )
        if current:
            idx = self.ui.comboNDStage.findData(current)
            if idx >= 0:
                self.ui.comboNDStage.setCurrentIndex(idx)
            elif not devices:
                self.ui.comboNDStage.addItem(current, userData=current)
        self._update_start_button_state()

    @Slot()
    def _toggle_nd(self) -> None:
        if self._nd.is_connected():
            self._nd.disconnect()
            self.ui.valueNDStatus.setText(self._t("status_not_connected"))
            self.ui.buttonConnectNDStage.setText(self._t("button_connect"))
            self.ui.buttonHomeNDStage.setEnabled(False)
            self.ui.buttonZeroNDStage.setEnabled(False)
            self.ui.buttonSelfTestNDStage.setEnabled(False)
            self._set_nd_manual_controls_enabled(False)
            self.ui.valueNDDriver.setText(self._t("nd_driver_unknown"))
        else:
            conn_id = self.ui.comboNDStage.currentData() or self.ui.comboNDStage.currentText()
            if not conn_id:
                self._warn("title_nd", "no_port")
                return
            try:
                self._nd.connect(conn_id)
                self.ui.valueNDStatus.setText(self._t("status_connected", name=conn_id))
                self.ui.buttonConnectNDStage.setText(self._t("button_disconnect"))
                self.ui.buttonHomeNDStage.setEnabled(True)
                self.ui.buttonZeroNDStage.setEnabled(True)
                self.ui.buttonSelfTestNDStage.setEnabled(True)
                self._set_nd_manual_controls_enabled(True)
                self._show_nd_position()
                self._show_nd_driver_status()
            except NDStageError as exc:
                self._error("title_nd_error", str(exc))
        self._update_start_button_state()

    @Slot()
    def _home_nd(self) -> None:
        if not self._nd.is_connected():
            return
        self.ui.buttonHomeNDStage.setEnabled(False)
        self._set_phase(self._m("nd_home_running"))
        self._nd_home_thread = KDC101HomeWorker(self._nd, parent=self)
        self._nd_home_thread.done.connect(self._on_nd_home_done)
        self._nd_home_thread.error.connect(self._on_nd_home_error)
        self._nd_home_thread.start()

    @Slot()
    def _zero_nd(self) -> None:
        """Define the wheel's current angle as 0° (the clear end of the filter)."""
        if not self._nd.is_connected():
            return
        try:
            self._nd.zero()
        except NDStageError as exc:
            self._error("title_nd_error", str(exc))
            return
        self._set_phase(self._m("nd_zero_set"))
        self._show_nd_position()

    def _set_nd_manual_controls_enabled(self, enabled: bool) -> None:
        for button in (
            self.ui.buttonNDJogMinus5,
            self.ui.buttonNDJogMinus1,
            self.ui.buttonNDJogPlus1,
            self.ui.buttonNDJogPlus5,
            self.ui.buttonNDMotorOff,
        ):
            button.setEnabled(enabled)

    @Slot()
    def _nd_motor_off(self) -> None:
        """Release the motor so the wheel can be turned by hand (next move re-energises)."""
        if not self._nd.is_connected():
            return
        try:
            self._nd.enable(False)
        except NDStageError as exc:
            self._error("title_nd_error", str(exc))
            return
        self._set_phase(self._m("nd_motor_off"))

    def _jog_nd(self, delta_deg: float) -> None:
        """Nudge the wheel by *delta_deg* to find the zero point by eye."""
        if not self._nd.is_connected():
            return
        try:
            self._nd.jog_deg(delta_deg)
        except NDStageError as exc:
            self._set_phase(self._m("nd_jog_rejected", error=exc))
            return
        self._show_nd_position()

    def _show_nd_driver_status(self) -> None:
        """Show the DRV8825 /FAULT state (OK / FAULT / not wired)."""
        try:
            status = self._nd.get_driver_status()
        except NDStageError:
            return
        keys = {"OK": "nd_driver_ok", "FAULT": "nd_driver_fault", "NA": "nd_driver_na"}
        key = keys.get(status)
        self.ui.valueNDDriver.setText(
            self._t(key) if key else self._t("nd_driver_other", status=status)
        )

    @Slot()
    def _selftest_nd(self) -> None:
        """Move the wheel briefly out and back while the controller watches /FAULT."""
        if not self._nd.is_connected():
            return
        self._set_phase(self._m("nd_selftest_running"))
        try:
            ok, detail = self._nd.self_test()
        except NDStageError as exc:
            self._error("title_nd_error", str(exc))
            return
        self._show_nd_position()
        self._show_nd_driver_status()
        if ok:
            self._set_phase(self._m("nd_selftest_passed"))
        elif detail.startswith("NA"):
            QMessageBox.information(
                self, self._t("title_selftest"), self._m("nd_selftest_not_wired")
            )
        else:
            answer = QMessageBox.question(
                self,
                self._t("title_selftest_failed"),
                self._m("nd_selftest_failed_reset", detail=detail),
            )
            if answer == QMessageBox.StandardButton.Yes:
                self._reset_nd_driver()

    def _reset_nd_driver(self) -> None:
        try:
            self._nd.reset_driver()
        except NDStageError as exc:
            self._error("title_driver_reset", str(exc))
            return
        self._show_nd_driver_status()
        self._set_phase(self._m("nd_driver_reset"))

    def _show_nd_position(self) -> None:
        pos = self._nd.get_position_deg_nowait()
        if pos is not None:
            self.ui.valueNDPosition.setText(self._t("nd_position", angle=f"{pos:.2f}"))

    @Slot()
    def _on_nd_home_done(self) -> None:
        self.ui.buttonHomeNDStage.setEnabled(True)
        self._set_phase(self._m("nd_home_done"))
        self._show_nd_position()

    @Slot(str)
    def _on_nd_home_error(self, msg: str) -> None:
        self.ui.buttonHomeNDStage.setEnabled(True)
        self._set_phase(self._m("nd_home_failed"))
        self._error("title_nd_error", msg)

    # ── PM400 A (reference) ───────────────────────────────────────────────────

    @Slot()
    def _refresh_pm_list(self) -> None:
        if self._pm_shared:
            self._sync_shared_pm_ui()
        else:
            populate_pm400_combo(
                self.ui.comboPM400, self._settings.pm400_visa_resource, config=self.config
            )
        self._update_start_button_state()

    def _sensor_text(self, info: tuple | list | None) -> str:
        """The first three sensor-info fields joined for the status label."""
        return " | ".join(str(x) for x in info[:3]) if info else self._t("text_dash")

    def _sync_shared_pm_ui(self) -> None:
        """Mirror MainWindow's PM400 connection; connecting happens there."""
        self.ui.buttonRefreshPM400.setEnabled(False)
        self.ui.comboPM400.setEnabled(False)
        self.ui.buttonConnectPM400.setEnabled(False)
        if self._pm.is_connected():
            info = self._pm.sensor_info()
            self.ui.valuePM400Status.setText(
                self._t("status_connected_main", sensor=self._sensor_text(info))
            )
            self.ui.buttonZeroPM400.setEnabled(True)
        else:
            self.ui.valuePM400Status.setText(self._t("status_main_not_connected"))
            self.ui.buttonZeroPM400.setEnabled(False)

    @Slot()
    def _toggle_pm400(self) -> None:
        if self._pm.is_connected():
            self._pm.disconnect()
            self.ui.valuePM400Status.setText(self._t("status_not_connected"))
            self.ui.buttonConnectPM400.setText(self._t("button_connect"))
            self.ui.buttonZeroPM400.setEnabled(False)
        else:
            resource = self.ui.comboPM400.currentText().strip()
            if not resource:
                self._warn("title_pm400", "no_visa_resource")
                return
            try:
                self._pm.connect(resource)
                info = self._pm.sensor_info()
                self.ui.valuePM400Status.setText(
                    self._t("status_connected", name=self._sensor_text(info))
                )
                self.ui.buttonConnectPM400.setText(self._t("button_disconnect"))
                self.ui.buttonZeroPM400.setEnabled(True)
            except PM400Error as exc:
                self._error("title_pm400_error", str(exc))
        self._update_start_button_state()

    @Slot()
    def _zero_pm400(self) -> None:
        if not self._pm.is_connected():
            return
        try:
            self._pm.zero()
            self._set_phase(self._m("pm400_zero_started"))
        except PM400Error as exc:
            self._error("title_pm400_error", str(exc))

    # ── PM400 B (detector cross-check) ───────────────────────────────────────

    @Slot()
    def _refresh_pm_b_list(self) -> None:
        current = self.ui.comboPM400B.currentText()
        resources = PM400PowerMeter.list_resources()
        self.ui.comboPM400B.clear()
        for r in resources:
            self.ui.comboPM400B.addItem(r)
        if current and self.ui.comboPM400B.findText(current) < 0:
            self.ui.comboPM400B.addItem(current)
        if current:
            idx = self.ui.comboPM400B.findText(current)
            if idx >= 0:
                self.ui.comboPM400B.setCurrentIndex(idx)
        self._update_start_button_state()

    @Slot()
    def _toggle_pm400_b(self) -> None:
        if self._pm_b.is_connected():
            self._pm_b.disconnect()
            self.ui.valuePM400BStatus.setText(self._t("status_not_connected"))
            self.ui.buttonConnectPM400B.setText(self._t("button_connect"))
            self.ui.buttonZeroPM400B.setEnabled(False)
        else:
            resource = self.ui.comboPM400B.currentText().strip()
            if not resource:
                self._warn("title_pm400b", "no_visa_resource")
                return
            try:
                self._pm_b.connect(resource)
                info = self._pm_b.sensor_info()
                self.ui.valuePM400BStatus.setText(
                    self._t("status_connected", name=self._sensor_text(info))
                )
                self.ui.buttonConnectPM400B.setText(self._t("button_disconnect"))
                self.ui.buttonZeroPM400B.setEnabled(True)
            except PM400Error as exc:
                self._error("title_pm400b_error", str(exc))
        self._update_start_button_state()

    @Slot()
    def _zero_pm400_b(self) -> None:
        if not self._pm_b.is_connected():
            return
        try:
            self._pm_b.zero()
            self._set_phase(self._m("pm400b_zero_started"))
        except PM400Error as exc:
            self._error("title_pm400b_error", str(exc))

    # ── Intensity source ──────────────────────────────────────────────────────

    @Slot()
    def _on_intensity_source_changed(self) -> None:
        """Enable the polariser-alignment or ND-power-grid controls, not both.

        Both group boxes stay visible (disabled, not hidden) per the
        Designer-first UI convention — hiding widgets that carry live state
        (like valueAngleOffset) is more surprising than greying them out.
        """
        nd_mode = self.ui.radioSourceND.isChecked()
        self.ui.groupAlignment.setEnabled(not nd_mode)
        self.ui.groupPowerGrid.setEnabled(nd_mode)
        self._on_power_source_changed()

    @Slot()
    def _on_power_source_changed(self) -> None:
        """Grey out the PM400-dependent grid options in curve mode and refresh Start."""
        from_curve = self.ui.checkPowerFromCurve.isChecked()
        self.ui.spinPowerTolerancePct.setEnabled(not from_curve)
        self.ui.spinMaxRefineSteps.setEnabled(not from_curve)
        self._update_start_button_state()

    @staticmethod
    def _nd_curve_between_ends(nd_range: NDFilterRange) -> tuple[tuple[float, float], ...]:
        """Keep only the scan points between the calibrated clear and dark ends.

        Points beyond the dark end sit in sensor noise and would make the
        power → position inversion ambiguous.
        """
        lo, hi = sorted((nd_range.pos_clear_deg, nd_range.pos_dark_deg))
        return tuple(pt for pt in nd_range.scan_points if lo <= pt[0] <= hi)

    def _get_nd_scan_points(self) -> tuple[tuple[float, float], ...]:
        """Return the best available ND position/power scan curve.

        Prefers a full-resolution scan taken this session; falls back to the
        2-point (clear, dark) summary persisted in settings from a previous
        session's range scan.
        """
        if self._nd_range is not None:
            return self._nd_range.scan_points
        s = self._settings
        if (
            s.nd_pos_clear_deg is not None
            and s.nd_pos_dark_deg is not None
            and s.nd_power_clear_W is not None
            and s.nd_power_dark_W is not None
        ):
            return (
                (s.nd_pos_clear_deg, s.nd_power_clear_W),
                (s.nd_pos_dark_deg, s.nd_power_dark_W),
            )
        return ()

    # ── Polariser alignment ───────────────────────────────────────────────────

    @Slot()
    def _start_align(self) -> None:
        """Scan the PM400 while rotating the stage to find the max-transmission angle."""
        if not self._kdc.is_connected() or not self._pm.is_connected():
            self._warn("title_align", "align_needs_devices")
            return

        self._align_worker = AlignPolariserWorker(
            kdc=self._kdc,
            pm=self._pm,
            start_deg=self.ui.spinAlignStart.value(),
            end_deg=self.ui.spinAlignEnd.value(),
            n_points=self.ui.spinAlignNPoints.value(),
            settle_s=self.ui.spinAlignSettle.value(),
            parent=self,
        )
        self._align_worker.progress.connect(self._on_align_progress)
        self._align_worker.finished.connect(self._on_align_finished)
        self._align_worker.failed.connect(self._on_align_failed)
        self._align_worker.log.connect(self._append_log)

        total = self.ui.spinAlignNPoints.value()
        self.ui.progressBar.setMaximum(total)
        self.ui.progressBar.setValue(0)

        self.ui.buttonAlignPolariser.setEnabled(False)
        self.ui.buttonAbortAlign.setEnabled(True)
        self.ui.buttonStart.setEnabled(False)
        self._set_phase(self._m("align_running"))
        self._align_worker.start()

    @Slot()
    def _abort_align(self) -> None:
        if self._align_worker is not None and self._align_worker.isRunning():
            self._align_worker.abort()
            self.ui.buttonAbortAlign.setEnabled(False)
            self._set_phase(self._m("align_aborting"))

    @Slot(int, int)
    def _on_align_progress(self, done: int, total: int) -> None:
        self.ui.progressBar.setValue(done)

    @Slot(float)
    def _on_align_finished(self, angle_max_deg: float) -> None:
        self._angle_offset_deg = angle_max_deg
        self.ui.valueAngleOffset.setText(
            self._t(
                "angle_offset_aligned",
                zero=fmt_angle(angle_max_deg),
                quarter=fmt_angle(angle_max_deg + 90.0),
            )
        )
        self._set_phase(self._m("align_done"))
        self.ui.buttonAbortAlign.setEnabled(False)
        self._update_start_button_state()

    @Slot(str)
    def _on_align_failed(self, message: str) -> None:
        self._set_phase(self._m("align_failed"))
        self.ui.buttonAbortAlign.setEnabled(False)
        self._update_start_button_state()
        if not self._is_abort_message(message):
            self._error("title_align_error", message)

    # ── Sweep control ─────────────────────────────────────────────────────────

    @Slot()
    def _start_sweep(self) -> None:
        gains = tuple(
            stage
            for stage, chk in (
                (1, self.ui.checkGain1),
                (2, self.ui.checkGain2),
                (3, self.ui.checkGain3),
                (4, self.ui.checkGain4),
            )
            if chk.isChecked()
        )
        if not gains:
            self._warn("title_start", "no_gain_selected")
            return

        profile_name = self.ui.editProfileName.text().strip()
        if not profile_name:
            self._warn("title_start", "no_profile_name")
            return

        nd_mode = self.ui.radioSourceND.isChecked()
        from_curve = nd_mode and self.ui.checkPowerFromCurve.isChecked()
        nd_scan_points = self._get_nd_scan_points() if nd_mode else ()
        if from_curve:
            if self._nd_range is None:
                self._warn("title_start", "curve_needs_session_scan")
                return
            nd_scan_points = self._nd_curve_between_ends(self._nd_range)
        if nd_mode and not nd_scan_points:
            self._warn("title_start", "no_nd_range")
            return

        params = AutoCalibrationParams(
            selected_gains=gains,
            angle_start_deg=self.ui.spinAngleStart.value(),
            angle_end_deg=self.ui.spinAngleEnd.value(),
            n_points=self.ui.spinNPoints.value(),
            grid_mode=("linear_cos2" if self.ui.radioLinearCos2.isChecked() else "linear_angle"),
            point_settle_s=self.ui.spinPointSettle.value(),
            gain_settle_s=self.ui.spinGainSettle.value(),
            detector_samples=self.ui.spinDetectorSamples.value(),
            pm_averaging=self.ui.spinPmAveraging.value(),
            profile_name=profile_name,
            wavelength_nm=self.ui.spinWavelength.value(),
            beamsplitter_attenuation_dB=self.ui.spinAttenuation.value(),
            angle_offset_deg=self._angle_offset_deg,
            adc_saturation_threshold_V=self.ui.spinSaturationThreshold.value(),
            intensity_source=("nd_filter" if nd_mode else "polariser"),
            power_grid_mode=(
                "log_power" if self.ui.radioGridLogPower.isChecked() else "linear_power"
            ),
            nd_scan_points=nd_scan_points,
            power_tolerance_pct=self.ui.spinPowerTolerancePct.value(),
            max_refine_steps=self.ui.spinMaxRefineSteps.value(),
            return_pass=self.ui.checkReturnPass.isChecked(),
            power_from_nd_curve=from_curve,
        )

        if self._data_controller is not None:
            self._data_controller.stop_continuous_reading()

        device_manager = (
            self._device_manager if self._standalone else self._data_controller.device_manager
        )
        actuator = (
            NDFilterActuator(self._nd, nd_range=self._nd_range)
            if nd_mode
            else PolariserActuator(self._kdc, angle_offset_deg=self._angle_offset_deg)
        )
        # A fresh sweep invalidates any gain-verification result computed
        # against the previous profile.
        self._verify_result = None
        self._worker = AutoPowerCalibrationWorker(
            device_manager=device_manager,
            actuator=actuator,
            pm=self._pm,
            params=params,
            parent=self,
        )
        self._worker.gain_started.connect(self._on_gain_started)
        self._worker.point_recorded.connect(self._on_point_recorded)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_sweep_finished)
        self._worker.failed.connect(self._on_sweep_failed)
        self._worker.log.connect(self._append_log)

        total = params.n_points * len(params.selected_gains) * (2 if params.return_pass else 1)
        self.ui.progressBar.setMaximum(total)
        self.ui.progressBar.setValue(0)
        self.ui.calibrationPlot.clear()
        self._set_running(True)
        self._worker.start()

    @Slot()
    def _abort_sweep(self) -> None:
        if self._worker is not None:
            self._worker.abort()
            self._set_phase(self._m("aborting"))
            self.ui.buttonAbort.setEnabled(False)

    # ── Sweep worker signal handlers ─────────────────────────────────────────

    @Slot(int)
    def _on_gain_started(self, gain: int) -> None:
        self._set_phase(self._m("gain_started", gain=gain))

    @Slot(int, float, float, float, float)
    def _on_point_recorded(
        self,
        gain: int,
        level: float,
        voltage: float,
        pm_power: float,
    ) -> None:
        self.ui.calibrationPlot.add_point(gain, voltage, pm_power)

    @Slot(int, int)
    def _on_progress(self, done: int, total: int) -> None:
        self.ui.progressBar.setValue(done)

    @Slot(object)
    def _on_sweep_finished(self, profile: PowerCalibrationProfile) -> None:
        self._profile = profile
        self._set_running(False)
        self._set_phase(self._m("calibration_done"))
        self.ui.buttonSave.setEnabled(True)
        if self._data_controller is not None:
            self._data_controller.start_continuous_reading()
        self._append_log(self._m("calibration_done_log"))

    @Slot(str)
    def _on_sweep_failed(self, message: str) -> None:
        self._set_running(False)
        self._set_phase(self._m("error_prefix", message=message))
        if self._data_controller is not None:
            self._data_controller.start_continuous_reading()
        self._error("title_sweep_failed", message)

    # ── ND range scan ─────────────────────────────────────────────────────────

    @Slot()
    def _start_nd_scan(self) -> None:
        if not self._nd.is_connected() or not self._pm.is_connected():
            self._warn("title_nd_scan", "nd_devices_required")
            return

        if not self._apply_pm_settings("title_nd_scan"):
            return

        dark_floor_uw = self.ui.spinNDDarkFloorUW.value()
        dark_floor_W = dark_floor_uw * 1e-6 if dark_floor_uw > 0 else None

        self.ui.ndRangePlot.clear()
        self._nd_scan_worker = NDRangeScanWorker(
            nd=self._nd,
            pm=self._pm,
            start_deg=self.ui.spinNDScanStart.value(),
            end_deg=self.ui.spinNDScanEnd.value(),
            n_points=self.ui.spinNDScanPoints.value(),
            settle_s=self.ui.spinNDScanSettle.value(),
            dark_floor_W=dark_floor_W,
            samples_per_point=self.ui.spinNDScanSamples.value(),
            parent=self,
        )
        self._nd_scan_worker.point_scanned.connect(self._on_nd_point_scanned)
        self._nd_scan_worker.progress.connect(self._on_progress)
        self._nd_scan_worker.finished.connect(self._on_nd_scan_finished)
        self._nd_scan_worker.failed.connect(self._on_nd_scan_failed)
        self._nd_scan_worker.log.connect(self._append_log)

        self.ui.progressBar.setMaximum(self.ui.spinNDScanPoints.value())
        self.ui.progressBar.setValue(0)
        self._set_nd_scan_running(True)
        self._nd_scan_worker.start()

    @Slot()
    def _abort_nd_scan(self) -> None:
        if self._nd_scan_worker is not None:
            self._nd_scan_worker.abort()
            self._set_phase(self._m("aborting"))
            self.ui.buttonAbortNDScan.setEnabled(False)

    @Slot(float, float)
    def _on_nd_point_scanned(self, position_deg: float, power_W: float) -> None:
        self.ui.ndRangePlot.add_point(position_deg, power_W)

    @Slot(object)
    def _on_nd_scan_finished(self, result: NDFilterRange) -> None:
        self._nd_range = result
        self._set_nd_scan_running(False)
        self.ui.ndRangePlot.set_range_markers(result.pos_clear_deg, result.pos_dark_deg)
        warning = "" if result.monotonic else self._t("nd_range_not_monotonic")
        self.ui.valueNDRange.setText(
            self._t(
                "nd_range_result",
                clear=f"{result.pos_clear_deg:.2f}",
                dark=f"{result.pos_dark_deg:.2f}",
                power_clear=f"{result.power_clear_W:.3e}",
                power_dark=f"{result.power_dark_W:.3e}",
                dynamic_range=f"{result.dynamic_range_dB:.1f}",
                warning=warning,
            )
        )
        self._set_phase(self._m("nd_scan_done"))
        # The linearity scans only matter inside the usable range.
        self.ui.spinNDLinStart.setValue(result.pos_clear_deg)
        self.ui.spinNDLinEnd.setValue(result.pos_dark_deg)
        self._refresh_nd_lin_status()
        self._persist_settings()

    @Slot(str)
    def _on_nd_scan_failed(self, message: str) -> None:
        self._set_nd_scan_running(False)
        self._set_phase(self._m("error_prefix", message=message))
        if not self._is_abort_message(message):
            self._error("title_nd_scan_failed", message)

    def _set_nd_scan_running(self, running: bool) -> None:
        self._nd_range_active = running
        self.ui.groupNDScanParams.setEnabled(not running)
        self.ui.buttonAbortNDScan.setEnabled(running)
        self._refresh_nd_scan_buttons()

    def _apply_pm_settings(self, title_key: str) -> bool:
        """Push the dialog's wavelength and attenuation to the PM400 before an ND scan.

        The calibration sweep sets these on the meter at its start. Scanning with
        whatever the device had stored would build a position/power curve in
        different units than the sweep later targets.
        """
        try:
            self._pm.set_wavelength_nm(self.ui.spinWavelength.value())
            self._pm.set_attenuation_dB(self.ui.spinAttenuation.value())
        except PM400Error as exc:
            self._error(title_key, self._m("pm_config_failed", error=exc))
            return False
        return True

    def _nd_scan_ready(self) -> bool:
        """Whether a new ND scan (range or linearity) may start now."""
        return (
            self._nd.is_connected()
            and self._pm.is_connected()
            and not self._nd_range_active
            and not self._nd_lin_active
        )

    def _refresh_nd_scan_buttons(self) -> None:
        ready = self._nd_scan_ready()
        self.ui.buttonScanNDRange.setEnabled(ready)
        self.ui.buttonScanNDLin.setEnabled(ready)
        self.ui.buttonClearNDLin.setEnabled(bool(self._nd_lin_scans) and not self._nd_lin_active)

    # ── ND linearity scans ────────────────────────────────────────────────────

    @Slot()
    def _start_nd_lin(self) -> None:
        if not self._nd_scan_ready():
            self._warn("title_nd_lin", "nd_devices_required")
            return
        if not self._apply_pm_settings("title_nd_lin"):
            return
        self._nd_lin_worker = NDLinearityScanWorker(
            nd=self._nd,
            pm=self._pm,
            start_deg=self.ui.spinNDLinStart.value(),
            end_deg=self.ui.spinNDLinEnd.value(),
            n_points=self.ui.spinNDLinPoints.value(),
            settle_s=self.ui.spinNDLinSettle.value(),
            n_scans=self.ui.spinNDLinScans.value(),
            alternate=self.ui.checkNDLinAlternate.isChecked(),
            samples_per_point=self.ui.spinNDLinSamples.value(),
            first_index=len(self._nd_lin_scans),
            parent=self,
        )
        worker = self._nd_lin_worker
        worker.scan_started.connect(self.ui.ndLinearityPlot.begin_scan)
        worker.point_scanned.connect(self.ui.ndLinearityPlot.add_point)
        worker.scan_finished.connect(self._on_nd_lin_scan_finished)
        worker.progress.connect(self._on_progress)
        worker.finished.connect(self._on_nd_lin_finished)
        worker.failed.connect(self._on_nd_lin_failed)
        worker.log.connect(self._append_log)

        self.ui.progressBar.setMaximum(
            self.ui.spinNDLinScans.value() * self.ui.spinNDLinPoints.value()
        )
        self.ui.progressBar.setValue(0)
        self._set_nd_lin_running(True)
        worker.start()

    @Slot()
    def _abort_nd_lin(self) -> None:
        if self._nd_lin_worker is not None:
            self._nd_lin_worker.abort()
            self._set_phase(self._m("aborting"))
            self.ui.buttonAbortNDLin.setEnabled(False)

    @Slot()
    def _clear_nd_lin(self) -> None:
        self._nd_lin_scans.clear()
        self.ui.ndLinearityPlot.clear()
        self._refresh_nd_lin_report()
        self._refresh_nd_scan_buttons()

    @Slot(object)
    def _on_nd_lin_scan_finished(self, scan: NDLinearityScan) -> None:
        self._nd_lin_scans.append(scan)
        self._refresh_nd_lin_report()

    @Slot(object)
    def _on_nd_lin_finished(self, scans: list[NDLinearityScan]) -> None:
        self._set_nd_lin_running(False)
        self._set_phase(self._m("nd_lin_done", count=len(scans)))

    @Slot(str)
    def _on_nd_lin_failed(self, message: str) -> None:
        self._set_nd_lin_running(False)
        self._set_phase(self._m("error_prefix", message=message))
        if not self._is_abort_message(message):
            self._error("title_nd_lin_failed", message)

    def _set_nd_lin_running(self, running: bool) -> None:
        self._nd_lin_active = running
        self.ui.groupNDLinParams.setEnabled(not running)
        self.ui.buttonAbortNDLin.setEnabled(running)
        self._refresh_nd_scan_buttons()

    def _nd_curve_source_text(self) -> str:
        """Describe which ND position/power curve the calibration sweeps invert."""
        if self._nd_range is not None:
            n = len(self._nd_range.scan_points)
            return self._t("nd_curve_session", points=n)
        if len(self._get_nd_scan_points()) == 2:
            return self._t("nd_curve_two_point")
        return self._t("nd_curve_none")

    def _refresh_nd_lin_status(self) -> None:
        """Say that the linearity result is diagnostic only, and what sweeps use instead."""
        n = len(self._nd_lin_scans)
        head = self._t("nd_lin_status_scans", count=n) if n else self._t("nd_lin_status_empty")
        self.ui.valueNDLinStatus.setText(
            self._t("nd_lin_status", head=head, curve=self._nd_curve_source_text())
        )

    @Slot()
    def _refresh_nd_lin_report(self) -> None:
        """Re-analyse all collected scans and redraw residuals + report."""
        tol = self.ui.spinNDLinTol.value()
        self.ui.ndLinearityPlot.set_tolerance(tol)
        self._refresh_nd_lin_status()
        if not self._nd_lin_scans:
            self.ui.editNDLinReport.clear()
            return
        floor_W = self.ui.spinNDLinFloorUW.value() * 1e-6
        try:
            report = analyse_linearity_set(self._nd_lin_scans, noise_floor_W=floor_W)
        except ValueError as exc:
            self.ui.editNDLinReport.setPlainText(self._t("analysis_failed", error=exc))
            return
        for fit in report.fits:
            self.ui.ndLinearityPlot.set_residuals(
                fit.index, fit.direction, fit.positions_deg, fit.residuals_od
            )
        self.ui.editNDLinReport.setPlainText(
            format_nd_linearity_report(report, tol, config=self.config)
        )

    # ── Detector cross-check ──────────────────────────────────────────────────

    @Slot()
    def _start_xcheck(self) -> None:
        if (
            not self._nd.is_connected()
            or not self._pm.is_connected()
            or not self._pm_b.is_connected()
        ):
            self._warn("title_xcheck", "xcheck_needs_devices")
            return
        scan = self._get_nd_scan_points()
        if not scan:
            self._warn("title_xcheck", "no_nd_range")
            return
        pos_clear = min(scan, key=lambda pt: abs(pt[1] - max(p for _, p in scan)))[0]
        pos_dark = min(scan, key=lambda pt: abs(pt[1] - min(p for _, p in scan)))[0]

        self.ui.xCheckPlot.clear()
        self._xcheck_worker = DetectorCrossCheckWorker(
            nd=self._nd,
            pm_a=self._pm,
            pm_b=self._pm_b,
            pos_clear_deg=pos_clear,
            pos_dark_deg=pos_dark,
            n_points=self.ui.spinXCheckPoints.value(),
            settle_s=self.ui.spinXCheckSettle.value(),
            tolerance_pct=self.ui.spinXCheckTolerance.value(),
            parent=self,
        )
        self._xcheck_worker.point_recorded.connect(self._on_xcheck_point_recorded)
        self._xcheck_worker.progress.connect(self._on_progress)
        self._xcheck_worker.finished.connect(self._on_xcheck_finished)
        self._xcheck_worker.failed.connect(self._on_xcheck_failed)
        self._xcheck_worker.log.connect(self._append_log)

        self.ui.progressBar.setMaximum(self.ui.spinXCheckPoints.value())
        self.ui.progressBar.setValue(0)
        self._set_xcheck_running(True)
        self._xcheck_worker.start()

    @Slot()
    def _abort_xcheck(self) -> None:
        if self._xcheck_worker is not None:
            self._xcheck_worker.abort()
            self._set_phase(self._m("aborting"))
            self.ui.buttonAbortXCheck.setEnabled(False)

    @Slot(float, float, float)
    def _on_xcheck_point_recorded(self, position: float, power_a: float, power_b: float) -> None:
        self.ui.xCheckPlot.add_point(power_a, power_b)

    @Slot(object)
    def _on_xcheck_finished(self, result: DetectorComparisonResult) -> None:
        self._xcheck_result = result
        self._set_xcheck_running(False)
        self.ui.buttonSaveXCheck.setEnabled(True)
        verdict = self._m("verdict_ok" if result.passed else "verdict_failed")
        self.ui.valueXCheckResult.setText(
            self._t(
                "xcheck_result",
                mean_ratio=f"{result.mean_ratio:.4f}",
                spread=f"{result.ratio_spread_pct:.2f}",
                worst=f"{result.worst_deviation_pct:.2f}",
                verdict=verdict,
            )
        )
        self._set_phase(self._m("xcheck_done"))

    @Slot(str)
    def _on_xcheck_failed(self, message: str) -> None:
        self._set_xcheck_running(False)
        self._set_phase(self._m("error_prefix", message=message))
        if not self._is_abort_message(message):
            self._error("title_xcheck_failed", message)

    @Slot()
    def _save_xcheck(self) -> None:
        if self._xcheck_result is None:
            return
        default_name = f"detector_crosscheck_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        path, _ = QFileDialog.getSaveFileName(
            self, self._t("save_xcheck_caption"), default_name, self._t("file_filter_json")
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(self._xcheck_result.to_json_dict(), fh, indent=2)
        except Exception as exc:
            self._error("title_save_failed", str(exc))
            return
        QMessageBox.information(self, self._t("title_saved"), self._m("saved_at", path=path))

    def _set_xcheck_running(self, running: bool) -> None:
        self.ui.groupXCheckParams.setEnabled(not running)
        self.ui.buttonStartXCheck.setEnabled(not running and self._xcheck_ready())
        self.ui.buttonAbortXCheck.setEnabled(running)

    def _xcheck_ready(self) -> bool:
        return self._nd.is_connected() and self._pm.is_connected() and self._pm_b.is_connected()

    # ── Gain-switch verification ──────────────────────────────────────────────

    def _compute_verify_levels(self, n_levels: int) -> list[float]:
        """Pick ND-stage positions inside adjacent-gain-window overlaps.

        Uses ``pdtia.gain_auto_switch_power_W`` from config.json (the same
        windows the live app uses for gain auto-switching) intersected with
        the gain stages actually present in ``self._profile``. There are at
        most ``len(calibrated_gains) - 1`` overlap windows (3, for 4 gain
        stages) regardless of *n_levels*, so *n_levels* controls how many
        target powers are spread across them, not how many overlaps exist:
        one log-spaced point per overlap when *n_levels* is small, several
        per overlap (log-spaced within it) when it's larger. Each target is
        inverted to a position via the calibrated ND scan.
        """
        if self._profile is None:
            return []
        limits = load_gain_power_limits(self.config.data)
        calibrated_gains = sorted(
            g for g, cal in self._profile.gains.items() if cal.points and g in limits
        )
        overlaps: list[tuple[float, float]] = []
        for g_hi, g_lo in zip(calibrated_gains, calibrated_gains[1:], strict=False):
            lo_min, lo_max = limits[g_lo]
            hi_min, hi_max = limits[g_hi]
            overlap_lo = max(lo_min, hi_min)
            overlap_hi = min(lo_max, hi_max)
            if overlap_lo > 0 and overlap_hi > overlap_lo:
                overlaps.append((overlap_lo, overlap_hi))
        if not overlaps:
            return []
        scan = self._get_nd_scan_points()
        if not scan:
            return []
        from polarisation_ui.core.auto_calibration_settings import (
            build_power_grid,
            positions_for_target_powers,
        )

        n_levels = max(1, n_levels)
        n_overlaps = len(overlaps)

        if n_levels <= n_overlaps:
            # Evenly-spaced subset of overlaps, one point (geometric mean) each.
            step = n_overlaps / n_levels
            chosen = (
                overlaps
                if n_levels == n_overlaps
                else [overlaps[int(i * step)] for i in range(n_levels)]
            )
            targets = [(lo * hi) ** 0.5 for lo, hi in chosen]
        else:
            # Distribute the extra points round-robin across overlaps, then
            # log-space that many points within each overlap that got > 1.
            counts = [1] * n_overlaps
            i = 0
            while sum(counts) < n_levels:
                counts[i % n_overlaps] += 1
                i += 1
            targets = []
            for (lo, hi), k in zip(overlaps, counts, strict=True):
                if k == 1:
                    targets.append((lo * hi) ** 0.5)
                else:
                    targets.extend(build_power_grid(hi, lo, k, mode="log_power"))

        return positions_for_target_powers(targets, scan)

    @Slot()
    def _start_verify(self) -> None:
        if self._profile is None:
            self._warn("title_verify", "verify_needs_profile")
            return
        from_curve = self.ui.checkVerifyFromCurve.isChecked()
        if not self._nd.is_connected() or not (from_curve or self._pm.is_connected()):
            self._warn("title_verify", "verify_devices_required")
            return
        if from_curve and self._nd_range is None:
            self._warn("title_verify", "verify_curve_needs_session_scan")
            return

        gains = tuple(sorted(g for g, cal in self._profile.gains.items() if cal.points))
        if len(gains) < 2:
            self._warn("title_verify", "verify_needs_two_gains")
            return

        levels = self._compute_verify_levels(self.ui.spinVerifyLevels.value())
        if not levels:
            self._warn("title_verify", "verify_no_levels")
            return

        device_manager = (
            self._device_manager if self._standalone else self._data_controller.device_manager
        )
        self.ui.tableGainVerify.setRowCount(0)
        self._verify_from_curve = from_curve
        self._verify_worker = GainCrossCheckWorker(
            device_manager=device_manager,
            actuator=NDFilterActuator(self._nd, nd_range=self._nd_range),
            pm=self._pm,
            profile=self._profile,
            levels=levels,
            gains=gains,
            settle_s=self.ui.spinVerifySettle.value(),
            detector_samples=self.ui.spinDetectorSamples.value(),
            tolerance_pct=self.ui.spinVerifyTolerancePct.value(),
            nd_curve=self._nd_curve_between_ends(self._nd_range) if from_curve else None,
            parent=self,
        )
        self._verify_worker.level_done.connect(self._on_verify_level_done)
        self._verify_worker.progress.connect(self._on_progress)
        self._verify_worker.finished.connect(self._on_verify_finished)
        self._verify_worker.failed.connect(self._on_verify_failed)
        self._verify_worker.log.connect(self._append_log)

        self.ui.progressBar.setMaximum(len(levels))
        self.ui.progressBar.setValue(0)
        self._set_verify_running(True)
        self._verify_worker.start()

    @Slot()
    def _abort_verify(self) -> None:
        if self._verify_worker is not None:
            self._verify_worker.abort()
            self._set_phase(self._m("aborting"))
            self.ui.buttonAbortVerify.setEnabled(False)

    @Slot(object)
    def _on_verify_level_done(self, level: GainCrossCheckLevel) -> None:
        row = self.ui.tableGainVerify.rowCount()
        self.ui.tableGainVerify.insertRow(row)
        self.ui.tableGainVerify.setItem(row, 0, QTableWidgetItem(f"{level.level:.2f}"))
        self.ui.tableGainVerify.setItem(row, 1, QTableWidgetItem(f"{level.pm_power_W:.3e}"))
        for gain, (_, power_w) in level.per_gain.items():
            col = _GAIN_COLUMNS.get(gain)
            if col is not None:
                self.ui.tableGainVerify.setItem(row, col, QTableWidgetItem(f"{power_w:.3e}"))

    @Slot(object)
    def _on_verify_finished(self, result: GainCrossCheckResult) -> None:
        self._verify_result = result
        self._set_verify_running(False)
        verdict = self._m("verdict_ok" if result.passed else "verdict_failed")
        reference = (
            "verify_reference_curve" if self._verify_from_curve else "verify_reference_pm400"
        )
        self.ui.valueVerifyResult.setText(
            self._t(
                "verify_result",
                spread=f"{result.worst_spread_pct:.2f}",
                pm_deviation=f"{result.worst_pm_deviation_pct:.2f}",
                reference=self._t(reference),
                verdict=verdict,
            )
        )
        self._set_phase(self._m("verify_done"))
        if self._profile is not None:
            self._profile.gain_crosscheck = result.to_json_dict()

    @Slot(str)
    def _on_verify_failed(self, message: str) -> None:
        self._set_verify_running(False)
        self._set_phase(self._m("error_prefix", message=message))
        if not self._is_abort_message(message):
            self._error("title_verify_failed", message)

    def _set_verify_running(self, running: bool) -> None:
        self.ui.groupVerifyParams.setEnabled(not running)
        self.ui.buttonStartVerify.setEnabled(not running and self._verify_ready())
        self.ui.buttonAbortVerify.setEnabled(running)

    def _verify_ready(self) -> bool:
        pm_ok = self._pm.is_connected() or self.ui.checkVerifyFromCurve.isChecked()
        return self._profile is not None and self._nd.is_connected() and pm_ok

    @Slot()
    def _on_verify_source_changed(self) -> None:
        self.ui.buttonStartVerify.setEnabled(
            not self._verify_worker_active() and self._verify_ready()
        )

    def _verify_worker_active(self) -> bool:
        return self._verify_worker is not None and self._verify_worker.isRunning()

    # ── Save ──────────────────────────────────────────────────────────────────

    @Slot()
    def _save_profile(self) -> None:
        if self._profile is None:
            return
        path = _Profile.default_path(self._profile.name)
        try:
            self._profile.save(path)
        except Exception as exc:
            self._error("title_save_failed", str(exc))
            return
        QMessageBox.information(
            self, self._t("title_profile_saved"), self._m("saved_at", path=path)
        )
        self.profile_saved.emit()

    # ── Helpers ───────────────────────────────────────────────────────────────

    @Slot(str)
    def _append_log(self, msg: str) -> None:
        self.ui.editLog.appendPlainText(msg)

    @Slot(str)
    def _update_output_path(self, name: str) -> None:
        if name.strip():
            path = _Profile.default_path(name.strip())
            self.ui.valueOutputPath.setText(str(path))
        else:
            self.ui.valueOutputPath.setText(self._t("text_dash"))
        self._update_start_button_state()

    def _update_start_button_state(self) -> None:
        arduino_ok = (
            (self._device_manager is not None and self._device_manager.is_encoder_connected())
            if self._standalone
            else True
        )
        nd_mode = self.ui.radioSourceND.isChecked()
        actuator_ok = self._nd.is_connected() if nd_mode else self._kdc.is_connected()
        pm_ok = self._pm.is_connected() or (nd_mode and self.ui.checkPowerFromCurve.isChecked())
        hw_ready = actuator_ok and pm_ok and arduino_ok
        self.ui.buttonAlignPolariser.setEnabled(
            self._kdc.is_connected() and self._pm.is_connected()
        )
        self.ui.buttonStart.setEnabled(hw_ready and bool(self.ui.editProfileName.text().strip()))
        self._refresh_nd_scan_buttons()
        self.ui.buttonStartXCheck.setEnabled(self._xcheck_ready())
        self.ui.buttonStartVerify.setEnabled(self._verify_ready())

    def _set_running(self, running: bool) -> None:
        for w in (
            self.ui.groupConnections,
            self.ui.groupBeam,
            self.ui.groupAlignment,
            self.ui.groupSweep,
            self.ui.groupPowerGrid,
            self.ui.groupProfile,
            self.ui.groupIntensitySource,
            self.ui.buttonStart,
        ):
            w.setEnabled(not running)
        self.ui.buttonAbort.setEnabled(running)
        if not running:
            # Restores the correct groupAlignment/groupPowerGrid enabled split.
            self._on_intensity_source_changed()
            self._update_start_button_state()

    def _persist_settings(self) -> None:
        kdc_conn_id = self.ui.comboKDC.currentData() or self.ui.comboKDC.currentText()
        nd_conn_id = self.ui.comboNDStage.currentData() or self.ui.comboNDStage.currentText()
        self._settings = AutoCalibrationConnectionSettings(
            kdc101_conn_id=kdc_conn_id or "",
            pm400_visa_resource=self.ui.comboPM400.currentText().strip(),
            beamsplitter_attenuation_dB=self.ui.spinAttenuation.value(),
            wavelength_nm=self.ui.spinWavelength.value(),
            angle_offset_deg=self._angle_offset_deg,
            nd_stage_conn_id=nd_conn_id or "",
            pm400_b_visa_resource=self.ui.comboPM400B.currentText().strip(),
            nd_pos_clear_deg=(self._nd_range.pos_clear_deg if self._nd_range else None),
            nd_pos_dark_deg=(self._nd_range.pos_dark_deg if self._nd_range else None),
            nd_power_clear_W=(self._nd_range.power_clear_W if self._nd_range else None),
            nd_power_dark_W=(self._nd_range.power_dark_W if self._nd_range else None),
            nd_calibrated_at=(datetime.now().isoformat() if self._nd_range else ""),
        )
        try:
            self._settings.save()
        except Exception as exc:
            Debug.warning(f"AutoPowerCalibrationWindow: could not save settings: {exc}")

    # ── Qt lifecycle ──────────────────────────────────────────────────────────

    def closeEvent(self, event) -> None:
        """Abort any running workers and wait for them before allowing the window to close."""
        if self._align_worker is not None and self._align_worker.isRunning():
            self._align_worker.abort()
            self._align_worker.wait(5000)
        if self._worker is not None and self._worker.isRunning():
            self._worker.abort()
            self._worker.wait(5000)
            if self._data_controller is not None:
                self._data_controller.start_continuous_reading()
        if self._nd_scan_worker is not None and self._nd_scan_worker.isRunning():
            self._nd_scan_worker.abort()
            self._nd_scan_worker.wait(5000)
        if self._nd_lin_worker is not None and self._nd_lin_worker.isRunning():
            self._nd_lin_worker.abort()
            self._nd_lin_worker.wait(5000)
        if self._xcheck_worker is not None and self._xcheck_worker.isRunning():
            self._xcheck_worker.abort()
            self._xcheck_worker.wait(5000)
        if self._verify_worker is not None and self._verify_worker.isRunning():
            self._verify_worker.abort()
            self._verify_worker.wait(5000)
        if self._home_thread is not None and self._home_thread.isRunning():
            self._home_thread.wait(3000)
        if self._nd_home_thread is not None and self._nd_home_thread.isRunning():
            self._nd_home_thread.wait(3000)
        self._kdc.disconnect()
        if not self._pm_shared:
            self._pm.disconnect()
        self._nd.disconnect()
        self._pm_b.disconnect()
        if self._standalone and self._device_manager is not None:
            self._device_manager.disconnect_all()
        self._persist_settings()
        super().closeEvent(event)


def format_nd_linearity_report(
    report: NDLinearityReport, tolerance_od: float, config: AppConfig | None = None
) -> str:
    """Render a fixed-width comparison of all scans in *report*.

    A scan passes when its largest deviation from the straight-line OD fit is
    within *tolerance_od*. The labels come from ``ui.auto_power_calibration.report_*``
    (``config`` defaults to ``default_config()``).
    """
    cfg = config if config is not None else default_config()

    def t(key: str, **fmt: object) -> str:
        return cfg.text(f"{_SECTION}.{key}", **fmt)

    forward = t("report_forward")
    backward = t("report_backward")
    width = max(len(forward), len(backward))
    lines = [
        t(
            "report_header",
            power=f"{report.reference_power_W:.3e}",
            tolerance=f"{tolerance_od:.3f}",
        ),
        t("report_columns"),
    ]
    for fit in report.fits:
        direction = (backward if fit.direction == BACKWARD else forward).ljust(width)
        status = (
            t("report_ok") if fit.max_residual_od <= tolerance_od else t("report_over_tolerance")
        )
        lines.append(
            f"{fit.index + 1:>4}  {direction}  {fit.n_used:>3}  "
            f"{fit.slope_od_per_deg:>14.5f}  {fit.rms_residual_od:>7.4f}  "
            f"{fit.max_residual_od:>7.4f}  {fit.max_residual_pct:>6.1f}  "
            f"{fit.max_residual_pos_deg:>6.1f}  {status}"
        )
    mean_slope = report.slope_mean_od_per_deg
    if len(report.fits) > 1:
        rel = abs(report.slope_std_od_per_deg / mean_slope) * 100.0 if mean_slope else 0.0
        lines.append(
            t(
                "report_slope",
                mean=f"{mean_slope:.5f}",
                std=f"{report.slope_std_od_per_deg:.5f}",
                rel=f"{rel:.2f}",
            )
        )
    if report.od_scatter_mean is not None and report.od_scatter_max is not None:
        lines.append(
            t(
                "report_scatter",
                mean=f"{report.od_scatter_mean:.4f}",
                max=f"{report.od_scatter_max:.4f}",
            )
        )
    if report.hysteresis_od is not None:
        deg = (
            t("report_hysteresis_deg", deg=f"{report.hysteresis_deg:.2f}")
            if report.hysteresis_deg is not None
            else ""
        )
        lines.append(t("report_hysteresis", od=f"{report.hysteresis_od:.4f}", deg=deg))
    elif len(report.fits) > 1:
        lines.append(t("report_hysteresis_unknown"))
    return "\n".join(lines)
