"""MeasurementController: group naming, filenames, prefix lock, save export, start/stop/reset."""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import datetime
from pathlib import Path

import pytest

from polarisation_ui.core.models import TabExport
from polarisation_ui.core.power_calibration import PowerCalibrationProfile
from polarisation_ui.infrastructure.utils import create_dropbox_foldername


def _export(tokens: list[str] | None = None) -> TabExport:
    return TabExport(
        filename_hint="malus",
        columns=["angle", "intensity"],
        rows=[["0", "1.0"], ["10", "0.97"]],
        metadata={"experiment": "malus"},
        filename_tokens=tokens or [],
    )


def _folder(group: str, team: str = "") -> str:
    tk = "TK41"
    sub = team.replace(" ", "_")
    return create_dropbox_foldername(group, tk, sub)


# ---- naming -----------------------------------------------------------------------------------


def test_group_team_and_suffix_are_stripped_and_announced(ctx, record) -> None:
    group = record(ctx.measurement.group_changed)
    team = record(ctx.measurement.team_changed)
    suffix = record(ctx.measurement.suffix_changed)
    persist = record(ctx.measurement.persist_requested)

    ctx.measurement.set_group(" B ")
    ctx.measurement.set_team(" Team Rot ")
    ctx.measurement.set_suffix(" run1 ")

    assert (ctx.measurement.group_letter, ctx.measurement.team_name) == ("B", "Team Rot")
    assert ctx.measurement.suffix == "run1"
    assert group.calls == [("B",)]
    assert team.calls == [("Team Rot",)]
    assert suffix.calls == [("run1",)]
    assert len(persist) == 3
    assert ctx.measurement.group_selected


def test_setting_an_unchanged_value_emits_nothing(ctx, record) -> None:
    ctx.measurement.set_group("A")
    ctx.measurement.set_team("x")
    ctx.measurement.set_suffix("y")
    persist = record(ctx.measurement.persist_requested)
    ctx.measurement.set_group("A")
    ctx.measurement.set_team(" x ")
    ctx.measurement.set_suffix("y")
    assert len(persist) == 0


def test_clearing_the_group_deselects_it(ctx, record) -> None:
    ctx.measurement.set_group("A")
    group = record(ctx.measurement.group_changed)
    ctx.measurement.set_group("")
    assert group.calls == [("",)]
    assert not ctx.measurement.group_selected


def test_the_filename_preview_is_empty_without_a_group(ctx) -> None:
    assert ctx.measurement.filename_display(_export()) == ""


def test_the_filename_preview_combines_folder_hint_group_and_suffix(ctx) -> None:
    ctx.measurement.set_group("C")
    ctx.measurement.set_team("Team Rot")
    ctx.measurement.set_suffix("run1")
    shown = ctx.measurement.filename_display(_export(["p"]))
    assert shown == f"{_folder('C', 'Team Rot')}/messung_malus_p_C_run1.csv"


def test_the_filename_preview_without_a_tab_uses_the_default_hint(ctx) -> None:
    ctx.measurement.set_group("A")
    assert ctx.measurement.filename_display(None) == f"{_folder('A')}/messung_messung_A.csv"


def test_the_calibration_wavelength_becomes_a_filename_token(ctx, tmp_path) -> None:
    ctx.measurement.set_group("A")
    path = tmp_path / "cal.json"
    PowerCalibrationProfile(name="cal", wavelength_nm=633.0).save(path)
    ctx.detector.select_profile(path)
    assert ctx.measurement.filename_tokens(["a"]) == ["a", "633nm"]
    assert ctx.measurement.file_stem("malus", ["a"]) == "messung_malus_a_633nm_A"
    ctx.detector.select_profile(None)
    assert ctx.measurement.filename_tokens(["a"]) == ["a"]


# ---- save -------------------------------------------------------------------------------------


def test_the_default_save_path_lives_in_the_group_folder_below_home(
    ctx, tmp_path, monkeypatch
) -> None:
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    ctx.measurement.set_group("D")
    path = ctx.measurement.default_save_path(_export())
    assert path == tmp_path / _folder("D") / "messung_malus_D.csv"
    assert path.parent.is_dir()


def test_saving_writes_csv_and_metadata_and_locks_the_prefix_once(ctx, tmp_path, record) -> None:
    ctx.measurement.set_group("A")
    ctx.measurement.set_suffix("s")
    locked = record(ctx.measurement.prefix_locked_changed)
    status = record(ctx.status.message)
    target = tmp_path / "out" / "a.csv"

    ctx.measurement.save_export(target, _export())

    assert target.read_text(encoding="utf-8").splitlines() == [
        "angle,intensity",
        "0,1.0",
        "10,0.97",
    ]
    meta = json.loads((tmp_path / "out" / "a_metadata.json").read_text(encoding="utf-8"))
    assert meta["group"] == "A"
    assert meta["suffix"] == "s"
    assert meta["point_count"] == 2
    assert meta["active_detector"] == "pdtia"
    assert meta["power_calibration"] == {}
    assert meta["experiment"] == "malus"
    assert ctx.measurement.prefix_locked
    assert locked.calls == [(True,)]
    assert status.last()[0] == "success"
    assert str(target) in status.last()[1]

    ctx.measurement.save_export(tmp_path / "b.csv", _export())
    assert locked.calls == [(True,)]  # locked only once


def test_saving_records_the_calibration_profile_and_the_active_detector(ctx, tmp_path) -> None:
    ctx.measurement.set_group("A")
    profile_path = tmp_path / "cal.json"
    PowerCalibrationProfile(name="cal", wavelength_nm=532.0).save(profile_path)
    ctx.detector.select_profile(profile_path)
    ctx.pm400.connect_resource("USB0::0x1313::0x8078::MOCK00001::INSTR")

    ctx.measurement.save_export(tmp_path / "c.csv", _export())

    meta = json.loads((tmp_path / "c_metadata.json").read_text(encoding="utf-8"))
    assert meta["active_detector"] == "pm400"
    assert meta["power_calibration"]["profile_name"] == "cal"
    assert meta["power_calibration"]["wavelength_nm"] == 532.0
    datetime.fromisoformat(meta["saved_at"])


# ---- start / stop / reset ---------------------------------------------------------------------


def test_starting_and_stopping_a_measurement(online, record) -> None:
    ctx = online
    started = record(ctx.measurement.started)
    stopped = record(ctx.measurement.stopped)
    status = record(ctx.status.message)

    assert ctx.measurement.start()
    assert ctx.measurement.is_measuring
    assert len(started) == 1
    assert status.last()[0] == "success"

    ctx.measurement.stop()
    assert not ctx.measurement.is_measuring
    assert len(stopped) == 1
    assert status.last()[0] == "info"


def test_starting_twice_is_reported_as_an_error(online, record) -> None:
    ctx = online
    ctx.measurement.start()
    status = record(ctx.status.message)
    assert not ctx.measurement.start()
    assert status.last()[0] == "error"
    ctx.measurement.stop()


def test_starting_without_a_connection_fails(ctx, record) -> None:
    status = record(ctx.status.message)
    assert not ctx.measurement.start()
    assert status.last()[0] == "error"


def test_resetting_asks_the_tabs_to_clear(ctx, record) -> None:
    reset = record(ctx.measurement.reset_performed)
    status = record(ctx.status.message)
    ctx.measurement.reset()
    assert len(reset) == 1
    assert status.last()[0] == "info"


def test_a_running_measurement_writes_a_journal_to_the_scratch_directory(online) -> None:
    ctx = online
    ctx.measurement.start()
    journal = ctx.data.current_journal
    assert journal is not None
    assert Path(ctx._scratch.name) in journal.journal_path.parents
    ctx.measurement.stop()


# ---- acquisition settings ---------------------------------------------------------------------


def test_the_acquisition_defaults_come_from_the_config(ctx) -> None:
    acq = ctx.config.section("acquisition")
    assert ctx.measurement.acq_settings.samp_averages == acq.get("samp_averages", 5)


def test_inline_changes_reach_the_data_controller_and_persist(ctx, record) -> None:
    persist = record(ctx.measurement.persist_requested)
    replaced = record(ctx.measurement.acq_settings_replaced)
    new = replace(ctx.measurement.acq_settings, samp_averages=9, det_average_on=False)

    ctx.measurement.set_acq_settings_inline(new)

    assert ctx.measurement.acq_settings == new
    assert ctx.data._sample_buffer.maxlen == 9
    assert len(persist) == 1
    assert len(replaced) == 0


@pytest.mark.parametrize("spike", [True, False])
def test_replaced_settings_update_the_data_controller_and_the_inline_controls(
    ctx, record, spike
) -> None:
    persist = record(ctx.measurement.persist_requested)
    replaced = record(ctx.measurement.acq_settings_replaced)
    new = replace(ctx.measurement.acq_settings, spike_filter_enabled=spike, pdtia_averages=7)

    ctx.measurement.replace_acq_settings(new)

    assert replaced.calls == [(new,)]
    assert ctx.data._intensity_buffer.maxlen == 7
    assert len(persist) == 0
