from PySide6.QtWidgets import QMainWindow

from polarisation_ui.infrastructure.logging import Debug
from polarisation_ui.infrastructure.config import import_config
from polarisation_ui.pyqt.mainwindow_ui import Ui_MainWindow

# Import settings and messages
CONFIG = import_config()


class MainWindow(QMainWindow):
    """Main window of the GMCounter application.

    It handles the user interface, the device connection and the
    processing of the recorded data.  The implementation is split
    into several functional sections:

    1. Initialization and setup
    2. Data processing and statistics
    3. Measurement management
    4. UI event handlers
    5. Device control
    6. Helper functions
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        Debug.debug("MainWindow initialized.")
