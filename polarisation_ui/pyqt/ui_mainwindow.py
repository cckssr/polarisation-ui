# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
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
    QAction,
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
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLCDNumber,
    QLabel,
    QLayout,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMenuBar,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QStatusBar,
    QTabWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1098, 901)
        MainWindow.setMinimumSize(QSize(0, 860))
        font = QFont()
        font.setPointSize(13)
        MainWindow.setFont(font)
        self.actionAutoSaveEnabled = QAction(MainWindow)
        self.actionAutoSaveEnabled.setObjectName("actionAutoSaveEnabled")
        self.actionAutoSaveEnabled.setCheckable(True)
        self.actionAutoSaveEnabled.setChecked(True)
        self.actionAcquisitionSettings = QAction(MainWindow)
        self.actionAcquisitionSettings.setObjectName("actionAcquisitionSettings")
        self.actionAcquisitionSettings.setMenuRole(QAction.MenuRole.NoRole)
        self.actionEncoderDebug = QAction(MainWindow)
        self.actionEncoderDebug.setObjectName("actionEncoderDebug")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_5 = QGridLayout(self.centralwidget)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.gridLayout_5.setContentsMargins(10, 0, 10, 10)
        self.verticalLayout_2 = QVBoxLayout()
        # ifndef Q_OS_MAC
        self.verticalLayout_2.setSpacing(-1)
        # endif
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout_2.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.verticalLayout_2.setContentsMargins(0, -1, -1, 0)
        self.gbArduinoConnection = QGroupBox(self.centralwidget)
        self.gbArduinoConnection.setObjectName("gbArduinoConnection")
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.gbArduinoConnection.sizePolicy().hasHeightForWidth()
        )
        self.gbArduinoConnection.setSizePolicy(sizePolicy)
        self.gbArduinoConnection.setMinimumSize(QSize(0, 100))
        font1 = QFont()
        font1.setPointSize(15)
        self.gbArduinoConnection.setFont(font1)
        self.gbArduinoConnection.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gbArduinoConnection.setCheckable(False)
        self.formArduinoConnection = QFormLayout(self.gbArduinoConnection)
        self.formArduinoConnection.setObjectName("formArduinoConnection")
        self.formArduinoConnection.setSizeConstraint(
            QLayout.SizeConstraint.SetNoConstraint
        )
        self.formArduinoConnection.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow
        )
        self.formArduinoConnection.setLabelAlignment(
            Qt.AlignmentFlag.AlignLeading
            | Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )
        self.formArduinoConnection.setHorizontalSpacing(-1)
        self.formArduinoConnection.setVerticalSpacing(10)
        self.formArduinoConnection.setContentsMargins(-1, 5, -1, 5)
        self.lblArduinoPort = QLabel(self.gbArduinoConnection)
        self.lblArduinoPort.setObjectName("lblArduinoPort")
        sizePolicy.setHeightForWidth(
            self.lblArduinoPort.sizePolicy().hasHeightForWidth()
        )
        self.lblArduinoPort.setSizePolicy(sizePolicy)
        self.lblArduinoPort.setFont(font)
        self.lblArduinoPort.setAlignment(
            Qt.AlignmentFlag.AlignLeading
            | Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.formArduinoConnection.setWidget(
            0, QFormLayout.ItemRole.LabelRole, self.lblArduinoPort
        )

        self.hlArduinoPort = QHBoxLayout()
        self.hlArduinoPort.setObjectName("hlArduinoPort")
        self.hlArduinoPort.setContentsMargins(-1, -1, -1, 0)
        self.cbArduinoPort = QComboBox(self.gbArduinoConnection)
        self.cbArduinoPort.setObjectName("cbArduinoPort")
        sizePolicy.setHeightForWidth(
            self.cbArduinoPort.sizePolicy().hasHeightForWidth()
        )
        self.cbArduinoPort.setSizePolicy(sizePolicy)
        self.cbArduinoPort.setMaximumSize(QSize(155, 16777215))

        self.hlArduinoPort.addWidget(self.cbArduinoPort)

        self.btnRefreshPorts = QToolButton(self.gbArduinoConnection)
        self.btnRefreshPorts.setObjectName("btnRefreshPorts")
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.ViewRefresh))
        self.btnRefreshPorts.setIcon(icon)
        self.btnRefreshPorts.setIconSize(QSize(14, 14))

        self.hlArduinoPort.addWidget(self.btnRefreshPorts)

        self.formArduinoConnection.setLayout(
            0, QFormLayout.ItemRole.FieldRole, self.hlArduinoPort
        )

        self.lblArduinoStatus = QLabel(self.gbArduinoConnection)
        self.lblArduinoStatus.setObjectName("lblArduinoStatus")
        sizePolicy.setHeightForWidth(
            self.lblArduinoStatus.sizePolicy().hasHeightForWidth()
        )
        self.lblArduinoStatus.setSizePolicy(sizePolicy)
        self.lblArduinoStatus.setFont(font)
        self.lblArduinoStatus.setAlignment(
            Qt.AlignmentFlag.AlignLeading
            | Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.formArduinoConnection.setWidget(
            1, QFormLayout.ItemRole.LabelRole, self.lblArduinoStatus
        )

        self.hlArduinoStatus = QHBoxLayout()
        self.hlArduinoStatus.setObjectName("hlArduinoStatus")
        self.lblArduinoStatusValue = QLabel(self.gbArduinoConnection)
        self.lblArduinoStatusValue.setObjectName("lblArduinoStatusValue")
        sizePolicy.setHeightForWidth(
            self.lblArduinoStatusValue.sizePolicy().hasHeightForWidth()
        )
        self.lblArduinoStatusValue.setSizePolicy(sizePolicy)
        self.lblArduinoStatusValue.setFont(font)
        self.lblArduinoStatusValue.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignTrailing
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.hlArduinoStatus.addWidget(self.lblArduinoStatusValue)

        self.ledArduinoStatus = QLabel(self.gbArduinoConnection)
        self.ledArduinoStatus.setObjectName("ledArduinoStatus")
        sizePolicy.setHeightForWidth(
            self.ledArduinoStatus.sizePolicy().hasHeightForWidth()
        )
        self.ledArduinoStatus.setSizePolicy(sizePolicy)
        self.ledArduinoStatus.setMinimumSize(QSize(20, 20))
        self.ledArduinoStatus.setMaximumSize(QSize(20, 20))
        self.ledArduinoStatus.setStyleSheet(
            "background-color: rgb(255, 11, 3); border: 0px; padding: 4px; border-radius: 10px"
        )

        self.hlArduinoStatus.addWidget(self.ledArduinoStatus)

        self.formArduinoConnection.setLayout(
            1, QFormLayout.ItemRole.FieldRole, self.hlArduinoStatus
        )

        self.btnArduinoConnect = QPushButton(self.gbArduinoConnection)
        self.btnArduinoConnect.setObjectName("btnArduinoConnect")
        sizePolicy.setHeightForWidth(
            self.btnArduinoConnect.sizePolicy().hasHeightForWidth()
        )
        self.btnArduinoConnect.setSizePolicy(sizePolicy)
        self.btnArduinoConnect.setMinimumSize(QSize(0, 0))
        self.btnArduinoConnect.setFont(font)

        self.formArduinoConnection.setWidget(
            2, QFormLayout.ItemRole.SpanningRole, self.btnArduinoConnect
        )

        self.verticalLayout_2.addWidget(self.gbArduinoConnection)

        self.verticalSpacer_4 = QSpacerItem(
            20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed
        )

        self.verticalLayout_2.addItem(self.verticalSpacer_4)

        self.gbSampleStage = QGroupBox(self.centralwidget)
        self.gbSampleStage.setObjectName("gbSampleStage")
        self.gbSampleStage.setEnabled(False)
        sizePolicy1 = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(
            self.gbSampleStage.sizePolicy().hasHeightForWidth()
        )
        self.gbSampleStage.setSizePolicy(sizePolicy1)
        self.gbSampleStage.setMinimumSize(QSize(0, 100))
        self.gbSampleStage.setFont(font1)
        self.gbSampleStage.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gbSampleStage.setCheckable(False)
        self.formSampleStage = QFormLayout(self.gbSampleStage)
        self.formSampleStage.setObjectName("formSampleStage")
        self.formSampleStage.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        self.formSampleStage.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow
        )
        self.formSampleStage.setLabelAlignment(
            Qt.AlignmentFlag.AlignLeading
            | Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )
        self.formSampleStage.setHorizontalSpacing(-1)
        self.formSampleStage.setVerticalSpacing(10)
        self.formSampleStage.setContentsMargins(-1, 5, -1, 5)
        self.lblSampleStatus = QLabel(self.gbSampleStage)
        self.lblSampleStatus.setObjectName("lblSampleStatus")
        sizePolicy2 = QSizePolicy(
            QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum
        )
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(
            self.lblSampleStatus.sizePolicy().hasHeightForWidth()
        )
        self.lblSampleStatus.setSizePolicy(sizePolicy2)
        self.lblSampleStatus.setFont(font)
        self.lblSampleStatus.setAlignment(
            Qt.AlignmentFlag.AlignLeading
            | Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.formSampleStage.setWidget(
            0, QFormLayout.ItemRole.LabelRole, self.lblSampleStatus
        )

        self.hlSampleStatus = QHBoxLayout()
        self.hlSampleStatus.setObjectName("hlSampleStatus")
        self.lblSampleStatusValue = QLabel(self.gbSampleStage)
        self.lblSampleStatusValue.setObjectName("lblSampleStatusValue")
        sizePolicy1.setHeightForWidth(
            self.lblSampleStatusValue.sizePolicy().hasHeightForWidth()
        )
        self.lblSampleStatusValue.setSizePolicy(sizePolicy1)
        self.lblSampleStatusValue.setFont(font)
        self.lblSampleStatusValue.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignTrailing
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.hlSampleStatus.addWidget(self.lblSampleStatusValue)

        self.ledSampleStatus = QLabel(self.gbSampleStage)
        self.ledSampleStatus.setObjectName("ledSampleStatus")
        sizePolicy.setHeightForWidth(
            self.ledSampleStatus.sizePolicy().hasHeightForWidth()
        )
        self.ledSampleStatus.setSizePolicy(sizePolicy)
        self.ledSampleStatus.setMinimumSize(QSize(20, 20))
        self.ledSampleStatus.setMaximumSize(QSize(20, 20))
        self.ledSampleStatus.setStyleSheet(
            "background-color: rgb(255, 11, 3); border: 0px; padding: 4px; border-radius: 10px"
        )

        self.hlSampleStatus.addWidget(self.ledSampleStatus)

        self.formSampleStage.setLayout(
            0, QFormLayout.ItemRole.FieldRole, self.hlSampleStatus
        )

        self.lblSampleAngle = QLabel(self.gbSampleStage)
        self.lblSampleAngle.setObjectName("lblSampleAngle")
        sizePolicy.setHeightForWidth(
            self.lblSampleAngle.sizePolicy().hasHeightForWidth()
        )
        self.lblSampleAngle.setSizePolicy(sizePolicy)
        self.lblSampleAngle.setMinimumSize(QSize(0, 40))
        self.lblSampleAngle.setFont(font)

        self.formSampleStage.setWidget(
            1, QFormLayout.ItemRole.LabelRole, self.lblSampleAngle
        )

        self.lcdSampleAngle = QLCDNumber(self.gbSampleStage)
        self.lcdSampleAngle.setObjectName("lcdSampleAngle")
        sizePolicy2.setHeightForWidth(
            self.lcdSampleAngle.sizePolicy().hasHeightForWidth()
        )
        self.lcdSampleAngle.setSizePolicy(sizePolicy2)
        self.lcdSampleAngle.setMinimumSize(QSize(0, 40))
        self.lcdSampleAngle.setFont(font)
        self.lcdSampleAngle.setLineWidth(2)
        self.lcdSampleAngle.setDigitCount(6)

        self.formSampleStage.setWidget(
            1, QFormLayout.ItemRole.FieldRole, self.lcdSampleAngle
        )

        self.btnSampleZero = QPushButton(self.gbSampleStage)
        self.btnSampleZero.setObjectName("btnSampleZero")
        sizePolicy3 = QSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum
        )
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(
            self.btnSampleZero.sizePolicy().hasHeightForWidth()
        )
        self.btnSampleZero.setSizePolicy(sizePolicy3)
        self.btnSampleZero.setMinimumSize(QSize(0, 0))
        self.btnSampleZero.setFont(font)

        self.formSampleStage.setWidget(
            2, QFormLayout.ItemRole.SpanningRole, self.btnSampleZero
        )

        self.verticalLayout_2.addWidget(self.gbSampleStage)

        self.verticalSpacer_3 = QSpacerItem(
            20, 5, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed
        )

        self.verticalLayout_2.addItem(self.verticalSpacer_3)

        self.gbDetectorStage = QGroupBox(self.centralwidget)
        self.gbDetectorStage.setObjectName("gbDetectorStage")
        self.gbDetectorStage.setEnabled(False)
        sizePolicy1.setHeightForWidth(
            self.gbDetectorStage.sizePolicy().hasHeightForWidth()
        )
        self.gbDetectorStage.setSizePolicy(sizePolicy1)
        self.gbDetectorStage.setMinimumSize(QSize(0, 100))
        self.gbDetectorStage.setFont(font1)
        self.gbDetectorStage.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.formDetectorStage = QFormLayout(self.gbDetectorStage)
        self.formDetectorStage.setObjectName("formDetectorStage")
        self.formDetectorStage.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        self.formDetectorStage.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow
        )
        self.formDetectorStage.setLabelAlignment(
            Qt.AlignmentFlag.AlignLeading
            | Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )
        self.formDetectorStage.setHorizontalSpacing(-1)
        self.formDetectorStage.setVerticalSpacing(10)
        self.formDetectorStage.setContentsMargins(-1, 5, -1, 5)
        self.lblDetectorStageStatus = QLabel(self.gbDetectorStage)
        self.lblDetectorStageStatus.setObjectName("lblDetectorStageStatus")
        sizePolicy1.setHeightForWidth(
            self.lblDetectorStageStatus.sizePolicy().hasHeightForWidth()
        )
        self.lblDetectorStageStatus.setSizePolicy(sizePolicy1)
        self.lblDetectorStageStatus.setFont(font)
        self.lblDetectorStageStatus.setAlignment(
            Qt.AlignmentFlag.AlignLeading
            | Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.formDetectorStage.setWidget(
            0, QFormLayout.ItemRole.LabelRole, self.lblDetectorStageStatus
        )

        self.hlDetectorStageStatus = QHBoxLayout()
        self.hlDetectorStageStatus.setObjectName("hlDetectorStageStatus")
        self.lblDetectorStageStatusValue = QLabel(self.gbDetectorStage)
        self.lblDetectorStageStatusValue.setObjectName("lblDetectorStageStatusValue")
        sizePolicy1.setHeightForWidth(
            self.lblDetectorStageStatusValue.sizePolicy().hasHeightForWidth()
        )
        self.lblDetectorStageStatusValue.setSizePolicy(sizePolicy1)
        self.lblDetectorStageStatusValue.setFont(font)
        self.lblDetectorStageStatusValue.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignTrailing
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.hlDetectorStageStatus.addWidget(self.lblDetectorStageStatusValue)

        self.ledDetectorStageStatus = QLabel(self.gbDetectorStage)
        self.ledDetectorStageStatus.setObjectName("ledDetectorStageStatus")
        sizePolicy.setHeightForWidth(
            self.ledDetectorStageStatus.sizePolicy().hasHeightForWidth()
        )
        self.ledDetectorStageStatus.setSizePolicy(sizePolicy)
        self.ledDetectorStageStatus.setMinimumSize(QSize(20, 20))
        self.ledDetectorStageStatus.setMaximumSize(QSize(20, 20))
        self.ledDetectorStageStatus.setStyleSheet(
            "background-color: rgb(255, 11, 3); border: 0px; padding: 4px; border-radius: 10px"
        )

        self.hlDetectorStageStatus.addWidget(self.ledDetectorStageStatus)

        self.formDetectorStage.setLayout(
            0, QFormLayout.ItemRole.FieldRole, self.hlDetectorStageStatus
        )

        self.lblDetectorStageAngle = QLabel(self.gbDetectorStage)
        self.lblDetectorStageAngle.setObjectName("lblDetectorStageAngle")
        sizePolicy.setHeightForWidth(
            self.lblDetectorStageAngle.sizePolicy().hasHeightForWidth()
        )
        self.lblDetectorStageAngle.setSizePolicy(sizePolicy)
        self.lblDetectorStageAngle.setMinimumSize(QSize(0, 40))
        self.lblDetectorStageAngle.setFont(font)

        self.formDetectorStage.setWidget(
            1, QFormLayout.ItemRole.LabelRole, self.lblDetectorStageAngle
        )

        self.lcdDetectorStageAngle = QLCDNumber(self.gbDetectorStage)
        self.lcdDetectorStageAngle.setObjectName("lcdDetectorStageAngle")
        sizePolicy2.setHeightForWidth(
            self.lcdDetectorStageAngle.sizePolicy().hasHeightForWidth()
        )
        self.lcdDetectorStageAngle.setSizePolicy(sizePolicy2)
        self.lcdDetectorStageAngle.setMinimumSize(QSize(0, 40))
        self.lcdDetectorStageAngle.setFont(font)
        self.lcdDetectorStageAngle.setLineWidth(2)
        self.lcdDetectorStageAngle.setDigitCount(6)

        self.formDetectorStage.setWidget(
            1, QFormLayout.ItemRole.FieldRole, self.lcdDetectorStageAngle
        )

        self.btnDetectorStageZero = QPushButton(self.gbDetectorStage)
        self.btnDetectorStageZero.setObjectName("btnDetectorStageZero")
        sizePolicy3.setHeightForWidth(
            self.btnDetectorStageZero.sizePolicy().hasHeightForWidth()
        )
        self.btnDetectorStageZero.setSizePolicy(sizePolicy3)
        self.btnDetectorStageZero.setMinimumSize(QSize(0, 0))
        self.btnDetectorStageZero.setFont(font)

        self.formDetectorStage.setWidget(
            2, QFormLayout.ItemRole.SpanningRole, self.btnDetectorStageZero
        )

        self.verticalLayout_2.addWidget(self.gbDetectorStage)

        self.verticalSpacer_2 = QSpacerItem(
            20, 15, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed
        )

        self.verticalLayout_2.addItem(self.verticalSpacer_2)

        self.gbDetector = QGroupBox(self.centralwidget)
        self.gbDetector.setObjectName("gbDetector")
        self.gbDetector.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.gbDetector.sizePolicy().hasHeightForWidth())
        self.gbDetector.setSizePolicy(sizePolicy1)
        self.gbDetector.setMinimumSize(QSize(0, 125))
        self.gbDetector.setFont(font1)
        self.gbDetector.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.formDetector = QFormLayout(self.gbDetector)
        self.formDetector.setObjectName("formDetector")
        self.formDetector.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        self.formDetector.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow
        )
        self.formDetector.setLabelAlignment(
            Qt.AlignmentFlag.AlignLeading
            | Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )
        self.formDetector.setHorizontalSpacing(-1)
        self.formDetector.setVerticalSpacing(10)
        self.lblDetectorStatus = QLabel(self.gbDetector)
        self.lblDetectorStatus.setObjectName("lblDetectorStatus")
        sizePolicy2.setHeightForWidth(
            self.lblDetectorStatus.sizePolicy().hasHeightForWidth()
        )
        self.lblDetectorStatus.setSizePolicy(sizePolicy2)
        self.lblDetectorStatus.setFont(font)
        self.lblDetectorStatus.setAlignment(
            Qt.AlignmentFlag.AlignLeading
            | Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.formDetector.setWidget(
            0, QFormLayout.ItemRole.LabelRole, self.lblDetectorStatus
        )

        self.hlDetectorStatus = QHBoxLayout()
        self.hlDetectorStatus.setObjectName("hlDetectorStatus")
        self.lblDetectorStatusValue = QLabel(self.gbDetector)
        self.lblDetectorStatusValue.setObjectName("lblDetectorStatusValue")
        sizePolicy1.setHeightForWidth(
            self.lblDetectorStatusValue.sizePolicy().hasHeightForWidth()
        )
        self.lblDetectorStatusValue.setSizePolicy(sizePolicy1)
        self.lblDetectorStatusValue.setFont(font)
        self.lblDetectorStatusValue.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignTrailing
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.hlDetectorStatus.addWidget(self.lblDetectorStatusValue)

        self.ledDetectorStatus = QLabel(self.gbDetector)
        self.ledDetectorStatus.setObjectName("ledDetectorStatus")
        sizePolicy.setHeightForWidth(
            self.ledDetectorStatus.sizePolicy().hasHeightForWidth()
        )
        self.ledDetectorStatus.setSizePolicy(sizePolicy)
        self.ledDetectorStatus.setMinimumSize(QSize(20, 20))
        self.ledDetectorStatus.setMaximumSize(QSize(20, 20))
        self.ledDetectorStatus.setStyleSheet(
            "background-color: rgb(255, 11, 3); border: 0px; padding: 4px; border-radius: 10px"
        )

        self.hlDetectorStatus.addWidget(self.ledDetectorStatus)

        self.formDetector.setLayout(
            0, QFormLayout.ItemRole.FieldRole, self.hlDetectorStatus
        )

        self.lblDetectorVoltage = QLabel(self.gbDetector)
        self.lblDetectorVoltage.setObjectName("lblDetectorVoltage")
        sizePolicy.setHeightForWidth(
            self.lblDetectorVoltage.sizePolicy().hasHeightForWidth()
        )
        self.lblDetectorVoltage.setSizePolicy(sizePolicy)
        self.lblDetectorVoltage.setMinimumSize(QSize(0, 40))
        self.lblDetectorVoltage.setFont(font)

        self.formDetector.setWidget(
            1, QFormLayout.ItemRole.LabelRole, self.lblDetectorVoltage
        )

        self.lcdDetectorVoltage = QLCDNumber(self.gbDetector)
        self.lcdDetectorVoltage.setObjectName("lcdDetectorVoltage")
        sizePolicy2.setHeightForWidth(
            self.lcdDetectorVoltage.sizePolicy().hasHeightForWidth()
        )
        self.lcdDetectorVoltage.setSizePolicy(sizePolicy2)
        self.lcdDetectorVoltage.setMinimumSize(QSize(0, 40))
        self.lcdDetectorVoltage.setFont(font)
        self.lcdDetectorVoltage.setLineWidth(2)
        self.lcdDetectorVoltage.setDigitCount(6)

        self.formDetector.setWidget(
            1, QFormLayout.ItemRole.FieldRole, self.lcdDetectorVoltage
        )

        self.verticalLayout_2.addWidget(self.gbDetector)

        self.verticalSpacer = QSpacerItem(
            20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.gbSave = QGroupBox(self.centralwidget)
        self.gbSave.setObjectName("gbSave")
        sizePolicy4 = QSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred
        )
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.gbSave.sizePolicy().hasHeightForWidth())
        self.gbSave.setSizePolicy(sizePolicy4)
        self.gbSave.setMinimumSize(QSize(0, 50))
        self.gbSave.setFont(font1)
        self.gbSave.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gbSave.setFlat(False)
        self.gbSave.setCheckable(False)
        self.verticalLayout = QVBoxLayout(self.gbSave)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.formSave = QFormLayout()
        self.formSave.setObjectName("formSave")
        self.formSave.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow
        )
        self.formSave.setContentsMargins(-1, -1, 0, 0)
        self.lblGroupLetter = QLabel(self.gbSave)
        self.lblGroupLetter.setObjectName("lblGroupLetter")
        self.lblGroupLetter.setFont(font)

        self.formSave.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lblGroupLetter)

        self.cbGroupLetter = QComboBox(self.gbSave)
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.addItem("")
        self.cbGroupLetter.setObjectName("cbGroupLetter")
        sizePolicy5 = QSizePolicy(
            QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed
        )
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(
            self.cbGroupLetter.sizePolicy().hasHeightForWidth()
        )
        self.cbGroupLetter.setSizePolicy(sizePolicy5)
        self.cbGroupLetter.setFont(font)
        self.cbGroupLetter.setMaxCount(24)
        self.cbGroupLetter.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        self.formSave.setWidget(0, QFormLayout.ItemRole.FieldRole, self.cbGroupLetter)

        self.lblSuffix = QLabel(self.gbSave)
        self.lblSuffix.setObjectName("lblSuffix")
        self.lblSuffix.setFont(font)

        self.formSave.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lblSuffix)

        self.leSuffix = QLineEdit(self.gbSave)
        self.leSuffix.setObjectName("leSuffix")
        sizePolicy5.setHeightForWidth(self.leSuffix.sizePolicy().hasHeightForWidth())
        self.leSuffix.setSizePolicy(sizePolicy5)
        self.leSuffix.setFont(font)
        self.leSuffix.setText("")
        self.leSuffix.setMaxLength(20)

        self.formSave.setWidget(1, QFormLayout.ItemRole.FieldRole, self.leSuffix)

        self.verticalLayout.addLayout(self.formSave)

        self.btnSave = QPushButton(self.gbSave)
        self.btnSave.setObjectName("btnSave")
        self.btnSave.setEnabled(False)
        sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.btnSave.sizePolicy().hasHeightForWidth())
        self.btnSave.setSizePolicy(sizePolicy6)
        self.btnSave.setMinimumSize(QSize(100, 30))
        self.btnSave.setMaximumSize(QSize(1000, 40))
        self.btnSave.setFont(font)

        self.verticalLayout.addWidget(self.btnSave)

        self.verticalLayout_2.addWidget(self.gbSave)

        self.hlMeasurementControls = QHBoxLayout()
        self.hlMeasurementControls.setObjectName("hlMeasurementControls")
        self.hlMeasurementControls.setContentsMargins(2, 2, 2, 2)
        self.btnStartMeasurement = QPushButton(self.centralwidget)
        self.btnStartMeasurement.setObjectName("btnStartMeasurement")
        self.btnStartMeasurement.setEnabled(False)
        self.btnStartMeasurement.setMinimumSize(QSize(75, 30))
        self.btnStartMeasurement.setMaximumSize(QSize(500, 40))
        self.btnStartMeasurement.setFont(font)

        self.hlMeasurementControls.addWidget(self.btnStartMeasurement)

        self.btnStopMeasurement = QPushButton(self.centralwidget)
        self.btnStopMeasurement.setObjectName("btnStopMeasurement")
        self.btnStopMeasurement.setEnabled(False)
        self.btnStopMeasurement.setMinimumSize(QSize(75, 30))
        self.btnStopMeasurement.setMaximumSize(QSize(500, 40))
        self.btnStopMeasurement.setFont(font)

        self.hlMeasurementControls.addWidget(self.btnStopMeasurement)

        self.lineMeasurementControls = QFrame(self.centralwidget)
        self.lineMeasurementControls.setObjectName("lineMeasurementControls")
        font2 = QFont()
        font2.setPointSize(11)
        self.lineMeasurementControls.setFont(font2)
        self.lineMeasurementControls.setFrameShape(QFrame.Shape.VLine)
        self.lineMeasurementControls.setFrameShadow(QFrame.Shadow.Sunken)

        self.hlMeasurementControls.addWidget(self.lineMeasurementControls)

        self.btnResetMeasurement = QPushButton(self.centralwidget)
        self.btnResetMeasurement.setObjectName("btnResetMeasurement")
        self.btnResetMeasurement.setEnabled(False)
        self.btnResetMeasurement.setFont(font)

        self.hlMeasurementControls.addWidget(self.btnResetMeasurement)

        self.verticalLayout_2.addLayout(self.hlMeasurementControls)

        self.verticalLayout_2.setStretch(7, 1)

        self.gridLayout_5.addLayout(self.verticalLayout_2, 0, 0, 1, 1)

        self.line = QFrame(self.centralwidget)
        self.line.setObjectName("line")
        self.line.setFont(font2)
        self.line.setFrameShadow(QFrame.Shadow.Plain)
        self.line.setFrameShape(QFrame.Shape.VLine)

        self.gridLayout_5.addWidget(self.line, 0, 1, 1, 1)

        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")

        self.gridLayout_5.addWidget(self.tabWidget, 0, 2, 1, 1)

        self.gridLayout_5.setColumnStretch(2, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        self.menubar.setGeometry(QRect(0, 0, 1098, 39))
        self.menuEinstellungen = QMenu(self.menubar)
        self.menuEinstellungen.setObjectName("menuEinstellungen")
        MainWindow.setMenuBar(self.menubar)
        self.statusBar = QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)

        self.menubar.addAction(self.menuEinstellungen.menuAction())
        self.menuEinstellungen.addAction(self.actionAutoSaveEnabled)
        self.menuEinstellungen.addAction(self.actionAcquisitionSettings)
        self.menuEinstellungen.addAction(self.actionEncoderDebug)

        self.retranslateUi(MainWindow)
        self.actionAutoSaveEnabled.triggered["bool"].connect(self.lblSuffix.setVisible)
        self.actionAutoSaveEnabled.triggered["bool"].connect(self.leSuffix.setVisible)

        self.cbGroupLetter.setCurrentIndex(-1)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            QCoreApplication.translate("MainWindow", "Polarisation-UI", None)
        )
        self.actionAutoSaveEnabled.setText(
            QCoreApplication.translate(
                "MainWindow", "Automatische Speicherung aktiviert", None
            )
        )
        self.actionAcquisitionSettings.setText(
            QCoreApplication.translate("MainWindow", "Aquisations-Einstellungen", None)
        )
        self.actionEncoderDebug.setText(
            QCoreApplication.translate("MainWindow", "Encoder Debugging", None)
        )
        self.gbArduinoConnection.setTitle(
            QCoreApplication.translate("MainWindow", "Arduino-Verbindung", None)
        )
        self.lblArduinoPort.setText(
            QCoreApplication.translate("MainWindow", "Port", None)
        )
        self.btnRefreshPorts.setText(
            QCoreApplication.translate("MainWindow", "...", None)
        )
        self.lblArduinoStatus.setText(
            QCoreApplication.translate("MainWindow", "Status", None)
        )
        self.lblArduinoStatusValue.setText(
            QCoreApplication.translate("MainWindow", "Nicht verbunden", None)
        )
        self.ledArduinoStatus.setText("")
        self.btnArduinoConnect.setText(
            QCoreApplication.translate("MainWindow", "Verbinden", None)
        )
        self.gbSampleStage.setTitle(
            QCoreApplication.translate("MainWindow", "Proben-Rotationsstage", None)
        )
        self.lblSampleStatus.setText(
            QCoreApplication.translate("MainWindow", "Status", None)
        )
        self.lblSampleStatusValue.setText(
            QCoreApplication.translate("MainWindow", "E12345", None)
        )
        self.ledSampleStatus.setText("")
        self.lblSampleAngle.setText(
            QCoreApplication.translate("MainWindow", "Rotationswinkel (\u00b0)", None)
        )
        self.btnSampleZero.setText(
            QCoreApplication.translate("MainWindow", "Nullpunkt-Kalibrierung", None)
        )
        self.gbDetectorStage.setTitle(
            QCoreApplication.translate("MainWindow", "Detektor-Rotationsstage", None)
        )
        self.lblDetectorStageStatus.setText(
            QCoreApplication.translate("MainWindow", "Status", None)
        )
        self.lblDetectorStageStatusValue.setText(
            QCoreApplication.translate("MainWindow", "E12345", None)
        )
        self.ledDetectorStageStatus.setText("")
        self.lblDetectorStageAngle.setText(
            QCoreApplication.translate("MainWindow", "Rotationswinkel (\u00b0)", None)
        )
        self.btnDetectorStageZero.setText(
            QCoreApplication.translate("MainWindow", "Nullpunkt-Kalibrierung", None)
        )
        self.gbDetector.setTitle(
            QCoreApplication.translate("MainWindow", "Detektor", None)
        )
        self.lblDetectorStatus.setText(
            QCoreApplication.translate("MainWindow", "Status", None)
        )
        self.lblDetectorStatusValue.setText(
            QCoreApplication.translate("MainWindow", "E12345", None)
        )
        self.ledDetectorStatus.setText("")
        self.lblDetectorVoltage.setText(
            QCoreApplication.translate("MainWindow", "Spannung (V)", None)
        )
        self.gbSave.setTitle(
            QCoreApplication.translate("MainWindow", "Speicherung", None)
        )
        self.lblGroupLetter.setText(
            QCoreApplication.translate("MainWindow", "Gruppe*", None)
        )
        self.cbGroupLetter.setItemText(
            0, QCoreApplication.translate("MainWindow", "A", None)
        )
        self.cbGroupLetter.setItemText(
            1, QCoreApplication.translate("MainWindow", "B", None)
        )
        self.cbGroupLetter.setItemText(
            2, QCoreApplication.translate("MainWindow", "C", None)
        )
        self.cbGroupLetter.setItemText(
            3, QCoreApplication.translate("MainWindow", "D", None)
        )
        self.cbGroupLetter.setItemText(
            4, QCoreApplication.translate("MainWindow", "E", None)
        )
        self.cbGroupLetter.setItemText(
            5, QCoreApplication.translate("MainWindow", "F", None)
        )
        self.cbGroupLetter.setItemText(
            6, QCoreApplication.translate("MainWindow", "G", None)
        )
        self.cbGroupLetter.setItemText(
            7, QCoreApplication.translate("MainWindow", "H", None)
        )
        self.cbGroupLetter.setItemText(
            8, QCoreApplication.translate("MainWindow", "I", None)
        )
        self.cbGroupLetter.setItemText(
            9, QCoreApplication.translate("MainWindow", "J", None)
        )
        self.cbGroupLetter.setItemText(
            10, QCoreApplication.translate("MainWindow", "K", None)
        )
        self.cbGroupLetter.setItemText(
            11, QCoreApplication.translate("MainWindow", "L", None)
        )
        self.cbGroupLetter.setItemText(
            12, QCoreApplication.translate("MainWindow", "M", None)
        )
        self.cbGroupLetter.setItemText(
            13, QCoreApplication.translate("MainWindow", "N", None)
        )
        self.cbGroupLetter.setItemText(
            14, QCoreApplication.translate("MainWindow", "O", None)
        )
        self.cbGroupLetter.setItemText(
            15, QCoreApplication.translate("MainWindow", "P", None)
        )
        self.cbGroupLetter.setItemText(
            16, QCoreApplication.translate("MainWindow", "Q", None)
        )
        self.cbGroupLetter.setItemText(
            17, QCoreApplication.translate("MainWindow", "R", None)
        )
        self.cbGroupLetter.setItemText(
            18, QCoreApplication.translate("MainWindow", "S", None)
        )
        self.cbGroupLetter.setItemText(
            19, QCoreApplication.translate("MainWindow", "T", None)
        )
        self.cbGroupLetter.setItemText(
            20, QCoreApplication.translate("MainWindow", "U", None)
        )
        self.cbGroupLetter.setItemText(
            21, QCoreApplication.translate("MainWindow", "V", None)
        )
        self.cbGroupLetter.setItemText(
            22, QCoreApplication.translate("MainWindow", "W", None)
        )
        self.cbGroupLetter.setItemText(
            23, QCoreApplication.translate("MainWindow", "Z", None)
        )

        # if QT_CONFIG(tooltip)
        self.cbGroupLetter.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                '<html><head/><body><p>Auswahl der GP Praktikumsgruppe <span style=" color:#ff001a;">(Pflichtfeld)</span></p></body></html>',
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.lblSuffix.setText(
            QCoreApplication.translate("MainWindow", "Eigenes Suffix", None)
        )
        # if QT_CONFIG(tooltip)
        self.leSuffix.setToolTip(
            QCoreApplication.translate(
                "MainWindow",
                "Ein benutzerdefiniertes Suffix mit maximal 20 Zeichen",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(tooltip)
        self.btnSave.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Messung speichern (Dateidialog)", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnSave.setText(
            QCoreApplication.translate("MainWindow", "Speichern", None)
        )
        # if QT_CONFIG(tooltip)
        self.btnStartMeasurement.setToolTip(
            QCoreApplication.translate("MainWindow", "Start der Messung", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.btnStartMeasurement.setText(
            QCoreApplication.translate("MainWindow", "Start", None)
        )
        # if QT_CONFIG(tooltip)
        self.btnStopMeasurement.setToolTip(
            QCoreApplication.translate("MainWindow", "Aktuelle Messung stoppen", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.btnStopMeasurement.setText(
            QCoreApplication.translate("MainWindow", "Stop", None)
        )
        self.btnResetMeasurement.setText(
            QCoreApplication.translate("MainWindow", "Reset", None)
        )
        self.menuEinstellungen.setTitle(
            QCoreApplication.translate("MainWindow", "Einstellungen", None)
        )

    # retranslateUi
