"""Automatic power calibration dialog.

Drives an intensity actuator (rotating polariser or stepper-driven ND-filter wheel)
and a Thorlabs PM400 power meter to record (voltage, power) pairs for all
four PDTIA gain stages, then writes a PowerCalibrationProfile in the same
format used by the manual calibration window.

Also hosts four related workflows, each on its own tab: calibrating the
ND filter's usable travel from a power-meter scan (ND-Bereich), measuring how
linear its optical density is over several repeated scans (ND-Linearität), cross-
checking a second PM400 against the first across that range before trusting
it as the calibration reference (Detektor-Vergleich), and verifying that all
PD-TIA gain stages agree after calibration (Gain-Prüfung).

Standalone mode (data_controller=None): the dialog manages its own Arduino
connection and shows the gbArduino section.  The Arduino is needed for ADC
reads and PDTIA gain switching during the sweep.
"""

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
from polarisation_ui.infrastructure.config import import_config
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

_GAIN_COLUMNS = {1: 2, 2: 3, 3: 4, 4: 5}  # gain stage -> tableGainVerify column index


class AutoPowerCalibrationWindow(QDialog):
    """Non-modal dialog for automated detector power calibration.

    When *data_controller* is provided the dialog is opened from MainWindow
    and the existing DataController supplies the Arduino device manager.
    When *data_controller* is None the dialog runs standalone: it shows the
    gbArduino section so the user can connect to the Arduino directly.
    """

    profile_saved = Signal()

    def __init__(
        self,
        data_controller=None,
        pm400: PM400PowerMeter | None = None,
        parent=None,
    ) -> None:
        """Build the dialog UI; standalone mode is enabled when data_controller is None."""
        super().__init__(parent)
        self.ui = Ui_AutoPowerCalibrationDialog()
        self.ui.setupUi(self)

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

        self._profile: PowerCalibrationProfile | None = None
        self._angle_offset_deg: float = 0.0
        # Fresh-this-session ND range scan (full curve). Falls back to the
        # 2-point summary persisted in settings when no fresh scan was run.
        self._nd_range: NDFilterRange | None = None
        self._xcheck_result: DetectorComparisonResult | None = None
        self._verify_result: GainCrossCheckResult | None = None

        self._settings = AutoCalibrationConnectionSettings.load()

        # The Arduino section is only relevant in standalone mode.
        self.ui.gbArduino.setVisible(self._standalone)

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
            self.ui.lblAngleOffset.setText(
                f"Winkelversatz: {fmt_angle(s.angle_offset_deg)}° (aus letzter Sitzung)"
            )
        if s.nd_pos_clear_deg is not None and s.nd_pos_dark_deg is not None:
            self.ui.lblNDRange.setText(
                f"Bereich (aus letzter Sitzung): {s.nd_pos_clear_deg:.2f}…{s.nd_pos_dark_deg:.2f}°"
            )

    def _set_phase(self, text: str) -> None:
        """Show *text* in the phase label; the full text stays available as tooltip.

        The label ignores its text width so a long message cannot enlarge the
        dialog — it is clipped instead.
        """
        self.ui.lblPhase.setText(text)
        self.ui.lblPhase.setToolTip(text)

    def _connect_signals(self) -> None:
        if self._standalone:
            self.ui.btnRefreshArduino.clicked.connect(self._refresh_arduino_list)
            self.ui.btnConnectArduino.clicked.connect(self._toggle_arduino)

        self.ui.btnRefreshKDC.clicked.connect(self._refresh_kdc_list)
        self.ui.btnConnectKDC.clicked.connect(self._toggle_kdc)
        self.ui.btnHomeKDC.clicked.connect(self._home_kdc)

        self.ui.btnRefreshNDStage.clicked.connect(self._refresh_nd_list)
        self.ui.btnConnectNDStage.clicked.connect(self._toggle_nd)
        self.ui.btnHomeNDStage.clicked.connect(self._home_nd)
        self.ui.btnZeroNDStage.clicked.connect(self._zero_nd)
        self.ui.btnSelfTestNDStage.clicked.connect(self._selftest_nd)
        self.ui.btnNDMotorOff.clicked.connect(self._nd_motor_off)
        for button, delta in (
            (self.ui.btnNDJogMinus5, -5.0),
            (self.ui.btnNDJogMinus1, -1.0),
            (self.ui.btnNDJogPlus1, 1.0),
            (self.ui.btnNDJogPlus5, 5.0),
        ):
            button.clicked.connect(partial(self._jog_nd, delta))

        self.ui.btnRefreshPM400.clicked.connect(self._refresh_pm_list)
        self.ui.btnConnectPM400.clicked.connect(self._toggle_pm400)
        self.ui.btnZeroPM400.clicked.connect(self._zero_pm400)

        self.ui.btnRefreshPM400B.clicked.connect(self._refresh_pm_b_list)
        self.ui.btnConnectPM400B.clicked.connect(self._toggle_pm400_b)
        self.ui.btnZeroPM400B.clicked.connect(self._zero_pm400_b)

        self.ui.radioSourcePolariser.toggled.connect(self._on_intensity_source_changed)
        self.ui.radioSourceND.toggled.connect(self._on_intensity_source_changed)

        self.ui.btnAlignPolariser.clicked.connect(self._start_align)
        self.ui.btnAbortAlign.clicked.connect(self._abort_align)

        self.ui.lineProfileName.textChanged.connect(self._update_output_path)
        self.ui.chkPowerFromCurve.toggled.connect(self._on_power_source_changed)
        self.ui.btnStart.clicked.connect(self._start_sweep)
        self.ui.btnAbort.clicked.connect(self._abort_sweep)
        self.ui.btnSave.clicked.connect(self._save_profile)

        self.ui.btnScanNDRange.clicked.connect(self._start_nd_scan)
        self.ui.btnAbortNDScan.clicked.connect(self._abort_nd_scan)

        self.ui.btnScanNDLin.clicked.connect(self._start_nd_lin)
        self.ui.btnAbortNDLin.clicked.connect(self._abort_nd_lin)
        self.ui.btnClearNDLin.clicked.connect(self._clear_nd_lin)
        self.ui.spinNDLinTol.valueChanged.connect(self._refresh_nd_lin_report)
        self.ui.spinNDLinFloorUW.valueChanged.connect(self._refresh_nd_lin_report)

        self.ui.btnStartXCheck.clicked.connect(self._start_xcheck)
        self.ui.btnAbortXCheck.clicked.connect(self._abort_xcheck)
        self.ui.btnSaveXCheck.clicked.connect(self._save_xcheck)

        self.ui.btnStartVerify.clicked.connect(self._start_verify)
        self.ui.btnAbortVerify.clicked.connect(self._abort_verify)

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
            self.ui.lblArduinoStatus.setText("Nicht verbunden")
            self.ui.btnConnectArduino.setText("Verbinden")
        else:
            port = self.ui.comboArduinoPort.currentText().strip()
            if not port:
                QMessageBox.warning(self, "Arduino", "Kein Port ausgewählt.")
                return
            ok = self._device_manager.connect_encoders(port)
            if ok:
                self.ui.lblArduinoStatus.setText(f"Verbunden: {port}")
                self.ui.btnConnectArduino.setText("Trennen")
            else:
                status = self._device_manager.get_encoder_status()
                err = status.error_message or "Verbindung fehlgeschlagen"
                QMessageBox.critical(
                    self,
                    "Arduino Verbindungsfehler",
                    f"Verbindung zu {port} fehlgeschlagen:\n{err}",
                )
        self._update_start_button_state()

    # ── KDC101 (polariser) ───────────────────────────────────────────────────

    @Slot()
    def _refresh_kdc_list(self) -> None:
        current = self.ui.comboKDC.currentText()
        self.ui.comboKDC.clear()
        devices = KDC101Polariser.list_devices()
        for conn_id, desc in devices:
            self.ui.comboKDC.addItem(f"{conn_id} — {desc}", userData=conn_id)
        if not devices and current:
            self.ui.comboKDC.addItem(current, userData=current)
        self._update_start_button_state()

    @Slot()
    def _toggle_kdc(self) -> None:
        if self._kdc.is_connected():
            self._kdc.disconnect()
            self.ui.lblKDCStatus.setText("Nicht verbunden")
            self.ui.btnConnectKDC.setText("Verbinden")
            self.ui.btnHomeKDC.setEnabled(False)
        else:
            conn_id = self.ui.comboKDC.currentData() or self.ui.comboKDC.currentText()
            if not conn_id:
                QMessageBox.warning(self, "KDC101", "Kein Gerät ausgewählt.")
                return
            try:
                self._kdc.connect(conn_id)
                self.ui.lblKDCStatus.setText(f"Verbunden: {conn_id}")
                self.ui.btnConnectKDC.setText("Trennen")
                self.ui.btnHomeKDC.setEnabled(True)
            except KDC101Error as exc:
                QMessageBox.critical(self, "KDC101 Fehler", str(exc))
        self._update_start_button_state()

    @Slot()
    def _home_kdc(self) -> None:
        if not self._kdc.is_connected():
            return
        self.ui.btnHomeKDC.setEnabled(False)
        self._set_phase("Referenzfahrt läuft…")
        self._home_thread = KDC101HomeWorker(self._kdc, parent=self)
        self._home_thread.done.connect(self._on_home_done)
        self._home_thread.error.connect(self._on_home_error)
        self._home_thread.start()

    @Slot()
    def _on_home_done(self) -> None:
        self.ui.btnHomeKDC.setEnabled(True)
        self._set_phase("Referenzfahrt abgeschlossen")

    @Slot(str)
    def _on_home_error(self, msg: str) -> None:
        self.ui.btnHomeKDC.setEnabled(True)
        self._set_phase("Referenzfahrt fehlgeschlagen")
        QMessageBox.critical(self, "KDC101 Fehler", msg)

    # ── KDC101 (ND-filter stage) ──────────────────────────────────────────────

    @Slot()
    def _refresh_nd_list(self) -> None:
        current = self.ui.comboNDStage.currentData() or self.ui.comboNDStage.currentText()
        self.ui.comboNDStage.clear()
        devices = NDStepperStage.list_devices()
        for conn_id, desc in devices:
            self.ui.comboNDStage.addItem(f"{conn_id} — {desc}", userData=conn_id)
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
            self.ui.lblNDStatus.setText("Nicht verbunden")
            self.ui.btnConnectNDStage.setText("Verbinden")
            self.ui.btnHomeNDStage.setEnabled(False)
            self.ui.btnZeroNDStage.setEnabled(False)
            self.ui.btnSelfTestNDStage.setEnabled(False)
            self._set_nd_manual_controls_enabled(False)
            self.ui.lblNDDriver.setText("Treiber: –")
        else:
            conn_id = self.ui.comboNDStage.currentData() or self.ui.comboNDStage.currentText()
            if not conn_id:
                QMessageBox.warning(self, "ND-Filterrad", "Kein Port ausgewählt.")
                return
            try:
                self._nd.connect(conn_id)
                self.ui.lblNDStatus.setText(f"Verbunden: {conn_id}")
                self.ui.btnConnectNDStage.setText("Trennen")
                self.ui.btnHomeNDStage.setEnabled(True)
                self.ui.btnZeroNDStage.setEnabled(True)
                self.ui.btnSelfTestNDStage.setEnabled(True)
                self._set_nd_manual_controls_enabled(True)
                self._show_nd_position()
                self._show_nd_driver_status()
            except NDStageError as exc:
                QMessageBox.critical(self, "ND-Filterrad Fehler", str(exc))
        self._update_start_button_state()

    @Slot()
    def _home_nd(self) -> None:
        if not self._nd.is_connected():
            return
        self.ui.btnHomeNDStage.setEnabled(False)
        self._set_phase("ND-Filterrad: Referenzfahrt läuft…")
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
            QMessageBox.critical(self, "ND-Filterrad Fehler", str(exc))
            return
        self._set_phase("ND-Filterrad: Nullpunkt gesetzt")
        self._show_nd_position()

    def _set_nd_manual_controls_enabled(self, enabled: bool) -> None:
        for button in (
            self.ui.btnNDJogMinus5,
            self.ui.btnNDJogMinus1,
            self.ui.btnNDJogPlus1,
            self.ui.btnNDJogPlus5,
            self.ui.btnNDMotorOff,
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
            QMessageBox.critical(self, "ND-Filterrad Fehler", str(exc))
            return
        self._set_phase("ND-Filterrad: Motor aus — von Hand drehen, dann „Nullpunkt hier setzen“")

    def _jog_nd(self, delta_deg: float) -> None:
        """Nudge the wheel by *delta_deg* to find the zero point by eye."""
        if not self._nd.is_connected():
            return
        try:
            self._nd.jog_deg(delta_deg)
        except NDStageError as exc:
            self._set_phase(f"ND-Filterrad: Schritt abgelehnt ({exc})")
            return
        self._show_nd_position()

    def _show_nd_driver_status(self) -> None:
        """Show the DRV8825 /FAULT state (OK / FAULT / not wired)."""
        try:
            status = self._nd.get_driver_status()
        except NDStageError:
            return
        labels = {
            "OK": "Treiber: OK (kein Fehler)",
            "FAULT": "Treiber: FEHLER (Überstrom/Übertemperatur)",
            "NA": "Treiber: /FAULT-Pin nicht verdrahtet",
        }
        self.ui.lblNDDriver.setText(labels.get(status, f"Treiber: {status}"))

    @Slot()
    def _selftest_nd(self) -> None:
        """Move the wheel briefly out and back while the controller watches /FAULT."""
        if not self._nd.is_connected():
            return
        self._set_phase("ND-Filterrad: Treibertest läuft…")
        try:
            ok, detail = self._nd.self_test()
        except NDStageError as exc:
            QMessageBox.critical(self, "ND-Filterrad Fehler", str(exc))
            return
        self._show_nd_position()
        self._show_nd_driver_status()
        if ok:
            self._set_phase("ND-Filterrad: Treibertest bestanden")
        elif detail.startswith("NA"):
            QMessageBox.information(
                self,
                "Treibertest",
                "Der /FAULT-Pin ist nicht verdrahtet, der Treiber kann nicht geprüft "
                "werden. Prüfe von Hand, ob sich das Rad bewegt hat.",
            )
        else:
            answer = QMessageBox.question(
                self,
                "Treibertest fehlgeschlagen",
                f"{detail}\n\nSoll der Treiber zurückgesetzt werden (/RESET-Impuls)? "
                "Die Ursache (Kurzschluss, zu hoher Strom, Überhitzung) muss vorher "
                "behoben sein.",
            )
            if answer == QMessageBox.StandardButton.Yes:
                self._reset_nd_driver()

    def _reset_nd_driver(self) -> None:
        try:
            self._nd.reset_driver()
        except NDStageError as exc:
            QMessageBox.critical(self, "Treiber-Reset", str(exc))
            return
        self._show_nd_driver_status()
        self._set_phase("ND-Filterrad: Treiber zurückgesetzt")

    def _show_nd_position(self) -> None:
        pos = self._nd.get_position_deg_nowait()
        if pos is not None:
            self.ui.lblNDPosition.setText(f"Winkel: {pos:.2f}°")

    @Slot()
    def _on_nd_home_done(self) -> None:
        self.ui.btnHomeNDStage.setEnabled(True)
        self._set_phase("ND-Filterrad: Referenzfahrt abgeschlossen")
        self._show_nd_position()

    @Slot(str)
    def _on_nd_home_error(self, msg: str) -> None:
        self.ui.btnHomeNDStage.setEnabled(True)
        self._set_phase("ND-Filterrad: Referenzfahrt fehlgeschlagen")
        QMessageBox.critical(self, "ND-Filterrad Fehler", msg)

    # ── PM400 A (reference) ───────────────────────────────────────────────────

    @Slot()
    def _refresh_pm_list(self) -> None:
        if self._pm_shared:
            self._sync_shared_pm_ui()
        else:
            populate_pm400_combo(self.ui.comboPM400, self._settings.pm400_visa_resource)
        self._update_start_button_state()

    def _sync_shared_pm_ui(self) -> None:
        """Mirror MainWindow's PM400 connection; connecting happens there."""
        self.ui.btnRefreshPM400.setEnabled(False)
        self.ui.comboPM400.setEnabled(False)
        self.ui.btnConnectPM400.setEnabled(False)
        if self._pm.is_connected():
            info = self._pm.sensor_info()
            sensor_str = " | ".join(str(x) for x in info[:3]) if info else "–"
            self.ui.lblPM400Status.setText(f"Verbunden (Hauptfenster): {sensor_str}")
            self.ui.btnZeroPM400.setEnabled(True)
        else:
            self.ui.lblPM400Status.setText("Nicht verbunden — PM400 im Hauptfenster verbinden")
            self.ui.btnZeroPM400.setEnabled(False)

    @Slot()
    def _toggle_pm400(self) -> None:
        if self._pm.is_connected():
            self._pm.disconnect()
            self.ui.lblPM400Status.setText("Nicht verbunden")
            self.ui.btnConnectPM400.setText("Verbinden")
            self.ui.btnZeroPM400.setEnabled(False)
        else:
            resource = self.ui.comboPM400.currentText().strip()
            if not resource:
                QMessageBox.warning(self, "PM400", "Kein VISA-Ressource angegeben.")
                return
            try:
                self._pm.connect(resource)
                info = self._pm.sensor_info()
                sensor_str = " | ".join(str(x) for x in info[:3]) if info else "–"
                self.ui.lblPM400Status.setText(f"Verbunden: {sensor_str}")
                self.ui.btnConnectPM400.setText("Trennen")
                self.ui.btnZeroPM400.setEnabled(True)
            except PM400Error as exc:
                QMessageBox.critical(self, "PM400 Fehler", str(exc))
        self._update_start_button_state()

    @Slot()
    def _zero_pm400(self) -> None:
        if not self._pm.is_connected():
            return
        try:
            self._pm.zero()
            self._set_phase("PM400 Nullabgleich gestartet")
        except PM400Error as exc:
            QMessageBox.critical(self, "PM400 Fehler", str(exc))

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
            self.ui.lblPM400BStatus.setText("Nicht verbunden")
            self.ui.btnConnectPM400B.setText("Verbinden")
            self.ui.btnZeroPM400B.setEnabled(False)
        else:
            resource = self.ui.comboPM400B.currentText().strip()
            if not resource:
                QMessageBox.warning(self, "PM400 B", "Kein VISA-Ressource angegeben.")
                return
            try:
                self._pm_b.connect(resource)
                info = self._pm_b.sensor_info()
                sensor_str = " | ".join(str(x) for x in info[:3]) if info else "–"
                self.ui.lblPM400BStatus.setText(f"Verbunden: {sensor_str}")
                self.ui.btnConnectPM400B.setText("Trennen")
                self.ui.btnZeroPM400B.setEnabled(True)
            except PM400Error as exc:
                QMessageBox.critical(self, "PM400 B Fehler", str(exc))
        self._update_start_button_state()

    @Slot()
    def _zero_pm400_b(self) -> None:
        if not self._pm_b.is_connected():
            return
        try:
            self._pm_b.zero()
            self._set_phase("PM400 B Nullabgleich gestartet")
        except PM400Error as exc:
            QMessageBox.critical(self, "PM400 B Fehler", str(exc))

    # ── Intensity source ──────────────────────────────────────────────────────

    @Slot()
    def _on_intensity_source_changed(self) -> None:
        """Enable the polariser-alignment or ND-power-grid controls, not both.

        Both group boxes stay visible (disabled, not hidden) per the
        Designer-first UI convention — hiding widgets that carry live state
        (like lblAngleOffset) is more surprising than greying them out.
        """
        nd_mode = self.ui.radioSourceND.isChecked()
        self.ui.gbAlignment.setEnabled(not nd_mode)
        self.ui.gbPowerGrid.setEnabled(nd_mode)
        self._on_power_source_changed()

    @Slot()
    def _on_power_source_changed(self) -> None:
        """Grey out the PM400-dependent grid options in curve mode and refresh Start."""
        from_curve = self.ui.chkPowerFromCurve.isChecked()
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
            QMessageBox.warning(self, "Ausrichtung", "KDC101 und PM400 müssen verbunden sein.")
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

        self.ui.btnAlignPolariser.setEnabled(False)
        self.ui.btnAbortAlign.setEnabled(True)
        self.ui.btnStart.setEnabled(False)
        self._set_phase("Ausrichtungsscan läuft…")
        self._align_worker.start()

    @Slot()
    def _abort_align(self) -> None:
        if self._align_worker is not None and self._align_worker.isRunning():
            self._align_worker.abort()
            self.ui.btnAbortAlign.setEnabled(False)
            self._set_phase("Ausrichtung wird abgebrochen…")

    @Slot(int, int)
    def _on_align_progress(self, done: int, total: int) -> None:
        self.ui.progressBar.setValue(done)

    @Slot(float)
    def _on_align_finished(self, angle_max_deg: float) -> None:
        self._angle_offset_deg = angle_max_deg
        self.ui.lblAngleOffset.setText(
            f"Polarisator 0°: {fmt_angle(angle_max_deg)}°  |  "
            f"90°: {fmt_angle(angle_max_deg + 90.0)}°"
        )
        self._set_phase("Ausrichtung abgeschlossen")
        self.ui.btnAbortAlign.setEnabled(False)
        self._update_start_button_state()

    @Slot(str)
    def _on_align_failed(self, message: str) -> None:
        self._set_phase("Ausrichtung fehlgeschlagen")
        self.ui.btnAbortAlign.setEnabled(False)
        self._update_start_button_state()
        if "abgebrochen" not in message.lower():
            QMessageBox.critical(self, "Ausrichtungsfehler", message)

    # ── Sweep control ─────────────────────────────────────────────────────────

    @Slot()
    def _start_sweep(self) -> None:
        gains = tuple(
            stage
            for stage, chk in (
                (1, self.ui.chkGain1),
                (2, self.ui.chkGain2),
                (3, self.ui.chkGain3),
                (4, self.ui.chkGain4),
            )
            if chk.isChecked()
        )
        if not gains:
            QMessageBox.warning(self, "Start", "Mindestens eine Gain-Stufe auswählen.")
            return

        profile_name = self.ui.lineProfileName.text().strip()
        if not profile_name:
            QMessageBox.warning(self, "Start", "Bitte einen Profilnamen eingeben.")
            return

        nd_mode = self.ui.radioSourceND.isChecked()
        from_curve = nd_mode and self.ui.chkPowerFromCurve.isChecked()
        nd_scan_points = self._get_nd_scan_points() if nd_mode else ()
        if from_curve:
            if self._nd_range is None:
                QMessageBox.warning(
                    self,
                    "Start",
                    "Für 'Leistung aus ND-Kennlinie' ist ein Bereichsscan dieser Sitzung nötig "
                    "(der Nullpunkt des Filterrads ist pro Sitzung beliebig).",
                )
                return
            nd_scan_points = self._nd_curve_between_ends(self._nd_range)
        if nd_mode and not nd_scan_points:
            QMessageBox.warning(
                self,
                "Start",
                "Kein ND-Bereich kalibriert. Bitte zuerst im Tab 'ND-Bereich' einen "
                "Bereichsscan durchführen.",
            )
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

        total = params.n_points * len(params.selected_gains)
        self.ui.progressBar.setMaximum(total)
        self.ui.progressBar.setValue(0)
        self.ui.plotWidget.clear()
        self._set_running(True)
        self._worker.start()

    @Slot()
    def _abort_sweep(self) -> None:
        if self._worker is not None:
            self._worker.abort()
            self._set_phase("Abbrechen…")
            self.ui.btnAbort.setEnabled(False)

    # ── Sweep worker signal handlers ─────────────────────────────────────────

    @Slot(int)
    def _on_gain_started(self, gain: int) -> None:
        self._set_phase(f"Gain {gain} wird kalibriert…")

    @Slot(int, float, float, float, float)
    def _on_point_recorded(
        self,
        gain: int,
        level: float,
        voltage: float,
        pm_power: float,
    ) -> None:
        self.ui.plotWidget.add_point(gain, voltage, pm_power)

    @Slot(int, int)
    def _on_progress(self, done: int, total: int) -> None:
        self.ui.progressBar.setValue(done)

    @Slot(object)
    def _on_sweep_finished(self, profile: PowerCalibrationProfile) -> None:
        self._profile = profile
        self._set_running(False)
        self._set_phase("Kalibrierung abgeschlossen")
        self.ui.btnSave.setEnabled(True)
        if self._data_controller is not None:
            self._data_controller.start_continuous_reading()
        self._append_log("Kalibrierung erfolgreich abgeschlossen.")

    @Slot(str)
    def _on_sweep_failed(self, message: str) -> None:
        self._set_running(False)
        self._set_phase(f"Fehler: {message}")
        if self._data_controller is not None:
            self._data_controller.start_continuous_reading()
        QMessageBox.critical(self, "Kalibrierung fehlgeschlagen", message)

    # ── ND range scan ─────────────────────────────────────────────────────────

    @Slot()
    def _start_nd_scan(self) -> None:
        if not self._nd.is_connected() or not self._pm.is_connected():
            QMessageBox.warning(
                self, "ND-Bereichsscan", "ND-Filterrad und PM400 müssen verbunden sein."
            )
            return

        if not self._apply_pm_settings("ND-Bereichsscan"):
            return

        dark_floor_uw = self.ui.spinNDDarkFloorUW.value()
        dark_floor_W = dark_floor_uw * 1e-6 if dark_floor_uw > 0 else None

        self.ui.ndPlotWidget.clear()
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
            self._set_phase("Abbrechen…")
            self.ui.btnAbortNDScan.setEnabled(False)

    @Slot(float, float)
    def _on_nd_point_scanned(self, position_deg: float, power_W: float) -> None:
        self.ui.ndPlotWidget.add_point(position_deg, power_W)

    @Slot(object)
    def _on_nd_scan_finished(self, result: NDFilterRange) -> None:
        self._nd_range = result
        self._set_nd_scan_running(False)
        self.ui.ndPlotWidget.set_range_markers(result.pos_clear_deg, result.pos_dark_deg)
        warning = "" if result.monotonic else " ⚠ nicht monoton — Ergebnis prüfen!"
        self.ui.lblNDRange.setText(
            f"Bereich: {result.pos_clear_deg:.2f}…{result.pos_dark_deg:.2f}° "
            f"({result.power_clear_W:.3e} → {result.power_dark_W:.3e} W, "
            f"{result.dynamic_range_dB:.1f} dB){warning}"
        )
        self._set_phase("ND-Bereichsscan abgeschlossen")
        # The linearity scans only matter inside the usable range.
        self.ui.spinNDLinStart.setValue(result.pos_clear_deg)
        self.ui.spinNDLinEnd.setValue(result.pos_dark_deg)
        self._refresh_nd_lin_status()
        self._persist_settings()

    @Slot(str)
    def _on_nd_scan_failed(self, message: str) -> None:
        self._set_nd_scan_running(False)
        self._set_phase(f"Fehler: {message}")
        if "abgebrochen" not in message.lower():
            QMessageBox.critical(self, "ND-Bereichsscan fehlgeschlagen", message)

    def _set_nd_scan_running(self, running: bool) -> None:
        self._nd_range_active = running
        self.ui.gbNDScanParams.setEnabled(not running)
        self.ui.btnAbortNDScan.setEnabled(running)
        self._refresh_nd_scan_buttons()

    def _apply_pm_settings(self, title: str) -> bool:
        """Push the dialog's wavelength and attenuation to the PM400 before an ND scan.

        The calibration sweep sets these on the meter at its start. Scanning with
        whatever the device had stored would build a position/power curve in
        different units than the sweep later targets.
        """
        try:
            self._pm.set_wavelength_nm(self.ui.spinWavelength.value())
            self._pm.set_attenuation_dB(self.ui.spinAttenuation.value())
        except PM400Error as exc:
            QMessageBox.critical(self, title, f"PM400-Konfiguration fehlgeschlagen: {exc}")
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
        self.ui.btnScanNDRange.setEnabled(ready)
        self.ui.btnScanNDLin.setEnabled(ready)
        self.ui.btnClearNDLin.setEnabled(bool(self._nd_lin_scans) and not self._nd_lin_active)

    # ── ND linearity scans ────────────────────────────────────────────────────

    @Slot()
    def _start_nd_lin(self) -> None:
        if not self._nd_scan_ready():
            QMessageBox.warning(
                self, "ND-Linearität", "ND-Filterrad und PM400 müssen verbunden sein."
            )
            return
        if not self._apply_pm_settings("ND-Linearität"):
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
        worker.scan_started.connect(self.ui.ndLinPlotWidget.begin_scan)
        worker.point_scanned.connect(self.ui.ndLinPlotWidget.add_point)
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
            self._set_phase("Abbrechen…")
            self.ui.btnAbortNDLin.setEnabled(False)

    @Slot()
    def _clear_nd_lin(self) -> None:
        self._nd_lin_scans.clear()
        self.ui.ndLinPlotWidget.clear()
        self._refresh_nd_lin_report()
        self._refresh_nd_scan_buttons()

    @Slot(object)
    def _on_nd_lin_scan_finished(self, scan: NDLinearityScan) -> None:
        self._nd_lin_scans.append(scan)
        self._refresh_nd_lin_report()

    @Slot(object)
    def _on_nd_lin_finished(self, scans: list[NDLinearityScan]) -> None:
        self._set_nd_lin_running(False)
        self._set_phase(f"ND-Linearität: {len(scans)} Scan(s) abgeschlossen")

    @Slot(str)
    def _on_nd_lin_failed(self, message: str) -> None:
        self._set_nd_lin_running(False)
        self._set_phase(f"Fehler: {message}")
        if "abgebrochen" not in message.lower():
            QMessageBox.critical(self, "ND-Linearität fehlgeschlagen", message)

    def _set_nd_lin_running(self, running: bool) -> None:
        self._nd_lin_active = running
        self.ui.gbNDLinParams.setEnabled(not running)
        self.ui.btnAbortNDLin.setEnabled(running)
        self._refresh_nd_scan_buttons()

    def _nd_curve_source_text(self) -> str:
        """Describe which ND position/power curve the calibration sweeps invert."""
        if self._nd_range is not None:
            n = len(self._nd_range.scan_points)
            return f"Sweep-Kennlinie: Bereichsscan dieser Sitzung ({n} Punkte, Tabelleninversion)"
        if len(self._get_nd_scan_points()) == 2:
            return (
                "Sweep-Kennlinie: nur 2-Punkt-Näherung aus letzter Sitzung — ungenau bei "
                "nichtlinearem Filter und nur gültig, wenn der Nullpunkt unverändert ist "
                "(kein Endschalter). Bereichsscan wiederholen"
            )
        return "Sweep-Kennlinie: keine — zuerst einen Bereichsscan durchführen"

    def _refresh_nd_lin_status(self) -> None:
        """Say that the linearity result is diagnostic only, and what sweeps use instead."""
        n = len(self._nd_lin_scans)
        head = (
            f"Linearität: {n} Scan(s) nur als Diagnose, nicht auf Sweeps angewendet."
            if n
            else "Linearität: noch nicht gemessen (nur Diagnose, wird nicht auf Sweeps angewendet)."
        )
        self.ui.lblNDLinStatus.setText(f"{head}\n{self._nd_curve_source_text()}")

    @Slot()
    def _refresh_nd_lin_report(self) -> None:
        """Re-analyse all collected scans and redraw residuals + report."""
        tol = self.ui.spinNDLinTol.value()
        self.ui.ndLinPlotWidget.set_tolerance(tol)
        self._refresh_nd_lin_status()
        if not self._nd_lin_scans:
            self.ui.txtNDLinReport.clear()
            return
        floor_W = self.ui.spinNDLinFloorUW.value() * 1e-6
        try:
            report = analyse_linearity_set(self._nd_lin_scans, noise_floor_W=floor_W)
        except ValueError as exc:
            self.ui.txtNDLinReport.setPlainText(f"Analyse nicht möglich: {exc}")
            return
        for fit in report.fits:
            self.ui.ndLinPlotWidget.set_residuals(
                fit.index, fit.direction, fit.positions_deg, fit.residuals_od
            )
        self.ui.txtNDLinReport.setPlainText(format_nd_linearity_report(report, tol))

    # ── Detector cross-check ──────────────────────────────────────────────────

    @Slot()
    def _start_xcheck(self) -> None:
        if (
            not self._nd.is_connected()
            or not self._pm.is_connected()
            or not self._pm_b.is_connected()
        ):
            QMessageBox.warning(
                self,
                "Detektor-Vergleich",
                "ND-Filterrad, PM400 A und PM400 B müssen verbunden sein.",
            )
            return
        scan = self._get_nd_scan_points()
        if not scan:
            QMessageBox.warning(
                self,
                "Detektor-Vergleich",
                "Kein ND-Bereich kalibriert. Bitte zuerst im Tab 'ND-Bereich' einen "
                "Bereichsscan durchführen.",
            )
            return
        pos_clear = min(scan, key=lambda pt: abs(pt[1] - max(p for _, p in scan)))[0]
        pos_dark = min(scan, key=lambda pt: abs(pt[1] - min(p for _, p in scan)))[0]

        self.ui.xCheckPlotWidget.clear()
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
            self._set_phase("Abbrechen…")
            self.ui.btnAbortXCheck.setEnabled(False)

    @Slot(float, float, float)
    def _on_xcheck_point_recorded(self, position: float, power_a: float, power_b: float) -> None:
        self.ui.xCheckPlotWidget.add_point(power_a, power_b)

    @Slot(object)
    def _on_xcheck_finished(self, result: DetectorComparisonResult) -> None:
        self._xcheck_result = result
        self._set_xcheck_running(False)
        self.ui.btnSaveXCheck.setEnabled(True)
        verdict = "OK" if result.passed else "FEHLGESCHLAGEN"
        self.ui.lblXCheckResult.setText(
            f"Ergebnis: mittleres Verhältnis={result.mean_ratio:.4f}, "
            f"Streuung={result.ratio_spread_pct:.2f}%, "
            f"max. Abweichung={result.worst_deviation_pct:.2f}% — {verdict}"
        )
        self._set_phase("Detektor-Vergleich abgeschlossen")

    @Slot(str)
    def _on_xcheck_failed(self, message: str) -> None:
        self._set_xcheck_running(False)
        self._set_phase(f"Fehler: {message}")
        if "abgebrochen" not in message.lower():
            QMessageBox.critical(self, "Detektor-Vergleich fehlgeschlagen", message)

    @Slot()
    def _save_xcheck(self) -> None:
        if self._xcheck_result is None:
            return
        default_name = f"detector_crosscheck_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        path, _ = QFileDialog.getSaveFileName(
            self, "Vergleichsergebnis speichern", default_name, "JSON (*.json)"
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(self._xcheck_result.to_json_dict(), fh, indent=2)
        except Exception as exc:
            QMessageBox.critical(self, "Speichern fehlgeschlagen", str(exc))
            return
        QMessageBox.information(self, "Gespeichert", f"Gespeichert unter:\n{path}")

    def _set_xcheck_running(self, running: bool) -> None:
        self.ui.gbXCheckParams.setEnabled(not running)
        self.ui.btnStartXCheck.setEnabled(not running and self._xcheck_ready())
        self.ui.btnAbortXCheck.setEnabled(running)

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
        config = import_config("de")
        limits = load_gain_power_limits(config)
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
            QMessageBox.warning(
                self,
                "Gain-Prüfung",
                "Bitte zuerst eine Kalibrierung durchführen oder ein Profil laden.",
            )
            return
        if not self._nd.is_connected() or not self._pm.is_connected():
            QMessageBox.warning(
                self, "Gain-Prüfung", "ND-Filterrad und PM400 müssen verbunden sein."
            )
            return

        gains = tuple(sorted(g for g, cal in self._profile.gains.items() if cal.points))
        if len(gains) < 2:
            QMessageBox.warning(
                self, "Gain-Prüfung", "Mindestens 2 kalibrierte Gain-Stufen erforderlich."
            )
            return

        levels = self._compute_verify_levels(self.ui.spinVerifyLevels.value())
        if not levels:
            QMessageBox.warning(
                self,
                "Gain-Prüfung",
                "Keine geeigneten Pegel gefunden (ND-Bereich kalibriert? "
                "Überlappen sich die Gain-Fenster in config.json?).",
            )
            return

        device_manager = (
            self._device_manager if self._standalone else self._data_controller.device_manager
        )
        self.ui.tableGainVerify.setRowCount(0)
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
            self._set_phase("Abbrechen…")
            self.ui.btnAbortVerify.setEnabled(False)

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
        verdict = "OK" if result.passed else "FEHLGESCHLAGEN"
        self.ui.lblVerifyResult.setText(
            f"Ergebnis: max. Streuung={result.worst_spread_pct:.2f}%, "
            f"max. PM400-Abweichung={result.worst_pm_deviation_pct:.2f}% — {verdict}"
        )
        self._set_phase("Gain-Prüfung abgeschlossen")
        if self._profile is not None:
            self._profile.gain_crosscheck = result.to_json_dict()

    @Slot(str)
    def _on_verify_failed(self, message: str) -> None:
        self._set_verify_running(False)
        self._set_phase(f"Fehler: {message}")
        if "abgebrochen" not in message.lower():
            QMessageBox.critical(self, "Gain-Prüfung fehlgeschlagen", message)

    def _set_verify_running(self, running: bool) -> None:
        self.ui.gbVerifyParams.setEnabled(not running)
        self.ui.btnStartVerify.setEnabled(not running and self._verify_ready())
        self.ui.btnAbortVerify.setEnabled(running)

    def _verify_ready(self) -> bool:
        return self._profile is not None and self._nd.is_connected() and self._pm.is_connected()

    # ── Save ──────────────────────────────────────────────────────────────────

    @Slot()
    def _save_profile(self) -> None:
        if self._profile is None:
            return
        path = _Profile.default_path(self._profile.name)
        try:
            self._profile.save(path)
        except Exception as exc:
            QMessageBox.critical(self, "Speichern fehlgeschlagen", str(exc))
            return
        QMessageBox.information(self, "Profil gespeichert", f"Gespeichert unter:\n{path}")
        self.profile_saved.emit()

    # ── Helpers ───────────────────────────────────────────────────────────────

    @Slot(str)
    def _append_log(self, msg: str) -> None:
        self.ui.plainTextLog.appendPlainText(msg)

    @Slot(str)
    def _update_output_path(self, name: str) -> None:
        if name.strip():
            path = _Profile.default_path(name.strip())
            self.ui.lblOutputPath.setText(str(path))
        else:
            self.ui.lblOutputPath.setText("–")
        self._update_start_button_state()

    def _update_start_button_state(self) -> None:
        arduino_ok = (
            (self._device_manager is not None and self._device_manager.is_encoder_connected())
            if self._standalone
            else True
        )
        nd_mode = self.ui.radioSourceND.isChecked()
        actuator_ok = self._nd.is_connected() if nd_mode else self._kdc.is_connected()
        pm_ok = self._pm.is_connected() or (nd_mode and self.ui.chkPowerFromCurve.isChecked())
        hw_ready = actuator_ok and pm_ok and arduino_ok
        self.ui.btnAlignPolariser.setEnabled(self._kdc.is_connected() and self._pm.is_connected())
        self.ui.btnStart.setEnabled(hw_ready and bool(self.ui.lineProfileName.text().strip()))
        self._refresh_nd_scan_buttons()
        self.ui.btnStartXCheck.setEnabled(self._xcheck_ready())
        self.ui.btnStartVerify.setEnabled(self._verify_ready())

    def _set_running(self, running: bool) -> None:
        for w in (
            self.ui.gbConnections,
            self.ui.gbBeam,
            self.ui.gbAlignment,
            self.ui.gbSweep,
            self.ui.gbPowerGrid,
            self.ui.gbProfile,
            self.ui.gbIntensitySource,
            self.ui.btnStart,
        ):
            w.setEnabled(not running)
        self.ui.btnAbort.setEnabled(running)
        if not running:
            # Restores the correct gbAlignment/gbPowerGrid enabled split.
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


def format_nd_linearity_report(report: NDLinearityReport, tolerance_od: float) -> str:
    """Render a fixed-width comparison of all scans in *report*.

    A scan passes when its largest deviation from the straight-line OD fit is
    within *tolerance_od*.
    """
    lines = [
        f"Referenz OD=0: {report.reference_power_W:.3e} W    Toleranz: ±{tolerance_od:.3f} OD",
        "Scan  Richtung   Pkt  Steigung[OD/°]  RMS[OD]  Max[OD]  Max[%]  bei[°]  Status",
    ]
    for fit in report.fits:
        direction = "rückwärts" if fit.direction == BACKWARD else "vorwärts "
        status = "OK" if fit.max_residual_od <= tolerance_od else "ÜBER TOLERANZ"
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
            f"Steigung: Mittel {mean_slope:.5f} OD/°, Streuung "
            f"{report.slope_std_od_per_deg:.5f} OD/° ({rel:.2f} %)"
        )
    if report.od_scatter_mean is not None and report.od_scatter_max is not None:
        lines.append(
            f"OD-Streuung zwischen Scans: Mittel {report.od_scatter_mean:.4f} OD, "
            f"Max {report.od_scatter_max:.4f} OD"
        )
    if report.hysteresis_od is not None:
        deg = f" ≈ {report.hysteresis_deg:.2f}°" if report.hysteresis_deg is not None else ""
        lines.append(f"Hysterese (vorwärts ↔ rückwärts): {report.hysteresis_od:.4f} OD{deg}")
    elif len(report.fits) > 1:
        lines.append("Hysterese: nicht bestimmbar (nur eine Richtung gemessen)")
    return "\n".join(lines)
