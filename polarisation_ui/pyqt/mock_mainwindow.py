"""Bare visual mock of MainWindow with all tabs, for Qt Creator / layout testing.

No devices, no controllers, no signal wiring beyond what build() does
internally. Run directly: python -m polarisation_ui.pyqt.mock_mainwindow
"""

import sys

from PySide6.QtWidgets import QApplication, QMainWindow

import polarisation_ui.ui.widgets.tabs  # NOQA: F401  (triggers tab registration)
from polarisation_ui.pyqt.ui_mainwindow import Ui_MainWindow
from polarisation_ui.ui.widgets.tab_registry import TabRegistry


def main() -> None:
    app = QApplication(sys.argv)

    window = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(window)

    for tab_cls in TabRegistry.all():
        tab = tab_cls()
        tab.build()
        ui.tabWidget.addTab(tab, tab.tab_title)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
