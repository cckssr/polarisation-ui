"""Application configuration: tunables and all (German) user-visible strings from config.json."""

from __future__ import annotations

import copy
import json
import sys
from importlib.resources import files
from pathlib import Path
from typing import Any

from .logging import Debug

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"
DEFAULT_PROFILE = "expert"


def _merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            _merge(base[key], value)
        else:
            base[key] = value
    return base


class AppConfig:
    """Read-only view on the parsed config.json with dotted-path access.

    ``profile`` names the entry of the ``profiles`` section that is active: its ``overrides``
    are already merged into the data, ``hidden_tabs`` / ``hidden_widgets`` are read by the UI.
    """

    def __init__(self, data: dict[str, Any], profile: str = DEFAULT_PROFILE) -> None:
        """Wrap the parsed ``data`` tree; ``profile`` is the active profile id."""
        self._data = data
        self.profile = profile

    @property
    def data(self) -> dict[str, Any]:
        """The parsed (profile-merged) configuration tree."""
        return self._data

    def get(self, path: str, default: Any = None) -> Any:
        """Look up ``"section.key.subkey"``; ``default`` if any part is missing."""
        node: Any = self._data
        for part in path.split("."):
            if not isinstance(node, dict) or part not in node:
                return default
            node = node[part]
        return node

    def section(self, name: str) -> dict[str, Any]:
        """Top-level section ``name`` (an empty dict if missing or not an object)."""
        value = self._data.get(name, {})
        return value if isinstance(value, dict) else {}

    def text(self, path: str, **fmt: Any) -> str:
        """German UI string at ``ui.<path>``; falls back to the path itself (visible, not fatal)."""
        value = self.get(f"ui.{path}", path)
        text = value if isinstance(value, str) else path
        return text.format(**fmt) if fmt else text

    def message(self, key: str, **fmt: Any) -> str:
        """Message (status/warning/error) at ``messages.<key>``; ``key`` may be dotted.

        Flat keys (``"connected"``) and area keys (``"pm400.not_found"``) both work. A missing
        key yields the key itself.
        """
        value = self.get(f"messages.{key}", key)
        text = value if isinstance(value, str) else key
        return text.format(**fmt) if fmt else text

    def with_overrides(self, overrides: dict[str, Any]) -> AppConfig:
        """Copy with a nested dict merged on top (used by tests and ``--simulate`` tweaks)."""
        return AppConfig(_merge(copy.deepcopy(self._data), copy.deepcopy(overrides)), self.profile)

    # ---- profiles ------------------------------------------------------------------------
    @property
    def profile_name(self) -> str:
        """German display name of the active profile."""
        return str(self.get(f"profiles.{self.profile}.name", self.profile))

    @property
    def profile_names(self) -> list[str]:
        """Ids of all profiles defined in config.json."""
        return list(self.section("profiles"))

    def hidden_tabs(self) -> list[str]:
        """Tab ids the active profile leaves out."""
        return list(self.get(f"profiles.{self.profile}.hidden_tabs", []))

    def hidden_widgets(self) -> dict[str, list[str]]:
        """Designer object names the active profile hides, per root (a panel or a tab id)."""
        value = self.get(f"profiles.{self.profile}.hidden_widgets", {})
        return (
            {root: list(names) for root, names in value.items()} if isinstance(value, dict) else {}
        )


def _candidate_paths() -> list[Path]:
    """Locations of config.json in priority order."""
    return [
        CONFIG_PATH,  # package directory
        CONFIG_PATH.parent.parent / "config.json",  # project root
        Path("config.json"),  # current directory
        Path(sys.prefix) / "config.json",  # installation prefix
    ]


def _read_data(path: Path | None) -> dict[str, Any]:
    """Parse config.json (an explicit ``path``, else the first candidate that loads).

    Falls back to the package resources; a missing or broken file yields ``{}`` (logged).
    """
    if path is not None:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            Debug.error(f"Cannot load {path}: {exc}")
            return {}

    for candidate in _candidate_paths():
        try:
            if candidate.exists():
                data = json.loads(candidate.read_text(encoding="utf-8"))
                Debug.debug(f"Config loaded from: {candidate}")
                return data
        except (OSError, json.JSONDecodeError):
            continue

    try:
        package_name = __package__.split(".", maxsplit=1)[0] if __package__ else "polarisation_ui"
        data = json.loads(files(package_name).joinpath("config.json").read_text(encoding="utf-8"))
        Debug.debug(f"Config loaded from package resources ({package_name}).")
        return data
    except Exception as exc:  # pylint: disable=broad-except
        Debug.debug(f"Failed to load config from package resources: {exc}")

    Debug.error("config.json not found. Please ensure it exists in the project root.")
    return {}


def load_config(
    path: Path | None = None,
    overrides: dict[str, Any] | None = None,
    profile: str | None = None,
) -> AppConfig:
    """Load config.json (UTF-8); a missing or broken file yields an empty config (logged).

    Without ``path`` the usual locations are searched (package directory, project root, current
    directory, ``sys.prefix``, package resources). ``profile`` (default: ``application.profile``)
    selects the entry of ``profiles`` whose ``overrides`` are merged over the defaults;
    ``overrides`` of the caller come last. An unknown profile is logged and replaced by the
    default one.
    """
    data = _read_data(path)
    profiles = data.get("profiles", {})
    name = profile or data.get("application", {}).get("profile", DEFAULT_PROFILE)
    if name not in profiles and name != DEFAULT_PROFILE:
        Debug.warning(f"unknown profile {name!r}, using {DEFAULT_PROFILE!r}")
        name = DEFAULT_PROFILE
    profile_overrides = profiles.get(name, {}).get("overrides", {})
    if profile_overrides:
        _merge(data, copy.deepcopy(profile_overrides))
    if overrides:
        _merge(data, copy.deepcopy(overrides))
    return AppConfig(data, name)


_default: AppConfig | None = None


def default_config() -> AppConfig:
    """The packaged configuration, loaded once per process (``reset_default_config`` clears it)."""
    global _default
    if _default is None:
        _default = load_config()
    return _default


def reset_default_config() -> None:
    """Forget the cached :func:`default_config` (tests)."""
    global _default
    _default = None


def import_config(language: str = "de") -> dict:
    """Return the configuration tree of :func:`default_config`.

    .. deprecated::
        Use :func:`default_config` / :func:`load_config` and the ``AppConfig`` accessors. The
        ``language`` argument is ignored since config.json no longer nests its sections below a
        language key; the function remains so existing call sites keep working.
    """
    del language
    return default_config().data
