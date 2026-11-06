"""Apply the German UI strings from config.json to widgets built from Designer forms.

Keys are Designer object names (camelCase, no underscore; ``self`` is the root widget);
``name@kind`` selects another property: ``@tooltip``, ``@suffix``, ``@prefix``,
``@placeholder``, ``@title`` (window title).
Keys with an underscore (e.g. ``plot_y_label``) are plain texts looked up by the code and are
skipped here.
"""

from __future__ import annotations

from collections.abc import Mapping

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QDockWidget

from polarisation_ui.infrastructure.logging import Debug


def apply_strings(root: QObject, strings: Mapping[str, object]) -> None:
    """Set the texts of ``strings`` on the children of ``root`` (see the module docstring)."""
    for key, text in strings.items():
        name, _, kind = key.partition("@")
        if "_" in name or not isinstance(text, str):
            continue
        obj: QObject | None = root if name == "self" else root.findChild(QObject, name)
        if obj is None:
            Debug.warning(f"ui string for unknown object {name!r}")
            continue
        if kind == "tooltip":
            obj.setToolTip(text)  # type: ignore[attr-defined]
        elif kind == "suffix":
            obj.setSuffix(text)  # type: ignore[attr-defined]
        elif kind == "prefix":
            obj.setPrefix(text)  # type: ignore[attr-defined]
        elif kind == "placeholder":
            obj.setPlaceholderText(text)  # type: ignore[attr-defined]
        elif kind == "title":
            obj.setWindowTitle(text)  # type: ignore[attr-defined]
        elif isinstance(obj, QDockWidget):
            obj.setWindowTitle(text)
        elif hasattr(obj, "setTitle"):
            obj.setTitle(text)
        elif hasattr(obj, "setText"):
            obj.setText(text)
        else:
            Debug.warning(f"cannot set text on {name!r}")
