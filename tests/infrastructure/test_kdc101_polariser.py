"""Mock-based unit tests for KDC101Polariser.

Patches the module's lazily-imported pylablib globals (_Thorlabs,
_ThorlabsError, _ThorlabsTimeoutError, _PYLABLIB_AVAILABLE) directly so these
tests never touch real hardware or require pylablib/a Kinesis backend to be
installed. Complements test_kdc101_polariser_hw.py, which is opt-in and
requires a real connected stage.
"""

from unittest.mock import MagicMock

import pytest

import polarisation_ui.infrastructure.devices.kdc101_polariser as kdc_mod
from polarisation_ui.core.exceptions import KDC101Error, KDC101TimeoutError


class _FakeThorlabsError(Exception):
    pass


class _FakeThorlabsTimeoutError(_FakeThorlabsError):
    pass


@pytest.fixture
def fake_thorlabs(monkeypatch):
    """Patch the module's cached pylablib globals with fakes; returns the fake module."""
    fake_module = MagicMock()
    monkeypatch.setattr(kdc_mod, "_Thorlabs", fake_module)
    monkeypatch.setattr(kdc_mod, "_ThorlabsError", _FakeThorlabsError)
    monkeypatch.setattr(kdc_mod, "_ThorlabsTimeoutError", _FakeThorlabsTimeoutError)
    monkeypatch.setattr(kdc_mod, "_PYLABLIB_AVAILABLE", True)
    return fake_module


@pytest.fixture
def connected(fake_thorlabs):
    """Return (KDC101Polariser, mock_motor) already connected to a fake KinesisMotor."""
    mock_motor = MagicMock()
    fake_thorlabs.KinesisMotor.return_value = mock_motor
    kdc = kdc_mod.KDC101Polariser()
    kdc.connect("mock-conn-id")
    return kdc, mock_motor


class TestConnect:
    def test_connect_opens_motor_with_prm1z8_scale(self, fake_thorlabs):
        mock_motor = MagicMock()
        fake_thorlabs.KinesisMotor.return_value = mock_motor
        kdc = kdc_mod.KDC101Polariser()

        kdc.connect("27266999")

        fake_thorlabs.KinesisMotor.assert_called_once_with("27266999", scale=kdc_mod._PRM1_Z8_SCALE)
        mock_motor.open.assert_called_once()
        assert kdc.is_connected() is True

    def test_connect_raises_kdc101error_when_pylablib_unavailable(self, monkeypatch):
        monkeypatch.setattr(kdc_mod, "_PYLABLIB_AVAILABLE", False)
        kdc = kdc_mod.KDC101Polariser()
        with pytest.raises(KDC101Error):
            kdc.connect("27266999")

    def test_connect_wraps_thorlabs_error(self, fake_thorlabs):
        fake_thorlabs.KinesisMotor.side_effect = _FakeThorlabsError("no device")
        kdc = kdc_mod.KDC101Polariser()
        with pytest.raises(KDC101Error):
            kdc.connect("27266999")
        assert kdc.is_connected() is False

    def test_connect_wraps_unexpected_error(self, fake_thorlabs):
        fake_thorlabs.KinesisMotor.side_effect = RuntimeError("backend missing")
        kdc = kdc_mod.KDC101Polariser()
        with pytest.raises(KDC101Error):
            kdc.connect("27266999")


class TestDisconnect:
    def test_disconnect_closes_motor_and_clears_state(self, connected):
        kdc, mock_motor = connected
        kdc.disconnect()
        mock_motor.close.assert_called_once()
        assert kdc.is_connected() is False

    def test_disconnect_safe_when_not_connected(self, fake_thorlabs):
        kdc = kdc_mod.KDC101Polariser()
        kdc.disconnect()  # must not raise
        assert kdc.is_connected() is False

    def test_disconnect_swallows_close_errors(self, connected):
        kdc, mock_motor = connected
        mock_motor.close.side_effect = RuntimeError("already gone")
        kdc.disconnect()  # must not raise
        assert kdc.is_connected() is False


class TestHome:
    def test_home_calls_motor_home_with_sync_and_timeout(self, connected):
        kdc, mock_motor = connected
        kdc.home(wait=True, timeout=42.0)
        mock_motor.home.assert_called_once_with(sync=True, timeout=42.0)

    def test_home_without_wait_passes_no_timeout(self, connected):
        kdc, mock_motor = connected
        kdc.home(wait=False)
        mock_motor.home.assert_called_once_with(sync=False, timeout=None)

    def test_home_wraps_timeout_error(self, connected):
        kdc, mock_motor = connected
        mock_motor.home.side_effect = _FakeThorlabsTimeoutError("timed out")
        with pytest.raises(KDC101TimeoutError):
            kdc.home()

    def test_home_wraps_thorlabs_error(self, connected):
        kdc, mock_motor = connected
        mock_motor.home.side_effect = _FakeThorlabsError("motor fault")
        with pytest.raises(KDC101Error):
            kdc.home()

    def test_home_raises_when_not_connected(self, fake_thorlabs):
        kdc = kdc_mod.KDC101Polariser()
        with pytest.raises(KDC101Error):
            kdc.home()


class TestMoveTo:
    def test_move_to_calls_motor_move_and_wait(self, connected):
        kdc, mock_motor = connected
        kdc.move_to(45.0, wait=True, timeout=10.0)
        mock_motor.move_to.assert_called_once_with(45.0)
        mock_motor.wait_move.assert_called_once_with(timeout=10.0)

    def test_move_to_without_wait_skips_wait_move(self, connected):
        kdc, mock_motor = connected
        kdc.move_to(45.0, wait=False)
        mock_motor.move_to.assert_called_once_with(45.0)
        mock_motor.wait_move.assert_not_called()

    def test_move_to_wraps_timeout_error(self, connected):
        kdc, mock_motor = connected
        mock_motor.wait_move.side_effect = _FakeThorlabsTimeoutError("stuck")
        with pytest.raises(KDC101TimeoutError):
            kdc.move_to(45.0)

    def test_move_to_wraps_thorlabs_error(self, connected):
        kdc, mock_motor = connected
        mock_motor.move_to.side_effect = _FakeThorlabsError("bad position")
        with pytest.raises(KDC101Error):
            kdc.move_to(45.0)

    def test_move_to_raises_when_not_connected(self, fake_thorlabs):
        kdc = kdc_mod.KDC101Polariser()
        with pytest.raises(KDC101Error):
            kdc.move_to(45.0)


class TestGetPositionDeg:
    def test_returns_float_position(self, connected):
        kdc, mock_motor = connected
        mock_motor.get_position.return_value = 12.5
        assert kdc.get_position_deg() == 12.5

    def test_wraps_thorlabs_error(self, connected):
        kdc, mock_motor = connected
        mock_motor.get_position.side_effect = _FakeThorlabsError("comm error")
        with pytest.raises(KDC101Error):
            kdc.get_position_deg()

    def test_raises_when_not_connected(self, fake_thorlabs):
        kdc = kdc_mod.KDC101Polariser()
        with pytest.raises(KDC101Error):
            kdc.get_position_deg()


class TestEnable:
    def test_enable_true_calls_enable_channel(self, connected):
        kdc, mock_motor = connected
        kdc.enable(True)
        mock_motor.enable_channel.assert_called_once()
        mock_motor.disable_channel.assert_not_called()

    def test_enable_false_calls_disable_channel(self, connected):
        kdc, mock_motor = connected
        kdc.enable(False)
        mock_motor.disable_channel.assert_called_once()
        mock_motor.enable_channel.assert_not_called()

    def test_enable_wraps_thorlabs_error(self, connected):
        kdc, mock_motor = connected
        mock_motor.enable_channel.side_effect = _FakeThorlabsError("fault")
        with pytest.raises(KDC101Error):
            kdc.enable(True)

    def test_enable_raises_when_not_connected(self, fake_thorlabs):
        kdc = kdc_mod.KDC101Polariser()
        with pytest.raises(KDC101Error):
            kdc.enable(True)


class TestListDevices:
    def test_normalises_tuple_entries(self, fake_thorlabs):
        fake_thorlabs.list_kinesis_devices.return_value = [("27266999", "KDC101")]
        result = kdc_mod.KDC101Polariser.list_devices()
        assert result == [("27266999", "KDC101")]

    def test_normalises_bare_string_entries(self, fake_thorlabs):
        fake_thorlabs.list_kinesis_devices.return_value = ["/dev/cu.usbserial-1"]
        result = kdc_mod.KDC101Polariser.list_devices()
        assert result == [("/dev/cu.usbserial-1", "/dev/cu.usbserial-1")]

    def test_empty_when_no_devices(self, fake_thorlabs):
        fake_thorlabs.list_kinesis_devices.return_value = []
        assert kdc_mod.KDC101Polariser.list_devices() == []

    def test_empty_when_pylablib_unavailable(self, monkeypatch):
        monkeypatch.setattr(kdc_mod, "_PYLABLIB_AVAILABLE", False)
        assert kdc_mod.KDC101Polariser.list_devices() == []

    def test_empty_on_unexpected_error(self, fake_thorlabs):
        fake_thorlabs.list_kinesis_devices.side_effect = RuntimeError("usb error")
        assert kdc_mod.KDC101Polariser.list_devices() == []
