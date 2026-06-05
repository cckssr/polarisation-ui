"""Tests for the p/s polarisation radio buttons in BrewsterTab."""

import pytest

from polarisation_ui.ui.widgets.tabs.brewster_tab import BrewsterTab


@pytest.fixture()
def tab(qtbot):
    t = BrewsterTab()
    t.build()
    qtbot.addWidget(t)
    return t


def test_default_polarisation_is_p(tab):
    assert tab._polarisation == "p"
    assert tab._ui.rbPolP.isChecked()
    assert not tab._ui.rbPolS.isChecked()


def test_selecting_s_updates_state(tab):
    tab._ui.rbPolS.setChecked(True)
    assert tab._polarisation == "s"


def test_switching_back_to_p(tab):
    tab._ui.rbPolS.setChecked(True)
    tab._ui.rbPolP.setChecked(True)
    assert tab._polarisation == "p"


def test_build_export_contains_polarisation_in_metadata(tab):
    exp = tab.build_export()
    assert exp.metadata["polarisation"] == "p"


def test_build_export_tokens_match_polarisation(tab):
    exp = tab.build_export()
    assert exp.filename_tokens == ["p"]
    tab._ui.rbPolS.setChecked(True)
    exp_s = tab.build_export()
    assert exp_s.filename_tokens == ["s"]
    assert exp_s.metadata["polarisation"] == "s"


def test_filename_hint_changed_emitted_on_toggle(tab, qtbot):
    with qtbot.waitSignal(tab.filename_hint_changed, timeout=1000):
        tab._ui.rbPolS.setChecked(True)
