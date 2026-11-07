# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'auto_power_calibration.ui'
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
    QAbstractItemView,
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from polarisation_ui.ui.widgets.detector_comparison_plot import DetectorComparisonPlot
from polarisation_ui.ui.widgets.multi_gain_calibration_plot import MultiGainCalibrationPlot
from polarisation_ui.ui.widgets.nd_linearity_plot import NDLinearityPlot
from polarisation_ui.ui.widgets.nd_transmission_plot import NDTransmissionPlot


class Ui_AutoPowerCalibrationDialog(object):
    def setupUi(self, AutoPowerCalibrationDialog):
        if not AutoPowerCalibrationDialog.objectName():
            AutoPowerCalibrationDialog.setObjectName("AutoPowerCalibrationDialog")
        AutoPowerCalibrationDialog.resize(1677, 1243)
        self.mainLayout = QVBoxLayout(AutoPowerCalibrationDialog)
        self.mainLayout.setSpacing(6)
        self.mainLayout.setObjectName("mainLayout")
        self.mainLayout.setContentsMargins(8, 8, 8, 8)
        self.groupConnections = QGroupBox(AutoPowerCalibrationDialog)
        self.groupConnections.setObjectName("groupConnections")
        self.gridLayout = QGridLayout(self.groupConnections)
        self.gridLayout.setObjectName("gridLayout")
        self.groupArduino = QGroupBox(self.groupConnections)
        self.groupArduino.setObjectName("groupArduino")
        self.groupArduino.setAlignment(
            Qt.AlignmentFlag.AlignLeading | Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        )
        self.arduinoGrid = QGridLayout(self.groupArduino)
        self.arduinoGrid.setSpacing(8)
        self.arduinoGrid.setObjectName("arduinoGrid")
        self.arduinoGrid.setContentsMargins(5, 5, 5, 5)
        self.labelArduinoPort = QLabel(self.groupArduino)
        self.labelArduinoPort.setObjectName("labelArduinoPort")

        self.arduinoGrid.addWidget(self.labelArduinoPort, 0, 0, 1, 1)

        self.comboArduinoPort = QComboBox(self.groupArduino)
        self.comboArduinoPort.setObjectName("comboArduinoPort")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboArduinoPort.sizePolicy().hasHeightForWidth())
        self.comboArduinoPort.setSizePolicy(sizePolicy)
        self.comboArduinoPort.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
        )
        self.comboArduinoPort.setMinimumContentsLength(14)

        self.arduinoGrid.addWidget(self.comboArduinoPort, 0, 1, 1, 1)

        self.buttonRefreshArduino = QPushButton(self.groupArduino)
        self.buttonRefreshArduino.setObjectName("buttonRefreshArduino")

        self.arduinoGrid.addWidget(self.buttonRefreshArduino, 0, 2, 1, 1)

        self.valueArduinoStatus = QLabel(self.groupArduino)
        self.valueArduinoStatus.setObjectName("valueArduinoStatus")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.valueArduinoStatus.sizePolicy().hasHeightForWidth())
        self.valueArduinoStatus.setSizePolicy(sizePolicy1)
        self.valueArduinoStatus.setMinimumSize(QSize(80, 0))

        self.arduinoGrid.addWidget(self.valueArduinoStatus, 1, 0, 1, 2)

        self.buttonConnectArduino = QPushButton(self.groupArduino)
        self.buttonConnectArduino.setObjectName("buttonConnectArduino")

        self.arduinoGrid.addWidget(self.buttonConnectArduino, 1, 2, 1, 1)

        self.gridLayout.addWidget(self.groupArduino, 0, 0, 1, 1)

        self.groupKDC = QGroupBox(self.groupConnections)
        self.groupKDC.setObjectName("groupKDC")
        self.groupKDC.setAlignment(
            Qt.AlignmentFlag.AlignLeading | Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        )
        self.groupKDC.setFlat(False)
        self.groupKDC.setCheckable(False)
        self.kdcGrid = QGridLayout(self.groupKDC)
        self.kdcGrid.setSpacing(8)
        self.kdcGrid.setObjectName("kdcGrid")
        self.kdcGrid.setContentsMargins(5, 5, 5, 5)
        self.buttonHomeKDC = QPushButton(self.groupKDC)
        self.buttonHomeKDC.setObjectName("buttonHomeKDC")
        self.buttonHomeKDC.setEnabled(False)

        self.kdcGrid.addWidget(self.buttonHomeKDC, 1, 3, 1, 1)

        self.labelKDCDevice = QLabel(self.groupKDC)
        self.labelKDCDevice.setObjectName("labelKDCDevice")

        self.kdcGrid.addWidget(self.labelKDCDevice, 0, 0, 1, 1)

        self.buttonConnectKDC = QPushButton(self.groupKDC)
        self.buttonConnectKDC.setObjectName("buttonConnectKDC")

        self.kdcGrid.addWidget(self.buttonConnectKDC, 1, 2, 1, 1)

        self.buttonRefreshKDC = QPushButton(self.groupKDC)
        self.buttonRefreshKDC.setObjectName("buttonRefreshKDC")

        self.kdcGrid.addWidget(self.buttonRefreshKDC, 0, 3, 1, 1)

        self.comboKDC = QComboBox(self.groupKDC)
        self.comboKDC.setObjectName("comboKDC")
        sizePolicy.setHeightForWidth(self.comboKDC.sizePolicy().hasHeightForWidth())
        self.comboKDC.setSizePolicy(sizePolicy)
        self.comboKDC.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
        )
        self.comboKDC.setMinimumContentsLength(14)

        self.kdcGrid.addWidget(self.comboKDC, 0, 1, 1, 2)

        self.valueKDCStatus = QLabel(self.groupKDC)
        self.valueKDCStatus.setObjectName("valueKDCStatus")
        sizePolicy1.setHeightForWidth(self.valueKDCStatus.sizePolicy().hasHeightForWidth())
        self.valueKDCStatus.setSizePolicy(sizePolicy1)
        self.valueKDCStatus.setMinimumSize(QSize(80, 0))
        self.valueKDCStatus.setTextFormat(Qt.TextFormat.AutoText)
        self.valueKDCStatus.setIndent(-1)

        self.kdcGrid.addWidget(self.valueKDCStatus, 1, 0, 1, 2)

        self.gridLayout.addWidget(self.groupKDC, 1, 0, 1, 1)

        self.groupNDStage = QGroupBox(self.groupConnections)
        self.groupNDStage.setObjectName("groupNDStage")
        self.ndGrid = QGridLayout(self.groupNDStage)
        self.ndGrid.setSpacing(8)
        self.ndGrid.setObjectName("ndGrid")
        self.ndGrid.setContentsMargins(5, 5, 5, 5)
        self.labelNDDevice = QLabel(self.groupNDStage)
        self.labelNDDevice.setObjectName("labelNDDevice")

        self.ndGrid.addWidget(self.labelNDDevice, 0, 0, 1, 1)

        self.valueNDDriver = QLabel(self.groupNDStage)
        self.valueNDDriver.setObjectName("valueNDDriver")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.valueNDDriver.sizePolicy().hasHeightForWidth())
        self.valueNDDriver.setSizePolicy(sizePolicy2)
        self.valueNDDriver.setMinimumSize(QSize(80, 0))

        self.ndGrid.addWidget(self.valueNDDriver, 3, 0, 1, 2)

        self.buttonHomeNDStage = QPushButton(self.groupNDStage)
        self.buttonHomeNDStage.setObjectName("buttonHomeNDStage")
        self.buttonHomeNDStage.setEnabled(False)

        self.ndGrid.addWidget(self.buttonHomeNDStage, 2, 0, 1, 2)

        self.valueNDStatus = QLabel(self.groupNDStage)
        self.valueNDStatus.setObjectName("valueNDStatus")
        sizePolicy2.setHeightForWidth(self.valueNDStatus.sizePolicy().hasHeightForWidth())
        self.valueNDStatus.setSizePolicy(sizePolicy2)
        self.valueNDStatus.setMinimumSize(QSize(80, 0))

        self.ndGrid.addWidget(self.valueNDStatus, 1, 0, 1, 2)

        self.buttonZeroNDStage = QPushButton(self.groupNDStage)
        self.buttonZeroNDStage.setObjectName("buttonZeroNDStage")
        self.buttonZeroNDStage.setEnabled(False)

        self.ndGrid.addWidget(self.buttonZeroNDStage, 2, 2, 1, 1)

        self.buttonConnectNDStage = QPushButton(self.groupNDStage)
        self.buttonConnectNDStage.setObjectName("buttonConnectNDStage")

        self.ndGrid.addWidget(self.buttonConnectNDStage, 1, 2, 1, 1)

        self.comboNDStage = QComboBox(self.groupNDStage)
        self.comboNDStage.setObjectName("comboNDStage")
        sizePolicy.setHeightForWidth(self.comboNDStage.sizePolicy().hasHeightForWidth())
        self.comboNDStage.setSizePolicy(sizePolicy)
        self.comboNDStage.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
        )
        self.comboNDStage.setMinimumContentsLength(14)

        self.ndGrid.addWidget(self.comboNDStage, 0, 1, 1, 1)

        self.buttonRefreshNDStage = QPushButton(self.groupNDStage)
        self.buttonRefreshNDStage.setObjectName("buttonRefreshNDStage")

        self.ndGrid.addWidget(self.buttonRefreshNDStage, 0, 2, 1, 1)

        self.ndJogLayout = QHBoxLayout()
        self.ndJogLayout.setSpacing(10)
        self.ndJogLayout.setObjectName("ndJogLayout")
        self.valueNDPosition = QLabel(self.groupNDStage)
        self.valueNDPosition.setObjectName("valueNDPosition")
        sizePolicy1.setHeightForWidth(self.valueNDPosition.sizePolicy().hasHeightForWidth())
        self.valueNDPosition.setSizePolicy(sizePolicy1)
        self.valueNDPosition.setMinimumSize(QSize(80, 0))

        self.ndJogLayout.addWidget(self.valueNDPosition)

        self.buttonNDJogMinus5 = QPushButton(self.groupNDStage)
        self.buttonNDJogMinus5.setObjectName("buttonNDJogMinus5")
        self.buttonNDJogMinus5.setEnabled(False)
        self.buttonNDJogMinus5.setMaximumSize(QSize(44, 30))

        self.ndJogLayout.addWidget(self.buttonNDJogMinus5)

        self.buttonNDJogMinus1 = QPushButton(self.groupNDStage)
        self.buttonNDJogMinus1.setObjectName("buttonNDJogMinus1")
        self.buttonNDJogMinus1.setEnabled(False)
        self.buttonNDJogMinus1.setMaximumSize(QSize(44, 30))

        self.ndJogLayout.addWidget(self.buttonNDJogMinus1)

        self.buttonNDJogPlus1 = QPushButton(self.groupNDStage)
        self.buttonNDJogPlus1.setObjectName("buttonNDJogPlus1")
        self.buttonNDJogPlus1.setEnabled(False)
        self.buttonNDJogPlus1.setMaximumSize(QSize(44, 30))

        self.ndJogLayout.addWidget(self.buttonNDJogPlus1)

        self.buttonNDJogPlus5 = QPushButton(self.groupNDStage)
        self.buttonNDJogPlus5.setObjectName("buttonNDJogPlus5")
        self.buttonNDJogPlus5.setEnabled(False)
        self.buttonNDJogPlus5.setMaximumSize(QSize(44, 30))

        self.ndJogLayout.addWidget(self.buttonNDJogPlus5)

        self.ndJogSpacer = QSpacerItem(
            20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.ndJogLayout.addItem(self.ndJogSpacer)

        self.buttonNDMotorOff = QPushButton(self.groupNDStage)
        self.buttonNDMotorOff.setObjectName("buttonNDMotorOff")
        self.buttonNDMotorOff.setEnabled(False)
        self.buttonNDMotorOff.setMaximumSize(QSize(80, 30))

        self.ndJogLayout.addWidget(self.buttonNDMotorOff)

        self.ndGrid.addLayout(self.ndJogLayout, 4, 0, 1, 3)

        self.buttonSelfTestNDStage = QPushButton(self.groupNDStage)
        self.buttonSelfTestNDStage.setObjectName("buttonSelfTestNDStage")
        self.buttonSelfTestNDStage.setEnabled(False)

        self.ndGrid.addWidget(self.buttonSelfTestNDStage, 3, 2, 1, 1)

        self.gridLayout.addWidget(self.groupNDStage, 0, 1, 2, 1)

        self.groupPM400 = QGroupBox(self.groupConnections)
        self.groupPM400.setObjectName("groupPM400")
        self.pmGrid = QGridLayout(self.groupPM400)
        self.pmGrid.setSpacing(8)
        self.pmGrid.setObjectName("pmGrid")
        self.pmGrid.setContentsMargins(5, 5, 5, 5)
        self.buttonRefreshPM400 = QPushButton(self.groupPM400)
        self.buttonRefreshPM400.setObjectName("buttonRefreshPM400")

        self.pmGrid.addWidget(self.buttonRefreshPM400, 0, 3, 1, 1)

        self.labelPMResource = QLabel(self.groupPM400)
        self.labelPMResource.setObjectName("labelPMResource")

        self.pmGrid.addWidget(self.labelPMResource, 0, 0, 1, 1)

        self.comboPM400 = QComboBox(self.groupPM400)
        self.comboPM400.setObjectName("comboPM400")
        sizePolicy.setHeightForWidth(self.comboPM400.sizePolicy().hasHeightForWidth())
        self.comboPM400.setSizePolicy(sizePolicy)
        self.comboPM400.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
        )
        self.comboPM400.setMinimumContentsLength(14)

        self.pmGrid.addWidget(self.comboPM400, 0, 1, 1, 2)

        self.buttonZeroPM400 = QPushButton(self.groupPM400)
        self.buttonZeroPM400.setObjectName("buttonZeroPM400")
        self.buttonZeroPM400.setEnabled(False)

        self.pmGrid.addWidget(self.buttonZeroPM400, 1, 3, 1, 1)

        self.buttonConnectPM400 = QPushButton(self.groupPM400)
        self.buttonConnectPM400.setObjectName("buttonConnectPM400")

        self.pmGrid.addWidget(self.buttonConnectPM400, 1, 2, 1, 1)

        self.valuePM400Status = QLabel(self.groupPM400)
        self.valuePM400Status.setObjectName("valuePM400Status")
        sizePolicy2.setHeightForWidth(self.valuePM400Status.sizePolicy().hasHeightForWidth())
        self.valuePM400Status.setSizePolicy(sizePolicy2)
        self.valuePM400Status.setMinimumSize(QSize(80, 0))

        self.pmGrid.addWidget(self.valuePM400Status, 1, 0, 1, 2)

        self.gridLayout.addWidget(self.groupPM400, 0, 2, 1, 1)

        self.groupPM400B = QGroupBox(self.groupConnections)
        self.groupPM400B.setObjectName("groupPM400B")
        self.pmBGrid = QGridLayout(self.groupPM400B)
        self.pmBGrid.setSpacing(8)
        self.pmBGrid.setObjectName("pmBGrid")
        self.pmBGrid.setContentsMargins(5, 5, 5, 5)
        self.buttonRefreshPM400B = QPushButton(self.groupPM400B)
        self.buttonRefreshPM400B.setObjectName("buttonRefreshPM400B")

        self.pmBGrid.addWidget(self.buttonRefreshPM400B, 0, 3, 1, 1)

        self.buttonZeroPM400B = QPushButton(self.groupPM400B)
        self.buttonZeroPM400B.setObjectName("buttonZeroPM400B")
        self.buttonZeroPM400B.setEnabled(False)

        self.pmBGrid.addWidget(self.buttonZeroPM400B, 1, 3, 1, 1)

        self.labelPM400BResource = QLabel(self.groupPM400B)
        self.labelPM400BResource.setObjectName("labelPM400BResource")

        self.pmBGrid.addWidget(self.labelPM400BResource, 0, 0, 1, 1)

        self.buttonConnectPM400B = QPushButton(self.groupPM400B)
        self.buttonConnectPM400B.setObjectName("buttonConnectPM400B")

        self.pmBGrid.addWidget(self.buttonConnectPM400B, 1, 2, 1, 1)

        self.valuePM400BStatus = QLabel(self.groupPM400B)
        self.valuePM400BStatus.setObjectName("valuePM400BStatus")
        sizePolicy2.setHeightForWidth(self.valuePM400BStatus.sizePolicy().hasHeightForWidth())
        self.valuePM400BStatus.setSizePolicy(sizePolicy2)
        self.valuePM400BStatus.setMinimumSize(QSize(80, 0))

        self.pmBGrid.addWidget(self.valuePM400BStatus, 1, 0, 1, 2)

        self.comboPM400B = QComboBox(self.groupPM400B)
        self.comboPM400B.setObjectName("comboPM400B")
        sizePolicy.setHeightForWidth(self.comboPM400B.sizePolicy().hasHeightForWidth())
        self.comboPM400B.setSizePolicy(sizePolicy)
        self.comboPM400B.setEditable(False)
        self.comboPM400B.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
        )
        self.comboPM400B.setMinimumContentsLength(14)

        self.pmBGrid.addWidget(self.comboPM400B, 0, 1, 1, 2)

        self.gridLayout.addWidget(self.groupPM400B, 1, 2, 1, 1)

        self.mainLayout.addWidget(self.groupConnections)

        self.workAreaLayout = QHBoxLayout()
        self.workAreaLayout.setSpacing(8)
        self.workAreaLayout.setObjectName("workAreaLayout")
        self.leftPanelLayout = QVBoxLayout()
        self.leftPanelLayout.setSpacing(5)
        self.leftPanelLayout.setObjectName("leftPanelLayout")
        self.tabMode = QTabWidget(AutoPowerCalibrationDialog)
        self.tabMode.setObjectName("tabMode")
        self.tabCalibration = QWidget()
        self.tabCalibration.setObjectName("tabCalibration")
        self.gridLayout_3 = QGridLayout(self.tabCalibration)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.tabCalibrationSpacer = QSpacerItem(
            20, 5, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.gridLayout_3.addItem(self.tabCalibrationSpacer, 6, 0, 1, 1)

        self.groupProfile = QGroupBox(self.tabCalibration)
        self.groupProfile.setObjectName("groupProfile")
        self.profileForm = QFormLayout(self.groupProfile)
        self.profileForm.setObjectName("profileForm")
        self.profileForm.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.profileForm.setVerticalSpacing(3)
        self.labelProfileName = QLabel(self.groupProfile)
        self.labelProfileName.setObjectName("labelProfileName")

        self.profileForm.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelProfileName)

        self.editProfileName = QLineEdit(self.groupProfile)
        self.editProfileName.setObjectName("editProfileName")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.editProfileName.sizePolicy().hasHeightForWidth())
        self.editProfileName.setSizePolicy(sizePolicy3)

        self.profileForm.setWidget(0, QFormLayout.ItemRole.FieldRole, self.editProfileName)

        self.valueOutputPath = QLabel(self.groupProfile)
        self.valueOutputPath.setObjectName("valueOutputPath")
        sizePolicy2.setHeightForWidth(self.valueOutputPath.sizePolicy().hasHeightForWidth())
        self.valueOutputPath.setSizePolicy(sizePolicy2)
        self.valueOutputPath.setMinimumSize(QSize(80, 48))
        self.valueOutputPath.setWordWrap(True)

        self.profileForm.setWidget(1, QFormLayout.ItemRole.SpanningRole, self.valueOutputPath)

        self.gridLayout_3.addWidget(self.groupProfile, 4, 0, 1, 1)

        self.groupSweep = QGroupBox(self.tabCalibration)
        self.groupSweep.setObjectName("groupSweep")
        self.sweepLayout = QVBoxLayout(self.groupSweep)
        self.sweepLayout.setSpacing(3)
        self.sweepLayout.setObjectName("sweepLayout")
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout_2.setVerticalSpacing(3)
        self.labelGainSettle = QLabel(self.groupSweep)
        self.labelGainSettle.setObjectName("labelGainSettle")

        self.gridLayout_2.addWidget(self.labelGainSettle, 2, 2, 1, 1)

        self.labelAngleEnd = QLabel(self.groupSweep)
        self.labelAngleEnd.setObjectName("labelAngleEnd")

        self.gridLayout_2.addWidget(self.labelAngleEnd, 0, 2, 1, 1)

        self.checkReturnPass = QCheckBox(self.groupSweep)
        self.checkReturnPass.setObjectName("checkReturnPass")

        self.gridLayout_2.addWidget(self.checkReturnPass, 3, 2, 1, 2)

        self.labelNPoints = QLabel(self.groupSweep)
        self.labelNPoints.setObjectName("labelNPoints")

        self.gridLayout_2.addWidget(self.labelNPoints, 1, 0, 1, 1)

        self.labelAngleStart = QLabel(self.groupSweep)
        self.labelAngleStart.setObjectName("labelAngleStart")

        self.gridLayout_2.addWidget(self.labelAngleStart, 0, 0, 1, 1)

        self.spinSaturationThreshold = QDoubleSpinBox(self.groupSweep)
        self.spinSaturationThreshold.setObjectName("spinSaturationThreshold")
        sizePolicy3.setHeightForWidth(self.spinSaturationThreshold.sizePolicy().hasHeightForWidth())
        self.spinSaturationThreshold.setSizePolicy(sizePolicy3)
        self.spinSaturationThreshold.setDecimals(2)
        self.spinSaturationThreshold.setMinimum(1.000000000000000)
        self.spinSaturationThreshold.setMaximum(3.300000000000000)
        self.spinSaturationThreshold.setSingleStep(0.050000000000000)
        self.spinSaturationThreshold.setValue(2.350000000000000)

        self.gridLayout_2.addWidget(self.spinSaturationThreshold, 1, 3, 1, 1)

        self.spinAngleStart = QDoubleSpinBox(self.groupSweep)
        self.spinAngleStart.setObjectName("spinAngleStart")
        sizePolicy3.setHeightForWidth(self.spinAngleStart.sizePolicy().hasHeightForWidth())
        self.spinAngleStart.setSizePolicy(sizePolicy3)
        self.spinAngleStart.setDecimals(1)
        self.spinAngleStart.setMinimum(0.000000000000000)
        self.spinAngleStart.setMaximum(360.000000000000000)
        self.spinAngleStart.setValue(0.000000000000000)

        self.gridLayout_2.addWidget(self.spinAngleStart, 0, 1, 1, 1)

        self.spinGainSettle = QDoubleSpinBox(self.groupSweep)
        self.spinGainSettle.setObjectName("spinGainSettle")
        sizePolicy3.setHeightForWidth(self.spinGainSettle.sizePolicy().hasHeightForWidth())
        self.spinGainSettle.setSizePolicy(sizePolicy3)
        self.spinGainSettle.setDecimals(2)
        self.spinGainSettle.setMinimum(0.000000000000000)
        self.spinGainSettle.setMaximum(10.000000000000000)
        self.spinGainSettle.setSingleStep(0.100000000000000)
        self.spinGainSettle.setValue(0.500000000000000)

        self.gridLayout_2.addWidget(self.spinGainSettle, 2, 3, 1, 1)

        self.spinNPoints = QSpinBox(self.groupSweep)
        self.spinNPoints.setObjectName("spinNPoints")
        sizePolicy3.setHeightForWidth(self.spinNPoints.sizePolicy().hasHeightForWidth())
        self.spinNPoints.setSizePolicy(sizePolicy3)
        self.spinNPoints.setMinimum(3)
        self.spinNPoints.setMaximum(200)
        self.spinNPoints.setValue(30)

        self.gridLayout_2.addWidget(self.spinNPoints, 1, 1, 1, 1)

        self.spinPointSettle = QDoubleSpinBox(self.groupSweep)
        self.spinPointSettle.setObjectName("spinPointSettle")
        sizePolicy3.setHeightForWidth(self.spinPointSettle.sizePolicy().hasHeightForWidth())
        self.spinPointSettle.setSizePolicy(sizePolicy3)
        self.spinPointSettle.setDecimals(2)
        self.spinPointSettle.setMinimum(0.000000000000000)
        self.spinPointSettle.setMaximum(30.000000000000000)
        self.spinPointSettle.setSingleStep(0.050000000000000)
        self.spinPointSettle.setValue(0.200000000000000)

        self.gridLayout_2.addWidget(self.spinPointSettle, 2, 1, 1, 1)

        self.spinAngleEnd = QDoubleSpinBox(self.groupSweep)
        self.spinAngleEnd.setObjectName("spinAngleEnd")
        sizePolicy3.setHeightForWidth(self.spinAngleEnd.sizePolicy().hasHeightForWidth())
        self.spinAngleEnd.setSizePolicy(sizePolicy3)
        self.spinAngleEnd.setDecimals(1)
        self.spinAngleEnd.setMinimum(0.000000000000000)
        self.spinAngleEnd.setMaximum(360.000000000000000)
        self.spinAngleEnd.setValue(90.000000000000000)

        self.gridLayout_2.addWidget(self.spinAngleEnd, 0, 3, 1, 1)

        self.spinDetectorSamples = QSpinBox(self.groupSweep)
        self.spinDetectorSamples.setObjectName("spinDetectorSamples")
        sizePolicy3.setHeightForWidth(self.spinDetectorSamples.sizePolicy().hasHeightForWidth())
        self.spinDetectorSamples.setSizePolicy(sizePolicy3)
        self.spinDetectorSamples.setMinimum(1)
        self.spinDetectorSamples.setMaximum(100)
        self.spinDetectorSamples.setValue(5)

        self.gridLayout_2.addWidget(self.spinDetectorSamples, 3, 1, 1, 1)

        self.labelPointSettle = QLabel(self.groupSweep)
        self.labelPointSettle.setObjectName("labelPointSettle")

        self.gridLayout_2.addWidget(self.labelPointSettle, 2, 0, 1, 1)

        self.labelDetectorSamples = QLabel(self.groupSweep)
        self.labelDetectorSamples.setObjectName("labelDetectorSamples")

        self.gridLayout_2.addWidget(self.labelDetectorSamples, 3, 0, 1, 1)

        self.labelSaturationThreshold = QLabel(self.groupSweep)
        self.labelSaturationThreshold.setObjectName("labelSaturationThreshold")

        self.gridLayout_2.addWidget(self.labelSaturationThreshold, 1, 2, 1, 1)

        self.sweepLayout.addLayout(self.gridLayout_2)

        self.gridModeLayout = QHBoxLayout()
        self.gridModeLayout.setSpacing(15)
        self.gridModeLayout.setObjectName("gridModeLayout")
        self.labelGridMode = QLabel(self.groupSweep)
        self.labelGridMode.setObjectName("labelGridMode")

        self.gridModeLayout.addWidget(self.labelGridMode)

        self.radioLinearAngle = QRadioButton(self.groupSweep)
        self.radioLinearAngle.setObjectName("radioLinearAngle")

        self.gridModeLayout.addWidget(self.radioLinearAngle)

        self.radioLinearCos2 = QRadioButton(self.groupSweep)
        self.radioLinearCos2.setObjectName("radioLinearCos2")
        self.radioLinearCos2.setChecked(True)

        self.gridModeLayout.addWidget(self.radioLinearCos2)

        self.horizontalSpacer_2 = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.gridModeLayout.addItem(self.horizontalSpacer_2)

        self.sweepLayout.addLayout(self.gridModeLayout)

        self.gainCheckboxLayout = QHBoxLayout()
        self.gainCheckboxLayout.setSpacing(15)
        self.gainCheckboxLayout.setObjectName("gainCheckboxLayout")
        self.labelGains = QLabel(self.groupSweep)
        self.labelGains.setObjectName("labelGains")

        self.gainCheckboxLayout.addWidget(self.labelGains)

        self.checkGain1 = QCheckBox(self.groupSweep)
        self.checkGain1.setObjectName("checkGain1")
        self.checkGain1.setChecked(True)

        self.gainCheckboxLayout.addWidget(self.checkGain1)

        self.checkGain2 = QCheckBox(self.groupSweep)
        self.checkGain2.setObjectName("checkGain2")
        self.checkGain2.setChecked(True)

        self.gainCheckboxLayout.addWidget(self.checkGain2)

        self.checkGain3 = QCheckBox(self.groupSweep)
        self.checkGain3.setObjectName("checkGain3")
        self.checkGain3.setChecked(True)

        self.gainCheckboxLayout.addWidget(self.checkGain3)

        self.checkGain4 = QCheckBox(self.groupSweep)
        self.checkGain4.setObjectName("checkGain4")
        self.checkGain4.setChecked(True)

        self.gainCheckboxLayout.addWidget(self.checkGain4)

        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.gainCheckboxLayout.addItem(self.horizontalSpacer)

        self.sweepLayout.addLayout(self.gainCheckboxLayout)

        self.gridLayout_3.addWidget(self.groupSweep, 2, 0, 1, 1)

        self.topControlsRow = QHBoxLayout()
        self.topControlsRow.setSpacing(5)
        self.topControlsRow.setObjectName("topControlsRow")
        self.groupAlignment = QGroupBox(self.tabCalibration)
        self.groupAlignment.setObjectName("groupAlignment")
        self.alignLayout = QVBoxLayout(self.groupAlignment)
        self.alignLayout.setSpacing(3)
        self.alignLayout.setObjectName("alignLayout")
        self.alignForm = QFormLayout()
        self.alignForm.setObjectName("alignForm")
        self.alignForm.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.alignForm.setVerticalSpacing(3)
        self.labelAlignStart = QLabel(self.groupAlignment)
        self.labelAlignStart.setObjectName("labelAlignStart")

        self.alignForm.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelAlignStart)

        self.spinAlignStart = QDoubleSpinBox(self.groupAlignment)
        self.spinAlignStart.setObjectName("spinAlignStart")
        sizePolicy3.setHeightForWidth(self.spinAlignStart.sizePolicy().hasHeightForWidth())
        self.spinAlignStart.setSizePolicy(sizePolicy3)
        self.spinAlignStart.setDecimals(1)
        self.spinAlignStart.setMinimum(0.000000000000000)
        self.spinAlignStart.setMaximum(360.000000000000000)
        self.spinAlignStart.setValue(0.000000000000000)

        self.alignForm.setWidget(0, QFormLayout.ItemRole.FieldRole, self.spinAlignStart)

        self.labelAlignEnd = QLabel(self.groupAlignment)
        self.labelAlignEnd.setObjectName("labelAlignEnd")

        self.alignForm.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelAlignEnd)

        self.spinAlignEnd = QDoubleSpinBox(self.groupAlignment)
        self.spinAlignEnd.setObjectName("spinAlignEnd")
        sizePolicy3.setHeightForWidth(self.spinAlignEnd.sizePolicy().hasHeightForWidth())
        self.spinAlignEnd.setSizePolicy(sizePolicy3)
        self.spinAlignEnd.setDecimals(1)
        self.spinAlignEnd.setMinimum(0.000000000000000)
        self.spinAlignEnd.setMaximum(360.000000000000000)
        self.spinAlignEnd.setValue(180.000000000000000)

        self.alignForm.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spinAlignEnd)

        self.labelAlignNPoints = QLabel(self.groupAlignment)
        self.labelAlignNPoints.setObjectName("labelAlignNPoints")

        self.alignForm.setWidget(2, QFormLayout.ItemRole.LabelRole, self.labelAlignNPoints)

        self.spinAlignNPoints = QSpinBox(self.groupAlignment)
        self.spinAlignNPoints.setObjectName("spinAlignNPoints")
        sizePolicy3.setHeightForWidth(self.spinAlignNPoints.sizePolicy().hasHeightForWidth())
        self.spinAlignNPoints.setSizePolicy(sizePolicy3)
        self.spinAlignNPoints.setMinimum(3)
        self.spinAlignNPoints.setMaximum(360)
        self.spinAlignNPoints.setValue(36)

        self.alignForm.setWidget(2, QFormLayout.ItemRole.FieldRole, self.spinAlignNPoints)

        self.labelAlignSettle = QLabel(self.groupAlignment)
        self.labelAlignSettle.setObjectName("labelAlignSettle")

        self.alignForm.setWidget(3, QFormLayout.ItemRole.LabelRole, self.labelAlignSettle)

        self.spinAlignSettle = QDoubleSpinBox(self.groupAlignment)
        self.spinAlignSettle.setObjectName("spinAlignSettle")
        sizePolicy3.setHeightForWidth(self.spinAlignSettle.sizePolicy().hasHeightForWidth())
        self.spinAlignSettle.setSizePolicy(sizePolicy3)
        self.spinAlignSettle.setDecimals(2)
        self.spinAlignSettle.setMinimum(0.000000000000000)
        self.spinAlignSettle.setMaximum(10.000000000000000)
        self.spinAlignSettle.setSingleStep(0.050000000000000)
        self.spinAlignSettle.setValue(0.200000000000000)

        self.alignForm.setWidget(3, QFormLayout.ItemRole.FieldRole, self.spinAlignSettle)

        self.alignLayout.addLayout(self.alignForm)

        self.alignButtonLayout = QHBoxLayout()
        self.alignButtonLayout.setSpacing(4)
        self.alignButtonLayout.setObjectName("alignButtonLayout")
        self.buttonAlignPolariser = QPushButton(self.groupAlignment)
        self.buttonAlignPolariser.setObjectName("buttonAlignPolariser")
        self.buttonAlignPolariser.setEnabled(False)

        self.alignButtonLayout.addWidget(self.buttonAlignPolariser)

        self.buttonAbortAlign = QPushButton(self.groupAlignment)
        self.buttonAbortAlign.setObjectName("buttonAbortAlign")
        self.buttonAbortAlign.setEnabled(False)

        self.alignButtonLayout.addWidget(self.buttonAbortAlign)

        self.alignLayout.addLayout(self.alignButtonLayout)

        self.valueAngleOffset = QLabel(self.groupAlignment)
        self.valueAngleOffset.setObjectName("valueAngleOffset")
        sizePolicy2.setHeightForWidth(self.valueAngleOffset.sizePolicy().hasHeightForWidth())
        self.valueAngleOffset.setSizePolicy(sizePolicy2)
        self.valueAngleOffset.setMinimumSize(QSize(80, 48))
        self.valueAngleOffset.setWordWrap(True)

        self.alignLayout.addWidget(self.valueAngleOffset)

        self.topControlsRow.addWidget(self.groupAlignment)

        self.groupBeam = QGroupBox(self.tabCalibration)
        self.groupBeam.setObjectName("groupBeam")
        self.beamForm = QFormLayout(self.groupBeam)
        self.beamForm.setObjectName("beamForm")
        self.beamForm.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.beamForm.setVerticalSpacing(3)
        self.labelWavelength = QLabel(self.groupBeam)
        self.labelWavelength.setObjectName("labelWavelength")

        self.beamForm.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelWavelength)

        self.spinWavelength = QDoubleSpinBox(self.groupBeam)
        self.spinWavelength.setObjectName("spinWavelength")
        sizePolicy3.setHeightForWidth(self.spinWavelength.sizePolicy().hasHeightForWidth())
        self.spinWavelength.setSizePolicy(sizePolicy3)
        self.spinWavelength.setDecimals(1)
        self.spinWavelength.setMinimum(200.000000000000000)
        self.spinWavelength.setMaximum(1100.000000000000000)
        self.spinWavelength.setValue(633.000000000000000)

        self.beamForm.setWidget(0, QFormLayout.ItemRole.FieldRole, self.spinWavelength)

        self.labelAttenuation = QLabel(self.groupBeam)
        self.labelAttenuation.setObjectName("labelAttenuation")

        self.beamForm.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelAttenuation)

        self.spinAttenuation = QDoubleSpinBox(self.groupBeam)
        self.spinAttenuation.setObjectName("spinAttenuation")
        sizePolicy3.setHeightForWidth(self.spinAttenuation.sizePolicy().hasHeightForWidth())
        self.spinAttenuation.setSizePolicy(sizePolicy3)
        self.spinAttenuation.setDecimals(5)
        self.spinAttenuation.setMinimum(-60.000000000000000)
        self.spinAttenuation.setMaximum(90.000000000000000)
        self.spinAttenuation.setSingleStep(0.100000000000000)
        self.spinAttenuation.setValue(3.000000000000000)

        self.beamForm.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spinAttenuation)

        self.labelPmAveraging = QLabel(self.groupBeam)
        self.labelPmAveraging.setObjectName("labelPmAveraging")

        self.beamForm.setWidget(2, QFormLayout.ItemRole.LabelRole, self.labelPmAveraging)

        self.spinPmAveraging = QSpinBox(self.groupBeam)
        self.spinPmAveraging.setObjectName("spinPmAveraging")
        sizePolicy3.setHeightForWidth(self.spinPmAveraging.sizePolicy().hasHeightForWidth())
        self.spinPmAveraging.setSizePolicy(sizePolicy3)
        self.spinPmAveraging.setMinimum(1)
        self.spinPmAveraging.setMaximum(300000)
        self.spinPmAveraging.setValue(100)

        self.beamForm.setWidget(2, QFormLayout.ItemRole.FieldRole, self.spinPmAveraging)

        self.topControlsRow.addWidget(self.groupBeam)

        self.gridLayout_3.addLayout(self.topControlsRow, 1, 0, 1, 1)

        self.groupPowerGrid = QGroupBox(self.tabCalibration)
        self.groupPowerGrid.setObjectName("groupPowerGrid")
        self.powerGridForm = QFormLayout(self.groupPowerGrid)
        self.powerGridForm.setObjectName("powerGridForm")
        self.powerGridForm.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.powerGridForm.setVerticalSpacing(3)
        self.labelPowerGridMode = QLabel(self.groupPowerGrid)
        self.labelPowerGridMode.setObjectName("labelPowerGridMode")

        self.powerGridForm.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelPowerGridMode)

        self.powerGridModeLayout = QHBoxLayout()
        self.powerGridModeLayout.setSpacing(6)
        self.powerGridModeLayout.setObjectName("powerGridModeLayout")
        self.radioGridLogPower = QRadioButton(self.groupPowerGrid)
        self.radioGridLogPower.setObjectName("radioGridLogPower")
        self.radioGridLogPower.setChecked(True)

        self.powerGridModeLayout.addWidget(self.radioGridLogPower)

        self.radioGridLinearPower = QRadioButton(self.groupPowerGrid)
        self.radioGridLinearPower.setObjectName("radioGridLinearPower")

        self.powerGridModeLayout.addWidget(self.radioGridLinearPower)

        self.powerGridForm.setLayout(0, QFormLayout.ItemRole.FieldRole, self.powerGridModeLayout)

        self.labelPowerTolerancePct = QLabel(self.groupPowerGrid)
        self.labelPowerTolerancePct.setObjectName("labelPowerTolerancePct")

        self.powerGridForm.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelPowerTolerancePct)

        self.spinPowerTolerancePct = QDoubleSpinBox(self.groupPowerGrid)
        self.spinPowerTolerancePct.setObjectName("spinPowerTolerancePct")
        sizePolicy3.setHeightForWidth(self.spinPowerTolerancePct.sizePolicy().hasHeightForWidth())
        self.spinPowerTolerancePct.setSizePolicy(sizePolicy3)
        self.spinPowerTolerancePct.setDecimals(1)
        self.spinPowerTolerancePct.setMinimum(0.100000000000000)
        self.spinPowerTolerancePct.setMaximum(50.000000000000000)
        self.spinPowerTolerancePct.setValue(5.000000000000000)

        self.powerGridForm.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spinPowerTolerancePct)

        self.labelMaxRefineSteps = QLabel(self.groupPowerGrid)
        self.labelMaxRefineSteps.setObjectName("labelMaxRefineSteps")

        self.powerGridForm.setWidget(2, QFormLayout.ItemRole.LabelRole, self.labelMaxRefineSteps)

        self.spinMaxRefineSteps = QSpinBox(self.groupPowerGrid)
        self.spinMaxRefineSteps.setObjectName("spinMaxRefineSteps")
        sizePolicy3.setHeightForWidth(self.spinMaxRefineSteps.sizePolicy().hasHeightForWidth())
        self.spinMaxRefineSteps.setSizePolicy(sizePolicy3)
        self.spinMaxRefineSteps.setMinimum(0)
        self.spinMaxRefineSteps.setMaximum(10)
        self.spinMaxRefineSteps.setValue(2)

        self.powerGridForm.setWidget(2, QFormLayout.ItemRole.FieldRole, self.spinMaxRefineSteps)

        self.checkPowerFromCurve = QCheckBox(self.groupPowerGrid)
        self.checkPowerFromCurve.setObjectName("checkPowerFromCurve")

        self.powerGridForm.setWidget(3, QFormLayout.ItemRole.SpanningRole, self.checkPowerFromCurve)

        self.gridLayout_3.addWidget(self.groupPowerGrid, 3, 0, 1, 1)

        self.groupIntensitySource = QGroupBox(self.tabCalibration)
        self.groupIntensitySource.setObjectName("groupIntensitySource")
        self.intensitySourceLayout = QHBoxLayout(self.groupIntensitySource)
        self.intensitySourceLayout.setSpacing(6)
        self.intensitySourceLayout.setObjectName("intensitySourceLayout")
        self.labelIntensitySource = QLabel(self.groupIntensitySource)
        self.labelIntensitySource.setObjectName("labelIntensitySource")

        self.intensitySourceLayout.addWidget(self.labelIntensitySource)

        self.radioSourcePolariser = QRadioButton(self.groupIntensitySource)
        self.radioSourcePolariser.setObjectName("radioSourcePolariser")
        self.radioSourcePolariser.setChecked(True)

        self.intensitySourceLayout.addWidget(self.radioSourcePolariser)

        self.radioSourceND = QRadioButton(self.groupIntensitySource)
        self.radioSourceND.setObjectName("radioSourceND")

        self.intensitySourceLayout.addWidget(self.radioSourceND)

        self.gridLayout_3.addWidget(self.groupIntensitySource, 0, 0, 1, 1)

        self.controlLayout = QHBoxLayout()
        self.controlLayout.setSpacing(6)
        self.controlLayout.setObjectName("controlLayout")
        self.buttonStart = QPushButton(self.tabCalibration)
        self.buttonStart.setObjectName("buttonStart")
        self.buttonStart.setEnabled(False)

        self.controlLayout.addWidget(self.buttonStart)

        self.buttonAbort = QPushButton(self.tabCalibration)
        self.buttonAbort.setObjectName("buttonAbort")
        self.buttonAbort.setEnabled(False)

        self.controlLayout.addWidget(self.buttonAbort)

        self.buttonSave = QPushButton(self.tabCalibration)
        self.buttonSave.setObjectName("buttonSave")
        self.buttonSave.setEnabled(False)

        self.controlLayout.addWidget(self.buttonSave)

        self.gridLayout_3.addLayout(self.controlLayout, 5, 0, 1, 1)

        self.calibrationPlot = MultiGainCalibrationPlot(self.tabCalibration)
        self.calibrationPlot.setObjectName("calibrationPlot")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(3)
        sizePolicy4.setHeightForWidth(self.calibrationPlot.sizePolicy().hasHeightForWidth())
        self.calibrationPlot.setSizePolicy(sizePolicy4)
        self.calibrationPlot.setMinimumSize(QSize(380, 250))

        self.gridLayout_3.addWidget(self.calibrationPlot, 0, 1, 7, 1)

        self.gridLayout_3.setColumnStretch(1, 1)
        self.tabMode.addTab(self.tabCalibration, "")
        self.tabNDRange = QWidget()
        self.tabNDRange.setObjectName("tabNDRange")
        self.gridLayout_4 = QGridLayout(self.tabNDRange)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.valueNDRange = QLabel(self.tabNDRange)
        self.valueNDRange.setObjectName("valueNDRange")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Minimum)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.valueNDRange.sizePolicy().hasHeightForWidth())
        self.valueNDRange.setSizePolicy(sizePolicy5)
        self.valueNDRange.setMinimumSize(QSize(80, 48))
        self.valueNDRange.setWordWrap(True)

        self.gridLayout_4.addWidget(self.valueNDRange, 2, 0, 1, 1)

        self.ndScanButtonLayout = QHBoxLayout()
        self.ndScanButtonLayout.setSpacing(6)
        self.ndScanButtonLayout.setObjectName("ndScanButtonLayout")
        self.buttonScanNDRange = QPushButton(self.tabNDRange)
        self.buttonScanNDRange.setObjectName("buttonScanNDRange")
        self.buttonScanNDRange.setEnabled(False)

        self.ndScanButtonLayout.addWidget(self.buttonScanNDRange)

        self.buttonAbortNDScan = QPushButton(self.tabNDRange)
        self.buttonAbortNDScan.setObjectName("buttonAbortNDScan")
        self.buttonAbortNDScan.setEnabled(False)

        self.ndScanButtonLayout.addWidget(self.buttonAbortNDScan)

        self.gridLayout_4.addLayout(self.ndScanButtonLayout, 1, 0, 1, 1)

        self.groupNDScanParams = QGroupBox(self.tabNDRange)
        self.groupNDScanParams.setObjectName("groupNDScanParams")
        sizePolicy1.setHeightForWidth(self.groupNDScanParams.sizePolicy().hasHeightForWidth())
        self.groupNDScanParams.setSizePolicy(sizePolicy1)
        self.ndScanForm = QFormLayout(self.groupNDScanParams)
        self.ndScanForm.setObjectName("ndScanForm")
        self.ndScanForm.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.ndScanForm.setVerticalSpacing(3)
        self.labelNDScanStart = QLabel(self.groupNDScanParams)
        self.labelNDScanStart.setObjectName("labelNDScanStart")

        self.ndScanForm.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelNDScanStart)

        self.spinNDScanStart = QDoubleSpinBox(self.groupNDScanParams)
        self.spinNDScanStart.setObjectName("spinNDScanStart")
        sizePolicy3.setHeightForWidth(self.spinNDScanStart.sizePolicy().hasHeightForWidth())
        self.spinNDScanStart.setSizePolicy(sizePolicy3)
        self.spinNDScanStart.setDecimals(1)
        self.spinNDScanStart.setMinimum(-360.000000000000000)
        self.spinNDScanStart.setMaximum(360.000000000000000)
        self.spinNDScanStart.setValue(0.000000000000000)

        self.ndScanForm.setWidget(0, QFormLayout.ItemRole.FieldRole, self.spinNDScanStart)

        self.labelNDScanEnd = QLabel(self.groupNDScanParams)
        self.labelNDScanEnd.setObjectName("labelNDScanEnd")

        self.ndScanForm.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelNDScanEnd)

        self.spinNDScanEnd = QDoubleSpinBox(self.groupNDScanParams)
        self.spinNDScanEnd.setObjectName("spinNDScanEnd")
        sizePolicy3.setHeightForWidth(self.spinNDScanEnd.sizePolicy().hasHeightForWidth())
        self.spinNDScanEnd.setSizePolicy(sizePolicy3)
        self.spinNDScanEnd.setDecimals(1)
        self.spinNDScanEnd.setMinimum(-360.000000000000000)
        self.spinNDScanEnd.setMaximum(360.000000000000000)
        self.spinNDScanEnd.setValue(360.000000000000000)

        self.ndScanForm.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spinNDScanEnd)

        self.labelNDScanPoints = QLabel(self.groupNDScanParams)
        self.labelNDScanPoints.setObjectName("labelNDScanPoints")

        self.ndScanForm.setWidget(2, QFormLayout.ItemRole.LabelRole, self.labelNDScanPoints)

        self.spinNDScanPoints = QSpinBox(self.groupNDScanParams)
        self.spinNDScanPoints.setObjectName("spinNDScanPoints")
        sizePolicy3.setHeightForWidth(self.spinNDScanPoints.sizePolicy().hasHeightForWidth())
        self.spinNDScanPoints.setSizePolicy(sizePolicy3)
        self.spinNDScanPoints.setMinimum(3)
        self.spinNDScanPoints.setMaximum(200)
        self.spinNDScanPoints.setValue(37)

        self.ndScanForm.setWidget(2, QFormLayout.ItemRole.FieldRole, self.spinNDScanPoints)

        self.labelNDScanSettle = QLabel(self.groupNDScanParams)
        self.labelNDScanSettle.setObjectName("labelNDScanSettle")

        self.ndScanForm.setWidget(3, QFormLayout.ItemRole.LabelRole, self.labelNDScanSettle)

        self.spinNDScanSettle = QDoubleSpinBox(self.groupNDScanParams)
        self.spinNDScanSettle.setObjectName("spinNDScanSettle")
        sizePolicy3.setHeightForWidth(self.spinNDScanSettle.sizePolicy().hasHeightForWidth())
        self.spinNDScanSettle.setSizePolicy(sizePolicy3)
        self.spinNDScanSettle.setDecimals(2)
        self.spinNDScanSettle.setMinimum(0.000000000000000)
        self.spinNDScanSettle.setMaximum(10.000000000000000)
        self.spinNDScanSettle.setSingleStep(0.050000000000000)
        self.spinNDScanSettle.setValue(0.200000000000000)

        self.ndScanForm.setWidget(3, QFormLayout.ItemRole.FieldRole, self.spinNDScanSettle)

        self.labelNDDarkFloor = QLabel(self.groupNDScanParams)
        self.labelNDDarkFloor.setObjectName("labelNDDarkFloor")

        self.ndScanForm.setWidget(4, QFormLayout.ItemRole.LabelRole, self.labelNDDarkFloor)

        self.spinNDDarkFloorUW = QDoubleSpinBox(self.groupNDScanParams)
        self.spinNDDarkFloorUW.setObjectName("spinNDDarkFloorUW")
        sizePolicy3.setHeightForWidth(self.spinNDDarkFloorUW.sizePolicy().hasHeightForWidth())
        self.spinNDDarkFloorUW.setSizePolicy(sizePolicy3)
        self.spinNDDarkFloorUW.setDecimals(4)
        self.spinNDDarkFloorUW.setMinimum(0.000000000000000)
        self.spinNDDarkFloorUW.setMaximum(1000.000000000000000)
        self.spinNDDarkFloorUW.setValue(0.000000000000000)

        self.ndScanForm.setWidget(4, QFormLayout.ItemRole.FieldRole, self.spinNDDarkFloorUW)

        self.labelNDScanSamples = QLabel(self.groupNDScanParams)
        self.labelNDScanSamples.setObjectName("labelNDScanSamples")

        self.ndScanForm.setWidget(5, QFormLayout.ItemRole.LabelRole, self.labelNDScanSamples)

        self.spinNDScanSamples = QSpinBox(self.groupNDScanParams)
        self.spinNDScanSamples.setObjectName("spinNDScanSamples")
        sizePolicy3.setHeightForWidth(self.spinNDScanSamples.sizePolicy().hasHeightForWidth())
        self.spinNDScanSamples.setSizePolicy(sizePolicy3)
        self.spinNDScanSamples.setMinimum(1)
        self.spinNDScanSamples.setMaximum(50)
        self.spinNDScanSamples.setValue(1)

        self.ndScanForm.setWidget(5, QFormLayout.ItemRole.FieldRole, self.spinNDScanSamples)

        self.gridLayout_4.addWidget(self.groupNDScanParams, 0, 0, 1, 1)

        self.ndRangePlot = NDTransmissionPlot(self.tabNDRange)
        self.ndRangePlot.setObjectName("ndRangePlot")
        sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(1)
        sizePolicy6.setHeightForWidth(self.ndRangePlot.sizePolicy().hasHeightForWidth())
        self.ndRangePlot.setSizePolicy(sizePolicy6)
        self.ndRangePlot.setMinimumSize(QSize(300, 200))

        self.gridLayout_4.addWidget(self.ndRangePlot, 0, 1, 2, 1)

        self.gridLayout_4.setColumnStretch(1, 1)
        self.tabMode.addTab(self.tabNDRange, "")
        self.tabNDLinearity = QWidget()
        self.tabNDLinearity.setObjectName("tabNDLinearity")
        self.gridLayout_5 = QGridLayout(self.tabNDLinearity)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.ndLinButtonLayout = QHBoxLayout()
        self.ndLinButtonLayout.setSpacing(6)
        self.ndLinButtonLayout.setObjectName("ndLinButtonLayout")
        self.buttonScanNDLin = QPushButton(self.tabNDLinearity)
        self.buttonScanNDLin.setObjectName("buttonScanNDLin")
        self.buttonScanNDLin.setEnabled(False)

        self.ndLinButtonLayout.addWidget(self.buttonScanNDLin)

        self.buttonAbortNDLin = QPushButton(self.tabNDLinearity)
        self.buttonAbortNDLin.setObjectName("buttonAbortNDLin")
        self.buttonAbortNDLin.setEnabled(False)

        self.ndLinButtonLayout.addWidget(self.buttonAbortNDLin)

        self.buttonClearNDLin = QPushButton(self.tabNDLinearity)
        self.buttonClearNDLin.setObjectName("buttonClearNDLin")
        self.buttonClearNDLin.setEnabled(False)

        self.ndLinButtonLayout.addWidget(self.buttonClearNDLin)

        self.ndLinButtonSpacer = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.ndLinButtonLayout.addItem(self.ndLinButtonSpacer)

        self.gridLayout_5.addLayout(self.ndLinButtonLayout, 1, 0, 1, 1)

        self.valueNDLinStatus = QLabel(self.tabNDLinearity)
        self.valueNDLinStatus.setObjectName("valueNDLinStatus")
        sizePolicy2.setHeightForWidth(self.valueNDLinStatus.sizePolicy().hasHeightForWidth())
        self.valueNDLinStatus.setSizePolicy(sizePolicy2)
        self.valueNDLinStatus.setMinimumSize(QSize(80, 34))
        self.valueNDLinStatus.setWordWrap(True)

        self.gridLayout_5.addWidget(self.valueNDLinStatus, 3, 0, 1, 1)

        self.groupNDLinParams = QGroupBox(self.tabNDLinearity)
        self.groupNDLinParams.setObjectName("groupNDLinParams")
        self.ndLinForm = QGridLayout(self.groupNDLinParams)
        self.ndLinForm.setObjectName("ndLinForm")
        self.ndLinForm.setVerticalSpacing(3)
        self.labelNDLinStart = QLabel(self.groupNDLinParams)
        self.labelNDLinStart.setObjectName("labelNDLinStart")

        self.ndLinForm.addWidget(self.labelNDLinStart, 0, 0, 1, 1)

        self.spinNDLinStart = QDoubleSpinBox(self.groupNDLinParams)
        self.spinNDLinStart.setObjectName("spinNDLinStart")
        sizePolicy3.setHeightForWidth(self.spinNDLinStart.sizePolicy().hasHeightForWidth())
        self.spinNDLinStart.setSizePolicy(sizePolicy3)
        self.spinNDLinStart.setDecimals(1)
        self.spinNDLinStart.setMinimum(-360.000000000000000)
        self.spinNDLinStart.setMaximum(360.000000000000000)
        self.spinNDLinStart.setValue(0.000000000000000)

        self.ndLinForm.addWidget(self.spinNDLinStart, 0, 1, 1, 1)

        self.labelNDLinScans = QLabel(self.groupNDLinParams)
        self.labelNDLinScans.setObjectName("labelNDLinScans")

        self.ndLinForm.addWidget(self.labelNDLinScans, 0, 2, 1, 1)

        self.spinNDLinScans = QSpinBox(self.groupNDLinParams)
        self.spinNDLinScans.setObjectName("spinNDLinScans")
        sizePolicy3.setHeightForWidth(self.spinNDLinScans.sizePolicy().hasHeightForWidth())
        self.spinNDLinScans.setSizePolicy(sizePolicy3)
        self.spinNDLinScans.setMinimum(1)
        self.spinNDLinScans.setMaximum(50)
        self.spinNDLinScans.setValue(3)

        self.ndLinForm.addWidget(self.spinNDLinScans, 0, 3, 1, 1)

        self.labelNDLinEnd = QLabel(self.groupNDLinParams)
        self.labelNDLinEnd.setObjectName("labelNDLinEnd")

        self.ndLinForm.addWidget(self.labelNDLinEnd, 1, 0, 1, 1)

        self.spinNDLinEnd = QDoubleSpinBox(self.groupNDLinParams)
        self.spinNDLinEnd.setObjectName("spinNDLinEnd")
        sizePolicy3.setHeightForWidth(self.spinNDLinEnd.sizePolicy().hasHeightForWidth())
        self.spinNDLinEnd.setSizePolicy(sizePolicy3)
        self.spinNDLinEnd.setDecimals(1)
        self.spinNDLinEnd.setMinimum(-360.000000000000000)
        self.spinNDLinEnd.setMaximum(360.000000000000000)
        self.spinNDLinEnd.setValue(360.000000000000000)

        self.ndLinForm.addWidget(self.spinNDLinEnd, 1, 1, 1, 1)

        self.checkNDLinAlternate = QCheckBox(self.groupNDLinParams)
        self.checkNDLinAlternate.setObjectName("checkNDLinAlternate")
        self.checkNDLinAlternate.setChecked(True)

        self.ndLinForm.addWidget(self.checkNDLinAlternate, 1, 2, 1, 2)

        self.labelNDLinPoints = QLabel(self.groupNDLinParams)
        self.labelNDLinPoints.setObjectName("labelNDLinPoints")

        self.ndLinForm.addWidget(self.labelNDLinPoints, 2, 0, 1, 1)

        self.spinNDLinPoints = QSpinBox(self.groupNDLinParams)
        self.spinNDLinPoints.setObjectName("spinNDLinPoints")
        sizePolicy3.setHeightForWidth(self.spinNDLinPoints.sizePolicy().hasHeightForWidth())
        self.spinNDLinPoints.setSizePolicy(sizePolicy3)
        self.spinNDLinPoints.setMinimum(3)
        self.spinNDLinPoints.setMaximum(500)
        self.spinNDLinPoints.setValue(37)

        self.ndLinForm.addWidget(self.spinNDLinPoints, 2, 1, 1, 1)

        self.labelNDLinFloor = QLabel(self.groupNDLinParams)
        self.labelNDLinFloor.setObjectName("labelNDLinFloor")

        self.ndLinForm.addWidget(self.labelNDLinFloor, 2, 2, 1, 1)

        self.spinNDLinFloorUW = QDoubleSpinBox(self.groupNDLinParams)
        self.spinNDLinFloorUW.setObjectName("spinNDLinFloorUW")
        sizePolicy3.setHeightForWidth(self.spinNDLinFloorUW.sizePolicy().hasHeightForWidth())
        self.spinNDLinFloorUW.setSizePolicy(sizePolicy3)
        self.spinNDLinFloorUW.setDecimals(4)
        self.spinNDLinFloorUW.setMinimum(0.000000000000000)
        self.spinNDLinFloorUW.setMaximum(1000.000000000000000)
        self.spinNDLinFloorUW.setValue(0.000000000000000)

        self.ndLinForm.addWidget(self.spinNDLinFloorUW, 2, 3, 1, 1)

        self.labelNDLinSettle = QLabel(self.groupNDLinParams)
        self.labelNDLinSettle.setObjectName("labelNDLinSettle")

        self.ndLinForm.addWidget(self.labelNDLinSettle, 3, 0, 1, 1)

        self.spinNDLinSettle = QDoubleSpinBox(self.groupNDLinParams)
        self.spinNDLinSettle.setObjectName("spinNDLinSettle")
        sizePolicy3.setHeightForWidth(self.spinNDLinSettle.sizePolicy().hasHeightForWidth())
        self.spinNDLinSettle.setSizePolicy(sizePolicy3)
        self.spinNDLinSettle.setDecimals(2)
        self.spinNDLinSettle.setMinimum(0.000000000000000)
        self.spinNDLinSettle.setMaximum(10.000000000000000)
        self.spinNDLinSettle.setSingleStep(0.050000000000000)
        self.spinNDLinSettle.setValue(0.200000000000000)

        self.ndLinForm.addWidget(self.spinNDLinSettle, 3, 1, 1, 1)

        self.labelNDLinTol = QLabel(self.groupNDLinParams)
        self.labelNDLinTol.setObjectName("labelNDLinTol")

        self.ndLinForm.addWidget(self.labelNDLinTol, 3, 2, 1, 1)

        self.spinNDLinTol = QDoubleSpinBox(self.groupNDLinParams)
        self.spinNDLinTol.setObjectName("spinNDLinTol")
        sizePolicy3.setHeightForWidth(self.spinNDLinTol.sizePolicy().hasHeightForWidth())
        self.spinNDLinTol.setSizePolicy(sizePolicy3)
        self.spinNDLinTol.setDecimals(3)
        self.spinNDLinTol.setMinimum(0.001000000000000)
        self.spinNDLinTol.setMaximum(5.000000000000000)
        self.spinNDLinTol.setSingleStep(0.005000000000000)
        self.spinNDLinTol.setValue(0.050000000000000)

        self.ndLinForm.addWidget(self.spinNDLinTol, 3, 3, 1, 1)

        self.labelNDLinSamples = QLabel(self.groupNDLinParams)
        self.labelNDLinSamples.setObjectName("labelNDLinSamples")

        self.ndLinForm.addWidget(self.labelNDLinSamples, 4, 0, 1, 1)

        self.spinNDLinSamples = QSpinBox(self.groupNDLinParams)
        self.spinNDLinSamples.setObjectName("spinNDLinSamples")
        sizePolicy3.setHeightForWidth(self.spinNDLinSamples.sizePolicy().hasHeightForWidth())
        self.spinNDLinSamples.setSizePolicy(sizePolicy3)
        self.spinNDLinSamples.setMinimum(1)
        self.spinNDLinSamples.setMaximum(50)
        self.spinNDLinSamples.setValue(1)

        self.ndLinForm.addWidget(self.spinNDLinSamples, 4, 1, 1, 1)

        self.gridLayout_5.addWidget(self.groupNDLinParams, 0, 0, 1, 1)

        self.editNDLinReport = QPlainTextEdit(self.tabNDLinearity)
        self.editNDLinReport.setObjectName("editNDLinReport")
        sizePolicy7 = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)
        sizePolicy7.setHorizontalStretch(0)
        sizePolicy7.setVerticalStretch(1)
        sizePolicy7.setHeightForWidth(self.editNDLinReport.sizePolicy().hasHeightForWidth())
        self.editNDLinReport.setSizePolicy(sizePolicy7)
        self.editNDLinReport.setMinimumSize(QSize(80, 90))
        font = QFont()
        font.setFamilies(["Menlo"])
        font.setPointSize(10)
        self.editNDLinReport.setFont(font)
        self.editNDLinReport.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.editNDLinReport.setReadOnly(True)

        self.gridLayout_5.addWidget(self.editNDLinReport, 4, 0, 1, 2)

        self.ndLinearityPlot = NDLinearityPlot(self.tabNDLinearity)
        self.ndLinearityPlot.setObjectName("ndLinearityPlot")
        sizePolicy4.setHeightForWidth(self.ndLinearityPlot.sizePolicy().hasHeightForWidth())
        self.ndLinearityPlot.setSizePolicy(sizePolicy4)
        self.ndLinearityPlot.setMinimumSize(QSize(300, 200))

        self.gridLayout_5.addWidget(self.ndLinearityPlot, 0, 1, 4, 1)

        self.gridLayout_5.setColumnStretch(1, 1)
        self.tabMode.addTab(self.tabNDLinearity, "")
        self.tabDetectorCompare = QWidget()
        self.tabDetectorCompare.setObjectName("tabDetectorCompare")
        self.gridLayout_6 = QGridLayout(self.tabDetectorCompare)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.valueXCheckResult = QLabel(self.tabDetectorCompare)
        self.valueXCheckResult.setObjectName("valueXCheckResult")
        sizePolicy2.setHeightForWidth(self.valueXCheckResult.sizePolicy().hasHeightForWidth())
        self.valueXCheckResult.setSizePolicy(sizePolicy2)
        self.valueXCheckResult.setMinimumSize(QSize(80, 48))
        self.valueXCheckResult.setWordWrap(True)

        self.gridLayout_6.addWidget(self.valueXCheckResult, 2, 0, 1, 1)

        self.xCheckButtonLayout = QHBoxLayout()
        self.xCheckButtonLayout.setSpacing(6)
        self.xCheckButtonLayout.setObjectName("xCheckButtonLayout")
        self.buttonStartXCheck = QPushButton(self.tabDetectorCompare)
        self.buttonStartXCheck.setObjectName("buttonStartXCheck")
        self.buttonStartXCheck.setEnabled(False)

        self.xCheckButtonLayout.addWidget(self.buttonStartXCheck)

        self.buttonAbortXCheck = QPushButton(self.tabDetectorCompare)
        self.buttonAbortXCheck.setObjectName("buttonAbortXCheck")
        self.buttonAbortXCheck.setEnabled(False)

        self.xCheckButtonLayout.addWidget(self.buttonAbortXCheck)

        self.buttonSaveXCheck = QPushButton(self.tabDetectorCompare)
        self.buttonSaveXCheck.setObjectName("buttonSaveXCheck")
        self.buttonSaveXCheck.setEnabled(False)

        self.xCheckButtonLayout.addWidget(self.buttonSaveXCheck)

        self.gridLayout_6.addLayout(self.xCheckButtonLayout, 1, 0, 1, 1)

        self.groupXCheckParams = QGroupBox(self.tabDetectorCompare)
        self.groupXCheckParams.setObjectName("groupXCheckParams")
        self.xCheckForm = QFormLayout(self.groupXCheckParams)
        self.xCheckForm.setObjectName("xCheckForm")
        self.xCheckForm.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.xCheckForm.setVerticalSpacing(3)
        self.labelXCheckPoints = QLabel(self.groupXCheckParams)
        self.labelXCheckPoints.setObjectName("labelXCheckPoints")

        self.xCheckForm.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelXCheckPoints)

        self.spinXCheckPoints = QSpinBox(self.groupXCheckParams)
        self.spinXCheckPoints.setObjectName("spinXCheckPoints")
        sizePolicy3.setHeightForWidth(self.spinXCheckPoints.sizePolicy().hasHeightForWidth())
        self.spinXCheckPoints.setSizePolicy(sizePolicy3)
        self.spinXCheckPoints.setMinimum(3)
        self.spinXCheckPoints.setMaximum(200)
        self.spinXCheckPoints.setValue(15)

        self.xCheckForm.setWidget(0, QFormLayout.ItemRole.FieldRole, self.spinXCheckPoints)

        self.labelXCheckSettle = QLabel(self.groupXCheckParams)
        self.labelXCheckSettle.setObjectName("labelXCheckSettle")

        self.xCheckForm.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelXCheckSettle)

        self.spinXCheckSettle = QDoubleSpinBox(self.groupXCheckParams)
        self.spinXCheckSettle.setObjectName("spinXCheckSettle")
        sizePolicy3.setHeightForWidth(self.spinXCheckSettle.sizePolicy().hasHeightForWidth())
        self.spinXCheckSettle.setSizePolicy(sizePolicy3)
        self.spinXCheckSettle.setDecimals(2)
        self.spinXCheckSettle.setMinimum(0.000000000000000)
        self.spinXCheckSettle.setMaximum(10.000000000000000)
        self.spinXCheckSettle.setSingleStep(0.050000000000000)
        self.spinXCheckSettle.setValue(0.200000000000000)

        self.xCheckForm.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spinXCheckSettle)

        self.labelXCheckTolerance = QLabel(self.groupXCheckParams)
        self.labelXCheckTolerance.setObjectName("labelXCheckTolerance")

        self.xCheckForm.setWidget(2, QFormLayout.ItemRole.LabelRole, self.labelXCheckTolerance)

        self.spinXCheckTolerance = QDoubleSpinBox(self.groupXCheckParams)
        self.spinXCheckTolerance.setObjectName("spinXCheckTolerance")
        sizePolicy3.setHeightForWidth(self.spinXCheckTolerance.sizePolicy().hasHeightForWidth())
        self.spinXCheckTolerance.setSizePolicy(sizePolicy3)
        self.spinXCheckTolerance.setDecimals(1)
        self.spinXCheckTolerance.setMinimum(0.100000000000000)
        self.spinXCheckTolerance.setMaximum(50.000000000000000)
        self.spinXCheckTolerance.setValue(5.000000000000000)

        self.xCheckForm.setWidget(2, QFormLayout.ItemRole.FieldRole, self.spinXCheckTolerance)

        self.gridLayout_6.addWidget(self.groupXCheckParams, 0, 0, 1, 1)

        self.xCheckPlot = DetectorComparisonPlot(self.tabDetectorCompare)
        self.xCheckPlot.setObjectName("xCheckPlot")
        sizePolicy6.setHeightForWidth(self.xCheckPlot.sizePolicy().hasHeightForWidth())
        self.xCheckPlot.setSizePolicy(sizePolicy6)
        self.xCheckPlot.setMinimumSize(QSize(300, 200))

        self.gridLayout_6.addWidget(self.xCheckPlot, 0, 1, 3, 1)

        self.gridLayout_6.setColumnStretch(1, 1)
        self.tabMode.addTab(self.tabDetectorCompare, "")
        self.tabGainVerify = QWidget()
        self.tabGainVerify.setObjectName("tabGainVerify")
        self.gridLayout_7 = QGridLayout(self.tabGainVerify)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.groupVerifyParams = QGroupBox(self.tabGainVerify)
        self.groupVerifyParams.setObjectName("groupVerifyParams")
        self.verifyForm = QFormLayout(self.groupVerifyParams)
        self.verifyForm.setObjectName("verifyForm")
        self.verifyForm.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.verifyForm.setVerticalSpacing(3)
        self.labelVerifyLevels = QLabel(self.groupVerifyParams)
        self.labelVerifyLevels.setObjectName("labelVerifyLevels")

        self.verifyForm.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelVerifyLevels)

        self.spinVerifyLevels = QSpinBox(self.groupVerifyParams)
        self.spinVerifyLevels.setObjectName("spinVerifyLevels")
        sizePolicy3.setHeightForWidth(self.spinVerifyLevels.sizePolicy().hasHeightForWidth())
        self.spinVerifyLevels.setSizePolicy(sizePolicy3)
        self.spinVerifyLevels.setMinimum(1)
        self.spinVerifyLevels.setMaximum(20)
        self.spinVerifyLevels.setValue(3)

        self.verifyForm.setWidget(0, QFormLayout.ItemRole.FieldRole, self.spinVerifyLevels)

        self.labelVerifySettle = QLabel(self.groupVerifyParams)
        self.labelVerifySettle.setObjectName("labelVerifySettle")

        self.verifyForm.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelVerifySettle)

        self.spinVerifySettle = QDoubleSpinBox(self.groupVerifyParams)
        self.spinVerifySettle.setObjectName("spinVerifySettle")
        sizePolicy3.setHeightForWidth(self.spinVerifySettle.sizePolicy().hasHeightForWidth())
        self.spinVerifySettle.setSizePolicy(sizePolicy3)
        self.spinVerifySettle.setDecimals(2)
        self.spinVerifySettle.setMinimum(0.000000000000000)
        self.spinVerifySettle.setMaximum(10.000000000000000)
        self.spinVerifySettle.setSingleStep(0.050000000000000)
        self.spinVerifySettle.setValue(0.300000000000000)

        self.verifyForm.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spinVerifySettle)

        self.labelVerifyTolerancePct = QLabel(self.groupVerifyParams)
        self.labelVerifyTolerancePct.setObjectName("labelVerifyTolerancePct")

        self.verifyForm.setWidget(2, QFormLayout.ItemRole.LabelRole, self.labelVerifyTolerancePct)

        self.spinVerifyTolerancePct = QDoubleSpinBox(self.groupVerifyParams)
        self.spinVerifyTolerancePct.setObjectName("spinVerifyTolerancePct")
        sizePolicy3.setHeightForWidth(self.spinVerifyTolerancePct.sizePolicy().hasHeightForWidth())
        self.spinVerifyTolerancePct.setSizePolicy(sizePolicy3)
        self.spinVerifyTolerancePct.setDecimals(1)
        self.spinVerifyTolerancePct.setMinimum(0.100000000000000)
        self.spinVerifyTolerancePct.setMaximum(50.000000000000000)
        self.spinVerifyTolerancePct.setValue(5.000000000000000)

        self.verifyForm.setWidget(2, QFormLayout.ItemRole.FieldRole, self.spinVerifyTolerancePct)

        self.checkVerifyFromCurve = QCheckBox(self.groupVerifyParams)
        self.checkVerifyFromCurve.setObjectName("checkVerifyFromCurve")

        self.verifyForm.setWidget(3, QFormLayout.ItemRole.SpanningRole, self.checkVerifyFromCurve)

        self.gridLayout_7.addWidget(self.groupVerifyParams, 0, 0, 1, 1)

        self.verifyButtonLayout = QHBoxLayout()
        self.verifyButtonLayout.setSpacing(6)
        self.verifyButtonLayout.setObjectName("verifyButtonLayout")
        self.buttonStartVerify = QPushButton(self.tabGainVerify)
        self.buttonStartVerify.setObjectName("buttonStartVerify")
        self.buttonStartVerify.setEnabled(False)

        self.verifyButtonLayout.addWidget(self.buttonStartVerify)

        self.buttonAbortVerify = QPushButton(self.tabGainVerify)
        self.buttonAbortVerify.setObjectName("buttonAbortVerify")
        self.buttonAbortVerify.setEnabled(False)

        self.verifyButtonLayout.addWidget(self.buttonAbortVerify)

        self.gridLayout_7.addLayout(self.verifyButtonLayout, 1, 0, 1, 1)

        self.tableGainVerify = QTableWidget(self.tabGainVerify)
        if self.tableGainVerify.columnCount() < 6:
            self.tableGainVerify.setColumnCount(6)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableGainVerify.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableGainVerify.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tableGainVerify.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tableGainVerify.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tableGainVerify.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.tableGainVerify.setHorizontalHeaderItem(5, __qtablewidgetitem5)
        self.tableGainVerify.setObjectName("tableGainVerify")
        sizePolicy6.setHeightForWidth(self.tableGainVerify.sizePolicy().hasHeightForWidth())
        self.tableGainVerify.setSizePolicy(sizePolicy6)
        self.tableGainVerify.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.gridLayout_7.addWidget(self.tableGainVerify, 2, 0, 1, 1)

        self.valueVerifyResult = QLabel(self.tabGainVerify)
        self.valueVerifyResult.setObjectName("valueVerifyResult")
        sizePolicy2.setHeightForWidth(self.valueVerifyResult.sizePolicy().hasHeightForWidth())
        self.valueVerifyResult.setSizePolicy(sizePolicy2)
        self.valueVerifyResult.setMinimumSize(QSize(80, 48))
        self.valueVerifyResult.setWordWrap(True)

        self.gridLayout_7.addWidget(self.valueVerifyResult, 3, 0, 1, 1)

        self.tabMode.addTab(self.tabGainVerify, "")

        self.leftPanelLayout.addWidget(self.tabMode)

        self.progressBar = QProgressBar(AutoPowerCalibrationDialog)
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setValue(0)
        self.progressBar.setTextVisible(True)

        self.leftPanelLayout.addWidget(self.progressBar)

        self.valuePhase = QLabel(AutoPowerCalibrationDialog)
        self.valuePhase.setObjectName("valuePhase")
        sizePolicy2.setHeightForWidth(self.valuePhase.sizePolicy().hasHeightForWidth())
        self.valuePhase.setSizePolicy(sizePolicy2)
        self.valuePhase.setMinimumSize(QSize(80, 0))

        self.leftPanelLayout.addWidget(self.valuePhase)

        self.workAreaLayout.addLayout(self.leftPanelLayout)

        self.mainLayout.addLayout(self.workAreaLayout)

        self.editLog = QPlainTextEdit(AutoPowerCalibrationDialog)
        self.editLog.setObjectName("editLog")
        sizePolicy8 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy8.setHorizontalStretch(0)
        sizePolicy8.setVerticalStretch(1)
        sizePolicy8.setHeightForWidth(self.editLog.sizePolicy().hasHeightForWidth())
        self.editLog.setSizePolicy(sizePolicy8)
        self.editLog.setMaximumSize(QSize(16777215, 150))
        self.editLog.setReadOnly(True)

        self.mainLayout.addWidget(self.editLog)

        self.retranslateUi(AutoPowerCalibrationDialog)

        self.tabMode.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(AutoPowerCalibrationDialog)

    # setupUi

    def retranslateUi(self, AutoPowerCalibrationDialog):
        AutoPowerCalibrationDialog.setWindowTitle(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog", "Automatische Leistungskalibrierung", None
            )
        )
        self.groupConnections.setTitle(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Verbindungen", None)
        )
        self.groupArduino.setTitle(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog", "Arduino (Detektor & Gain)", None
            )
        )
        self.labelArduinoPort.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Port:", None)
        )
        self.buttonRefreshArduino.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Aktualisieren", None)
        )
        self.valueArduinoStatus.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Nicht verbunden", None)
        )
        self.buttonConnectArduino.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Verbinden", None)
        )
        self.groupKDC.setTitle(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog", "KDC101 Rotationsantrieb (PRM1/MZ8)", None
            )
        )
        self.buttonHomeKDC.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Referenzfahrt (Home)", None)
        )
        self.labelKDCDevice.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Ger\u00e4t:", None)
        )
        self.buttonConnectKDC.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Verbinden", None)
        )
        self.buttonRefreshKDC.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Aktualisieren", None)
        )
        self.valueKDCStatus.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Nicht verbunden", None)
        )
        self.groupNDStage.setTitle(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog",
                "ND-Filter Drehantrieb (Schrittmotor, ESP32 + DRV8825)",
                None,
            )
        )
        self.labelNDDevice.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Port:", None)
        )
        self.valueNDDriver.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Treiber: \u2013", None)
        )
        # if QT_CONFIG(tooltip)
        self.buttonHomeNDStage.setToolTip(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog",
                "F\u00e4hrt den Referenzschalter an und setzt dort 0\u00b0. Ohne Referenzschalter (Firmware: PIN_HOME = -1) wird 0\u00b0 an der aktuellen Position gesetzt.",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonHomeNDStage.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Referenzfahrt (Home)", None)
        )
        self.valueNDStatus.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Nicht verbunden", None)
        )
        # if QT_CONFIG(tooltip)
        self.buttonZeroNDStage.setToolTip(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog",
                "Setzt die aktuelle Position des Filterrads als 0\u00b0 (klare Stelle des Filters), ohne zu fahren.",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonZeroNDStage.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Nullpunkt hier setzen", None)
        )
        self.buttonConnectNDStage.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Verbinden", None)
        )
        self.buttonRefreshNDStage.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Aktualisieren", None)
        )
        self.valueNDPosition.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Winkel: \u2013 \u00b0", None)
        )
        # if QT_CONFIG(tooltip)
        self.buttonNDJogMinus5.setToolTip(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog",
                "Filterrad um 5\u00b0 zur\u00fcckdrehen (Handjustage des Nullpunkts).",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonNDJogMinus5.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "\u22125\u00b0", None)
        )
        # if QT_CONFIG(tooltip)
        self.buttonNDJogMinus1.setToolTip(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog",
                "Filterrad um 1\u00b0 zur\u00fcckdrehen (Handjustage des Nullpunkts).",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonNDJogMinus1.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "\u22121\u00b0", None)
        )
        # if QT_CONFIG(tooltip)
        self.buttonNDJogPlus1.setToolTip(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog",
                "Filterrad um 1\u00b0 vordrehen (Handjustage des Nullpunkts).",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonNDJogPlus1.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "+1\u00b0", None)
        )
        # if QT_CONFIG(tooltip)
        self.buttonNDJogPlus5.setToolTip(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog",
                "Filterrad um 5\u00b0 vordrehen (Handjustage des Nullpunkts).",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonNDJogPlus5.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "+5\u00b0", None)
        )
        # if QT_CONFIG(tooltip)
        self.buttonNDMotorOff.setToolTip(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog",
                "Gibt den Motor frei (kein Haltestrom), damit das Rad von Hand gedreht werden kann. Die n\u00e4chste Fahrt schaltet den Motor automatisch wieder ein. Danach \u201eNullpunkt hier setzen\u201c.",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonNDMotorOff.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Motor aus", None)
        )
        # if QT_CONFIG(tooltip)
        self.buttonSelfTestNDStage.setToolTip(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog",
                "F\u00e4hrt das Filterrad kurz hin und zur\u00fcck und pr\u00fcft dabei den /FAULT-Pin des DRV8825 (\u00dcberstrom/\u00dcbertemperatur).",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonSelfTestNDStage.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Treiber testen", None)
        )
        self.groupPM400.setTitle(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog", "PM400 A (Referenz, S120C)", None
            )
        )
        self.buttonRefreshPM400.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Aktualisieren", None)
        )
        self.labelPMResource.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "VISA:", None)
        )
        self.buttonZeroPM400.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Nullabgleich (Zero)", None)
        )
        self.buttonConnectPM400.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Verbinden", None)
        )
        self.valuePM400Status.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Nicht verbunden", None)
        )
        self.groupPM400B.setTitle(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog", "PM400 B (Vergleichsmessger\u00e4t)", None
            )
        )
        self.buttonRefreshPM400B.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Aktualisieren", None)
        )
        self.buttonZeroPM400B.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Nullabgleich (Zero)", None)
        )
        self.labelPM400BResource.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "VISA:", None)
        )
        self.buttonConnectPM400B.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Verbinden", None)
        )
        self.valuePM400BStatus.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Nicht verbunden", None)
        )
        self.groupProfile.setTitle(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Profil", None)
        )
        self.labelProfileName.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Profilname:", None)
        )
        self.editProfileName.setPlaceholderText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "z.B. Det-A_auto", None)
        )
        self.valueOutputPath.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "\u2013", None)
        )
        self.groupSweep.setTitle(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Sweep-Einstellungen", None)
        )
        self.labelGainSettle.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Wartezeit / Gain (s):", None)
        )
        self.labelAngleEnd.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Endwinkel (\u00b0):", None)
        )
        # if QT_CONFIG(tooltip)
        self.checkReturnPass.setToolTip(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog",
                "Misst nach dem Hin-Durchlauf jedes Gains dieselben Positionen in umgekehrter Reihenfolge noch einmal. Das Log vergleicht die angepassten W/V-Faktoren von Hin- und R\u00fcckfahrt (Hysterese/Drift); beide Durchl\u00e4ufe gehen ins Profil ein.",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.checkReturnPass.setText(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog", "R\u00fcckfahrt (R\u00fcckw\u00e4rts-Durchlauf)", None
            )
        )
        self.labelNPoints.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Anzahl Punkte:", None)
        )
        self.labelAngleStart.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Startwinkel (\u00b0):", None)
        )
        # if QT_CONFIG(tooltip)
        self.spinSaturationThreshold.setToolTip(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog",
                "ADC-Spannung ab der ein Messpunkt als ges\u00e4ttigt gilt und nicht aufgezeichnet wird. Typisch ~2.35 V (ADS1220 Vollaussteuerung \u22482.4 V).",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.labelPointSettle.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Wartezeit / Punkt (s):", None)
        )
        self.labelDetectorSamples.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Detektor-Samples:", None)
        )
        self.labelSaturationThreshold.setText(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog", "S\u00e4ttigungsschwelle (V):", None
            )
        )
        self.labelGridMode.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Winkelraster:", None)
        )
        self.radioLinearAngle.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Linear in \u03b8", None)
        )
        self.radioLinearCos2.setText(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog", "Linear in cos\u00b2(\u03b8)", None
            )
        )
        self.labelGains.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Gain-Stufen:", None)
        )
        self.checkGain1.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", "1", None))
        self.checkGain2.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", "2", None))
        self.checkGain3.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", "3", None))
        self.checkGain4.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", "4", None))
        self.groupAlignment.setTitle(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog", "Polarisator-Ausrichtung", None
            )
        )
        self.labelAlignStart.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Scanstart (\u00b0):", None)
        )
        # if QT_CONFIG(tooltip)
        self.spinAlignStart.setToolTip(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog",
                "Startwinkel des Ausrichtungsscans (physikalische Stufenposition)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.labelAlignEnd.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Scanende (\u00b0):", None)
        )
        # if QT_CONFIG(tooltip)
        self.spinAlignEnd.setToolTip(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog",
                "Endwinkel des Ausrichtungsscans. 180\u00b0 deckt eine volle cos\u00b2-Periode ab.",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.labelAlignNPoints.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Schritte:", None)
        )
        # if QT_CONFIG(tooltip)
        self.spinAlignNPoints.setToolTip(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog",
                "Anzahl Messpunkte im Ausrichtungsscan (empfohlen: \u226536 f\u00fcr 5\u00b0-Aufl\u00f6sung \u00fcber 180\u00b0)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.labelAlignSettle.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Wartezeit (s):", None)
        )
        self.buttonAlignPolariser.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Ausrichtung starten", None)
        )
        self.buttonAbortAlign.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Abbrechen", None)
        )
        self.valueAngleOffset.setText(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog", "Winkelversatz: nicht gesetzt", None
            )
        )
        self.groupBeam.setTitle(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog", "Licht / Leistungsmessung", None
            )
        )
        self.labelWavelength.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Wellenl\u00e4nge (nm):", None)
        )
        self.labelAttenuation.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "ST D\u00e4mpfung (dB):", None)
        )
        # if QT_CONFIG(tooltip)
        self.spinAttenuation.setToolTip(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog",
                "D\u00e4mpfung des Strahlteilers in dB. Wird direkt an das PM400 \u00fcbergeben.",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.labelPmAveraging.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "PM400 Mittelwerte:", None)
        )
        self.groupPowerGrid.setTitle(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog", "Leistungsraster (nur ND-Filter)", None
            )
        )
        self.labelPowerGridMode.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Rastermodus:", None)
        )
        self.radioGridLogPower.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Log", None)
        )
        self.radioGridLinearPower.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Linear", None)
        )
        self.labelPowerTolerancePct.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Toleranz (%):", None)
        )
        # if QT_CONFIG(tooltip)
        self.spinPowerTolerancePct.setToolTip(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog",
                "Maximal erlaubte Abweichung der erreichten von der Ziel-Leistung, bevor die Position per Bisektion nachjustiert wird.",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.labelMaxRefineSteps.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Max. Nachjustierungen:", None)
        )
        # if QT_CONFIG(tooltip)
        self.checkPowerFromCurve.setToolTip(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog",
                "Die Leistung jedes Punkts wird aus der ND-Kennlinie des Bereichsscans dieser Sitzung genommen, der PM400 wird nicht gelesen und darf au\u00dferhalb des Strahls stehen. Keine Nachjustierung. Die Genauigkeit h\u00e4ngt von der Kennlinie ab: Bereichsscan mit vielen Punkten und Mittelung messen, Nullpunkt danach nicht mehr \u00e4ndern.",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.checkPowerFromCurve.setText(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog",
                "Leistung aus ND-Kennlinie (PM400 nicht im Strahl)",
                None,
            )
        )
        self.groupIntensitySource.setTitle(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Intensit\u00e4tsquelle", None)
        )
        self.labelIntensitySource.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Quelle:", None)
        )
        self.radioSourcePolariser.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Polarisator", None)
        )
        self.radioSourceND.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "ND-Filter", None)
        )
        self.buttonStart.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Starten", None)
        )
        self.buttonAbort.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Abbrechen", None)
        )
        self.buttonSave.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Profil speichern", None)
        )
        self.tabMode.setTabText(
            self.tabMode.indexOf(self.tabCalibration),
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Kalibrierung", None),
        )
        self.valueNDRange.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Bereich: \u2013", None)
        )
        self.buttonScanNDRange.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Bereichsscan starten", None)
        )
        self.buttonAbortNDScan.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Abbrechen", None)
        )
        self.groupNDScanParams.setTitle(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Scan-Parameter", None)
        )
        self.labelNDScanStart.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Start (\u00b0):", None)
        )
        self.labelNDScanEnd.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Ende (\u00b0):", None)
        )
        self.labelNDScanPoints.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Punkte:", None)
        )
        self.labelNDScanSettle.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Wartezeit (s):", None)
        )
        self.labelNDDarkFloor.setText(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog", "Dunkel-Schwelle (\u00b5W):", None
            )
        )
        # if QT_CONFIG(tooltip)
        self.spinNDDarkFloorUW.setToolTip(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog",
                "Optional: Leistung, unterhalb derer das Dunkelende als erreicht gilt (vermeidet Parken im Rauschen). 0 = deaktiviert, verwendet stattdessen das Minimum des Scans.",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.labelNDScanSamples.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Mittelungen/Punkt:", None)
        )
        # if QT_CONFIG(tooltip)
        self.spinNDScanSamples.setToolTip(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog",
                "Anzahl PM400-Messungen, die pro Winkel gemittelt werden (reduziert Rauschen, verl\u00e4ngert den Scan).",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.tabMode.setTabText(
            self.tabMode.indexOf(self.tabNDRange),
            QCoreApplication.translate("AutoPowerCalibrationDialog", "ND-Bereich", None),
        )
        # if QT_CONFIG(tooltip)
        self.buttonScanNDLin.setToolTip(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog",
                "Misst die konfigurierte Anzahl Scans und h\u00e4ngt sie an die vorhandenen an, damit mehrere L\u00e4ufe (z. B. nach Umbau) verglichen werden k\u00f6nnen.",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonScanNDLin.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Scans starten", None)
        )
        self.buttonAbortNDLin.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Abbrechen", None)
        )
        self.buttonClearNDLin.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Scans verwerfen", None)
        )
        self.valueNDLinStatus.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Status: \u2013", None)
        )
        self.groupNDLinParams.setTitle(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Scan-Parameter", None)
        )
        self.labelNDLinStart.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Start (\u00b0):", None)
        )
        self.labelNDLinScans.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Anzahl Scans:", None)
        )
        # if QT_CONFIG(tooltip)
        self.spinNDLinScans.setToolTip(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog", "Wie viele Scans nacheinander gemessen werden.", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.labelNDLinEnd.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Ende (\u00b0):", None)
        )
        # if QT_CONFIG(tooltip)
        self.checkNDLinAlternate.setToolTip(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog",
                "Jeder zweite Scan l\u00e4uft r\u00fcckw\u00e4rts. Der Versatz zwischen vorw\u00e4rts und r\u00fcckw\u00e4rts misst Hysterese / Getriebespiel.",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.checkNDLinAlternate.setText(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog", "Richtung abwechseln (Hysterese)", None
            )
        )
        self.labelNDLinPoints.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Punkte:", None)
        )
        self.labelNDLinFloor.setText(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog", "Rausch-Schwelle (\u00b5W):", None
            )
        )
        # if QT_CONFIG(tooltip)
        self.spinNDLinFloorUW.setToolTip(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog",
                "Messpunkte mit Leistung unterhalb dieser Schwelle werden nicht in den Fit einbezogen. 0 = nur Leistung > 0.",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.labelNDLinSettle.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Wartezeit (s):", None)
        )
        self.labelNDLinTol.setText(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog", "Toleranz max. Abw. (OD):", None
            )
        )
        # if QT_CONFIG(tooltip)
        self.spinNDLinTol.setToolTip(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog",
                "Ein Scan gilt als linear, wenn die gr\u00f6\u00dfte Abweichung vom Geraden-Fit des OD diese Schwelle nicht \u00fcberschreitet. 0,05 OD \u2248 12 % Transmission.",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.labelNDLinSamples.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Mittelungen/Punkt:", None)
        )
        self.editNDLinReport.setPlaceholderText(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog",
                "Noch keine Scans. Der Bericht vergleicht Linearit\u00e4t, Streuung und Hysterese.",
                None,
            )
        )
        self.tabMode.setTabText(
            self.tabMode.indexOf(self.tabNDLinearity),
            QCoreApplication.translate("AutoPowerCalibrationDialog", "ND-Linearit\u00e4t", None),
        )
        self.valueXCheckResult.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Ergebnis: \u2013", None)
        )
        self.buttonStartXCheck.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Vergleich starten", None)
        )
        self.buttonAbortXCheck.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Abbrechen", None)
        )
        self.buttonSaveXCheck.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Ergebnis speichern", None)
        )
        self.groupXCheckParams.setTitle(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Vergleichs-Parameter", None)
        )
        self.labelXCheckPoints.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Punkte:", None)
        )
        self.labelXCheckSettle.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Wartezeit (s):", None)
        )
        self.labelXCheckTolerance.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Toleranz (%):", None)
        )
        self.tabMode.setTabText(
            self.tabMode.indexOf(self.tabDetectorCompare),
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Detektor-Vergleich", None),
        )
        self.groupVerifyParams.setTitle(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Pr\u00fcf-Parameter", None)
        )
        self.labelVerifyLevels.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Pegel:", None)
        )
        # if QT_CONFIG(tooltip)
        self.spinVerifyLevels.setToolTip(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog",
                "Anzahl Pr\u00fcfpegel \u2014 Positionen werden automatisch in den \u00dcberlappbereichen benachbarter Gain-Fenster gew\u00e4hlt (siehe config.json: pdtia.gain_auto_switch_power_W).",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.labelVerifySettle.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Wartezeit (s):", None)
        )
        self.labelVerifyTolerancePct.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Toleranz (%):", None)
        )
        # if QT_CONFIG(tooltip)
        self.checkVerifyFromCurve.setToolTip(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog",
                "Die Referenzleistung jedes Pegels wird aus der ND-Kennlinie des Bereichsscans dieser Sitzung genommen; der PM400 wird nicht gelesen und darf au\u00dferhalb des Strahls stehen.",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.checkVerifyFromCurve.setText(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog",
                "Referenz aus ND-Kennlinie (PM400 nicht im Strahl)",
                None,
            )
        )
        self.buttonStartVerify.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Pr\u00fcfung starten", None)
        )
        self.buttonAbortVerify.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Abbrechen", None)
        )
        ___qtablewidgetitem = self.tableGainVerify.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Pegel", None)
        )
        ___qtablewidgetitem1 = self.tableGainVerify.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "PM400 (W)", None)
        )
        ___qtablewidgetitem2 = self.tableGainVerify.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Gain 1 (W)", None)
        )
        ___qtablewidgetitem3 = self.tableGainVerify.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Gain 2 (W)", None)
        )
        ___qtablewidgetitem4 = self.tableGainVerify.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Gain 3 (W)", None)
        )
        ___qtablewidgetitem5 = self.tableGainVerify.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Gain 4 (W)", None)
        )
        self.valueVerifyResult.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Ergebnis: \u2013", None)
        )
        self.tabMode.setTabText(
            self.tabMode.indexOf(self.tabGainVerify),
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Gain-Pr\u00fcfung", None),
        )
        self.valuePhase.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Bereit", None)
        )
        self.editLog.setPlaceholderText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Log-Ausgabe\u2026", None)
        )

    # retranslateUi
