"""Mock-based unit tests for KDC101NDStage.

Patches kdc101_base's lazily-imported pylablib globals directly, mirroring
tests/infrastructure/test_kdc101_polariser.py. The interesting behaviour here
is the mm<->m unit conversion: pylablib's "MTS50-Z8" scale is natively in
metres (unlike "PRM1-Z8", which is natively in degrees), so KDC101NDStage
converts at its public API boundary.
"""

from unittest.mock import MagicMock

import pytest

import polarisation_ui.infrastructure.devices.kdc101_base as kdc_base
import polarisation_ui.infrastructure.devices.kdc101_nd_stage as nd_mod
from polarisation_ui.core.exceptions import KDC101Error, KDC101TimeoutError


class _FakeThorlabsError(Exception):
    pass


class _FakeThorlabsTimeoutError(_FakeThorlabsError):
    pass


@pytest.fixture
def fake_thorlabs(monkeypatch):
    """Patch kdc101_base's cached pylablib globals with fakes; returns the fake module."""
    fake_module = MagicMock()
    monkeypatch.setattr(kdc_base, "_Thorlabs", fake_module)
    monkeypatch.setattr(kdc_base, "_ThorlabsError", _FakeThorlabsError)
    monkeypatch.setattr(kdc_base, "_ThorlabsTimeoutError", _FakeThorlabsTimeoutError)
    monkeypatch.setattr(kdc_base, "_PYLABLIB_AVAILABLE", True)
    return fake_module


@pytest.fixture
def connected(fake_thorlabs):
    """Return (KDC101NDStage, mock_motor) already connected to a fake KinesisMotor."""
    mock_motor = MagicMock()
    fake_thorlabs.KinesisMotor.return_value = mock_motor
    nd = nd_mod.KDC101NDStage()
    nd.connect("mock-conn-id")
    return nd, mock_motor


@pytest.fixture(autouse=True)
def _no_real_sleep(monkeypatch):
    """Skip real waits between position polls in _wait_until_stopped()."""
    monkeypatch.setattr(kdc_base.time, "sleep", lambda _seconds: None)


class TestConnect:
    def test_connect_opens_motor_with_mts50z8_scale(self, fake_thorlabs):
        mock_motor = MagicMock()
        fake_thorlabs.KinesisMotor.return_value = mock_motor
        nd = nd_mod.KDC101NDStage()

        nd.connect("27123456")

        fake_thorlabs.KinesisMotor.assert_called_once_with("27123456", scale=nd_mod._MTS50_Z8_SCALE)
        mock_motor.open.assert_called_once()
        assert nd.is_connected() is True

    def test_connect_raises_kdc101error_when_pylablib_unavailable(self, monkeypatch):
        monkeypatch.setattr(kdc_base, "_PYLABLIB_AVAILABLE", False)
        nd = nd_mod.KDC101NDStage()
        with pytest.raises(KDC101Error):
            nd.connect("27123456")


class TestMoveToMm:
    def test_move_to_mm_passes_metres_to_pylablib(self, connected):
        """MTS50-Z8 is natively metres — move_to_mm(25.0) must send 0.025, not 25.0."""
        nd, mock_motor = connected
        mock_motor.get_position.return_value = 0.025
        nd.move_to_mm(25.0, wait=True, timeout=5.0)
        mock_motor.move_to.assert_called_once_with(0.025)

    def test_move_to_mm_clamps_above_travel(self, connected):
        nd, mock_motor = connected
        mock_motor.get_position.return_value = 0.050
        nd.move_to_mm(75.0)
        mock_motor.move_to.assert_called_once_with(0.050)

    def test_move_to_mm_clamps_below_zero(self, connected):
        nd, mock_motor = connected
        mock_motor.get_position.return_value = 0.0
        nd.move_to_mm(-10.0)
        mock_motor.move_to.assert_called_once_with(0.0)

    def test_move_to_mm_wraps_thorlabs_error(self, connected):
        nd, mock_motor = connected
        mock_motor.move_to.side_effect = _FakeThorlabsError("bad position")
        with pytest.raises(KDC101Error):
            nd.move_to_mm(10.0)

    def test_move_to_mm_times_out_when_position_never_stabilises(self, connected):
        nd, mock_motor = connected
        counter = iter(range(10_000))
        mock_motor.get_position.side_effect = lambda: next(counter) * 1e-3
        with pytest.raises(KDC101TimeoutError):
            nd.move_to_mm(10.0, timeout=0.05)

    def test_move_to_mm_raises_when_not_connected(self, fake_thorlabs):
        nd = nd_mod.KDC101NDStage()
        with pytest.raises(KDC101Error):
            nd.move_to_mm(10.0)


class TestGetPositionMm:
    def test_returns_position_converted_from_metres(self, connected):
        nd, mock_motor = connected
        mock_motor.get_position.return_value = 0.0125
        assert nd.get_position_mm() == pytest.approx(12.5)

    def test_wraps_thorlabs_error(self, connected):
        nd, mock_motor = connected
        mock_motor.get_position.side_effect = _FakeThorlabsError("comm error")
        with pytest.raises(KDC101Error):
            nd.get_position_mm()

    def test_raises_when_not_connected(self, fake_thorlabs):
        nd = nd_mod.KDC101NDStage()
        with pytest.raises(KDC101Error):
            nd.get_position_mm()


class TestGetPositionMmNowait:
    def test_returns_position_converted_from_metres(self, connected):
        nd, mock_motor = connected
        mock_motor.get_position.return_value = 0.0125
        assert nd.get_position_mm_nowait() == pytest.approx(12.5)

    def test_returns_none_when_lock_held_by_another_call(self, connected):
        nd, _mock_motor = connected
        assert nd._lock.acquire(blocking=False)
        try:
            assert nd.get_position_mm_nowait() is None
        finally:
            nd._lock.release()


class TestHomeAndStop:
    def test_home_calls_motor_home_with_sync_and_timeout(self, connected):
        nd, mock_motor = connected
        nd.home(wait=True, timeout=42.0)
        mock_motor.home.assert_called_once_with(sync=True, timeout=42.0)

    def test_stop_calls_motor_stop(self, connected):
        nd, mock_motor = connected
        nd.stop()
        mock_motor.stop.assert_called_once_with(immediate=True, sync=False)


class TestListDevices:
    def test_normalises_tuple_entries(self, fake_thorlabs):
        fake_thorlabs.list_kinesis_devices.return_value = [("27123456", "KDC101")]
        result = nd_mod.KDC101NDStage.list_devices()
        assert result == [("27123456", "KDC101")]

    def test_empty_when_pylablib_unavailable(self, monkeypatch):
        monkeypatch.setattr(kdc_base, "_PYLABLIB_AVAILABLE", False)
        assert nd_mod.KDC101NDStage.list_devices() == []
