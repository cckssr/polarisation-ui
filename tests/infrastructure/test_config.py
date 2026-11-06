"""Tests for infrastructure.config: AppConfig, load_config, default_config, import_config.

The path-resolution tests exercise the real config.json of the package; tests of the merge and
profile logic write small config files into ``tmp_path``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from polarisation_ui.infrastructure.config import (
    AppConfig,
    default_config,
    import_config,
    load_config,
    reset_default_config,
)
from polarisation_ui.infrastructure.logging import Debug

SAMPLE: dict[str, Any] = {
    "version": "9.9.9",
    "application": {"name": "Test", "profile": "expert"},
    "ui": {"malus_tab": {"buttonSave": "Speichern", "text_header": "Messung {n}"}},
    "messages": {
        "connected": "Verbunden",
        "pm400": {"not_found": "Kein PM400 an {port}"},
    },
    "timers": {"gui_update_interval": 200},
    "profiles": {
        "expert": {"name": "Experte"},
        "student": {
            "name": "Praktikum",
            "hidden_tabs": ["waveplate"],
            "hidden_widgets": {"malus_tab": ["buttonSave"]},
            "overrides": {
                "timers": {"gui_update_interval": 500},
                "ui": {"malus_tab": {"buttonSave": "Sichern"}},
            },
        },
    },
}


def _write(tmp_path: Path, data: dict[str, Any]) -> Path:
    path = tmp_path / "config.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


@pytest.fixture
def warnings(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Collect the messages passed to ``Debug.warning``."""
    messages: list[str] = []
    monkeypatch.setattr(Debug, "warning", classmethod(lambda cls, msg: messages.append(msg)))
    return messages


class TestPackagedConfig:
    def test_the_sections_are_top_level_not_nested_under_a_language(self):
        data = load_config().data
        assert "de" not in data
        assert {"version", "application", "connection", "ui", "messages", "profiles"} <= set(data)
        assert "plot_colors" in data

    def test_the_application_starts_as_expert_maximized(self):
        cfg = load_config()
        assert cfg.get("application.profile") == "expert"
        assert cfg.get("application.window_mode") == "maximized"
        assert cfg.profile == "expert"

    def test_every_form_has_a_ui_section(self):
        from polarisation_ui.pyqt.sync_texts import PYQT_DIR

        ui = load_config().section("ui")
        for form in (p.stem for p in PYQT_DIR.glob("*.ui")):
            assert isinstance(ui.get(form), dict), form

    def test_both_profiles_are_defined(self):
        cfg = load_config()
        assert set(cfg.profile_names) == {"expert", "student"}
        assert cfg.with_overrides({}).get("profiles.student.name") == "Praktikum"


class TestAppConfig:
    def test_get_resolves_dotted_paths_and_falls_back_to_the_default(self):
        cfg = AppConfig(SAMPLE)
        assert cfg.get("timers.gui_update_interval") == 200
        assert cfg.get("timers.missing", 7) == 7
        assert cfg.get("nothing.at.all") is None
        assert cfg.get("application.name.deeper", "x") == "x"

    def test_section_returns_a_dict_or_an_empty_one(self):
        cfg = AppConfig(SAMPLE)
        assert cfg.section("timers") == {"gui_update_interval": 200}
        assert cfg.section("nope") == {}
        assert cfg.section("version") == {}

    def test_text_reads_the_ui_section_formats_and_falls_back_to_the_path(self):
        cfg = AppConfig(SAMPLE)
        assert cfg.text("malus_tab.buttonSave") == "Speichern"
        assert cfg.text("malus_tab.text_header", n=3) == "Messung 3"
        assert cfg.text("malus_tab.unknown") == "malus_tab.unknown"

    def test_message_supports_flat_and_dotted_keys(self):
        cfg = AppConfig(SAMPLE)
        assert cfg.message("connected") == "Verbunden"
        assert cfg.message("pm400.not_found", port="COM3") == "Kein PM400 an COM3"
        assert cfg.message("pm400.missing") == "pm400.missing"

    def test_with_overrides_merges_a_copy_and_leaves_the_original_alone(self):
        cfg = AppConfig(SAMPLE)
        changed = cfg.with_overrides({"timers": {"gui_update_interval": 5}, "new": {"a": 1}})
        assert changed.get("timers.gui_update_interval") == 5
        assert changed.get("new.a") == 1
        assert changed.get("ui.malus_tab.buttonSave") == "Speichern"  # untouched siblings stay
        assert cfg.get("timers.gui_update_interval") == 200
        assert cfg.get("new") is None


class TestLoadConfig:
    def test_a_missing_file_yields_an_empty_config(self, tmp_path: Path):
        cfg = load_config(tmp_path / "absent.json")
        assert cfg.data == {}
        assert cfg.profile == "expert"

    def test_a_broken_file_yields_an_empty_config(self, tmp_path: Path):
        path = tmp_path / "config.json"
        path.write_text("{not json", encoding="utf-8")
        assert load_config(path).data == {}

    def test_the_caller_overrides_are_merged_last(self, tmp_path: Path):
        cfg = load_config(
            _write(tmp_path, SAMPLE),
            overrides={"timers": {"gui_update_interval": 1}},
            profile="student",
        )
        assert cfg.get("timers.gui_update_interval") == 1

    def test_the_profile_overrides_are_merged_into_the_data(self, tmp_path: Path):
        cfg = load_config(_write(tmp_path, SAMPLE), profile="student")
        assert cfg.profile == "student"
        assert cfg.profile_name == "Praktikum"
        assert cfg.get("timers.gui_update_interval") == 500
        assert cfg.text("malus_tab.buttonSave") == "Sichern"
        assert cfg.text("malus_tab.text_header", n=1) == "Messung 1"  # siblings survive
        assert cfg.hidden_tabs() == ["waveplate"]
        assert cfg.hidden_widgets() == {"malus_tab": ["buttonSave"]}

    def test_the_expert_profile_changes_nothing(self, tmp_path: Path):
        cfg = load_config(_write(tmp_path, SAMPLE))
        assert cfg.profile_name == "Experte"
        assert cfg.get("timers.gui_update_interval") == 200
        assert cfg.hidden_tabs() == []
        assert cfg.hidden_widgets() == {}

    def test_an_unknown_profile_falls_back_to_expert_and_warns(
        self, tmp_path: Path, warnings: list[str]
    ):
        cfg = load_config(_write(tmp_path, SAMPLE), profile="professor")
        assert cfg.profile == "expert"
        assert any("professor" in message for message in warnings)

    def test_the_profile_of_the_application_section_is_the_default(self, tmp_path: Path):
        data = json.loads(json.dumps(SAMPLE))
        data["application"]["profile"] = "student"
        assert load_config(_write(tmp_path, data)).profile == "student"

    def test_the_packaged_file_is_found_without_a_path(self):
        assert load_config().get("application.name") == "Polarisation UI"


class TestDefaultConfig:
    def test_it_is_loaded_once(self):
        reset_default_config()
        assert default_config() is default_config()

    def test_reset_forces_a_reload(self):
        first = default_config()
        reset_default_config()
        assert default_config() is not first


class TestImportConfig:
    """``import_config`` is the deprecated shim for the pre-AppConfig call sites."""

    def test_loads_real_config(self):
        config = import_config()
        assert isinstance(config, dict)
        assert "application" in config
        assert "connection" in config

    def test_returns_the_sections_of_the_default_config(self):
        assert import_config() is default_config().data
        assert "ui" in import_config()
        assert "status_led" in import_config()["ui"]

    def test_the_language_argument_is_ignored(self):
        assert import_config(language="fr") == import_config(language="de")

    def test_connection_backoff_defaults_present(self):
        backoff = import_config().get("connection", {}).get("backoff_delays_ms")
        assert isinstance(backoff, list)
        assert len(backoff) >= 1
