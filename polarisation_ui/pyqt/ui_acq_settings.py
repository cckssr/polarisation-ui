# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'acq_settings.ui'
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
    QAbstractSpinBox,
    QApplication,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName("Dialog")
        Dialog.resize(433, 356)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setSpacing(30)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupDetRot = QGroupBox(Dialog)
        self.groupDetRot.setObjectName("groupDetRot")
        self.formLayout = QFormLayout(self.groupDetRot)
        self.formLayout.setObjectName("formLayout")
        self.labelDetAverages = QLabel(self.groupDetRot)
        self.labelDetAverages.setObjectName("labelDetAverages")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelDetAverages)

        self.spinDetAverages = QSpinBox(self.groupDetRot)
        self.spinDetAverages.setObjectName("spinDetAverages")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.spinDetAverages.sizePolicy().hasHeightForWidth())
        self.spinDetAverages.setSizePolicy(sizePolicy1)
        self.spinDetAverages.setMinimum(2)
        self.spinDetAverages.setStepType(QAbstractSpinBox.StepType.AdaptiveDecimalStepType)
        self.spinDetAverages.setValue(2)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spinDetAverages)

        self.checkDetAverage = QCheckBox(self.groupDetRot)
        self.checkDetAverage.setObjectName("checkDetAverage")
        self.checkDetAverage.setChecked(True)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.SpanningRole, self.checkDetAverage)

        self.verticalLayout.addWidget(self.groupDetRot)

        self.groupSampRot = QGroupBox(Dialog)
        self.groupSampRot.setObjectName("groupSampRot")
        self.formLayout_2 = QFormLayout(self.groupSampRot)
        self.formLayout_2.setObjectName("formLayout_2")
        self.labelSampAverages = QLabel(self.groupSampRot)
        self.labelSampAverages.setObjectName("labelSampAverages")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelSampAverages)

        self.spinSampAverages = QSpinBox(self.groupSampRot)
        self.spinSampAverages.setObjectName("spinSampAverages")
        sizePolicy1.setHeightForWidth(self.spinSampAverages.sizePolicy().hasHeightForWidth())
        self.spinSampAverages.setSizePolicy(sizePolicy1)
        self.spinSampAverages.setMinimum(2)

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spinSampAverages)

        self.checkSampAverage = QCheckBox(self.groupSampRot)
        self.checkSampAverage.setObjectName("checkSampAverage")
        self.checkSampAverage.setChecked(True)

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.SpanningRole, self.checkSampAverage)

        self.verticalLayout.addWidget(self.groupSampRot)

        self.groupSpikeFilter = QGroupBox(Dialog)
        self.groupSpikeFilter.setObjectName("groupSpikeFilter")
        self.formSpikeFilter = QFormLayout(self.groupSpikeFilter)
        self.formSpikeFilter.setObjectName("formSpikeFilter")
        self.checkSpikeFilter = QCheckBox(self.groupSpikeFilter)
        self.checkSpikeFilter.setObjectName("checkSpikeFilter")

        self.formSpikeFilter.setWidget(0, QFormLayout.ItemRole.SpanningRole, self.checkSpikeFilter)

        self.labelSpikeMaxDelta = QLabel(self.groupSpikeFilter)
        self.labelSpikeMaxDelta.setObjectName("labelSpikeMaxDelta")

        self.formSpikeFilter.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelSpikeMaxDelta)

        self.spinSpikeMaxDelta = QDoubleSpinBox(self.groupSpikeFilter)
        self.spinSpikeMaxDelta.setObjectName("spinSpikeMaxDelta")
        self.spinSpikeMaxDelta.setMinimum(1.000000000000000)
        self.spinSpikeMaxDelta.setMaximum(180.000000000000000)
        self.spinSpikeMaxDelta.setSingleStep(1.000000000000000)
        self.spinSpikeMaxDelta.setDecimals(1)

        self.formSpikeFilter.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spinSpikeMaxDelta)

        self.verticalLayout.addWidget(self.groupSpikeFilter)

        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(
            QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok
        )

        self.verticalLayout.addWidget(self.buttonBox)

        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 1)
        self.verticalLayout.setStretch(2, 1)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)

    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(
            QCoreApplication.translate("Dialog", "Akquisitions-Einstellungen", None)
        )
        self.groupDetRot.setTitle(
            QCoreApplication.translate("Dialog", "Detektor-Rotationsstage", None)
        )
        self.labelDetAverages.setText(
            QCoreApplication.translate("Dialog", "Anzahl Mittelwerte", None)
        )
        self.checkDetAverage.setText(
            QCoreApplication.translate("Dialog", "Mittelung aktiviert", None)
        )
        self.groupSampRot.setTitle(
            QCoreApplication.translate("Dialog", "Sample-Rotationsstage", None)
        )
        self.labelSampAverages.setText(
            QCoreApplication.translate("Dialog", "Anzahl Mittelwerte", None)
        )
        self.checkSampAverage.setText(
            QCoreApplication.translate("Dialog", "Mittelung aktiviert", None)
        )
        self.groupSpikeFilter.setTitle(QCoreApplication.translate("Dialog", "Spike-Filter", None))
        self.checkSpikeFilter.setText(
            QCoreApplication.translate("Dialog", "Spike-Filter aktivieren", None)
        )
        self.labelSpikeMaxDelta.setText(
            QCoreApplication.translate("Dialog", "Max. Winkelsprung", None)
        )
        # if QT_CONFIG(tooltip)
        self.spinSpikeMaxDelta.setToolTip(
            QCoreApplication.translate(
                "Dialog",
                "Maximale erlaubte Winkel\u00e4nderung pro Abtastung (100 ms). Messungen mit gr\u00f6\u00dferer \u00c4nderung werden verworfen.",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.spinSpikeMaxDelta.setSuffix(QCoreApplication.translate("Dialog", " \u00b0/Poll", None))

    # retranslateUi
