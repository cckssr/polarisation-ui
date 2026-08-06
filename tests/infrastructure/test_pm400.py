"""Mock-based unit tests for PM400PowerMeter.

Patches the module's pymeasure/pyvisa globals (_ThorlabsPM400,
_PYMEASURE_AVAILABLE, _pyvisa, _PYVISA_AVAILABLE) directly so these tests
never touch real hardware or require pymeasure/pyvisa to be installed.
Complements test_pm400_hw.py, which is opt-in and requires a real connected
PM400.
"""

from unittest.mock import MagicMock

import pytest

import polarisation_ui.infrastructure.devices.pm400 as pm400_mod
from polarisation_ui.core.exceptions import PM400Error


@pytest.fixture
def fake_thorlabs_pm400(monkeypatch):
    """Patch _ThorlabsPM400 with a factory returning a fresh MagicMock instrument."""
    fake_class = MagicMock()
    monkeypatch.setattr(pm400_mod, "_ThorlabsPM400", fake_class)
    monkeypatch.setattr(pm400_mod, "_PYMEASURE_AVAILABLE", True)
    return fake_class


@pytest.fixture
def connected(fake_thorlabs_pm400):
    """Return (PM400PowerMeter, mock_inst) already connected to a fake instrument."""
    mock_inst = MagicMock()
    mock_inst.sensor_info = ["S120C", "SN0001", "cal msg", "PHOT"]
    fake_thorlabs_pm400.return_value = mock_inst
    pm = pm400_mod.PM400PowerMeter()
    pm.connect("USB0::0x1313::0x8078::P0000001::INSTR")
    return pm, mock_inst


class TestConnect:
    def test_connect_configures_power_measurement(self, fake_thorlabs_pm400):
        mock_inst = MagicMock()
        mock_inst.sensor_info = ["S120C", "SN0001", "cal msg", "PHOT"]
        fake_thorlabs_pm400.return_value = mock_inst

        pm = pm400_mod.PM400PowerMeter()
        pm.connect("USB0::0x1313::0x8078::P0000001::INSTR")

        fake_thorlabs_pm400.assert_called_once_with("USB0::0x1313::0x8078::P0000001::INSTR")
        assert mock_inst.configure == "POW"
        assert mock_inst.power_unit == "W"
        assert mock_inst.power_autorange is True
        assert pm.is_connected() is True

    def test_connect_raises_when_pymeasure_unavailable(self, monkeypatch):
        monkeypatch.setattr(pm400_mod, "_PYMEASURE_AVAILABLE", False)
        pm = pm400_mod.PM400PowerMeter()
        with pytest.raises(PM400Error):
            pm.connect("USB0::0x1313::0x8078::P0000001::INSTR")

    def test_connect_wraps_construction_error(self, fake_thorlabs_pm400):
        fake_thorlabs_pm400.side_effect = RuntimeError("VISA resource not found")
        pm = pm400_mod.PM400PowerMeter()
        with pytest.raises(PM400Error):
            pm.connect("USB0::0x1313::0x8078::P0000001::INSTR")
        assert pm.is_connected() is False


class TestDisconnect:
    def test_disconnect_shuts_down_and_clears_state(self, connected):
        pm, mock_inst = connected
        pm.disconnect()
        mock_inst.shutdown.assert_called_once()
        assert pm.is_connected() is False

    def test_disconnect_safe_when_not_connected(self, fake_thorlabs_pm400):
        pm = pm400_mod.PM400PowerMeter()
        pm.disconnect()  # must not raise
        assert pm.is_connected() is False

    def test_disconnect_swallows_shutdown_errors(self, connected):
        pm, mock_inst = connected
        mock_inst.shutdown.side_effect = RuntimeError("already gone")
        pm.disconnect()  # must not raise
        assert pm.is_connected() is False


class TestReadPowerW:
    def test_returns_float_power(self, connected):
        pm, mock_inst = connected
        mock_inst.power = 1.234e-6
        assert pm.read_power_W() == pytest.approx(1.234e-6)

    def test_wraps_communication_error(self, connected):
        pm, mock_inst = connected
        type(mock_inst).power = property(
            lambda self: (_ for _ in ()).throw(RuntimeError("comm timeout"))
        )
        with pytest.raises(PM400Error):
            pm.read_power_W()

    def test_raises_when_not_connected(self, fake_thorlabs_pm400):
        pm = pm400_mod.PM400PowerMeter()
        with pytest.raises(PM400Error):
            pm.read_power_W()


class TestWavelength:
    def test_set_wavelength_nm(self, connected):
        pm, mock_inst = connected
        pm.set_wavelength_nm(633.0)
        assert mock_inst.wavelength == 633.0

    def test_get_wavelength_nm(self, connected):
        pm, mock_inst = connected
        mock_inst.wavelength = 780.0
        assert pm.get_wavelength_nm() == 780.0

    def test_set_wavelength_wraps_error(self, connected):
        pm, mock_inst = connected
        type(mock_inst).wavelength = property(
            lambda self: 0.0,
            lambda self, v: (_ for _ in ()).throw(RuntimeError("out of range")),
        )
        with pytest.raises(PM400Error):
            pm.set_wavelength_nm(9999.0)


class TestAttenuation:
    def test_set_attenuation_dB(self, connected):
        pm, mock_inst = connected
        pm.set_attenuation_dB(3.0)
        assert mock_inst.attenuation == 3.0

    def test_get_attenuation_dB(self, connected):
        pm, mock_inst = connected
        mock_inst.attenuation = 4.5
        assert pm.get_attenuation_dB() == 4.5


class TestAveragingAndZero:
    def test_set_averaging(self, connected):
        pm, mock_inst = connected
        pm.set_averaging(100)
        assert mock_inst.averaging_count == 100

    def test_zero_calls_instrument_zero(self, connected):
        pm, mock_inst = connected
        pm.zero()
        mock_inst.zero.assert_called_once()

    def test_zero_wraps_error(self, connected):
        pm, mock_inst = connected
        mock_inst.zero.side_effect = RuntimeError("zero failed")
        with pytest.raises(PM400Error):
            pm.zero()


class TestSensorInfo:
    def test_returns_list_when_connected(self, connected):
        pm, _mock_inst = connected
        assert pm.sensor_info() == ["S120C", "SN0001", "cal msg", "PHOT"]

    def test_returns_empty_list_when_not_connected(self, fake_thorlabs_pm400):
        pm = pm400_mod.PM400PowerMeter()
        assert pm.sensor_info() == []

    def test_returns_empty_list_on_error(self, connected):
        pm, mock_inst = connected
        type(mock_inst).sensor_info = property(
            lambda self: (_ for _ in ()).throw(RuntimeError("comm error"))
        )
        assert pm.sensor_info() == []


class TestListResources:
    def test_filters_to_thorlabs_vid(self, monkeypatch):
        fake_pyvisa = MagicMock()
        fake_rm = MagicMock()
        fake_rm.list_resources.return_value = (
            "USB0::0x1313::0x8078::P0000001::INSTR",
            "USB0::0x0000::0x0000::OTHER::INSTR",
        )
        fake_pyvisa.ResourceManager.return_value = fake_rm
        monkeypatch.setattr(pm400_mod, "_pyvisa", fake_pyvisa)
        monkeypatch.setattr(pm400_mod, "_PYVISA_AVAILABLE", True)

        result = pm400_mod.PM400PowerMeter.list_resources()

        assert result == ["USB0::0x1313::0x8078::P0000001::INSTR"]

    def test_empty_when_pyvisa_unavailable(self, monkeypatch):
        monkeypatch.setattr(pm400_mod, "_PYVISA_AVAILABLE", False)
        assert pm400_mod.PM400PowerMeter.list_resources() == []

    def test_empty_on_unexpected_error(self, monkeypatch):
        fake_pyvisa = MagicMock()
        fake_pyvisa.ResourceManager.side_effect = RuntimeError("no backend")
        monkeypatch.setattr(pm400_mod, "_pyvisa", fake_pyvisa)
        monkeypatch.setattr(pm400_mod, "_PYVISA_AVAILABLE", True)
        assert pm400_mod.PM400PowerMeter.list_resources() == []
