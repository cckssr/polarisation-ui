"""
Goniometer control widget combining graphics view and controls.

This widget integrates the visualization with manual/electronic
angle input and displays encoder feedback.
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QDoubleSpinBox,
    QLabel,
    QPushButton,
    QGroupBox,
    QFormLayout,
)
from PySide6.QtCore import QTimer

from ...core.services import GoniometerService
from ...infrastructure.devices.base import EncoderAdapter
from ...graphics.goniometer_view import GoniometerView


class GoniometerWidget(QWidget):
    """
    Complete goniometer control widget.

    Combines:
    - Graphics visualization (GoniometerView)
    - Manual angle input controls
    - Encoder feedback display
    - State validation
    """

    # Signals for integration with main window
    angles_changed = Signal(float, float)  # (probe_angle, detector_angle)
    error_occurred = Signal(str)  # error message

    def __init__(
        self,
        service: GoniometerService,
        probe_encoder: EncoderAdapter = None,
        detector_encoder: EncoderAdapter = None,
        parent=None,
    ):
        """
        Initialize goniometer widget.

        Args:
            service: GoniometerService instance for business logic.
            probe_encoder: Optional encoder for probe stage feedback.
            detector_encoder: Optional encoder for detector feedback.
            parent: Parent widget.
        """
        super().__init__(parent)
        self.service = service
        self.probe_encoder = probe_encoder
        self.detector_encoder = detector_encoder

        # Initialize service
        self.service.initialize_state(0.0)

        # Setup polling timer for encoder updates (100ms)
        self.encoder_timer = QTimer()
        self.encoder_timer.timeout.connect(self._poll_encoders)
        self.encoder_timer.setInterval(100)

        self._setup_ui()
        self._update_display()

    def _setup_ui(self) -> None:
        """Build the UI layout."""
        layout = QVBoxLayout()

        # Graphics view
        self.graphics_view = GoniometerView()
        layout.addWidget(self.graphics_view)

        # Control panel
        control_panel = self._create_control_panel()
        layout.addWidget(control_panel)

        # Status panel
        status_panel = self._create_status_panel()
        layout.addWidget(status_panel)

        self.setLayout(layout)
        self.setWindowTitle("Goniometer Control")

    def _create_control_panel(self) -> QGroupBox:
        """Create manual angle input controls."""
        group = QGroupBox("Manual Control")
        layout = QFormLayout()

        # Probe angle input
        self.probe_input = QDoubleSpinBox()
        self.probe_input.setRange(-180, 180)
        self.probe_input.setSingleStep(1.0)
        self.probe_input.setDecimals(1)
        self.probe_input.setSuffix("°")
        self.probe_input.valueChanged.connect(self._on_probe_angle_changed)
        layout.addRow("Probe Angle:", self.probe_input)

        # Detector angle display (read-only)
        self.detector_display = QDoubleSpinBox()
        self.detector_display.setRange(-360, 360)
        self.detector_display.setDecimals(1)
        self.detector_display.setSuffix("°")
        self.detector_display.setReadOnly(True)
        self.detector_display.setButtonSymbols(QDoubleSpinBox.NoButtons)
        layout.addRow("Detector Angle:", self.detector_display)

        # Reset button
        reset_btn = QPushButton("Reset to Zero")
        reset_btn.clicked.connect(self._on_reset_clicked)
        layout.addRow(reset_btn)

        group.setLayout(layout)
        return group

    def _create_status_panel(self) -> QGroupBox:
        """Create encoder feedback display."""
        group = QGroupBox("Encoder Feedback")
        layout = QFormLayout()

        # Probe encoder reading
        self.probe_feedback = QDoubleSpinBox()
        self.probe_feedback.setRange(-180, 180)
        self.probe_feedback.setDecimals(2)
        self.probe_feedback.setSuffix("°")
        self.probe_feedback.setReadOnly(True)
        self.probe_feedback.setButtonSymbols(QDoubleSpinBox.NoButtons)
        layout.addRow("Probe Feedback:", self.probe_feedback)

        # Detector encoder reading
        self.detector_feedback = QDoubleSpinBox()
        self.detector_feedback.setRange(-360, 360)
        self.detector_feedback.setDecimals(2)
        self.detector_feedback.setSuffix("°")
        self.detector_feedback.setReadOnly(True)
        self.detector_feedback.setButtonSymbols(QDoubleSpinBox.NoButtons)
        layout.addRow("Detector Feedback:", self.detector_feedback)

        # Status message
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: green;")
        layout.addRow("Status:", self.status_label)

        group.setLayout(layout)
        return group

    def _on_probe_angle_changed(self, angle: float) -> None:
        """Handle probe angle input change."""
        try:
            self.service.update_probe_angle(angle)
            self._update_display()
            self.angles_changed.emit(angle, angle * 2.0)
        except Exception as e:
            self.error_occurred.emit(str(e))
            self.status_label.setText(f"Error: {str(e)}")
            self.status_label.setStyleSheet("color: red;")

    def _on_reset_clicked(self) -> None:
        """Handle reset button click."""
        self.probe_input.setValue(0.0)
        self.service.reset()
        self.service.initialize_state(0.0)
        self._update_display()
        self.status_label.setText("Reset to zero")
        self.status_label.setStyleSheet("color: blue;")

    def _update_display(self) -> None:
        """Update all UI elements with current state."""
        state = self.service.get_state()
        if state is None:
            return

        # Block signals to avoid recursion
        self.probe_input.blockSignals(True)
        self.probe_input.setValue(state.probe_angle)
        self.probe_input.blockSignals(False)

        self.detector_display.setValue(state.detector_angle)
        self.graphics_view.update_goniometer(state.probe_angle, state.detector_angle)

        # Update status
        if state.validate():
            self.status_label.setText("Valid")
            self.status_label.setStyleSheet("color: green;")
        else:
            error_msg = state.get_validation_error()
            self.status_label.setText(f"Warning: {error_msg}")
            self.status_label.setStyleSheet("color: orange;")

    def _poll_encoders(self) -> None:
        """Poll encoder devices for updated values."""
        try:
            if self.probe_encoder and self.probe_encoder.is_connected():
                probe_angle = self.probe_encoder.read()
                self.probe_feedback.setValue(probe_angle)
                # Don't automatically update service - let user decide

            if self.detector_encoder and self.detector_encoder.is_connected():
                detector_angle = self.detector_encoder.read()
                self.detector_feedback.setValue(detector_angle)

        except Exception as e:
            # Don't crash on encoder read errors
            self.status_label.setText(f"Encoder error: {str(e)}")
            self.status_label.setStyleSheet("color: red;")

    def start_encoder_polling(self) -> None:
        """Start polling encoder devices."""
        if self.probe_encoder or self.detector_encoder:
            self.encoder_timer.start()

    def stop_encoder_polling(self) -> None:
        """Stop polling encoder devices."""
        self.encoder_timer.stop()

    def show_error(self, message: str) -> None:
        """Display error message to user."""
        self.status_label.setText(f"Error: {message}")
        self.status_label.setStyleSheet("color: red;")

    def closeEvent(self, event):
        """Cleanup on widget close."""
        self.stop_encoder_polling()
        super().closeEvent(event)
