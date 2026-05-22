"""
Hardware tests for KDC101Polariser.

These tests require a real Thorlabs KDC101 controller with a PRM1-Z8
rotation stage attached.  Run with::

    pytest tests/test_kdc101_polariser_hw.py --kdc101-port=27266999

All tests are skipped automatically when --kdc101-port is not provided.

WARNING: the stage will physically move during these tests.  Make sure the
beam path is clear and the motor is free to rotate.
"""

import pytest

from polarisation_ui.core.exceptions import KDC101Error
from polarisation_ui.infrastructure.devices.kdc101_polariser import KDC101Polariser

# Tolerance used when checking reported vs. commanded position (degrees).
_POS_TOL_DEG = 0.5


# ── Static / no-hardware tests ────────────────────────────────────────────────


def test_list_devices_returns_list() -> None:
    """list_devices() must return a list even without hardware present."""
    devices = KDC101Polariser.list_devices()
    assert isinstance(devices, list)
    for conn_id, desc in devices:
        assert isinstance(conn_id, str)
        assert isinstance(desc, str)


def test_connect_invalid_port_raises() -> None:
    """Connecting to a non-existent port must raise KDC101Error, not a raw exception."""
    kdc = KDC101Polariser()
    with pytest.raises(KDC101Error):
        kdc.connect("INVALID_PORT_DOES_NOT_EXIST_99999")


def test_operations_without_connect_raise() -> None:
    """Calling motion methods on a disconnected instance must raise KDC101Error."""
    kdc = KDC101Polariser()
    with pytest.raises(KDC101Error):
        kdc.get_position_deg()
    with pytest.raises(KDC101Error):
        kdc.move_to(0.0)
    with pytest.raises(KDC101Error):
        kdc.home()


# ── Hardware tests (skip without --kdc101-port) ───────────────────────────────


def test_connect_and_disconnect(connected_kdc: KDC101Polariser) -> None:
    """Fixture verifies connect; test verifies is_connected() reflects true state."""
    assert connected_kdc.is_connected()
    # disconnect happens in fixture teardown — just check state here


def test_is_connected_after_disconnect(kdc101_port: str | None) -> None:
    """is_connected() returns False after explicit disconnect."""
    if kdc101_port is None:
        pytest.skip("--kdc101-port not provided")
    kdc = KDC101Polariser()
    kdc.connect(kdc101_port)
    assert kdc.is_connected()
    kdc.disconnect()
    assert not kdc.is_connected()


def test_home(connected_kdc: KDC101Polariser) -> None:
    """Homing must complete without error and leave position near 0°."""
    connected_kdc.home(wait=True, timeout=120.0)
    pos = connected_kdc.get_position_deg()
    assert (
        abs(pos) < _POS_TOL_DEG
    ), f"Position after home should be near 0°, got {pos:.3f}°"


def test_move_to_45(connected_kdc: KDC101Polariser) -> None:
    """Stage must reach 45° within tolerance after move_to(45)."""
    connected_kdc.home()
    connected_kdc.move_to(45.0)
    pos = connected_kdc.get_position_deg()
    assert abs(pos - 45.0) < _POS_TOL_DEG, f"Expected ~45°, got {pos:.3f}°"


def test_move_to_90(connected_kdc: KDC101Polariser) -> None:
    """Stage must reach 90° within tolerance after move_to(90)."""
    connected_kdc.home()
    connected_kdc.move_to(90.0)
    pos = connected_kdc.get_position_deg()
    assert abs(pos - 90.0) < _POS_TOL_DEG, f"Expected ~90°, got {pos:.3f}°"


def test_move_sequence(connected_kdc: KDC101Polariser) -> None:
    """Multiple sequential moves must all land within tolerance."""
    targets = [0.0, 30.0, 60.0, 90.0, 45.0, 0.0]
    connected_kdc.home()
    for target in targets:
        connected_kdc.move_to(target)
        pos = connected_kdc.get_position_deg()
        assert abs(pos - target) < _POS_TOL_DEG, f"Expected ~{target}°, got {pos:.3f}°"


def test_enable_disable(connected_kdc: KDC101Polariser) -> None:
    """enable()/disable() must not raise."""
    connected_kdc.enable(True)
    connected_kdc.enable(False)
    connected_kdc.enable(True)  # leave enabled


def test_get_position_after_home(connected_kdc: KDC101Polariser) -> None:
    """get_position_deg() must return a float after homing."""
    connected_kdc.home()
    pos = connected_kdc.get_position_deg()
    assert isinstance(pos, float)
    assert -5.0 <= pos <= 5.0, f"Home position out of expected range: {pos:.3f}°"
