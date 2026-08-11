# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'waveplate_tab.ui'
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
    QGridLayout,
    QGroupBox,
    QHeaderView,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from polarisation_ui.ui.widgets.malus_curve_plot import MalusCurvePlot


class Ui_WaveplateTab(object):
    def setupUi(self, WaveplateTab):
        if not WaveplateTab.objectName():
            WaveplateTab.setObjectName("WaveplateTab")
        WaveplateTab.resize(1054, 626)
        self.gridLayout = QGridLayout(WaveplateTab)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setContentsMargins(0, 10, 0, 0)
        self.pointsTable = QTableWidget(WaveplateTab)
        if self.pointsTable.columnCount() < 4:
            self.pointsTable.setColumnCount(4)
        __qtablewidgetitem = QTableWidgetItem()
        self.pointsTable.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.pointsTable.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.pointsTable.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.pointsTable.setHorizontalHeaderItem(3, __qtablewidgetitem3)
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
        self.gbLive = QGroupBox(WaveplateTab)
        self.gbLive.setObjectName("gbLive")
        self.formLive = QFormLayout(self.gbLive)
        self.formLive.setObjectName("formLive")
        self.formLive.setVerticalSpacing(2)
        self.formLive.setContentsMargins(6, 4, 6, 4)
        self.lblLiveIntensityLabel = QLabel(self.gbLive)
        self.lblLiveIntensityLabel.setObjectName("lblLiveIntensityLabel")

        self.formLive.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lblLiveIntensityLabel)

        self.lblLiveIntensity = QLabel(self.gbLive)
        self.lblLiveIntensity.setObjectName("lblLiveIntensity")

        self.formLive.setWidget(0, QFormLayout.ItemRole.FieldRole, self.lblLiveIntensity)

        self.lblKDCPositionLabel = QLabel(self.gbLive)
        self.lblKDCPositionLabel.setObjectName("lblKDCPositionLabel")

        self.formLive.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lblKDCPositionLabel)

        self.lblKDCPosition = QLabel(self.gbLive)
        self.lblKDCPosition.setObjectName("lblKDCPosition")

        self.formLive.setWidget(1, QFormLayout.ItemRole.FieldRole, self.lblKDCPosition)

        self.rightLayout.addWidget(self.gbLive)

        self.gbSweep = QGroupBox(WaveplateTab)
        self.gbSweep.setObjectName("gbSweep")
        self.vboxSweep = QVBoxLayout(self.gbSweep)
        self.vboxSweep.setObjectName("vboxSweep")
        self.vboxSweep.setContentsMargins(6, 6, 6, 6)
        self.formWaveplateType = QFormLayout()
        self.formWaveplateType.setObjectName("formWaveplateType")
        self.lblWaveplateType = QLabel(self.gbSweep)
        self.lblWaveplateType.setObjectName("lblWaveplateType")

        self.formWaveplateType.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lblWaveplateType)

        self.cmbWaveplateType = QComboBox(self.gbSweep)
        self.cmbWaveplateType.addItem("")
        self.cmbWaveplateType.addItem("")
        self.cmbWaveplateType.setObjectName("cmbWaveplateType")

        self.formWaveplateType.setWidget(0, QFormLayout.ItemRole.FieldRole, self.cmbWaveplateType)

        self.vboxSweep.addLayout(self.formWaveplateType)

        self.cbWaveplatePlaced = QCheckBox(self.gbSweep)
        self.cbWaveplatePlaced.setObjectName("cbWaveplatePlaced")

        self.vboxSweep.addWidget(self.cbWaveplatePlaced)

        self.formSweepParams = QFormLayout()
        self.formSweepParams.setObjectName("formSweepParams")
        self.formSweepParams.setVerticalSpacing(3)
        self.lblSweepStart = QLabel(self.gbSweep)
        self.lblSweepStart.setObjectName("lblSweepStart")

        self.formSweepParams.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lblSweepStart)

        self.spinSweepStart = QDoubleSpinBox(self.gbSweep)
        self.spinSweepStart.setObjectName("spinSweepStart")
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
        self.spinSweepEnd.setDecimals(1)
        self.spinSweepEnd.setMinimum(0.000000000000000)
        self.spinSweepEnd.setMaximum(360.000000000000000)
        self.spinSweepEnd.setValue(360.000000000000000)

        self.formSweepParams.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spinSweepEnd)

        self.lblSweepStep = QLabel(self.gbSweep)
        self.lblSweepStep.setObjectName("lblSweepStep")

        self.formSweepParams.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lblSweepStep)

        self.spinSweepStep = QDoubleSpinBox(self.gbSweep)
        self.spinSweepStep.setObjectName("spinSweepStep")
        self.spinSweepStep.setDecimals(1)
        self.spinSweepStep.setMinimum(0.100000000000000)
        self.spinSweepStep.setMaximum(90.000000000000000)
        self.spinSweepStep.setSingleStep(0.500000000000000)
        self.spinSweepStep.setValue(10.000000000000000)

        self.formSweepParams.setWidget(2, QFormLayout.ItemRole.FieldRole, self.spinSweepStep)

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

        self.verticalSpacer = QSpacerItem(
            20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.rightLayout.addItem(self.verticalSpacer)

        self.btnDeleteSelected = QPushButton(WaveplateTab)
        self.btnDeleteSelected.setObjectName("btnDeleteSelected")
        self.btnDeleteSelected.setEnabled(False)

        self.rightLayout.addWidget(self.btnDeleteSelected)

        self.btnDeleteLast = QPushButton(WaveplateTab)
        self.btnDeleteLast.setObjectName("btnDeleteLast")
        self.btnDeleteLast.setEnabled(False)

        self.rightLayout.addWidget(self.btnDeleteLast)

        self.btnClear = QPushButton(WaveplateTab)
        self.btnClear.setObjectName("btnClear")
        self.btnClear.setEnabled(False)

        self.rightLayout.addWidget(self.btnClear)

        self.gridLayout.addLayout(self.rightLayout, 1, 1, 1, 1)

        self.intensityCurvePlot = MalusCurvePlot(WaveplateTab)
        self.intensityCurvePlot.setObjectName("intensityCurvePlot")

        self.gridLayout.addWidget(self.intensityCurvePlot, 0, 0, 1, 2)

        self.gridLayout.setRowStretch(0, 2)
        self.gridLayout.setRowStretch(1, 1)
        self.gridLayout.setColumnStretch(0, 2)

        self.retranslateUi(WaveplateTab)

        QMetaObject.connectSlotsByName(WaveplateTab)

    # setupUi

    def retranslateUi(self, WaveplateTab):
        ___qtablewidgetitem = self.pointsTable.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(
            QCoreApplication.translate("WaveplateTab", "\u03b8 (\u00b0)", None)
        )
        ___qtablewidgetitem1 = self.pointsTable.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("WaveplateTab", "I (V)", None))
        ___qtablewidgetitem2 = self.pointsTable.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(
            QCoreApplication.translate("WaveplateTab", "P (\u00b5W)", None)
        )
        ___qtablewidgetitem3 = self.pointsTable.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("WaveplateTab", "Gain", None))
        self.gbLive.setTitle(QCoreApplication.translate("WaveplateTab", "Aktuell", None))
        self.lblLiveIntensityLabel.setText(QCoreApplication.translate("WaveplateTab", "I:", None))
        self.lblLiveIntensity.setText(QCoreApplication.translate("WaveplateTab", "\u2014", None))
        self.lblKDCPositionLabel.setText(
            QCoreApplication.translate("WaveplateTab", "Position:", None)
        )
        self.lblKDCPosition.setText(QCoreApplication.translate("WaveplateTab", "\u2014", None))
        self.gbSweep.setTitle(QCoreApplication.translate("WaveplateTab", "Scan (KDC101)", None))
        self.lblWaveplateType.setText(QCoreApplication.translate("WaveplateTab", "Typ:", None))
        self.cmbWaveplateType.setItemText(
            0, QCoreApplication.translate("WaveplateTab", "\u03bb/4 (QWP)", None)
        )
        self.cmbWaveplateType.setItemText(
            1, QCoreApplication.translate("WaveplateTab", "\u03bb/2 (HWP)", None)
        )

        # if QT_CONFIG(tooltip)
        self.cmbWaveplateType.setToolTip(
            QCoreApplication.translate(
                "WaveplateTab",
                "Typ der eingesetzten Verz\u00f6gerungsplatte \u2014 bestimmt nur den Export-Dateinamen und die Metadaten, nicht den Scanablauf",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(tooltip)
        self.cbWaveplatePlaced.setToolTip(
            QCoreApplication.translate(
                "WaveplateTab",
                "Best\u00e4tigen, dass die Verz\u00f6gerungsplatte im Strahlengang eingesetzt ist",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.cbWaveplatePlaced.setText(
            QCoreApplication.translate("WaveplateTab", "Verz\u00f6gerungsplatte eingesetzt", None)
        )
        self.lblSweepStart.setText(
            QCoreApplication.translate("WaveplateTab", "Von (\u00b0):", None)
        )
        # if QT_CONFIG(tooltip)
        self.spinSweepStart.setToolTip(
            QCoreApplication.translate(
                "WaveplateTab",
                "Startwinkel des automatischen Scans, relativ zum Polarisator-Nullpunkt aus der Konfiguration (\u00b0)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.spinSweepStart.setSuffix(QCoreApplication.translate("WaveplateTab", " \u00b0", None))
        self.lblSweepEnd.setText(QCoreApplication.translate("WaveplateTab", "Bis (\u00b0):", None))
        # if QT_CONFIG(tooltip)
        self.spinSweepEnd.setToolTip(
            QCoreApplication.translate(
                "WaveplateTab",
                "Endwinkel des automatischen Scans, relativ zum Polarisator-Nullpunkt aus der Konfiguration (\u00b0)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.spinSweepEnd.setSuffix(QCoreApplication.translate("WaveplateTab", " \u00b0", None))
        self.lblSweepStep.setText(
            QCoreApplication.translate("WaveplateTab", "Schritt (\u00b0):", None)
        )
        # if QT_CONFIG(tooltip)
        self.spinSweepStep.setToolTip(
            QCoreApplication.translate(
                "WaveplateTab", "Schrittweite des automatischen Scans (\u00b0)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.spinSweepStep.setSuffix(QCoreApplication.translate("WaveplateTab", " \u00b0", None))
        # if QT_CONFIG(tooltip)
        self.btnStartSweep.setToolTip(
            QCoreApplication.translate(
                "WaveplateTab",
                "Automatischen Verz\u00f6gerungsplatten-Scan starten (referenziert auf den Polarisator-Nullpunkt aus der Konfiguration; erneutes Homing nur falls n\u00f6tig)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnStartSweep.setText(QCoreApplication.translate("WaveplateTab", "Scan starten", None))
        self.btnAbortSweep.setText(QCoreApplication.translate("WaveplateTab", "Abbrechen", None))
        # if QT_CONFIG(tooltip)
        self.btnDeleteSelected.setToolTip(
            QCoreApplication.translate(
                "WaveplateTab", "Markierten Punkt aus der Kurve l\u00f6schen", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnDeleteSelected.setText(
            QCoreApplication.translate("WaveplateTab", "Ausgew\u00e4hlten l\u00f6schen", None)
        )
        self.btnDeleteLast.setText(
            QCoreApplication.translate("WaveplateTab", "Letzten Punkt l\u00f6schen", None)
        )
        self.btnClear.setText(QCoreApplication.translate("WaveplateTab", "Alle l\u00f6schen", None))
        pass

    # retranslateUi
