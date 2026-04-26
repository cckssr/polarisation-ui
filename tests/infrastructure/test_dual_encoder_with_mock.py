"""
Tests for DualEncoderArduino using MockArduino — SCPI 2.0.0.

Run with: .venv/bin/pytest tests/infrastructure/test_dual_encoder_with_mock.py
"""

import pytest
import time
from polarisation_ui.infrastructure.devices import (
    DualEncoderArduino,
    MockArduino,
    EncoderID,
)


@pytest.fixture
def mock_arduino():
    mock = MockArduino(
        encoder_a_speed=0.5,
        encoder_b_speed=0.3,
        poll_interval_ms=50,
        start_angle_a=10.0,
        start_angle_b=20.0,
    )
    pty_path = mock.start()
    yield mock, pty_path
    mock.stop()


@pytest.fixture
def encoder_client(mock_arduino):
    mock, pty_path = mock_arduino
    encoder = DualEncoderArduino(port=pty_path)
    assert encoder.connect()
    yield encoder
    encoder.disconnect()


# ── Basic reads ───────────────────────────────────────────────────────────────

class TestBasicReading:

    def test_read_encoder_a(self, encoder_client):
        angle = encoder_client.read_encoder_a()
        assert angle is not None
        assert isinstance(angle, float)
        assert 9.0 < angle < 11.0

    def test_read_encoder_b(self, encoder_client):
        angle = encoder_client.read_encoder_b()
        assert angle is not None
        assert isinstance(angle, float)
        assert 19.0 < angle < 21.0

    def test_read_both(self, encoder_client):
        both = encoder_client.read_both()
        assert both is not None
        assert hasattr(both, "angle_a")
        assert hasattr(both, "angle_b")
        assert 9.0 < both.angle_a < 11.0
        assert 19.0 < both.angle_b < 21.0

    def test_read_single(self, encoder_client):
        value = encoder_client.read_single(EncoderID.A)
        assert value is not None
        assert value.encoder_id == EncoderID.A
        assert isinstance(value.angle_deg, float)
        # angle_raw is not populated by MEAS:ENC:ANGL? (magnitude needs MEAS:ENC:MAGN?)
        assert value.angle_raw is None

    def test_read_magnitude(self, encoder_client):
        mag = encoder_client.read_magnitude(EncoderID.A)
        assert mag is not None
        assert isinstance(mag, int)
        assert 0 <= mag <= 16383


# ── Zero reset ────────────────────────────────────────────────────────────────

class TestZeroReset:

    def test_reset_zero_a(self, encoder_client, mock_arduino):
        mock, _ = mock_arduino
        initial = encoder_client.read_encoder_a()
        assert initial is not None

        assert encoder_client.reset_zero_a()

        time.sleep(0.1)
        after = encoder_client.read_encoder_a()
        assert after is not None
        assert abs(after) < 0.1

    def test_reset_zero_b(self, encoder_client, mock_arduino):
        mock, _ = mock_arduino
        assert encoder_client.reset_zero_b()
        time.sleep(0.1)
        after = encoder_client.read_encoder_b()
        assert after is not None
        assert abs(after) < 0.1

    def test_reset_zero_both(self, encoder_client):
        assert encoder_client.reset_zero_both()
        time.sleep(0.1)
        assert abs(encoder_client.read_encoder_a()) < 0.1
        assert abs(encoder_client.read_encoder_b()) < 0.1

    def test_zero_offset_independent(self, encoder_client, mock_arduino):
        mock, _ = mock_arduino
        encoder_client.reset_zero_a()
        time.sleep(0.1)
        assert abs(encoder_client.read_encoder_a()) < 0.1
        assert 19.0 < encoder_client.read_encoder_b() < 21.0


# ── Continuous mode ───────────────────────────────────────────────────────────

class TestContinuousMode:

    def test_start_stop_continuous_a(self, encoder_client, mock_arduino):
        mock, _ = mock_arduino

        assert encoder_client.start_continuous_a()
        state = mock.get_state()
        assert state["continuous_running"]
        assert "ENC:A" in state["stream_sources"]

        assert encoder_client.abort()
        state = mock.get_state()
        assert not state["continuous_running"]

    def test_start_stop_continuous_both(self, encoder_client, mock_arduino):
        mock, _ = mock_arduino

        assert encoder_client.start_continuous_both()
        state = mock.get_state()
        assert state["continuous_running"]
        assert "ENC:BOTH" in state["stream_sources"]

        assert encoder_client.abort()
        assert not mock.get_state()["continuous_running"]

    def test_continuous_values_advance(self, encoder_client, mock_arduino):
        """Verify encoder angle advances while streaming is running."""
        mock, _ = mock_arduino
        mock.set_encoder_a_angle(0.0)

        encoder_client.start_continuous_a()
        initial_angle = mock.get_state()["encoder_a"]["current_angle"]
        time.sleep(0.2)  # ~4 intervals at 50ms
        encoder_client.abort()

        final_angle = mock.get_state()["encoder_a"]["current_angle"]
        assert final_angle > initial_angle

    def test_both_encoders_different_speeds(self, encoder_client, mock_arduino):
        """Verify encoder A advances faster than B when speeds differ."""
        mock, _ = mock_arduino
        mock.set_encoder_a_angle(0.0)
        mock.set_encoder_b_angle(0.0)

        encoder_client.start_continuous_both()
        time.sleep(0.3)
        encoder_client.abort()

        state = mock.get_state()
        assert state["encoder_a"]["current_angle"] > state["encoder_b"]["current_angle"]


# ── Poll rate ─────────────────────────────────────────────────────────────────

class TestPollInterval:

    def test_set_poll_interval_valid(self, encoder_client):
        assert encoder_client.set_poll_interval(100)

    def test_set_poll_interval_min(self, encoder_client):
        assert encoder_client.set_poll_interval(1)

    def test_set_poll_interval_max(self, encoder_client):
        assert encoder_client.set_poll_interval(9999)

    def test_set_poll_interval_invalid_low(self, encoder_client):
        assert not encoder_client.set_poll_interval(0)

    def test_set_poll_interval_invalid_high(self, encoder_client):
        assert not encoder_client.set_poll_interval(10000)


# ── Diagnostics ───────────────────────────────────────────────────────────────

class TestDiagnostics:

    def test_diagnostics_a(self, encoder_client):
        diag = encoder_client.get_diagnostics_a()
        assert diag is not None
        assert isinstance(diag, dict)
        for key in ("compHigh", "compLow", "cof", "ocf"):
            assert key in diag
            assert isinstance(diag[key], bool)
        assert "agc" in diag
        assert isinstance(diag["agc"], int)

    def test_diagnostics_b(self, encoder_client):
        diag = encoder_client.get_diagnostics_b()
        assert diag is not None
        assert isinstance(diag, dict)


# ── Connection lifecycle ──────────────────────────────────────────────────────

class TestConnectionManagement:

    def test_connect_disconnect(self, mock_arduino):
        mock, pty_path = mock_arduino
        encoder = DualEncoderArduino(port=pty_path)
        assert not encoder.is_connected()
        assert encoder.connect()
        assert encoder.is_connected()
        encoder.disconnect()
        assert not encoder.is_connected()

    def test_multiple_connects(self, mock_arduino):
        mock, pty_path = mock_arduino
        encoder = DualEncoderArduino(port=pty_path)
        assert encoder.connect()
        encoder.disconnect()
        assert encoder.connect()
        encoder.disconnect()


# ── MockArduino state ─────────────────────────────────────────────────────────

class TestMockArduinoState:

    def test_initial_state(self, mock_arduino):
        mock, _ = mock_arduino
        state = mock.get_state()
        assert not state["continuous_running"]
        assert state["encoder_a"]["current_angle"] == 10.0
        assert state["encoder_b"]["current_angle"] == 20.0
        assert state["pdtia_gain"] == 0

    def test_state_after_zero_reset(self, mock_arduino, encoder_client):
        mock, _ = mock_arduino
        encoder_client.reset_zero_a()
        state = mock.get_state()
        assert state["encoder_a"]["zero_offset"] == 10.0
        assert state["encoder_a"]["effective_angle"] == 0.0

    def test_manual_angle_set(self, mock_arduino):
        mock, _ = mock_arduino
        mock.set_encoder_a_angle(45.0)
        state = mock.get_state()
        assert state["encoder_a"]["current_angle"] == 45.0
        assert state["encoder_a"]["effective_angle"] == 45.0


# ── Firmware version check ────────────────────────────────────────────────────

class TestFirmwareVersionCheck:

    def test_compatible_firmware_connects(self, mock_arduino):
        """2.0.0 mock should connect without error."""
        mock, pty_path = mock_arduino
        encoder = DualEncoderArduino(port=pty_path)
        assert encoder.connect()
        encoder.disconnect()

    def test_incompatible_firmware_raises(self, mock_arduino):
        """Firmware 1.0 should raise IncompatibleFirmwareError."""
        from polarisation_ui.core.exceptions import IncompatibleFirmwareError

        mock, pty_path = mock_arduino
        mock.set_firmware_version("1.0.0")

        encoder = DualEncoderArduino(port=pty_path)
        with pytest.raises(IncompatibleFirmwareError):
            encoder.connect()


# ── DATA:FRAME parser ─────────────────────────────────────────────────────────

class TestDataFrameParser:

    def test_parse_full_frame(self):
        line = "DATA:FRAME tsMs=1234,angA=45.50,angB=91.00,adcV=1.234567,pdGain=0,stat=0"
        result = DualEncoderArduino._parse_data_frame(line)
        assert result["tsMs"] == "1234"
        assert result["angA"] == "45.50"
        assert result["angB"] == "91.00"
        assert result["adcV"] == "1.234567"

    def test_parse_unknown_keys_included(self):
        line = "DATA:FRAME tsMs=1,newKey=99"
        result = DualEncoderArduino._parse_data_frame(line)
        assert result["newKey"] == "99"

    def test_parse_non_frame_returns_empty(self):
        assert DualEncoderArduino._parse_data_frame("0,0,0,1,200") == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
