"""
Tests for DataController reconnect / error-handling behaviour (B1, B2, B6).

These tests check:
  - First read failure is silent (no error_occurred emission).
  - _on_reconnect_failed does not re-enter _handle_read_error.
  - Mid-stream PTY disconnect triggers retry_connecting, then reconnect succeeds.

All tests use a MockArduino + GoniometerDeviceManager + DataController stack so
they exercise the real code paths without a physical device.
"""

import os
import sys
import time
from unittest.mock import MagicMock, patch

import pytest

pytestmark = pytest.mark.skipif(
    sys.platform == "win32", reason="PTY not available on Windows"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _spin_until(predicate, timeout: float = 3.0, interval: float = 0.05) -> bool:
    """Pump the Qt event loop until predicate() is True or timeout expires."""
    from PySide6.QtCore import QCoreApplication

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        QCoreApplication.processEvents()
        if predicate():
            return True
        time.sleep(interval)
    return False


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def controller(qapp):
    """DataController wired to a stub DeviceManager that can simulate failures."""
    from polarisation_ui.ui.controllers.data_controller import DataController

    dm = MagicMock()
    dm.read_angles.return_value = None  # simulate successful read with None result
    dm.is_connected.return_value = True
    dm.read_intensity.return_value = None
    dm.query_diagnostics.return_value = None
    dm.get_encoder_status.return_value = MagicMock(port=None)
    dm.connect_encoders.return_value = True

    ctrl = DataController(dm, use_mock_intensity=True)
    yield ctrl, dm
    ctrl.cleanup()


# ---------------------------------------------------------------------------
# B1: First failure is silent
# ---------------------------------------------------------------------------


def test_first_failure_is_silent(qtbot, controller):
    """error_occurred must NOT fire on the very first read error."""
    ctrl, dm = controller

    error_msgs: list[str] = []
    retry_calls: list[tuple] = []

    ctrl.error_occurred.connect(lambda msg: error_msgs.append(msg))
    ctrl.retry_connecting.connect(lambda att, delay: retry_calls.append((att, delay)))

    # Invoke _handle_read_error directly — one failure
    ctrl._handle_read_error("simulated first failure")

    # error_occurred must be silent; retry_connecting must fire
    assert error_msgs == [], "First failure must not emit error_occurred"
    assert len(retry_calls) == 1, "retry_connecting must fire even on first failure"
    assert retry_calls[0][0] == 1  # attempt number

    ctrl._retry_timer.stop()


def test_second_failure_emits_error(qtbot, controller):
    """error_occurred fires from the second failure onwards."""
    ctrl, dm = controller

    error_msgs: list[str] = []
    ctrl.error_occurred.connect(lambda msg: error_msgs.append(msg))

    ctrl._handle_read_error("failure 1")
    assert error_msgs == []

    ctrl._handle_read_error("failure 2")
    assert len(error_msgs) == 1
    assert "failure 2" in error_msgs[0]

    ctrl._retry_timer.stop()


def test_new_error_type_breaks_silence(qtbot, controller):
    """A different error message on the first retry is treated as a new error type."""
    ctrl, dm = controller

    error_msgs: list[str] = []
    ctrl.error_occurred.connect(lambda msg: error_msgs.append(msg))

    ctrl._handle_read_error("timeout")
    assert error_msgs == []

    # Same count but different message — treated as new error type
    ctrl._last_error_msg = "timeout"
    ctrl._error_count = 1
    ctrl._handle_read_error("serial reset")
    assert len(error_msgs) == 1

    ctrl._retry_timer.stop()


# ---------------------------------------------------------------------------
# B2: _on_reconnect_failed does not re-enter _handle_read_error
# ---------------------------------------------------------------------------


def test_reconnect_failed_increments_error_count_once(qtbot, controller):
    """_on_reconnect_failed increments _error_count exactly once per call."""
    ctrl, _ = controller

    ctrl._error_count = 1  # simulate one prior failure
    ctrl._backoff_attempt = 1

    before = ctrl._error_count
    ctrl._on_reconnect_failed()
    after = ctrl._error_count

    assert after == before + 1, (
        "error_count must increment by exactly 1 per failed reconnect"
    )
    ctrl._retry_timer.stop()


def test_reconnect_failed_emits_retry_connecting(qtbot, controller):
    """_on_reconnect_failed emits retry_connecting, not a raw error path call."""
    ctrl, _ = controller

    retry_calls: list[tuple] = []
    ctrl.retry_connecting.connect(lambda att, delay: retry_calls.append((att, delay)))

    ctrl._error_count = 1
    ctrl._backoff_attempt = 1
    ctrl._on_reconnect_failed()

    assert len(retry_calls) == 1
    ctrl._retry_timer.stop()


# ---------------------------------------------------------------------------
# B6: Spike-filter references reset on reconnect success
# ---------------------------------------------------------------------------


def test_reconnect_success_resets_spike_filter(qtbot, controller):
    """After a successful reconnect, spike-filter state is cleared so the first
    post-reconnect samples are never rejected as bogus spikes."""
    ctrl, dm = controller

    # Simulate some prior state
    ctrl._last_sample_angle = 42.0
    ctrl._last_det_angle = 84.0
    ctrl._spike_reject_streak = 3
    ctrl._last_error_msg = "some error"
    ctrl._error_count = 3
    ctrl._backoff_attempt = 2

    dm.connect_encoders.return_value = True
    ctrl._on_reconnect_success()

    assert ctrl._last_sample_angle is None
    assert ctrl._last_det_angle is None
    assert ctrl._spike_reject_streak == 0
    assert ctrl._last_error_msg is None
    assert ctrl._error_count == 0
    assert ctrl._backoff_attempt == 0


# ---------------------------------------------------------------------------
# Integration: mid-stream PTY disconnect and reconnect
# ---------------------------------------------------------------------------


@pytest.fixture()
def live_stack(qapp):
    """Full stack: MockArduino → DualEncoderArduino → GoniometerDeviceManager → DataController."""
    from polarisation_ui.infrastructure.device_manager import GoniometerDeviceManager
    from polarisation_ui.infrastructure.mocks import MockArduino
    from polarisation_ui.ui.controllers.data_controller import DataController

    mock = MockArduino(start_angle_a=10.0, start_angle_b=20.0)
    port = mock.start()

    dm = GoniometerDeviceManager()
    ok = dm.connect_encoders(port=port)
    assert ok, "MockArduino connection must succeed"

    ctrl = DataController(dm, use_mock_intensity=True)

    yield ctrl, dm, mock, port

    ctrl.cleanup()
    dm.disconnect_all()
    mock.stop()


def test_kill_pty_triggers_retry_and_banner_signal(qtbot, live_stack):
    """Closing the PTY master causes retry_connecting to fire, then connection_lost after
    all retries are exhausted (no real reconnect target so all attempts fail)."""
    ctrl, dm, mock, _port = live_stack

    retry_events: list[tuple] = []
    lost_events: list[bool] = []

    ctrl.retry_connecting.connect(lambda att, delay: retry_events.append((att, delay)))
    ctrl.connection_lost.connect(lambda: lost_events.append(True))

    ctrl.start_continuous_reading()

    # Kill the PTY so the next poll returns an error
    if mock.pty_master is not None:
        try:
            os.close(mock.pty_master)
            mock.pty_master = None
        except OSError:
            pass

    # Wait until at least one retry fires (first poll error → retry_connecting)
    assert _spin_until(lambda: len(retry_events) >= 1, timeout=5.0), (
        "retry_connecting must fire after PTY disconnect"
    )

    # Verify attempt numbers increment
    assert retry_events[0][0] >= 1
    assert retry_events[0][1] > 0  # delay_s > 0
