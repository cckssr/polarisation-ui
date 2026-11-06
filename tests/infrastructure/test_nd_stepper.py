"""Tests for NDStepperStage against MockNDStepperFirmware (PTY-based protocol simulator).

Run with: .venv/bin/pytest tests/infrastructure/test_nd_stepper.py
"""

import sys
import time

import pytest

from polarisation_ui.core.exceptions import NDStageError, NDStageTimeoutError
from polarisation_ui.infrastructure.devices.nd_stepper import NDStepperStage
from polarisation_ui.infrastructure.mocks import MockArduino, MockNDStage, MockNDStepperFirmware

pytestmark = pytest.mark.skipif(sys.platform == "win32", reason="PTY not available on Windows")


@pytest.fixture
def firmware():
    fw = MockNDStepperFirmware()
    port = fw.start()
    yield fw, port
    fw.stop()


@pytest.fixture
def stage(firmware):
    fw, port = firmware
    nd = NDStepperStage()
    nd.connect(port)
    yield nd
    nd.disconnect()


class TestConnection:
    def test_connect_verifies_identity(self, stage):
        assert stage.is_connected()

    def test_disconnect_marks_disconnected(self, stage):
        stage.disconnect()
        assert not stage.is_connected()

    def test_rejects_other_serial_device(self):
        arduino = MockArduino()
        port = arduino.start()
        try:
            nd = NDStepperStage()
            with pytest.raises(NDStageError, match="not an ND stepper"):
                nd.connect(port)
            assert not nd.is_connected()
        finally:
            arduino.stop()

    def test_commands_require_connection(self):
        with pytest.raises(NDStageError, match="not connected"):
            NDStepperStage().move_to_deg(10.0)


class TestMotion:
    def test_move_waits_until_target_reached(self, stage):
        stage.move_to_deg(123.4)
        assert not stage.is_busy()
        assert stage.get_position_deg() == pytest.approx(123.4, abs=1e-2)

    def test_move_sends_absolute_command(self, stage, firmware):
        fw, _ = firmware
        stage.move_to_deg(45.0)
        assert "MOT:MOVE:ABS 45.000" in fw.commands

    def test_target_is_clamped_to_range(self, stage):
        stage.move_to_deg(400.0)
        assert stage.get_position_deg() == pytest.approx(360.0, abs=1e-2)
        stage.move_to_deg(-400.0)
        assert stage.get_position_deg() == pytest.approx(-360.0, abs=1e-2)

    def test_negative_angles_are_allowed(self, stage, firmware):
        fw, _ = firmware
        stage.move_to_deg(-30.0)
        assert "MOT:MOVE:ABS -30.000" in fw.commands
        assert stage.get_position_deg() == pytest.approx(-30.0, abs=1e-2)

    def test_custom_range_is_respected(self, firmware):
        fw, port = firmware
        nd = NDStepperStage(max_angle_deg=270.0)
        nd.connect(port)
        try:
            nd.move_to_deg(300.0)
            assert nd.get_position_deg() == pytest.approx(270.0, abs=1e-2)
        finally:
            nd.disconnect()

    def test_firmware_rejection_raises(self, stage, firmware):
        fw, _ = firmware
        fw.limits = (0.0, 100.0)
        with pytest.raises(NDStageError, match="travel limits"):
            stage.move_to_deg(200.0)

    def test_timeout_stops_motion_and_raises(self, firmware):
        fw, port = firmware
        fw.speed_dps = 1.0  # 300 s for a 300° move
        nd = NDStepperStage()
        nd.connect(port)
        try:
            with pytest.raises(NDStageTimeoutError):
                nd.move_to_deg(300.0, timeout=0.3)
            assert "MOT:STOP" in fw.commands
            assert not nd.is_busy()
        finally:
            nd.disconnect()

    def test_stop_without_connection_is_a_noop(self):
        NDStepperStage().stop()


class TestHoming:
    def test_home_with_switch_establishes_reference(self, stage):
        stage.move_to_deg(200.0)
        stage.home()
        assert stage.is_homed()
        assert stage.get_position_deg() == pytest.approx(0.0, abs=1e-2)

    def test_home_without_switch_zeroes_in_place(self):
        fw = MockNDStepperFirmware(has_home_switch=False)
        port = fw.start()
        nd = NDStepperStage()
        try:
            nd.connect(port)
            nd.move_to_deg(90.0)
            nd.home()
            assert nd.is_homed()
            assert nd.get_position_deg() == pytest.approx(0.0, abs=1e-2)
        finally:
            nd.disconnect()
            fw.stop()

    def test_zero_redefines_current_position(self, stage):
        stage.move_to_deg(80.0)
        stage.zero()
        assert stage.is_homed()
        assert stage.get_position_deg() == pytest.approx(0.0, abs=1e-2)

    def test_jog_moves_relative_to_current_position(self, stage):
        stage.move_to_deg(40.0)
        stage.jog_deg(5.0)
        stage.jog_deg(-1.0)
        assert stage.get_position_deg() == pytest.approx(44.0, abs=1e-2)

    def test_jog_below_zero_is_allowed(self, stage):
        stage.move_to_deg(0.0)
        stage.jog_deg(-1.0)
        assert stage.get_position_deg() == pytest.approx(-1.0, abs=1e-2)

    def test_jog_beyond_travel_limit_raises(self, stage):
        stage.move_to_deg(-359.0)
        with pytest.raises(NDStageError):
            stage.jog_deg(-2.0)


class TestConfiguration:
    def test_enable_toggles_motor(self, stage, firmware):
        fw, _ = firmware
        stage.enable(False)
        assert fw.enabled is False
        stage.enable(True)
        assert fw.enabled is True

    def test_invalid_speed_rejected(self, stage):
        with pytest.raises(NDStageError, match="speed"):
            stage.set_speed_dps(10_000.0)


class TestIdleRelease:
    def test_motor_is_released_after_idle_time_and_reenabled_by_next_move(self, stage, firmware):
        fw, _ = firmware
        stage.set_idle_disable_ms(100)
        stage.move_to_deg(10.0)
        assert fw.enabled is True
        time.sleep(0.25)
        stage.get_position_deg()  # any command lets the simulator evaluate the idle timer
        assert fw.enabled is False
        stage.move_to_deg(20.0)
        assert fw.enabled is True

    def test_zero_idle_time_holds_forever(self, stage, firmware):
        fw, _ = firmware
        stage.set_idle_disable_ms(0)
        stage.move_to_deg(10.0)
        time.sleep(0.2)
        stage.get_position_deg()
        assert fw.enabled is True

    def test_out_of_range_idle_time_rejected(self, stage):
        with pytest.raises(NDStageError, match="idle"):
            stage.set_idle_disable_ms(700_000)


class TestUiPolling:
    def test_nowait_returns_position(self, stage):
        stage.move_to_deg(10.0)
        assert stage.get_position_deg_nowait() == pytest.approx(10.0, abs=1e-2)

    def test_nowait_returns_none_when_busy_or_disconnected(self, stage):
        assert stage._lock.acquire(blocking=False)
        try:
            assert stage.get_position_deg_nowait() is None
        finally:
            stage._lock.release()
        stage.disconnect()
        assert stage.get_position_deg_nowait() is None


class TestDisconnection:
    def test_pty_teardown_surfaces_as_nd_stage_error(self, stage, firmware):
        fw, _ = firmware
        stage.move_to_deg(10.0)
        fw.kill_pty()
        with pytest.raises(NDStageError):
            stage.move_to_deg(20.0)


class TestMockNDStage:
    def test_clamps_and_homes(self):
        nd = MockNDStage()
        nd.connect("mock://nd-stage")
        nd.move_to_deg(500.0)
        assert nd.get_position_deg() == 360.0
        nd.move_to_deg(-500.0)
        assert nd.get_position_deg() == -360.0
        nd.home()
        assert nd.get_position_deg() == 0.0 and nd.is_homed()

    def test_requires_connection(self):
        with pytest.raises(NDStageError):
            MockNDStage().move_to_deg(1.0)


class TestDriverDiagnostics:
    def test_status_ok(self, stage):
        assert stage.get_driver_status() == "OK"

    def test_status_fault_is_latched(self, stage, firmware):
        fw, _ = firmware
        fw.fault = True
        assert stage.get_driver_status() == "FAULT"
        fw.fault = False
        assert stage.get_driver_status() == "FAULT"  # latched until *CLS
        stage._command("*CLS")
        assert stage.get_driver_status() == "OK"

    def test_status_na_without_fault_pin(self):
        fw = MockNDStepperFirmware(has_fault_pin=False)
        port = fw.start()
        nd = NDStepperStage()
        try:
            nd.connect(port)
            assert nd.get_driver_status() == "NA"
            assert nd.self_test() == (False, "NA,NO_FAULT_PIN")
        finally:
            nd.disconnect()
            fw.stop()

    def test_reset_clears_latched_fault(self, stage, firmware):
        fw, _ = firmware
        fw.fault = True
        assert stage.get_driver_status() == "FAULT"
        fw.fault = False
        assert stage.reset_driver() == "OK"
        assert "DIAG:DRV:RES" in fw.commands

    def test_reset_keeps_fault_while_pin_still_low(self, stage, firmware):
        fw, _ = firmware
        fw.fault = True
        assert stage.reset_driver() == "FAULT"

    def test_reset_requires_reset_pin(self):
        fw = MockNDStepperFirmware(has_reset_pin=False)
        port = fw.start()
        nd = NDStepperStage()
        try:
            nd.connect(port)
            with pytest.raises(NDStageError, match="PIN_RESET"):
                nd.reset_driver()
        finally:
            nd.disconnect()
            fw.stop()

    def test_self_test_passes(self, stage):
        assert stage.self_test() == (True, "PASS")

    def test_self_test_reports_fault(self, stage, firmware):
        fw, _ = firmware
        fw.fault = True
        ok, detail = stage.self_test()
        assert not ok and detail.startswith("FAIL")

    def test_moves_refused_while_faulted(self, stage, firmware):
        fw, _ = firmware
        fw.fault = True
        with pytest.raises(NDStageError, match="DRV8825 fault"):
            stage.move_to_deg(10.0)


def test_termios_error_on_open_becomes_nd_stage_error(monkeypatch):
    """A tty rejecting its settings (macOS EINVAL) must not escape as termios.error."""
    import termios

    import serial

    def _raise(*args, **kwargs):
        raise termios.error(22, "Invalid argument")

    monkeypatch.setattr(serial, "Serial", _raise)
    stage = NDStepperStage()
    with pytest.raises(NDStageError, match="Cannot open"):
        stage.connect("/dev/cu.usbserial-0001")
