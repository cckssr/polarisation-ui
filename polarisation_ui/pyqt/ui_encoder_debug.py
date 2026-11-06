# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'encoder_debug.ui'
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
    QAbstractButton,
    QAbstractSpinBox,
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLCDNumber,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)


class Ui_EncoderDebugDialog(object):
    def setupUi(self, EncoderDebugDialog):
        if not EncoderDebugDialog.objectName():
            EncoderDebugDialog.setObjectName("EncoderDebugDialog")
        EncoderDebugDialog.resize(860, 683)
        self.layoutRoot = QVBoxLayout(EncoderDebugDialog)
        self.layoutRoot.setSpacing(6)
        self.layoutRoot.setObjectName("layoutRoot")
        self.groupConnection = QGroupBox(EncoderDebugDialog)
        self.groupConnection.setObjectName("groupConnection")
        self.layoutConnection = QHBoxLayout(self.groupConnection)
        self.layoutConnection.setObjectName("layoutConnection")
        self.labelPort = QLabel(self.groupConnection)
        self.labelPort.setObjectName("labelPort")

        self.layoutConnection.addWidget(self.labelPort)

        self.comboPort = QComboBox(self.groupConnection)
        self.comboPort.setObjectName("comboPort")
        self.comboPort.setMinimumSize(QSize(160, 0))

        self.layoutConnection.addWidget(self.comboPort)

        self.buttonRefreshPorts = QToolButton(self.groupConnection)
        self.buttonRefreshPorts.setObjectName("buttonRefreshPorts")
        icon = QIcon(QIcon.fromTheme("view-refresh"))
        self.buttonRefreshPorts.setIcon(icon)

        self.layoutConnection.addWidget(self.buttonRefreshPorts)

        self.buttonConnect = QPushButton(self.groupConnection)
        self.buttonConnect.setObjectName("buttonConnect")
        self.buttonConnect.setMinimumSize(QSize(100, 0))

        self.layoutConnection.addWidget(self.buttonConnect)

        self.valueConnectionStatus = QLabel(self.groupConnection)
        self.valueConnectionStatus.setObjectName("valueConnectionStatus")

        self.layoutConnection.addWidget(self.valueConnectionStatus)

        self.spacerConnection = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.layoutConnection.addItem(self.spacerConnection)

        self.layoutRoot.addWidget(self.groupConnection)

        self.groupControl = QGroupBox(EncoderDebugDialog)
        self.groupControl.setObjectName("groupControl")
        self.hlControl = QHBoxLayout(self.groupControl)
        self.hlControl.setObjectName("hlControl")
        self.labelEncoderSelect = QLabel(self.groupControl)
        self.labelEncoderSelect.setObjectName("labelEncoderSelect")

        self.hlControl.addWidget(self.labelEncoderSelect)

        self.comboEncoderSelect = QComboBox(self.groupControl)
        self.comboEncoderSelect.addItem("")
        self.comboEncoderSelect.addItem("")
        self.comboEncoderSelect.addItem("")
        self.comboEncoderSelect.setObjectName("comboEncoderSelect")
        self.comboEncoderSelect.setMinimumSize(QSize(180, 30))

        self.hlControl.addWidget(self.comboEncoderSelect)

        self.checkAutoRefresh = QCheckBox(self.groupControl)
        self.checkAutoRefresh.setObjectName("checkAutoRefresh")
        self.checkAutoRefresh.setChecked(True)

        self.hlControl.addWidget(self.checkAutoRefresh)

        self.spinRefreshInterval = QSpinBox(self.groupControl)
        self.spinRefreshInterval.setObjectName("spinRefreshInterval")
        self.spinRefreshInterval.setMinimum(100)
        self.spinRefreshInterval.setMaximum(5000)
        self.spinRefreshInterval.setSingleStep(100)
        self.spinRefreshInterval.setValue(500)

        self.hlControl.addWidget(self.spinRefreshInterval)

        self.buttonRefresh = QPushButton(self.groupControl)
        self.buttonRefresh.setObjectName("buttonRefresh")
        icon1 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.ViewRefresh))
        self.buttonRefresh.setIcon(icon1)

        self.hlControl.addWidget(self.buttonRefresh)

        self.hspacer_ctrl = QSpacerItem(
            20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.hlControl.addItem(self.hspacer_ctrl)

        self.buttonZeroEncoder = QPushButton(self.groupControl)
        self.buttonZeroEncoder.setObjectName("buttonZeroEncoder")

        self.hlControl.addWidget(self.buttonZeroEncoder)

        self.buttonClearErrorFlag = QPushButton(self.groupControl)
        self.buttonClearErrorFlag.setObjectName("buttonClearErrorFlag")

        self.hlControl.addWidget(self.buttonClearErrorFlag)

        self.layoutRoot.addWidget(self.groupControl)

        self.tabWidget = QTabWidget(EncoderDebugDialog)
        self.tabWidget.setObjectName("tabWidget")
        self.tabMeasurements = QWidget()
        self.tabMeasurements.setObjectName("tabMeasurements")
        self.hlMeasurements = QHBoxLayout(self.tabMeasurements)
        self.hlMeasurements.setObjectName("hlMeasurements")
        self.groupMeasA = QGroupBox(self.tabMeasurements)
        self.groupMeasA.setObjectName("groupMeasA")
        self.formMeasA = QFormLayout(self.groupMeasA)
        self.formMeasA.setObjectName("formMeasA")
        self.formMeasA.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.labelConnA = QLabel(self.groupMeasA)
        self.labelConnA.setObjectName("labelConnA")

        self.formMeasA.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelConnA)

        self.ledConnA = QFrame(self.groupMeasA)
        self.ledConnA.setObjectName("ledConnA")
        self.ledConnA.setMinimumSize(QSize(20, 20))
        self.ledConnA.setMaximumSize(QSize(20, 20))
        self.ledConnA.setFrameShape(QFrame.Shape.Box)

        self.formMeasA.setWidget(0, QFormLayout.ItemRole.FieldRole, self.ledConnA)

        self.labelAngleA = QLabel(self.groupMeasA)
        self.labelAngleA.setObjectName("labelAngleA")

        self.formMeasA.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelAngleA)

        self.lcdAngleA = QLCDNumber(self.groupMeasA)
        self.lcdAngleA.setObjectName("lcdAngleA")
        self.lcdAngleA.setMinimumSize(QSize(150, 50))
        self.lcdAngleA.setSmallDecimalPoint(True)
        self.lcdAngleA.setDigitCount(8)
        self.lcdAngleA.setMode(QLCDNumber.Mode.Dec)

        self.formMeasA.setWidget(1, QFormLayout.ItemRole.FieldRole, self.lcdAngleA)

        self.labelMagnitudeA = QLabel(self.groupMeasA)
        self.labelMagnitudeA.setObjectName("labelMagnitudeA")

        self.formMeasA.setWidget(2, QFormLayout.ItemRole.LabelRole, self.labelMagnitudeA)

        self.lcdMagnitudeA = QLCDNumber(self.groupMeasA)
        self.lcdMagnitudeA.setObjectName("lcdMagnitudeA")
        self.lcdMagnitudeA.setMinimumSize(QSize(150, 50))
        self.lcdMagnitudeA.setSmallDecimalPoint(True)
        self.lcdMagnitudeA.setDigitCount(8)
        self.lcdMagnitudeA.setMode(QLCDNumber.Mode.Dec)

        self.formMeasA.setWidget(2, QFormLayout.ItemRole.FieldRole, self.lcdMagnitudeA)

        self.labelFieldStrengthA = QLabel(self.groupMeasA)
        self.labelFieldStrengthA.setObjectName("labelFieldStrengthA")

        self.formMeasA.setWidget(3, QFormLayout.ItemRole.LabelRole, self.labelFieldStrengthA)

        self.progressMagnitudeA = QProgressBar(self.groupMeasA)
        self.progressMagnitudeA.setObjectName("progressMagnitudeA")
        self.progressMagnitudeA.setMaximum(16383)
        self.progressMagnitudeA.setValue(0)
        self.progressMagnitudeA.setTextVisible(False)

        self.formMeasA.setWidget(3, QFormLayout.ItemRole.FieldRole, self.progressMagnitudeA)

        self.lineSeparatorA = QFrame(self.groupMeasA)
        self.lineSeparatorA.setObjectName("lineSeparatorA")
        self.lineSeparatorA.setMinimumSize(QSize(50, 10))
        self.lineSeparatorA.setFrameShape(QFrame.Shape.HLine)
        self.lineSeparatorA.setFrameShadow(QFrame.Shadow.Sunken)

        self.formMeasA.setWidget(4, QFormLayout.ItemRole.SpanningRole, self.lineSeparatorA)

        self.labelCofA = QLabel(self.groupMeasA)
        self.labelCofA.setObjectName("labelCofA")

        self.formMeasA.setWidget(5, QFormLayout.ItemRole.LabelRole, self.labelCofA)

        self.ledCofA = QFrame(self.groupMeasA)
        self.ledCofA.setObjectName("ledCofA")
        self.ledCofA.setMinimumSize(QSize(20, 20))
        self.ledCofA.setMaximumSize(QSize(20, 20))
        self.ledCofA.setFrameShape(QFrame.Shape.Box)

        self.formMeasA.setWidget(5, QFormLayout.ItemRole.FieldRole, self.ledCofA)

        self.labelCompHA = QLabel(self.groupMeasA)
        self.labelCompHA.setObjectName("labelCompHA")

        self.formMeasA.setWidget(6, QFormLayout.ItemRole.LabelRole, self.labelCompHA)

        self.ledCompHA = QFrame(self.groupMeasA)
        self.ledCompHA.setObjectName("ledCompHA")
        self.ledCompHA.setMinimumSize(QSize(20, 20))
        self.ledCompHA.setMaximumSize(QSize(20, 20))
        self.ledCompHA.setFrameShape(QFrame.Shape.Box)

        self.formMeasA.setWidget(6, QFormLayout.ItemRole.FieldRole, self.ledCompHA)

        self.labelCompLA = QLabel(self.groupMeasA)
        self.labelCompLA.setObjectName("labelCompLA")

        self.formMeasA.setWidget(7, QFormLayout.ItemRole.LabelRole, self.labelCompLA)

        self.ledCompLA = QFrame(self.groupMeasA)
        self.ledCompLA.setObjectName("ledCompLA")
        self.ledCompLA.setMinimumSize(QSize(20, 20))
        self.ledCompLA.setMaximumSize(QSize(20, 20))
        self.ledCompLA.setFrameShape(QFrame.Shape.Box)

        self.formMeasA.setWidget(7, QFormLayout.ItemRole.FieldRole, self.ledCompLA)

        self.labelOcfA = QLabel(self.groupMeasA)
        self.labelOcfA.setObjectName("labelOcfA")

        self.formMeasA.setWidget(8, QFormLayout.ItemRole.LabelRole, self.labelOcfA)

        self.ledOcfA = QFrame(self.groupMeasA)
        self.ledOcfA.setObjectName("ledOcfA")
        self.ledOcfA.setMinimumSize(QSize(20, 20))
        self.ledOcfA.setMaximumSize(QSize(20, 20))
        self.ledOcfA.setFrameShape(QFrame.Shape.Box)

        self.formMeasA.setWidget(8, QFormLayout.ItemRole.FieldRole, self.ledOcfA)

        self.labelErrorA = QLabel(self.groupMeasA)
        self.labelErrorA.setObjectName("labelErrorA")

        self.formMeasA.setWidget(9, QFormLayout.ItemRole.LabelRole, self.labelErrorA)

        self.ledErrorA = QFrame(self.groupMeasA)
        self.ledErrorA.setObjectName("ledErrorA")
        self.ledErrorA.setMinimumSize(QSize(20, 20))
        self.ledErrorA.setMaximumSize(QSize(20, 20))
        self.ledErrorA.setFrameShape(QFrame.Shape.Box)

        self.formMeasA.setWidget(9, QFormLayout.ItemRole.FieldRole, self.ledErrorA)

        self.labelAgcA = QLabel(self.groupMeasA)
        self.labelAgcA.setObjectName("labelAgcA")

        self.formMeasA.setWidget(10, QFormLayout.ItemRole.LabelRole, self.labelAgcA)

        self.layoutAgcA = QHBoxLayout()
        self.layoutAgcA.setObjectName("layoutAgcA")
        self.layoutAgcA.setContentsMargins(-1, -1, 0, -1)
        self.progressAgcA = QProgressBar(self.groupMeasA)
        self.progressAgcA.setObjectName("progressAgcA")
        self.progressAgcA.setMaximum(255)
        self.progressAgcA.setValue(0)

        self.layoutAgcA.addWidget(self.progressAgcA)

        self.spinAgcA = QSpinBox(self.groupMeasA)
        self.spinAgcA.setObjectName("spinAgcA")
        self.spinAgcA.setReadOnly(True)
        self.spinAgcA.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.spinAgcA.setMaximum(255)

        self.layoutAgcA.addWidget(self.spinAgcA)

        self.formMeasA.setLayout(10, QFormLayout.ItemRole.FieldRole, self.layoutAgcA)

        self.hlMeasurements.addWidget(self.groupMeasA)

        self.groupMeasB = QGroupBox(self.tabMeasurements)
        self.groupMeasB.setObjectName("groupMeasB")
        self.formMeasB = QFormLayout(self.groupMeasB)
        self.formMeasB.setObjectName("formMeasB")
        self.formMeasB.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.labelConnB = QLabel(self.groupMeasB)
        self.labelConnB.setObjectName("labelConnB")

        self.formMeasB.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelConnB)

        self.ledConnB = QFrame(self.groupMeasB)
        self.ledConnB.setObjectName("ledConnB")
        self.ledConnB.setMinimumSize(QSize(20, 20))
        self.ledConnB.setMaximumSize(QSize(20, 20))
        self.ledConnB.setFrameShape(QFrame.Shape.Box)

        self.formMeasB.setWidget(0, QFormLayout.ItemRole.FieldRole, self.ledConnB)

        self.labelAngleB = QLabel(self.groupMeasB)
        self.labelAngleB.setObjectName("labelAngleB")

        self.formMeasB.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelAngleB)

        self.lcdAngleB = QLCDNumber(self.groupMeasB)
        self.lcdAngleB.setObjectName("lcdAngleB")
        self.lcdAngleB.setMinimumSize(QSize(150, 50))
        self.lcdAngleB.setSmallDecimalPoint(True)
        self.lcdAngleB.setDigitCount(8)
        self.lcdAngleB.setMode(QLCDNumber.Mode.Dec)

        self.formMeasB.setWidget(1, QFormLayout.ItemRole.FieldRole, self.lcdAngleB)

        self.labelMagnitudeB = QLabel(self.groupMeasB)
        self.labelMagnitudeB.setObjectName("labelMagnitudeB")

        self.formMeasB.setWidget(2, QFormLayout.ItemRole.LabelRole, self.labelMagnitudeB)

        self.lcdMagnitudeB = QLCDNumber(self.groupMeasB)
        self.lcdMagnitudeB.setObjectName("lcdMagnitudeB")
        self.lcdMagnitudeB.setMinimumSize(QSize(150, 50))
        self.lcdMagnitudeB.setSmallDecimalPoint(True)
        self.lcdMagnitudeB.setDigitCount(8)
        self.lcdMagnitudeB.setMode(QLCDNumber.Mode.Dec)

        self.formMeasB.setWidget(2, QFormLayout.ItemRole.FieldRole, self.lcdMagnitudeB)

        self.labelFieldStrengthB = QLabel(self.groupMeasB)
        self.labelFieldStrengthB.setObjectName("labelFieldStrengthB")

        self.formMeasB.setWidget(3, QFormLayout.ItemRole.LabelRole, self.labelFieldStrengthB)

        self.progressMagnitudeB = QProgressBar(self.groupMeasB)
        self.progressMagnitudeB.setObjectName("progressMagnitudeB")
        self.progressMagnitudeB.setMaximum(16383)
        self.progressMagnitudeB.setValue(0)
        self.progressMagnitudeB.setTextVisible(False)

        self.formMeasB.setWidget(3, QFormLayout.ItemRole.FieldRole, self.progressMagnitudeB)

        self.lineSeparatorB = QFrame(self.groupMeasB)
        self.lineSeparatorB.setObjectName("lineSeparatorB")
        self.lineSeparatorB.setMinimumSize(QSize(50, 10))
        self.lineSeparatorB.setFrameShape(QFrame.Shape.HLine)
        self.lineSeparatorB.setFrameShadow(QFrame.Shadow.Sunken)

        self.formMeasB.setWidget(4, QFormLayout.ItemRole.SpanningRole, self.lineSeparatorB)

        self.labelCofB = QLabel(self.groupMeasB)
        self.labelCofB.setObjectName("labelCofB")

        self.formMeasB.setWidget(5, QFormLayout.ItemRole.LabelRole, self.labelCofB)

        self.ledCofB = QFrame(self.groupMeasB)
        self.ledCofB.setObjectName("ledCofB")
        self.ledCofB.setMinimumSize(QSize(20, 20))
        self.ledCofB.setMaximumSize(QSize(20, 20))
        self.ledCofB.setFrameShape(QFrame.Shape.Box)

        self.formMeasB.setWidget(5, QFormLayout.ItemRole.FieldRole, self.ledCofB)

        self.labelCompHB = QLabel(self.groupMeasB)
        self.labelCompHB.setObjectName("labelCompHB")

        self.formMeasB.setWidget(6, QFormLayout.ItemRole.LabelRole, self.labelCompHB)

        self.ledCompHB = QFrame(self.groupMeasB)
        self.ledCompHB.setObjectName("ledCompHB")
        self.ledCompHB.setMinimumSize(QSize(20, 20))
        self.ledCompHB.setMaximumSize(QSize(20, 20))
        self.ledCompHB.setFrameShape(QFrame.Shape.Box)

        self.formMeasB.setWidget(6, QFormLayout.ItemRole.FieldRole, self.ledCompHB)

        self.labelCompLB = QLabel(self.groupMeasB)
        self.labelCompLB.setObjectName("labelCompLB")

        self.formMeasB.setWidget(7, QFormLayout.ItemRole.LabelRole, self.labelCompLB)

        self.ledCompLB = QFrame(self.groupMeasB)
        self.ledCompLB.setObjectName("ledCompLB")
        self.ledCompLB.setMinimumSize(QSize(20, 20))
        self.ledCompLB.setMaximumSize(QSize(20, 20))
        self.ledCompLB.setFrameShape(QFrame.Shape.Box)

        self.formMeasB.setWidget(7, QFormLayout.ItemRole.FieldRole, self.ledCompLB)

        self.labelOcfB = QLabel(self.groupMeasB)
        self.labelOcfB.setObjectName("labelOcfB")

        self.formMeasB.setWidget(8, QFormLayout.ItemRole.LabelRole, self.labelOcfB)

        self.ledOcfB = QFrame(self.groupMeasB)
        self.ledOcfB.setObjectName("ledOcfB")
        self.ledOcfB.setMinimumSize(QSize(20, 20))
        self.ledOcfB.setMaximumSize(QSize(20, 20))
        self.ledOcfB.setFrameShape(QFrame.Shape.Box)

        self.formMeasB.setWidget(8, QFormLayout.ItemRole.FieldRole, self.ledOcfB)

        self.labelErrorB = QLabel(self.groupMeasB)
        self.labelErrorB.setObjectName("labelErrorB")

        self.formMeasB.setWidget(9, QFormLayout.ItemRole.LabelRole, self.labelErrorB)

        self.ledErrorB = QFrame(self.groupMeasB)
        self.ledErrorB.setObjectName("ledErrorB")
        self.ledErrorB.setMinimumSize(QSize(20, 20))
        self.ledErrorB.setMaximumSize(QSize(20, 20))
        self.ledErrorB.setFrameShape(QFrame.Shape.Box)

        self.formMeasB.setWidget(9, QFormLayout.ItemRole.FieldRole, self.ledErrorB)

        self.labelAgcB = QLabel(self.groupMeasB)
        self.labelAgcB.setObjectName("labelAgcB")

        self.formMeasB.setWidget(10, QFormLayout.ItemRole.LabelRole, self.labelAgcB)

        self.layoutAgcB = QHBoxLayout()
        self.layoutAgcB.setObjectName("layoutAgcB")
        self.layoutAgcB.setContentsMargins(-1, -1, 0, -1)
        self.progressAgcB = QProgressBar(self.groupMeasB)
        self.progressAgcB.setObjectName("progressAgcB")
        self.progressAgcB.setMaximum(255)
        self.progressAgcB.setValue(0)

        self.layoutAgcB.addWidget(self.progressAgcB)

        self.spinAgcB = QSpinBox(self.groupMeasB)
        self.spinAgcB.setObjectName("spinAgcB")
        self.spinAgcB.setReadOnly(True)
        self.spinAgcB.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.spinAgcB.setMaximum(255)

        self.layoutAgcB.addWidget(self.spinAgcB)

        self.formMeasB.setLayout(10, QFormLayout.ItemRole.FieldRole, self.layoutAgcB)

        self.hlMeasurements.addWidget(self.groupMeasB)

        self.tabWidget.addTab(self.tabMeasurements, "")
        self.tabSystem = QWidget()
        self.tabSystem.setObjectName("tabSystem")
        self.vlSystem = QVBoxLayout(self.tabSystem)
        self.vlSystem.setObjectName("vlSystem")
        self.groupSysInfo = QGroupBox(self.tabSystem)
        self.groupSysInfo.setObjectName("groupSysInfo")
        self.formSysInfo = QFormLayout(self.groupSysInfo)
        self.formSysInfo.setObjectName("formSysInfo")
        self.formSysInfo.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.labelIdn = QLabel(self.groupSysInfo)
        self.labelIdn.setObjectName("labelIdn")

        self.formSysInfo.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelIdn)

        self.editIdn = QLineEdit(self.groupSysInfo)
        self.editIdn.setObjectName("editIdn")
        self.editIdn.setReadOnly(True)

        self.formSysInfo.setWidget(0, QFormLayout.ItemRole.FieldRole, self.editIdn)

        self.labelPollInterval = QLabel(self.groupSysInfo)
        self.labelPollInterval.setObjectName("labelPollInterval")

        self.formSysInfo.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelPollInterval)

        self.spinPollInterval = QSpinBox(self.groupSysInfo)
        self.spinPollInterval.setObjectName("spinPollInterval")
        self.spinPollInterval.setReadOnly(True)
        self.spinPollInterval.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.spinPollInterval.setMaximum(9999)

        self.formSysInfo.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spinPollInterval)

        self.labelDebugMode = QLabel(self.groupSysInfo)
        self.labelDebugMode.setObjectName("labelDebugMode")

        self.formSysInfo.setWidget(2, QFormLayout.ItemRole.LabelRole, self.labelDebugMode)

        self.checkDebugMode = QCheckBox(self.groupSysInfo)
        self.checkDebugMode.setObjectName("checkDebugMode")

        self.formSysInfo.setWidget(2, QFormLayout.ItemRole.FieldRole, self.checkDebugMode)

        self.labelSampleInverted = QLabel(self.groupSysInfo)
        self.labelSampleInverted.setObjectName("labelSampleInverted")

        self.formSysInfo.setWidget(3, QFormLayout.ItemRole.LabelRole, self.labelSampleInverted)

        self.checkSampleInverted = QCheckBox(self.groupSysInfo)
        self.checkSampleInverted.setObjectName("checkSampleInverted")
        self.checkSampleInverted.setEnabled(False)

        self.formSysInfo.setWidget(3, QFormLayout.ItemRole.FieldRole, self.checkSampleInverted)

        self.vlSystem.addWidget(self.groupSysInfo)

        self.groupScpiErrors = QGroupBox(self.tabSystem)
        self.groupScpiErrors.setObjectName("groupScpiErrors")
        self.vlScpiErrors = QVBoxLayout(self.groupScpiErrors)
        self.vlScpiErrors.setObjectName("vlScpiErrors")
        self.editScpiErrors = QTextEdit(self.groupScpiErrors)
        self.editScpiErrors.setObjectName("editScpiErrors")
        self.editScpiErrors.setReadOnly(True)

        self.vlScpiErrors.addWidget(self.editScpiErrors)

        self.hlScpiErrBtns = QHBoxLayout()
        self.hlScpiErrBtns.setObjectName("hlScpiErrBtns")
        self.hspacerErrQ = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.hlScpiErrBtns.addItem(self.hspacerErrQ)

        self.buttonReadScpiErrors = QPushButton(self.groupScpiErrors)
        self.buttonReadScpiErrors.setObjectName("buttonReadScpiErrors")

        self.hlScpiErrBtns.addWidget(self.buttonReadScpiErrors)

        self.buttonClearScpiErrors = QPushButton(self.groupScpiErrors)
        self.buttonClearScpiErrors.setObjectName("buttonClearScpiErrors")

        self.hlScpiErrBtns.addWidget(self.buttonClearScpiErrors)

        self.vlScpiErrors.addLayout(self.hlScpiErrBtns)

        self.vlSystem.addWidget(self.groupScpiErrors)

        self.vspacerSys = QSpacerItem(
            20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.vlSystem.addItem(self.vspacerSys)

        self.tabWidget.addTab(self.tabSystem, "")
        self.tabTerminal = QWidget()
        self.tabTerminal.setObjectName("tabTerminal")
        self.vlTerminal = QVBoxLayout(self.tabTerminal)
        self.vlTerminal.setObjectName("vlTerminal")
        self.editTerminalLog = QTextEdit(self.tabTerminal)
        self.editTerminalLog.setObjectName("editTerminalLog")
        self.editTerminalLog.setReadOnly(True)

        self.vlTerminal.addWidget(self.editTerminalLog)

        self.hlTerminalInput = QHBoxLayout()
        self.hlTerminalInput.setObjectName("hlTerminalInput")
        self.editCommandInput = QLineEdit(self.tabTerminal)
        self.editCommandInput.setObjectName("editCommandInput")

        self.hlTerminalInput.addWidget(self.editCommandInput)

        self.buttonSendCommand = QPushButton(self.tabTerminal)
        self.buttonSendCommand.setObjectName("buttonSendCommand")

        self.hlTerminalInput.addWidget(self.buttonSendCommand)

        self.buttonClearLog = QPushButton(self.tabTerminal)
        self.buttonClearLog.setObjectName("buttonClearLog")

        self.hlTerminalInput.addWidget(self.buttonClearLog)

        self.vlTerminal.addLayout(self.hlTerminalInput)

        self.tabWidget.addTab(self.tabTerminal, "")
        self.tabAds = QWidget()
        self.tabAds.setObjectName("tabAds")
        self.vlAds = QVBoxLayout(self.tabAds)
        self.vlAds.setObjectName("vlAds")
        self.groupAdcLive = QGroupBox(self.tabAds)
        self.groupAdcLive.setObjectName("groupAdcLive")
        self.formAdcLive = QFormLayout(self.groupAdcLive)
        self.formAdcLive.setObjectName("formAdcLive")
        self.labelAdcPresent = QLabel(self.groupAdcLive)
        self.labelAdcPresent.setObjectName("labelAdcPresent")

        self.formAdcLive.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelAdcPresent)

        self.ledAdcPresent = QFrame(self.groupAdcLive)
        self.ledAdcPresent.setObjectName("ledAdcPresent")
        self.ledAdcPresent.setMinimumSize(QSize(20, 20))
        self.ledAdcPresent.setMaximumSize(QSize(20, 20))
        self.ledAdcPresent.setFrameShape(QFrame.Shape.Box)

        self.formAdcLive.setWidget(0, QFormLayout.ItemRole.FieldRole, self.ledAdcPresent)

        self.labelAdcVoltage = QLabel(self.groupAdcLive)
        self.labelAdcVoltage.setObjectName("labelAdcVoltage")

        self.formAdcLive.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelAdcVoltage)

        self.lcdAdcVoltage = QLCDNumber(self.groupAdcLive)
        self.lcdAdcVoltage.setObjectName("lcdAdcVoltage")
        self.lcdAdcVoltage.setMinimumSize(QSize(180, 50))
        self.lcdAdcVoltage.setSmallDecimalPoint(True)
        self.lcdAdcVoltage.setDigitCount(10)

        self.formAdcLive.setWidget(1, QFormLayout.ItemRole.FieldRole, self.lcdAdcVoltage)

        self.labelAdcDrdy = QLabel(self.groupAdcLive)
        self.labelAdcDrdy.setObjectName("labelAdcDrdy")

        self.formAdcLive.setWidget(2, QFormLayout.ItemRole.LabelRole, self.labelAdcDrdy)

        self.ledAdcDrdy = QFrame(self.groupAdcLive)
        self.ledAdcDrdy.setObjectName("ledAdcDrdy")
        self.ledAdcDrdy.setMinimumSize(QSize(20, 20))
        self.ledAdcDrdy.setMaximumSize(QSize(20, 20))
        self.ledAdcDrdy.setFrameShape(QFrame.Shape.Box)

        self.formAdcLive.setWidget(2, QFormLayout.ItemRole.FieldRole, self.ledAdcDrdy)

        self.vlAds.addWidget(self.groupAdcLive)

        self.hlAdsMid = QHBoxLayout()
        self.hlAdsMid.setObjectName("hlAdsMid")
        self.groupAdcRegisters = QGroupBox(self.tabAds)
        self.groupAdcRegisters.setObjectName("groupAdcRegisters")
        self.formAdcRegisters = QFormLayout(self.groupAdcRegisters)
        self.formAdcRegisters.setObjectName("formAdcRegisters")
        self.labelReg0 = QLabel(self.groupAdcRegisters)
        self.labelReg0.setObjectName("labelReg0")

        self.formAdcRegisters.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelReg0)

        self.editReg0 = QLineEdit(self.groupAdcRegisters)
        self.editReg0.setObjectName("editReg0")
        self.editReg0.setReadOnly(True)

        self.formAdcRegisters.setWidget(0, QFormLayout.ItemRole.FieldRole, self.editReg0)

        self.labelReg1 = QLabel(self.groupAdcRegisters)
        self.labelReg1.setObjectName("labelReg1")

        self.formAdcRegisters.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelReg1)

        self.editReg1 = QLineEdit(self.groupAdcRegisters)
        self.editReg1.setObjectName("editReg1")
        self.editReg1.setReadOnly(True)

        self.formAdcRegisters.setWidget(1, QFormLayout.ItemRole.FieldRole, self.editReg1)

        self.labelReg2 = QLabel(self.groupAdcRegisters)
        self.labelReg2.setObjectName("labelReg2")

        self.formAdcRegisters.setWidget(2, QFormLayout.ItemRole.LabelRole, self.labelReg2)

        self.editReg2 = QLineEdit(self.groupAdcRegisters)
        self.editReg2.setObjectName("editReg2")
        self.editReg2.setReadOnly(True)

        self.formAdcRegisters.setWidget(2, QFormLayout.ItemRole.FieldRole, self.editReg2)

        self.labelReg3 = QLabel(self.groupAdcRegisters)
        self.labelReg3.setObjectName("labelReg3")

        self.formAdcRegisters.setWidget(3, QFormLayout.ItemRole.LabelRole, self.labelReg3)

        self.editReg3 = QLineEdit(self.groupAdcRegisters)
        self.editReg3.setObjectName("editReg3")
        self.editReg3.setReadOnly(True)

        self.formAdcRegisters.setWidget(3, QFormLayout.ItemRole.FieldRole, self.editReg3)

        self.labelLastRaw = QLabel(self.groupAdcRegisters)
        self.labelLastRaw.setObjectName("labelLastRaw")

        self.formAdcRegisters.setWidget(4, QFormLayout.ItemRole.LabelRole, self.labelLastRaw)

        self.editLastRaw = QLineEdit(self.groupAdcRegisters)
        self.editLastRaw.setObjectName("editLastRaw")
        self.editLastRaw.setReadOnly(True)

        self.formAdcRegisters.setWidget(4, QFormLayout.ItemRole.FieldRole, self.editLastRaw)

        self.hlAdsMid.addWidget(self.groupAdcRegisters)

        self.groupAdcConfig = QGroupBox(self.tabAds)
        self.groupAdcConfig.setObjectName("groupAdcConfig")
        self.formAdcConfig = QFormLayout(self.groupAdcConfig)
        self.formAdcConfig.setObjectName("formAdcConfig")
        self.labelMux = QLabel(self.groupAdcConfig)
        self.labelMux.setObjectName("labelMux")

        self.formAdcConfig.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelMux)

        self.editMux = QLineEdit(self.groupAdcConfig)
        self.editMux.setObjectName("editMux")
        self.editMux.setReadOnly(True)

        self.formAdcConfig.setWidget(0, QFormLayout.ItemRole.FieldRole, self.editMux)

        self.labelGain = QLabel(self.groupAdcConfig)
        self.labelGain.setObjectName("labelGain")

        self.formAdcConfig.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelGain)

        self.editGain = QLineEdit(self.groupAdcConfig)
        self.editGain.setObjectName("editGain")
        self.editGain.setReadOnly(True)

        self.formAdcConfig.setWidget(1, QFormLayout.ItemRole.FieldRole, self.editGain)

        self.labelRate = QLabel(self.groupAdcConfig)
        self.labelRate.setObjectName("labelRate")

        self.formAdcConfig.setWidget(2, QFormLayout.ItemRole.LabelRole, self.labelRate)

        self.editRate = QLineEdit(self.groupAdcConfig)
        self.editRate.setObjectName("editRate")
        self.editRate.setReadOnly(True)

        self.formAdcConfig.setWidget(2, QFormLayout.ItemRole.FieldRole, self.editRate)

        self.labelMode = QLabel(self.groupAdcConfig)
        self.labelMode.setObjectName("labelMode")

        self.formAdcConfig.setWidget(3, QFormLayout.ItemRole.LabelRole, self.labelMode)

        self.editMode = QLineEdit(self.groupAdcConfig)
        self.editMode.setObjectName("editMode")
        self.editMode.setReadOnly(True)

        self.formAdcConfig.setWidget(3, QFormLayout.ItemRole.FieldRole, self.editMode)

        self.labelFir = QLabel(self.groupAdcConfig)
        self.labelFir.setObjectName("labelFir")

        self.formAdcConfig.setWidget(4, QFormLayout.ItemRole.LabelRole, self.labelFir)

        self.editFir = QLineEdit(self.groupAdcConfig)
        self.editFir.setObjectName("editFir")
        self.editFir.setReadOnly(True)

        self.formAdcConfig.setWidget(4, QFormLayout.ItemRole.FieldRole, self.editFir)

        self.labelVref = QLabel(self.groupAdcConfig)
        self.labelVref.setObjectName("labelVref")

        self.formAdcConfig.setWidget(5, QFormLayout.ItemRole.LabelRole, self.labelVref)

        self.editVref = QLineEdit(self.groupAdcConfig)
        self.editVref.setObjectName("editVref")
        self.editVref.setReadOnly(True)

        self.formAdcConfig.setWidget(5, QFormLayout.ItemRole.FieldRole, self.editVref)

        self.buttonReadAdcConfig = QPushButton(self.groupAdcConfig)
        self.buttonReadAdcConfig.setObjectName("buttonReadAdcConfig")

        self.formAdcConfig.setWidget(6, QFormLayout.ItemRole.SpanningRole, self.buttonReadAdcConfig)

        self.hlAdsMid.addWidget(self.groupAdcConfig)

        self.vlAds.addLayout(self.hlAdsMid)

        self.groupPdtia = QGroupBox(self.tabAds)
        self.groupPdtia.setObjectName("groupPdtia")
        self.formPdtia = QFormLayout(self.groupPdtia)
        self.formPdtia.setObjectName("formPdtia")
        self.labelPdtiaStage = QLabel(self.groupPdtia)
        self.labelPdtiaStage.setObjectName("labelPdtiaStage")

        self.formPdtia.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelPdtiaStage)

        self.editPdtiaStage = QLineEdit(self.groupPdtia)
        self.editPdtiaStage.setObjectName("editPdtiaStage")
        self.editPdtiaStage.setReadOnly(True)

        self.formPdtia.setWidget(0, QFormLayout.ItemRole.FieldRole, self.editPdtiaStage)

        self.labelPdtiaPattern = QLabel(self.groupPdtia)
        self.labelPdtiaPattern.setObjectName("labelPdtiaPattern")

        self.formPdtia.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelPdtiaPattern)

        self.editPdtiaPattern = QLineEdit(self.groupPdtia)
        self.editPdtiaPattern.setObjectName("editPdtiaPattern")
        self.editPdtiaPattern.setReadOnly(True)

        self.formPdtia.setWidget(1, QFormLayout.ItemRole.FieldRole, self.editPdtiaPattern)

        self.vlAds.addWidget(self.groupPdtia)

        self.vspacerAds = QSpacerItem(
            20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.vlAds.addItem(self.vspacerAds)

        self.tabWidget.addTab(self.tabAds, "")
        self.tabRawStream = QWidget()
        self.tabRawStream.setObjectName("tabRawStream")
        self.vlRawStream = QVBoxLayout(self.tabRawStream)
        self.vlRawStream.setObjectName("vlRawStream")
        self.labelRawStreamNotice = QLabel(self.tabRawStream)
        self.labelRawStreamNotice.setObjectName("labelRawStreamNotice")
        self.labelRawStreamNotice.setWordWrap(True)

        self.vlRawStream.addWidget(self.labelRawStreamNotice)

        self.editRawStream = QPlainTextEdit(self.tabRawStream)
        self.editRawStream.setObjectName("editRawStream")
        self.editRawStream.setReadOnly(True)
        font = QFont()
        font.setFamilies(["Monospace"])
        self.editRawStream.setFont(font)
        self.editRawStream.setMaximumBlockCount(500)

        self.vlRawStream.addWidget(self.editRawStream)

        self.hlRawStreamButtons = QHBoxLayout()
        self.hlRawStreamButtons.setObjectName("hlRawStreamButtons")
        self.buttonClearRawStream = QPushButton(self.tabRawStream)
        self.buttonClearRawStream.setObjectName("buttonClearRawStream")

        self.hlRawStreamButtons.addWidget(self.buttonClearRawStream)

        self.hspacerRawStream = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.hlRawStreamButtons.addItem(self.hspacerRawStream)

        self.vlRawStream.addLayout(self.hlRawStreamButtons)

        self.tabWidget.addTab(self.tabRawStream, "")
        self.tabSelfTest = QWidget()
        self.tabSelfTest.setObjectName("tabSelfTest")
        self.vlSelfTest = QVBoxLayout(self.tabSelfTest)
        self.vlSelfTest.setObjectName("vlSelfTest")
        self.labelSelfTestInfo = QLabel(self.tabSelfTest)
        self.labelSelfTestInfo.setObjectName("labelSelfTestInfo")
        self.labelSelfTestInfo.setWordWrap(True)

        self.vlSelfTest.addWidget(self.labelSelfTestInfo)

        self.buttonRunSelfTest = QPushButton(self.tabSelfTest)
        self.buttonRunSelfTest.setObjectName("buttonRunSelfTest")

        self.vlSelfTest.addWidget(self.buttonRunSelfTest)

        self.editSelfTest = QPlainTextEdit(self.tabSelfTest)
        self.editSelfTest.setObjectName("editSelfTest")
        self.editSelfTest.setReadOnly(True)
        self.editSelfTest.setFont(font)

        self.vlSelfTest.addWidget(self.editSelfTest)

        self.tabWidget.addTab(self.tabSelfTest, "")

        self.layoutRoot.addWidget(self.tabWidget)

        self.buttonBox = QDialogButtonBox(EncoderDebugDialog)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Close)

        self.layoutRoot.addWidget(self.buttonBox)

        self.retranslateUi(EncoderDebugDialog)
        self.buttonBox.rejected.connect(EncoderDebugDialog.reject)

        self.tabWidget.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(EncoderDebugDialog)

    # setupUi

    def retranslateUi(self, EncoderDebugDialog):
        EncoderDebugDialog.setWindowTitle(
            QCoreApplication.translate("EncoderDebugDialog", "Encoder Debug", None)
        )
        self.groupConnection.setTitle(
            QCoreApplication.translate("EncoderDebugDialog", "Arduino-Verbindung", None)
        )
        self.labelPort.setText(QCoreApplication.translate("EncoderDebugDialog", "Port:", None))
        self.buttonRefreshPorts.setText(
            QCoreApplication.translate("EncoderDebugDialog", "\u21bb", None)
        )
        # if QT_CONFIG(tooltip)
        self.buttonRefreshPorts.setToolTip(
            QCoreApplication.translate("EncoderDebugDialog", "Ports neu laden", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonConnect.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Verbinden", None)
        )
        self.valueConnectionStatus.setText("")
        self.groupControl.setTitle(
            QCoreApplication.translate("EncoderDebugDialog", "Steuerung", None)
        )
        self.labelEncoderSelect.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Encoder:", None)
        )
        self.comboEncoderSelect.setItemText(
            0, QCoreApplication.translate("EncoderDebugDialog", "A \u2013 Sample", None)
        )
        self.comboEncoderSelect.setItemText(
            1, QCoreApplication.translate("EncoderDebugDialog", "B \u2013 Detektor", None)
        )
        self.comboEncoderSelect.setItemText(
            2, QCoreApplication.translate("EncoderDebugDialog", "Beide", None)
        )

        self.checkAutoRefresh.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Auto-Refresh", None)
        )
        # if QT_CONFIG(tooltip)
        self.spinRefreshInterval.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog", "Refresh-Intervall in Millisekunden", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.spinRefreshInterval.setSuffix(
            QCoreApplication.translate("EncoderDebugDialog", " ms", None)
        )
        # if QT_CONFIG(tooltip)
        self.buttonRefresh.setToolTip(
            QCoreApplication.translate("EncoderDebugDialog", "Alle Werte einmalig abrufen", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonRefresh.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Aktualisieren", None)
        )
        # if QT_CONFIG(tooltip)
        self.buttonZeroEncoder.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog", "Aktuelle Position als Nullpunkt setzen (CONF:ZERO)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonZeroEncoder.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Nullpunkt setzen", None)
        )
        # if QT_CONFIG(tooltip)
        self.buttonClearErrorFlag.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog", "Hardware Error-Flag l\u00f6schen (CONF:ERR)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonClearErrorFlag.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Fehler l\u00f6schen", None)
        )
        self.groupMeasA.setTitle(
            QCoreApplication.translate("EncoderDebugDialog", "Encoder A \u2013 Sample", None)
        )
        self.labelConnA.setText(QCoreApplication.translate("EncoderDebugDialog", "Verbunden", None))
        # if QT_CONFIG(tooltip)
        self.ledConnA.setToolTip(
            QCoreApplication.translate("EncoderDebugDialog", "Verbindungsstatus Encoder A", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.labelAngleA.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Winkel (\u00b0)", None)
        )
        # if QT_CONFIG(tooltip)
        self.lcdAngleA.setToolTip(
            QCoreApplication.translate("EncoderDebugDialog", "Winkel in Grad (MEAS:ANGL? A)", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.labelMagnitudeA.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Magnitude (raw)", None)
        )
        # if QT_CONFIG(tooltip)
        self.lcdMagnitudeA.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog", "Magnitude des Magnetfelds (MEAS:ENC:MAGN? A)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.labelFieldStrengthA.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Feldst\u00e4rke", None)
        )
        # if QT_CONFIG(tooltip)
        self.progressMagnitudeA.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog", "Visuelle Darstellung der Magnet-Amplitude", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.labelCofA.setText(
            QCoreApplication.translate("EncoderDebugDialog", "COF \u2013 CORDIC Overflow", None)
        )
        # if QT_CONFIG(tooltip)
        self.ledCofA.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog",
                "COF: CORDIC Overflow \u2013 Winkelberechnung fehlgeschlagen",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.labelCompHA.setText(
            QCoreApplication.translate("EncoderDebugDialog", "COMP_H \u2013 Feld zu schwach", None)
        )
        # if QT_CONFIG(tooltip)
        self.ledCompHA.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog",
                "COMP_H: Magnetfeld zu schwach (compHigh=1 \u2192 Problem)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.labelCompLA.setText(
            QCoreApplication.translate("EncoderDebugDialog", "COMP_L \u2013 Feld zu stark", None)
        )
        # if QT_CONFIG(tooltip)
        self.ledCompLA.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog", "COMP_L: Magnetfeld zu stark (compLow=1 \u2192 Problem)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.labelOcfA.setText(
            QCoreApplication.translate("EncoderDebugDialog", "OCF \u2013 Sensor bereit", None)
        )
        # if QT_CONFIG(tooltip)
        self.ledOcfA.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog",
                "OCF: Offset Compensation Finished \u2013 1 = Sensor bereit",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.labelErrorA.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Error Flag", None)
        )
        # if QT_CONFIG(tooltip)
        self.ledErrorA.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog",
                "Hardware Error Flag des Sensors (mit CONF:ERR A l\u00f6schbar)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.labelAgcA.setText(
            QCoreApplication.translate("EncoderDebugDialog", "AGC - Automatic Gain Control", None)
        )
        # if QT_CONFIG(tooltip)
        self.progressAgcA.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog",
                "AGC: 0 = max Verst\u00e4rkung (schwaches Feld), 255 = min Verst\u00e4rkung (starkes Feld)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(tooltip)
        self.spinAgcA.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog",
                "Automatic Gain Control 0\u2013255 (niedrig = starkes Feld)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.groupMeasB.setTitle(
            QCoreApplication.translate("EncoderDebugDialog", "Encoder B \u2013 Detektor", None)
        )
        self.labelConnB.setText(QCoreApplication.translate("EncoderDebugDialog", "Verbunden", None))
        # if QT_CONFIG(tooltip)
        self.ledConnB.setToolTip(
            QCoreApplication.translate("EncoderDebugDialog", "Verbindungsstatus Encoder B", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.labelAngleB.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Winkel (\u00b0)", None)
        )
        # if QT_CONFIG(tooltip)
        self.lcdAngleB.setToolTip(
            QCoreApplication.translate("EncoderDebugDialog", "Winkel in Grad (MEAS:ANGL? B)", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.labelMagnitudeB.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Magnitude (raw)", None)
        )
        # if QT_CONFIG(tooltip)
        self.lcdMagnitudeB.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog", "Magnitude des Magnetfelds (MEAS:ENC:MAGN? B)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.labelFieldStrengthB.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Feldst\u00e4rke", None)
        )
        # if QT_CONFIG(tooltip)
        self.progressMagnitudeB.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog", "Visuelle Darstellung der Magnet-Amplitude", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.labelCofB.setText(
            QCoreApplication.translate("EncoderDebugDialog", "COF \u2013 CORDIC Overflow", None)
        )
        # if QT_CONFIG(tooltip)
        self.ledCofB.setToolTip(
            QCoreApplication.translate("EncoderDebugDialog", "COF: CORDIC Overflow", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.labelCompHB.setText(
            QCoreApplication.translate("EncoderDebugDialog", "COMP_H \u2013 Feld zu schwach", None)
        )
        # if QT_CONFIG(tooltip)
        self.ledCompHB.setToolTip(
            QCoreApplication.translate("EncoderDebugDialog", "COMP_H: Magnetfeld zu schwach", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.labelCompLB.setText(
            QCoreApplication.translate("EncoderDebugDialog", "COMP_L \u2013 Feld zu stark", None)
        )
        # if QT_CONFIG(tooltip)
        self.ledCompLB.setToolTip(
            QCoreApplication.translate("EncoderDebugDialog", "COMP_L: Magnetfeld zu stark", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.labelOcfB.setText(
            QCoreApplication.translate("EncoderDebugDialog", "OCF \u2013 Sensor bereit", None)
        )
        # if QT_CONFIG(tooltip)
        self.ledOcfB.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog", "OCF: Sensor bereit (1 = bereit)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.labelErrorB.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Error Flag", None)
        )
        # if QT_CONFIG(tooltip)
        self.ledErrorB.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog", "Hardware Error Flag (mit CONF:ERR B l\u00f6schbar)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.labelAgcB.setText(
            QCoreApplication.translate("EncoderDebugDialog", "AGC - Automatic Gain Control", None)
        )
        # if QT_CONFIG(tooltip)
        self.progressAgcB.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog",
                "AGC: 0 = max Verst\u00e4rkung, 255 = min Verst\u00e4rkung",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(tooltip)
        self.spinAgcB.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog", "Automatic Gain Control 0\u2013255", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tabMeasurements),
            QCoreApplication.translate("EncoderDebugDialog", "Messwerte", None),
        )
        self.groupSysInfo.setTitle(
            QCoreApplication.translate("EncoderDebugDialog", "Ger\u00e4teinformationen", None)
        )
        self.labelIdn.setText(QCoreApplication.translate("EncoderDebugDialog", "IDN (*IDN?)", None))
        # if QT_CONFIG(tooltip)
        self.editIdn.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog", "Ger\u00e4teidentifikation (*IDN?)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.editIdn.setPlaceholderText(
            QCoreApplication.translate("EncoderDebugDialog", "\u2013", None)
        )
        self.labelPollInterval.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Poll-Intervall (SENS:INT?)", None)
        )
        # if QT_CONFIG(tooltip)
        self.spinPollInterval.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog",
                "Aktuelles Abfrageintervall des Arduino in ms (SENS:INT?)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.spinPollInterval.setSuffix(
            QCoreApplication.translate("EncoderDebugDialog", " ms", None)
        )
        self.labelDebugMode.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Debug-Modus (SYST:DEB?)", None)
        )
        # if QT_CONFIG(tooltip)
        self.checkDebugMode.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog", "Arduino Debug-Ausgabe aktiv (SYST:DEB ON/OFF)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.checkDebugMode.setText(QCoreApplication.translate("EncoderDebugDialog", "Aktiv", None))
        self.labelSampleInverted.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Probe invertiert:", None)
        )
        self.groupScpiErrors.setTitle(
            QCoreApplication.translate("EncoderDebugDialog", "SCPI Fehler-Queue (SYST:ERR?)", None)
        )
        # if QT_CONFIG(tooltip)
        self.editScpiErrors.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog", "Inhalt der SCPI Fehler-Queue (SYST:ERR?)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.editScpiErrors.setPlaceholderText(
            QCoreApplication.translate("EncoderDebugDialog", "Keine Fehler", None)
        )
        # if QT_CONFIG(tooltip)
        self.buttonReadScpiErrors.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog", "Alle Eintr\u00e4ge aus der SCPI Fehler-Queue lesen", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonReadScpiErrors.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Queue auslesen", None)
        )
        # if QT_CONFIG(tooltip)
        self.buttonClearScpiErrors.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog", "SCPI Error Queue l\u00f6schen (*CLS)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonClearScpiErrors.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Queue l\u00f6schen (*CLS)", None)
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tabSystem),
            QCoreApplication.translate("EncoderDebugDialog", "System", None),
        )
        # if QT_CONFIG(tooltip)
        self.editTerminalLog.setToolTip(
            QCoreApplication.translate("EncoderDebugDialog", "SCPI Kommunikationslog", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.editTerminalLog.setPlaceholderText(
            QCoreApplication.translate("EncoderDebugDialog", "Bereit\u2026", None)
        )
        # if QT_CONFIG(tooltip)
        self.editCommandInput.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog", "SCPI-Befehl eingeben, z.B.  MEAS:ANGL? A  oder  *IDN?", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.editCommandInput.setPlaceholderText(
            QCoreApplication.translate("EncoderDebugDialog", "SCPI-Befehl, z.B. MEAS:ANGL? A", None)
        )
        # if QT_CONFIG(tooltip)
        self.buttonSendCommand.setToolTip(
            QCoreApplication.translate("EncoderDebugDialog", "Befehl senden (auch Enter)", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonSendCommand.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Senden", None)
        )
        # if QT_CONFIG(tooltip)
        self.buttonClearLog.setToolTip(
            QCoreApplication.translate("EncoderDebugDialog", "Terminal-Log leeren", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonClearLog.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Log leeren", None)
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tabTerminal),
            QCoreApplication.translate("EncoderDebugDialog", "SCPI Terminal", None),
        )
        self.groupAdcLive.setTitle(
            QCoreApplication.translate("EncoderDebugDialog", "Live-Messwerte", None)
        )
        self.labelAdcPresent.setText(
            QCoreApplication.translate("EncoderDebugDialog", "ADS1220 vorhanden:", None)
        )
        # if QT_CONFIG(tooltip)
        self.ledAdcPresent.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog", "ADS1220 antwortet auf DIAG:ADC?", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.labelAdcVoltage.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Spannung (V):", None)
        )
        # if QT_CONFIG(tooltip)
        self.lcdAdcVoltage.setToolTip(
            QCoreApplication.translate("EncoderDebugDialog", "MEAS:ADC:VOLT? (V)", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.labelAdcDrdy.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Bereit (zeitbasiert):", None)
        )
        # if QT_CONFIG(tooltip)
        self.ledAdcDrdy.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog",
                "Zeitbasierte Bereitschaft (DRDY-Pin nicht angeschlossen)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.groupAdcRegisters.setTitle(
            QCoreApplication.translate("EncoderDebugDialog", "Register (DIAG:ADC?)", None)
        )
        self.labelReg0.setText(QCoreApplication.translate("EncoderDebugDialog", "REG0:", None))
        self.editReg0.setPlaceholderText(
            QCoreApplication.translate("EncoderDebugDialog", "\u2013", None)
        )
        self.labelReg1.setText(QCoreApplication.translate("EncoderDebugDialog", "REG1:", None))
        self.editReg1.setPlaceholderText(
            QCoreApplication.translate("EncoderDebugDialog", "\u2013", None)
        )
        self.labelReg2.setText(QCoreApplication.translate("EncoderDebugDialog", "REG2:", None))
        self.editReg2.setPlaceholderText(
            QCoreApplication.translate("EncoderDebugDialog", "\u2013", None)
        )
        self.labelReg3.setText(QCoreApplication.translate("EncoderDebugDialog", "REG3:", None))
        self.editReg3.setPlaceholderText(
            QCoreApplication.translate("EncoderDebugDialog", "\u2013", None)
        )
        self.labelLastRaw.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Last Raw:", None)
        )
        self.editLastRaw.setPlaceholderText(
            QCoreApplication.translate("EncoderDebugDialog", "\u2013", None)
        )
        self.groupAdcConfig.setTitle(
            QCoreApplication.translate("EncoderDebugDialog", "Konfiguration (CONF:ADC:*?)", None)
        )
        self.labelMux.setText(QCoreApplication.translate("EncoderDebugDialog", "MUX:", None))
        self.editMux.setPlaceholderText(
            QCoreApplication.translate("EncoderDebugDialog", "\u2013", None)
        )
        self.labelGain.setText(QCoreApplication.translate("EncoderDebugDialog", "Gain:", None))
        self.editGain.setPlaceholderText(
            QCoreApplication.translate("EncoderDebugDialog", "\u2013", None)
        )
        self.labelRate.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Rate (SPS):", None)
        )
        self.editRate.setPlaceholderText(
            QCoreApplication.translate("EncoderDebugDialog", "\u2013", None)
        )
        self.labelMode.setText(QCoreApplication.translate("EncoderDebugDialog", "Mode:", None))
        self.editMode.setPlaceholderText(
            QCoreApplication.translate("EncoderDebugDialog", "\u2013", None)
        )
        self.labelFir.setText(QCoreApplication.translate("EncoderDebugDialog", "FIR Filter:", None))
        self.editFir.setPlaceholderText(
            QCoreApplication.translate("EncoderDebugDialog", "\u2013", None)
        )
        self.labelVref.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Spannungsref.:", None)
        )
        self.editVref.setPlaceholderText(
            QCoreApplication.translate("EncoderDebugDialog", "\u2013", None)
        )
        self.buttonReadAdcConfig.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Konfiguration lesen", None)
        )
        self.groupPdtia.setTitle(
            QCoreApplication.translate(
                "EncoderDebugDialog", "PD-TIA Verst\u00e4rkung (DIAG:PDTIA?)", None
            )
        )
        self.labelPdtiaStage.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Stufe:", None)
        )
        self.editPdtiaStage.setPlaceholderText(
            QCoreApplication.translate("EncoderDebugDialog", "\u2013", None)
        )
        self.labelPdtiaPattern.setText(
            QCoreApplication.translate("EncoderDebugDialog", "GPIO Muster:", None)
        )
        self.editPdtiaPattern.setPlaceholderText(
            QCoreApplication.translate("EncoderDebugDialog", "\u2013", None)
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tabAds),
            QCoreApplication.translate("EncoderDebugDialog", "ADS1220", None),
        )
        self.labelRawStreamNotice.setText(
            QCoreApplication.translate(
                "EncoderDebugDialog",
                "Kein DataController verf\u00fcgbar.\n"
                "\u00d6ffne den Debug-Dialog \u00fcber das Hauptfenster (Strg+D).",
                None,
            )
        )
        self.editRawStream.setPlaceholderText(
            QCoreApplication.translate("EncoderDebugDialog", "Warte auf Frames \u2026", None)
        )
        self.buttonClearRawStream.setText(
            QCoreApplication.translate("EncoderDebugDialog", "L\u00f6schen", None)
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tabRawStream),
            QCoreApplication.translate("EncoderDebugDialog", "Raw Stream", None),
        )
        self.labelSelfTestInfo.setText(
            QCoreApplication.translate(
                "EncoderDebugDialog",
                "F\u00fchrt DIAG:SELF? aus \u2014 \u00fcberpr\u00fcft alle Subsysteme (Encoder A/B, ADC, PD-TIA).\n"
                "Jedes Subsystem meldet PASS oder FAIL.",
                None,
            )
        )
        self.buttonRunSelfTest.setText(
            QCoreApplication.translate(
                "EncoderDebugDialog", "Selbsttest ausf\u00fchren  (DIAG:SELF?)", None
            )
        )
        self.editSelfTest.setPlaceholderText(
            QCoreApplication.translate(
                "EncoderDebugDialog", "Noch kein Test durchgef\u00fchrt.", None
            )
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tabSelfTest),
            QCoreApplication.translate("EncoderDebugDialog", "Selbsttest", None),
        )

    # retranslateUi
