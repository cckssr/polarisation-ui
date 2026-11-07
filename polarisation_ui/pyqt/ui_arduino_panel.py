# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'arduino_panel.ui'
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


class Ui_ArduinoPanel(object):
    def setupUi(self, ArduinoPanel):
        if not ArduinoPanel.objectName():
            ArduinoPanel.setObjectName("ArduinoPanel")
        ArduinoPanel.resize(247, 133)
        self.gridLayout = QGridLayout(ArduinoPanel)
        self.gridLayout.setSpacing(6)
        self.gridLayout.setObjectName("gridLayout")
        self.labelPort = QLabel(ArduinoPanel)
        self.labelPort.setObjectName("labelPort")

        self.gridLayout.addWidget(self.labelPort, 0, 0, 1, 1)

        self.comboPort = QComboBox(ArduinoPanel)
        self.comboPort.setObjectName("comboPort")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboPort.sizePolicy().hasHeightForWidth())
        self.comboPort.setSizePolicy(sizePolicy)
        self.comboPort.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
        )
        self.comboPort.setMinimumContentsLength(8)

        self.gridLayout.addWidget(self.comboPort, 0, 1, 1, 1)

        self.buttonRefreshPorts = QToolButton(ArduinoPanel)
        self.buttonRefreshPorts.setObjectName("buttonRefreshPorts")
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.ViewRefresh))
        self.buttonRefreshPorts.setIcon(icon)

        self.gridLayout.addWidget(self.buttonRefreshPorts, 0, 2, 1, 1)

        self.labelStatus = QLabel(ArduinoPanel)
        self.labelStatus.setObjectName("labelStatus")

        self.gridLayout.addWidget(self.labelStatus, 1, 0, 1, 1)

        self.statusLayout = QHBoxLayout()
        self.statusLayout.setSpacing(6)
        self.statusLayout.setObjectName("statusLayout")
        self.valueStatus = ElidedLabel(ArduinoPanel)
        self.valueStatus.setObjectName("valueStatus")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.valueStatus.sizePolicy().hasHeightForWidth())
        self.valueStatus.setSizePolicy(sizePolicy1)

        self.statusLayout.addWidget(self.valueStatus)

        self.ledStatus = QLabel(ArduinoPanel)
        self.ledStatus.setObjectName("ledStatus")

        self.statusLayout.addWidget(self.ledStatus)

        self.gridLayout.addLayout(self.statusLayout, 1, 1, 1, 2)

        self.buttonConnect = QPushButton(ArduinoPanel)
        self.buttonConnect.setObjectName("buttonConnect")

        self.gridLayout.addWidget(self.buttonConnect, 2, 0, 1, 3)

        self.gridLayout.setColumnStretch(1, 1)

        self.retranslateUi(ArduinoPanel)

        QMetaObject.connectSlotsByName(ArduinoPanel)

    # setupUi

    def retranslateUi(self, ArduinoPanel):
        ArduinoPanel.setTitle(
            QCoreApplication.translate("ArduinoPanel", "Arduino-Verbindung", None)
        )
        self.labelPort.setText(QCoreApplication.translate("ArduinoPanel", "Port", None))
        # if QT_CONFIG(tooltip)
        self.comboPort.setToolTip(
            QCoreApplication.translate(
                "ArduinoPanel", "Serieller Port des Arduino Nano ESP32", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(tooltip)
        self.buttonRefreshPorts.setToolTip(
            QCoreApplication.translate(
                "ArduinoPanel", "Verf\u00fcgbare serielle Ports aktualisieren", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonRefreshPorts.setText(QCoreApplication.translate("ArduinoPanel", "...", None))
        self.labelStatus.setText(QCoreApplication.translate("ArduinoPanel", "Status", None))
        self.ledStatus.setStyleSheet(
            QCoreApplication.translate(
                "ArduinoPanel",
                "background-color: rgb(255, 11, 3); border: 0px; padding: 4px; border-radius: 10px",
                None,
            )
        )
        # if QT_CONFIG(tooltip)
        self.buttonConnect.setToolTip(
            QCoreApplication.translate(
                "ArduinoPanel",
                "Arduino \u00fcber den gew\u00e4hlten seriellen Port verbinden oder trennen",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonConnect.setText(QCoreApplication.translate("ArduinoPanel", "Verbinden", None))

    # retranslateUi
