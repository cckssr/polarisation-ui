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
    QFrame,
    QGridLayout,
    QGroupBox,
    QHeaderView,
    QLabel,
    QPushButton,
    QScrollArea,
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
        WaveplateTab.resize(1088, 788)
        self.gridLayout = QGridLayout(WaveplateTab)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setContentsMargins(0, 10, 0, 0)
        self.tablePoints = QTableWidget(WaveplateTab)
        if self.tablePoints.columnCount() < 4:
            self.tablePoints.setColumnCount(4)
        __qtablewidgetitem = QTableWidgetItem()
        self.tablePoints.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tablePoints.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tablePoints.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tablePoints.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        self.tablePoints.setObjectName("tablePoints")
        self.tablePoints.setMinimumSize(QSize(0, 120))
        self.tablePoints.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tablePoints.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tablePoints.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tablePoints.verticalHeader().setVisible(False)

        self.gridLayout.addWidget(self.tablePoints, 1, 0, 1, 1)

        self.scrollSide = QScrollArea(WaveplateTab)
        self.scrollSide.setObjectName("scrollSide")
        self.scrollSide.setFrameShape(QFrame.Shape.NoFrame)
        self.scrollSide.setWidgetResizable(True)
        self.contentSide = QWidget()
        self.contentSide.setObjectName("contentSide")
        self.contentSide.setGeometry(QRect(0, 0, 223, 778))
        self.layoutSide = QVBoxLayout(self.contentSide)
        self.layoutSide.setSpacing(6)
        self.layoutSide.setObjectName("layoutSide")
        self.layoutSide.setContentsMargins(4, 0, 0, 0)
        self.groupLive = QGroupBox(self.contentSide)
        self.groupLive.setObjectName("groupLive")
        self.formLive = QFormLayout(self.groupLive)
        self.formLive.setObjectName("formLive")
        self.formLive.setVerticalSpacing(2)
        self.formLive.setContentsMargins(6, 4, 6, 4)
        self.labelLiveIntensity = QLabel(self.groupLive)
        self.labelLiveIntensity.setObjectName("labelLiveIntensity")

        self.formLive.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelLiveIntensity)

        self.valueLiveIntensity = QLabel(self.groupLive)
        self.valueLiveIntensity.setObjectName("valueLiveIntensity")

        self.formLive.setWidget(0, QFormLayout.ItemRole.FieldRole, self.valueLiveIntensity)

        self.labelKdcPosition = QLabel(self.groupLive)
        self.labelKdcPosition.setObjectName("labelKdcPosition")

        self.formLive.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelKdcPosition)

        self.valueKdcPosition = QLabel(self.groupLive)
        self.valueKdcPosition.setObjectName("valueKdcPosition")

        self.formLive.setWidget(1, QFormLayout.ItemRole.FieldRole, self.valueKdcPosition)

        self.layoutSide.addWidget(self.groupLive)

        self.groupSweep = QGroupBox(self.contentSide)
        self.groupSweep.setObjectName("groupSweep")
        self.vboxSweep = QVBoxLayout(self.groupSweep)
        self.vboxSweep.setObjectName("vboxSweep")
        self.vboxSweep.setContentsMargins(6, 6, 6, 6)
        self.formWaveplateType = QFormLayout()
        self.formWaveplateType.setObjectName("formWaveplateType")
        self.labelWaveplateType = QLabel(self.groupSweep)
        self.labelWaveplateType.setObjectName("labelWaveplateType")

        self.formWaveplateType.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelWaveplateType)

        self.comboWaveplateType = QComboBox(self.groupSweep)
        self.comboWaveplateType.addItem("")
        self.comboWaveplateType.addItem("")
        self.comboWaveplateType.setObjectName("comboWaveplateType")

        self.formWaveplateType.setWidget(0, QFormLayout.ItemRole.FieldRole, self.comboWaveplateType)

        self.vboxSweep.addLayout(self.formWaveplateType)

        self.checkWaveplatePlaced = QCheckBox(self.groupSweep)
        self.checkWaveplatePlaced.setObjectName("checkWaveplatePlaced")

        self.vboxSweep.addWidget(self.checkWaveplatePlaced)

        self.formSweepParams = QFormLayout()
        self.formSweepParams.setObjectName("formSweepParams")
        self.formSweepParams.setVerticalSpacing(3)
        self.labelSweepStart = QLabel(self.groupSweep)
        self.labelSweepStart.setObjectName("labelSweepStart")

        self.formSweepParams.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelSweepStart)

        self.spinSweepStart = QDoubleSpinBox(self.groupSweep)
        self.spinSweepStart.setObjectName("spinSweepStart")
        self.spinSweepStart.setDecimals(1)
        self.spinSweepStart.setMinimum(0.000000000000000)
        self.spinSweepStart.setMaximum(360.000000000000000)
        self.spinSweepStart.setValue(0.000000000000000)

        self.formSweepParams.setWidget(0, QFormLayout.ItemRole.FieldRole, self.spinSweepStart)

        self.labelSweepEnd = QLabel(self.groupSweep)
        self.labelSweepEnd.setObjectName("labelSweepEnd")

        self.formSweepParams.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelSweepEnd)

        self.spinSweepEnd = QDoubleSpinBox(self.groupSweep)
        self.spinSweepEnd.setObjectName("spinSweepEnd")
        self.spinSweepEnd.setDecimals(1)
        self.spinSweepEnd.setMinimum(0.000000000000000)
        self.spinSweepEnd.setMaximum(360.000000000000000)
        self.spinSweepEnd.setValue(360.000000000000000)

        self.formSweepParams.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spinSweepEnd)

        self.labelSweepStep = QLabel(self.groupSweep)
        self.labelSweepStep.setObjectName("labelSweepStep")

        self.formSweepParams.setWidget(2, QFormLayout.ItemRole.LabelRole, self.labelSweepStep)

        self.spinSweepStep = QDoubleSpinBox(self.groupSweep)
        self.spinSweepStep.setObjectName("spinSweepStep")
        self.spinSweepStep.setDecimals(1)
        self.spinSweepStep.setMinimum(0.100000000000000)
        self.spinSweepStep.setMaximum(90.000000000000000)
        self.spinSweepStep.setSingleStep(0.500000000000000)
        self.spinSweepStep.setValue(10.000000000000000)

        self.formSweepParams.setWidget(2, QFormLayout.ItemRole.FieldRole, self.spinSweepStep)

        self.vboxSweep.addLayout(self.formSweepParams)

        self.buttonStartSweep = QPushButton(self.groupSweep)
        self.buttonStartSweep.setObjectName("buttonStartSweep")
        self.buttonStartSweep.setEnabled(False)

        self.vboxSweep.addWidget(self.buttonStartSweep)

        self.buttonAbortSweep = QPushButton(self.groupSweep)
        self.buttonAbortSweep.setObjectName("buttonAbortSweep")
        self.buttonAbortSweep.setEnabled(False)

        self.vboxSweep.addWidget(self.buttonAbortSweep)

        self.layoutSide.addWidget(self.groupSweep)

        self.verticalSpacer = QSpacerItem(
            20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.layoutSide.addItem(self.verticalSpacer)

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

        self.gridLayout.addWidget(self.scrollSide, 0, 1, 2, 1)

        self.intensityCurvePlot = MalusCurvePlot(WaveplateTab)
        self.intensityCurvePlot.setObjectName("intensityCurvePlot")

        self.gridLayout.addWidget(self.intensityCurvePlot, 0, 0, 1, 1)

        self.gridLayout.setRowStretch(0, 2)
        self.gridLayout.setRowStretch(1, 1)
        self.gridLayout.setColumnStretch(0, 2)

        self.retranslateUi(WaveplateTab)

        QMetaObject.connectSlotsByName(WaveplateTab)

    # setupUi

    def retranslateUi(self, WaveplateTab):
        ___qtablewidgetitem = self.tablePoints.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(
            QCoreApplication.translate("WaveplateTab", "\u03b8 (\u00b0)", None)
        )
        ___qtablewidgetitem1 = self.tablePoints.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("WaveplateTab", "I (V)", None))
        ___qtablewidgetitem2 = self.tablePoints.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(
            QCoreApplication.translate("WaveplateTab", "P (\u00b5W)", None)
        )
        ___qtablewidgetitem3 = self.tablePoints.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("WaveplateTab", "Gain", None))
        self.groupLive.setTitle(QCoreApplication.translate("WaveplateTab", "Aktuell", None))
        self.labelLiveIntensity.setText(QCoreApplication.translate("WaveplateTab", "I:", None))
        self.valueLiveIntensity.setText(QCoreApplication.translate("WaveplateTab", "\u2014", None))
        self.labelKdcPosition.setText(QCoreApplication.translate("WaveplateTab", "Position:", None))
        self.valueKdcPosition.setText(QCoreApplication.translate("WaveplateTab", "\u2014", None))
        self.groupSweep.setTitle(QCoreApplication.translate("WaveplateTab", "Scan (KDC101)", None))
        self.labelWaveplateType.setText(QCoreApplication.translate("WaveplateTab", "Typ:", None))
        self.comboWaveplateType.setItemText(
            0, QCoreApplication.translate("WaveplateTab", "\u03bb/4 (QWP)", None)
        )
        self.comboWaveplateType.setItemText(
            1, QCoreApplication.translate("WaveplateTab", "\u03bb/2 (HWP)", None)
        )

        # if QT_CONFIG(tooltip)
        self.comboWaveplateType.setToolTip(
            QCoreApplication.translate(
                "WaveplateTab",
                "Typ der eingesetzten Verz\u00f6gerungsplatte \u2014 bestimmt nur den Export-Dateinamen und die Metadaten, nicht den Scanablauf",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(tooltip)
        self.checkWaveplatePlaced.setToolTip(
            QCoreApplication.translate(
                "WaveplateTab",
                "Best\u00e4tigen, dass die Verz\u00f6gerungsplatte im Strahlengang eingesetzt ist",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.checkWaveplatePlaced.setText(
            QCoreApplication.translate("WaveplateTab", "Verz\u00f6gerungsplatte eingesetzt", None)
        )
        self.labelSweepStart.setText(
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
        self.labelSweepEnd.setText(
            QCoreApplication.translate("WaveplateTab", "Bis (\u00b0):", None)
        )
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
        self.labelSweepStep.setText(
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
        self.buttonStartSweep.setToolTip(
            QCoreApplication.translate(
                "WaveplateTab",
                "Automatischen Verz\u00f6gerungsplatten-Scan starten (referenziert auf den Polarisator-Nullpunkt aus der Konfiguration; erneutes Homing nur falls n\u00f6tig)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonStartSweep.setText(
            QCoreApplication.translate("WaveplateTab", "Scan starten", None)
        )
        self.buttonAbortSweep.setText(QCoreApplication.translate("WaveplateTab", "Abbrechen", None))
        # if QT_CONFIG(tooltip)
        self.buttonDeleteSelected.setToolTip(
            QCoreApplication.translate(
                "WaveplateTab", "Markierten Punkt aus der Kurve l\u00f6schen", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonDeleteSelected.setText(
            QCoreApplication.translate("WaveplateTab", "Ausgew\u00e4hlten l\u00f6schen", None)
        )
        self.buttonDeleteLast.setText(
            QCoreApplication.translate("WaveplateTab", "Letzten Punkt l\u00f6schen", None)
        )
        self.buttonClear.setText(
            QCoreApplication.translate("WaveplateTab", "Alle l\u00f6schen", None)
        )
        pass

    # retranslateUi
