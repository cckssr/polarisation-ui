# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'brewster_tab.ui'
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
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QRadioButton,
    QSizePolicy,
    QSpacerItem,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from polarisation_ui.ui.widgets.brewster_curve_plot import BrewsterCurvePlot
from polarisation_ui.ui.widgets.brewster_detector_plot import BrewsterDetectorPlot


class Ui_BrewsterTab(object):
    def setupUi(self, BrewsterTab):
        if not BrewsterTab.objectName():
            BrewsterTab.setObjectName("BrewsterTab")
        BrewsterTab.resize(959, 839)
        self.gridLayout = QGridLayout(BrewsterTab)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.detectorPlot = BrewsterDetectorPlot(BrewsterTab)
        self.detectorPlot.setObjectName("detectorPlot")

        self.gridLayout.addWidget(self.detectorPlot, 0, 0, 1, 2)

        self.brewsterCurvePlot = BrewsterCurvePlot(BrewsterTab)
        self.brewsterCurvePlot.setObjectName("brewsterCurvePlot")
        self.brewsterCurvePlot.setMinimumSize(QSize(0, 100))

        self.gridLayout.addWidget(self.brewsterCurvePlot, 1, 0, 1, 2)

        self.pointsTable = QTableWidget(BrewsterTab)
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
        self.pointsTable.setMinimumSize(QSize(0, 80))
        self.pointsTable.setMaximumSize(QSize(16777215, 400))
        self.pointsTable.setAutoScroll(True)
        self.pointsTable.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.pointsTable.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.pointsTable.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.pointsTable.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerItem)
        self.pointsTable.verticalHeader().setVisible(False)

        self.gridLayout.addWidget(self.pointsTable, 2, 0, 1, 1)

        self.rightLayout = QVBoxLayout()
        self.rightLayout.setSpacing(10)
        self.rightLayout.setObjectName("rightLayout")
        self.rightLayout.setContentsMargins(4, 0, 0, 0)
        self.btnClearDetector = QPushButton(BrewsterTab)
        self.btnClearDetector.setObjectName("btnClearDetector")
        self.btnClearDetector.setEnabled(False)

        self.rightLayout.addWidget(self.btnClearDetector)

        self.gbMax = QGroupBox(BrewsterTab)
        self.gbMax.setObjectName("gbMax")
        self.formMax = QFormLayout(self.gbMax)
        self.formMax.setObjectName("formMax")
        self.formMax.setVerticalSpacing(2)
        self.formMax.setContentsMargins(6, 4, 6, 4)
        self.lblMaxIntensityLabel = QLabel(self.gbMax)
        self.lblMaxIntensityLabel.setObjectName("lblMaxIntensityLabel")

        self.formMax.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lblMaxIntensityLabel)

        self.lblMaxIntensity = QLabel(self.gbMax)
        self.lblMaxIntensity.setObjectName("lblMaxIntensity")

        self.formMax.setWidget(0, QFormLayout.ItemRole.FieldRole, self.lblMaxIntensity)

        self.lblMaxAngleLabel = QLabel(self.gbMax)
        self.lblMaxAngleLabel.setObjectName("lblMaxAngleLabel")

        self.formMax.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lblMaxAngleLabel)

        self.lblMaxAngle = QLabel(self.gbMax)
        self.lblMaxAngle.setObjectName("lblMaxAngle")

        self.formMax.setWidget(1, QFormLayout.ItemRole.FieldRole, self.lblMaxAngle)

        self.rightLayout.addWidget(self.gbMax)

        self.verticalSpacer = QSpacerItem(
            20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.rightLayout.addItem(self.verticalSpacer)

        self.btnDeleteSelected = QPushButton(BrewsterTab)
        self.btnDeleteSelected.setObjectName("btnDeleteSelected")
        self.btnDeleteSelected.setEnabled(False)

        self.rightLayout.addWidget(self.btnDeleteSelected)

        self.btnDeleteLast = QPushButton(BrewsterTab)
        self.btnDeleteLast.setObjectName("btnDeleteLast")
        self.btnDeleteLast.setEnabled(False)

        self.rightLayout.addWidget(self.btnDeleteLast)

        self.line = QFrame(BrewsterTab)
        self.line.setObjectName("line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.rightLayout.addWidget(self.line)

        self.gbPolarisation = QGroupBox(BrewsterTab)
        self.gbPolarisation.setObjectName("gbPolarisation")
        self.hlPolarisation = QHBoxLayout(self.gbPolarisation)
        self.hlPolarisation.setObjectName("hlPolarisation")
        self.hlPolarisation.setContentsMargins(6, 4, 6, 4)
        self.rbPolP = QRadioButton(self.gbPolarisation)
        self.rbPolP.setObjectName("rbPolP")
        self.rbPolP.setChecked(True)

        self.hlPolarisation.addWidget(self.rbPolP)

        self.rbPolS = QRadioButton(self.gbPolarisation)
        self.rbPolS.setObjectName("rbPolS")

        self.hlPolarisation.addWidget(self.rbPolS)

        self.rightLayout.addWidget(self.gbPolarisation)

        self.btnSaveCurrent = QPushButton(BrewsterTab)
        self.btnSaveCurrent.setObjectName("btnSaveCurrent")
        self.btnSaveCurrent.setEnabled(False)

        self.rightLayout.addWidget(self.btnSaveCurrent)

        self.btnSaveMax = QPushButton(BrewsterTab)
        self.btnSaveMax.setObjectName("btnSaveMax")
        self.btnSaveMax.setEnabled(False)

        self.rightLayout.addWidget(self.btnSaveMax)

        self.gridLayout.addLayout(self.rightLayout, 2, 1, 1, 1)

        self.gridLayout.setRowStretch(0, 2)
        self.gridLayout.setRowStretch(1, 2)
        self.gridLayout.setRowStretch(2, 1)
        self.gridLayout.setColumnStretch(0, 1)

        self.retranslateUi(BrewsterTab)

        QMetaObject.connectSlotsByName(BrewsterTab)

    # setupUi

    def retranslateUi(self, BrewsterTab):
        ___qtablewidgetitem = self.pointsTable.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(
            QCoreApplication.translate("BrewsterTab", "\u03b8_S (\u00b0)", None)
        )
        ___qtablewidgetitem1 = self.pointsTable.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(
            QCoreApplication.translate("BrewsterTab", "\u03b8_D (\u00b0)", None)
        )
        ___qtablewidgetitem2 = self.pointsTable.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("BrewsterTab", "I (mV)", None))
        ___qtablewidgetitem3 = self.pointsTable.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("BrewsterTab", "P (\u00b5W)", None))
        ___qtablewidgetitem4 = self.pointsTable.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("BrewsterTab", "Gain", None))
        # if QT_CONFIG(tooltip)
        self.btnClearDetector.setToolTip(
            QCoreApplication.translate(
                "BrewsterTab",
                "L\u00f6scht alle Punkte im oberen Detektorwinkel-Intensit\u00e4ts-Graphen",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnClearDetector.setText(
            QCoreApplication.translate("BrewsterTab", "Detektorgraph l\u00f6schen", None)
        )
        self.gbMax.setTitle(QCoreApplication.translate("BrewsterTab", "Maximum", None))
        self.lblMaxIntensityLabel.setText(QCoreApplication.translate("BrewsterTab", "I:", None))
        self.lblMaxIntensity.setText(QCoreApplication.translate("BrewsterTab", "\u2014", None))
        self.lblMaxAngleLabel.setText(QCoreApplication.translate("BrewsterTab", "\u03b8:", None))
        self.lblMaxAngle.setText(QCoreApplication.translate("BrewsterTab", "\u2014", None))
        # if QT_CONFIG(tooltip)
        self.btnDeleteSelected.setToolTip(
            QCoreApplication.translate(
                "BrewsterTab", "Markierten Punkt aus der Kurve l\u00f6schen", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnDeleteSelected.setText(
            QCoreApplication.translate("BrewsterTab", "Ausgew\u00e4hlten l\u00f6schen", None)
        )
        # if QT_CONFIG(tooltip)
        self.btnDeleteLast.setToolTip(
            QCoreApplication.translate(
                "BrewsterTab", "Letzten gespeicherten Messpunkt entfernen", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnDeleteLast.setText(
            QCoreApplication.translate("BrewsterTab", "Letzten Punkt l\u00f6schen", None)
        )
        self.gbPolarisation.setTitle(
            QCoreApplication.translate("BrewsterTab", "Polarisation", None)
        )
        # if QT_CONFIG(tooltip)
        self.rbPolP.setToolTip(
            QCoreApplication.translate(
                "BrewsterTab",
                "p-Polarisation (transversal-magnetisch, parallel zur Einfallsebene)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.rbPolP.setText(QCoreApplication.translate("BrewsterTab", "p", None))
        # if QT_CONFIG(tooltip)
        self.rbPolS.setToolTip(
            QCoreApplication.translate(
                "BrewsterTab",
                "s-Polarisation (transversal-elektrisch, senkrecht zur Einfallsebene)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.rbPolS.setText(QCoreApplication.translate("BrewsterTab", "s", None))
        # if QT_CONFIG(tooltip)
        self.btnSaveCurrent.setToolTip(
            QCoreApplication.translate(
                "BrewsterTab",
                "Aktuellen Messwert (live) als Punkt in der Brewster-Kurve speichern",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnSaveCurrent.setText(
            QCoreApplication.translate("BrewsterTab", "Aktuell speichern", None)
        )
        # if QT_CONFIG(tooltip)
        self.btnSaveMax.setToolTip(
            QCoreApplication.translate(
                "BrewsterTab",
                "Maximum des Detektorscans als Punkt speichern und Scan zur\u00fccksetzen",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnSaveMax.setText(
            QCoreApplication.translate("BrewsterTab", "Maximum speichern", None)
        )
        pass

    # retranslateUi
