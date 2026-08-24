"""Tests for GainCrossCheckWorker using mocks — no real hardware."""

import time

import pytest
from PySide6.QtCore import Qt

from polarisation_ui.core.gain_crosscheck import GainCrossCheckResult
from polarisation_ui.core.power_calibration import GainCalibration, PowerCalibrationProfile
from polarisation_ui.infrastructure.devices.intensity_actuator import NDFilterActuator
from polarisation_ui.infrastructure.mocks.mock_arduino import MockArduino
from polarisation_ui.infrastructure.mocks.mock_kdc101_nd_stage import MockKDC101NDStage
from polarisation_ui.infrastructure.mocks.mock_pm400 import MockPM400

_DIRECT = Qt.ConnectionType.DirectConnection


def _make_device_manager(mock_arduino: MockArduino):
    """Return a GoniometerDeviceManager connected to the mock Arduino PTY."""
    from polarisation_ui.infrastructure.device_manager import GoniometerDeviceManager

    dm = GoniometerDeviceManager()
    port = mock_arduino.start()
    ok = dm.connect_encoders(port)
    assert ok, "Could not connect device manager to mock Arduino"
    return dm


def _make_devices():
    """MockArduino's ADC voltage is ~2.5 V at encoder_a=0° regardless of pdtia_gain
    (Malus's law on encoder angle only — see mock_arduino._compute_adc_voltage),
    so distinguishing "gain stages agree" from "gain stages disagree" in these
    tests comes entirely from the profile's per-gain conversion factors."""
    mock_arduino = MockArduino()
    dm = _make_device_manager(mock_arduino)
    nd = MockKDC101NDStage()
    nd.connect("mock://nd-stage")
    pm = MockPM400(nd_mock=nd)
    pm.connect("mock://pm400")
    return mock_arduino, dm, nd, pm


@pytest.mark.skipif(
    __import__("sys").platform == "win32",
    reason="PTY-based MockArduino not available on Windows",
)
class TestGainCrossCheckWorker:
    def setup_method(self):
        import sys

        from PySide6.QtWidgets import QApplication

        self._app = QApplication.instance() or QApplication(sys.argv)

    def test_consistent_gains_pass(self):
        from polarisation_ui.infrastructure.qt_threads import GainCrossCheckWorker

        mock_arduino, dm, nd, pm = _make_devices()
        # Both gains calibrated so ~2.5 V (the mock's fixed ADC reading) maps
        # to ~1e-6 W, matching MockPM400's ND model at position 0 mm.
        profile = PowerCalibrationProfile(name="test", adc_saturation_threshold_V=2.6)
        profile.gains[1] = GainCalibration(gain_stage=1, points=[(2.5, 1.0e-6)])
        profile.gains[2] = GainCalibration(gain_stage=2, points=[(2.5, 1.0e-6)])

        results: list[GainCrossCheckResult] = []
        failures: list[str] = []

        # A single level: MockArduino's ADC voltage tracks encoder_a (Malus's
        # law), not the ND stage, so it doesn't vary with position — using
        # more than one level here would drift the PM400 reading away from
        # the (position-independent) mock ADC reading and fail the
        # PM-vs-gain deviation check for a reason unrelated to what this
        # test is verifying (gain-vs-gain spread).
        worker = GainCrossCheckWorker(
            device_manager=dm,
            actuator=NDFilterActuator(nd),
            pm=pm,
            profile=profile,
            levels=[0.0],
            gains=(1, 2),
            settle_s=0.0,
            detector_samples=2,
            tolerance_pct=10.0,
        )
        worker.finished.connect(lambda r: results.append(r), _DIRECT)
        worker.failed.connect(lambda m: failures.append(m), _DIRECT)
        worker.start()
        worker.wait(15_000)

        assert not failures, f"Worker failed: {failures}"
        assert len(results) == 1
        assert results[0].passed is True
        assert results[0].worst_spread_pct == pytest.approx(0.0, abs=0.5)

        dm.disconnect_all()
        mock_arduino.stop()

    def test_detects_gain_mismatch(self):
        from polarisation_ui.infrastructure.qt_threads import GainCrossCheckWorker

        mock_arduino, dm, nd, pm = _make_devices()
        # Gain 2's calibration reads roughly double gain 1's for the same voltage.
        profile = PowerCalibrationProfile(name="test", adc_saturation_threshold_V=2.6)
        profile.gains[1] = GainCalibration(gain_stage=1, points=[(2.5, 1.0e-6)])
        profile.gains[2] = GainCalibration(gain_stage=2, points=[(2.5, 2.0e-6)])

        results: list[GainCrossCheckResult] = []
        failures: list[str] = []

        worker = GainCrossCheckWorker(
            device_manager=dm,
            actuator=NDFilterActuator(nd),
            pm=pm,
            profile=profile,
            levels=[0.0],
            gains=(1, 2),
            settle_s=0.0,
            detector_samples=2,
            tolerance_pct=5.0,
        )
        worker.finished.connect(lambda r: results.append(r), _DIRECT)
        worker.failed.connect(lambda m: failures.append(m), _DIRECT)
        worker.start()
        worker.wait(15_000)

        assert not failures, f"Worker failed: {failures}"
        assert len(results) == 1
        assert results[0].passed is False
        assert results[0].worst_spread_pct > 5.0

        dm.disconnect_all()
        mock_arduino.stop()

    def test_abort_stops_worker_cleanly(self):
        from polarisation_ui.infrastructure.qt_threads import GainCrossCheckWorker

        mock_arduino, dm, nd, pm = _make_devices()
        profile = PowerCalibrationProfile(name="test", adc_saturation_threshold_V=2.6)
        profile.gains[1] = GainCalibration(gain_stage=1, points=[(2.5, 1.0e-6)])
        profile.gains[2] = GainCalibration(gain_stage=2, points=[(2.5, 1.0e-6)])

        failures: list[str] = []
        worker = GainCrossCheckWorker(
            device_manager=dm,
            actuator=NDFilterActuator(nd),
            pm=pm,
            profile=profile,
            levels=[0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0],
            gains=(1, 2, 3, 4),
            settle_s=0.05,
            detector_samples=2,
        )
        worker.failed.connect(lambda m: failures.append(m), _DIRECT)
        worker.start()
        time.sleep(0.2)
        worker.abort()
        worker.wait(10_000)

        assert len(failures) == 1
        assert "abort" in failures[0].lower()

        dm.disconnect_all()
        mock_arduino.stop()

    def test_uncalibrated_gain_is_skipped_not_failed(self):
        from polarisation_ui.infrastructure.qt_threads import GainCrossCheckWorker

        mock_arduino, dm, nd, pm = _make_devices()
        profile = PowerCalibrationProfile(name="test", adc_saturation_threshold_V=2.6)
        profile.gains[1] = GainCalibration(gain_stage=1, points=[(2.5, 1.0e-6)])
        # gain 2 left uncalibrated (no points) -> conversion_factor is None;
        # gain 3 calibrated so the level still has 2 comparable readings.
        profile.gains[3] = GainCalibration(gain_stage=3, points=[(2.5, 1.0e-6)])

        results: list[GainCrossCheckResult] = []
        failures: list[str] = []

        worker = GainCrossCheckWorker(
            device_manager=dm,
            actuator=NDFilterActuator(nd),
            pm=pm,
            profile=profile,
            levels=[0.0],
            gains=(1, 2, 3),
            settle_s=0.0,
            detector_samples=2,
            tolerance_pct=10.0,
        )
        worker.finished.connect(lambda r: results.append(r), _DIRECT)
        worker.failed.connect(lambda m: failures.append(m), _DIRECT)
        worker.start()
        worker.wait(15_000)

        assert not failures, f"Worker failed: {failures}"
        assert len(results) == 1
        assert 2 not in results[0].levels[0].per_gain
        assert 1 in results[0].levels[0].per_gain
        assert 3 in results[0].levels[0].per_gain

        dm.disconnect_all()
        mock_arduino.stop()
