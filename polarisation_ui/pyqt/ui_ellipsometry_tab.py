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
        self.gridLayout = QGridLayout(EllipsometryTab)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setContentsMargins(0, 10, 0, 0)
        self.plotSplitter = QSplitter(EllipsometryTab)
        self.plotSplitter.setObjectName("plotSplitter")
        self.plotSplitter.setOrientation(Qt.Orientation.Horizontal)
        self.fitPlot = EllipsometryFitPlot(self.plotSplitter)
        self.fitPlot.setObjectName("fitPlot")
        self.plotSplitter.addWidget(self.fitPlot)
        self.ellipsoCurvePlot = EllipsometryCurvePlot(self.plotSplitter)
        self.ellipsoCurvePlot.setObjectName("ellipsoCurvePlot")
        self.plotSplitter.addWidget(self.ellipsoCurvePlot)

        self.gridLayout.addWidget(self.plotSplitter, 0, 0, 1, 1)

        self.seriesTable = QTableWidget(EllipsometryTab)
        if self.seriesTable.columnCount() < 8:
            self.seriesTable.setColumnCount(8)
        __qtablewidgetitem = QTableWidgetItem()
        self.seriesTable.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.seriesTable.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.seriesTable.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.seriesTable.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.seriesTable.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.seriesTable.setHorizontalHeaderItem(5, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.seriesTable.setHorizontalHeaderItem(6, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.seriesTable.setHorizontalHeaderItem(7, __qtablewidgetitem7)
        self.seriesTable.setObjectName("seriesTable")
        self.seriesTable.setMinimumSize(QSize(0, 120))
        self.seriesTable.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.seriesTable.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.seriesTable.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.seriesTable.verticalHeader().setVisible(False)

        self.gridLayout.addWidget(self.seriesTable, 1, 0, 1, 1)

        self.rightScroll = QScrollArea(EllipsometryTab)
        self.rightScroll.setObjectName("rightScroll")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.rightScroll.sizePolicy().hasHeightForWidth())
        self.rightScroll.setSizePolicy(sizePolicy)
        self.rightScroll.setMinimumWidth(340)
        self.rightScroll.setFrameShape(QFrame.Shape.NoFrame)
        self.rightScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.rightScroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.rightScroll.setWidgetResizable(True)
        self.rightScrollContents = QWidget()
        self.rightScrollContents.setObjectName("rightScrollContents")
        self.rightScrollContents.setGeometry(QRect(0, -275, 371, 1320))
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.rightScrollContents.sizePolicy().hasHeightForWidth())
        self.rightScrollContents.setSizePolicy(sizePolicy1)
        self.rightLayout = QVBoxLayout(self.rightScrollContents)
        self.rightLayout.setSpacing(6)
        self.rightLayout.setObjectName("rightLayout")
        self.rightLayout.setContentsMargins(4, 0, 4, 0)
        self.gbLive = QGroupBox(self.rightScrollContents)
        self.gbLive.setObjectName("gbLive")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.gbLive.sizePolicy().hasHeightForWidth())
        self.gbLive.setSizePolicy(sizePolicy2)
        self.formLive = QFormLayout(self.gbLive)
        self.formLive.setObjectName("formLive")
        self.formLive.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.FieldsStayAtSizeHint)
        self.formLive.setVerticalSpacing(2)
        self.formLive.setContentsMargins(6, 4, 6, 4)
        self.lblLiveIntensityLabel = QLabel(self.gbLive)
        self.lblLiveIntensityLabel.setObjectName("lblLiveIntensityLabel")

        self.formLive.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lblLiveIntensityLabel)

        self.lblLiveIntensity = QLabel(self.gbLive)
        self.lblLiveIntensity.setObjectName("lblLiveIntensity")

        self.formLive.setWidget(0, QFormLayout.ItemRole.FieldRole, self.lblLiveIntensity)

        self.lblLivePowerLabel = QLabel(self.gbLive)
        self.lblLivePowerLabel.setObjectName("lblLivePowerLabel")

        self.formLive.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lblLivePowerLabel)

        self.lblLivePower = QLabel(self.gbLive)
        self.lblLivePower.setObjectName("lblLivePower")

        self.formLive.setWidget(1, QFormLayout.ItemRole.FieldRole, self.lblLivePower)

        self.lblLiveAoiLabel = QLabel(self.gbLive)
        self.lblLiveAoiLabel.setObjectName("lblLiveAoiLabel")

        self.formLive.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lblLiveAoiLabel)

        self.lblLiveAoi = QLabel(self.gbLive)
        self.lblLiveAoi.setObjectName("lblLiveAoi")

        self.formLive.setWidget(2, QFormLayout.ItemRole.FieldRole, self.lblLiveAoi)

        self.lblLiveDetectorLabel = QLabel(self.gbLive)
        self.lblLiveDetectorLabel.setObjectName("lblLiveDetectorLabel")

        self.formLive.setWidget(3, QFormLayout.ItemRole.LabelRole, self.lblLiveDetectorLabel)

        self.lblLiveDetector = QLabel(self.gbLive)
        self.lblLiveDetector.setObjectName("lblLiveDetector")

        self.formLive.setWidget(3, QFormLayout.ItemRole.FieldRole, self.lblLiveDetector)

        self.lblSpecularErrorLabel = QLabel(self.gbLive)
        self.lblSpecularErrorLabel.setObjectName("lblSpecularErrorLabel")

        self.formLive.setWidget(4, QFormLayout.ItemRole.LabelRole, self.lblSpecularErrorLabel)

        self.lblSpecularError = QLabel(self.gbLive)
        self.lblSpecularError.setObjectName("lblSpecularError")

        self.formLive.setWidget(4, QFormLayout.ItemRole.FieldRole, self.lblSpecularError)

        self.lblKDCPositionLabel = QLabel(self.gbLive)
        self.lblKDCPositionLabel.setObjectName("lblKDCPositionLabel")

        self.formLive.setWidget(5, QFormLayout.ItemRole.LabelRole, self.lblKDCPositionLabel)

        self.lblKDCPosition = QLabel(self.gbLive)
        self.lblKDCPosition.setObjectName("lblKDCPosition")

        self.formLive.setWidget(5, QFormLayout.ItemRole.FieldRole, self.lblKDCPosition)

        self.rightLayout.addWidget(self.gbLive)

        self.gbSetup = QGroupBox(self.rightScrollContents)
        self.gbSetup.setObjectName("gbSetup")
        self.formSetup = QFormLayout(self.gbSetup)
        self.formSetup.setObjectName("formSetup")
        self.formSetup.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.FieldsStayAtSizeHint)
        self.formSetup.setVerticalSpacing(4)
        self.formSetup.setContentsMargins(6, 6, 6, 6)
        self.lblWavelength = QLabel(self.gbSetup)
        self.lblWavelength.setObjectName("lblWavelength")

        self.formSetup.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lblWavelength)

        self.spinWavelength = QDoubleSpinBox(self.gbSetup)
        self.spinWavelength.setObjectName("spinWavelength")
        self.spinWavelength.setMaximumWidth(90)
        self.spinWavelength.setDecimals(1)
        self.spinWavelength.setMinimum(200.000000000000000)
        self.spinWavelength.setMaximum(2000.000000000000000)
        self.spinWavelength.setValue(532.000000000000000)

        self.formSetup.setWidget(0, QFormLayout.ItemRole.FieldRole, self.spinWavelength)

        self.lblPolariser = QLabel(self.gbSetup)
        self.lblPolariser.setObjectName("lblPolariser")

        self.formSetup.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lblPolariser)

        self.spinPolariser = QDoubleSpinBox(self.gbSetup)
        self.spinPolariser.setObjectName("spinPolariser")
        self.spinPolariser.setMaximumWidth(90)
        self.spinPolariser.setDecimals(2)
        self.spinPolariser.setMinimum(-360.000000000000000)
        self.spinPolariser.setMaximum(360.000000000000000)
        self.spinPolariser.setSingleStep(1.000000000000000)
        self.spinPolariser.setValue(45.000000000000000)

        self.formSetup.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spinPolariser)

        self.lblAnalyserOffset = QLabel(self.gbSetup)
        self.lblAnalyserOffset.setObjectName("lblAnalyserOffset")

        self.formSetup.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lblAnalyserOffset)

        self.spinAnalyserOffset = QDoubleSpinBox(self.gbSetup)
        self.spinAnalyserOffset.setObjectName("spinAnalyserOffset")
        self.spinAnalyserOffset.setMaximumWidth(90)
        self.spinAnalyserOffset.setDecimals(2)
        self.spinAnalyserOffset.setMinimum(-360.000000000000000)
        self.spinAnalyserOffset.setMaximum(360.000000000000000)
        self.spinAnalyserOffset.setSingleStep(1.000000000000000)
        self.spinAnalyserOffset.setValue(135.000000000000000)

        self.formSetup.setWidget(2, QFormLayout.ItemRole.FieldRole, self.spinAnalyserOffset)

        self.lblAmbientIndex = QLabel(self.gbSetup)
        self.lblAmbientIndex.setObjectName("lblAmbientIndex")

        self.formSetup.setWidget(3, QFormLayout.ItemRole.LabelRole, self.lblAmbientIndex)

        self.spinAmbientIndex = QDoubleSpinBox(self.gbSetup)
        self.spinAmbientIndex.setObjectName("spinAmbientIndex")
        self.spinAmbientIndex.setMaximumWidth(70)
        self.spinAmbientIndex.setDecimals(4)
        self.spinAmbientIndex.setMinimum(1.000000000000000)
        self.spinAmbientIndex.setMaximum(2.000000000000000)
        self.spinAmbientIndex.setSingleStep(0.000100000000000)
        self.spinAmbientIndex.setValue(1.000300000000000)

        self.formSetup.setWidget(3, QFormLayout.ItemRole.FieldRole, self.spinAmbientIndex)

        self.lblKdcZeroOffsetLabel = QLabel(self.gbSetup)
        self.lblKdcZeroOffsetLabel.setObjectName("lblKdcZeroOffsetLabel")

        self.formSetup.setWidget(4, QFormLayout.ItemRole.LabelRole, self.lblKdcZeroOffsetLabel)

        self.lblKdcZeroOffset = QLabel(self.gbSetup)
        self.lblKdcZeroOffset.setObjectName("lblKdcZeroOffset")

        self.formSetup.setWidget(4, QFormLayout.ItemRole.FieldRole, self.lblKdcZeroOffset)

        self.btnSetAoiZero = QPushButton(self.gbSetup)
        self.btnSetAoiZero.setObjectName("btnSetAoiZero")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.btnSetAoiZero.sizePolicy().hasHeightForWidth())
        self.btnSetAoiZero.setSizePolicy(sizePolicy3)

        self.formSetup.setWidget(5, QFormLayout.ItemRole.SpanningRole, self.btnSetAoiZero)

        self.rightLayout.addWidget(self.gbSetup)

        self.gbSweep = QGroupBox(self.rightScrollContents)
        self.gbSweep.setObjectName("gbSweep")
        self.gbSweep.setEnabled(False)
        self.vboxSweep = QVBoxLayout(self.gbSweep)
        self.vboxSweep.setObjectName("vboxSweep")
        self.vboxSweep.setContentsMargins(6, 6, 6, 6)
        self.cbAnalyserPlaced = QCheckBox(self.gbSweep)
        self.cbAnalyserPlaced.setObjectName("cbAnalyserPlaced")

        self.vboxSweep.addWidget(self.cbAnalyserPlaced)

        self.formSweepParams = QFormLayout()
        self.formSweepParams.setObjectName("formSweepParams")
        self.formSweepParams.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.FieldsStayAtSizeHint
        )
        self.formSweepParams.setVerticalSpacing(3)
        self.lblSweepStart = QLabel(self.gbSweep)
        self.lblSweepStart.setObjectName("lblSweepStart")

        self.formSweepParams.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lblSweepStart)

        self.spinSweepStart = QDoubleSpinBox(self.gbSweep)
        self.spinSweepStart.setObjectName("spinSweepStart")
        self.spinSweepStart.setMaximumWidth(80)
        self.spinSweepStart.setDecimals(1)
        self.spinSweepStart.setMinimum(0.000000000000000)
        self.spinSweepStart.setMaximum(360.000000000000000)
        self.spinSweepStart.setValue(0.000000000000000)

        self.formSweepParams.setWidget(0, QFormLayout.ItemRole.FieldRole, self.spinSweepStart)

        self.lblSweepEnd = QLabel(self.gbSweep)
        self.lblSweepEnd.setObjectName("lblSweepEnd")

        self.formSweepParams.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lblSweepEnd)

        self.spinSweepEnd = QDoubleSpinBox(self.gbSweep)
        self.spinSweepEnd.setObjectName("spinSweepEnd")
        self.spinSweepEnd.setMaximumWidth(80)
        self.spinSweepEnd.setDecimals(1)
        self.spinSweepEnd.setMinimum(0.000000000000000)
        self.spinSweepEnd.setMaximum(360.000000000000000)
        self.spinSweepEnd.setValue(180.000000000000000)

        self.formSweepParams.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spinSweepEnd)

        self.lblSweepStep = QLabel(self.gbSweep)
        self.lblSweepStep.setObjectName("lblSweepStep")

        self.formSweepParams.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lblSweepStep)

        self.spinSweepStep = QDoubleSpinBox(self.gbSweep)
        self.spinSweepStep.setObjectName("spinSweepStep")
        self.spinSweepStep.setMaximumWidth(80)
        self.spinSweepStep.setDecimals(1)
        self.spinSweepStep.setMinimum(0.100000000000000)
        self.spinSweepStep.setMaximum(90.000000000000000)
        self.spinSweepStep.setSingleStep(0.500000000000000)
        self.spinSweepStep.setValue(5.000000000000000)

        self.formSweepParams.setWidget(2, QFormLayout.ItemRole.FieldRole, self.spinSweepStep)

        self.lblSettleMs = QLabel(self.gbSweep)
        self.lblSettleMs.setObjectName("lblSettleMs")

        self.formSweepParams.setWidget(3, QFormLayout.ItemRole.LabelRole, self.lblSettleMs)

        self.spinSettleMs = QSpinBox(self.gbSweep)
        self.spinSettleMs.setObjectName("spinSettleMs")
        self.spinSettleMs.setMaximumWidth(80)
        self.spinSettleMs.setMinimum(0)
        self.spinSettleMs.setMaximum(5000)
        self.spinSettleMs.setSingleStep(50)
        self.spinSettleMs.setValue(150)

        self.formSweepParams.setWidget(3, QFormLayout.ItemRole.FieldRole, self.spinSettleMs)

        self.vboxSweep.addLayout(self.formSweepParams)

        self.btnStartSweep = QPushButton(self.gbSweep)
        self.btnStartSweep.setObjectName("btnStartSweep")
        self.btnStartSweep.setEnabled(False)

        self.vboxSweep.addWidget(self.btnStartSweep)

        self.btnAbortSweep = QPushButton(self.gbSweep)
        self.btnAbortSweep.setObjectName("btnAbortSweep")
        self.btnAbortSweep.setEnabled(False)

        self.vboxSweep.addWidget(self.btnAbortSweep)

        self.rightLayout.addWidget(self.gbSweep)

        self.gbManual = QGroupBox(self.rightScrollContents)
        self.gbManual.setObjectName("gbManual")
        self.gbManual.setEnabled(False)
        self.vboxManual = QVBoxLayout(self.gbManual)
        self.vboxManual.setObjectName("vboxManual")
        self.vboxManual.setContentsMargins(6, 6, 6, 6)
        self.formManual = QFormLayout()
        self.formManual.setObjectName("formManual")
        self.formManual.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.FieldsStayAtSizeHint)
        self.lblAnalyserManual = QLabel(self.gbManual)
        self.lblAnalyserManual.setObjectName("lblAnalyserManual")

        self.formManual.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lblAnalyserManual)

        self.spinAnalyserManual = QDoubleSpinBox(self.gbManual)
        self.spinAnalyserManual.setObjectName("spinAnalyserManual")
        self.spinAnalyserManual.setMaximumWidth(90)
        self.spinAnalyserManual.setDecimals(2)
        self.spinAnalyserManual.setMinimum(-360.000000000000000)
        self.spinAnalyserManual.setMaximum(360.000000000000000)
        self.spinAnalyserManual.setSingleStep(1.000000000000000)
        self.spinAnalyserManual.setValue(0.000000000000000)

        self.formManual.setWidget(0, QFormLayout.ItemRole.FieldRole, self.spinAnalyserManual)

        self.vboxManual.addLayout(self.formManual)

        self.btnAddPoint = QPushButton(self.gbManual)
        self.btnAddPoint.setObjectName("btnAddPoint")

        self.vboxManual.addWidget(self.btnAddPoint)

        self.btnClearSweep = QPushButton(self.gbManual)
        self.btnClearSweep.setObjectName("btnClearSweep")

        self.vboxManual.addWidget(self.btnClearSweep)

        self.rightLayout.addWidget(self.gbManual)

        self.gbResult = QGroupBox(self.rightScrollContents)
        self.gbResult.setObjectName("gbResult")
        self.vboxResult = QVBoxLayout(self.gbResult)
        self.vboxResult.setObjectName("vboxResult")
        self.vboxResult.setContentsMargins(6, 6, 6, 6)
        self.formResult = QFormLayout()
        self.formResult.setObjectName("formResult")
        self.formResult.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.FieldsStayAtSizeHint)
        self.formResult.setVerticalSpacing(2)
        self.lblAlphaLabel = QLabel(self.gbResult)
        self.lblAlphaLabel.setObjectName("lblAlphaLabel")

        self.formResult.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lblAlphaLabel)

        self.lblAlpha = QLabel(self.gbResult)
        self.lblAlpha.setObjectName("lblAlpha")

        self.formResult.setWidget(0, QFormLayout.ItemRole.FieldRole, self.lblAlpha)

        self.lblBetaLabel = QLabel(self.gbResult)
        self.lblBetaLabel.setObjectName("lblBetaLabel")

        self.formResult.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lblBetaLabel)

        self.lblBeta = QLabel(self.gbResult)
        self.lblBeta.setObjectName("lblBeta")

        self.formResult.setWidget(1, QFormLayout.ItemRole.FieldRole, self.lblBeta)

        self.lblI0Label = QLabel(self.gbResult)
        self.lblI0Label.setObjectName("lblI0Label")

        self.formResult.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lblI0Label)

        self.lblI0 = QLabel(self.gbResult)
        self.lblI0.setObjectName("lblI0")

        self.formResult.setWidget(2, QFormLayout.ItemRole.FieldRole, self.lblI0)

        self.lblResidualLabel = QLabel(self.gbResult)
        self.lblResidualLabel.setObjectName("lblResidualLabel")

        self.formResult.setWidget(3, QFormLayout.ItemRole.LabelRole, self.lblResidualLabel)

        self.lblResidual = QLabel(self.gbResult)
        self.lblResidual.setObjectName("lblResidual")

        self.formResult.setWidget(3, QFormLayout.ItemRole.FieldRole, self.lblResidual)

        self.lblModulationLabel = QLabel(self.gbResult)
        self.lblModulationLabel.setObjectName("lblModulationLabel")

        self.formResult.setWidget(4, QFormLayout.ItemRole.LabelRole, self.lblModulationLabel)

        self.lblModulation = QLabel(self.gbResult)
        self.lblModulation.setObjectName("lblModulation")

        self.formResult.setWidget(4, QFormLayout.ItemRole.FieldRole, self.lblModulation)

        self.lblPsiLabel = QLabel(self.gbResult)
        self.lblPsiLabel.setObjectName("lblPsiLabel")

        self.formResult.setWidget(5, QFormLayout.ItemRole.LabelRole, self.lblPsiLabel)

        self.lblPsi = QLabel(self.gbResult)
        self.lblPsi.setObjectName("lblPsi")

        self.formResult.setWidget(5, QFormLayout.ItemRole.FieldRole, self.lblPsi)

        self.lblDeltaLabel = QLabel(self.gbResult)
        self.lblDeltaLabel.setObjectName("lblDeltaLabel")

        self.formResult.setWidget(6, QFormLayout.ItemRole.LabelRole, self.lblDeltaLabel)

        self.lblDelta = QLabel(self.gbResult)
        self.lblDelta.setObjectName("lblDelta")

        self.formResult.setWidget(6, QFormLayout.ItemRole.FieldRole, self.lblDelta)

        self.lblNPseudoLabel = QLabel(self.gbResult)
        self.lblNPseudoLabel.setObjectName("lblNPseudoLabel")

        self.formResult.setWidget(7, QFormLayout.ItemRole.LabelRole, self.lblNPseudoLabel)

        self.lblNPseudo = QLabel(self.gbResult)
        self.lblNPseudo.setObjectName("lblNPseudo")

        self.formResult.setWidget(7, QFormLayout.ItemRole.FieldRole, self.lblNPseudo)

        self.lblKPseudoLabel = QLabel(self.gbResult)
        self.lblKPseudoLabel.setObjectName("lblKPseudoLabel")

        self.formResult.setWidget(8, QFormLayout.ItemRole.LabelRole, self.lblKPseudoLabel)

        self.lblKPseudo = QLabel(self.gbResult)
        self.lblKPseudo.setObjectName("lblKPseudo")

        self.formResult.setWidget(8, QFormLayout.ItemRole.FieldRole, self.lblKPseudo)

        self.vboxResult.addLayout(self.formResult)

        self.btnAcceptPoint = QPushButton(self.gbResult)
        self.btnAcceptPoint.setObjectName("btnAcceptPoint")
        self.btnAcceptPoint.setEnabled(False)

        self.vboxResult.addWidget(self.btnAcceptPoint)

        self.rightLayout.addWidget(self.gbResult)

        self.gbModel = QGroupBox(self.rightScrollContents)
        self.gbModel.setObjectName("gbModel")
        self.vboxModel = QVBoxLayout(self.gbModel)
        self.vboxModel.setObjectName("vboxModel")
        self.vboxModel.setContentsMargins(6, 6, 6, 6)
        self.formModel = QFormLayout()
        self.formModel.setObjectName("formModel")
        self.formModel.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.FieldsStayAtSizeHint)
        self.formModel.setVerticalSpacing(3)
        self.lblModelType = QLabel(self.gbModel)
        self.lblModelType.setObjectName("lblModelType")

        self.formModel.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lblModelType)

        self.cmbModel = QComboBox(self.gbModel)
        self.cmbModel.addItem("")
        self.cmbModel.addItem("")
        self.cmbModel.setObjectName("cmbModel")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.cmbModel.sizePolicy().hasHeightForWidth())
        self.cmbModel.setSizePolicy(sizePolicy4)

        self.formModel.setWidget(0, QFormLayout.ItemRole.FieldRole, self.cmbModel)

        self.lblSubstrateN = QLabel(self.gbModel)
        self.lblSubstrateN.setObjectName("lblSubstrateN")

        self.formModel.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lblSubstrateN)

        self.spinSubstrateN = QDoubleSpinBox(self.gbModel)
        self.spinSubstrateN.setObjectName("spinSubstrateN")
        self.spinSubstrateN.setMaximumWidth(70)
        self.spinSubstrateN.setDecimals(3)
        self.spinSubstrateN.setMinimum(0.100000000000000)
        self.spinSubstrateN.setMaximum(10.000000000000000)
        self.spinSubstrateN.setSingleStep(0.010000000000000)
        self.spinSubstrateN.setValue(3.880000000000000)

        self.formModel.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spinSubstrateN)

        self.lblSubstrateK = QLabel(self.gbModel)
        self.lblSubstrateK.setObjectName("lblSubstrateK")

        self.formModel.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lblSubstrateK)

        self.spinSubstrateK = QDoubleSpinBox(self.gbModel)
        self.spinSubstrateK.setObjectName("spinSubstrateK")
        self.spinSubstrateK.setMaximumWidth(70)
        self.spinSubstrateK.setDecimals(3)
        self.spinSubstrateK.setMinimum(0.000000000000000)
        self.spinSubstrateK.setMaximum(10.000000000000000)
        self.spinSubstrateK.setSingleStep(0.010000000000000)
        self.spinSubstrateK.setValue(0.020000000000000)

        self.formModel.setWidget(2, QFormLayout.ItemRole.FieldRole, self.spinSubstrateK)

        self.lblDMin = QLabel(self.gbModel)
        self.lblDMin.setObjectName("lblDMin")

        self.formModel.setWidget(3, QFormLayout.ItemRole.LabelRole, self.lblDMin)

        self.hboxDRange = QHBoxLayout()
        self.hboxDRange.setObjectName("hboxDRange")
        self.spinDMin = QDoubleSpinBox(self.gbModel)
        self.spinDMin.setObjectName("spinDMin")
        self.spinDMin.setMaximumWidth(90)
        self.spinDMin.setDecimals(0)
        self.spinDMin.setMinimum(0.000000000000000)
        self.spinDMin.setMaximum(100000.000000000000000)
        self.spinDMin.setValue(0.000000000000000)

        self.hboxDRange.addWidget(self.spinDMin)

        self.spinDMax = QDoubleSpinBox(self.gbModel)
        self.spinDMax.setObjectName("spinDMax")
        self.spinDMax.setMaximumWidth(90)
        self.spinDMax.setDecimals(0)
        self.spinDMax.setMinimum(0.000000000000000)
        self.spinDMax.setMaximum(100000.000000000000000)
        self.spinDMax.setValue(1000.000000000000000)

        self.hboxDRange.addWidget(self.spinDMax)

        self.formModel.setLayout(3, QFormLayout.ItemRole.FieldRole, self.hboxDRange)

        self.lblNfMin = QLabel(self.gbModel)
        self.lblNfMin.setObjectName("lblNfMin")

        self.formModel.setWidget(4, QFormLayout.ItemRole.LabelRole, self.lblNfMin)

        self.hboxNRange = QHBoxLayout()
        self.hboxNRange.setObjectName("hboxNRange")
        self.spinNfMin = QDoubleSpinBox(self.gbModel)
        self.spinNfMin.setObjectName("spinNfMin")
        self.spinNfMin.setMaximumWidth(70)
        self.spinNfMin.setDecimals(3)
        self.spinNfMin.setMinimum(1.000000000000000)
        self.spinNfMin.setMaximum(10.000000000000000)
        self.spinNfMin.setValue(1.200000000000000)

        self.hboxNRange.addWidget(self.spinNfMin)

        self.spinNfMax = QDoubleSpinBox(self.gbModel)
        self.spinNfMax.setObjectName("spinNfMax")
        self.spinNfMax.setMaximumWidth(70)
        self.spinNfMax.setDecimals(3)
        self.spinNfMax.setMinimum(1.000000000000000)
        self.spinNfMax.setMaximum(10.000000000000000)
        self.spinNfMax.setValue(3.000000000000000)

        self.hboxNRange.addWidget(self.spinNfMax)

        self.formModel.setLayout(4, QFormLayout.ItemRole.FieldRole, self.hboxNRange)

        self.vboxModel.addLayout(self.formModel)

        self.cbFitK = QCheckBox(self.gbModel)
        self.cbFitK.setObjectName("cbFitK")

        self.vboxModel.addWidget(self.cbFitK)

        self.btnFitModel = QPushButton(self.gbModel)
        self.btnFitModel.setObjectName("btnFitModel")
        self.btnFitModel.setEnabled(False)

        self.vboxModel.addWidget(self.btnFitModel)

        self.formModelResult = QFormLayout()
        self.formModelResult.setObjectName("formModelResult")
        self.formModelResult.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.FieldsStayAtSizeHint
        )
        self.formModelResult.setVerticalSpacing(2)
        self.lblThicknessLabel = QLabel(self.gbModel)
        self.lblThicknessLabel.setObjectName("lblThicknessLabel")

        self.formModelResult.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lblThicknessLabel)

        self.lblThickness = QLabel(self.gbModel)
        self.lblThickness.setObjectName("lblThickness")

        self.formModelResult.setWidget(0, QFormLayout.ItemRole.FieldRole, self.lblThickness)

        self.lblNFilmLabel = QLabel(self.gbModel)
        self.lblNFilmLabel.setObjectName("lblNFilmLabel")

        self.formModelResult.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lblNFilmLabel)

        self.lblNFilm = QLabel(self.gbModel)
        self.lblNFilm.setObjectName("lblNFilm")

        self.formModelResult.setWidget(1, QFormLayout.ItemRole.FieldRole, self.lblNFilm)

        self.lblKFilmLabel = QLabel(self.gbModel)
        self.lblKFilmLabel.setObjectName("lblKFilmLabel")

        self.formModelResult.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lblKFilmLabel)

        self.lblKFilm = QLabel(self.gbModel)
        self.lblKFilm.setObjectName("lblKFilm")

        self.formModelResult.setWidget(2, QFormLayout.ItemRole.FieldRole, self.lblKFilm)

        self.lblMSELabel = QLabel(self.gbModel)
        self.lblMSELabel.setObjectName("lblMSELabel")

        self.formModelResult.setWidget(3, QFormLayout.ItemRole.LabelRole, self.lblMSELabel)

        self.lblMSE = QLabel(self.gbModel)
        self.lblMSE.setObjectName("lblMSE")

        self.formModelResult.setWidget(3, QFormLayout.ItemRole.FieldRole, self.lblMSE)

        self.vboxModel.addLayout(self.formModelResult)

        self.lblBranches = QLabel(self.gbModel)
        self.lblBranches.setObjectName("lblBranches")
        self.lblBranches.setWordWrap(True)

        self.vboxModel.addWidget(self.lblBranches)

        self.rightLayout.addWidget(self.gbModel)

        self.btnDeleteSelected = QPushButton(self.rightScrollContents)
        self.btnDeleteSelected.setObjectName("btnDeleteSelected")
        self.btnDeleteSelected.setEnabled(False)

        self.rightLayout.addWidget(self.btnDeleteSelected)

        self.btnDeleteLast = QPushButton(self.rightScrollContents)
        self.btnDeleteLast.setObjectName("btnDeleteLast")
        self.btnDeleteLast.setEnabled(False)

        self.rightLayout.addWidget(self.btnDeleteLast)

        self.btnClear = QPushButton(self.rightScrollContents)
        self.btnClear.setObjectName("btnClear")
        self.btnClear.setEnabled(False)

        self.rightLayout.addWidget(self.btnClear)

        self.rightScroll.setWidget(self.rightScrollContents)

        self.gridLayout.addWidget(self.rightScroll, 0, 1, 2, 1)

        self.gridLayout.setRowStretch(0, 2)
        self.gridLayout.setColumnStretch(0, 2)

        self.retranslateUi(EllipsometryTab)

        QMetaObject.connectSlotsByName(EllipsometryTab)

    # setupUi

    def retranslateUi(self, EllipsometryTab):
        ___qtablewidgetitem = self.seriesTable.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(
            QCoreApplication.translate("EllipsometryTab", "\u03b8 (\u00b0)", None)
        )
        ___qtablewidgetitem1 = self.seriesTable.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(
            QCoreApplication.translate("EllipsometryTab", "\u03a8 (\u00b0)", None)
        )
        ___qtablewidgetitem2 = self.seriesTable.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(
            QCoreApplication.translate("EllipsometryTab", "\u0394 (\u00b0)", None)
        )
        ___qtablewidgetitem3 = self.seriesTable.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("EllipsometryTab", "n", None))
        ___qtablewidgetitem4 = self.seriesTable.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("EllipsometryTab", "k", None))
        ___qtablewidgetitem5 = self.seriesTable.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("EllipsometryTab", "N", None))
        ___qtablewidgetitem6 = self.seriesTable.horizontalHeaderItem(6)
        ___qtablewidgetitem6.setText(
            QCoreApplication.translate("EllipsometryTab", "RMS (\u00b5W)", None)
        )
        ___qtablewidgetitem7 = self.seriesTable.horizontalHeaderItem(7)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("EllipsometryTab", "m", None))
        self.gbLive.setTitle(QCoreApplication.translate("EllipsometryTab", "Aktuell", None))
        self.lblLiveIntensityLabel.setText(
            QCoreApplication.translate("EllipsometryTab", "I:", None)
        )
        self.lblLiveIntensity.setText(QCoreApplication.translate("EllipsometryTab", "\u2014", None))
        self.lblLivePowerLabel.setText(QCoreApplication.translate("EllipsometryTab", "P:", None))
        self.lblLivePower.setText(QCoreApplication.translate("EllipsometryTab", "\u2014", None))
        self.lblLiveAoiLabel.setText(
            QCoreApplication.translate("EllipsometryTab", "AOI \u03b8:", None)
        )
        self.lblLiveAoi.setText(QCoreApplication.translate("EllipsometryTab", "\u2014", None))
        self.lblLiveDetectorLabel.setText(
            QCoreApplication.translate("EllipsometryTab", "Detektorarm:", None)
        )
        self.lblLiveDetector.setText(QCoreApplication.translate("EllipsometryTab", "\u2014", None))
        self.lblSpecularErrorLabel.setText(
            QCoreApplication.translate("EllipsometryTab", "Spiegel-Fehler:", None)
        )
        # if QT_CONFIG(tooltip)
        self.lblSpecularError.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab",
                "Abweichung des Detektorarms von 2\u00b7\u03b8 (Spiegelbedingung) \u2014 gro\u00dfer Wert deutet auf eine Fehljustage hin",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.lblSpecularError.setText(QCoreApplication.translate("EllipsometryTab", "\u2014", None))
        self.lblKDCPositionLabel.setText(
            QCoreApplication.translate("EllipsometryTab", "Analysator-Position:", None)
        )
        self.lblKDCPosition.setText(QCoreApplication.translate("EllipsometryTab", "\u2014", None))
        self.gbSetup.setTitle(QCoreApplication.translate("EllipsometryTab", "Konfiguration", None))
        self.lblWavelength.setText(
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
        self.lblPolariser.setText(
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
        self.lblAnalyserOffset.setText(
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
        self.lblAmbientIndex.setText(
            QCoreApplication.translate("EllipsometryTab", "Umgebung n\u2080:", None)
        )
        # if QT_CONFIG(tooltip)
        self.spinAmbientIndex.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab", "Brechungsindex des Umgebungsmediums (Luft \u2248 1.0003)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.lblKdcZeroOffsetLabel.setText(
            QCoreApplication.translate("EllipsometryTab", "KDC-Nullpunkt:", None)
        )
        # if QT_CONFIG(tooltip)
        self.lblKdcZeroOffset.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab",
                "Aktueller kdc.zero_offset_deg aus der Konfiguration (Referenzierung auf den Polarisator)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.lblKdcZeroOffset.setText(QCoreApplication.translate("EllipsometryTab", "\u2014", None))
        # if QT_CONFIG(tooltip)
        self.btnSetAoiZero.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab",
                "Aktuelle Proben- und Detektorarm-Winkel als Geradeausstrahl-Referenz (AOI = 0\u00b0) \u00fcbernehmen",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnSetAoiZero.setText(
            QCoreApplication.translate("EllipsometryTab", "AOI-Nullpunkt setzen", None)
        )
        self.gbSweep.setTitle(
            QCoreApplication.translate("EllipsometryTab", "Automatischer Scan (KDC101)", None)
        )
        # if QT_CONFIG(tooltip)
        self.cbAnalyserPlaced.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab",
                "Best\u00e4tigen, dass der Analysator im Strahlengang eingesetzt ist",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.cbAnalyserPlaced.setText(
            QCoreApplication.translate("EllipsometryTab", "Analysator eingesetzt", None)
        )
        self.lblSweepStart.setText(
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
        self.lblSweepEnd.setText(
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
        self.lblSweepStep.setText(
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
        self.lblSettleMs.setText(
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
        self.btnStartSweep.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab",
                "Automatischen Analysator-Scan starten (erneutes Homing nur falls n\u00f6tig)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnStartSweep.setText(
            QCoreApplication.translate("EllipsometryTab", "Scan starten", None)
        )
        # if QT_CONFIG(tooltip)
        self.btnAbortSweep.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab", "Laufenden automatischen Scan sofort abbrechen", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnAbortSweep.setText(QCoreApplication.translate("EllipsometryTab", "Abbrechen", None))
        self.gbManual.setTitle(
            QCoreApplication.translate("EllipsometryTab", "Manueller Analysatorpunkt", None)
        )
        self.lblAnalyserManual.setText(
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
        self.btnAddPoint.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab",
                "Aktuellen Analysatorwinkel mit gemittelter Leistung zum Sweep-Puffer hinzuf\u00fcgen",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnAddPoint.setText(
            QCoreApplication.translate("EllipsometryTab", "Punkt hinzuf\u00fcgen", None)
        )
        # if QT_CONFIG(tooltip)
        self.btnClearSweep.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab",
                "Sweep-Puffer der aktuellen AOI-Messung leeren (ohne die Serie zu ver\u00e4ndern)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnClearSweep.setText(
            QCoreApplication.translate("EllipsometryTab", "Sweep-Puffer leeren", None)
        )
        self.gbResult.setTitle(
            QCoreApplication.translate("EllipsometryTab", "Fit-Ergebnis (aktuelle AOI)", None)
        )
        self.lblAlphaLabel.setText(QCoreApplication.translate("EllipsometryTab", "\u03b1:", None))
        self.lblAlpha.setText(QCoreApplication.translate("EllipsometryTab", "\u2014", None))
        self.lblBetaLabel.setText(QCoreApplication.translate("EllipsometryTab", "\u03b2:", None))
        self.lblBeta.setText(QCoreApplication.translate("EllipsometryTab", "\u2014", None))
        self.lblI0Label.setText(QCoreApplication.translate("EllipsometryTab", "I\u2080:", None))
        self.lblI0.setText(QCoreApplication.translate("EllipsometryTab", "\u2014", None))
        self.lblResidualLabel.setText(
            QCoreApplication.translate("EllipsometryTab", "Residuum:", None)
        )
        self.lblResidual.setText(QCoreApplication.translate("EllipsometryTab", "\u2014", None))
        self.lblModulationLabel.setText(
            QCoreApplication.translate("EllipsometryTab", "Modulation m:", None)
        )
        # if QT_CONFIG(tooltip)
        self.lblModulation.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab",
                "sqrt(\u03b1\u00b2+\u03b2\u00b2) \u2014 muss < 1 sein, sonst ist der Fit unphysikalisch",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.lblModulation.setText(QCoreApplication.translate("EllipsometryTab", "\u2014", None))
        self.lblPsiLabel.setText(QCoreApplication.translate("EllipsometryTab", "\u03a8:", None))
        self.lblPsi.setText(QCoreApplication.translate("EllipsometryTab", "\u2014", None))
        self.lblDeltaLabel.setText(QCoreApplication.translate("EllipsometryTab", "\u0394:", None))
        # if QT_CONFIG(tooltip)
        self.lblDelta.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab",
                "Nur cos(\u0394) wird gemessen \u2014 das Vorzeichen von \u0394 ist prinzipiell unbestimmt",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.lblDelta.setText(QCoreApplication.translate("EllipsometryTab", "\u2014", None))
        self.lblNPseudoLabel.setText(
            QCoreApplication.translate("EllipsometryTab", "n (pseudo):", None)
        )
        self.lblNPseudo.setText(QCoreApplication.translate("EllipsometryTab", "\u2014", None))
        self.lblKPseudoLabel.setText(
            QCoreApplication.translate("EllipsometryTab", "k (pseudo):", None)
        )
        self.lblKPseudo.setText(QCoreApplication.translate("EllipsometryTab", "\u2014", None))
        # if QT_CONFIG(tooltip)
        self.btnAcceptPoint.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab",
                "Aktuellen Fit als Messpunkt dieser AOI in die \u03a8(\u03b8)/\u0394(\u03b8)-Serie \u00fcbernehmen und den Sweep-Puffer f\u00fcr die n\u00e4chste AOI leeren",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnAcceptPoint.setText(
            QCoreApplication.translate("EllipsometryTab", "In Serie \u00fcbernehmen", None)
        )
        self.gbModel.setTitle(
            QCoreApplication.translate("EllipsometryTab", "Optisches Modell", None)
        )
        self.lblModelType.setText(QCoreApplication.translate("EllipsometryTab", "Modell:", None))
        self.cmbModel.setItemText(
            0, QCoreApplication.translate("EllipsometryTab", "Substrat (2-Phasen)", None)
        )
        self.cmbModel.setItemText(
            1, QCoreApplication.translate("EllipsometryTab", "Schicht auf Substrat (3-Ph.)", None)
        )

        # if QT_CONFIG(tooltip)
        self.cmbModel.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab",
                "2-Phasen: Probe als Substrat behandeln (Pseudo-n,k). 3-Phasen: Schichtdicke und -index auf bekanntem Substrat fitten",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.lblSubstrateN.setText(
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
        self.lblSubstrateK.setText(
            QCoreApplication.translate("EllipsometryTab", "Substrat k:", None)
        )
        # if QT_CONFIG(tooltip)
        self.spinSubstrateK.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab", "Bekannter Extinktionskoeffizient des Substrats bei \u03bb", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.lblDMin.setText(QCoreApplication.translate("EllipsometryTab", "d-Suchbereich:", None))
        self.spinDMin.setSuffix(QCoreApplication.translate("EllipsometryTab", " nm", None))
        self.spinDMax.setSuffix(QCoreApplication.translate("EllipsometryTab", " nm", None))
        self.lblNfMin.setText(QCoreApplication.translate("EllipsometryTab", "n-Suchbereich:", None))
        # if QT_CONFIG(tooltip)
        self.cbFitK.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab",
                "Absorption k der Schicht mitfitten (grobes festes Raster, 0\u20262) \u2014 f\u00fcr transparente Schichten (k=0) deaktiviert lassen, sonst ist das Problem unterbestimmt",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.cbFitK.setText(
            QCoreApplication.translate("EllipsometryTab", "k der Schicht mitfitten", None)
        )
        # if QT_CONFIG(tooltip)
        self.btnFitModel.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab",
                "Optisches Modell an die gesamte \u03a8(\u03b8)/\u0394(\u03b8)-Serie anpassen (mindestens 1 AOI-Punkt erforderlich)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnFitModel.setText(
            QCoreApplication.translate("EllipsometryTab", "Modell fitten", None)
        )
        self.lblThicknessLabel.setText(
            QCoreApplication.translate("EllipsometryTab", "Dicke d:", None)
        )
        self.lblThickness.setText(QCoreApplication.translate("EllipsometryTab", "\u2014", None))
        self.lblNFilmLabel.setText(
            QCoreApplication.translate("EllipsometryTab", "n (Schicht):", None)
        )
        self.lblNFilm.setText(QCoreApplication.translate("EllipsometryTab", "\u2014", None))
        self.lblKFilmLabel.setText(
            QCoreApplication.translate("EllipsometryTab", "k (Schicht):", None)
        )
        self.lblKFilm.setText(QCoreApplication.translate("EllipsometryTab", "\u2014", None))
        self.lblMSELabel.setText(QCoreApplication.translate("EllipsometryTab", "MSE:", None))
        self.lblMSE.setText(QCoreApplication.translate("EllipsometryTab", "\u2014", None))
        # if QT_CONFIG(tooltip)
        self.lblBranches.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab",
                "Alternative Schichtdicken-L\u00f6sungen (Perioden-Mehrdeutigkeit bei einer Wellenl\u00e4nge) \u2014 durch weitere AOI-Punkte aufl\u00f6sbar",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.lblBranches.setText("")
        # if QT_CONFIG(tooltip)
        self.btnDeleteSelected.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab", "Markierte AOI-Zeile aus der Serie l\u00f6schen", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnDeleteSelected.setText(
            QCoreApplication.translate("EllipsometryTab", "Ausgew\u00e4hlte AOI l\u00f6schen", None)
        )
        # if QT_CONFIG(tooltip)
        self.btnDeleteLast.setToolTip(
            QCoreApplication.translate(
                "EllipsometryTab", "Letzte AOI-Zeile aus der Serie l\u00f6schen", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnDeleteLast.setText(
            QCoreApplication.translate("EllipsometryTab", "Letzte AOI l\u00f6schen", None)
        )
        # if QT_CONFIG(tooltip)
        self.btnClear.setToolTip(
            QCoreApplication.translate("EllipsometryTab", "Gesamte Serie l\u00f6schen", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.btnClear.setText(
            QCoreApplication.translate("EllipsometryTab", "Alle l\u00f6schen", None)
        )
        pass

    # retranslateUi
