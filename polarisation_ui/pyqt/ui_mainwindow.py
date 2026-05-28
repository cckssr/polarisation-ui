# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
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
    QButtonGroup,
    QComboBox,
    QDockWidget,
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

from polarisation_ui.ui.widgets.connection_banner import ConnectionBanner
from polarisation_ui.ui.widgets.event_log_panel import EventLogPanel


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(900, 750)
        MainWindow.setMinimumSize(QSize(0, 0))
        self.actionAutoSaveEnabled = QAction(MainWindow)
        self.actionAutoSaveEnabled.setObjectName("actionAutoSaveEnabled")
        self.actionAutoSaveEnabled.setCheckable(True)
        self.actionAutoSaveEnabled.setChecked(True)
        self.actionAcquisitionSettings = QAction(MainWindow)
        self.actionAcquisitionSettings.setObjectName("actionAcquisitionSettings")
        self.actionAcquisitionSettings.setMenuRole(QAction.MenuRole.NoRole)
        self.actionEncoderDebug = QAction(MainWindow)
        self.actionEncoderDebug.setObjectName("actionEncoderDebug")
        self.actionLogWindow = QAction(MainWindow)
        self.actionLogWindow.setObjectName("actionLogWindow")
        self.actionPowerCalibration = QAction(MainWindow)
        self.actionPowerCalibration.setObjectName("actionPowerCalibration")
        self.actionPowerCalibration.setMenuRole(QAction.MenuRole.NoRole)
        self.actionEventLog = QAction(MainWindow)
        self.actionEventLog.setObjectName("actionEventLog")
        self.actionEventLog.setCheckable(True)
        self.actionAutoPowerCalibration = QAction(MainWindow)
        self.actionAutoPowerCalibration.setObjectName("actionAutoPowerCalibration")
        self.actionAutoPowerCalibration.setMenuRole(QAction.MenuRole.NoRole)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_5 = QGridLayout(self.centralwidget)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.gridLayout_5.setContentsMargins(10, 0, 10, 10)
        self.connectionBanner = ConnectionBanner(self.centralwidget)
        self.connectionBanner.setObjectName("connectionBanner")
        self.connectionBanner.setVisible(False)

        self.gridLayout_5.addWidget(self.connectionBanner, 0, 0, 1, 3)

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
        self.gbArduinoConnection.setMinimumSize(QSize(0, 0))
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
        self.formArduinoConnection.setVerticalSpacing(6)
        self.formArduinoConnection.setContentsMargins(-1, 5, -1, 5)
        self.lblArduinoPort = QLabel(self.gbArduinoConnection)
        self.lblArduinoPort.setObjectName("lblArduinoPort")
        sizePolicy.setHeightForWidth(
            self.lblArduinoPort.sizePolicy().hasHeightForWidth()
        )
        self.lblArduinoPort.setSizePolicy(sizePolicy)
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
        self.ledArduinoStatus.setMinimumSize(QSize(16, 16))
        self.ledArduinoStatus.setMaximumSize(QSize(16, 16))
        self.ledArduinoStatus.setStyleSheet(
            "background-color: rgb(255, 11, 3); border: 0px; padding: 3px; border-radius: 8px"
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

        self.formArduinoConnection.setWidget(
            2, QFormLayout.ItemRole.SpanningRole, self.btnArduinoConnect
        )

        self.verticalLayout_2.addWidget(self.gbArduinoConnection)

        self.verticalSpacer_4 = QSpacerItem(
            20, 6, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed
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
        self.gbSampleStage.setMinimumSize(QSize(0, 0))
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
        self.formSampleStage.setVerticalSpacing(6)
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
        self.ledSampleStatus.setMinimumSize(QSize(16, 16))
        self.ledSampleStatus.setMaximumSize(QSize(16, 16))
        self.ledSampleStatus.setStyleSheet(
            "background-color: rgb(255, 11, 3); border: 0px; padding: 3px; border-radius: 8px"
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

        self.formSampleStage.setWidget(
            1, QFormLayout.ItemRole.LabelRole, self.lblSampleAngle
        )

        self.lcdSampleAngle = QLCDNumber(self.gbSampleStage)
        self.lcdSampleAngle.setObjectName("lcdSampleAngle")
        sizePolicy2.setHeightForWidth(
            self.lcdSampleAngle.sizePolicy().hasHeightForWidth()
        )
        self.lcdSampleAngle.setSizePolicy(sizePolicy2)
        self.lcdSampleAngle.setMinimumSize(QSize(0, 26))
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

        self.formSampleStage.setWidget(
            2, QFormLayout.ItemRole.SpanningRole, self.btnSampleZero
        )

        self.verticalLayout_2.addWidget(self.gbSampleStage)

        self.verticalSpacer_3 = QSpacerItem(
            20, 4, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed
        )

        self.verticalLayout_2.addItem(self.verticalSpacer_3)

        self.gbDetectorStage = QGroupBox(self.centralwidget)
        self.gbDetectorStage.setObjectName("gbDetectorStage")
        self.gbDetectorStage.setEnabled(False)
        sizePolicy1.setHeightForWidth(
            self.gbDetectorStage.sizePolicy().hasHeightForWidth()
        )
        self.gbDetectorStage.setSizePolicy(sizePolicy1)
        self.gbDetectorStage.setMinimumSize(QSize(0, 0))
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
        self.formDetectorStage.setVerticalSpacing(6)
        self.formDetectorStage.setContentsMargins(-1, 5, -1, 5)
        self.lblDetectorStageStatus = QLabel(self.gbDetectorStage)
        self.lblDetectorStageStatus.setObjectName("lblDetectorStageStatus")
        sizePolicy1.setHeightForWidth(
            self.lblDetectorStageStatus.sizePolicy().hasHeightForWidth()
        )
        self.lblDetectorStageStatus.setSizePolicy(sizePolicy1)
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
        self.ledDetectorStageStatus.setMinimumSize(QSize(16, 16))
        self.ledDetectorStageStatus.setMaximumSize(QSize(16, 16))
        self.ledDetectorStageStatus.setStyleSheet(
            "background-color: rgb(255, 11, 3); border: 0px; padding: 3px; border-radius: 8px"
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

        self.formDetectorStage.setWidget(
            1, QFormLayout.ItemRole.LabelRole, self.lblDetectorStageAngle
        )

        self.lcdDetectorStageAngle = QLCDNumber(self.gbDetectorStage)
        self.lcdDetectorStageAngle.setObjectName("lcdDetectorStageAngle")
        sizePolicy2.setHeightForWidth(
            self.lcdDetectorStageAngle.sizePolicy().hasHeightForWidth()
        )
        self.lcdDetectorStageAngle.setSizePolicy(sizePolicy2)
        self.lcdDetectorStageAngle.setMinimumSize(QSize(0, 26))
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

        self.formDetectorStage.setWidget(
            2, QFormLayout.ItemRole.SpanningRole, self.btnDetectorStageZero
        )

        self.verticalLayout_2.addWidget(self.gbDetectorStage)

        self.verticalSpacer_2 = QSpacerItem(
            20, 8, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed
        )

        self.verticalLayout_2.addItem(self.verticalSpacer_2)

        self.gbDetector = QGroupBox(self.centralwidget)
        self.gbDetector.setObjectName("gbDetector")
        self.gbDetector.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.gbDetector.sizePolicy().hasHeightForWidth())
        self.gbDetector.setSizePolicy(sizePolicy1)
        self.gbDetector.setMinimumSize(QSize(0, 0))
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
        self.formDetector.setVerticalSpacing(6)
        self.lblDetectorStatus = QLabel(self.gbDetector)
        self.lblDetectorStatus.setObjectName("lblDetectorStatus")
        sizePolicy2.setHeightForWidth(
            self.lblDetectorStatus.sizePolicy().hasHeightForWidth()
        )
        self.lblDetectorStatus.setSizePolicy(sizePolicy2)
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
        self.ledDetectorStatus.setMinimumSize(QSize(16, 16))
        self.ledDetectorStatus.setMaximumSize(QSize(16, 16))
        self.ledDetectorStatus.setStyleSheet(
            "background-color: rgb(255, 11, 3); border: 0px; padding: 3px; border-radius: 8px"
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

        self.formDetector.setWidget(
            1, QFormLayout.ItemRole.LabelRole, self.lblDetectorVoltage
        )

        self.lcdDetectorVoltage = QLCDNumber(self.gbDetector)
        self.lcdDetectorVoltage.setObjectName("lcdDetectorVoltage")
        sizePolicy2.setHeightForWidth(
            self.lcdDetectorVoltage.sizePolicy().hasHeightForWidth()
        )
        self.lcdDetectorVoltage.setSizePolicy(sizePolicy2)
        self.lcdDetectorVoltage.setMinimumSize(QSize(0, 26))
        self.lcdDetectorVoltage.setLineWidth(2)
        self.lcdDetectorVoltage.setDigitCount(8)

        self.formDetector.setWidget(
            1, QFormLayout.ItemRole.FieldRole, self.lcdDetectorVoltage
        )

        self.lblGainLabel = QLabel(self.gbDetector)
        self.lblGainLabel.setObjectName("lblGainLabel")
        sizePolicy.setHeightForWidth(self.lblGainLabel.sizePolicy().hasHeightForWidth())
        self.lblGainLabel.setSizePolicy(sizePolicy)

        self.formDetector.setWidget(
            2, QFormLayout.ItemRole.LabelRole, self.lblGainLabel
        )

        self.hlGainButtons = QHBoxLayout()
        self.hlGainButtons.setSpacing(2)
        self.hlGainButtons.setObjectName("hlGainButtons")
        self.btnGain1 = QPushButton(self.gbDetector)
        self.gainButtonGroup = QButtonGroup(MainWindow)
        self.gainButtonGroup.setObjectName("gainButtonGroup")
        self.gainButtonGroup.addButton(self.btnGain1)
        self.btnGain1.setObjectName("btnGain1")
        self.btnGain1.setMaximumSize(QSize(36, 16777215))
        self.btnGain1.setCheckable(True)

        self.hlGainButtons.addWidget(self.btnGain1)

        self.btnGain2 = QPushButton(self.gbDetector)
        self.gainButtonGroup.addButton(self.btnGain2)
        self.btnGain2.setObjectName("btnGain2")
        self.btnGain2.setMaximumSize(QSize(36, 16777215))
        self.btnGain2.setCheckable(True)

        self.hlGainButtons.addWidget(self.btnGain2)

        self.btnGain3 = QPushButton(self.gbDetector)
        self.gainButtonGroup.addButton(self.btnGain3)
        self.btnGain3.setObjectName("btnGain3")
        self.btnGain3.setMaximumSize(QSize(36, 16777215))
        self.btnGain3.setCheckable(True)

        self.hlGainButtons.addWidget(self.btnGain3)

        self.btnGain4 = QPushButton(self.gbDetector)
        self.gainButtonGroup.addButton(self.btnGain4)
        self.btnGain4.setObjectName("btnGain4")
        self.btnGain4.setMaximumSize(QSize(36, 16777215))
        self.btnGain4.setCheckable(True)

        self.hlGainButtons.addWidget(self.btnGain4)

        self.gainSpacer = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.hlGainButtons.addItem(self.gainSpacer)

        self.formDetector.setLayout(
            2, QFormLayout.ItemRole.FieldRole, self.hlGainButtons
        )

        self.lblWattage = QLabel(self.gbDetector)
        self.lblWattage.setObjectName("lblWattage")
        sizePolicy.setHeightForWidth(self.lblWattage.sizePolicy().hasHeightForWidth())
        self.lblWattage.setSizePolicy(sizePolicy)

        self.formDetector.setWidget(3, QFormLayout.ItemRole.LabelRole, self.lblWattage)

        self.lcdWattage = QLCDNumber(self.gbDetector)
        self.lcdWattage.setObjectName("lcdWattage")
        sizePolicy2.setHeightForWidth(self.lcdWattage.sizePolicy().hasHeightForWidth())
        self.lcdWattage.setSizePolicy(sizePolicy2)
        self.lcdWattage.setMinimumSize(QSize(0, 26))
        self.lcdWattage.setLineWidth(2)
        self.lcdWattage.setDigitCount(10)

        self.formDetector.setWidget(3, QFormLayout.ItemRole.FieldRole, self.lcdWattage)

        self.verticalLayout_2.addWidget(self.gbDetector)

        self.gbPowerCal = QGroupBox(self.centralwidget)
        self.gbPowerCal.setObjectName("gbPowerCal")
        sizePolicy.setHeightForWidth(self.gbPowerCal.sizePolicy().hasHeightForWidth())
        self.gbPowerCal.setSizePolicy(sizePolicy)
        self.gbPowerCal.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.vboxPowerCal = QVBoxLayout(self.gbPowerCal)
        self.vboxPowerCal.setSpacing(4)
        self.vboxPowerCal.setObjectName("vboxPowerCal")
        self.vboxPowerCal.setContentsMargins(6, 4, 6, 6)
        self.cbProfile = QComboBox(self.gbPowerCal)
        self.cbProfile.setObjectName("cbProfile")
        sizePolicy4 = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.cbProfile.sizePolicy().hasHeightForWidth())
        self.cbProfile.setSizePolicy(sizePolicy4)

        self.vboxPowerCal.addWidget(self.cbProfile)

        self.hlProfileButtons = QHBoxLayout()
        self.hlProfileButtons.setObjectName("hlProfileButtons")
        self.btnReloadProfiles = QPushButton(self.gbPowerCal)
        self.btnReloadProfiles.setObjectName("btnReloadProfiles")

        self.hlProfileButtons.addWidget(self.btnReloadProfiles)

        self.btnOpenCalibration = QPushButton(self.gbPowerCal)
        self.btnOpenCalibration.setObjectName("btnOpenCalibration")

        self.hlProfileButtons.addWidget(self.btnOpenCalibration)

        self.vboxPowerCal.addLayout(self.hlProfileButtons)

        self.verticalLayout_2.addWidget(self.gbPowerCal)

        self.verticalSpacer = QSpacerItem(
            20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.gbSave = QGroupBox(self.centralwidget)
        self.gbSave.setObjectName("gbSave")
        sizePolicy5 = QSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred
        )
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.gbSave.sizePolicy().hasHeightForWidth())
        self.gbSave.setSizePolicy(sizePolicy5)
        self.gbSave.setMinimumSize(QSize(0, 0))
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
        sizePolicy6 = QSizePolicy(
            QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed
        )
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(
            self.cbGroupLetter.sizePolicy().hasHeightForWidth()
        )
        self.cbGroupLetter.setSizePolicy(sizePolicy6)
        self.cbGroupLetter.setMaxCount(24)
        self.cbGroupLetter.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        self.formSave.setWidget(0, QFormLayout.ItemRole.FieldRole, self.cbGroupLetter)

        self.lblSuffix = QLabel(self.gbSave)
        self.lblSuffix.setObjectName("lblSuffix")

        self.formSave.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lblSuffix)

        self.leSuffix = QLineEdit(self.gbSave)
        self.leSuffix.setObjectName("leSuffix")
        sizePolicy6.setHeightForWidth(self.leSuffix.sizePolicy().hasHeightForWidth())
        self.leSuffix.setSizePolicy(sizePolicy6)
        self.leSuffix.setText("")
        self.leSuffix.setMaxLength(20)

        self.formSave.setWidget(1, QFormLayout.ItemRole.FieldRole, self.leSuffix)

        self.verticalLayout.addLayout(self.formSave)

        self.btnSave = QPushButton(self.gbSave)
        self.btnSave.setObjectName("btnSave")
        self.btnSave.setEnabled(False)
        sizePolicy7 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy7.setHorizontalStretch(0)
        sizePolicy7.setVerticalStretch(0)
        sizePolicy7.setHeightForWidth(self.btnSave.sizePolicy().hasHeightForWidth())
        self.btnSave.setSizePolicy(sizePolicy7)
        self.btnSave.setMinimumSize(QSize(100, 24))
        self.btnSave.setMaximumSize(QSize(1000, 32))

        self.verticalLayout.addWidget(self.btnSave)

        self.verticalLayout_2.addWidget(self.gbSave)

        self.hlMeasurementControls = QHBoxLayout()
        self.hlMeasurementControls.setObjectName("hlMeasurementControls")
        self.hlMeasurementControls.setContentsMargins(2, 2, 2, 2)
        self.btnStartMeasurement = QPushButton(self.centralwidget)
        self.btnStartMeasurement.setObjectName("btnStartMeasurement")
        self.btnStartMeasurement.setEnabled(False)
        self.btnStartMeasurement.setMinimumSize(QSize(60, 24))
        self.btnStartMeasurement.setMaximumSize(QSize(500, 32))

        self.hlMeasurementControls.addWidget(self.btnStartMeasurement)

        self.btnStopMeasurement = QPushButton(self.centralwidget)
        self.btnStopMeasurement.setObjectName("btnStopMeasurement")
        self.btnStopMeasurement.setEnabled(False)
        self.btnStopMeasurement.setMinimumSize(QSize(60, 24))
        self.btnStopMeasurement.setMaximumSize(QSize(500, 32))

        self.hlMeasurementControls.addWidget(self.btnStopMeasurement)

        self.lineMeasurementControls = QFrame(self.centralwidget)
        self.lineMeasurementControls.setObjectName("lineMeasurementControls")
        self.lineMeasurementControls.setFrameShape(QFrame.Shape.VLine)
        self.lineMeasurementControls.setFrameShadow(QFrame.Shadow.Sunken)

        self.hlMeasurementControls.addWidget(self.lineMeasurementControls)

        self.btnResetMeasurement = QPushButton(self.centralwidget)
        self.btnResetMeasurement.setObjectName("btnResetMeasurement")
        self.btnResetMeasurement.setEnabled(False)

        self.hlMeasurementControls.addWidget(self.btnResetMeasurement)

        self.verticalLayout_2.addLayout(self.hlMeasurementControls)

        self.verticalLayout_2.setStretch(8, 1)

        self.gridLayout_5.addLayout(self.verticalLayout_2, 1, 0, 1, 1)

        self.line = QFrame(self.centralwidget)
        self.line.setObjectName("line")
        self.line.setFrameShadow(QFrame.Shadow.Plain)
        self.line.setFrameShape(QFrame.Shape.VLine)

        self.gridLayout_5.addWidget(self.line, 1, 1, 1, 1)

        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")

        self.gridLayout_5.addWidget(self.tabWidget, 1, 2, 1, 1)

        self.gridLayout_5.setRowStretch(1, 1)
        self.gridLayout_5.setColumnStretch(2, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.dockEventLog = QDockWidget(MainWindow)
        self.dockEventLog.setObjectName("dockEventLog")
        self.eventLogPanel = EventLogPanel()
        self.eventLogPanel.setObjectName("eventLogPanel")
        self.dockEventLog.setWidget(self.eventLogPanel)
        MainWindow.addDockWidget(
            Qt.DockWidgetArea.BottomDockWidgetArea, self.dockEventLog
        )
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        self.menubar.setGeometry(QRect(0, 0, 900, 22))
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
        self.menuEinstellungen.addAction(self.actionLogWindow)
        self.menuEinstellungen.addAction(self.actionEventLog)
        self.menuEinstellungen.addAction(self.actionPowerCalibration)
        self.menuEinstellungen.addAction(self.actionAutoPowerCalibration)

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
        self.actionLogWindow.setText(
            QCoreApplication.translate("MainWindow", "Log-Ausgabe anzeigen", None)
        )
        self.actionPowerCalibration.setText(
            QCoreApplication.translate(
                "MainWindow", "Leistungskalibrierung\u2026", None
            )
        )
        self.actionEventLog.setText(
            QCoreApplication.translate("MainWindow", "Ereignisprotokoll anzeigen", None)
        )
        self.actionAutoPowerCalibration.setText(
            QCoreApplication.translate(
                "MainWindow", "Automatische Leistungskalibrierung\u2026", None
            )
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
        self.lblSampleStatusValue.setText("")
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
        self.lblDetectorStageStatusValue.setText("")
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
        self.lblDetectorStatusValue.setText("")
        self.ledDetectorStatus.setText("")
        self.lblDetectorVoltage.setText(
            QCoreApplication.translate("MainWindow", "Spannung (V)", None)
        )
        self.lblGainLabel.setText(
            QCoreApplication.translate("MainWindow", "PD-TIA Gain", None)
        )
        self.btnGain1.setText(QCoreApplication.translate("MainWindow", "1", None))
        self.btnGain2.setText(QCoreApplication.translate("MainWindow", "2", None))
        self.btnGain3.setText(QCoreApplication.translate("MainWindow", "3", None))
        self.btnGain4.setText(QCoreApplication.translate("MainWindow", "4", None))
        self.lblWattage.setText(
            QCoreApplication.translate("MainWindow", "Leistung (mW)", None)
        )
        self.gbPowerCal.setTitle(
            QCoreApplication.translate("MainWindow", "Detektor-Kalibrierung", None)
        )
        self.cbProfile.setPlaceholderText(
            QCoreApplication.translate(
                "MainWindow", "\u2014 Kein Profil geladen \u2014", None
            )
        )
        # if QT_CONFIG(tooltip)
        self.btnReloadProfiles.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Profil-Liste aus dem Verzeichnis neu einlesen", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnReloadProfiles.setText(
            QCoreApplication.translate("MainWindow", "Aktualisieren", None)
        )
        # if QT_CONFIG(tooltip)
        self.btnOpenCalibration.setToolTip(
            QCoreApplication.translate(
                "MainWindow", "Leistungskalibrierungstool \u00f6ffnen", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnOpenCalibration.setText(
            QCoreApplication.translate("MainWindow", "Kalibrierungstool\u2026", None)
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
                "MainWindow", "Auswahl der GP Praktikumsgruppe (Pflichtfeld)", None
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
        self.dockEventLog.setWindowTitle(
            QCoreApplication.translate("MainWindow", "Ereignisprotokoll", None)
        )
        self.menuEinstellungen.setTitle(
            QCoreApplication.translate("MainWindow", "Einstellungen", None)
        )

    # retranslateUi
