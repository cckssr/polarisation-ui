"""Fixtures for the controller tests: a simulated bench without any window."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from PySide6.QtCore import QObject

from polarisation_ui.infrastructure.config import AppConfig
from polarisation_ui.infrastructure.modules import ModuleRegistry
from polarisation_ui.ui.context import AppContext


@pytest.fixture
def ctx(qtbot, config: AppConfig) -> Iterator[AppContext]:
    """All controllers on the simulated bench (mock Arduino, KDC101, PM400); persistence off."""
    ModuleRegistry.clear()
    owner = QObject()
    context = AppContext.create(config, simulate=True, persist=False, parent=owner)
    yield context
    context.shutdown()
    ModuleRegistry.clear()
    owner.deleteLater()


@pytest.fixture
def port(ctx: AppContext) -> str:
    """The simulated Arduino's port."""
    assert ctx.simulation is not None
    return ctx.simulation.port


@pytest.fixture
def online(qtbot, ctx: AppContext, port: str) -> AppContext:
    """The context after the simulated Arduino connected and a first frame arrived."""
    with qtbot.waitSignal(ctx.data.frame_ready, timeout=5000):
        assert ctx.connection.connect_port(port)
    return ctx


class Recorder:
    """Collects the emissions of one signal for later assertions."""

    def __init__(self, signal) -> None:
        self.calls: list[tuple] = []
        signal.connect(lambda *args: self.calls.append(args))

    def __len__(self) -> int:
        return len(self.calls)

    def last(self) -> tuple:
        return self.calls[-1]


@pytest.fixture
def record():
    """Factory: ``rec = record(controller.some_signal)``."""
    return Recorder
