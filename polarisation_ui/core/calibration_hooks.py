"""Calibration hooks — pure-Python data surface.

No Qt, no serial imports.  Importable by both the main app and the
calibration_tool sibling app.

Classes:
    CalibrationFrame    — one data point captured during a calibration run.
    CalibrationRecorder — write CalibrationFrames to an append-safe CSV with a
                          YAML-ish header that carries firmware version + config.

Config-change tracking
----------------------
A config snapshot is written as comment lines to the CSV header at run start.
If the caller passes a ``config_snapshot`` on a subsequent ``record()`` call
that differs from the previous snapshot, a new comment block is inserted inline
so the file is self-describing even when settings change mid-run.
"""

import csv
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from polarisation_ui.core.models import Frame

_log = logging.getLogger(__name__)


@dataclass
class CalibrationFrame:
    """One data point captured during a calibration run."""

    ts_ms: int
    ang_a: float  # sample-stage angle (degrees)
    ang_b: float  # detector-arm angle (degrees)
    adc_v: float  # ADS1220 voltage (V)
    adc_temp: Optional[float]  # ADS1220 internal temperature (°C), or None
    pd_gain: int  # current PD-TIA discrete gain stage
    config_snapshot: Optional[dict] = None  # CONF:* settings at this point


class CalibrationRecorder:
    """Write CalibrationFrames to an append-safe CSV.

    The output file has a YAML-ish comment header followed by a standard CSV.
    Comment lines (starting with ``#``) are skipped by most CSV importers and
    can be parsed manually.  The header is written once at ``start()``;
    mid-run config changes produce additional ``# config_change_*`` comment
    lines inline before the affected data row.

    Example:
        rec = CalibrationRecorder(
            output_path=Path("calib_20250101.csv"),
            firmware_version="2.0.0",
            config_snapshot={"adc_gain": 8, "pdtia_gain": 2},
        )
        rec.start()
        rec.record(CalibrationFrame(ts_ms=..., ang_a=..., ...))
        # or, if you have a core Frame from DataController.frame_ready:
        rec.record_from_frame(frame, pd_gain=2)
        rec.stop()
    """

    _FSYNC_INTERVAL_S: float = 1.0

    def __init__(
        self,
        output_path: Path,
        firmware_version: str = "unknown",
        config_snapshot: Optional[dict] = None,
    ) -> None:
        self._path = output_path
        self._firmware_version = firmware_version
        self._config_snapshot: dict = config_snapshot or {}
        self._file: Optional[object] = None
        self._writer: Optional[csv.writer] = None  # type: ignore[type-arg]
        self._last_fsync: float = 0.0
        self._row_count: int = 0
        self._active: bool = False
        # Track last-seen config to detect mid-run changes.
        self._last_config: dict = dict(self._config_snapshot)

    # ── public properties ──────────────────────────────────────────────────────

    @property
    def is_active(self) -> bool:
        """True between start() and stop()."""
        return self._active

    @property
    def row_count(self) -> int:
        """Number of data rows written so far."""
        return self._row_count

    @property
    def output_path(self) -> Path:
        return self._path

    # ── lifecycle ──────────────────────────────────────────────────────────────

    def start(self) -> None:
        """Create the output file and write the YAML-ish header + CSV column row."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        f = open(self._path, "w", newline="", encoding="utf-8")  # noqa: SIM115
        self._file = f
        f.write(f"# firmware_version: {self._firmware_version}\n")
        f.write(f"# start_ts: {datetime.now().isoformat()}\n")
        for key, value in self._config_snapshot.items():
            safe_val = str(value).replace("\n", " ")
            f.write(f"# config_{key}: {safe_val}\n")
        self._writer = csv.writer(f)
        if self._writer:
            self._writer.writerow(
                ["ts_ms", "ang_a", "ang_b", "adc_v", "adc_temp", "pd_gain"]
            )
        else:
            raise RuntimeError("Failed to create CSV writer")
        f.flush()  # type: ignore[union-attr]
        self._last_fsync = time.monotonic()
        self._active = True
        _log.info("CalibrationRecorder started: %s", self._path)

    def record(self, frame: CalibrationFrame) -> None:
        """Write one calibration frame row.  No-op when not active."""
        if not self._active or self._writer is None or self._file is None:
            return

        # Detect config change — insert an inline comment block before the row.
        if (
            frame.config_snapshot is not None
            and frame.config_snapshot != self._last_config
        ):
            for key, value in frame.config_snapshot.items():
                safe_val = str(value).replace("\n", " ")
                self._file.write(  # type: ignore[union-attr]
                    f"# config_change_{key}: {safe_val}\n"
                )
            self._last_config = dict(frame.config_snapshot)

        self._writer.writerow(
            [
                frame.ts_ms,
                f"{frame.ang_a:.4f}",
                f"{frame.ang_b:.4f}",
                f"{frame.adc_v:.6f}",
                f"{frame.adc_temp:.3f}" if frame.adc_temp is not None else "",
                frame.pd_gain,
            ]
        )
        self._row_count += 1
        self._file.flush()  # type: ignore[union-attr]
        now = time.monotonic()
        if now - self._last_fsync >= self._FSYNC_INTERVAL_S:
            os.fsync(self._file.fileno())  # type: ignore[union-attr]
            self._last_fsync = now

    def record_from_frame(
        self,
        frame: Frame,
        pd_gain: int = 0,
        adc_temp: Optional[float] = None,
        config_snapshot: Optional[dict] = None,
    ) -> None:
        """Convenience wrapper: convert a core ``Frame`` to ``CalibrationFrame`` and record.

        Intended for use when connected to ``DataController.frame_ready``::

            rec.start()
            data_controller.frame_ready.connect(
                lambda f: rec.record_from_frame(f, pd_gain=current_gain)
            )
        """
        cal_frame = CalibrationFrame(
            ts_ms=frame.ts_ms,
            ang_a=frame.sample_angle,
            ang_b=frame.detector_angle,
            adc_v=frame.intensity,
            adc_temp=adc_temp,
            pd_gain=pd_gain,
            config_snapshot=config_snapshot,
        )
        self.record(cal_frame)

    def stop(self) -> None:
        """Flush, fsync, and close the output file."""
        if not self._active or self._file is None:
            return
        try:
            self._file.flush()  # type: ignore[union-attr]
            os.fsync(self._file.fileno())  # type: ignore[union-attr]
        finally:
            self._file.close()  # type: ignore[union-attr]
            self._file = None
            self._writer = None
            self._active = False
        _log.info(
            "CalibrationRecorder stopped (%d rows): %s", self._row_count, self._path
        )
