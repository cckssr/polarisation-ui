"""
Example main window showing goniometer widget integration.

This demonstrates how to integrate the GoniometerWidget into
your main application window.
"""

from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QMenuBar, QMenu
from PySide6.QtCore import Qt

from ...core.services import GoniometerService
from ...infrastructure.devices.base import EncoderMock
from ..widgets.goniometer_widget import GoniometerWidget


class GoniometerMainWindow(QMainWindow):
    """
    Example main window with goniometer control.

    In your actual main window, integrate the GoniometerWidget
    into your existing layout.
    """

    def __init__(self):
        """Initialize main window."""
        super().__init__()
        self.setWindowTitle("Goniometer Control System")
        self.setGeometry(100, 100, 800, 700)

        # Create services and adapters
        # In real application, you might want to inject these
        self.goniometer_service = GoniometerService()

        # Use mock encoders for development/testing
        self.probe_encoder = EncoderMock(start_angle=0.0, name="Probe")
        self.detector_encoder = EncoderMock(start_angle=0.0, name="Detector")

        # Create main widget
        self.goniometer_widget = GoniometerWidget(
            service=self.goniometer_service,
            probe_encoder=self.probe_encoder,
            detector_encoder=self.detector_encoder,
        )

        # Set as central widget
        self.setCentralWidget(self.goniometer_widget)

        # Connect signals
        self.goniometer_widget.angles_changed.connect(self._on_angles_changed)
        self.goniometer_widget.error_occurred.connect(self._on_error)

        # Create menus
        self._setup_menus()

        # Start encoder polling
        self.goniometer_widget.start_encoder_polling()

    def _setup_menus(self) -> None:
        """Create application menus."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")
        file_menu.addAction("Exit", self.close)

        # View menu
        view_menu = menubar.addMenu("View")
        view_menu.addAction("Reset View", self._on_reset_view)

        # Simulation menu (for testing with mock encoders)
        sim_menu = menubar.addMenu("Simulation")
        sim_menu.addAction("Set Probe to 45°", lambda: self._set_mock_angle(45))
        sim_menu.addAction("Set Probe to 90°", lambda: self._set_mock_angle(90))
        sim_menu.addAction("Set Probe to -45°", lambda: self._set_mock_angle(-45))

    def _on_angles_changed(self, probe_angle: float, detector_angle: float) -> None:
        """Handle angle changes from widget."""
        # Can be used to trigger other actions (logging, saving, etc.)
        print(f"Angles changed: Probe={probe_angle}°, Detector={detector_angle}°")

    def _on_error(self, message: str) -> None:
        """Handle errors from widget."""
        print(f"Error: {message}")

    def _on_reset_view(self) -> None:
        """Reset graphics view."""
        self.goniometer_widget.graphics_view.reset_view()

    def _set_mock_angle(self, angle: float) -> None:
        """Set mock encoder to specific angle (for testing)."""
        self.probe_encoder.set_angle(angle)
        self.detector_encoder.set_angle(angle * 2.0)
        # These will be picked up by the polling mechanism
