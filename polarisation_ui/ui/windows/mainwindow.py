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

from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import Slot
from PySide6.QtGui import QCloseEvent

from polarisation_ui.infrastructure.logging import Debug
from polarisation_ui.infrastructure.config import import_config
from polarisation_ui.infrastructure.device_manager import GoniometerDeviceManager
from polarisation_ui.pyqt.ui_mainwindow import Ui_MainWindow

# UI components
from polarisation_ui.ui.common.dialogs import show_info, show_error
from polarisation_ui.ui.common.statusbar import StatusBarManager
from polarisation_ui.ui.controllers.data_controller import DataController

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

    # LED colors
    LED_GREEN = "background-color: rgb(0, 255, 0); border: 0px; padding: 4px; border-radius: 10px"
    LED_RED = "background-color: rgb(255, 11, 3); border: 0px; padding: 4px; border-radius: 10px"
    LED_GRAY = "background-color: rgb(128, 128, 128); border: 0px; padding: 4px; border-radius: 10px"

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

        # Setup UI and connections
        self._setup_initial_state()
        self._connect_signals()

        # Start continuous reading
        self.data_controller.start_continuous_reading()

        Debug.info("MainWindow initialized with Qt Designer UI")

    # ==================== UI Setup ====================

    def _setup_initial_state(self) -> None:
        """Setup initial UI state."""
        # Set LEDs to green (connected)
        self.ui.sample_statusLED.setStyleSheet(self.LED_GREEN)
        self.ui.dstage_statusLED.setStyleSheet(self.LED_GREEN)
        self.ui.detector_statusLED.setStyleSheet(self.LED_GRAY)  # Not implemented yet

        # Set encoder labels
        self.ui.sample_enr.setText("Encoder A")
        self.ui.dstage_enr.setText("Encoder B")
        self.ui.detector_enr.setText("Not Connected")

        # Set initial LCD values
        self.ui.sample_angle.display(0.00)
        self.ui.dstage_angle.display(0.00)
        self.ui.detector_voltage.display(0.00)

        # Enable controls
        self.ui.sample_zero.setEnabled(True)
        self.ui.dstage_zero_2.setEnabled(True)
        self.ui.buttonStart.setEnabled(True)
        self.ui.buttonStop.setEnabled(False)
        self.ui.buttonReset.setEnabled(False)

        # Show status
        self.statusbar_manager.show_success("Encoders connected")

    # ==================== Signal Connections ====================

    def _connect_signals(self) -> None:
        """Connect all signals between components."""
        # Zero buttons
        self.ui.sample_zero.clicked.connect(self._zero_sample_encoder)
        self.ui.dstage_zero_2.clicked.connect(self._zero_detector_encoder)

        # Measurement controls
        self.ui.buttonStart.clicked.connect(self._start_measurement)
        self.ui.buttonStop.clicked.connect(self._stop_measurement)
        self.ui.buttonReset.clicked.connect(self._reset_measurement)

        # Save button
        self.ui.buttonSave.clicked.connect(self._save_data)

        # Data controller signals
        self.data_controller.angles_updated.connect(self._update_angle_displays)
        self.data_controller.error_occurred.connect(self._handle_data_error)

        # Measurement state changes
        self.data_controller.measurement_started.connect(self._on_measurement_started)
        self.data_controller.measurement_stopped.connect(self._on_measurement_stopped)

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
        # Update LCD displays
        self.ui.sample_angle.display(f"{sample_angle:.2f}")
        self.ui.dstage_angle.display(f"{detector_angle:.2f}")

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
        self.ui.buttonReset.setEnabled(False)

    @Slot()
    def _on_measurement_started(self) -> None:
        """Handle measurement started event."""
        self._is_measuring = True

        # Update UI state
        self.ui.buttonStart.setEnabled(False)
        self.ui.buttonStop.setEnabled(True)
        self.ui.buttonReset.setEnabled(False)

        # Disable zeroing during measurement
        self.ui.sample_zero.setEnabled(False)
        self.ui.dstage_zero_2.setEnabled(False)

        # Enable save when measurement has data
        self.ui.buttonSave.setEnabled(False)  # Enable after first data point

    @Slot()
    def _on_measurement_stopped(self) -> None:
        """Handle measurement stopped event."""
        self._is_measuring = False

        # Update UI state
        self.ui.buttonStart.setEnabled(True)
        self.ui.buttonStop.setEnabled(False)
        self.ui.buttonReset.setEnabled(True)

        # Re-enable zeroing
        self.ui.sample_zero.setEnabled(True)
        self.ui.dstage_zero_2.setEnabled(True)

        # Enable save if we have data
        self.ui.buttonSave.setEnabled(True)

    # ==================== Data Saving ====================

    @Slot()
    def _save_data(self) -> None:
        """Save measurement data to file."""
        # Get save parameters from UI
        group_letter = self.ui.groupLetter.currentText()
        suffix = self.ui.suffix.text()

        if not group_letter:
            show_error(self, "Save Error", "Please select a group letter.")
            return

        # TODO: Implement actual data saving using save_service
        self.statusbar_manager.show_success("Data saved (placeholder)")
        Debug.info(f"Data save requested: Group={group_letter}, Suffix={suffix}")

    # ==================== Error Handling ====================

    @Slot(str)
    def _handle_data_error(self, error_msg: str) -> None:
        """
        Handle data acquisition errors.

        Args:
            error_msg: Error message from data controller
        """
        self.statusbar_manager.show_error(f"Data error: {error_msg}")
        Debug.error(f"Data acquisition error: {error_msg}")

        # Set LEDs to red if connection lost
        self.ui.sample_statusLED.setStyleSheet(self.LED_RED)
        self.ui.dstage_statusLED.setStyleSheet(self.LED_RED)

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
