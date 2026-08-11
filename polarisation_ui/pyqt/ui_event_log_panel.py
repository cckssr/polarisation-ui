# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'event_log_panel.ui'
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
from PySide6.QtWidgets import QApplication, QPlainTextEdit, QSizePolicy, QVBoxLayout, QWidget


class Ui_EventLogPanel(object):
    def setupUi(self, EventLogPanel):
        if not EventLogPanel.objectName():
            EventLogPanel.setObjectName("EventLogPanel")
        EventLogPanel.resize(800, 150)
        self.verticalLayout = QVBoxLayout(EventLogPanel)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.textLog = QPlainTextEdit(EventLogPanel)
        self.textLog.setObjectName("textLog")
        self.textLog.setReadOnly(True)
        self.textLog.setMaximumBlockCount(500)
        font = QFont()
        font.setFamilies(["Courier New"])
        font.setStyleStrategy(QFont.PreferDefault)
        self.textLog.setFont(font)

        self.verticalLayout.addWidget(self.textLog)

        self.retranslateUi(EventLogPanel)

        QMetaObject.connectSlotsByName(EventLogPanel)

    # setupUi

    def retranslateUi(self, EventLogPanel):
        pass

    # retranslateUi
