"""
Unit tests for DualEncoderArduino using MockArduino.

Demonstrates how to write tests that exercise the full encoder interface
without requiring real hardware.

Run with: pytest tests/infrastructure/test_dual_encoder_with_mock.py
"""

import pytest
import time
from polarisation_ui.infrastructure.devices import (
    DualEncoderArduino,
    MockArduino,
    EncoderID,
)
from polarisation_ui.infrastructure.logging import Debug


@pytest.fixture
def debug_setup():
    """Setup logging for tests."""
    Debug.setup(level="DEBUG")
    yield
    # Cleanup if needed


@pytest.fixture
def mock_arduino():
    """Fixture: Create and start mock Arduino."""
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
    """Fixture: Create DualEncoderArduino connected to mock."""
    mock, pty_path = mock_arduino
    encoder = DualEncoderArduino(port=pty_path)
    assert encoder.connect()
    yield encoder
    encoder.disconnect()


class TestBasicReading:
    """Tests for basic single reads."""

    def test_read_encoder_a(self, encoder_client):
        """Test reading encoder A."""
        angle = encoder_client.read_encoder_a()
        assert angle is not None
        assert isinstance(angle, float)
        assert 9.0 < angle < 11.0  # Started at 10°

    def test_read_encoder_b(self, encoder_client):
        """Test reading encoder B."""
        angle = encoder_client.read_encoder_b()
        assert angle is not None
        assert isinstance(angle, float)
        assert 19.0 < angle < 21.0  # Started at 20°

    def test_read_both(self, encoder_client):
        """Test reading both encoders simultaneously."""
        both = encoder_client.read_both()
        assert both is not None
        assert hasattr(both, "angle_a")
        assert hasattr(both, "angle_b")
        assert 9.0 < both.angle_a < 11.0
        assert 19.0 < both.angle_b < 21.0

    def test_read_single_with_raw(self, encoder_client):
        """Test reading with raw value."""
        value = encoder_client.read_single(EncoderID.A)
        assert value is not None
        assert value.encoder_id == EncoderID.A
        assert value.angle_deg is not None
        assert value.angle_raw is not None
        assert isinstance(value.angle_raw, int)
        assert 0 <= value.angle_raw <= 65535


class TestZeroReset:
    """Tests for zero position management."""

    def test_reset_zero_a_basic(self, encoder_client, mock_arduino):
        """Test resetting encoder A zero position."""
        mock, _ = mock_arduino

        # Get initial angle
        initial = encoder_client.read_encoder_a()
        assert initial is not None

        # Reset to zero
        success = encoder_client.reset_zero_a()
        assert success

        # Next reading should be near 0°
        time.sleep(0.1)
        after_reset = encoder_client.read_encoder_a()
        assert after_reset is not None
        assert abs(after_reset) < 0.1  # Very close to 0°

    def test_reset_zero_b_basic(self, encoder_client, mock_arduino):
        """Test resetting encoder B zero position."""
        mock, _ = mock_arduino

        # Get initial angle
        initial = encoder_client.read_encoder_b()
        assert initial is not None

        # Reset to zero
        success = encoder_client.reset_zero_b()
        assert success

        # Next reading should be near 0°
        time.sleep(0.1)
        after_reset = encoder_client.read_encoder_b()
        assert after_reset is not None
        assert abs(after_reset) < 0.1

    def test_reset_zero_both(self, encoder_client):
        """Test resetting both encoders to zero."""
        success = encoder_client.reset_zero_both()
        assert success

        time.sleep(0.1)

        # Both should be near 0°
        a = encoder_client.read_encoder_a()
        b = encoder_client.read_encoder_b()
        assert abs(a) < 0.1
        assert abs(b) < 0.1

    def test_zero_offset_independent(self, encoder_client, mock_arduino):
        """Test that zero offsets for A and B are independent."""
        mock, _ = mock_arduino

        # Reset only encoder A
        encoder_client.reset_zero_a()
        time.sleep(0.1)

        a_reset = encoder_client.read_encoder_a()
        b_unchanged = encoder_client.read_encoder_b()

        # A should be near 0°
        assert abs(a_reset) < 0.1

        # B should still be near 20° (not reset)
        assert 19.0 < b_unchanged < 21.0


class TestContinuousMode:
    """Tests for continuous polling modes."""

    def test_start_stop_continuous_a(self, encoder_client, mock_arduino):
        """Test starting and stopping continuous mode for A."""
        mock, _ = mock_arduino

        # Start continuous A
        success = encoder_client.start_continuous_a()
        assert success

        state = mock.get_state()
        assert state["continuous_running"]
        assert state["mode"] == "CONTINUOUS_A"

        # Stop continuous A
        success = encoder_client.stop_continuous_a()
        assert success

        state = mock.get_state()
        assert not state["continuous_running"]

    def test_start_stop_continuous_both(self, encoder_client, mock_arduino):
        """Test starting and stopping continuous mode for both."""
        mock, _ = mock_arduino

        # Start continuous BOTH
        success = encoder_client.start_continuous_both()
        assert success

        state = mock.get_state()
        assert state["continuous_running"]
        assert state["mode"] == "CONTINUOUS_BOTH"

        # Stop
        success = encoder_client.stop_continuous_both()
        assert success

        state = mock.get_state()
        assert not state["continuous_running"]

    def test_continuous_values_increase(self, encoder_client, mock_arduino):
        """Test that values increase during continuous mode."""
        mock, _ = mock_arduino

        # Manually set starting angle
        mock.set_encoder_a_angle(0.0)

        # Start continuous with known speed
        encoder_client.start_continuous_a()
        time.sleep(0.05)

        # Read first value
        val1 = encoder_client.read_encoder_a()
        time.sleep(0.2)  # Wait ~4 polling intervals at 50ms each

        # Read second value
        val2 = encoder_client.read_encoder_a()

        encoder_client.stop_continuous_a()

        # Second should be greater than first
        assert val2 > val1
        # Speed is 0.5°/poll, ~4 polls = ~2° difference
        assert (val2 - val1) > 1.0

    def test_both_encoders_different_speeds(self, encoder_client, mock_arduino):
        """Test that A and B advance at different speeds."""
        mock, _ = mock_arduino

        # Reset both to 0°
        mock.set_encoder_a_angle(0.0)
        mock.set_encoder_b_angle(0.0)

        # Start continuous mode
        encoder_client.start_continuous_both()

        # Let encoders advance (A at 0.5°/poll, B at 0.3°/poll)
        time.sleep(0.3)

        both = encoder_client.read_both()
        assert both is not None

        # A should be ahead of B
        assert both.angle_a > both.angle_b

        encoder_client.stop_continuous_both()


class TestPollInterval:
    """Tests for poll interval configuration."""

    def test_set_poll_interval_valid(self, encoder_client):
        """Test setting valid poll interval."""
        success = encoder_client.set_poll_interval(100)
        assert success

    def test_set_poll_interval_min(self, encoder_client):
        """Test setting minimum poll interval."""
        success = encoder_client.set_poll_interval(1)
        assert success

    def test_set_poll_interval_max(self, encoder_client):
        """Test setting maximum poll interval."""
        success = encoder_client.set_poll_interval(10000)
        assert success

    def test_set_poll_interval_invalid_low(self, encoder_client):
        """Test that invalid low interval is rejected."""
        success = encoder_client.set_poll_interval(0)
        assert not success

    def test_set_poll_interval_invalid_high(self, encoder_client):
        """Test that invalid high interval is rejected."""
        success = encoder_client.set_poll_interval(10001)
        assert not success


class TestDiagnostics:
    """Tests for encoder diagnostics."""

    def test_diagnostics_a(self, encoder_client):
        """Test reading diagnostics from encoder A."""
        diag = encoder_client.get_diagnostics_a()
        assert diag is not None
        assert isinstance(diag, dict)
        assert "compHigh" in diag
        assert "compLow" in diag
        assert "ocf" in diag
        assert "agc" in diag

    def test_diagnostics_b(self, encoder_client):
        """Test reading diagnostics from encoder B."""
        diag = encoder_client.get_diagnostics_b()
        assert diag is not None
        assert isinstance(diag, dict)

    def test_diagnostics_values_boolean(self, encoder_client):
        """Test that diagnostic flags are boolean."""
        diag = encoder_client.get_diagnostics_a()
        for key, value in diag.items():
            assert isinstance(value, bool)


class TestConnectionManagement:
    """Tests for connection lifecycle."""

    def test_connect_disconnect(self, mock_arduino):
        """Test connecting and disconnecting."""
        mock, pty_path = mock_arduino

        encoder = DualEncoderArduino(port=pty_path)

        # Initially not connected
        assert not encoder.is_connected()

        # Connect
        success = encoder.connect()
        assert success
        assert encoder.is_connected()

        # Disconnect
        encoder.disconnect()
        assert not encoder.is_connected()

    def test_multiple_connects(self, mock_arduino):
        """Test connecting multiple times."""
        mock, pty_path = mock_arduino

        encoder = DualEncoderArduino(port=pty_path)

        # First connect
        assert encoder.connect()
        assert encoder.is_connected()

        # Disconnect and reconnect
        encoder.disconnect()
        assert encoder.connect()
        assert encoder.is_connected()

        encoder.disconnect()


class TestMockArduinoState:
    """Tests for MockArduino state tracking."""

    def test_mock_state_initial(self, mock_arduino):
        """Test initial mock state."""
        mock, _ = mock_arduino

        state = mock.get_state()
        assert state["mode"] == "IDLE"
        assert not state["continuous_running"]
        assert state["encoder_a"]["current_angle"] == 10.0
        assert state["encoder_b"]["current_angle"] == 20.0

    def test_mock_state_after_zero_reset(self, mock_arduino, encoder_client):
        """Test mock state after zero reset."""
        mock, _ = mock_arduino

        encoder_client.reset_zero_a()
        state = mock.get_state()

        # Zero offset should be set
        assert state["encoder_a"]["zero_offset"] == 10.0
        # Effective angle should be 0
        assert state["encoder_a"]["effective_angle"] == 0.0

    def test_mock_manual_angle_set(self, mock_arduino):
        """Test manually setting encoder angles."""
        mock, _ = mock_arduino

        # Set specific angle
        mock.set_encoder_a_angle(45.0)

        state = mock.get_state()
        assert state["encoder_a"]["current_angle"] == 45.0
        assert state["encoder_a"]["effective_angle"] == 45.0  # No zero offset yet


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
