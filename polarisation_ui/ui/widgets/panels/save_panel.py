"""Save panel: group letter, team name, file-name suffix and the Save button."""

from __future__ import annotations

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QGroupBox, QLineEdit, QWidget

from polarisation_ui.infrastructure.config import AppConfig
from polarisation_ui.pyqt.ui_save_panel import Ui_SavePanel
from polarisation_ui.ui.i18n import apply_strings


class SavePanel(QGroupBox):
    """Inputs that make up the file name of an export and the Save button."""

    group_changed = Signal(str)  # group letter, "" when none is selected
    team_changed = Signal(str)
    suffix_changed = Signal(str)
    save_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build the form; no group is selected and Save is disabled until there is data."""
        super().__init__(parent)
        self.ui = Ui_SavePanel()
        self.ui.setupUi(self)
        self.ui.comboGroup.currentIndexChanged.connect(self._on_group_index_changed)
        self.ui.editTeam.textChanged.connect(self.team_changed)
        self.ui.editSuffix.textChanged.connect(self.suffix_changed)
        self.ui.buttonSave.clicked.connect(self.save_requested)
        self.ui.comboGroup.setCurrentIndex(-1)
        self.ui.buttonSave.setEnabled(False)

    def apply_config(self, config: AppConfig) -> None:
        """Apply the ``ui.save_panel`` strings."""
        apply_strings(self, config.section("ui").get("save_panel", {}))

    # ---- setters (driven by the controller) -----------------------------------------------
    @Slot(str)
    def set_group(self, letter: str) -> None:
        """Select ``letter`` ("" for none) without emitting :attr:`group_changed`."""
        combo = self.ui.comboGroup
        index = combo.findText(letter) if letter else -1
        if index != combo.currentIndex():
            combo.blockSignals(True)
            combo.setCurrentIndex(index)
            combo.blockSignals(False)

    @Slot(str)
    def set_team(self, text: str) -> None:
        """Show the team name unless it already shows it (ignoring surrounding blanks)."""
        self._set_text(self.ui.editTeam, text)

    @Slot(str)
    def set_suffix(self, text: str) -> None:
        """Show the suffix unless it already shows it (ignoring surrounding blanks)."""
        self._set_text(self.ui.editSuffix, text)

    @staticmethod
    def _set_text(edit: QLineEdit, text: str) -> None:
        if edit.text().strip() != text:
            edit.blockSignals(True)
            edit.setText(text)
            edit.blockSignals(False)

    @Slot(str)
    def set_filename(self, path: str) -> None:
        """Show the expected save path ("" while no group is selected)."""
        self.ui.valueFilename.setText(path)

    @Slot(bool)
    def set_prefix_locked(self, locked: bool) -> None:
        """Group and team are frozen after the first save."""
        self.ui.comboGroup.setEnabled(not locked)
        self.ui.editTeam.setEnabled(not locked)

    @Slot(bool)
    def set_save_enabled(self, enabled: bool) -> None:
        """Save needs saved points in the active tab."""
        self.ui.buttonSave.setEnabled(enabled)

    @Slot(bool)
    def set_suffix_visible(self, visible: bool) -> None:
        """Show or hide the suffix input (the *Suffix* toolbar action)."""
        self.ui.labelSuffix.setVisible(visible)
        self.ui.editSuffix.setVisible(visible)

    @Slot(int)
    def _on_group_index_changed(self, index: int) -> None:
        self.group_changed.emit(self.ui.comboGroup.itemText(index) if index >= 0 else "")
