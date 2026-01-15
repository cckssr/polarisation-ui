"""
Main Window for Goniometer Polarisation UI.

Integrates all components following the 3-layer architecture:
    - UI Layer: This window and widgets
    - Infrastructure: Device manager, config, logging
    - Core: Services and business logic (future)

Responsibilities:
    - Coordinate UI components
    - Handle user interactions
    - Connect signals between components
    - Manage application lifecycle
"""

from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Slot
from PySide6.QtGui import QAction, QCloseEvent

from polarisation_ui.infrastructure.logging import Debug
from polarisation_ui.infrastructure.config import import_config
from polarisation_ui.infrastructure.device_manager import GoniometerDeviceManager

# UI components
from polarisation_ui.ui.widgets.status_display import StatusDisplayWidget
from polarisation_ui.ui.widgets.control_panel import ControlPanelWidget
from polarisation_ui.ui.dialogs.connection import ConnectionDialog
from polarisation_ui.ui.common.dialogs import show_info, show_error
from polarisation_ui.ui.common.statusbar import StatusBarManager
from polarisation_ui.ui.controllers.data_controller import DataController

# Import settings
CONFIG = import_config()


class MainWindow(QMainWindow):
    """
    Main window of the Goniometer Polarisation UI.

    Provides interface for:
        - Connecting to encoder hardware
        - Viewing live sensor readings
        - Controlling measurement sessions
        - Configuring system settings
        - Saving and exporting data (future)

    Architecture:
        - Follows 3-layer separation
        - Uses signals/slots for component communication
        - Delegates hardware operations to device manager
        - Delegates data acquisition to data controller
    """

    def __init__(self, parent=None):
        """
        Initialize main window.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Window properties
        self.setWindowTitle("Goniometer Polarisation Control")
        self.resize(1200, 800)

        # Initialize infrastructure
        self.device_manager = GoniometerDeviceManager(use_mock=False)

        # Initialize UI components
        self._setup_ui()
        self._setup_menubar()
        self._setup_statusbar()

        # Initialize data controller
        self.data_controller = DataController(self.device_manager, self)

        # Connect signals
        self._connect_signals()

        Debug.info("MainWindow initialized")

    # ==================== UI Setup ====================

    def _setup_ui(self) -> None:
        """Build main window UI layout."""
        # Central widget with main content
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)

        # Left panel: Control panel
        self.control_panel = ControlPanelWidget()
        main_layout.addWidget(self.control_panel, stretch=1)

        # Center: Main display area (future: plots, goniometer view)
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.addStretch()
        main_layout.addWidget(center_widget, stretch=3)

        # Right panel: Status display
        self.status_display = StatusDisplayWidget()
        main_layout.addWidget(self.status_display, stretch=1)

    def _setup_menubar(self) -> None:
        """Create menu bar with actions."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        # Save action (future)
        self.save_action = QAction("&Save Data...", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.setEnabled(False)  # Enable when measurement data exists
        file_menu.addAction(self.save_action)

        file_menu.addSeparator()

        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Connection menu
        connection_menu = menubar.addMenu("&Connection")

        connect_action = QAction("&Connect Devices...", self)
        connect_action.setShortcut("Ctrl+C")
        connect_action.triggered.connect(self._show_connection_dialog)
        connection_menu.addAction(connect_action)

        disconnect_action = QAction("&Disconnect", self)
        disconnect_action.setShortcut("Ctrl+D")
        disconnect_action.triggered.connect(self._disconnect_devices)
        connection_menu.addAction(disconnect_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _setup_statusbar(self) -> None:
        """Create status bar."""
        statusbar = self.statusBar()
        self.statusbar_manager = StatusBarManager(statusbar)
        self.statusbar_manager.show_info("Ready")

    # ==================== Signal Connections ====================

    def _connect_signals(self) -> None:
        """Connect all signals between components."""
        # Control panel → Main window
        self.control_panel.connect_requested.connect(self._show_connection_dialog)
        self.control_panel.disconnect_requested.connect(self._disconnect_devices)

        # Encoder zeroing
        self.control_panel.zero_sample_requested.connect(self._zero_sample_encoder)
        self.control_panel.zero_detector_requested.connect(self._zero_detector_encoder)
        self.control_panel.zero_both_requested.connect(self._zero_both_encoders)

        # Measurement control
        self.control_panel.start_measurement_requested.connect(self._start_measurement)
        self.control_panel.stop_measurement_requested.connect(self._stop_measurement)

        # Data controller → Status display
        self.data_controller.angles_updated.connect(self.status_display.update_angles)
        self.data_controller.error_occurred.connect(self._handle_data_error)

        # Measurement state changes
        self.data_controller.measurement_started.connect(
            lambda: self.control_panel.set_measuring(True)
        )
        self.data_controller.measurement_stopped.connect(
            lambda: self.control_panel.set_measuring(False)
        )

    # ==================== Connection Management ====================

    @Slot()
    def _show_connection_dialog(self) -> None:
        """Show connection dialog and connect to devices."""
        dialog = ConnectionDialog(self)

        # Connect test signal
        dialog.connection_requested.connect(self._test_connection)

        # Show dialog
        if dialog.exec() == ConnectionDialog.DialogCode.Accepted:
            params = dialog.get_connection_params()
            self._connect_devices(params)

    @Slot(dict)
    def _test_connection(self, params: dict) -> None:
        """
        Test connection with given parameters.

        Args:
            params: Connection parameters from dialog
        """
        success = self.device_manager.connect_encoders(**params)

        # Find dialog and update test result
        for widget in self.findChildren(ConnectionDialog):
            if isinstance(widget, ConnectionDialog):
                if success:
                    widget.set_test_result(True, "Connection successful")
                    # Disconnect after test
                    self.device_manager.disconnect_encoders()
                else:
                    error_msg = self.device_manager.get_encoder_status().error_message
                    widget.set_test_result(False, error_msg or "Unknown error")
                break

    def _connect_devices(self, params: dict) -> None:
        """
        Connect to devices with given parameters.

        Args:
            params: Connection parameters
        """
        self.statusbar_manager.show_info("Connecting to devices...")

        success = self.device_manager.connect_encoders(**params)

        if success:
            self.statusbar_manager.show_success("Devices connected")
            self.control_panel.set_connected(True)
            self.status_display.set_connected(True)

            # Start continuous reading
            self.data_controller.start_continuous_reading()

            Debug.info("Devices connected successfully")
        else:
            error_msg = self.device_manager.get_encoder_status().error_message
            self.statusbar_manager.show_error("Connection failed")
            show_error(
                self,
                "Connection Error",
                "Failed to connect to encoder device.",
                detailed_text=error_msg,
            )

    @Slot()
    def _disconnect_devices(self) -> None:
        """Disconnect all devices."""
        # Stop data acquisition
        self.data_controller.stop_continuous_reading()

        if self.data_controller.is_measuring():
            self.data_controller.stop_measurement()

        # Disconnect devices
        self.device_manager.disconnect_all()

        # Update UI
        self.control_panel.set_connected(False)
        self.status_display.set_connected(False)
        self.statusbar_manager.show_info("Devices disconnected")

        Debug.info("Devices disconnected")

    # ==================== Encoder Control ====================

    @Slot()
    def _zero_sample_encoder(self) -> None:
        """Zero sample encoder at current position."""
        success = self.device_manager.zero_sample_encoder()

        if success:
            self.statusbar_manager.show_success("Sample encoder zeroed")
        else:
            self.statusbar_manager.show_error("Failed to zero sample encoder")

    @Slot()
    def _zero_detector_encoder(self) -> None:
        """Zero detector encoder at current position."""
        success = self.device_manager.zero_detector_encoder()

        if success:
            self.statusbar_manager.show_success("Detector encoder zeroed")
        else:
            self.statusbar_manager.show_error("Failed to zero detector encoder")

    @Slot()
    def _zero_both_encoders(self) -> None:
        """Zero both encoders at current positions."""
        success = self.device_manager.zero_both_encoders()

        if success:
            self.statusbar_manager.show_success("Both encoders zeroed")
        else:
            self.statusbar_manager.show_error("Failed to zero encoders")

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

    # ==================== Menu Actions ====================

    @Slot()
    def _show_about(self) -> None:
        """Show about dialog."""
        about_text = (
            "<h3>Goniometer Polarisation Control</h3>"
            "<p>Version 0.1.0 (Phase 0)</p>"
            "<p>Manual goniometer control and data acquisition system.</p>"
            "<p>Built with PySide6 and Python.</p>"
        )
        show_info(self, "About", about_text)

    # ==================== Window Lifecycle ====================

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Handle window close event.

        Args:
            event: Close event
        """
        # Check for unsaved data (future)
        # if self.has_unsaved_data():
        #     if not ask_confirmation(...):
        #         event.ignore()
        #         return

        # Clean up
        Debug.info("Closing application...")

        self.data_controller.cleanup()
        self.device_manager.disconnect_all()

        event.accept()
