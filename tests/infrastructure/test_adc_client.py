"""
Tests for ADCClient via MockArduino — SCPI 2.0.0.

Verifies one-shot voltage/temperature reads, ADC configuration,
PD-TIA gain control, and Malus-law simulation in the mock.

Run with: .venv/bin/pytest tests/infrastructure/test_adc_client.py
"""

import math
import pytest
import time

from polarisation_ui.infrastructure.devices import DualEncoderArduino, MockArduino


@pytest.fixture
def mock_arduino():
    mock = MockArduino(poll_interval_ms=50, start_angle_a=0.0, start_angle_b=0.0)
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


# ── Voltage reads ─────────────────────────────────────────────────────────────

class TestVoltageRead:

    def test_read_voltage_returns_float(self, encoder_client):
        v = encoder_client.adc.read_voltage()
        assert v is not None
        assert isinstance(v, float)

    def test_read_voltage_in_range(self, encoder_client):
        """Voltage must be within [0, V_REF=2.048]."""
        for _ in range(5):
            v = encoder_client.adc.read_voltage()
            assert v is not None
            assert 0.0 <= v <= 2.1  # small headroom above V_REF for noise

    def test_voltage_malus_law_at_zero_angle(self, encoder_client, mock_arduino):
        """At sample angle = 0°, cos²(0) = 1 → voltage near V_REF."""
        mock, _ = mock_arduino
        mock.set_encoder_a_angle(0.0)
        v = encoder_client.adc.read_voltage()
        assert v is not None
        assert v > 1.9  # close to 2.048 V

    def test_voltage_malus_law_at_90_degrees(self, encoder_client, mock_arduino):
        """At sample angle = 90°, cos²(90°) = 0 → voltage near 0 V."""
        mock, _ = mock_arduino
        mock.set_encoder_a_angle(90.0)
        # Allow a brief moment for angle to take effect
        v = encoder_client.adc.read_voltage()
        assert v is not None
        assert v < 0.1  # near zero

    def test_voltage_varies_with_angle(self, encoder_client, mock_arduino):
        """Voltage at 45° should be roughly half of voltage at 0°."""
        mock, _ = mock_arduino
        mock.set_encoder_a_angle(0.0)
        v_zero = encoder_client.adc.read_voltage()

        mock.set_encoder_a_angle(45.0)
        v_45 = encoder_client.adc.read_voltage()

        assert v_zero is not None and v_45 is not None
        # cos²(45°) ≈ 0.5, so v_45 should be roughly half of v_zero
        assert v_45 < v_zero * 0.75


# ── Temperature reads ─────────────────────────────────────────────────────────

class TestTemperatureRead:

    def test_read_temperature_returns_float(self, encoder_client):
        temp = encoder_client.adc.read_temperature()
        assert temp is not None
        assert isinstance(temp, float)

    def test_read_temperature_in_range(self, encoder_client):
        """Mock temperature should be near 25 °C."""
        temp = encoder_client.adc.read_temperature()
        assert temp is not None
        assert 20.0 <= temp <= 30.0


# ── ADC configuration ─────────────────────────────────────────────────────────

class TestADCConfiguration:

    def test_set_gain(self, encoder_client, mock_arduino):
        mock, _ = mock_arduino
        assert encoder_client.adc.set_gain(8)
        state = mock.get_state()
        assert state["adc_gain"] == 8

    def test_configure_batch(self, encoder_client, mock_arduino):
        mock, _ = mock_arduino
        result = encoder_client.adc.configure(gain=4, mux="DIFF01", rate=90)
        assert result
        state = mock.get_state()
        assert state["adc_gain"] == 4

    def test_set_gain_reflected_in_mock(self, encoder_client, mock_arduino):
        mock, _ = mock_arduino
        encoder_client.adc.set_gain(128)
        assert mock.get_state()["adc_gain"] == 128


# ── PD-TIA gain ───────────────────────────────────────────────────────────────

class TestPdTiaGain:

    def test_set_pdtia_gain(self, encoder_client, mock_arduino):
        mock, _ = mock_arduino
        assert encoder_client.adc.set_pdtia_gain(2)
        assert mock.get_state()["pdtia_gain"] == 2

    def test_get_pdtia_gain_format(self, encoder_client, mock_arduino):
        mock, _ = mock_arduino
        encoder_client.adc.set_pdtia_gain(3)
        response = encoder_client.adc.get_pdtia_gain()
        assert response is not None
        # Expected format: "3,0b0011"
        assert response.startswith("3,")
        assert "0b" in response

    def test_pdtia_gain_zero_default(self, mock_arduino):
        mock, pty_path = mock_arduino
        encoder = DualEncoderArduino(port=pty_path)
        assert encoder.connect()
        assert mock.get_state()["pdtia_gain"] == 0
        encoder.disconnect()


# ── CONF:SRC and CONF:RATE ────────────────────────────────────────────────────

class TestStreamConfiguration:

    def test_conf_src_stored_in_mock(self, encoder_client, mock_arduino):
        mock, _ = mock_arduino
        # start_continuous_both sends CONF:SRC ENC:BOTH,ADC + INIT:CONT ON
        encoder_client.start_continuous_both()
        state = mock.get_state()
        assert "ENC:BOTH" in state["stream_sources"]
        assert "ADC" in state["stream_sources"]
        encoder_client.abort()

    def test_conf_rate_updates_poll_interval(self, encoder_client, mock_arduino):
        mock, _ = mock_arduino
        # set_poll_interval(100 ms) → CONF:RATE 10 Hz → poll_interval_ms = 100
        assert encoder_client.set_poll_interval(100)
        state = mock.get_state()
        assert state["stream_rate_hz"] == 10
        assert state["poll_interval_ms"] == 100
