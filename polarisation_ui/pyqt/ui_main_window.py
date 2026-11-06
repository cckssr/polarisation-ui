# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.12.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    QTime,
    QUrl,
    Qt,
)
from PySide6.QtGui import (
    QAction,
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PySide6.QtWidgets import (
    QApplication,
    QDockWidget,
    QFrame,
    QMainWindow,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QStatusBar,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from polarisation_ui.ui.widgets.event_log_panel import EventLogPanel
from polarisation_ui.ui.widgets.panels.arduino_panel import ArduinoPanel
from polarisation_ui.ui.widgets.panels.detector_panel import DetectorPanel
from polarisation_ui.ui.widgets.panels.kdc_panel import KdcPanel
from polarisation_ui.ui.widgets.panels.measurement_panel import MeasurementPanel
from polarisation_ui.ui.widgets.panels.readout_panel import ReadoutPanel
from polarisation_ui.ui.widgets.panels.save_panel import SavePanel
from polarisation_ui.ui.widgets.panels.stage_panel import StagePanel


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        self.actionAcquisitionSettings = QAction(MainWindow)
        self.actionAcquisitionSettings.setObjectName("actionAcquisitionSettings")
        self.actionPowerCalibration = QAction(MainWindow)
        self.actionPowerCalibration.setObjectName("actionPowerCalibration")
        self.actionAutoPowerCalibration = QAction(MainWindow)
        self.actionAutoPowerCalibration.setObjectName("actionAutoPowerCalibration")
        self.actionEncoderDebug = QAction(MainWindow)
        self.actionEncoderDebug.setObjectName("actionEncoderDebug")
        self.actionLogWindow = QAction(MainWindow)
        self.actionLogWindow.setObjectName("actionLogWindow")
        self.actionAutoSaveEnabled = QAction(MainWindow)
        self.actionAutoSaveEnabled.setObjectName("actionAutoSaveEnabled")
        self.actionAutoSaveEnabled.setCheckable(True)
        self.actionAutoSaveEnabled.setChecked(True)
        self.actionToggleControls = QAction(MainWindow)
        self.actionToggleControls.setObjectName("actionToggleControls")
        self.actionToggleControls.setCheckable(True)
        self.actionToggleControls.setChecked(True)
        self.actionToggleMeasurement = QAction(MainWindow)
        self.actionToggleMeasurement.setObjectName("actionToggleMeasurement")
        self.actionToggleMeasurement.setCheckable(True)
        self.actionToggleMeasurement.setChecked(True)
        self.actionToggleEventLog = QAction(MainWindow)
        self.actionToggleEventLog.setObjectName("actionToggleEventLog")
        self.actionToggleEventLog.setCheckable(True)
        self.actionToggleEventLog.setChecked(True)
        self.actionFullScreen = QAction(MainWindow)
        self.actionFullScreen.setObjectName("actionFullScreen")
        self.actionFullScreen.setCheckable(True)
        self.actionSwitchProfile = QAction(MainWindow)
        self.actionSwitchProfile.setObjectName("actionSwitchProfile")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.centralLayout = QVBoxLayout(self.centralwidget)
        self.centralLayout.setObjectName("centralLayout")
        self.centralLayout.setContentsMargins(0, 0, 0, 0)
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tabWidget.setDocumentMode(False)

        self.centralLayout.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.toolBar = QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        self.toolBar.setMovable(False)
        MainWindow.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolBar)
        self.dockControls = QDockWidget(MainWindow)
        self.dockControls.setObjectName("dockControls")
        self.dockControls.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
        )
        self.dockControls.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.dockControlsContents = QWidget()
        self.dockControlsContents.setObjectName("dockControlsContents")
        self.dockControlsLayout = QVBoxLayout(self.dockControlsContents)
        self.dockControlsLayout.setObjectName("dockControlsLayout")
        self.dockControlsLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollControls = QScrollArea(self.dockControlsContents)
        self.scrollControls.setObjectName("scrollControls")
        self.scrollControls.setFrameShape(QFrame.Shape.NoFrame)
        self.scrollControls.setWidgetResizable(True)
        self.contentControls = QWidget()
        self.contentControls.setObjectName("contentControls")
        self.contentControlsLayout = QVBoxLayout(self.contentControls)
        self.contentControlsLayout.setSpacing(6)
        self.contentControlsLayout.setObjectName("contentControlsLayout")
        self.contentControlsLayout.setContentsMargins(4, 4, 4, 4)
        self.arduinoPanel = ArduinoPanel(self.contentControls)
        self.arduinoPanel.setObjectName("arduinoPanel")

        self.contentControlsLayout.addWidget(self.arduinoPanel)

        self.sampleStagePanel = StagePanel(self.contentControls)
        self.sampleStagePanel.setObjectName("sampleStagePanel")

        self.contentControlsLayout.addWidget(self.sampleStagePanel)

        self.detectorStagePanel = StagePanel(self.contentControls)
        self.detectorStagePanel.setObjectName("detectorStagePanel")

        self.contentControlsLayout.addWidget(self.detectorStagePanel)

        self.kdcPanel = KdcPanel(self.contentControls)
        self.kdcPanel.setObjectName("kdcPanel")

        self.contentControlsLayout.addWidget(self.kdcPanel)

        self.detectorPanel = DetectorPanel(self.contentControls)
        self.detectorPanel.setObjectName("detectorPanel")

        self.contentControlsLayout.addWidget(self.detectorPanel)

        self.spacerControls = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.contentControlsLayout.addItem(self.spacerControls)

        self.scrollControls.setWidget(self.contentControls)

        self.dockControlsLayout.addWidget(self.scrollControls)

        self.dockControls.setWidget(self.dockControlsContents)
        MainWindow.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dockControls)
        self.dockMeasurement = QDockWidget(MainWindow)
        self.dockMeasurement.setObjectName("dockMeasurement")
        self.dockMeasurement.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
        )
        self.dockMeasurement.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        self.dockMeasurementContents = QWidget()
        self.dockMeasurementContents.setObjectName("dockMeasurementContents")
        self.dockMeasurementLayout = QVBoxLayout(self.dockMeasurementContents)
        self.dockMeasurementLayout.setObjectName("dockMeasurementLayout")
        self.dockMeasurementLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollMeasurement = QScrollArea(self.dockMeasurementContents)
        self.scrollMeasurement.setObjectName("scrollMeasurement")
        self.scrollMeasurement.setFrameShape(QFrame.Shape.NoFrame)
        self.scrollMeasurement.setWidgetResizable(True)
        self.contentMeasurement = QWidget()
        self.contentMeasurement.setObjectName("contentMeasurement")
        self.contentMeasurementLayout = QVBoxLayout(self.contentMeasurement)
        self.contentMeasurementLayout.setSpacing(6)
        self.contentMeasurementLayout.setObjectName("contentMeasurementLayout")
        self.contentMeasurementLayout.setContentsMargins(4, 4, 4, 4)
        self.readoutPanel = ReadoutPanel(self.contentMeasurement)
        self.readoutPanel.setObjectName("readoutPanel")

        self.contentMeasurementLayout.addWidget(self.readoutPanel)

        self.measurementPanel = MeasurementPanel(self.contentMeasurement)
        self.measurementPanel.setObjectName("measurementPanel")

        self.contentMeasurementLayout.addWidget(self.measurementPanel)

        self.savePanel = SavePanel(self.contentMeasurement)
        self.savePanel.setObjectName("savePanel")

        self.contentMeasurementLayout.addWidget(self.savePanel)

        self.spacerMeasurement = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.contentMeasurementLayout.addItem(self.spacerMeasurement)

        self.scrollMeasurement.setWidget(self.contentMeasurement)

        self.dockMeasurementLayout.addWidget(self.scrollMeasurement)

        self.dockMeasurement.setWidget(self.dockMeasurementContents)
        MainWindow.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dockMeasurement)
        self.dockEventLog = QDockWidget(MainWindow)
        self.dockEventLog.setObjectName("dockEventLog")
        self.dockEventLog.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
        )
        self.eventLogPanel = EventLogPanel()
        self.eventLogPanel.setObjectName("eventLogPanel")
        self.dockEventLog.setWidget(self.eventLogPanel)
        MainWindow.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.dockEventLog)
        self.statusBar = QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)

        self.toolBar.addAction(self.actionAcquisitionSettings)
        self.toolBar.addAction(self.actionPowerCalibration)
        self.toolBar.addAction(self.actionAutoPowerCalibration)
        self.toolBar.addAction(self.actionEncoderDebug)
        self.toolBar.addAction(self.actionLogWindow)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionAutoSaveEnabled)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionToggleControls)
        self.toolBar.addAction(self.actionToggleMeasurement)
        self.toolBar.addAction(self.actionToggleEventLog)
        self.toolBar.addAction(self.actionFullScreen)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionSwitchProfile)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", "Polarisation-UI", None))
        self.actionAcquisitionSettings.setText(
            QCoreApplication.translate("MainWindow", "Akquisition\u2026", None)
        )
        # if QT_CONFIG(tooltip)
        self.actionAcquisitionSettings.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "Akquisitions-Einstellungen (Spike-Filter, Probenstage-Inversion)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.actionPowerCalibration.setText(
            QCoreApplication.translate("MainWindow", "Leistungskalibrierung\u2026", None)
        )
        # if QT_CONFIG(tooltip)
        self.actionPowerCalibration.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Leistungskalibrierung (manuell) \u00f6ffnen", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.actionAutoPowerCalibration.setText(
            QCoreApplication.translate("MainWindow", "Auto-Kalibrierung\u2026", None)
        )
        # if QT_CONFIG(tooltip)
        self.actionAutoPowerCalibration.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Automatische Leistungskalibrierung \u00f6ffnen", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.actionEncoderDebug.setText(
            QCoreApplication.translate("MainWindow", "Encoder-Debug", None)
        )
        # if QT_CONFIG(tooltip)
        self.actionEncoderDebug.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Encoder-Debugging mit SCPI-Terminal und Diagnose \u00f6ffnen", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.actionLogWindow.setText(QCoreApplication.translate("MainWindow", "Log", None))
        # if QT_CONFIG(tooltip)
        self.actionLogWindow.setToolTip(
            QCoreApplication.translate("MainWindow", "Log-Ausgabe anzeigen", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.actionAutoSaveEnabled.setText(
            QCoreApplication.translate("MainWindow", "Dateiname-Zusatz", None)
        )
        # if QT_CONFIG(tooltip)
        self.actionAutoSaveEnabled.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "Eingabefeld \u201eEigenes Suffix\u201c im Bereich Speichern ein- oder ausblenden; ein bereits eingegebener Zusatz bleibt im Dateinamen erhalten",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.actionToggleControls.setText(
            QCoreApplication.translate("MainWindow", "Steuerung", None)
        )
        # if QT_CONFIG(tooltip)
        self.actionToggleControls.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "Seitenleiste mit Ger\u00e4ten und Detektor ein- oder ausblenden",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.actionToggleMeasurement.setText(
            QCoreApplication.translate("MainWindow", "Messdaten", None)
        )
        # if QT_CONFIG(tooltip)
        self.actionToggleMeasurement.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "Seitenleiste mit Messwerten, Messung und Speicherung ein- oder ausblenden",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.actionToggleEventLog.setText(
            QCoreApplication.translate("MainWindow", "Ereignisprotokoll", None)
        )
        # if QT_CONFIG(tooltip)
        self.actionToggleEventLog.setToolTip(
            QCoreApplication.translate("MainWindow", "Ereignisprotokoll ein- oder ausblenden", None)
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(shortcut)
        self.actionFullScreen.setShortcut(QCoreApplication.translate("MainWindow", "F11", None))
        # endif // QT_CONFIG(shortcut)
        self.actionFullScreen.setText(QCoreApplication.translate("MainWindow", "Vollbild", None))
        # if QT_CONFIG(tooltip)
        self.actionFullScreen.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Zwischen Vollbild und Fenster wechseln (F11)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.actionSwitchProfile.setText(
            QCoreApplication.translate("MainWindow", "Profil wechseln", None)
        )
        # if QT_CONFIG(tooltip)
        self.actionSwitchProfile.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Zwischen Experten- und Praktikumsprofil wechseln", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.toolBar.setWindowTitle(
            QCoreApplication.translate("MainWindow", "Werkzeugleiste", None)
        )
        self.dockControls.setWindowTitle(
            QCoreApplication.translate("MainWindow", "Steuerung", None)
        )
        self.dockMeasurement.setWindowTitle(
            QCoreApplication.translate("MainWindow", "Messdaten", None)
        )
        self.dockEventLog.setWindowTitle(
            QCoreApplication.translate("MainWindow", "Ereignisprotokoll", None)
        )

    # retranslateUi
