# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'acq_settings.ui'
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
    QAbstractSpinBox,
    QApplication,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
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
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setSpacing(30)
        self.verticalLayout.setObjectName("verticalLayout")
        self.detRot_box = QGroupBox(Dialog)
        self.detRot_box.setObjectName("detRot_box")
        self.formLayout = QFormLayout(self.detRot_box)
        self.formLayout.setObjectName("formLayout")
        self.label = QLabel(self.detRot_box)
        self.label.setObjectName("label")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label)

        self.det_averages = QSpinBox(self.detRot_box)
        self.det_averages.setObjectName("det_averages")
        sizePolicy1 = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(
            self.det_averages.sizePolicy().hasHeightForWidth()
        )
        self.det_averages.setSizePolicy(sizePolicy1)
        self.det_averages.setMinimum(2)
        self.det_averages.setStepType(QAbstractSpinBox.StepType.AdaptiveDecimalStepType)
        self.det_averages.setValue(2)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.det_averages)

        self.det_averageOn = QCheckBox(self.detRot_box)
        self.det_averageOn.setObjectName("det_averageOn")
        self.det_averageOn.setChecked(True)

        self.formLayout.setWidget(
            0, QFormLayout.ItemRole.SpanningRole, self.det_averageOn
        )

        self.verticalLayout.addWidget(self.detRot_box)

        self.sampRot_box = QGroupBox(Dialog)
        self.sampRot_box.setObjectName("sampRot_box")
        self.formLayout_2 = QFormLayout(self.sampRot_box)
        self.formLayout_2.setObjectName("formLayout_2")
        self.label_2 = QLabel(self.sampRot_box)
        self.label_2.setObjectName("label_2")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_2)

        self.samp_averages = QSpinBox(self.sampRot_box)
        self.samp_averages.setObjectName("samp_averages")
        sizePolicy1.setHeightForWidth(
            self.samp_averages.sizePolicy().hasHeightForWidth()
        )
        self.samp_averages.setSizePolicy(sizePolicy1)
        self.samp_averages.setMinimum(2)

        self.formLayout_2.setWidget(
            1, QFormLayout.ItemRole.FieldRole, self.samp_averages
        )

        self.samp_averageOn = QCheckBox(self.sampRot_box)
        self.samp_averageOn.setObjectName("samp_averageOn")
        self.samp_averageOn.setChecked(True)

        self.formLayout_2.setWidget(
            0, QFormLayout.ItemRole.SpanningRole, self.samp_averageOn
        )

        self.verticalLayout.addWidget(self.sampRot_box)

        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(
            QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok
        )

        self.verticalLayout.addWidget(self.buttonBox)

        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 1)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)

    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", "Dialog", None))
        self.detRot_box.setTitle(
            QCoreApplication.translate("Dialog", "Detektor-Rotationsstage", None)
        )
        self.label.setText(
            QCoreApplication.translate("Dialog", "Anzahl Mittelwerte", None)
        )
        self.det_averageOn.setText(
            QCoreApplication.translate("Dialog", "Mittelung aktiviert", None)
        )
        self.sampRot_box.setTitle(
            QCoreApplication.translate("Dialog", "Sample-Rotationsstage", None)
        )
        self.label_2.setText(
            QCoreApplication.translate("Dialog", "Anzahl Mittelwerte", None)
        )
        self.samp_averageOn.setText(
            QCoreApplication.translate("Dialog", "Mittelung aktiviert", None)
        )

    # retranslateUi
