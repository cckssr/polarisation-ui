"""Experiment tabs in the central ``QTabWidget``: registry gating, wiring and fan-out.

``TabHost`` adds the tabs the ``TabRegistry`` offers for the registered host modules, keeps them in
sync with module changes (e.g. WaveplateTab once the KDC101 connects), gates them on the group
selection and forwards the measurement and connection events to every tab. The tab widget itself
(and its first "Konfiguration" page) is declared in the main window's Designer form.
"""

from __future__ import annotations

from dataclasses import asdict

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWidgets import QTabWidget

from polarisation_ui.core.models import TabExport
from polarisation_ui.infrastructure.config import AppConfig
from polarisation_ui.infrastructure.modules import ModuleRegistry
from polarisation_ui.ui.controllers.data_controller import DataController
from polarisation_ui.ui.widgets.plot_tab_base import ConnState, PlotTabBase
from polarisation_ui.ui.widgets.tab_registry import TabRegistry

# Page 0 of the tab widget is the configuration page; only the pages after it are experiments.
CONFIG_PAGE_COUNT = 1


class TabHost(QObject):
    """Owns the experiment tab instances of one main window."""

    status_message = Signal(str, str)  # level, text — from any tab
    filename_hint_changed = Signal()
    points_changed = Signal(int)
    active_tab_changed = Signal()  # another page became current
    sources_changed = Signal()  # the set of visible tabs (and so the stream sources) changed

    def __init__(
        self,
        tab_widget: QTabWidget,
        config: AppConfig,
        data: DataController,
        parent: QObject | None = None,
    ) -> None:
        """Wrap ``tab_widget``; call :meth:`build` to add the available tabs."""
        super().__init__(parent)
        self._tabs_widget = tab_widget
        self._cfg = config
        self._data = data
        self._tabs: list[PlotTabBase] = []
        self._group_selected = False
        tab_widget.currentChanged.connect(self._on_current_changed)

    @property
    def tabs(self) -> list[PlotTabBase]:
        """All instantiated tabs (visible or not)."""
        return list(self._tabs)

    # ---- building ------------------------------------------------------------------------
    def build(self) -> None:
        """Instantiate every tab the registry offers for the registered modules."""
        import polarisation_ui.ui.widgets.tabs  # NOQA: F401  (registers the tab classes)

        modules = ModuleRegistry.all()
        for tab_cls in TabRegistry.available(modules=modules):
            self._add_tab(tab_cls, modules)

    def _add_tab(self, tab_cls: type[PlotTabBase], modules: dict[str, object]) -> PlotTabBase:
        """Instantiate one tab, wire its standard signals and append it to the widget."""
        tab = tab_cls(config=self._cfg)
        tab.build()
        tab.status_message.connect(self.status_message)
        tab.filename_hint_changed.connect(self.filename_hint_changed)
        points_changed = getattr(tab, "points_changed", None)
        if points_changed is not None:
            points_changed.connect(self.points_changed)
        self._data.frame_ready.connect(tab.on_frame)
        index = self._tabs_widget.addTab(tab, tab.tab_title)
        self._tabs.append(tab)
        tab.inject_modules(modules)
        # Tabs added after startup must respect the current group gate.
        self._apply_group_gating(index)
        return tab

    @Slot()
    def refresh_visibility(self) -> None:
        """Re-evaluate the tabs after a module (un)registered.

        Tabs whose ``required_modules`` are no longer met are hidden, newly satisfied tabs are
        added; satisfied tabs keep their state.
        """
        modules = ModuleRegistry.all()
        available = TabRegistry.available(modules=modules)
        available_ids = {cls.tab_id for cls in available}
        existing_ids = {tab.tab_id for tab in self._tabs}

        for tab in self._tabs:
            tab.inject_modules(modules)
        for tab_cls in available:
            if tab_cls.tab_id not in existing_ids:
                self._add_tab(tab_cls, modules)
        for tab in self._tabs:
            idx = self._tabs_widget.indexOf(tab)
            if idx >= 0:
                self._tabs_widget.setTabVisible(idx, tab.tab_id in available_ids)
        self.sources_changed.emit()

    def required_sources(self) -> set[str]:
        """Union of the ``required_sources`` of all visible tabs (for ``CONF:SRC``)."""
        sources: set[str] = set()
        for tab in self._tabs:
            idx = self._tabs_widget.indexOf(tab)
            if idx >= 0 and self._tabs_widget.isTabVisible(idx):
                sources |= tab.required_sources
        return sources

    # ---- group gating --------------------------------------------------------------------
    @Slot(bool)
    def set_group_selected(self, selected: bool) -> None:
        """Enable or disable the experiment tabs depending on whether a group is selected."""
        self._group_selected = selected
        for i in range(CONFIG_PAGE_COUNT, self._tabs_widget.count()):
            self._apply_group_gating(i)
        if not selected and self._tabs_widget.currentIndex() >= CONFIG_PAGE_COUNT:
            self._tabs_widget.setCurrentIndex(0)

    def _apply_group_gating(self, tab_index: int) -> None:
        if tab_index < CONFIG_PAGE_COUNT:
            return  # the configuration page is always accessible
        tooltip = "" if self._group_selected else self._cfg.text("mainwindow.tab_group_required")
        self._tabs_widget.setTabEnabled(tab_index, self._group_selected)
        self._tabs_widget.setTabToolTip(tab_index, tooltip)

    # ---- fan-out -------------------------------------------------------------------------
    @Slot(str)
    def notify_link_state(self, state: str) -> None:
        """Forward the Arduino link state ("connected"/"reconnecting"/"lost") to every tab."""
        for tab in self._tabs:
            tab.on_connection_state(ConnState(state))

    @Slot()
    def on_measurement_started(self) -> None:
        """Tell every tab a measurement began."""
        for tab in self._tabs:
            tab.on_measurement_started()

    @Slot()
    def on_measurement_stopped(self) -> None:
        """Tell every tab a measurement ended."""
        for tab in self._tabs:
            tab.on_measurement_stopped()

    @Slot()
    def reset_all(self) -> None:
        """Clear the data of every tab."""
        for tab in self._tabs:
            tab.on_reset()

    @Slot(int)
    def _on_current_changed(self, index: int) -> None:
        for tab in self._tabs:
            if self._tabs_widget.indexOf(tab) == index:
                tab.on_activated()
            else:
                tab.on_deactivated()
        self.active_tab_changed.emit()

    # ---- export / session ----------------------------------------------------------------
    def active_export_tab(self) -> PlotTabBase | None:
        """The current tab if it exposes the export contract, else None."""
        idx = self._tabs_widget.currentIndex()
        if idx < 0:
            return None
        widget = self._tabs_widget.widget(idx)
        tab = next((t for t in self._tabs if t is widget), None)
        if tab is not None and hasattr(tab, "build_export") and hasattr(tab, "get_saved_points"):
            return tab
        return None

    def active_export(self) -> TabExport | None:
        """Export bundle of the active tab (None when it has no export contract)."""
        tab = self.active_export_tab()
        return tab.build_export() if tab is not None else None

    def active_tab_has_points(self) -> bool:
        """True when the active tab holds saved points (Save is enabled)."""
        tab = self.active_export_tab()
        return tab is not None and len(tab.get_saved_points()) > 0

    def saved_points(self) -> dict[str, list[dict]]:
        """Saved points of every tab as ``{tab_id: [dicts]}`` (session state)."""
        points: dict[str, list[dict]] = {}
        for tab in self._tabs:
            if hasattr(tab, "get_saved_points"):
                pts = tab.get_saved_points()
                if pts:
                    points[tab.tab_id] = [asdict(p) for p in pts]
        return points

    @Slot(dict)
    def restore_points(self, points: dict[str, list[dict]]) -> None:
        """Reload saved points into the matching tabs."""
        for tab in self._tabs:
            pts = points.get(tab.tab_id, [])
            if pts:
                tab.restore_points(pts)
