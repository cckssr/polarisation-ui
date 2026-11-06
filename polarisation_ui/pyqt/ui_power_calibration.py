# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'power_calibration.ui'
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
    QAbstractButton,
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


class Ui_PowerCalibrationWindow(object):
    def setupUi(self, PowerCalibrationWindow):
        if not PowerCalibrationWindow.objectName():
            PowerCalibrationWindow.setObjectName("PowerCalibrationWindow")
        PowerCalibrationWindow.resize(700, 700)
        self.layoutDialog = QVBoxLayout(PowerCalibrationWindow)
        self.layoutDialog.setSpacing(0)
        self.layoutDialog.setObjectName("layoutDialog")
        self.layoutDialog.setContentsMargins(0, 0, 0, 0)
        self.scrollMain = QScrollArea(PowerCalibrationWindow)
        self.scrollMain.setObjectName("scrollMain")
        self.scrollMain.setFrameShape(QFrame.Shape.NoFrame)
        self.scrollMain.setWidgetResizable(True)
        self.contentMain = QWidget()
        self.contentMain.setObjectName("contentMain")
        self.contentMain.setGeometry(QRect(0, 0, 700, 660))
        self.layoutContent = QVBoxLayout(self.contentMain)
        self.layoutContent.setSpacing(8)
        self.layoutContent.setObjectName("layoutContent")
        self.layoutContent.setContentsMargins(10, 10, 10, 10)
        self.tabGains = QTabWidget(self.contentMain)
        self.tabGains.setObjectName("tabGains")

        self.layoutContent.addWidget(self.tabGains)

        self.groupProfile = QGroupBox(self.contentMain)
        self.groupProfile.setObjectName("groupProfile")
        self.layoutProfile = QFormLayout(self.groupProfile)
        self.layoutProfile.setObjectName("layoutProfile")
        self.layoutProfile.setVerticalSpacing(4)
        self.layoutProfile.setContentsMargins(8, 6, 8, 6)
        self.labelProfileName = QLabel(self.groupProfile)
        self.labelProfileName.setObjectName("labelProfileName")

        self.layoutProfile.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelProfileName)

        self.editProfileName = QLineEdit(self.groupProfile)
        self.editProfileName.setObjectName("editProfileName")

        self.layoutProfile.setWidget(0, QFormLayout.ItemRole.FieldRole, self.editProfileName)

        self.labelWavelength = QLabel(self.groupProfile)
        self.labelWavelength.setObjectName("labelWavelength")

        self.layoutProfile.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelWavelength)

        self.spinWavelength = QDoubleSpinBox(self.groupProfile)
        self.spinWavelength.setObjectName("spinWavelength")
        self.spinWavelength.setDecimals(1)
        self.spinWavelength.setMinimum(1.000000000000000)
        self.spinWavelength.setMaximum(10000.000000000000000)
        self.spinWavelength.setValue(633.000000000000000)

        self.layoutProfile.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spinWavelength)

        self.layoutProfileButtons = QHBoxLayout()
        self.layoutProfileButtons.setObjectName("layoutProfileButtons")
        self.buttonSave = QPushButton(self.groupProfile)
        self.buttonSave.setObjectName("buttonSave")

        self.layoutProfileButtons.addWidget(self.buttonSave)

        self.buttonLoad = QPushButton(self.groupProfile)
        self.buttonLoad.setObjectName("buttonLoad")

        self.layoutProfileButtons.addWidget(self.buttonLoad)

        self.layoutProfile.setLayout(
            2, QFormLayout.ItemRole.SpanningRole, self.layoutProfileButtons
        )

        self.layoutContent.addWidget(self.groupProfile)

        self.groupPm400 = QGroupBox(self.contentMain)
        self.groupPm400.setObjectName("groupPm400")
        self.layoutPm400 = QFormLayout(self.groupPm400)
        self.layoutPm400.setObjectName("layoutPm400")
        self.layoutPm400.setVerticalSpacing(4)
        self.layoutPm400.setContentsMargins(8, 6, 8, 6)
        self.labelResource = QLabel(self.groupPm400)
        self.labelResource.setObjectName("labelResource")

        self.layoutPm400.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelResource)

        self.layoutConnection = QHBoxLayout()
        self.layoutConnection.setObjectName("layoutConnection")
        self.comboPm400 = QComboBox(self.groupPm400)
        self.comboPm400.setObjectName("comboPm400")

        self.layoutConnection.addWidget(self.comboPm400)

        self.buttonRefresh = QPushButton(self.groupPm400)
        self.buttonRefresh.setObjectName("buttonRefresh")

        self.layoutConnection.addWidget(self.buttonRefresh)

        self.buttonConnect = QPushButton(self.groupPm400)
        self.buttonConnect.setObjectName("buttonConnect")

        self.layoutConnection.addWidget(self.buttonConnect)

        self.layoutConnection.setStretch(0, 1)

        self.layoutPm400.setLayout(0, QFormLayout.ItemRole.FieldRole, self.layoutConnection)

        self.valuePm400Status = QLabel(self.groupPm400)
        self.valuePm400Status.setObjectName("valuePm400Status")
        self.valuePm400Status.setText("\u2014")

        self.layoutPm400.setWidget(1, QFormLayout.ItemRole.SpanningRole, self.valuePm400Status)

        self.labelAttenuation = QLabel(self.groupPm400)
        self.labelAttenuation.setObjectName("labelAttenuation")

        self.layoutPm400.setWidget(2, QFormLayout.ItemRole.LabelRole, self.labelAttenuation)

        self.layoutAttenuation = QHBoxLayout()
        self.layoutAttenuation.setObjectName("layoutAttenuation")
        self.spinAttenuation = QDoubleSpinBox(self.groupPm400)
        self.spinAttenuation.setObjectName("spinAttenuation")
        self.spinAttenuation.setDecimals(2)
        self.spinAttenuation.setMaximum(60.000000000000000)

        self.layoutAttenuation.addWidget(self.spinAttenuation)

        self.buttonToggleAttenuation = QPushButton(self.groupPm400)
        self.buttonToggleAttenuation.setObjectName("buttonToggleAttenuation")
        self.buttonToggleAttenuation.setEnabled(False)

        self.layoutAttenuation.addWidget(self.buttonToggleAttenuation)

        self.layoutPm400.setLayout(2, QFormLayout.ItemRole.FieldRole, self.layoutAttenuation)

        self.layoutContent.addWidget(self.groupPm400)

        self.groupLive = QGroupBox(self.contentMain)
        self.groupLive.setObjectName("groupLive")
        self.layoutLive = QFormLayout(self.groupLive)
        self.layoutLive.setObjectName("layoutLive")
        self.layoutLive.setVerticalSpacing(4)
        self.layoutLive.setContentsMargins(8, 6, 8, 6)
        self.labelDetectorVoltage = QLabel(self.groupLive)
        self.labelDetectorVoltage.setObjectName("labelDetectorVoltage")

        self.layoutLive.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelDetectorVoltage)

        self.valueDetectorVoltage = QLabel(self.groupLive)
        self.valueDetectorVoltage.setObjectName("valueDetectorVoltage")
        self.valueDetectorVoltage.setText("\u2014")

        self.layoutLive.setWidget(0, QFormLayout.ItemRole.FieldRole, self.valueDetectorVoltage)

        self.labelPm400Power = QLabel(self.groupLive)
        self.labelPm400Power.setObjectName("labelPm400Power")

        self.layoutLive.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelPm400Power)

        self.valuePm400Power = QLabel(self.groupLive)
        self.valuePm400Power.setObjectName("valuePm400Power")
        self.valuePm400Power.setText("\u2014")

        self.layoutLive.setWidget(1, QFormLayout.ItemRole.FieldRole, self.valuePm400Power)

        self.layoutContent.addWidget(self.groupLive)

        self.layoutContent.setStretch(0, 1)
        self.scrollMain.setWidget(self.contentMain)

        self.layoutDialog.addWidget(self.scrollMain)

        self.buttonBox = QDialogButtonBox(PowerCalibrationWindow)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Close)

        self.layoutDialog.addWidget(self.buttonBox)

        self.layoutDialog.setStretch(0, 1)

        self.retranslateUi(PowerCalibrationWindow)
        self.buttonBox.rejected.connect(PowerCalibrationWindow.close)

        self.tabGains.setCurrentIndex(-1)

        QMetaObject.connectSlotsByName(PowerCalibrationWindow)

    # setupUi

    def retranslateUi(self, PowerCalibrationWindow):
        PowerCalibrationWindow.setWindowTitle(
            QCoreApplication.translate(
                "PowerCalibrationWindow", "Leistungskalibrierung \u2014 PD-TIA Detektor", None
            )
        )
        self.groupProfile.setTitle(
            QCoreApplication.translate("PowerCalibrationWindow", "Profil", None)
        )
        self.labelProfileName.setText(
            QCoreApplication.translate("PowerCalibrationWindow", "Profilname:", None)
        )
        self.editProfileName.setPlaceholderText(
            QCoreApplication.translate("PowerCalibrationWindow", "z.B. Det-A", None)
        )
        self.labelWavelength.setText(
            QCoreApplication.translate("PowerCalibrationWindow", "Wellenl\u00e4nge:", None)
        )
        # if QT_CONFIG(tooltip)
        self.spinWavelength.setToolTip(
            QCoreApplication.translate(
                "PowerCalibrationWindow",
                "Laserwellenl\u00e4nge \u2014 die Responsivit\u00e4t des Detektors ist wellenl\u00e4ngenabh\u00e4ngig.",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.spinWavelength.setSuffix(
            QCoreApplication.translate("PowerCalibrationWindow", " nm", None)
        )
        self.buttonSave.setText(
            QCoreApplication.translate("PowerCalibrationWindow", "Kalibrierung speichern", None)
        )
        self.buttonLoad.setText(
            QCoreApplication.translate("PowerCalibrationWindow", "Kalibrierung laden\u2026", None)
        )
        self.groupPm400.setTitle(
            QCoreApplication.translate("PowerCalibrationWindow", "PM400 Leistungsmesser", None)
        )
        self.labelResource.setText(
            QCoreApplication.translate("PowerCalibrationWindow", "VISA-Ressource:", None)
        )
        self.buttonRefresh.setText(
            QCoreApplication.translate("PowerCalibrationWindow", "Aktualisieren", None)
        )
        self.buttonConnect.setText(
            QCoreApplication.translate("PowerCalibrationWindow", "Verbinden", None)
        )
        self.labelAttenuation.setText(
            QCoreApplication.translate("PowerCalibrationWindow", "Abschw\u00e4chung:", None)
        )
        self.spinAttenuation.setSuffix(
            QCoreApplication.translate("PowerCalibrationWindow", " dB", None)
        )
        # if QT_CONFIG(tooltip)
        self.buttonToggleAttenuation.setToolTip(
            QCoreApplication.translate(
                "PowerCalibrationWindow",
                "Setzt die PM400-Abschw\u00e4chung auf den nebenstehenden Wert, bzw. schaltet sie aus, falls bereits aktiv.",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonToggleAttenuation.setText(
            QCoreApplication.translate("PowerCalibrationWindow", "Abschw\u00e4chung setzen", None)
        )
        self.groupLive.setTitle(
            QCoreApplication.translate("PowerCalibrationWindow", "Live-Werte", None)
        )
        self.labelDetectorVoltage.setText(
            QCoreApplication.translate("PowerCalibrationWindow", "Detektorspannung:", None)
        )
        self.labelPm400Power.setText(
            QCoreApplication.translate("PowerCalibrationWindow", "PM400-Leistung:", None)
        )

    # retranslateUi
