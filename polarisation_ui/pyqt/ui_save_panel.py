# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'save_panel.ui'
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
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QWidget,
)

from polarisation_ui.ui.widgets.elided_label import ElidedLabel


class Ui_SavePanel(object):
    def setupUi(self, SavePanel):
        if not SavePanel.objectName():
            SavePanel.setObjectName("SavePanel")
        SavePanel.resize(339, 259)
        self.gridLayout = QGridLayout(SavePanel)
        self.gridLayout.setSpacing(6)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setContentsMargins(5, 5, 5, 5)
        self.labelHint = QLabel(SavePanel)
        self.labelHint.setObjectName("labelHint")
        self.labelHint.setWordWrap(True)

        self.gridLayout.addWidget(self.labelHint, 0, 0, 1, 2)

        self.labelGroup = QLabel(SavePanel)
        self.labelGroup.setObjectName("labelGroup")

        self.gridLayout.addWidget(self.labelGroup, 1, 0, 1, 1)

        self.comboGroup = QComboBox(SavePanel)
        self.comboGroup.addItem("A")
        self.comboGroup.addItem("B")
        self.comboGroup.addItem("C")
        self.comboGroup.addItem("D")
        self.comboGroup.addItem("E")
        self.comboGroup.addItem("F")
        self.comboGroup.addItem("G")
        self.comboGroup.addItem("H")
        self.comboGroup.addItem("I")
        self.comboGroup.addItem("J")
        self.comboGroup.addItem("K")
        self.comboGroup.addItem("L")
        self.comboGroup.addItem("M")
        self.comboGroup.addItem("N")
        self.comboGroup.addItem("O")
        self.comboGroup.addItem("P")
        self.comboGroup.addItem("Q")
        self.comboGroup.addItem("R")
        self.comboGroup.addItem("S")
        self.comboGroup.addItem("T")
        self.comboGroup.addItem("U")
        self.comboGroup.addItem("V")
        self.comboGroup.addItem("W")
        self.comboGroup.addItem("Z")
        self.comboGroup.setObjectName("comboGroup")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboGroup.sizePolicy().hasHeightForWidth())
        self.comboGroup.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.comboGroup, 1, 1, 1, 1)

        self.labelTeam = QLabel(SavePanel)
        self.labelTeam.setObjectName("labelTeam")

        self.gridLayout.addWidget(self.labelTeam, 2, 0, 1, 1)

        self.editTeam = QLineEdit(SavePanel)
        self.editTeam.setObjectName("editTeam")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.editTeam.sizePolicy().hasHeightForWidth())
        self.editTeam.setSizePolicy(sizePolicy1)
        self.editTeam.setClearButtonEnabled(True)

        self.gridLayout.addWidget(self.editTeam, 2, 1, 1, 1)

        self.labelSuffix = QLabel(SavePanel)
        self.labelSuffix.setObjectName("labelSuffix")

        self.gridLayout.addWidget(self.labelSuffix, 3, 0, 1, 1)

        self.editSuffix = QLineEdit(SavePanel)
        self.editSuffix.setObjectName("editSuffix")
        sizePolicy1.setHeightForWidth(self.editSuffix.sizePolicy().hasHeightForWidth())
        self.editSuffix.setSizePolicy(sizePolicy1)
        self.editSuffix.setMaxLength(20)

        self.gridLayout.addWidget(self.editSuffix, 3, 1, 1, 1)

        self.labelFilename = QLabel(SavePanel)
        self.labelFilename.setObjectName("labelFilename")

        self.gridLayout.addWidget(self.labelFilename, 4, 0, 1, 2)

        self.valueFilename = ElidedLabel(SavePanel)
        self.valueFilename.setObjectName("valueFilename")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(1)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.valueFilename.sizePolicy().hasHeightForWidth())
        self.valueFilename.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.valueFilename, 5, 0, 1, 2)

        self.labelDropbox = QLabel(SavePanel)
        self.labelDropbox.setObjectName("labelDropbox")
        self.labelDropbox.setTextFormat(Qt.TextFormat.RichText)
        self.labelDropbox.setOpenExternalLinks(True)

        self.gridLayout.addWidget(self.labelDropbox, 6, 0, 1, 2)

        self.buttonSave = QPushButton(SavePanel)
        self.buttonSave.setObjectName("buttonSave")

        self.gridLayout.addWidget(self.buttonSave, 7, 0, 1, 2)

        self.gridLayout.setColumnStretch(1, 2)

        self.retranslateUi(SavePanel)

        QMetaObject.connectSlotsByName(SavePanel)

    # setupUi

    def retranslateUi(self, SavePanel):
        SavePanel.setTitle(QCoreApplication.translate("SavePanel", "Speicherung", None))
        self.labelHint.setText(
            QCoreApplication.translate(
                "SavePanel",
                "Bitte vor Beginn der Messungen Gruppe ausw\u00e4hlen und ggf. individuelle Team-Bezeichnung hinzuf\u00fcgen",
                None,
            )
        )
        self.labelGroup.setText(QCoreApplication.translate("SavePanel", "Buchstabe*", None))

        # if QT_CONFIG(tooltip)
        self.comboGroup.setToolTip(
            QCoreApplication.translate(
                "SavePanel", "Auswahl der GP Praktikumsgruppe (Pflichtfeld)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.labelTeam.setText(QCoreApplication.translate("SavePanel", "Team-Bezeichnung", None))
        # if QT_CONFIG(tooltip)
        self.editTeam.setToolTip(
            QCoreApplication.translate(
                "SavePanel",
                "Bezeichnung des spezifischen Teams einer Gruppe zur Identifizierung",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.editTeam.setPlaceholderText(
            QCoreApplication.translate("SavePanel", "Bspw. TimStruppi", None)
        )
        self.labelSuffix.setText(QCoreApplication.translate("SavePanel", "Eigenes Suffix", None))
        # if QT_CONFIG(tooltip)
        self.editSuffix.setToolTip(
            QCoreApplication.translate(
                "SavePanel", "Ein benutzerdefiniertes Suffix mit maximal 20 Zeichen", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.labelFilename.setText(
            QCoreApplication.translate("SavePanel", "Aktueller Dateiname", None)
        )
        # if QT_CONFIG(tooltip)
        self.labelDropbox.setToolTip(
            QCoreApplication.translate(
                "SavePanel",
                "Die Dateien werden in einem speziell generierten Ordner abgelegt, welcher die Nutzung der GP-Dropbox f\u00fcr den automatischen Upload erleichtert.",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.labelDropbox.setText(
            QCoreApplication.translate(
                "SavePanel",
                '<a href="https://openbis.physik.tu-berlin.de/doku/students/gp/automatic_upload.html">GP-Dropbox</a>',
                None,
            )
        )
        # if QT_CONFIG(tooltip)
        self.buttonSave.setToolTip(
            QCoreApplication.translate("SavePanel", "Messung speichern (Dateidialog)", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonSave.setText(QCoreApplication.translate("SavePanel", "Speichern", None))

    # retranslateUi
