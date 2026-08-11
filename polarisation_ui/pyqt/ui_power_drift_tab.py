# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'power_drift_tab.ui'
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
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from polarisation_ui.ui.widgets.power_drift_plot import (
    PowerDriftAnglesPlot,
    PowerDriftIntensityPlot,
)


class Ui_PowerDriftTab(object):
    def setupUi(self, PowerDriftTab):
        if not PowerDriftTab.objectName():
            PowerDriftTab.setObjectName("PowerDriftTab")
        PowerDriftTab.resize(959, 839)
        self.horizontalLayout = QHBoxLayout(PowerDriftTab)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 10, 0, 0)
        self.plotsContainer = QWidget(PowerDriftTab)
        self.plotsContainer.setObjectName("plotsContainer")
        self.plotsContainer.setMinimumSize(QSize(50, 0))
        self.plotsLayout = QVBoxLayout(self.plotsContainer)
        self.plotsLayout.setSpacing(4)
        self.plotsLayout.setObjectName("plotsLayout")
        self.plotsLayout.setContentsMargins(0, 0, 0, 0)
        self.intensityPlot = PowerDriftIntensityPlot(self.plotsContainer)
        self.intensityPlot.setObjectName("intensityPlot")

        self.plotsLayout.addWidget(self.intensityPlot)

        self.anglesPlot = PowerDriftAnglesPlot(self.plotsContainer)
        self.anglesPlot.setObjectName("anglesPlot")

        self.plotsLayout.addWidget(self.anglesPlot)

        self.plotsLayout.setStretch(0, 3)
        self.plotsLayout.setStretch(1, 2)

        self.horizontalLayout.addWidget(self.plotsContainer)

        self.controlsPanel = QWidget(PowerDriftTab)
        self.controlsPanel.setObjectName("controlsPanel")
        self.controlsLayout = QVBoxLayout(self.controlsPanel)
        self.controlsLayout.setSpacing(8)
        self.controlsLayout.setObjectName("controlsLayout")
        self.controlsLayout.setContentsMargins(4, 0, 0, 0)
        self.gbRuntime = QGroupBox(self.controlsPanel)
        self.gbRuntime.setObjectName("gbRuntime")
        self.runtimeLayout = QVBoxLayout(self.gbRuntime)
        self.runtimeLayout.setObjectName("runtimeLayout")
        self.runtimeLayout.setContentsMargins(6, 6, 6, 6)
        self.lblElapsed = QLabel(self.gbRuntime)
        self.lblElapsed.setObjectName("lblElapsed")
        self.lblElapsed.setStyleSheet("font-size: 22px; font-weight: bold;")
        self.lblElapsed.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.runtimeLayout.addWidget(self.lblElapsed)

        self.progressBar = QProgressBar(self.gbRuntime)
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setMaximumSize(QSize(16777215, 8))
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(3600)
        self.progressBar.setValue(0)
        self.progressBar.setTextVisible(False)

        self.runtimeLayout.addWidget(self.progressBar)

        self.lblScale = QLabel(self.gbRuntime)
        self.lblScale.setObjectName("lblScale")
        self.lblScale.setStyleSheet("font-size: 9px; color: #888;")
        self.lblScale.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.runtimeLayout.addWidget(self.lblScale)

        self.controlsLayout.addWidget(self.gbRuntime)

        self.gbIntensity = QGroupBox(self.controlsPanel)
        self.gbIntensity.setObjectName("gbIntensity")
        self.intensityForm = QFormLayout(self.gbIntensity)
        self.intensityForm.setObjectName("intensityForm")
        self.intensityForm.setVerticalSpacing(2)
        self.intensityForm.setContentsMargins(6, 4, 6, 6)
        self.lblICurrentLabel = QLabel(self.gbIntensity)
        self.lblICurrentLabel.setObjectName("lblICurrentLabel")

        self.intensityForm.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lblICurrentLabel)

        self.lblICurrent = QLabel(self.gbIntensity)
        self.lblICurrent.setObjectName("lblICurrent")

        self.intensityForm.setWidget(0, QFormLayout.ItemRole.FieldRole, self.lblICurrent)

        self.lblIMeanLabel = QLabel(self.gbIntensity)
        self.lblIMeanLabel.setObjectName("lblIMeanLabel")

        self.intensityForm.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lblIMeanLabel)

        self.lblIMean = QLabel(self.gbIntensity)
        self.lblIMean.setObjectName("lblIMean")

        self.intensityForm.setWidget(1, QFormLayout.ItemRole.FieldRole, self.lblIMean)

        self.lblIMinLabel = QLabel(self.gbIntensity)
        self.lblIMinLabel.setObjectName("lblIMinLabel")

        self.intensityForm.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lblIMinLabel)

        self.lblIMin = QLabel(self.gbIntensity)
        self.lblIMin.setObjectName("lblIMin")

        self.intensityForm.setWidget(2, QFormLayout.ItemRole.FieldRole, self.lblIMin)

        self.lblIMaxLabel = QLabel(self.gbIntensity)
        self.lblIMaxLabel.setObjectName("lblIMaxLabel")

        self.intensityForm.setWidget(3, QFormLayout.ItemRole.LabelRole, self.lblIMaxLabel)

        self.lblIMax = QLabel(self.gbIntensity)
        self.lblIMax.setObjectName("lblIMax")

        self.intensityForm.setWidget(3, QFormLayout.ItemRole.FieldRole, self.lblIMax)

        self.controlsLayout.addWidget(self.gbIntensity)

        self.gbAngleStability = QGroupBox(self.controlsPanel)
        self.gbAngleStability.setObjectName("gbAngleStability")
        self.angleForm = QFormLayout(self.gbAngleStability)
        self.angleForm.setObjectName("angleForm")
        self.angleForm.setVerticalSpacing(2)
        self.angleForm.setContentsMargins(6, 4, 6, 6)
        self.lblDeltaSampleLabel = QLabel(self.gbAngleStability)
        self.lblDeltaSampleLabel.setObjectName("lblDeltaSampleLabel")

        self.angleForm.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lblDeltaSampleLabel)

        self.lblDeltaSample = QLabel(self.gbAngleStability)
        self.lblDeltaSample.setObjectName("lblDeltaSample")

        self.angleForm.setWidget(0, QFormLayout.ItemRole.FieldRole, self.lblDeltaSample)

        self.lblDeltaDetectorLabel = QLabel(self.gbAngleStability)
        self.lblDeltaDetectorLabel.setObjectName("lblDeltaDetectorLabel")

        self.angleForm.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lblDeltaDetectorLabel)

        self.lblDeltaDetector = QLabel(self.gbAngleStability)
        self.lblDeltaDetector.setObjectName("lblDeltaDetector")

        self.angleForm.setWidget(1, QFormLayout.ItemRole.FieldRole, self.lblDeltaDetector)

        self.controlsLayout.addWidget(self.gbAngleStability)

        self.lblHint = QLabel(self.controlsPanel)
        self.lblHint.setObjectName("lblHint")
        self.lblHint.setStyleSheet("color: #555; font-size: 10px;")
        self.lblHint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lblHint.setWordWrap(True)

        self.controlsLayout.addWidget(self.lblHint)

        self.verticalSpacer = QSpacerItem(
            20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.controlsLayout.addItem(self.verticalSpacer)

        self.btnClear = QPushButton(self.controlsPanel)
        self.btnClear.setObjectName("btnClear")
        self.btnClear.setEnabled(False)

        self.controlsLayout.addWidget(self.btnClear)

        self.horizontalLayout.addWidget(self.controlsPanel)

        self.horizontalLayout.setStretch(0, 1)

        self.retranslateUi(PowerDriftTab)

        QMetaObject.connectSlotsByName(PowerDriftTab)

    # setupUi

    def retranslateUi(self, PowerDriftTab):
        self.gbRuntime.setTitle(QCoreApplication.translate("PowerDriftTab", "Laufzeit", None))
        self.lblElapsed.setText(QCoreApplication.translate("PowerDriftTab", "00:00:00", None))
        self.lblScale.setText(
            QCoreApplication.translate("PowerDriftTab", "0 min                        60 min", None)
        )
        self.gbIntensity.setTitle(
            QCoreApplication.translate("PowerDriftTab", "Intensit\u00e4t", None)
        )
        self.lblICurrentLabel.setText(QCoreApplication.translate("PowerDriftTab", "Aktuell:", None))
        self.lblICurrent.setText(QCoreApplication.translate("PowerDriftTab", "\u2014", None))
        self.lblIMeanLabel.setText(QCoreApplication.translate("PowerDriftTab", "Mittel:", None))
        self.lblIMean.setText(QCoreApplication.translate("PowerDriftTab", "\u2014", None))
        self.lblIMinLabel.setText(QCoreApplication.translate("PowerDriftTab", "Min:", None))
        self.lblIMin.setText(QCoreApplication.translate("PowerDriftTab", "\u2014", None))
        self.lblIMaxLabel.setText(QCoreApplication.translate("PowerDriftTab", "Max:", None))
        self.lblIMax.setText(QCoreApplication.translate("PowerDriftTab", "\u2014", None))
        self.gbAngleStability.setTitle(
            QCoreApplication.translate("PowerDriftTab", "Winkelstabilit\u00e4t", None)
        )
        self.lblDeltaSampleLabel.setText(
            QCoreApplication.translate("PowerDriftTab", "\u0394\u03b8S:", None)
        )
        self.lblDeltaSample.setText(QCoreApplication.translate("PowerDriftTab", "\u2014", None))
        self.lblDeltaDetectorLabel.setText(
            QCoreApplication.translate("PowerDriftTab", "\u0394\u03b8D:", None)
        )
        self.lblDeltaDetector.setText(QCoreApplication.translate("PowerDriftTab", "\u2014", None))
        self.lblHint.setText(
            QCoreApplication.translate(
                "PowerDriftTab",
                "<i>Laser mindestens<br><b>30 Minuten</b> vor der<br>Messung einschalten,<br>damit er thermisch<br>stabil wird.</i>",
                None,
            )
        )
        # if QT_CONFIG(tooltip)
        self.btnClear.setToolTip(
            QCoreApplication.translate(
                "PowerDriftTab",
                "Alle gesammelten Drift-Daten l\u00f6schen und die Zeitmessung neu starten",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.btnClear.setText(
            QCoreApplication.translate("PowerDriftTab", "Drift-Daten l\u00f6schen", None)
        )
        pass

    # retranslateUi
