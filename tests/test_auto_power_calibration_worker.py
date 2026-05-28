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
        angle_offset_deg=0.0,
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


# ── AlignPolariserWorker tests (mock hardware only) ───────────────────────────


@pytest.mark.skipif(
    __import__("sys").platform == "win32",
    reason="PTY-based MockArduino not available on Windows",
)
class TestAlignPolariserWorker:
    def setup_method(self):
        from PySide6.QtWidgets import QApplication
        import sys

        self._app = QApplication.instance() or QApplication(sys.argv)

    def test_finds_max_power_angle(self):
        """Worker should return the angle closest to 0° where cos²(θ) is max."""
        from polarisation_ui.infrastructure.qt_threads import AlignPolariserWorker

        kdc = MockKDC101Polariser()
        kdc.connect("mock://kdc101")
        pm = MockPM400(kdc_mock=kdc)
        pm.connect("mock://pm400")

        finished_angles: list[float] = []
        failed_messages: list[str] = []
        scanned_points: list[tuple] = []

        worker = AlignPolariserWorker(
            kdc=kdc,
            pm=pm,
            start_deg=0.0,
            end_deg=180.0,
            n_points=37,  # 5° steps — 0° should yield max cos²
            settle_s=0.0,
        )
        worker.point_scanned.connect(
            lambda a, p: scanned_points.append((a, p)), _DIRECT
        )
        worker.finished.connect(lambda a: finished_angles.append(a), _DIRECT)
        worker.failed.connect(lambda m: failed_messages.append(m), _DIRECT)
        worker.start()
        worker.wait(15_000)

        assert not failed_messages, f"Worker failed: {failed_messages}"
        assert len(finished_angles) == 1

        # MockPM400 returns cos²(physical_angle).  cos²(0°) == cos²(180°) == 1,
        # so either endpoint is a valid maximum; accept both.
        angle = finished_angles[0]
        near_0 = abs(angle) < 6.0
        near_180 = abs(angle - 180.0) < 6.0
        assert near_0 or near_180, (
            f"Expected max-power angle near 0° or 180°, got {angle:.1f}°"
        )
        assert len(scanned_points) == 37

    def test_abort_stops_cleanly(self):
        """Aborting mid-scan should emit failed with an abort message."""
        import time
        from polarisation_ui.infrastructure.qt_threads import AlignPolariserWorker

        kdc = MockKDC101Polariser()
        kdc.connect("mock://kdc101")
        pm = MockPM400(kdc_mock=kdc)
        pm.connect("mock://pm400")

        failed_messages: list[str] = []

        worker = AlignPolariserWorker(
            kdc=kdc,
            pm=pm,
            start_deg=0.0,
            end_deg=180.0,
            n_points=60,
            settle_s=0.02,
        )
        worker.failed.connect(lambda m: failed_messages.append(m), _DIRECT)
        worker.start()
        time.sleep(0.3)
        worker.abort()
        worker.wait(10_000)

        assert len(failed_messages) == 1
        assert "abgebrochen" in failed_messages[0].lower()

    def test_sweep_with_nonzero_offset_shifts_stage_angle(self):
        """When angle_offset_deg != 0, the calibration worker moves the stage to logical_angle + offset, not to logical_angle alone."""
        from polarisation_ui.infrastructure.qt_threads import AutoPowerCalibrationWorker

        mock_arduino = MockArduino()
        dm = _make_device_manager(mock_arduino)
        kdc = MockKDC101Polariser()
        kdc.connect("mock://kdc101")
        pm = MockPM400(kdc_mock=kdc)
        pm.connect("mock://pm400")

        OFFSET = 30.0
        params = _make_params(
            selected_gains=(1,),
            n_points=3,
            angle_start_deg=0.0,
            angle_end_deg=90.0,
            grid_mode="linear_angle",
            angle_offset_deg=OFFSET,
        )

        recorded: list[tuple] = []
        finished: list = []
        failed: list[str] = []

        worker = AutoPowerCalibrationWorker(
            device_manager=dm, kdc=kdc, pm=pm, params=params
        )
        worker.point_recorded.connect(lambda *a: recorded.append(a), _DIRECT)
        worker.finished.connect(lambda p: finished.append(p), _DIRECT)
        worker.failed.connect(lambda m: failed.append(m), _DIRECT)
        worker.start()
        worker.wait(15_000)

        assert not failed, f"Worker failed: {failed}"
        assert len(finished) == 1
        assert len(recorded) == 3

        # Logical angles are 0, 45, 90.  KDC should have ended at 90 + 30 = 120°.
        final_stage_pos = kdc.get_position_deg()
        assert abs(final_stage_pos - (90.0 + OFFSET)) < 0.5, (
            f"Expected stage at {90 + OFFSET}°, got {final_stage_pos:.2f}°"
        )

        dm.disconnect_all()
        mock_arduino.stop()
