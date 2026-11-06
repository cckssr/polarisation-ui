#!/usr/bin/env python

"""Polarisation-UI - Main program for Goniometer Control GUI.

Entry point for the application. Sets up the Qt application,
initializes logging, and launches the main window.

Flags:
    --debug-only    Skip the main window and open only the encoder debug dialog.
                    Useful for hardware diagnostics without the full measurement UI.
    --power-cal     Launch the automatic power calibration window as a standalone
    --simulate      Run the main window on simulated devices (mock Arduino, KDC101, PM400);
                    no hardware needed.
    --profile       UI profile of the main window (expert or student); default:
                    ``application.profile`` of config.json. The toolbar can switch it at run time.
"""

import argparse
import os
import sys

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

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from polarisation_ui.core.formatting import init_from_config
from polarisation_ui.infrastructure.config import default_config
from polarisation_ui.infrastructure.device_manager import GoniometerDeviceManager
from polarisation_ui.infrastructure.logging import Debug
from polarisation_ui.ui.launcher import Launcher
from polarisation_ui.ui.windows.auto_power_calibration_window import (
    AutoPowerCalibrationWindow,
)
from polarisation_ui.ui.windows.encoder_debug_window import EncoderDebugDialog


def main():
    """Main entry point of the application.

    Initializes:
        - Debug/logging system
        - Qt application
        - Main window (or debug-only window when --debug-only is passed)
    """
    # Parse CLI flags before handing remaining args to Qt
    parser = argparse.ArgumentParser(description="Polarisation-UI — Goniometer control interface")
    parser.add_argument(
        "--debug-only",
        action="store_true",
        help="Launch only the encoder debug window (skips the main measurement UI)",
    )
    parser.add_argument(
        "--power-cal",
        action="store_true",
        help=(
            "Launch only the automatic power calibration window (standalone mode). "
            "The Arduino connection is managed inside the window itself."
        ),
    )
    parser.add_argument(
        "--simulate",
        action="store_true",
        help="Run the main window on simulated devices (no hardware needed)",
    )
    config = default_config()
    parser.add_argument(
        "--profile",
        choices=config.profile_names,
        default=None,
        help=(
            "UI profile of the main window "
            f"(default: {config.get('application.profile', 'expert')} from config.json)"
        ),
    )
    args, qt_argv = parser.parse_known_args()
    # Qt expects the program name as argv[0]
    qt_argv = [sys.argv[0]] + qt_argv

    # Enable fractional DPI scaling so Windows at 125 %/150 % renders correctly.
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # Configuration (loaded above for the --profile choices)
    init_from_config(config.data)
    version = config.get("version", "unknown")

    # Initialize debug system
    debug_level_map = {
        "verbose": Debug.DEBUG_VERBOSE,
        "info": Debug.DEBUG_INFO,
        "error": Debug.DEBUG_ERROR,
        "off": Debug.DEBUG_OFF,
    }
    debug_level_str = config.get("debug.level_default", "info")
    debug_level = debug_level_map.get(debug_level_str, Debug.DEBUG_INFO)

    app_name = config.get("application.name", "Goniometer Control")
    Debug.init(debug_level=debug_level, app_name=app_name)

    # Register global exception handler
    sys.excepthook = Debug.exception_hook

    Debug.info(f"Starting application version {version} with debug level {debug_level_str}...")

    # Create QApplication
    app = QApplication(qt_argv)
    app.setApplicationName(app_name)
    app.setQuitOnLastWindowClosed(True)

    if args.debug_only:
        # Not yet connected — the connection is made inside the dialog
        _run_debug_only(app, GoniometerDeviceManager(use_mock=False))
    elif args.power_cal:
        _run_power_cal(app)
    else:
        _run_main(app, profile=args.profile, simulate=args.simulate)


def _run_main(app: "QApplication", profile: str | None = None, simulate: bool = False) -> None:
    """Launch the full main window for ``profile`` (on simulated devices with ``simulate``).

    The :class:`Launcher` owns the window so the toolbar can switch the profile at run time.
    """
    launcher = Launcher(profile=profile, simulate=simulate, parent=app)
    launcher.start()
    Debug.info("Main window displayed")
    sys.exit(app.exec())


def _run_power_cal(app: "QApplication") -> None:
    """Launch the automatic power calibration window as a standalone main window."""
    Debug.info("Launching standalone power calibration mode")
    window = AutoPowerCalibrationWindow(data_controller=None)
    window.setWindowTitle("Automatische Leistungskalibrierung (Standalone)")
    # Make the dialog behave like a top-level window (own taskbar entry on Windows)
    window.setWindowFlag(Qt.WindowType.Window, True)
    window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
    window.show()
    sys.exit(app.exec())


def _run_debug_only(app: "QApplication", device_manager: GoniometerDeviceManager) -> None:
    """Launch only the encoder debug window (standalone mode)."""
    Debug.info("Launching debug-only mode")
    dialog = EncoderDebugDialog(device_manager, standalone=True)
    dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
    dialog.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
