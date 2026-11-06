"""Session persistence: debounced state saving, restore, orphan journals and partial export.

Every controller reports "something worth persisting changed" through ``persist_requested``; this
controller collects them into one debounced write of ``last_session.json``. Saving stays disarmed
until the start-up restore question was answered, so an early change cannot overwrite the session
file before it was offered for restore. With ``state_path=None`` nothing is read or written.
"""

from __future__ import annotations

import shutil
from collections.abc import Callable
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QObject, QTimer, Signal, Slot

from polarisation_ui.core.models import AcquisitionSettings
from polarisation_ui.infrastructure.config import AppConfig
from polarisation_ui.infrastructure.logging import Debug
from polarisation_ui.infrastructure.session_journal import SessionJournal
from polarisation_ui.infrastructure.session_state import (
    SessionState,
    has_restorable_data,
    is_from_today,
    load_session_state,
    save_session_state,
)
from polarisation_ui.ui.controllers.connection_controller import ConnectionController
from polarisation_ui.ui.controllers.data_controller import DataController
from polarisation_ui.ui.controllers.detector_controller import DetectorController
from polarisation_ui.ui.controllers.kdc_controller import KdcController
from polarisation_ui.ui.controllers.measurement_controller import MeasurementController
from polarisation_ui.ui.controllers.pm400_controller import PM400Controller
from polarisation_ui.ui.controllers.status import StatusHub

SAVE_DEBOUNCE_MS = 500


class SessionController(QObject):
    """Saves and restores the working session; finds and exports unfinished journals."""

    tab_points_restored = Signal(dict)  # {tab_id: [point dicts]}
    restored = Signal()

    def __init__(
        self,
        config: AppConfig,
        status: StatusHub,
        data: DataController,
        connection: ConnectionController,
        kdc: KdcController,
        pm400: PM400Controller,
        detector: DetectorController,
        measurement: MeasurementController,
        state_path: Path | None = None,
        journal_base: Path | None = None,
        parent: QObject | None = None,
    ) -> None:
        """Subscribe to the controllers' ``persist_requested`` signals."""
        super().__init__(parent)
        self._cfg = config
        self._status = status
        self._data = data
        self._kdc = kdc
        self._pm400 = pm400
        self._detector = detector
        self._measurement = measurement
        self.state_path = state_path
        self.journal_base = journal_base
        self._armed = False
        self._tab_points: Callable[[], dict[str, list[dict]]] = dict

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(SAVE_DEBOUNCE_MS)
        self._timer.timeout.connect(self.save_state)
        for controller in (connection, kdc, pm400, detector, measurement):
            controller.persist_requested.connect(self.schedule_save)

    def _m(self, key: str, **fmt: object) -> str:
        return self._cfg.message(f"session.{key}", **fmt)

    @property
    def enabled(self) -> bool:
        """True when a state file is configured."""
        return self.state_path is not None

    def set_tab_points_provider(self, provider: Callable[[], dict[str, list[dict]]]) -> None:
        """Function returning the saved points of every tab as ``{tab_id: [dicts]}``."""
        self._tab_points = provider

    # ---- saving --------------------------------------------------------------------------
    def arm(self) -> None:
        """Allow saving (called once the start-up restore question was settled)."""
        self._armed = True

    @Slot()
    def schedule_save(self) -> None:
        """Restart the debounce so the state is written 500 ms after the last change."""
        if self.enabled and self._armed:
            self._timer.start()

    def build_state(self) -> SessionState:
        """Snapshot the persistable state of all controllers."""
        now = datetime.now()
        acq = self._measurement.acq_settings
        return SessionState(
            saved_date=now.date().isoformat(),
            saved_at=now.isoformat(),
            group_letter=self._measurement.group_letter,
            team_name=self._measurement.team_name,
            suffix=self._measurement.suffix,
            profile_name=self._detector.profile_name,
            gain_stage=self._data.pdtia_gain,
            detector_offset_deg=self._data.detector_offset_deg,
            kdc_zero_offset_deg=self._kdc.zero_offset_deg,
            pm400_visa_resource=self._pm400.resource,
            pm400_wavelength_nm=self._pm400.wavelength_nm,
            pdtia_id=self._detector.pdtia_id,
            acq_settings=asdict(acq),
            tab_points=self._tab_points(),
        )

    @Slot()
    def save_state(self) -> None:
        """Write the state file now."""
        if self.state_path is None:
            return
        try:
            save_session_state(self.build_state(), self.state_path)
        except OSError as exc:
            Debug.warning(f"Could not save session state: {exc}")

    # ---- restoring -----------------------------------------------------------------------
    def restorable_state(self) -> SessionState | None:
        """Today's saved state if it holds anything worth restoring."""
        if self.state_path is None:
            return None
        state = load_session_state(self.state_path)
        if state is None or not is_from_today(state) or not has_restorable_data(state):
            return None
        return state

    def restore(self, state: SessionState) -> None:
        """Apply a saved state to the controllers (the window follows via their signals)."""
        m = self._measurement
        if state.group_letter:
            m.set_group(state.group_letter)
        if state.team_name:
            m.set_team(state.team_name)
        if state.suffix:
            m.set_suffix(state.suffix)
        if state.profile_name:
            self._detector.select_profile_by_name(state.profile_name)
        if state.pdtia_id:
            self._detector.restore_pdtia_id(state.pdtia_id)
        self._detector.set_pending_gain(state.gain_stage)
        if state.detector_offset_deg in (0.0, 180.0):
            self._data.set_detector_offset(state.detector_offset_deg)
        if state.kdc_zero_offset_deg:
            self._kdc.set_zero_offset(state.kdc_zero_offset_deg)
        if state.pm400_visa_resource:
            self._pm400.select_resource(state.pm400_visa_resource)
        if state.pm400_wavelength_nm:
            self._pm400.set_wavelength(state.pm400_wavelength_nm)
        if state.acq_settings:
            self._restore_acq_settings(state.acq_settings)
        self.tab_points_restored.emit(state.tab_points)
        self._status.success(self._m("restored"))
        self.restored.emit()

    def _restore_acq_settings(self, saved: dict) -> None:
        current = asdict(self._measurement.acq_settings)
        try:
            merged = {k: saved.get(k, v) for k, v in current.items()}
            self._measurement.replace_acq_settings(AcquisitionSettings(**merged))
        except Exception as exc:
            Debug.warning(f"Could not restore acquisition settings: {exc}")

    # ---- journals ------------------------------------------------------------------------
    def find_orphans(self) -> list[Path]:
        """Unfinished session journals left behind by a crash (none when persistence is off)."""
        if self.state_path is None:
            return []
        return SessionJournal.find_orphans(self.journal_base)

    def discard_orphans(self, session_dirs: list[Path]) -> None:
        """Delete orphaned journals so they do not reappear on the next launch."""
        for session_dir in session_dirs:
            try:
                shutil.rmtree(session_dir)
                Debug.info(f"Orphan journal deleted: {session_dir}")
            except OSError as exc:
                Debug.warning(f"Could not delete orphan {session_dir}: {exc}")

    def export_orphan(self, session_dir: Path, target: Path) -> int:
        """Export an orphaned journal to ``target`` and mark it finalized; returns the rows."""
        rows = SessionJournal.export_orphan(session_dir, target)
        self._status.success(self._m("orphan_exported", rows=rows, path=target))
        return rows

    def partial_journal(self) -> SessionJournal | None:
        """The current journal if it holds data (offered for export after a permanent loss)."""
        journal = self._data.current_journal
        return journal if journal is not None and journal.row_count > 0 else None

    def export_partial(self, journal: SessionJournal, target: Path) -> int:
        """Export the partial data of ``journal`` to ``target``; returns the rows."""
        rows = journal.export_to_csv(target, finalize=True)
        self._status.success(self._m("partial_exported", rows=rows, path=target))
        return rows

    def shutdown(self) -> None:
        """Flush a pending debounced save (window close)."""
        if self._timer.isActive():
            self._timer.stop()
            if self._armed:
                self.save_state()
