"""
Hardware tests for PM400PowerMeter.

These tests require a real Thorlabs PM400 power meter connected via USB.
Run with::

    pytest tests/test_pm400_hw.py \
        --pm400-visa="USB0::0x1313::0x8078::P0000001::INSTR"

All tests are skipped automatically when --pm400-visa is not provided.

To discover the VISA resource string without running tests::

    python -c "import pyvisa; print(pyvisa.ResourceManager().list_resources())"
"""

import pytest

from polarisation_ui.core.exceptions import PM400Error
from polarisation_ui.infrastructure.devices.pm400 import PM400PowerMeter

# ── Static / no-hardware tests ────────────────────────────────────────────────


def test_list_resources_returns_list() -> None:
    """list_resources() must return a list even without hardware present."""
    resources = PM400PowerMeter.list_resources()
    assert isinstance(resources, list)
    for r in resources:
        assert isinstance(r, str)


def test_connect_invalid_visa_raises() -> None:
    """Connecting to an invalid VISA string must raise PM400Error."""
    pm = PM400PowerMeter()
    with pytest.raises(PM400Error):
        # Non-routable TCP address — will time out or fail immediately
        pm.connect("TCPIP::192.0.2.255::9999::SOCKET")


def test_operations_without_connect_raise() -> None:
    """Calling measurement methods on a disconnected instance must raise PM400Error."""
    pm = PM400PowerMeter()
    with pytest.raises(PM400Error):
        pm.read_power_W()
    with pytest.raises(PM400Error):
        pm.set_wavelength_nm(633.0)
    with pytest.raises(PM400Error):
        pm.get_wavelength_nm()


# ── Hardware tests (skip without --pm400-visa) ────────────────────────────────


def test_connect_and_disconnect(connected_pm400: PM400PowerMeter) -> None:
    """Fixture verifies connect; test verifies is_connected() state."""
    assert connected_pm400.is_connected()


def test_is_connected_after_disconnect(pm400_visa: str | None) -> None:
    """is_connected() returns False after explicit disconnect."""
    if pm400_visa is None:
        pytest.skip("--pm400-visa not provided")
    pm = PM400PowerMeter()
    pm.connect(pm400_visa)
    assert pm.is_connected()
    pm.disconnect()
    assert not pm.is_connected()


def test_sensor_info_is_nonempty(connected_pm400: PM400PowerMeter) -> None:
    """sensor_info() must return a non-empty list with at least a model name."""
    info = connected_pm400.sensor_info()
    assert isinstance(info, list)
    assert len(info) > 0, "sensor_info() returned an empty list"


def test_read_power_is_non_negative(connected_pm400: PM400PowerMeter) -> None:
    """Optical power reading must be a non-negative float."""
    power = connected_pm400.read_power_W()
    assert isinstance(power, float)
    assert power >= 0.0, f"Power reading is negative: {power}"


def test_wavelength_roundtrip(connected_pm400: PM400PowerMeter) -> None:
    """Setting and reading back wavelength must agree within 1 nm."""
    for wl in (532.0, 633.0, 780.0):
        connected_pm400.set_wavelength_nm(wl)
        got = connected_pm400.get_wavelength_nm()
        assert abs(got - wl) < 1.0, f"Wavelength roundtrip failed: set {wl}, got {got}"


def test_attenuation_roundtrip(connected_pm400: PM400PowerMeter) -> None:
    """Setting and reading back attenuation must agree within 0.1 dB."""
    for db in (0.0, 3.01, 6.0):
        connected_pm400.set_attenuation_dB(db)
        got = connected_pm400.get_attenuation_dB()
        assert abs(got - db) < 0.1, (
            f"Attenuation roundtrip failed: set {db} dB, got {got} dB"
        )
    # Restore to 0 dB so the instrument is in a known state after the test
    connected_pm400.set_attenuation_dB(0.0)


def test_averaging_accepted(connected_pm400: PM400PowerMeter) -> None:
    """set_averaging() must not raise for reasonable values."""
    for n in (1, 10, 100):
        connected_pm400.set_averaging(n)  # must not raise


def test_multiple_power_readings_are_consistent(
    connected_pm400: PM400PowerMeter,
) -> None:
    """Ten consecutive readings must agree within 20 % of their mean (stable beam assumed)."""
    readings = [connected_pm400.read_power_W() for _ in range(10)]
    mean = sum(readings) / len(readings)
    if mean < 1e-12:
        pytest.skip("Power too low for consistency check (beam blocked or very dark)")
    for r in readings:
        assert abs(r - mean) / mean < 0.20, (
            f"Reading {r:.3e} W deviates >20 % from mean {mean:.3e} W"
        )


def test_zero_does_not_raise(connected_pm400: PM400PowerMeter) -> None:
    """zero() must not raise (dark-current zeroing routine)."""
    connected_pm400.zero()
