"""Tests for KDC101 Stage Communication.

Tests the KDC101Stage class backed by pylablib's KinesisMotor.

Usage:
    pytest test_kdc101.py -v
    pytest test_kdc101.py -v --hardware  # requires actual device
"""

import os
import struct
import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from devices.kdc101_stage import KDC101Stage


def _make_connected_stage() -> tuple[KDC101Stage, MagicMock]:
    """Return a KDC101Stage wired to a mock KinesisMotor that reports as open."""
    stage = KDC101Stage("/dev/test")
    mock_motor = MagicMock()
    mock_motor.is_opened.return_value = True
    stage._stage = mock_motor
    return stage, mock_motor


class TestKDC101Initialization:
    def test_default_baudrate(self):
        stage = KDC101Stage("/dev/test")
        assert stage.baudrate == 115200

    def test_custom_baudrate(self):
        stage = KDC101Stage("/dev/test", baudrate=9600)
        assert stage.baudrate == 9600

    def test_default_timeout(self):
        stage = KDC101Stage("/dev/test")
        assert stage.timeout == 1.0

    def test_custom_timeout(self):
        stage = KDC101Stage("/dev/test", timeout=2.5)
        assert stage.timeout == 2.5

    def test_not_connected_initially(self):
        stage = KDC101Stage("/dev/test")
        assert stage.connected is False


class TestKDC101EncoderConversion:
    def test_encoder_counts_per_degree_constant(self):
        assert abs(KDC101Stage.ENCODER_COUNTS_PER_DEG - 1919.64186) < 0.001

    def test_zero_counts_to_zero_degrees(self):
        assert 0 / KDC101Stage.ENCODER_COUNTS_PER_DEG == 0.0

    def test_full_rotation_counts(self):
        expected = 360 * KDC101Stage.ENCODER_COUNTS_PER_DEG
        assert abs(expected - 691071.07) < 1

    def test_90_degree_counts(self):
        expected = 90.0 * KDC101Stage.ENCODER_COUNTS_PER_DEG
        assert abs(expected - 172767.77) < 1


class TestKDC101Connection:
    def test_connect_success(self):
        """connect() returns True and stage becomes connected on success."""
        with patch("devices.kdc101_stage.Thorlabs") as mock_thorlabs:
            mock_motor = MagicMock()
            mock_motor.is_opened.return_value = True
            mock_motor.get_device_info.return_value = MagicMock(serial_no=27000001)
            mock_thorlabs.KinesisMotor.return_value = mock_motor

            stage = KDC101Stage("/dev/test")
            result = stage.connect()

        assert result is True
        assert stage.connected is True
        mock_motor.open.assert_called_once()

    def test_connect_failure_on_open_error(self):
        """connect() returns False when KinesisMotor.open() raises."""
        from pylablib.devices.Thorlabs import ThorlabsError

        with patch("devices.kdc101_stage.Thorlabs") as mock_thorlabs:
            mock_motor = MagicMock()
            mock_motor.open.side_effect = ThorlabsError("device not found")
            mock_motor.is_opened.return_value = False
            mock_thorlabs.KinesisMotor.return_value = mock_motor

            stage = KDC101Stage("/dev/test")
            result = stage.connect()

        assert result is False
        assert stage.connected is False

    def test_disconnect_calls_close(self):
        """disconnect() closes the motor and clears _stage."""
        stage, mock_motor = _make_connected_stage()

        stage.disconnect()

        mock_motor.close.assert_called_once()
        assert stage._stage is None
        assert stage.connected is False

    def test_disconnect_when_not_connected_is_safe(self):
        """disconnect() on a stage that was never connected does not raise."""
        stage = KDC101Stage("/dev/test")
        stage.disconnect()  # should not raise


class TestKDC101PositionReading:
    def test_get_position_counts(self):
        stage, mock_motor = _make_connected_stage()
        mock_motor.get_position.return_value = 172768

        result = stage.get_position_counts()

        assert result == 172768
        mock_motor.get_position.assert_called_once_with(scale=False)

    def test_get_position_degrees(self):
        stage, mock_motor = _make_connected_stage()
        counts = int(90 * KDC101Stage.ENCODER_COUNTS_PER_DEG)
        mock_motor.get_position.return_value = counts

        result = stage.get_position_degrees()

        assert result is not None
        assert abs(result - 90.0) < 0.1

    def test_get_position_negative(self):
        stage, mock_motor = _make_connected_stage()
        counts = int(-45 * KDC101Stage.ENCODER_COUNTS_PER_DEG)
        mock_motor.get_position.return_value = counts

        result = stage.get_position_degrees()

        assert result is not None
        assert abs(result - (-45.0)) < 0.1

    def test_get_position_not_connected_returns_none(self):
        stage = KDC101Stage("/dev/test")
        assert stage.get_position_counts() is None

    def test_get_position_degrees_not_connected_returns_none(self):
        stage = KDC101Stage("/dev/test")
        assert stage.get_position_degrees() is None

    def test_get_position_on_thorlabs_error_returns_none(self):
        from pylablib.devices.Thorlabs import ThorlabsError

        stage, mock_motor = _make_connected_stage()
        mock_motor.get_position.side_effect = ThorlabsError("timeout")

        assert stage.get_position_counts() is None


class TestKDC101Commands:
    def test_identify_calls_blink(self):
        stage, mock_motor = _make_connected_stage()
        stage.identify()
        mock_motor.blink.assert_called_once_with(channel=KDC101Stage.CHANNEL)

    def test_identify_does_nothing_when_not_connected(self):
        stage = KDC101Stage("/dev/test")
        stage.identify()  # should not raise

    def test_enable_sends_correct_state(self):
        stage, mock_motor = _make_connected_stage()
        stage.enable(True)
        mock_motor.send_comm.assert_called_once_with(
            KDC101Stage._MSG_MOD_SET_CHANENABLESTATE,
            param1=KDC101Stage.CHANNEL,
            param2=0x01,
        )

    def test_disable_sends_correct_state(self):
        stage, mock_motor = _make_connected_stage()
        stage.enable(False)
        mock_motor.send_comm.assert_called_once_with(
            KDC101Stage._MSG_MOD_SET_CHANENABLESTATE,
            param1=KDC101Stage.CHANNEL,
            param2=0x02,
        )

    def test_enable_does_nothing_when_not_connected(self):
        stage = KDC101Stage("/dev/test")
        stage.enable(True)  # should not raise


class TestKDC101EncoderCounter:
    def _make_enc_reply(self, encoder_count: int) -> MagicMock:
        """Build a mock CommData reply for MSG_MOT_GET_ENCCOUNTER."""
        data = struct.pack("<H", KDC101Stage.CHANNEL) + struct.pack("<i", encoder_count)
        reply = MagicMock()
        reply.data = data
        return reply

    def test_get_encoder_counts(self):
        stage, mock_motor = _make_connected_stage()
        mock_motor.query.return_value = self._make_enc_reply(98765)

        result = stage.get_encoder_counts()

        assert result == 98765
        mock_motor.query.assert_called_once_with(
            KDC101Stage._MSG_MOT_REQ_ENCCOUNTER,
            param1=KDC101Stage.CHANNEL,
            replyID=KDC101Stage._MSG_MOT_GET_ENCCOUNTER,
        )

    def test_get_encoder_counts_negative(self):
        stage, mock_motor = _make_connected_stage()
        mock_motor.query.return_value = self._make_enc_reply(-12345)

        assert stage.get_encoder_counts() == -12345

    def test_get_encoder_counts_not_connected_returns_none(self):
        stage = KDC101Stage("/dev/test")
        assert stage.get_encoder_counts() is None

    def test_get_encoder_counts_on_thorlabs_error_returns_none(self):
        from pylablib.devices.Thorlabs import ThorlabsError

        stage, mock_motor = _make_connected_stage()
        mock_motor.query.side_effect = ThorlabsError("timeout")

        assert stage.get_encoder_counts() is None


# =============================================================================
# Hardware Tests (require actual KDC101 connected)
# =============================================================================


def pytest_addoption(parser):
    parser.addoption(
        "--hardware",
        action="store_true",
        default=False,
        help="Run tests that require actual hardware",
    )


@pytest.fixture
def hardware_stage():
    try:
        from config import KDC101_PORT

        stage = KDC101Stage(KDC101_PORT)
        if stage.connect():
            yield stage
            stage.disconnect()
        else:
            pytest.skip("Could not connect to KDC101")
    except Exception as e:
        pytest.skip(f"Hardware not available: {e}")


@pytest.mark.hardware
class TestKDC101Hardware:
    def test_hardware_connect(self, hardware_stage):
        assert hardware_stage.connected is True

    def test_hardware_read_position(self, hardware_stage):
        position = hardware_stage.get_position_degrees()
        assert position is not None
        assert -720 <= position <= 720

    def test_hardware_identify(self, hardware_stage):
        hardware_stage.identify()

    def test_hardware_multiple_reads(self, hardware_stage):
        import time

        positions = []
        for _ in range(5):
            pos = hardware_stage.get_position_degrees()
            if pos is not None:
                positions.append(pos)
            time.sleep(0.1)

        assert len(positions) >= 3
        if len(positions) >= 2:
            assert max(positions) - min(positions) < 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
