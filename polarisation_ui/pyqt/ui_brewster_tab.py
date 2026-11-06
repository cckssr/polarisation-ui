# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'brewster_tab.ui'
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
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QSplitter,
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
        self.layoutMain = QGridLayout(BrewsterTab)
        self.layoutMain.setObjectName("layoutMain")
        self.layoutMain.setContentsMargins(0, 10, 0, 0)
        self.tablePoints = QTableWidget(BrewsterTab)
        if self.tablePoints.columnCount() < 5:
            self.tablePoints.setColumnCount(5)
        self.tablePoints.setObjectName("tablePoints")
        self.tablePoints.setMinimumSize(QSize(0, 80))
        self.tablePoints.setMaximumSize(QSize(16777215, 400))
        self.tablePoints.setAutoScroll(True)
        self.tablePoints.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tablePoints.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tablePoints.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tablePoints.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerItem)
        self.tablePoints.verticalHeader().setVisible(False)

        self.layoutMain.addWidget(self.tablePoints, 1, 0, 1, 1)

        self.scrollSide = QScrollArea(BrewsterTab)
        self.scrollSide.setObjectName("scrollSide")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollSide.sizePolicy().hasHeightForWidth())
        self.scrollSide.setSizePolicy(sizePolicy)
        self.scrollSide.setFrameShape(QFrame.Shape.NoFrame)
        self.scrollSide.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollSide.setWidgetResizable(True)
        self.contentSide = QWidget()
        self.contentSide.setObjectName("contentSide")
        self.layoutSide = QVBoxLayout(self.contentSide)
        self.layoutSide.setSpacing(10)
        self.layoutSide.setObjectName("layoutSide")
        self.layoutSide.setContentsMargins(4, 0, 0, 0)
        self.buttonClearDetector = QPushButton(self.contentSide)
        self.buttonClearDetector.setObjectName("buttonClearDetector")
        self.buttonClearDetector.setEnabled(False)

        self.layoutSide.addWidget(self.buttonClearDetector)

        self.groupMax = QGroupBox(self.contentSide)
        self.groupMax.setObjectName("groupMax")
        self.layoutMax = QFormLayout(self.groupMax)
        self.layoutMax.setObjectName("layoutMax")
        self.layoutMax.setVerticalSpacing(2)
        self.layoutMax.setContentsMargins(6, 4, 6, 4)
        self.labelMaxIntensity = QLabel(self.groupMax)
        self.labelMaxIntensity.setObjectName("labelMaxIntensity")

        self.layoutMax.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelMaxIntensity)

        self.valueMaxIntensity = QLabel(self.groupMax)
        self.valueMaxIntensity.setObjectName("valueMaxIntensity")

        self.layoutMax.setWidget(0, QFormLayout.ItemRole.FieldRole, self.valueMaxIntensity)

        self.labelMaxAngle = QLabel(self.groupMax)
        self.labelMaxAngle.setObjectName("labelMaxAngle")

        self.layoutMax.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelMaxAngle)

        self.valueMaxAngle = QLabel(self.groupMax)
        self.valueMaxAngle.setObjectName("valueMaxAngle")

        self.layoutMax.setWidget(1, QFormLayout.ItemRole.FieldRole, self.valueMaxAngle)

        self.layoutSide.addWidget(self.groupMax)

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

        self.lineSeparator = QFrame(self.contentSide)
        self.lineSeparator.setObjectName("lineSeparator")
        self.lineSeparator.setFrameShape(QFrame.Shape.HLine)
        self.lineSeparator.setFrameShadow(QFrame.Shadow.Sunken)

        self.layoutSide.addWidget(self.lineSeparator)

        self.groupPolarisation = QGroupBox(self.contentSide)
        self.groupPolarisation.setObjectName("groupPolarisation")
        self.layoutPolarisation = QHBoxLayout(self.groupPolarisation)
        self.layoutPolarisation.setObjectName("layoutPolarisation")
        self.layoutPolarisation.setContentsMargins(6, 4, 6, 4)
        self.radioPolP = QRadioButton(self.groupPolarisation)
        self.radioPolP.setObjectName("radioPolP")
        self.radioPolP.setChecked(True)

        self.layoutPolarisation.addWidget(self.radioPolP)

        self.radioPolS = QRadioButton(self.groupPolarisation)
        self.radioPolS.setObjectName("radioPolS")

        self.layoutPolarisation.addWidget(self.radioPolS)

        self.layoutSide.addWidget(self.groupPolarisation)

        self.buttonSaveCurrent = QPushButton(self.contentSide)
        self.buttonSaveCurrent.setObjectName("buttonSaveCurrent")
        self.buttonSaveCurrent.setEnabled(False)

        self.layoutSide.addWidget(self.buttonSaveCurrent)

        self.buttonSaveMax = QPushButton(self.contentSide)
        self.buttonSaveMax.setObjectName("buttonSaveMax")
        self.buttonSaveMax.setEnabled(False)

        self.layoutSide.addWidget(self.buttonSaveMax)

        self.scrollSide.setWidget(self.contentSide)

        self.layoutMain.addWidget(self.scrollSide, 0, 1, 2, 1)

        self.splitterPlots = QSplitter(BrewsterTab)
        self.splitterPlots.setObjectName("splitterPlots")
        self.splitterPlots.setOrientation(Qt.Orientation.Vertical)
        self.detectorPlot = BrewsterDetectorPlot(self.splitterPlots)
        self.detectorPlot.setObjectName("detectorPlot")
        self.splitterPlots.addWidget(self.detectorPlot)
        self.brewsterCurvePlot = BrewsterCurvePlot(self.splitterPlots)
        self.brewsterCurvePlot.setObjectName("brewsterCurvePlot")
        self.brewsterCurvePlot.setMinimumSize(QSize(0, 100))
        self.splitterPlots.addWidget(self.brewsterCurvePlot)

        self.layoutMain.addWidget(self.splitterPlots, 0, 0, 1, 1)

        self.layoutMain.setRowStretch(0, 1)
        self.layoutMain.setColumnStretch(0, 1)

        self.retranslateUi(BrewsterTab)

        QMetaObject.connectSlotsByName(BrewsterTab)

    # setupUi

    def retranslateUi(self, BrewsterTab):
        # if QT_CONFIG(tooltip)
        self.buttonClearDetector.setToolTip(
            QCoreApplication.translate(
                "BrewsterTab",
                "L\u00f6scht alle Punkte im oberen Detektorwinkel-Intensit\u00e4ts-Graphen",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonClearDetector.setText(
            QCoreApplication.translate("BrewsterTab", "Detektorgraph l\u00f6schen", None)
        )
        self.groupMax.setTitle(QCoreApplication.translate("BrewsterTab", "Maximum", None))
        self.labelMaxIntensity.setText(QCoreApplication.translate("BrewsterTab", "I:", None))
        self.valueMaxIntensity.setText(QCoreApplication.translate("BrewsterTab", "\u2014", None))
        self.labelMaxAngle.setText(QCoreApplication.translate("BrewsterTab", "\u03b8:", None))
        self.valueMaxAngle.setText(QCoreApplication.translate("BrewsterTab", "\u2014", None))
        # if QT_CONFIG(tooltip)
        self.buttonDeleteSelected.setToolTip(
            QCoreApplication.translate(
                "BrewsterTab", "Markierten Punkt aus der Kurve l\u00f6schen", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonDeleteSelected.setText(
            QCoreApplication.translate("BrewsterTab", "Ausgew\u00e4hlten l\u00f6schen", None)
        )
        # if QT_CONFIG(tooltip)
        self.buttonDeleteLast.setToolTip(
            QCoreApplication.translate(
                "BrewsterTab", "Letzten gespeicherten Messpunkt entfernen", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonDeleteLast.setText(
            QCoreApplication.translate("BrewsterTab", "Letzten Punkt l\u00f6schen", None)
        )
        self.groupPolarisation.setTitle(
            QCoreApplication.translate("BrewsterTab", "Polarisation", None)
        )
        # if QT_CONFIG(tooltip)
        self.radioPolP.setToolTip(
            QCoreApplication.translate(
                "BrewsterTab",
                "p-Polarisation (transversal-magnetisch, parallel zur Einfallsebene)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.radioPolP.setText(QCoreApplication.translate("BrewsterTab", "p", None))
        # if QT_CONFIG(tooltip)
        self.radioPolS.setToolTip(
            QCoreApplication.translate(
                "BrewsterTab",
                "s-Polarisation (transversal-elektrisch, senkrecht zur Einfallsebene)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.radioPolS.setText(QCoreApplication.translate("BrewsterTab", "s", None))
        # if QT_CONFIG(tooltip)
        self.buttonSaveCurrent.setToolTip(
            QCoreApplication.translate(
                "BrewsterTab",
                "Aktuellen Messwert (live) als Punkt in der Brewster-Kurve speichern",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonSaveCurrent.setText(
            QCoreApplication.translate("BrewsterTab", "Aktuell speichern", None)
        )
        # if QT_CONFIG(tooltip)
        self.buttonSaveMax.setToolTip(
            QCoreApplication.translate(
                "BrewsterTab",
                "Maximum des Detektorscans als Punkt speichern und Scan zur\u00fccksetzen",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonSaveMax.setText(
            QCoreApplication.translate("BrewsterTab", "Maximum speichern", None)
        )
        pass

    # retranslateUi
