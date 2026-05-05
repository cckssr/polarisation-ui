"""
Registry for PlotTabBase subclasses.

Import tabs/__init__.py to trigger registrations before calling TabRegistry.all().
"""

from __future__ import annotations

from polarisation_ui.ui.widgets.plot_tab_base import PlotTabBase


class TabRegistry:
    _tabs: list[type[PlotTabBase]] = []

    @classmethod
    def register(cls, tab_class: type[PlotTabBase]) -> None:
        if tab_class not in cls._tabs:
            cls._tabs.append(tab_class)

    @classmethod
    def all(cls) -> list[type[PlotTabBase]]:
        return list(cls._tabs)

    @classmethod
    def available(cls, modules: dict[str, object]) -> list[type[PlotTabBase]]:
        """Return tabs whose required_modules are all present in `modules`."""
        return [t for t in cls._tabs if t.required_modules.issubset(modules.keys())]

    @classmethod
    def clear(cls) -> None:
        """Remove all registrations (for use in tests)."""
        cls._tabs.clear()
