"""Tests for AcquisitionSettingsDialog.

CI runs with QT_QPA_PLATFORM=offscreen so no physical display is required.
"""

from polarisation_ui.core.models import AcquisitionSettings
from polarisation_ui.ui.dialogs.acq_settings import AcquisitionSettingsDialog


def _make_settings(**overrides) -> AcquisitionSettings:
    base = AcquisitionSettings(
        det_average_on=True,
        det_averages=7,
        samp_average_on=True,
        samp_averages=9,
        pdtia_average_on=False,
        pdtia_averages=11,
        sample_stage_inverted=False,
        spike_filter_enabled=True,
        spike_max_delta_deg=5.0,
    )
    for key, value in overrides.items():
        setattr(base, key, value)
    return base


def test_get_settings_preserves_pdtia_averaging(qtbot):
    """Regression test: get_settings() used to omit pdtia_average_on/pdtia_averages,
    silently resetting them to the dataclass defaults (True, 5) on every accept
    since the dialog has no widgets for them (same as sample_stage_inverted).
    """
    settings = _make_settings(pdtia_average_on=False, pdtia_averages=11)
    dialog = AcquisitionSettingsDialog(settings)
    qtbot.addWidget(dialog)

    result = dialog.get_settings()

    assert result.pdtia_average_on is False
    assert result.pdtia_averages == 11


def test_get_settings_preserves_sample_stage_inverted(qtbot):
    settings = _make_settings(sample_stage_inverted=False)
    dialog = AcquisitionSettingsDialog(settings)
    qtbot.addWidget(dialog)

    result = dialog.get_settings()

    assert result.sample_stage_inverted is False


def test_get_settings_reflects_form_edits(qtbot):
    settings = _make_settings()
    dialog = AcquisitionSettingsDialog(settings)
    qtbot.addWidget(dialog)

    dialog.ui.det_averages.setValue(3)
    dialog.ui.samp_averageOn.setChecked(False)

    result = dialog.get_settings()

    assert result.det_averages == 3
    assert result.samp_average_on is False
