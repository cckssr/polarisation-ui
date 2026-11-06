"""Main window of the Goniometer Polarisation UI.

A thin shell around the Designer form ``mainwindow.ui``: it builds the :class:`AppContext`
(controllers), maps controller signals to widget updates and widget signals to controller slots,
hosts the experiment tabs and opens the auxiliary windows. All device handling, state and
business logic live in ``polarisation_ui/ui/controllers/``.
"""

from __future__ import annotations

import math
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QFileDialog,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QWidget,
)

from polarisation_ui.core.detector import DETECTOR_PDTIA, DETECTOR_PM400
from polarisation_ui.core.formatting import fmt_angle, fmt_stat
from polarisation_ui.core.models import AcquisitionSettings
from polarisation_ui.infrastructure.config import AppConfig, default_config
from polarisation_ui.infrastructure.logging import Debug
from polarisation_ui.pyqt.ui_mainwindow import Ui_MainWindow
from polarisation_ui.ui.common.dialogs import show_error
from polarisation_ui.ui.common.pm400_combo import populate_pm400_combo
from polarisation_ui.ui.common.status_led import (
    LED_GREEN,
    LED_RED,
    LED_YELLOW,
    set_connection_status,
)
from polarisation_ui.ui.common.statusbar import StatusBarManager
from polarisation_ui.ui.context import AppContext
from polarisation_ui.ui.controllers.detector_controller import DARK_TARE_SAMPLES
from polarisation_ui.ui.controllers.status import (
    LED_BUSY,
    LED_ERROR,
    LED_OFF,
    LED_OK,
    LED_WARN,
    ROW_ARDUINO,
    ROW_DETECTOR,
    ROW_DETECTOR_STAGE,
    ROW_SAMPLE,
)
from polarisation_ui.ui.dialogs.acq_settings import AcquisitionSettingsDialog
from polarisation_ui.ui.i18n import apply_strings
from polarisation_ui.ui.widgets.tab_host import TabHost
from polarisation_ui.ui.windows.encoder_debug_window import EncoderDebugDialog

_LED_STYLES = {
    LED_OK: LED_GREEN,
    LED_BUSY: LED_YELLOW,
    LED_WARN: LED_YELLOW,
    LED_ERROR: LED_RED,
    LED_OFF: LED_RED,
}
_GAIN_STAGES = (1, 2, 3, 4)


class MainWindow(QMainWindow):
    """Main window: Designer form + controller wiring.

    ``simulate=True`` runs the whole bench on the mocks of ``SimulatedBench`` (no hardware).
    ``persist=False`` reads and writes no user files (session state, orphan journals) — for tests.
    """

    def __init__(
        self,
        config: AppConfig | None = None,
        simulate: bool = False,
        persist: bool = True,
        parent: QWidget | None = None,
    ) -> None:
        """Build the form, the controllers and the tabs, then wire everything."""
        super().__init__(parent)
        self.config: AppConfig = config if config is not None else default_config()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        apply_strings(self, self.config.section("ui").get("mainwindow", {}))

        self.ctx = AppContext.create(self.config, simulate=simulate, persist=persist, parent=self)
        self.statusbar_manager = StatusBarManager(self.ui.statusBar)
        # Mirror every status-bar message to the event log panel
        self.statusbar_manager.set_mirror(self.ui.eventLogPanel)
        self.tabs = TabHost(self.ui.tabWidget, self.config, self.ctx.data, self)
        self._gain_button_group_2 = QButtonGroup(self)
        self._status_rows = {
            ROW_ARDUINO: (self.ui.ledArduinoStatus, self.ui.lblArduinoStatusValue),
            ROW_SAMPLE: (self.ui.ledSampleStatus, self.ui.lblSampleStatusValue),
            ROW_DETECTOR_STAGE: (
                self.ui.ledDetectorStageStatus,
                self.ui.lblDetectorStageStatusValue,
            ),
            ROW_DETECTOR: (self.ui.ledDetectorStatus, self.ui.lblDetectorStatusValue),
        }

        self._connect_status()
        self._connect_connection()
        self._connect_kdc()
        self._connect_pm400()
        self._connect_detector()
        self._connect_measurement()
        self._connect_session()
        self._connect_menu()

        self._setup_initial_widget_state()
        self.tabs.build()
        self._connect_tabs()
        self._publish_initial_state()

        if persist:
            # Defer until the event loop runs so the window is shown before any modal dialog
            # appears — otherwise the port combo ends up in a broken state on macOS.
            QTimer.singleShot(0, self._run_startup_checks)
        Debug.info("MainWindow initialized with Qt Designer UI")

    # ==================== Text helpers ====================

    def _t(self, key: str, **fmt: object) -> str:
        return self.config.text(f"mainwindow.{key}", **fmt)

    def _m(self, key: str, **fmt: object) -> str:
        return self.config.message(key, **fmt)

    # ==================== Wiring ====================

    def _connect_status(self) -> None:
        self.ctx.status.message.connect(self._show_status)
        self.ctx.connection.row_state_changed.connect(self._show_row)
        self.ctx.detector.row_state_changed.connect(self._show_row)

    def _connect_connection(self) -> None:
        conn = self.ctx.connection
        conn.ports_changed.connect(self._fill_ports)
        conn.connected_changed.connect(self._on_arduino_connected_changed)
        conn.connecting_changed.connect(self._on_arduino_connecting_changed)
        conn.ready.connect(self._apply_required_stream_sources)
        conn.zero_failed.connect(lambda title, text: show_error(self, title, text))
        conn.lost.connect(self._offer_partial_export)
        self.ui.btnRefreshPorts.clicked.connect(conn.refresh_ports)
        self.ui.btnArduinoConnect.clicked.connect(self._on_arduino_button)
        self.ui.btnSampleZero.clicked.connect(conn.zero_sample)
        self.ui.btnDetectorStageZero.clicked.connect(conn.zero_detector)
        self.ui.btnDetectorStage180.clicked.connect(conn.zero_detector_at_180)

        data = self.ctx.data
        data.angles_updated.connect(self._update_angle_displays)
        data.intensity_updated.connect(self._update_intensity_display)

    def _connect_kdc(self) -> None:
        kdc = self.ctx.kdc
        kdc.devices_changed.connect(self._fill_kdc_devices)
        kdc.state_changed.connect(self._show_kdc_state)
        kdc.connected_changed.connect(self._on_kdc_connected_changed)
        kdc.controls_changed.connect(self._set_kdc_controls)
        kdc.position_changed.connect(self._show_kdc_position)
        kdc.offset_changed.connect(self._show_kdc_offset)
        kdc.notice.connect(lambda title, text: QMessageBox.warning(self, title, text))
        self.ui.btnKDCRefresh.clicked.connect(kdc.refresh_devices)
        self.ui.btnKDCConnect.clicked.connect(self._on_kdc_button)
        self.ui.btnKDCHome.clicked.connect(kdc.home)
        self.ui.btnKDCZero.clicked.connect(kdc.start_zero_find)
        self.ui.btnKDCOffsetReset.clicked.connect(kdc.reset_offset)

    def _connect_pm400(self) -> None:
        pm = self.ctx.pm400
        pm.resources_changed.connect(self._fill_pm400_resources)
        pm.resource_selected.connect(self._select_pm400_resource)
        pm.wavelength_changed.connect(self._show_pm400_wavelength)
        pm.state_changed.connect(self._show_pm400_state)
        pm.connected_changed.connect(self._on_pm400_connected_changed)
        pm.notice.connect(lambda title, text: QMessageBox.warning(self, title, text))
        self.ui.btnRefreshPM400.clicked.connect(pm.refresh_resources)
        self.ui.btnConnectPM400.clicked.connect(self._on_pm400_button)
        self.ui.btnZeroPM400.clicked.connect(pm.zero)
        self.ui.spbPM400Wavelength.valueChanged.connect(pm.set_wavelength)
        self.ui.comboPM400.currentTextChanged.connect(pm.set_resource)

    def _connect_detector(self) -> None:
        det = self.ctx.detector
        det.gain_changed.connect(self._sync_gain_visual)
        det.gain_cleared.connect(self._clear_gain_visual)
        det.gain_auto_changed.connect(self._sync_gain_auto_visual)
        det.active_detector_changed.connect(self._set_active_detector)
        det.profile_changed.connect(self._on_profile_changed)
        det.pdtia_id_changed.connect(self._sync_pdtia_combo)
        det.dark_tare_busy.connect(self._on_dark_tare_busy)
        det.dark_offset_changed.connect(self._show_dark_offset)
        self.ctx.data.power_updated.connect(self._update_wattage_display)

        # PD-TIA gain: both button groups use the stage numbers as ids
        for stage in _GAIN_STAGES:
            self.ui.gainButtonGroup.setId(getattr(self.ui, f"btnGain{stage}"), stage)
            self._gain_button_group_2.addButton(getattr(self.ui, f"btnGain{stage}_2"), stage)
        self.ui.gainButtonGroup.idClicked.connect(det.select_gain)
        self._gain_button_group_2.idClicked.connect(det.select_gain)
        if not det.gain_auto_available:
            tooltip = self._t("gain_auto_no_limits")
            for btn in (self.ui.btnGainA, self.ui.btnGainA_2):
                btn.setEnabled(False)
                btn.setToolTip(tooltip)
        self.ui.btnGainA.toggled.connect(det.set_gain_auto)
        self.ui.btnGainA_2.toggled.connect(det.set_gain_auto)

        self.ui.cbPdtiaID.currentIndexChanged.connect(self._on_pdtia_combo_changed)
        self.ui.cbProfile.currentIndexChanged.connect(self._on_profile_combo_changed)
        self.ui.btnReloadProfiles.clicked.connect(self._reload_profiles)
        self.ui.btnOpenCalibration.clicked.connect(self._open_power_calibration)
        self.ui.btnDarkTare.clicked.connect(self._on_dark_tare_clicked)
        self.ui.btnDarkReset.clicked.connect(det.reset_dark_offset)

    def _connect_measurement(self) -> None:
        meas = self.ctx.measurement
        meas.started.connect(self._on_measurement_started)
        meas.stopped.connect(self._on_measurement_stopped)
        meas.reset_performed.connect(self._on_measurement_reset)
        meas.group_changed.connect(self._on_group_changed)
        meas.team_changed.connect(lambda text: self._sync_line_edit(self.ui.leTeamName, text))
        meas.suffix_changed.connect(lambda text: self._sync_line_edit(self.ui.leSuffix, text))
        meas.team_changed.connect(self._update_filename_display)
        meas.suffix_changed.connect(self._update_filename_display)
        meas.prefix_locked_changed.connect(self._on_prefix_locked)
        meas.acq_settings_replaced.connect(self._sync_inline_acq_controls)

        self.ui.btnStartMeasurement.clicked.connect(meas.start)
        self.ui.btnStopMeasurement.clicked.connect(meas.stop)
        self.ui.btnResetMeasurement.clicked.connect(meas.reset)
        self.ui.btnSave.clicked.connect(self._save_data)
        self.ui.cbGroupLetter.currentIndexChanged.connect(self._on_group_combo_changed)
        self.ui.leSuffix.textChanged.connect(meas.set_suffix)
        self.ui.leTeamName.textChanged.connect(meas.set_team)

        # Inline averaging controls (configuration tab)
        for check, spin in (
            (self.ui.cbSampleAverageOn, self.ui.spbSampleAverages),
            (self.ui.cbDetectorAverageOn, self.ui.spbDetectorAverages),
            (self.ui.cbPdtiaAveragesOn, self.ui.spbPdtiaAverages),
        ):
            check.toggled.connect(spin.setEnabled)
            check.toggled.connect(self._on_acq_inline_changed)
            spin.valueChanged.connect(self._on_acq_inline_changed)

    def _connect_session(self) -> None:
        session = self.ctx.session
        session.set_tab_points_provider(self.tabs.saved_points)
        session.tab_points_restored.connect(self.tabs.restore_points)

    def _connect_tabs(self) -> None:
        tabs = self.tabs
        ctx = self.ctx
        tabs.status_message.connect(self._show_status)
        tabs.filename_hint_changed.connect(self._update_filename_display)
        tabs.points_changed.connect(self._on_tab_points_changed)
        tabs.points_changed.connect(lambda _count: ctx.session.schedule_save())
        tabs.active_tab_changed.connect(self._on_active_tab_changed)
        tabs.sources_changed.connect(self._apply_required_stream_sources)
        ctx.kdc.modules_changed.connect(tabs.refresh_visibility)
        ctx.pm400.modules_changed.connect(tabs.refresh_visibility)
        ctx.connection.link_state_changed.connect(tabs.notify_link_state)
        ctx.measurement.started.connect(tabs.on_measurement_started)
        ctx.measurement.stopped.connect(tabs.on_measurement_stopped)
        ctx.measurement.reset_performed.connect(tabs.reset_all)

    def _connect_menu(self) -> None:
        self.ui.actionAcquisitionSettings.triggered.connect(self._open_acq_settings)
        self.ui.actionEncoderDebug.triggered.connect(self._open_encoder_debug)
        self.ui.actionLogWindow.triggered.connect(self._open_log_window)
        self.ui.actionEventLog.toggled.connect(self.ui.dockEventLog.setVisible)
        self.ui.dockEventLog.visibilityChanged.connect(self.ui.actionEventLog.setChecked)
        self.ui.actionPowerCalibration.triggered.connect(self._open_power_calibration)
        self.ui.actionAutoPowerCalibration.triggered.connect(self._open_auto_power_calibration)
        self._log_window: QDialog | None = None

    # ==================== Initial state ====================

    def _setup_initial_widget_state(self) -> None:
        """Widgets start disconnected; the controllers then publish their own initial state."""
        self.ui.lblDropbox.setOpenExternalLinks(True)
        self.ui.gbSampleStage.setEnabled(False)
        self.ui.gbDetectorStage.setEnabled(False)
        self.ui.tabDetector.setEnabled(False)
        for button in (
            self.ui.btnStartMeasurement,
            self.ui.btnStopMeasurement,
            self.ui.btnResetMeasurement,
            self.ui.btnSave,
            self.ui.btnZeroPM400,
        ):
            button.setEnabled(False)
        self.ui.btnArduinoConnect.setText(self._t("button_connect"))
        self.ui.btnKDCConnect.setText(self._t("button_connect"))
        self.ui.btnConnectPM400.setText(self._t("button_connect"))
        self.ui.lblKDCPositionValue.setText(self._t("value_none"))

        det = self.ctx.detector
        combo = self.ui.cbPdtiaID
        combo.blockSignals(True)
        combo.clear()
        combo.addItems(det.pdtia_ids)
        combo.blockSignals(False)
        det.init_pdtia_id(combo.currentText())
        self._set_active_detector(DETECTOR_PDTIA)
        self._sync_inline_acq_controls(self.ctx.measurement.acq_settings)

    def _publish_initial_state(self) -> None:
        ctx = self.ctx
        ctx.connection.publish_state()
        ctx.kdc.publish_state()
        ctx.pm400.publish_state()
        self._reload_profiles()
        # Apply the initial group state (the selector starts empty: experiment tabs locked)
        self._on_group_changed(ctx.measurement.group_letter)

    # ==================== Status ====================

    @Slot(str, str)
    def _show_status(self, level: str, text: str) -> None:
        bar = self.statusbar_manager
        if level == "success":
            bar.show_success(text)
        elif level == "warning":
            bar.show_warning(text)
        elif level == "error":
            bar.show_error(text)
        else:
            bar.show_info(text)

    @Slot(str, str, str)
    def _show_row(self, row: str, led: str, text: str) -> None:
        led_widget, label = self._status_rows[row]
        set_connection_status(led_widget, label, text, _LED_STYLES[led])

    # ==================== Arduino connection ====================

    @Slot(list)
    def _fill_ports(self, ports: list[str]) -> None:
        self.ui.cbArduinoPort.clear()
        for port in ports:
            self.ui.cbArduinoPort.addItem(port)
        if not ports:
            self.ui.cbArduinoPort.addItem(self.ctx.connection.ports_missing_text)

    @Slot()
    def _on_arduino_button(self) -> None:
        if self.ctx.connection.is_connected:
            self.ctx.connection.disconnect_port()
        else:
            combo = self.ui.cbArduinoPort
            self.ctx.connection.connect_port(combo.itemText(combo.currentIndex()))

    @Slot(bool)
    def _on_arduino_connecting_changed(self, connecting: bool) -> None:
        self.ui.cbArduinoPort.setEnabled(not connecting)
        self.ui.btnRefreshPorts.setEnabled(not connecting)

    @Slot(bool)
    def _on_arduino_connected_changed(self, connected: bool) -> None:
        self.ui.gbSampleStage.setEnabled(connected)
        self.ui.gbDetectorStage.setEnabled(connected)
        self.ui.tabDetector.setEnabled(connected)
        self.ui.btnStartMeasurement.setEnabled(connected)
        self.ui.btnArduinoConnect.setText(
            self._t("button_disconnect" if connected else "button_connect")
        )
        if connected:
            for lcd in (
                self.ui.lcdSampleAngle,
                self.ui.lcdDetectorStageAngle,
                self.ui.lcdDetectorVoltage_mV,
                self.ui.lcdDetectorPower,
                self.ui.lcdSampleAngle_2,
                self.ui.lcdDetectorStageAngle_2,
                self.ui.lcdDetectorVoltage_2,
                self.ui.lcdDetectorPower_2,
            ):
                lcd.display(0.00)

    @Slot()
    def _apply_required_stream_sources(self) -> None:
        """Keep ``CONF:SRC`` at the union of the visible tabs' required sources."""
        self.ctx.connection.set_stream_sources(self.tabs.required_sources())

    # ==================== Live displays ====================

    @Slot(float, float)
    def _update_angle_displays(self, sample_angle: float, detector_angle: float) -> None:
        # Values from the DataController are already averaged — always display. The LED colour
        # already indicates sensor health; freezing the value on a fault is more confusing.
        self.ui.lcdSampleAngle.display(fmt_angle(sample_angle))
        self.ui.lcdDetectorStageAngle.display(fmt_angle(detector_angle))
        self.ui.lcdSampleAngle_2.display(fmt_angle(sample_angle))
        self.ui.lcdDetectorStageAngle_2.display(fmt_angle(detector_angle))

    @Slot(float)
    def _update_intensity_display(self, voltage: float) -> None:
        if math.isnan(voltage):
            text = "----"
        else:
            text = fmt_stat(voltage * 1000.0)
        self.ui.lcdDetectorVoltage_mV.display(text)
        self.ui.lcdDetectorVoltage_2.display(text)

    @Slot(float)
    def _update_wattage_display(self, power_W: float) -> None:
        """Update the power LCDs from the active detector.

        The sidebar ``lcdDetectorPower`` always tracks the active detector;
        ``lcdDetectorPower_2`` (PD-TIA tab) and ``lcdPM400Power`` (PM400 tab) only receive updates
        while their own detector is active — the other stays frozen at its last value.
        """
        pm400_active = self.ctx.data.is_pm400_active
        target = self.ui.lcdPM400Power if pm400_active else self.ui.lcdDetectorPower_2
        if math.isnan(power_W):
            text = "----"
        else:
            text = fmt_stat(power_W * 1e6)
        self.ui.lcdDetectorPower.display(text)
        target.display(text)

    # ==================== KDC101 ====================

    @Slot(list)
    def _fill_kdc_devices(self, devices: list[tuple[str, str]]) -> None:
        combo = self.ui.cbKDCDevice
        current = combo.currentText()
        combo.clear()
        for conn_id, desc in devices:
            combo.addItem(f"{conn_id} — {desc}", userData=conn_id)
        if not devices:
            combo.addItem(self._t("kdc_none_found"))
        if current:
            idx = combo.findText(current)
            if idx >= 0:
                combo.setCurrentIndex(idx)

    @Slot()
    def _on_kdc_button(self) -> None:
        if self.ctx.kdc.is_connected:
            self.ctx.kdc.disconnect_device()
        else:
            self.ctx.kdc.connect_device(self.ui.cbKDCDevice.currentData())

    @Slot(str, str)
    def _show_kdc_state(self, led: str, text: str) -> None:
        set_connection_status(
            self.ui.ledKDCStatus, self.ui.lblKDCStatusValue, text, _LED_STYLES[led]
        )

    @Slot(bool)
    def _on_kdc_connected_changed(self, connected: bool) -> None:
        self.ui.btnKDCConnect.setText(
            self._t("button_disconnect" if connected else "button_connect")
        )

    @Slot(bool, bool, bool, bool)
    def _set_kdc_controls(self, connect: bool, home: bool, zero: bool, reset: bool) -> None:
        self.ui.btnKDCConnect.setEnabled(connect)
        self.ui.btnKDCHome.setEnabled(home)
        self.ui.btnKDCZero.setEnabled(zero)
        self.ui.btnKDCOffsetReset.setEnabled(reset)

    @Slot(object)
    def _show_kdc_position(self, position: float | None) -> None:
        self.ui.lblKDCPositionValue.setText(
            self._t("value_none") if position is None else f"{fmt_angle(position)}°"
        )

    @Slot(float)
    def _show_kdc_offset(self, offset: float) -> None:
        self.ui.lblKDCOffsetValue.setText(
            self._t("value_none") if offset == 0.0 else f"{fmt_angle(offset)}°"
        )

    # ==================== PM400 ====================

    @Slot(list)
    def _fill_pm400_resources(self, resources: list[str]) -> None:
        populate_pm400_combo(
            self.ui.comboPM400, self.ctx.pm400.preferred_resource, self.config, resources
        )

    @Slot(str)
    def _select_pm400_resource(self, resource: str) -> None:
        idx = self.ui.comboPM400.findText(resource)
        if idx >= 0:
            self.ui.comboPM400.setCurrentIndex(idx)

    @Slot(float)
    def _show_pm400_wavelength(self, nm: float) -> None:
        spin = self.ui.spbPM400Wavelength
        if spin.value() != nm:
            spin.blockSignals(True)
            spin.setValue(nm)
            spin.blockSignals(False)

    @Slot()
    def _on_pm400_button(self) -> None:
        if self.ctx.pm400.is_connected:
            self.ctx.pm400.disconnect_device()
        else:
            self.ctx.pm400.connect_resource(self.ui.comboPM400.currentText())

    @Slot(str, str)
    def _show_pm400_state(self, led: str, text: str) -> None:
        set_connection_status(
            self.ui.ledPM400Status, self.ui.lblPM400Status, text, _LED_STYLES[led]
        )

    @Slot(bool)
    def _on_pm400_connected_changed(self, connected: bool) -> None:
        self.ui.btnConnectPM400.setText(
            self._t("button_disconnect" if connected else "button_connect")
        )
        self.ui.btnZeroPM400.setEnabled(connected)

    # ==================== Detector: gain, profile, dark tare ====================

    @Slot(str)
    def _set_active_detector(self, source: str) -> None:
        """Apply every UI consequence of ``source`` becoming the active detector.

        The PD-TIA configuration (device ID, calibration profile, averaging, dark tare) stays
        interactive either way — only the gain buttons and the PD-TIA-tab power readout, which are
        meaningless once the PM400 has replaced the photodiode, go inert.
        """
        pm400_active = source == DETECTOR_PM400
        self.ui.lcdDetectorPower_2.setEnabled(not pm400_active)
        for stage in _GAIN_STAGES:
            getattr(self.ui, f"btnGain{stage}").setEnabled(not pm400_active)
            getattr(self.ui, f"btnGain{stage}_2").setEnabled(not pm400_active)
        # AUTO stays unavailable when the config defines no power windows
        auto_ok = self.ctx.detector.gain_auto_available and not pm400_active
        self.ui.btnGainA.setEnabled(auto_ok)
        self.ui.btnGainA_2.setEnabled(auto_ok)
        if not pm400_active:
            self.ui.lcdPM400Power.display("----")

    @Slot(int)
    def _sync_gain_visual(self, stage: int) -> None:
        """Check the matching button in both gain groups without re-emitting."""
        for grp in (self.ui.gainButtonGroup, self._gain_button_group_2):
            btn = grp.button(stage)
            if btn is not None and not btn.isChecked():
                btn.blockSignals(True)
                btn.setChecked(True)
                btn.blockSignals(False)

    @Slot()
    def _clear_gain_visual(self) -> None:
        for grp in (self.ui.gainButtonGroup, self._gain_button_group_2):
            checked = grp.checkedButton()
            if checked is not None:
                grp.setExclusive(False)
                checked.setChecked(False)
                grp.setExclusive(True)

    @Slot(bool)
    def _sync_gain_auto_visual(self, checked: bool) -> None:
        """Mirror the AUTO state between the main panel and the sidebar button."""
        for btn in (self.ui.btnGainA, self.ui.btnGainA_2):
            if btn.isChecked() != checked:
                btn.blockSignals(True)
                btn.setChecked(checked)
                btn.blockSignals(False)

    @Slot()
    def _reload_profiles(self) -> None:
        """Refill the profile selector from the profiles directory and re-select the profile."""
        cb = self.ui.cbProfile
        cb.blockSignals(True)
        current_name = cb.currentText() or self.ctx.detector.profile_name
        cb.clear()
        for path in self.ctx.detector.list_profiles():
            cb.addItem(path.stem, userData=path)
        idx = cb.findText(current_name)
        if idx >= 0:
            cb.setCurrentIndex(idx)
        cb.blockSignals(False)
        self._on_profile_combo_changed(cb.currentIndex())

    @Slot(int)
    def _on_profile_combo_changed(self, index: int) -> None:
        path: Path | None = self.ui.cbProfile.itemData(index) if index >= 0 else None
        self.ctx.detector.select_profile(path)

    @Slot(str)
    def _on_profile_changed(self, name: str) -> None:
        cb = self.ui.cbProfile
        idx = cb.findText(name) if name else -1
        if idx != cb.currentIndex():
            cb.blockSignals(True)
            cb.setCurrentIndex(idx)
            cb.blockSignals(False)
        self._update_filename_display()

    @Slot(int)
    def _on_pdtia_combo_changed(self, _index: int) -> None:
        self.ctx.detector.set_pdtia_id(self.ui.cbPdtiaID.currentText())

    @Slot(str)
    def _sync_pdtia_combo(self, device_id: str) -> None:
        cb = self.ui.cbPdtiaID
        idx = cb.findText(device_id)
        if idx >= 0 and idx != cb.currentIndex():
            cb.blockSignals(True)
            cb.setCurrentIndex(idx)
            cb.blockSignals(False)

    @Slot()
    def _on_dark_tare_clicked(self) -> None:
        reply = QMessageBox.question(
            self,
            self._m("detector.dark_tare_title"),
            self._m("detector.dark_tare_text", count=DARK_TARE_SAMPLES),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.ctx.detector.start_dark_tare()

    @Slot(bool)
    def _on_dark_tare_busy(self, busy: bool) -> None:
        self.ui.btnDarkTare.setEnabled(not busy)
        self.ui.btnDarkReset.setEnabled(not busy)

    @Slot(float)
    def _show_dark_offset(self, offset_V: float) -> None:
        if offset_V == 0.0:
            self.ui.lblDarkOffsetValue.setText(self._t("dark_offset_none"))
        else:
            self.ui.lblDarkOffsetValue.setText(
                self._t("dark_offset_value", offset_mV=offset_V * 1000.0)
            )

    # ==================== Acquisition settings ====================

    @Slot()
    def _on_acq_inline_changed(self) -> None:
        """Build the settings from the inline controls (spike filter etc. stay unchanged)."""
        current = self.ctx.measurement.acq_settings
        self.ctx.measurement.set_acq_settings_inline(
            AcquisitionSettings(
                samp_average_on=self.ui.cbSampleAverageOn.isChecked(),
                samp_averages=self.ui.spbSampleAverages.value(),
                det_average_on=self.ui.cbDetectorAverageOn.isChecked(),
                det_averages=self.ui.spbDetectorAverages.value(),
                pdtia_average_on=self.ui.cbPdtiaAveragesOn.isChecked(),
                pdtia_averages=self.ui.spbPdtiaAverages.value(),
                sample_stage_inverted=current.sample_stage_inverted,
                spike_filter_enabled=current.spike_filter_enabled,
                spike_max_delta_deg=current.spike_max_delta_deg,
            )
        )

    @Slot(object)
    def _sync_inline_acq_controls(self, settings: AcquisitionSettings) -> None:
        """Push ``settings`` to the inline controls without re-emitting their signals."""
        pairs = (
            (
                self.ui.cbSampleAverageOn,
                self.ui.spbSampleAverages,
                "samp_average_on",
                "samp_averages",
            ),
            (
                self.ui.cbDetectorAverageOn,
                self.ui.spbDetectorAverages,
                "det_average_on",
                "det_averages",
            ),
            (
                self.ui.cbPdtiaAveragesOn,
                self.ui.spbPdtiaAverages,
                "pdtia_average_on",
                "pdtia_averages",
            ),
        )
        for check, spin, on_key, count_key in pairs:
            check.blockSignals(True)
            spin.blockSignals(True)
            check.setChecked(getattr(settings, on_key))
            spin.setValue(getattr(settings, count_key))
            spin.setEnabled(getattr(settings, on_key))
            check.blockSignals(False)
            spin.blockSignals(False)

    @Slot()
    def _open_acq_settings(self) -> None:
        """Open the acquisition settings dialog (spike filter + inversion settings)."""
        dialog = AcquisitionSettingsDialog(
            self.ctx.measurement.acq_settings, parent=self, config=self.config
        )
        # Without this the dialog's C++ object stays parented to the main window forever (Qt only
        # auto-deletes on close), so re-opening would leak one QDialog per open.
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        # exec() makes the dialog application-modal; setEnabled(False) is NOT used because it
        # propagates to child QObjects and would disable the dialog itself.
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.ctx.measurement.replace_acq_settings(dialog.get_settings())

    # ==================== Group / filename / save ====================

    @Slot(int)
    def _on_group_combo_changed(self, index: int) -> None:
        combo = self.ui.cbGroupLetter
        self.ctx.measurement.set_group(combo.itemText(index) if index >= 0 else "")

    @Slot(str)
    def _on_group_changed(self, letter: str) -> None:
        combo = self.ui.cbGroupLetter
        idx = combo.findText(letter) if letter else -1
        if idx != combo.currentIndex():
            combo.blockSignals(True)
            combo.setCurrentIndex(idx)
            combo.blockSignals(False)
        self.tabs.set_group_selected(bool(letter))
        self._update_filename_display()

    @staticmethod
    def _sync_line_edit(edit: QLineEdit, text: str) -> None:
        """Set ``edit`` to ``text`` unless it already shows it (ignoring surrounding blanks)."""
        if edit.text().strip() != text:
            edit.blockSignals(True)
            edit.setText(text)
            edit.blockSignals(False)

    @Slot(bool)
    def _on_prefix_locked(self, locked: bool) -> None:
        self.ui.cbGroupLetter.setEnabled(not locked)
        self.ui.leTeamName.setEnabled(not locked)

    @Slot()
    def _update_filename_display(self) -> None:
        """Refresh the expected save path shown for the active tab."""
        meas = self.ctx.measurement
        text = meas.filename_display(self.tabs.active_export()) if meas.group_selected else ""
        self.ui.pteCurrentFilename.setPlainText(text)

    @Slot()
    def _save_data(self) -> None:
        """Export the active tab's saved points to a user-chosen CSV file."""
        tab = self.tabs.active_export_tab()
        title = self._m("save.no_points_title")
        if tab is None or not tab.get_saved_points():
            show_error(self, title, self._m("save.no_points"))
            return
        export = tab.build_export()
        if not export.rows:
            show_error(self, title, self._m("save.no_points"))
            return
        default = self.ctx.measurement.default_save_path(export)
        path, _ = QFileDialog.getSaveFileName(
            self, self._m("save.dialog_title"), str(default), self._m("save.csv_filter")
        )
        if path:
            self.ctx.measurement.save_export(Path(path), export)

    # ==================== Measurement / tabs ====================

    @Slot()
    def _on_measurement_started(self) -> None:
        self.ui.btnStartMeasurement.setEnabled(False)
        self.ui.btnStopMeasurement.setEnabled(True)
        self.ui.btnResetMeasurement.setEnabled(False)
        self.ui.btnSave.setEnabled(False)
        # No zeroing and no tab switching during a run
        self.ui.btnSampleZero.setEnabled(False)
        self.ui.btnDetectorStageZero.setEnabled(False)
        self.ui.btnDetectorStage180.setEnabled(False)
        self.ui.tabWidget.tabBar().setEnabled(False)

    @Slot()
    def _on_measurement_stopped(self) -> None:
        self.ui.btnStartMeasurement.setEnabled(True)
        self.ui.btnStopMeasurement.setEnabled(False)
        self.ui.btnResetMeasurement.setEnabled(True)
        self.ui.btnSampleZero.setEnabled(True)
        self.ui.btnDetectorStageZero.setEnabled(True)
        self.ui.btnDetectorStage180.setEnabled(True)
        self.ui.tabWidget.tabBar().setEnabled(True)
        self._sync_save_button()

    @Slot()
    def _on_measurement_reset(self) -> None:
        self.ui.btnResetMeasurement.setEnabled(False)

    @Slot(int)
    def _on_tab_points_changed(self, _count: int) -> None:
        if not self.ctx.measurement.is_measuring:
            self._sync_save_button()

    @Slot()
    def _on_active_tab_changed(self) -> None:
        if not self.ctx.measurement.is_measuring:
            self._sync_save_button()
        self._update_filename_display()

    def _sync_save_button(self) -> None:
        """Enable Save iff the active tab has saved points."""
        self.ui.btnSave.setEnabled(self.tabs.active_tab_has_points())

    # ==================== Auxiliary windows ====================

    def _open_power_calibration(self) -> None:
        from polarisation_ui.ui.windows.power_calibration_window import PowerCalibrationWindow

        dialog = PowerCalibrationWindow(
            data_controller=self.ctx.data,
            pm400=self.ctx.pm400.pm400,
            parent=self,
            config=self.config,
        )
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        dialog.profile_saved.connect(self._reload_profiles)
        dialog.show()

    def _open_auto_power_calibration(self) -> None:
        from polarisation_ui.ui.windows.auto_power_calibration_window import (
            AutoPowerCalibrationWindow,
        )

        dialog = AutoPowerCalibrationWindow(
            data_controller=self.ctx.data,
            pm400=self.ctx.pm400.pm400,
            parent=self,
            config=self.config,
        )
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        dialog.profile_saved.connect(self._reload_profiles)
        dialog.show()

    @Slot()
    def _open_encoder_debug(self) -> None:
        """Open the encoder debug dialog (non-modal)."""
        dialog = EncoderDebugDialog(
            self.ctx.connection.device_manager,
            sample_inverted=self.ctx.measurement.acq_settings.sample_stage_inverted,
            data_controller=self.ctx.data,
            pm400=self.ctx.pm400.pm400,
            parent=self,
            config=self.config,
        )
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        dialog.show()

    @Slot()
    def _open_log_window(self) -> None:
        """Open or raise the live log output window."""
        if self._log_window is None:
            from polarisation_ui.ui.windows.log_window import LogWindow

            self._log_window = LogWindow(parent=self, config=self.config)
            self._log_window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            self._log_window.destroyed.connect(self._on_log_window_closed)
        self._log_window.show()
        self._log_window.raise_()
        self._log_window.activateWindow()

    def _on_log_window_closed(self) -> None:
        self._log_window = None

    # ==================== Start-up checks and data recovery ====================

    def _ask(self, title_key: str, text_key: str, **fmt: object) -> bool:
        reply = QMessageBox.question(
            self,
            self._m(title_key),
            self._m(text_key, **fmt),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        return reply == QMessageBox.StandardButton.Yes

    def _csv_target(self, title: str, proposal: Path) -> Path | None:
        path, _ = QFileDialog.getSaveFileName(
            self, title, str(proposal), self._m("save.csv_filter")
        )
        return Path(path) if path else None

    @Slot()
    def _run_startup_checks(self) -> None:
        """Offer to export unfinished journals, then to restore today's session."""
        session = self.ctx.session
        orphans = session.find_orphans()
        if orphans:
            if self._ask("session.orphans_title", "session.orphans_text", count=len(orphans)):
                for session_dir in orphans:
                    target = self._csv_target(
                        self._m("session.orphan_export_title", name=session_dir.name),
                        Path.home() / f"recovery_{session_dir.name}.csv",
                    )
                    if target is not None:
                        session.export_orphan(session_dir, target)
            else:
                # Dismissed: delete them so they do not reappear on the next launch.
                session.discard_orphans(orphans)

        state = session.restorable_state()
        session.arm()
        if state is not None and self._ask("session.restore_title", "session.restore_text"):
            session.restore(state)

    @Slot()
    def _offer_partial_export(self) -> None:
        """After a permanent connection loss: offer to export the data recorded so far."""
        journal = self.ctx.session.partial_journal()
        if journal is None:
            return
        if not self._ask("session.lost_title", "session.lost_text", count=journal.row_count):
            return
        target = self._csv_target(
            self._m("session.partial_export_title"), Path.home() / "messung_partial.csv"
        )
        if target is not None:
            self.ctx.session.export_partial(journal, target)

    # ==================== Window lifecycle ====================

    def closeEvent(self, event: QCloseEvent) -> None:
        """Stop measurement and polling, close all devices."""
        Debug.info("Closing application...")
        self.ctx.shutdown()
        event.accept()
