"""Tests for KDC101ModuleAdapter — verifies it satisfies the HostModule protocol."""

from polarisation_ui.infrastructure.mocks.mock_kdc101_polariser import (
    MockKDC101Polariser,
)
from polarisation_ui.infrastructure.modules import HostModule, ModuleRegistry
from polarisation_ui.infrastructure.modules.kdc101_adapter import KDC101ModuleAdapter


def _make_adapter() -> KDC101ModuleAdapter:
    kdc = MockKDC101Polariser()
    kdc.connect("mock://kdc101")
    return KDC101ModuleAdapter(kdc)


def test_adapter_satisfies_host_module_protocol():
    adapter = _make_adapter()
    assert isinstance(adapter, HostModule)


def test_adapter_id():
    assert KDC101ModuleAdapter.id == "kdc101"


def test_adapter_is_connected_reflects_kdc():
    kdc = MockKDC101Polariser()
    adapter = KDC101ModuleAdapter(kdc)
    assert not adapter.is_connected()
    kdc.connect("mock://kdc101")
    assert adapter.is_connected()


def test_adapter_describe():
    adapter = _make_adapter()
    assert "kdc101" in adapter.describe().lower() or "connected" in adapter.describe().lower()


def test_adapter_registers_in_module_registry():
    ModuleRegistry.clear()
    adapter = _make_adapter()
    ModuleRegistry.register(adapter)
    retrieved = ModuleRegistry.get("kdc101")
    assert retrieved is adapter
    ModuleRegistry.clear()
