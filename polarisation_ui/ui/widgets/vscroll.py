"""Side columns scroll vertically only: the minimum width follows the content."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QScrollArea


def lock_vertical_scroll(scroll: QScrollArea) -> int:
    """Lock ``scroll`` to vertical scrolling and return its new minimum width.

    The area never shows a horizontal scrollbar; its minimum width is the content's minimum
    width plus the vertical scrollbar and frame.
    """
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    content = scroll.widget()
    content.setMinimumWidth(0)
    width = (
        content.minimumSizeHint().width()
        + scroll.verticalScrollBar().sizeHint().width()
        + 2 * scroll.frameWidth()
    )
    scroll.setMinimumWidth(width)
    return width
