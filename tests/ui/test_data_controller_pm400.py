"""Tests for DataController's PM400 detector-precedence integration.

PM400 readings arrive via PM400PollWorker on a background QThread, so tests
that need a fresh reading pump the Qt event loop (queued cross-thread signal
delivery) rather than calling _poll_sensors() immediately after set_pm400().
"""

import sys
import time
from unittest.mock import MagicMock

import pytest

from polarisation_ui.core.detector import DETECTOR_PDTIA, DETECTOR_PM400
from polarisation_ui.infrastructure.mocks.mock_pm400 import MockPM400

pytestmark = pytest.mark.skipif(
    sys.platform == "win32", reason="QThread timing is flaky on CI Windows"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _spin_until(predicate, timeout: float = 5.0, interval: float = 0.02) -> bool:
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
def tmp_journal_base(tmp_path, monkeypatch):
    """Redirect JOURNAL_BASE to a temp directory so tests don't touch ~/.polarisation-ui."""
    import polarisation_ui.infrastructure.session_journal as sj_mod

    monkeypatch.setattr(sj_mod, "JOURNAL_BASE", tmp_path / "sessions")


@pytest.fixture()
def controller(qapp, tmp_journal_base):
    """DataController wired to a stub DeviceManager that reports valid angles/firmware."""
    from polarisation_ui.ui.controllers.data_controller import DataController

    dm = MagicMock()
    dm.is_encoder_connected.return_value = True
    dm.read_angles.return_value = MagicMock(sample_angle=10.0, detector_angle=20.0)
    dm.get_firmware_version.return_value = "2.1.0"
    dm.get_desired_state.return_value.as_config_snapshot.return_value = {}

    ctrl = DataController(dm, use_mock_intensity=True)
    yield ctrl
    ctrl.cleanup()


def _connected_mock_pm400() -> MockPM400:
    pm = MockPM400()
    pm.connect("mock://pm400")
    return pm


# ---------------------------------------------------------------------------
# set_pm400 / clear_pm400 precedence
# ---------------------------------------------------------------------------


def test_frame_reports_pm400_as_detector_once_a_reading_arrives(controller):
    ctrl = controller
    detector_changes: list[str] = []
    ctrl.active_detector_changed.connect(detector_changes.append)

    pm = _connected_mock_pm400()
    ctrl.set_pm400(pm)

    assert detector_changes == [DETECTOR_PM400]
    assert ctrl.is_pm400_active

    # Wait for the background poll worker to deliver at least one reading.
    assert _spin_until(lambda: ctrl._pm400_power_W is not None), "no PM400 reading arrived"

    frames: list = []
    ctrl.frame_ready.connect(frames.append)
    ctrl._poll_sensors()

    assert len(frames) == 1
    assert frames[0].detector == DETECTOR_PM400
    assert frames[0].power_W is not None
    assert frames[0].power_W >= 0.0
    # PM400 measures power directly — no PD-TIA voltage-based conversion factor.
    assert frames[0].conv_factor_W_per_V is None


def test_stale_pm400_reading_yields_none_power_but_stays_active_detector(controller):
    """A cached reading older than _PM400_STALE_S must not be reported as current."""
    ctrl = controller
    pm = _connected_mock_pm400()
    ctrl.set_pm400(pm)
    # Force staleness without waiting for the real 1 s window.
    ctrl._pm400_last_ts = 0.0

    frames: list = []
    ctrl.frame_ready.connect(frames.append)
    ctrl._poll_sensors()

    assert len(frames) == 1
    assert frames[0].detector == DETECTOR_PM400
    assert frames[0].power_W is None


def test_clear_pm400_falls_back_to_pdtia(controller):
    ctrl = controller
    detector_changes: list[str] = []
    ctrl.active_detector_changed.connect(detector_changes.append)

    pm = _connected_mock_pm400()
    ctrl.set_pm400(pm)
    ctrl.clear_pm400()

    assert detector_changes == [DETECTOR_PM400, DETECTOR_PDTIA]
    assert not ctrl.is_pm400_active

    frames: list = []
    ctrl.frame_ready.connect(frames.append)
    ctrl._poll_sensors()

    assert frames[0].detector == DETECTOR_PDTIA


def test_clear_pm400_when_never_set_is_a_no_op(controller):
    ctrl = controller
    detector_changes: list[str] = []
    ctrl.active_detector_changed.connect(detector_changes.append)
    ctrl.clear_pm400()  # must not emit — was_active is False
    assert detector_changes == []


# ---------------------------------------------------------------------------
# Disconnection path (required by CLAUDE.md testing conventions)
# ---------------------------------------------------------------------------


def test_pm400_connection_lost_stops_measurement_and_restores_pdtia(controller):
    """A real unplug (simulated via pm.disconnect()) mid-measurement must stop the
    measurement and fall back to PD-TIA — mirrors the MockArduino.kill_pty() pattern
    used for the Arduino disconnection path."""
    ctrl = controller
    assert ctrl.start_continuous_reading()
    assert ctrl.start_measurement()

    pm = _connected_mock_pm400()
    ctrl.set_pm400(pm)
    assert _spin_until(lambda: ctrl._pm400_power_W is not None), "no PM400 reading arrived"

    lost_messages: list[str] = []
    detector_changes: list[str] = []
    stopped: list[bool] = []
    ctrl.pm400_connection_lost.connect(lost_messages.append)
    ctrl.active_detector_changed.connect(detector_changes.append)
    ctrl.measurement_stopped.connect(lambda: stopped.append(True))

    pm.disconnect()  # simulate the meter being unplugged mid-poll

    assert _spin_until(lambda: not ctrl.is_measuring(), timeout=5.0), (
        "measurement was not stopped after PM400 connection loss"
    )
    assert len(lost_messages) == 1
    assert stopped == [True]
    assert not ctrl.is_pm400_active
    assert detector_changes[-1] == DETECTOR_PDTIA

    ctrl.stop_continuous_reading()
