"""Tests for PM400PollWorker using MockPM400 — no real hardware.

Mirrors the pattern in tests/test_auto_power_calibration_worker.py: signals
are connected with a DirectConnection and collected into plain lists, then
worker.start() + worker.wait() blocks the test thread until the worker
QThread returns, so no running Qt event loop is required.
"""

import sys

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from polarisation_ui.infrastructure.mocks.mock_pm400 import MockPM400
from polarisation_ui.infrastructure.qt_threads import PM400PollWorker

_DIRECT = Qt.ConnectionType.DirectConnection

pytestmark = pytest.mark.skipif(
    sys.platform == "win32", reason="QThread timing is flaky on CI Windows"
)


@pytest.fixture(autouse=True)
def _qapp():
    yield QApplication.instance() or QApplication(sys.argv)


def _connected_mock() -> MockPM400:
    pm = MockPM400()
    pm.connect("mock://pm400")
    return pm


def test_emits_power_readings_while_connected():
    pm = _connected_mock()
    readings: list[float] = []

    worker = PM400PollWorker(pm)
    worker.power_read.connect(lambda w: readings.append(w), _DIRECT)
    worker.start()
    # Let a handful of poll ticks (100 ms each) happen, then stop cleanly.
    worker.msleep(350)
    worker.abort()
    worker.wait(2000)

    assert len(readings) >= 2
    assert all(r >= 0.0 for r in readings)


def test_abort_stops_worker_without_emitting_connection_lost():
    pm = _connected_mock()
    lost: list[str] = []

    worker = PM400PollWorker(pm)
    worker.connection_lost.connect(lambda m: lost.append(m), _DIRECT)
    worker.start()
    worker.msleep(50)
    worker.abort()
    assert worker.wait(2000), "worker did not stop promptly after abort()"
    assert lost == []


def test_disconnection_mid_poll_emits_connection_lost_after_three_failures():
    """MockPM400.read_power_W() raises PM400Error once disconnected — the
    worker must tolerate transient glitches but declare the meter lost after
    _DISCONNECT_THRESHOLD consecutive failures, mirroring the Arduino-side
    disconnection-path convention required by the testing guidelines."""
    pm = _connected_mock()
    lost: list[str] = []
    readings: list[float] = []

    worker = PM400PollWorker(pm)
    worker.power_read.connect(lambda w: readings.append(w), _DIRECT)
    worker.connection_lost.connect(lambda m: lost.append(m), _DIRECT)
    worker.start()
    worker.msleep(150)  # at least one good reading first
    pm.disconnect()  # simulate an unplug mid-poll
    ok = worker.wait(5000)

    assert ok, "worker never returned after simulated disconnect"
    assert len(readings) >= 1, "should have at least one reading before the disconnect"
    assert len(lost) == 1
    assert "not connected" in lost[0].lower()
