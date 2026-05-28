"""Tests for polarisation_ui.core.calibration_hooks.

Verifies:
- CalibrationRecorder writes the YAML-ish header + CSV rows to disk.
- Config changes mid-run are recorded as inline comment lines.
- record_from_frame() correctly converts a core Frame to a CalibrationFrame.
- stop() is idempotent.
"""

import csv
from pathlib import Path

import pytest

from polarisation_ui.core.calibration_hooks import CalibrationFrame, CalibrationRecorder
from polarisation_ui.core.models import Frame

# ── helpers ────────────────────────────────────────────────────────────────────


def _make_frame(
    ts_ms: int = 1000,
    ang_a: float = 10.0,
    ang_b: float = 20.0,
    adc_v: float = 0.5,
    pd_gain: int = 0,
) -> CalibrationFrame:
    return CalibrationFrame(
        ts_ms=ts_ms,
        ang_a=ang_a,
        ang_b=ang_b,
        adc_v=adc_v,
        adc_temp=25.0,
        pd_gain=pd_gain,
    )


def _read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


# ── tests ──────────────────────────────────────────────────────────────────────


def test_header_written_on_start(tmp_path: Path) -> None:
    """Header comment lines appear before the CSV column row."""
    out = tmp_path / "calib.csv"
    rec = CalibrationRecorder(
        output_path=out,
        firmware_version="2.0.0",
        config_snapshot={"adc_gain": 8, "pdtia_gain": 2},
    )
    rec.start()
    rec.stop()

    lines = _read_lines(out)
    assert lines[0] == "# firmware_version: 2.0.0"
    assert any("start_ts" in ln for ln in lines)
    assert any("config_adc_gain: 8" in ln for ln in lines)
    assert any("config_pdtia_gain: 2" in ln for ln in lines)


def test_csv_column_row_present(tmp_path: Path) -> None:
    """The CSV column-header row is the first non-comment line."""
    out = tmp_path / "calib.csv"
    rec = CalibrationRecorder(output_path=out)
    rec.start()
    rec.stop()

    lines = [ln for ln in _read_lines(out) if not ln.startswith("#")]
    assert lines[0] == "ts_ms,ang_a,ang_b,adc_v,adc_temp,pd_gain"


def test_record_writes_data_rows(tmp_path: Path) -> None:
    """N recorded frames produce exactly N data rows in the CSV."""
    out = tmp_path / "calib.csv"
    rec = CalibrationRecorder(output_path=out)
    rec.start()

    frames = [_make_frame(ts_ms=i * 100, ang_a=float(i)) for i in range(5)]
    for f in frames:
        rec.record(f)

    rec.stop()
    assert rec.row_count == 5

    # Parse only non-comment lines
    data_lines = [ln for ln in _read_lines(out) if not ln.startswith("#")]
    # First line is the column header
    rows = list(csv.reader(data_lines[1:]))
    assert len(rows) == 5
    assert float(rows[0][1]) == pytest.approx(0.0)  # ang_a of frame 0
    assert float(rows[4][1]) == pytest.approx(4.0)  # ang_a of frame 4


def test_config_change_emits_inline_comment(tmp_path: Path) -> None:
    """Mid-run config change produces a ``# config_change_*`` comment inline."""
    out = tmp_path / "calib.csv"
    config_v1 = {"adc_gain": 1}
    config_v2 = {"adc_gain": 8}

    rec = CalibrationRecorder(output_path=out, config_snapshot=config_v1)
    rec.start()
    rec.record(_make_frame(ts_ms=100))
    # Second frame carries a changed config snapshot
    frame_v2 = CalibrationFrame(
        ts_ms=200,
        ang_a=10.0,
        ang_b=20.0,
        adc_v=0.5,
        adc_temp=25.0,
        pd_gain=0,
        config_snapshot=config_v2,
    )
    rec.record(frame_v2)
    rec.stop()

    lines = _read_lines(out)
    change_lines = [ln for ln in lines if "config_change_adc_gain" in ln]
    assert len(change_lines) == 1
    assert "8" in change_lines[0]


def test_no_config_change_no_extra_comments(tmp_path: Path) -> None:
    """If config_snapshot is identical, no extra comment lines are added."""
    out = tmp_path / "calib.csv"
    config = {"adc_gain": 4}
    rec = CalibrationRecorder(output_path=out, config_snapshot=config)
    rec.start()
    for i in range(3):
        frame = CalibrationFrame(
            ts_ms=i * 100,
            ang_a=0.0,
            ang_b=0.0,
            adc_v=0.0,
            adc_temp=None,
            pd_gain=0,
            config_snapshot=config,
        )
        rec.record(frame)
    rec.stop()

    lines = _read_lines(out)
    change_lines = [ln for ln in lines if "config_change" in ln]
    assert len(change_lines) == 0


def test_record_from_frame_converts_core_frame(tmp_path: Path) -> None:
    """record_from_frame() maps core Frame fields to the CSV correctly."""
    out = tmp_path / "calib.csv"
    rec = CalibrationRecorder(output_path=out)
    rec.start()

    core_frame = Frame(
        ts_ms=5000, sample_angle=45.0, detector_angle=90.0, intensity=0.123
    )
    rec.record_from_frame(core_frame, pd_gain=3, adc_temp=26.5)
    rec.stop()

    data_lines = [ln for ln in _read_lines(out) if not ln.startswith("#")]
    rows = list(csv.reader(data_lines[1:]))
    assert len(rows) == 1
    row = rows[0]
    assert int(row[0]) == 5000  # ts_ms
    assert float(row[1]) == pytest.approx(45.0)  # ang_a = sample_angle
    assert float(row[2]) == pytest.approx(90.0)  # ang_b = detector_angle
    assert float(row[3]) == pytest.approx(0.123)  # adc_v = intensity
    assert float(row[4]) == pytest.approx(26.5)  # adc_temp
    assert int(row[5]) == 3  # pd_gain


def test_adc_temp_none_written_as_empty(tmp_path: Path) -> None:
    """adc_temp=None produces an empty string in the CSV, not 'None'."""
    out = tmp_path / "calib.csv"
    rec = CalibrationRecorder(output_path=out)
    rec.start()
    rec.record(
        CalibrationFrame(
            ts_ms=1, ang_a=0.0, ang_b=0.0, adc_v=0.0, adc_temp=None, pd_gain=0
        )
    )
    rec.stop()

    data_lines = [ln for ln in _read_lines(out) if not ln.startswith("#")]
    rows = list(csv.reader(data_lines[1:]))
    assert rows[0][4] == ""


def test_stop_is_idempotent(tmp_path: Path) -> None:
    """Calling stop() twice does not raise."""
    out = tmp_path / "calib.csv"
    rec = CalibrationRecorder(output_path=out)
    rec.start()
    rec.stop()
    rec.stop()  # second call must be a no-op


def test_record_after_stop_is_noop(tmp_path: Path) -> None:
    """Recording after stop() does not raise and does not write extra rows."""
    out = tmp_path / "calib.csv"
    rec = CalibrationRecorder(output_path=out)
    rec.start()
    rec.record(_make_frame())
    rec.stop()
    rec.record(_make_frame())  # must be silently ignored

    assert rec.row_count == 1  # only the first frame
