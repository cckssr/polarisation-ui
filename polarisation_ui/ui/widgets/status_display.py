"""
Status display widget for live values.

Shows current encoder readings and photodetector values in real-time.
Updates via signals from data controller.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QFrame,
)
from PySide6.QtCore import Slot
from typing import Optional


class StatusDisplayWidget(QWidget):
    """
    Widget displaying live sensor readings.

    Shows:
        - Sample stage angle (Encoder A)
        - Detector stage angle (Encoder B)
        - Photodetector value (future)
        - Connection status
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize status display widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self._setup_ui()
        self._reset_values()

    def _setup_ui(self) -> None:
        """Build widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Encoder readings group
        encoder_group = self._create_encoder_group()
        layout.addWidget(encoder_group)

        # Future: Photodetector group
        # photo_group = self._create_photodetector_group()
        # layout.addWidget(photo_group)

        layout.addStretch()

    def _create_encoder_group(self) -> QGroupBox:
        """Create encoder readings display group."""
        group = QGroupBox("Encoder Readings")
        layout = QVBoxLayout()

        # Sample stage (Encoder A)
        sample_layout = QHBoxLayout()
        sample_layout.addWidget(QLabel("Sample Stage:"))
        sample_layout.addStretch()
        self.sample_angle_label = QLabel("---.--°")
        self.sample_angle_label.setStyleSheet("font-weight: bold; font-size: 14pt;")
        sample_layout.addWidget(self.sample_angle_label)
        layout.addLayout(sample_layout)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        # Detector stage (Encoder B)
        detector_layout = QHBoxLayout()
        detector_layout.addWidget(QLabel("Detector Stage:"))
        detector_layout.addStretch()
        self.detector_angle_label = QLabel("---.--°")
        self.detector_angle_label.setStyleSheet("font-weight: bold; font-size: 14pt;")
        detector_layout.addWidget(self.detector_angle_label)
        layout.addLayout(detector_layout)

        # Separator
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line2)

        # Validation status
        validation_layout = QHBoxLayout()
        validation_layout.addWidget(QLabel("Geometry:"))
        validation_layout.addStretch()
        self.validation_label = QLabel("Not validated")
        self.validation_label.setStyleSheet("color: gray; font-style: italic;")
        validation_layout.addWidget(self.validation_label)
        layout.addLayout(validation_layout)

        group.setLayout(layout)
        return group

    def _reset_values(self) -> None:
        """Reset all displayed values to default."""
        self.sample_angle_label.setText("---.--°")
        self.detector_angle_label.setText("---.--°")
        self.validation_label.setText("Not validated")
        self.validation_label.setStyleSheet("color: gray; font-style: italic;")

    @Slot(float, float)
    def update_angles(self, sample_angle: float, detector_angle: float) -> None:
        """
        Update displayed angles.

        Args:
            sample_angle: Sample stage angle in degrees
            detector_angle: Detector stage angle in degrees
        """
        self.sample_angle_label.setText(f"{sample_angle:6.2f}°")
        self.detector_angle_label.setText(f"{detector_angle:6.2f}°")

        # Validate geometry (detector should be ~2x sample)
        self._validate_geometry(sample_angle, detector_angle)

    def _validate_geometry(self, sample_angle: float, detector_angle: float) -> None:
        """
        Validate goniometer geometry and update status.

        Args:
            sample_angle: Sample stage angle
            detector_angle: Detector stage angle
        """
        expected_detector = 2.0 * sample_angle
        difference = abs(detector_angle - expected_detector)
        tolerance = 0.5  # degrees

        if difference <= tolerance:
            self.validation_label.setText("✓ Valid")
            self.validation_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.validation_label.setText(f"✗ Error: {difference:.2f}°")
            self.validation_label.setStyleSheet("color: red; font-weight: bold;")

    @Slot(float)
    def update_sample_angle(self, angle: float) -> None:
        """
        Update only sample angle.

        Args:
            angle: Sample angle in degrees
        """
        self.sample_angle_label.setText(f"{angle:6.2f}°")

    @Slot(float)
    def update_detector_angle(self, angle: float) -> None:
        """
        Update only detector angle.

        Args:
            angle: Detector angle in degrees
        """
        self.detector_angle_label.setText(f"{angle:6.2f}°")

    @Slot()
    def clear_display(self) -> None:
        """Clear all displayed values."""
        self._reset_values()

    @Slot(bool)
    def set_connected(self, connected: bool) -> None:
        """
        Update display based on connection status.

        Args:
            connected: Whether devices are connected
        """
        if not connected:
            self.clear_display()
