"""Acquisition Settings Dialog.

Wraps the Qt Designer UI (ui_acq_settings.py) and provides
a clean interface to read/write AcquisitionSettings values.

Settings changed here apply only to the current session;
nothing is written back to config.json.
"""

from __future__ import annotations

from PySide6.QtWidgets import QDialog

from polarisation_ui.core.models import AcquisitionSettings
from polarisation_ui.infrastructure.config import AppConfig, default_config
from polarisation_ui.pyqt.ui_acq_settings import Ui_Dialog
from polarisation_ui.ui.i18n import apply_strings


class AcquisitionSettingsDialog(QDialog):
    """Dialog for editing acquisition averaging settings."""

    def __init__(
        self,
        settings: AcquisitionSettings,
        parent=None,
        config: AppConfig | None = None,
    ) -> None:
        """Initialize the dialog with current settings.

        Args:
            settings: Current session settings used to pre-populate the form.
            parent: Parent widget (MainWindow); passed to QDialog for modality.
            config: Application configuration supplying the German texts (default: packaged config).
        """
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        config = config or default_config()
        apply_strings(self, config.section("ui").get("acq_settings", {}))
        self.ui.checkSpikeFilter.toggled.connect(self.ui.spinSpikeMaxDelta.setEnabled)
        self._original_settings = settings
        self._apply_settings(settings)

    def _apply_settings(self, settings: AcquisitionSettings) -> None:
        """Populate form widgets from an AcquisitionSettings instance."""
        self.ui.checkDetAverage.setChecked(settings.det_average_on)
        self.ui.spinDetAverages.setValue(settings.det_averages)
        self.ui.checkSampAverage.setChecked(settings.samp_average_on)
        self.ui.spinSampAverages.setValue(settings.samp_averages)
        self.ui.checkSpikeFilter.setChecked(settings.spike_filter_enabled)
        self.ui.spinSpikeMaxDelta.setValue(settings.spike_max_delta_deg)
        self.ui.spinSpikeMaxDelta.setEnabled(settings.spike_filter_enabled)

    def get_settings(self) -> AcquisitionSettings:
        """Return an AcquisitionSettings instance reflecting the current form state."""
        return AcquisitionSettings(
            det_average_on=self.ui.checkDetAverage.isChecked(),
            det_averages=self.ui.spinDetAverages.value(),
            samp_average_on=self.ui.checkSampAverage.isChecked(),
            samp_averages=self.ui.spinSampAverages.value(),
            pdtia_average_on=self._original_settings.pdtia_average_on,
            pdtia_averages=self._original_settings.pdtia_averages,
            sample_stage_inverted=self._original_settings.sample_stage_inverted,
            spike_filter_enabled=self.ui.checkSpikeFilter.isChecked(),
            spike_max_delta_deg=self.ui.spinSpikeMaxDelta.value(),
        )
