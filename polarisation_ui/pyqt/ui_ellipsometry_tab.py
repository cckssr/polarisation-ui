# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ellipsometry_tab.ui'
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
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from polarisation_ui.ui.widgets.ellipsometry_curve_plot import EllipsometryCurvePlot
from polarisation_ui.ui.widgets.ellipsometry_fit_plot import EllipsometryFitPlot


class Ui_EllipsometryTab(object):
    def setupUi(self, EllipsometryTab):
        if not EllipsometryTab.objectName():
            EllipsometryTab.setObjectName("EllipsometryTab")
        EllipsometryTab.resize(1218, 1072)
        self.layoutMain = QGridLayout(EllipsometryTab)
        self.layoutMain.setObjectName("layoutMain")
        self.layoutMain.setContentsMargins(0, 10, 0, 0)
        self.splitterPlots = QSplitter(EllipsometryTab)
        self.splitterPlots.setObjectName("splitterPlots")
        self.splitterPlots.setOrientation(Qt.Orientation.Horizontal)
        self.fitPlot = EllipsometryFitPlot(self.splitterPlots)
        self.fitPlot.setObjectName("fitPlot")
        self.splitterPlots.addWidget(self.fitPlot)
        self.ellipsoCurvePlot = EllipsometryCurvePlot(self.splitterPlots)
        self.ellipsoCurvePlot.setObjectName("ellipsoCurvePlot")
        self.splitterPlots.addWidget(self.ellipsoCurvePlot)

        self.layoutMain.addWidget(self.splitterPlots, 0, 0, 1, 1)

        self.tableSeries = QTableWidget(EllipsometryTab)
        if self.tableSeries.columnCount() < 8:
            self.tableSeries.setColumnCount(8)
        self.tableSeries.setObjectName("tableSeries")
        self.tableSeries.setMinimumSize(QSize(0, 120))
        self.tableSeries.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableSeries.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tableSeries.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableSeries.verticalHeader().setVisible(False)

        self.layoutMain.addWidget(self.tableSeries, 1, 0, 1, 1)

        self.scrollSide = QScrollArea(EllipsometryTab)
        self.scrollSide.setObjectName("scrollSide")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollSide.sizePolicy().hasHeightForWidth())
        self.scrollSide.setSizePolicy(sizePolicy)
        self.scrollSide.setMinimumSize(QSize(310, 0))
        self.scrollSide.setFrameShape(QFrame.Shape.NoFrame)
        self.scrollSide.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scrollSide.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollSide.setWidgetResizable(True)
        self.contentSide = QWidget()
        self.contentSide.setObjectName("contentSide")
        self.contentSide.setGeometry(QRect(0, 0, 346, 1208))
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.contentSide.sizePolicy().hasHeightForWidth())
        self.contentSide.setSizePolicy(sizePolicy1)
        self.layoutSide = QVBoxLayout(self.contentSide)
        self.layoutSide.setSpacing(6)
        self.layoutSide.setObjectName("layoutSide")
        self.layoutSide.setContentsMargins(4, 0, 4, 0)
        self.groupLive = QGroupBox(self.contentSide)
        self.groupLive.setObjectName("groupLive")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.groupLive.sizePolicy().hasHeightForWidth())
        self.groupLive.setSizePolicy(sizePolicy2)
        self.layoutLive = QFormLayout(self.groupLive)
        self.layoutLive.setObjectName("layoutLive")
        self.layoutLive.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.layoutLive.setVerticalSpacing(2)
        self.layoutLive.setContentsMargins(6, 4, 6, 4)
        self.labelLiveIntensity = QLabel(self.groupLive)
        self.labelLiveIntensity.setObjectName("labelLiveIntensity")

        self.layoutLive.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelLiveIntensity)

        self.valueLiveIntensity = QLabel(self.groupLive)
        self.valueLiveIntensity.setObjectName("valueLiveIntensity")

        self.layoutLive.setWidget(0, QFormLayout.ItemRole.FieldRole, self.valueLiveIntensity)

        self.labelLivePower = QLabel(self.groupLive)
        self.labelLivePower.setObjectName("labelLivePower")

        self.layoutLive.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelLivePower)

        self.valueLivePower = QLabel(self.groupLive)
        self.valueLivePower.setObjectName("valueLivePower")

        self.layoutLive.setWidget(1, QFormLayout.ItemRole.FieldRole, self.valueLivePower)

        self.labelLiveAoi = QLabel(self.groupLive)
        self.labelLiveAoi.setObjectName("labelLiveAoi")

        self.layoutLive.setWidget(2, QFormLayout.ItemRole.LabelRole, self.labelLiveAoi)

        self.valueLiveAoi = QLabel(self.groupLive)
        self.valueLiveAoi.setObjectName("valueLiveAoi")

        self.layoutLive.setWidget(2, QFormLayout.ItemRole.FieldRole, self.valueLiveAoi)

        self.labelLiveDetector = QLabel(self.groupLive)
        self.labelLiveDetector.setObjectName("labelLiveDetector")

        self.layoutLive.setWidget(3, QFormLayout.ItemRole.LabelRole, self.labelLiveDetector)

        self.valueLiveDetector = QLabel(self.groupLive)
        self.valueLiveDetector.setObjectName("valueLiveDetector")

        self.layoutLive.setWidget(3, QFormLayout.ItemRole.FieldRole, self.valueLiveDetector)

        self.labelSpecularError = QLabel(self.groupLive)
        self.labelSpecularError.setObjectName("labelSpecularError")

        self.layoutLive.setWidget(4, QFormLayout.ItemRole.LabelRole, self.labelSpecularError)

        self.valueSpecularError = QLabel(self.groupLive)
        self.valueSpecularError.setObjectName("valueSpecularError")

        self.layoutLive.setWidget(4, QFormLayout.ItemRole.FieldRole, self.valueSpecularError)

        self.labelKdcPosition = QLabel(self.groupLive)
        self.labelKdcPosition.setObjectName("labelKdcPosition")

        self.layoutLive.setWidget(5, QFormLayout.ItemRole.LabelRole, self.labelKdcPosition)

        self.valueKdcPosition = QLabel(self.groupLive)
        self.valueKdcPosition.setObjectName("valueKdcPosition")

        self.layoutLive.setWidget(5, QFormLayout.ItemRole.FieldRole, self.valueKdcPosition)

        self.layoutSide.addWidget(self.groupLive)

        self.groupSetup = QGroupBox(self.contentSide)
        self.groupSetup.setObjectName("groupSetup")
        sizePolicy1.setHeightForWidth(self.groupSetup.sizePolicy().hasHeightForWidth())
        self.groupSetup.setSizePolicy(sizePolicy1)
        self.layoutSetup = QFormLayout(self.groupSetup)
        self.layoutSetup.setObjectName("layoutSetup")
        self.layoutSetup.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.layoutSetup.setVerticalSpacing(4)
        self.layoutSetup.setContentsMargins(6, 6, 6, 6)
        self.labelWavelength = QLabel(self.groupSetup)
        self.labelWavelength.setObjectName("labelWavelength")

        self.layoutSetup.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelWavelength)

        self.spinWavelength = QDoubleSpinBox(self.groupSetup)
        self.spinWavelength.setObjectName("spinWavelength")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.spinWavelength.sizePolicy().hasHeightForWidth())
        self.spinWavelength.setSizePolicy(sizePolicy3)
        self.spinWavelength.setDecimals(1)
        self.spinWavelength.setMinimum(200.000000000000000)
        self.spinWavelength.setMaximum(2000.000000000000000)
        self.spinWavelength.setValue(532.000000000000000)

        self.layoutSetup.setWidget(0, QFormLayout.ItemRole.FieldRole, self.spinWavelength)

        self.labelPolariser = QLabel(self.groupSetup)
        self.labelPolariser.setObjectName("labelPolariser")

        self.layoutSetup.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelPolariser)

        self.spinPolariser = QDoubleSpinBox(self.groupSetup)
        self.spinPolariser.setObjectName("spinPolariser")
        self.spinPolariser.setDecimals(2)
        self.spinPolariser.setMinimum(-360.000000000000000)
        self.spinPolariser.setMaximum(360.000000000000000)
        self.spinPolariser.setSingleStep(1.000000000000000)
        self.spinPolariser.setValue(45.000000000000000)

        self.layoutSetup.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spinPolariser)

        self.labelAnalyserOffset = QLabel(self.groupSetup)
        self.labelAnalyserOffset.setObjectName("labelAnalyserOffset")

        self.layoutSetup.setWidget(2, QFormLayout.ItemRole.LabelRole, self.labelAnalyserOffset)

        self.spinAnalyserOffset = QDoubleSpinBox(self.groupSetup)
        self.spinAnalyserOffset.setObjectName("spinAnalyserOffset")
        self.spinAnalyserOffset.setDecimals(2)
        self.spinAnalyserOffset.setMinimum(-360.000000000000000)
        self.spinAnalyserOffset.setMaximum(360.000000000000000)
        self.spinAnalyserOffset.setSingleStep(1.000000000000000)
        self.spinAnalyserOffset.setValue(135.000000000000000)

        self.layoutSetup.setWidget(2, QFormLayout.ItemRole.FieldRole, self.spinAnalyserOffset)

        self.labelAmbientIndex = QLabel(self.groupSetup)
        self.labelAmbientIndex.setObjectName("labelAmbientIndex")

        self.layoutSetup.setWidget(3, QFormLayout.ItemRole.LabelRole, self.labelAmbientIndex)

        self.spinAmbientIndex = QDoubleSpinBox(self.groupSetup)
        self.spinAmbientIndex.setObjectName("spinAmbientIndex")
        self.spinAmbientIndex.setDecimals(4)
        self.spinAmbientIndex.setMinimum(1.000000000000000)
        self.spinAmbientIndex.setMaximum(2.000000000000000)
        self.spinAmbientIndex.setSingleStep(0.000100000000000)
        self.spinAmbientIndex.setValue(1.000300000000000)

        self.layoutSetup.setWidget(3, QFormLayout.ItemRole.FieldRole, self.spinAmbientIndex)

        self.labelKdcZeroOffset = QLabel(self.groupSetup)
        self.labelKdcZeroOffset.setObjectName("labelKdcZeroOffset")

        self.layoutSetup.setWidget(4, QFormLayout.ItemRole.LabelRole, self.labelKdcZeroOffset)

        self.valueKdcZeroOffset = QLabel(self.groupSetup)
        self.valueKdcZeroOffset.setObjectName("valueKdcZeroOffset")

        self.layoutSetup.setWidget(4, QFormLayout.ItemRole.FieldRole, self.valueKdcZeroOffset)

        self.buttonSetAoiZero = QPushButton(self.groupSetup)
        self.buttonSetAoiZero.setObjectName("buttonSetAoiZero")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.buttonSetAoiZero.sizePolicy().hasHeightForWidth())
        self.buttonSetAoiZero.setSizePolicy(sizePolicy4)

        self.layoutSetup.setWidget(5, QFormLayout.ItemRole.SpanningRole, self.buttonSetAoiZero)

        self.layoutSide.addWidget(self.groupSetup)

        self.groupSweep = QGroupBox(self.contentSide)
        self.groupSweep.setObjectName("groupSweep")
        self.groupSweep.setEnabled(False)
        self.layoutSweep = QVBoxLayout(self.groupSweep)
        self.layoutSweep.setObjectName("layoutSweep")
        self.layoutSweep.setContentsMargins(6, 6, 6, 6)
        self.checkAnalyserPlaced = QCheckBox(self.groupSweep)
        self.checkAnalyserPlaced.setObjectName("checkAnalyserPlaced")

        self.layoutSweep.addWidget(self.checkAnalyserPlaced)

        self.layoutSweepParams = QFormLayout()
        self.layoutSweepParams.setObjectName("layoutSweepParams")
        self.layoutSweepParams.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow
        )
        self.layoutSweepParams.setVerticalSpacing(3)
        self.labelSweepStart = QLabel(self.groupSweep)
        self.labelSweepStart.setObjectName("labelSweepStart")

        self.layoutSweepParams.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelSweepStart)

        self.spinSweepStart = QDoubleSpinBox(self.groupSweep)
        self.spinSweepStart.setObjectName("spinSweepStart")
        self.spinSweepStart.setDecimals(1)
        self.spinSweepStart.setMinimum(0.000000000000000)
        self.spinSweepStart.setMaximum(360.000000000000000)
        self.spinSweepStart.setValue(0.000000000000000)

        self.layoutSweepParams.setWidget(0, QFormLayout.ItemRole.FieldRole, self.spinSweepStart)

        self.labelSweepEnd = QLabel(self.groupSweep)
        self.labelSweepEnd.setObjectName("labelSweepEnd")

        self.layoutSweepParams.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelSweepEnd)

        self.spinSweepEnd = QDoubleSpinBox(self.groupSweep)
        self.spinSweepEnd.setObjectName("spinSweepEnd")
        self.spinSweepEnd.setDecimals(1)
        self.spinSweepEnd.setMinimum(0.000000000000000)
        self.spinSweepEnd.setMaximum(360.000000000000000)
        self.spinSweepEnd.setValue(180.000000000000000)

        self.layoutSweepParams.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spinSweepEnd)

        self.labelSweepStep = QLabel(self.groupSweep)
        self.labelSweepStep.setObjectName("labelSweepStep")

        self.layoutSweepParams.setWidget(2, QFormLayout.ItemRole.LabelRole, self.labelSweepStep)

        self.spinSweepStep = QDoubleSpinBox(self.groupSweep)
        self.spinSweepStep.setObjectName("spinSweepStep")
        self.spinSweepStep.setDecimals(1)
        self.spinSweepStep.setMinimum(0.100000000000000)
        self.spinSweepStep.setMaximum(90.000000000000000)
        self.spinSweepStep.setSingleStep(0.500000000000000)
        self.spinSweepStep.setValue(5.000000000000000)

        self.layoutSweepParams.setWidget(2, QFormLayout.ItemRole.FieldRole, self.spinSweepStep)

        self.labelSettleMs = QLabel(self.groupSweep)
        self.labelSettleMs.setObjectName("labelSettleMs")

        self.layoutSweepParams.setWidget(3, QFormLayout.ItemRole.LabelRole, self.labelSettleMs)

        self.spinSettleMs = QSpinBox(self.groupSweep)
        self.spinSettleMs.setObjectName("spinSettleMs")
        self.spinSettleMs.setMinimum(0)
        self.spinSettleMs.setMaximum(5000)
        self.spinSettleMs.setSingleStep(50)
        self.spinSettleMs.setValue(150)

        self.layoutSweepParams.setWidget(3, QFormLayout.ItemRole.FieldRole, self.spinSettleMs)

        self.layoutSweep.addLayout(self.layoutSweepParams)

        self.buttonStartSweep = QPushButton(self.groupSweep)
        self.buttonStartSweep.setObjectName("buttonStartSweep")
        self.buttonStartSweep.setEnabled(False)

        self.layoutSweep.addWidget(self.buttonStartSweep)

        self.buttonAbortSweep = QPushButton(self.groupSweep)
        self.buttonAbortSweep.setObjectName("buttonAbortSweep")
        self.buttonAbortSweep.setEnabled(False)

        self.layoutSweep.addWidget(self.buttonAbortSweep)

        self.layoutSide.addWidget(self.groupSweep)

        self.groupManual = QGroupBox(self.contentSide)
        self.groupManual.setObjectName("groupManual")
        self.groupManual.setEnabled(False)
        self.layoutManual = QVBoxLayout(self.groupManual)
        self.layoutManual.setObjectName("layoutManual")
        self.layoutManual.setContentsMargins(6, 6, 6, 6)
        self.layoutManualEntry = QFormLayout()
        self.layoutManualEntry.setObjectName("layoutManualEntry")
        self.layoutManualEntry.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow
        )
        self.labelAnalyserManual = QLabel(self.groupManual)
        self.labelAnalyserManual.setObjectName("labelAnalyserManual")

        self.layoutManualEntry.setWidget(
            0, QFormLayout.ItemRole.LabelRole, self.labelAnalyserManual
        )

        self.spinAnalyserManual = QDoubleSpinBox(self.groupManual)
        self.spinAnalyserManual.setObjectName("spinAnalyserManual")
        self.spinAnalyserManual.setDecimals(2)
        self.spinAnalyserManual.setMinimum(-360.000000000000000)
        self.spinAnalyserManual.setMaximum(360.000000000000000)
        self.spinAnalyserManual.setSingleStep(1.000000000000000)
        self.spinAnalyserManual.setValue(0.000000000000000)

        self.layoutManualEntry.setWidget(0, QFormLayout.ItemRole.FieldRole, self.spinAnalyserManual)

        self.layoutManual.addLayout(self.layoutManualEntry)

        self.buttonAddPoint = QPushButton(self.groupManual)
        self.buttonAddPoint.setObjectName("buttonAddPoint")

        self.layoutManual.addWidget(self.buttonAddPoint)

        self.buttonClearSweep = QPushButton(self.groupManual)
        self.buttonClearSweep.setObjectName("buttonClearSweep")

        self.layoutManual.addWidget(self.buttonClearSweep)

        self.layoutSide.addWidget(self.groupManual)

        self.groupResult = QGroupBox(self.contentSide)
        self.groupResult.setObjectName("groupResult")
        self.layoutResult = QVBoxLayout(self.groupResult)
        self.layoutResult.setObjectName("layoutResult")
        self.layoutResult.setContentsMargins(6, 6, 6, 6)
        self.layoutResultValues = QGridLayout()
        self.layoutResultValues.setObjectName("layoutResultValues")
        self.layoutResultValues.setVerticalSpacing(2)
        self.labelI0 = QLabel(self.groupResult)
        self.labelI0.setObjectName("labelI0")
        self.labelI0.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignTrailing
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.layoutResultValues.addWidget(self.labelI0, 1, 0, 1, 1)

        self.valueBeta = QLabel(self.groupResult)
        self.valueBeta.setObjectName("valueBeta")

        self.layoutResultValues.addWidget(self.valueBeta, 0, 4, 1, 1)

        self.valueResidual = QLabel(self.groupResult)
        self.valueResidual.setObjectName("valueResidual")

        self.layoutResultValues.addWidget(self.valueResidual, 1, 4, 1, 1)

        self.valueDelta = QLabel(self.groupResult)
        self.valueDelta.setObjectName("valueDelta")

        self.layoutResultValues.addWidget(self.valueDelta, 3, 1, 1, 1)

        self.labelKPseudo = QLabel(self.groupResult)
        self.labelKPseudo.setObjectName("labelKPseudo")
        self.labelKPseudo.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignTrailing
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.layoutResultValues.addWidget(self.labelKPseudo, 4, 3, 1, 1)

        self.labelBeta = QLabel(self.groupResult)
        self.labelBeta.setObjectName("labelBeta")
        self.labelBeta.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignTrailing
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.layoutResultValues.addWidget(self.labelBeta, 0, 3, 1, 1)

        self.labelModulation = QLabel(self.groupResult)
        self.labelModulation.setObjectName("labelModulation")
        self.labelModulation.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignTrailing
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.layoutResultValues.addWidget(self.labelModulation, 2, 0, 1, 1)

        self.valueI0 = QLabel(self.groupResult)
        self.valueI0.setObjectName("valueI0")

        self.layoutResultValues.addWidget(self.valueI0, 1, 1, 1, 1)

        self.valueAlpha = QLabel(self.groupResult)
        self.valueAlpha.setObjectName("valueAlpha")

        self.layoutResultValues.addWidget(self.valueAlpha, 0, 1, 1, 1)

        self.labelAlpha = QLabel(self.groupResult)
        self.labelAlpha.setObjectName("labelAlpha")
        self.labelAlpha.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignTrailing
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.layoutResultValues.addWidget(self.labelAlpha, 0, 0, 1, 1)

        self.valueKPseudo = QLabel(self.groupResult)
        self.valueKPseudo.setObjectName("valueKPseudo")

        self.layoutResultValues.addWidget(self.valueKPseudo, 4, 4, 1, 1)

        self.labelDelta = QLabel(self.groupResult)
        self.labelDelta.setObjectName("labelDelta")
        self.labelDelta.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignTrailing
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.layoutResultValues.addWidget(self.labelDelta, 3, 0, 1, 1)

        self.valuePsi = QLabel(self.groupResult)
        self.valuePsi.setObjectName("valuePsi")

        self.layoutResultValues.addWidget(self.valuePsi, 2, 4, 1, 1)

        self.valueModulation = QLabel(self.groupResult)
        self.valueModulation.setObjectName("valueModulation")

        self.layoutResultValues.addWidget(self.valueModulation, 2, 1, 1, 1)

        self.labelPsi = QLabel(self.groupResult)
        self.labelPsi.setObjectName("labelPsi")
        self.labelPsi.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignTrailing
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.layoutResultValues.addWidget(self.labelPsi, 2, 3, 1, 1)

        self.valueNPseudo = QLabel(self.groupResult)
        self.valueNPseudo.setObjectName("valueNPseudo")

        self.layoutResultValues.addWidget(self.valueNPseudo, 4, 1, 1, 1)

        self.labelNPseudo = QLabel(self.groupResult)
        self.labelNPseudo.setObjectName("labelNPseudo")
        self.labelNPseudo.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignTrailing
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.layoutResultValues.addWidget(self.labelNPseudo, 4, 0, 1, 1)

        self.labelResidual = QLabel(self.groupResult)
        self.labelResidual.setObjectName("labelResidual")
        self.labelResidual.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignTrailing
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.layoutResultValues.addWidget(self.labelResidual, 1, 3, 1, 1)

        self.lineResult = QFrame(self.groupResult)
        self.lineResult.setObjectName("lineResult")
        self.lineResult.setFrameShape(QFrame.Shape.VLine)
        self.lineResult.setFrameShadow(QFrame.Shadow.Sunken)

        self.layoutResultValues.addWidget(self.lineResult, 0, 2, 5, 1)

        self.layoutResultValues.setColumnStretch(1, 1)
        self.layoutResultValues.setColumnStretch(4, 1)

        self.layoutResult.addLayout(self.layoutResultValues)

        self.buttonAcceptPoint = QPushButton(self.groupResult)
        self.buttonAcceptPoint.setObjectName("buttonAcceptPoint")
        self.buttonAcceptPoint.setEnabled(False)

        self.layoutResult.addWidget(self.buttonAcceptPoint)

        self.layoutSide.addWidget(self.groupResult)

        self.groupModel = QGroupBox(self.contentSide)
        self.groupModel.setObjectName("groupModel")
        self.layoutModel = QVBoxLayout(self.groupModel)
        self.layoutModel.setObjectName("layoutModel")
        self.layoutModel.setContentsMargins(6, 6, 6, 6)
        self.layoutModelParams = QFormLayout()
        self.layoutModelParams.setObjectName("layoutModelParams")
        self.layoutModelParams.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow
        )
        self.layoutModelParams.setVerticalSpacing(3)
        self.labelModelType = QLabel(self.groupModel)
        self.labelModelType.setObjectName("labelModelType")

        self.layoutModelParams.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelModelType)

        self.comboModel = QComboBox(self.groupModel)
        self.comboModel.setObjectName("comboModel")
        sizePolicy3.setHeightForWidth(self.comboModel.sizePolicy().hasHeightForWidth())
        self.comboModel.setSizePolicy(sizePolicy3)

        self.layoutModelParams.setWidget(0, QFormLayout.ItemRole.FieldRole, self.comboModel)

        self.labelSubstrateN = QLabel(self.groupModel)
        self.labelSubstrateN.setObjectName("labelSubstrateN")

        self.layoutModelParams.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelSubstrateN)

        self.spinSubstrateN = QDoubleSpinBox(self.groupModel)
        self.spinSubstrateN.setObjectName("spinSubstrateN")
        self.spinSubstrateN.setDecimals(3)
        self.spinSubstrateN.setMinimum(0.100000000000000)
        self.spinSubstrateN.setMaximum(10.000000000000000)
        self.spinSubstrateN.setSingleStep(0.010000000000000)
        self.spinSubstrateN.setValue(3.880000000000000)

        self.layoutModelParams.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spinSubstrateN)

        self.labelSubstrateK = QLabel(self.groupModel)
        self.labelSubstrateK.setObjectName("labelSubstrateK")

        self.layoutModelParams.setWidget(2, QFormLayout.ItemRole.LabelRole, self.labelSubstrateK)

        self.spinSubstrateK = QDoubleSpinBox(self.groupModel)
        self.spinSubstrateK.setObjectName("spinSubstrateK")
        self.spinSubstrateK.setDecimals(3)
        self.spinSubstrateK.setMinimum(0.000000000000000)
        self.spinSubstrateK.setMaximum(10.000000000000000)
        self.spinSubstrateK.setSingleStep(0.010000000000000)
        self.spinSubstrateK.setValue(0.020000000000000)

        self.layoutModelParams.setWidget(2, QFormLayout.ItemRole.FieldRole, self.spinSubstrateK)

        self.labelDMin = QLabel(self.groupModel)
        self.labelDMin.setObjectName("labelDMin")

        self.layoutModelParams.setWidget(3, QFormLayout.ItemRole.LabelRole, self.labelDMin)

        self.containerDRange = QWidget(self.groupModel)
        self.containerDRange.setObjectName("containerDRange")
        self.layoutDRange = QHBoxLayout(self.containerDRange)
        self.layoutDRange.setObjectName("layoutDRange")
        self.layoutDRange.setContentsMargins(0, 0, 0, 0)
        self.spinDMin = QDoubleSpinBox(self.containerDRange)
        self.spinDMin.setObjectName("spinDMin")
        sizePolicy3.setHeightForWidth(self.spinDMin.sizePolicy().hasHeightForWidth())
        self.spinDMin.setSizePolicy(sizePolicy3)
        self.spinDMin.setDecimals(0)
        self.spinDMin.setMinimum(0.000000000000000)
        self.spinDMin.setMaximum(100000.000000000000000)
        self.spinDMin.setValue(0.000000000000000)

        self.layoutDRange.addWidget(self.spinDMin)

        self.spinDMax = QDoubleSpinBox(self.containerDRange)
        self.spinDMax.setObjectName("spinDMax")
        sizePolicy3.setHeightForWidth(self.spinDMax.sizePolicy().hasHeightForWidth())
        self.spinDMax.setSizePolicy(sizePolicy3)
        self.spinDMax.setDecimals(0)
        self.spinDMax.setMinimum(0.000000000000000)
        self.spinDMax.setMaximum(100000.000000000000000)
        self.spinDMax.setValue(1000.000000000000000)

        self.layoutDRange.addWidget(self.spinDMax)

        self.layoutModelParams.setWidget(3, QFormLayout.ItemRole.FieldRole, self.containerDRange)

        self.labelNfMin = QLabel(self.groupModel)
        self.labelNfMin.setObjectName("labelNfMin")

        self.layoutModelParams.setWidget(4, QFormLayout.ItemRole.LabelRole, self.labelNfMin)

        self.containerNRange = QWidget(self.groupModel)
        self.containerNRange.setObjectName("containerNRange")
        self.layoutNRange = QHBoxLayout(self.containerNRange)
        self.layoutNRange.setObjectName("layoutNRange")
        self.layoutNRange.setContentsMargins(0, 0, 0, 0)
        self.spinNfMin = QDoubleSpinBox(self.containerNRange)
        self.spinNfMin.setObjectName("spinNfMin")
        sizePolicy3.setHeightForWidth(self.spinNfMin.sizePolicy().hasHeightForWidth())
        self.spinNfMin.setSizePolicy(sizePolicy3)
        self.spinNfMin.setDecimals(3)
        self.spinNfMin.setMinimum(1.000000000000000)
        self.spinNfMin.setMaximum(10.000000000000000)
        self.spinNfMin.setValue(1.200000000000000)

        self.layoutNRange.addWidget(self.spinNfMin)

        self.spinNfMax = QDoubleSpinBox(self.containerNRange)
        self.spinNfMax.setObjectName("spinNfMax")
        sizePolicy3.setHeightForWidth(self.spinNfMax.sizePolicy().hasHeightForWidth())
        self.spinNfMax.setSizePolicy(sizePolicy3)
        self.spinNfMax.setDecimals(3)
        self.spinNfMax.setMinimum(1.000000000000000)
        self.spinNfMax.setMaximum(10.000000000000000)
        self.spinNfMax.setValue(3.000000000000000)

        self.layoutNRange.addWidget(self.spinNfMax)

        self.layoutModelParams.setWidget(4, QFormLayout.ItemRole.FieldRole, self.containerNRange)

        self.layoutModel.addLayout(self.layoutModelParams)

        self.checkFitK = QCheckBox(self.groupModel)
        self.checkFitK.setObjectName("checkFitK")

        self.layoutModel.addWidget(self.checkFitK)

        self.buttonFitModel = QPushButton(self.groupModel)
        self.buttonFitModel.setObjectName("buttonFitModel")
        self.buttonFitModel.setEnabled(False)

        self.layoutModel.addWidget(self.buttonFitModel)

        self.layoutModelValues = QGridLayout()
        self.layoutModelValues.setObjectName("layoutModelValues")
        self.layoutModelValues.setVerticalSpacing(2)
        self.labelMSE = QLabel(self.groupModel)
        self.labelMSE.setObjectName("labelMSE")
        self.labelMSE.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignTrailing
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.layoutModelValues.addWidget(self.labelMSE, 1, 3, 1, 1)

        self.valueThickness = QLabel(self.groupModel)
        self.valueThickness.setObjectName("valueThickness")

        self.layoutModelValues.addWidget(self.valueThickness, 0, 1, 1, 1)

        self.valueMSE = QLabel(self.groupModel)
        self.valueMSE.setObjectName("valueMSE")

        self.layoutModelValues.addWidget(self.valueMSE, 1, 4, 1, 1)

        self.valueKFilm = QLabel(self.groupModel)
        self.valueKFilm.setObjectName("valueKFilm")

        self.layoutModelValues.addWidget(self.valueKFilm, 1, 1, 1, 1)

        self.valueNFilm = QLabel(self.groupModel)
        self.valueNFilm.setObjectName("valueNFilm")

        self.layoutModelValues.addWidget(self.valueNFilm, 0, 4, 1, 1)

        self.labelNFilm = QLabel(self.groupModel)
        self.labelNFilm.setObjectName("labelNFilm")
        self.labelNFilm.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignTrailing
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.layoutModelValues.addWidget(self.labelNFilm, 0, 3, 1, 1)

        self.labelThickness = QLabel(self.groupModel)
        self.labelThickness.setObjectName("labelThickness")
        self.labelThickness.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignTrailing
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.layoutModelValues.addWidget(self.labelThickness, 0, 0, 1, 1)

        self.labelKFilm = QLabel(self.groupModel)
        self.labelKFilm.setObjectName("labelKFilm")
        self.labelKFilm.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignTrailing
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.layoutModelValues.addWidget(self.labelKFilm, 1, 0, 1, 1)

        self.lineModel = QFrame(self.groupModel)
        self.lineModel.setObjectName("lineModel")
        self.lineModel.setFrameShape(QFrame.Shape.VLine)
        self.lineModel.setFrameShadow(QFrame.Shadow.Sunken)

        self.layoutModelValues.addWidget(self.lineModel, 0, 2, 2, 1)

        self.layoutModelValues.setColumnStretch(1, 1)
        self.layoutModelValues.setColumnStretch(4, 1)

        self.layoutModel.addLayout(self.layoutModelValues)

        self.valueBranches = QLabel(self.groupModel)
        self.valueBranches.setObjectName("valueBranches")
        self.valueBranches.setWordWrap(True)

        self.layoutModel.addWidget(self.valueBranches)

        self.layoutSide.addWidget(self.groupModel)

        self.buttonDeleteSelected = QPushButton(self.contentSide)
        self.buttonDeleteSelected.setObjectName("buttonDeleteSelected")
        self.buttonDeleteSelected.setEnabled(False)

        self.layoutSide.addWidget(self.buttonDeleteSelected)

        self.buttonDeleteLast = QPushButton(self.contentSide)
        self.buttonDeleteLast.setObjectName("buttonDeleteLast")
        self.buttonDeleteLast.setEnabled(False)

        self.layoutSide.addWidget(self.buttonDeleteLast)

        self.buttonClear = QPushButton(self.contentSide)
        self.buttonClear.setObjectName("buttonClear")
        self.buttonClear.setEnabled(False)

        self.layoutSide.addWidget(self.buttonClear)

        self.scrollSide.setWidget(self.contentSide)

        self.layoutMain.addWidget(self.scrollSide, 0, 1, 2, 1)

        self.layoutMain.setRowStretch(0, 2)
        self.layoutMain.setColumnStretch(0, 2)

        self.retranslateUi(EllipsometryTab)

        QMetaObject.connectSlotsByName(EllipsometryTab)

    # setupUi

    def retranslateUi(self, EllipsometryTab):
        self.groupLive.setTitle(QCoreApplication.translate("EllipsometryTab", "Aktuell", None))
        self.labelLiveIntensity.setText(QCoreApplication.translate("EllipsometryTab", "I:", None))
        self.valueLiveIntensity.setText(
            QCoreApplication.translate("EllipsometryTab", "\u2014", None)
        )
        self.labelLivePower.setText(QCoreApplication.translate("EllipsometryTab", "P:", None))
        self.valueLivePower.setText(QCoreApplication.translate("EllipsometryTab", "\u2014", None))
        self.labelLiveAoi.setText(
            QCoreApplication.translate("EllipsometryTab", "AOI \u03b8:", None)
        )
        self.valueLiveAoi.setText(QCoreApplication.translate("EllipsometryTab", "\u2014", None))
        self.labelLiveDetector.setText(
            QCoreApplication.translate("EllipsometryTab", "Detektorarm:", None)
        )
        self.valueLiveDetector.setText(
            QCoreApplication.translate("EllipsometryTab", "\u2014", None)
        )
        self.labelSpecularError.setText(
            QCoreApplication.translate("EllipsometryTab", "Spiegel-Fehler:", None)
        )
        # if QT_CONFIG(tooltip)
        self.valueSpecularError.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab",
                "Abweichung des Detektorarms von 2\u00b7\u03b8 (Spiegelbedingung) \u2014 gro\u00dfer Wert deutet auf eine Fehljustage hin",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.valueSpecularError.setText(
            QCoreApplication.translate("EllipsometryTab", "\u2014", None)
        )
        self.labelKdcPosition.setText(
            QCoreApplication.translate("EllipsometryTab", "Analysator-Position:", None)
        )
        self.valueKdcPosition.setText(QCoreApplication.translate("EllipsometryTab", "\u2014", None))
        self.groupSetup.setTitle(
            QCoreApplication.translate("EllipsometryTab", "Konfiguration", None)
        )
        self.labelWavelength.setText(
            QCoreApplication.translate("EllipsometryTab", "Wellenl\u00e4nge \u03bb:", None)
        )
        # if QT_CONFIG(tooltip)
        self.spinWavelength.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab",
                "Beleuchtungswellenl\u00e4nge \u2014 geht in das D\u00fcnnschicht-Modell ein (d/\u03bb)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.spinWavelength.setSuffix(QCoreApplication.translate("EllipsometryTab", " nm", None))
        self.labelPolariser.setText(
            QCoreApplication.translate("EllipsometryTab", "Polarisator P:", None)
        )
        # if QT_CONFIG(tooltip)
        self.spinPolariser.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab",
                "Polarisatorazimut relativ zur Einfallsebene \u2014 45\u00b0 maximiert die RAE-Empfindlichkeit; darf nicht 0\u00b0 oder 90\u00b0 sein",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.spinPolariser.setSuffix(QCoreApplication.translate("EllipsometryTab", " \u00b0", None))
        self.labelAnalyserOffset.setText(
            QCoreApplication.translate("EllipsometryTab", "Analysator-Offset A\u2080:", None)
        )
        # if QT_CONFIG(tooltip)
        self.spinAnalyserOffset.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab",
                "Azimut = KDC-Winkel (logisch) + dieser Offset. Der KDC-Nullpunkt referenziert auf den Polarisator, nicht auf die Einfallsebene \u2014 Standardwert P+90\u00b0 (Ausl\u00f6schung des Geradeausstrahls), bei Bedarf hier korrigieren",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.spinAnalyserOffset.setSuffix(
            QCoreApplication.translate("EllipsometryTab", " \u00b0", None)
        )
        self.labelAmbientIndex.setText(
            QCoreApplication.translate("EllipsometryTab", "Umgebung n\u2080:", None)
        )
        # if QT_CONFIG(tooltip)
        self.spinAmbientIndex.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab", "Brechungsindex des Umgebungsmediums (Luft \u2248 1.0003)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.labelKdcZeroOffset.setText(
            QCoreApplication.translate("EllipsometryTab", "KDC-Nullpunkt:", None)
        )
        # if QT_CONFIG(tooltip)
        self.valueKdcZeroOffset.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab",
                "Aktueller kdc.zero_offset_deg aus der Konfiguration (Referenzierung auf den Polarisator)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.valueKdcZeroOffset.setText(
            QCoreApplication.translate("EllipsometryTab", "\u2014", None)
        )
        # if QT_CONFIG(tooltip)
        self.buttonSetAoiZero.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab",
                "Aktuelle Proben- und Detektorarm-Winkel als Geradeausstrahl-Referenz (AOI = 0\u00b0) \u00fcbernehmen",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonSetAoiZero.setText(
            QCoreApplication.translate("EllipsometryTab", "AOI-Nullpunkt setzen", None)
        )
        self.groupSweep.setTitle(
            QCoreApplication.translate("EllipsometryTab", "Automatischer Scan (KDC101)", None)
        )
        # if QT_CONFIG(tooltip)
        self.checkAnalyserPlaced.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab",
                "Best\u00e4tigen, dass der Analysator im Strahlengang eingesetzt ist",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.checkAnalyserPlaced.setText(
            QCoreApplication.translate("EllipsometryTab", "Analysator eingesetzt", None)
        )
        self.labelSweepStart.setText(
            QCoreApplication.translate("EllipsometryTab", "Von (\u00b0):", None)
        )
        # if QT_CONFIG(tooltip)
        self.spinSweepStart.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab", "Startwinkel des Analysator-Scans (logischer KDC-Winkel)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.spinSweepStart.setSuffix(
            QCoreApplication.translate("EllipsometryTab", " \u00b0", None)
        )
        self.labelSweepEnd.setText(
            QCoreApplication.translate("EllipsometryTab", "Bis (\u00b0):", None)
        )
        # if QT_CONFIG(tooltip)
        self.spinSweepEnd.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab", "Endwinkel des Analysator-Scans (logischer KDC-Winkel)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.spinSweepEnd.setSuffix(QCoreApplication.translate("EllipsometryTab", " \u00b0", None))
        self.labelSweepStep.setText(
            QCoreApplication.translate("EllipsometryTab", "Schritt (\u00b0):", None)
        )
        # if QT_CONFIG(tooltip)
        self.spinSweepStep.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab", "Schrittweite des Analysator-Scans (\u00b0)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.spinSweepStep.setSuffix(QCoreApplication.translate("EllipsometryTab", " \u00b0", None))
        self.labelSettleMs.setText(
            QCoreApplication.translate("EllipsometryTab", "Einschwingzeit:", None)
        )
        # if QT_CONFIG(tooltip)
        self.spinSettleMs.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab",
                "Wartezeit nach jedem Analysator-Schritt vor der Mittelung (ms)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.spinSettleMs.setSuffix(QCoreApplication.translate("EllipsometryTab", " ms", None))
        # if QT_CONFIG(tooltip)
        self.buttonStartSweep.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab",
                "Automatischen Analysator-Scan starten (erneutes Homing nur falls n\u00f6tig)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonStartSweep.setText(
            QCoreApplication.translate("EllipsometryTab", "Scan starten", None)
        )
        # if QT_CONFIG(tooltip)
        self.buttonAbortSweep.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab", "Laufenden automatischen Scan sofort abbrechen", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonAbortSweep.setText(
            QCoreApplication.translate("EllipsometryTab", "Abbrechen", None)
        )
        self.groupManual.setTitle(
            QCoreApplication.translate("EllipsometryTab", "Manueller Analysatorpunkt", None)
        )
        self.labelAnalyserManual.setText(
            QCoreApplication.translate("EllipsometryTab", "Analysator (logisch):", None)
        )
        # if QT_CONFIG(tooltip)
        self.spinAnalyserManual.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab",
                "Logischer KDC-Winkel f\u00fcr diesen Einzelpunkt (Analysator per Hand gedreht)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.spinAnalyserManual.setSuffix(
            QCoreApplication.translate("EllipsometryTab", " \u00b0", None)
        )
        # if QT_CONFIG(tooltip)
        self.buttonAddPoint.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab",
                "Aktuellen Analysatorwinkel mit gemittelter Leistung zum Sweep-Puffer hinzuf\u00fcgen",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonAddPoint.setText(
            QCoreApplication.translate("EllipsometryTab", "Punkt hinzuf\u00fcgen", None)
        )
        # if QT_CONFIG(tooltip)
        self.buttonClearSweep.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab",
                "Sweep-Puffer der aktuellen AOI-Messung leeren (ohne die Serie zu ver\u00e4ndern)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonClearSweep.setText(
            QCoreApplication.translate("EllipsometryTab", "Sweep-Puffer leeren", None)
        )
        self.groupResult.setTitle(
            QCoreApplication.translate("EllipsometryTab", "Fit-Ergebnis (aktuelle AOI)", None)
        )
        self.labelI0.setText(QCoreApplication.translate("EllipsometryTab", "I\u2080:", None))
        self.valueBeta.setText(QCoreApplication.translate("EllipsometryTab", "\u2014", None))
        self.valueResidual.setText(QCoreApplication.translate("EllipsometryTab", "\u2014", None))
        # if QT_CONFIG(tooltip)
        self.valueDelta.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab",
                "Nur cos(\u0394) wird gemessen \u2014 das Vorzeichen von \u0394 ist prinzipiell unbestimmt",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.valueDelta.setText(QCoreApplication.translate("EllipsometryTab", "\u2014", None))
        self.labelKPseudo.setText(
            QCoreApplication.translate("EllipsometryTab", "k (pseudo):", None)
        )
        self.labelBeta.setText(QCoreApplication.translate("EllipsometryTab", "\u03b2:", None))
        self.labelModulation.setText(
            QCoreApplication.translate("EllipsometryTab", "Modulation m:", None)
        )
        self.valueI0.setText(QCoreApplication.translate("EllipsometryTab", "\u2014", None))
        self.valueAlpha.setText(QCoreApplication.translate("EllipsometryTab", "\u2014", None))
        self.labelAlpha.setText(QCoreApplication.translate("EllipsometryTab", "\u03b1:", None))
        self.valueKPseudo.setText(QCoreApplication.translate("EllipsometryTab", "\u2014", None))
        self.labelDelta.setText(QCoreApplication.translate("EllipsometryTab", "\u0394:", None))
        self.valuePsi.setText(QCoreApplication.translate("EllipsometryTab", "\u2014", None))
        # if QT_CONFIG(tooltip)
        self.valueModulation.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab",
                "sqrt(\u03b1\u00b2+\u03b2\u00b2) \u2014 muss < 1 sein, sonst ist der Fit unphysikalisch",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.valueModulation.setText(QCoreApplication.translate("EllipsometryTab", "\u2014", None))
        self.labelPsi.setText(QCoreApplication.translate("EllipsometryTab", "\u03a8:", None))
        self.valueNPseudo.setText(QCoreApplication.translate("EllipsometryTab", "\u2014", None))
        self.labelNPseudo.setText(
            QCoreApplication.translate("EllipsometryTab", "n (pseudo):", None)
        )
        self.labelResidual.setText(QCoreApplication.translate("EllipsometryTab", "Residuum:", None))
        # if QT_CONFIG(tooltip)
        self.buttonAcceptPoint.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab",
                "Aktuellen Fit als Messpunkt dieser AOI in die \u03a8(\u03b8)/\u0394(\u03b8)-Serie \u00fcbernehmen und den Sweep-Puffer f\u00fcr die n\u00e4chste AOI leeren",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonAcceptPoint.setText(
            QCoreApplication.translate("EllipsometryTab", "In Serie \u00fcbernehmen", None)
        )
        self.groupModel.setTitle(
            QCoreApplication.translate("EllipsometryTab", "Optisches Modell", None)
        )
        self.labelModelType.setText(QCoreApplication.translate("EllipsometryTab", "Modell:", None))
        # if QT_CONFIG(tooltip)
        self.comboModel.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab",
                "2-Phasen: Probe als Substrat behandeln (Pseudo-n,k). 3-Phasen: Schichtdicke und -index auf bekanntem Substrat fitten",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.labelSubstrateN.setText(
            QCoreApplication.translate("EllipsometryTab", "Substrat n:", None)
        )
        # if QT_CONFIG(tooltip)
        self.spinSubstrateN.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab",
                "Bekannter Brechungsindex des Substrats bei \u03bb (Standard: Silizium bei 632.8 nm)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.labelSubstrateK.setText(
            QCoreApplication.translate("EllipsometryTab", "Substrat k:", None)
        )
        # if QT_CONFIG(tooltip)
        self.spinSubstrateK.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab", "Bekannter Extinktionskoeffizient des Substrats bei \u03bb", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.labelDMin.setText(
            QCoreApplication.translate("EllipsometryTab", "d-Suchbereich:", None)
        )
        self.spinDMin.setSuffix(QCoreApplication.translate("EllipsometryTab", " nm", None))
        self.spinDMax.setSuffix(QCoreApplication.translate("EllipsometryTab", " nm", None))
        self.labelNfMin.setText(
            QCoreApplication.translate("EllipsometryTab", "n-Suchbereich:", None)
        )
        # if QT_CONFIG(tooltip)
        self.checkFitK.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab",
                "Absorption k der Schicht mitfitten (grobes festes Raster, 0\u20262) \u2014 f\u00fcr transparente Schichten (k=0) deaktiviert lassen, sonst ist das Problem unterbestimmt",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.checkFitK.setText(
            QCoreApplication.translate("EllipsometryTab", "k der Schicht mitfitten", None)
        )
        # if QT_CONFIG(tooltip)
        self.buttonFitModel.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab",
                "Optisches Modell an die gesamte \u03a8(\u03b8)/\u0394(\u03b8)-Serie anpassen (mindestens 1 AOI-Punkt erforderlich)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonFitModel.setText(
            QCoreApplication.translate("EllipsometryTab", "Modell fitten", None)
        )
        self.labelMSE.setText(QCoreApplication.translate("EllipsometryTab", "MSE:", None))
        self.valueThickness.setText(QCoreApplication.translate("EllipsometryTab", "\u2014", None))
        self.valueMSE.setText(QCoreApplication.translate("EllipsometryTab", "\u2014", None))
        self.valueKFilm.setText(QCoreApplication.translate("EllipsometryTab", "\u2014", None))
        self.valueNFilm.setText(QCoreApplication.translate("EllipsometryTab", "\u2014", None))
        self.labelNFilm.setText(QCoreApplication.translate("EllipsometryTab", "n (Schicht):", None))
        self.labelThickness.setText(QCoreApplication.translate("EllipsometryTab", "Dicke d:", None))
        self.labelKFilm.setText(QCoreApplication.translate("EllipsometryTab", "k (Schicht):", None))
        # if QT_CONFIG(tooltip)
        self.valueBranches.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab",
                "Alternative Schichtdicken-L\u00f6sungen (Perioden-Mehrdeutigkeit bei einer Wellenl\u00e4nge) \u2014 durch weitere AOI-Punkte aufl\u00f6sbar",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.valueBranches.setText("")
        # if QT_CONFIG(tooltip)
        self.buttonDeleteSelected.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab", "Markierte AOI-Zeile aus der Serie l\u00f6schen", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonDeleteSelected.setText(
            QCoreApplication.translate("EllipsometryTab", "Ausgew\u00e4hlte AOI l\u00f6schen", None)
        )
        # if QT_CONFIG(tooltip)
        self.buttonDeleteLast.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab", "Letzte AOI-Zeile aus der Serie l\u00f6schen", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonDeleteLast.setText(
            QCoreApplication.translate("EllipsometryTab", "Letzte AOI l\u00f6schen", None)
        )
        # if QT_CONFIG(tooltip)
        self.buttonClear.setToolTip(
            QCoreApplication.translate("EllipsometryTab", "Gesamte Serie l\u00f6schen", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonClear.setText(
            QCoreApplication.translate("EllipsometryTab", "Alle l\u00f6schen", None)
        )
        pass

    # retranslateUi
