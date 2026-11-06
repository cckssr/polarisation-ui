# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'detector_panel.ui'
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
    QComboBox,
    QDoubleSpinBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from polarisation_ui.ui.widgets.elided_label import ElidedLabel


class Ui_DetectorPanel(object):
    def setupUi(self, DetectorPanel):
        if not DetectorPanel.objectName():
            DetectorPanel.setObjectName("DetectorPanel")
        self.verticalLayout = QVBoxLayout(DetectorPanel)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabDetector = QTabWidget(DetectorPanel)
        self.tabDetector.setObjectName("tabDetector")
        self.tabPdtia = QWidget()
        self.tabPdtia.setObjectName("tabPdtia")
        self.gridPdtia = QGridLayout(self.tabPdtia)
        self.gridPdtia.setObjectName("gridPdtia")
        self.gridPdtia.setHorizontalSpacing(6)
        self.gridPdtia.setVerticalSpacing(6)
        self.labelPdtiaStatus = QLabel(self.tabPdtia)
        self.labelPdtiaStatus.setObjectName("labelPdtiaStatus")

        self.gridPdtia.addWidget(self.labelPdtiaStatus, 0, 0, 1, 1)

        self.pdtiaStatusLayout = QHBoxLayout()
        self.pdtiaStatusLayout.setSpacing(6)
        self.pdtiaStatusLayout.setObjectName("pdtiaStatusLayout")
        self.valuePdtiaStatus = ElidedLabel(self.tabPdtia)
        self.valuePdtiaStatus.setObjectName("valuePdtiaStatus")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.valuePdtiaStatus.sizePolicy().hasHeightForWidth())
        self.valuePdtiaStatus.setSizePolicy(sizePolicy)

        self.pdtiaStatusLayout.addWidget(self.valuePdtiaStatus)

        self.ledPdtiaStatus = QLabel(self.tabPdtia)
        self.ledPdtiaStatus.setObjectName("ledPdtiaStatus")

        self.pdtiaStatusLayout.addWidget(self.ledPdtiaStatus)

        self.gridPdtia.addLayout(self.pdtiaStatusLayout, 0, 1, 1, 2)

        self.labelPdtiaId = QLabel(self.tabPdtia)
        self.labelPdtiaId.setObjectName("labelPdtiaId")

        self.gridPdtia.addWidget(self.labelPdtiaId, 1, 0, 1, 1)

        self.comboPdtiaId = QComboBox(self.tabPdtia)
        self.comboPdtiaId.setObjectName("comboPdtiaId")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.comboPdtiaId.sizePolicy().hasHeightForWidth())
        self.comboPdtiaId.setSizePolicy(sizePolicy1)
        self.comboPdtiaId.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
        )
        self.comboPdtiaId.setMinimumContentsLength(8)

        self.gridPdtia.addWidget(self.comboPdtiaId, 1, 1, 1, 2)

        self.labelProfile = QLabel(self.tabPdtia)
        self.labelProfile.setObjectName("labelProfile")

        self.gridPdtia.addWidget(self.labelProfile, 2, 0, 1, 1)

        self.comboProfile = QComboBox(self.tabPdtia)
        self.comboProfile.setObjectName("comboProfile")
        sizePolicy1.setHeightForWidth(self.comboProfile.sizePolicy().hasHeightForWidth())
        self.comboProfile.setSizePolicy(sizePolicy1)
        self.comboProfile.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
        )
        self.comboProfile.setMinimumContentsLength(8)

        self.gridPdtia.addWidget(self.comboProfile, 2, 1, 1, 1)

        self.buttonReloadProfiles = QPushButton(self.tabPdtia)
        self.buttonReloadProfiles.setObjectName("buttonReloadProfiles")

        self.gridPdtia.addWidget(self.buttonReloadProfiles, 2, 2, 1, 1)

        self.buttonOpenCalibration = QPushButton(self.tabPdtia)
        self.buttonOpenCalibration.setObjectName("buttonOpenCalibration")

        self.gridPdtia.addWidget(self.buttonOpenCalibration, 3, 0, 1, 3)

        self.pdtiaAverageLayout = QHBoxLayout()
        self.pdtiaAverageLayout.setObjectName("pdtiaAverageLayout")
        self.checkPdtiaAverage = QCheckBox(self.tabPdtia)
        self.checkPdtiaAverage.setObjectName("checkPdtiaAverage")

        self.pdtiaAverageLayout.addWidget(self.checkPdtiaAverage)

        self.spinPdtiaAverages = QSpinBox(self.tabPdtia)
        self.spinPdtiaAverages.setObjectName("spinPdtiaAverages")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.spinPdtiaAverages.sizePolicy().hasHeightForWidth())
        self.spinPdtiaAverages.setSizePolicy(sizePolicy2)
        self.spinPdtiaAverages.setMinimum(2)
        self.spinPdtiaAverages.setMaximum(100)
        self.spinPdtiaAverages.setValue(5)

        self.pdtiaAverageLayout.addWidget(self.spinPdtiaAverages)

        self.gridPdtia.addLayout(self.pdtiaAverageLayout, 4, 0, 1, 3)

        self.darkLayout = QHBoxLayout()
        self.darkLayout.setObjectName("darkLayout")
        self.buttonDarkTare = QPushButton(self.tabPdtia)
        self.buttonDarkTare.setObjectName("buttonDarkTare")

        self.darkLayout.addWidget(self.buttonDarkTare)

        self.buttonDarkReset = QPushButton(self.tabPdtia)
        self.buttonDarkReset.setObjectName("buttonDarkReset")

        self.darkLayout.addWidget(self.buttonDarkReset)

        self.gridPdtia.addLayout(self.darkLayout, 5, 0, 1, 3)

        self.valueDarkOffset = ElidedLabel(self.tabPdtia)
        self.valueDarkOffset.setObjectName("valueDarkOffset")
        sizePolicy.setHeightForWidth(self.valueDarkOffset.sizePolicy().hasHeightForWidth())
        self.valueDarkOffset.setSizePolicy(sizePolicy)

        self.gridPdtia.addWidget(self.valueDarkOffset, 6, 0, 1, 3)

        self.gridPdtia.setColumnStretch(1, 1)
        self.tabDetector.addTab(self.tabPdtia, "")
        self.tabPm400 = QWidget()
        self.tabPm400.setObjectName("tabPm400")
        self.gridPm400 = QGridLayout(self.tabPm400)
        self.gridPm400.setObjectName("gridPm400")
        self.gridPm400.setHorizontalSpacing(6)
        self.gridPm400.setVerticalSpacing(6)
        self.labelPm400Status = QLabel(self.tabPm400)
        self.labelPm400Status.setObjectName("labelPm400Status")

        self.gridPm400.addWidget(self.labelPm400Status, 0, 0, 1, 1)

        self.pm400StatusLayout = QHBoxLayout()
        self.pm400StatusLayout.setSpacing(6)
        self.pm400StatusLayout.setObjectName("pm400StatusLayout")
        self.valuePm400Status = ElidedLabel(self.tabPm400)
        self.valuePm400Status.setObjectName("valuePm400Status")
        sizePolicy.setHeightForWidth(self.valuePm400Status.sizePolicy().hasHeightForWidth())
        self.valuePm400Status.setSizePolicy(sizePolicy)

        self.pm400StatusLayout.addWidget(self.valuePm400Status)

        self.ledPm400Status = QLabel(self.tabPm400)
        self.ledPm400Status.setObjectName("ledPm400Status")

        self.pm400StatusLayout.addWidget(self.ledPm400Status)

        self.gridPm400.addLayout(self.pm400StatusLayout, 0, 1, 1, 2)

        self.labelResource = QLabel(self.tabPm400)
        self.labelResource.setObjectName("labelResource")

        self.gridPm400.addWidget(self.labelResource, 1, 0, 1, 1)

        self.comboPm400Resource = QComboBox(self.tabPm400)
        self.comboPm400Resource.setObjectName("comboPm400Resource")
        sizePolicy1.setHeightForWidth(self.comboPm400Resource.sizePolicy().hasHeightForWidth())
        self.comboPm400Resource.setSizePolicy(sizePolicy1)
        self.comboPm400Resource.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
        )
        self.comboPm400Resource.setMinimumContentsLength(8)

        self.gridPm400.addWidget(self.comboPm400Resource, 1, 1, 1, 1)

        self.buttonPm400Refresh = QPushButton(self.tabPm400)
        self.buttonPm400Refresh.setObjectName("buttonPm400Refresh")

        self.gridPm400.addWidget(self.buttonPm400Refresh, 1, 2, 1, 1)

        self.labelWavelength = QLabel(self.tabPm400)
        self.labelWavelength.setObjectName("labelWavelength")

        self.gridPm400.addWidget(self.labelWavelength, 2, 0, 1, 1)

        self.spinWavelength = QDoubleSpinBox(self.tabPm400)
        self.spinWavelength.setObjectName("spinWavelength")
        self.spinWavelength.setDecimals(1)
        self.spinWavelength.setMinimum(200.000000000000000)
        self.spinWavelength.setMaximum(2000.000000000000000)
        self.spinWavelength.setValue(633.000000000000000)

        self.gridPm400.addWidget(self.spinWavelength, 2, 1, 1, 2)

        self.pm400ButtonLayout = QHBoxLayout()
        self.pm400ButtonLayout.setObjectName("pm400ButtonLayout")
        self.buttonPm400Connect = QPushButton(self.tabPm400)
        self.buttonPm400Connect.setObjectName("buttonPm400Connect")

        self.pm400ButtonLayout.addWidget(self.buttonPm400Connect)

        self.buttonPm400Zero = QPushButton(self.tabPm400)
        self.buttonPm400Zero.setObjectName("buttonPm400Zero")

        self.pm400ButtonLayout.addWidget(self.buttonPm400Zero)

        self.gridPm400.addLayout(self.pm400ButtonLayout, 3, 0, 1, 3)

        self.gridPm400.setColumnStretch(1, 1)
        self.tabDetector.addTab(self.tabPm400, "")

        self.verticalLayout.addWidget(self.tabDetector)

        self.retranslateUi(DetectorPanel)

        self.tabDetector.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(DetectorPanel)

    # setupUi

    def retranslateUi(self, DetectorPanel):
        DetectorPanel.setTitle(QCoreApplication.translate("DetectorPanel", "Detektor", None))
        self.labelPdtiaStatus.setText(QCoreApplication.translate("DetectorPanel", "Status", None))
        self.ledPdtiaStatus.setStyleSheet(
            QCoreApplication.translate(
                "DetectorPanel",
                "background-color: rgb(255, 11, 3); border: 0px; padding: 4px; border-radius: 10px",
                None,
            )
        )
        self.labelPdtiaId.setText(
            QCoreApplication.translate("DetectorPanel", "Photodetektor", None)
        )
        # if QT_CONFIG(tooltip)
        self.comboPdtiaId.setToolTip(
            QCoreApplication.translate(
                "DetectorPanel", "Photodetektor (PD-TIA-Ger\u00e4t) ausw\u00e4hlen", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.comboPdtiaId.setPlaceholderText(
            QCoreApplication.translate(
                "DetectorPanel", "\u2014 Kein Photodetektor ausgew\u00e4hlt! \u2014", None
            )
        )
        self.labelProfile.setText(QCoreApplication.translate("DetectorPanel", "Kalibrierung", None))
        # if QT_CONFIG(tooltip)
        self.comboProfile.setToolTip(
            QCoreApplication.translate(
                "DetectorPanel",
                "Leistungskalibrierungsprofil ausw\u00e4hlen (optional \u2014 schaltet \u00b5W-Anzeige frei)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.comboProfile.setPlaceholderText(
            QCoreApplication.translate("DetectorPanel", "\u2014 Kein Profil geladen \u2014", None)
        )
        self.buttonReloadProfiles.setText(
            QCoreApplication.translate("DetectorPanel", "Aktualisieren", None)
        )
        # if QT_CONFIG(tooltip)
        self.buttonReloadProfiles.setToolTip(
            QCoreApplication.translate(
                "DetectorPanel", "Profil-Liste aus dem Verzeichnis neu einlesen", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonOpenCalibration.setText(
            QCoreApplication.translate("DetectorPanel", "Kalibrierungstool\u2026", None)
        )
        # if QT_CONFIG(tooltip)
        self.buttonOpenCalibration.setToolTip(
            QCoreApplication.translate(
                "DetectorPanel", "Leistungskalibrierungstool \u00f6ffnen", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.checkPdtiaAverage.setText(
            QCoreApplication.translate("DetectorPanel", "Mittelung aktivieren", None)
        )
        # if QT_CONFIG(tooltip)
        self.checkPdtiaAverage.setToolTip(
            QCoreApplication.translate(
                "DetectorPanel",
                "Aktiviert die kontinuierliche Mittelung der PD-TIA-Spannungswerte",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(tooltip)
        self.spinPdtiaAverages.setToolTip(
            QCoreApplication.translate(
                "DetectorPanel",
                "Anzahl der Messwerte f\u00fcr die gleitende Mittelung (2\u2013100)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.spinPdtiaAverages.setSuffix(
            QCoreApplication.translate("DetectorPanel", " Werte", None)
        )
        self.buttonDarkTare.setText(
            QCoreApplication.translate("DetectorPanel", "Dunkelstrom nullen", None)
        )
        # if QT_CONFIG(tooltip)
        self.buttonDarkTare.setToolTip(
            QCoreApplication.translate(
                "DetectorPanel",
                "Detektor vollst\u00e4ndig abdecken, dann Dunkelstrom-Offset \u00fcber 2 s messen",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonDarkReset.setText(
            QCoreApplication.translate("DetectorPanel", "Offset zur\u00fccksetzen", None)
        )
        # if QT_CONFIG(tooltip)
        self.buttonDarkReset.setToolTip(
            QCoreApplication.translate(
                "DetectorPanel", "Dunkelstrom-Offset auf 0 zur\u00fccksetzen", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(tooltip)
        self.valueDarkOffset.setToolTip(
            QCoreApplication.translate(
                "DetectorPanel", "Aktuell abgezogener Dunkelstrom-Offset in Millivolt", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.tabDetector.setTabText(
            self.tabDetector.indexOf(self.tabPdtia),
            QCoreApplication.translate("DetectorPanel", "PD-TIA", None),
        )
        self.labelPm400Status.setText(QCoreApplication.translate("DetectorPanel", "Status", None))
        self.ledPm400Status.setStyleSheet(
            QCoreApplication.translate(
                "DetectorPanel",
                "background-color: rgb(255, 11, 3); border: 0px; padding: 4px; border-radius: 10px",
                None,
            )
        )
        self.labelResource.setText(
            QCoreApplication.translate("DetectorPanel", "VISA-Adresse", None)
        )
        # if QT_CONFIG(tooltip)
        self.comboPm400Resource.setToolTip(
            QCoreApplication.translate(
                "DetectorPanel",
                "Automatisch erkannte USB/VISA-Ressourcen des PM400 (Aktualisieren zum erneuten Suchen)",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonPm400Refresh.setText(
            QCoreApplication.translate("DetectorPanel", "Aktualisieren", None)
        )
        # if QT_CONFIG(tooltip)
        self.buttonPm400Refresh.setToolTip(
            QCoreApplication.translate("DetectorPanel", "VISA-Ressourcenliste neu einlesen", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.labelWavelength.setText(
            QCoreApplication.translate("DetectorPanel", "Wellenl\u00e4nge", None)
        )
        # if QT_CONFIG(tooltip)
        self.spinWavelength.setToolTip(
            QCoreApplication.translate(
                "DetectorPanel",
                "Betriebswellenl\u00e4nge f\u00fcr die spektrale Empfindlichkeitskorrektur des PM400",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.spinWavelength.setSuffix(QCoreApplication.translate("DetectorPanel", " nm", None))
        self.buttonPm400Connect.setText(
            QCoreApplication.translate("DetectorPanel", "Verbinden", None)
        )
        # if QT_CONFIG(tooltip)
        self.buttonPm400Connect.setToolTip(
            QCoreApplication.translate("DetectorPanel", "PM400 verbinden oder trennen", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonPm400Zero.setText(
            QCoreApplication.translate("DetectorPanel", "Nullabgleich (Zero)", None)
        )
        # if QT_CONFIG(tooltip)
        self.buttonPm400Zero.setToolTip(
            QCoreApplication.translate(
                "DetectorPanel", "Dunkelstrom-Nullabgleich des PM400 starten", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.tabDetector.setTabText(
            self.tabDetector.indexOf(self.tabPm400),
            QCoreApplication.translate("DetectorPanel", "PM400", None),
        )

    # retranslateUi
