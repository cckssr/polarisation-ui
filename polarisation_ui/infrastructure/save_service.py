"""!/usr/bin/env python
Data persistence and file management for measurement sessions.

This module provides services for saving, loading, and managing measurement data
to disk. It handles CSV export, metadata creation, automatic backups, and
directory management. All I/O operations are encapsulated here, separated from
core business logic.

Features:
    - CSV data export with metadata
    - Automatic file naming and organization
    - Incremental backup creation
    - Metadata management (Dublin Core fields)
    - Configurable storage locations
    - Old backup cleanup

Usage:
    Initialize and save measurement data:

    >>> save_service = MeasurementSaveService(base_dir="/path/to/data")
    >>> file_path = save_service.save_measurement(
    ...     file_name="data/measurement_001.csv",
    ...     data=csv_rows,
    ...     metadata=metadata_dict
    ... )
    >>> backup_path = save_service.auto_backup(data, start_time, sample_id)

Dependencies:
    - pathlib (standard library)
    - csv (standard library)
    - json (standard library)
    - polarisation_ui.infrastructure.logging (Debug)
    - polarisation_ui.infrastructure.utils (folder naming)
"""

import csv
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List

from .logging import Debug
from .utils import (
    create_dropbox_foldername,
    sanitize_subterm_for_folder,
    create_group_name,
)


class MeasurementSaveService:
    """
    File I/O service for saving and managing measurement data.

    Handles CSV export, metadata creation, automatic backups, and directory
    organization. Operates independently from core business logic, providing
    a clean interface for persisting measurement data.
    """

    def __init__(
        self,
        base_dir: Optional[Path | str] = None,
        tk_designation: str = "TKXX",
    ):
        """
        Initialize the measurement save service.

        Args:
            base_dir: Base directory for storing measurement files.
                     Defaults to ~/Documents/MeasurementData.
            tk_designation: Test kit designation (e.g., "TK08").
                           Default "TKXX".
        """
        if base_dir is None:
            base_dir = Path.home() / "Documents" / "MeasurementData"
        if isinstance(base_dir, str):
            base_dir = Path(base_dir)

        self.base_dir = Path(base_dir)
        self.tk_designation = tk_designation
        self.index = 0
        self._backup_counter = 0
        self._unsaved = False

        Debug.info(f"Measurement save service initialized: {self.base_dir}")
        try:
            self.base_dir.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            Debug.error(f"Failed to create base directory {self.base_dir}: {exc}")

    def has_unsaved(self) -> bool:
        """
        Check if there is unsaved measurement data.

        Returns:
            bool: True if data has been modified since last save.
        """
        return self._unsaved

    def mark_saved(self):
        """Mark current data as saved."""
        self._unsaved = False

    def mark_unsaved(self):
        """Mark current data as modified."""
        self._unsaved = True

    def generate_filename(
        self,
        identifier: str,
        group_letter: str,
        subterm: str = "",
        suffix: str = "",
        extension: str = ".csv",
    ) -> str:
        """
        Generate standardized measurement file name with folder structure.

        Creates Dropbox-compatible folder paths following naming conventions:
        `<Day><Group><TK>-<Subterm>/YYYY_MM_DD-NN-identifier.csv`

        Args:
            identifier: Measurement identifier (e.g., sample name).
            group_letter: Group letter (A-Z).
            subterm: Optional subgroup term for folder organization.
            suffix: Optional suffix (e.g., "-run1"). Auto-prefixed with dash.
            extension: File extension including leading dot. Default ".csv".

        Returns:
            str: Generated file path with folder structure.

        Raises:
            ValueError: If identifier or group_letter is empty/invalid.
        """
        if not identifier:
            raise ValueError("Identifier cannot be empty")
        if not group_letter:
            raise ValueError("Group letter cannot be empty")

        timestamp = datetime.now().strftime("%Y_%m_%d")
        if suffix and not suffix.startswith("-"):
            suffix = "-" + suffix
        self.index += 1

        # Create folder structure
        sanitized_subterm = ""
        if subterm:
            sanitized_subterm = sanitize_subterm_for_folder(subterm, max_length=20)
        folder_name = create_dropbox_foldername(
            group_letter, self.tk_designation, sanitized_subterm
        )

        filename = f"{timestamp}-{self.index:02d}-{identifier}{suffix}{extension}"
        return f"{folder_name}/{filename}"

    def create_metadata(
        self,
        start_time: datetime,
        end_time: datetime,
        group: str,
        identifier: str,
        subterm: str = "",
        extra_fields: dict | None = None,
    ) -> dict:
        """
        Create metadata dictionary for a measurement session.

        Uses Dublin Core fields for standardization. Can be extended with
        custom fields via extra_fields parameter.

        Args:
            start_time: Measurement start timestamp.
            end_time: Measurement end timestamp.
            group: Group identifier/name.
            identifier: Measurement identifier.
            subterm: Optional subgroup term.
            extra_fields: Additional metadata fields (e.g., device info).

        Returns:
            dict: Metadata dictionary.
        """
        group_name = (
            group if group and len(str(group)) > 1 else create_group_name(group)
        )
        metadata = {
            "dc:date": start_time.strftime("%Y-%m-%d"),
            "dc:creator": group_name,
            "dc:title": identifier,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "identifier": identifier,
            "subgroup": subterm if subterm else "",
        }
        if extra_fields:
            metadata.update(extra_fields)
        return metadata

    def save_measurement(
        self, file_name: str, data: List[List[str]], metadata: dict
    ) -> Path:
        """
        Save CSV measurement data with metadata.

        Saves data as CSV and metadata as JSON alongside it. Creates
        parent directories automatically if needed.

        Args:
            file_name: File path (absolute or relative to base_dir).
            data: List of rows (including header row).
            metadata: Metadata dictionary.

        Returns:
            Path: Full path to saved CSV file.

        Raises:
            IOError: If file operations fail.
        """
        csv_path = Path(file_name)
        if not csv_path.is_absolute():
            csv_path = self.base_dir / csv_path

        csv_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(csv_path, "w", newline="", encoding="utf-8") as csv_f:
                writer = csv.writer(csv_f)
                writer.writerows(data)

            # Save metadata as JSON
            metadata_path = csv_path.parent / (csv_path.stem + "_metadata.json")
            with open(metadata_path, "w", encoding="utf-8") as js_f:
                json.dump(metadata, js_f, indent=2)

            Debug.info(f"Measurement saved: {csv_path}")
            self.mark_saved()
        except Exception as exc:
            Debug.error(f"Failed to save measurement: {exc}", exc_info=exc)
            raise IOError(f"Save failed: {exc}") from exc

        return csv_path

    def auto_save(
        self,
        identifier: str,
        group_letter: str,
        data: List[List[str]],
        start_time: datetime,
        end_time: datetime,
        subterm: str = "",
        suffix: str = "",
    ) -> Optional[Path]:
        """
        Automatically save measurement with generated file name.

        Convenience method that generates the file name, creates metadata,
        and saves in one call.

        Args:
            identifier: Measurement identifier.
            group_letter: Group letter.
            data: CSV rows including header.
            start_time: Measurement start time.
            end_time: Measurement end time.
            subterm: Optional subgroup term.
            suffix: Optional suffix.

        Returns:
            Path to saved file, or None if save failed.
        """
        if not data:
            Debug.error("No data to auto-save")
            return None

        try:
            file_name = self.generate_filename(
                identifier, group_letter, subterm, suffix
            )
            metadata = self.create_metadata(
                start_time, end_time, group_letter, identifier, subterm
            )
            return self.save_measurement(file_name, data, metadata)
        except Exception as exc:
            Debug.error(f"Auto-save failed: {exc}", exc_info=exc)
            return None

    def auto_backup(
        self,
        data: List[List[str]],
        start_time: datetime,
        identifier: str = "unknown",
        group_letter: str = "unknown",
        subterm: str = "",
        extra_metadata: dict | None = None,
    ) -> Optional[Path]:
        """
        Create incremental backup of measurement data.

        Designed for periodic calls during long measurements to create
        recovery points. Old backups are automatically cleaned up.

        Args:
            data: CSV rows including header.
            start_time: Measurement start time.
            identifier: Measurement identifier. Default "unknown".
            group_letter: Group letter. Default "unknown".
            subterm: Optional subgroup term.
            extra_metadata: Additional metadata (device info, version, etc).

        Returns:
            Path to backup file, or None if no data or backup failed.
        """
        if not data or len(data) <= 1:  # Only header present
            return None

        try:
            backup_dir = self.base_dir / ".backup"
            backup_dir.mkdir(parents=True, exist_ok=True)

            # Create unique backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self._backup_counter += 1
            backup_filename = f"backup_{timestamp}_{self._backup_counter:03d}.csv"
            backup_path = backup_dir / backup_filename

            # Create and save metadata
            metadata = self.create_metadata(
                start_time,
                datetime.now(),
                group_letter,
                identifier,
                subterm,
                extra_fields=extra_metadata,
            )

            # Save CSV
            with open(backup_path, "w", newline="", encoding="utf-8") as csv_f:
                writer = csv.writer(csv_f)
                writer.writerows(data)

            # Save metadata
            metadata_path = backup_path.parent / (backup_path.stem + "_metadata.json")
            with open(metadata_path, "w", encoding="utf-8") as js_f:
                json.dump(metadata, js_f, indent=2)

            Debug.debug(f"Backup created: {backup_path} ({len(data)-1} data points)")

            # Cleanup old backups
            self.cleanup_old_backups(backup_dir)

            return backup_path

        except Exception as exc:
            Debug.error(f"Backup failed: {exc}", exc_info=exc)
            return None

    def save_calibration_run(
        self,
        output_path: Path,
        data: list[list[str]],
        firmware_version: str = "unknown",
        config_snapshot: Optional[dict] = None,
    ) -> Path:
        """
        Save a calibration run CSV with a YAML-ish header.

        The header carries the firmware version and the full ``CONF:*`` config
        snapshot so the file is self-describing.  The body is written as plain
        CSV with column headers on the first non-comment row.

        Args:
            output_path:      Destination file (absolute).  Parent dirs are
                              created automatically.
            data:             List of rows **including** the column-header row.
                              Each row is a list of strings.
            firmware_version: Firmware IDN version string, e.g. ``"2.0.0"``.
            config_snapshot:  Dict of CONF:* settings captured at run start
                              (e.g. from ``DesiredState.as_config_snapshot()``).

        Returns:
            The resolved absolute path of the written file.

        Raises:
            IOError: On any file I/O failure.
        """
        if config_snapshot is None:
            config_snapshot = {}

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(output_path, "w", newline="", encoding="utf-8") as fh:
                # YAML-ish comment header
                fh.write(f"# firmware_version: {firmware_version}\n")
                fh.write(f"# saved_ts: {datetime.now().isoformat()}\n")
                for key, value in config_snapshot.items():
                    safe_val = str(value).replace("\n", " ")
                    fh.write(f"# config_{key}: {safe_val}\n")

                writer = csv.writer(fh)
                writer.writerows(data)

            Debug.info(
                f"Calibration run saved: {output_path} "
                f"({len(data) - 1 if data else 0} data rows, "
                f"firmware={firmware_version})"
            )
        except Exception as exc:
            Debug.error(f"Failed to save calibration run: {exc}", exc_info=exc)
            raise IOError(f"Calibration save failed: {exc}") from exc

        return output_path

    def cleanup_old_backups(self, backup_dir: Path, max_age_hours: int = 24):
        """
        Remove old backup files.

        Automatically called after backup creation. Removes backups older
        than max_age_hours along with their metadata files.

        Args:
            backup_dir: Directory containing backup files.
            max_age_hours: Maximum age in hours. Default 24.
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)

            for file in backup_dir.glob("backup_*.csv"):
                if file.stat().st_mtime < cutoff_time.timestamp():
                    file.unlink()
                    metadata_file = file.parent / (file.stem + "_metadata.json")
                    if metadata_file.exists():
                        metadata_file.unlink()
                    Debug.debug(f"Deleted old backup: {file}")
        except Exception as exc:
            Debug.info(f"Backup cleanup encountered error: {exc}")
