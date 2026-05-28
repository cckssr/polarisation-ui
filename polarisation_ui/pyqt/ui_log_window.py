# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'log_window.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
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
    QAbstractButton,
    QApplication,
    QDialog,
    QDialogButtonBox,
    QPlainTextEdit,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class Ui_LogWindow(object):
    def setupUi(self, LogWindow):
        if not LogWindow.objectName():
            LogWindow.setObjectName("LogWindow")
        LogWindow.resize(820, 480)
        self.verticalLayout = QVBoxLayout(LogWindow)
        self.verticalLayout.setObjectName("verticalLayout")
        self.textLog = QPlainTextEdit(LogWindow)
        self.textLog.setObjectName("textLog")
        self.textLog.setReadOnly(True)
        font = QFont()
        font.setFamilies(["Courier New"])
        font.setStyleStrategy(QFont.PreferDefault)
        self.textLog.setFont(font)
        self.textLog.setMaximumBlockCount(2000)

        self.verticalLayout.addWidget(self.textLog)

        self.buttonBox = QDialogButtonBox(LogWindow)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Close)

        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(LogWindow)

        QMetaObject.connectSlotsByName(LogWindow)

    # setupUi

    def retranslateUi(self, LogWindow):
        LogWindow.setWindowTitle(
            QCoreApplication.translate("LogWindow", "Log-Ausgabe", None)
        )

    # retranslateUi
