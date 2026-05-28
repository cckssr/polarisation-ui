# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'connection_banner.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy, QSpacerItem, QWidget)

class Ui_ConnectionBanner(object):
    def setupUi(self, ConnectionBanner):
        if not ConnectionBanner.objectName():
            ConnectionBanner.setObjectName(u"ConnectionBanner")
        ConnectionBanner.resize(600, 36)
        ConnectionBanner.setFrameShape(QFrame.Shape.StyledPanel)
        self.horizontalLayout = QHBoxLayout(ConnectionBanner)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(8, 4, 8, 4)
        self.lblBannerText = QLabel(ConnectionBanner)
        self.lblBannerText.setObjectName(u"lblBannerText")
        self.lblBannerText.setWordWrap(False)

        self.horizontalLayout.addWidget(self.lblBannerText)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.btnBannerExport = QPushButton(ConnectionBanner)
        self.btnBannerExport.setObjectName(u"btnBannerExport")
        self.btnBannerExport.setVisible(False)

        self.horizontalLayout.addWidget(self.btnBannerExport)


        self.retranslateUi(ConnectionBanner)

        QMetaObject.connectSlotsByName(ConnectionBanner)
    # setupUi

    def retranslateUi(self, ConnectionBanner):
        self.lblBannerText.setText("")
        self.btnBannerExport.setText(QCoreApplication.translate("ConnectionBanner", u"Exportieren\u2026", None))
        pass
    # retranslateUi

