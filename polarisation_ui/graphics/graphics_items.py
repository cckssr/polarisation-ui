"""
Graphics items for visualizing goniometer components.

This module contains QGraphicsItem subclasses for rendering
the probe stage, detector arm, and associated labels.
"""

from PySide6.QtCore import Qt, QPointF, QRect
from PySide6.QtGui import QPainter, QPen, QColor, QBrush
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsTextItem,
)


class StageIndicator(QGraphicsItem):
    """
    Represents a rotational stage indicator.

    Shows the current angle of a stage with a rotating arm.
    """

    def __init__(self, radius: float = 50.0, label: str = "Stage"):
        """
        Initialize stage indicator.

        Args:
            radius: Radius of the stage circle in pixels.
            label: Text label for the stage.
        """
        super().__init__()
        self.radius = radius
        self.label = label
        self.angle = 0.0  # Current angle in degrees
        self.setAcceptHoverEvents(False)

    def set_angle(self, angle: float) -> None:
        """
        Update the displayed angle.

        Args:
            angle: Angle in degrees.
        """
        self.angle = angle
        self.update()  # Trigger repaint

    def boundingRect(self) -> QRect:
        """Define bounding rectangle for drawing."""
        r = self.radius
        return QRect(-int(r), -int(r), int(2 * r), int(2 * r))

    def paint(self, painter: QPainter, option, widget) -> None:
        """Draw the stage indicator."""
        # Draw circle background
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.setBrush(QBrush(QColor(240, 240, 240)))
        painter.drawEllipse(QPointF(0, 0), self.radius, self.radius)

        # Draw angle indicator (arm)
        painter.setPen(QPen(QColor(0, 0, 200), 3))
        arm_length = self.radius * 0.85

        # Convert angle to radians and draw arm
        import math

        rad = math.radians(self.angle)
        end_x = arm_length * math.cos(rad)
        end_y = arm_length * math.sin(rad)

        painter.drawLine(QPointF(0, 0), QPointF(end_x, end_y))

        # Draw center point
        painter.setPen(QPen(QColor(0, 0, 0), 1))
        painter.setBrush(QBrush(QColor(0, 0, 0)))
        painter.drawEllipse(QPointF(0, 0), 3, 3)

        # Draw angle text
        painter.setPen(QPen(QColor(0, 0, 0)))
        font = painter.font()
        font.setPointSize(10)
        painter.setFont(font)
        painter.drawText(
            QRect(-self.radius, self.radius + 5, self.radius * 2, 20),
            Qt.AlignCenter,
            f"{self.angle:.1f}°",
        )


class DetectorArm(QGraphicsItem):
    """
    Represents the detector arm attached to the lower stage.

    Shows the detector position relative to the lower stage angle.
    """

    def __init__(self, arm_length: float = 80.0):
        """
        Initialize detector arm.

        Args:
            arm_length: Length of the arm in pixels.
        """
        super().__init__()
        self.arm_length = arm_length
        self.angle = 0.0  # Current angle in degrees
        self.setAcceptHoverEvents(False)

    def set_angle(self, angle: float) -> None:
        """
        Update the detector arm angle.

        Args:
            angle: Angle in degrees.
        """
        self.angle = angle
        self.update()

    def boundingRect(self) -> QRect:
        """Define bounding rectangle."""
        r = int(self.arm_length) + 20
        return QRect(-r, -r, 2 * r, 2 * r)

    def paint(self, painter: QPainter, option, widget) -> None:
        """Draw the detector arm."""
        import math

        # Draw arm
        painter.setPen(QPen(QColor(200, 0, 0), 4))
        rad = math.radians(self.angle)
        end_x = self.arm_length * math.cos(rad)
        end_y = self.arm_length * math.sin(rad)

        painter.drawLine(QPointF(0, 0), QPointF(end_x, end_y))

        # Draw detector (circle at arm end)
        painter.setPen(QPen(QColor(200, 0, 0), 2))
        painter.setBrush(QBrush(QColor(255, 100, 100)))
        detector_size = 8
        painter.drawEllipse(QPointF(end_x, end_y), detector_size, detector_size)

        # Draw mounting point
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.setBrush(QBrush(QColor(100, 100, 100)))
        painter.drawEllipse(QPointF(0, 0), 4, 4)


class GoniometerLabel(QGraphicsTextItem):
    """Simple text label for goniometer components."""

    def __init__(self, text: str = ""):
        """Initialize label."""
        super().__init__(text)
        font = self.font()
        font.setPointSize(12)
        font.setBold(True)
        self.setFont(font)
