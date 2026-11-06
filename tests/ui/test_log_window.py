"""Tests for the live log window (strings from config.json, log lines shown in the editor)."""

from PySide6.QtCore import QObject

from polarisation_ui.infrastructure.config import default_config
from polarisation_ui.ui.windows.log_window import LogWindow


def test_the_log_window_shows_the_configured_title(qtbot):
    window = LogWindow()
    qtbot.addWidget(window)

    assert window.windowTitle() == "Log-Ausgabe"


def test_every_log_window_key_resolves_to_a_child_widget(qtbot):
    window = LogWindow()
    qtbot.addWidget(window)

    for key in default_config().section("ui")["log_window"]:
        name = key.partition("@")[0]
        if name == "self":
            continue
        assert window.findChild(QObject, name) is not None, f"unknown object name in {key!r}"


def test_appended_lines_land_in_the_log_editor(qtbot):
    window = LogWindow()
    qtbot.addWidget(window)

    window._append_line("first line")
    window._append_line("second line")

    assert window.ui.editLog.toPlainText().splitlines() == ["first line", "second line"]
    assert window.ui.editLog.isReadOnly() is True
