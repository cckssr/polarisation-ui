"""SessionController: debounced saving, restore round trip, orphan journals, partial export."""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from PySide6.QtCore import QObject

from polarisation_ui.core.power_calibration import PowerCalibrationProfile
from polarisation_ui.infrastructure.session_journal import SessionJournal
from polarisation_ui.infrastructure.session_state import (
    SessionState,
    load_session_state,
    save_session_state,
)
from polarisation_ui.ui.context import AppContext
from polarisation_ui.ui.controllers.session_controller import SessionController


@pytest.fixture
def paths(tmp_path: Path) -> dict[str, Path]:
    return {"state": tmp_path / "state" / "last_session.json", "journals": tmp_path / "journals"}


@pytest.fixture
def make_session(ctx: AppContext, paths):
    """A session controller with real persistence in tmp_path, bound to the simulated bench."""
    owner = QObject()
    holder = []

    def build() -> SessionController:
        session = SessionController(
            ctx.config,
            ctx.status,
            ctx.data,
            ctx.connection,
            ctx.kdc,
            ctx.pm400,
            ctx.detector,
            ctx.measurement,
            state_path=paths["state"],
            journal_base=paths["journals"],
            parent=owner,
        )
        holder.append(session)
        return session

    yield build
    for session in holder:
        session._timer.stop()
    owner.deleteLater()


# ---- saving -----------------------------------------------------------------------------------


def test_nothing_is_written_until_the_session_is_armed(qtbot, make_session, ctx, paths) -> None:
    session = make_session()
    ctx.measurement.set_group("A")
    session.schedule_save()
    qtbot.wait(700)
    assert not paths["state"].exists()


def test_changes_are_written_once_after_the_debounce(qtbot, make_session, ctx, paths) -> None:
    session = make_session()
    session.arm()
    ctx.measurement.set_group("B")  # persist_requested -> schedule_save
    ctx.measurement.set_team("Team Rot")
    assert not paths["state"].exists()  # still debouncing
    qtbot.waitUntil(lambda: paths["state"].exists(), timeout=3000)

    state = load_session_state(paths["state"])
    assert state is not None
    assert (state.group_letter, state.team_name) == ("B", "Team Rot")


def test_the_state_snapshot_collects_every_controller(online, make_session, tmp_path) -> None:
    ctx = online
    session = make_session()
    ctx.measurement.set_group("A")
    ctx.measurement.set_suffix("s")
    ctx.detector.select_gain(3)
    ctx.data.set_detector_offset(180.0)
    ctx.kdc.set_zero_offset(21.0)
    ctx.pm400.set_wavelength(532.0)
    ctx.pm400.set_resource("USB0::x")
    ctx.detector.init_pdtia_id("E1")
    profile = tmp_path / "cal.json"
    PowerCalibrationProfile(name="cal").save(profile)
    ctx.detector.select_profile(profile)
    session.set_tab_points_provider(lambda: {"malus": [{"angle": 1.0}]})

    state = session.build_state()

    assert state.group_letter == "A"
    assert state.suffix == "s"
    assert state.gain_stage == 3
    assert state.detector_offset_deg == 180.0
    assert state.kdc_zero_offset_deg == 21.0
    assert state.pm400_wavelength_nm == 532.0
    assert state.pm400_visa_resource == "USB0::x"
    assert state.pdtia_id == "E1"
    assert state.profile_name == "cal"
    assert state.acq_settings["samp_averages"] == ctx.measurement.acq_settings.samp_averages
    assert state.tab_points == {"malus": [{"angle": 1.0}]}
    assert state.saved_date == datetime.now().date().isoformat()


def test_a_session_without_a_state_path_never_touches_disk(ctx, paths) -> None:
    session = SessionController(
        ctx.config,
        ctx.status,
        ctx.data,
        ctx.connection,
        ctx.kdc,
        ctx.pm400,
        ctx.detector,
        ctx.measurement,
    )
    session.arm()
    session.schedule_save()
    session.save_state()
    assert not session.enabled
    assert session.restorable_state() is None
    assert session.find_orphans() == []
    assert not paths["state"].exists()


def test_shutdown_flushes_a_pending_save(qtbot, make_session, ctx, paths) -> None:
    session = make_session()
    session.arm()
    ctx.measurement.set_group("C")
    session.shutdown()
    state = load_session_state(paths["state"])
    assert state is not None and state.group_letter == "C"


# ---- restore ----------------------------------------------------------------------------------


def _saved(**changes) -> SessionState:
    now = datetime.now()
    base = SessionState(saved_date=now.date().isoformat(), saved_at=now.isoformat())
    return replace(base, **changes)


def test_only_todays_non_empty_state_is_offered_for_restore(make_session, paths) -> None:
    session = make_session()
    assert session.restorable_state() is None  # no file

    save_session_state(_saved(), paths["state"])
    assert session.restorable_state() is None  # nothing worth restoring

    yesterday = datetime.now() - timedelta(days=1)
    save_session_state(
        _saved(group_letter="A", saved_date=yesterday.date().isoformat()), paths["state"]
    )
    assert session.restorable_state() is None

    save_session_state(_saved(group_letter="A"), paths["state"])
    state = session.restorable_state()
    assert state is not None and state.group_letter == "A"


def test_the_session_round_trips_through_save_and_restore(
    online, make_session, tmp_path, record
) -> None:
    ctx = online
    session = make_session()
    profile = tmp_path / "cal.json"
    PowerCalibrationProfile(name="cal").save(profile)
    ctx.detector._profiles_dir = tmp_path
    ctx.pm400.refresh_resources()
    resource = ctx.pm400._resources[0]

    ctx.measurement.set_group("D")
    ctx.measurement.set_team("Team Blau")
    ctx.measurement.set_suffix("run2")
    ctx.detector.select_profile(profile)
    ctx.detector.restore_pdtia_id("E20057")
    ctx.data.set_detector_offset(180.0)
    ctx.kdc.set_zero_offset(33.0)
    ctx.pm400.select_resource(resource)
    ctx.pm400.set_wavelength(700.0)
    ctx.measurement.replace_acq_settings(
        replace(ctx.measurement.acq_settings, samp_averages=11, spike_max_delta_deg=4.0)
    )
    ctx.detector.select_gain(2)
    session.set_tab_points_provider(lambda: {"malus": [{"angle": 5.0, "intensity": 0.5}]})
    session.save_state()
    saved = load_session_state(paths_state(session))
    assert saved is not None

    # a fresh application state
    ctx.measurement.set_group("")
    ctx.measurement.set_team("")
    ctx.measurement.set_suffix("")
    ctx.detector.select_profile(None)
    ctx.data.set_detector_offset(0.0)
    ctx.kdc.set_zero_offset(0.0)
    ctx.pm400.set_wavelength(633.0)
    ctx.measurement.replace_acq_settings(replace(ctx.measurement.acq_settings, samp_averages=5))
    points = record(session.tab_points_restored)
    restored = record(session.restored)
    status = record(ctx.status.message)

    session.restore(saved)

    m = ctx.measurement
    assert (m.group_letter, m.team_name, m.suffix) == ("D", "Team Blau", "run2")
    assert ctx.detector.profile_name == "cal"
    assert ctx.detector.pdtia_id == "E20057"
    assert ctx.data.detector_offset_deg == 180.0
    assert ctx.kdc.zero_offset_deg == 33.0
    assert ctx.pm400.resource == resource
    assert ctx.pm400.wavelength_nm == 700.0
    assert m.acq_settings.samp_averages == 11
    assert m.acq_settings.spike_max_delta_deg == 4.0
    assert points.calls == [({"malus": [{"angle": 5.0, "intensity": 0.5}]},)]
    assert len(restored) == 1
    assert status.last()[0] == "success"
    # the saved gain is applied the next time the Arduino connects
    assert ctx.detector._pending_gain_restore == 2


def paths_state(session: SessionController) -> Path:
    assert session.state_path is not None
    return session.state_path


def test_a_restore_ignores_unknown_acquisition_keys(make_session, ctx) -> None:
    session = make_session()
    before = ctx.measurement.acq_settings
    session.restore(_saved(group_letter="A", acq_settings={"nonsense": 1, "det_averages": 8}))
    assert ctx.measurement.group_letter == "A"
    assert ctx.measurement.acq_settings.det_averages == 8
    assert ctx.measurement.acq_settings.samp_averages == before.samp_averages


# ---- orphan journals --------------------------------------------------------------------------


def _orphan(base: Path, name: str, rows: int = 2) -> Path:
    session_dir = base / name
    session_dir.mkdir(parents=True)
    lines = ["# firmware_version: 2.1.0", "ts_ms,sample_angle,detector_angle,intensity,gap"]
    lines += [f"{i},1.0,2.0,0.5," for i in range(rows)]
    (session_dir / "journal.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return session_dir


def test_unfinished_journals_are_detected_exported_and_finalized(
    make_session, paths, tmp_path
) -> None:
    session = make_session()
    first = _orphan(paths["journals"], "20260101T000000_000001")
    done = _orphan(paths["journals"], "20260101T000000_000002")
    (done / "finalized").touch()

    assert session.find_orphans() == [first]

    target = tmp_path / "recovered.csv"
    rows = session.export_orphan(first, target)

    assert rows == 2
    assert len(target.read_text(encoding="utf-8").splitlines()) == 3  # header + two rows
    assert session.find_orphans() == []


def test_dismissed_orphans_are_deleted(make_session, paths) -> None:
    session = make_session()
    orphans = [_orphan(paths["journals"], f"2026010{i}T000000_000000") for i in (1, 2)]
    session.discard_orphans(orphans)
    assert session.find_orphans() == []
    assert not any(p.exists() for p in orphans)


def test_the_partial_journal_is_only_offered_when_it_holds_data(
    online, make_session, tmp_path
) -> None:
    ctx = online
    session = make_session()
    assert session.partial_journal() is None  # no journal yet

    ctx.measurement.start()
    journal = ctx.data.current_journal
    assert journal is not None
    assert session.partial_journal() is None  # started but empty
    from polarisation_ui.core.models import Frame

    frame = Frame(ts_ms=1, sample_angle=1.0, detector_angle=2.0, intensity=0.1)
    journal.append_frame(frame)
    assert session.partial_journal() is journal

    target = tmp_path / "partial.csv"
    assert session.export_partial(journal, target) == 1
    assert target.exists()


def test_the_journal_base_follows_the_context_scratch_directory(ctx, port) -> None:
    assert ctx.session.journal_base is not None
    assert ctx.session.find_orphans() == []  # persistence off -> no scan at all
    assert SessionJournal.find_orphans(ctx.session.journal_base) == []


def test_state_files_are_valid_json(make_session, ctx, paths) -> None:
    session = make_session()
    ctx.measurement.set_group("A")
    session.save_state()
    data = json.loads(paths["state"].read_text(encoding="utf-8"))
    assert data["group_letter"] == "A"
