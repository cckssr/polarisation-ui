"""Mock port registry helpers shared by mock_arduino and the main app."""

from __future__ import annotations

import os
import tempfile
import time
from pathlib import Path

MOCK_PORT_DIR_ENV = "POLARISATION_UI_MOCK_PORT_DIR"
_DEFAULT_DIR_NAME = "polarisation-ui-mock-ports"
_FILE_PATTERN = "mock_arduino_*.port"


def get_registry_dir() -> Path:
    """Return the directory used to exchange mock PTY ports."""
    configured = os.environ.get(MOCK_PORT_DIR_ENV)
    if configured:
        return Path(configured)
    return Path(tempfile.gettempdir()) / _DEFAULT_DIR_NAME


def register_mock_port(port: str) -> Path:
    """Create a port file for the running mock process and return its path."""
    registry_dir = get_registry_dir()
    registry_dir.mkdir(parents=True, exist_ok=True)

    timestamp_ms = int(time.time() * 1000)
    file_path = registry_dir / f"mock_arduino_{os.getpid()}_{timestamp_ms}.port"
    file_path.write_text(f"{port}\n", encoding="utf-8")
    return file_path


def unregister_mock_port(file_path: Path | None) -> None:
    """Delete a previously created mock port file if it still exists."""
    if file_path is None:
        return
    try:
        file_path.unlink(missing_ok=True)
    except OSError:
        # Best effort cleanup only.
        return


def discover_mock_ports() -> list[str]:
    """Read all registered mock port files and return live PTY paths."""
    registry_dir = get_registry_dir()
    if not registry_dir.exists():
        return []

    ports: set[str] = set()
    for file_path in registry_dir.glob(_FILE_PATTERN):
        try:
            port = file_path.read_text(encoding="utf-8").strip()
        except OSError:
            continue

        if not port:
            continue

        if not os.path.exists(port):
            # Drop stale files from crashed or stopped mock instances.
            unregister_mock_port(file_path)
            continue

        ports.add(port)

    return sorted(ports)
