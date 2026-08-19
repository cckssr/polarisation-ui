"""Tests for the new compose_filename and save_tab_export helpers."""

import json
from datetime import datetime

from polarisation_ui.core.models import TabExport
from polarisation_ui.infrastructure.save_service import (
    compose_filename,
    save_tab_export,
)

# ---------------------------------------------------------------------------
# compose_filename
# ---------------------------------------------------------------------------


def test_compose_filename_no_tokens_no_suffix():
    assert compose_filename("brewster", "A") == "messung_brewster_A"


def test_compose_filename_with_suffix():
    assert compose_filename("brewster", "A", "run1") == "messung_brewster_A_run1"


def test_compose_filename_with_tokens():
    assert compose_filename("brewster", "A", "", ["p"]) == "messung_brewster_p_A"


def test_compose_filename_with_tokens_and_suffix():
    assert compose_filename("brewster", "A", "run1", ["p"]) == "messung_brewster_p_A_run1"


def test_compose_filename_multiple_tokens():
    assert compose_filename("waveplate", "B", "", ["qwp"]) == "messung_waveplate_qwp_B"


def test_compose_filename_empty_tokens_list():
    assert compose_filename("malus", "C", "x", []) == "messung_malus_C_x"


# ---------------------------------------------------------------------------
# save_tab_export
# ---------------------------------------------------------------------------


def test_save_tab_export_writes_csv_and_metadata(tmp_path):
    exp = TabExport(
        filename_hint="brewster",
        columns=["sample_angle_deg", "intensity_V"],
        rows=[["30.0000", "0.5000"], ["45.0000", "0.3000"]],
        metadata={"polarisation": "p"},
        filename_tokens=["p"],
    )
    csv_path = tmp_path / "messung_brewster_p_A.csv"
    saved_at = datetime(2025, 1, 1, 12, 0, 0)

    save_tab_export(
        csv_path,
        exp,
        group_letter="A",
        suffix="",
        power_cal_meta={},
        saved_at=saved_at,
    )

    assert csv_path.exists()
    lines = csv_path.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "sample_angle_deg,intensity_V"
    assert lines[1] == "30.0000,0.5000"
    assert lines[2] == "45.0000,0.3000"

    meta_path = tmp_path / "messung_brewster_p_A_metadata.json"
    assert meta_path.exists()
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert meta["point_count"] == 2
    assert meta["group"] == "A"
    assert meta["polarisation"] == "p"
    assert meta["saved_at"] == "2025-01-01T12:00:00"


def test_save_tab_export_active_detector_defaults_to_pdtia(tmp_path):
    exp = TabExport(filename_hint="malus", columns=["a"], rows=[["1"]], metadata={})
    csv_path = tmp_path / "messung_malus_A.csv"
    save_tab_export(
        csv_path, exp, group_letter="A", suffix="", power_cal_meta={}, saved_at=datetime.now()
    )
    meta = json.loads((tmp_path / "messung_malus_A_metadata.json").read_text(encoding="utf-8"))
    assert meta["active_detector"] == "pdtia"


def test_save_tab_export_records_pm400_as_active_detector(tmp_path):
    """active_detector must be a top-level key, not nested in power_calibration —
    power_cal_meta is {} whenever no PD-TIA calibration profile is loaded, which
    is exactly the case where PM400 is likely to be the active detector."""
    exp = TabExport(filename_hint="malus", columns=["a"], rows=[["1"]], metadata={})
    csv_path = tmp_path / "messung_malus_A.csv"
    save_tab_export(
        csv_path,
        exp,
        group_letter="A",
        suffix="",
        power_cal_meta={},
        saved_at=datetime.now(),
        active_detector="pm400",
    )
    meta = json.loads((tmp_path / "messung_malus_A_metadata.json").read_text(encoding="utf-8"))
    assert meta["active_detector"] == "pm400"
    assert meta["power_calibration"] == {}


def test_save_tab_export_creates_parent_dirs(tmp_path):
    exp = TabExport(
        filename_hint="malus",
        columns=["a", "b"],
        rows=[["1", "2"]],
        metadata={},
    )
    csv_path = tmp_path / "group" / "messung_malus_B.csv"
    save_tab_export(
        csv_path,
        exp,
        group_letter="B",
        suffix="",
        power_cal_meta={},
        saved_at=datetime.now(),
    )
    assert csv_path.exists()
