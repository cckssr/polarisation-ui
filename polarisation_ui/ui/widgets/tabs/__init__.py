"""Experiment tab package — importing this module registers every tab with TabRegistry."""

from polarisation_ui.ui.widgets.tab_registry import TabRegistry
from polarisation_ui.ui.widgets.tabs.brewster_tab import BrewsterTab
from polarisation_ui.ui.widgets.tabs.malus_tab import MalusTab
from polarisation_ui.ui.widgets.tabs.power_drift_tab import PowerDriftTab
from polarisation_ui.ui.widgets.tabs.waveplate_tab import WaveplateTab

TabRegistry.register(BrewsterTab)
TabRegistry.register(MalusTab)
TabRegistry.register(WaveplateTab)
TabRegistry.register(PowerDriftTab)
