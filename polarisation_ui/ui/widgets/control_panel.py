"""
Control panel widget for device operations.

Provides buttons and controls for:
    - Connecting/disconnecting devices
    - Zeroing encoders
    - Starting/stopping measurements
"""

from typing import Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton
from PySide6.QtCore import Signal, Slot


class ControlPanelWidget(QWidget):
    """
    Widget providing device control buttons.

    Signals:
        connect_requested: User clicked connect button
        disconnect_requested: User clicked disconnect button
        zero_sample_requested: User clicked zero sample encoder
        zero_detector_requested: User clicked zero detector encoder
        zero_both_requested: User clicked zero both encoders
        start_measurement_requested: User clicked start measurement
        stop_measurement_requested: User clicked stop measurement
    """

    # Connection signals
    connect_requested = Signal()
    disconnect_requested = Signal()

    # Zeroing signals
    zero_sample_requested = Signal()
    zero_detector_requested = Signal()
    zero_both_requested = Signal()

    # Measurement signals
    start_measurement_requested = Signal()
    stop_measurement_requested = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize control panel widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self._setup_ui()
        self._set_disconnected_state()

    def _setup_ui(self) -> None:
        """Build widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Connection control
        connection_group = self._create_connection_group()
        layout.addWidget(connection_group)

        # Encoder zeroing controls
        zeroing_group = self._create_zeroing_group()
        layout.addWidget(zeroing_group)

        # Measurement controls
        measurement_group = self._create_measurement_group()
        layout.addWidget(measurement_group)

        layout.addStretch()

    def _create_connection_group(self) -> QGroupBox:
        """Create connection control group."""
        group = QGroupBox("Connection")
        layout = QVBoxLayout()

        self.connect_button = QPushButton("Connect Devices")
        self.connect_button.clicked.connect(self.connect_requested.emit)
        layout.addWidget(self.connect_button)

        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.clicked.connect(self.disconnect_requested.emit)
        layout.addWidget(self.disconnect_button)

        group.setLayout(layout)
        return group

    def _create_zeroing_group(self) -> QGroupBox:
        """Create encoder zeroing control group."""
        group = QGroupBox("Zero Encoders")
        layout = QVBoxLayout()

        # Individual zeroing buttons
        button_layout = QHBoxLayout()

        self.zero_sample_button = QPushButton("Zero Sample")
        self.zero_sample_button.clicked.connect(self.zero_sample_requested.emit)
        button_layout.addWidget(self.zero_sample_button)

        self.zero_detector_button = QPushButton("Zero Detector")
        self.zero_detector_button.clicked.connect(self.zero_detector_requested.emit)
        button_layout.addWidget(self.zero_detector_button)

        layout.addLayout(button_layout)

        # Zero both button
        self.zero_both_button = QPushButton("Zero Both Encoders")
        self.zero_both_button.clicked.connect(self.zero_both_requested.emit)
        layout.addWidget(self.zero_both_button)

        group.setLayout(layout)
        return group

    def _create_measurement_group(self) -> QGroupBox:
        """Create measurement control group."""
        group = QGroupBox("Measurement")
        layout = QVBoxLayout()

        self.start_button = QPushButton("Start Measurement")
        self.start_button.clicked.connect(self.start_measurement_requested.emit)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Measurement")
        self.stop_button.clicked.connect(self.stop_measurement_requested.emit)
        layout.addWidget(self.stop_button)

        group.setLayout(layout)
        return group

    def _set_disconnected_state(self) -> None:
        """Set button states for disconnected mode."""
        self.connect_button.setEnabled(True)
        self.disconnect_button.setEnabled(False)

        # Disable encoder controls
        self.zero_sample_button.setEnabled(False)
        self.zero_detector_button.setEnabled(False)
        self.zero_both_button.setEnabled(False)

        # Disable measurement controls
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(False)

    def _set_connected_state(self) -> None:
        """Set button states for connected mode."""
        self.connect_button.setEnabled(False)
        self.disconnect_button.setEnabled(True)

        # Enable encoder controls
        self.zero_sample_button.setEnabled(True)
        self.zero_detector_button.setEnabled(True)
        self.zero_both_button.setEnabled(True)

        # Enable measurement controls
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def _set_measuring_state(self) -> None:
        """Set button states for active measurement."""
        # Keep disconnect enabled
        self.disconnect_button.setEnabled(True)

        # Disable encoder zeroing during measurement
        self.zero_sample_button.setEnabled(False)
        self.zero_detector_button.setEnabled(False)
        self.zero_both_button.setEnabled(False)

        # Swap measurement buttons
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    @Slot(bool)
    def set_connected(self, connected: bool) -> None:
        """
        Update button states based on connection status.

        Args:
            connected: Whether devices are connected
        """
        if connected:
            self._set_connected_state()
        else:
            self._set_disconnected_state()

    @Slot(bool)
    def set_measuring(self, measuring: bool) -> None:
        """
        Update button states based on measurement status.

        Args:
            measuring: Whether measurement is active
        """
        if measuring:
            self._set_measuring_state()
        else:
            self._set_connected_state()
