# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'encoder_debug.ui'
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
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class Ui_EncoderDebugDialog(object):
    def setupUi(self, EncoderDebugDialog):
        if not EncoderDebugDialog.objectName():
            EncoderDebugDialog.setObjectName("EncoderDebugDialog")
        EncoderDebugDialog.resize(860, 683)
        self.verticalLayout_root = QVBoxLayout(EncoderDebugDialog)
        self.verticalLayout_root.setSpacing(6)
        self.verticalLayout_root.setObjectName("verticalLayout_root")
        self.gbControl = QGroupBox(EncoderDebugDialog)
        self.gbControl.setObjectName("gbControl")
        self.hlControl = QHBoxLayout(self.gbControl)
        self.hlControl.setObjectName("hlControl")
        self.lblEncoderSel = QLabel(self.gbControl)
        self.lblEncoderSel.setObjectName("lblEncoderSel")

        self.hlControl.addWidget(self.lblEncoderSel)

        self.cbEncoderSelect = QComboBox(self.gbControl)
        self.cbEncoderSelect.addItem("")
        self.cbEncoderSelect.addItem("")
        self.cbEncoderSelect.addItem("")
        self.cbEncoderSelect.setObjectName("cbEncoderSelect")
        self.cbEncoderSelect.setMinimumSize(QSize(180, 30))

        self.hlControl.addWidget(self.cbEncoderSelect)

        self.cbAutoRefresh = QCheckBox(self.gbControl)
        self.cbAutoRefresh.setObjectName("cbAutoRefresh")
        self.cbAutoRefresh.setChecked(True)

        self.hlControl.addWidget(self.cbAutoRefresh)

        self.spbRefreshInterval = QSpinBox(self.gbControl)
        self.spbRefreshInterval.setObjectName("spbRefreshInterval")
        self.spbRefreshInterval.setMinimum(100)
        self.spbRefreshInterval.setMaximum(5000)
        self.spbRefreshInterval.setSingleStep(100)
        self.spbRefreshInterval.setValue(500)

        self.hlControl.addWidget(self.spbRefreshInterval)

        self.btnRefresh = QPushButton(self.gbControl)
        self.btnRefresh.setObjectName("btnRefresh")
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.ViewRefresh))
        self.btnRefresh.setIcon(icon)

        self.hlControl.addWidget(self.btnRefresh)

        self.hspacer_ctrl = QSpacerItem(
            20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.hlControl.addItem(self.hspacer_ctrl)

        self.btnZeroEncoder = QPushButton(self.gbControl)
        self.btnZeroEncoder.setObjectName("btnZeroEncoder")

        self.hlControl.addWidget(self.btnZeroEncoder)

        self.btnClearErrorFlag = QPushButton(self.gbControl)
        self.btnClearErrorFlag.setObjectName("btnClearErrorFlag")

        self.hlControl.addWidget(self.btnClearErrorFlag)

        self.verticalLayout_root.addWidget(self.gbControl)

        self.tabWidget = QTabWidget(EncoderDebugDialog)
        self.tabWidget.setObjectName("tabWidget")
        self.tabMeasurements = QWidget()
        self.tabMeasurements.setObjectName("tabMeasurements")
        self.hlMeasurements = QHBoxLayout(self.tabMeasurements)
        self.hlMeasurements.setObjectName("hlMeasurements")
        self.gbMeasA = QGroupBox(self.tabMeasurements)
        self.gbMeasA.setObjectName("gbMeasA")
        self.formMeasA = QFormLayout(self.gbMeasA)
        self.formMeasA.setObjectName("formMeasA")
        self.formMeasA.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow
        )
        self.lblConnA = QLabel(self.gbMeasA)
        self.lblConnA.setObjectName("lblConnA")

        self.formMeasA.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lblConnA)

        self.ledConnA = QFrame(self.gbMeasA)
        self.ledConnA.setObjectName("ledConnA")
        self.ledConnA.setMinimumSize(QSize(20, 20))
        self.ledConnA.setMaximumSize(QSize(20, 20))
        self.ledConnA.setFrameShape(QFrame.Shape.Box)

        self.formMeasA.setWidget(0, QFormLayout.ItemRole.FieldRole, self.ledConnA)

        self.lblAngleA = QLabel(self.gbMeasA)
        self.lblAngleA.setObjectName("lblAngleA")

        self.formMeasA.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lblAngleA)

        self.lcdAngleA = QLCDNumber(self.gbMeasA)
        self.lcdAngleA.setObjectName("lcdAngleA")
        self.lcdAngleA.setMinimumSize(QSize(150, 50))
        self.lcdAngleA.setSmallDecimalPoint(True)
        self.lcdAngleA.setDigitCount(8)
        self.lcdAngleA.setMode(QLCDNumber.Mode.Dec)

        self.formMeasA.setWidget(1, QFormLayout.ItemRole.FieldRole, self.lcdAngleA)

        self.lblMagnitudeA = QLabel(self.gbMeasA)
        self.lblMagnitudeA.setObjectName("lblMagnitudeA")

        self.formMeasA.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lblMagnitudeA)

        self.lcdMagnitudeA = QLCDNumber(self.gbMeasA)
        self.lcdMagnitudeA.setObjectName("lcdMagnitudeA")
        self.lcdMagnitudeA.setMinimumSize(QSize(150, 50))
        self.lcdMagnitudeA.setSmallDecimalPoint(True)
        self.lcdMagnitudeA.setDigitCount(8)
        self.lcdMagnitudeA.setMode(QLCDNumber.Mode.Dec)

        self.formMeasA.setWidget(2, QFormLayout.ItemRole.FieldRole, self.lcdMagnitudeA)

        self.lblMagBarA = QLabel(self.gbMeasA)
        self.lblMagBarA.setObjectName("lblMagBarA")

        self.formMeasA.setWidget(3, QFormLayout.ItemRole.LabelRole, self.lblMagBarA)

        self.pbarMagnitudeA = QProgressBar(self.gbMeasA)
        self.pbarMagnitudeA.setObjectName("pbarMagnitudeA")
        self.pbarMagnitudeA.setMaximum(16383)
        self.pbarMagnitudeA.setValue(0)
        self.pbarMagnitudeA.setTextVisible(False)

        self.formMeasA.setWidget(3, QFormLayout.ItemRole.FieldRole, self.pbarMagnitudeA)

        self.line = QFrame(self.gbMeasA)
        self.line.setObjectName("line")
        self.line.setMinimumSize(QSize(50, 10))
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.formMeasA.setWidget(4, QFormLayout.ItemRole.SpanningRole, self.line)

        self.lblCofA = QLabel(self.gbMeasA)
        self.lblCofA.setObjectName("lblCofA")

        self.formMeasA.setWidget(5, QFormLayout.ItemRole.LabelRole, self.lblCofA)

        self.ledCofA = QFrame(self.gbMeasA)
        self.ledCofA.setObjectName("ledCofA")
        self.ledCofA.setMinimumSize(QSize(20, 20))
        self.ledCofA.setMaximumSize(QSize(20, 20))
        self.ledCofA.setFrameShape(QFrame.Shape.Box)

        self.formMeasA.setWidget(5, QFormLayout.ItemRole.FieldRole, self.ledCofA)

        self.lblCompHA = QLabel(self.gbMeasA)
        self.lblCompHA.setObjectName("lblCompHA")

        self.formMeasA.setWidget(6, QFormLayout.ItemRole.LabelRole, self.lblCompHA)

        self.ledCompHA = QFrame(self.gbMeasA)
        self.ledCompHA.setObjectName("ledCompHA")
        self.ledCompHA.setMinimumSize(QSize(20, 20))
        self.ledCompHA.setMaximumSize(QSize(20, 20))
        self.ledCompHA.setFrameShape(QFrame.Shape.Box)

        self.formMeasA.setWidget(6, QFormLayout.ItemRole.FieldRole, self.ledCompHA)

        self.lblCompLA = QLabel(self.gbMeasA)
        self.lblCompLA.setObjectName("lblCompLA")

        self.formMeasA.setWidget(7, QFormLayout.ItemRole.LabelRole, self.lblCompLA)

        self.ledCompLA = QFrame(self.gbMeasA)
        self.ledCompLA.setObjectName("ledCompLA")
        self.ledCompLA.setMinimumSize(QSize(20, 20))
        self.ledCompLA.setMaximumSize(QSize(20, 20))
        self.ledCompLA.setFrameShape(QFrame.Shape.Box)

        self.formMeasA.setWidget(7, QFormLayout.ItemRole.FieldRole, self.ledCompLA)

        self.lblOcfA = QLabel(self.gbMeasA)
        self.lblOcfA.setObjectName("lblOcfA")

        self.formMeasA.setWidget(8, QFormLayout.ItemRole.LabelRole, self.lblOcfA)

        self.ledOcfA = QFrame(self.gbMeasA)
        self.ledOcfA.setObjectName("ledOcfA")
        self.ledOcfA.setMinimumSize(QSize(20, 20))
        self.ledOcfA.setMaximumSize(QSize(20, 20))
        self.ledOcfA.setFrameShape(QFrame.Shape.Box)

        self.formMeasA.setWidget(8, QFormLayout.ItemRole.FieldRole, self.ledOcfA)

        self.lblErrorA = QLabel(self.gbMeasA)
        self.lblErrorA.setObjectName("lblErrorA")

        self.formMeasA.setWidget(9, QFormLayout.ItemRole.LabelRole, self.lblErrorA)

        self.ledErrorA = QFrame(self.gbMeasA)
        self.ledErrorA.setObjectName("ledErrorA")
        self.ledErrorA.setMinimumSize(QSize(20, 20))
        self.ledErrorA.setMaximumSize(QSize(20, 20))
        self.ledErrorA.setFrameShape(QFrame.Shape.Box)

        self.formMeasA.setWidget(9, QFormLayout.ItemRole.FieldRole, self.ledErrorA)

        self.lblAgcA_lbl = QLabel(self.gbMeasA)
        self.lblAgcA_lbl.setObjectName("lblAgcA_lbl")

        self.formMeasA.setWidget(10, QFormLayout.ItemRole.LabelRole, self.lblAgcA_lbl)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalLayout.setContentsMargins(-1, -1, 0, -1)
        self.pbarAgcA = QProgressBar(self.gbMeasA)
        self.pbarAgcA.setObjectName("pbarAgcA")
        self.pbarAgcA.setMaximum(255)
        self.pbarAgcA.setValue(0)

        self.horizontalLayout.addWidget(self.pbarAgcA)

        self.spbAgcA = QSpinBox(self.gbMeasA)
        self.spbAgcA.setObjectName("spbAgcA")
        self.spbAgcA.setReadOnly(True)
        self.spbAgcA.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.spbAgcA.setMaximum(255)

        self.horizontalLayout.addWidget(self.spbAgcA)

        self.formMeasA.setLayout(
            10, QFormLayout.ItemRole.FieldRole, self.horizontalLayout
        )

        self.hlMeasurements.addWidget(self.gbMeasA)

        self.gbMeasB = QGroupBox(self.tabMeasurements)
        self.gbMeasB.setObjectName("gbMeasB")
        self.formMeasB = QFormLayout(self.gbMeasB)
        self.formMeasB.setObjectName("formMeasB")
        self.formMeasB.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow
        )
        self.lblConnB = QLabel(self.gbMeasB)
        self.lblConnB.setObjectName("lblConnB")

        self.formMeasB.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lblConnB)

        self.ledConnB = QFrame(self.gbMeasB)
        self.ledConnB.setObjectName("ledConnB")
        self.ledConnB.setMinimumSize(QSize(20, 20))
        self.ledConnB.setMaximumSize(QSize(20, 20))
        self.ledConnB.setFrameShape(QFrame.Shape.Box)

        self.formMeasB.setWidget(0, QFormLayout.ItemRole.FieldRole, self.ledConnB)

        self.lblAngleB = QLabel(self.gbMeasB)
        self.lblAngleB.setObjectName("lblAngleB")

        self.formMeasB.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lblAngleB)

        self.lcdAngleB = QLCDNumber(self.gbMeasB)
        self.lcdAngleB.setObjectName("lcdAngleB")
        self.lcdAngleB.setMinimumSize(QSize(150, 50))
        self.lcdAngleB.setSmallDecimalPoint(True)
        self.lcdAngleB.setDigitCount(8)
        self.lcdAngleB.setMode(QLCDNumber.Mode.Dec)

        self.formMeasB.setWidget(1, QFormLayout.ItemRole.FieldRole, self.lcdAngleB)

        self.lblMagnitudeB = QLabel(self.gbMeasB)
        self.lblMagnitudeB.setObjectName("lblMagnitudeB")

        self.formMeasB.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lblMagnitudeB)

        self.lcdMagnitudeB = QLCDNumber(self.gbMeasB)
        self.lcdMagnitudeB.setObjectName("lcdMagnitudeB")
        self.lcdMagnitudeB.setMinimumSize(QSize(150, 50))
        self.lcdMagnitudeB.setSmallDecimalPoint(True)
        self.lcdMagnitudeB.setDigitCount(8)
        self.lcdMagnitudeB.setMode(QLCDNumber.Mode.Dec)

        self.formMeasB.setWidget(2, QFormLayout.ItemRole.FieldRole, self.lcdMagnitudeB)

        self.lblMagBarB = QLabel(self.gbMeasB)
        self.lblMagBarB.setObjectName("lblMagBarB")

        self.formMeasB.setWidget(3, QFormLayout.ItemRole.LabelRole, self.lblMagBarB)

        self.pbarMagnitudeB = QProgressBar(self.gbMeasB)
        self.pbarMagnitudeB.setObjectName("pbarMagnitudeB")
        self.pbarMagnitudeB.setMaximum(16383)
        self.pbarMagnitudeB.setValue(0)
        self.pbarMagnitudeB.setTextVisible(False)

        self.formMeasB.setWidget(3, QFormLayout.ItemRole.FieldRole, self.pbarMagnitudeB)

        self.line_2 = QFrame(self.gbMeasB)
        self.line_2.setObjectName("line_2")
        self.line_2.setMinimumSize(QSize(50, 10))
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.formMeasB.setWidget(4, QFormLayout.ItemRole.SpanningRole, self.line_2)

        self.lblCofB = QLabel(self.gbMeasB)
        self.lblCofB.setObjectName("lblCofB")

        self.formMeasB.setWidget(5, QFormLayout.ItemRole.LabelRole, self.lblCofB)

        self.ledCofB = QFrame(self.gbMeasB)
        self.ledCofB.setObjectName("ledCofB")
        self.ledCofB.setMinimumSize(QSize(20, 20))
        self.ledCofB.setMaximumSize(QSize(20, 20))
        self.ledCofB.setFrameShape(QFrame.Shape.Box)

        self.formMeasB.setWidget(5, QFormLayout.ItemRole.FieldRole, self.ledCofB)

        self.lblCompHB = QLabel(self.gbMeasB)
        self.lblCompHB.setObjectName("lblCompHB")

        self.formMeasB.setWidget(6, QFormLayout.ItemRole.LabelRole, self.lblCompHB)

        self.ledCompHB = QFrame(self.gbMeasB)
        self.ledCompHB.setObjectName("ledCompHB")
        self.ledCompHB.setMinimumSize(QSize(20, 20))
        self.ledCompHB.setMaximumSize(QSize(20, 20))
        self.ledCompHB.setFrameShape(QFrame.Shape.Box)

        self.formMeasB.setWidget(6, QFormLayout.ItemRole.FieldRole, self.ledCompHB)

        self.lblCompLB = QLabel(self.gbMeasB)
        self.lblCompLB.setObjectName("lblCompLB")

        self.formMeasB.setWidget(7, QFormLayout.ItemRole.LabelRole, self.lblCompLB)

        self.ledCompLB = QFrame(self.gbMeasB)
        self.ledCompLB.setObjectName("ledCompLB")
        self.ledCompLB.setMinimumSize(QSize(20, 20))
        self.ledCompLB.setMaximumSize(QSize(20, 20))
        self.ledCompLB.setFrameShape(QFrame.Shape.Box)

        self.formMeasB.setWidget(7, QFormLayout.ItemRole.FieldRole, self.ledCompLB)

        self.lblOcfB = QLabel(self.gbMeasB)
        self.lblOcfB.setObjectName("lblOcfB")

        self.formMeasB.setWidget(8, QFormLayout.ItemRole.LabelRole, self.lblOcfB)

        self.ledOcfB = QFrame(self.gbMeasB)
        self.ledOcfB.setObjectName("ledOcfB")
        self.ledOcfB.setMinimumSize(QSize(20, 20))
        self.ledOcfB.setMaximumSize(QSize(20, 20))
        self.ledOcfB.setFrameShape(QFrame.Shape.Box)

        self.formMeasB.setWidget(8, QFormLayout.ItemRole.FieldRole, self.ledOcfB)

        self.lblErrorB = QLabel(self.gbMeasB)
        self.lblErrorB.setObjectName("lblErrorB")

        self.formMeasB.setWidget(9, QFormLayout.ItemRole.LabelRole, self.lblErrorB)

        self.ledErrorB = QFrame(self.gbMeasB)
        self.ledErrorB.setObjectName("ledErrorB")
        self.ledErrorB.setMinimumSize(QSize(20, 20))
        self.ledErrorB.setMaximumSize(QSize(20, 20))
        self.ledErrorB.setFrameShape(QFrame.Shape.Box)

        self.formMeasB.setWidget(9, QFormLayout.ItemRole.FieldRole, self.ledErrorB)

        self.lblAgcB_lbl = QLabel(self.gbMeasB)
        self.lblAgcB_lbl.setObjectName("lblAgcB_lbl")

        self.formMeasB.setWidget(10, QFormLayout.ItemRole.LabelRole, self.lblAgcB_lbl)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(-1, -1, 0, -1)
        self.pbarAgcB = QProgressBar(self.gbMeasB)
        self.pbarAgcB.setObjectName("pbarAgcB")
        self.pbarAgcB.setMaximum(255)
        self.pbarAgcB.setValue(0)

        self.horizontalLayout_2.addWidget(self.pbarAgcB)

        self.spbAgcB = QSpinBox(self.gbMeasB)
        self.spbAgcB.setObjectName("spbAgcB")
        self.spbAgcB.setReadOnly(True)
        self.spbAgcB.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.spbAgcB.setMaximum(255)

        self.horizontalLayout_2.addWidget(self.spbAgcB)

        self.formMeasB.setLayout(
            10, QFormLayout.ItemRole.FieldRole, self.horizontalLayout_2
        )

        self.hlMeasurements.addWidget(self.gbMeasB)

        self.tabWidget.addTab(self.tabMeasurements, "")
        self.tabSystem = QWidget()
        self.tabSystem.setObjectName("tabSystem")
        self.vlSystem = QVBoxLayout(self.tabSystem)
        self.vlSystem.setObjectName("vlSystem")
        self.gbSysInfo = QGroupBox(self.tabSystem)
        self.gbSysInfo.setObjectName("gbSysInfo")
        self.formSysInfo = QFormLayout(self.gbSysInfo)
        self.formSysInfo.setObjectName("formSysInfo")
        self.formSysInfo.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow
        )
        self.lblIdn_lbl = QLabel(self.gbSysInfo)
        self.lblIdn_lbl.setObjectName("lblIdn_lbl")

        self.formSysInfo.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lblIdn_lbl)

        self.leIdn = QLineEdit(self.gbSysInfo)
        self.leIdn.setObjectName("leIdn")
        self.leIdn.setReadOnly(True)

        self.formSysInfo.setWidget(0, QFormLayout.ItemRole.FieldRole, self.leIdn)

        self.lblPollInt_lbl = QLabel(self.gbSysInfo)
        self.lblPollInt_lbl.setObjectName("lblPollInt_lbl")

        self.formSysInfo.setWidget(
            1, QFormLayout.ItemRole.LabelRole, self.lblPollInt_lbl
        )

        self.spbPollInterval = QSpinBox(self.gbSysInfo)
        self.spbPollInterval.setObjectName("spbPollInterval")
        self.spbPollInterval.setReadOnly(True)
        self.spbPollInterval.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.spbPollInterval.setMaximum(9999)

        self.formSysInfo.setWidget(
            1, QFormLayout.ItemRole.FieldRole, self.spbPollInterval
        )

        self.lblDebugMode_lbl = QLabel(self.gbSysInfo)
        self.lblDebugMode_lbl.setObjectName("lblDebugMode_lbl")

        self.formSysInfo.setWidget(
            2, QFormLayout.ItemRole.LabelRole, self.lblDebugMode_lbl
        )

        self.cbDebugMode = QCheckBox(self.gbSysInfo)
        self.cbDebugMode.setObjectName("cbDebugMode")

        self.formSysInfo.setWidget(2, QFormLayout.ItemRole.FieldRole, self.cbDebugMode)

        self.vlSystem.addWidget(self.gbSysInfo)

        self.gbScpiErrors = QGroupBox(self.tabSystem)
        self.gbScpiErrors.setObjectName("gbScpiErrors")
        self.vlScpiErrors = QVBoxLayout(self.gbScpiErrors)
        self.vlScpiErrors.setObjectName("vlScpiErrors")
        self.teScpiErrors = QTextEdit(self.gbScpiErrors)
        self.teScpiErrors.setObjectName("teScpiErrors")
        self.teScpiErrors.setReadOnly(True)

        self.vlScpiErrors.addWidget(self.teScpiErrors)

        self.hlScpiErrBtns = QHBoxLayout()
        self.hlScpiErrBtns.setObjectName("hlScpiErrBtns")
        self.hspacerErrQ = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.hlScpiErrBtns.addItem(self.hspacerErrQ)

        self.btnReadScpiErrors = QPushButton(self.gbScpiErrors)
        self.btnReadScpiErrors.setObjectName("btnReadScpiErrors")

        self.hlScpiErrBtns.addWidget(self.btnReadScpiErrors)

        self.btnClearScpiErrors = QPushButton(self.gbScpiErrors)
        self.btnClearScpiErrors.setObjectName("btnClearScpiErrors")

        self.hlScpiErrBtns.addWidget(self.btnClearScpiErrors)

        self.vlScpiErrors.addLayout(self.hlScpiErrBtns)

        self.vlSystem.addWidget(self.gbScpiErrors)

        self.vspacerSys = QSpacerItem(
            20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.vlSystem.addItem(self.vspacerSys)

        self.tabWidget.addTab(self.tabSystem, "")
        self.tabTerminal = QWidget()
        self.tabTerminal.setObjectName("tabTerminal")
        self.vlTerminal = QVBoxLayout(self.tabTerminal)
        self.vlTerminal.setObjectName("vlTerminal")
        self.teTerminalLog = QTextEdit(self.tabTerminal)
        self.teTerminalLog.setObjectName("teTerminalLog")
        self.teTerminalLog.setReadOnly(True)

        self.vlTerminal.addWidget(self.teTerminalLog)

        self.hlTerminalInput = QHBoxLayout()
        self.hlTerminalInput.setObjectName("hlTerminalInput")
        self.leCommandInput = QLineEdit(self.tabTerminal)
        self.leCommandInput.setObjectName("leCommandInput")

        self.hlTerminalInput.addWidget(self.leCommandInput)

        self.btnSendCommand = QPushButton(self.tabTerminal)
        self.btnSendCommand.setObjectName("btnSendCommand")

        self.hlTerminalInput.addWidget(self.btnSendCommand)

        self.btnClearLog = QPushButton(self.tabTerminal)
        self.btnClearLog.setObjectName("btnClearLog")

        self.hlTerminalInput.addWidget(self.btnClearLog)

        self.vlTerminal.addLayout(self.hlTerminalInput)

        self.tabWidget.addTab(self.tabTerminal, "")

        self.verticalLayout_root.addWidget(self.tabWidget)

        self.buttonBox = QDialogButtonBox(EncoderDebugDialog)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Close)

        self.verticalLayout_root.addWidget(self.buttonBox)

        self.retranslateUi(EncoderDebugDialog)
        self.buttonBox.rejected.connect(EncoderDebugDialog.reject)

        self.tabWidget.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(EncoderDebugDialog)

    # setupUi

    def retranslateUi(self, EncoderDebugDialog):
        EncoderDebugDialog.setWindowTitle(
            QCoreApplication.translate("EncoderDebugDialog", "Encoder Debug", None)
        )
        self.gbControl.setTitle(
            QCoreApplication.translate("EncoderDebugDialog", "Steuerung", None)
        )
        self.lblEncoderSel.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Encoder:", None)
        )
        self.cbEncoderSelect.setItemText(
            0, QCoreApplication.translate("EncoderDebugDialog", "A \u2013 Sample", None)
        )
        self.cbEncoderSelect.setItemText(
            1,
            QCoreApplication.translate("EncoderDebugDialog", "B \u2013 Detektor", None),
        )
        self.cbEncoderSelect.setItemText(
            2, QCoreApplication.translate("EncoderDebugDialog", "Beide", None)
        )

        self.cbAutoRefresh.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Auto-Refresh", None)
        )
        # if QT_CONFIG(tooltip)
        self.spbRefreshInterval.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog", "Refresh-Intervall in Millisekunden", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.spbRefreshInterval.setSuffix(
            QCoreApplication.translate("EncoderDebugDialog", " ms", None)
        )
        # if QT_CONFIG(tooltip)
        self.btnRefresh.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog", "Alle Werte einmalig abrufen", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnRefresh.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Aktualisieren", None)
        )
        # if QT_CONFIG(tooltip)
        self.btnZeroEncoder.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog",
                "Aktuelle Position als Nullpunkt setzen (CONF:ZERO)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnZeroEncoder.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Nullpunkt setzen", None)
        )
        # if QT_CONFIG(tooltip)
        self.btnClearErrorFlag.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog",
                "Hardware Error-Flag l\u00f6schen (CONF:ERR)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnClearErrorFlag.setText(
            QCoreApplication.translate(
                "EncoderDebugDialog", "Fehler l\u00f6schen", None
            )
        )
        self.gbMeasA.setTitle(
            QCoreApplication.translate(
                "EncoderDebugDialog", "Encoder A \u2013 Sample", None
            )
        )
        self.lblConnA.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Verbunden", None)
        )
        # if QT_CONFIG(tooltip)
        self.ledConnA.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog", "Verbindungsstatus Encoder A", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.lblAngleA.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Winkel (\u00b0)", None)
        )
        # if QT_CONFIG(tooltip)
        self.lcdAngleA.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog", "Winkel in Grad (MEAS:ANGL? A)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.lblMagnitudeA.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Magnitude (raw)", None)
        )
        # if QT_CONFIG(tooltip)
        self.lcdMagnitudeA.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog", "Winkel in Grad (MEAS:ANGL? A)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.lblMagBarA.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Feldst\u00e4rke", None)
        )
        # if QT_CONFIG(tooltip)
        self.pbarMagnitudeA.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog", "Visuelle Darstellung der Magnet-Amplitude", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.lblCofA.setText(
            QCoreApplication.translate(
                "EncoderDebugDialog", "COF \u2013 CORDIC Overflow", None
            )
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
        self.lblCompHA.setText(
            QCoreApplication.translate(
                "EncoderDebugDialog", "COMP_H \u2013 Feld zu schwach", None
            )
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
        self.lblCompLA.setText(
            QCoreApplication.translate(
                "EncoderDebugDialog", "COMP_L \u2013 Feld zu stark", None
            )
        )
        # if QT_CONFIG(tooltip)
        self.ledCompLA.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog",
                "COMP_L: Magnetfeld zu stark (compLow=1 \u2192 Problem)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.lblOcfA.setText(
            QCoreApplication.translate(
                "EncoderDebugDialog", "OCF \u2013 Sensor bereit", None
            )
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
        self.lblErrorA.setText(
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
        self.lblAgcA_lbl.setText(
            QCoreApplication.translate(
                "EncoderDebugDialog", "AGC - Automatic Gain Control", None
            )
        )
        # if QT_CONFIG(tooltip)
        self.pbarAgcA.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog",
                "AGC: 0 = max Verst\u00e4rkung (schwaches Feld), 255 = min Verst\u00e4rkung (starkes Feld)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(tooltip)
        self.spbAgcA.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog",
                "Automatic Gain Control 0\u2013255 (niedrig = starkes Feld)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.gbMeasB.setTitle(
            QCoreApplication.translate(
                "EncoderDebugDialog", "Encoder B \u2013 Detektor", None
            )
        )
        self.lblConnB.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Verbunden", None)
        )
        # if QT_CONFIG(tooltip)
        self.ledConnB.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog", "Verbindungsstatus Encoder B", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.lblAngleB.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Winkel (\u00b0)", None)
        )
        # if QT_CONFIG(tooltip)
        self.lcdAngleB.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog", "Winkel in Grad (MEAS:ANGL? B)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.lblMagnitudeB.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Magnitude (raw)", None)
        )
        # if QT_CONFIG(tooltip)
        self.lcdMagnitudeB.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog", "Winkel in Grad (MEAS:ANGL? A)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.lblMagBarB.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Feldst\u00e4rke", None)
        )
        # if QT_CONFIG(tooltip)
        self.pbarMagnitudeB.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog", "Visuelle Darstellung der Magnet-Amplitude", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.lblCofB.setText(
            QCoreApplication.translate(
                "EncoderDebugDialog", "COF \u2013 CORDIC Overflow", None
            )
        )
        # if QT_CONFIG(tooltip)
        self.ledCofB.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog", "COF: CORDIC Overflow", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.lblCompHB.setText(
            QCoreApplication.translate(
                "EncoderDebugDialog", "COMP_H \u2013 Feld zu schwach", None
            )
        )
        # if QT_CONFIG(tooltip)
        self.ledCompHB.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog", "COMP_H: Magnetfeld zu schwach", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.lblCompLB.setText(
            QCoreApplication.translate(
                "EncoderDebugDialog", "COMP_L \u2013 Feld zu stark", None
            )
        )
        # if QT_CONFIG(tooltip)
        self.ledCompLB.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog", "COMP_L: Magnetfeld zu stark", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.lblOcfB.setText(
            QCoreApplication.translate(
                "EncoderDebugDialog", "OCF \u2013 Sensor bereit", None
            )
        )
        # if QT_CONFIG(tooltip)
        self.ledOcfB.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog", "OCF: Sensor bereit (1 = bereit)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.lblErrorB.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Error Flag", None)
        )
        # if QT_CONFIG(tooltip)
        self.ledErrorB.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog",
                "Hardware Error Flag (mit CONF:ERR B l\u00f6schbar)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.lblAgcB_lbl.setText(
            QCoreApplication.translate(
                "EncoderDebugDialog", "AGC - Automatic Gain Control", None
            )
        )
        # if QT_CONFIG(tooltip)
        self.pbarAgcB.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog",
                "AGC: 0 = max Verst\u00e4rkung, 255 = min Verst\u00e4rkung",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(tooltip)
        self.spbAgcB.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog", "Automatic Gain Control 0\u2013255", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tabMeasurements),
            QCoreApplication.translate("EncoderDebugDialog", "Messwerte", None),
        )
        self.gbSysInfo.setTitle(
            QCoreApplication.translate(
                "EncoderDebugDialog", "Ger\u00e4teinformationen", None
            )
        )
        self.lblIdn_lbl.setText(
            QCoreApplication.translate("EncoderDebugDialog", "IDN (*IDN?)", None)
        )
        # if QT_CONFIG(tooltip)
        self.leIdn.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog", "Ger\u00e4teidentifikation (*IDN?)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.leIdn.setPlaceholderText(
            QCoreApplication.translate("EncoderDebugDialog", "\u2013", None)
        )
        self.lblPollInt_lbl.setText(
            QCoreApplication.translate(
                "EncoderDebugDialog", "Poll-Intervall (SENS:INT?)", None
            )
        )
        # if QT_CONFIG(tooltip)
        self.spbPollInterval.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog",
                "Aktuelles Abfrageintervall des Arduino in ms (SENS:INT?)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.spbPollInterval.setSuffix(
            QCoreApplication.translate("EncoderDebugDialog", " ms", None)
        )
        self.lblDebugMode_lbl.setText(
            QCoreApplication.translate(
                "EncoderDebugDialog", "Debug-Modus (SYST:DEB?)", None
            )
        )
        # if QT_CONFIG(tooltip)
        self.cbDebugMode.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog",
                "Arduino Debug-Ausgabe aktiv (SYST:DEB ON/OFF)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.cbDebugMode.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Aktiv", None)
        )
        self.gbScpiErrors.setTitle(
            QCoreApplication.translate(
                "EncoderDebugDialog", "SCPI Fehler-Queue (SYST:ERR?)", None
            )
        )
        # if QT_CONFIG(tooltip)
        self.teScpiErrors.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog", "Inhalt der SCPI Fehler-Queue (SYST:ERR?)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.teScpiErrors.setPlaceholderText(
            QCoreApplication.translate("EncoderDebugDialog", "Keine Fehler", None)
        )
        # if QT_CONFIG(tooltip)
        self.btnReadScpiErrors.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog",
                "Alle Eintr\u00e4ge aus der SCPI Fehler-Queue lesen",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnReadScpiErrors.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Queue auslesen", None)
        )
        # if QT_CONFIG(tooltip)
        self.btnClearScpiErrors.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog", "SCPI Error Queue l\u00f6schen (*CLS)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnClearScpiErrors.setText(
            QCoreApplication.translate(
                "EncoderDebugDialog", "Queue l\u00f6schen (*CLS)", None
            )
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tabSystem),
            QCoreApplication.translate("EncoderDebugDialog", "System", None),
        )
        # if QT_CONFIG(tooltip)
        self.teTerminalLog.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog", "SCPI Kommunikationslog", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.teTerminalLog.setPlaceholderText(
            QCoreApplication.translate("EncoderDebugDialog", "Bereit\u2026", None)
        )
        # if QT_CONFIG(tooltip)
        self.leCommandInput.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog",
                "SCPI-Befehl eingeben, z.B.  MEAS:ANGL? A  oder  *IDN?",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.leCommandInput.setPlaceholderText(
            QCoreApplication.translate(
                "EncoderDebugDialog", "SCPI-Befehl, z.B. MEAS:ANGL? A", None
            )
        )
        # if QT_CONFIG(tooltip)
        self.btnSendCommand.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog", "Befehl senden (auch Enter)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnSendCommand.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Senden", None)
        )
        # if QT_CONFIG(tooltip)
        self.btnClearLog.setToolTip(
            QCoreApplication.translate(
                "EncoderDebugDialog", "Terminal-Log leeren", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnClearLog.setText(
            QCoreApplication.translate("EncoderDebugDialog", "Log leeren", None)
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tabTerminal),
            QCoreApplication.translate("EncoderDebugDialog", "SCPI Terminal", None),
        )

    # retranslateUi
