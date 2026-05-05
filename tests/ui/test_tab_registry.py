"""
Tests for TabRegistry and PlotTabBase.

These tests run headless (no display required) because they only exercise
registration logic and the on_frame / on_reset hooks — no pyqtgraph widgets
are constructed.
"""

import pytest

from polarisation_ui.core.models import Frame
from polarisation_ui.ui.widgets.plot_tab_base import ConnState, PlotTabBase
from polarisation_ui.ui.widgets.tab_registry import TabRegistry


# ---------------------------------------------------------------------------
# Stub tabs
# ---------------------------------------------------------------------------

class _StubTab(PlotTabBase):
    tab_id = "stub"
    tab_title = "Stub"
    required_sources: set[str] = {"ENC:BOTH"}
    required_modules: set[str] = set()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.built = False
        self.frames: list[Frame] = []
        self.resets = 0
        self.conn_states: list[ConnState] = []

    def build(self) -> None:
        self.built = True

    def on_frame(self, frame: Frame) -> None:
        self.frames.append(frame)

    def on_reset(self) -> None:
        self.resets += 1

    def on_connection_state(self, state: ConnState) -> None:
        self.conn_states.append(state)


class _KdcTab(PlotTabBase):
    tab_id = "kdc_stub"
    tab_title = "KDC"
    required_sources: set[str] = set()
    required_modules: set[str] = {"kdc101"}

    def build(self) -> None:
        pass


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _clean_registry():
    """Isolate each test by clearing the registry before and after."""
    TabRegistry.clear()
    yield
    TabRegistry.clear()


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

def test_register_once():
    TabRegistry.register(_StubTab)
    assert TabRegistry.all() == [_StubTab]


def test_register_idempotent():
    TabRegistry.register(_StubTab)
    TabRegistry.register(_StubTab)
    assert len(TabRegistry.all()) == 1


def test_registration_order():
    TabRegistry.register(_StubTab)
    TabRegistry.register(_KdcTab)
    assert TabRegistry.all() == [_StubTab, _KdcTab]


# ---------------------------------------------------------------------------
# available() filtering by required_modules
# ---------------------------------------------------------------------------

def test_available_no_modules():
    TabRegistry.register(_StubTab)
    TabRegistry.register(_KdcTab)
    available = TabRegistry.available(modules={})
    assert _StubTab in available
    assert _KdcTab not in available


def test_available_with_kdc_module():
    TabRegistry.register(_StubTab)
    TabRegistry.register(_KdcTab)
    available = TabRegistry.available(modules={"kdc101": object()})
    assert _StubTab in available
    assert _KdcTab in available


# ---------------------------------------------------------------------------
# Lifecycle hooks
# ---------------------------------------------------------------------------

def test_on_frame_receives_data(qtbot):
    tab = _StubTab()
    tab.build()
    assert tab.built

    frame = Frame(ts_ms=100, sample_angle=10.0, detector_angle=20.0, intensity=0.5)
    tab.on_frame(frame)
    assert len(tab.frames) == 1
    assert tab.frames[0].sample_angle == 10.0


def test_on_reset_increments_counter(qtbot):
    tab = _StubTab()
    tab.build()
    tab.on_reset()
    tab.on_reset()
    assert tab.resets == 2


def test_on_connection_state(qtbot):
    tab = _StubTab()
    tab.on_connection_state(ConnState.CONNECTED)
    tab.on_connection_state(ConnState.RECONNECTING)
    tab.on_connection_state(ConnState.LOST)
    assert tab.conn_states == [
        ConnState.CONNECTED,
        ConnState.RECONNECTING,
        ConnState.LOST,
    ]


# ---------------------------------------------------------------------------
# status_message signal
# ---------------------------------------------------------------------------

def test_status_message_signal(qtbot):
    tab = _StubTab()
    messages: list[tuple[str, str]] = []
    tab.status_message.connect(lambda level, msg: messages.append((level, msg)))

    tab.status_message.emit("warning", "test warning")
    assert messages == [("warning", "test warning")]
