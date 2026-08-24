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
from polarisation_ui.ui.widgets.nd_transmission_plot import NDTransmissionPlot


class Ui_AutoPowerCalibrationDialog(object):
    def setupUi(self, AutoPowerCalibrationDialog):
        if not AutoPowerCalibrationDialog.objectName():
            AutoPowerCalibrationDialog.setObjectName("AutoPowerCalibrationDialog")
        AutoPowerCalibrationDialog.resize(1280, 980)
        self.mainLayout = QVBoxLayout(AutoPowerCalibrationDialog)
        self.mainLayout.setSpacing(6)
        self.mainLayout.setObjectName("mainLayout")
        self.mainLayout.setContentsMargins(8, 8, 8, 8)
        self.gbConnections = QGroupBox(AutoPowerCalibrationDialog)
        self.gbConnections.setObjectName("gbConnections")
        self.connectionsLayout = QHBoxLayout(self.gbConnections)
        self.connectionsLayout.setSpacing(6)
        self.connectionsLayout.setObjectName("connectionsLayout")
        self.connectionsLayout.setContentsMargins(6, 4, 6, 6)
        self.gbArduino = QGroupBox(self.gbConnections)
        self.gbArduino.setObjectName("gbArduino")
        self.arduinoGrid = QGridLayout(self.gbArduino)
        self.arduinoGrid.setSpacing(4)
        self.arduinoGrid.setObjectName("arduinoGrid")
        self.lblArduinoPort = QLabel(self.gbArduino)
        self.lblArduinoPort.setObjectName("lblArduinoPort")

        self.arduinoGrid.addWidget(self.lblArduinoPort, 0, 0, 1, 1)

        self.comboArduinoPort = QComboBox(self.gbArduino)
        self.comboArduinoPort.setObjectName("comboArduinoPort")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboArduinoPort.sizePolicy().hasHeightForWidth())
        self.comboArduinoPort.setSizePolicy(sizePolicy)

        self.arduinoGrid.addWidget(self.comboArduinoPort, 0, 1, 1, 1)

        self.btnRefreshArduino = QPushButton(self.gbArduino)
        self.btnRefreshArduino.setObjectName("btnRefreshArduino")

        self.arduinoGrid.addWidget(self.btnRefreshArduino, 0, 2, 1, 1)

        self.lblArduinoStatus = QLabel(self.gbArduino)
        self.lblArduinoStatus.setObjectName("lblArduinoStatus")

        self.arduinoGrid.addWidget(self.lblArduinoStatus, 1, 0, 1, 2)

        self.btnConnectArduino = QPushButton(self.gbArduino)
        self.btnConnectArduino.setObjectName("btnConnectArduino")

        self.arduinoGrid.addWidget(self.btnConnectArduino, 1, 2, 1, 1)

        self.connectionsLayout.addWidget(self.gbArduino)

        self.gbKDC = QGroupBox(self.gbConnections)
        self.gbKDC.setObjectName("gbKDC")
        self.kdcGrid = QGridLayout(self.gbKDC)
        self.kdcGrid.setSpacing(4)
        self.kdcGrid.setObjectName("kdcGrid")
        self.lblKDCDevice = QLabel(self.gbKDC)
        self.lblKDCDevice.setObjectName("lblKDCDevice")

        self.kdcGrid.addWidget(self.lblKDCDevice, 0, 0, 1, 1)

        self.comboKDC = QComboBox(self.gbKDC)
        self.comboKDC.setObjectName("comboKDC")
        sizePolicy.setHeightForWidth(self.comboKDC.sizePolicy().hasHeightForWidth())
        self.comboKDC.setSizePolicy(sizePolicy)

        self.kdcGrid.addWidget(self.comboKDC, 0, 1, 1, 1)

        self.btnRefreshKDC = QPushButton(self.gbKDC)
        self.btnRefreshKDC.setObjectName("btnRefreshKDC")

        self.kdcGrid.addWidget(self.btnRefreshKDC, 0, 2, 1, 1)

        self.lblKDCStatus = QLabel(self.gbKDC)
        self.lblKDCStatus.setObjectName("lblKDCStatus")

        self.kdcGrid.addWidget(self.lblKDCStatus, 1, 0, 1, 2)

        self.btnConnectKDC = QPushButton(self.gbKDC)
        self.btnConnectKDC.setObjectName("btnConnectKDC")

        self.kdcGrid.addWidget(self.btnConnectKDC, 1, 2, 1, 1)

        self.btnHomeKDC = QPushButton(self.gbKDC)
        self.btnHomeKDC.setObjectName("btnHomeKDC")
        self.btnHomeKDC.setEnabled(False)

        self.kdcGrid.addWidget(self.btnHomeKDC, 2, 0, 1, 3)

        self.connectionsLayout.addWidget(self.gbKDC)

        self.gbNDStage = QGroupBox(self.gbConnections)
        self.gbNDStage.setObjectName("gbNDStage")
        self.ndGrid = QGridLayout(self.gbNDStage)
        self.ndGrid.setSpacing(4)
        self.ndGrid.setObjectName("ndGrid")
        self.lblNDDevice = QLabel(self.gbNDStage)
        self.lblNDDevice.setObjectName("lblNDDevice")

        self.ndGrid.addWidget(self.lblNDDevice, 0, 0, 1, 1)

        self.comboNDStage = QComboBox(self.gbNDStage)
        self.comboNDStage.setObjectName("comboNDStage")
        sizePolicy.setHeightForWidth(self.comboNDStage.sizePolicy().hasHeightForWidth())
        self.comboNDStage.setSizePolicy(sizePolicy)

        self.ndGrid.addWidget(self.comboNDStage, 0, 1, 1, 1)

        self.btnRefreshNDStage = QPushButton(self.gbNDStage)
        self.btnRefreshNDStage.setObjectName("btnRefreshNDStage")

        self.ndGrid.addWidget(self.btnRefreshNDStage, 0, 2, 1, 1)

        self.lblNDStatus = QLabel(self.gbNDStage)
        self.lblNDStatus.setObjectName("lblNDStatus")

        self.ndGrid.addWidget(self.lblNDStatus, 1, 0, 1, 2)

        self.btnConnectNDStage = QPushButton(self.gbNDStage)
        self.btnConnectNDStage.setObjectName("btnConnectNDStage")

        self.ndGrid.addWidget(self.btnConnectNDStage, 1, 2, 1, 1)

        self.btnHomeNDStage = QPushButton(self.gbNDStage)
        self.btnHomeNDStage.setObjectName("btnHomeNDStage")
        self.btnHomeNDStage.setEnabled(False)

        self.ndGrid.addWidget(self.btnHomeNDStage, 2, 0, 1, 3)

        self.lblNDPosition = QLabel(self.gbNDStage)
        self.lblNDPosition.setObjectName("lblNDPosition")

        self.ndGrid.addWidget(self.lblNDPosition, 3, 0, 1, 3)

        self.connectionsLayout.addWidget(self.gbNDStage)

        self.gbPM400 = QGroupBox(self.gbConnections)
        self.gbPM400.setObjectName("gbPM400")
        self.pmGrid = QGridLayout(self.gbPM400)
        self.pmGrid.setSpacing(4)
        self.pmGrid.setObjectName("pmGrid")
        self.lblPMResource = QLabel(self.gbPM400)
        self.lblPMResource.setObjectName("lblPMResource")

        self.pmGrid.addWidget(self.lblPMResource, 0, 0, 1, 1)

        self.comboPM400 = QComboBox(self.gbPM400)
        self.comboPM400.setObjectName("comboPM400")
        sizePolicy.setHeightForWidth(self.comboPM400.sizePolicy().hasHeightForWidth())
        self.comboPM400.setSizePolicy(sizePolicy)
        self.comboPM400.setEditable(True)

        self.pmGrid.addWidget(self.comboPM400, 0, 1, 1, 1)

        self.btnRefreshPM400 = QPushButton(self.gbPM400)
        self.btnRefreshPM400.setObjectName("btnRefreshPM400")

        self.pmGrid.addWidget(self.btnRefreshPM400, 0, 2, 1, 1)

        self.lblPM400Status = QLabel(self.gbPM400)
        self.lblPM400Status.setObjectName("lblPM400Status")

        self.pmGrid.addWidget(self.lblPM400Status, 1, 0, 1, 2)

        self.btnConnectPM400 = QPushButton(self.gbPM400)
        self.btnConnectPM400.setObjectName("btnConnectPM400")

        self.pmGrid.addWidget(self.btnConnectPM400, 1, 2, 1, 1)

        self.btnZeroPM400 = QPushButton(self.gbPM400)
        self.btnZeroPM400.setObjectName("btnZeroPM400")
        self.btnZeroPM400.setEnabled(False)

        self.pmGrid.addWidget(self.btnZeroPM400, 2, 0, 1, 3)

        self.connectionsLayout.addWidget(self.gbPM400)

        self.gbPM400B = QGroupBox(self.gbConnections)
        self.gbPM400B.setObjectName("gbPM400B")
        self.pmBGrid = QGridLayout(self.gbPM400B)
        self.pmBGrid.setSpacing(4)
        self.pmBGrid.setObjectName("pmBGrid")
        self.lblPM400BResource = QLabel(self.gbPM400B)
        self.lblPM400BResource.setObjectName("lblPM400BResource")

        self.pmBGrid.addWidget(self.lblPM400BResource, 0, 0, 1, 1)

        self.comboPM400B = QComboBox(self.gbPM400B)
        self.comboPM400B.setObjectName("comboPM400B")
        sizePolicy.setHeightForWidth(self.comboPM400B.sizePolicy().hasHeightForWidth())
        self.comboPM400B.setSizePolicy(sizePolicy)
        self.comboPM400B.setEditable(True)

        self.pmBGrid.addWidget(self.comboPM400B, 0, 1, 1, 1)

        self.btnRefreshPM400B = QPushButton(self.gbPM400B)
        self.btnRefreshPM400B.setObjectName("btnRefreshPM400B")

        self.pmBGrid.addWidget(self.btnRefreshPM400B, 0, 2, 1, 1)

        self.lblPM400BStatus = QLabel(self.gbPM400B)
        self.lblPM400BStatus.setObjectName("lblPM400BStatus")

        self.pmBGrid.addWidget(self.lblPM400BStatus, 1, 0, 1, 2)

        self.btnConnectPM400B = QPushButton(self.gbPM400B)
        self.btnConnectPM400B.setObjectName("btnConnectPM400B")

        self.pmBGrid.addWidget(self.btnConnectPM400B, 1, 2, 1, 1)

        self.btnZeroPM400B = QPushButton(self.gbPM400B)
        self.btnZeroPM400B.setObjectName("btnZeroPM400B")
        self.btnZeroPM400B.setEnabled(False)

        self.pmBGrid.addWidget(self.btnZeroPM400B, 2, 0, 1, 3)

        self.connectionsLayout.addWidget(self.gbPM400B)

        self.mainLayout.addWidget(self.gbConnections)

        self.workAreaLayout = QHBoxLayout()
        self.workAreaLayout.setSpacing(8)
        self.workAreaLayout.setObjectName("workAreaLayout")
        self.leftPanelLayout = QVBoxLayout()
        self.leftPanelLayout.setSpacing(5)
        self.leftPanelLayout.setObjectName("leftPanelLayout")
        self.tabsMode = QTabWidget(AutoPowerCalibrationDialog)
        self.tabsMode.setObjectName("tabsMode")
        self.tabCalibration = QWidget()
        self.tabCalibration.setObjectName("tabCalibration")
        self.tabCalibrationLayout = QVBoxLayout(self.tabCalibration)
        self.tabCalibrationLayout.setSpacing(5)
        self.tabCalibrationLayout.setObjectName("tabCalibrationLayout")
        self.gbIntensitySource = QGroupBox(self.tabCalibration)
        self.gbIntensitySource.setObjectName("gbIntensitySource")
        self.intensitySourceLayout = QHBoxLayout(self.gbIntensitySource)
        self.intensitySourceLayout.setSpacing(6)
        self.intensitySourceLayout.setObjectName("intensitySourceLayout")
        self.lblIntensitySource = QLabel(self.gbIntensitySource)
        self.lblIntensitySource.setObjectName("lblIntensitySource")

        self.intensitySourceLayout.addWidget(self.lblIntensitySource)

        self.radioSourcePolariser = QRadioButton(self.gbIntensitySource)
        self.radioSourcePolariser.setObjectName("radioSourcePolariser")
        self.radioSourcePolariser.setChecked(True)

        self.intensitySourceLayout.addWidget(self.radioSourcePolariser)

        self.radioSourceND = QRadioButton(self.gbIntensitySource)
        self.radioSourceND.setObjectName("radioSourceND")

        self.intensitySourceLayout.addWidget(self.radioSourceND)

        self.tabCalibrationLayout.addWidget(self.gbIntensitySource)

        self.topControlsRow = QHBoxLayout()
        self.topControlsRow.setSpacing(5)
        self.topControlsRow.setObjectName("topControlsRow")
        self.gbAlignment = QGroupBox(self.tabCalibration)
        self.gbAlignment.setObjectName("gbAlignment")
        self.alignLayout = QVBoxLayout(self.gbAlignment)
        self.alignLayout.setSpacing(3)
        self.alignLayout.setObjectName("alignLayout")
        self.alignForm = QFormLayout()
        self.alignForm.setObjectName("alignForm")
        self.alignForm.setVerticalSpacing(3)
        self.lblAlignStart = QLabel(self.gbAlignment)
        self.lblAlignStart.setObjectName("lblAlignStart")

        self.alignForm.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lblAlignStart)

        self.spinAlignStart = QDoubleSpinBox(self.gbAlignment)
        self.spinAlignStart.setObjectName("spinAlignStart")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.spinAlignStart.sizePolicy().hasHeightForWidth())
        self.spinAlignStart.setSizePolicy(sizePolicy1)
        self.spinAlignStart.setDecimals(1)
        self.spinAlignStart.setMinimum(0.000000000000000)
        self.spinAlignStart.setMaximum(360.000000000000000)
        self.spinAlignStart.setValue(0.000000000000000)

        self.alignForm.setWidget(0, QFormLayout.ItemRole.FieldRole, self.spinAlignStart)

        self.lblAlignEnd = QLabel(self.gbAlignment)
        self.lblAlignEnd.setObjectName("lblAlignEnd")

        self.alignForm.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lblAlignEnd)

        self.spinAlignEnd = QDoubleSpinBox(self.gbAlignment)
        self.spinAlignEnd.setObjectName("spinAlignEnd")
        sizePolicy1.setHeightForWidth(self.spinAlignEnd.sizePolicy().hasHeightForWidth())
        self.spinAlignEnd.setSizePolicy(sizePolicy1)
        self.spinAlignEnd.setDecimals(1)
        self.spinAlignEnd.setMinimum(0.000000000000000)
        self.spinAlignEnd.setMaximum(360.000000000000000)
        self.spinAlignEnd.setValue(180.000000000000000)

        self.alignForm.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spinAlignEnd)

        self.lblAlignNPoints = QLabel(self.gbAlignment)
        self.lblAlignNPoints.setObjectName("lblAlignNPoints")

        self.alignForm.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lblAlignNPoints)

        self.spinAlignNPoints = QSpinBox(self.gbAlignment)
        self.spinAlignNPoints.setObjectName("spinAlignNPoints")
        sizePolicy1.setHeightForWidth(self.spinAlignNPoints.sizePolicy().hasHeightForWidth())
        self.spinAlignNPoints.setSizePolicy(sizePolicy1)
        self.spinAlignNPoints.setMinimum(3)
        self.spinAlignNPoints.setMaximum(360)
        self.spinAlignNPoints.setValue(36)

        self.alignForm.setWidget(2, QFormLayout.ItemRole.FieldRole, self.spinAlignNPoints)

        self.lblAlignSettle = QLabel(self.gbAlignment)
        self.lblAlignSettle.setObjectName("lblAlignSettle")

        self.alignForm.setWidget(3, QFormLayout.ItemRole.LabelRole, self.lblAlignSettle)

        self.spinAlignSettle = QDoubleSpinBox(self.gbAlignment)
        self.spinAlignSettle.setObjectName("spinAlignSettle")
        sizePolicy1.setHeightForWidth(self.spinAlignSettle.sizePolicy().hasHeightForWidth())
        self.spinAlignSettle.setSizePolicy(sizePolicy1)
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
        self.btnAlignPolariser = QPushButton(self.gbAlignment)
        self.btnAlignPolariser.setObjectName("btnAlignPolariser")
        self.btnAlignPolariser.setEnabled(False)

        self.alignButtonLayout.addWidget(self.btnAlignPolariser)

        self.btnAbortAlign = QPushButton(self.gbAlignment)
        self.btnAbortAlign.setObjectName("btnAbortAlign")
        self.btnAbortAlign.setEnabled(False)

        self.alignButtonLayout.addWidget(self.btnAbortAlign)

        self.alignLayout.addLayout(self.alignButtonLayout)

        self.lblAngleOffset = QLabel(self.gbAlignment)
        self.lblAngleOffset.setObjectName("lblAngleOffset")
        self.lblAngleOffset.setWordWrap(True)

        self.alignLayout.addWidget(self.lblAngleOffset)

        self.topControlsRow.addWidget(self.gbAlignment)

        self.gbBeam = QGroupBox(self.tabCalibration)
        self.gbBeam.setObjectName("gbBeam")
        self.beamForm = QFormLayout(self.gbBeam)
        self.beamForm.setObjectName("beamForm")
        self.beamForm.setVerticalSpacing(3)
        self.lblWavelength = QLabel(self.gbBeam)
        self.lblWavelength.setObjectName("lblWavelength")

        self.beamForm.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lblWavelength)

        self.spinWavelength = QDoubleSpinBox(self.gbBeam)
        self.spinWavelength.setObjectName("spinWavelength")
        sizePolicy1.setHeightForWidth(self.spinWavelength.sizePolicy().hasHeightForWidth())
        self.spinWavelength.setSizePolicy(sizePolicy1)
        self.spinWavelength.setDecimals(1)
        self.spinWavelength.setMinimum(200.000000000000000)
        self.spinWavelength.setMaximum(1100.000000000000000)
        self.spinWavelength.setValue(633.000000000000000)

        self.beamForm.setWidget(0, QFormLayout.ItemRole.FieldRole, self.spinWavelength)

        self.lblAttenuation = QLabel(self.gbBeam)
        self.lblAttenuation.setObjectName("lblAttenuation")

        self.beamForm.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lblAttenuation)

        self.spinAttenuation = QDoubleSpinBox(self.gbBeam)
        self.spinAttenuation.setObjectName("spinAttenuation")
        sizePolicy1.setHeightForWidth(self.spinAttenuation.sizePolicy().hasHeightForWidth())
        self.spinAttenuation.setSizePolicy(sizePolicy1)
        self.spinAttenuation.setDecimals(3)
        self.spinAttenuation.setMinimum(-60.000000000000000)
        self.spinAttenuation.setMaximum(90.000000000000000)
        self.spinAttenuation.setSingleStep(0.100000000000000)
        self.spinAttenuation.setValue(3.000000000000000)

        self.beamForm.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spinAttenuation)

        self.lblPmAveraging = QLabel(self.gbBeam)
        self.lblPmAveraging.setObjectName("lblPmAveraging")

        self.beamForm.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lblPmAveraging)

        self.spinPmAveraging = QSpinBox(self.gbBeam)
        self.spinPmAveraging.setObjectName("spinPmAveraging")
        sizePolicy1.setHeightForWidth(self.spinPmAveraging.sizePolicy().hasHeightForWidth())
        self.spinPmAveraging.setSizePolicy(sizePolicy1)
        self.spinPmAveraging.setMinimum(1)
        self.spinPmAveraging.setMaximum(300000)
        self.spinPmAveraging.setValue(100)

        self.beamForm.setWidget(2, QFormLayout.ItemRole.FieldRole, self.spinPmAveraging)

        self.topControlsRow.addWidget(self.gbBeam)

        self.tabCalibrationLayout.addLayout(self.topControlsRow)

        self.gbSweep = QGroupBox(self.tabCalibration)
        self.gbSweep.setObjectName("gbSweep")
        self.sweepLayout = QVBoxLayout(self.gbSweep)
        self.sweepLayout.setSpacing(3)
        self.sweepLayout.setObjectName("sweepLayout")
        self.sweepForm = QFormLayout()
        self.sweepForm.setObjectName("sweepForm")
        self.sweepForm.setVerticalSpacing(3)
        self.lblAngleStart = QLabel(self.gbSweep)
        self.lblAngleStart.setObjectName("lblAngleStart")

        self.sweepForm.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lblAngleStart)

        self.spinAngleStart = QDoubleSpinBox(self.gbSweep)
        self.spinAngleStart.setObjectName("spinAngleStart")
        sizePolicy1.setHeightForWidth(self.spinAngleStart.sizePolicy().hasHeightForWidth())
        self.spinAngleStart.setSizePolicy(sizePolicy1)
        self.spinAngleStart.setDecimals(1)
        self.spinAngleStart.setMinimum(0.000000000000000)
        self.spinAngleStart.setMaximum(360.000000000000000)
        self.spinAngleStart.setValue(0.000000000000000)

        self.sweepForm.setWidget(0, QFormLayout.ItemRole.FieldRole, self.spinAngleStart)

        self.lblAngleEnd = QLabel(self.gbSweep)
        self.lblAngleEnd.setObjectName("lblAngleEnd")

        self.sweepForm.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lblAngleEnd)

        self.spinAngleEnd = QDoubleSpinBox(self.gbSweep)
        self.spinAngleEnd.setObjectName("spinAngleEnd")
        sizePolicy1.setHeightForWidth(self.spinAngleEnd.sizePolicy().hasHeightForWidth())
        self.spinAngleEnd.setSizePolicy(sizePolicy1)
        self.spinAngleEnd.setDecimals(1)
        self.spinAngleEnd.setMinimum(0.000000000000000)
        self.spinAngleEnd.setMaximum(360.000000000000000)
        self.spinAngleEnd.setValue(90.000000000000000)

        self.sweepForm.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spinAngleEnd)

        self.lblNPoints = QLabel(self.gbSweep)
        self.lblNPoints.setObjectName("lblNPoints")

        self.sweepForm.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lblNPoints)

        self.spinNPoints = QSpinBox(self.gbSweep)
        self.spinNPoints.setObjectName("spinNPoints")
        sizePolicy1.setHeightForWidth(self.spinNPoints.sizePolicy().hasHeightForWidth())
        self.spinNPoints.setSizePolicy(sizePolicy1)
        self.spinNPoints.setMinimum(3)
        self.spinNPoints.setMaximum(200)
        self.spinNPoints.setValue(30)

        self.sweepForm.setWidget(2, QFormLayout.ItemRole.FieldRole, self.spinNPoints)

        self.lblPointSettle = QLabel(self.gbSweep)
        self.lblPointSettle.setObjectName("lblPointSettle")

        self.sweepForm.setWidget(3, QFormLayout.ItemRole.LabelRole, self.lblPointSettle)

        self.spinPointSettle = QDoubleSpinBox(self.gbSweep)
        self.spinPointSettle.setObjectName("spinPointSettle")
        sizePolicy1.setHeightForWidth(self.spinPointSettle.sizePolicy().hasHeightForWidth())
        self.spinPointSettle.setSizePolicy(sizePolicy1)
        self.spinPointSettle.setDecimals(2)
        self.spinPointSettle.setMinimum(0.000000000000000)
        self.spinPointSettle.setMaximum(30.000000000000000)
        self.spinPointSettle.setSingleStep(0.050000000000000)
        self.spinPointSettle.setValue(0.200000000000000)

        self.sweepForm.setWidget(3, QFormLayout.ItemRole.FieldRole, self.spinPointSettle)

        self.lblGainSettle = QLabel(self.gbSweep)
        self.lblGainSettle.setObjectName("lblGainSettle")

        self.sweepForm.setWidget(4, QFormLayout.ItemRole.LabelRole, self.lblGainSettle)

        self.spinGainSettle = QDoubleSpinBox(self.gbSweep)
        self.spinGainSettle.setObjectName("spinGainSettle")
        sizePolicy1.setHeightForWidth(self.spinGainSettle.sizePolicy().hasHeightForWidth())
        self.spinGainSettle.setSizePolicy(sizePolicy1)
        self.spinGainSettle.setDecimals(2)
        self.spinGainSettle.setMinimum(0.000000000000000)
        self.spinGainSettle.setMaximum(10.000000000000000)
        self.spinGainSettle.setSingleStep(0.100000000000000)
        self.spinGainSettle.setValue(0.500000000000000)

        self.sweepForm.setWidget(4, QFormLayout.ItemRole.FieldRole, self.spinGainSettle)

        self.lblDetectorSamples = QLabel(self.gbSweep)
        self.lblDetectorSamples.setObjectName("lblDetectorSamples")

        self.sweepForm.setWidget(5, QFormLayout.ItemRole.LabelRole, self.lblDetectorSamples)

        self.spinDetectorSamples = QSpinBox(self.gbSweep)
        self.spinDetectorSamples.setObjectName("spinDetectorSamples")
        sizePolicy1.setHeightForWidth(self.spinDetectorSamples.sizePolicy().hasHeightForWidth())
        self.spinDetectorSamples.setSizePolicy(sizePolicy1)
        self.spinDetectorSamples.setMinimum(1)
        self.spinDetectorSamples.setMaximum(100)
        self.spinDetectorSamples.setValue(5)

        self.sweepForm.setWidget(5, QFormLayout.ItemRole.FieldRole, self.spinDetectorSamples)

        self.lblSaturationThreshold = QLabel(self.gbSweep)
        self.lblSaturationThreshold.setObjectName("lblSaturationThreshold")

        self.sweepForm.setWidget(6, QFormLayout.ItemRole.LabelRole, self.lblSaturationThreshold)

        self.spinSaturationThreshold = QDoubleSpinBox(self.gbSweep)
        self.spinSaturationThreshold.setObjectName("spinSaturationThreshold")
        sizePolicy1.setHeightForWidth(self.spinSaturationThreshold.sizePolicy().hasHeightForWidth())
        self.spinSaturationThreshold.setSizePolicy(sizePolicy1)
        self.spinSaturationThreshold.setDecimals(2)
        self.spinSaturationThreshold.setMinimum(1.000000000000000)
        self.spinSaturationThreshold.setMaximum(3.300000000000000)
        self.spinSaturationThreshold.setSingleStep(0.050000000000000)
        self.spinSaturationThreshold.setValue(2.350000000000000)

        self.sweepForm.setWidget(6, QFormLayout.ItemRole.FieldRole, self.spinSaturationThreshold)

        self.sweepLayout.addLayout(self.sweepForm)

        self.gridModeLayout = QHBoxLayout()
        self.gridModeLayout.setSpacing(6)
        self.gridModeLayout.setObjectName("gridModeLayout")
        self.lblGridMode = QLabel(self.gbSweep)
        self.lblGridMode.setObjectName("lblGridMode")

        self.gridModeLayout.addWidget(self.lblGridMode)

        self.radioLinearAngle = QRadioButton(self.gbSweep)
        self.radioLinearAngle.setObjectName("radioLinearAngle")

        self.gridModeLayout.addWidget(self.radioLinearAngle)

        self.radioLinearCos2 = QRadioButton(self.gbSweep)
        self.radioLinearCos2.setObjectName("radioLinearCos2")
        self.radioLinearCos2.setChecked(True)

        self.gridModeLayout.addWidget(self.radioLinearCos2)

        self.sweepLayout.addLayout(self.gridModeLayout)

        self.gainCheckboxLayout = QHBoxLayout()
        self.gainCheckboxLayout.setSpacing(6)
        self.gainCheckboxLayout.setObjectName("gainCheckboxLayout")
        self.lblGains = QLabel(self.gbSweep)
        self.lblGains.setObjectName("lblGains")

        self.gainCheckboxLayout.addWidget(self.lblGains)

        self.chkGain1 = QCheckBox(self.gbSweep)
        self.chkGain1.setObjectName("chkGain1")
        self.chkGain1.setChecked(True)

        self.gainCheckboxLayout.addWidget(self.chkGain1)

        self.chkGain2 = QCheckBox(self.gbSweep)
        self.chkGain2.setObjectName("chkGain2")
        self.chkGain2.setChecked(True)

        self.gainCheckboxLayout.addWidget(self.chkGain2)

        self.chkGain3 = QCheckBox(self.gbSweep)
        self.chkGain3.setObjectName("chkGain3")
        self.chkGain3.setChecked(True)

        self.gainCheckboxLayout.addWidget(self.chkGain3)

        self.chkGain4 = QCheckBox(self.gbSweep)
        self.chkGain4.setObjectName("chkGain4")
        self.chkGain4.setChecked(True)

        self.gainCheckboxLayout.addWidget(self.chkGain4)

        self.sweepLayout.addLayout(self.gainCheckboxLayout)

        self.tabCalibrationLayout.addWidget(self.gbSweep)

        self.gbPowerGrid = QGroupBox(self.tabCalibration)
        self.gbPowerGrid.setObjectName("gbPowerGrid")
        self.powerGridForm = QFormLayout(self.gbPowerGrid)
        self.powerGridForm.setObjectName("powerGridForm")
        self.powerGridForm.setVerticalSpacing(3)
        self.lblPowerGridMode = QLabel(self.gbPowerGrid)
        self.lblPowerGridMode.setObjectName("lblPowerGridMode")

        self.powerGridForm.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lblPowerGridMode)

        self.powerGridModeLayout = QHBoxLayout()
        self.powerGridModeLayout.setSpacing(6)
        self.powerGridModeLayout.setObjectName("powerGridModeLayout")
        self.radioGridLogPower = QRadioButton(self.gbPowerGrid)
        self.radioGridLogPower.setObjectName("radioGridLogPower")
        self.radioGridLogPower.setChecked(True)

        self.powerGridModeLayout.addWidget(self.radioGridLogPower)

        self.radioGridLinearPower = QRadioButton(self.gbPowerGrid)
        self.radioGridLinearPower.setObjectName("radioGridLinearPower")

        self.powerGridModeLayout.addWidget(self.radioGridLinearPower)

        self.powerGridForm.setLayout(0, QFormLayout.ItemRole.FieldRole, self.powerGridModeLayout)

        self.lblPowerTolerancePct = QLabel(self.gbPowerGrid)
        self.lblPowerTolerancePct.setObjectName("lblPowerTolerancePct")

        self.powerGridForm.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lblPowerTolerancePct)

        self.spinPowerTolerancePct = QDoubleSpinBox(self.gbPowerGrid)
        self.spinPowerTolerancePct.setObjectName("spinPowerTolerancePct")
        sizePolicy1.setHeightForWidth(self.spinPowerTolerancePct.sizePolicy().hasHeightForWidth())
        self.spinPowerTolerancePct.setSizePolicy(sizePolicy1)
        self.spinPowerTolerancePct.setDecimals(1)
        self.spinPowerTolerancePct.setMinimum(0.100000000000000)
        self.spinPowerTolerancePct.setMaximum(50.000000000000000)
        self.spinPowerTolerancePct.setValue(5.000000000000000)

        self.powerGridForm.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spinPowerTolerancePct)

        self.lblMaxRefineSteps = QLabel(self.gbPowerGrid)
        self.lblMaxRefineSteps.setObjectName("lblMaxRefineSteps")

        self.powerGridForm.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lblMaxRefineSteps)

        self.spinMaxRefineSteps = QSpinBox(self.gbPowerGrid)
        self.spinMaxRefineSteps.setObjectName("spinMaxRefineSteps")
        sizePolicy1.setHeightForWidth(self.spinMaxRefineSteps.sizePolicy().hasHeightForWidth())
        self.spinMaxRefineSteps.setSizePolicy(sizePolicy1)
        self.spinMaxRefineSteps.setMinimum(0)
        self.spinMaxRefineSteps.setMaximum(10)
        self.spinMaxRefineSteps.setValue(2)

        self.powerGridForm.setWidget(2, QFormLayout.ItemRole.FieldRole, self.spinMaxRefineSteps)

        self.tabCalibrationLayout.addWidget(self.gbPowerGrid)

        self.gbProfile = QGroupBox(self.tabCalibration)
        self.gbProfile.setObjectName("gbProfile")
        self.profileForm = QFormLayout(self.gbProfile)
        self.profileForm.setObjectName("profileForm")
        self.profileForm.setVerticalSpacing(3)
        self.lblProfileName = QLabel(self.gbProfile)
        self.lblProfileName.setObjectName("lblProfileName")

        self.profileForm.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lblProfileName)

        self.lineProfileName = QLineEdit(self.gbProfile)
        self.lineProfileName.setObjectName("lineProfileName")
        sizePolicy1.setHeightForWidth(self.lineProfileName.sizePolicy().hasHeightForWidth())
        self.lineProfileName.setSizePolicy(sizePolicy1)

        self.profileForm.setWidget(0, QFormLayout.ItemRole.FieldRole, self.lineProfileName)

        self.lblOutputPath = QLabel(self.gbProfile)
        self.lblOutputPath.setObjectName("lblOutputPath")
        self.lblOutputPath.setWordWrap(True)

        self.profileForm.setWidget(1, QFormLayout.ItemRole.SpanningRole, self.lblOutputPath)

        self.tabCalibrationLayout.addWidget(self.gbProfile)

        self.controlLayout = QHBoxLayout()
        self.controlLayout.setSpacing(6)
        self.controlLayout.setObjectName("controlLayout")
        self.btnStart = QPushButton(self.tabCalibration)
        self.btnStart.setObjectName("btnStart")
        self.btnStart.setEnabled(False)

        self.controlLayout.addWidget(self.btnStart)

        self.btnAbort = QPushButton(self.tabCalibration)
        self.btnAbort.setObjectName("btnAbort")
        self.btnAbort.setEnabled(False)

        self.controlLayout.addWidget(self.btnAbort)

        self.btnSave = QPushButton(self.tabCalibration)
        self.btnSave.setObjectName("btnSave")
        self.btnSave.setEnabled(False)

        self.controlLayout.addWidget(self.btnSave)

        self.tabCalibrationLayout.addLayout(self.controlLayout)

        self.tabCalibrationSpacer = QSpacerItem(
            20, 5, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.tabCalibrationLayout.addItem(self.tabCalibrationSpacer)

        self.tabsMode.addTab(self.tabCalibration, "")
        self.tabNDRange = QWidget()
        self.tabNDRange.setObjectName("tabNDRange")
        self.tabNDRangeLayout = QVBoxLayout(self.tabNDRange)
        self.tabNDRangeLayout.setSpacing(5)
        self.tabNDRangeLayout.setObjectName("tabNDRangeLayout")
        self.gbNDScanParams = QGroupBox(self.tabNDRange)
        self.gbNDScanParams.setObjectName("gbNDScanParams")
        self.ndScanForm = QFormLayout(self.gbNDScanParams)
        self.ndScanForm.setObjectName("ndScanForm")
        self.ndScanForm.setVerticalSpacing(3)
        self.lblNDScanStart = QLabel(self.gbNDScanParams)
        self.lblNDScanStart.setObjectName("lblNDScanStart")

        self.ndScanForm.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lblNDScanStart)

        self.spinNDScanStart = QDoubleSpinBox(self.gbNDScanParams)
        self.spinNDScanStart.setObjectName("spinNDScanStart")
        sizePolicy1.setHeightForWidth(self.spinNDScanStart.sizePolicy().hasHeightForWidth())
        self.spinNDScanStart.setSizePolicy(sizePolicy1)
        self.spinNDScanStart.setDecimals(2)
        self.spinNDScanStart.setMinimum(0.000000000000000)
        self.spinNDScanStart.setMaximum(50.000000000000000)
        self.spinNDScanStart.setValue(0.000000000000000)

        self.ndScanForm.setWidget(0, QFormLayout.ItemRole.FieldRole, self.spinNDScanStart)

        self.lblNDScanEnd = QLabel(self.gbNDScanParams)
        self.lblNDScanEnd.setObjectName("lblNDScanEnd")

        self.ndScanForm.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lblNDScanEnd)

        self.spinNDScanEnd = QDoubleSpinBox(self.gbNDScanParams)
        self.spinNDScanEnd.setObjectName("spinNDScanEnd")
        sizePolicy1.setHeightForWidth(self.spinNDScanEnd.sizePolicy().hasHeightForWidth())
        self.spinNDScanEnd.setSizePolicy(sizePolicy1)
        self.spinNDScanEnd.setDecimals(2)
        self.spinNDScanEnd.setMinimum(0.000000000000000)
        self.spinNDScanEnd.setMaximum(50.000000000000000)
        self.spinNDScanEnd.setValue(50.000000000000000)

        self.ndScanForm.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spinNDScanEnd)

        self.lblNDScanPoints = QLabel(self.gbNDScanParams)
        self.lblNDScanPoints.setObjectName("lblNDScanPoints")

        self.ndScanForm.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lblNDScanPoints)

        self.spinNDScanPoints = QSpinBox(self.gbNDScanParams)
        self.spinNDScanPoints.setObjectName("spinNDScanPoints")
        sizePolicy1.setHeightForWidth(self.spinNDScanPoints.sizePolicy().hasHeightForWidth())
        self.spinNDScanPoints.setSizePolicy(sizePolicy1)
        self.spinNDScanPoints.setMinimum(3)
        self.spinNDScanPoints.setMaximum(200)
        self.spinNDScanPoints.setValue(26)

        self.ndScanForm.setWidget(2, QFormLayout.ItemRole.FieldRole, self.spinNDScanPoints)

        self.lblNDScanSettle = QLabel(self.gbNDScanParams)
        self.lblNDScanSettle.setObjectName("lblNDScanSettle")

        self.ndScanForm.setWidget(3, QFormLayout.ItemRole.LabelRole, self.lblNDScanSettle)

        self.spinNDScanSettle = QDoubleSpinBox(self.gbNDScanParams)
        self.spinNDScanSettle.setObjectName("spinNDScanSettle")
        sizePolicy1.setHeightForWidth(self.spinNDScanSettle.sizePolicy().hasHeightForWidth())
        self.spinNDScanSettle.setSizePolicy(sizePolicy1)
        self.spinNDScanSettle.setDecimals(2)
        self.spinNDScanSettle.setMinimum(0.000000000000000)
        self.spinNDScanSettle.setMaximum(10.000000000000000)
        self.spinNDScanSettle.setSingleStep(0.050000000000000)
        self.spinNDScanSettle.setValue(0.200000000000000)

        self.ndScanForm.setWidget(3, QFormLayout.ItemRole.FieldRole, self.spinNDScanSettle)

        self.lblNDDarkFloor = QLabel(self.gbNDScanParams)
        self.lblNDDarkFloor.setObjectName("lblNDDarkFloor")

        self.ndScanForm.setWidget(4, QFormLayout.ItemRole.LabelRole, self.lblNDDarkFloor)

        self.spinNDDarkFloorUW = QDoubleSpinBox(self.gbNDScanParams)
        self.spinNDDarkFloorUW.setObjectName("spinNDDarkFloorUW")
        sizePolicy1.setHeightForWidth(self.spinNDDarkFloorUW.sizePolicy().hasHeightForWidth())
        self.spinNDDarkFloorUW.setSizePolicy(sizePolicy1)
        self.spinNDDarkFloorUW.setDecimals(4)
        self.spinNDDarkFloorUW.setMinimum(0.000000000000000)
        self.spinNDDarkFloorUW.setMaximum(1000.000000000000000)
        self.spinNDDarkFloorUW.setValue(0.000000000000000)

        self.ndScanForm.setWidget(4, QFormLayout.ItemRole.FieldRole, self.spinNDDarkFloorUW)

        self.tabNDRangeLayout.addWidget(self.gbNDScanParams)

        self.ndScanButtonLayout = QHBoxLayout()
        self.ndScanButtonLayout.setSpacing(6)
        self.ndScanButtonLayout.setObjectName("ndScanButtonLayout")
        self.btnScanNDRange = QPushButton(self.tabNDRange)
        self.btnScanNDRange.setObjectName("btnScanNDRange")
        self.btnScanNDRange.setEnabled(False)

        self.ndScanButtonLayout.addWidget(self.btnScanNDRange)

        self.btnAbortNDScan = QPushButton(self.tabNDRange)
        self.btnAbortNDScan.setObjectName("btnAbortNDScan")
        self.btnAbortNDScan.setEnabled(False)

        self.ndScanButtonLayout.addWidget(self.btnAbortNDScan)

        self.tabNDRangeLayout.addLayout(self.ndScanButtonLayout)

        self.lblNDRange = QLabel(self.tabNDRange)
        self.lblNDRange.setObjectName("lblNDRange")
        self.lblNDRange.setWordWrap(True)

        self.tabNDRangeLayout.addWidget(self.lblNDRange)

        self.ndPlotWidget = NDTransmissionPlot(self.tabNDRange)
        self.ndPlotWidget.setObjectName("ndPlotWidget")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(1)
        sizePolicy2.setHeightForWidth(self.ndPlotWidget.sizePolicy().hasHeightForWidth())
        self.ndPlotWidget.setSizePolicy(sizePolicy2)
        self.ndPlotWidget.setMinimumSize(QSize(300, 200))

        self.tabNDRangeLayout.addWidget(self.ndPlotWidget)

        self.tabsMode.addTab(self.tabNDRange, "")
        self.tabDetectorCompare = QWidget()
        self.tabDetectorCompare.setObjectName("tabDetectorCompare")
        self.tabDetectorCompareLayout = QVBoxLayout(self.tabDetectorCompare)
        self.tabDetectorCompareLayout.setSpacing(5)
        self.tabDetectorCompareLayout.setObjectName("tabDetectorCompareLayout")
        self.gbXCheckParams = QGroupBox(self.tabDetectorCompare)
        self.gbXCheckParams.setObjectName("gbXCheckParams")
        self.xCheckForm = QFormLayout(self.gbXCheckParams)
        self.xCheckForm.setObjectName("xCheckForm")
        self.xCheckForm.setVerticalSpacing(3)
        self.lblXCheckPoints = QLabel(self.gbXCheckParams)
        self.lblXCheckPoints.setObjectName("lblXCheckPoints")

        self.xCheckForm.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lblXCheckPoints)

        self.spinXCheckPoints = QSpinBox(self.gbXCheckParams)
        self.spinXCheckPoints.setObjectName("spinXCheckPoints")
        sizePolicy1.setHeightForWidth(self.spinXCheckPoints.sizePolicy().hasHeightForWidth())
        self.spinXCheckPoints.setSizePolicy(sizePolicy1)
        self.spinXCheckPoints.setMinimum(3)
        self.spinXCheckPoints.setMaximum(200)
        self.spinXCheckPoints.setValue(15)

        self.xCheckForm.setWidget(0, QFormLayout.ItemRole.FieldRole, self.spinXCheckPoints)

        self.lblXCheckSettle = QLabel(self.gbXCheckParams)
        self.lblXCheckSettle.setObjectName("lblXCheckSettle")

        self.xCheckForm.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lblXCheckSettle)

        self.spinXCheckSettle = QDoubleSpinBox(self.gbXCheckParams)
        self.spinXCheckSettle.setObjectName("spinXCheckSettle")
        sizePolicy1.setHeightForWidth(self.spinXCheckSettle.sizePolicy().hasHeightForWidth())
        self.spinXCheckSettle.setSizePolicy(sizePolicy1)
        self.spinXCheckSettle.setDecimals(2)
        self.spinXCheckSettle.setMinimum(0.000000000000000)
        self.spinXCheckSettle.setMaximum(10.000000000000000)
        self.spinXCheckSettle.setSingleStep(0.050000000000000)
        self.spinXCheckSettle.setValue(0.200000000000000)

        self.xCheckForm.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spinXCheckSettle)

        self.lblXCheckTolerance = QLabel(self.gbXCheckParams)
        self.lblXCheckTolerance.setObjectName("lblXCheckTolerance")

        self.xCheckForm.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lblXCheckTolerance)

        self.spinXCheckTolerance = QDoubleSpinBox(self.gbXCheckParams)
        self.spinXCheckTolerance.setObjectName("spinXCheckTolerance")
        sizePolicy1.setHeightForWidth(self.spinXCheckTolerance.sizePolicy().hasHeightForWidth())
        self.spinXCheckTolerance.setSizePolicy(sizePolicy1)
        self.spinXCheckTolerance.setDecimals(1)
        self.spinXCheckTolerance.setMinimum(0.100000000000000)
        self.spinXCheckTolerance.setMaximum(50.000000000000000)
        self.spinXCheckTolerance.setValue(5.000000000000000)

        self.xCheckForm.setWidget(2, QFormLayout.ItemRole.FieldRole, self.spinXCheckTolerance)

        self.tabDetectorCompareLayout.addWidget(self.gbXCheckParams)

        self.xCheckButtonLayout = QHBoxLayout()
        self.xCheckButtonLayout.setSpacing(6)
        self.xCheckButtonLayout.setObjectName("xCheckButtonLayout")
        self.btnStartXCheck = QPushButton(self.tabDetectorCompare)
        self.btnStartXCheck.setObjectName("btnStartXCheck")
        self.btnStartXCheck.setEnabled(False)

        self.xCheckButtonLayout.addWidget(self.btnStartXCheck)

        self.btnAbortXCheck = QPushButton(self.tabDetectorCompare)
        self.btnAbortXCheck.setObjectName("btnAbortXCheck")
        self.btnAbortXCheck.setEnabled(False)

        self.xCheckButtonLayout.addWidget(self.btnAbortXCheck)

        self.btnSaveXCheck = QPushButton(self.tabDetectorCompare)
        self.btnSaveXCheck.setObjectName("btnSaveXCheck")
        self.btnSaveXCheck.setEnabled(False)

        self.xCheckButtonLayout.addWidget(self.btnSaveXCheck)

        self.tabDetectorCompareLayout.addLayout(self.xCheckButtonLayout)

        self.lblXCheckResult = QLabel(self.tabDetectorCompare)
        self.lblXCheckResult.setObjectName("lblXCheckResult")
        self.lblXCheckResult.setWordWrap(True)

        self.tabDetectorCompareLayout.addWidget(self.lblXCheckResult)

        self.xCheckPlotWidget = DetectorComparisonPlot(self.tabDetectorCompare)
        self.xCheckPlotWidget.setObjectName("xCheckPlotWidget")
        sizePolicy2.setHeightForWidth(self.xCheckPlotWidget.sizePolicy().hasHeightForWidth())
        self.xCheckPlotWidget.setSizePolicy(sizePolicy2)
        self.xCheckPlotWidget.setMinimumSize(QSize(300, 200))

        self.tabDetectorCompareLayout.addWidget(self.xCheckPlotWidget)

        self.tabsMode.addTab(self.tabDetectorCompare, "")
        self.tabGainVerify = QWidget()
        self.tabGainVerify.setObjectName("tabGainVerify")
        self.tabGainVerifyLayout = QVBoxLayout(self.tabGainVerify)
        self.tabGainVerifyLayout.setSpacing(5)
        self.tabGainVerifyLayout.setObjectName("tabGainVerifyLayout")
        self.gbVerifyParams = QGroupBox(self.tabGainVerify)
        self.gbVerifyParams.setObjectName("gbVerifyParams")
        self.verifyForm = QFormLayout(self.gbVerifyParams)
        self.verifyForm.setObjectName("verifyForm")
        self.verifyForm.setVerticalSpacing(3)
        self.lblVerifyLevels = QLabel(self.gbVerifyParams)
        self.lblVerifyLevels.setObjectName("lblVerifyLevels")

        self.verifyForm.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lblVerifyLevels)

        self.spinVerifyLevels = QSpinBox(self.gbVerifyParams)
        self.spinVerifyLevels.setObjectName("spinVerifyLevels")
        sizePolicy1.setHeightForWidth(self.spinVerifyLevels.sizePolicy().hasHeightForWidth())
        self.spinVerifyLevels.setSizePolicy(sizePolicy1)
        self.spinVerifyLevels.setMinimum(1)
        self.spinVerifyLevels.setMaximum(20)
        self.spinVerifyLevels.setValue(3)

        self.verifyForm.setWidget(0, QFormLayout.ItemRole.FieldRole, self.spinVerifyLevels)

        self.lblVerifySettle = QLabel(self.gbVerifyParams)
        self.lblVerifySettle.setObjectName("lblVerifySettle")

        self.verifyForm.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lblVerifySettle)

        self.spinVerifySettle = QDoubleSpinBox(self.gbVerifyParams)
        self.spinVerifySettle.setObjectName("spinVerifySettle")
        sizePolicy1.setHeightForWidth(self.spinVerifySettle.sizePolicy().hasHeightForWidth())
        self.spinVerifySettle.setSizePolicy(sizePolicy1)
        self.spinVerifySettle.setDecimals(2)
        self.spinVerifySettle.setMinimum(0.000000000000000)
        self.spinVerifySettle.setMaximum(10.000000000000000)
        self.spinVerifySettle.setSingleStep(0.050000000000000)
        self.spinVerifySettle.setValue(0.300000000000000)

        self.verifyForm.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spinVerifySettle)

        self.lblVerifyTolerancePct = QLabel(self.gbVerifyParams)
        self.lblVerifyTolerancePct.setObjectName("lblVerifyTolerancePct")

        self.verifyForm.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lblVerifyTolerancePct)

        self.spinVerifyTolerancePct = QDoubleSpinBox(self.gbVerifyParams)
        self.spinVerifyTolerancePct.setObjectName("spinVerifyTolerancePct")
        sizePolicy1.setHeightForWidth(self.spinVerifyTolerancePct.sizePolicy().hasHeightForWidth())
        self.spinVerifyTolerancePct.setSizePolicy(sizePolicy1)
        self.spinVerifyTolerancePct.setDecimals(1)
        self.spinVerifyTolerancePct.setMinimum(0.100000000000000)
        self.spinVerifyTolerancePct.setMaximum(50.000000000000000)
        self.spinVerifyTolerancePct.setValue(5.000000000000000)

        self.verifyForm.setWidget(2, QFormLayout.ItemRole.FieldRole, self.spinVerifyTolerancePct)

        self.tabGainVerifyLayout.addWidget(self.gbVerifyParams)

        self.verifyButtonLayout = QHBoxLayout()
        self.verifyButtonLayout.setSpacing(6)
        self.verifyButtonLayout.setObjectName("verifyButtonLayout")
        self.btnStartVerify = QPushButton(self.tabGainVerify)
        self.btnStartVerify.setObjectName("btnStartVerify")
        self.btnStartVerify.setEnabled(False)

        self.verifyButtonLayout.addWidget(self.btnStartVerify)

        self.btnAbortVerify = QPushButton(self.tabGainVerify)
        self.btnAbortVerify.setObjectName("btnAbortVerify")
        self.btnAbortVerify.setEnabled(False)

        self.verifyButtonLayout.addWidget(self.btnAbortVerify)

        self.tabGainVerifyLayout.addLayout(self.verifyButtonLayout)

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
        sizePolicy2.setHeightForWidth(self.tableGainVerify.sizePolicy().hasHeightForWidth())
        self.tableGainVerify.setSizePolicy(sizePolicy2)
        self.tableGainVerify.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.tabGainVerifyLayout.addWidget(self.tableGainVerify)

        self.lblVerifyResult = QLabel(self.tabGainVerify)
        self.lblVerifyResult.setObjectName("lblVerifyResult")
        self.lblVerifyResult.setWordWrap(True)

        self.tabGainVerifyLayout.addWidget(self.lblVerifyResult)

        self.tabsMode.addTab(self.tabGainVerify, "")

        self.leftPanelLayout.addWidget(self.tabsMode)

        self.progressBar = QProgressBar(AutoPowerCalibrationDialog)
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setValue(0)
        self.progressBar.setTextVisible(True)

        self.leftPanelLayout.addWidget(self.progressBar)

        self.lblPhase = QLabel(AutoPowerCalibrationDialog)
        self.lblPhase.setObjectName("lblPhase")

        self.leftPanelLayout.addWidget(self.lblPhase)

        self.workAreaLayout.addLayout(self.leftPanelLayout)

        self.rightPanelLayout = QVBoxLayout()
        self.rightPanelLayout.setSpacing(5)
        self.rightPanelLayout.setObjectName("rightPanelLayout")
        self.plotWidget = MultiGainCalibrationPlot(AutoPowerCalibrationDialog)
        self.plotWidget.setObjectName("plotWidget")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(3)
        sizePolicy3.setHeightForWidth(self.plotWidget.sizePolicy().hasHeightForWidth())
        self.plotWidget.setSizePolicy(sizePolicy3)
        self.plotWidget.setMinimumSize(QSize(380, 250))

        self.rightPanelLayout.addWidget(self.plotWidget)

        self.plainTextLog = QPlainTextEdit(AutoPowerCalibrationDialog)
        self.plainTextLog.setObjectName("plainTextLog")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(1)
        sizePolicy4.setHeightForWidth(self.plainTextLog.sizePolicy().hasHeightForWidth())
        self.plainTextLog.setSizePolicy(sizePolicy4)
        self.plainTextLog.setMaximumSize(QSize(16777215, 150))
        self.plainTextLog.setReadOnly(True)

        self.rightPanelLayout.addWidget(self.plainTextLog)

        self.workAreaLayout.addLayout(self.rightPanelLayout)

        self.workAreaLayout.setStretch(1, 1)

        self.mainLayout.addLayout(self.workAreaLayout)

        self.retranslateUi(AutoPowerCalibrationDialog)

        self.tabsMode.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(AutoPowerCalibrationDialog)

    # setupUi

    def retranslateUi(self, AutoPowerCalibrationDialog):
        AutoPowerCalibrationDialog.setWindowTitle(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog", "Automatische Leistungskalibrierung", None
            )
        )
        self.gbConnections.setTitle(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Verbindungen", None)
        )
        self.gbArduino.setTitle(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog", "Arduino (Detektor & Gain)", None
            )
        )
        self.lblArduinoPort.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Port:", None)
        )
        self.btnRefreshArduino.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Aktualisieren", None)
        )
        self.lblArduinoStatus.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Nicht verbunden", None)
        )
        self.btnConnectArduino.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Verbinden", None)
        )
        self.gbKDC.setTitle(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog", "KDC101 Rotationsantrieb (PRM1/MZ8)", None
            )
        )
        self.lblKDCDevice.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Ger\u00e4t:", None)
        )
        self.btnRefreshKDC.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Aktualisieren", None)
        )
        self.lblKDCStatus.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Nicht verbunden", None)
        )
        self.btnConnectKDC.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Verbinden", None)
        )
        self.btnHomeKDC.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Referenzfahrt (Home)", None)
        )
        self.gbNDStage.setTitle(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog", "ND-Filter Linearantrieb (MTS50/M-Z8)", None
            )
        )
        self.lblNDDevice.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Ger\u00e4t:", None)
        )
        self.btnRefreshNDStage.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Aktualisieren", None)
        )
        self.lblNDStatus.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Nicht verbunden", None)
        )
        self.btnConnectNDStage.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Verbinden", None)
        )
        self.btnHomeNDStage.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Referenzfahrt (Home)", None)
        )
        self.lblNDPosition.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Position: \u2013 mm", None)
        )
        self.gbPM400.setTitle(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog", "PM400 A (Referenz, S120C)", None
            )
        )
        self.lblPMResource.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "VISA:", None)
        )
        self.btnRefreshPM400.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Aktualisieren", None)
        )
        self.lblPM400Status.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Nicht verbunden", None)
        )
        self.btnConnectPM400.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Verbinden", None)
        )
        self.btnZeroPM400.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Nullabgleich (Zero)", None)
        )
        self.gbPM400B.setTitle(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog", "PM400 B (Vergleichsmessger\u00e4t)", None
            )
        )
        self.lblPM400BResource.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "VISA:", None)
        )
        self.btnRefreshPM400B.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Aktualisieren", None)
        )
        self.lblPM400BStatus.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Nicht verbunden", None)
        )
        self.btnConnectPM400B.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Verbinden", None)
        )
        self.btnZeroPM400B.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Nullabgleich (Zero)", None)
        )
        self.gbIntensitySource.setTitle(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Intensit\u00e4tsquelle", None)
        )
        self.lblIntensitySource.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Quelle:", None)
        )
        self.radioSourcePolariser.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Polarisator", None)
        )
        self.radioSourceND.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "ND-Filter", None)
        )
        self.gbAlignment.setTitle(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog", "Polarisator-Ausrichtung", None
            )
        )
        self.lblAlignStart.setText(
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
        self.lblAlignEnd.setText(
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
        self.lblAlignNPoints.setText(
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
        self.lblAlignSettle.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Wartezeit (s):", None)
        )
        self.btnAlignPolariser.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Ausrichtung starten", None)
        )
        self.btnAbortAlign.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Abbrechen", None)
        )
        self.lblAngleOffset.setText(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog", "Winkelversatz: nicht gesetzt", None
            )
        )
        self.gbBeam.setTitle(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog", "Licht / Leistungsmessung", None
            )
        )
        self.lblWavelength.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Wellenl\u00e4nge (nm):", None)
        )
        self.lblAttenuation.setText(
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
        self.lblPmAveraging.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "PM400 Mittelwerte:", None)
        )
        self.gbSweep.setTitle(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Sweep-Einstellungen", None)
        )
        self.lblAngleStart.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Startwinkel (\u00b0):", None)
        )
        self.lblAngleEnd.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Endwinkel (\u00b0):", None)
        )
        self.lblNPoints.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Anzahl Punkte:", None)
        )
        self.lblPointSettle.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Wartezeit / Punkt (s):", None)
        )
        self.lblGainSettle.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Wartezeit / Gain (s):", None)
        )
        self.lblDetectorSamples.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Detektor-Samples:", None)
        )
        self.lblSaturationThreshold.setText(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog", "S\u00e4ttigungsschwelle (V):", None
            )
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
        self.lblGridMode.setText(
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
        self.lblGains.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Gain-Stufen:", None)
        )
        self.chkGain1.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", "1", None))
        self.chkGain2.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", "2", None))
        self.chkGain3.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", "3", None))
        self.chkGain4.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", "4", None))
        self.gbPowerGrid.setTitle(
            QCoreApplication.translate(
                "AutoPowerCalibrationDialog", "Leistungsraster (nur ND-Filter)", None
            )
        )
        self.lblPowerGridMode.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Rastermodus:", None)
        )
        self.radioGridLogPower.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Log", None)
        )
        self.radioGridLinearPower.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Linear", None)
        )
        self.lblPowerTolerancePct.setText(
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
        self.lblMaxRefineSteps.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Max. Nachjustierungen:", None)
        )
        self.gbProfile.setTitle(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Profil", None)
        )
        self.lblProfileName.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Profilname:", None)
        )
        self.lineProfileName.setPlaceholderText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "z.B. Det-A_auto", None)
        )
        self.lblOutputPath.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "\u2013", None)
        )
        self.btnStart.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Starten", None)
        )
        self.btnAbort.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Abbrechen", None)
        )
        self.btnSave.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Profil speichern", None)
        )
        self.tabsMode.setTabText(
            self.tabsMode.indexOf(self.tabCalibration),
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Kalibrierung", None),
        )
        self.gbNDScanParams.setTitle(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Scan-Parameter", None)
        )
        self.lblNDScanStart.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Start (mm):", None)
        )
        self.lblNDScanEnd.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Ende (mm):", None)
        )
        self.lblNDScanPoints.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Punkte:", None)
        )
        self.lblNDScanSettle.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Wartezeit (s):", None)
        )
        self.lblNDDarkFloor.setText(
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
        self.btnScanNDRange.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Bereichsscan starten", None)
        )
        self.btnAbortNDScan.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Abbrechen", None)
        )
        self.lblNDRange.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Bereich: \u2013", None)
        )
        self.tabsMode.setTabText(
            self.tabsMode.indexOf(self.tabNDRange),
            QCoreApplication.translate("AutoPowerCalibrationDialog", "ND-Bereich", None),
        )
        self.gbXCheckParams.setTitle(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Vergleichs-Parameter", None)
        )
        self.lblXCheckPoints.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Punkte:", None)
        )
        self.lblXCheckSettle.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Wartezeit (s):", None)
        )
        self.lblXCheckTolerance.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Toleranz (%):", None)
        )
        self.btnStartXCheck.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Vergleich starten", None)
        )
        self.btnAbortXCheck.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Abbrechen", None)
        )
        self.btnSaveXCheck.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Ergebnis speichern", None)
        )
        self.lblXCheckResult.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Ergebnis: \u2013", None)
        )
        self.tabsMode.setTabText(
            self.tabsMode.indexOf(self.tabDetectorCompare),
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Detektor-Vergleich", None),
        )
        self.gbVerifyParams.setTitle(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Pr\u00fcf-Parameter", None)
        )
        self.lblVerifyLevels.setText(
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
        self.lblVerifySettle.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Wartezeit (s):", None)
        )
        self.lblVerifyTolerancePct.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Toleranz (%):", None)
        )
        self.btnStartVerify.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Pr\u00fcfung starten", None)
        )
        self.btnAbortVerify.setText(
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
        self.lblVerifyResult.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Ergebnis: \u2013", None)
        )
        self.tabsMode.setTabText(
            self.tabsMode.indexOf(self.tabGainVerify),
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Gain-Pr\u00fcfung", None),
        )
        self.lblPhase.setText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Bereit", None)
        )
        self.plainTextLog.setPlaceholderText(
            QCoreApplication.translate("AutoPowerCalibrationDialog", "Log-Ausgabe\u2026", None)
        )

    # retranslateUi
