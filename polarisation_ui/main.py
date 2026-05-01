#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Polarisation-UI - Main program for Goniometer Control GUI.

Entry point for the application. Sets up the Qt application,
initializes logging, and launches the main window.

Flags:
  --debug-only   Skip the main window and open only the encoder debug dialog.
                 Useful for hardware diagnostics without the full measurement UI.
"""

import argparse
import sys
import os

# If executed as a script (package context missing), ensure the repo root is on
# sys.path and set __package__ so relative imports below work correctly.
if __package__ is None:
    # polarisation_ui/ is the package directory; parent is repository root
    package_dir = os.path.dirname(__file__)
    repo_root = os.path.dirname(package_dir)
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    # define package name to allow relative imports
    __package__ = "polarisation_ui"

from PySide6.QtWidgets import QApplication

from polarisation_ui.infrastructure.logging import Debug
from polarisation_ui.infrastructure.config import import_config
from polarisation_ui.infrastructure.device_manager import GoniometerDeviceManager
from polarisation_ui.ui.windows.mainwindow import MainWindow


def main():
    """
    Main entry point of the application.

    Initializes:
        - Debug/logging system
        - Qt application
        - Main window (or debug-only window when --debug-only is passed)
    """
    # Parse CLI flags before handing remaining args to Qt
    parser = argparse.ArgumentParser(
        description="Polarisation-UI — Goniometer control interface"
    )
    parser.add_argument(
        "--debug-only",
        action="store_true",
        help="Launch only the encoder debug window (skips the main measurement UI)",
    )
    args, qt_argv = parser.parse_known_args()
    # Qt expects the program name as argv[0]
    qt_argv = [sys.argv[0]] + qt_argv

    # Load configuration
    config = import_config()

    # Initialize debug system
    debug_level_map = {
        "verbose": Debug.DEBUG_VERBOSE,
        "info": Debug.DEBUG_INFO,
        "error": Debug.DEBUG_ERROR,
        "off": Debug.DEBUG_OFF,
    }

    debug_level_str = config.get("debug", {}).get("level_default", "info")
    debug_level = debug_level_map.get(debug_level_str, Debug.DEBUG_INFO)

    app_name = config.get("application", {}).get("name", "Goniometer Control")
    Debug.init(debug_level=debug_level, app_name=app_name)

    # Register global exception handler
    sys.excepthook = Debug.exception_hook

    Debug.info("Starting application...")

    # Create QApplication
    app = QApplication(qt_argv)
    app.setApplicationName(app_name)
    app.setQuitOnLastWindowClosed(True)

    # Initialize device manager (not yet connected — connection happens in the window)
    device_manager = GoniometerDeviceManager(use_mock=False)

    if args.debug_only:
        _run_debug_only(app, device_manager)
    else:
        _run_main(app, device_manager)


def _run_main(app: "QApplication", device_manager: GoniometerDeviceManager) -> None:
    """Launch the full main window."""
    from polarisation_ui.ui.windows.mainwindow import MainWindow

    main_window = MainWindow(device_manager)
    main_window.show()
    Debug.info("Main window displayed")
    sys.exit(app.exec())


def _run_debug_only(
    app: "QApplication", device_manager: GoniometerDeviceManager
) -> None:
    """Launch only the encoder debug window (standalone mode)."""
    from polarisation_ui.ui.windows.encoder_debug_window import EncoderDebugDialog
    from PySide6.QtCore import Qt

    Debug.info("Launching debug-only mode")
    dialog = EncoderDebugDialog(device_manager, standalone=True)
    dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
    dialog.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
