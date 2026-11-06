"""Detect background workers that must not be torn down (profile switch)."""

from __future__ import annotations

from PySide6.QtCore import QObject, QThread
from shiboken6 import isValid


def has_running_thread(owner: QObject) -> bool:
    """True when ``owner`` holds a :class:`QThread` attribute that is still running.

    Covers the sweep, zero-find and calibration workers the windows and controllers keep.
    """
    return any(
        isinstance(value, QThread) and isValid(value) and value.isRunning()
        for value in vars(owner).values()
    )
