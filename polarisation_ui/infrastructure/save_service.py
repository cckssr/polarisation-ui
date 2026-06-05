"""Data persistence — compose filenames and write TabExport bundles to CSV.

All production I/O for measurement exports lives here.  The two public
functions are ``compose_filename`` and ``save_tab_export``.
"""

import csv
import json
from collections.abc import Sequence
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from .logging import Debug

if TYPE_CHECKING:
    from polarisation_ui.core.models import TabExport

_SENSOR_METADATA_PATH = Path(__file__).parent.parent / "sensor_metadata.json"
with _SENSOR_METADATA_PATH.open("r", encoding="utf-8") as _f:
    SENSOR_DESCRIPTIONS: dict = json.load(_f)


def compose_filename(
    hint: str,
    group_letter: str,
    suffix: str = "",
    tokens: Sequence[str] = (),
) -> str:
    """Compose a measurement CSV file stem (no extension).

    Format: messung_{hint}_{tokens...}_{group_letter}[_{suffix}]
    """
    parts = ["messung", hint] + list(tokens) + [group_letter]
    if suffix:
        parts.append(suffix)
    return "_".join(parts)


def save_tab_export(
    csv_path: Path,
    exp: "TabExport",
    *,
    group_letter: str,
    suffix: str,
    power_cal_meta: dict,
    saved_at: datetime,
) -> None:
    """Write a TabExport to CSV + sibling metadata JSON.

    Does not open any dialogs — the caller must resolve the path first.
    """
    csv_path = Path(csv_path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(exp.columns)
        for row in exp.rows:
            writer.writerow(row)

    metadata: dict = {
        "saved_at": saved_at.isoformat(),
        "point_count": len(exp.rows),
        "group": group_letter,
        "suffix": suffix,
        "power_calibration": power_cal_meta,
        "sensors": SENSOR_DESCRIPTIONS,
        **exp.metadata,
    }
    metadata_path = csv_path.with_name(csv_path.stem + "_metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as fh:
        json.dump(metadata, fh, indent=2)

    Debug.info(f"Data exported to {csv_path} ({len(exp.rows)} points)")
