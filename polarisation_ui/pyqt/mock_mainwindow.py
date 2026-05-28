import sys

from PySide6.QtWidgets import QApplication

from polarisation_ui.ui.windows.mainwindow import MainWindow
from polarisation_ui.infrastructure.device_manager import GoniometerDeviceManager


def main():
    """Main entry point for the application."""

    device_manager = GoniometerDeviceManager(use_mock=True)

    # Create QApplication
    app = QApplication()
    app.setApplicationName("Mock Main Window")
    app.setQuitOnLastWindowClosed(True)

    main_window = MainWindow(device_manager)
    main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
