"""Show a Designer form on its own, without controllers, devices or the infrastructure layer.

A design check for Qt Creator / Designer: the ``.ui`` file is loaded on the fly (no ``pyuic.sh``
run needed) and the German strings from ``config.json`` are applied, so the window looks like
the running application minus the logic. Nothing of ``polarisation_ui.infrastructure`` is
imported, so no serial, VISA or Thorlabs packages are needed; PySide6 is enough.

Promoted widgets are replaced by stand-ins instead of importing their classes:

- a dock panel promoted in ``main_window.ui`` (``ArduinoPanel``, ``StagePanel``, …) is built from
  its own form (``arduino_panel.ui``, …), like the real panel class does;
- a plot (pyqtgraph) becomes a framed placeholder that names the class;
- anything else (e.g. ``ElidedLabel``) becomes the Qt class it extends.

Combo boxes, tables and plots that the code fills stay empty.

    .venv/bin/python -m polarisation_ui.pyqt.preview                  # pick a form (dialog)
    .venv/bin/python -m polarisation_ui.pyqt.preview --list           # list the forms
    .venv/bin/python -m polarisation_ui.pyqt.preview main_window      # show one form
    .venv/bin/python -m polarisation_ui.pyqt.preview malus_tab --watch   # reload on save
    .venv/bin/python -m polarisation_ui.pyqt.preview main_window --profile student

Qt Creator runs this file as a script (``Run`` on the project opened from ``pyproject.toml``):
without arguments it asks for the form and reloads it whenever the ``.ui`` file is saved.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
import xml.etree.ElementTree as ET
from collections.abc import Callable
from pathlib import Path
from typing import Any

if __package__ in (None, ""):  # run as a script (Qt Creator): make the package importable
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from PySide6.QtCore import QFileSystemWatcher, QObject, Qt, QTimer  # noqa: E402
from PySide6.QtUiTools import QUiLoader  # noqa: E402
from PySide6.QtWidgets import (  # noqa: E402
    QApplication,
    QFrame,
    QInputDialog,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from polarisation_ui.pyqt.forms import CONFIG_PATH, PYQT_DIR, SECTIONS, form_names  # noqa: E402
from polarisation_ui.ui.i18n import apply_strings  # noqa: E402

DEFAULT_PROFILE = "expert"


def _warn(message: str) -> None:
    print(f"preview: {message}", file=sys.stderr)


def load_ui_strings(profile: str = DEFAULT_PROFILE, path: Path = CONFIG_PATH) -> dict[str, Any]:
    """The ``ui`` section of ``config.json`` with the overrides of ``profile`` merged in."""
    data = json.loads(path.read_text(encoding="utf-8"))
    ui: dict[str, Any] = copy.deepcopy(data.get("ui", {}))
    overrides = data.get("profiles", {}).get(profile, {}).get("overrides", {}).get("ui", {})
    _merge(ui, overrides)
    return ui


def _merge(base: dict[str, Any], override: dict[str, Any]) -> None:
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            _merge(base[key], value)
        else:
            base[key] = copy.deepcopy(value)


def _custom_widgets(path: Path) -> dict[str, tuple[str, str]]:
    """``class -> (extends, header)`` of the promoted widgets declared in the ``.ui`` file."""
    root = ET.parse(path).getroot()
    found: dict[str, tuple[str, str]] = {}
    for node in root.iter("customwidget"):
        name = node.findtext("class", "")
        found[name] = (node.findtext("extends", "QWidget"), node.findtext("header", ""))
    return found


class _PreviewLoader(QUiLoader):
    """``QUiLoader`` that builds stand-ins for promoted widgets (see the module docstring)."""

    def __init__(self, path: Path, build: Callable[[str], QWidget]) -> None:
        super().__init__()
        self._custom = _custom_widgets(path)
        self._build = build
        self._known = set(self.availableWidgets())

    def createWidget(  # noqa: N802 - Qt override
        self, class_name: str, parent: QWidget | None = None, name: str = ""
    ) -> QWidget:
        if class_name in self._known or class_name not in self._custom:
            widget = super().createWidget(class_name, parent, name)
        else:
            widget = self._stand_in(class_name, parent)
        widget.setObjectName(name)
        return widget

    def _stand_in(self, class_name: str, parent: QWidget | None) -> QWidget:
        extends, header = self._custom[class_name]
        form = header.rsplit(".", maxsplit=1)[-1]
        if (PYQT_DIR / f"{form}.ui").exists():  # a panel: its own form, as the real class does
            panel = self._build(form)
            panel.setParent(parent)
            return panel
        if class_name.endswith(("Plot", "PlotWidget")):
            frame = QFrame(parent)
            frame.setFrameShape(QFrame.Shape.StyledPanel)
            frame.setMinimumSize(160, 120)
            label = QLabel(f"{class_name}\n(pyqtgraph, filled by the code)", frame)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setEnabled(False)
            QVBoxLayout(frame).addWidget(label)
            return frame
        return super().createWidget(extends, parent, "")


def build_form(
    name: str, profile: str = DEFAULT_PROFILE, ui_strings: dict[str, Any] | None = None
) -> QWidget:
    """Instantiate the form ``name`` (a ``.ui`` file stem) with the configured UI strings."""
    strings = load_ui_strings(profile) if ui_strings is None else ui_strings
    path = PYQT_DIR / f"{name}.ui"
    loader = _PreviewLoader(path, lambda form: build_form(form, profile, strings))
    widget = loader.load(str(path))
    if widget is None:
        raise RuntimeError(f"cannot load {path.name}: {loader.errorString()}")
    for section in SECTIONS.get(name, (name,)):
        apply_strings(widget, strings.get(section, {}), warn=_warn)
    return widget


def _choose_form(forms: list[str]) -> str | None:
    """Ask for a form in a dialog (used when no form is given, e.g. from Qt Creator)."""
    default = forms.index("main_window") if "main_window" in forms else 0
    form, ok = QInputDialog.getItem(None, "Designer preview", "Form:", forms, default, False)
    return form if ok else None


def _watch(form: str, profile: str, windows: list[QWidget]) -> QObject:
    """Reload ``windows[0]`` when ``form``'s ``.ui`` file or ``config.json`` is saved."""
    paths = [str(PYQT_DIR / f"{form}.ui"), str(CONFIG_PATH)]
    watcher = QFileSystemWatcher(paths)

    def reload() -> None:
        old = windows.pop()
        try:
            new = build_form(form, profile)
        except Exception as error:  # a half-saved or invalid file must not end the preview
            _warn(f"reload failed: {error}")
            windows.append(old)
        else:
            new.setGeometry(old.geometry())
            new.show()
            old.close()
            windows.append(new)
        for path in paths:  # editors replace the file on save
            if path not in watcher.files():
                watcher.addPath(path)

    watcher.fileChanged.connect(lambda _: QTimer.singleShot(200, reload))
    return watcher


def main(argv: list[str] | None = None) -> int:
    """Show one form (asking for it if none is given); ``--list`` prints the form names."""
    forms = form_names()
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", maxsplit=1)[0])
    parser.add_argument("form", nargs="?", choices=forms, help="stem of the .ui file")
    parser.add_argument("--list", action="store_true", help="print the form names and exit")
    parser.add_argument("--watch", action="store_true", help="reload when the files change")
    parser.add_argument("--profile", default=DEFAULT_PROFILE, help="config.json profile id")
    args = parser.parse_args(argv)
    if args.list:
        print("\n".join(forms))
        return 0

    app = QApplication(sys.argv[:1])
    form = args.form or _choose_form(forms)
    if form is None:
        return 0
    windows: list[QWidget] = [build_form(form, args.profile)]
    windows[0].show()
    _watcher = _watch(form, args.profile, windows) if args.watch or args.form is None else None
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
