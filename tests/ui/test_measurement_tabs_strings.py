"""Malus, wave plate and Laser-Drift tabs: German strings and tunables come from config.json."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import QApplication, QScrollArea

from polarisation_ui.core.models import Frame
from polarisation_ui.infrastructure.config import AppConfig
from polarisation_ui.ui.widgets.malus_curve_plot import MalusCurvePlot
from polarisation_ui.ui.widgets.plot_tab_base import PlotTabBase
from polarisation_ui.ui.widgets.power_drift_plot import (
    PowerDriftAnglesPlot,
    PowerDriftIntensityPlot,
)
from polarisation_ui.ui.widgets.tabs.malus_tab import MalusTab
from polarisation_ui.ui.widgets.tabs.power_drift_tab import PowerDriftTab
from polarisation_ui.ui.widgets.tabs.waveplate_tab import WaveplateTab

TABS: list[tuple[type[PlotTabBase], str]] = [
    (MalusTab, "malus_tab"),
    (WaveplateTab, "waveplate_tab"),
    (PowerDriftTab, "power_drift_tab"),
]


def _build(qtbot, tab_class: type[PlotTabBase], config: AppConfig | None = None) -> PlotTabBase:
    tab = tab_class(config=config)
    tab.build()
    qtbot.addWidget(tab)
    return tab


def _frame(intensity: float = 0.5, power_W: float | None = None) -> Frame:
    return Frame(
        ts_ms=1000, sample_angle=10.0, detector_angle=20.0, intensity=intensity, power_W=power_W
    )


# -- every configured key resolves to a widget --------------------------------------------------


@pytest.mark.parametrize(("tab_class", "section"), TABS)
def test_every_object_key_of_the_form_names_a_child_widget(
    qtbot, config: AppConfig, tab_class: type[PlotTabBase], section: str
) -> None:
    tab = _build(qtbot, tab_class, config)
    for key in config.section("ui")[section]:
        name = key.partition("@")[0]
        if "_" in name:
            continue  # plain texts read by code
        assert tab.findChild(QObject, name) is not None, f"ui.{section}.{key} has no widget"


# -- German strings --------------------------------------------------------------------------


def test_the_malus_tab_shows_the_configured_german_texts(qtbot, config: AppConfig) -> None:
    tab = _build(qtbot, MalusTab, config)
    ui = tab._ui
    assert ui.buttonAdd.text() == "Punkt hinzufügen"
    assert ui.groupSweep.title() == "Automatischer Scan (KDC101)"
    assert ui.spinPolariser.suffix() == " °"
    assert "Analysatorwinkel" in ui.spinAnalyser.toolTip()
    headers = [ui.tablePoints.horizontalHeaderItem(i).text() for i in range(5)]
    assert headers == ["θ_A (°)", "θ_P (°)", "I (mV)", "P (µW)", "Gain"]


def test_the_waveplate_tab_shows_the_configured_german_texts(qtbot, config: AppConfig) -> None:
    tab = _build(qtbot, WaveplateTab, config)
    ui = tab._ui
    assert ui.checkWaveplatePlaced.text() == "Verzögerungsplatte eingesetzt"
    assert ui.groupSweep.title() == "Scan (KDC101)"
    assert ui.comboWaveplateType.itemText(0) == "λ/4 (QWP)"
    assert ui.comboWaveplateType.itemText(1) == "λ/2 (HWP)"
    headers = [ui.tablePoints.horizontalHeaderItem(i).text() for i in range(4)]
    assert headers == ["θ (°)", "I (V)", "P (µW)", "Gain"]


def test_the_power_drift_tab_shows_the_configured_german_texts(qtbot, config: AppConfig) -> None:
    tab = _build(qtbot, PowerDriftTab, config)
    ui = tab._ui
    assert ui.groupRuntime.title() == "Laufzeit"
    assert ui.labelScaleStart.text() == "0 min"
    assert ui.labelScaleEnd.text() == "60 min"
    assert "30 Minuten" in ui.labelHint.text()
    assert ui.buttonClear.text() == "Drift-Daten löschen"


def test_the_tab_texts_follow_an_overridden_config(qtbot, config: AppConfig) -> None:
    custom = config.with_overrides({"ui": {"malus_tab": {"buttonAdd": "Add point"}}})
    assert _build(qtbot, MalusTab, custom)._ui.buttonAdd.text() == "Add point"


# -- tab titles --------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("tab_class", "title"),
    [(MalusTab, "Malus"), (WaveplateTab, "Verzögerungsplatte"), (PowerDriftTab, "Laser-Drift")],
)
def test_the_tab_title_comes_from_ui_tabs(
    qtbot, config: AppConfig, tab_class: type[PlotTabBase], title: str
) -> None:
    assert tab_class.tab_title == title  # class access uses default_config()
    assert _build(qtbot, tab_class, config).tab_title == title


def test_the_tab_title_of_an_instance_uses_its_own_config(qtbot, config: AppConfig) -> None:
    custom = config.with_overrides({"ui": {"tabs": {"malus": "Malus-Gesetz"}}})
    assert _build(qtbot, MalusTab, custom).tab_title == "Malus-Gesetz"


# -- status messages and formats ------------------------------------------------------------


def test_the_malus_warning_text_comes_from_messages(qtbot, config: AppConfig) -> None:
    custom = config.with_overrides({"messages": {"tabs": {"malus_no_valid_intensity": "leer"}}})
    tab = _build(qtbot, MalusTab, custom)
    tab.on_measurement_started()
    messages: list[tuple[str, str]] = []
    tab.status_message.connect(lambda level, text: messages.append((level, text)))
    tab._add_point()
    assert messages == [("warning", "leer")]


def test_the_malus_scan_messages_fill_their_placeholders(qtbot, config: AppConfig) -> None:
    tab = _build(qtbot, MalusTab, config)
    messages: list[tuple[str, str]] = []
    tab.status_message.connect(lambda level, text: messages.append((level, text)))
    tab._on_sweep_progress(3, 8)
    tab._on_sweep_failed("boom")
    assert messages == [("info", "Scan: 3/8"), ("error", "Scan fehlgeschlagen: boom")]


def test_the_waveplate_messages_come_from_messages(qtbot, config: AppConfig) -> None:
    tab = _build(qtbot, WaveplateTab, config)
    messages: list[tuple[str, str]] = []
    tab.status_message.connect(lambda level, text: messages.append((level, text)))
    tab._delete_last_point()
    tab._on_sweep_progress(1, 2)
    tab._on_sweep_finished()
    assert messages == [
        ("warning", "Keine Punkte zum Löschen"),
        ("info", "Scan: 1/2"),
        ("info", "Scan abgeschlossen"),
    ]


def test_the_live_value_formats_come_from_config(qtbot, config: AppConfig) -> None:
    custom = config.with_overrides(
        {"ui": {"malus_tab": {"live_intensity": "{value} Volt", "live_power": "{value} Milliwatt"}}}
    )
    tab = _build(qtbot, MalusTab, custom)
    tab.on_frame(_frame(1.5, power_W=0.002))
    assert tab._ui.valueLiveIntensity.text().endswith(" Volt")
    assert tab._ui.valueLivePower.text() == "2.000 Milliwatt"


def test_the_power_drift_stat_and_delta_formats_come_from_config(qtbot, config: AppConfig) -> None:
    custom = config.with_overrides(
        {"ui": {"power_drift_tab": {"stat_voltage": "{value} Volt", "delta_angle": "{value} Grad"}}}
    )
    tab = _build(qtbot, PowerDriftTab, custom)
    tab.on_measurement_started()
    tab.on_frame(_frame(0.25))
    assert tab._ui.valueIntensityCurrent.text() == "0.25000 Volt"
    assert tab._ui.valueDeltaSample.text() == "+0.000 Grad"


# -- plots ---------------------------------------------------------------------------------------


def _axis(plot_widget, side: str) -> tuple[str, str]:
    axis = plot_widget.getAxis(side)
    return axis.labelText, axis.labelUnits


def test_the_malus_plot_axes_use_the_configured_labels(qtbot) -> None:
    plot = MalusCurvePlot()
    qtbot.addWidget(plot)
    assert _axis(plot._plot_widget, "bottom") == ("Analysatorwinkel", "°")
    assert _axis(plot._plot_widget, "left") == ("Intensität", "V")
    plot.add_point(10.0, 0.0, 0.5, power_W=0.001)
    assert _axis(plot._plot_widget, "left") == ("Leistung", "mW")


def test_the_waveplate_tab_labels_its_x_axis_with_the_plate_angle(qtbot, config: AppConfig) -> None:
    tab = _build(qtbot, WaveplateTab, config)
    assert _axis(tab._ui.intensityCurvePlot._plot_widget, "bottom") == ("Plattenwinkel", "°")


def test_the_malus_plot_follows_apply_config(qtbot, config: AppConfig) -> None:
    plot = MalusCurvePlot()
    qtbot.addWidget(plot)
    plot.add_point(10.0, 0.0, 0.5, power_W=0.001)
    custom = config.with_overrides(
        {"ui": {"plots": {"malus_curve_x_label": "Angle", "malus_curve_power_label": "Power"}}}
    )
    plot.apply_config(custom)
    assert _axis(plot._plot_widget, "bottom")[0] == "Angle"
    assert _axis(plot._plot_widget, "left")[0] == "Power"


def test_the_power_drift_plots_use_the_configured_labels(qtbot) -> None:
    intensity = PowerDriftIntensityPlot()
    angles = PowerDriftAnglesPlot()
    qtbot.addWidget(intensity)
    qtbot.addWidget(angles)
    assert _axis(intensity._plot_widget, "bottom") == ("Zeit", "min")
    assert _axis(intensity._plot_widget, "left") == ("Intensität", "V")
    assert _axis(angles._plot_widget, "left") == ("Winkel", "°")
    legend = angles._plot_widget.plotItem.legend
    assert legend.getLabel(angles._curve_sample).text == "Probenwinkel (θS)"
    assert legend.getLabel(angles._curve_detector).text == "Detektorwinkel (θD)"
    assert intensity._plot_widget.plotItem.legend.getLabel(intensity._curve).text == "Intensität"


def test_the_power_drift_plots_follow_apply_config(qtbot, config: AppConfig) -> None:
    angles = PowerDriftAnglesPlot()
    qtbot.addWidget(angles)
    custom = config.with_overrides(
        {"ui": {"plots": {"power_drift_legend_sample": "Sample", "power_drift_hour_marker": "60'"}}}
    )
    angles.apply_config(custom)
    legend = angles._plot_widget.plotItem.legend
    assert legend.getLabel(angles._curve_sample).text == "Sample"
    assert angles._marker.label.textItem.toPlainText() == "60'"


# -- side column -----------------------------------------------------------------------------------


@pytest.mark.parametrize(("tab_class", "section"), TABS)
def test_the_side_column_scrolls_vertically_only(
    qtbot, config: AppConfig, tab_class: type[PlotTabBase], section: str
) -> None:
    tab = _build(qtbot, tab_class, config)
    scroll = tab.findChild(QScrollArea, "scrollSide")
    assert scroll is not None
    assert scroll.horizontalScrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAlwaysOff
    assert scroll.minimumWidth() >= scroll.widget().minimumSizeHint().width()


@pytest.mark.parametrize(("tab_class", "section"), TABS)
def test_the_side_column_clips_nothing_horizontally(
    qtbot, config: AppConfig, tab_class: type[PlotTabBase], section: str
) -> None:
    tab = _build(qtbot, tab_class, config)
    tab.resize(1000, 700)
    tab.show()
    qtbot.waitExposed(tab)
    scroll = tab.findChild(QScrollArea, "scrollSide")
    assert scroll is not None
    for height in (700, 250):  # tall enough for no scrollbar, then a vertical scrollbar
        tab.resize(1000, height)
        QApplication.processEvents()
        assert scroll.widget().width() <= scroll.viewport().width()
        assert not scroll.horizontalScrollBar().isVisible()
