"""Questions the main window asks about saved data: orphaned journals, restore, partial export."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QFileDialog, QMessageBox, QWidget

from polarisation_ui.infrastructure.config import AppConfig
from polarisation_ui.ui.controllers.session_controller import SessionController


class SessionPrompts:
    """Yes/No questions and file dialogs around :class:`SessionController` (data recovery)."""

    def __init__(self, parent: QWidget, session: SessionController, config: AppConfig) -> None:
        """Dialogs are children of ``parent``; the answers drive ``session``."""
        self._parent = parent
        self._session = session
        self._config = config

    def _m(self, key: str, **fmt: object) -> str:
        return self._config.message(key, **fmt)

    def _ask(self, title_key: str, text_key: str, **fmt: object) -> bool:
        reply = QMessageBox.question(
            self._parent,
            self._m(title_key),
            self._m(text_key, **fmt),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        return reply == QMessageBox.StandardButton.Yes

    def _csv_target(self, title: str, proposal: Path) -> Path | None:
        path, _ = QFileDialog.getSaveFileName(
            self._parent, title, str(proposal), self._m("save.csv_filter")
        )
        return Path(path) if path else None

    def run_startup_checks(self) -> None:
        """Offer to export unfinished journals, then to restore today's session."""
        session = self._session
        orphans = session.find_orphans()
        if orphans:
            if self._ask("session.orphans_title", "session.orphans_text", count=len(orphans)):
                for session_dir in orphans:
                    target = self._csv_target(
                        self._m("session.orphan_export_title", name=session_dir.name),
                        Path.home() / f"recovery_{session_dir.name}.csv",
                    )
                    if target is not None:
                        session.export_orphan(session_dir, target)
            else:
                # Dismissed: delete them so they do not reappear on the next launch.
                session.discard_orphans(orphans)

        state = session.restorable_state()
        session.arm()
        if state is not None and self._ask("session.restore_title", "session.restore_text"):
            session.restore(state)

    def offer_partial_export(self) -> None:
        """After a permanent connection loss: offer to export the data recorded so far."""
        journal = self._session.partial_journal()
        if journal is None:
            return
        if not self._ask("session.lost_title", "session.lost_text", count=journal.row_count):
            return
        target = self._csv_target(
            self._m("session.partial_export_title"), Path.home() / "messung_partial.csv"
        )
        if target is not None:
            self._session.export_partial(journal, target)
