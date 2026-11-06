"""Measurement session: start / stop / reset, group + team + suffix naming, export, settings.

Holds the lab-group identity (group letter, team name, suffix) that composes the export file name
and the Dropbox folder, the one-time prefix lock after the first save, and the acquisition
(averaging) settings. File dialogs stay in the window: this controller computes the proposed
path and writes the file once the window has a target.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from polarisation_ui.core.detector import DETECTOR_PDTIA, DETECTOR_PM400
from polarisation_ui.core.models import AcquisitionSettings, TabExport
from polarisation_ui.infrastructure.config import AppConfig
from polarisation_ui.infrastructure.logging import Debug
from polarisation_ui.infrastructure.save_service import compose_filename, save_tab_export
from polarisation_ui.infrastructure.utils import (
    create_dropbox_foldername,
    sanitize_subterm_for_folder,
)
from polarisation_ui.ui.controllers.data_controller import DataController
from polarisation_ui.ui.controllers.detector_controller import DetectorController
from polarisation_ui.ui.controllers.status import StatusHub


class MeasurementController(QObject):
    """Measurement lifecycle, naming and export."""

    started = Signal()
    stopped = Signal()
    reset_performed = Signal()  # the tabs must drop their data
    group_changed = Signal(str)  # group letter, "" when none is selected
    team_changed = Signal(str)
    suffix_changed = Signal(str)
    prefix_locked_changed = Signal(bool)  # group + team are frozen after the first save
    acq_settings_replaced = Signal(object)  # AcquisitionSettings set by a dialog or a restore
    persist_requested = Signal()

    def __init__(
        self,
        config: AppConfig,
        data: DataController,
        status: StatusHub,
        detector: DetectorController,
        parent: QObject | None = None,
    ) -> None:
        """Load the acquisition defaults from ``acquisition`` in config.json."""
        super().__init__(parent)
        self._cfg = config
        self._data = data
        self._status = status
        self._detector = detector
        self._group = ""
        self._team = ""
        self._suffix = ""
        self._prefix_locked = False
        self._acq_settings = AcquisitionSettings.from_config(config.section("acquisition"))
        data.update_acq_settings(self._acq_settings)
        data.measurement_started.connect(self.started)
        data.measurement_stopped.connect(self.stopped)

    def _m(self, key: str, **fmt: object) -> str:
        return self._cfg.message(f"measurement.{key}", **fmt)

    # ---- state ---------------------------------------------------------------------------
    @property
    def is_measuring(self) -> bool:
        """True while a measurement session runs."""
        return self._data.is_measuring()

    @property
    def group_letter(self) -> str:
        """Selected lab-group letter ("" when none)."""
        return self._group

    @property
    def group_selected(self) -> bool:
        """True once a group letter is chosen (experiment tabs unlock)."""
        return bool(self._group)

    @property
    def team_name(self) -> str:
        """Team name used as the Dropbox folder sub-term."""
        return self._team

    @property
    def suffix(self) -> str:
        """Free text appended to the file name."""
        return self._suffix

    @property
    def prefix_locked(self) -> bool:
        """True after the first save (group letter and team name are then frozen)."""
        return self._prefix_locked

    @property
    def acq_settings(self) -> AcquisitionSettings:
        """The current acquisition (averaging, spike filter) settings."""
        return self._acq_settings

    @Slot(str)
    def set_group(self, letter: str) -> None:
        """Select the group letter ("" clears the selection)."""
        letter = letter.strip()
        if letter != self._group:
            self._group = letter
            self.group_changed.emit(letter)
            self.persist_requested.emit()

    @Slot(str)
    def set_team(self, name: str) -> None:
        """Set the team name."""
        name = name.strip()
        if name != self._team:
            self._team = name
            self.team_changed.emit(name)
            self.persist_requested.emit()

    @Slot(str)
    def set_suffix(self, suffix: str) -> None:
        """Set the file-name suffix."""
        suffix = suffix.strip()
        if suffix != self._suffix:
            self._suffix = suffix
            self.suffix_changed.emit(suffix)
            self.persist_requested.emit()

    # ---- acquisition settings ------------------------------------------------------------
    def set_acq_settings_inline(self, settings: AcquisitionSettings) -> None:
        """Apply averaging settings edited in the configuration tab (persisted)."""
        self._acq_settings = settings
        self._data.update_acq_settings(settings)
        self.persist_requested.emit()

    def replace_acq_settings(self, settings: AcquisitionSettings) -> None:
        """Apply settings from the dialog or a session restore; the inline controls follow."""
        self._acq_settings = settings
        self._data.update_acq_settings(settings)
        self.acq_settings_replaced.emit(settings)

    # ---- start / stop / reset ------------------------------------------------------------
    @Slot()
    def start(self) -> bool:
        """Start a measurement session."""
        if self._data.start_measurement():
            self._status.success(self._m("started"))
            Debug.info("Measurement session started")
            return True
        self._status.error(self._m("start_failed"))
        return False

    @Slot()
    def stop(self) -> None:
        """Stop the measurement session."""
        self._data.stop_measurement()
        self._status.info(self._m("stopped"))
        Debug.info("Measurement session stopped")

    @Slot()
    def reset(self) -> None:
        """Ask all tabs to drop their data."""
        self.reset_performed.emit()
        self._status.info(self._m("reset"))
        Debug.info("Measurement data reset")

    # ---- naming --------------------------------------------------------------------------
    def filename_tokens(self, tokens: list[str]) -> list[str]:
        """Append the calibration wavelength (if a profile defines one) as a file-name token."""
        profile = self._detector.calibration_profile
        if profile is not None and profile.wavelength_nm is not None:
            return [*tokens, f"{profile.wavelength_nm:g}nm"]
        return list(tokens)

    def folder_name(self) -> str:
        """Dropbox folder name for the current group and team."""
        tk = self._cfg.get("save.tk_designation", "TKXX")
        subterm = sanitize_subterm_for_folder(self._team) if self._team else ""
        return create_dropbox_foldername(self._group, tk, subterm)

    def file_stem(self, hint: str, tokens: list[str]) -> str:
        """File name stem (no extension) for an export with ``hint`` and ``tokens``."""
        return compose_filename(hint, self._group, self._suffix, self.filename_tokens(tokens))

    def filename_display(self, export: TabExport | None) -> str:
        """Expected ``folder/stem.csv`` for the active tab's export ("" while no group is set)."""
        if not self._group:
            return ""
        if export is not None:
            hint, tokens = export.filename_hint, export.filename_tokens
        else:
            hint, tokens = self._cfg.get("save.default_filename_hint", "messung"), []
        return f"{self.folder_name()}/{self.file_stem(hint, tokens)}.csv"

    # ---- save ----------------------------------------------------------------------------
    def default_save_path(self, export: TabExport) -> Path:
        """Proposed target in the group's Dropbox folder below the home directory (created)."""
        default_dir = Path.home() / self.folder_name()
        default_dir.mkdir(parents=True, exist_ok=True)
        return default_dir / f"{self.file_stem(export.filename_hint, export.filename_tokens)}.csv"

    def save_export(self, path: Path, export: TabExport) -> None:
        """Write ``export`` (CSV + metadata JSON) to ``path`` and lock the group/team prefix."""
        profile = self._detector.calibration_profile
        save_tab_export(
            path,
            export,
            group_letter=self._group,
            suffix=self._suffix,
            power_cal_meta=profile.to_save_metadata() if profile is not None else {},
            saved_at=datetime.now(),
            active_detector=DETECTOR_PM400 if self._data.is_pm400_active else DETECTOR_PDTIA,
        )
        self._status.success(self._cfg.message("save.saved", count=len(export.rows), path=path))
        if not self._prefix_locked:
            self._prefix_locked = True
            self.prefix_locked_changed.emit(True)
            Debug.info("Group/team prefix locked after first save")
