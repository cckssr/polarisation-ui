"""Tests for ui/common/dialogs.py standardised QMessageBox wrappers."""

from unittest.mock import patch

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox

from polarisation_ui.ui.common.dialogs import show_error


def test_show_error_sets_delete_on_close(qtbot):
    """Regression test: show_error() used to create a QMessageBox parented to
    the caller without WA_DeleteOnClose, so the C++ object stayed alive as a
    child of `parent` forever (Qt only auto-deletes on close, not on Python
    GC) — every error dialog shown over an app session leaked one QMessageBox.
    """
    captured = {}

    def fake_exec(self):
        captured["dialog"] = self
        return QMessageBox.StandardButton.Ok

    with patch.object(QMessageBox, "exec", fake_exec):
        show_error(None, "Title", "Something went wrong")

    assert captured["dialog"].testAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
