"""
Tests for polarisation_ui.infrastructure.modules (ModuleRegistry + HostModule protocol).

Verifies:
- register / unregister / get / all / clear work correctly.
- Missing-module lookup returns None.
- Kdc101Stub satisfies the HostModule protocol.
- Stub describe() returns a non-empty string.
- Registry is isolated between tests via clear().
"""

import pytest

from polarisation_ui.infrastructure.modules import HostModule, ModuleRegistry
from polarisation_ui.infrastructure.modules.kdc101_stub import Kdc101Stub


@pytest.fixture(autouse=True)
def _clear_registry() -> None:
    """Ensure a clean registry before and after each test."""
    ModuleRegistry.clear()
    yield
    ModuleRegistry.clear()


# ── protocol conformance ───────────────────────────────────────────────────────


def test_kdc101_stub_satisfies_host_module_protocol() -> None:
    """isinstance check via @runtime_checkable passes for Kdc101Stub."""
    stub = Kdc101Stub()
    assert isinstance(stub, HostModule)


def test_kdc101_stub_id() -> None:
    assert Kdc101Stub().id == "kdc101"


def test_kdc101_stub_connect_returns_true() -> None:
    assert Kdc101Stub().connect() is True


def test_kdc101_stub_is_connected_returns_true() -> None:
    assert Kdc101Stub().is_connected() is True


def test_kdc101_stub_describe_is_nonempty() -> None:
    desc = Kdc101Stub().describe()
    assert isinstance(desc, str) and len(desc) > 0


def test_kdc101_stub_disconnect_does_not_raise() -> None:
    Kdc101Stub().disconnect()  # must not raise


# ── ModuleRegistry CRUD ───────────────────────────────────────────────────────


def test_register_and_get() -> None:
    stub = Kdc101Stub()
    ModuleRegistry.register(stub)
    result = ModuleRegistry.get("kdc101")
    assert result is stub


def test_get_missing_returns_none() -> None:
    assert ModuleRegistry.get("nonexistent") is None


def test_all_returns_shallow_copy() -> None:
    stub = Kdc101Stub()
    ModuleRegistry.register(stub)
    snapshot = ModuleRegistry.all()
    assert "kdc101" in snapshot
    # Modifying the copy must not affect the registry
    del snapshot["kdc101"]
    assert ModuleRegistry.get("kdc101") is stub


def test_unregister_removes_module() -> None:
    ModuleRegistry.register(Kdc101Stub())
    ModuleRegistry.unregister("kdc101")
    assert ModuleRegistry.get("kdc101") is None


def test_unregister_nonexistent_is_noop() -> None:
    ModuleRegistry.unregister("does_not_exist")  # must not raise


def test_register_overwrites_previous_entry() -> None:
    first = Kdc101Stub()
    second = Kdc101Stub()
    ModuleRegistry.register(first)
    ModuleRegistry.register(second)
    assert ModuleRegistry.get("kdc101") is second


def test_clear_removes_all_modules() -> None:
    ModuleRegistry.register(Kdc101Stub())
    ModuleRegistry.clear()
    assert ModuleRegistry.all() == {}


# ── custom stub to test multi-module registry ─────────────────────────────────


class _FakeModule:
    """Minimal stub satisfying HostModule for multi-module tests."""

    def __init__(self, module_id: str) -> None:
        self._id = module_id

    @property
    def id(self) -> str:
        return self._id

    def connect(self) -> bool:
        return True

    def disconnect(self) -> None:
        pass

    def is_connected(self) -> bool:
        return True

    def describe(self) -> str:
        return f"fake module {self._id}"


def test_multiple_modules_coexist() -> None:
    m1 = _FakeModule("foo")
    m2 = _FakeModule("bar")
    ModuleRegistry.register(m1)
    ModuleRegistry.register(m2)
    assert ModuleRegistry.get("foo") is m1
    assert ModuleRegistry.get("bar") is m2
    assert len(ModuleRegistry.all()) == 2


def test_fake_module_satisfies_protocol() -> None:
    assert isinstance(_FakeModule("test"), HostModule)
