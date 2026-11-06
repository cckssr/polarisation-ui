"""Profiles (``profiles`` in config.json): hide the tabs and widgets a profile does not need.

The renamed texts of a profile are plain ``ui`` overrides merged by ``load_config``; this module
only hides things. Widgets and toolbar actions are addressed by Designer object name below a
*root*: the main window, one of the dock panels (``arduino_panel``, ``detector_panel`` ...) or a
tab id (``malus``). Tabs listed in ``hidden_tabs`` are never instantiated (see ``TabHost``).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QObject
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QBoxLayout, QWidget

from polarisation_ui.infrastructure.logging import Debug
from polarisation_ui.ui.widgets.tab_registry import TabRegistry

if TYPE_CHECKING:
    from polarisation_ui.ui.windows.main_window import MainWindow


def profile_roots(window: MainWindow) -> dict[str, QObject]:
    """The objects ``hidden_widgets`` may refer to (tabs the profile leaves out are missing)."""
    ui = window.ui
    roots: dict[str, QObject] = {
        "main_window": window,
        "arduino_panel": ui.arduinoPanel,
        "sample_stage_panel": ui.sampleStagePanel,
        "detector_stage_panel": ui.detectorStagePanel,
        "kdc_panel": ui.kdcPanel,
        "detector_panel": ui.detectorPanel,
        "readout_panel": ui.readoutPanel,
        "measurement_panel": ui.measurementPanel,
        "save_panel": ui.savePanel,
    }
    roots.update({tab.tab_id: tab for tab in window.tabs.tabs})
    return roots


def _keep_rows_left_aligned(root: QObject, hidden: QWidget) -> None:
    """Keep a row left-aligned after hiding ``hidden``.

    A box layout row whose only stretching item is now hidden would spread the remaining items
    over the whole width: give the row a trailing stretch instead.
    """
    for layout in root.findChildren(QBoxLayout):
        index = layout.indexOf(hidden)
        if index < 0 or layout.stretch(index) <= 0:
            continue

        def stretches(i: int, layout: QBoxLayout = layout) -> bool:
            if layout.stretch(i) <= 0:
                return False
            widget = layout.itemAt(i).widget()
            return widget is None or not widget.isHidden()  # a spacer or a visible widget

        if not any(stretches(i) for i in range(layout.count()) if i != index):
            layout.addStretch(1)


def apply_profile(window: MainWindow) -> list[str]:
    """Hide the widgets of the active profile.

    Returns the names that could not be found (``root.name``), which are also logged: a typo
    must not pass silently.
    """
    cfg = window.config
    roots = profile_roots(window)
    missing: list[str] = []
    # tabs that exist but are not instantiated (hidden by the profile or waiting for a module)
    known_tabs = {cls.tab_id for cls in TabRegistry.all()}
    for root_name, names in cfg.hidden_widgets().items():
        root = roots.get(root_name)
        if root is None:
            if root_name not in cfg.hidden_tabs() and root_name not in known_tabs:
                Debug.warning(f"profile {cfg.profile!r}: unknown root {root_name!r}")
                missing.append(root_name)
            continue
        for name in names:
            target = root.findChild(QObject, name)
            if isinstance(target, (QWidget, QAction)):
                target.setVisible(False)
                if isinstance(target, QWidget):
                    _keep_rows_left_aligned(root, target)
            else:
                Debug.warning(f"profile {cfg.profile!r}: no widget {name!r} in {root_name!r}")
                missing.append(f"{root_name}.{name}")
    return missing


def next_profile(current: str, names: list[str]) -> str:
    """The profile the switch action leads to (cycles through ``names``)."""
    if current not in names or len(names) < 2:
        return current
    return names[(names.index(current) + 1) % len(names)]
