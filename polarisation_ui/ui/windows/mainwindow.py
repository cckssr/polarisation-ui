"""Main Window for Goniometer Polarisation UI.

Uses Qt Designer UI (ui_mainwindow.py) and integrates with the 3-layer architecture:
    - UI Layer: This window and Qt Designer UI
    - Infrastructure: Device manager, config, logging
    - Core: Services and business logic

Responsibilities:
    - Load and setup Qt Designer UI
    - Connect UI elements to functionality
    - Handle user interactions via signals/slots
    - Update live displays with encoder readings
    - Manage measurement sessions
    - Status indicators (LEDs)
"""

import math
import shutil
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QMainWindow,
    QMessageBox,
)

from polarisation_ui.core.exceptions import KDC101Error
from polarisation_ui.core.models import AcquisitionSettings
from polarisation_ui.core.power_calibration import PowerCalibrationProfile
from polarisation_ui.infrastructure.config import import_config
from polarisation_ui.infrastructure.device_manager import GoniometerDeviceManager
from polarisation_ui.infrastructure.devices.kdc101_polariser import KDC101Polariser
from polarisation_ui.infrastructure.logging import Debug
from polarisation_ui.infrastructure.modules import ModuleRegistry
from polarisation_ui.infrastructure.modules.kdc101_adapter import KDC101ModuleAdapter
from polarisation_ui.infrastructure.qt_threads import KDC101HomeWorker
from polarisation_ui.infrastructure.save_service import (
    compose_filename,
    save_tab_export,
)
from polarisation_ui.infrastructure.utils import (
    create_dropbox_foldername,
    sanitize_subterm_for_folder,
)
from polarisation_ui.infrastructure.session_journal import SessionJournal
from polarisation_ui.pyqt.ui_mainwindow import Ui_MainWindow
from polarisation_ui.ui.dialogs.acq_settings import AcquisitionSettingsDialog
from polarisation_ui.ui.common.dialogs import show_error
from polarisation_ui.ui.common.status_led import (
    LED_GREEN,
    LED_RED,
    LED_YELLOW,
    set_connection_status,
)
from polarisation_ui.ui.common.statusbar import StatusBarManager
from polarisation_ui.ui.controllers.data_controller import DataController
from polarisation_ui.ui.widgets.plot_tab_base import ConnState, PlotTabBase
from polarisation_ui.ui.widgets.tab_registry import TabRegistry
from polarisation_ui.ui.windows.encoder_debug_window import EncoderDebugDialog

CONFIG = import_config()

# ADC saturation thresholds (ADS1220, PGA=1, Vref=2.048V)
_ADC_SAT_LOW = 0.02  # V — near GND
_ADC_SAT_HIGH = 2.0  # V — near rail


class MainWindow(QMainWindow):
    """Main window of the Goniometer Polarisation UI.

    Uses Qt Designer UI and provides:
        - Live encoder readings display (LCD)
        - Encoder zeroing controls
        - Measurement start/stop/reset
        - Data saving functionality
        - Status indicators (LEDs)

    Architecture:
        - Uses pre-designed UI from ui_mainwindow.py
        - Delegates hardware operations to device manager
        - Delegates data acquisition to data controller
        - Follows 3-layer separation
    """

    def __init__(self, device_manager: GoniometerDeviceManager, parent=None):
        """Initialize main window.

        Args:
            device_manager: Connected device manager instance
            parent: Parent widget
        """
        super().__init__(parent)

        # Setup Qt Designer UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Store device manager
        self.device_manager = device_manager

        # Initialisation
        self.data_controller = DataController(self.device_manager, self)
        self.statusbar_manager = StatusBarManager(self.ui.statusBar)
        self._is_measuring = False
        self._is_connected = False
        self._adc_saturated = False  # tracks last saturation state to avoid LED flicker

        # Mirror every status-bar message to the event log panel
        self.statusbar_manager.set_mirror(self.ui.eventLogPanel)

        self._acq_settings: AcquisitionSettings = self._load_acq_settings_from_config()

        self._sensor_a_ok: bool = True
        self._sensor_b_ok: bool = True
        self._tab_instances: list[PlotTabBase] = []

        # Log window — created lazily on first open, reused thereafter
        self._log_window = None

        # Power calibration — lazily loaded from selected profile
        self._calibration_profile: Optional[PowerCalibrationProfile] = None

        # KDC101 rotation stage
        self._kdc = KDC101Polariser()
        self._kdc_home_worker: Optional[KDC101HomeWorker] = None
        # 250 ms timer that polls get_position_deg() while the KDC is connected
        self._kdc_position_timer = QTimer(self)
        self._kdc_position_timer.setInterval(250)
        self._kdc_position_timer.timeout.connect(self._refresh_kdc_position)

        self.data_controller.update_acq_settings(self._acq_settings)

        # Setup UI and connections
        self._setup_initial_state()
        self._setup_tabs()
        self._connect_signals()
        # Defer until after the event loop starts so the window is fully shown
        # before any modal dialog appears — otherwise the port combobox ends up
        # in a broken state on macOS.
        QTimer.singleShot(0, self._check_orphan_journals)

        Debug.info("MainWindow initialized with Qt Designer UI")

    # ==================== UI Setup ====================

    def _setup_initial_state(self) -> None:
        """Setup initial UI state (disconnected)."""
        self._populate_ports()
        self.ui.lblDropbox.setOpenExternalLinks(True)

        # Arduino connection group: start disconnected
        self.ui.ledArduinoStatus.setStyleSheet(LED_RED)
        self.ui.lblArduinoStatusValue.setText(
            CONFIG["messages"]["device_not_connected"]
        )

        # Encoder/detector groups disabled until connected
        self.ui.gbSampleStage.setEnabled(False)
        self.ui.gbDetectorStage.setEnabled(False)
        self.ui.gbDetector.setEnabled(False)

        # Measurement controls disabled until connected
        self.ui.btnStartMeasurement.setEnabled(False)
        self.ui.btnStopMeasurement.setEnabled(False)
        self.ui.btnResetMeasurement.setEnabled(False)
        self.ui.btnSave.setEnabled(False)

        self.statusbar_manager.show_info(CONFIG["messages"]["device_please_connect"])

        # KDC101 group: populate device list and set initial state
        self._populate_kdc_devices()
        set_connection_status(
            self.ui.ledKDCStatus,
            self.ui.lblKDCStatusValue,
            "Nicht verbunden",
            LED_RED,
        )
        self.ui.btnKDCHome.setEnabled(False)
        self.ui.lblKDCPositionValue.setText("—")

        # Initialise inline acquisition settings from loaded config
        self._sync_inline_acq_controls()

    def _add_tab(self, tab_cls, modules) -> "PlotTabBase":
        """Instantiate one tab, wire all standard signals, and append it to the widget."""
        tab = tab_cls()
        tab.build()
        tab.status_message.connect(self._handle_tab_status)
        tab.filename_hint_changed.connect(self._update_filename_display)
        if hasattr(tab, "points_changed"):
            tab.points_changed.connect(self._on_tab_points_changed)
        self.data_controller.frame_ready.connect(tab.on_frame)
        self.ui.tabWidget.addTab(tab, tab.tab_title)
        self._tab_instances.append(tab)
        tab.inject_modules(modules)
        return tab

    def _setup_tabs(self) -> None:
        """Instantiate and register all available experiment tabs into tabWidget."""
        # Trigger tab registrations by importing the tabs package
        import polarisation_ui.ui.widgets.tabs  # NOQA: F401

        modules = ModuleRegistry.all()
        for tab_cls in TabRegistry.available(modules=modules):
            self._add_tab(tab_cls, modules)

    def _refresh_tab_visibility(self) -> None:
        """Re-evaluate which tabs are visible based on current module registry.

        Tabs whose ``required_modules`` are not met become hidden; new tabs
        that are now satisfied are added.  Existing satisfied tabs are kept in
        place (their state is preserved).
        """
        modules = ModuleRegistry.all()
        available_ids = {cls.tab_id for cls in TabRegistry.available(modules=modules)}
        existing_ids = {tab.tab_id for tab in self._tab_instances}

        # Inject modules into already-existing tabs (they may gain new capabilities)
        for tab in self._tab_instances:
            tab.inject_modules(modules)

        # Add newly available tabs (tabs that need kdc101 and it just connected)
        for tab_cls in TabRegistry.available(modules=modules):
            if tab_cls.tab_id not in existing_ids:
                self._add_tab(tab_cls, modules)

        # Hide tabs whose requirements are no longer met
        for tab in self._tab_instances:
            if tab.tab_id not in available_ids:
                idx = self.ui.tabWidget.indexOf(tab)
                if idx >= 0:
                    self.ui.tabWidget.setTabVisible(idx, False)
            else:
                idx = self.ui.tabWidget.indexOf(tab)
                if idx >= 0:
                    self.ui.tabWidget.setTabVisible(idx, True)

    # ==================== Signal Connections ====================

    def _connect_signals(self) -> None:
        """Connect all signals between components."""
        # Menu actions
        self.ui.actionAcquisitionSettings.triggered.connect(self._open_acq_settings)
        self.ui.actionEncoderDebug.triggered.connect(self._open_encoder_debug)
        self.ui.actionLogWindow.triggered.connect(self._open_log_window)
        self.ui.actionEventLog.toggled.connect(self.ui.dockEventLog.setVisible)
        self.ui.dockEventLog.visibilityChanged.connect(
            self.ui.actionEventLog.setChecked
        )
        self.ui.actionPowerCalibration.triggered.connect(self._open_power_calibration)
        self.ui.actionAutoPowerCalibration.triggered.connect(
            self._open_auto_power_calibration
        )

        # PDTIA gain button group — assign IDs 1–4 to match stage numbers
        for stage in (1, 2, 3, 4):
            self.ui.gainButtonGroup.setId(getattr(self.ui, f"btnGain{stage}"), stage)
        self.ui.gainButtonGroup.idClicked.connect(self._on_gain_button_clicked)

        # Power calibration profile controls
        self.ui.cbProfile.currentIndexChanged.connect(self._on_profile_selected)
        self.ui.btnReloadProfiles.clicked.connect(self._reload_profiles)
        self.ui.btnOpenCalibration.clicked.connect(self._open_power_calibration)
        self._reload_profiles()

        # Inline acquisition settings (averaging)
        self.ui.cbSampleAverageOn.toggled.connect(self.ui.spbSampleAverages.setEnabled)
        self.ui.cbDetectorAverageOn.toggled.connect(
            self.ui.spbDetectorAverages.setEnabled
        )
        self.ui.cbSampleAverageOn.toggled.connect(self._on_acq_inline_changed)
        self.ui.spbSampleAverages.valueChanged.connect(self._on_acq_inline_changed)
        self.ui.cbDetectorAverageOn.toggled.connect(self._on_acq_inline_changed)
        self.ui.spbDetectorAverages.valueChanged.connect(self._on_acq_inline_changed)

        # Group selection — enables/disables experiment tabs and updates filename preview
        self.ui.cbGroupLetter.currentIndexChanged.connect(self._on_group_changed)
        self.ui.leSuffix.textChanged.connect(self._update_filename_display)
        self.ui.leTeamName.textChanged.connect(self._update_filename_display)

        # Arduino connection controls
        self.ui.btnRefreshPorts.clicked.connect(self._populate_ports)
        self.ui.btnArduinoConnect.clicked.connect(self._connect_arduino)

        # KDC101 connection controls
        self.ui.btnKDCRefresh.clicked.connect(self._populate_kdc_devices)
        self.ui.btnKDCConnect.clicked.connect(self._connect_kdc)
        self.ui.btnKDCHome.clicked.connect(self._home_kdc)

        # Zero buttons
        self.ui.btnSampleZero.clicked.connect(self._zero_sample_encoder)
        self.ui.btnDetectorStageZero.clicked.connect(self._zero_detector_encoder)

        # Measurement controls
        self.ui.btnStartMeasurement.clicked.connect(self._start_measurement)
        self.ui.btnStopMeasurement.clicked.connect(self._stop_measurement)
        self.ui.btnResetMeasurement.clicked.connect(self._reset_measurement)

        # Save button
        self.ui.btnSave.clicked.connect(self._save_data)

        # Data controller signals
        self.data_controller.angles_updated.connect(self._update_angle_displays)
        self.data_controller.intensity_updated.connect(self._update_intensity_display)
        self.data_controller.power_updated.connect(self._update_wattage_display)
        self.data_controller.poll_rate_updated.connect(self._update_poll_rate)
        self.data_controller.diagnostics_updated.connect(
            self._handle_diagnostics_update
        )
        self.data_controller.error_occurred.connect(self._handle_data_error)
        self.data_controller.retry_connecting.connect(self._handle_reconnect_attempt)
        self.data_controller.reconnect_succeeded.connect(self._handle_reconnect_success)
        self.data_controller.connection_lost.connect(self._handle_connection_lost)

        # Measurement state changes
        self.data_controller.measurement_started.connect(self._on_measurement_started)
        self.data_controller.measurement_stopped.connect(self._on_measurement_stopped)

        # Connection state changes → all tabs
        self.data_controller.reconnect_succeeded.connect(
            lambda: self._notify_tabs_connection_state(ConnState.CONNECTED)
        )
        self.data_controller.retry_connecting.connect(
            lambda _attempt, _delay: self._notify_tabs_connection_state(
                ConnState.RECONNECTING
            )
        )
        self.data_controller.connection_lost.connect(
            lambda: self._notify_tabs_connection_state(ConnState.LOST)
        )

        # Tab activation
        self.ui.tabWidget.currentChanged.connect(self._on_tab_changed)

        # Apply initial group state (cbGroupLetter starts at -1 → all experiment tabs disabled)
        self._on_group_changed(self.ui.cbGroupLetter.currentIndex())

    def _notify_tabs_connection_state(self, state: ConnState) -> None:
        for tab in self._tab_instances:
            tab.on_connection_state(state)

    @Slot(int)
    def _on_tab_changed(self, index: int) -> None:
        for tab in self._tab_instances:
            if self.ui.tabWidget.indexOf(tab) == index:
                tab.on_activated()
            else:
                tab.on_deactivated()
        if not self._is_measuring:
            self._sync_save_button()
        self._update_filename_display()

    @Slot(str, str)
    def _handle_tab_status(self, level: str, msg: str) -> None:
        if level == "warning":
            self.statusbar_manager.show_warning(msg)
        elif level == "error":
            self.statusbar_manager.show_error(msg)
        else:
            self.statusbar_manager.show_info(msg)

    # ==================== Group / Filename ====================

    @Slot(int)
    def _on_group_changed(self, index: int) -> None:
        """Enable or disable experiment tabs depending on whether a group is selected."""
        group_selected = index >= 0
        tooltip = "" if group_selected else "Bitte zuerst eine Gruppe auswählen"
        # Tab 0 is "Konfiguration" — always accessible.
        # Tabs 1+ are experiment tabs added by _setup_tabs.
        for i in range(1, self.ui.tabWidget.count()):
            self.ui.tabWidget.setTabEnabled(i, group_selected)
            self.ui.tabWidget.setTabToolTip(i, tooltip)
        if not group_selected and self.ui.tabWidget.currentIndex() > 0:
            self.ui.tabWidget.setCurrentIndex(0)
        self._update_filename_display()

    def _update_filename_display(self) -> None:
        """Refresh pteCurrentFilename with the expected save path for the active tab."""
        group = self.ui.cbGroupLetter.currentText()
        if not group:
            self.ui.pteCurrentFilename.setPlainText("")
            return

        suffix = self.ui.leSuffix.text().strip()
        tab = self._get_active_export_tab()
        if tab is not None:
            exp = tab.build_export()
            hint, tokens = exp.filename_hint, exp.filename_tokens
        else:
            hint, tokens = "messung", []
        stem = compose_filename(hint, group, suffix, tokens)
        tk = CONFIG.get("save", {}).get("tk_designation", "TKXX")
        team_raw = self.ui.leTeamName.text().strip()
        subterm = sanitize_subterm_for_folder(team_raw) if team_raw else ""
        folder = create_dropbox_foldername(group, tk, subterm)
        display = f"{folder}/{stem}.csv"
        self.ui.pteCurrentFilename.setPlainText(display)

    # ==================== Arduino Connection ====================

    def _populate_ports(self) -> None:
        """Populate the port combobox with currently available serial ports."""
        ports = self.device_manager.list_available_ports()
        self.ui.cbArduinoPort.clear()
        for port in ports:
            self.ui.cbArduinoPort.addItem(port)
        if not ports:
            self.ui.cbArduinoPort.addItem(CONFIG["messages"]["device_ports_missing"])
        Debug.info(f"Available serial ports: {ports}")

    @Slot()
    def _connect_arduino(self) -> None:
        """Attempt to connect to Arduino on the selected port."""
        port = self.ui.cbArduinoPort.itemText(self.ui.cbArduinoPort.currentIndex())
        if not port or port == CONFIG["messages"]["device_ports_missing"]:
            self.ui.lblArduinoStatusValue.setText(
                CONFIG["messages"]["device_not_connected"]
            )
            return

        set_connection_status(
            self.ui.ledArduinoStatus,
            self.ui.lblArduinoStatusValue,
            "Wird verbunden",
            LED_YELLOW,
        )
        self.ui.cbArduinoPort.setEnabled(False)
        self.ui.btnRefreshPorts.setEnabled(False)

        success = self.device_manager.connect_encoders(port=port)

        if success:
            set_connection_status(
                self.ui.ledArduinoStatus,
                self.ui.lblArduinoStatusValue,
                "Verbunden",
                LED_GREEN,
            )
            self._is_connected = True
            # Toggle button to disconnect
            self.ui.btnArduinoConnect.setText("Trennen")
            self.ui.btnArduinoConnect.clicked.disconnect(self._connect_arduino)
            self.ui.btnArduinoConnect.clicked.connect(self._disconnect_arduino)

            self._on_arduino_connected()
            self.statusbar_manager.show_success(f"Arduino verbunden auf {port}")
            Debug.info(f"Arduino connected on {port}")
        else:
            error = (
                self.device_manager.get_encoder_status().error_message
                or "Verbindung fehlgeschlagen"
            )
            set_connection_status(
                self.ui.ledArduinoStatus,
                self.ui.lblArduinoStatusValue,
                f"Fehler: {error}",
                LED_RED,
            )
            self.ui.cbArduinoPort.setEnabled(True)
            self.ui.btnRefreshPorts.setEnabled(True)
            self.statusbar_manager.show_error(f"Verbindung fehlgeschlagen: {error}")
            Debug.error(f"Arduino connection failed: {error}")

    @Slot()
    def _disconnect_arduino(self) -> None:
        """User-initiated disconnect from Arduino."""
        self.data_controller.stop_continuous_reading()
        self.device_manager.disconnect_all()
        self._reset_connection_ui()
        self.statusbar_manager.show_info("Arduino getrennt")
        Debug.info("Arduino disconnected by user")

    def _reset_connection_ui(self) -> None:
        """Reset all connection-related UI elements to the disconnected state."""
        self._is_connected = False
        self._adc_saturated = False

        # Restore connect button
        try:
            self.ui.btnArduinoConnect.clicked.disconnect(self._disconnect_arduino)
        except RuntimeError:
            pass  # not connected — safe to ignore
        try:
            self.ui.btnArduinoConnect.clicked.disconnect(self._connect_arduino)
        except RuntimeError:
            pass
        self.ui.btnArduinoConnect.setText("Verbinden")
        self.ui.btnArduinoConnect.clicked.connect(self._connect_arduino)

        # Re-enable port selection
        self.ui.cbArduinoPort.setEnabled(True)
        self.ui.btnRefreshPorts.setEnabled(True)

        # Disable hardware groups
        self.ui.gbSampleStage.setEnabled(False)
        self.ui.gbDetectorStage.setEnabled(False)
        self.ui.gbDetector.setEnabled(False)
        self.ui.btnStartMeasurement.setEnabled(False)

        set_connection_status(
            self.ui.ledArduinoStatus,
            self.ui.lblArduinoStatusValue,
            "Getrennt",
            LED_RED,
        )
        set_connection_status(
            self.ui.ledSampleStatus,
            self.ui.lblSampleStatusValue,
            "Kein Signal",
            LED_RED,
        )
        set_connection_status(
            self.ui.ledDetectorStageStatus,
            self.ui.lblDetectorStageStatusValue,
            "Kein Signal",
            LED_RED,
        )
        set_connection_status(
            self.ui.ledDetectorStatus,
            self.ui.lblDetectorStatusValue,
            "Kein Signal",
            LED_RED,
        )

    def _on_arduino_connected(self) -> None:
        """Enable encoder UI sections and start data acquisition after connection."""
        self.ui.gbSampleStage.setEnabled(True)
        self.ui.gbDetectorStage.setEnabled(True)
        self.ui.gbDetector.setEnabled(True)
        set_connection_status(
            self.ui.ledSampleStatus,
            self.ui.lblSampleStatusValue,
            "Encoder A",
            LED_GREEN,
        )
        set_connection_status(
            self.ui.ledDetectorStageStatus,
            self.ui.lblDetectorStageStatusValue,
            "Encoder B",
            LED_GREEN,
        )
        set_connection_status(
            self.ui.ledDetectorStatus,
            self.ui.lblDetectorStatusValue,
            "ADC",
            LED_GREEN,
        )
        self.ui.lcdSampleAngle.display(0.00)
        self.ui.lcdDetectorStageAngle.display(0.00)
        self.ui.lcdWattage.display(0.00)
        self.ui.lcdDetectorVoltage.display(0.00)
        self.ui.lcdSampleAngle_2.display(0.00)
        self.ui.lcdDetectorStageAngle_2.display(0.00)
        self.ui.lcdDetectorVoltage_2.display(0.00)
        self.ui.lcdWattage_2.display(0.00)
        self.ui.btnStartMeasurement.setEnabled(True)
        self._sensor_a_ok = True
        self._sensor_b_ok = True
        self._adc_saturated = False
        self.data_controller.start_continuous_reading()
        self._notify_tabs_connection_state(ConnState.CONNECTED)

        # Sync gain buttons to the stage the firmware already has active
        stage = self.device_manager.get_pdtia_gain()
        if 1 <= stage <= 4:
            btn = getattr(self.ui, f"btnGain{stage}", None)
            if btn is not None:
                btn.setChecked(True)
            self.data_controller._current_pdtia_gain = stage

        self._update_detector_calibration_status()

    # ==================== KDC101 Connection ====================

    def _populate_kdc_devices(self) -> None:
        """Populate cbKDCDevice with currently discovered Thorlabs KDC101 devices."""
        current = self.ui.cbKDCDevice.currentText()
        self.ui.cbKDCDevice.clear()
        devices = KDC101Polariser.list_devices()
        for conn_id, desc in devices:
            self.ui.cbKDCDevice.addItem(f"{conn_id} — {desc}", userData=conn_id)
        if not devices:
            self.ui.cbKDCDevice.addItem("Kein KDC101 gefunden")
        # Restore previous selection if still present
        if current:
            idx = self.ui.cbKDCDevice.findText(current)
            if idx >= 0:
                self.ui.cbKDCDevice.setCurrentIndex(idx)
        Debug.info(f"KDC101 devices found: {devices}")

    @Slot()
    def _connect_kdc(self) -> None:
        """Connect to the selected KDC101 device."""
        conn_id = self.ui.cbKDCDevice.currentData() or self.ui.cbKDCDevice.currentText()
        if not conn_id or conn_id == "Kein KDC101 gefunden":
            QMessageBox.warning(self, "KDC101", "Kein Gerät ausgewählt.")
            return
        set_connection_status(
            self.ui.ledKDCStatus,
            self.ui.lblKDCStatusValue,
            "Verbinde...",
            LED_YELLOW,
        )
        try:
            self._kdc.connect(conn_id)
        except KDC101Error as exc:
            set_connection_status(
                self.ui.ledKDCStatus,
                self.ui.lblKDCStatusValue,
                f"Fehler: {exc}",
                LED_RED,
            )
            self.statusbar_manager.show_error(f"KDC101 Verbindungsfehler: {exc}")
            return
        ModuleRegistry.register(KDC101ModuleAdapter(self._kdc))
        self._refresh_tab_visibility()
        set_connection_status(
            self.ui.ledKDCStatus,
            self.ui.lblKDCStatusValue,
            f"Verbunden: {conn_id}",
            LED_GREEN,
        )
        self.ui.btnKDCConnect.setText("Trennen")
        self.ui.btnKDCConnect.clicked.disconnect(self._connect_kdc)
        self.ui.btnKDCConnect.clicked.connect(self._disconnect_kdc)
        self.ui.btnKDCHome.setEnabled(True)
        self._kdc_position_timer.start()
        self.statusbar_manager.show_success(f"KDC101 verbunden: {conn_id}")
        Debug.info(f"KDC101 connected: {conn_id}")

    @Slot()
    def _disconnect_kdc(self) -> None:
        """Disconnect from the currently connected KDC101 device."""
        self._kdc_position_timer.stop()
        self._kdc.disconnect()
        ModuleRegistry.unregister("kdc101")
        self._refresh_tab_visibility()
        set_connection_status(
            self.ui.ledKDCStatus,
            self.ui.lblKDCStatusValue,
            "Nicht verbunden",
            LED_RED,
        )
        self.ui.btnKDCConnect.setText("Verbinden")
        self.ui.btnKDCConnect.clicked.disconnect(self._disconnect_kdc)
        self.ui.btnKDCConnect.clicked.connect(self._connect_kdc)
        self.ui.btnKDCHome.setEnabled(False)
        self.ui.lblKDCPositionValue.setText("—")
        self.statusbar_manager.show_info("KDC101 getrennt")

    @Slot()
    def _home_kdc(self) -> None:
        """Home the KDC101 stage off the main thread."""
        if not self._kdc.is_connected():
            return
        self.ui.btnKDCHome.setEnabled(False)
        self.ui.btnKDCConnect.setEnabled(False)
        self._kdc_home_worker = KDC101HomeWorker(self._kdc, parent=self)
        self._kdc_home_worker.done.connect(self._on_kdc_home_done)
        self._kdc_home_worker.error.connect(self._on_kdc_home_error)
        self._kdc_home_worker.start()
        self.statusbar_manager.show_info("KDC101 Referenzfahrt läuft…")

    @Slot()
    def _on_kdc_home_done(self) -> None:
        self.ui.btnKDCHome.setEnabled(True)
        self.ui.btnKDCConnect.setEnabled(True)
        self.statusbar_manager.show_success("KDC101 Referenzfahrt abgeschlossen")

    @Slot(str)
    def _on_kdc_home_error(self, msg: str) -> None:
        self.ui.btnKDCHome.setEnabled(True)
        self.ui.btnKDCConnect.setEnabled(True)
        self.statusbar_manager.show_error(f"KDC101 Referenzfahrt fehlgeschlagen: {msg}")

    @Slot()
    def _refresh_kdc_position(self) -> None:
        """Poll current KDC101 position and update the live display label."""
        try:
            pos = self._kdc.get_position_deg()
            self.ui.lblKDCPositionValue.setText(f"{pos:.2f}°")
        except KDC101Error:
            pass  # transient read error — label stays at last known value

    # ==================== Acquisition Settings ====================

    def _load_acq_settings_from_config(self) -> AcquisitionSettings:
        return AcquisitionSettings.from_config(CONFIG.get("acquisition", {}))

    @Slot()
    def _on_acq_inline_changed(self) -> None:
        """Update AcquisitionSettings from the inline configuration-tab controls."""
        self._acq_settings = AcquisitionSettings(
            samp_average_on=self.ui.cbSampleAverageOn.isChecked(),
            samp_averages=self.ui.spbSampleAverages.value(),
            det_average_on=self.ui.cbDetectorAverageOn.isChecked(),
            det_averages=self.ui.spbDetectorAverages.value(),
            sample_stage_inverted=self._acq_settings.sample_stage_inverted,
            spike_filter_enabled=self._acq_settings.spike_filter_enabled,
            spike_max_delta_deg=self._acq_settings.spike_max_delta_deg,
        )
        self.data_controller.update_acq_settings(self._acq_settings)

    def _sync_inline_acq_controls(self) -> None:
        """Push current _acq_settings to the inline configuration-tab widgets."""
        for widget in (
            self.ui.cbSampleAverageOn,
            self.ui.spbSampleAverages,
            self.ui.cbDetectorAverageOn,
            self.ui.spbDetectorAverages,
        ):
            widget.blockSignals(True)
        self.ui.cbSampleAverageOn.setChecked(self._acq_settings.samp_average_on)
        self.ui.spbSampleAverages.setValue(self._acq_settings.samp_averages)
        self.ui.spbSampleAverages.setEnabled(self._acq_settings.samp_average_on)
        self.ui.cbDetectorAverageOn.setChecked(self._acq_settings.det_average_on)
        self.ui.spbDetectorAverages.setValue(self._acq_settings.det_averages)
        self.ui.spbDetectorAverages.setEnabled(self._acq_settings.det_average_on)
        for widget in (
            self.ui.cbSampleAverageOn,
            self.ui.spbSampleAverages,
            self.ui.cbDetectorAverageOn,
            self.ui.spbDetectorAverages,
        ):
            widget.blockSignals(False)

    @Slot()
    def _open_acq_settings(self) -> None:
        """Open the acquisition settings dialog (spike filter + inversion settings)."""
        dialog = AcquisitionSettingsDialog(self._acq_settings, parent=self)
        # exec() makes the dialog application-modal: the main window cannot
        # receive input while the dialog is open. setEnabled(False) is NOT
        # used because it propagates to child QObjects and would disable the
        # dialog itself.
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._acq_settings = dialog.get_settings()
            self._sync_inline_acq_controls()
            self.data_controller.update_acq_settings(self._acq_settings)

    # ==================== Data Display Updates ====================

    @Slot(float, float)
    def _update_angle_displays(
        self, sample_angle: float, detector_angle: float
    ) -> None:
        """Update LCD displays with encoder readings.

        Args:
            sample_angle: Sample stage angle in degrees
            detector_angle: Detector stage angle in degrees
        """
        # Values received from DataController are already averaged — always display.
        # The LED colour already indicates sensor health; freezing the value on a
        # diagnostic fault is more confusing than showing a potentially noisy reading.
        self.ui.lcdSampleAngle.display(f"{sample_angle:.2f}")
        self.ui.lcdDetectorStageAngle.display(f"{detector_angle:.2f}")
        self.ui.lcdSampleAngle_2.display(f"{sample_angle:.2f}")
        self.ui.lcdDetectorStageAngle_2.display(f"{detector_angle:.2f}")

    @Slot(float)
    def _update_intensity_display(self, voltage: float) -> None:
        """Update the detector voltage LCD (in mV) and check for ADC saturation."""
        if math.isnan(voltage):
            self.ui.lcdWattage.display("----")
            self.ui.lcdDetectorVoltage_2.display("----")
            return

        voltage_mv = voltage * 1000.0
        self.ui.lcdWattage.display(f"{voltage_mv:.2f}")
        self.ui.lcdDetectorVoltage_2.display(f"{voltage_mv:.2f}")

        saturated = voltage < _ADC_SAT_LOW or voltage > _ADC_SAT_HIGH
        if saturated != self._adc_saturated:
            self._adc_saturated = saturated
            if saturated:
                set_connection_status(
                    self.ui.ledDetectorStatus,
                    self.ui.lblDetectorStatusValue,
                    "Sättigung",
                    LED_YELLOW,
                )
            else:
                set_connection_status(
                    self.ui.ledDetectorStatus,
                    self.ui.lblDetectorStatusValue,
                    "ADC",
                    LED_GREEN,
                )

    @Slot(float)
    def _update_poll_rate(self, hz: float) -> None:
        """Show the measured poll rate in the detector status label when ADC is healthy."""
        if not self._adc_saturated and self._is_connected:
            self.ui.lblDetectorStatusValue.setText(f"ADC  {hz:.1f} Hz")

    # ==================== PDTIA Gain Control ====================

    @Slot(int)
    def _on_gain_button_clicked(self, stage: int) -> None:
        """Set PDTIA gain stage on the device and visually select the button."""
        ok = self.data_controller.set_pdtia_gain(stage)
        if not ok:
            # Deselect all buttons so the UI doesn't show a wrong state
            grp = self.ui.gainButtonGroup
            checked = grp.checkedButton()
            if checked is not None:
                grp.setExclusive(False)
                checked.setChecked(False)
                grp.setExclusive(True)
            self.statusbar_manager.show_error(
                f"PDTIA Gain {stage} konnte nicht gesetzt werden"
            )
        else:
            self.statusbar_manager.show_info(f"PDTIA Gain auf Stufe {stage} gesetzt")

    # ==================== Power / Wattage Display ====================

    @Slot(float)
    def _update_wattage_display(self, power_W: float) -> None:
        if math.isnan(power_W):
            self.ui.lcdDetectorVoltage.display("----")
            self.ui.lcdWattage_2.display("----")
        else:
            power_uw = power_W * 1e6
            self.ui.lcdDetectorVoltage.display(f"{power_uw:.2f}")
            self.ui.lcdWattage_2.display(f"{power_uw:.2f}")

    # ==================== Calibration Profile Management ====================

    def _reload_profiles(self) -> None:
        """Refresh the profile combobox from the detector profiles directory."""
        cb = self.ui.cbProfile
        cb.blockSignals(True)
        current_name = cb.currentText()
        cb.clear()
        for path in PowerCalibrationProfile.list_profiles():
            cb.addItem(path.stem, userData=path)
        idx = cb.findText(current_name)
        if idx >= 0:
            cb.setCurrentIndex(idx)
        cb.blockSignals(False)
        self._on_profile_selected(cb.currentIndex())

    @Slot(int)
    def _on_profile_selected(self, index: int) -> None:
        if index < 0:
            self._calibration_profile = None
            self.data_controller.update_calibration_profile(None)
            self._update_detector_calibration_status()
            return
        path: Path = self.ui.cbProfile.itemData(index)
        if path is None:
            self._calibration_profile = None
            self.data_controller.update_calibration_profile(None)
            self._update_detector_calibration_status()
            return
        try:
            self._calibration_profile = PowerCalibrationProfile.load(path)
            Debug.info(f"Loaded calibration profile: {path}")
        except Exception as exc:
            Debug.error(f"Failed to load calibration profile {path}: {exc}")
            self._calibration_profile = None
        self.data_controller.update_calibration_profile(self._calibration_profile)
        self._update_detector_calibration_status()

    def _update_detector_calibration_status(self) -> None:
        """Show calibration hint in the detector status when connected and no profile is loaded."""
        if not self._is_connected:
            return
        if self._calibration_profile is None:
            set_connection_status(
                self.ui.ledDetectorStatus,
                self.ui.lblDetectorStatusValue,
                "Kalibrierung auswählen",
                LED_YELLOW,
            )
        else:
            set_connection_status(
                self.ui.ledDetectorStatus,
                self.ui.lblDetectorStatusValue,
                "ADC",
                LED_GREEN,
            )

    def _open_power_calibration(self) -> None:
        from polarisation_ui.ui.windows.power_calibration_window import (
            PowerCalibrationWindow,
        )

        dialog = PowerCalibrationWindow(
            data_controller=self.data_controller,
            parent=self,
        )
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        dialog.profile_saved.connect(self._reload_profiles)
        dialog.show()

    def _open_auto_power_calibration(self) -> None:
        from polarisation_ui.ui.windows.auto_power_calibration_window import (
            AutoPowerCalibrationWindow,
        )

        dialog = AutoPowerCalibrationWindow(
            data_controller=self.data_controller,
            parent=self,
        )
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        dialog.profile_saved.connect(self._reload_profiles)
        dialog.show()

    # ==================== Encoder Control ====================

    @Slot()
    def _zero_sample_encoder(self) -> None:
        """Zero sample encoder at current position."""
        success = self.device_manager.zero_sample_encoder()

        if success:
            self.statusbar_manager.show_success("Probe-Encoder auf Null gesetzt")
            Debug.info("Sample encoder zeroed")
        else:
            self.statusbar_manager.show_error(
                "Fehler beim Nullsetzen des Probe-Encoders"
            )
            show_error(
                self,
                "Nullsetzen fehlgeschlagen",
                "Probe-Encoder konnte nicht auf Null gesetzt werden.",
            )

    @Slot()
    def _zero_detector_encoder(self) -> None:
        """Zero detector encoder at current position."""
        success = self.device_manager.zero_detector_encoder()

        if success:
            self.statusbar_manager.show_success("Detektor-Encoder auf Null gesetzt")
            Debug.info("Detector encoder zeroed")
        else:
            self.statusbar_manager.show_error(
                "Fehler beim Nullsetzen des Detektor-Encoders"
            )
            show_error(
                self,
                "Nullsetzen fehlgeschlagen",
                "Detektor-Encoder konnte nicht auf Null gesetzt werden.",
            )

    @Slot()
    def _open_encoder_debug(self) -> None:
        """Open the encoder debug dialog (non-modal)."""
        dialog = EncoderDebugDialog(
            self.device_manager,
            sample_inverted=self._acq_settings.sample_stage_inverted,
            data_controller=self.data_controller,
            parent=self,
        )
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        dialog.show()

    @Slot()
    def _open_log_window(self) -> None:
        """Open or raise the live log output window."""
        if self._log_window is None:
            from polarisation_ui.ui.windows.log_window import LogWindow

            self._log_window = LogWindow(parent=self)
            self._log_window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            self._log_window.destroyed.connect(self._on_log_window_closed)
        self._log_window.show()
        self._log_window.raise_()
        self._log_window.activateWindow()

    def _on_log_window_closed(self) -> None:
        self._log_window = None

    # ==================== Measurement Control ====================

    @Slot()
    def _start_measurement(self) -> None:
        """Start measurement session."""
        success = self.data_controller.start_measurement()

        if success:
            self.statusbar_manager.show_success("Messung gestartet")
            Debug.info("Measurement session started")
        else:
            self.statusbar_manager.show_error("Messung konnte nicht gestartet werden")

    @Slot()
    def _stop_measurement(self) -> None:
        """Stop measurement session."""
        self.data_controller.stop_measurement()
        self.statusbar_manager.show_info("Messung gestoppt")
        Debug.info("Measurement session stopped")

    @Slot()
    def _reset_measurement(self) -> None:
        """Reset measurement data across all tabs."""
        for tab in self._tab_instances:
            tab.on_reset()
        self.statusbar_manager.show_info("Messung zurückgesetzt")
        Debug.info("Measurement data reset")

        # Disable reset button
        self.ui.btnResetMeasurement.setEnabled(False)

    @Slot()
    def _on_measurement_started(self) -> None:
        """Handle measurement started event."""
        self._is_measuring = True

        self.ui.btnStartMeasurement.setEnabled(False)
        self.ui.btnStopMeasurement.setEnabled(True)
        self.ui.btnResetMeasurement.setEnabled(False)
        self.ui.btnSave.setEnabled(False)

        # Disable zeroing and tab switching during a run
        self.ui.btnSampleZero.setEnabled(False)
        self.ui.btnDetectorStageZero.setEnabled(False)
        self.ui.tabWidget.tabBar().setEnabled(False)

        for tab in self._tab_instances:
            tab.on_measurement_started()

    @Slot()
    def _on_measurement_stopped(self) -> None:
        """Handle measurement stopped event."""
        self._is_measuring = False

        self.ui.btnStartMeasurement.setEnabled(True)
        self.ui.btnStopMeasurement.setEnabled(False)
        self.ui.btnResetMeasurement.setEnabled(True)

        # Re-enable zeroing and tab switching
        self.ui.btnSampleZero.setEnabled(True)
        self.ui.btnDetectorStageZero.setEnabled(True)
        self.ui.tabWidget.tabBar().setEnabled(True)

        self._sync_save_button()

        for tab in self._tab_instances:
            tab.on_measurement_stopped()

    @Slot(int)
    def _on_tab_points_changed(self, count: int) -> None:
        """Keep save button in sync with the active tab's point count when not measuring."""
        if not self._is_measuring:
            self._sync_save_button()

    def _sync_save_button(self) -> None:
        """Enable Save iff the currently active tab has saved points."""
        tab = self._get_active_export_tab()
        has_points = tab is not None and len(tab.get_saved_points()) > 0
        self.ui.btnSave.setEnabled(has_points)

    # ==================== Data Saving ====================

    def _get_active_export_tab(self):
        """Return the currently selected tab if it exposes the export contract, else None."""
        idx = self.ui.tabWidget.currentIndex()
        if idx < 0:
            return None
        widget = self.ui.tabWidget.widget(idx)
        tab = next((t for t in self._tab_instances if t is widget), None)
        return (
            tab
            if tab is not None
            and hasattr(tab, "build_export")
            and hasattr(tab, "get_saved_points")
            else None
        )

    @Slot()
    def _save_data(self) -> None:
        """Export the active tab's saved points to a user-chosen CSV file."""
        tab = self._get_active_export_tab()
        if tab is None or not tab.get_saved_points():
            show_error(self, "Speichern", "Keine Messpunkte gespeichert.")
            return

        exp = tab.build_export()
        if not exp.rows:
            show_error(self, "Speichern", "Keine Messpunkte gespeichert.")
            return

        group_letter = self.ui.cbGroupLetter.currentText()
        suffix = self.ui.leSuffix.text().strip()
        stem = compose_filename(
            exp.filename_hint, group_letter, suffix, exp.filename_tokens
        )
        tk = CONFIG.get("save", {}).get("tk_designation", "TKXX")
        team_raw = self.ui.leTeamName.text().strip()
        subterm = sanitize_subterm_for_folder(team_raw) if team_raw else ""
        folder = create_dropbox_foldername(group_letter, tk, subterm)
        default_dir = Path.home() / folder
        default_dir.mkdir(parents=True, exist_ok=True)

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Messdaten speichern",
            str(default_dir / f"{stem}.csv"),
            "CSV-Dateien (*.csv);;Alle Dateien (*)",
        )
        if not path:
            return

        cal_meta: dict = {}
        if self._calibration_profile is not None:
            cal_meta = self._calibration_profile.to_save_metadata()

        save_tab_export(
            Path(path),
            exp,
            group_letter=group_letter,
            suffix=suffix,
            power_cal_meta=cal_meta,
            saved_at=datetime.now(),
        )
        self.statusbar_manager.show_success(
            f"{len(exp.rows)} Datenpunkte gespeichert: {path}"
        )

    # ==================== Error Handling ====================

    @Slot(bool, str, bool, str)
    def _handle_diagnostics_update(
        self, a_ok: bool, a_desc: str, b_ok: bool, b_desc: str
    ) -> None:
        """React to per-encoder diagnostic results from the data controller.

        Each encoder's LED and display gate is updated independently so a
        fault on one stage doesn't affect the other.
        """
        prev_a_ok = self._sensor_a_ok
        prev_b_ok = self._sensor_b_ok

        self._update_encoder_health(
            ok=a_ok,
            prev_ok=prev_a_ok,
            led=self.ui.ledSampleStatus,
            label=self.ui.lblSampleStatusValue,
            label_ok="Encoder A",
            clear_fn=self.data_controller.clear_sample_buffer,
        )
        self._sensor_a_ok = a_ok

        self._update_encoder_health(
            ok=b_ok,
            prev_ok=prev_b_ok,
            led=self.ui.ledDetectorStageStatus,
            label=self.ui.lblDetectorStageStatusValue,
            label_ok="Encoder B",
            clear_fn=self.data_controller.clear_det_buffer,
        )
        self._sensor_b_ok = b_ok

        # Status bar: only show when something is wrong or just recovered
        if not a_ok or not b_ok:
            parts = [d for ok, d in ((a_ok, a_desc), (b_ok, b_desc)) if not ok]
            self.statusbar_manager.show_warning(f"Sensor-Diagnose: {' | '.join(parts)}")
        elif not prev_a_ok and not prev_b_ok:
            # Both just recovered from fault
            self.statusbar_manager.show_success("Sensor-Diagnose OK")

    def _update_encoder_health(
        self,
        *,
        ok: bool,
        prev_ok: bool,
        led,
        label,
        label_ok: str,
        clear_fn: Callable[[], None],
    ) -> None:
        """Apply LED update for one encoder; flush its averaging buffer on recovery."""
        if ok:
            if not prev_ok:
                clear_fn()
                set_connection_status(led, label, label_ok, LED_GREEN)
        else:
            set_connection_status(led, label, "Sensor-Fehler", LED_YELLOW)

    @Slot(str)
    def _handle_data_error(self, error_msg: str) -> None:
        """First read error: mark encoder LEDs yellow, show in status bar."""
        Debug.error(f"Data acquisition error: {error_msg}")
        set_connection_status(
            self.ui.ledSampleStatus,
            self.ui.lblSampleStatusValue,
            "Verbindungsfehler",
            LED_YELLOW,
        )
        set_connection_status(
            self.ui.ledDetectorStageStatus,
            self.ui.lblDetectorStageStatusValue,
            "Verbindungsfehler",
            LED_YELLOW,
        )
        set_connection_status(
            self.ui.ledDetectorStatus,
            self.ui.lblDetectorStatusValue,
            "Verbindungsfehler",
            LED_YELLOW,
        )
        self.statusbar_manager.show_error(f"Lesefehler: {error_msg}")

    @Slot(int, float)
    def _handle_reconnect_attempt(self, attempt: int, _delay_s: float) -> None:
        """Show reconnection progress in status bar (banner shows the detailed countdown)."""
        self.statusbar_manager.show_warning(
            "Verbindung unterbrochen – Wiederverbindung wird versucht..."
        )

    @Slot()
    def _handle_reconnect_success(self) -> None:
        """Serial connection re-established: restore all status indicators."""
        set_connection_status(
            self.ui.ledArduinoStatus,
            self.ui.lblArduinoStatusValue,
            "Verbunden",
            LED_GREEN,
        )
        set_connection_status(
            self.ui.ledSampleStatus,
            self.ui.lblSampleStatusValue,
            "Encoder A",
            LED_GREEN,
        )
        set_connection_status(
            self.ui.ledDetectorStageStatus,
            self.ui.lblDetectorStageStatusValue,
            "Encoder B",
            LED_GREEN,
        )
        set_connection_status(
            self.ui.ledDetectorStatus,
            self.ui.lblDetectorStatusValue,
            "ADC",
            LED_GREEN,
        )
        self._adc_saturated = False
        self.statusbar_manager.show_success("Verbindung wiederhergestellt")
        Debug.info("Reconnect: UI status restored")

    @Slot()
    def _handle_connection_lost(self) -> None:
        """Max reconnect attempts exhausted: show disconnected state, offer data export."""
        self._reset_connection_ui()
        self.ui.gbSampleStage.setEnabled(False)
        self.ui.gbDetectorStage.setEnabled(False)
        self.statusbar_manager.show_error(
            "Verbindung verloren – bitte Arduino neu verbinden"
        )
        Debug.error("Connection permanently lost; user must reconnect manually")

        journal = self.data_controller.current_journal
        if journal is not None and journal.row_count > 0:
            self._offer_partial_export(journal)

    # ==================== Session Journal Helpers ====================

    def _check_orphan_journals(self) -> None:
        """On startup, scan for unfinalized session journals and offer recovery."""
        orphans = SessionJournal.find_orphans()
        if not orphans:
            return
        n = len(orphans)
        reply = QMessageBox.question(
            self,
            "Ungespeicherte Sitzungen",
            f"{n} unvollständige Messsitzung(en) gefunden.\n"
            "Möchten Sie die Daten jetzt exportieren?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if reply != QMessageBox.StandardButton.Yes:
            # User dismissed — delete all orphan directories so they don't
            # reappear on the next launch.
            for session_dir in orphans:
                try:
                    shutil.rmtree(session_dir)
                    Debug.info(f"Orphan journal deleted: {session_dir}")
                except OSError as e:
                    Debug.warning(f"Could not delete orphan {session_dir}: {e}")
            return
        for session_dir in orphans:
            path, _ = QFileDialog.getSaveFileName(
                self,
                f"Sitzung exportieren — {session_dir.name}",
                str(Path.home() / f"recovery_{session_dir.name}.csv"),
                "CSV-Dateien (*.csv);;Alle Dateien (*)",
            )
            if path:
                rows = SessionJournal.export_orphan(session_dir, Path(path))
                self.statusbar_manager.show_success(f"{rows} Zeilen exportiert: {path}")

    def _offer_partial_export(self, journal: "SessionJournal") -> None:
        """Show a modal offering to export partial data after connection_lost."""
        reply = QMessageBox.question(
            self,
            "Verbindung verloren",
            f"Verbindung nach {journal.row_count} Messpunkten verloren.\n"
            "Teildaten jetzt exportieren?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Teildaten exportieren",
            str(Path.home() / "messung_partial.csv"),
            "CSV-Dateien (*.csv);;Alle Dateien (*)",
        )
        if path:
            rows = journal.export_to_csv(Path(path), finalize=True)
            self.statusbar_manager.show_success(f"{rows} Teildaten gespeichert: {path}")

    # ==================== Window Lifecycle ====================

    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle window close event.

        Args:
            event: Close event
        """
        Debug.info("Closing application...")

        # Stop measurement if active
        if self._is_measuring:
            self.data_controller.stop_measurement()

        # Clean up
        self.data_controller.cleanup()
        self.device_manager.disconnect_all()

        event.accept()
