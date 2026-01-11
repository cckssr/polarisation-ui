# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFormLayout,
    QFrame, QGridLayout, QGroupBox, QHBoxLayout,
    QLCDNumber, QLabel, QLayout, QLineEdit,
    QMainWindow, QMenuBar, QPushButton, QSizePolicy,
    QSpacerItem, QStatusBar, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1144, 750)
        MainWindow.setMinimumSize(QSize(0, 750))
        font = QFont()
        font.setPointSize(13)
        MainWindow.setFont(font)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout_5 = QGridLayout(self.centralwidget)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.gridLayout_5.setContentsMargins(10, 0, 10, 10)
        self.line = QFrame(self.centralwidget)
        self.line.setObjectName(u"line")
        font1 = QFont()
        font1.setPointSize(11)
        self.line.setFont(font1)
        self.line.setFrameShadow(QFrame.Shadow.Plain)
        self.line.setFrameShape(QFrame.Shape.VLine)

        self.gridLayout_5.addWidget(self.line, 0, 1, 1, 1)

        self.verticalLayout_2 = QVBoxLayout()
#ifndef Q_OS_MAC
        self.verticalLayout_2.setSpacing(-1)
#endif
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.verticalLayout_2.setContentsMargins(0, -1, -1, 0)
        self.live_values = QGroupBox(self.centralwidget)
        self.live_values.setObjectName(u"live_values")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.live_values.sizePolicy().hasHeightForWidth())
        self.live_values.setSizePolicy(sizePolicy)
        self.live_values.setMinimumSize(QSize(0, 50))
        font2 = QFont()
        font2.setPointSize(15)
        self.live_values.setFont(font2)
        self.live_values.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.live_values.setCheckable(False)
        self.formLayout = QFormLayout(self.live_values)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        self.formLayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.formLayout.setLabelAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.formLayout.setHorizontalSpacing(-1)
        self.formLayout.setVerticalSpacing(8)
        self.label_4 = QLabel(self.live_values)
        self.label_4.setObjectName(u"label_4")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy1)
        self.label_4.setFont(font)
        self.label_4.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_4)

        self.sample_group = QHBoxLayout()
        self.sample_group.setObjectName(u"sample_group")
        self.sample_enr = QLabel(self.live_values)
        self.sample_enr.setObjectName(u"sample_enr")
        sizePolicy.setHeightForWidth(self.sample_enr.sizePolicy().hasHeightForWidth())
        self.sample_enr.setSizePolicy(sizePolicy)
        self.sample_enr.setFont(font)
        self.sample_enr.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.sample_group.addWidget(self.sample_enr)

        self.sample_statusLED = QLabel(self.live_values)
        self.sample_statusLED.setObjectName(u"sample_statusLED")
        self.sample_statusLED.setMinimumSize(QSize(20, 20))
        self.sample_statusLED.setMaximumSize(QSize(20, 20))
        self.sample_statusLED.setStyleSheet(u"background-color: rgb(255, 11, 3); border: 0px; padding: 4px; border-radius: 10px")

        self.sample_group.addWidget(self.sample_statusLED)


        self.formLayout.setLayout(0, QFormLayout.ItemRole.FieldRole, self.sample_group)

        self.label = QLabel(self.live_values)
        self.label.setObjectName(u"label")
        self.label.setFont(font)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label)

        self.sample_angle = QLCDNumber(self.live_values)
        self.sample_angle.setObjectName(u"sample_angle")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.sample_angle.sizePolicy().hasHeightForWidth())
        self.sample_angle.setSizePolicy(sizePolicy2)
        self.sample_angle.setFont(font)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.sample_angle)

        self.sample_zero = QPushButton(self.live_values)
        self.sample_zero.setObjectName(u"sample_zero")
        self.sample_zero.setFont(font)

        self.formLayout.setWidget(2, QFormLayout.ItemRole.SpanningRole, self.sample_zero)


        self.verticalLayout_2.addWidget(self.live_values)

        self.verticalSpacer_3 = QSpacerItem(20, 15, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout_2.addItem(self.verticalSpacer_3)

        self.live_values_2 = QGroupBox(self.centralwidget)
        self.live_values_2.setObjectName(u"live_values_2")
        sizePolicy.setHeightForWidth(self.live_values_2.sizePolicy().hasHeightForWidth())
        self.live_values_2.setSizePolicy(sizePolicy)
        self.live_values_2.setMinimumSize(QSize(0, 50))
        self.live_values_2.setFont(font2)
        self.live_values_2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.formLayout_3 = QFormLayout(self.live_values_2)
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.formLayout_3.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        self.formLayout_3.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.formLayout_3.setLabelAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.formLayout_3.setHorizontalSpacing(-1)
        self.formLayout_3.setVerticalSpacing(8)
        self.label_14 = QLabel(self.live_values_2)
        self.label_14.setObjectName(u"label_14")
        sizePolicy.setHeightForWidth(self.label_14.sizePolicy().hasHeightForWidth())
        self.label_14.setSizePolicy(sizePolicy)
        self.label_14.setFont(font)
        self.label_14.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.formLayout_3.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_14)

        self.dstage_group = QHBoxLayout()
        self.dstage_group.setObjectName(u"dstage_group")
        self.dstage_enr = QLabel(self.live_values_2)
        self.dstage_enr.setObjectName(u"dstage_enr")
        sizePolicy.setHeightForWidth(self.dstage_enr.sizePolicy().hasHeightForWidth())
        self.dstage_enr.setSizePolicy(sizePolicy)
        self.dstage_enr.setFont(font)
        self.dstage_enr.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.dstage_group.addWidget(self.dstage_enr)

        self.dstage_statusLED = QLabel(self.live_values_2)
        self.dstage_statusLED.setObjectName(u"dstage_statusLED")
        self.dstage_statusLED.setMinimumSize(QSize(20, 20))
        self.dstage_statusLED.setMaximumSize(QSize(20, 20))
        self.dstage_statusLED.setStyleSheet(u"background-color: rgb(255, 11, 3); border: 0px; padding: 4px; border-radius: 10px")

        self.dstage_group.addWidget(self.dstage_statusLED)


        self.formLayout_3.setLayout(0, QFormLayout.ItemRole.FieldRole, self.dstage_group)

        self.label_11 = QLabel(self.live_values_2)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setFont(font)

        self.formLayout_3.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_11)

        self.dstage_angle = QLCDNumber(self.live_values_2)
        self.dstage_angle.setObjectName(u"dstage_angle")
        sizePolicy2.setHeightForWidth(self.dstage_angle.sizePolicy().hasHeightForWidth())
        self.dstage_angle.setSizePolicy(sizePolicy2)
        self.dstage_angle.setFont(font)

        self.formLayout_3.setWidget(1, QFormLayout.ItemRole.FieldRole, self.dstage_angle)

        self.dstage_zero_2 = QPushButton(self.live_values_2)
        self.dstage_zero_2.setObjectName(u"dstage_zero_2")
        self.dstage_zero_2.setFont(font)

        self.formLayout_3.setWidget(2, QFormLayout.ItemRole.SpanningRole, self.dstage_zero_2)


        self.verticalLayout_2.addWidget(self.live_values_2)

        self.verticalSpacer_2 = QSpacerItem(20, 15, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout_2.addItem(self.verticalSpacer_2)

        self.live_values_3 = QGroupBox(self.centralwidget)
        self.live_values_3.setObjectName(u"live_values_3")
        sizePolicy.setHeightForWidth(self.live_values_3.sizePolicy().hasHeightForWidth())
        self.live_values_3.setSizePolicy(sizePolicy)
        self.live_values_3.setMinimumSize(QSize(0, 50))
        self.live_values_3.setFont(font2)
        self.live_values_3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.formLayout_4 = QFormLayout(self.live_values_3)
        self.formLayout_4.setObjectName(u"formLayout_4")
        self.formLayout_4.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        self.formLayout_4.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.formLayout_4.setLabelAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.formLayout_4.setHorizontalSpacing(-1)
        self.formLayout_4.setVerticalSpacing(8)
        self.label_18 = QLabel(self.live_values_3)
        self.label_18.setObjectName(u"label_18")
        sizePolicy1.setHeightForWidth(self.label_18.sizePolicy().hasHeightForWidth())
        self.label_18.setSizePolicy(sizePolicy1)
        self.label_18.setFont(font)
        self.label_18.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.formLayout_4.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_18)

        self.detector_group = QHBoxLayout()
        self.detector_group.setObjectName(u"detector_group")
        self.detector_enr = QLabel(self.live_values_3)
        self.detector_enr.setObjectName(u"detector_enr")
        sizePolicy.setHeightForWidth(self.detector_enr.sizePolicy().hasHeightForWidth())
        self.detector_enr.setSizePolicy(sizePolicy)
        self.detector_enr.setFont(font)
        self.detector_enr.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.detector_group.addWidget(self.detector_enr)

        self.detector_statusLED = QLabel(self.live_values_3)
        self.detector_statusLED.setObjectName(u"detector_statusLED")
        self.detector_statusLED.setMinimumSize(QSize(20, 20))
        self.detector_statusLED.setMaximumSize(QSize(20, 20))
        self.detector_statusLED.setStyleSheet(u"background-color: rgb(255, 11, 3); border: 0px; padding: 4px; border-radius: 10px")

        self.detector_group.addWidget(self.detector_statusLED)


        self.formLayout_4.setLayout(0, QFormLayout.ItemRole.FieldRole, self.detector_group)

        self.label_19 = QLabel(self.live_values_3)
        self.label_19.setObjectName(u"label_19")
        self.label_19.setFont(font)
        self.label_19.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.formLayout_4.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_19)

        self.detector_voltage = QLCDNumber(self.live_values_3)
        self.detector_voltage.setObjectName(u"detector_voltage")
        sizePolicy2.setHeightForWidth(self.detector_voltage.sizePolicy().hasHeightForWidth())
        self.detector_voltage.setSizePolicy(sizePolicy2)
        self.detector_voltage.setFont(font)

        self.formLayout_4.setWidget(1, QFormLayout.ItemRole.FieldRole, self.detector_voltage)


        self.verticalLayout_2.addWidget(self.live_values_3)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy3)
        self.groupBox.setMinimumSize(QSize(0, 50))
        self.groupBox.setFont(font2)
        self.groupBox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.groupBox.setFlat(False)
        self.groupBox.setCheckable(False)
        self.verticalLayout = QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.formLayout_2 = QFormLayout()
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.formLayout_2.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.formLayout_2.setContentsMargins(-1, -1, 0, 0)
        self.label_7 = QLabel(self.groupBox)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setFont(font)

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_7)

        self.groupLetter = QComboBox(self.groupBox)
        self.groupLetter.addItem("")
        self.groupLetter.addItem("")
        self.groupLetter.addItem("")
        self.groupLetter.addItem("")
        self.groupLetter.addItem("")
        self.groupLetter.addItem("")
        self.groupLetter.addItem("")
        self.groupLetter.addItem("")
        self.groupLetter.addItem("")
        self.groupLetter.addItem("")
        self.groupLetter.addItem("")
        self.groupLetter.addItem("")
        self.groupLetter.addItem("")
        self.groupLetter.addItem("")
        self.groupLetter.addItem("")
        self.groupLetter.addItem("")
        self.groupLetter.addItem("")
        self.groupLetter.addItem("")
        self.groupLetter.addItem("")
        self.groupLetter.addItem("")
        self.groupLetter.addItem("")
        self.groupLetter.addItem("")
        self.groupLetter.addItem("")
        self.groupLetter.addItem("")
        self.groupLetter.setObjectName(u"groupLetter")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.groupLetter.sizePolicy().hasHeightForWidth())
        self.groupLetter.setSizePolicy(sizePolicy4)
        self.groupLetter.setFont(font)
        self.groupLetter.setMaxCount(24)
        self.groupLetter.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.FieldRole, self.groupLetter)

        self.label_5 = QLabel(self.groupBox)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setFont(font)

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_5)

        self.suffix = QLineEdit(self.groupBox)
        self.suffix.setObjectName(u"suffix")
        sizePolicy4.setHeightForWidth(self.suffix.sizePolicy().hasHeightForWidth())
        self.suffix.setSizePolicy(sizePolicy4)
        self.suffix.setFont(font)
        self.suffix.setText(u"")
        self.suffix.setMaxLength(20)

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.FieldRole, self.suffix)


        self.verticalLayout.addLayout(self.formLayout_2)

        self.buttonSave = QPushButton(self.groupBox)
        self.buttonSave.setObjectName(u"buttonSave")
        self.buttonSave.setEnabled(False)
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.buttonSave.sizePolicy().hasHeightForWidth())
        self.buttonSave.setSizePolicy(sizePolicy5)
        self.buttonSave.setMinimumSize(QSize(100, 30))
        self.buttonSave.setMaximumSize(QSize(1000, 40))
        self.buttonSave.setFont(font)

        self.verticalLayout.addWidget(self.buttonSave)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(-1, -1, 0, 0)
        self.autoSave = QCheckBox(self.groupBox)
        self.autoSave.setObjectName(u"autoSave")
        sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.autoSave.sizePolicy().hasHeightForWidth())
        self.autoSave.setSizePolicy(sizePolicy6)
        self.autoSave.setMaximumSize(QSize(850, 16777215))
        self.autoSave.setFont(font)
        self.autoSave.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.autoSave.setChecked(True)
        self.autoSave.setTristate(False)

        self.horizontalLayout_5.addWidget(self.autoSave)


        self.verticalLayout.addLayout(self.horizontalLayout_5)


        self.verticalLayout_2.addWidget(self.groupBox)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(2, 2, 2, 2)
        self.buttonStart = QPushButton(self.centralwidget)
        self.buttonStart.setObjectName(u"buttonStart")
        self.buttonStart.setEnabled(False)
        self.buttonStart.setMinimumSize(QSize(75, 30))
        self.buttonStart.setMaximumSize(QSize(500, 40))
        self.buttonStart.setFont(font)

        self.horizontalLayout.addWidget(self.buttonStart)

        self.buttonStop = QPushButton(self.centralwidget)
        self.buttonStop.setObjectName(u"buttonStop")
        self.buttonStop.setEnabled(False)
        self.buttonStop.setMinimumSize(QSize(75, 30))
        self.buttonStop.setMaximumSize(QSize(500, 40))
        self.buttonStop.setFont(font)

        self.horizontalLayout.addWidget(self.buttonStop)

        self.line_3 = QFrame(self.centralwidget)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFont(font1)
        self.line_3.setFrameShape(QFrame.Shape.VLine)
        self.line_3.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout.addWidget(self.line_3)

        self.buttonReset = QPushButton(self.centralwidget)
        self.buttonReset.setObjectName(u"buttonReset")
        self.buttonReset.setEnabled(False)
        self.buttonReset.setFont(font)

        self.horizontalLayout.addWidget(self.buttonReset)


        self.verticalLayout_2.addLayout(self.horizontalLayout)


        self.gridLayout_5.addLayout(self.verticalLayout_2, 0, 0, 1, 1)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        self.verticalLayout_3.setContentsMargins(-1, -1, 0, -1)
        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        sizePolicy7 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy7.setHorizontalStretch(0)
        sizePolicy7.setVerticalStretch(1)
        sizePolicy7.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy7)

        self.verticalLayout_3.addWidget(self.widget)

        self.widget_2 = QWidget(self.centralwidget)
        self.widget_2.setObjectName(u"widget_2")
        sizePolicy8 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy8.setHorizontalStretch(0)
        sizePolicy8.setVerticalStretch(1)
        sizePolicy8.setHeightForWidth(self.widget_2.sizePolicy().hasHeightForWidth())
        self.widget_2.setSizePolicy(sizePolicy8)

        self.verticalLayout_3.addWidget(self.widget_2)


        self.gridLayout_5.addLayout(self.verticalLayout_3, 0, 2, 1, 1)

        self.gridLayout_5.setColumnStretch(2, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1144, 39))
        MainWindow.setMenuBar(self.menubar)
        self.statusBar = QStatusBar(MainWindow)
        self.statusBar.setObjectName(u"statusBar")
        MainWindow.setStatusBar(self.statusBar)

        self.retranslateUi(MainWindow)
        self.autoSave.toggled.connect(self.label_5.setVisible)
        self.autoSave.toggled.connect(self.suffix.setVisible)

        self.groupLetter.setCurrentIndex(-1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Polarisation-UI", None))
        self.live_values.setTitle(QCoreApplication.translate("MainWindow", u"Proben-Rotationsstage", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Status", None))
        self.sample_enr.setText(QCoreApplication.translate("MainWindow", u"E12345", None))
        self.sample_statusLED.setText("")
        self.label.setText(QCoreApplication.translate("MainWindow", u"Rotationswinkel (\u00b0)", None))
        self.sample_zero.setText(QCoreApplication.translate("MainWindow", u"Nullpunkt-Kalibrierung", None))
        self.live_values_2.setTitle(QCoreApplication.translate("MainWindow", u"Detektor-Rotationsstage", None))
        self.label_14.setText(QCoreApplication.translate("MainWindow", u"Status", None))
        self.dstage_enr.setText(QCoreApplication.translate("MainWindow", u"E12345", None))
        self.dstage_statusLED.setText("")
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"Rotationswinkel (\u00b0)", None))
        self.dstage_zero_2.setText(QCoreApplication.translate("MainWindow", u"Nullpunkt-Kalibrierung", None))
        self.live_values_3.setTitle(QCoreApplication.translate("MainWindow", u"Detektor", None))
        self.label_18.setText(QCoreApplication.translate("MainWindow", u"Status", None))
        self.detector_enr.setText(QCoreApplication.translate("MainWindow", u"E12345", None))
        self.detector_statusLED.setText("")
        self.label_19.setText(QCoreApplication.translate("MainWindow", u"Fotospannung (V)", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Speicherung", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"Gruppe*", None))
        self.groupLetter.setItemText(0, QCoreApplication.translate("MainWindow", u"A", None))
        self.groupLetter.setItemText(1, QCoreApplication.translate("MainWindow", u"B", None))
        self.groupLetter.setItemText(2, QCoreApplication.translate("MainWindow", u"C", None))
        self.groupLetter.setItemText(3, QCoreApplication.translate("MainWindow", u"D", None))
        self.groupLetter.setItemText(4, QCoreApplication.translate("MainWindow", u"E", None))
        self.groupLetter.setItemText(5, QCoreApplication.translate("MainWindow", u"F", None))
        self.groupLetter.setItemText(6, QCoreApplication.translate("MainWindow", u"G", None))
        self.groupLetter.setItemText(7, QCoreApplication.translate("MainWindow", u"H", None))
        self.groupLetter.setItemText(8, QCoreApplication.translate("MainWindow", u"I", None))
        self.groupLetter.setItemText(9, QCoreApplication.translate("MainWindow", u"J", None))
        self.groupLetter.setItemText(10, QCoreApplication.translate("MainWindow", u"K", None))
        self.groupLetter.setItemText(11, QCoreApplication.translate("MainWindow", u"L", None))
        self.groupLetter.setItemText(12, QCoreApplication.translate("MainWindow", u"M", None))
        self.groupLetter.setItemText(13, QCoreApplication.translate("MainWindow", u"N", None))
        self.groupLetter.setItemText(14, QCoreApplication.translate("MainWindow", u"O", None))
        self.groupLetter.setItemText(15, QCoreApplication.translate("MainWindow", u"P", None))
        self.groupLetter.setItemText(16, QCoreApplication.translate("MainWindow", u"Q", None))
        self.groupLetter.setItemText(17, QCoreApplication.translate("MainWindow", u"R", None))
        self.groupLetter.setItemText(18, QCoreApplication.translate("MainWindow", u"S", None))
        self.groupLetter.setItemText(19, QCoreApplication.translate("MainWindow", u"T", None))
        self.groupLetter.setItemText(20, QCoreApplication.translate("MainWindow", u"U", None))
        self.groupLetter.setItemText(21, QCoreApplication.translate("MainWindow", u"V", None))
        self.groupLetter.setItemText(22, QCoreApplication.translate("MainWindow", u"W", None))
        self.groupLetter.setItemText(23, QCoreApplication.translate("MainWindow", u"Z", None))

#if QT_CONFIG(tooltip)
        self.groupLetter.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Auswahl der GP Praktikumsgruppe <span style=\" color:#ff001a;\">(Pflichtfeld)</span></p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Eigenes Suffix", None))
#if QT_CONFIG(tooltip)
        self.suffix.setToolTip(QCoreApplication.translate("MainWindow", u"Ein benutzerdefiniertes Suffix mit maximal 20 Zeichen", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.buttonSave.setToolTip(QCoreApplication.translate("MainWindow", u"Messung speichern (Dateidialog)", None))
#endif // QT_CONFIG(tooltip)
        self.buttonSave.setText(QCoreApplication.translate("MainWindow", u"Speichern", None))
#if QT_CONFIG(tooltip)
        self.autoSave.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Bei Aktivierung werden die Messungen automatisch im Format:</p><p>YYYY_MM_DD-<span style=\" font-style:italic;\">Radioaktive Probe</span>-<span style=\" font-style:italic;\">Suffix</span>.csv</p><p>im Ordner Dokumente/Geiger-Mueller/ gespeichert.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.autoSave.setText(QCoreApplication.translate("MainWindow", u"Automatische Speicherung. ", None))
#if QT_CONFIG(tooltip)
        self.buttonStart.setToolTip(QCoreApplication.translate("MainWindow", u"Start der Messung", None))
#endif // QT_CONFIG(tooltip)
        self.buttonStart.setText(QCoreApplication.translate("MainWindow", u"Start", None))
#if QT_CONFIG(tooltip)
        self.buttonStop.setToolTip(QCoreApplication.translate("MainWindow", u"Aktuelle Messung stoppen", None))
#endif // QT_CONFIG(tooltip)
        self.buttonStop.setText(QCoreApplication.translate("MainWindow", u"Stop", None))
        self.buttonReset.setText(QCoreApplication.translate("MainWindow", u"Reset", None))
    # retranslateUi

