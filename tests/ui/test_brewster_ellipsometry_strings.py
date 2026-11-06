"""Configured strings, Designer wiring and side columns of the Brewster / Ellipsometry tabs."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QLabel

from polarisation_ui.core.models import Frame
from polarisation_ui.infrastructure.config import AppConfig
from polarisation_ui.ui.widgets.plot_tab_base import PlotTabBase
from polarisation_ui.ui.widgets.tabs.brewster_tab import BrewsterTab
from polarisation_ui.ui.widgets.tabs.ellipsometry_tab import EllipsometryTab

TABS: list[tuple[type[PlotTabBase], str]] = [
    (BrewsterTab, "brewster_tab"),
    (EllipsometryTab, "ellipsometry_tab"),
]


def _build(qtbot, tab_class: type[PlotTabBase], config: AppConfig) -> PlotTabBase:
    tab = tab_class(config=config)
    tab.build()
    qtbot.addWidget(tab)
    return tab


@pytest.fixture()
def brewster(qtbot, config: AppConfig) -> BrewsterTab:
    tab = _build(qtbot, BrewsterTab, config)
    assert isinstance(tab, BrewsterTab)
    return tab


@pytest.fixture()
def ellipsometry(qtbot, config: AppConfig) -> EllipsometryTab:
    tab = _build(qtbot, EllipsometryTab, config)
    assert isinstance(tab, EllipsometryTab)
    return tab


# ---------------------------------------------------------------------------
# Strings come from config.json
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(("tab_class", "section"), TABS)
def test_every_configured_object_name_exists_in_the_tab(
    qtbot, config: AppConfig, tab_class: type[PlotTabBase], section: str
) -> None:
    tab = _build(qtbot, tab_class, config)
    for key in config.section("ui")[section]:
        name = key.partition("@")[0]
        if "_" in name or name == "self":
            continue
        assert tab.findChild(QObject, name) is not None, f"ui.{section}.{key} has no widget"


@pytest.mark.parametrize(("tab_class", "section"), TABS)
def test_no_caption_or_button_is_left_without_text(
    qtbot, config: AppConfig, tab_class: type[PlotTabBase], section: str
) -> None:
    tab = _build(qtbot, tab_class, config)
    for label in tab.findChildren(QLabel):
        if label.objectName().startswith("label"):
            assert label.text(), f"{label.objectName()} has no text"
    for prefix in ("button", "check", "radio"):
        for widget in tab.findChildren(QObject):
            if widget.objectName().startswith(prefix) and hasattr(widget, "text"):
                assert widget.text(), f"{widget.objectName()} has no text"  # type: ignore[attr-defined]


def test_the_brewster_tab_shows_the_configured_german_texts(brewster: BrewsterTab) -> None:
    ui = brewster._ui
    assert ui.buttonSaveMax.text() == "Maximum speichern"
    assert ui.groupMax.title() == "Maximum"
    assert ui.radioPolP.text() == "p"
    assert "Brewster-Kurve" in ui.buttonSaveCurrent.toolTip()


def test_the_brewster_table_headers_match_the_columns_the_table_fills(
    brewster: BrewsterTab,
) -> None:
    table = brewster._ui.tablePoints
    headers = [table.horizontalHeaderItem(i).text() for i in range(table.columnCount())]
    assert headers == ["θ_S (°)", "θ_D (°)", "I (V)", "Gain", "P (W)"]
    brewster.on_frame(
        Frame(
            ts_ms=1,
            sample_angle=30.0,
            detector_angle=60.0,
            intensity=0.5,
            pdtia_gain=3,
            power_W=2e-6,
        )
    )
    brewster.on_measurement_started()
    brewster._save_point_current()
    assert table.item(0, 3).text() == "3"
    assert table.item(0, 4).text() == f"{2e-6:.3e}"


def test_the_ellipsometry_tab_shows_the_configured_german_texts(
    ellipsometry: EllipsometryTab,
) -> None:
    ui = ellipsometry._ui
    assert ui.buttonFitModel.text() == "Modell fitten"
    assert ui.groupSweep.title() == "Automatischer Scan (KDC101)"
    assert ui.spinWavelength.suffix() == " nm"
    assert [ui.comboModel.itemText(i) for i in range(ui.comboModel.count())] == [
        "Substrat (2-Phasen)",
        "Schicht auf Substrat (3-Ph.)",
    ]
    headers = [
        ui.tableSeries.horizontalHeaderItem(i).text() for i in range(ui.tableSeries.columnCount())
    ]
    assert headers[:3] == ["θ (°)", "Ψ (°)", "Δ (°)"]
    assert headers[-2:] == ["RMS (µW)", "m"]


def test_the_tab_titles_come_from_the_configuration(config: AppConfig) -> None:
    assert BrewsterTab.tab_title == "Brewster"
    assert EllipsometryTab.tab_title == "Ellipsometrie"
    renamed = config.with_overrides({"ui": {"tabs": {"brewster": "Brewster-Winkel"}}})
    assert BrewsterTab(config=renamed).tab_title == "Brewster-Winkel"


# ---------------------------------------------------------------------------
# Messages and formatted values
# ---------------------------------------------------------------------------


def test_the_brewster_tab_reports_a_missing_peak_with_the_configured_message(
    brewster: BrewsterTab,
) -> None:
    messages: list[tuple[str, str]] = []
    brewster.status_message.connect(lambda level, text: messages.append((level, text)))
    brewster.on_frame(
        Frame(ts_ms=1, sample_angle=30.0, detector_angle=60.0, intensity=float("nan"))
    )
    brewster._save_point_max()
    assert messages == [("warning", "Kein Maximum verfügbar")]


def test_the_brewster_peak_labels_use_the_configured_unit_templates(brewster: BrewsterTab) -> None:
    brewster._update_max_labels(0.5, 61.0)
    assert brewster._ui.valueMaxIntensity.text().endswith(" V")
    assert brewster._ui.valueMaxAngle.text().endswith("°")
    custom = brewster.config.with_overrides(
        {"ui": {"brewster_tab": {"fmt_voltage": "{value} Volt"}}}
    )
    brewster.config = custom
    brewster._update_max_labels(0.5, 61.0)
    assert brewster._ui.valueMaxIntensity.text().endswith(" Volt")


def test_the_ellipsometry_tab_reports_a_missing_frame_with_the_configured_message(
    ellipsometry: EllipsometryTab,
) -> None:
    messages: list[tuple[str, str]] = []
    ellipsometry.status_message.connect(lambda level, text: messages.append((level, text)))
    ellipsometry._set_aoi_zero()
    assert messages == [("warning", "Kein aktueller Messwert vorhanden")]


def test_the_ellipsometry_sweep_button_explains_why_it_is_disabled(
    ellipsometry: EllipsometryTab,
) -> None:
    ellipsometry._update_gates()
    tip = ellipsometry._ui.buttonStartSweep.toolTip()
    assert "Leistungsmessung erforderlich" in tip
    assert "KDC101 nicht verbunden" in tip
    assert " / " in tip


def test_the_ellipsometry_live_labels_use_the_configured_unit_templates(
    ellipsometry: EllipsometryTab,
) -> None:
    ellipsometry.on_frame(
        Frame(ts_ms=1, sample_angle=65.0, detector_angle=130.0, intensity=0.5, power_W=1.5e-3)
    )
    assert ellipsometry._ui.valueLiveIntensity.text().endswith(" V")
    assert ellipsometry._ui.valueLivePower.text() == "1.500 mW"
    assert ellipsometry._ui.valueLiveDetector.text().endswith("°")


# ---------------------------------------------------------------------------
# Plot axis labels
# ---------------------------------------------------------------------------


def _axis_label(plot_widget, axis: str) -> str:
    return plot_widget.getAxis(axis).labelText


def test_the_brewster_plots_take_their_axis_labels_from_the_configuration(
    qtbot, config: AppConfig
) -> None:
    renamed = config.with_overrides(
        {"ui": {"plots": {"brewster_detector_x_label": "Arm", "brewster_curve_x_label": "Probe"}}}
    )
    tab = _build(qtbot, BrewsterTab, renamed)
    assert _axis_label(tab._ui.detectorPlot._plot_widget, "bottom") == "Arm"
    assert _axis_label(tab._ui.brewsterCurvePlot._plot_widget, "bottom") == "Probe"
    assert _axis_label(tab._ui.detectorPlot._plot_widget, "left") == "Intensität"


def test_the_brewster_detector_plot_relabels_for_power_mode(brewster: BrewsterTab) -> None:
    plot = brewster._ui.detectorPlot
    plot.set_power_mode(True)
    assert _axis_label(plot._plot_widget, "left") == "Leistung"
    plot.set_power_mode(False)
    assert _axis_label(plot._plot_widget, "left") == "Intensität"


def test_the_ellipsometry_plots_take_their_axis_labels_from_the_configuration(
    ellipsometry: EllipsometryTab,
) -> None:
    curve = ellipsometry._ui.ellipsoCurvePlot._plot_widget
    assert _axis_label(curve, "bottom") == "Einfallswinkel θ"
    assert _axis_label(curve, "left") == "Ψ"
    assert _axis_label(curve, "right") == "Δ"
    fit = ellipsometry._ui.fitPlot
    assert _axis_label(fit._plot_widget, "bottom") == "Analysatorazimut"
    assert _axis_label(fit._residual_widget, "left") == "Residuum"


# ---------------------------------------------------------------------------
# Side columns
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("fixture", ["brewster", "ellipsometry"])
def test_the_side_column_never_scrolls_horizontally(request, fixture: str) -> None:
    tab = request.getfixturevalue(fixture)
    scroll = tab._ui.scrollSide
    tab.resize(1000, 700)
    tab.show()
    content_width = scroll.widget().minimumSizeHint().width()
    assert scroll.minimumWidth() >= content_width
    assert scroll.horizontalScrollBar().maximum() == 0


def test_the_ellipsometry_side_column_keeps_the_form_floor_width(
    ellipsometry: EllipsometryTab,
) -> None:
    assert ellipsometry._ui.scrollSide.minimumWidth() >= 310


def test_the_brewster_plots_get_the_stretch_next_to_the_side_column(
    brewster: BrewsterTab,
) -> None:
    brewster.resize(1200, 800)
    brewster.show()
    assert brewster._ui.splitterPlots.width() > brewster._ui.scrollSide.width()
