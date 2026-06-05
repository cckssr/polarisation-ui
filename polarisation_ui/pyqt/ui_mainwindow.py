# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
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
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDockWidget,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLCDNumber,
    QLabel,
    QLayout,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMenuBar,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QStatusBar,
    QTabWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from polarisation_ui.ui.widgets.event_log_panel import EventLogPanel


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1316, 1029)
        MainWindow.setMinimumSize(QSize(0, 0))
        self.actionAutoSaveEnabled = QAction(MainWindow)
        self.actionAutoSaveEnabled.setObjectName("actionAutoSaveEnabled")
        self.actionAutoSaveEnabled.setCheckable(True)
        self.actionAutoSaveEnabled.setChecked(True)
        self.actionAcquisitionSettings = QAction(MainWindow)
        self.actionAcquisitionSettings.setObjectName("actionAcquisitionSettings")
        self.actionAcquisitionSettings.setMenuRole(QAction.MenuRole.NoRole)
        self.actionEncoderDebug = QAction(MainWindow)
        self.actionEncoderDebug.setObjectName("actionEncoderDebug")
        self.actionLogWindow = QAction(MainWindow)
        self.actionLogWindow.setObjectName("actionLogWindow")
        self.actionPowerCalibration = QAction(MainWindow)
        self.actionPowerCalibration.setObjectName("actionPowerCalibration")
        self.actionPowerCalibration.setMenuRole(QAction.MenuRole.NoRole)
        self.actionEventLog = QAction(MainWindow)
        self.actionEventLog.setObjectName("actionEventLog")
        self.actionEventLog.setCheckable(True)
        self.actionAutoPowerCalibration = QAction(MainWindow)
        self.actionAutoPowerCalibration.setObjectName("actionAutoPowerCalibration")
        self.actionAutoPowerCalibration.setMenuRole(QAction.MenuRole.NoRole)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_5 = QGridLayout(self.centralwidget)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.gridLayout_5.setContentsMargins(10, 0, 10, 10)
        self.verticalLayout_2 = QVBoxLayout()
        # ifndef Q_OS_MAC
        self.verticalLayout_2.setSpacing(-1)
        # endif
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout_2.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.verticalLayout_2.setContentsMargins(0, -1, -1, 0)
        self.lblSampleStatus_2 = QLabel(self.centralwidget)
        self.lblSampleStatus_2.setObjectName("lblSampleStatus_2")
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.lblSampleStatus_2.sizePolicy().hasHeightForWidth()
        )
        self.lblSampleStatus_2.setSizePolicy(sizePolicy)
        self.lblSampleStatus_2.setAlignment(
            Qt.AlignmentFlag.AlignLeading
            | Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.verticalLayout_2.addWidget(self.lblSampleStatus_2)

        self.lcdSampleAngle = QLCDNumber(self.centralwidget)
        self.lcdSampleAngle.setObjectName("lcdSampleAngle")
        self.lcdSampleAngle.setEnabled(True)
        sizePolicy1 = QSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum
        )
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(
            self.lcdSampleAngle.sizePolicy().hasHeightForWidth()
        )
        self.lcdSampleAngle.setSizePolicy(sizePolicy1)
        self.lcdSampleAngle.setMinimumSize(QSize(0, 40))
        self.lcdSampleAngle.setLineWidth(2)
        self.lcdSampleAngle.setSmallDecimalPoint(False)
        self.lcdSampleAngle.setDigitCount(8)
        self.lcdSampleAngle.setProperty("value", 359.990000000000009)

        self.verticalLayout_2.addWidget(self.lcdSampleAngle)

        self.lblSampleStatus_3 = QLabel(self.centralwidget)
        self.lblSampleStatus_3.setObjectName("lblSampleStatus_3")
        sizePolicy.setHeightForWidth(
            self.lblSampleStatus_3.sizePolicy().hasHeightForWidth()
        )
        self.lblSampleStatus_3.setSizePolicy(sizePolicy)
        self.lblSampleStatus_3.setAlignment(
            Qt.AlignmentFlag.AlignLeading
            | Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.verticalLayout_2.addWidget(self.lblSampleStatus_3)

        self.lcdDetectorStageAngle = QLCDNumber(self.centralwidget)
        self.lcdDetectorStageAngle.setObjectName("lcdDetectorStageAngle")
        self.lcdDetectorStageAngle.setEnabled(True)
        sizePolicy1.setHeightForWidth(
            self.lcdDetectorStageAngle.sizePolicy().hasHeightForWidth()
        )
        self.lcdDetectorStageAngle.setSizePolicy(sizePolicy1)
        self.lcdDetectorStageAngle.setMinimumSize(QSize(0, 40))
        self.lcdDetectorStageAngle.setLineWidth(2)
        self.lcdDetectorStageAngle.setSmallDecimalPoint(False)
        self.lcdDetectorStageAngle.setDigitCount(8)
        self.lcdDetectorStageAngle.setProperty("value", 359.990000000000009)

        self.verticalLayout_2.addWidget(self.lcdDetectorStageAngle)

        self.verticalSpacer_2 = QSpacerItem(
            20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed
        )

        self.verticalLayout_2.addItem(self.verticalSpacer_2)

        self.lblSampleStatus_4 = QLabel(self.centralwidget)
        self.lblSampleStatus_4.setObjectName("lblSampleStatus_4")
        sizePolicy.setHeightForWidth(
            self.lblSampleStatus_4.sizePolicy().hasHeightForWidth()
        )
        self.lblSampleStatus_4.setSizePolicy(sizePolicy)
        self.lblSampleStatus_4.setAlignment(
            Qt.AlignmentFlag.AlignLeading
            | Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.verticalLayout_2.addWidget(self.lblSampleStatus_4)

        self.lcdWattage = QLCDNumber(self.centralwidget)
        self.lcdWattage.setObjectName("lcdWattage")
        self.lcdWattage.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.lcdWattage.sizePolicy().hasHeightForWidth())
        self.lcdWattage.setSizePolicy(sizePolicy1)
        self.lcdWattage.setMinimumSize(QSize(0, 40))
        self.lcdWattage.setLineWidth(2)
        self.lcdWattage.setDigitCount(8)
        self.lcdWattage.setProperty("value", 2499.989999999999782)

        self.verticalLayout_2.addWidget(self.lcdWattage)

        self.lblSampleStatus_5 = QLabel(self.centralwidget)
        self.lblSampleStatus_5.setObjectName("lblSampleStatus_5")
        sizePolicy.setHeightForWidth(
            self.lblSampleStatus_5.sizePolicy().hasHeightForWidth()
        )
        self.lblSampleStatus_5.setSizePolicy(sizePolicy)
        self.lblSampleStatus_5.setAlignment(
            Qt.AlignmentFlag.AlignLeading
            | Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.verticalLayout_2.addWidget(self.lblSampleStatus_5)

        self.lcdDetectorVoltage = QLCDNumber(self.centralwidget)
        self.lcdDetectorVoltage.setObjectName("lcdDetectorVoltage")
        self.lcdDetectorVoltage.setEnabled(True)
        sizePolicy1.setHeightForWidth(
            self.lcdDetectorVoltage.sizePolicy().hasHeightForWidth()
        )
        self.lcdDetectorVoltage.setSizePolicy(sizePolicy1)
        self.lcdDetectorVoltage.setMinimumSize(QSize(0, 40))
        self.lcdDetectorVoltage.setLineWidth(2)
        self.lcdDetectorVoltage.setDigitCount(8)
        self.lcdDetectorVoltage.setProperty("value", 499.990000000000009)

        self.verticalLayout_2.addWidget(self.lcdDetectorVoltage)

        self.gbDarkTare = QGroupBox(self.centralwidget)
        self.gbDarkTare.setObjectName("gbDarkTare")
        self.vlDarkTare = QVBoxLayout(self.gbDarkTare)
        self.vlDarkTare.setObjectName("vlDarkTare")
        self.vlDarkTare.setContentsMargins(5, 8, 5, 5)
        self.lblDarkOffsetValue = QLabel(self.gbDarkTare)
        self.lblDarkOffsetValue.setObjectName("lblDarkOffsetValue")

        self.vlDarkTare.addWidget(self.lblDarkOffsetValue)

        self.btnDarkTare = QPushButton(self.gbDarkTare)
        self.btnDarkTare.setObjectName("btnDarkTare")

        self.vlDarkTare.addWidget(self.btnDarkTare)

        self.btnDarkReset = QPushButton(self.gbDarkTare)
        self.btnDarkReset.setObjectName("btnDarkReset")

        self.vlDarkTare.addWidget(self.btnDarkReset)

        self.verticalLayout_2.addWidget(self.gbDarkTare)

        self.verticalSpacer = QSpacerItem(
            20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.MinimumExpanding
        )

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName("groupBox")
        self.groupBox.setMinimumSize(QSize(0, 40))
        self.verticalLayout_3 = QVBoxLayout(self.groupBox)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(5, 10, 5, 5)
        self.lblSuffix = QLabel(self.groupBox)
        self.lblSuffix.setObjectName("lblSuffix")

        self.verticalLayout_3.addWidget(self.lblSuffix)

        self.leSuffix = QLineEdit(self.groupBox)
        self.leSuffix.setObjectName("leSuffix")
        sizePolicy2 = QSizePolicy(
            QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed
        )
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.leSuffix.sizePolicy().hasHeightForWidth())
        self.leSuffix.setSizePolicy(sizePolicy2)
        self.leSuffix.setText("")
        self.leSuffix.setMaxLength(20)

        self.verticalLayout_3.addWidget(self.leSuffix)

        self.lblCurrentFilename = QLabel(self.groupBox)
        self.lblCurrentFilename.setObjectName("lblCurrentFilename")

        self.verticalLayout_3.addWidget(self.lblCurrentFilename)

        self.pteCurrentFilename = QPlainTextEdit(self.groupBox)
        self.pteCurrentFilename.setObjectName("pteCurrentFilename")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(
            self.pteCurrentFilename.sizePolicy().hasHeightForWidth()
        )
        self.pteCurrentFilename.setSizePolicy(sizePolicy3)
        self.pteCurrentFilename.setMaximumSize(QSize(200, 45))
        self.pteCurrentFilename.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.pteCurrentFilename.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.pteCurrentFilename.setUndoRedoEnabled(False)
        self.pteCurrentFilename.setReadOnly(True)

        self.verticalLayout_3.addWidget(self.pteCurrentFilename)

        self.lblDropbox = QLabel(self.groupBox)
        self.lblDropbox.setObjectName("lblDropbox")
        font = QFont()
        font.setPointSize(11)
        self.lblDropbox.setFont(font)
        self.lblDropbox.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop
        )

        self.verticalLayout_3.addWidget(self.lblDropbox)

        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout_2.setContentsMargins(2, 10, 2, 2)
        self.btnStopMeasurement = QPushButton(self.groupBox)
        self.btnStopMeasurement.setObjectName("btnStopMeasurement")
        self.btnStopMeasurement.setEnabled(False)
        self.btnStopMeasurement.setMinimumSize(QSize(60, 24))
        self.btnStopMeasurement.setMaximumSize(QSize(500, 32))

        self.gridLayout_2.addWidget(self.btnStopMeasurement, 0, 1, 1, 1)

        self.btnStartMeasurement = QPushButton(self.groupBox)
        self.btnStartMeasurement.setObjectName("btnStartMeasurement")
        self.btnStartMeasurement.setEnabled(False)
        self.btnStartMeasurement.setMinimumSize(QSize(60, 24))
        self.btnStartMeasurement.setMaximumSize(QSize(500, 32))

        self.gridLayout_2.addWidget(self.btnStartMeasurement, 0, 0, 1, 1)

        self.btnResetMeasurement = QPushButton(self.groupBox)
        self.btnResetMeasurement.setObjectName("btnResetMeasurement")
        self.btnResetMeasurement.setEnabled(False)

        self.gridLayout_2.addWidget(self.btnResetMeasurement, 1, 0, 1, 2)

        self.verticalLayout_3.addLayout(self.gridLayout_2)

        self.verticalLayout_2.addWidget(self.groupBox)

        self.gridLayout_5.addLayout(self.verticalLayout_2, 1, 0, 1, 1)

        self.line = QFrame(self.centralwidget)
        self.line.setObjectName("line")
        self.line.setFrameShadow(QFrame.Shadow.Plain)
        self.line.setFrameShape(QFrame.Shape.VLine)

        self.gridLayout_5.addWidget(self.line, 1, 1, 1, 1)

        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.configuration = QWidget()
        self.configuration.setObjectName("configuration")
        self.gridLayout = QGridLayout(self.configuration)
        self.gridLayout.setSpacing(20)
        self.gridLayout.setObjectName("gridLayout")
        self.gbSave = QGroupBox(self.configuration)
        self.gbSave.setObjectName("gbSave")
        sizePolicy4 = QSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred
        )
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.gbSave.sizePolicy().hasHeightForWidth())
        self.gbSave.setSizePolicy(sizePolicy4)
        self.gbSave.setMinimumSize(QSize(0, 0))
        self.gbSave.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gbSave.setFlat(False)
        self.gbSave.setCheckable(False)
        self.verticalLayout = QVBoxLayout(self.gbSave)
        self.verticalLayout.setSpacing(15)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.label = QLabel(self.gbSave)
        self.label.setObjectName("label")

        self.verticalLayout.addWidget(self.label)

        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.gridLayout_3.setContentsMargins(-1, -1, 0, 0)
        self.cbGroupLetter = QComboBox(self.gbSave)
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.setObjectName("cbGroupLetter")
        sizePolicy2.setHeightForWidth(
            self.cbGroupLetter.sizePolicy().hasHeightForWidth()
        )
        self.cbGroupLetter.setSizePolicy(sizePolicy2)
        self.cbGroupLetter.setMaxCount(24)
        self.cbGroupLetter.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        self.gridLayout_3.addWidget(self.cbGroupLetter, 0, 1, 1, 1)

        self.lblTeamName = QLabel(self.gbSave)
        self.lblTeamName.setObjectName("lblTeamName")

        self.gridLayout_3.addWidget(self.lblTeamName, 0, 2, 1, 1)

        self.lblGroupLetter = QLabel(self.gbSave)
        self.lblGroupLetter.setObjectName("lblGroupLetter")

        self.gridLayout_3.addWidget(self.lblGroupLetter, 0, 0, 1, 1)

        self.leTeamName = QLineEdit(self.gbSave)
        self.leTeamName.setObjectName("leTeamName")
        self.leTeamName.setMaxLength(20)

        self.gridLayout_3.addWidget(self.leTeamName, 0, 3, 1, 1)

        self.gridLayout_3.setColumnMinimumWidth(1, 1)
        self.gridLayout_3.setColumnMinimumWidth(3, 1)

        self.verticalLayout.addLayout(self.gridLayout_3)

        self.btnSave = QPushButton(self.gbSave)
        self.btnSave.setObjectName("btnSave")
        self.btnSave.setEnabled(False)
        sizePolicy3.setHeightForWidth(self.btnSave.sizePolicy().hasHeightForWidth())
        self.btnSave.setSizePolicy(sizePolicy3)
        self.btnSave.setMinimumSize(QSize(100, 30))
        self.btnSave.setMaximumSize(QSize(1000, 32))

        self.verticalLayout.addWidget(self.btnSave)

        self.gridLayout.addWidget(self.gbSave, 5, 0, 1, 2)

        self.gbDetector = QGroupBox(self.configuration)
        self.gbDetector.setObjectName("gbDetector")
        self.gbDetector.setEnabled(False)
        sizePolicy5 = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.gbDetector.sizePolicy().hasHeightForWidth())
        self.gbDetector.setSizePolicy(sizePolicy5)
        self.gbDetector.setMinimumSize(QSize(0, 0))
        self.gbDetector.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.horizontalLayout = QHBoxLayout(self.gbDetector)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.formLayout.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow
        )
        self.formLayout.setContentsMargins(-1, -1, 0, -1)
        self.hlGainButtons = QHBoxLayout()
        self.hlGainButtons.setSpacing(5)
        self.hlGainButtons.setObjectName("hlGainButtons")
        self.btnGain1 = QPushButton(self.gbDetector)
        self.gainButtonGroup = QButtonGroup(MainWindow)
        self.gainButtonGroup.setObjectName("gainButtonGroup")
        self.gainButtonGroup.addButton(self.btnGain1)
        self.btnGain1.setObjectName("btnGain1")
        sizePolicy6 = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.btnGain1.sizePolicy().hasHeightForWidth())
        self.btnGain1.setSizePolicy(sizePolicy6)
        self.btnGain1.setMaximumSize(QSize(100, 16777215))
        self.btnGain1.setCheckable(True)

        self.hlGainButtons.addWidget(self.btnGain1)

        self.btnGain2 = QPushButton(self.gbDetector)
        self.gainButtonGroup.addButton(self.btnGain2)
        self.btnGain2.setObjectName("btnGain2")
        sizePolicy6.setHeightForWidth(self.btnGain2.sizePolicy().hasHeightForWidth())
        self.btnGain2.setSizePolicy(sizePolicy6)
        self.btnGain2.setMaximumSize(QSize(100, 16777215))
        self.btnGain2.setCheckable(True)

        self.hlGainButtons.addWidget(self.btnGain2)

        self.btnGain3 = QPushButton(self.gbDetector)
        self.gainButtonGroup.addButton(self.btnGain3)
        self.btnGain3.setObjectName("btnGain3")
        sizePolicy6.setHeightForWidth(self.btnGain3.sizePolicy().hasHeightForWidth())
        self.btnGain3.setSizePolicy(sizePolicy6)
        self.btnGain3.setMaximumSize(QSize(100, 16777215))
        self.btnGain3.setCheckable(True)

        self.hlGainButtons.addWidget(self.btnGain3)

        self.btnGain4 = QPushButton(self.gbDetector)
        self.gainButtonGroup.addButton(self.btnGain4)
        self.btnGain4.setObjectName("btnGain4")
        sizePolicy6.setHeightForWidth(self.btnGain4.sizePolicy().hasHeightForWidth())
        self.btnGain4.setSizePolicy(sizePolicy6)
        self.btnGain4.setMaximumSize(QSize(100, 16777215))
        self.btnGain4.setCheckable(True)

        self.hlGainButtons.addWidget(self.btnGain4)

        self.hlGainButtons.setStretch(0, 1)
        self.hlGainButtons.setStretch(1, 1)
        self.hlGainButtons.setStretch(2, 1)
        self.hlGainButtons.setStretch(3, 1)

        self.formLayout.setLayout(2, QFormLayout.ItemRole.FieldRole, self.hlGainButtons)

        self.lblGainLabel = QLabel(self.gbDetector)
        self.lblGainLabel.setObjectName("lblGainLabel")
        sizePolicy7 = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum
        )
        sizePolicy7.setHorizontalStretch(0)
        sizePolicy7.setVerticalStretch(0)
        sizePolicy7.setHeightForWidth(
            self.lblGainLabel.sizePolicy().hasHeightForWidth()
        )
        self.lblGainLabel.setSizePolicy(sizePolicy7)

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lblGainLabel)

        self.lcdDetectorVoltage_2 = QLCDNumber(self.gbDetector)
        self.lcdDetectorVoltage_2.setObjectName("lcdDetectorVoltage_2")
        sizePolicy2.setHeightForWidth(
            self.lcdDetectorVoltage_2.sizePolicy().hasHeightForWidth()
        )
        self.lcdDetectorVoltage_2.setSizePolicy(sizePolicy2)
        self.lcdDetectorVoltage_2.setMinimumSize(QSize(0, 40))
        self.lcdDetectorVoltage_2.setLineWidth(2)
        self.lcdDetectorVoltage_2.setDigitCount(8)
        self.lcdDetectorVoltage_2.setSegmentStyle(QLCDNumber.SegmentStyle.Filled)

        self.formLayout.setWidget(
            1, QFormLayout.ItemRole.FieldRole, self.lcdDetectorVoltage_2
        )

        self.lblDetectorVoltage = QLabel(self.gbDetector)
        self.lblDetectorVoltage.setObjectName("lblDetectorVoltage")
        sizePolicy7.setHeightForWidth(
            self.lblDetectorVoltage.sizePolicy().hasHeightForWidth()
        )
        self.lblDetectorVoltage.setSizePolicy(sizePolicy7)

        self.formLayout.setWidget(
            1, QFormLayout.ItemRole.LabelRole, self.lblDetectorVoltage
        )

        self.lblWattage = QLabel(self.gbDetector)
        self.lblWattage.setObjectName("lblWattage")
        sizePolicy7.setHeightForWidth(self.lblWattage.sizePolicy().hasHeightForWidth())
        self.lblWattage.setSizePolicy(sizePolicy7)

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.lblWattage)

        self.lcdWattage_2 = QLCDNumber(self.gbDetector)
        self.lcdWattage_2.setObjectName("lcdWattage_2")
        sizePolicy2.setHeightForWidth(
            self.lcdWattage_2.sizePolicy().hasHeightForWidth()
        )
        self.lcdWattage_2.setSizePolicy(sizePolicy2)
        self.lcdWattage_2.setMinimumSize(QSize(0, 40))
        self.lcdWattage_2.setLineWidth(2)
        self.lcdWattage_2.setDigitCount(10)
        self.lcdWattage_2.setSegmentStyle(QLCDNumber.SegmentStyle.Filled)

        self.formLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.lcdWattage_2)

        self.lblDetectorStatus = QLabel(self.gbDetector)
        self.lblDetectorStatus.setObjectName("lblDetectorStatus")
        sizePolicy.setHeightForWidth(
            self.lblDetectorStatus.sizePolicy().hasHeightForWidth()
        )
        self.lblDetectorStatus.setSizePolicy(sizePolicy)
        self.lblDetectorStatus.setAlignment(
            Qt.AlignmentFlag.AlignLeading
            | Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.formLayout.setWidget(
            0, QFormLayout.ItemRole.LabelRole, self.lblDetectorStatus
        )

        self.hlDetectorStatus = QHBoxLayout()
        self.hlDetectorStatus.setObjectName("hlDetectorStatus")
        self.lblDetectorStatusValue = QLabel(self.gbDetector)
        self.lblDetectorStatusValue.setObjectName("lblDetectorStatusValue")
        sizePolicy5.setHeightForWidth(
            self.lblDetectorStatusValue.sizePolicy().hasHeightForWidth()
        )
        self.lblDetectorStatusValue.setSizePolicy(sizePolicy5)
        self.lblDetectorStatusValue.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignTrailing
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.hlDetectorStatus.addWidget(self.lblDetectorStatusValue)

        self.ledDetectorStatus = QLabel(self.gbDetector)
        self.ledDetectorStatus.setObjectName("ledDetectorStatus")
        sizePolicy7.setHeightForWidth(
            self.ledDetectorStatus.sizePolicy().hasHeightForWidth()
        )
        self.ledDetectorStatus.setSizePolicy(sizePolicy7)
        self.ledDetectorStatus.setMinimumSize(QSize(16, 16))
        self.ledDetectorStatus.setMaximumSize(QSize(16, 16))
        self.ledDetectorStatus.setStyleSheet(
            "background-color: rgb(255, 11, 3); border: 0px; padding: 3px; border-radius: 8px"
        )

        self.hlDetectorStatus.addWidget(self.ledDetectorStatus)

        self.formLayout.setLayout(
            0, QFormLayout.ItemRole.FieldRole, self.hlDetectorStatus
        )

        self.horizontalLayout.addLayout(self.formLayout)

        self.formLayout_2 = QFormLayout()
        self.formLayout_2.setObjectName("formLayout_2")
        self.formLayout_2.setFormAlignment(
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter
        )
        self.formLayout_2.setContentsMargins(-1, -1, 0, -1)
        self.cbProfile = QComboBox(self.gbDetector)
        self.cbProfile.setObjectName("cbProfile")
        sizePolicy6.setHeightForWidth(self.cbProfile.sizePolicy().hasHeightForWidth())
        self.cbProfile.setSizePolicy(sizePolicy6)

        self.formLayout_2.setWidget(
            0, QFormLayout.ItemRole.SpanningRole, self.cbProfile
        )

        self.hlProfileButtons = QHBoxLayout()
        self.hlProfileButtons.setObjectName("hlProfileButtons")
        self.btnReloadProfiles = QPushButton(self.gbDetector)
        self.btnReloadProfiles.setObjectName("btnReloadProfiles")

        self.hlProfileButtons.addWidget(self.btnReloadProfiles)

        self.btnOpenCalibration = QPushButton(self.gbDetector)
        self.btnOpenCalibration.setObjectName("btnOpenCalibration")

        self.hlProfileButtons.addWidget(self.btnOpenCalibration)

        self.formLayout_2.setLayout(
            1, QFormLayout.ItemRole.SpanningRole, self.hlProfileButtons
        )

        self.horizontalLayout.addLayout(self.formLayout_2)

        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 1)

        self.gridLayout.addWidget(self.gbDetector, 3, 0, 1, 2)

        self.gbDetectorStage = QGroupBox(self.configuration)
        self.gbDetectorStage.setObjectName("gbDetectorStage")
        self.gbDetectorStage.setEnabled(False)
        sizePolicy5.setHeightForWidth(
            self.gbDetectorStage.sizePolicy().hasHeightForWidth()
        )
        self.gbDetectorStage.setSizePolicy(sizePolicy5)
        self.gbDetectorStage.setMinimumSize(QSize(0, 0))
        self.gbDetectorStage.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.formDetectorStage = QFormLayout(self.gbDetectorStage)
        self.formDetectorStage.setObjectName("formDetectorStage")
        self.formDetectorStage.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        self.formDetectorStage.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow
        )
        self.formDetectorStage.setLabelAlignment(
            Qt.AlignmentFlag.AlignLeading
            | Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )
        self.formDetectorStage.setHorizontalSpacing(15)
        self.formDetectorStage.setVerticalSpacing(15)
        self.formDetectorStage.setContentsMargins(-1, 5, -1, 5)
        self.lblDetectorStageStatus = QLabel(self.gbDetectorStage)
        self.lblDetectorStageStatus.setObjectName("lblDetectorStageStatus")
        sizePolicy5.setHeightForWidth(
            self.lblDetectorStageStatus.sizePolicy().hasHeightForWidth()
        )
        self.lblDetectorStageStatus.setSizePolicy(sizePolicy5)
        self.lblDetectorStageStatus.setAlignment(
            Qt.AlignmentFlag.AlignLeading
            | Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.formDetectorStage.setWidget(
            0, QFormLayout.ItemRole.LabelRole, self.lblDetectorStageStatus
        )

        self.hlDetectorStageStatus = QHBoxLayout()
        self.hlDetectorStageStatus.setObjectName("hlDetectorStageStatus")
        self.lblDetectorStageStatusValue = QLabel(self.gbDetectorStage)
        self.lblDetectorStageStatusValue.setObjectName("lblDetectorStageStatusValue")
        sizePolicy5.setHeightForWidth(
            self.lblDetectorStageStatusValue.sizePolicy().hasHeightForWidth()
        )
        self.lblDetectorStageStatusValue.setSizePolicy(sizePolicy5)
        self.lblDetectorStageStatusValue.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignTrailing
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.hlDetectorStageStatus.addWidget(self.lblDetectorStageStatusValue)

        self.ledDetectorStageStatus = QLabel(self.gbDetectorStage)
        self.ledDetectorStageStatus.setObjectName("ledDetectorStageStatus")
        sizePolicy7.setHeightForWidth(
            self.ledDetectorStageStatus.sizePolicy().hasHeightForWidth()
        )
        self.ledDetectorStageStatus.setSizePolicy(sizePolicy7)
        self.ledDetectorStageStatus.setMinimumSize(QSize(16, 16))
        self.ledDetectorStageStatus.setMaximumSize(QSize(16, 16))
        self.ledDetectorStageStatus.setStyleSheet(
            "background-color: rgb(255, 11, 3); border: 0px; padding: 3px; border-radius: 8px"
        )

        self.hlDetectorStageStatus.addWidget(self.ledDetectorStageStatus)

        self.formDetectorStage.setLayout(
            0, QFormLayout.ItemRole.FieldRole, self.hlDetectorStageStatus
        )

        self.lblDetectorStageAngle = QLabel(self.gbDetectorStage)
        self.lblDetectorStageAngle.setObjectName("lblDetectorStageAngle")
        sizePolicy7.setHeightForWidth(
            self.lblDetectorStageAngle.sizePolicy().hasHeightForWidth()
        )
        self.lblDetectorStageAngle.setSizePolicy(sizePolicy7)

        self.formDetectorStage.setWidget(
            1, QFormLayout.ItemRole.LabelRole, self.lblDetectorStageAngle
        )

        self.lcdDetectorStageAngle_2 = QLCDNumber(self.gbDetectorStage)
        self.lcdDetectorStageAngle_2.setObjectName("lcdDetectorStageAngle_2")
        sizePolicy2.setHeightForWidth(
            self.lcdDetectorStageAngle_2.sizePolicy().hasHeightForWidth()
        )
        self.lcdDetectorStageAngle_2.setSizePolicy(sizePolicy2)
        self.lcdDetectorStageAngle_2.setMinimumSize(QSize(0, 40))
        self.lcdDetectorStageAngle_2.setLineWidth(2)
        self.lcdDetectorStageAngle_2.setDigitCount(6)
        self.lcdDetectorStageAngle_2.setSegmentStyle(QLCDNumber.SegmentStyle.Filled)

        self.formDetectorStage.setWidget(
            1, QFormLayout.ItemRole.FieldRole, self.lcdDetectorStageAngle_2
        )

        self.btnDetectorStageZero = QPushButton(self.gbDetectorStage)
        self.btnDetectorStageZero.setObjectName("btnDetectorStageZero")
        sizePolicy1.setHeightForWidth(
            self.btnDetectorStageZero.sizePolicy().hasHeightForWidth()
        )
        self.btnDetectorStageZero.setSizePolicy(sizePolicy1)
        self.btnDetectorStageZero.setMinimumSize(QSize(0, 0))

        self.formDetectorStage.setWidget(
            4, QFormLayout.ItemRole.SpanningRole, self.btnDetectorStageZero
        )

        self.spbDetectorAverages = QSpinBox(self.gbDetectorStage)
        self.spbDetectorAverages.setObjectName("spbDetectorAverages")
        self.spbDetectorAverages.setMinimum(2)
        self.spbDetectorAverages.setMaximum(100)
        self.spbDetectorAverages.setValue(5)

        self.formDetectorStage.setWidget(
            3, QFormLayout.ItemRole.FieldRole, self.spbDetectorAverages
        )

        self.lblDetectorAverages = QLabel(self.gbDetectorStage)
        self.lblDetectorAverages.setObjectName("lblDetectorAverages")
        sizePolicy7.setHeightForWidth(
            self.lblDetectorAverages.sizePolicy().hasHeightForWidth()
        )
        self.lblDetectorAverages.setSizePolicy(sizePolicy7)

        self.formDetectorStage.setWidget(
            3, QFormLayout.ItemRole.LabelRole, self.lblDetectorAverages
        )

        self.cbDetectorAverageOn = QCheckBox(self.gbDetectorStage)
        self.cbDetectorAverageOn.setObjectName("cbDetectorAverageOn")

        self.formDetectorStage.setWidget(
            2, QFormLayout.ItemRole.SpanningRole, self.cbDetectorAverageOn
        )

        self.gridLayout.addWidget(self.gbDetectorStage, 1, 1, 1, 1)

        self.gbSampleStage = QGroupBox(self.configuration)
        self.gbSampleStage.setObjectName("gbSampleStage")
        self.gbSampleStage.setEnabled(False)
        sizePolicy5.setHeightForWidth(
            self.gbSampleStage.sizePolicy().hasHeightForWidth()
        )
        self.gbSampleStage.setSizePolicy(sizePolicy5)
        self.gbSampleStage.setMinimumSize(QSize(0, 0))
        self.gbSampleStage.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gbSampleStage.setCheckable(False)
        self.formSampleStage = QFormLayout(self.gbSampleStage)
        self.formSampleStage.setObjectName("formSampleStage")
        self.formSampleStage.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        self.formSampleStage.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow
        )
        self.formSampleStage.setLabelAlignment(
            Qt.AlignmentFlag.AlignLeading
            | Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )
        self.formSampleStage.setHorizontalSpacing(15)
        self.formSampleStage.setVerticalSpacing(15)
        self.formSampleStage.setContentsMargins(-1, 5, -1, 5)
        self.lblSampleStatus = QLabel(self.gbSampleStage)
        self.lblSampleStatus.setObjectName("lblSampleStatus")
        sizePolicy.setHeightForWidth(
            self.lblSampleStatus.sizePolicy().hasHeightForWidth()
        )
        self.lblSampleStatus.setSizePolicy(sizePolicy)
        self.lblSampleStatus.setAlignment(
            Qt.AlignmentFlag.AlignLeading
            | Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.formSampleStage.setWidget(
            0, QFormLayout.ItemRole.LabelRole, self.lblSampleStatus
        )

        self.hlSampleStatus = QHBoxLayout()
        self.hlSampleStatus.setObjectName("hlSampleStatus")
        self.lblSampleStatusValue = QLabel(self.gbSampleStage)
        self.lblSampleStatusValue.setObjectName("lblSampleStatusValue")
        sizePolicy5.setHeightForWidth(
            self.lblSampleStatusValue.sizePolicy().hasHeightForWidth()
        )
        self.lblSampleStatusValue.setSizePolicy(sizePolicy5)
        self.lblSampleStatusValue.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignTrailing
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.hlSampleStatus.addWidget(self.lblSampleStatusValue)

        self.ledSampleStatus = QLabel(self.gbSampleStage)
        self.ledSampleStatus.setObjectName("ledSampleStatus")
        sizePolicy7.setHeightForWidth(
            self.ledSampleStatus.sizePolicy().hasHeightForWidth()
        )
        self.ledSampleStatus.setSizePolicy(sizePolicy7)
        self.ledSampleStatus.setMinimumSize(QSize(16, 16))
        self.ledSampleStatus.setMaximumSize(QSize(16, 16))
        self.ledSampleStatus.setStyleSheet(
            "background-color: rgb(255, 11, 3); border: 0px; padding: 3px; border-radius: 8px"
        )

        self.hlSampleStatus.addWidget(self.ledSampleStatus)

        self.formSampleStage.setLayout(
            0, QFormLayout.ItemRole.FieldRole, self.hlSampleStatus
        )

        self.lblSampleAngle = QLabel(self.gbSampleStage)
        self.lblSampleAngle.setObjectName("lblSampleAngle")
        sizePolicy7.setHeightForWidth(
            self.lblSampleAngle.sizePolicy().hasHeightForWidth()
        )
        self.lblSampleAngle.setSizePolicy(sizePolicy7)

        self.formSampleStage.setWidget(
            1, QFormLayout.ItemRole.LabelRole, self.lblSampleAngle
        )

        self.lcdSampleAngle_2 = QLCDNumber(self.gbSampleStage)
        self.lcdSampleAngle_2.setObjectName("lcdSampleAngle_2")
        sizePolicy2.setHeightForWidth(
            self.lcdSampleAngle_2.sizePolicy().hasHeightForWidth()
        )
        self.lcdSampleAngle_2.setSizePolicy(sizePolicy2)
        self.lcdSampleAngle_2.setMinimumSize(QSize(0, 40))
        self.lcdSampleAngle_2.setLineWidth(2)
        self.lcdSampleAngle_2.setDigitCount(6)
        self.lcdSampleAngle_2.setSegmentStyle(QLCDNumber.SegmentStyle.Filled)

        self.formSampleStage.setWidget(
            1, QFormLayout.ItemRole.FieldRole, self.lcdSampleAngle_2
        )

        self.btnSampleZero = QPushButton(self.gbSampleStage)
        self.btnSampleZero.setObjectName("btnSampleZero")
        sizePolicy1.setHeightForWidth(
            self.btnSampleZero.sizePolicy().hasHeightForWidth()
        )
        self.btnSampleZero.setSizePolicy(sizePolicy1)
        self.btnSampleZero.setMinimumSize(QSize(0, 0))

        self.formSampleStage.setWidget(
            4, QFormLayout.ItemRole.SpanningRole, self.btnSampleZero
        )

        self.lblSampleAverages = QLabel(self.gbSampleStage)
        self.lblSampleAverages.setObjectName("lblSampleAverages")
        sizePolicy7.setHeightForWidth(
            self.lblSampleAverages.sizePolicy().hasHeightForWidth()
        )
        self.lblSampleAverages.setSizePolicy(sizePolicy7)

        self.formSampleStage.setWidget(
            3, QFormLayout.ItemRole.LabelRole, self.lblSampleAverages
        )

        self.spbSampleAverages = QSpinBox(self.gbSampleStage)
        self.spbSampleAverages.setObjectName("spbSampleAverages")
        self.spbSampleAverages.setMinimum(2)
        self.spbSampleAverages.setMaximum(100)
        self.spbSampleAverages.setValue(5)

        self.formSampleStage.setWidget(
            3, QFormLayout.ItemRole.FieldRole, self.spbSampleAverages
        )

        self.cbSampleAverageOn = QCheckBox(self.gbSampleStage)
        self.cbSampleAverageOn.setObjectName("cbSampleAverageOn")

        self.formSampleStage.setWidget(
            2, QFormLayout.ItemRole.SpanningRole, self.cbSampleAverageOn
        )

        self.gridLayout.addWidget(self.gbSampleStage, 1, 0, 1, 1)

        self.gbKDCConnection = QGroupBox(self.configuration)
        self.gbKDCConnection.setObjectName("gbKDCConnection")
        sizePolicy7.setHeightForWidth(
            self.gbKDCConnection.sizePolicy().hasHeightForWidth()
        )
        self.gbKDCConnection.setSizePolicy(sizePolicy7)
        self.gbKDCConnection.setMinimumSize(QSize(0, 0))
        self.gbKDCConnection.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gbKDCConnection.setCheckable(False)
        self.formKDCConnection = QFormLayout(self.gbKDCConnection)
        self.formKDCConnection.setObjectName("formKDCConnection")
        self.formKDCConnection.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        self.formKDCConnection.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow
        )
        self.formKDCConnection.setLabelAlignment(
            Qt.AlignmentFlag.AlignLeading
            | Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )
        self.formKDCConnection.setHorizontalSpacing(15)
        self.formKDCConnection.setVerticalSpacing(15)
        self.formKDCConnection.setContentsMargins(-1, 5, -1, 5)
        self.lblKDCDeviceLabel = QLabel(self.gbKDCConnection)
        self.lblKDCDeviceLabel.setObjectName("lblKDCDeviceLabel")
        sizePolicy7.setHeightForWidth(
            self.lblKDCDeviceLabel.sizePolicy().hasHeightForWidth()
        )
        self.lblKDCDeviceLabel.setSizePolicy(sizePolicy7)
        self.lblKDCDeviceLabel.setAlignment(
            Qt.AlignmentFlag.AlignLeading
            | Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.formKDCConnection.setWidget(
            0, QFormLayout.ItemRole.LabelRole, self.lblKDCDeviceLabel
        )

        self.hlKDCDevice = QHBoxLayout()
        self.hlKDCDevice.setObjectName("hlKDCDevice")
        self.hlKDCDevice.setContentsMargins(-1, -1, -1, 0)
        self.cbKDCDevice = QComboBox(self.gbKDCConnection)
        self.cbKDCDevice.setObjectName("cbKDCDevice")
        sizePolicy.setHeightForWidth(self.cbKDCDevice.sizePolicy().hasHeightForWidth())
        self.cbKDCDevice.setSizePolicy(sizePolicy)
        self.cbKDCDevice.setMaximumSize(QSize(500, 16777215))

        self.hlKDCDevice.addWidget(self.cbKDCDevice)

        self.btnKDCRefresh = QToolButton(self.gbKDCConnection)
        self.btnKDCRefresh.setObjectName("btnKDCRefresh")
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.ViewRefresh))
        self.btnKDCRefresh.setIcon(icon)
        self.btnKDCRefresh.setIconSize(QSize(14, 14))

        self.hlKDCDevice.addWidget(self.btnKDCRefresh)

        self.formKDCConnection.setLayout(
            0, QFormLayout.ItemRole.FieldRole, self.hlKDCDevice
        )

        self.lblKDCStatusLabel = QLabel(self.gbKDCConnection)
        self.lblKDCStatusLabel.setObjectName("lblKDCStatusLabel")
        sizePolicy7.setHeightForWidth(
            self.lblKDCStatusLabel.sizePolicy().hasHeightForWidth()
        )
        self.lblKDCStatusLabel.setSizePolicy(sizePolicy7)
        self.lblKDCStatusLabel.setAlignment(
            Qt.AlignmentFlag.AlignLeading
            | Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.formKDCConnection.setWidget(
            1, QFormLayout.ItemRole.LabelRole, self.lblKDCStatusLabel
        )

        self.hlKDCStatus = QHBoxLayout()
        self.hlKDCStatus.setObjectName("hlKDCStatus")
        self.lblKDCStatusValue = QLabel(self.gbKDCConnection)
        self.lblKDCStatusValue.setObjectName("lblKDCStatusValue")
        sizePolicy7.setHeightForWidth(
            self.lblKDCStatusValue.sizePolicy().hasHeightForWidth()
        )
        self.lblKDCStatusValue.setSizePolicy(sizePolicy7)
        self.lblKDCStatusValue.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignTrailing
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.hlKDCStatus.addWidget(self.lblKDCStatusValue)

        self.ledKDCStatus = QLabel(self.gbKDCConnection)
        self.ledKDCStatus.setObjectName("ledKDCStatus")
        sizePolicy7.setHeightForWidth(
            self.ledKDCStatus.sizePolicy().hasHeightForWidth()
        )
        self.ledKDCStatus.setSizePolicy(sizePolicy7)
        self.ledKDCStatus.setMinimumSize(QSize(16, 16))
        self.ledKDCStatus.setMaximumSize(QSize(16, 16))
        self.ledKDCStatus.setStyleSheet(
            "background-color: rgb(255, 11, 3); border: 0px; padding: 3px; border-radius: 8px"
        )

        self.hlKDCStatus.addWidget(self.ledKDCStatus)

        self.formKDCConnection.setLayout(
            1, QFormLayout.ItemRole.FieldRole, self.hlKDCStatus
        )

        self.lblKDCPositionLabel = QLabel(self.gbKDCConnection)
        self.lblKDCPositionLabel.setObjectName("lblKDCPositionLabel")
        sizePolicy7.setHeightForWidth(
            self.lblKDCPositionLabel.sizePolicy().hasHeightForWidth()
        )
        self.lblKDCPositionLabel.setSizePolicy(sizePolicy7)
        self.lblKDCPositionLabel.setAlignment(
            Qt.AlignmentFlag.AlignLeading
            | Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.formKDCConnection.setWidget(
            2, QFormLayout.ItemRole.LabelRole, self.lblKDCPositionLabel
        )

        self.lblKDCPositionValue = QLabel(self.gbKDCConnection)
        self.lblKDCPositionValue.setObjectName("lblKDCPositionValue")
        sizePolicy7.setHeightForWidth(
            self.lblKDCPositionValue.sizePolicy().hasHeightForWidth()
        )
        self.lblKDCPositionValue.setSizePolicy(sizePolicy7)
        self.lblKDCPositionValue.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignTrailing
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.formKDCConnection.setWidget(
            2, QFormLayout.ItemRole.FieldRole, self.lblKDCPositionValue
        )

        self.btnKDCConnect = QPushButton(self.gbKDCConnection)
        self.btnKDCConnect.setObjectName("btnKDCConnect")
        sizePolicy7.setHeightForWidth(
            self.btnKDCConnect.sizePolicy().hasHeightForWidth()
        )
        self.btnKDCConnect.setSizePolicy(sizePolicy7)

        self.formKDCConnection.setWidget(
            3, QFormLayout.ItemRole.SpanningRole, self.btnKDCConnect
        )

        self.btnKDCHome = QPushButton(self.gbKDCConnection)
        self.btnKDCHome.setObjectName("btnKDCHome")
        self.btnKDCHome.setEnabled(False)
        sizePolicy7.setHeightForWidth(self.btnKDCHome.sizePolicy().hasHeightForWidth())
        self.btnKDCHome.setSizePolicy(sizePolicy7)

        self.formKDCConnection.setWidget(
            4, QFormLayout.ItemRole.SpanningRole, self.btnKDCHome
        )

        self.gridLayout.addWidget(self.gbKDCConnection, 0, 1, 1, 1)

        self.gbArduinoConnection = QGroupBox(self.configuration)
        self.gbArduinoConnection.setObjectName("gbArduinoConnection")
        sizePolicy7.setHeightForWidth(
            self.gbArduinoConnection.sizePolicy().hasHeightForWidth()
        )
        self.gbArduinoConnection.setSizePolicy(sizePolicy7)
        self.gbArduinoConnection.setMinimumSize(QSize(0, 0))
        self.gbArduinoConnection.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gbArduinoConnection.setCheckable(False)
        self.formArduinoConnection = QFormLayout(self.gbArduinoConnection)
        self.formArduinoConnection.setObjectName("formArduinoConnection")
        self.formArduinoConnection.setSizeConstraint(
            QLayout.SizeConstraint.SetNoConstraint
        )
        self.formArduinoConnection.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow
        )
        self.formArduinoConnection.setLabelAlignment(
            Qt.AlignmentFlag.AlignLeading
            | Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )
        self.formArduinoConnection.setHorizontalSpacing(15)
        self.formArduinoConnection.setVerticalSpacing(15)
        self.formArduinoConnection.setContentsMargins(-1, 5, -1, 5)
        self.lblArduinoPort = QLabel(self.gbArduinoConnection)
        self.lblArduinoPort.setObjectName("lblArduinoPort")
        sizePolicy7.setHeightForWidth(
            self.lblArduinoPort.sizePolicy().hasHeightForWidth()
        )
        self.lblArduinoPort.setSizePolicy(sizePolicy7)
        self.lblArduinoPort.setAlignment(
            Qt.AlignmentFlag.AlignLeading
            | Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.formArduinoConnection.setWidget(
            0, QFormLayout.ItemRole.LabelRole, self.lblArduinoPort
        )

        self.hlArduinoPort = QHBoxLayout()
        self.hlArduinoPort.setObjectName("hlArduinoPort")
        self.hlArduinoPort.setContentsMargins(-1, -1, -1, 0)
        self.cbArduinoPort = QComboBox(self.gbArduinoConnection)
        self.cbArduinoPort.setObjectName("cbArduinoPort")
        sizePolicy.setHeightForWidth(
            self.cbArduinoPort.sizePolicy().hasHeightForWidth()
        )
        self.cbArduinoPort.setSizePolicy(sizePolicy)
        self.cbArduinoPort.setMaximumSize(QSize(500, 16777215))

        self.hlArduinoPort.addWidget(self.cbArduinoPort)

        self.btnRefreshPorts = QToolButton(self.gbArduinoConnection)
        self.btnRefreshPorts.setObjectName("btnRefreshPorts")
        self.btnRefreshPorts.setIcon(icon)
        self.btnRefreshPorts.setIconSize(QSize(14, 14))

        self.hlArduinoPort.addWidget(self.btnRefreshPorts)

        self.formArduinoConnection.setLayout(
            0, QFormLayout.ItemRole.FieldRole, self.hlArduinoPort
        )

        self.lblArduinoStatus = QLabel(self.gbArduinoConnection)
        self.lblArduinoStatus.setObjectName("lblArduinoStatus")
        sizePolicy7.setHeightForWidth(
            self.lblArduinoStatus.sizePolicy().hasHeightForWidth()
        )
        self.lblArduinoStatus.setSizePolicy(sizePolicy7)
        self.lblArduinoStatus.setAlignment(
            Qt.AlignmentFlag.AlignLeading
            | Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.formArduinoConnection.setWidget(
            1, QFormLayout.ItemRole.LabelRole, self.lblArduinoStatus
        )

        self.hlArduinoStatus = QHBoxLayout()
        self.hlArduinoStatus.setObjectName("hlArduinoStatus")
        self.lblArduinoStatusValue = QLabel(self.gbArduinoConnection)
        self.lblArduinoStatusValue.setObjectName("lblArduinoStatusValue")
        sizePolicy7.setHeightForWidth(
            self.lblArduinoStatusValue.sizePolicy().hasHeightForWidth()
        )
        self.lblArduinoStatusValue.setSizePolicy(sizePolicy7)
        self.lblArduinoStatusValue.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignTrailing
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.hlArduinoStatus.addWidget(self.lblArduinoStatusValue)

        self.ledArduinoStatus = QLabel(self.gbArduinoConnection)
        self.ledArduinoStatus.setObjectName("ledArduinoStatus")
        sizePolicy7.setHeightForWidth(
            self.ledArduinoStatus.sizePolicy().hasHeightForWidth()
        )
        self.ledArduinoStatus.setSizePolicy(sizePolicy7)
        self.ledArduinoStatus.setMinimumSize(QSize(16, 16))
        self.ledArduinoStatus.setMaximumSize(QSize(16, 16))
        self.ledArduinoStatus.setStyleSheet(
            "background-color: rgb(255, 11, 3); border: 0px; padding: 3px; border-radius: 8px"
        )

        self.hlArduinoStatus.addWidget(self.ledArduinoStatus)

        self.formArduinoConnection.setLayout(
            1, QFormLayout.ItemRole.FieldRole, self.hlArduinoStatus
        )

        self.btnArduinoConnect = QPushButton(self.gbArduinoConnection)
        self.btnArduinoConnect.setObjectName("btnArduinoConnect")
        sizePolicy7.setHeightForWidth(
            self.btnArduinoConnect.sizePolicy().hasHeightForWidth()
        )
        self.btnArduinoConnect.setSizePolicy(sizePolicy7)
        self.btnArduinoConnect.setMinimumSize(QSize(0, 0))

        self.formArduinoConnection.setWidget(
            2, QFormLayout.ItemRole.SpanningRole, self.btnArduinoConnect
        )

        self.gridLayout.addWidget(self.gbArduinoConnection, 0, 0, 1, 1)

        self.verticalSpacer_3 = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.gridLayout.addItem(self.verticalSpacer_3, 4, 0, 1, 2)

        self.tabWidget.addTab(self.configuration, "")

        self.gridLayout_5.addWidget(self.tabWidget, 1, 2, 1, 1)

        self.gridLayout_5.setRowStretch(1, 1)
        self.gridLayout_5.setColumnStretch(2, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.dockEventLog = QDockWidget(MainWindow)
        self.dockEventLog.setObjectName("dockEventLog")
        self.eventLogPanel = EventLogPanel()
        self.eventLogPanel.setObjectName("eventLogPanel")
        self.dockEventLog.setWidget(self.eventLogPanel)
        MainWindow.addDockWidget(
            Qt.DockWidgetArea.BottomDockWidgetArea, self.dockEventLog
        )
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        self.menubar.setGeometry(QRect(0, 0, 1316, 39))
        self.menuEinstellungen = QMenu(self.menubar)
        self.menuEinstellungen.setObjectName("menuEinstellungen")
        MainWindow.setMenuBar(self.menubar)
        self.statusBar = QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)

        self.menubar.addAction(self.menuEinstellungen.menuAction())
        self.menuEinstellungen.addAction(self.actionAutoSaveEnabled)
        self.menuEinstellungen.addAction(self.actionAcquisitionSettings)
        self.menuEinstellungen.addAction(self.actionEncoderDebug)
        self.menuEinstellungen.addAction(self.actionLogWindow)
        self.menuEinstellungen.addAction(self.actionEventLog)
        self.menuEinstellungen.addAction(self.actionPowerCalibration)
        self.menuEinstellungen.addAction(self.actionAutoPowerCalibration)

        self.retranslateUi(MainWindow)
        self.actionAutoSaveEnabled.triggered["bool"].connect(self.lblSuffix.setVisible)
        self.actionAutoSaveEnabled.triggered["bool"].connect(self.leSuffix.setVisible)

        self.tabWidget.setCurrentIndex(0)
        self.cbGroupLetter.setCurrentIndex(-1)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            QCoreApplication.translate("MainWindow", "Polarisation-UI", None)
        )
        self.actionAutoSaveEnabled.setText(
            QCoreApplication.translate(
                "MainWindow", "Automatische Speicherung aktiviert", None
            )
        )
        self.actionAcquisitionSettings.setText(
            QCoreApplication.translate("MainWindow", "Aquisations-Einstellungen", None)
        )
        self.actionEncoderDebug.setText(
            QCoreApplication.translate("MainWindow", "Encoder Debugging", None)
        )
        self.actionLogWindow.setText(
            QCoreApplication.translate("MainWindow", "Log-Ausgabe anzeigen", None)
        )
        self.actionPowerCalibration.setText(
            QCoreApplication.translate(
                "MainWindow", "Leistungskalibrierung\u2026", None
            )
        )
        self.actionEventLog.setText(
            QCoreApplication.translate("MainWindow", "Ereignisprotokoll anzeigen", None)
        )
        self.actionAutoPowerCalibration.setText(
            QCoreApplication.translate(
                "MainWindow", "Automatische Leistungskalibrierung\u2026", None
            )
        )
        self.lblSampleStatus_2.setText(
            QCoreApplication.translate(
                "MainWindow", "Proben-Rotationswinkel (\u00b0)", None
            )
        )
        # if QT_CONFIG(tooltip)
        self.lcdSampleAngle.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "Aktueller Winkel der Proben-Rotationsstage (\u00b0)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.lblSampleStatus_3.setText(
            QCoreApplication.translate(
                "MainWindow", "Detektor-Rotationswinkel (\u00b0)", None
            )
        )
        # if QT_CONFIG(tooltip)
        self.lcdDetectorStageAngle.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "Aktueller Winkel der Detektor-Rotationsstage (\u00b0)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.lblSampleStatus_4.setText(
            QCoreApplication.translate("MainWindow", "Detektor-Spannung (mV)", None)
        )
        # if QT_CONFIG(tooltip)
        self.lcdWattage.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Detektorspannung in Millivolt (mV)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.lblSampleStatus_5.setText(
            QCoreApplication.translate(
                "MainWindow", "Detektor-Leistung (\u00b5W)", None
            )
        )
        # if QT_CONFIG(tooltip)
        self.lcdDetectorVoltage.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "Berechnete Laserleistung in Mikrowatt (\u00b5W) \u2014 nur mit geladenem Kalibrierungsprofil",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.gbDarkTare.setTitle(
            QCoreApplication.translate("MainWindow", "Dunkelstrom-Korrektur", None)
        )
        self.lblDarkOffsetValue.setText(
            QCoreApplication.translate("MainWindow", "Offset: \u2013", None)
        )
        # if QT_CONFIG(tooltip)
        self.lblDarkOffsetValue.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "Aktuell abgezogener Dunkelstrom-Offset in Millivolt",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnDarkTare.setText(
            QCoreApplication.translate("MainWindow", "Dunkelstrom nullen", None)
        )
        # if QT_CONFIG(tooltip)
        self.btnDarkTare.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "Detektor vollst\u00e4ndig abdecken, dann Dunkelstrom-Offset \u00fcber 2 s messen",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnDarkReset.setText(
            QCoreApplication.translate("MainWindow", "Offset zur\u00fccksetzen", None)
        )
        # if QT_CONFIG(tooltip)
        self.btnDarkReset.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Dunkelstrom-Offset auf 0 zur\u00fccksetzen", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.groupBox.setTitle(
            QCoreApplication.translate("MainWindow", "Messungseinstellung", None)
        )
        self.lblSuffix.setText(
            QCoreApplication.translate("MainWindow", "Eigenes Suffix", None)
        )
        # if QT_CONFIG(tooltip)
        self.leSuffix.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "Ein benutzerdefiniertes Suffix mit maximal 20 Zeichen",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.lblCurrentFilename.setText(
            QCoreApplication.translate("MainWindow", "Aktueller Dateiname", None)
        )
        # if QT_CONFIG(tooltip)
        self.pteCurrentFilename.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                '<html><head/><body><p>Die Dateien werden in einem speziell generierten Ordner abgelegt, welche die Nutzung der <a href="https://openbis.physik.tu-berlin.de/doku/students/gp/automatic_upload.html"><span style=" text-decoration: underline; color:#27bf73;">GP Dropbox</span></a> f\u00fcr den automatischen Upload erleichtert.</p></body></html>',
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.pteCurrentFilename.setPlainText("")
        self.lblDropbox.setText(
            QCoreApplication.translate(
                "MainWindow",
                '<html><head/><body><p><a href="https://openbis.physik.tu-berlin.de/doku/students/gp/automatic_upload.html"><span style=" text-decoration: underline; color:#27bf73;">GP-Dropbox</span></a></p></body></html>',
                None,
            )
        )
        # if QT_CONFIG(tooltip)
        self.btnStopMeasurement.setToolTip(
            QCoreApplication.translate("MainWindow", "Aktuelle Messung stoppen", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.btnStopMeasurement.setText(
            QCoreApplication.translate("MainWindow", "Stop", None)
        )
        # if QT_CONFIG(tooltip)
        self.btnStartMeasurement.setToolTip(
            QCoreApplication.translate("MainWindow", "Start der Messung", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.btnStartMeasurement.setText(
            QCoreApplication.translate("MainWindow", "Start", None)
        )
        # if QT_CONFIG(tooltip)
        self.btnResetMeasurement.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Alle gespeicherten Messpunkte verwerfen", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnResetMeasurement.setText(
            QCoreApplication.translate("MainWindow", "Reset", None)
        )
        self.gbSave.setTitle(
            QCoreApplication.translate("MainWindow", "Speicherung", None)
        )
        self.label.setText(
            QCoreApplication.translate(
                "MainWindow",
                "Bitte vor Beginn der Messungen Gruppe ausw\u00e4hlen.",
                None,
            )
        )
        self.cbGroupLetter.setItemText(
            0, QCoreApplication.translate("MainWindow", "A", None)
        )
        self.cbGroupLetter.setItemText(
            1, QCoreApplication.translate("MainWindow", "B", None)
        )
        self.cbGroupLetter.setItemText(
            2, QCoreApplication.translate("MainWindow", "C", None)
        )
        self.cbGroupLetter.setItemText(
            3, QCoreApplication.translate("MainWindow", "D", None)
        )
        self.cbGroupLetter.setItemText(
            4, QCoreApplication.translate("MainWindow", "E", None)
        )
        self.cbGroupLetter.setItemText(
            5, QCoreApplication.translate("MainWindow", "F", None)
        )
        self.cbGroupLetter.setItemText(
            6, QCoreApplication.translate("MainWindow", "G", None)
        )
        self.cbGroupLetter.setItemText(
            7, QCoreApplication.translate("MainWindow", "H", None)
        )
        self.cbGroupLetter.setItemText(
            8, QCoreApplication.translate("MainWindow", "I", None)
        )
        self.cbGroupLetter.setItemText(
            9, QCoreApplication.translate("MainWindow", "J", None)
        )
        self.cbGroupLetter.setItemText(
            10, QCoreApplication.translate("MainWindow", "K", None)
        )
        self.cbGroupLetter.setItemText(
            11, QCoreApplication.translate("MainWindow", "L", None)
        )
        self.cbGroupLetter.setItemText(
            12, QCoreApplication.translate("MainWindow", "M", None)
        )
        self.cbGroupLetter.setItemText(
            13, QCoreApplication.translate("MainWindow", "N", None)
        )
        self.cbGroupLetter.setItemText(
            14, QCoreApplication.translate("MainWindow", "O", None)
        )
        self.cbGroupLetter.setItemText(
            15, QCoreApplication.translate("MainWindow", "P", None)
        )
        self.cbGroupLetter.setItemText(
            16, QCoreApplication.translate("MainWindow", "Q", None)
        )
        self.cbGroupLetter.setItemText(
            17, QCoreApplication.translate("MainWindow", "R", None)
        )
        self.cbGroupLetter.setItemText(
            18, QCoreApplication.translate("MainWindow", "S", None)
        )
        self.cbGroupLetter.setItemText(
            19, QCoreApplication.translate("MainWindow", "T", None)
        )
        self.cbGroupLetter.setItemText(
            20, QCoreApplication.translate("MainWindow", "U", None)
        )
        self.cbGroupLetter.setItemText(
            21, QCoreApplication.translate("MainWindow", "V", None)
        )
        self.cbGroupLetter.setItemText(
            22, QCoreApplication.translate("MainWindow", "W", None)
        )
        self.cbGroupLetter.setItemText(
            23, QCoreApplication.translate("MainWindow", "Z", None)
        )

        # if QT_CONFIG(tooltip)
        self.cbGroupLetter.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Auswahl der GP Praktikumsgruppe (Pflichtfeld)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(tooltip)
        self.lblTeamName.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "Bezeichnung des spezifischen Teams einer Gruppe zur Identifizierung",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.lblTeamName.setText(
            QCoreApplication.translate("MainWindow", "Team-Bezeichnung*", None)
        )
        self.lblGroupLetter.setText(
            QCoreApplication.translate("MainWindow", "Buchstabe*", None)
        )
        # if QT_CONFIG(tooltip)
        self.leTeamName.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "Bezeichnung des spezifischen Teams einer Gruppe zur Identifizierung",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.leTeamName.setPlaceholderText(
            QCoreApplication.translate("MainWindow", "Bspw. TimStruppi", None)
        )
        # if QT_CONFIG(tooltip)
        self.btnSave.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Messung speichern (Dateidialog)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnSave.setText(
            QCoreApplication.translate("MainWindow", "Speichern", None)
        )
        self.gbDetector.setTitle(
            QCoreApplication.translate("MainWindow", "Detektor", None)
        )
        # if QT_CONFIG(tooltip)
        self.btnGain1.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "PD-TIA Verst\u00e4rkungsstufe 1 (niedrigste Empfindlichkeit)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnGain1.setText(QCoreApplication.translate("MainWindow", "1", None))
        # if QT_CONFIG(tooltip)
        self.btnGain2.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "PD-TIA Verst\u00e4rkungsstufe 2", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnGain2.setText(QCoreApplication.translate("MainWindow", "2", None))
        # if QT_CONFIG(tooltip)
        self.btnGain3.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "PD-TIA Verst\u00e4rkungsstufe 3", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnGain3.setText(QCoreApplication.translate("MainWindow", "3", None))
        # if QT_CONFIG(tooltip)
        self.btnGain4.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "PD-TIA Verst\u00e4rkungsstufe 4 (h\u00f6chste Empfindlichkeit)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnGain4.setText(QCoreApplication.translate("MainWindow", "4", None))
        self.lblGainLabel.setText(
            QCoreApplication.translate("MainWindow", "PD-TIA Gain", None)
        )
        self.lblDetectorVoltage.setText(
            QCoreApplication.translate("MainWindow", "Spannung (mV)", None)
        )
        self.lblWattage.setText(
            QCoreApplication.translate("MainWindow", "Leistung (\u00b5W)", None)
        )
        self.lblDetectorStatus.setText(
            QCoreApplication.translate("MainWindow", "Status", None)
        )
        self.lblDetectorStatusValue.setText("")
        self.ledDetectorStatus.setText("")
        # if QT_CONFIG(tooltip)
        self.cbProfile.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "Leistungskalibrierungsprofil ausw\u00e4hlen (optional \u2014 schaltet \u00b5W-Anzeige frei)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.cbProfile.setPlaceholderText(
            QCoreApplication.translate(
                "MainWindow", "\u2014 Kein Profil geladen \u2014", None
            )
        )
        # if QT_CONFIG(tooltip)
        self.btnReloadProfiles.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Profil-Liste aus dem Verzeichnis neu einlesen", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnReloadProfiles.setText(
            QCoreApplication.translate("MainWindow", "Aktualisieren", None)
        )
        # if QT_CONFIG(tooltip)
        self.btnOpenCalibration.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Leistungskalibrierungstool \u00f6ffnen", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnOpenCalibration.setText(
            QCoreApplication.translate("MainWindow", "Kalibrierungstool\u2026", None)
        )
        self.gbDetectorStage.setTitle(
            QCoreApplication.translate("MainWindow", "Detektor-Rotationsstage", None)
        )
        self.lblDetectorStageStatus.setText(
            QCoreApplication.translate("MainWindow", "Status", None)
        )
        self.lblDetectorStageStatusValue.setText("")
        self.ledDetectorStageStatus.setText("")
        self.lblDetectorStageAngle.setText(
            QCoreApplication.translate("MainWindow", "Rotationswinkel (\u00b0)", None)
        )
        # if QT_CONFIG(tooltip)
        self.btnDetectorStageZero.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "Aktuellen Winkel als Nullpunkt (0\u00b0) setzen (Encoder B)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnDetectorStageZero.setText(
            QCoreApplication.translate("MainWindow", "Nullpunkt-Kalibrierung", None)
        )
        # if QT_CONFIG(tooltip)
        self.spbDetectorAverages.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "Anzahl der Messwerte f\u00fcr die gleitende Mittelung (2\u2013100)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.lblDetectorAverages.setText(
            QCoreApplication.translate("MainWindow", "Anzahl Mittelwerte", None)
        )
        # if QT_CONFIG(tooltip)
        self.cbDetectorAverageOn.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "<html><head/><body><p>Aktiviert die kontinuierliche Mittelung der Detektor-Rotationsstage Winkel-Messwerte</p></body></html>",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.cbDetectorAverageOn.setText(
            QCoreApplication.translate("MainWindow", "Mittelung aktivieren", None)
        )
        self.gbSampleStage.setTitle(
            QCoreApplication.translate("MainWindow", "Proben-Rotationsstage", None)
        )
        self.lblSampleStatus.setText(
            QCoreApplication.translate("MainWindow", "Status", None)
        )
        self.lblSampleStatusValue.setText("")
        self.ledSampleStatus.setText("")
        self.lblSampleAngle.setText(
            QCoreApplication.translate("MainWindow", "Rotationswinkel (\u00b0)", None)
        )
        # if QT_CONFIG(tooltip)
        self.btnSampleZero.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "Aktuellen Winkel als Nullpunkt (0\u00b0) setzen (Encoder A)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnSampleZero.setText(
            QCoreApplication.translate("MainWindow", "Nullpunkt-Kalibrierung", None)
        )
        self.lblSampleAverages.setText(
            QCoreApplication.translate("MainWindow", "Anzahl Mittelwerte", None)
        )
        # if QT_CONFIG(tooltip)
        self.spbSampleAverages.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "Anzahl der Messwerte f\u00fcr die gleitende Mittelung (2\u2013100)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(tooltip)
        self.cbSampleAverageOn.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "<html><head/><body><p>Aktiviert die kontinuierliche Mittelung der Proben-Rotationsstage Winkel-Messwerte</p></body></html>",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.cbSampleAverageOn.setText(
            QCoreApplication.translate("MainWindow", "Mittelung aktivieren", None)
        )
        self.gbKDCConnection.setTitle(
            QCoreApplication.translate("MainWindow", "KDC-Verbindung", None)
        )
        self.lblKDCDeviceLabel.setText(
            QCoreApplication.translate("MainWindow", "Ger\u00e4t", None)
        )
        # if QT_CONFIG(tooltip)
        self.cbKDCDevice.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Thorlabs KDC101 Polarisationsrotator (USB-APT)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(tooltip)
        self.btnKDCRefresh.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "KDC101-Ger\u00e4teliste aktualisieren", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnKDCRefresh.setText(
            QCoreApplication.translate("MainWindow", "...", None)
        )
        self.lblKDCStatusLabel.setText(
            QCoreApplication.translate("MainWindow", "Status", None)
        )
        self.lblKDCStatusValue.setText(
            QCoreApplication.translate("MainWindow", "Nicht verbunden", None)
        )
        self.ledKDCStatus.setText("")
        self.lblKDCPositionLabel.setText(
            QCoreApplication.translate("MainWindow", "Position", None)
        )
        self.lblKDCPositionValue.setText(
            QCoreApplication.translate("MainWindow", "\u2014", None)
        )
        # if QT_CONFIG(tooltip)
        self.btnKDCConnect.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "KDC101 Polarisationsrotator verbinden oder trennen", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnKDCConnect.setText(
            QCoreApplication.translate("MainWindow", "Verbinden", None)
        )
        # if QT_CONFIG(tooltip)
        self.btnKDCHome.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "KDC101 auf Nullposition fahren (Home)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnKDCHome.setText(QCoreApplication.translate("MainWindow", "Home", None))
        self.gbArduinoConnection.setTitle(
            QCoreApplication.translate("MainWindow", "Arduino-Verbindung", None)
        )
        self.lblArduinoPort.setText(
            QCoreApplication.translate("MainWindow", "Port", None)
        )
        # if QT_CONFIG(tooltip)
        self.cbArduinoPort.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Serieller Port des Arduino Nano ESP32", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(tooltip)
        self.btnRefreshPorts.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Verf\u00fcgbare serielle Ports aktualisieren", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnRefreshPorts.setText(
            QCoreApplication.translate("MainWindow", "...", None)
        )
        self.lblArduinoStatus.setText(
            QCoreApplication.translate("MainWindow", "Status", None)
        )
        self.lblArduinoStatusValue.setText(
            QCoreApplication.translate("MainWindow", "Nicht verbunden", None)
        )
        self.ledArduinoStatus.setText("")
        # if QT_CONFIG(tooltip)
        self.btnArduinoConnect.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "Arduino \u00fcber den gew\u00e4hlten seriellen Port verbinden oder trennen",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnArduinoConnect.setText(
            QCoreApplication.translate("MainWindow", "Verbinden", None)
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.configuration),
            QCoreApplication.translate("MainWindow", "Konfiguration", None),
        )
        self.dockEventLog.setWindowTitle(
            QCoreApplication.translate("MainWindow", "Ereignisprotokoll", None)
        )
        self.menuEinstellungen.setTitle(
            QCoreApplication.translate("MainWindow", "Einstellungen", None)
        )

    # retranslateUi
