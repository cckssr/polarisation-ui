"""Automatic power calibration dialog.

Drives a KDC101 + PRM1/MZ8 polariser rotation stage and a Thorlabs PM400
power meter to record (voltage, power) pairs for all four PDTIA gain stages,
then writes a PowerCalibrationProfile in the same format used by the manual
calibration window.

Standalone mode (data_controller=None): the dialog manages its own Arduino
connection and shows the gbArduino section.  The Arduino is needed for ADC
reads and PDTIA gain switching during the sweep.
"""

from typing import Optional

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QDialog, QMessageBox

from polarisation_ui.core.auto_calibration_settings import (
    AutoCalibrationConnectionSettings,
    AutoCalibrationParams,
)
from polarisation_ui.core.exceptions import KDC101Error, PM400Error
from polarisation_ui.core.power_calibration import (
    PowerCalibrationProfile,
    PowerCalibrationProfile as _Profile,
)
from polarisation_ui.infrastructure.device_manager import GoniometerDeviceManager
from polarisation_ui.infrastructure.devices.kdc101_polariser import KDC101Polariser
from polarisation_ui.infrastructure.devices.pm400 import PM400PowerMeter
from polarisation_ui.infrastructure.logging import Debug
from polarisation_ui.infrastructure.qt_threads import (
    AlignPolariserWorker,
    AutoPowerCalibrationWorker,
    KDC101HomeWorker,
)
from polarisation_ui.pyqt.ui_auto_power_calibration import Ui_AutoPowerCalibrationDialog


class AutoPowerCalibrationWindow(QDialog):
    """Non-modal dialog for automated detector power calibration.

    When *data_controller* is provided the dialog is opened from MainWindow
    and the existing DataController supplies the Arduino device manager.
    When *data_controller* is None the dialog runs standalone: it shows the
    gbArduino section so the user can connect to the Arduino directly.
    """

    profile_saved = Signal()

    def __init__(self, data_controller=None, parent=None) -> None:
        super().__init__(parent)
        self.ui = Ui_AutoPowerCalibrationDialog()
        self.ui.setupUi(self)

        self._data_controller = data_controller
        self._standalone = data_controller is None
        # In standalone mode we own the device manager; otherwise we borrow it.
        self._device_manager: Optional[GoniometerDeviceManager] = (
            GoniometerDeviceManager(use_mock=False) if self._standalone else None
        )

        self._kdc = KDC101Polariser()
        self._pm = PM400PowerMeter()
        self._worker: Optional[AutoPowerCalibrationWorker] = None
        self._align_worker: Optional[AlignPolariserWorker] = None
        self._home_thread: Optional[KDC101HomeWorker] = None
        self._profile: Optional[PowerCalibrationProfile] = None
        self._angle_offset_deg: float = 0.0
        self._settings = AutoCalibrationConnectionSettings.load()

        # The Arduino section is only relevant in standalone mode.
        self.ui.gbArduino.setVisible(self._standalone)

        self._apply_settings()
        self._connect_signals()
        self._refresh_kdc_list()
        self._refresh_pm_list()
        if self._standalone:
            self._refresh_arduino_list()
        self._update_start_button_state()

    # ── Setup ─────────────────────────────────────────────────────────────────

    def _apply_settings(self) -> None:
        s = self._settings
        if s.kdc101_conn_id:
            self.ui.comboKDC.addItem(s.kdc101_conn_id)
        if s.pm400_visa_resource:
            self.ui.comboPM400.setEditText(s.pm400_visa_resource)
        self.ui.spinWavelength.setValue(s.wavelength_nm)
        self.ui.spinAttenuation.setValue(s.beamsplitter_attenuation_dB)
        if s.angle_offset_deg != 0.0:
            self._angle_offset_deg = s.angle_offset_deg
            self.ui.lblAngleOffset.setText(
                f"Winkelversatz: {s.angle_offset_deg:.2f}° (aus letzter Sitzung)"
            )

    def _connect_signals(self) -> None:
        if self._standalone:
            self.ui.btnRefreshArduino.clicked.connect(self._refresh_arduino_list)
            self.ui.btnConnectArduino.clicked.connect(self._toggle_arduino)

        self.ui.btnRefreshKDC.clicked.connect(self._refresh_kdc_list)
        self.ui.btnConnectKDC.clicked.connect(self._toggle_kdc)
        self.ui.btnHomeKDC.clicked.connect(self._home_kdc)

        self.ui.btnRefreshPM400.clicked.connect(self._refresh_pm_list)
        self.ui.btnConnectPM400.clicked.connect(self._toggle_pm400)
        self.ui.btnZeroPM400.clicked.connect(self._zero_pm400)

        self.ui.btnAlignPolariser.clicked.connect(self._start_align)
        self.ui.btnAbortAlign.clicked.connect(self._abort_align)

        self.ui.lineProfileName.textChanged.connect(self._update_output_path)
        self.ui.btnStart.clicked.connect(self._start_sweep)
        self.ui.btnAbort.clicked.connect(self._abort_sweep)
        self.ui.btnSave.clicked.connect(self._save_profile)

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

    # ── KDC101 ────────────────────────────────────────────────────────────────

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
        self.ui.lblPhase.setText("Referenzfahrt läuft…")
        self._home_thread = KDC101HomeWorker(self._kdc, parent=self)
        self._home_thread.done.connect(self._on_home_done)
        self._home_thread.error.connect(self._on_home_error)
        self._home_thread.start()

    @Slot()
    def _on_home_done(self) -> None:
        self.ui.btnHomeKDC.setEnabled(True)
        self.ui.lblPhase.setText("Referenzfahrt abgeschlossen")

    @Slot(str)
    def _on_home_error(self, msg: str) -> None:
        self.ui.btnHomeKDC.setEnabled(True)
        self.ui.lblPhase.setText("Referenzfahrt fehlgeschlagen")
        QMessageBox.critical(self, "KDC101 Fehler", msg)

    # ── PM400 ─────────────────────────────────────────────────────────────────

    @Slot()
    def _refresh_pm_list(self) -> None:
        current = self.ui.comboPM400.currentText()
        resources = PM400PowerMeter.list_resources()
        self.ui.comboPM400.clear()
        for r in resources:
            self.ui.comboPM400.addItem(r)
        if current and self.ui.comboPM400.findText(current) < 0:
            self.ui.comboPM400.addItem(current)
        if current:
            idx = self.ui.comboPM400.findText(current)
            if idx >= 0:
                self.ui.comboPM400.setCurrentIndex(idx)
        self._update_start_button_state()

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
            self.ui.lblPhase.setText("PM400 Nullabgleich gestartet")
        except PM400Error as exc:
            QMessageBox.critical(self, "PM400 Fehler", str(exc))

    # ── Polariser alignment ───────────────────────────────────────────────────

    @Slot()
    def _start_align(self) -> None:
        """Scan the PM400 while rotating the stage to find the max-transmission angle."""
        if not self._kdc.is_connected() or not self._pm.is_connected():
            QMessageBox.warning(
                self, "Ausrichtung", "KDC101 und PM400 müssen verbunden sein."
            )
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
        self.ui.lblPhase.setText("Ausrichtungsscan läuft…")
        self._align_worker.start()

    @Slot()
    def _abort_align(self) -> None:
        if self._align_worker is not None and self._align_worker.isRunning():
            self._align_worker.abort()
            self.ui.btnAbortAlign.setEnabled(False)
            self.ui.lblPhase.setText("Ausrichtung wird abgebrochen…")

    @Slot(int, int)
    def _on_align_progress(self, done: int, total: int) -> None:
        self.ui.progressBar.setValue(done)

    @Slot(float)
    def _on_align_finished(self, angle_max_deg: float) -> None:
        self._angle_offset_deg = angle_max_deg
        self.ui.lblAngleOffset.setText(
            f"Polarisator 0°: {angle_max_deg:.2f}°  |  90°: {angle_max_deg + 90.0:.2f}°"
        )
        self.ui.lblPhase.setText("Ausrichtung abgeschlossen")
        self.ui.btnAbortAlign.setEnabled(False)
        self._update_start_button_state()

    @Slot(str)
    def _on_align_failed(self, message: str) -> None:
        self.ui.lblPhase.setText("Ausrichtung fehlgeschlagen")
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

        params = AutoCalibrationParams(
            selected_gains=gains,
            angle_start_deg=self.ui.spinAngleStart.value(),
            angle_end_deg=self.ui.spinAngleEnd.value(),
            n_points=self.ui.spinNPoints.value(),
            grid_mode=(
                "linear_cos2" if self.ui.radioLinearCos2.isChecked() else "linear_angle"
            ),
            point_settle_s=self.ui.spinPointSettle.value(),
            gain_settle_s=self.ui.spinGainSettle.value(),
            detector_samples=self.ui.spinDetectorSamples.value(),
            pm_averaging=self.ui.spinPmAveraging.value(),
            profile_name=profile_name,
            wavelength_nm=self.ui.spinWavelength.value(),
            beamsplitter_attenuation_dB=self.ui.spinAttenuation.value(),
            angle_offset_deg=self._angle_offset_deg,
            adc_saturation_threshold_V=self.ui.spinSaturationThreshold.value(),
        )

        if self._data_controller is not None:
            self._data_controller.stop_continuous_reading()

        device_manager = (
            self._device_manager
            if self._standalone
            else self._data_controller.device_manager
        )
        self._worker = AutoPowerCalibrationWorker(
            device_manager=device_manager,
            kdc=self._kdc,
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
            self.ui.lblPhase.setText("Abbrechen…")
            self.ui.btnAbort.setEnabled(False)

    # ── Worker signal handlers ─────────────────────────────────────────────────

    @Slot(int)
    def _on_gain_started(self, gain: int) -> None:
        self.ui.lblPhase.setText(f"Gain {gain} wird kalibriert…")

    @Slot(int, float, float, float, float)
    def _on_point_recorded(
        self,
        gain: int,
        angle_deg: float,
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
        self.ui.lblPhase.setText("Kalibrierung abgeschlossen")
        self.ui.btnSave.setEnabled(True)
        if self._data_controller is not None:
            self._data_controller.start_continuous_reading()
        self._append_log("Kalibrierung erfolgreich abgeschlossen.")

    @Slot(str)
    def _on_sweep_failed(self, message: str) -> None:
        self._set_running(False)
        self.ui.lblPhase.setText(f"Fehler: {message}")
        if self._data_controller is not None:
            self._data_controller.start_continuous_reading()
        QMessageBox.critical(self, "Kalibrierung fehlgeschlagen", message)

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
        QMessageBox.information(
            self, "Profil gespeichert", f"Gespeichert unter:\n{path}"
        )
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
            (
                self._device_manager is not None
                and self._device_manager.is_encoder_connected()
            )
            if self._standalone
            else True
        )
        hw_ready = self._kdc.is_connected() and self._pm.is_connected() and arduino_ok
        self.ui.btnAlignPolariser.setEnabled(hw_ready)
        self.ui.btnStart.setEnabled(
            hw_ready and bool(self.ui.lineProfileName.text().strip())
        )

    def _set_running(self, running: bool) -> None:
        for w in (
            self.ui.gbConnections,
            self.ui.gbBeam,
            self.ui.gbAlignment,
            self.ui.gbSweep,
            self.ui.gbProfile,
            self.ui.btnStart,
        ):
            w.setEnabled(not running)
        self.ui.btnAbort.setEnabled(running)
        if not running:
            self._update_start_button_state()

    def _persist_settings(self) -> None:
        conn_id = self.ui.comboKDC.currentData() or self.ui.comboKDC.currentText()
        self._settings = AutoCalibrationConnectionSettings(
            kdc101_conn_id=conn_id or "",
            pm400_visa_resource=self.ui.comboPM400.currentText().strip(),
            beamsplitter_attenuation_dB=self.ui.spinAttenuation.value(),
            wavelength_nm=self.ui.spinWavelength.value(),
            angle_offset_deg=self._angle_offset_deg,
        )
        try:
            self._settings.save()
        except Exception as exc:
            Debug.warning(f"AutoPowerCalibrationWindow: could not save settings: {exc}")

    # ── Qt lifecycle ──────────────────────────────────────────────────────────

    def closeEvent(self, event) -> None:
        if self._align_worker is not None and self._align_worker.isRunning():
            self._align_worker.abort()
            self._align_worker.wait(5000)
        if self._worker is not None and self._worker.isRunning():
            self._worker.abort()
            self._worker.wait(5000)
            if self._data_controller is not None:
                self._data_controller.start_continuous_reading()
        if self._home_thread is not None and self._home_thread.isRunning():
            self._home_thread.wait(3000)
        self._kdc.disconnect()
        self._pm.disconnect()
        if self._standalone and self._device_manager is not None:
            self._device_manager.disconnect_all()
        self._persist_settings()
        super().closeEvent(event)
