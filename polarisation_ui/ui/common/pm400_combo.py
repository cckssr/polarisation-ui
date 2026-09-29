"""Populate a PM400 resource dropdown from the currently attached devices."""

from __future__ import annotations

from PySide6.QtWidgets import QComboBox

from polarisation_ui.infrastructure.devices.pm400 import PM400PowerMeter


def populate_pm400_combo(combo: QComboBox, preferred: str = "") -> list[str]:
    """Fill *combo* with the VISA resources found right now and return them.

    Only discovered devices are listed — a remembered resource string that is
    no longer attached is never re-added, so a stale address cannot be picked
    by accident. Selection order: the current entry, then *preferred* (the
    last-used resource), then the first device.
    """
    wanted = combo.currentText() or preferred
    resources = PM400PowerMeter.list_resources()
    combo.clear()
    combo.addItems(resources)
    if not resources:
        combo.setPlaceholderText("Kein PM400 gefunden")
        return resources
    idx = combo.findText(wanted)
    combo.setCurrentIndex(idx if idx >= 0 else 0)
    return resources
