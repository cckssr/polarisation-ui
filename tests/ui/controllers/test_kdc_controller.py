"""KdcController against the in-memory KDC101 mock."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QObject, QThread, Signal

from polarisation_ui.core.exceptions import KDC101Error
from polarisation_ui.infrastructure.modules import ModuleRegistry
from polarisation_ui.ui.controllers import kdc_controller
from polarisation_ui.ui.controllers.kdc_controller import DISCONNECT_THRESHOLD
from polarisation_ui.ui.controllers.status import LED_ERROR, LED_OFF, LED_OK

CONN_ID = "mock://kdc101"


class FakeZeroFindWorker(QThread):
    """Stands in for KDCZeroFindWorker: the test emits its signals by hand."""

    gain_requested = Signal(int)
    finished = Signal(float)
    failed = Signal(str)
    log = Signal(str)

    def __init__(self, kdc, read_latest, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.aborted = False

    def start(self) -> None:  # type: ignore[override]
        pass

    def abort(self) -> None:
        self.aborted = True


def test_the_device_list_comes_from_the_mock(ctx, record) -> None:
    devices = record(ctx.kdc.devices_changed)
    ctx.kdc.refresh_devices()
    assert devices.last() == ([(CONN_ID, "Mock KDC101 (PRM1-Z8)")],)


def test_connecting_registers_the_module_and_starts_the_position_poll(ctx, record) -> None:
    state = record(ctx.kdc.state_changed)
    controls = record(ctx.kdc.controls_changed)
    modules = record(ctx.kdc.modules_changed)
    connected = record(ctx.kdc.connected_changed)

    assert ctx.kdc.connect_device(CONN_ID)

    assert ctx.kdc.is_connected
    assert ModuleRegistry.get("kdc101") is not None
    assert len(modules) == 1
    assert state.last()[0] == LED_OK
    assert CONN_ID in state.last()[1]
    assert connected.calls == [(True,)]
    assert controls.last() == (True, True, True, True)
    assert ctx.kdc._position_timer.isActive()


def test_connecting_without_a_selection_asks_for_a_notice(ctx, record) -> None:
    notice = record(ctx.kdc.notice)
    assert not ctx.kdc.connect_device(None)
    assert len(notice) == 1
    assert not ctx.kdc.is_connected


def test_a_failing_connect_reports_the_error_and_registers_nothing(ctx, record) -> None:
    def fail(conn_id: str) -> None:
        raise KDC101Error("no such device")

    ctx.kdc.kdc.connect = fail
    state = record(ctx.kdc.state_changed)
    status = record(ctx.status.message)
    assert not ctx.kdc.connect_device(CONN_ID)
    assert state.last()[0] == LED_ERROR
    assert status.last()[0] == "error"
    assert ModuleRegistry.get("kdc101") is None


def test_disconnecting_unregisters_the_module_and_resets_the_controls(ctx, record) -> None:
    ctx.kdc.connect_device(CONN_ID)
    state = record(ctx.kdc.state_changed)
    controls = record(ctx.kdc.controls_changed)
    position = record(ctx.kdc.position_changed)

    ctx.kdc.disconnect_device()

    assert not ctx.kdc.is_connected
    assert ModuleRegistry.get("kdc101") is None
    assert state.last()[0] == LED_OFF
    assert controls.last() == (True, False, False, False)
    assert position.last() == (None,)
    assert not ctx.kdc._position_timer.isActive()


def test_the_position_poll_reports_the_stage_angle(ctx, record) -> None:
    ctx.kdc.connect_device(CONN_ID)
    ctx.kdc.kdc.move_to(42.0)
    position = record(ctx.kdc.position_changed)
    ctx.kdc.poll_position()
    assert position.last() == (42.0,)


def test_repeated_read_failures_count_as_an_unplugged_stage(ctx, record) -> None:
    ctx.kdc.connect_device(CONN_ID)

    def broken() -> float:
        raise KDC101Error("read failed")

    ctx.kdc.kdc.get_position_deg_nowait = broken
    status = record(ctx.status.message)
    connected = record(ctx.kdc.connected_changed)

    for _ in range(DISCONNECT_THRESHOLD - 1):
        ctx.kdc.poll_position()
    assert ctx.kdc.is_connected
    ctx.kdc.poll_position()

    assert not ctx.kdc.is_connected
    assert connected.calls == [(False,)]
    assert status.last()[0] == "error"
    assert ModuleRegistry.get("kdc101") is None


def test_homing_locks_the_connect_and_home_buttons_until_done(qtbot, ctx, record) -> None:
    ctx.kdc.connect_device(CONN_ID)
    controls = record(ctx.kdc.controls_changed)
    ctx.kdc.kdc.move_to(77.0)

    ctx.kdc.home()
    assert controls.calls[0] == (False, False, True, True)
    qtbot.waitUntil(lambda: controls.last() == (True, True, True, True), timeout=3000)
    assert ctx.kdc.kdc.get_position_deg() == 0.0


def test_homing_while_disconnected_does_nothing(ctx, record) -> None:
    controls = record(ctx.kdc.controls_changed)
    ctx.kdc.home()
    assert len(controls) == 0


def test_resetting_the_offset_clears_it_and_persists(ctx, record) -> None:
    ctx.kdc.connect_device(CONN_ID)
    ctx.kdc.set_zero_offset(33.0)
    offset = record(ctx.kdc.offset_changed)
    persist = record(ctx.kdc.persist_requested)

    ctx.kdc.reset_offset()

    assert ctx.kdc.zero_offset_deg == 0.0
    assert offset.last() == (0.0,)
    assert len(persist) == 1


def test_the_zero_find_needs_an_arduino_stream(ctx, record) -> None:
    ctx.kdc.connect_device(CONN_ID)
    status = record(ctx.status.message)
    ctx.kdc.start_zero_find()
    assert status.last()[0] == "error"
    assert not ctx.kdc.zero_find_running


def test_the_zero_find_success_stores_the_offset_and_unlocks_the_controls(
    online, monkeypatch, record
) -> None:
    ctx = online
    monkeypatch.setattr(kdc_controller, "KDCZeroFindWorker", FakeZeroFindWorker)
    ctx.kdc.connect_device(CONN_ID)
    controls = record(ctx.kdc.controls_changed)
    persist = record(ctx.kdc.persist_requested)

    ctx.kdc.start_zero_find()
    worker = ctx.kdc._zero_worker
    assert ctx.kdc.zero_find_running
    assert ctx.detector.gain_auto_suspended
    assert controls.last() == (False, False, False, False)

    worker.gain_requested.emit(3)
    assert ctx.data.pdtia_gain == 3
    worker.finished.emit(12.5)

    assert not ctx.kdc.zero_find_running
    assert not ctx.detector.gain_auto_suspended
    assert ctx.kdc.zero_offset_deg == 12.5
    assert controls.last() == (True, True, True, True)
    assert len(persist) == 1


def test_a_failed_zero_find_restores_the_previous_gain(online, monkeypatch, record) -> None:
    ctx = online
    monkeypatch.setattr(kdc_controller, "KDCZeroFindWorker", FakeZeroFindWorker)
    ctx.kdc.connect_device(CONN_ID)
    assert ctx.detector.apply_gain(2)
    status = record(ctx.status.message)

    ctx.kdc.start_zero_find()
    worker = ctx.kdc._zero_worker
    worker.gain_requested.emit(1)
    assert ctx.data.pdtia_gain == 1
    worker.failed.emit("no minimum")

    assert ctx.data.pdtia_gain == 2
    assert not ctx.kdc.zero_find_running
    assert not ctx.detector.gain_auto_suspended
    assert status.last()[0] == "error"


def test_disconnecting_during_a_zero_find_aborts_the_worker(online, monkeypatch) -> None:
    ctx = online
    monkeypatch.setattr(kdc_controller, "KDCZeroFindWorker", FakeZeroFindWorker)
    ctx.kdc.connect_device(CONN_ID)
    ctx.kdc.start_zero_find()
    worker = ctx.kdc._zero_worker
    ctx.kdc.disconnect_device()
    assert worker.aborted


def test_shutdown_disconnects_and_unregisters(ctx) -> None:
    ctx.kdc.connect_device(CONN_ID)
    ctx.kdc.shutdown()
    assert not ctx.kdc.is_connected
    assert ModuleRegistry.get("kdc101") is None


@pytest.mark.parametrize("offset", [0.0, 15.0])
def test_publishing_the_state_reports_the_offset_and_disabled_actions(ctx, record, offset) -> None:
    ctx.kdc.set_zero_offset(offset)
    controls = record(ctx.kdc.controls_changed)
    shown = record(ctx.kdc.offset_changed)
    ctx.kdc.publish_state()
    assert controls.last() == (True, False, False, False)
    assert shown.last() == (offset,)
