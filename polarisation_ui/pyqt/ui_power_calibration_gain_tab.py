# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'power_calibration_gain_tab.ui'
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
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from pyqtgraph import PlotWidget


class Ui_PowerCalibrationGainTab(object):
    def setupUi(self, PowerCalibrationGainTab):
        if not PowerCalibrationGainTab.objectName():
            PowerCalibrationGainTab.setObjectName("PowerCalibrationGainTab")
        PowerCalibrationGainTab.resize(520, 520)
        self.layoutMain = QVBoxLayout(PowerCalibrationGainTab)
        self.layoutMain.setSpacing(6)
        self.layoutMain.setObjectName("layoutMain")
        self.layoutMain.setContentsMargins(6, 6, 6, 6)
        self.groupEntry = QGroupBox(PowerCalibrationGainTab)
        self.groupEntry.setObjectName("groupEntry")
        self.layoutEntry = QFormLayout(self.groupEntry)
        self.layoutEntry.setObjectName("layoutEntry")
        self.layoutEntry.setVerticalSpacing(4)
        self.layoutEntry.setContentsMargins(8, 6, 8, 6)
        self.labelVoltage = QLabel(self.groupEntry)
        self.labelVoltage.setObjectName("labelVoltage")

        self.layoutEntry.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelVoltage)

        self.layoutVoltage = QHBoxLayout()
        self.layoutVoltage.setObjectName("layoutVoltage")
        self.spinVoltage = QDoubleSpinBox(self.groupEntry)
        self.spinVoltage.setObjectName("spinVoltage")
        self.spinVoltage.setDecimals(6)
        self.spinVoltage.setMaximum(10.000000000000000)
        self.spinVoltage.setSingleStep(0.001000000000000)

        self.layoutVoltage.addWidget(self.spinVoltage)

        self.buttonLive = QPushButton(self.groupEntry)
        self.buttonLive.setObjectName("buttonLive")
        self.buttonLive.setEnabled(False)
        self.buttonLive.setMaximumSize(QSize(55, 16777215))

        self.layoutVoltage.addWidget(self.buttonLive)

        self.layoutEntry.setLayout(0, QFormLayout.ItemRole.FieldRole, self.layoutVoltage)

        self.labelPower = QLabel(self.groupEntry)
        self.labelPower.setObjectName("labelPower")

        self.layoutEntry.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelPower)

        self.spinPower = QDoubleSpinBox(self.groupEntry)
        self.spinPower.setObjectName("spinPower")
        self.spinPower.setDecimals(9)
        self.spinPower.setMaximum(1.000000000000000)
        self.spinPower.setSingleStep(0.000000100000000)

        self.layoutEntry.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spinPower)

        self.buttonAdd = QPushButton(self.groupEntry)
        self.buttonAdd.setObjectName("buttonAdd")

        self.layoutEntry.setWidget(2, QFormLayout.ItemRole.SpanningRole, self.buttonAdd)

        self.layoutMain.addWidget(self.groupEntry)

        self.valueFactor = QLabel(PowerCalibrationGainTab)
        self.valueFactor.setObjectName("valueFactor")
        self.valueFactor.setText("\u2014")

        self.layoutMain.addWidget(self.valueFactor)

        self.tablePoints = QTableWidget(PowerCalibrationGainTab)
        if self.tablePoints.columnCount() < 3:
            self.tablePoints.setColumnCount(3)
        self.tablePoints.setObjectName("tablePoints")
        self.tablePoints.setMinimumSize(QSize(0, 100))
        self.tablePoints.setMaximumSize(QSize(16777215, 180))
        self.tablePoints.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tablePoints.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tablePoints.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tablePoints.verticalHeader().setVisible(False)

        self.layoutMain.addWidget(self.tablePoints)

        self.buttonRemove = QPushButton(PowerCalibrationGainTab)
        self.buttonRemove.setObjectName("buttonRemove")

        self.layoutMain.addWidget(self.buttonRemove)

        self.calibrationPlot = PlotWidget(PowerCalibrationGainTab)
        self.calibrationPlot.setObjectName("calibrationPlot")

        self.layoutMain.addWidget(self.calibrationPlot)

        self.layoutMain.setStretch(4, 1)

        self.retranslateUi(PowerCalibrationGainTab)

        QMetaObject.connectSlotsByName(PowerCalibrationGainTab)

    # setupUi

    def retranslateUi(self, PowerCalibrationGainTab):
        self.groupEntry.setTitle(
            QCoreApplication.translate("PowerCalibrationGainTab", "Messpunkt hinzuf\u00fcgen", None)
        )
        self.labelVoltage.setText(
            QCoreApplication.translate("PowerCalibrationGainTab", "Spannung (V):", None)
        )
        self.spinVoltage.setSuffix(
            QCoreApplication.translate("PowerCalibrationGainTab", " V", None)
        )
        # if QT_CONFIG(tooltip)
        self.buttonLive.setToolTip(
            QCoreApplication.translate(
                "PowerCalibrationGainTab", "Aktuelle Sensorspannung \u00fcbernehmen", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonLive.setText(QCoreApplication.translate("PowerCalibrationGainTab", "Live", None))
        self.labelPower.setText(
            QCoreApplication.translate("PowerCalibrationGainTab", "Leistung (W):", None)
        )
        self.spinPower.setSuffix(QCoreApplication.translate("PowerCalibrationGainTab", " W", None))
        self.buttonAdd.setText(
            QCoreApplication.translate("PowerCalibrationGainTab", "Punkt hinzuf\u00fcgen", None)
        )
        self.buttonRemove.setText(
            QCoreApplication.translate(
                "PowerCalibrationGainTab", "Ausgew\u00e4hlten Punkt l\u00f6schen", None
            )
        )
        pass

    # retranslateUi
