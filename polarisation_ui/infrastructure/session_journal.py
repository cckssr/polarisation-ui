"""Append-only crash-safe session journal.

Every measurement frame is flushed to disk; fsync is called every ≤1 s so
at most 1 s of data is lost if the process is killed.  Each session lives in

    ~/.polarisation-ui/sessions/<YYYYMMDDTHHMMSS>/journal.csv

A session is "orphaned" when it has a journal.csv but no ``finalized`` marker.
Orphans are detected on next startup and offered for recovery export.

Usage::

    journal = SessionJournal(firmware_version="2.0.0")
    journal.start()
    for frame in frames:
        journal.append_frame(frame)
    journal.finalize()  # marks as done
    # OR
    journal.export_to_csv(path)  # export → finalize
"""

import csv
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from polarisation_ui.core.models import Frame
from polarisation_ui.infrastructure.logging import Debug

JOURNAL_BASE = Path.home() / ".polarisation-ui" / "sessions"
_FINALIZED = "finalized"


class SessionJournal:
    """One-per-measurement-session append-only journal.

    Thread-safety: all methods must be called from the same thread (the Qt
    main thread via DataController).  No locking is needed.
    """

    _FSYNC_INTERVAL_S: float = 1.0

    def __init__(
        self,
        firmware_version: str = "unknown",
        config_snapshot: Optional[dict] = None,
    ) -> None:
        ts = datetime.now().strftime("%Y%m%dT%H%M%S_%f")
        self._session_dir = JOURNAL_BASE / ts
        self._journal_path = self._session_dir / "journal.csv"
        self._firmware_version = firmware_version
        self._config_snapshot: dict = config_snapshot or {}
        self._file: Optional[object] = None
        self._writer: Optional[csv.writer] = None  # type: ignore[type-arg]
        self._last_fsync: float = 0.0
        self._row_count: int = 0

    # ── public properties ──────────────────────────────────────────────────────

    @property
    def session_dir(self) -> Path:
        return self._session_dir

    @property
    def journal_path(self) -> Path:
        return self._journal_path

    @property
    def is_active(self) -> bool:
        return self._file is not None

    @property
    def row_count(self) -> int:
        return self._row_count

    # ── lifecycle ──────────────────────────────────────────────────────────────

    def start(self) -> None:
        """Create the session directory and open the journal file for writing."""
        self._session_dir.mkdir(parents=True, exist_ok=True)
        f = open(self._journal_path, "w", newline="", encoding="utf-8")  # noqa: SIM115
        self._file = f
        # YAML-ish metadata header (lines starting with # are skipped on import)
        f.write(f"# firmware_version: {self._firmware_version}\n")
        f.write(f"# start_ts: {datetime.now().isoformat()}\n")
        for key, value in self._config_snapshot.items():
            safe_val = str(value).replace("\n", " ")
            f.write(f"# config_{key}: {safe_val}\n")
        self._writer = csv.writer(f)
        if self._writer:
            self._writer.writerow(
                ["ts_ms", "sample_angle", "detector_angle", "intensity", "gap"]
            )
        else:
            Debug.error("SessionJournal failed to initialize CSV writer")
        f.flush()
        self._last_fsync = time.monotonic()
        Debug.info(f"SessionJournal started: {self._journal_path}")

    def append_frame(self, frame: Frame) -> None:
        """Write one data row; flush Python buffer every call, fsync every ~1 s."""
        if self._writer is None or self._file is None:
            return
        self._writer.writerow(
            [
                frame.ts_ms,
                f"{frame.sample_angle:.4f}",
                f"{frame.detector_angle:.4f}",
                f"{frame.intensity:.6f}",
                "",
            ]
        )
        self._row_count += 1
        f = self._file
        f.flush()  # type: ignore[union-attr]
        now = time.monotonic()
        if now - self._last_fsync >= self._FSYNC_INTERVAL_S:
            os.fsync(f.fileno())  # type: ignore[union-attr]
            self._last_fsync = now

    def append_gap(self) -> None:
        """Record a reconnection gap; force-syncs to disk immediately."""
        if self._writer is None or self._file is None:
            return
        self._writer.writerow(
            [
                int(time.monotonic() * 1000),
                "",
                "",
                "",
                "1",
            ]
        )
        f = self._file
        f.flush()  # type: ignore[union-attr]
        os.fsync(f.fileno())  # type: ignore[union-attr]
        self._last_fsync = time.monotonic()
        Debug.debug("SessionJournal gap marker written")

    def close(self) -> None:
        """Flush and close the file without adding a finalized marker (recoverable)."""
        if self._file is None:
            return
        try:
            self._file.flush()  # type: ignore[union-attr]
            os.fsync(self._file.fileno())  # type: ignore[union-attr]
        finally:
            self._file.close()  # type: ignore[union-attr]
            self._file = None
            self._writer = None
        Debug.info(f"SessionJournal closed (not finalized, {self._row_count} rows)")

    def finalize(self) -> None:
        """Flush, close, and write the finalized marker — no longer an orphan."""
        self.close()
        (self._session_dir / _FINALIZED).touch()
        Debug.info(f"SessionJournal finalized: {self._journal_path}")

    # ── export ─────────────────────────────────────────────────────────────────

    def export_to_csv(self, output_path: Path, finalize: bool = True) -> int:
        """Export data rows (no gaps, no header comments) to *output_path*.

        Returns the number of rows written.  Calls finalize() afterwards
        unless *finalize* is False.
        """
        rows_written = _copy_data_rows(self._journal_path, output_path)
        if finalize:
            self.finalize()
        return rows_written

    # ── class-level helpers ────────────────────────────────────────────────────

    @classmethod
    def find_orphans(cls) -> list[Path]:
        """Return a sorted list of session directories that are not finalized."""
        if not JOURNAL_BASE.exists():
            return []
        orphans: list[Path] = []
        for d in sorted(JOURNAL_BASE.iterdir()):
            if not d.is_dir():
                continue
            if (d / "journal.csv").exists() and not (d / _FINALIZED).exists():
                orphans.append(d)
        return orphans

    @classmethod
    def export_orphan(cls, session_dir: Path, output_path: Path) -> int:
        """Export an orphaned session to *output_path* and mark it finalized.

        Returns the number of data rows exported.
        """
        journal_path = session_dir / "journal.csv"
        rows = _copy_data_rows(journal_path, output_path)
        (session_dir / _FINALIZED).touch()
        Debug.info(f"Orphan exported: {session_dir.name} → {output_path} ({rows} rows)")
        return rows


# ── module-level helper ────────────────────────────────────────────────────────


def _copy_data_rows(src: Path, dst: Path) -> int:
    """Read *src* journal and write only non-gap data rows to *dst*.

    Comments (lines starting with ``#``) and gap rows are skipped.
    Returns the number of data rows written.
    """
    rows_written = 0
    try:
        with open(src, "r", encoding="utf-8") as fh_in:
            with open(dst, "w", newline="", encoding="utf-8") as fh_out:
                writer = csv.writer(fh_out)
                writer.writerow(
                    ["ts_ms", "sample_angle", "detector_angle", "intensity"]
                )
                header_skipped = False
                for raw_line in fh_in:
                    line = raw_line.rstrip("\n")
                    if line.startswith("#") or not line.strip():
                        continue
                    row = next(csv.reader([line]))
                    if not header_skipped:
                        header_skipped = True  # skip the column-header row
                        continue
                    # gap rows have "1" in the 5th column
                    if len(row) >= 5 and row[4] == "1":
                        continue
                    if len(row) >= 4:
                        writer.writerow(row[:4])
                        rows_written += 1
    except (OSError, csv.Error, StopIteration) as e:
        Debug.error(f"SessionJournal export failed: {e}")
    return rows_written
