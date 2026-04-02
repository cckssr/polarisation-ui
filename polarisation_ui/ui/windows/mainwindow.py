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
"""

import math
from collections import deque

from PySide6.QtWidgets import QDialog, QMainWindow, QComboBox
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QCloseEvent

from polarisation_ui.infrastructure.logging import Debug
from polarisation_ui.infrastructure.config import import_config
from polarisation_ui.infrastructure.device_manager import GoniometerDeviceManager
from polarisation_ui.pyqt.ui_mainwindow import Ui_MainWindow

# UI components
from polarisation_ui.core.models import AcquisitionSettings
from polarisation_ui.ui.common.dialogs import show_error
from polarisation_ui.ui.dialogs.acq_settings import AcquisitionSettingsDialog

from polarisation_ui.ui.common.statusbar import StatusBarManager
from polarisation_ui.ui.common.status_led import (
    set_connection_status,
    LED_GREEN,
    LED_RED,
    LED_YELLOW,
)
from polarisation_ui.ui.controllers.data_controller import DataController
from polarisation_ui.ui.windows.encoder_debug_window import EncoderDebugDialog

def _circular_mean_deg(angles: deque) -> float:
    """
    Circular mean for a buffer of angles in degrees.

    Arithmetic mean is wrong near the 0°/360° wrap (e.g. mean([359°, 1°])
    would give 180° instead of 0°).  The circular mean uses atan2 of the
    mean sin/cos components and is always correct.

    Returns a value in [0°, 360°).
    """
    n = len(angles)
    sin_sum = sum(math.sin(math.radians(a)) for a in angles)
    cos_sum = sum(math.cos(math.radians(a)) for a in angles)
    return math.degrees(math.atan2(sin_sum / n, cos_sum / n)) % 360


# Import settings
CONFIG = import_config()


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

        # Initialize data controller
        self.data_controller = DataController(self.device_manager, self)

        # Initialize status bar
        self.statusbar_manager = StatusBarManager(self.ui.statusBar)

        # Measurement state
        self._is_measuring = False

        # Load acquisition settings from config once; changes are session-only
        self._acq_settings: AcquisitionSettings = self._load_acq_settings_from_config()

        # Rolling-average buffers; sized from initial settings
        self._sample_buffer: deque[float] = deque(
            maxlen=self._acq_settings.samp_averages
        )
        self._det_buffer: deque[float] = deque(maxlen=self._acq_settings.det_averages)

        # Per-encoder sensor health — gates the respective angle display independently
        self._sensor_a_ok: bool = True
        self._sensor_b_ok: bool = True

        # Setup UI and connections
        self._setup_initial_state()
        self._connect_signals()

        Debug.info("MainWindow initialized with Qt Designer UI")

    # ==================== UI Setup ====================

    def _setup_initial_state(self) -> None:
        """Setup initial UI state (disconnected)."""
        # Make the combobox editable with a read-only line edit so the popup can show
        # full port names while the collapsed view shows a truncated version.
        self.ui.cbArduinoPort.setEditable(True)
        self.ui.cbArduinoPort.lineEdit().setReadOnly(True)
        self.ui.cbArduinoPort.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
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

        self.statusbar_manager.show_info(CONFIG["messages"]["device_please_connect"])

    # ==================== Signal Connections ====================

    def _connect_signals(self) -> None:
        """Connect all signals between components."""
        # Menu actions
        self.ui.actionAcquisitionSettings.triggered.connect(self._open_acq_settings)
        self.ui.actionEncoderDebug.triggered.connect(self._open_encoder_debug)

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
        self.data_controller.diagnostics_updated.connect(self._handle_diagnostics_update)
        self.data_controller.error_occurred.connect(self._handle_data_error)
        self.data_controller.retry_connecting.connect(self._handle_reconnect_attempt)
        self.data_controller.reconnect_succeeded.connect(self._handle_reconnect_success)
        self.data_controller.connection_lost.connect(self._handle_connection_lost)

        # Measurement state changes
        self.data_controller.measurement_started.connect(self._on_measurement_started)
        self.data_controller.measurement_stopped.connect(self._on_measurement_stopped)

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
            self.ui.lblArduinoStatusValue.setText(CONFIG["messages"]["device_not_connected"])
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

    def _on_arduino_connected(self) -> None:
        """Enable encoder UI sections and start data acquisition after connection."""
        self.ui.gbSampleStage.setEnabled(True)
        self.ui.gbDetectorStage.setEnabled(True)
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
        self.ui.lcdSampleAngle.display(0.00)
        self.ui.lcdDetectorStageAngle.display(0.00)
        self.ui.btnStartMeasurement.setEnabled(True)
        self._sensor_a_ok = True
        self._sensor_b_ok = True
        self.data_controller.sample_inverted = self._acq_settings.sample_stage_inverted
        self.data_controller.start_continuous_reading()

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
            # Recreate buffers with the new window size; old samples are discarded
            self._sample_buffer = deque(maxlen=self._acq_settings.samp_averages)
            self._det_buffer = deque(maxlen=self._acq_settings.det_averages)
            # Sync inversion flag immediately
            self.data_controller.sample_inverted = self._acq_settings.sample_stage_inverted
            Debug.info(
                f"Acquisition settings updated: "
                f"det={self._acq_settings.det_averages}x "
                f"(on={self._acq_settings.det_average_on}), "
                f"samp={self._acq_settings.samp_averages}x "
                f"(on={self._acq_settings.samp_average_on})"
            )

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
        # Always feed the buffers — cleared on health recovery to avoid stale samples
        self._sample_buffer.append(sample_angle)
        self._det_buffer.append(detector_angle)

        # Each encoder gates its own display independently
        if self._sensor_a_ok:
            display_sample = (
                _circular_mean_deg(self._sample_buffer)
                if self._acq_settings.samp_average_on
                else sample_angle
            )
            self.ui.lcdSampleAngle.display(f"{display_sample:.2f}")

        if self._sensor_b_ok:
            display_det = (
                _circular_mean_deg(self._det_buffer)
                if self._acq_settings.det_average_on
                else detector_angle
            )
            self.ui.lcdDetectorStageAngle.display(f"{display_det:.2f}")

        # Validate geometry (detector should be ~2x sample)
        expected_detector = 2.0 * sample_angle
        difference = abs(detector_angle - expected_detector)
        tolerance = 0.5  # degrees

        if difference > tolerance:
            # Geometry error - show in status bar occasionally
            if not hasattr(self, "_last_error_shown"):
                self._last_error_shown = 0

            # Only show every 50 updates to avoid spam
            self._last_error_shown += 1
            if self._last_error_shown >= 50:
                self.statusbar_manager.show_warning(
                    f"Geometry error: {difference:.2f}°", timeout=2000
                )
                self._last_error_shown = 0

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
            parent=self,
        )
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        dialog.show()

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
        """Reset measurement data."""
        # TODO: Clear accumulated measurement data
        self.statusbar_manager.show_info("Measurement reset")
        Debug.info("Measurement data reset")

        # Disable reset button
        self.ui.btnResetMeasurement.setEnabled(False)

    @Slot()
    def _on_measurement_started(self) -> None:
        """Handle measurement started event."""
        self._is_measuring = True

        # Update UI state
        self.ui.btnStartMeasurement.setEnabled(False)
        self.ui.btnStopMeasurement.setEnabled(True)
        self.ui.btnResetMeasurement.setEnabled(False)

        # Disable zeroing during measurement
        self.ui.btnSampleZero.setEnabled(False)
        self.ui.btnDetectorStageZero.setEnabled(False)

        # Enable save when measurement has data
        self.ui.btnSave.setEnabled(False)  # Enable after first data point

    @Slot()
    def _on_measurement_stopped(self) -> None:
        """Handle measurement stopped event."""
        self._is_measuring = False

        # Update UI state
        self.ui.btnStartMeasurement.setEnabled(True)
        self.ui.btnStopMeasurement.setEnabled(False)
        self.ui.btnResetMeasurement.setEnabled(True)

        # Re-enable zeroing
        self.ui.btnSampleZero.setEnabled(True)
        self.ui.btnDetectorStageZero.setEnabled(True)

        # Enable save if we have data
        self.ui.btnSave.setEnabled(True)

    # ==================== Data Saving ====================

    @Slot()
    def _save_data(self) -> None:
        """Save measurement data to file."""
        # Get save parameters from UI
        group_letter = self.ui.cbGroupLetter.currentText()
        suffix = self.ui.leSuffix.text()

        if not group_letter:
            show_error(self, "Save Error", "Please select a group letter.")
            return

        # TODO: Implement actual data saving using save_service
        self.statusbar_manager.show_success("Data saved (placeholder)")
        Debug.info(f"Data save requested: Group={group_letter}, Suffix={suffix}")

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
        self._update_encoder_health(
            ok=a_ok,
            prev_ok=self._sensor_a_ok,
            led=self.ui.ledSampleStatus,
            label=self.ui.lblSampleStatusValue,
            label_ok="Encoder A",
            buffer=self._sample_buffer,
        )
        self._sensor_a_ok = a_ok

        self._update_encoder_health(
            ok=b_ok,
            prev_ok=self._sensor_b_ok,
            led=self.ui.ledDetectorStageStatus,
            label=self.ui.lblDetectorStageStatusValue,
            label_ok="Encoder B",
            buffer=self._det_buffer,
        )
        self._sensor_b_ok = b_ok

        # Status bar: only show when something is wrong or just recovered
        if not a_ok or not b_ok:
            parts = [d for ok, d in ((a_ok, a_desc), (b_ok, b_desc)) if not ok]
            self.statusbar_manager.show_warning(f"Sensor-Diagnose: {' | '.join(parts)}")
        elif not self._sensor_a_ok and not self._sensor_b_ok:
            # Both just recovered
            self.statusbar_manager.show_success("Sensor-Diagnose OK")

    def _update_encoder_health(
        self, *, ok: bool, prev_ok: bool,
        led, label, label_ok: str, buffer: deque
    ) -> None:
        """Apply LED + buffer update for one encoder based on its diagnostic result."""
        if ok:
            if not prev_ok:
                buffer.clear()
                set_connection_status(led, label, label_ok, LED_GREEN)
        else:
            set_connection_status(led, label, "Sensor-Fehler", LED_YELLOW)

    @Slot(str)
    def _handle_data_error(self, error_msg: str) -> None:
        """First read error: mark encoder LEDs yellow, show in status bar."""
        Debug.error(f"Data acquisition error: {error_msg}")
        self._sensor_ok = False
        set_connection_status(
            self.ui.ledSampleStatus, self.ui.lblSampleStatusValue,
            "Verbindungsfehler", LED_YELLOW,
        )
        set_connection_status(
            self.ui.ledDetectorStageStatus, self.ui.lblDetectorStageStatusValue,
            "Verbindungsfehler", LED_YELLOW,
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
        self._sensor_ok = True
        self._sample_buffer.clear()
        self._det_buffer.clear()
        set_connection_status(
            self.ui.ledArduinoStatus, self.ui.lblArduinoStatusValue,
            "Verbunden", LED_GREEN,
        )
        set_connection_status(
            self.ui.ledSampleStatus, self.ui.lblSampleStatusValue,
            "Encoder A", LED_GREEN,
        )
        set_connection_status(
            self.ui.ledDetectorStageStatus, self.ui.lblDetectorStageStatusValue,
            "Encoder B", LED_GREEN,
        )
        self.statusbar_manager.show_success("Verbindung wiederhergestellt")
        Debug.info("Reconnect: UI status restored")

    @Slot()
    def _handle_connection_lost(self) -> None:
        """Max reconnect attempts exhausted: show disconnected state, re-enable connect UI."""
        self._sensor_ok = False
        set_connection_status(
            self.ui.ledArduinoStatus, self.ui.lblArduinoStatusValue,
            "Getrennt", LED_RED,
        )
        set_connection_status(
            self.ui.ledSampleStatus, self.ui.lblSampleStatusValue,
            "Kein Signal", LED_RED,
        )
        set_connection_status(
            self.ui.ledDetectorStageStatus, self.ui.lblDetectorStageStatusValue,
            "Kein Signal", LED_RED,
        )
        self.ui.gbSampleStage.setEnabled(False)
        self.ui.gbDetectorStage.setEnabled(False)
        self.ui.btnStartMeasurement.setEnabled(False)
        self.ui.cbArduinoPort.setEnabled(True)
        self.ui.btnRefreshPorts.setEnabled(True)
        self.statusbar_manager.show_error(
            "Verbindung verloren – bitte Arduino neu verbinden"
        )
        Debug.error("Connection permanently lost; user must reconnect manually")

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
