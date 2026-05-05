"""
Acquisition Settings Dialog.

Wraps the Qt Designer UI (acq_settings_ui.py) and provides
a clean interface to read/write AcquisitionSettings values.

Settings changed here apply only to the current session;
nothing is written back to config.json.
"""

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QLabel,
)

from polarisation_ui.pyqt.ui_acq_settings import Ui_Dialog
from polarisation_ui.core.models import AcquisitionSettings


class AcquisitionSettingsDialog(QDialog):
    """Dialog for editing acquisition averaging settings."""

    def __init__(self, settings: AcquisitionSettings, parent=None):
        """
        Args:
            settings: Current session settings used to pre-populate the form.
            parent: Parent widget (MainWindow); passed to QDialog for modality.
        """
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self._build_spike_filter_group()
        self._original_settings = settings
        self._apply_settings(settings)

    def _build_spike_filter_group(self) -> None:
        """Add spike-filter controls programmatically before the button box."""
        group = QGroupBox("Spike-Filter")
        form = QFormLayout(group)

        self._spike_enabled = QCheckBox("Spike-Filter aktivieren")
        form.addRow(self._spike_enabled)

        self._spike_max_delta = QDoubleSpinBox()
        self._spike_max_delta.setMinimum(1.0)
        self._spike_max_delta.setMaximum(180.0)
        self._spike_max_delta.setDecimals(1)
        self._spike_max_delta.setSingleStep(1.0)
        self._spike_max_delta.setSuffix(" °/Poll")
        self._spike_max_delta.setToolTip(
            "Maximale erlaubte Winkeländerung pro Abtastung (100 ms). "
            "Messungen mit größerer Änderung werden verworfen."
        )
        form.addRow(QLabel("Max. Winkelsprung"), self._spike_max_delta)

        # Insert before the button box (last item in the vertical layout)
        layout = self.layout()
        layout.insertWidget(layout.count() - 1, group)

        # Enable/disable the spinbox based on the checkbox state
        self._spike_enabled.toggled.connect(self._spike_max_delta.setEnabled)

    def _apply_settings(self, settings: AcquisitionSettings) -> None:
        """Populate form widgets from an AcquisitionSettings instance."""
        self.ui.det_averageOn.setChecked(settings.det_average_on)
        self.ui.det_averages.setValue(settings.det_averages)
        self.ui.samp_averageOn.setChecked(settings.samp_average_on)
        self.ui.samp_averages.setValue(settings.samp_averages)
        self._spike_enabled.setChecked(settings.spike_filter_enabled)
        self._spike_max_delta.setValue(settings.spike_max_delta_deg)
        self._spike_max_delta.setEnabled(settings.spike_filter_enabled)

    def get_settings(self) -> AcquisitionSettings:
        """Return an AcquisitionSettings instance reflecting the current form state."""
        return AcquisitionSettings(
            det_average_on=self.ui.det_averageOn.isChecked(),
            det_averages=self.ui.det_averages.value(),
            samp_average_on=self.ui.samp_averageOn.isChecked(),
            samp_averages=self.ui.samp_averages.value(),
            sample_stage_inverted=self._original_settings.sample_stage_inverted,
            spike_filter_enabled=self._spike_enabled.isChecked(),
            spike_max_delta_deg=self._spike_max_delta.value(),
        )
