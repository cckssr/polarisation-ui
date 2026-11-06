# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'measurement_panel.ui'
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
    QGroupBox,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QWidget,
)


class Ui_MeasurementPanel(object):
    def setupUi(self, MeasurementPanel):
        if not MeasurementPanel.objectName():
            MeasurementPanel.setObjectName("MeasurementPanel")
        self.horizontalLayout = QHBoxLayout(MeasurementPanel)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.buttonStart = QPushButton(MeasurementPanel)
        self.buttonStart.setObjectName("buttonStart")

        self.horizontalLayout.addWidget(self.buttonStart)

        self.buttonStop = QPushButton(MeasurementPanel)
        self.buttonStop.setObjectName("buttonStop")

        self.horizontalLayout.addWidget(self.buttonStop)

        self.buttonReset = QPushButton(MeasurementPanel)
        self.buttonReset.setObjectName("buttonReset")

        self.horizontalLayout.addWidget(self.buttonReset)

        self.retranslateUi(MeasurementPanel)

        QMetaObject.connectSlotsByName(MeasurementPanel)

    # setupUi

    def retranslateUi(self, MeasurementPanel):
        MeasurementPanel.setTitle(QCoreApplication.translate("MeasurementPanel", "Messung", None))
        self.buttonStart.setText(QCoreApplication.translate("MeasurementPanel", "Start", None))
        # if QT_CONFIG(tooltip)
        self.buttonStart.setToolTip(
            QCoreApplication.translate("MeasurementPanel", "Start der Messung", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonStop.setText(QCoreApplication.translate("MeasurementPanel", "Stop", None))
        # if QT_CONFIG(tooltip)
        self.buttonStop.setToolTip(
            QCoreApplication.translate("MeasurementPanel", "Aktuelle Messung stoppen", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonReset.setText(QCoreApplication.translate("MeasurementPanel", "Reset", None))
        # if QT_CONFIG(tooltip)
        self.buttonReset.setToolTip(
            QCoreApplication.translate(
                "MeasurementPanel", "Alle gespeicherten Messpunkte verwerfen", None
            )
        )


# endif // QT_CONFIG(tooltip)
# retranslateUi
