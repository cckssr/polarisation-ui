"""``apply_strings`` writes the configured German strings onto Designer-built widgets."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from polarisation_ui.infrastructure.logging import Debug
from polarisation_ui.ui.i18n import apply_strings


@pytest.fixture
def form(qtbot) -> QWidget:
    root = QWidget()
    root.setObjectName("root")
    layout = QVBoxLayout(root)
    group = QGroupBox(root)
    group.setObjectName("groupMain")
    layout.addWidget(group)
    for cls, name in (
        (QPushButton, "buttonGo"),
        (QLabel, "labelInfo"),
        (QDoubleSpinBox, "spinAngle"),
        (QLineEdit, "editName"),
    ):
        widget = cls(root)
        widget.setObjectName(name)
        layout.addWidget(widget)
    qtbot.addWidget(root)
    return root


@pytest.fixture
def warnings(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    messages: list[str] = []
    monkeypatch.setattr(Debug, "warning", classmethod(lambda cls, msg: messages.append(msg)))
    return messages


def test_a_plain_key_sets_the_text_of_a_button_and_a_label(form: QWidget) -> None:
    apply_strings(form, {"buttonGo": "Start", "labelInfo": "Winkel:"})
    assert form.findChild(QPushButton, "buttonGo").text() == "Start"
    assert form.findChild(QLabel, "labelInfo").text() == "Winkel:"


def test_a_plain_key_sets_the_title_of_a_group_box(form: QWidget) -> None:
    apply_strings(form, {"groupMain": "Messung"})
    assert form.findChild(QGroupBox, "groupMain").title() == "Messung"


def test_suffix_prefix_tooltip_and_placeholder_kinds(form: QWidget) -> None:
    apply_strings(
        form,
        {
            "spinAngle@suffix": " °",
            "spinAngle@prefix": "θ = ",
            "buttonGo@tooltip": "Messung starten",
            "editName@placeholder": "Name",
        },
    )
    spin = form.findChild(QDoubleSpinBox, "spinAngle")
    assert (spin.suffix(), spin.prefix()) == (" °", "θ = ")
    assert form.findChild(QPushButton, "buttonGo").toolTip() == "Messung starten"
    assert form.findChild(QLineEdit, "editName").placeholderText() == "Name"


def test_self_with_the_title_kind_sets_the_window_title(form: QWidget) -> None:
    apply_strings(form, {"self@title": "Fenster", "self@tooltip": "Hinweis"})
    assert form.windowTitle() == "Fenster"
    assert form.toolTip() == "Hinweis"


def test_the_title_kind_on_a_child_sets_its_window_title(form: QWidget) -> None:
    apply_strings(form, {"buttonGo@title": "Titel"})
    assert form.findChild(QPushButton, "buttonGo").windowTitle() == "Titel"


def test_an_unknown_object_name_is_logged_and_the_rest_still_applies(
    form: QWidget, warnings: list[str]
) -> None:
    apply_strings(form, {"buttonMissing": "x", "buttonGo": "Start"})
    assert any("buttonMissing" in message for message in warnings)
    assert form.findChild(QPushButton, "buttonGo").text() == "Start"


def test_keys_with_an_underscore_are_skipped_without_a_warning(
    form: QWidget, warnings: list[str]
) -> None:
    apply_strings(form, {"text_connect": "Verbinden", "buttonGo": "Start", "plot_y_label": "Y"})
    assert warnings == []
    assert form.findChild(QPushButton, "buttonGo").text() == "Start"


def test_a_widget_without_a_text_property_is_reported(form: QWidget, warnings: list[str]) -> None:
    apply_strings(form, {"spinAngle": "42"})
    assert any("spinAngle" in message for message in warnings)


def test_non_string_values_are_ignored(form: QWidget, warnings: list[str]) -> None:
    apply_strings(form, {"buttonGo": 5, "labelInfo": {"nested": "x"}})  # type: ignore[dict-item]
    assert warnings == []
    assert form.findChild(QPushButton, "buttonGo").text() == ""


def test_the_tab_kind_sets_the_title_of_a_tab_page(qtbot, warnings: list[str]) -> None:
    tabs = QTabWidget()
    qtbot.addWidget(tabs)
    page = QWidget()
    page.setObjectName("tabSettings")
    tabs.addTab(page, "")
    apply_strings(tabs, {"tabSettings@tab": "Einstellungen", "labelInfo@tab": "x"})
    assert tabs.tabText(0) == "Einstellungen"
    assert any("labelInfo" in w for w in warnings)


def test_the_tab_kind_on_a_widget_outside_a_tab_widget_is_reported(
    form: QWidget, warnings: list[str]
) -> None:
    apply_strings(form, {"labelInfo@tab": "Info"})
    assert any("not a tab page" in w for w in warnings)
