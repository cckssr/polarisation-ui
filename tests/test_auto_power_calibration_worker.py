"""Tests for AutoPowerCalibrationWorker using mocks — no real hardware."""

import time
import pytest
from PySide6.QtCore import Qt

from polarisation_ui.core.auto_calibration_settings import AutoCalibrationParams
from polarisation_ui.core.power_calibration import PowerCalibrationProfile
from polarisation_ui.infrastructure.mocks.mock_arduino import MockArduino
from polarisation_ui.infrastructure.mocks.mock_kdc101_polariser import (
    MockKDC101Polariser,
)
from polarisation_ui.infrastructure.mocks.mock_pm400 import MockPM400

_DIRECT = Qt.ConnectionType.DirectConnection


# ── Helpers ───────────────────────────────────────────────────────────────────


def _make_params(**overrides) -> AutoCalibrationParams:
    defaults = dict(
        selected_gains=(1, 2),
        angle_start_deg=0.0,
        angle_end_deg=90.0,
        n_points=4,
        grid_mode="linear_angle",
        point_settle_s=0.0,
        gain_settle_s=0.0,
        detector_samples=2,
        pm_averaging=1,
        profile_name="test_profile",
        wavelength_nm=633.0,
        beamsplitter_attenuation_dB=3.0,
    )
    defaults.update(overrides)
    return AutoCalibrationParams(**defaults)


def _make_device_manager(mock_arduino: MockArduino):
    """Return a GoniometerDeviceManager connected to the mock Arduino PTY."""
    from polarisation_ui.infrastructure.device_manager import GoniometerDeviceManager

    dm = GoniometerDeviceManager()
    port = mock_arduino.start()
    ok = dm.connect_encoders(port)
    assert ok, "Could not connect device manager to mock Arduino"
    return dm


# ── Worker tests (no Qt event loop needed — runs via QThread.wait()) ──────────


@pytest.mark.skipif(
    __import__("sys").platform == "win32",
    reason="PTY-based MockArduino not available on Windows",
)
class TestAutoPowerCalibrationWorker:
    def setup_method(self):
        from PySide6.QtWidgets import QApplication
        import sys

        self._app = QApplication.instance() or QApplication(sys.argv)

    def test_full_sweep_emits_correct_point_count(self):
        from polarisation_ui.infrastructure.qt_threads import AutoPowerCalibrationWorker

        mock_arduino = MockArduino()
        dm = _make_device_manager(mock_arduino)
        kdc = MockKDC101Polariser()
        kdc.connect("mock://kdc101")
        pm = MockPM400(kdc_mock=kdc)
        pm.connect("mock://pm400")

        params = _make_params(selected_gains=(1, 2, 3, 4), n_points=5)

        received_points: list[tuple] = []
        finished_profiles: list[PowerCalibrationProfile] = []
        failed_messages: list[str] = []

        worker = AutoPowerCalibrationWorker(
            device_manager=dm, kdc=kdc, pm=pm, params=params
        )
        worker.point_recorded.connect(
            lambda *args: received_points.append(args), _DIRECT
        )
        worker.finished.connect(lambda p: finished_profiles.append(p), _DIRECT)
        worker.failed.connect(lambda m: failed_messages.append(m), _DIRECT)
        worker.start()
        worker.wait(30_000)

        assert not failed_messages, f"Worker failed: {failed_messages}"
        assert len(finished_profiles) == 1

        profile = finished_profiles[0]
        assert isinstance(profile, PowerCalibrationProfile)
        assert profile.name == "test_profile"

        # 4 gains × 5 angles = 20 points total
        expected = 4 * 5
        assert len(received_points) == expected

        # Each gain should have 5 calibration points
        for gain in (1, 2, 3, 4):
            assert len(profile.gains[gain].points) == 5

        dm.disconnect_all()
        mock_arduino.stop()

    def test_abort_stops_worker_cleanly(self):
        from polarisation_ui.infrastructure.qt_threads import AutoPowerCalibrationWorker

        mock_arduino = MockArduino()
        dm = _make_device_manager(mock_arduino)
        kdc = MockKDC101Polariser()
        kdc.connect("mock://kdc101")
        pm = MockPM400(kdc_mock=kdc)
        pm.connect("mock://pm400")

        params = _make_params(
            selected_gains=(1, 2, 3, 4),
            n_points=30,
            point_settle_s=0.02,
            gain_settle_s=0.05,
        )

        failed_messages: list[str] = []

        worker = AutoPowerCalibrationWorker(
            device_manager=dm, kdc=kdc, pm=pm, params=params
        )
        worker.failed.connect(lambda m: failed_messages.append(m), _DIRECT)
        worker.start()
        # Give the worker time to start and enter the angle loop, then abort
        time.sleep(0.3)
        worker.abort()
        worker.wait(10_000)

        assert len(failed_messages) == 1
        assert "abort" in failed_messages[0].lower()

        dm.disconnect_all()
        mock_arduino.stop()

    def test_profile_name_stored_correctly(self):
        from polarisation_ui.infrastructure.qt_threads import AutoPowerCalibrationWorker

        mock_arduino = MockArduino()
        dm = _make_device_manager(mock_arduino)
        kdc = MockKDC101Polariser()
        kdc.connect("mock://kdc101")
        pm = MockPM400(kdc_mock=kdc)
        pm.connect("mock://pm400")

        params = _make_params(
            selected_gains=(1,), n_points=3, profile_name="det_b_test"
        )

        finished: list[PowerCalibrationProfile] = []
        worker = AutoPowerCalibrationWorker(
            device_manager=dm, kdc=kdc, pm=pm, params=params
        )
        worker.finished.connect(lambda p: finished.append(p), _DIRECT)
        worker.start()
        worker.wait(15_000)

        assert finished and finished[0].name == "det_b_test"

        dm.disconnect_all()
        mock_arduino.stop()
