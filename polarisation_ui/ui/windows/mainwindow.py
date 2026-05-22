"""
Main Window for Goniometer Polarisation UI.

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

import csv
import json
import math
import shutil
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QMainWindow,
    QMessageBox,
)
from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QCloseEvent

from polarisation_ui.core.models import AcquisitionSettings
from polarisation_ui.core.power_calibration import PowerCalibrationProfile
from polarisation_ui.infrastructure.config import import_config
from polarisation_ui.infrastructure.device_manager import GoniometerDeviceManager
from polarisation_ui.infrastructure.logging import Debug
from polarisation_ui.infrastructure.save_service import SENSOR_DESCRIPTIONS
from polarisation_ui.infrastructure.session_journal import SessionJournal
from polarisation_ui.pyqt.ui_mainwindow import Ui_MainWindow
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
    """
    Main window of the Goniometer Polarisation UI.

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
        """
        Initialize main window.

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

        self._acq_settings: AcquisitionSettings = self._load_acq_settings_from_config()

        self._sensor_a_ok: bool = True
        self._sensor_b_ok: bool = True
        self._tab_instances: list[PlotTabBase] = []

        # Log window — created lazily on first open, reused thereafter
        self._log_window = None

        # Power calibration — lazily loaded from selected profile
        self._calibration_profile: Optional[PowerCalibrationProfile] = None

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
        # Make the combobox editable with a read-only line edit so the popup can show
        # full port names while the collapsed view shows a truncated version.
        self.ui.cbArduinoPort.setEditable(True)
        self.ui.cbArduinoPort.lineEdit().setReadOnly(True)
        self.ui.cbArduinoPort.setSizeAdjustPolicy(
            self.ui.cbArduinoPort.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
        )
        self.ui.cbArduinoPort.setMinimumContentsLength(18)
        self._populate_ports()

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

    def _setup_tabs(self) -> None:
        """Instantiate and register all available experiment tabs into tabWidget."""
        # Trigger tab registrations by importing the tabs package
        import polarisation_ui.ui.widgets.tabs  # NOQA: F401

        for tab_cls in TabRegistry.available(modules={}):
            tab = tab_cls()
            tab.build()
            tab.status_message.connect(self._handle_tab_status)
            if hasattr(tab, "points_changed"):
                tab.points_changed.connect(self._on_malus_points_changed)
            self.ui.tabWidget.addTab(tab, tab.tab_title)
            self._tab_instances.append(tab)

    # ==================== Signal Connections ====================

    def _connect_signals(self) -> None:
        """Connect all signals between components."""
        # Menu actions
        self.ui.actionAcquisitionSettings.triggered.connect(self._open_acq_settings)
        self.ui.actionEncoderDebug.triggered.connect(self._open_encoder_debug)
        self.ui.actionLogWindow.triggered.connect(self._open_log_window)
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

        # Arduino connection controls
        self.ui.btnRefreshPorts.clicked.connect(self._populate_ports)
        self.ui.btnArduinoConnect.clicked.connect(self._connect_arduino)
        self.ui.cbArduinoPort.currentIndexChanged.connect(self._update_port_display)

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

        # Fan frame_ready to all tab on_frame handlers
        for tab in self._tab_instances:
            self.data_controller.frame_ready.connect(tab.on_frame)

        # Connection state changes → all tabs
        self.data_controller.reconnect_succeeded.connect(
            lambda: self._notify_tabs_connection_state(ConnState.CONNECTED)
        )
        self.data_controller.retry_connecting.connect(
            lambda: self._notify_tabs_connection_state(ConnState.RECONNECTING)
        )
        self.data_controller.connection_lost.connect(
            lambda: self._notify_tabs_connection_state(ConnState.LOST)
        )

        # Tab activation
        self.ui.tabWidget.currentChanged.connect(self._on_tab_changed)

    def _notify_tabs_connection_state(self, state: ConnState) -> None:
        for tab in self._tab_instances:
            tab.on_connection_state(state)

    @Slot(int)
    def _on_tab_changed(self, index: int) -> None:
        for i, tab in enumerate(self._tab_instances):
            if i == index:
                tab.on_activated()
            else:
                tab.on_deactivated()

    @Slot(str, str)
    def _handle_tab_status(self, level: str, msg: str) -> None:
        if level == "warning":
            self.statusbar_manager.show_warning(msg)
        elif level == "error":
            self.statusbar_manager.show_error(msg)
        else:
            self.statusbar_manager.show_info(msg)

    # ==================== Arduino Connection ====================

    def _populate_ports(self) -> None:
        """Populate the port combobox with currently available serial ports."""
        ports = self.device_manager.list_available_ports()
        self.ui.cbArduinoPort.clear()
        for port in ports:
            self.ui.cbArduinoPort.addItem(port)
        if not ports:
            self.ui.cbArduinoPort.addItem(CONFIG["messages"]["device_ports_missing"])

        # Let the popup grow wide enough for the longest entry while the collapsed
        # combobox stays narrow (limited by minimumContentsLength).
        fm = self.ui.cbArduinoPort.fontMetrics()
        all_items = ports if ports else [CONFIG["messages"]["device_ports_missing"]]
        popup_width = max(fm.horizontalAdvance(p) for p in all_items) + 32
        self.ui.cbArduinoPort.view().setMinimumWidth(popup_width)

        # Truncate the collapsed display (signal may not be connected yet on first call)
        self._update_port_display(self.ui.cbArduinoPort.currentIndex())
        Debug.info(f"Available serial ports: {ports}")

    @Slot(int)
    def _update_port_display(self, index: int) -> None:
        """Show truncated port name in the collapsed combobox; full name stays in the popup."""
        if index < 0 or not self.ui.cbArduinoPort.isEditable():
            return
        line_edit = self.ui.cbArduinoPort.lineEdit()
        if line_edit is None:
            return
        full = self.ui.cbArduinoPort.itemText(index)
        truncated = f"..{full[-13:]}" if len(full) > 15 else full
        line_edit.setText(truncated)

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
            "Verbinde...",
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
                f"Fehler: {error[:30]}",
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
        self.ui.lcdDetectorVoltage.display(0.0000)
        self.ui.btnStartMeasurement.setEnabled(True)
        self._sensor_a_ok = True
        self._sensor_b_ok = True
        self._adc_saturated = False
        self.data_controller.start_continuous_reading()
        self._notify_tabs_connection_state(ConnState.CONNECTED)

    # ==================== Acquisition Settings ====================

    def _load_acq_settings_from_config(self) -> AcquisitionSettings:
        """
        Build AcquisitionSettings from config.json defaults.

        Called once at startup. The returned object is the authoritative
        session state; it is never written back to disk.
        """
        acq = CONFIG.get("acquisition", {})
        return AcquisitionSettings(
            det_average_on=acq.get("det_average_on", True),
            det_averages=acq.get("det_averages", 5),
            samp_average_on=acq.get("samp_average_on", True),
            samp_averages=acq.get("samp_averages", 5),
            sample_stage_inverted=acq.get("sample_stage_inverted", True),
            spike_filter_enabled=acq.get("spike_filter_enabled", True),
            spike_max_delta_deg=acq.get("spike_max_delta_deg", 10.0),
        )

    @Slot()
    def _open_acq_settings(self) -> None:
        """Open the acquisition settings dialog. Main window is disabled while open."""
        dialog = AcquisitionSettingsDialog(self._acq_settings, parent=self)
        # exec() makes the dialog application-modal: the main window cannot
        # receive input while the dialog is open. setEnabled(False) is NOT
        # used because it propagates to child QObjects and would disable the
        # dialog itself.
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._acq_settings = dialog.get_settings()
            self.data_controller.update_acq_settings(self._acq_settings)

    # ==================== Data Display Updates ====================

    @Slot(float, float)
    def _update_angle_displays(
        self, sample_angle: float, detector_angle: float
    ) -> None:
        """
        Update LCD displays with encoder readings.

        Args:
            sample_angle: Sample stage angle in degrees
            detector_angle: Detector stage angle in degrees
        """
        # Values received from DataController are already averaged — always display.
        # The LED colour already indicates sensor health; freezing the value on a
        # diagnostic fault is more confusing than showing a potentially noisy reading.
        self.ui.lcdSampleAngle.display(f"{sample_angle:.2f}")
        self.ui.lcdDetectorStageAngle.display(f"{detector_angle:.2f}")

    @Slot(float)
    def _update_intensity_display(self, voltage: float) -> None:
        """Update the detector voltage LCD and check for ADC saturation."""
        if math.isnan(voltage):
            self.ui.lcdDetectorVoltage.display("----")
            return

        self.ui.lcdDetectorVoltage.display(f"{voltage:.4f}")

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
            self.ui.lcdWattage.display("    ----")
        else:
            power_mw = power_W * 1e3
            self.ui.lcdWattage.display(f"{power_mw:.3f}")

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
            return
        path: Path = self.ui.cbProfile.itemData(index)
        if path is None:
            self._calibration_profile = None
            self.data_controller.update_calibration_profile(None)
            return
        try:
            self._calibration_profile = PowerCalibrationProfile.load(path)
            Debug.info(f"Loaded calibration profile: {path}")
        except Exception as exc:
            Debug.error(f"Failed to load calibration profile {path}: {exc}")
            self._calibration_profile = None
        self.data_controller.update_calibration_profile(self._calibration_profile)

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
            self.statusbar_manager.show_success("Sample encoder zeroed")
            Debug.info("Sample encoder zeroed")
        else:
            self.statusbar_manager.show_error("Failed to zero sample encoder")
            show_error(self, "Zero Error", "Failed to zero sample encoder.")

    @Slot()
    def _zero_detector_encoder(self) -> None:
        """Zero detector encoder at current position."""
        success = self.device_manager.zero_detector_encoder()

        if success:
            self.statusbar_manager.show_success("Detector encoder zeroed")
            Debug.info("Detector encoder zeroed")
        else:
            self.statusbar_manager.show_error("Failed to zero detector encoder")
            show_error(self, "Zero Error", "Failed to zero detector encoder.")

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
            self.statusbar_manager.show_success("Measurement started")
            Debug.info("Measurement session started")
        else:
            self.statusbar_manager.show_error("Failed to start measurement")

    @Slot()
    def _stop_measurement(self) -> None:
        """Stop measurement session."""
        self.data_controller.stop_measurement()
        self.statusbar_manager.show_info("Measurement stopped")
        Debug.info("Measurement session stopped")

    @Slot()
    def _reset_measurement(self) -> None:
        """Reset measurement data across all tabs."""
        for tab in self._tab_instances:
            tab.on_reset()
        self.statusbar_manager.show_info("Measurement reset")
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

        # Enable save only when there are saved malus points
        malus_tab = self._get_malus_tab()
        has_points = malus_tab is not None and len(malus_tab.get_malus_points()) > 0
        self.ui.btnSave.setEnabled(has_points)

        for tab in self._tab_instances:
            tab.on_measurement_stopped()

    @Slot(int)
    def _on_malus_points_changed(self, count: int) -> None:
        """Keep save button in sync with malus curve point count when not measuring."""
        if not self._is_measuring:
            self.ui.btnSave.setEnabled(count > 0)

    # ==================== Data Saving ====================

    def _get_malus_tab(self):
        """Return the first tab instance that exposes get_malus_points(), or None."""
        return next(
            (t for t in self._tab_instances if hasattr(t, "get_malus_points")), None
        )

    @Slot()
    def _save_data(self) -> None:
        """Export manually saved malus curve points to a user-chosen CSV file."""
        malus_tab = self._get_malus_tab()
        points = malus_tab.get_malus_points() if malus_tab is not None else []
        if not points:
            show_error(self, "Speichern", "Keine Messpunkte gespeichert.")
            return

        group_letter = self.ui.cbGroupLetter.currentText()
        suffix = self.ui.leSuffix.text().strip()
        default_name = (
            f"messung_{group_letter}_{suffix}.csv"
            if suffix
            else f"messung_{group_letter}.csv"
        )

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Messdaten speichern",
            str(Path.home() / default_name),
            "CSV-Dateien (*.csv);;Alle Dateien (*)",
        )
        if not path:
            return

        saved_at = datetime.now()
        csv_path = Path(path)

        with open(csv_path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(
                [
                    "sample_angle_deg",
                    "detector_angle_deg",
                    "intensity_V",
                    "pdtia_gain",
                    "power_W",
                    "conv_factor_W_per_V",
                ]
            )
            for pt in points:
                writer.writerow(
                    [
                        f"{pt.sample_angle:.4f}",
                        f"{pt.detector_angle:.4f}",
                        f"{pt.intensity_V:.6f}",
                        str(pt.pdtia_gain) if pt.pdtia_gain else "",
                        f"{pt.power_W:.6e}" if pt.power_W is not None else "",
                        (
                            f"{pt.conv_factor_W_per_V:.6e}"
                            if pt.conv_factor_W_per_V is not None
                            else ""
                        ),
                    ]
                )

        cal_meta: dict = {}
        if self._calibration_profile is not None:
            cal_meta = {
                "profile_name": self._calibration_profile.name,
                "calibrated_at": self._calibration_profile.calibrated_at,
                "gain_conversion_factors": {
                    str(stage): cal.conversion_factor_W_per_V()
                    for stage, cal in self._calibration_profile.gains.items()
                    if cal.conversion_factor_W_per_V() is not None
                },
            }

        metadata = {
            "saved_at": saved_at.isoformat(),
            "point_count": len(points),
            "group": self.ui.cbGroupLetter.currentText(),
            "suffix": self.ui.leSuffix.text().strip(),
            "columns": [
                "sample_angle_deg",
                "detector_angle_deg",
                "intensity_V",
                "pdtia_gain",
                "power_W",
                "conv_factor_W_per_V",
            ],
            "units": {
                "sample_angle_deg": "degrees",
                "detector_angle_deg": "degrees",
                "intensity_V": "volts",
                "power_W": "watts",
                "conv_factor_W_per_V": "watts_per_volt",
            },
            "power_calibration": cal_meta,
            "sensors": SENSOR_DESCRIPTIONS,
        }
        metadata_path = csv_path.with_name(csv_path.stem + "_metadata.json")
        with open(metadata_path, "w", encoding="utf-8") as fh:
            json.dump(metadata, fh, indent=2)

        self.statusbar_manager.show_success(
            f"{len(points)} Datenpunkte gespeichert: {path}"
        )
        Debug.info(f"Malus data exported to {csv_path} ({len(points)} points)")

    # ==================== Error Handling ====================

    @Slot(bool, str, bool, str)
    def _handle_diagnostics_update(
        self, a_ok: bool, a_desc: str, b_ok: bool, b_desc: str
    ) -> None:
        """
        React to per-encoder diagnostic results from the data controller.

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

    @Slot()
    def _handle_reconnect_attempt(self) -> None:
        """Show reconnection progress in status bar."""
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
        """
        Handle window close event.

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
