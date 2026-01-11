import sys
from PySide6.QtWidgets import QApplication  # pylint: disable=no-name-in-module
from PySide6.QtWidgets import QMainWindow  # pylint: disable=no-name-in-module
from ui_mainwindow import Ui_MainWindow

# Globalen Exception-Handler registrieren
# sys.excepthook = Debug.exception_hook

# Debug.info("Starte Anwendung...")
if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(window)
    window.show()
    sys.exit(app.exec())
