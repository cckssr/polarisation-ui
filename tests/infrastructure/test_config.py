"""Tests for infrastructure.config.import_config.

The function resolves several fixed candidate paths derived from __file__/cwd/
sys.prefix internally (not dependency-injected), so from within this repo the
first candidate (the package directory's config.json) always matches. These
tests exercise the real config.json rather than mocking internal path
resolution, which would require refactoring the function for testability.
"""

from polarisation_ui.infrastructure.config import import_config


class TestImportConfig:
    def test_loads_real_config(self):
        config = import_config()
        assert isinstance(config, dict)
        assert config  # non-empty
        assert "application" in config
        assert "connection" in config

    def test_unknown_language_falls_back_to_de(self):
        de_config = import_config(language="de")
        unknown_config = import_config(language="fr")
        assert unknown_config == de_config

    def test_connection_backoff_defaults_present(self):
        config = import_config()
        backoff = config.get("connection", {}).get("backoff_delays_ms")
        assert isinstance(backoff, list)
        assert len(backoff) >= 1
