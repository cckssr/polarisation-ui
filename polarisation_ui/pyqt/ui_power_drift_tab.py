# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'power_drift_tab.ui'
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
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
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

        self.scrollSide = QScrollArea(PowerDriftTab)
        self.scrollSide.setObjectName("scrollSide")
        self.scrollSide.setFrameShape(QFrame.Shape.NoFrame)
        self.scrollSide.setWidgetResizable(True)
        self.contentSide = QWidget()
        self.contentSide.setObjectName("contentSide")
        self.layoutSide = QVBoxLayout(self.contentSide)
        self.layoutSide.setSpacing(8)
        self.layoutSide.setObjectName("layoutSide")
        self.layoutSide.setContentsMargins(4, 0, 0, 0)
        self.groupRuntime = QGroupBox(self.contentSide)
        self.groupRuntime.setObjectName("groupRuntime")
        self.runtimeLayout = QVBoxLayout(self.groupRuntime)
        self.runtimeLayout.setObjectName("runtimeLayout")
        self.runtimeLayout.setContentsMargins(6, 6, 6, 6)
        self.valueElapsed = QLabel(self.groupRuntime)
        self.valueElapsed.setObjectName("valueElapsed")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.valueElapsed.setFont(font)
        self.valueElapsed.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.runtimeLayout.addWidget(self.valueElapsed)

        self.progressBar = QProgressBar(self.groupRuntime)
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setMaximumSize(QSize(16777215, 8))
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(3600)
        self.progressBar.setValue(0)
        self.progressBar.setTextVisible(False)

        self.runtimeLayout.addWidget(self.progressBar)

        self.layoutScale = QHBoxLayout()
        self.layoutScale.setObjectName("layoutScale")
        self.labelScaleStart = QLabel(self.groupRuntime)
        self.labelScaleStart.setObjectName("labelScaleStart")
        font1 = QFont()
        font1.setPointSize(7)
        self.labelScaleStart.setFont(font1)
        self.labelScaleStart.setStyleSheet("color: palette(placeholder-text);")
        self.labelScaleStart.setAlignment(
            Qt.AlignmentFlag.AlignLeading
            | Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.layoutScale.addWidget(self.labelScaleStart)

        self.labelScaleEnd = QLabel(self.groupRuntime)
        self.labelScaleEnd.setObjectName("labelScaleEnd")
        self.labelScaleEnd.setFont(font1)
        self.labelScaleEnd.setStyleSheet("color: palette(placeholder-text);")
        self.labelScaleEnd.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignTrailing
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.layoutScale.addWidget(self.labelScaleEnd)

        self.runtimeLayout.addLayout(self.layoutScale)

        self.layoutSide.addWidget(self.groupRuntime)

        self.groupIntensity = QGroupBox(self.contentSide)
        self.groupIntensity.setObjectName("groupIntensity")
        self.intensityForm = QFormLayout(self.groupIntensity)
        self.intensityForm.setObjectName("intensityForm")
        self.intensityForm.setVerticalSpacing(2)
        self.intensityForm.setContentsMargins(6, 4, 6, 6)
        self.labelIntensityCurrent = QLabel(self.groupIntensity)
        self.labelIntensityCurrent.setObjectName("labelIntensityCurrent")

        self.intensityForm.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelIntensityCurrent)

        self.valueIntensityCurrent = QLabel(self.groupIntensity)
        self.valueIntensityCurrent.setObjectName("valueIntensityCurrent")

        self.intensityForm.setWidget(0, QFormLayout.ItemRole.FieldRole, self.valueIntensityCurrent)

        self.labelIntensityMean = QLabel(self.groupIntensity)
        self.labelIntensityMean.setObjectName("labelIntensityMean")

        self.intensityForm.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelIntensityMean)

        self.valueIntensityMean = QLabel(self.groupIntensity)
        self.valueIntensityMean.setObjectName("valueIntensityMean")

        self.intensityForm.setWidget(1, QFormLayout.ItemRole.FieldRole, self.valueIntensityMean)

        self.labelIntensityMin = QLabel(self.groupIntensity)
        self.labelIntensityMin.setObjectName("labelIntensityMin")

        self.intensityForm.setWidget(2, QFormLayout.ItemRole.LabelRole, self.labelIntensityMin)

        self.valueIntensityMin = QLabel(self.groupIntensity)
        self.valueIntensityMin.setObjectName("valueIntensityMin")

        self.intensityForm.setWidget(2, QFormLayout.ItemRole.FieldRole, self.valueIntensityMin)

        self.labelIntensityMax = QLabel(self.groupIntensity)
        self.labelIntensityMax.setObjectName("labelIntensityMax")

        self.intensityForm.setWidget(3, QFormLayout.ItemRole.LabelRole, self.labelIntensityMax)

        self.valueIntensityMax = QLabel(self.groupIntensity)
        self.valueIntensityMax.setObjectName("valueIntensityMax")

        self.intensityForm.setWidget(3, QFormLayout.ItemRole.FieldRole, self.valueIntensityMax)

        self.layoutSide.addWidget(self.groupIntensity)

        self.groupAngleStability = QGroupBox(self.contentSide)
        self.groupAngleStability.setObjectName("groupAngleStability")
        self.angleForm = QFormLayout(self.groupAngleStability)
        self.angleForm.setObjectName("angleForm")
        self.angleForm.setVerticalSpacing(2)
        self.angleForm.setContentsMargins(6, 4, 6, 6)
        self.labelDeltaSample = QLabel(self.groupAngleStability)
        self.labelDeltaSample.setObjectName("labelDeltaSample")

        self.angleForm.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelDeltaSample)

        self.valueDeltaSample = QLabel(self.groupAngleStability)
        self.valueDeltaSample.setObjectName("valueDeltaSample")

        self.angleForm.setWidget(0, QFormLayout.ItemRole.FieldRole, self.valueDeltaSample)

        self.labelDeltaDetector = QLabel(self.groupAngleStability)
        self.labelDeltaDetector.setObjectName("labelDeltaDetector")

        self.angleForm.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelDeltaDetector)

        self.valueDeltaDetector = QLabel(self.groupAngleStability)
        self.valueDeltaDetector.setObjectName("valueDeltaDetector")

        self.angleForm.setWidget(1, QFormLayout.ItemRole.FieldRole, self.valueDeltaDetector)

        self.layoutSide.addWidget(self.groupAngleStability)

        self.labelHint = QLabel(self.contentSide)
        self.labelHint.setObjectName("labelHint")
        font2 = QFont()
        font2.setPointSize(8)
        self.labelHint.setFont(font2)
        self.labelHint.setStyleSheet("color: palette(placeholder-text);")
        self.labelHint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.labelHint.setWordWrap(True)

        self.layoutSide.addWidget(self.labelHint)

        self.verticalSpacer = QSpacerItem(
            20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.layoutSide.addItem(self.verticalSpacer)

        self.buttonClear = QPushButton(self.contentSide)
        self.buttonClear.setObjectName("buttonClear")
        self.buttonClear.setEnabled(False)

        self.layoutSide.addWidget(self.buttonClear)

        self.scrollSide.setWidget(self.contentSide)

        self.horizontalLayout.addWidget(self.scrollSide)

        self.horizontalLayout.setStretch(0, 1)

        self.retranslateUi(PowerDriftTab)

        QMetaObject.connectSlotsByName(PowerDriftTab)

    # setupUi

    def retranslateUi(self, PowerDriftTab):
        self.groupRuntime.setTitle(QCoreApplication.translate("PowerDriftTab", "Laufzeit", None))
        self.valueElapsed.setText(QCoreApplication.translate("PowerDriftTab", "00:00:00", None))
        self.labelScaleStart.setText(QCoreApplication.translate("PowerDriftTab", "0 min", None))
        self.labelScaleEnd.setText(QCoreApplication.translate("PowerDriftTab", "60 min", None))
        self.groupIntensity.setTitle(
            QCoreApplication.translate("PowerDriftTab", "Intensit\u00e4t", None)
        )
        self.labelIntensityCurrent.setText(
            QCoreApplication.translate("PowerDriftTab", "Aktuell:", None)
        )
        self.valueIntensityCurrent.setText(
            QCoreApplication.translate("PowerDriftTab", "\u2014", None)
        )
        self.labelIntensityMean.setText(
            QCoreApplication.translate("PowerDriftTab", "Mittel:", None)
        )
        self.valueIntensityMean.setText(QCoreApplication.translate("PowerDriftTab", "\u2014", None))
        self.labelIntensityMin.setText(QCoreApplication.translate("PowerDriftTab", "Min:", None))
        self.valueIntensityMin.setText(QCoreApplication.translate("PowerDriftTab", "\u2014", None))
        self.labelIntensityMax.setText(QCoreApplication.translate("PowerDriftTab", "Max:", None))
        self.valueIntensityMax.setText(QCoreApplication.translate("PowerDriftTab", "\u2014", None))
        self.groupAngleStability.setTitle(
            QCoreApplication.translate("PowerDriftTab", "Winkelstabilit\u00e4t", None)
        )
        self.labelDeltaSample.setText(
            QCoreApplication.translate("PowerDriftTab", "\u0394\u03b8S:", None)
        )
        self.valueDeltaSample.setText(QCoreApplication.translate("PowerDriftTab", "\u2014", None))
        self.labelDeltaDetector.setText(
            QCoreApplication.translate("PowerDriftTab", "\u0394\u03b8D:", None)
        )
        self.valueDeltaDetector.setText(QCoreApplication.translate("PowerDriftTab", "\u2014", None))
        self.labelHint.setText(
            QCoreApplication.translate(
                "PowerDriftTab",
                "<i>Laser mindestens<br><b>30 Minuten</b> vor der<br>Messung einschalten,<br>damit er thermisch<br>stabil wird.</i>",
                None,
            )
        )
        # if QT_CONFIG(tooltip)
        self.buttonClear.setToolTip(
            QCoreApplication.translate(
                "PowerDriftTab",
                "Alle gesammelten Drift-Daten l\u00f6schen und die Zeitmessung neu starten",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.buttonClear.setText(
            QCoreApplication.translate("PowerDriftTab", "Drift-Daten l\u00f6schen", None)
        )
        pass

    # retranslateUi
