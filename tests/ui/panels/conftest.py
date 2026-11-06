"""Fixtures for the panel tests: each panel on its own, configured from the packaged config."""

from __future__ import annotations

import pytest

from polarisation_ui.infrastructure.config import AppConfig
from polarisation_ui.ui.widgets.panels.arduino_panel import ArduinoPanel
from polarisation_ui.ui.widgets.panels.detector_panel import DetectorPanel
from polarisation_ui.ui.widgets.panels.kdc_panel import KdcPanel
from polarisation_ui.ui.widgets.panels.measurement_panel import MeasurementPanel
from polarisation_ui.ui.widgets.panels.readout_panel import ReadoutPanel
from polarisation_ui.ui.widgets.panels.save_panel import SavePanel
from polarisation_ui.ui.widgets.panels.stage_panel import StagePanel


def _shown(qtbot, panel, config: AppConfig, *args):
    qtbot.addWidget(panel)
    panel.apply_config(config, *args)
    panel.show()
    return panel


@pytest.fixture
def arduino(qtbot, config: AppConfig) -> ArduinoPanel:
    return _shown(qtbot, ArduinoPanel(), config)


@pytest.fixture
def sample_stage(qtbot, config: AppConfig) -> StagePanel:
    return _shown(qtbot, StagePanel(), config, "sample")


@pytest.fixture
def detector_stage(qtbot, config: AppConfig) -> StagePanel:
    return _shown(qtbot, StagePanel(), config, "detector")


@pytest.fixture
def kdc(qtbot, config: AppConfig) -> KdcPanel:
    return _shown(qtbot, KdcPanel(), config)


@pytest.fixture
def detector(qtbot, config: AppConfig) -> DetectorPanel:
    return _shown(qtbot, DetectorPanel(), config)


@pytest.fixture
def readout(qtbot, config: AppConfig) -> ReadoutPanel:
    return _shown(qtbot, ReadoutPanel(), config)


@pytest.fixture
def measurement(qtbot, config: AppConfig) -> MeasurementPanel:
    return _shown(qtbot, MeasurementPanel(), config)


@pytest.fixture
def save(qtbot, config: AppConfig) -> SavePanel:
    return _shown(qtbot, SavePanel(), config)
