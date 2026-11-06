"""Fixtures shared by the UI tests."""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from polarisation_ui.infrastructure.config import AppConfig, load_config, reset_default_config
from polarisation_ui.ui.plot_style import set_plot_colors


@pytest.fixture
def config() -> AppConfig:
    """The packaged configuration (expert profile)."""
    return load_config()


@pytest.fixture(autouse=True)
def _fresh_config_state() -> Iterator[None]:
    """Keep tests that swap the cached default config or the plot colours independent."""
    reset_default_config()
    set_plot_colors(None)
    yield
    reset_default_config()
    set_plot_colors(None)
