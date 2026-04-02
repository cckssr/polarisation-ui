"""
Acquisition Settings Dialog.

Wraps the Qt Designer UI (acq_settings_ui.py) and provides
a clean interface to read/write AcquisitionSettings values.

Settings changed here apply only to the current session;
nothing is written back to config.json.
"""

from PySide6.QtWidgets import QDialog

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
        self._apply_settings(settings)

    def _apply_settings(self, settings: AcquisitionSettings) -> None:
        """Populate form widgets from an AcquisitionSettings instance."""
        self.ui.det_averageOn.setChecked(settings.det_average_on)
        self.ui.det_averages.setValue(settings.det_averages)
        self.ui.samp_averageOn.setChecked(settings.samp_average_on)
        self.ui.samp_averages.setValue(settings.samp_averages)

    def get_settings(self) -> AcquisitionSettings:
        """Return an AcquisitionSettings instance reflecting the current form state."""
        return AcquisitionSettings(
            det_average_on=self.ui.det_averageOn.isChecked(),
            det_averages=self.ui.det_averages.value(),
            samp_average_on=self.ui.samp_averageOn.isChecked(),
            samp_averages=self.ui.samp_averages.value(),
        )
