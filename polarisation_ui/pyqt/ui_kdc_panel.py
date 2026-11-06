# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'kdc_panel.ui'
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
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QToolButton,
    QWidget,
)

from polarisation_ui.ui.widgets.elided_label import ElidedLabel


class Ui_KdcPanel(object):
    def setupUi(self, KdcPanel):
        if not KdcPanel.objectName():
            KdcPanel.setObjectName("KdcPanel")
        self.gridLayout = QGridLayout(KdcPanel)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setHorizontalSpacing(6)
        self.gridLayout.setVerticalSpacing(6)
        self.labelDevice = QLabel(KdcPanel)
        self.labelDevice.setObjectName("labelDevice")

        self.gridLayout.addWidget(self.labelDevice, 0, 0, 1, 1)

        self.comboDevice = QComboBox(KdcPanel)
        self.comboDevice.setObjectName("comboDevice")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboDevice.sizePolicy().hasHeightForWidth())
        self.comboDevice.setSizePolicy(sizePolicy)
        self.comboDevice.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
        )
        self.comboDevice.setMinimumContentsLength(8)

        self.gridLayout.addWidget(self.comboDevice, 0, 1, 1, 1)

        self.buttonRefresh = QToolButton(KdcPanel)
        self.buttonRefresh.setObjectName("buttonRefresh")

        self.gridLayout.addWidget(self.buttonRefresh, 0, 2, 1, 1)

        self.labelStatus = QLabel(KdcPanel)
        self.labelStatus.setObjectName("labelStatus")

        self.gridLayout.addWidget(self.labelStatus, 1, 0, 1, 1)

        self.statusLayout = QHBoxLayout()
        self.statusLayout.setSpacing(6)
        self.statusLayout.setObjectName("statusLayout")
        self.valueStatus = ElidedLabel(KdcPanel)
        self.valueStatus.setObjectName("valueStatus")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.valueStatus.sizePolicy().hasHeightForWidth())
        self.valueStatus.setSizePolicy(sizePolicy1)

        self.statusLayout.addWidget(self.valueStatus)

        self.ledStatus = QLabel(KdcPanel)
        self.ledStatus.setObjectName("ledStatus")

        self.statusLayout.addWidget(self.ledStatus)

        self.gridLayout.addLayout(self.statusLayout, 1, 1, 1, 2)

        self.labelPosition = QLabel(KdcPanel)
        self.labelPosition.setObjectName("labelPosition")

        self.gridLayout.addWidget(self.labelPosition, 2, 0, 1, 1)

        self.valuePosition = QLabel(KdcPanel)
        self.valuePosition.setObjectName("valuePosition")

        self.gridLayout.addWidget(self.valuePosition, 2, 1, 1, 2)

        self.labelOffset = QLabel(KdcPanel)
        self.labelOffset.setObjectName("labelOffset")

        self.gridLayout.addWidget(self.labelOffset, 3, 0, 1, 1)

        self.valueOffset = QLabel(KdcPanel)
        self.valueOffset.setObjectName("valueOffset")

        self.gridLayout.addWidget(self.valueOffset, 3, 1, 1, 2)

        self.connectLayout = QHBoxLayout()
        self.connectLayout.setObjectName("connectLayout")
        self.buttonConnect = QPushButton(KdcPanel)
        self.buttonConnect.setObjectName("buttonConnect")

        self.connectLayout.addWidget(self.buttonConnect)

        self.buttonHome = QPushButton(KdcPanel)
        self.buttonHome.setObjectName("buttonHome")

        self.connectLayout.addWidget(self.buttonHome)

        self.gridLayout.addLayout(self.connectLayout, 4, 0, 1, 3)

        self.zeroLayout = QHBoxLayout()
        self.zeroLayout.setObjectName("zeroLayout")
        self.buttonZero = QPushButton(KdcPanel)
        self.buttonZero.setObjectName("buttonZero")

        self.zeroLayout.addWidget(self.buttonZero)

        self.buttonOffsetReset = QPushButton(KdcPanel)
        self.buttonOffsetReset.setObjectName("buttonOffsetReset")

        self.zeroLayout.addWidget(self.buttonOffsetReset)

        self.gridLayout.addLayout(self.zeroLayout, 5, 0, 1, 3)

        self.gridLayout.setColumnStretch(1, 1)

        self.retranslateUi(KdcPanel)

        QMetaObject.connectSlotsByName(KdcPanel)

    # setupUi

    def retranslateUi(self, KdcPanel):
        KdcPanel.setTitle(QCoreApplication.translate("KdcPanel", "KDC-Verbindung", None))
        self.labelDevice.setText(QCoreApplication.translate("KdcPanel", "Ger\u00e4t", None))
        # if QT_CONFIG(tooltip)
        self.comboDevice.setToolTip(
            QCoreApplication.translate(
                "KdcPanel",
                "Thorlabs KDC101 Polarisationsrotator (USB-APT) \u2014 Seriennummer oder COM-Port eingeben",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonRefresh.setText(QCoreApplication.translate("KdcPanel", "...", None))
        # if QT_CONFIG(tooltip)
        self.buttonRefresh.setToolTip(
            QCoreApplication.translate("KdcPanel", "KDC101-Ger\u00e4teliste aktualisieren", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.labelStatus.setText(QCoreApplication.translate("KdcPanel", "Status", None))
        self.ledStatus.setStyleSheet(
            QCoreApplication.translate(
                "KdcPanel",
                "background-color: rgb(255, 11, 3); border: 0px; padding: 4px; border-radius: 10px",
                None,
            )
        )
        self.labelPosition.setText(QCoreApplication.translate("KdcPanel", "Position", None))
        # if QT_CONFIG(tooltip)
        self.valuePosition.setToolTip(
            QCoreApplication.translate(
                "KdcPanel",
                "Aktuelle mechanische Position des KDC101 (roher Stage-Winkel, ohne Offset)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.labelOffset.setText(QCoreApplication.translate("KdcPanel", "Offset", None))
        # if QT_CONFIG(tooltip)
        self.valueOffset.setToolTip(
            QCoreApplication.translate(
                "KdcPanel",
                "Aktueller Nullpunkt-Offset, gesetzt durch \u201eOptik Nullen\u201c. Wird von Malus- und Verz\u00f6gerungsplatten-Scans als Referenzwinkel verwendet.",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonConnect.setText(QCoreApplication.translate("KdcPanel", "Verbinden", None))
        # if QT_CONFIG(tooltip)
        self.buttonConnect.setToolTip(
            QCoreApplication.translate(
                "KdcPanel", "KDC101 Polarisationsrotator verbinden oder trennen", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonHome.setText(QCoreApplication.translate("KdcPanel", "Home", None))
        # if QT_CONFIG(tooltip)
        self.buttonHome.setToolTip(
            QCoreApplication.translate("KdcPanel", "KDC101 auf Nullposition fahren (Home)", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonZero.setText(QCoreApplication.translate("KdcPanel", "Optik Nullen", None))
        # if QT_CONFIG(tooltip)
        self.buttonZero.setToolTip(
            QCoreApplication.translate(
                "KdcPanel",
                "Extinktionswinkel des eingesetzten Polarisators (linear, \u03bb/4 oder \u03bb/2) suchen: Grobsuche bei PDTIA-Gain 1, Feinsuche bei Gain 3 oder alternativ mit PM400. Das Ergebnis wird als Offset gespeichert und von Malus- und Verz\u00f6gerungsplatten-Scans automatisch verwendet.",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonOffsetReset.setText(
            QCoreApplication.translate("KdcPanel", "Offset zur\u00fccksetzen", None)
        )
        # if QT_CONFIG(tooltip)
        self.buttonOffsetReset.setToolTip(
            QCoreApplication.translate(
                "KdcPanel", "Gespeicherten Nullpunkt-Offset auf 0\u00b0 zur\u00fccksetzen", None
            )
        )


# endif // QT_CONFIG(tooltip)
# retranslateUi
