"""Tests for ManualCalibrationController."""

import math
import time
from unittest.mock import MagicMock

import pytest

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from calibration.manual_runner import ManualCalibrationController
from calibration.measurement import MeasurementPoint


def _make_arduino(angle: float = 12.34) -> MagicMock:
    arduino = MagicMock()
    arduino.connected = True
    arduino.read_angle.return_value = angle
    return arduino


class TestManualCalibrationControllerInit:
    def test_step_size_10_produces_36_steps(self):
        ctrl = ManualCalibrationController(_make_arduino(), step_size_deg=10.0)
        assert ctrl.total_steps == 36

    def test_step_size_45_produces_8_steps(self):
        ctrl = ManualCalibrationController(_make_arduino(), step_size_deg=45.0)
        assert ctrl.total_steps == 8

    def test_step_size_1_produces_360_steps(self):
        ctrl = ManualCalibrationController(_make_arduino(), step_size_deg=1.0)
        assert ctrl.total_steps == 360

    def test_targets_start_at_zero(self):
        ctrl = ManualCalibrationController(_make_arduino(), step_size_deg=90.0)
        assert ctrl.current_target == pytest.approx(0.0)

    def test_targets_do_not_include_360(self):
        ctrl = ManualCalibrationController(_make_arduino(), step_size_deg=90.0)
        assert ctrl.total_steps == 4
        # last target should be 270, not 360
        targets = [ctrl._targets[i] for i in range(ctrl.total_steps)]
        assert max(targets) == pytest.approx(270.0)

    def test_run_name_auto_generated_when_empty(self):
        ctrl = ManualCalibrationController(_make_arduino(), step_size_deg=10.0)
        assert "manual_cal_" in ctrl.run_name

    def test_custom_run_name(self):
        ctrl = ManualCalibrationController(
            _make_arduino(), step_size_deg=10.0, run_name="my_run"
        )
        assert ctrl.run_name == "my_run"

    def test_invalid_step_size_raises(self):
        with pytest.raises(ValueError):
            ManualCalibrationController(_make_arduino(), step_size_deg=0.0)
        with pytest.raises(ValueError):
            ManualCalibrationController(_make_arduino(), step_size_deg=91.0)


class TestManualCalibrationControllerFlow:
    def test_accept_records_correct_reference_angle_encoder_b(self):
        arduino = _make_arduino(angle=5.5)
        ctrl = ManualCalibrationController(arduino, step_size_deg=10.0, encoder_id="B")
        # First target is 0.0°; encoder B: no reversal
        point = ctrl.accept_current()
        assert point.reference_deg == pytest.approx(0.0)
        assert point.measured_deg == pytest.approx(5.5)

    def test_accept_encoder_a_reverses_reading(self):
        arduino = _make_arduino(angle=90.0)
        ctrl = ManualCalibrationController(arduino, step_size_deg=90.0, encoder_id="A")
        point = ctrl.accept_current()
        assert point.measured_deg == pytest.approx(270.0)  # (-90) % 360

    def test_accept_encoder_a_zero_stays_zero(self):
        arduino = _make_arduino(angle=0.0)
        ctrl = ManualCalibrationController(arduino, step_size_deg=90.0, encoder_id="A")
        point = ctrl.accept_current()
        assert point.measured_deg == pytest.approx(0.0)

    def test_invalid_encoder_id_raises(self):
        with pytest.raises(ValueError, match="encoder_id"):
            ManualCalibrationController(_make_arduino(), step_size_deg=10.0, encoder_id="C")

    def test_accept_advances_step(self):
        ctrl = ManualCalibrationController(_make_arduino(), step_size_deg=10.0)
        assert ctrl.step_index == 0
        ctrl.accept_current()
        assert ctrl.step_index == 1
        assert ctrl.current_target == pytest.approx(10.0)

    def test_skip_advances_without_recording(self):
        ctrl = ManualCalibrationController(_make_arduino(), step_size_deg=10.0)
        ctrl.skip_current()
        assert ctrl.step_index == 1
        assert ctrl.get_run().num_points == 0

    def test_mixed_accept_skip(self):
        ctrl = ManualCalibrationController(_make_arduino(angle=0.0), step_size_deg=90.0)
        ctrl.accept_current()  # 0°
        ctrl.skip_current()    # 90° skipped
        ctrl.accept_current()  # 180°
        ctrl.skip_current()    # 270° skipped
        run = ctrl.get_run()
        assert run.num_points == 2
        assert run.points[0].reference_deg == pytest.approx(0.0)
        assert run.points[1].reference_deg == pytest.approx(180.0)

    def test_is_complete_after_all_steps(self):
        ctrl = ManualCalibrationController(_make_arduino(), step_size_deg=90.0)
        for _ in range(4):
            ctrl.accept_current()
        assert ctrl.is_complete
        assert ctrl.current_target is None

    def test_accept_on_complete_raises(self):
        ctrl = ManualCalibrationController(_make_arduino(), step_size_deg=90.0)
        for _ in range(4):
            ctrl.accept_current()
        with pytest.raises(RuntimeError, match="already complete"):
            ctrl.accept_current()

    def test_accept_raises_on_encoder_none(self):
        arduino = _make_arduino()
        arduino.read_angle.return_value = None
        ctrl = ManualCalibrationController(arduino, step_size_deg=90.0)
        with pytest.raises(RuntimeError, match="None"):
            ctrl.accept_current()
        # Step should NOT have advanced
        assert ctrl.step_index == 0

    def test_get_run_contains_all_accepted_points(self):
        arduino = _make_arduino(angle=45.0)
        ctrl = ManualCalibrationController(arduino, step_size_deg=90.0)
        for _ in range(4):
            ctrl.accept_current()
        run = ctrl.get_run()
        assert run.num_points == 4
        refs = [p.reference_deg for p in run.points]
        assert refs == pytest.approx([0.0, 90.0, 180.0, 270.0])

    def test_point_has_timestamp(self):
        before = time.time()
        ctrl = ManualCalibrationController(_make_arduino(angle=1.0), step_size_deg=90.0)
        point = ctrl.accept_current()
        after = time.time()
        assert before <= point.timestamp <= after
