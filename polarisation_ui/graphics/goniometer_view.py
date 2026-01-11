"""
QGraphicsView for goniometer visualization.

Provides the view component that displays the GoniometerScene
and handles user interactions.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QGraphicsView

from .goniometer_scene import GoniometerScene


class GoniometerView(QGraphicsView):
    """
    Graphics view for displaying goniometer visualization.

    Provides zoom and pan capabilities, smooth rendering,
    and animation support.
    """

    def __init__(self, parent=None):
        """Initialize goniometer view."""
        super().__init__(parent)

        # Create and set scene
        self.scene_obj = GoniometerScene(width=500, height=400)
        self.setScene(self.scene_obj)

        # Configure rendering
        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        # Set view properties
        self.setMinimumSize(500, 400)
        self.setFocusPolicy(Qt.StrongFocus)

        # Zoom level
        self.zoom_level = 1.0

    def update_goniometer(self, probe_angle: float, detector_angle: float) -> None:
        """
        Update goniometer visualization.

        Args:
            probe_angle: Probe stage angle in degrees.
            detector_angle: Detector stage angle in degrees.
        """
        self.scene_obj.update_angles(probe_angle, detector_angle)

    def wheelEvent(self, event):
        """Handle mouse wheel zoom."""
        if event.modifiers() == Qt.ControlModifier:
            zoom_factor = 1.2 if event.angleDelta().y() > 0 else 0.8
            self.scale(zoom_factor, zoom_factor)
            self.zoom_level *= zoom_factor
            event.accept()
        else:
            super().wheelEvent(event)

    def reset_view(self) -> None:
        """Reset zoom and pan to default."""
        self.resetTransform()
        self.zoom_level = 1.0
        self.fitInView(self.scene_obj.itemsBoundingRect(), Qt.KeepAspectRatio)
