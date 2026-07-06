"""Tests for DualEncoderArduino using MockArduino — SCPI 2.0.0.

Run with: .venv/bin/pytest tests/infrastructure/test_dual_encoder_with_mock.py
"""

import sys
import pytest
import time
from polarisation_ui.infrastructure.devices import (
    DualEncoderArduino,
    EncoderID,
    StreamSource,
)
from polarisation_ui.infrastructure.mocks import MockArduino

pytestmark = pytest.mark.skipif(
    sys.platform == "win32", reason="PTY not available on Windows"
)


def _await_mock_state(mock, predicate, timeout: float = 2.0) -> bool:
    """Poll mock.get_state() until predicate returns True or timeout expires.

    Fire-and-forget SCPI commands are processed by the MockArduino PTY thread
    asynchronously.  On Linux CI the scheduler may not switch to that thread
    before the test asserts state, causing a race.  Polling at 10 ms intervals
    is more robust than an arbitrary sleep.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        if predicate(mock.get_state()):
            return True
        time.sleep(0.01)
    return False


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
    def test_read_angle_a(self, encoder_client):
        val = encoder_client.read_angle(EncoderID.A)
        assert val is not None
        assert val.encoder_id == EncoderID.A
        assert isinstance(val.angle_deg, float)
        assert 9.0 < val.angle_deg < 11.0

    def test_read_angle_b(self, encoder_client):
        val = encoder_client.read_angle(EncoderID.B)
        assert val is not None
        assert val.encoder_id == EncoderID.B
        assert isinstance(val.angle_deg, float)
        assert 19.0 < val.angle_deg < 21.0

    def test_read_angle_both(self, encoder_client):
        both = encoder_client.read_angle("BOTH")
        assert both is not None
        assert hasattr(both, "angle_a")
        assert hasattr(both, "angle_b")
        assert 9.0 < both.angle_a < 11.0
        assert 19.0 < both.angle_b < 21.0

    def test_read_angle_raw_is_none(self, encoder_client):
        # angle_raw is not populated by MEAS:ENC:ANGL? (magnitude needs MEAS:ENC:MAGN?)
        val = encoder_client.read_angle(EncoderID.A)
        assert val is not None
        assert val.angle_raw is None

    def test_read_magnitude(self, encoder_client):
        mag = encoder_client.read_magnitude(EncoderID.A)
        assert mag is not None
        assert isinstance(mag, int)
        assert 0 <= mag <= 16383


# ── Zero reset ────────────────────────────────────────────────────────────────


class TestZeroReset:
    def test_zero_a(self, encoder_client, mock_arduino):
        mock, _ = mock_arduino
        initial = encoder_client.read_angle(EncoderID.A)
        assert initial is not None

        assert encoder_client.zero(EncoderID.A)

        time.sleep(0.1)
        after = encoder_client.read_angle(EncoderID.A)
        assert after is not None
        assert abs(after.angle_deg) < 0.1

    def test_zero_b(self, encoder_client, mock_arduino):
        mock, _ = mock_arduino
        assert encoder_client.zero(EncoderID.B)
        time.sleep(0.1)
        after = encoder_client.read_angle(EncoderID.B)
        assert after is not None
        assert abs(after.angle_deg) < 0.1

    def test_zero_both(self, encoder_client):
        assert encoder_client.zero("BOTH")
        time.sleep(0.1)
        a = encoder_client.read_angle(EncoderID.A)
        b = encoder_client.read_angle(EncoderID.B)
        assert a is not None and abs(a.angle_deg) < 0.1
        assert b is not None and abs(b.angle_deg) < 0.1

    def test_zero_independent(self, encoder_client, mock_arduino):
        mock, _ = mock_arduino
        encoder_client.zero(EncoderID.A)
        time.sleep(0.1)
        a = encoder_client.read_angle(EncoderID.A)
        b = encoder_client.read_angle(EncoderID.B)
        assert a is not None and abs(a.angle_deg) < 0.1
        assert b is not None and 19.0 < b.angle_deg < 21.0


# ── Parametric tests (new per plan) ──────────────────────────────────────────


class TestParametricAPI:
    def test_read_angle_parametric(self, encoder_client, mock_arduino):
        mock, _ = mock_arduino
        mock.set_encoder_angle("A", 30.0)
        mock.set_encoder_angle("B", 60.0)
        time.sleep(0.05)

        val_a = encoder_client.read_angle(EncoderID.A)
        val_b = encoder_client.read_angle(EncoderID.B)
        both = encoder_client.read_angle("BOTH")

        assert val_a is not None and 29.0 < val_a.angle_deg < 31.0
        assert val_b is not None and 59.0 < val_b.angle_deg < 61.0
        assert both is not None
        assert 29.0 < both.angle_a < 31.0
        assert 59.0 < both.angle_b < 61.0

    def test_zero_and_clear_error_parametric(self, encoder_client):
        for target in (EncoderID.A, EncoderID.B, "BOTH"):
            assert encoder_client.zero(target)
            assert encoder_client.clear_error(target)

    def test_diagnostics_both_single_roundtrip(self, encoder_client):
        """query_diagnostics('BOTH') returns (diag_a, diag_b) from one DIAG:ENC? BOTH call."""
        result = encoder_client.query_diagnostics("BOTH")
        assert result is not None
        diag_a, diag_b = result
        # Both dicts must be populated — confirms the BOTH path parsed correctly
        assert isinstance(diag_a, dict)
        assert isinstance(diag_b, dict)
        for key in ("compHigh", "compLow", "cof", "ocf", "agc"):
            assert key in diag_a
            assert key in diag_b


# ── Continuous mode ───────────────────────────────────────────────────────────


class TestContinuousMode:
    def test_start_stop_stream_enc_a(self, encoder_client, mock_arduino):
        mock, _ = mock_arduino

        assert encoder_client.start_stream([StreamSource.ENC_A])
        assert _await_mock_state(
            mock, lambda s: s["continuous_running"]
        ), "continuous mode not started"
        state = mock.get_state()
        assert state["continuous_running"]
        assert "ENC:A" in state["stream_sources"]

        assert encoder_client.abort()
        assert _await_mock_state(
            mock, lambda s: not s["continuous_running"]
        ), "continuous mode not stopped"
        assert not mock.get_state()["continuous_running"]

    def test_start_stop_stream_enc_both(self, encoder_client, mock_arduino):
        mock, _ = mock_arduino

        assert encoder_client.start_stream(
            [StreamSource.ENC_BOTH, StreamSource.ADC, StreamSource.DIAG]
        )
        assert _await_mock_state(
            mock, lambda s: s["continuous_running"]
        ), "continuous mode not started"
        state = mock.get_state()
        assert state["continuous_running"]
        assert "ENC:A" in state["stream_sources"]
        assert "ENC:B" in state["stream_sources"]
        assert "DIAG" in state["stream_sources"]

        assert encoder_client.abort()
        assert _await_mock_state(
            mock, lambda s: not s["continuous_running"]
        ), "continuous mode not stopped"
        assert not mock.get_state()["continuous_running"]

    def test_continuous_values_advance(self, encoder_client, mock_arduino):
        """Verify encoder angle advances while streaming is running."""
        mock, _ = mock_arduino
        mock.set_encoder_angle("A", 0.0)

        encoder_client.start_stream([StreamSource.ENC_A])
        initial_angle = mock.get_state()["encoder_a"]["current_angle"]
        time.sleep(0.2)  # ~4 intervals at 50ms
        encoder_client.abort()

        final_angle = mock.get_state()["encoder_a"]["current_angle"]
        assert final_angle > initial_angle

    def test_both_encoders_different_speeds(self, encoder_client, mock_arduino):
        """Verify encoder A advances faster than B when speeds differ."""
        mock, _ = mock_arduino
        mock.set_encoder_angle("A", 0.0)
        mock.set_encoder_angle("B", 0.0)

        encoder_client.start_stream(
            [StreamSource.ENC_BOTH, StreamSource.ADC, StreamSource.DIAG]
        )
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
        diag = encoder_client.query_diagnostics(EncoderID.A)
        assert diag is not None
        assert isinstance(diag, dict)
        for key in ("compHigh", "compLow", "cof", "ocf"):
            assert key in diag
            assert isinstance(diag[key], bool)
        assert "agc" in diag
        assert isinstance(diag["agc"], int)

    def test_diagnostics_b(self, encoder_client):
        diag = encoder_client.query_diagnostics(EncoderID.B)
        assert diag is not None
        assert isinstance(diag, dict)

    def test_diagnostics_both(self, encoder_client):
        result = encoder_client.query_diagnostics("BOTH")
        assert result is not None
        diag_a, diag_b = result
        assert diag_a is not None
        assert diag_b is not None
        assert isinstance(diag_a, dict)
        assert isinstance(diag_b, dict)


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
        encoder_client.zero(EncoderID.A)
        assert _await_mock_state(
            mock, lambda s: s["encoder_a"]["zero_offset"] == 10.0
        ), "zero_offset not updated after zero(A)"
        state = mock.get_state()
        assert state["encoder_a"]["zero_offset"] == 10.0
        assert state["encoder_a"]["effective_angle"] == 0.0

    def test_manual_angle_set(self, mock_arduino):
        mock, _ = mock_arduino
        mock.set_encoder_angle("A", 45.0)
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

    def test_empty_idn_response_raises(self, mock_arduino):
        """An empty/garbled *IDN? response must not silently skip the version check.

        Regression test: connect() used to do ``if idn: _check_firmware_version(...)``,
        so a falsy response from query_idn() (no reply, garbled line) bypassed the
        check entirely and connect() returned True.
        """
        from polarisation_ui.core.exceptions import IncompatibleFirmwareError

        mock, pty_path = mock_arduino
        encoder = DualEncoderArduino(port=pty_path)
        encoder.query_idn = lambda: ""
        with pytest.raises(IncompatibleFirmwareError):
            encoder.connect()


# ── DATA:FRAME parser ─────────────────────────────────────────────────────────


class TestDataFrameParser:
    def test_parse_full_frame(self):
        line = (
            "DATA:FRAME tsMs=1234,angA=45.50,angB=91.00,adcV=1.234567,pdGain=0,stat=0"
        )
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


# ── MockArduino ↔ firmware 2.1.0 parity ────────────────────────────────────────


class TestFirmwareParity:
    """Regression tests for MockArduino behaviors added to match firmware 2.1.0."""

    def test_idn_reports_2_1_0_by_default(self, mock_arduino):
        mock, pty_path = mock_arduino
        encoder = DualEncoderArduino(port=pty_path)
        assert encoder.connect()
        assert encoder.firmware_version == "2.1.0"
        encoder.disconnect()

    def test_fetc_all_matches_meas_all_six_fields(self, encoder_client):
        """FETC:ALL? is an alias of MEAS:ALL? in firmware — both are
        tsMs,angA,angB,magA,magB,volt (6 fields). The mock used to return
        only 4 fields (tsMs,angA,angB,volt) for FETC:ALL?.
        """
        meas = encoder_client.send_query("MEAS:ALL?")
        fetc = encoder_client.send_query("FETC:ALL?")
        assert meas is not None and fetc is not None
        assert len(meas.split(",")) == 6
        assert len(fetc.split(",")) == 6

    def test_read_bare_matches_meas_all(self, encoder_client):
        resp = encoder_client.send_query("READ?")
        assert resp is not None
        assert len(resp.split(",")) == 6

    def test_read_adc_returns_voltage(self, encoder_client):
        resp = encoder_client.send_query("READ? ADC")
        assert resp is not None
        float(resp)  # must parse as a plain voltage, not a multi-field frame

    def test_read_adc_temp_returns_temperature(self, encoder_client):
        resp = encoder_client.send_query("READ? ADC:T")
        assert resp is not None
        float(resp)

    def test_conf_adc_pwr_round_trips(self, encoder_client):
        assert encoder_client.send_control_command("CONF:ADC:PWR OFF")
        assert encoder_client.send_query("CONF:ADC:PWR?") == "OFF"
        assert encoder_client.send_control_command("CONF:ADC:PWR ON")
        assert encoder_client.send_query("CONF:ADC:PWR?") == "ON"

    def test_diag_self_returns_one_line_per_subsystem(self, encoder_client):
        lines = encoder_client.query_self_test()
        assert lines is not None
        assert len(lines) == 4
        assert lines[0] == "DIAG:SELF ENC:A,PASS"
        assert lines[1] == "DIAG:SELF ENC:B,PASS"
        assert lines[2] == "DIAG:SELF ADC,PASS"
        assert lines[3] == "DIAG:SELF PDTIA,PASS"

    def test_conf_src_rejects_unknown_token(self, encoder_client):
        """Regression test: the mock used to accept any CONF:SRC token
        verbatim with no validation, unlike firmware's handleConfSrc(),
        which rejects the whole command on the first unrecognised token.
        """
        assert encoder_client.send_control_command("CONF:SRC ADC")
        before = encoder_client.send_query("CONF:SRC?")

        assert encoder_client.send_control_command("CONF:SRC BOGUS:TOKEN")
        after = encoder_client.send_query("CONF:SRC?")

        assert after == before  # rejected command must not change state

    def test_conf_src_rejects_enc_b_when_absent(self, mock_arduino):
        """Regression test: the mock had no concept of "encoder B absent" at
        all, so it could never exercise the -241 rejection path that
        firmware's handleConfSrc() enforces for ENC:B/ENC:BOTH.
        """
        mock, pty_path = mock_arduino
        mock.encoder_b_present = False
        encoder = DualEncoderArduino(port=pty_path)
        assert encoder.connect()
        try:
            assert encoder.send_control_command("CONF:SRC ADC")
            before = encoder.send_query("CONF:SRC?")

            assert encoder.send_control_command("CONF:SRC ENC:BOTH")
            after = encoder.send_query("CONF:SRC?")

            assert after == before
        finally:
            encoder.disconnect()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
