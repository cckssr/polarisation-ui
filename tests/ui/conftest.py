"""Fixtures shared by the UI tests."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from PySide6.QtCore import QSettings

from polarisation_ui.infrastructure.config import AppConfig, load_config, reset_default_config
from polarisation_ui.infrastructure.modules import ModuleRegistry
from polarisation_ui.ui.plot_style import set_plot_colors
from polarisation_ui.ui.windows import main_window as main_window_module
from polarisation_ui.ui.windows.main_window import MainWindow

# Fast timings so simulated frames arrive quickly and a lost link is declared within a second.
FAST_SIM = {
    "timers": {"acquisition_timer_interval": 20},
    "connection": {"max_retry_attempts": 2, "backoff_delays_ms": [30, 30]},
}


@pytest.fixture
def config() -> AppConfig:
    """The packaged configuration (expert profile) with fast simulation timings."""
    return load_config(overrides=FAST_SIM)


@pytest.fixture(autouse=True)
def layout_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Keep the window layout of every test out of the user's real settings."""
    path = tmp_path / "layout.ini"
    monkeypatch.setattr(
        main_window_module,
        "layout_settings",
        lambda: QSettings(str(path), QSettings.Format.IniFormat),
    )
    return path


@pytest.fixture(autouse=True)
def _fresh_config_state() -> Iterator[None]:
    """Keep tests that swap the cached default config or the plot colours independent."""
    reset_default_config()
    set_plot_colors(None)
    yield
    reset_default_config()
    set_plot_colors(None)


@pytest.fixture
def window(qtbot, config: AppConfig) -> Iterator[MainWindow]:
    """A main window on the simulated bench; touches no user files."""
    ModuleRegistry.clear()
    win = MainWindow(config, simulate=True, persist=False)
    qtbot.addWidget(win)
    win.show()
    yield win
    win.close()
    ModuleRegistry.clear()


@pytest.fixture
def connected(qtbot, window: MainWindow) -> MainWindow:
    """The window after the simulated Arduino connected and the first frame arrived."""
    with qtbot.waitSignal(window.ctx.data.frame_ready, timeout=5000):
        window.ui.arduinoPanel.ui.buttonConnect.click()
    assert window.ctx.connection.is_connected
    return window
