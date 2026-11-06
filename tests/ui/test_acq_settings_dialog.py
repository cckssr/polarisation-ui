"""Tests for AcquisitionSettingsDialog.

CI runs with QT_QPA_PLATFORM=offscreen so no physical display is required.
"""

from PySide6.QtCore import QObject

from polarisation_ui.core.models import AcquisitionSettings
from polarisation_ui.infrastructure.config import default_config
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

    dialog.ui.spinDetAverages.setValue(3)
    dialog.ui.checkSampAverage.setChecked(False)

    result = dialog.get_settings()

    assert result.det_averages == 3
    assert result.samp_average_on is False


def test_the_dialog_shows_the_configured_german_strings(qtbot):
    dialog = AcquisitionSettingsDialog(_make_settings())
    qtbot.addWidget(dialog)

    assert dialog.windowTitle() == "Akquisitions-Einstellungen"
    assert dialog.ui.groupDetRot.title() == "Detektor-Rotationsstage"
    assert dialog.ui.groupSampRot.title() == "Sample-Rotationsstage"
    assert dialog.ui.groupSpikeFilter.title() == "Spike-Filter"
    assert dialog.ui.labelDetAverages.text() == "Anzahl Mittelwerte"
    assert dialog.ui.checkDetAverage.text() == "Mittelung aktiviert"
    assert dialog.ui.checkSpikeFilter.text() == "Spike-Filter aktivieren"
    assert dialog.ui.labelSpikeMaxDelta.text() == "Max. Winkelsprung"
    assert dialog.ui.spinSpikeMaxDelta.suffix() == " °/Poll"
    assert "Winkeländerung" in dialog.ui.spinSpikeMaxDelta.toolTip()


def test_every_acq_settings_key_resolves_to_a_child_widget(qtbot):
    dialog = AcquisitionSettingsDialog(_make_settings())
    qtbot.addWidget(dialog)
    strings = default_config().section("ui")["acq_settings"]

    for key in strings:
        name = key.partition("@")[0]
        if name == "self":
            continue
        assert dialog.findChild(QObject, name) is not None, f"unknown object name in {key!r}"


def test_the_spike_max_delta_follows_the_spike_checkbox(qtbot):
    dialog = AcquisitionSettingsDialog(_make_settings(spike_filter_enabled=False))
    qtbot.addWidget(dialog)

    assert dialog.ui.spinSpikeMaxDelta.isEnabled() is False

    dialog.ui.checkSpikeFilter.setChecked(True)

    assert dialog.ui.spinSpikeMaxDelta.isEnabled() is True
