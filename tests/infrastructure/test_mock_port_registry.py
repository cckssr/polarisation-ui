"""Tests for mock port temp-file registration and discovery."""

from __future__ import annotations

import sys
from types import SimpleNamespace
from unittest.mock import patch

import pytest

import polarisation_ui.infrastructure.mocks.mock_arduino as mock_arduino_module
from polarisation_ui.infrastructure.device_manager import GoniometerDeviceManager
from polarisation_ui.infrastructure.mocks.mock_arduino import MockArduino

pytestmark = pytest.mark.skipif(sys.platform == "win32", reason="PTY not available on Windows")


class TestMockPortRegistry:
    """Verify temp-file based mock port discovery and cleanup."""

    def test_mock_creates_and_deletes_port_file(self, tmp_path, monkeypatch) -> None:
        """Mock should register its PTY port and remove it on stop."""
        monkeypatch.setenv("POLARISATION_UI_MOCK_PORT_DIR", str(tmp_path))

        mock = MockArduino()
        pty_path = mock.start()

        files_while_running = list(tmp_path.glob("mock_arduino_*.port"))
        assert len(files_while_running) == 1
        assert files_while_running[0].read_text(encoding="utf-8").strip() == pty_path

        mock.stop()

        files_after_stop = list(tmp_path.glob("mock_arduino_*.port"))
        assert files_after_stop == []

    def test_device_manager_includes_registered_mock_port(self, tmp_path, monkeypatch) -> None:
        """list_available_ports should merge serial ports and mock-port files."""
        monkeypatch.setenv("POLARISATION_UI_MOCK_PORT_DIR", str(tmp_path))
        mock_file = tmp_path / "mock_arduino_1_123.port"
        mock_file.parent.mkdir(parents=True, exist_ok=True)
        mock_file.write_text("/dev/ttys999\n", encoding="utf-8")

        comports = [SimpleNamespace(device="/dev/cu.usbmodem14101")]
        with (
            patch(
                "polarisation_ui.infrastructure.device_manager.list_ports.comports",
                return_value=comports,
            ),
            patch(
                "polarisation_ui.infrastructure.mocks.mock_port_registry.os.path.exists",
                return_value=True,
            ),
        ):
            ports = GoniometerDeviceManager.list_available_ports()

        assert ports == ["/dev/cu.usbmodem14101", "/dev/ttys999"]

    def test_cli_exits_cleanly_without_pty_support(self, monkeypatch, capsys) -> None:
        """The CLI should stop with a clear error when PTY support is absent."""
        monkeypatch.setattr(mock_arduino_module, "_PTY_AVAILABLE", False)

        exit_code = mock_arduino_module.main()

        captured = capsys.readouterr()
        assert exit_code == 1
        assert "PTY support is unavailable" in captured.err
