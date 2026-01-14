#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Polarisation-UI - Main program for Goniometer Control GUI.

Entry point for the application. Sets up the Qt application,
initializes logging, and launches the main window.
"""

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
from polarisation_ui.ui.windows.mainwindow import MainWindow


def main():
    """
    Main entry point of the application.

    Initializes:
        - Debug/logging system
        - Qt application
        - Main window
    """
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
    app = QApplication(sys.argv)
    app.setApplicationName(app_name)
    app.setQuitOnLastWindowClosed(True)

    # Create and show main window
    main_window = MainWindow()
    main_window.show()

    Debug.info("Main window displayed")

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
