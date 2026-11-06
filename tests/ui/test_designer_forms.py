"""The Designer forms carry the German strings from config.json and open on their own.

Regenerate out-of-date forms with ``polarisation_ui/pyqt/pyuic.sh``.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from polarisation_ui.infrastructure.config import AppConfig
from polarisation_ui.pyqt.preview import build_form
from polarisation_ui.pyqt.sync_texts import PYQT_DIR, SECTIONS, synced_text

FORMS = sorted(path.stem for path in PYQT_DIR.glob("*.ui"))

# Forms that still carry untranslated texts in their .ui (or lack a config section); the
# migration phases remove a form from this set once all its texts come from config.json.
NOT_YET_MIGRATED: set[str] = {
    "mainwindow",
}  # one entry per line: each migration removes its own line

# .ui property -> key suffix of ``apply_strings`` (``""``: the plain ``name`` key).
_TEXT_PROPERTIES = {
    "text": "",
    "title": "",
    "toolTip": "@tooltip",
    "windowTitle": "@title",
    "placeholderText": "@placeholder",
    "suffix": "@suffix",
    "prefix": "@prefix",
}


def _form_strings(form: str, config: AppConfig) -> dict[str, object]:
    strings: dict[str, object] = {}
    for section in SECTIONS.get(form, (form,)):
        strings.update(config.section("ui").get(section, {}))
    return strings


def untranslated_texts(path: Path, strings: dict[str, object]) -> list[str]:
    """Config keys the form at ``path`` lacks for its visible, translatable texts."""
    root = ET.parse(path).getroot()
    top = root.find("widget")
    missing: list[str] = []
    for element in root.iter():
        if element.tag not in ("widget", "action") or not element.get("name"):
            continue
        name = "self" if element is top else element.get("name", "")
        is_dock = element.get("class") == "QDockWidget"
        for prop in element.findall("property"):
            kind = _TEXT_PROPERTIES.get(prop.get("name", ""))
            string = prop.find("string")
            if kind is None or string is None or string.get("notr") == "true":
                continue
            if not any(char.isalpha() for char in string.text or ""):
                continue
            if is_dock and prop.get("name") == "windowTitle":
                kind = ""  # a dock's caption is its plain key
            key = f"{name}{kind}"
            if not isinstance(strings.get(key), str):
                missing.append(key)
    return missing


@pytest.mark.parametrize("form", FORMS)
def test_form_texts_match_config(form: str, config: AppConfig) -> None:
    path = PYQT_DIR / f"{form}.ui"
    assert synced_text(path, config) == path.read_text(encoding="utf-8")


@pytest.mark.parametrize("form", FORMS)
def test_form_opens_without_logic(qtbot, form: str) -> None:
    widget = build_form(form)
    qtbot.addWidget(widget)
    widget.show()


@pytest.mark.parametrize("form", FORMS)
def test_every_ui_text_comes_from_config(form: str, config: AppConfig) -> None:
    if form in NOT_YET_MIGRATED:
        pytest.skip(f"{form} is not migrated to config.json strings yet")
    missing = untranslated_texts(PYQT_DIR / f"{form}.ui", _form_strings(form, config))
    assert not missing, f"{form}.ui has texts without a ui.{form} key: {missing}"


def test_the_not_yet_migrated_set_only_names_existing_forms() -> None:
    assert NOT_YET_MIGRATED <= set(FORMS)


def test_the_text_check_reports_a_missing_key_and_accepts_a_complete_form(tmp_path: Path) -> None:
    form = tmp_path / "demo.ui"
    form.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>Demo</class>
 <widget class="QWidget" name="Demo">
  <property name="windowTitle"><string>Demo</string></property>
  <widget class="QPushButton" name="buttonGo">
   <property name="text"><string>Start</string></property>
   <property name="toolTip"><string>Los</string></property>
  </widget>
  <widget class="QLabel" name="valueAngle">
   <property name="text"><string notr="true">0.0</string></property>
  </widget>
  <widget class="QLabel" name="labelDash">
   <property name="text"><string>--</string></property>
  </widget>
  <widget class="QGroupBox" name="groupMain">
   <property name="title"><string>Gruppe</string></property>
  </widget>
 </widget>
</ui>
""",
        encoding="utf-8",
    )
    assert untranslated_texts(form, {}) == [
        "self@title",
        "buttonGo",
        "buttonGo@tooltip",
        "groupMain",
    ]
    complete = {"self@title": "T", "buttonGo": "S", "buttonGo@tooltip": "L", "groupMain": "G"}
    assert untranslated_texts(form, complete) == []


def test_the_tab_kind_writes_the_title_attribute_of_a_tab_page() -> None:
    from polarisation_ui.pyqt.sync_texts import sync_text

    source = (
        '<?xml version="1.0" encoding="UTF-8"?>\n<ui version="4.0"><class>Form</class>'
        '<widget class="QTabWidget" name="tabWidget"><widget class="QWidget" name="tabMain">'
        '<attribute name="title"><string>Old</string></attribute></widget>'
        '<widget class="QWidget" name="tabOther"/></widget></ui>'
    )
    root = ET.fromstring(sync_text(source, {"tabMain@tab": "Neu", "tabOther@tab": "Zweiter"}))
    titles = {
        page.get("name"): page.find("attribute/string").text  # type: ignore[union-attr]
        for page in root.iter("widget")
        if page.find("attribute") is not None
    }
    assert titles == {"tabMain": "Neu", "tabOther": "Zweiter"}


def test_sync_texts_handles_only_the_named_forms() -> None:
    from polarisation_ui.pyqt import sync_texts

    assert sync_texts.main(["--check", "log_window"]) == 0
