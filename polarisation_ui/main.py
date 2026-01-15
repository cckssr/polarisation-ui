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

from PySide6.QtWidgets import QApplication, QMessageBox

from polarisation_ui.infrastructure.logging import Debug
from polarisation_ui.infrastructure.config import import_config
from polarisation_ui.infrastructure.device_manager import GoniometerDeviceManager
from polarisation_ui.ui.windows.mainwindow import MainWindow
from polarisation_ui.ui.dialogs.connection import ConnectionDialog


def main():
    """
    Main entry point of the application.

    Initializes:
        - Debug/logging system
        - Qt application
        - Connection dialog (before main window)
        - Main window with connected devices
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

    # Initialize device manager
    device_manager = GoniometerDeviceManager(use_mock=False)

    # Show connection dialog
    connection_dialog = ConnectionDialog()

    # Connect test signal
    def test_connection(params):
        success = device_manager.connect_encoders(**params)
        if success:
            connection_dialog.set_test_result(True, "Connection successful")
            device_manager.disconnect_encoders()  # Disconnect after test
        else:
            error_msg = device_manager.get_encoder_status().error_message
            connection_dialog.set_test_result(False, error_msg or "Unknown error")

    connection_dialog.connection_requested.connect(test_connection)

    # Show dialog and wait for user
    if connection_dialog.exec() == ConnectionDialog.DialogCode.Accepted:
        params = connection_dialog.get_connection_params()

        # Connect devices
        success = device_manager.connect_encoders(**params)

        if success:
            Debug.info("Devices connected successfully")

            # Create and show main window with connected devices
            main_window = MainWindow(device_manager)
            main_window.show()

            Debug.info("Main window displayed")

            # Run application
            sys.exit(app.exec())
        else:
            # Connection failed
            error_msg = device_manager.get_encoder_status().error_message
            QMessageBox.critical(
                None,
                "Connection Error",
                f"Failed to connect to encoder device.\n\n{error_msg or 'Unknown error'}",
            )
            Debug.error("Connection failed, exiting")
            sys.exit(1)
    else:
        # User cancelled connection dialog
        Debug.info("Connection cancelled by user")
        sys.exit(0)


if __name__ == "__main__":
    main()
