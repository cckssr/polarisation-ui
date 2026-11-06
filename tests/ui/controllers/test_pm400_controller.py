"""PM400Controller against the in-memory PM400 mock."""

from __future__ import annotations

import pytest

from polarisation_ui.core.detector import DETECTOR_PM400
from polarisation_ui.core.exceptions import PM400Error
from polarisation_ui.infrastructure.modules import ModuleRegistry
from polarisation_ui.ui.controllers.status import LED_ERROR, LED_OFF, LED_OK

RESOURCE = "USB0::0x1313::0x8078::MOCK00001::INSTR"


def test_the_resource_list_comes_from_the_mock(ctx, record) -> None:
    resources = record(ctx.pm400.resources_changed)
    ctx.pm400.refresh_resources()
    assert resources.last() == ([RESOURCE],)


def test_connecting_makes_the_pm400_the_active_detector(ctx, record) -> None:
    ctx.pm400.refresh_resources()
    state = record(ctx.pm400.state_changed)
    connected = record(ctx.pm400.connected_changed)
    modules = record(ctx.pm400.modules_changed)
    persist = record(ctx.pm400.persist_requested)

    assert ctx.pm400.connect_resource(RESOURCE)

    assert ctx.pm400.is_connected
    assert ctx.data.is_pm400_active
    assert ModuleRegistry.get("pm400") is not None
    assert state.last()[0] == LED_OK
    assert "S120C" in state.last()[1]
    assert connected.calls == [(True,)]
    assert len(modules) == 1
    assert len(persist) == 1
    assert ctx.pm400.resource == RESOURCE


def test_the_active_detector_signal_follows_the_connection(qtbot, ctx, record) -> None:
    active = record(ctx.detector.active_detector_changed)
    ctx.pm400.connect_resource(RESOURCE)
    qtbot.waitUntil(lambda: any(args == (DETECTOR_PM400,) for args in active.calls), timeout=2000)


def test_connecting_without_a_resource_asks_for_a_notice(ctx, record) -> None:
    notice = record(ctx.pm400.notice)
    assert not ctx.pm400.connect_resource("   ")
    assert len(notice) == 1
    assert not ctx.pm400.is_connected


def test_a_failing_connect_reports_the_error(ctx, record) -> None:
    def fail(resource: str) -> None:
        raise PM400Error("no VISA")

    ctx.pm400.pm400.connect = fail
    state = record(ctx.pm400.state_changed)
    status = record(ctx.status.message)
    assert not ctx.pm400.connect_resource(RESOURCE)
    assert state.last()[0] == LED_ERROR
    assert status.last()[0] == "error"
    assert not ctx.data.is_pm400_active


def test_user_disconnect_falls_back_to_the_pdtia(ctx, record) -> None:
    ctx.pm400.connect_resource(RESOURCE)
    state = record(ctx.pm400.state_changed)
    connected = record(ctx.pm400.connected_changed)

    ctx.pm400.disconnect_device()

    assert not ctx.pm400.is_connected
    assert not ctx.data.is_pm400_active
    assert ModuleRegistry.get("pm400") is None
    assert state.last()[0] == LED_OFF
    assert connected.calls == [(False,)]


def test_a_lost_connection_is_torn_down_like_a_disconnect(ctx, record) -> None:
    ctx.pm400.connect_resource(RESOURCE)
    state = record(ctx.pm400.state_changed)
    status = record(ctx.status.message)

    ctx.data.pm400_connection_lost.emit("timeout")

    assert not ctx.pm400.is_connected
    assert ModuleRegistry.get("pm400") is None
    assert state.last()[0] == LED_OFF
    assert status.last()[0] == "error"
    assert "timeout" in status.last()[1]


def test_zeroing_is_ignored_while_disconnected_and_reported_when_connected(ctx, record) -> None:
    status = record(ctx.status.message)
    ctx.pm400.zero()
    assert len(status) == 0
    ctx.pm400.connect_resource(RESOURCE)
    status.calls.clear()
    ctx.pm400.zero()
    assert status.last()[0] == "info"


def test_a_failing_zero_is_reported_as_an_error(ctx, record) -> None:
    ctx.pm400.connect_resource(RESOURCE)

    def fail() -> None:
        raise PM400Error("zero failed")

    ctx.pm400.pm400.zero = fail
    status = record(ctx.status.message)
    ctx.pm400.zero()
    assert status.last()[0] == "error"


def test_the_wavelength_is_pushed_to_a_connected_meter_and_persisted(ctx, record) -> None:
    ctx.pm400.connect_resource(RESOURCE)
    persist = record(ctx.pm400.persist_requested)
    ctx.pm400.set_wavelength(532.0)
    assert ctx.pm400.pm400.get_wavelength_nm() == 532.0
    assert ctx.pm400.wavelength_nm == 532.0
    assert len(persist) == 1


def test_the_wavelength_is_applied_on_connect(ctx) -> None:
    ctx.pm400.set_wavelength(780.0)
    ctx.pm400.connect_resource(RESOURCE)
    assert ctx.pm400.pm400.get_wavelength_nm() == 780.0


def test_a_failing_wavelength_push_is_reported(ctx, record) -> None:
    ctx.pm400.connect_resource(RESOURCE)

    def fail(nm: float) -> None:
        raise PM400Error("rejected")

    ctx.pm400.pm400.set_wavelength_nm = fail
    status = record(ctx.status.message)
    ctx.pm400.set_wavelength(600.0)
    assert status.last()[0] == "error"


def test_a_remembered_resource_is_only_selected_when_listed(ctx, record) -> None:
    selected = record(ctx.pm400.resource_selected)
    ctx.pm400.refresh_resources()
    ctx.pm400.select_resource("USB0::elsewhere")
    assert len(selected) == 0
    ctx.pm400.select_resource(RESOURCE)
    assert selected.calls == [(RESOURCE,)]


def test_shutdown_releases_the_meter(ctx) -> None:
    ctx.pm400.connect_resource(RESOURCE)
    ctx.data.clear_pm400()
    ctx.pm400.shutdown()
    assert not ctx.pm400.is_connected
    assert ModuleRegistry.get("pm400") is None


@pytest.mark.parametrize("nm", [633.0, 405.0])
def test_publishing_the_state_reports_the_wavelength(ctx, record, nm) -> None:
    ctx.pm400.set_wavelength(nm)
    shown = record(ctx.pm400.wavelength_changed)
    ctx.pm400.publish_state()
    assert shown.last() == (nm,)


def test_the_simulated_meter_reads_power_before_the_stage_is_connected(qtbot, ctx, record) -> None:
    """The mock PM400 follows the polariser angle, which must not need a connected stage."""
    lost = record(ctx.data.pm400_connection_lost)
    ctx.pm400.connect_resource(RESOURCE)
    assert ctx.data.is_pm400_active
    ctx.pm400.pm400.read_power_W()  # does not raise
    qtbot.wait(300)
    assert len(lost) == 0
