"""
Goniometer QGraphicsScene with animation support.

This module provides a scene for visualizing the dual-stage goniometer
and updates the visualization based on angle changes.
"""

from PySide6.QtCore import Qt, QTimer, QRect, QSize
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsScene, QGraphicsEllipseItem, QGraphicsTextItem

from .graphics_items import StageIndicator, DetectorArm, GoniometerLabel


class GoniometerScene(QGraphicsScene):
    """
    Graphics scene for goniometer visualization.

    Displays:
    - Probe stage (upper) with angle indicator
    - Detector arm (lower) with angle indicator
    - Relationship visualization showing 2x geometry
    """

    def __init__(self, width: int = 400, height: int = 300):
        """
        Initialize goniometer scene.

        Args:
            width: Scene width in pixels.
            height: Scene height in pixels.
        """
        super().__init__()
        self.setSceneRect(0, 0, width, height)
        self.setBackgroundBrush(QColor(250, 250, 250))

        # Create graphics items
        center_x = width / 2
        upper_y = height / 4
        lower_y = height * 3 / 4

        # Probe stage (upper)
        self.probe_stage = StageIndicator(radius=40, label="Probe")
        self.probe_stage.setPos(center_x, upper_y)
        self.addItem(self.probe_stage)

        # Probe label
        probe_label = GoniometerLabel("Sample (Probe)")
        probe_label.setPos(center_x - 50, upper_y - 70)
        self.addItem(probe_label)

        # Detector arm (lower stage)
        self.detector_arm = DetectorArm(arm_length=60)
        self.detector_arm.setPos(center_x, lower_y)
        self.addItem(self.detector_arm)

        # Detector label
        detector_label = GoniometerLabel("Detector Arm")
        detector_label.setPos(center_x - 50, lower_y + 50)
        self.addItem(detector_label)

        # Relationship indicator (showing 2x geometry)
        self.relationship_text = QGraphicsTextItem()
        self.relationship_text.setPos(center_x - 100, height - 40)
        font = self.relationship_text.font()
        font.setPointSize(11)
        self.relationship_text.setFont(font)
        self.relationship_text.setDefaultTextColor(QColor(0, 100, 0))
        self.addItem(self.relationship_text)

        # Connection line between stages
        self.connection_line = self.addLine(
            center_x, upper_y + 50, center_x, lower_y - 50, pen=self.get_grid_pen()
        )

    def update_angles(self, probe_angle: float, detector_angle: float) -> None:
        """
        Update both stage angles in the visualization.

        Args:
            probe_angle: Upper stage angle in degrees.
            detector_angle: Lower stage angle in degrees.
        """
        self.probe_stage.set_angle(probe_angle)
        self.detector_arm.set_angle(detector_angle)

        # Update relationship text
        ratio = detector_angle / probe_angle if probe_angle != 0 else 0
        self.relationship_text.setPlainText(
            f"Probe: {probe_angle:.1f}° | Detector: {detector_angle:.1f}° | Ratio: {ratio:.1f}x"
        )

    def set_probe_angle(self, angle: float) -> None:
        """
        Update only the probe stage angle.

        Args:
            angle: Probe angle in degrees.
        """
        self.probe_stage.set_angle(angle)

    def set_detector_angle(self, angle: float) -> None:
        """
        Update only the detector arm angle.

        Args:
            angle: Detector angle in degrees.
        """
        self.detector_arm.set_angle(angle)

    def get_grid_pen(self):
        """Get pen style for grid lines."""
        from PySide6.QtGui import QPen

        pen = QPen(QColor(200, 200, 200))
        pen.setStyle(Qt.DashLine)
        pen.setWidth(1)
        return pen
