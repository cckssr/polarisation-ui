# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'malus_tab.ui'
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
    QDoubleSpinBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHeaderView,
    QLabel,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from polarisation_ui.ui.widgets.malus_curve_plot import MalusCurvePlot


class Ui_MalusTab(object):
    def setupUi(self, MalusTab):
        if not MalusTab.objectName():
            MalusTab.setObjectName("MalusTab")
        MalusTab.resize(963, 896)
        self.gridLayout = QGridLayout(MalusTab)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.pointsTable = QTableWidget(MalusTab)
        if self.pointsTable.columnCount() < 5:
            self.pointsTable.setColumnCount(5)
        __qtablewidgetitem = QTableWidgetItem()
        self.pointsTable.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.pointsTable.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.pointsTable.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.pointsTable.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.pointsTable.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        self.pointsTable.setObjectName("pointsTable")
        self.pointsTable.setMinimumSize(QSize(0, 120))
        self.pointsTable.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.pointsTable.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.pointsTable.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.pointsTable.verticalHeader().setVisible(False)

        self.gridLayout.addWidget(self.pointsTable, 1, 0, 1, 1)

        self.rightLayout = QVBoxLayout()
        self.rightLayout.setSpacing(6)
        self.rightLayout.setObjectName("rightLayout")
        self.rightLayout.setContentsMargins(4, 0, 0, 0)
        self.gbLive = QGroupBox(MalusTab)
        self.gbLive.setObjectName("gbLive")
        self.formLive = QFormLayout(self.gbLive)
        self.formLive.setObjectName("formLive")
        self.formLive.setVerticalSpacing(2)
        self.formLive.setContentsMargins(6, 4, 6, 4)
        self.lblLiveIntensityLabel = QLabel(self.gbLive)
        self.lblLiveIntensityLabel.setObjectName("lblLiveIntensityLabel")

        self.formLive.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lblLiveIntensityLabel)

        self.lblLiveIntensity = QLabel(self.gbLive)
        self.lblLiveIntensity.setObjectName("lblLiveIntensity")

        self.formLive.setWidget(1, QFormLayout.ItemRole.FieldRole, self.lblLiveIntensity)

        self.lblLivePowerLabel = QLabel(self.gbLive)
        self.lblLivePowerLabel.setObjectName("lblLivePowerLabel")

        self.formLive.setWidget(3, QFormLayout.ItemRole.LabelRole, self.lblLivePowerLabel)

        self.lblLivePower = QLabel(self.gbLive)
        self.lblLivePower.setObjectName("lblLivePower")

        self.formLive.setWidget(3, QFormLayout.ItemRole.FieldRole, self.lblLivePower)

        self.lblLiveVoltageLabel = QLabel(self.gbLive)
        self.lblLiveVoltageLabel.setObjectName("lblLiveVoltageLabel")

        self.formLive.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lblLiveVoltageLabel)

        self.lblLiveVoltage = QLabel(self.gbLive)
        self.lblLiveVoltage.setObjectName("lblLiveVoltage")

        self.formLive.setWidget(0, QFormLayout.ItemRole.FieldRole, self.lblLiveVoltage)

        self.rightLayout.addWidget(self.gbLive)

        self.gbEntry = QGroupBox(MalusTab)
        self.gbEntry.setObjectName("gbEntry")
        self.formEntry = QFormLayout(self.gbEntry)
        self.formEntry.setObjectName("formEntry")
        self.formEntry.setVerticalSpacing(4)
        self.formEntry.setContentsMargins(6, 6, 6, 6)
        self.lblPolariser = QLabel(self.gbEntry)
        self.lblPolariser.setObjectName("lblPolariser")

        self.formEntry.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lblPolariser)

        self.spinPolariser = QDoubleSpinBox(self.gbEntry)
        self.spinPolariser.setObjectName("spinPolariser")
        self.spinPolariser.setDecimals(2)
        self.spinPolariser.setMinimum(-360.000000000000000)
        self.spinPolariser.setMaximum(360.000000000000000)
        self.spinPolariser.setSingleStep(1.000000000000000)
        self.spinPolariser.setValue(0.000000000000000)

        self.formEntry.setWidget(0, QFormLayout.ItemRole.FieldRole, self.spinPolariser)

        self.lblAnalyser = QLabel(self.gbEntry)
        self.lblAnalyser.setObjectName("lblAnalyser")

        self.formEntry.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lblAnalyser)

        self.spinAnalyser = QDoubleSpinBox(self.gbEntry)
        self.spinAnalyser.setObjectName("spinAnalyser")
        self.spinAnalyser.setEnabled(False)
        self.spinAnalyser.setDecimals(2)
        self.spinAnalyser.setMinimum(-360.000000000000000)
        self.spinAnalyser.setMaximum(360.000000000000000)
        self.spinAnalyser.setSingleStep(1.000000000000000)
        self.spinAnalyser.setValue(0.000000000000000)

        self.formEntry.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spinAnalyser)

        self.btnAdd = QPushButton(self.gbEntry)
        self.btnAdd.setObjectName("btnAdd")
        self.btnAdd.setEnabled(False)

        self.formEntry.setWidget(2, QFormLayout.ItemRole.SpanningRole, self.btnAdd)

        self.rightLayout.addWidget(self.gbEntry)

        self.gbSweep = QGroupBox(MalusTab)
        self.gbSweep.setObjectName("gbSweep")
        self.gbSweep.setEnabled(False)
        self.vboxSweep = QVBoxLayout(self.gbSweep)
        self.vboxSweep.setObjectName("vboxSweep")
        self.vboxSweep.setContentsMargins(6, 6, 6, 6)
        self.cbPolariserPlaced = QCheckBox(self.gbSweep)
        self.cbPolariserPlaced.setObjectName("cbPolariserPlaced")

        self.vboxSweep.addWidget(self.cbPolariserPlaced)

        self.formSweepParams = QFormLayout()
        self.formSweepParams.setObjectName("formSweepParams")
        self.formSweepParams.setVerticalSpacing(3)
        self.lblZeroOffsetLabel = QLabel(self.gbSweep)
        self.lblZeroOffsetLabel.setObjectName("lblZeroOffsetLabel")

        self.formSweepParams.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lblZeroOffsetLabel)

        self.lblZeroOffset = QLabel(self.gbSweep)
        self.lblZeroOffset.setObjectName("lblZeroOffset")

        self.formSweepParams.setWidget(0, QFormLayout.ItemRole.FieldRole, self.lblZeroOffset)

        self.lblSweepStart = QLabel(self.gbSweep)
        self.lblSweepStart.setObjectName("lblSweepStart")

        self.formSweepParams.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lblSweepStart)

        self.spinSweepStart = QDoubleSpinBox(self.gbSweep)
        self.spinSweepStart.setObjectName("spinSweepStart")
        self.spinSweepStart.setDecimals(1)
        self.spinSweepStart.setMinimum(0.000000000000000)
        self.spinSweepStart.setMaximum(360.000000000000000)
        self.spinSweepStart.setValue(0.000000000000000)

        self.formSweepParams.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spinSweepStart)

        self.lblSweepEnd = QLabel(self.gbSweep)
        self.lblSweepEnd.setObjectName("lblSweepEnd")

        self.formSweepParams.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lblSweepEnd)

        self.spinSweepEnd = QDoubleSpinBox(self.gbSweep)
        self.spinSweepEnd.setObjectName("spinSweepEnd")
        self.spinSweepEnd.setDecimals(1)
        self.spinSweepEnd.setMinimum(0.000000000000000)
        self.spinSweepEnd.setMaximum(360.000000000000000)
        self.spinSweepEnd.setValue(180.000000000000000)

        self.formSweepParams.setWidget(2, QFormLayout.ItemRole.FieldRole, self.spinSweepEnd)

        self.lblSweepStep = QLabel(self.gbSweep)
        self.lblSweepStep.setObjectName("lblSweepStep")

        self.formSweepParams.setWidget(3, QFormLayout.ItemRole.LabelRole, self.lblSweepStep)

        self.spinSweepStep = QDoubleSpinBox(self.gbSweep)
        self.spinSweepStep.setObjectName("spinSweepStep")
        self.spinSweepStep.setDecimals(1)
        self.spinSweepStep.setMinimum(0.100000000000000)
        self.spinSweepStep.setMaximum(90.000000000000000)
        self.spinSweepStep.setSingleStep(0.500000000000000)
        self.spinSweepStep.setValue(5.000000000000000)

        self.formSweepParams.setWidget(3, QFormLayout.ItemRole.FieldRole, self.spinSweepStep)

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

        self.btnDeleteSelected = QPushButton(MalusTab)
        self.btnDeleteSelected.setObjectName("btnDeleteSelected")
        self.btnDeleteSelected.setEnabled(False)

        self.rightLayout.addWidget(self.btnDeleteSelected)

        self.btnDeleteLast = QPushButton(MalusTab)
        self.btnDeleteLast.setObjectName("btnDeleteLast")
        self.btnDeleteLast.setEnabled(False)

        self.rightLayout.addWidget(self.btnDeleteLast)

        self.btnClear = QPushButton(MalusTab)
        self.btnClear.setObjectName("btnClear")
        self.btnClear.setEnabled(False)

        self.rightLayout.addWidget(self.btnClear)

        self.gridLayout.addLayout(self.rightLayout, 1, 1, 1, 1)

        self.malusCurvePlot = MalusCurvePlot(MalusTab)
        self.malusCurvePlot.setObjectName("malusCurvePlot")

        self.gridLayout.addWidget(self.malusCurvePlot, 0, 0, 1, 2)

        self.gridLayout.setRowStretch(0, 2)
        self.gridLayout.setRowStretch(1, 1)
        self.gridLayout.setColumnStretch(0, 2)

        self.retranslateUi(MalusTab)

        QMetaObject.connectSlotsByName(MalusTab)

    # setupUi

    def retranslateUi(self, MalusTab):
        ___qtablewidgetitem = self.pointsTable.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(
            QCoreApplication.translate("MalusTab", "\u03b8_A (\u00b0)", None)
        )
        ___qtablewidgetitem1 = self.pointsTable.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(
            QCoreApplication.translate("MalusTab", "\u03b8_P (\u00b0)", None)
        )
        ___qtablewidgetitem2 = self.pointsTable.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MalusTab", "I (mV)", None))
        ___qtablewidgetitem3 = self.pointsTable.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("MalusTab", "P (\u00b5W)", None))
        ___qtablewidgetitem4 = self.pointsTable.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("MalusTab", "Gain", None))
        self.gbLive.setTitle(QCoreApplication.translate("MalusTab", "Aktuell", None))
        self.lblLiveIntensityLabel.setText(QCoreApplication.translate("MalusTab", "I:", None))
        self.lblLiveIntensity.setText(QCoreApplication.translate("MalusTab", "\u2014", None))
        self.lblLivePowerLabel.setText(QCoreApplication.translate("MalusTab", "P:", None))
        self.lblLivePower.setText(QCoreApplication.translate("MalusTab", "\u2014", None))
        self.lblLiveVoltageLabel.setText(QCoreApplication.translate("MalusTab", "U:", None))
        self.lblLiveVoltage.setText(QCoreApplication.translate("MalusTab", "\u2014", None))
        self.gbEntry.setTitle(QCoreApplication.translate("MalusTab", "Messpunkt", None))
        self.lblPolariser.setText(
            QCoreApplication.translate("MalusTab", "Polarisator \u03b8_P:", None)
        )
        # if QT_CONFIG(tooltip)
        self.spinPolariser.setToolTip(
            QCoreApplication.translate(
                "MalusTab",
                "Polarisatorwinkel (fest f\u00fcr die gesamte Messreihe)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.spinPolariser.setSuffix(QCoreApplication.translate("MalusTab", " \u00b0", None))
        self.lblAnalyser.setText(
            QCoreApplication.translate("MalusTab", "Analysator \u03b8_A:", None)
        )
        # if QT_CONFIG(tooltip)
        self.spinAnalyser.setToolTip(
            QCoreApplication.translate(
                "MalusTab", "Analysatorwinkel f\u00fcr diesen Messpunkt", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.spinAnalyser.setSuffix(QCoreApplication.translate("MalusTab", " \u00b0", None))
        # if QT_CONFIG(tooltip)
        self.btnAdd.setToolTip(
            QCoreApplication.translate(
                "MalusTab",
                "Aktuellen Analysatorwinkel mit gemittelter Intensit\u00e4t speichern",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnAdd.setText(QCoreApplication.translate("MalusTab", "Punkt hinzuf\u00fcgen", None))
        self.gbSweep.setTitle(
            QCoreApplication.translate("MalusTab", "Automatischer Scan (KDC101)", None)
        )
        # if QT_CONFIG(tooltip)
        self.cbPolariserPlaced.setToolTip(
            QCoreApplication.translate(
                "MalusTab",
                "Best\u00e4tigen, dass der Polarisator im Strahlengang eingesetzt ist",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.cbPolariserPlaced.setText(
            QCoreApplication.translate("MalusTab", "Polarisator eingesetzt", None)
        )
        self.lblZeroOffsetLabel.setText(
            QCoreApplication.translate("MalusTab", "Zero-Offset:", None)
        )
        self.lblZeroOffset.setText(QCoreApplication.translate("MalusTab", "\u2014", None))
        self.lblSweepStart.setText(QCoreApplication.translate("MalusTab", "Von (\u00b0):", None))
        # if QT_CONFIG(tooltip)
        self.spinSweepStart.setToolTip(
            QCoreApplication.translate(
                "MalusTab", "Startwinkel des automatischen Scans (\u00b0)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.spinSweepStart.setSuffix(QCoreApplication.translate("MalusTab", " \u00b0", None))
        self.lblSweepEnd.setText(QCoreApplication.translate("MalusTab", "Bis (\u00b0):", None))
        # if QT_CONFIG(tooltip)
        self.spinSweepEnd.setToolTip(
            QCoreApplication.translate(
                "MalusTab", "Endwinkel des automatischen Scans (\u00b0)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.spinSweepEnd.setSuffix(QCoreApplication.translate("MalusTab", " \u00b0", None))
        self.lblSweepStep.setText(QCoreApplication.translate("MalusTab", "Schritt (\u00b0):", None))
        # if QT_CONFIG(tooltip)
        self.spinSweepStep.setToolTip(
            QCoreApplication.translate(
                "MalusTab", "Schrittweite des automatischen Scans (\u00b0)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.spinSweepStep.setSuffix(QCoreApplication.translate("MalusTab", " \u00b0", None))
        # if QT_CONFIG(tooltip)
        self.btnStartSweep.setToolTip(
            QCoreApplication.translate(
                "MalusTab", "Home, Auto-Zero und automatischer Scan starten", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnStartSweep.setText(QCoreApplication.translate("MalusTab", "Scan starten", None))
        # if QT_CONFIG(tooltip)
        self.btnAbortSweep.setToolTip(
            QCoreApplication.translate(
                "MalusTab", "Laufenden automatischen Scan sofort abbrechen", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnAbortSweep.setText(QCoreApplication.translate("MalusTab", "Abbrechen", None))
        # if QT_CONFIG(tooltip)
        self.btnDeleteSelected.setToolTip(
            QCoreApplication.translate(
                "MalusTab", "Markierten Punkt aus der Kurve l\u00f6schen", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnDeleteSelected.setText(
            QCoreApplication.translate("MalusTab", "Ausgew\u00e4hlten l\u00f6schen", None)
        )
        # if QT_CONFIG(tooltip)
        self.btnDeleteLast.setToolTip(
            QCoreApplication.translate(
                "MalusTab", "Letzten gespeicherten Messpunkt entfernen", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnDeleteLast.setText(
            QCoreApplication.translate("MalusTab", "Letzten Punkt l\u00f6schen", None)
        )
        # if QT_CONFIG(tooltip)
        self.btnClear.setToolTip(
            QCoreApplication.translate(
                "MalusTab", "Alle gespeicherten Messpunkte l\u00f6schen", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnClear.setText(QCoreApplication.translate("MalusTab", "Alle l\u00f6schen", None))
        pass

    # retranslateUi
