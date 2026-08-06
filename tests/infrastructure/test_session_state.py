"""Tests for infrastructure.session_state — session persistence to JSON."""

from datetime import date, timedelta

from polarisation_ui.infrastructure.session_state import (
    SessionState,
    is_from_today,
    load_session_state,
    save_session_state,
)


def _make_state(**overrides) -> SessionState:
    base = dict(
        saved_date=date.today().isoformat(),
        saved_at="2026-06-05T14:30:00.123456",
        group_letter="A",
        team_name="Team1",
        suffix="run1",
        profile_name="Det-A",
        gain_stage=2,
        pdtia_id="PDTIA-01",
        detector_offset_deg=180.0,
        acq_settings={"samp_averages": 5},
        tab_points={"malus": [{"analyser_angle": 10.0}]},
    )
    base.update(overrides)
    return SessionState(**base)


class TestSaveLoadRoundTrip:
    def test_round_trip_preserves_all_fields(self, tmp_path):
        path = tmp_path / "session.json"
        state = _make_state()
        save_session_state(state, path=path)

        loaded = load_session_state(path=path)

        assert loaded == state

    def test_save_creates_parent_directories(self, tmp_path):
        path = tmp_path / "nested" / "dir" / "session.json"
        save_session_state(_make_state(), path=path)
        assert path.exists()

    def test_save_overwrites_previous_file(self, tmp_path):
        path = tmp_path / "session.json"
        save_session_state(_make_state(group_letter="A"), path=path)
        save_session_state(_make_state(group_letter="B"), path=path)

        loaded = load_session_state(path=path)
        assert loaded.group_letter == "B"


class TestLoadEdgeCases:
    def test_load_missing_file_returns_none(self, tmp_path):
        assert load_session_state(path=tmp_path / "does_not_exist.json") is None

    def test_load_corrupt_json_returns_none(self, tmp_path):
        path = tmp_path / "session.json"
        path.write_text("{not valid json", encoding="utf-8")
        assert load_session_state(path=path) is None

    def test_load_ignores_unknown_keys(self, tmp_path):
        """Old JSON files with keys removed in a later version must still load."""
        path = tmp_path / "session.json"
        path.write_text(
            '{"saved_date": "2026-01-01", "saved_at": "2026-01-01T00:00:00", '
            '"group_letter": "A", "some_future_field": "ignored"}',
            encoding="utf-8",
        )
        loaded = load_session_state(path=path)
        assert loaded is not None
        assert loaded.group_letter == "A"

    def test_load_missing_new_keys_uses_defaults(self, tmp_path):
        """Old JSON files missing keys added in a later version get dataclass defaults."""
        path = tmp_path / "session.json"
        path.write_text(
            '{"saved_date": "2026-01-01", "saved_at": "2026-01-01T00:00:00"}',
            encoding="utf-8",
        )
        loaded = load_session_state(path=path)
        assert loaded is not None
        assert loaded.gain_stage == 0
        assert loaded.tab_points == {}


class TestIsFromToday:
    def test_todays_date_is_true(self):
        assert is_from_today(_make_state(saved_date=date.today().isoformat())) is True

    def test_yesterdays_date_is_false(self):
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        assert is_from_today(_make_state(saved_date=yesterday)) is False

    def test_malformed_date_is_false(self):
        assert is_from_today(_make_state(saved_date="not-a-date")) is False
