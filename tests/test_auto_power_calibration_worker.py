"""Tests for AutoPowerCalibrationWorker using mocks — no real hardware."""

import time

import pytest
from PySide6.QtCore import Qt

from polarisation_ui.core.auto_calibration_settings import AutoCalibrationParams
from polarisation_ui.core.power_calibration import PowerCalibrationProfile
from polarisation_ui.infrastructure.devices.intensity_actuator import (
    NDFilterActuator,
    PolariserActuator,
)
from polarisation_ui.infrastructure.mocks.mock_arduino import MockArduino
from polarisation_ui.infrastructure.mocks.mock_kdc101_nd_stage import MockKDC101NDStage
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
        import sys

        from PySide6.QtWidgets import QApplication

        self._app = QApplication.instance() or QApplication(sys.argv)

    def test_full_sweep_emits_correct_point_count(self):
        from polarisation_ui.infrastructure.qt_threads import AutoPowerCalibrationWorker

        mock_arduino = MockArduino()
        dm = _make_device_manager(mock_arduino)
        kdc = MockKDC101Polariser()
        kdc.connect("mock://kdc101")
        pm = MockPM400(kdc_mock=kdc)
        pm.connect("mock://pm400")

        # Use a threshold above EXT VREF (2.5 V) so the mock encoder at 0°
        # does not saturate all points (cos²(0°) × 2.5 V = 2.5 V > 2.35 V default).
        params = _make_params(
            selected_gains=(1, 2, 3, 4), n_points=5, adc_saturation_threshold_V=2.6
        )

        received_points: list[tuple] = []
        finished_profiles: list[PowerCalibrationProfile] = []
        failed_messages: list[str] = []

        worker = AutoPowerCalibrationWorker(
            device_manager=dm, actuator=PolariserActuator(kdc), pm=pm, params=params
        )
        worker.point_recorded.connect(lambda *args: received_points.append(args), _DIRECT)
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
            device_manager=dm, actuator=PolariserActuator(kdc), pm=pm, params=params
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

        params = _make_params(selected_gains=(1,), n_points=3, profile_name="det_b_test")

        finished: list[PowerCalibrationProfile] = []
        worker = AutoPowerCalibrationWorker(
            device_manager=dm, actuator=PolariserActuator(kdc), pm=pm, params=params
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
        import sys

        from PySide6.QtWidgets import QApplication

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
        worker.point_scanned.connect(lambda a, p: scanned_points.append((a, p)), _DIRECT)
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
        assert near_0 or near_180, f"Expected max-power angle near 0° or 180°, got {angle:.1f}°"
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
        """With the actuator's angle_offset_deg set, the worker moves to logical_angle + offset."""
        from polarisation_ui.infrastructure.qt_threads import AutoPowerCalibrationWorker

        mock_arduino = MockArduino()
        dm = _make_device_manager(mock_arduino)
        kdc = MockKDC101Polariser()
        kdc.connect("mock://kdc101")
        pm = MockPM400(kdc_mock=kdc)
        pm.connect("mock://pm400")

        OFFSET = 30.0
        # Use threshold above EXT VREF (2.5 V) so the static encoder_a=0° does
        # not saturate all points (2.5 × cos²(0°) = 2.5 V > 2.35 V default).
        params = _make_params(
            selected_gains=(1,),
            n_points=3,
            angle_start_deg=0.0,
            angle_end_deg=90.0,
            grid_mode="linear_angle",
            angle_offset_deg=OFFSET,
            adc_saturation_threshold_V=2.6,
        )

        recorded: list[tuple] = []
        finished: list = []
        failed: list[str] = []

        # The offset is applied by the actuator itself now, not read from params.
        worker = AutoPowerCalibrationWorker(
            device_manager=dm,
            actuator=PolariserActuator(kdc, angle_offset_deg=OFFSET),
            pm=pm,
            params=params,
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


# ── AutoPowerCalibrationWorker, ND-filter (power-domain) mode ─────────────────


@pytest.mark.skipif(
    __import__("sys").platform == "win32",
    reason="PTY-based MockArduino not available on Windows",
)
class TestAutoPowerCalibrationWorkerNDMode:
    def setup_method(self):
        import sys

        from PySide6.QtWidgets import QApplication

        self._app = QApplication.instance() or QApplication(sys.argv)

    def _nd_scan(self, end_mm: float = 20.0, n: int = 5) -> tuple[tuple[float, float], ...]:
        """Coarse scan matching MockPM400's ND model exactly (P_max=1e-6, OD_MAX=3, travel=50).

        Deliberately coarse (5 points over 20 mm) so linear interpolation of
        this exponential curve has real error — exercising the worker's
        bisection refinement, not just its initial interpolated guess.
        """
        step = end_mm / (n - 1)
        return tuple((i * step, 1e-6 * 10 ** (-3.0 * (i * step) / 50.0)) for i in range(n))

    def test_nd_sweep_hits_target_powers_within_tolerance(self):
        from polarisation_ui.infrastructure.qt_threads import AutoPowerCalibrationWorker

        mock_arduino = MockArduino()
        dm = _make_device_manager(mock_arduino)
        nd = MockKDC101NDStage()
        nd.connect("mock://nd-stage")
        pm = MockPM400(nd_mock=nd)
        pm.connect("mock://pm400")

        scan = self._nd_scan()
        tolerance_pct = 8.0
        params = _make_params(
            selected_gains=(1, 2),
            n_points=6,
            intensity_source="nd_filter",
            power_grid_mode="log_power",
            nd_scan_points=scan,
            power_tolerance_pct=tolerance_pct,
            max_refine_steps=3,
            adc_saturation_threshold_V=2.6,
            # _nd_scan()'s reference powers don't include a beamsplitter
            # attenuation factor, so match the PM400 config to 0 dB here —
            # otherwise every achieved reading is off by a constant factor
            # relative to the synthetic scan, not a real tolerance failure.
            beamsplitter_attenuation_dB=0.0,
        )

        from polarisation_ui.core.auto_calibration_settings import build_power_grid

        powers_in_scan = [p for _, p in scan]
        expected_targets = build_power_grid(
            max(powers_in_scan), min(powers_in_scan), params.n_points, params.power_grid_mode
        )

        recorded: list[tuple] = []
        finished: list[PowerCalibrationProfile] = []
        failed: list[str] = []

        worker = AutoPowerCalibrationWorker(
            device_manager=dm, actuator=NDFilterActuator(nd), pm=pm, params=params
        )
        worker.point_recorded.connect(lambda *a: recorded.append(a), _DIRECT)
        worker.finished.connect(lambda p: finished.append(p), _DIRECT)
        worker.failed.connect(lambda m: failed.append(m), _DIRECT)
        worker.start()
        worker.wait(30_000)

        assert not failed, f"Worker failed: {failed}"
        assert len(finished) == 1
        assert len(recorded) == 2 * params.n_points

        # First gain's points, in sweep order, should match expected_targets 1:1.
        gain1_points = [r for r in recorded if r[0] == 1]
        assert len(gain1_points) == len(expected_targets)
        for (_, _position, _voltage, achieved), target in zip(
            gain1_points, expected_targets, strict=True
        ):
            assert abs(achieved - target) / target <= tolerance_pct / 100.0 + 1e-6, (
                f"achieved={achieved:.3e} W outside {tolerance_pct}% of target={target:.3e} W"
            )

        profile = finished[0]
        assert profile.intensity_control["kind"] == "nd_filter"
        assert profile.intensity_control["grid"]["mode"] == "log_power"
        assert len(profile.intensity_control["levels"]) == len(expected_targets)

        dm.disconnect_all()
        mock_arduino.stop()

    def test_abort_stops_nd_sweep_cleanly(self):
        from polarisation_ui.infrastructure.qt_threads import AutoPowerCalibrationWorker

        mock_arduino = MockArduino()
        dm = _make_device_manager(mock_arduino)
        nd = MockKDC101NDStage()
        nd.connect("mock://nd-stage")
        pm = MockPM400(nd_mock=nd)
        pm.connect("mock://pm400")

        params = _make_params(
            selected_gains=(1, 2, 3, 4),
            n_points=30,
            point_settle_s=0.02,
            gain_settle_s=0.05,
            intensity_source="nd_filter",
            nd_scan_points=self._nd_scan(),
        )

        failed_messages: list[str] = []
        worker = AutoPowerCalibrationWorker(
            device_manager=dm, actuator=NDFilterActuator(nd), pm=pm, params=params
        )
        worker.failed.connect(lambda m: failed_messages.append(m), _DIRECT)
        worker.start()
        time.sleep(0.3)
        worker.abort()
        worker.wait(10_000)

        assert len(failed_messages) == 1
        assert "abort" in failed_messages[0].lower()

        dm.disconnect_all()
        mock_arduino.stop()

        dm.disconnect_all()
        mock_arduino.stop()
