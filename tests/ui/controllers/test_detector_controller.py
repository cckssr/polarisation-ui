"""DetectorController: gain (manual + auto), profiles, PD-TIA id, dark tare."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from polarisation_ui.core.power_calibration import GainCalibration, PowerCalibrationProfile
from polarisation_ui.infrastructure.config import AppConfig, load_config
from polarisation_ui.ui.controllers.detector_controller import DARK_TARE_SAMPLES
from tests.ui.conftest import FAST_SIM

LIMITS = {
    "pdtia": {
        "device_ids": ["E1", "E2"],
        "gain_auto_switch_power_W": {
            "1": {"min": 1e-4, "max": 1.0},
            "2": {"min": 1e-5, "max": 1e-3},
            "3": {"min": 0.0, "max": 1e-4},
        },
    }
}


@pytest.fixture
def config() -> AppConfig:
    return load_config(overrides={**FAST_SIM, **LIMITS})


def _profile(path: Path, name: str, wavelength: float | None = None) -> Path:
    profile = PowerCalibrationProfile(name=name, wavelength_nm=wavelength)
    profile.gains[1] = GainCalibration(gain_stage=1, points=[(1.0, 1e-3), (2.0, 2e-3)])
    profile.save(path / f"{name}.json")
    return path / f"{name}.json"


# ---- gain -------------------------------------------------------------------------------------


def test_a_manual_gain_click_sets_the_stage_and_persists(online, record) -> None:
    ctx = online
    changed = record(ctx.detector.gain_changed)
    persist = record(ctx.detector.persist_requested)
    status = record(ctx.status.message)

    ctx.detector.select_gain(3)

    assert ctx.data.pdtia_gain == 3
    assert changed.calls == [(3,)]
    assert len(persist) == 1
    assert status.last()[0] == "info"


def test_a_failed_gain_change_clears_the_buttons_and_reports(online, record) -> None:
    ctx = online
    ctx.data.set_pdtia_gain = MagicMock(return_value=False)
    cleared = record(ctx.detector.gain_cleared)
    status = record(ctx.status.message)

    ctx.detector.select_gain(2)

    assert len(cleared) == 1
    assert status.last()[0] == "error"


def test_the_arduino_connect_applies_a_gain_so_one_is_always_active(online) -> None:
    assert 1 <= online.data.pdtia_gain <= 4


def test_a_pending_session_gain_wins_over_the_firmware_gain_on_connect(ctx, port, qtbot) -> None:
    ctx.detector.set_pending_gain(3)
    with qtbot.waitSignal(ctx.data.frame_ready, timeout=5000):
        ctx.connection.connect_port(port)
    assert ctx.data.pdtia_gain == 3


def test_auto_gain_follows_the_configured_power_windows(online, record) -> None:
    ctx = online
    ctx.detector.select_gain(1)
    ctx.detector.set_gain_auto(True)
    assert ctx.detector.gain_auto_enabled

    ctx.data.power_updated.emit(5e-5)  # only gain 2 and 3 cover this; the lowest wins
    assert ctx.data.pdtia_gain == 2
    ctx.data.power_updated.emit(2e-3)  # above gain 2: gain 1 is nearest-covering
    assert ctx.data.pdtia_gain == 1
    ctx.data.power_updated.emit(2e-5)
    assert ctx.data.pdtia_gain == 2
    ctx.data.power_updated.emit(1e-9)
    assert ctx.data.pdtia_gain == 3


def test_auto_gain_keeps_the_stage_while_its_window_still_covers_the_power(online) -> None:
    ctx = online
    ctx.detector.select_gain(2)
    ctx.detector.set_gain_auto(True)
    ctx.data.power_updated.emit(2e-4)  # in the overlap of gain 1 and 2: no flapping
    assert ctx.data.pdtia_gain == 2


def test_auto_gain_is_idle_while_switched_off(online) -> None:
    ctx = online
    ctx.detector.select_gain(1)
    ctx.data.power_updated.emit(1e-9)
    assert ctx.data.pdtia_gain == 1


def test_switching_auto_on_reacts_to_the_last_known_power_at_once(online) -> None:
    ctx = online
    ctx.detector.select_gain(1)
    ctx.data.power_updated.emit(1e-9)
    assert ctx.data.pdtia_gain == 1
    ctx.detector.set_gain_auto(True)
    assert ctx.data.pdtia_gain == 3


def test_auto_gain_ignores_nan_power(online) -> None:
    ctx = online
    ctx.detector.select_gain(1)
    ctx.detector.set_gain_auto(True)
    ctx.data.power_updated.emit(float("nan"))
    assert ctx.data.pdtia_gain == 1


def test_auto_gain_is_suspended_during_the_kdc_zero_find(online) -> None:
    ctx = online
    ctx.detector.select_gain(1)
    ctx.detector.set_gain_auto(True)
    ctx.detector.gain_auto_suspended = True
    ctx.data.power_updated.emit(1e-9)
    assert ctx.data.pdtia_gain == 1


def test_auto_gain_is_idle_while_the_pm400_is_the_active_detector(online) -> None:
    ctx = online
    ctx.pm400.connect_resource("USB0::0x1313::0x8078::MOCK00001::INSTR")
    ctx.detector.select_gain(1)
    ctx.detector.set_gain_auto(True)
    ctx.data.power_updated.emit(1e-9)
    assert ctx.data.pdtia_gain == 1


def test_a_manual_gain_click_turns_auto_off(online, record) -> None:
    ctx = online
    ctx.detector.set_gain_auto(True)
    auto = record(ctx.detector.gain_auto_changed)
    ctx.detector.select_gain(4)
    assert not ctx.detector.gain_auto_enabled
    assert auto.calls == [(False,)]


def test_auto_gain_is_unavailable_without_valid_limits(ctx) -> None:
    from polarisation_ui.ui.controllers.detector_controller import DetectorController

    assert ctx.detector.gain_auto_available
    broken = {"pdtia": {"gain_auto_switch_power_W": {str(stage): "bad" for stage in (1, 2, 3, 4)}}}
    detector = DetectorController(
        load_config(overrides=broken), ctx.data, ctx.status, ctx.connection
    )
    assert not detector.gain_auto_available
    detector.set_gain_auto(True)  # harmless: nothing to switch to
    assert detector.gain_auto_enabled


# ---- profiles ---------------------------------------------------------------------------------


def test_selecting_a_profile_loads_it_into_the_data_controller(ctx, tmp_path, record) -> None:
    ctx.detector._profiles_dir = tmp_path
    path = _profile(tmp_path, "cal-a", wavelength=633.0)
    changed = record(ctx.detector.profile_changed)
    persist = record(ctx.detector.persist_requested)

    ctx.detector.select_profile(path)

    assert ctx.detector.calibration_profile is not None
    assert ctx.detector.calibration_profile.name == "cal-a"
    assert ctx.detector.profile_name == "cal-a"
    assert changed.calls == [("cal-a",)]
    assert len(persist) == 1


def test_clearing_the_profile_unloads_it(ctx, tmp_path) -> None:
    ctx.detector._profiles_dir = tmp_path
    ctx.detector.select_profile(_profile(tmp_path, "cal-a"))
    ctx.detector.select_profile(None)
    assert ctx.detector.calibration_profile is None
    assert ctx.detector.profile_name == ""


def test_a_broken_profile_file_leaves_no_profile_loaded(ctx, tmp_path) -> None:
    bad = tmp_path / "broken.json"
    bad.write_text("{not json", encoding="utf-8")
    ctx.detector.select_profile(bad)
    assert ctx.detector.calibration_profile is None
    assert ctx.detector.profile_name == "broken"


def test_profiles_can_be_selected_by_name(ctx, tmp_path) -> None:
    ctx.detector._profiles_dir = tmp_path
    _profile(tmp_path, "cal-a")
    _profile(tmp_path, "cal-b")
    assert ctx.detector.select_profile_by_name("cal-b")
    assert ctx.detector.profile_name == "cal-b"
    assert not ctx.detector.select_profile_by_name("missing")


def test_the_detector_row_asks_for_a_calibration_while_none_is_loaded(
    online, tmp_path, record
) -> None:
    ctx = online
    rows = record(ctx.detector.row_state_changed)
    ctx.detector.select_profile(None)
    assert rows.last()[1] == "warn"
    ctx.detector._profiles_dir = tmp_path
    ctx.detector.select_profile(_profile(tmp_path, "cal-a"))
    assert rows.last()[1] == "ok"


def test_the_calibration_hint_is_not_shown_while_disconnected(ctx, record) -> None:
    rows = record(ctx.detector.row_state_changed)
    ctx.detector.select_profile(None)
    assert len(rows) == 0


# ---- PD-TIA id --------------------------------------------------------------------------------


def test_the_pdtia_ids_come_from_the_config(ctx) -> None:
    assert ctx.detector.pdtia_ids == ["E1", "E2"]


def test_connecting_auto_selects_the_newest_profile_for_the_pdtia_id(
    ctx, port, qtbot, tmp_path, record
) -> None:
    ctx.detector._profiles_dir = tmp_path
    _profile(tmp_path, "20240101_E1")
    _profile(tmp_path, "20250101_E1")
    _profile(tmp_path, "20260101_E2")
    ctx.detector.init_pdtia_id("E1")
    changed = record(ctx.detector.profile_changed)

    with qtbot.waitSignal(ctx.data.frame_ready, timeout=5000):
        ctx.connection.connect_port(port)

    assert ctx.detector.profile_name == "20250101_E1"
    assert changed.calls == [("20250101_E1",)]


def test_changing_the_pdtia_id_while_connected_reruns_the_auto_selection(
    online, tmp_path, record
) -> None:
    ctx = online
    ctx.detector._profiles_dir = tmp_path
    _profile(tmp_path, "cal_E1")
    _profile(tmp_path, "cal_E2")
    persist = record(ctx.detector.persist_requested)

    ctx.detector.set_pdtia_id("E2")
    assert ctx.detector.profile_name == "cal_E2"
    ctx.detector.set_pdtia_id("E1")
    assert ctx.detector.profile_name == "cal_E1"
    assert len(persist) >= 2


def test_the_auto_selection_runs_once_per_id(online, tmp_path) -> None:
    ctx = online
    ctx.detector._profiles_dir = tmp_path
    _profile(tmp_path, "cal_E1")
    ctx.detector.set_pdtia_id("E1")
    ctx.detector.select_profile(None)  # the user clears it afterwards
    ctx.detector._auto_select_calibration_for_id("E1")
    assert ctx.detector.profile_name == ""


def test_restoring_a_pdtia_id_does_not_auto_select(ctx, tmp_path, record) -> None:
    ctx.detector._profiles_dir = tmp_path
    _profile(tmp_path, "cal_E2")
    shown = record(ctx.detector.pdtia_id_changed)
    ctx.detector.restore_pdtia_id("E2")
    assert ctx.detector.pdtia_id == "E2"
    assert shown.calls == [("E2",)]
    assert ctx.detector.profile_name == ""
    ctx.detector.restore_pdtia_id("unknown")
    assert ctx.detector.pdtia_id == "E2"


# ---- dark tare --------------------------------------------------------------------------------


def test_the_dark_tare_runs_and_reports_the_offset(qtbot, online, record) -> None:
    ctx = online
    busy = record(ctx.detector.dark_tare_busy)
    offset = record(ctx.detector.dark_offset_changed)
    status = record(ctx.status.message)

    ctx.detector.start_dark_tare()
    assert busy.calls == [(True,)]
    qtbot.waitUntil(lambda: len(offset) == 1, timeout=10000)

    assert busy.calls == [(True,), (False,)]
    assert offset.last()[0] != 0.0
    assert status.calls[0][1].endswith(f"0/{DARK_TARE_SAMPLES}")
    assert any(level == "success" for level, _ in status.calls)


def test_resetting_the_dark_offset_reports_zero(online, record) -> None:
    ctx = online
    offset = record(ctx.detector.dark_offset_changed)
    status = record(ctx.status.message)
    ctx.detector.reset_dark_offset()
    assert offset.calls == [(0.0,)]
    assert status.last()[0] == "info"


# ---- active detector --------------------------------------------------------------------------


def test_the_active_detector_signal_is_forwarded(ctx, record) -> None:
    active = record(ctx.detector.active_detector_changed)
    ctx.data.active_detector_changed.emit("pm400")
    assert active.calls == [("pm400",)]
