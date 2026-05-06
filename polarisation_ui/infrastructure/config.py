"""Configuration loading and management."""

import json
import sys
from pathlib import Path
from importlib.resources import files
from .logging import Debug


def import_config(language: str = "de") -> dict:
    """
    Imports the language-specific configuration from config.json.

    Priority order:
    1. File paths (package directory, project root, current directory, sys.prefix)
    2. Package resources as fallback

    Args:
        language (str): The language code to load the configuration for (default is "de").

    Returns:
        dict: The configuration dictionary for the specified language,
              or empty dict if not found.
    """

    # File paths in priority order
    possible_paths = [
        Path(__file__).parent.parent / "config.json",  # Package directory
        Path(__file__).parent.parent.parent / "config.json",  # Project root
        Path("config.json"),  # Current directory
        Path(sys.prefix) / "config.json",  # Installation prefix
    ]

    # Try to load from file paths first
    for config_path in possible_paths:
        try:
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    Debug.debug(f"Config loaded from: {config_path}")
                    return config.get(language, config.get("de", {}))
        except (FileNotFoundError, json.JSONDecodeError):
            continue

    # Fallback: try to load from package resources
    try:
        package_name = (
            __package__.split(".", maxsplit=1)[0] if __package__ else "application"
        )
        if sys.version_info >= (3, 9):
            package_config = files(package_name).joinpath("config.json")
            if hasattr(package_config, "read_text"):
                config = json.loads(package_config.read_text(encoding="utf-8"))
                Debug.debug(f"Config loaded from package resources ({package_name}).")
                return config.get(language, config.get("de", {}))
    except Exception as e:  # pylint: disable=broad-except
        Debug.debug(f"Failed to load config from package resources: {e}")

    Debug.error("config.json not found. Please ensure it exists in the project root.")
    return {}
