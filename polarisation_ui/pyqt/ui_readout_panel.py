# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'readout_panel.ui'
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
    QApplication,
    QButtonGroup,
    QGroupBox,
    QHBoxLayout,
    QLCDNumber,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class Ui_ReadoutPanel(object):
    def setupUi(self, ReadoutPanel):
        if not ReadoutPanel.objectName():
            ReadoutPanel.setObjectName("ReadoutPanel")
        self.verticalLayout = QVBoxLayout(ReadoutPanel)
        self.verticalLayout.setObjectName("verticalLayout")
        self.labelSampleAngle = QLabel(ReadoutPanel)
        self.labelSampleAngle.setObjectName("labelSampleAngle")

        self.verticalLayout.addWidget(self.labelSampleAngle)

        self.lcdSampleAngle = QLCDNumber(ReadoutPanel)
        self.lcdSampleAngle.setObjectName("lcdSampleAngle")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lcdSampleAngle.sizePolicy().hasHeightForWidth())
        self.lcdSampleAngle.setSizePolicy(sizePolicy)
        self.lcdSampleAngle.setMinimumSize(QSize(0, 40))
        self.lcdSampleAngle.setLineWidth(2)
        self.lcdSampleAngle.setSmallDecimalPoint(False)
        self.lcdSampleAngle.setDigitCount(8)
        self.lcdSampleAngle.setSegmentStyle(QLCDNumber.SegmentStyle.Filled)

        self.verticalLayout.addWidget(self.lcdSampleAngle)

        self.labelDetectorAngle = QLabel(ReadoutPanel)
        self.labelDetectorAngle.setObjectName("labelDetectorAngle")

        self.verticalLayout.addWidget(self.labelDetectorAngle)

        self.lcdDetectorAngle = QLCDNumber(ReadoutPanel)
        self.lcdDetectorAngle.setObjectName("lcdDetectorAngle")
        sizePolicy.setHeightForWidth(self.lcdDetectorAngle.sizePolicy().hasHeightForWidth())
        self.lcdDetectorAngle.setSizePolicy(sizePolicy)
        self.lcdDetectorAngle.setMinimumSize(QSize(0, 40))
        self.lcdDetectorAngle.setLineWidth(2)
        self.lcdDetectorAngle.setSmallDecimalPoint(False)
        self.lcdDetectorAngle.setDigitCount(8)
        self.lcdDetectorAngle.setSegmentStyle(QLCDNumber.SegmentStyle.Filled)

        self.verticalLayout.addWidget(self.lcdDetectorAngle)

        self.labelVoltage = QLabel(ReadoutPanel)
        self.labelVoltage.setObjectName("labelVoltage")

        self.verticalLayout.addWidget(self.labelVoltage)

        self.lcdVoltage = QLCDNumber(ReadoutPanel)
        self.lcdVoltage.setObjectName("lcdVoltage")
        sizePolicy.setHeightForWidth(self.lcdVoltage.sizePolicy().hasHeightForWidth())
        self.lcdVoltage.setSizePolicy(sizePolicy)
        self.lcdVoltage.setMinimumSize(QSize(0, 40))
        self.lcdVoltage.setLineWidth(2)
        self.lcdVoltage.setSmallDecimalPoint(False)
        self.lcdVoltage.setDigitCount(8)
        self.lcdVoltage.setSegmentStyle(QLCDNumber.SegmentStyle.Filled)

        self.verticalLayout.addWidget(self.lcdVoltage)

        self.labelPower = QLabel(ReadoutPanel)
        self.labelPower.setObjectName("labelPower")

        self.verticalLayout.addWidget(self.labelPower)

        self.lcdPower = QLCDNumber(ReadoutPanel)
        self.lcdPower.setObjectName("lcdPower")
        sizePolicy.setHeightForWidth(self.lcdPower.sizePolicy().hasHeightForWidth())
        self.lcdPower.setSizePolicy(sizePolicy)
        self.lcdPower.setMinimumSize(QSize(0, 40))
        self.lcdPower.setLineWidth(2)
        self.lcdPower.setSmallDecimalPoint(False)
        self.lcdPower.setDigitCount(8)
        self.lcdPower.setSegmentStyle(QLCDNumber.SegmentStyle.Filled)

        self.verticalLayout.addWidget(self.lcdPower)

        self.labelGain = QLabel(ReadoutPanel)
        self.labelGain.setObjectName("labelGain")

        self.verticalLayout.addWidget(self.labelGain)

        self.gainLayout = QHBoxLayout()
        self.gainLayout.setSpacing(4)
        self.gainLayout.setObjectName("gainLayout")
        self.buttonGain1 = QPushButton(ReadoutPanel)
        self.buttonGroupGain = QButtonGroup(ReadoutPanel)
        self.buttonGroupGain.setObjectName("buttonGroupGain")
        self.buttonGroupGain.addButton(self.buttonGain1)
        self.buttonGain1.setObjectName("buttonGain1")
        self.buttonGain1.setCheckable(True)
        self.buttonGain1.setMinimumSize(QSize(28, 0))

        self.gainLayout.addWidget(self.buttonGain1)

        self.buttonGain2 = QPushButton(ReadoutPanel)
        self.buttonGroupGain.addButton(self.buttonGain2)
        self.buttonGain2.setObjectName("buttonGain2")
        self.buttonGain2.setCheckable(True)
        self.buttonGain2.setMinimumSize(QSize(28, 0))

        self.gainLayout.addWidget(self.buttonGain2)

        self.buttonGain3 = QPushButton(ReadoutPanel)
        self.buttonGroupGain.addButton(self.buttonGain3)
        self.buttonGain3.setObjectName("buttonGain3")
        self.buttonGain3.setCheckable(True)
        self.buttonGain3.setMinimumSize(QSize(28, 0))

        self.gainLayout.addWidget(self.buttonGain3)

        self.buttonGain4 = QPushButton(ReadoutPanel)
        self.buttonGroupGain.addButton(self.buttonGain4)
        self.buttonGain4.setObjectName("buttonGain4")
        self.buttonGain4.setCheckable(True)
        self.buttonGain4.setMinimumSize(QSize(28, 0))

        self.gainLayout.addWidget(self.buttonGain4)

        self.buttonGainAuto = QPushButton(ReadoutPanel)
        self.buttonGainAuto.setObjectName("buttonGainAuto")
        self.buttonGainAuto.setCheckable(True)
        self.buttonGainAuto.setMinimumSize(QSize(28, 0))

        self.gainLayout.addWidget(self.buttonGainAuto)

        self.verticalLayout.addLayout(self.gainLayout)

        self.retranslateUi(ReadoutPanel)

        QMetaObject.connectSlotsByName(ReadoutPanel)

    # setupUi

    def retranslateUi(self, ReadoutPanel):
        ReadoutPanel.setTitle(QCoreApplication.translate("ReadoutPanel", "Messwerte", None))
        self.labelSampleAngle.setText(
            QCoreApplication.translate("ReadoutPanel", "Proben-Rotationswinkel (\u00b0)", None)
        )
        # if QT_CONFIG(tooltip)
        self.lcdSampleAngle.setToolTip(
            QCoreApplication.translate(
                "ReadoutPanel", "Aktueller Winkel der Proben-Rotationsstage (\u00b0)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.labelDetectorAngle.setText(
            QCoreApplication.translate("ReadoutPanel", "Detektor-Rotationswinkel (\u00b0)", None)
        )
        # if QT_CONFIG(tooltip)
        self.lcdDetectorAngle.setToolTip(
            QCoreApplication.translate(
                "ReadoutPanel", "Aktueller Winkel der Detektor-Rotationsstage (\u00b0)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.labelVoltage.setText(
            QCoreApplication.translate("ReadoutPanel", "Detektor-Spannung (mV)", None)
        )
        # if QT_CONFIG(tooltip)
        self.lcdVoltage.setToolTip(
            QCoreApplication.translate("ReadoutPanel", "Detektorspannung in Millivolt (mV)", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.labelPower.setText(
            QCoreApplication.translate("ReadoutPanel", "Detektor-Leistung (\u00b5W)", None)
        )
        # if QT_CONFIG(tooltip)
        self.lcdPower.setToolTip(
            QCoreApplication.translate(
                "ReadoutPanel",
                "Berechnete Laserleistung in Mikrowatt (\u00b5W) \u2014 nur mit geladenem Kalibrierungsprofil oder PM400",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.labelGain.setText(
            QCoreApplication.translate("ReadoutPanel", "Detektor-Gainstufe", None)
        )
        self.buttonGain1.setText(QCoreApplication.translate("ReadoutPanel", "1", None))
        # if QT_CONFIG(tooltip)
        self.buttonGain1.setToolTip(
            QCoreApplication.translate(
                "ReadoutPanel", "PD-TIA Verst\u00e4rkungsstufe 1 (niedrigste Empfindlichkeit)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonGain2.setText(QCoreApplication.translate("ReadoutPanel", "2", None))
        # if QT_CONFIG(tooltip)
        self.buttonGain2.setToolTip(
            QCoreApplication.translate("ReadoutPanel", "PD-TIA Verst\u00e4rkungsstufe 2", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonGain3.setText(QCoreApplication.translate("ReadoutPanel", "3", None))
        # if QT_CONFIG(tooltip)
        self.buttonGain3.setToolTip(
            QCoreApplication.translate("ReadoutPanel", "PD-TIA Verst\u00e4rkungsstufe 3", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonGain4.setText(QCoreApplication.translate("ReadoutPanel", "4", None))
        # if QT_CONFIG(tooltip)
        self.buttonGain4.setToolTip(
            QCoreApplication.translate(
                "ReadoutPanel",
                "PD-TIA Verst\u00e4rkungsstufe 4 (h\u00f6chste Empfindlichkeit)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonGainAuto.setText(QCoreApplication.translate("ReadoutPanel", "AUTO", None))
        # if QT_CONFIG(tooltip)
        self.buttonGainAuto.setToolTip(
            QCoreApplication.translate(
                "ReadoutPanel", "Automatische Wahl der PD-TIA Verst\u00e4rkungsstufe", None
            )
        )


# endif // QT_CONFIG(tooltip)
# retranslateUi
