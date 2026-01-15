"""
Tests for KDC101 Stage Communication.

This module contains unit tests for the KDC101Stage class,
testing the APT serial protocol implementation.

Usage:
    pytest test_kdc101.py -v
    pytest test_kdc101.py -v -k "test_message"  # Run specific tests

For hardware tests (requires actual KDC101 connected):
    pytest test_kdc101.py -v --hardware
"""

import struct
from unittest.mock import MagicMock, patch, PropertyMock
from typing import Optional

import pytest

# Import the class under test
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from devices.kdc101_stage import KDC101Stage


class TestKDC101MessageBuilding:
    """Tests for APT message building functions."""

    def test_build_short_msg_structure(self):
        """Test that short messages have correct 6-byte structure."""
        stage = KDC101Stage("/dev/null")

        msg = stage._build_short_msg(0x0411, 0x01, 0x00)

        assert len(msg) == 6
        # Check message ID (little-endian)
        msg_id = struct.unpack("<H", msg[0:2])[0]
        assert msg_id == 0x0411

    def test_build_short_msg_params(self):
        """Test parameter bytes in short message."""
        stage = KDC101Stage("/dev/null")

        msg = stage._build_short_msg(0x0411, 0x01, 0x02)

        # param1 is byte 2, param2 is byte 3
        assert msg[2] == 0x01
        assert msg[3] == 0x02

    def test_build_short_msg_destination_with_flag(self):
        """Test destination byte has data flag set."""
        stage = KDC101Stage("/dev/null")

        msg = stage._build_short_msg(0x0411, 0x01, 0x00)

        # Destination (byte 4) should be DEVICE | 0x80
        assert msg[4] == (KDC101Stage.DEVICE | 0x80)

    def test_build_short_msg_simple_no_flag(self):
        """Test simple message without data flag."""
        stage = KDC101Stage("/dev/null")

        msg = stage._build_short_msg_simple(0x0005, 0x00, 0x00)

        # Destination (byte 4) should be DEVICE without flag
        assert msg[4] == KDC101Stage.DEVICE

    def test_build_short_msg_source(self):
        """Test source byte is HOST address."""
        stage = KDC101Stage("/dev/null")

        msg = stage._build_short_msg(0x0411, 0x01, 0x00)

        # Source (byte 5) should be HOST
        assert msg[5] == KDC101Stage.HOST


class TestKDC101MessageIDs:
    """Tests for correct message ID usage."""

    def test_hw_req_info_id(self):
        """Test hardware info request message ID."""
        assert KDC101Stage.MSG_HW_REQ_INFO == 0x0005

    def test_hw_get_info_id(self):
        """Test hardware info response message ID."""
        assert KDC101Stage.MSG_HW_GET_INFO == 0x0006

    def test_position_request_id(self):
        """Test position request message ID."""
        assert KDC101Stage.MSG_MOT_REQ_POSCOUNTER == 0x0411

    def test_position_response_id(self):
        """Test position response message ID."""
        assert KDC101Stage.MSG_MOT_GET_POSCOUNTER == 0x0412

    def test_status_request_id(self):
        """Test status update request message ID."""
        assert KDC101Stage.MSG_MOT_REQ_USTATUSUPDATE == 0x0490

    def test_status_response_id(self):
        """Test status update response message ID."""
        assert KDC101Stage.MSG_MOT_GET_USTATUSUPDATE == 0x0491

    def test_identify_id(self):
        """Test identify (flash LED) message ID."""
        assert KDC101Stage.MSG_MOD_IDENTIFY == 0x0223


class TestKDC101Initialization:
    """Tests for KDC101Stage initialization."""

    def test_default_baudrate(self):
        """Test default baud rate is 115200."""
        stage = KDC101Stage("/dev/test")
        assert stage.baudrate == 115200

    def test_custom_baudrate(self):
        """Test custom baud rate can be set."""
        stage = KDC101Stage("/dev/test", baudrate=9600)
        assert stage.baudrate == 9600

    def test_default_timeout(self):
        """Test default timeout is 1.0 second."""
        stage = KDC101Stage("/dev/test")
        assert stage.timeout == 1.0

    def test_custom_timeout(self):
        """Test custom timeout can be set."""
        stage = KDC101Stage("/dev/test", timeout=2.5)
        assert stage.timeout == 2.5

    def test_not_connected_initially(self):
        """Test stage is not connected after initialization."""
        stage = KDC101Stage("/dev/test")
        assert stage.connected is False


class TestKDC101EncoderConversion:
    """Tests for encoder count to degree conversion."""

    def test_encoder_counts_per_degree_constant(self):
        """Test PRM1-Z8 encoder counts per degree value."""
        # PRM1-Z8 has 1919.64186 counts per degree
        assert abs(KDC101Stage.ENCODER_COUNTS_PER_DEG - 1919.64186) < 0.001

    def test_zero_counts_to_zero_degrees(self):
        """Test 0 counts = 0 degrees."""
        counts = 0
        degrees = counts / KDC101Stage.ENCODER_COUNTS_PER_DEG
        assert degrees == 0.0

    def test_full_rotation_counts(self):
        """Test full rotation (360°) count calculation."""
        expected_counts = 360 * KDC101Stage.ENCODER_COUNTS_PER_DEG
        # Should be approximately 691071
        assert abs(expected_counts - 691071.07) < 1

    def test_90_degree_counts(self):
        """Test 90° position counts."""
        degrees = 90.0
        expected_counts = degrees * KDC101Stage.ENCODER_COUNTS_PER_DEG
        # Should be approximately 172768
        assert abs(expected_counts - 172767.77) < 1


class TestKDC101MockedConnection:
    """Tests using mocked serial connection."""

    @patch("serial.Serial")
    def test_connect_success(self, mock_serial_class):
        """Test successful connection."""
        # Setup mock
        mock_serial = MagicMock()
        mock_serial.is_open = True
        mock_serial_class.return_value = mock_serial

        # Build HW_GET_INFO response
        # Response: msg_id (2) + header (4) + serial (4) + ...
        hw_info_response = struct.pack("<H", KDC101Stage.MSG_HW_GET_INFO)
        hw_info_response += b"\x00" * 4  # Header padding
        hw_info_response += struct.pack("<I", 27000001)  # Serial number
        hw_info_response += b"\x00" * 80  # Remaining bytes

        mock_serial.read.return_value = hw_info_response

        stage = KDC101Stage("/dev/test")
        result = stage.connect()

        assert result is True
        assert stage.connected is True
        mock_serial_class.assert_called_once()

    @patch("serial.Serial")
    def test_connect_no_response(self, mock_serial_class):
        """Test connection failure when device doesn't respond."""
        mock_serial = MagicMock()
        mock_serial.is_open = True
        mock_serial_class.return_value = mock_serial

        # No response
        mock_serial.read.return_value = b""

        stage = KDC101Stage("/dev/test")
        result = stage.connect()

        assert result is False

    @patch("serial.Serial")
    def test_disconnect(self, mock_serial_class):
        """Test disconnect closes serial port."""
        mock_serial = MagicMock()
        mock_serial.is_open = True
        mock_serial_class.return_value = mock_serial

        stage = KDC101Stage("/dev/test")
        stage._serial = mock_serial
        stage._connected = True

        stage.disconnect()

        mock_serial.close.assert_called_once()
        assert stage.connected is False


class TestKDC101PositionReading:
    """Tests for position reading with mocked serial."""

    def _create_position_response(self, position_counts: int) -> bytes:
        """Helper to create a position response message."""
        # MSG_MOT_GET_POSCOUNTER response:
        # [msg_id (2)] [data_len (2)] [dest|src (2)] [chan (2)] [position (4)]
        response = struct.pack("<H", KDC101Stage.MSG_MOT_GET_POSCOUNTER)
        response += struct.pack("<H", 6)  # Data length
        response += struct.pack("<BB", KDC101Stage.HOST, KDC101Stage.DEVICE)
        response += struct.pack("<H", KDC101Stage.CHANNEL)
        response += struct.pack("<i", position_counts)  # Signed 32-bit
        return response

    @patch("serial.Serial")
    def test_get_position_counts(self, mock_serial_class):
        """Test reading position in encoder counts."""
        mock_serial = MagicMock()
        mock_serial.is_open = True
        mock_serial_class.return_value = mock_serial

        # Expected position: 172768 counts (~90°)
        expected_counts = 172768
        mock_serial.read.return_value = self._create_position_response(expected_counts)

        stage = KDC101Stage("/dev/test")
        stage._serial = mock_serial
        stage._connected = True

        result = stage.get_position_counts()

        assert result == expected_counts

    @patch("serial.Serial")
    def test_get_position_degrees(self, mock_serial_class):
        """Test reading position in degrees."""
        mock_serial = MagicMock()
        mock_serial.is_open = True
        mock_serial_class.return_value = mock_serial

        # 90 degrees in counts
        counts = int(90 * KDC101Stage.ENCODER_COUNTS_PER_DEG)
        mock_serial.read.return_value = self._create_position_response(counts)

        stage = KDC101Stage("/dev/test")
        stage._serial = mock_serial
        stage._connected = True

        result = stage.get_position_degrees()

        assert result is not None
        assert abs(result - 90.0) < 0.1

    @patch("serial.Serial")
    def test_get_position_negative(self, mock_serial_class):
        """Test reading negative position (counter-clockwise)."""
        mock_serial = MagicMock()
        mock_serial.is_open = True
        mock_serial_class.return_value = mock_serial

        # -45 degrees in counts
        counts = int(-45 * KDC101Stage.ENCODER_COUNTS_PER_DEG)
        mock_serial.read.return_value = self._create_position_response(counts)

        stage = KDC101Stage("/dev/test")
        stage._serial = mock_serial
        stage._connected = True

        result = stage.get_position_degrees()

        assert result is not None
        assert abs(result - (-45.0)) < 0.1

    def test_get_position_not_connected(self):
        """Test position read returns None when not connected."""
        stage = KDC101Stage("/dev/test")

        result = stage.get_position_counts()

        assert result is None


class TestKDC101Commands:
    """Tests for command message generation."""

    @patch("serial.Serial")
    def test_identify_sends_correct_message(self, mock_serial_class):
        """Test identify command sends correct APT message."""
        mock_serial = MagicMock()
        mock_serial.is_open = True
        mock_serial_class.return_value = mock_serial

        stage = KDC101Stage("/dev/test")
        stage._serial = mock_serial
        stage._connected = True

        stage.identify()

        # Check message was sent
        mock_serial.write.assert_called()
        sent_msg = mock_serial.write.call_args[0][0]

        # Verify message ID
        msg_id = struct.unpack("<H", sent_msg[0:2])[0]
        assert msg_id == KDC101Stage.MSG_MOD_IDENTIFY

    @patch("serial.Serial")
    def test_enable_sends_correct_message(self, mock_serial_class):
        """Test enable command sends correct APT message."""
        mock_serial = MagicMock()
        mock_serial.is_open = True
        mock_serial_class.return_value = mock_serial

        stage = KDC101Stage("/dev/test")
        stage._serial = mock_serial
        stage._connected = True

        stage.enable(True)

        mock_serial.write.assert_called()
        sent_msg = mock_serial.write.call_args[0][0]

        msg_id = struct.unpack("<H", sent_msg[0:2])[0]
        assert msg_id == KDC101Stage.MSG_MOD_SET_CHANENABLESTATE
        # Enable state should be 0x01
        assert sent_msg[3] == 0x01

    @patch("serial.Serial")
    def test_disable_sends_correct_state(self, mock_serial_class):
        """Test disable command sends correct state byte."""
        mock_serial = MagicMock()
        mock_serial.is_open = True
        mock_serial_class.return_value = mock_serial

        stage = KDC101Stage("/dev/test")
        stage._serial = mock_serial
        stage._connected = True

        stage.enable(False)

        sent_msg = mock_serial.write.call_args[0][0]
        # Disable state should be 0x02
        assert sent_msg[3] == 0x02


class TestKDC101StatusUpdate:
    """Tests for status update message parsing."""

    def _create_status_response(self, position_counts: int) -> bytes:
        """Helper to create a status update response."""
        # MSG_MOT_GET_USTATUSUPDATE response:
        # [msg_id (2)] [data_len (2)] [dest|src (2)] [chan (2)] [position (4)] [...]
        response = struct.pack("<H", KDC101Stage.MSG_MOT_GET_USTATUSUPDATE)
        response += struct.pack("<H", 14)  # Data length
        response += struct.pack("<BB", KDC101Stage.HOST, KDC101Stage.DEVICE)
        response += struct.pack("<H", KDC101Stage.CHANNEL)
        response += struct.pack("<i", position_counts)  # Position
        response += b"\x00" * 6  # Remaining status bytes
        return response

    @patch("serial.Serial")
    def test_get_position_from_status(self, mock_serial_class):
        """Test position extraction from status update."""
        mock_serial = MagicMock()
        mock_serial.is_open = True
        mock_serial_class.return_value = mock_serial

        expected_counts = 345536  # ~180°
        mock_serial.read.return_value = self._create_status_response(expected_counts)

        stage = KDC101Stage("/dev/test")
        stage._serial = mock_serial
        stage._connected = True

        result = stage._get_position_from_status()

        assert result == expected_counts


# =============================================================================
# Hardware Tests (require actual KDC101 connected)
# =============================================================================


def pytest_addoption(parser):
    """Add --hardware option for pytest."""
    parser.addoption(
        "--hardware",
        action="store_true",
        default=False,
        help="Run tests that require actual hardware",
    )


@pytest.fixture
def hardware_stage():
    """Fixture that provides a connected KDC101 stage for hardware tests."""
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
    """
    Tests that require actual KDC101 hardware.

    Run with: pytest test_kdc101.py -v --hardware
    """

    def test_hardware_connect(self, hardware_stage):
        """Test actual hardware connection."""
        assert hardware_stage.connected is True

    def test_hardware_read_position(self, hardware_stage):
        """Test reading position from actual hardware."""
        position = hardware_stage.get_position_degrees()

        assert position is not None
        # Position should be reasonable (within ±720°)
        assert -720 <= position <= 720

    def test_hardware_identify(self, hardware_stage):
        """Test identify command (LED should flash)."""
        # This should not raise an exception
        hardware_stage.identify()

    def test_hardware_multiple_reads(self, hardware_stage):
        """Test multiple consecutive position reads."""
        import time

        positions = []
        for _ in range(5):
            pos = hardware_stage.get_position_degrees()
            if pos is not None:
                positions.append(pos)
            time.sleep(0.1)

        assert len(positions) >= 3  # At least 3 successful reads

        # If stage is stationary, positions should be similar
        if len(positions) >= 2:
            max_diff = max(positions) - min(positions)
            # Allow 0.5° drift for stationary stage
            assert max_diff < 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
