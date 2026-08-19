"""Tests for PM400ModuleAdapter — verifies it satisfies the HostModule protocol."""

from polarisation_ui.infrastructure.mocks.mock_pm400 import MockPM400
from polarisation_ui.infrastructure.modules import HostModule, ModuleRegistry
from polarisation_ui.infrastructure.modules.pm400_adapter import PM400ModuleAdapter


def _make_adapter() -> PM400ModuleAdapter:
    pm = MockPM400()
    pm.connect("mock://pm400")
    return PM400ModuleAdapter(pm)


def test_adapter_satisfies_host_module_protocol():
    adapter = _make_adapter()
    assert isinstance(adapter, HostModule)


def test_adapter_id():
    assert PM400ModuleAdapter.id == "pm400"


def test_adapter_is_connected_reflects_pm400():
    pm = MockPM400()
    adapter = PM400ModuleAdapter(pm)
    assert not adapter.is_connected()
    pm.connect("mock://pm400")
    assert adapter.is_connected()


def test_adapter_describe():
    adapter = _make_adapter()
    assert "pm400" in adapter.describe().lower()


def test_adapter_registers_in_module_registry():
    ModuleRegistry.clear()
    adapter = _make_adapter()
    ModuleRegistry.register(adapter)
    retrieved = ModuleRegistry.get("pm400")
    assert retrieved is adapter
    ModuleRegistry.clear()


def test_adapter_forwards_calls_to_wrapped_pm400():
    """Tabs receive the adapter (not the raw PM400PowerMeter) via inject_modules(),
    so read_power_W/set_wavelength_nm/... must be forwarded."""
    adapter = _make_adapter()
    adapter.set_wavelength_nm(532.0)
    assert adapter.get_wavelength_nm() == 532.0
    assert adapter.read_power_W() >= 0.0
