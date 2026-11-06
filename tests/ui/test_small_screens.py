"""The window stays usable on the target screens; side columns never scroll horizontally.

Screens (user decision): 1920x1080 with both side docks visible and 1366x768 with the right
dock (readout / measurement / save) collapsed. The heights leave room for a task bar.
"""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QScrollArea

WIDE_W, WIDE_H = 1920, 1000  # both docks visible
NARROW_W, NARROW_H = 1366, 700  # right dock collapsed
# Widest minimum of a central tab. Measured: the ellipsometry tab needs about 500 px, every other
# tab less. 560 px leaves the plots at least ~800 px of the 1366 px screen next to the left dock
# (about 380 px minimum), so no tab squeezes its plots on the narrow screen.
TAB_MAX_W = 560


def _side_scrolls(window) -> list[QScrollArea]:
    scrolls = [window.ui.scrollControls, window.ui.scrollMeasurement]
    for tab in window.tabs.tabs:
        scrolls += [s for s in tab.findChildren(QScrollArea) if s.objectName() == "scrollSide"]
    return scrolls


def _assert_no_horizontal_scrolling(window) -> None:
    scrolls = _side_scrolls(window)
    assert len(scrolls) >= 2 + len(window.tabs.tabs)  # both docks and every tab's side column
    for scroll in scrolls:
        name = scroll.objectName()
        assert scroll.horizontalScrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAlwaysOff, name
        assert not scroll.horizontalScrollBar().isVisible(), name
        # nothing is clipped: the viewport is at least as wide as the content needs
        assert scroll.widget().minimumSizeHint().width() <= scroll.viewport().width(), name


def _show_every_tab(qtbot, window, width: int, height: int) -> None:
    window.resize(width, height)
    for index, tab in enumerate(window.tabs.tabs):
        window.ui.tabWidget.setCurrentIndex(index)
        qtbot.wait(20)
        assert tab.minimumSizeHint().width() <= TAB_MAX_W, tab.tab_id
        assert window.minimumSizeHint().width() <= width, tab.tab_id
        _assert_no_horizontal_scrolling(window)


def test_the_minimum_width_fits_the_wide_screen_with_both_docks(qtbot, window):
    assert window.ui.dockControls.isVisible() and window.ui.dockMeasurement.isVisible()
    assert window.minimumSizeHint().width() <= WIDE_W
    window.resize(WIDE_W, WIDE_H)
    qtbot.wait(50)
    assert window.width() == WIDE_W
    _assert_no_horizontal_scrolling(window)
    for dock in (window.ui.dockControls, window.ui.dockMeasurement):
        assert dock.width() >= dock.minimumWidth()


def test_the_minimum_width_fits_the_narrow_screen_with_the_right_dock_collapsed(qtbot, window):
    window.ui.actionToggleMeasurement.setChecked(False)
    qtbot.wait(50)
    assert not window.ui.dockMeasurement.isVisible()
    assert window.minimumSizeHint().width() <= NARROW_W
    window.resize(NARROW_W, NARROW_H)
    qtbot.wait(50)
    assert window.width() == NARROW_W
    _assert_no_horizontal_scrolling(window)


def test_every_tab_is_narrow_enough_on_the_wide_screen(qtbot, window):
    window.ui.kdcPanel.ui.buttonConnect.click()  # adds the waveplate tab
    assert "waveplate" in {tab.tab_id for tab in window.tabs.tabs}
    _show_every_tab(qtbot, window, WIDE_W, WIDE_H)


def test_every_tab_is_narrow_enough_on_the_narrow_screen(qtbot, window):
    window.ui.kdcPanel.ui.buttonConnect.click()
    window.ui.actionToggleMeasurement.setChecked(False)
    qtbot.wait(50)
    _show_every_tab(qtbot, window, NARROW_W, NARROW_H)


def test_the_ellipsometry_tab_is_within_the_budget(window):
    tab = next(t for t in window.tabs.tabs if t.tab_id == "ellipsometry")
    assert tab.minimumSizeHint().width() <= TAB_MAX_W


def test_the_collapsed_right_dock_leaves_the_tabs_most_of_the_narrow_screen(qtbot, window):
    window.ui.actionToggleMeasurement.setChecked(False)
    window.resize(NARROW_W, NARROW_H)
    qtbot.wait(50)
    assert window.ui.tabWidget.width() >= NARROW_W - window.ui.dockControls.width() - 40


@pytest.mark.parametrize("dock", ["dockControls", "dockMeasurement"])
def test_a_side_dock_never_shows_a_horizontal_scroll_bar_even_when_squeezed(qtbot, window, dock):
    ui = window.ui
    scroll = {"dockControls": ui.scrollControls, "dockMeasurement": ui.scrollMeasurement}[dock]
    window.resize(window.minimumSizeHint().width(), WIDE_H)
    qtbot.wait(50)
    assert not scroll.horizontalScrollBar().isVisible()
    assert getattr(ui, dock).minimumWidth() == scroll.minimumWidth() + 2


def test_a_long_file_name_is_elided_and_never_widens_the_window(qtbot, window):
    window.ui.actionToggleMeasurement.setChecked(True)
    label = window.ui.savePanel.ui.valueFilename
    long_path = "/Users/student/Messdaten/" + "sehr_langer_ordnername/" * 8 + "messung_malus_A.csv"
    width_before = window.minimumSizeHint().width()
    label.setText(long_path)
    qtbot.wait(30)
    shown = label.elided_text()
    assert "…" in shown and shown.endswith("malus_A.csv")
    assert label.fontMetrics().horizontalAdvance(shown) <= label.contentsRect().width()
    assert label.text() == long_path and label.toolTip() == long_path
    assert label.minimumSizeHint().width() < 100
    assert window.minimumSizeHint().width() == width_before


def test_a_long_status_text_is_elided_and_never_widens_the_left_dock(qtbot, window):
    width_before = window.ui.dockControls.minimumWidth()
    window.ui.arduinoPanel.set_state("error", "Fehler: " + "sehr langer Fehlertext " * 10)
    qtbot.wait(30)
    assert window.ui.dockControls.minimumWidth() == width_before
    assert not window.ui.scrollControls.horizontalScrollBar().isVisible()
