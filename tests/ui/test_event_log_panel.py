"""Tests for the event log panel (timestamped scrollback in the editor)."""

import re

from polarisation_ui.ui.widgets.event_log_panel import EventLogPanel


def test_append_adds_a_timestamped_line(qtbot):
    panel = EventLogPanel()
    qtbot.addWidget(panel)

    panel.append("Verbunden mit COM3.")

    lines = panel.ui.editLog.toPlainText().splitlines()
    assert len(lines) == 1
    assert re.fullmatch(r"\[\d{2}:\d{2}:\d{2}\] Verbunden mit COM3\.", lines[0])


def test_the_event_log_is_read_only_and_keeps_500_lines(qtbot):
    panel = EventLogPanel()
    qtbot.addWidget(panel)

    assert panel.ui.editLog.isReadOnly() is True
    assert panel.ui.editLog.maximumBlockCount() == 500
