# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'malus_tab.ui'
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
    QAbstractItemView,
    QApplication,
    QCheckBox,
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
    QSplitter,
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
        self.gridLayout.setContentsMargins(0, 10, 0, 0)
        self.splitter = QSplitter(MalusTab)
        self.splitter.setObjectName("splitter")
        self.splitter.setOrientation(Qt.Orientation.Vertical)
        self.malusCurvePlot = MalusCurvePlot(self.splitter)
        self.malusCurvePlot.setObjectName("malusCurvePlot")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(3)
        sizePolicy.setHeightForWidth(self.malusCurvePlot.sizePolicy().hasHeightForWidth())
        self.malusCurvePlot.setSizePolicy(sizePolicy)
        self.splitter.addWidget(self.malusCurvePlot)
        self.tablePoints = QTableWidget(self.splitter)
        if self.tablePoints.columnCount() < 5:
            self.tablePoints.setColumnCount(5)
        __qtablewidgetitem = QTableWidgetItem()
        self.tablePoints.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tablePoints.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tablePoints.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tablePoints.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tablePoints.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        self.tablePoints.setObjectName("tablePoints")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(1)
        sizePolicy1.setHeightForWidth(self.tablePoints.sizePolicy().hasHeightForWidth())
        self.tablePoints.setSizePolicy(sizePolicy1)
        self.tablePoints.setMinimumSize(QSize(0, 120))
        self.tablePoints.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tablePoints.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tablePoints.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.splitter.addWidget(self.tablePoints)
        self.tablePoints.verticalHeader().setVisible(False)

        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)

        self.scrollSide = QScrollArea(MalusTab)
        self.scrollSide.setObjectName("scrollSide")
        self.scrollSide.setFrameShape(QFrame.Shape.NoFrame)
        self.scrollSide.setWidgetResizable(True)
        self.contentSide = QWidget()
        self.contentSide.setObjectName("contentSide")
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

        self.formLive.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelLiveIntensity)

        self.valueLiveIntensity = QLabel(self.groupLive)
        self.valueLiveIntensity.setObjectName("valueLiveIntensity")

        self.formLive.setWidget(1, QFormLayout.ItemRole.FieldRole, self.valueLiveIntensity)

        self.labelLivePower = QLabel(self.groupLive)
        self.labelLivePower.setObjectName("labelLivePower")

        self.formLive.setWidget(3, QFormLayout.ItemRole.LabelRole, self.labelLivePower)

        self.valueLivePower = QLabel(self.groupLive)
        self.valueLivePower.setObjectName("valueLivePower")

        self.formLive.setWidget(3, QFormLayout.ItemRole.FieldRole, self.valueLivePower)

        self.labelLiveVoltage = QLabel(self.groupLive)
        self.labelLiveVoltage.setObjectName("labelLiveVoltage")

        self.formLive.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelLiveVoltage)

        self.valueLiveVoltage = QLabel(self.groupLive)
        self.valueLiveVoltage.setObjectName("valueLiveVoltage")

        self.formLive.setWidget(0, QFormLayout.ItemRole.FieldRole, self.valueLiveVoltage)

        self.layoutSide.addWidget(self.groupLive)

        self.groupEntry = QGroupBox(self.contentSide)
        self.groupEntry.setObjectName("groupEntry")
        self.formEntry = QFormLayout(self.groupEntry)
        self.formEntry.setObjectName("formEntry")
        self.formEntry.setVerticalSpacing(4)
        self.formEntry.setContentsMargins(6, 6, 6, 6)
        self.labelPolariser = QLabel(self.groupEntry)
        self.labelPolariser.setObjectName("labelPolariser")

        self.formEntry.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelPolariser)

        self.spinPolariser = QDoubleSpinBox(self.groupEntry)
        self.spinPolariser.setObjectName("spinPolariser")
        self.spinPolariser.setDecimals(2)
        self.spinPolariser.setMinimum(-360.000000000000000)
        self.spinPolariser.setMaximum(360.000000000000000)
        self.spinPolariser.setSingleStep(1.000000000000000)
        self.spinPolariser.setValue(0.000000000000000)

        self.formEntry.setWidget(0, QFormLayout.ItemRole.FieldRole, self.spinPolariser)

        self.labelAnalyser = QLabel(self.groupEntry)
        self.labelAnalyser.setObjectName("labelAnalyser")

        self.formEntry.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelAnalyser)

        self.spinAnalyser = QDoubleSpinBox(self.groupEntry)
        self.spinAnalyser.setObjectName("spinAnalyser")
        self.spinAnalyser.setEnabled(False)
        self.spinAnalyser.setDecimals(2)
        self.spinAnalyser.setMinimum(-360.000000000000000)
        self.spinAnalyser.setMaximum(360.000000000000000)
        self.spinAnalyser.setSingleStep(1.000000000000000)
        self.spinAnalyser.setValue(0.000000000000000)

        self.formEntry.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spinAnalyser)

        self.buttonAdd = QPushButton(self.groupEntry)
        self.buttonAdd.setObjectName("buttonAdd")
        self.buttonAdd.setEnabled(False)

        self.formEntry.setWidget(2, QFormLayout.ItemRole.SpanningRole, self.buttonAdd)

        self.layoutSide.addWidget(self.groupEntry)

        self.groupSweep = QGroupBox(self.contentSide)
        self.groupSweep.setObjectName("groupSweep")
        self.groupSweep.setEnabled(False)
        self.vboxSweep = QVBoxLayout(self.groupSweep)
        self.vboxSweep.setObjectName("vboxSweep")
        self.vboxSweep.setContentsMargins(6, 6, 6, 6)
        self.checkPolariserPlaced = QCheckBox(self.groupSweep)
        self.checkPolariserPlaced.setObjectName("checkPolariserPlaced")

        self.vboxSweep.addWidget(self.checkPolariserPlaced)

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
        self.spinSweepEnd.setValue(180.000000000000000)

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
        self.spinSweepStep.setValue(5.000000000000000)

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

        self.gridLayout.addWidget(self.scrollSide, 0, 1, 1, 1)

        self.gridLayout.setColumnStretch(0, 1)

        self.retranslateUi(MalusTab)

        QMetaObject.connectSlotsByName(MalusTab)

    # setupUi

    def retranslateUi(self, MalusTab):
        ___qtablewidgetitem = self.tablePoints.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(
            QCoreApplication.translate("MalusTab", "\u03b8_A (\u00b0)", None)
        )
        ___qtablewidgetitem1 = self.tablePoints.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(
            QCoreApplication.translate("MalusTab", "\u03b8_P (\u00b0)", None)
        )
        ___qtablewidgetitem2 = self.tablePoints.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MalusTab", "I (mV)", None))
        ___qtablewidgetitem3 = self.tablePoints.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("MalusTab", "P (\u00b5W)", None))
        ___qtablewidgetitem4 = self.tablePoints.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("MalusTab", "Gain", None))
        self.groupLive.setTitle(QCoreApplication.translate("MalusTab", "Aktuell", None))
        self.labelLiveIntensity.setText(QCoreApplication.translate("MalusTab", "I:", None))
        self.valueLiveIntensity.setText(QCoreApplication.translate("MalusTab", "\u2014", None))
        self.labelLivePower.setText(QCoreApplication.translate("MalusTab", "P:", None))
        self.valueLivePower.setText(QCoreApplication.translate("MalusTab", "\u2014", None))
        self.labelLiveVoltage.setText(QCoreApplication.translate("MalusTab", "U:", None))
        self.valueLiveVoltage.setText(QCoreApplication.translate("MalusTab", "\u2014", None))
        self.groupEntry.setTitle(QCoreApplication.translate("MalusTab", "Messpunkt", None))
        self.labelPolariser.setText(
            QCoreApplication.translate("MalusTab", "Polarisator \u03b8_P:", None)
        )
        # if QT_CONFIG(tooltip)
        self.spinPolariser.setToolTip(
            QCoreApplication.translate(
                "MalusTab", "Polarisatorwinkel (fest f\u00fcr die gesamte Messreihe)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.spinPolariser.setSuffix(QCoreApplication.translate("MalusTab", " \u00b0", None))
        self.labelAnalyser.setText(
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
        self.buttonAdd.setToolTip(
            QCoreApplication.translate(
                "MalusTab",
                "Aktuellen Analysatorwinkel mit gemittelter Intensit\u00e4t speichern",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonAdd.setText(
            QCoreApplication.translate("MalusTab", "Punkt hinzuf\u00fcgen", None)
        )
        self.groupSweep.setTitle(
            QCoreApplication.translate("MalusTab", "Automatischer Scan (KDC101)", None)
        )
        # if QT_CONFIG(tooltip)
        self.checkPolariserPlaced.setToolTip(
            QCoreApplication.translate(
                "MalusTab",
                "Best\u00e4tigen, dass der Polarisator im Strahlengang eingesetzt ist",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.checkPolariserPlaced.setText(
            QCoreApplication.translate("MalusTab", "Polarisator eingesetzt", None)
        )
        self.labelSweepStart.setText(QCoreApplication.translate("MalusTab", "Von (\u00b0):", None))
        # if QT_CONFIG(tooltip)
        self.spinSweepStart.setToolTip(
            QCoreApplication.translate(
                "MalusTab",
                "Startwinkel des automatischen Scans, relativ zum Polarisator-Nullpunkt aus der Konfiguration (\u00b0)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.spinSweepStart.setSuffix(QCoreApplication.translate("MalusTab", " \u00b0", None))
        self.labelSweepEnd.setText(QCoreApplication.translate("MalusTab", "Bis (\u00b0):", None))
        # if QT_CONFIG(tooltip)
        self.spinSweepEnd.setToolTip(
            QCoreApplication.translate(
                "MalusTab",
                "Endwinkel des automatischen Scans, relativ zum Polarisator-Nullpunkt aus der Konfiguration (\u00b0)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.spinSweepEnd.setSuffix(QCoreApplication.translate("MalusTab", " \u00b0", None))
        self.labelSweepStep.setText(
            QCoreApplication.translate("MalusTab", "Schritt (\u00b0):", None)
        )
        # if QT_CONFIG(tooltip)
        self.spinSweepStep.setToolTip(
            QCoreApplication.translate(
                "MalusTab", "Schrittweite des automatischen Scans (\u00b0)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.spinSweepStep.setSuffix(QCoreApplication.translate("MalusTab", " \u00b0", None))
        # if QT_CONFIG(tooltip)
        self.buttonStartSweep.setToolTip(
            QCoreApplication.translate(
                "MalusTab",
                "Automatischen Analysatorwinkel-Scan starten (referenziert auf den Polarisator-Nullpunkt aus der Konfiguration; erneutes Homing nur falls n\u00f6tig)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonStartSweep.setText(QCoreApplication.translate("MalusTab", "Scan starten", None))
        # if QT_CONFIG(tooltip)
        self.buttonAbortSweep.setToolTip(
            QCoreApplication.translate(
                "MalusTab", "Laufenden automatischen Scan sofort abbrechen", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonAbortSweep.setText(QCoreApplication.translate("MalusTab", "Abbrechen", None))
        # if QT_CONFIG(tooltip)
        self.buttonDeleteSelected.setToolTip(
            QCoreApplication.translate(
                "MalusTab", "Markierten Punkt aus der Kurve l\u00f6schen", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonDeleteSelected.setText(
            QCoreApplication.translate("MalusTab", "Ausgew\u00e4hlten l\u00f6schen", None)
        )
        # if QT_CONFIG(tooltip)
        self.buttonDeleteLast.setToolTip(
            QCoreApplication.translate(
                "MalusTab", "Letzten gespeicherten Messpunkt entfernen", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonDeleteLast.setText(
            QCoreApplication.translate("MalusTab", "Letzten Punkt l\u00f6schen", None)
        )
        # if QT_CONFIG(tooltip)
        self.buttonClear.setToolTip(
            QCoreApplication.translate(
                "MalusTab", "Alle gespeicherten Messpunkte l\u00f6schen", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonClear.setText(QCoreApplication.translate("MalusTab", "Alle l\u00f6schen", None))
        pass

    # retranslateUi
