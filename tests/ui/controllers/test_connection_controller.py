"""ConnectionController against the simulated Arduino (PTY mock)."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from polarisation_ui.ui.controllers.status import (
    LED_ERROR,
    LED_OFF,
    LED_OK,
    LED_WARN,
    ROW_ARDUINO,
    ROW_DETECTOR,
    ROW_DETECTOR_STAGE,
    ROW_SAMPLE,
)

pytestmark = pytest.mark.skipif(sys.platform == "win32", reason="PTY not available on Windows")


def _rows(recorder) -> dict[str, tuple[str, str]]:
    """Last (led, text) per row."""
    return {row: (led, text) for row, led, text in recorder.calls}


def test_the_simulated_port_is_the_only_port_offered(ctx, port, record) -> None:
    ports = record(ctx.connection.ports_changed)
    ctx.connection.refresh_ports()
    assert ports.last() == ([port],)


def test_connecting_brings_the_link_up_and_frames_arrive(qtbot, ctx, port, record) -> None:
    rows = record(ctx.connection.row_state_changed)
    changed = record(ctx.connection.connected_changed)
    ready = record(ctx.connection.ready)
    links = record(ctx.connection.link_state_changed)
    status = record(ctx.status.message)

    assert ctx.connection.connect_port(port)
    last = _rows(rows)  # before the first frame can flag saturation
    qtbot.waitSignal(ctx.data.frame_ready, timeout=5000).wait()

    assert ctx.connection.is_connected
    assert changed.calls == [(True,)]
    assert len(ready) == 1
    assert links.calls == [("connected",)]
    assert last[ROW_ARDUINO][0] == LED_OK
    assert last[ROW_SAMPLE][0] == LED_OK
    assert last[ROW_DETECTOR_STAGE][0] == LED_OK
    assert last[ROW_DETECTOR][0] == LED_OK
    assert status.last()[0] == "success"
    assert ctx.data.is_reading()


def test_connecting_to_a_dead_port_reports_an_error(ctx, record) -> None:
    rows = record(ctx.connection.row_state_changed)
    connecting = record(ctx.connection.connecting_changed)
    status = record(ctx.status.message)

    assert not ctx.connection.connect_port("/dev/does-not-exist")

    assert not ctx.connection.is_connected
    assert _rows(rows)[ROW_ARDUINO][0] == LED_ERROR
    assert connecting.calls == [(True,), (False,)]
    assert status.last()[0] == "error"


def test_the_ports_missing_placeholder_is_not_connected(ctx, record) -> None:
    rows = record(ctx.connection.row_state_changed)
    placeholder = ctx.connection.ports_missing_text
    assert not ctx.connection.connect_port(placeholder)
    assert not ctx.connection.connect_port("")
    assert _rows(rows)[ROW_ARDUINO][0] == LED_OFF


def test_disconnecting_resets_all_rows_and_tells_the_tabs(online, record) -> None:
    ctx = online
    rows = record(ctx.connection.row_state_changed)
    changed = record(ctx.connection.connected_changed)
    links = record(ctx.connection.link_state_changed)

    ctx.connection.disconnect_port()

    assert not ctx.connection.is_connected
    assert not ctx.data.is_reading()
    assert changed.calls == [(False,)]
    assert links.calls == [("lost",)]
    last = _rows(rows)
    assert last[ROW_ARDUINO][0] == LED_OFF
    assert {last[ROW_SAMPLE][0], last[ROW_DETECTOR_STAGE][0], last[ROW_DETECTOR][0]} == {LED_ERROR}


def test_adc_saturation_flips_the_detector_row_once_per_change(online, record) -> None:
    ctx = online
    ctx.data.intensity_updated.emit(1.0)  # the simulated first frame may already be saturated
    rows = record(ctx.connection.row_state_changed)

    ctx.data.intensity_updated.emit(2.4)
    ctx.data.intensity_updated.emit(2.4)
    assert len(rows) == 1
    assert rows.last()[:2] == (ROW_DETECTOR, LED_WARN)

    ctx.data.intensity_updated.emit(1.0)
    assert rows.last()[:2] == (ROW_DETECTOR, LED_OK)
    assert len(rows) == 2

    ctx.data.intensity_updated.emit(float("nan"))
    assert len(rows) == 2


def test_the_poll_rate_is_shown_only_while_connected_and_unsaturated(
    ctx, port, qtbot, record
) -> None:
    rows = record(ctx.connection.row_state_changed)
    ctx.data.poll_rate_updated.emit(9.5)
    assert len(rows) == 0  # not connected yet

    with qtbot.waitSignal(ctx.data.frame_ready, timeout=5000):
        ctx.connection.connect_port(port)
    rows.calls.clear()
    ctx.data.intensity_updated.emit(1.0)
    ctx.data.poll_rate_updated.emit(9.5)
    assert rows.last()[1] == LED_OK
    assert "9.5" in rows.last()[2]

    ctx.data.intensity_updated.emit(2.4)
    rows.calls.clear()
    ctx.data.poll_rate_updated.emit(9.5)
    assert len(rows) == 0


def test_a_sensor_fault_warns_and_recovery_flushes_the_averaging_buffer(online, record) -> None:
    ctx = online
    rows = record(ctx.connection.row_state_changed)
    status = record(ctx.status.message)
    ctx.data.clear_sample_buffer = MagicMock()
    ctx.data.clear_det_buffer = MagicMock()

    ctx.data.diagnostics_updated.emit(False, "Enc A: fault", True, "Enc B: OK")
    assert _rows(rows)[ROW_SAMPLE][0] == LED_WARN
    assert status.last()[0] == "warning"
    assert "Enc A: fault" in status.last()[1]

    ctx.data.diagnostics_updated.emit(True, "Enc A: OK", True, "Enc B: OK")
    assert _rows(rows)[ROW_SAMPLE][0] == LED_OK
    ctx.data.clear_sample_buffer.assert_called_once()
    ctx.data.clear_det_buffer.assert_not_called()


def test_both_sensors_recovering_is_reported_as_success(online, record) -> None:
    ctx = online
    ctx.data.diagnostics_updated.emit(False, "a", False, "b")
    status = record(ctx.status.message)
    ctx.data.diagnostics_updated.emit(True, "a", True, "b")
    assert status.last()[0] == "success"


def test_a_read_error_marks_the_three_sensor_rows(online, record) -> None:
    ctx = online
    rows = record(ctx.connection.row_state_changed)
    status = record(ctx.status.message)
    ctx.data.error_occurred.emit("boom")
    last = _rows(rows)
    assert {last[ROW_SAMPLE][0], last[ROW_DETECTOR_STAGE][0], last[ROW_DETECTOR][0]} == {LED_WARN}
    assert status.last()[0] == "error"
    assert "boom" in status.last()[1]


def test_the_link_dropping_triggers_reconnect_states_then_permanent_loss(
    qtbot, online, record
) -> None:
    """kill_pty() tears the port down mid-stream (CLAUDE.md disconnection-path test)."""
    ctx = online
    links = record(ctx.connection.link_state_changed)
    lost = record(ctx.connection.lost)
    changed = record(ctx.connection.connected_changed)
    status = record(ctx.status.message)

    ctx.simulation.arduino.kill_pty()

    qtbot.waitUntil(lambda: len(lost) == 1, timeout=10000)
    states = [args[0] for args in links.calls]
    assert states[0] == "reconnecting"
    assert states[-1] == "lost"
    assert changed.last() == (False,)
    assert not ctx.connection.is_connected
    assert "warning" in [level for level, _ in status.calls]
    assert status.calls[-1][0] == "error"


def test_zeroing_the_sample_encoder_reports_success(online, record) -> None:
    ctx = online
    status = record(ctx.status.message)
    assert ctx.connection.zero_sample()
    assert status.last()[0] == "success"


def test_a_failed_zeroing_reports_an_error_and_asks_for_a_dialog(online, record) -> None:
    ctx = online
    ctx.connection.device_manager.zero_sample_encoder = MagicMock(return_value=False)
    failed = record(ctx.connection.zero_failed)
    status = record(ctx.status.message)
    assert not ctx.connection.zero_sample()
    assert len(failed) == 1
    assert status.last()[0] == "error"


def test_zeroing_the_detector_at_180_sets_the_host_offset_and_persists(online, record) -> None:
    ctx = online
    persist = record(ctx.connection.persist_requested)
    assert ctx.connection.zero_detector_at_180()
    assert ctx.data.detector_offset_deg == 180.0
    assert len(persist) == 1
    assert ctx.connection.zero_detector()
    assert ctx.data.detector_offset_deg == 0.0


def test_stream_sources_are_only_configured_while_connected(ctx, port, qtbot) -> None:
    assert not ctx.connection.set_stream_sources({"ENC:BOTH", "ADC"})
    with qtbot.waitSignal(ctx.data.frame_ready, timeout=5000):
        ctx.connection.connect_port(port)
    assert ctx.connection.set_stream_sources({"ENC:BOTH", "ADC"})
