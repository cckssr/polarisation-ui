"""
Connection Dialog for device setup.

Provides UI for configuring and connecting to encoder hardware.
Displays available serial ports and allows user to select connection parameters.
"""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QComboBox,
    QPushButton,
    QLabel,
    QGroupBox,
    QSpinBox,
    QWidget,
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtSerialPort import QSerialPortInfo
from typing import Optional, Dict, Any

from polarisation_ui.infrastructure.logging import Debug


class ConnectionDialog(QDialog):
    """
    Dialog for configuring device connections.

    Allows user to:
        - Select serial port for encoder Arduino
        - Configure baudrate and timeout
        - Test connection before accepting
        - View connection status

    Signals:
        connection_requested: Emitted when user requests connection
    """

    connection_requested = Signal(dict)  # Emits connection parameters

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize connection dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self.setWindowTitle("Device Connection")
        self.setModal(True)
        self.setMinimumWidth(400)

        # Connection parameters
        self.connection_params: Dict[str, Any] = {}

        # Build UI
        self._setup_ui()
        self._populate_ports()

        Debug.debug("Connection dialog initialized")

    def _setup_ui(self) -> None:
        """Build dialog UI."""
        layout = QVBoxLayout(self)

        # Encoder connection group
        encoder_group = self._create_encoder_group()
        layout.addWidget(encoder_group)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # Buttons
        button_layout = QHBoxLayout()

        self.refresh_button = QPushButton("Refresh Ports")
        self.refresh_button.clicked.connect(self._populate_ports)
        button_layout.addWidget(self.refresh_button)

        button_layout.addStretch()

        self.test_button = QPushButton("Test Connection")
        self.test_button.clicked.connect(self._test_connection)
        button_layout.addWidget(self.test_button)

        self.connect_button = QPushButton("Connect")
        self.connect_button.setDefault(True)
        self.connect_button.clicked.connect(self._on_connect)
        button_layout.addWidget(self.connect_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

    def _create_encoder_group(self) -> QGroupBox:
        """Create encoder connection settings group."""
        group = QGroupBox("Encoder Arduino")
        form = QFormLayout()

        # Port selection
        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(200)
        form.addRow("Serial Port:", self.port_combo)

        # Baudrate
        self.baudrate_combo = QComboBox()
        self.baudrate_combo.addItems(
            ["9600", "19200", "38400", "57600", "115200", "230400"]
        )
        self.baudrate_combo.setCurrentText("115200")
        form.addRow("Baudrate:", self.baudrate_combo)

        # Timeout
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(100, 5000)
        self.timeout_spin.setValue(1000)
        self.timeout_spin.setSuffix(" ms")
        form.addRow("Timeout:", self.timeout_spin)

        group.setLayout(form)
        return group

    def _populate_ports(self) -> None:
        """Populate port combo box with available serial ports."""
        self.port_combo.clear()

        ports = QSerialPortInfo.availablePorts()

        if not ports:
            self.port_combo.addItem("No ports found")
            self.test_button.setEnabled(False)
            self.connect_button.setEnabled(False)
            return

        for port in ports:
            # Show port name and description
            description = port.description()
            manufacturer = port.manufacturer()

            display_text = port.portName()
            if description:
                display_text += f" - {description}"
            if manufacturer:
                display_text += f" ({manufacturer})"

            self.port_combo.addItem(display_text, port.portName())

        self.test_button.setEnabled(True)
        self.connect_button.setEnabled(True)

        Debug.debug(f"Found {len(ports)} serial port(s)")

    def _get_connection_params(self) -> Dict[str, Any]:
        """
        Extract connection parameters from UI.

        Returns:
            dict: Connection parameters
        """
        port_data = self.port_combo.currentData()
        if port_data is None:
            port_data = self.port_combo.currentText()

        return {
            "port": port_data,
            "baudrate": int(self.baudrate_combo.currentText()),
            "timeout": self.timeout_spin.value() / 1000.0,  # Convert ms to seconds
        }

    def _test_connection(self) -> None:
        """Test connection to encoder without accepting dialog."""
        params = self._get_connection_params()

        self.status_label.setText("Testing connection...")
        self.test_button.setEnabled(False)

        # Emit signal for parent to test
        # Parent should call set_test_result() when done
        self.connection_requested.emit(params)

    def set_test_result(self, success: bool, message: str = "") -> None:
        """
        Set result of connection test.

        Args:
            success: Whether test was successful
            message: Optional status message
        """
        if success:
            self.status_label.setText("✓ Connection successful")
            self.status_label.setStyleSheet("color: green;")
        else:
            error_text = "✗ Connection failed"
            if message:
                error_text += f": {message}"
            self.status_label.setText(error_text)
            self.status_label.setStyleSheet("color: red;")

        self.test_button.setEnabled(True)

    def _on_connect(self) -> None:
        """Handle connect button click."""
        self.connection_params = self._get_connection_params()
        Debug.info(f"Connection accepted: {self.connection_params['port']}")
        self.accept()

    def get_connection_params(self) -> Dict[str, Any]:
        """
        Get selected connection parameters.

        Returns:
            dict: Connection parameters
        """
        return self.connection_params

    @staticmethod
    def get_connection(parent: Optional[QWidget] = None) -> Optional[Dict[str, Any]]:
        """
        Show connection dialog and return parameters if accepted.

        Args:
            parent: Parent widget

        Returns:
            dict: Connection parameters, or None if cancelled
        """
        dialog = ConnectionDialog(parent)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.get_connection_params()

        return None
