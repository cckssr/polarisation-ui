# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'auto_power_calibration.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog,
    QDoubleSpinBox, QFormLayout, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QPlainTextEdit,
    QProgressBar, QPushButton, QRadioButton, QSizePolicy,
    QSpacerItem, QSpinBox, QVBoxLayout, QWidget)

from polarisation_ui.ui.widgets.multi_gain_calibration_plot import MultiGainCalibrationPlot

class Ui_AutoPowerCalibrationDialog(object):
    def setupUi(self, AutoPowerCalibrationDialog):
        if not AutoPowerCalibrationDialog.objectName():
            AutoPowerCalibrationDialog.setObjectName(u"AutoPowerCalibrationDialog")
        AutoPowerCalibrationDialog.resize(1100, 660)
        self.mainLayout = QVBoxLayout(AutoPowerCalibrationDialog)
        self.mainLayout.setSpacing(6)
        self.mainLayout.setObjectName(u"mainLayout")
        self.mainLayout.setContentsMargins(8, 8, 8, 8)
        self.gbConnections = QGroupBox(AutoPowerCalibrationDialog)
        self.gbConnections.setObjectName(u"gbConnections")
        self.connectionsLayout = QHBoxLayout(self.gbConnections)
        self.connectionsLayout.setSpacing(6)
        self.connectionsLayout.setObjectName(u"connectionsLayout")
        self.connectionsLayout.setContentsMargins(6, 4, 6, 6)
        self.gbArduino = QGroupBox(self.gbConnections)
        self.gbArduino.setObjectName(u"gbArduino")
        self.arduinoGrid = QGridLayout(self.gbArduino)
        self.arduinoGrid.setSpacing(4)
        self.arduinoGrid.setObjectName(u"arduinoGrid")
        self.lblArduinoPort = QLabel(self.gbArduino)
        self.lblArduinoPort.setObjectName(u"lblArduinoPort")

        self.arduinoGrid.addWidget(self.lblArduinoPort, 0, 0, 1, 1)

        self.comboArduinoPort = QComboBox(self.gbArduino)
        self.comboArduinoPort.setObjectName(u"comboArduinoPort")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboArduinoPort.sizePolicy().hasHeightForWidth())
        self.comboArduinoPort.setSizePolicy(sizePolicy)

        self.arduinoGrid.addWidget(self.comboArduinoPort, 0, 1, 1, 1)

        self.btnRefreshArduino = QPushButton(self.gbArduino)
        self.btnRefreshArduino.setObjectName(u"btnRefreshArduino")

        self.arduinoGrid.addWidget(self.btnRefreshArduino, 0, 2, 1, 1)

        self.lblArduinoStatus = QLabel(self.gbArduino)
        self.lblArduinoStatus.setObjectName(u"lblArduinoStatus")

        self.arduinoGrid.addWidget(self.lblArduinoStatus, 1, 0, 1, 2)

        self.btnConnectArduino = QPushButton(self.gbArduino)
        self.btnConnectArduino.setObjectName(u"btnConnectArduino")

        self.arduinoGrid.addWidget(self.btnConnectArduino, 1, 2, 1, 1)


        self.connectionsLayout.addWidget(self.gbArduino)

        self.gbKDC = QGroupBox(self.gbConnections)
        self.gbKDC.setObjectName(u"gbKDC")
        self.kdcGrid = QGridLayout(self.gbKDC)
        self.kdcGrid.setSpacing(4)
        self.kdcGrid.setObjectName(u"kdcGrid")
        self.lblKDCDevice = QLabel(self.gbKDC)
        self.lblKDCDevice.setObjectName(u"lblKDCDevice")

        self.kdcGrid.addWidget(self.lblKDCDevice, 0, 0, 1, 1)

        self.comboKDC = QComboBox(self.gbKDC)
        self.comboKDC.setObjectName(u"comboKDC")
        sizePolicy.setHeightForWidth(self.comboKDC.sizePolicy().hasHeightForWidth())
        self.comboKDC.setSizePolicy(sizePolicy)

        self.kdcGrid.addWidget(self.comboKDC, 0, 1, 1, 1)

        self.btnRefreshKDC = QPushButton(self.gbKDC)
        self.btnRefreshKDC.setObjectName(u"btnRefreshKDC")

        self.kdcGrid.addWidget(self.btnRefreshKDC, 0, 2, 1, 1)

        self.lblKDCStatus = QLabel(self.gbKDC)
        self.lblKDCStatus.setObjectName(u"lblKDCStatus")

        self.kdcGrid.addWidget(self.lblKDCStatus, 1, 0, 1, 2)

        self.btnConnectKDC = QPushButton(self.gbKDC)
        self.btnConnectKDC.setObjectName(u"btnConnectKDC")

        self.kdcGrid.addWidget(self.btnConnectKDC, 1, 2, 1, 1)

        self.btnHomeKDC = QPushButton(self.gbKDC)
        self.btnHomeKDC.setObjectName(u"btnHomeKDC")
        self.btnHomeKDC.setEnabled(False)

        self.kdcGrid.addWidget(self.btnHomeKDC, 2, 0, 1, 3)


        self.connectionsLayout.addWidget(self.gbKDC)

        self.gbPM400 = QGroupBox(self.gbConnections)
        self.gbPM400.setObjectName(u"gbPM400")
        self.pmGrid = QGridLayout(self.gbPM400)
        self.pmGrid.setSpacing(4)
        self.pmGrid.setObjectName(u"pmGrid")
        self.lblPMResource = QLabel(self.gbPM400)
        self.lblPMResource.setObjectName(u"lblPMResource")

        self.pmGrid.addWidget(self.lblPMResource, 0, 0, 1, 1)

        self.comboPM400 = QComboBox(self.gbPM400)
        self.comboPM400.setObjectName(u"comboPM400")
        sizePolicy.setHeightForWidth(self.comboPM400.sizePolicy().hasHeightForWidth())
        self.comboPM400.setSizePolicy(sizePolicy)
        self.comboPM400.setEditable(True)

        self.pmGrid.addWidget(self.comboPM400, 0, 1, 1, 1)

        self.btnRefreshPM400 = QPushButton(self.gbPM400)
        self.btnRefreshPM400.setObjectName(u"btnRefreshPM400")

        self.pmGrid.addWidget(self.btnRefreshPM400, 0, 2, 1, 1)

        self.lblPM400Status = QLabel(self.gbPM400)
        self.lblPM400Status.setObjectName(u"lblPM400Status")

        self.pmGrid.addWidget(self.lblPM400Status, 1, 0, 1, 2)

        self.btnConnectPM400 = QPushButton(self.gbPM400)
        self.btnConnectPM400.setObjectName(u"btnConnectPM400")

        self.pmGrid.addWidget(self.btnConnectPM400, 1, 2, 1, 1)

        self.btnZeroPM400 = QPushButton(self.gbPM400)
        self.btnZeroPM400.setObjectName(u"btnZeroPM400")
        self.btnZeroPM400.setEnabled(False)

        self.pmGrid.addWidget(self.btnZeroPM400, 2, 0, 1, 3)


        self.connectionsLayout.addWidget(self.gbPM400)


        self.mainLayout.addWidget(self.gbConnections)

        self.workAreaLayout = QHBoxLayout()
        self.workAreaLayout.setSpacing(8)
        self.workAreaLayout.setObjectName(u"workAreaLayout")
        self.leftPanelLayout = QVBoxLayout()
        self.leftPanelLayout.setSpacing(5)
        self.leftPanelLayout.setObjectName(u"leftPanelLayout")
        self.topControlsRow = QHBoxLayout()
        self.topControlsRow.setSpacing(5)
        self.topControlsRow.setObjectName(u"topControlsRow")
        self.gbAlignment = QGroupBox(AutoPowerCalibrationDialog)
        self.gbAlignment.setObjectName(u"gbAlignment")
        self.alignLayout = QVBoxLayout(self.gbAlignment)
        self.alignLayout.setSpacing(3)
        self.alignLayout.setObjectName(u"alignLayout")
        self.alignForm = QFormLayout()
        self.alignForm.setObjectName(u"alignForm")
        self.alignForm.setVerticalSpacing(3)
        self.lblAlignStart = QLabel(self.gbAlignment)
        self.lblAlignStart.setObjectName(u"lblAlignStart")

        self.alignForm.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lblAlignStart)

        self.spinAlignStart = QDoubleSpinBox(self.gbAlignment)
        self.spinAlignStart.setObjectName(u"spinAlignStart")
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
        self.lblAlignEnd.setObjectName(u"lblAlignEnd")

        self.alignForm.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lblAlignEnd)

        self.spinAlignEnd = QDoubleSpinBox(self.gbAlignment)
        self.spinAlignEnd.setObjectName(u"spinAlignEnd")
        sizePolicy1.setHeightForWidth(self.spinAlignEnd.sizePolicy().hasHeightForWidth())
        self.spinAlignEnd.setSizePolicy(sizePolicy1)
        self.spinAlignEnd.setDecimals(1)
        self.spinAlignEnd.setMinimum(0.000000000000000)
        self.spinAlignEnd.setMaximum(360.000000000000000)
        self.spinAlignEnd.setValue(180.000000000000000)

        self.alignForm.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spinAlignEnd)

        self.lblAlignNPoints = QLabel(self.gbAlignment)
        self.lblAlignNPoints.setObjectName(u"lblAlignNPoints")

        self.alignForm.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lblAlignNPoints)

        self.spinAlignNPoints = QSpinBox(self.gbAlignment)
        self.spinAlignNPoints.setObjectName(u"spinAlignNPoints")
        sizePolicy1.setHeightForWidth(self.spinAlignNPoints.sizePolicy().hasHeightForWidth())
        self.spinAlignNPoints.setSizePolicy(sizePolicy1)
        self.spinAlignNPoints.setMinimum(3)
        self.spinAlignNPoints.setMaximum(360)
        self.spinAlignNPoints.setValue(36)

        self.alignForm.setWidget(2, QFormLayout.ItemRole.FieldRole, self.spinAlignNPoints)

        self.lblAlignSettle = QLabel(self.gbAlignment)
        self.lblAlignSettle.setObjectName(u"lblAlignSettle")

        self.alignForm.setWidget(3, QFormLayout.ItemRole.LabelRole, self.lblAlignSettle)

        self.spinAlignSettle = QDoubleSpinBox(self.gbAlignment)
        self.spinAlignSettle.setObjectName(u"spinAlignSettle")
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
        self.alignButtonLayout.setObjectName(u"alignButtonLayout")
        self.btnAlignPolariser = QPushButton(self.gbAlignment)
        self.btnAlignPolariser.setObjectName(u"btnAlignPolariser")
        self.btnAlignPolariser.setEnabled(False)

        self.alignButtonLayout.addWidget(self.btnAlignPolariser)

        self.btnAbortAlign = QPushButton(self.gbAlignment)
        self.btnAbortAlign.setObjectName(u"btnAbortAlign")
        self.btnAbortAlign.setEnabled(False)

        self.alignButtonLayout.addWidget(self.btnAbortAlign)


        self.alignLayout.addLayout(self.alignButtonLayout)

        self.lblAngleOffset = QLabel(self.gbAlignment)
        self.lblAngleOffset.setObjectName(u"lblAngleOffset")
        self.lblAngleOffset.setWordWrap(True)

        self.alignLayout.addWidget(self.lblAngleOffset)


        self.topControlsRow.addWidget(self.gbAlignment)

        self.gbBeam = QGroupBox(AutoPowerCalibrationDialog)
        self.gbBeam.setObjectName(u"gbBeam")
        self.beamForm = QFormLayout(self.gbBeam)
        self.beamForm.setObjectName(u"beamForm")
        self.beamForm.setVerticalSpacing(3)
        self.lblWavelength = QLabel(self.gbBeam)
        self.lblWavelength.setObjectName(u"lblWavelength")

        self.beamForm.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lblWavelength)

        self.spinWavelength = QDoubleSpinBox(self.gbBeam)
        self.spinWavelength.setObjectName(u"spinWavelength")
        sizePolicy1.setHeightForWidth(self.spinWavelength.sizePolicy().hasHeightForWidth())
        self.spinWavelength.setSizePolicy(sizePolicy1)
        self.spinWavelength.setDecimals(1)
        self.spinWavelength.setMinimum(200.000000000000000)
        self.spinWavelength.setMaximum(1100.000000000000000)
        self.spinWavelength.setValue(633.000000000000000)

        self.beamForm.setWidget(0, QFormLayout.ItemRole.FieldRole, self.spinWavelength)

        self.lblAttenuation = QLabel(self.gbBeam)
        self.lblAttenuation.setObjectName(u"lblAttenuation")

        self.beamForm.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lblAttenuation)

        self.spinAttenuation = QDoubleSpinBox(self.gbBeam)
        self.spinAttenuation.setObjectName(u"spinAttenuation")
        sizePolicy1.setHeightForWidth(self.spinAttenuation.sizePolicy().hasHeightForWidth())
        self.spinAttenuation.setSizePolicy(sizePolicy1)
        self.spinAttenuation.setDecimals(3)
        self.spinAttenuation.setMinimum(-60.000000000000000)
        self.spinAttenuation.setMaximum(90.000000000000000)
        self.spinAttenuation.setSingleStep(0.100000000000000)
        self.spinAttenuation.setValue(3.000000000000000)

        self.beamForm.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spinAttenuation)

        self.lblPmAveraging = QLabel(self.gbBeam)
        self.lblPmAveraging.setObjectName(u"lblPmAveraging")

        self.beamForm.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lblPmAveraging)

        self.spinPmAveraging = QSpinBox(self.gbBeam)
        self.spinPmAveraging.setObjectName(u"spinPmAveraging")
        sizePolicy1.setHeightForWidth(self.spinPmAveraging.sizePolicy().hasHeightForWidth())
        self.spinPmAveraging.setSizePolicy(sizePolicy1)
        self.spinPmAveraging.setMinimum(1)
        self.spinPmAveraging.setMaximum(300000)
        self.spinPmAveraging.setValue(100)

        self.beamForm.setWidget(2, QFormLayout.ItemRole.FieldRole, self.spinPmAveraging)


        self.topControlsRow.addWidget(self.gbBeam)


        self.leftPanelLayout.addLayout(self.topControlsRow)

        self.gbSweep = QGroupBox(AutoPowerCalibrationDialog)
        self.gbSweep.setObjectName(u"gbSweep")
        self.sweepLayout = QVBoxLayout(self.gbSweep)
        self.sweepLayout.setSpacing(3)
        self.sweepLayout.setObjectName(u"sweepLayout")
        self.sweepForm = QFormLayout()
        self.sweepForm.setObjectName(u"sweepForm")
        self.sweepForm.setVerticalSpacing(3)
        self.lblAngleStart = QLabel(self.gbSweep)
        self.lblAngleStart.setObjectName(u"lblAngleStart")

        self.sweepForm.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lblAngleStart)

        self.spinAngleStart = QDoubleSpinBox(self.gbSweep)
        self.spinAngleStart.setObjectName(u"spinAngleStart")
        sizePolicy1.setHeightForWidth(self.spinAngleStart.sizePolicy().hasHeightForWidth())
        self.spinAngleStart.setSizePolicy(sizePolicy1)
        self.spinAngleStart.setDecimals(1)
        self.spinAngleStart.setMinimum(0.000000000000000)
        self.spinAngleStart.setMaximum(360.000000000000000)
        self.spinAngleStart.setValue(0.000000000000000)

        self.sweepForm.setWidget(0, QFormLayout.ItemRole.FieldRole, self.spinAngleStart)

        self.lblAngleEnd = QLabel(self.gbSweep)
        self.lblAngleEnd.setObjectName(u"lblAngleEnd")

        self.sweepForm.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lblAngleEnd)

        self.spinAngleEnd = QDoubleSpinBox(self.gbSweep)
        self.spinAngleEnd.setObjectName(u"spinAngleEnd")
        sizePolicy1.setHeightForWidth(self.spinAngleEnd.sizePolicy().hasHeightForWidth())
        self.spinAngleEnd.setSizePolicy(sizePolicy1)
        self.spinAngleEnd.setDecimals(1)
        self.spinAngleEnd.setMinimum(0.000000000000000)
        self.spinAngleEnd.setMaximum(360.000000000000000)
        self.spinAngleEnd.setValue(90.000000000000000)

        self.sweepForm.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spinAngleEnd)

        self.lblNPoints = QLabel(self.gbSweep)
        self.lblNPoints.setObjectName(u"lblNPoints")

        self.sweepForm.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lblNPoints)

        self.spinNPoints = QSpinBox(self.gbSweep)
        self.spinNPoints.setObjectName(u"spinNPoints")
        sizePolicy1.setHeightForWidth(self.spinNPoints.sizePolicy().hasHeightForWidth())
        self.spinNPoints.setSizePolicy(sizePolicy1)
        self.spinNPoints.setMinimum(3)
        self.spinNPoints.setMaximum(200)
        self.spinNPoints.setValue(30)

        self.sweepForm.setWidget(2, QFormLayout.ItemRole.FieldRole, self.spinNPoints)

        self.lblPointSettle = QLabel(self.gbSweep)
        self.lblPointSettle.setObjectName(u"lblPointSettle")

        self.sweepForm.setWidget(3, QFormLayout.ItemRole.LabelRole, self.lblPointSettle)

        self.spinPointSettle = QDoubleSpinBox(self.gbSweep)
        self.spinPointSettle.setObjectName(u"spinPointSettle")
        sizePolicy1.setHeightForWidth(self.spinPointSettle.sizePolicy().hasHeightForWidth())
        self.spinPointSettle.setSizePolicy(sizePolicy1)
        self.spinPointSettle.setDecimals(2)
        self.spinPointSettle.setMinimum(0.000000000000000)
        self.spinPointSettle.setMaximum(30.000000000000000)
        self.spinPointSettle.setSingleStep(0.050000000000000)
        self.spinPointSettle.setValue(0.200000000000000)

        self.sweepForm.setWidget(3, QFormLayout.ItemRole.FieldRole, self.spinPointSettle)

        self.lblGainSettle = QLabel(self.gbSweep)
        self.lblGainSettle.setObjectName(u"lblGainSettle")

        self.sweepForm.setWidget(4, QFormLayout.ItemRole.LabelRole, self.lblGainSettle)

        self.spinGainSettle = QDoubleSpinBox(self.gbSweep)
        self.spinGainSettle.setObjectName(u"spinGainSettle")
        sizePolicy1.setHeightForWidth(self.spinGainSettle.sizePolicy().hasHeightForWidth())
        self.spinGainSettle.setSizePolicy(sizePolicy1)
        self.spinGainSettle.setDecimals(2)
        self.spinGainSettle.setMinimum(0.000000000000000)
        self.spinGainSettle.setMaximum(10.000000000000000)
        self.spinGainSettle.setSingleStep(0.100000000000000)
        self.spinGainSettle.setValue(0.500000000000000)

        self.sweepForm.setWidget(4, QFormLayout.ItemRole.FieldRole, self.spinGainSettle)

        self.lblDetectorSamples = QLabel(self.gbSweep)
        self.lblDetectorSamples.setObjectName(u"lblDetectorSamples")

        self.sweepForm.setWidget(5, QFormLayout.ItemRole.LabelRole, self.lblDetectorSamples)

        self.spinDetectorSamples = QSpinBox(self.gbSweep)
        self.spinDetectorSamples.setObjectName(u"spinDetectorSamples")
        sizePolicy1.setHeightForWidth(self.spinDetectorSamples.sizePolicy().hasHeightForWidth())
        self.spinDetectorSamples.setSizePolicy(sizePolicy1)
        self.spinDetectorSamples.setMinimum(1)
        self.spinDetectorSamples.setMaximum(100)
        self.spinDetectorSamples.setValue(5)

        self.sweepForm.setWidget(5, QFormLayout.ItemRole.FieldRole, self.spinDetectorSamples)

        self.lblSaturationThreshold = QLabel(self.gbSweep)
        self.lblSaturationThreshold.setObjectName(u"lblSaturationThreshold")

        self.sweepForm.setWidget(6, QFormLayout.ItemRole.LabelRole, self.lblSaturationThreshold)

        self.spinSaturationThreshold = QDoubleSpinBox(self.gbSweep)
        self.spinSaturationThreshold.setObjectName(u"spinSaturationThreshold")
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
        self.gridModeLayout.setObjectName(u"gridModeLayout")
        self.lblGridMode = QLabel(self.gbSweep)
        self.lblGridMode.setObjectName(u"lblGridMode")

        self.gridModeLayout.addWidget(self.lblGridMode)

        self.radioLinearAngle = QRadioButton(self.gbSweep)
        self.radioLinearAngle.setObjectName(u"radioLinearAngle")

        self.gridModeLayout.addWidget(self.radioLinearAngle)

        self.radioLinearCos2 = QRadioButton(self.gbSweep)
        self.radioLinearCos2.setObjectName(u"radioLinearCos2")
        self.radioLinearCos2.setChecked(True)

        self.gridModeLayout.addWidget(self.radioLinearCos2)


        self.sweepLayout.addLayout(self.gridModeLayout)

        self.gainCheckboxLayout = QHBoxLayout()
        self.gainCheckboxLayout.setSpacing(6)
        self.gainCheckboxLayout.setObjectName(u"gainCheckboxLayout")
        self.lblGains = QLabel(self.gbSweep)
        self.lblGains.setObjectName(u"lblGains")

        self.gainCheckboxLayout.addWidget(self.lblGains)

        self.chkGain1 = QCheckBox(self.gbSweep)
        self.chkGain1.setObjectName(u"chkGain1")
        self.chkGain1.setChecked(True)

        self.gainCheckboxLayout.addWidget(self.chkGain1)

        self.chkGain2 = QCheckBox(self.gbSweep)
        self.chkGain2.setObjectName(u"chkGain2")
        self.chkGain2.setChecked(True)

        self.gainCheckboxLayout.addWidget(self.chkGain2)

        self.chkGain3 = QCheckBox(self.gbSweep)
        self.chkGain3.setObjectName(u"chkGain3")
        self.chkGain3.setChecked(True)

        self.gainCheckboxLayout.addWidget(self.chkGain3)

        self.chkGain4 = QCheckBox(self.gbSweep)
        self.chkGain4.setObjectName(u"chkGain4")
        self.chkGain4.setChecked(True)

        self.gainCheckboxLayout.addWidget(self.chkGain4)


        self.sweepLayout.addLayout(self.gainCheckboxLayout)


        self.leftPanelLayout.addWidget(self.gbSweep)

        self.gbProfile = QGroupBox(AutoPowerCalibrationDialog)
        self.gbProfile.setObjectName(u"gbProfile")
        self.profileForm = QFormLayout(self.gbProfile)
        self.profileForm.setObjectName(u"profileForm")
        self.profileForm.setVerticalSpacing(3)
        self.lblProfileName = QLabel(self.gbProfile)
        self.lblProfileName.setObjectName(u"lblProfileName")

        self.profileForm.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lblProfileName)

        self.lineProfileName = QLineEdit(self.gbProfile)
        self.lineProfileName.setObjectName(u"lineProfileName")
        sizePolicy1.setHeightForWidth(self.lineProfileName.sizePolicy().hasHeightForWidth())
        self.lineProfileName.setSizePolicy(sizePolicy1)

        self.profileForm.setWidget(0, QFormLayout.ItemRole.FieldRole, self.lineProfileName)

        self.lblOutputPath = QLabel(self.gbProfile)
        self.lblOutputPath.setObjectName(u"lblOutputPath")
        self.lblOutputPath.setWordWrap(True)

        self.profileForm.setWidget(1, QFormLayout.ItemRole.SpanningRole, self.lblOutputPath)


        self.leftPanelLayout.addWidget(self.gbProfile)

        self.controlLayout = QHBoxLayout()
        self.controlLayout.setSpacing(6)
        self.controlLayout.setObjectName(u"controlLayout")
        self.btnStart = QPushButton(AutoPowerCalibrationDialog)
        self.btnStart.setObjectName(u"btnStart")
        self.btnStart.setEnabled(False)

        self.controlLayout.addWidget(self.btnStart)

        self.btnAbort = QPushButton(AutoPowerCalibrationDialog)
        self.btnAbort.setObjectName(u"btnAbort")
        self.btnAbort.setEnabled(False)

        self.controlLayout.addWidget(self.btnAbort)

        self.btnSave = QPushButton(AutoPowerCalibrationDialog)
        self.btnSave.setObjectName(u"btnSave")
        self.btnSave.setEnabled(False)

        self.controlLayout.addWidget(self.btnSave)


        self.leftPanelLayout.addLayout(self.controlLayout)

        self.progressBar = QProgressBar(AutoPowerCalibrationDialog)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(0)
        self.progressBar.setTextVisible(True)

        self.leftPanelLayout.addWidget(self.progressBar)

        self.lblPhase = QLabel(AutoPowerCalibrationDialog)
        self.lblPhase.setObjectName(u"lblPhase")

        self.leftPanelLayout.addWidget(self.lblPhase)

        self.leftSpacer = QSpacerItem(20, 5, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.leftPanelLayout.addItem(self.leftSpacer)


        self.workAreaLayout.addLayout(self.leftPanelLayout)

        self.rightPanelLayout = QVBoxLayout()
        self.rightPanelLayout.setSpacing(5)
        self.rightPanelLayout.setObjectName(u"rightPanelLayout")
        self.plotWidget = MultiGainCalibrationPlot(AutoPowerCalibrationDialog)
        self.plotWidget.setObjectName(u"plotWidget")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(3)
        sizePolicy2.setHeightForWidth(self.plotWidget.sizePolicy().hasHeightForWidth())
        self.plotWidget.setSizePolicy(sizePolicy2)
        self.plotWidget.setMinimumSize(QSize(380, 250))

        self.rightPanelLayout.addWidget(self.plotWidget)

        self.plainTextLog = QPlainTextEdit(AutoPowerCalibrationDialog)
        self.plainTextLog.setObjectName(u"plainTextLog")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(1)
        sizePolicy3.setHeightForWidth(self.plainTextLog.sizePolicy().hasHeightForWidth())
        self.plainTextLog.setSizePolicy(sizePolicy3)
        self.plainTextLog.setMaximumSize(QSize(16777215, 150))
        self.plainTextLog.setReadOnly(True)

        self.rightPanelLayout.addWidget(self.plainTextLog)


        self.workAreaLayout.addLayout(self.rightPanelLayout)


        self.mainLayout.addLayout(self.workAreaLayout)


        self.retranslateUi(AutoPowerCalibrationDialog)

        QMetaObject.connectSlotsByName(AutoPowerCalibrationDialog)
    # setupUi

    def retranslateUi(self, AutoPowerCalibrationDialog):
        AutoPowerCalibrationDialog.setWindowTitle(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Automatische Leistungskalibrierung", None))
        self.gbConnections.setTitle(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Verbindungen", None))
        self.gbArduino.setTitle(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Arduino (Detektor & Gain)", None))
        self.lblArduinoPort.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Port:", None))
        self.btnRefreshArduino.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Aktualisieren", None))
        self.lblArduinoStatus.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Nicht verbunden", None))
        self.btnConnectArduino.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Verbinden", None))
        self.gbKDC.setTitle(QCoreApplication.translate("AutoPowerCalibrationDialog", u"KDC101 Rotationsantrieb (PRM1/MZ8)", None))
        self.lblKDCDevice.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Ger\u00e4t:", None))
        self.btnRefreshKDC.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Aktualisieren", None))
        self.lblKDCStatus.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Nicht verbunden", None))
        self.btnConnectKDC.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Verbinden", None))
        self.btnHomeKDC.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Referenzfahrt (Home)", None))
        self.gbPM400.setTitle(QCoreApplication.translate("AutoPowerCalibrationDialog", u"PM400 Leistungsmessger\u00e4t (S120C)", None))
        self.lblPMResource.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"VISA:", None))
        self.btnRefreshPM400.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Aktualisieren", None))
        self.lblPM400Status.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Nicht verbunden", None))
        self.btnConnectPM400.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Verbinden", None))
        self.btnZeroPM400.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Nullabgleich (Zero)", None))
        self.gbAlignment.setTitle(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Polarisator-Ausrichtung", None))
        self.lblAlignStart.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Scanstart (\u00b0):", None))
#if QT_CONFIG(tooltip)
        self.spinAlignStart.setToolTip(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Startwinkel des Ausrichtungsscans (physikalische Stufenposition)", None))
#endif // QT_CONFIG(tooltip)
        self.lblAlignEnd.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Scanende (\u00b0):", None))
#if QT_CONFIG(tooltip)
        self.spinAlignEnd.setToolTip(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Endwinkel des Ausrichtungsscans. 180\u00b0 deckt eine volle cos\u00b2-Periode ab.", None))
#endif // QT_CONFIG(tooltip)
        self.lblAlignNPoints.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Schritte:", None))
#if QT_CONFIG(tooltip)
        self.spinAlignNPoints.setToolTip(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Anzahl Messpunkte im Ausrichtungsscan (empfohlen: \u226536 f\u00fcr 5\u00b0-Aufl\u00f6sung \u00fcber 180\u00b0)", None))
#endif // QT_CONFIG(tooltip)
        self.lblAlignSettle.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Wartezeit (s):", None))
        self.btnAlignPolariser.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Ausrichtung starten", None))
        self.btnAbortAlign.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Abbrechen", None))
        self.lblAngleOffset.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Winkelversatz: nicht gesetzt", None))
        self.gbBeam.setTitle(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Licht / Leistungsmessung", None))
        self.lblWavelength.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Wellenl\u00e4nge (nm):", None))
        self.lblAttenuation.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Strahlteiler D\u00e4mpfung (dB):", None))
#if QT_CONFIG(tooltip)
        self.spinAttenuation.setToolTip(QCoreApplication.translate("AutoPowerCalibrationDialog", u"D\u00e4mpfung des Strahlteilers in dB. Wird direkt an das PM400 \u00fcbergeben.", None))
#endif // QT_CONFIG(tooltip)
        self.lblPmAveraging.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"PM400 Mittelwerte:", None))
        self.gbSweep.setTitle(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Sweep-Einstellungen", None))
        self.lblAngleStart.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Startwinkel (\u00b0):", None))
        self.lblAngleEnd.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Endwinkel (\u00b0):", None))
        self.lblNPoints.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Anzahl Punkte:", None))
        self.lblPointSettle.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Wartezeit / Punkt (s):", None))
        self.lblGainSettle.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Wartezeit / Gain (s):", None))
        self.lblDetectorSamples.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Detektor-Samples:", None))
        self.lblSaturationThreshold.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"S\u00e4ttigungsschwelle (V):", None))
#if QT_CONFIG(tooltip)
        self.spinSaturationThreshold.setToolTip(QCoreApplication.translate("AutoPowerCalibrationDialog", u"ADC-Spannung ab der ein Messpunkt als ges\u00e4ttigt gilt und nicht aufgezeichnet wird. Typisch ~2.35 V (ADS1220 Vollaussteuerung \u22482.4 V).", None))
#endif // QT_CONFIG(tooltip)
        self.lblGridMode.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Winkelraster:", None))
        self.radioLinearAngle.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Linear in \u03b8", None))
        self.radioLinearCos2.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Linear in cos\u00b2(\u03b8)", None))
        self.lblGains.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Gain-Stufen:", None))
        self.chkGain1.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"1", None))
        self.chkGain2.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"2", None))
        self.chkGain3.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"3", None))
        self.chkGain4.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"4", None))
        self.gbProfile.setTitle(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Profil", None))
        self.lblProfileName.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Profilname:", None))
        self.lineProfileName.setPlaceholderText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"z.B. Det-A_auto", None))
        self.lblOutputPath.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"\u2013", None))
        self.btnStart.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Starten", None))
        self.btnAbort.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Abbrechen", None))
        self.btnSave.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Profil speichern", None))
        self.lblPhase.setText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Bereit", None))
        self.plainTextLog.setPlaceholderText(QCoreApplication.translate("AutoPowerCalibrationDialog", u"Log-Ausgabe\u2026", None))
    # retranslateUi

