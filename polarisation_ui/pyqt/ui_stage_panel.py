# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'stage_panel.ui'
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
    QCheckBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QWidget,
)

from polarisation_ui.ui.widgets.elided_label import ElidedLabel


class Ui_StagePanel(object):
    def setupUi(self, StagePanel):
        if not StagePanel.objectName():
            StagePanel.setObjectName("StagePanel")
        self.gridLayout = QGridLayout(StagePanel)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setHorizontalSpacing(6)
        self.gridLayout.setVerticalSpacing(6)
        self.labelStatus = QLabel(StagePanel)
        self.labelStatus.setObjectName("labelStatus")

        self.gridLayout.addWidget(self.labelStatus, 0, 0, 1, 1)

        self.statusLayout = QHBoxLayout()
        self.statusLayout.setSpacing(6)
        self.statusLayout.setObjectName("statusLayout")
        self.valueStatus = ElidedLabel(StagePanel)
        self.valueStatus.setObjectName("valueStatus")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.valueStatus.sizePolicy().hasHeightForWidth())
        self.valueStatus.setSizePolicy(sizePolicy)

        self.statusLayout.addWidget(self.valueStatus)

        self.ledStatus = QLabel(StagePanel)
        self.ledStatus.setObjectName("ledStatus")

        self.statusLayout.addWidget(self.ledStatus)

        self.gridLayout.addLayout(self.statusLayout, 0, 1, 1, 1)

        self.averageLayout = QHBoxLayout()
        self.averageLayout.setObjectName("averageLayout")
        self.checkAverage = QCheckBox(StagePanel)
        self.checkAverage.setObjectName("checkAverage")

        self.averageLayout.addWidget(self.checkAverage)

        self.spinAverages = QSpinBox(StagePanel)
        self.spinAverages.setObjectName("spinAverages")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.spinAverages.sizePolicy().hasHeightForWidth())
        self.spinAverages.setSizePolicy(sizePolicy1)
        self.spinAverages.setMinimum(2)
        self.spinAverages.setMaximum(100)
        self.spinAverages.setValue(5)

        self.averageLayout.addWidget(self.spinAverages)

        self.gridLayout.addLayout(self.averageLayout, 1, 0, 1, 2)

        self.zeroLayout = QHBoxLayout()
        self.zeroLayout.setObjectName("zeroLayout")
        self.buttonZero = QPushButton(StagePanel)
        self.buttonZero.setObjectName("buttonZero")

        self.zeroLayout.addWidget(self.buttonZero)

        self.button180 = QPushButton(StagePanel)
        self.button180.setObjectName("button180")

        self.zeroLayout.addWidget(self.button180)

        self.gridLayout.addLayout(self.zeroLayout, 2, 0, 1, 2)

        self.gridLayout.setColumnStretch(1, 1)

        self.retranslateUi(StagePanel)

        QMetaObject.connectSlotsByName(StagePanel)

    # setupUi

    def retranslateUi(self, StagePanel):
        StagePanel.setTitle(QCoreApplication.translate("StagePanel", "Rotationsstage", None))
        self.labelStatus.setText(QCoreApplication.translate("StagePanel", "Status", None))
        self.ledStatus.setStyleSheet(
            QCoreApplication.translate(
                "StagePanel",
                "background-color: rgb(255, 11, 3); border: 0px; padding: 4px; border-radius: 10px",
                None,
            )
        )
        self.checkAverage.setText(
            QCoreApplication.translate("StagePanel", "Mittelung aktivieren", None)
        )
        self.spinAverages.setSuffix(QCoreApplication.translate("StagePanel", " Werte", None))
        self.buttonZero.setText(
            QCoreApplication.translate("StagePanel", "Nullpunkt-Kalibrierung", None)
        )
        self.button180.setText(
            QCoreApplication.translate("StagePanel", "180\u00b0-Kalibrierung", None)
        )
        # if QT_CONFIG(tooltip)
        self.button180.setToolTip(
            QCoreApplication.translate(
                "StagePanel",
                "Aktuellen Winkel als halbe Rotation (180\u00b0) setzen (Encoder B)",
                None,
            )
        )


# endif // QT_CONFIG(tooltip)
# retranslateUi
