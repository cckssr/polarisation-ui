import sys
from PySide6.QtWidgets import QApplication  # pylint: disable=no-name-in-module
from PySide6.QtWidgets import QMainWindow, QDialog  # pylint: disable=no-name-in-module
from ui_mainwindow import Ui_MainWindow
from ui_acq_settings import Ui_Dialog as Ui_AcqSettingsDialog

# Globalen Exception-Handler registrieren
# sys.excepthook = Debug.exception_hook

# Debug.info("Starte Anwendung...")
if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(window)
    window.show()

    # Add signal to open acquisition settings dialog when menu action is triggered
    def open_acq_settings():
        dialog = QDialog(window)
        acq_ui = Ui_AcqSettingsDialog()
        acq_ui.setupUi(dialog)
        dialog.exec()

    ui.actionAcquisitionSettings.triggered.connect(open_acq_settings)

    sys.exit(app.exec())
