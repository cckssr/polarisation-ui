"""
Tests for MeasurementSaveService.

Verifies CSV output, metadata JSON correctness (including sensor descriptions),
backup creation and cleanup, calibration-run saves, and crash-recovery from the
temporary backup directory.

Run with: .venv/bin/pytest tests/infrastructure/test_save_service.py
"""

import csv
import json
import stat
import time
from datetime import datetime
from pathlib import Path

import pytest

from polarisation_ui.infrastructure.save_service import (
    MeasurementSaveService,
    SENSOR_DESCRIPTIONS,
)

# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def svc(tmp_path):
    return MeasurementSaveService(base_dir=tmp_path, tk_designation="TK01")


@pytest.fixture
def sample_data():
    return [
        ["ts_ms", "sample_angle", "detector_angle", "intensity"],
        ["1000", "10.0000", "20.0000", "512.000000"],
        ["1100", "10.5000", "21.0000", "498.000000"],
        ["1200", "11.0000", "22.0000", "523.000000"],
    ]


@pytest.fixture
def start_end():
    t0 = datetime(2025, 6, 1, 10, 0, 0)
    t1 = datetime(2025, 6, 1, 10, 5, 0)
    return t0, t1


@pytest.fixture
def sensor_metadata():
    with open(
        Path(__file__).parent.parent / "sensor_metadata.json", "r", encoding="utf-8"
    ) as f:
        return json.load(f)


# ── Unsaved tracking ──────────────────────────────────────────────────────────


class TestUnsavedTracking:
    def test_initial_state_is_not_unsaved(self, svc):
        assert not svc.has_unsaved()

    def test_mark_unsaved(self, svc):
        svc.mark_unsaved()
        assert svc.has_unsaved()

    def test_mark_saved_clears_flag(self, svc):
        svc.mark_unsaved()
        svc.mark_saved()
        assert not svc.has_unsaved()


# ── File naming ───────────────────────────────────────────────────────────────


class TestGenerateFilename:
    def test_returns_string_with_folder_and_file(self, svc):
        name = svc.generate_filename("MySample", "A")
        parts = name.split("/")
        assert len(parts) == 2  # folder/file

    def test_filename_contains_identifier(self, svc):
        name = svc.generate_filename("MySample", "A")
        assert "MySample" in name.split("/")[1]

    def test_filename_contains_date(self, svc):
        name = svc.generate_filename("X", "B")
        today = datetime.now().strftime("%Y_%m_%d")
        assert today in name

    def test_index_increments(self, svc):
        n1 = svc.generate_filename("X", "A")
        n2 = svc.generate_filename("X", "A")
        idx1 = int(n1.split("/")[1].split("-")[1])
        idx2 = int(n2.split("/")[1].split("-")[1])
        assert idx2 == idx1 + 1

    def test_suffix_added_with_dash(self, svc):
        name = svc.generate_filename("X", "A", suffix="run1")
        assert "-run1" in name

    def test_suffix_with_leading_dash_not_doubled(self, svc):
        name = svc.generate_filename("X", "A", suffix="-run1")
        assert "--run1" not in name

    def test_subterm_appears_in_folder(self, svc):
        name = svc.generate_filename("X", "A", subterm="Polariser test")
        folder = name.split("/")[0]
        assert "Polariser" in folder or "Polariser_test" in folder

    def test_extension_applied(self, svc):
        name = svc.generate_filename("X", "A", extension=".tsv")
        assert name.endswith(".tsv")

    def test_empty_identifier_raises(self, svc):
        with pytest.raises(ValueError):
            svc.generate_filename("", "A")

    def test_empty_group_raises(self, svc):
        with pytest.raises(ValueError):
            svc.generate_filename("X", "")


# ── Metadata creation ─────────────────────────────────────────────────────────


class TestCreateMetadata:
    def test_dublin_core_fields_present(self, svc, start_end):
        t0, t1 = start_end
        m = svc.create_metadata(t0, t1, "A", "SampleX")
        assert "dc:date" in m
        assert "dc:creator" in m
        assert "dc:title" in m

    def test_date_matches_start(self, svc, start_end):
        t0, t1 = start_end
        m = svc.create_metadata(t0, t1, "A", "SampleX")
        assert m["dc:date"] == "2025-06-01"

    def test_identifier_recorded(self, svc, start_end):
        t0, t1 = start_end
        m = svc.create_metadata(t0, t1, "A", "SampleX")
        assert m["identifier"] == "SampleX"
        assert m["dc:title"] == "SampleX"

    def test_times_iso_format(self, svc, start_end):
        t0, t1 = start_end
        m = svc.create_metadata(t0, t1, "A", "SampleX")
        assert m["start_time"] == t0.isoformat()
        assert m["end_time"] == t1.isoformat()

    def test_subgroup_recorded(self, svc, start_end):
        t0, t1 = start_end
        m = svc.create_metadata(t0, t1, "A", "SampleX", subterm="Phase2")
        assert m["subgroup"] == "Phase2"

    def test_subgroup_empty_when_omitted(self, svc, start_end):
        t0, t1 = start_end
        m = svc.create_metadata(t0, t1, "A", "SampleX")
        assert m["subgroup"] == ""

    def test_extra_fields_merged(self, svc, start_end):
        t0, t1 = start_end
        m = svc.create_metadata(t0, t1, "A", "X", extra_fields={"firmware": "2.0.0"})
        assert m["firmware"] == "2.0.0"

    def test_group_letter_expanded_to_name(self, svc, start_end):
        t0, t1 = start_end
        m = svc.create_metadata(t0, t1, "B", "X")
        assert "B" in m["dc:creator"]

    def test_sensor_descriptions_present(self, svc, start_end):
        t0, t1 = start_end
        m = svc.create_metadata(t0, t1, "A", "SampleX")
        assert "sensors" in m

    def test_all_four_sensors_documented(self, svc, start_end):
        t0, t1 = start_end
        m = svc.create_metadata(t0, t1, "A", "SampleX")
        sensors = m["sensors"]
        assert "encoder_sample" in sensors
        assert "encoder_detector" in sensors
        assert "adc_intensity" in sensors
        assert "pdtia_gain" in sensors

    def test_sensor_entries_have_required_fields(self, svc, start_end):
        t0, t1 = start_end
        m = svc.create_metadata(t0, t1, "A", "SampleX")
        for key, entry in m["sensors"].items():
            assert "type" in entry, f"sensor '{key}' missing 'type'"
            assert "description" in entry, f"sensor '{key}' missing 'description'"
            assert len(entry["description"]) > 20, (
                f"sensor '{key}' description too short: {entry['description']!r}"
            )

    def test_encoder_sample_resolution_14_bit(self, svc, start_end):
        t0, t1 = start_end
        m = svc.create_metadata(t0, t1, "A", "X")
        assert m["sensors"]["encoder_sample"]["resolution_bits"] == 14

    def test_encoder_detector_resolution_14_bit(self, svc, start_end):
        t0, t1 = start_end
        m = svc.create_metadata(t0, t1, "A", "X")
        assert m["sensors"]["encoder_detector"]["resolution_bits"] == 14

    def test_adc_resolution_24_bit(self, svc, start_end):
        t0, t1 = start_end
        m = svc.create_metadata(t0, t1, "A", "X")
        assert m["sensors"]["adc_intensity"]["resolution_bits"] == 24


# ── save_measurement ──────────────────────────────────────────────────────────


class TestSaveMeasurement:
    def test_csv_file_created(self, svc, sample_data, start_end, tmp_path):
        t0, t1 = start_end
        meta = svc.create_metadata(t0, t1, "A", "Test")
        path = svc.save_measurement("run_001.csv", sample_data, meta)
        assert path.exists()

    def test_csv_rows_match_input(self, svc, sample_data, start_end, tmp_path):
        t0, t1 = start_end
        meta = svc.create_metadata(t0, t1, "A", "Test")
        path = svc.save_measurement("run_001.csv", sample_data, meta)
        with open(path, newline="") as f:
            rows = list(csv.reader(f))
        assert rows == sample_data

    def test_metadata_json_created_alongside(self, svc, sample_data, start_end):
        t0, t1 = start_end
        meta = svc.create_metadata(t0, t1, "A", "Test")
        path = svc.save_measurement("run_001.csv", sample_data, meta)
        meta_path = path.parent / (path.stem + "_metadata.json")
        assert meta_path.exists()

    def test_metadata_json_valid(self, svc, sample_data, start_end):
        t0, t1 = start_end
        meta = svc.create_metadata(t0, t1, "A", "Test")
        path = svc.save_measurement("run_001.csv", sample_data, meta)
        meta_path = path.parent / (path.stem + "_metadata.json")
        with open(meta_path) as f:
            loaded = json.load(f)
        assert loaded["identifier"] == "Test"

    def test_metadata_json_contains_sensors(self, svc, sample_data, start_end):
        t0, t1 = start_end
        meta = svc.create_metadata(t0, t1, "A", "Test")
        path = svc.save_measurement("run_001.csv", sample_data, meta)
        meta_path = path.parent / (path.stem + "_metadata.json")
        loaded = json.load(open(meta_path))
        assert "sensors" in loaded
        assert "encoder_sample" in loaded["sensors"]
        assert "adc_intensity" in loaded["sensors"]

    def test_relative_path_resolves_to_base_dir(self, svc, sample_data, start_end):
        t0, t1 = start_end
        meta = svc.create_metadata(t0, t1, "A", "Test")
        path = svc.save_measurement("subdir/run_001.csv", sample_data, meta)
        assert path.parent == svc.base_dir / "subdir"

    def test_absolute_path_used_directly(self, svc, sample_data, start_end, tmp_path):
        t0, t1 = start_end
        meta = svc.create_metadata(t0, t1, "A", "Test")
        abs_path = tmp_path / "absolute_run.csv"
        path = svc.save_measurement(str(abs_path), sample_data, meta)
        assert path == abs_path

    def test_marks_as_saved(self, svc, sample_data, start_end):
        svc.mark_unsaved()
        t0, t1 = start_end
        meta = svc.create_metadata(t0, t1, "A", "Test")
        svc.save_measurement("run.csv", sample_data, meta)
        assert not svc.has_unsaved()

    def test_unwritable_path_raises_ioerror(
        self, svc, sample_data, start_end, tmp_path
    ):
        t0, t1 = start_end
        meta = svc.create_metadata(t0, t1, "A", "Test")
        # make base_dir read-only
        locked_dir = tmp_path / "locked"
        locked_dir.mkdir()
        locked_dir.chmod(stat.S_IRUSR | stat.S_IXUSR)
        try:
            with pytest.raises(IOError):
                svc.save_measurement(str(locked_dir / "data.csv"), sample_data, meta)
        finally:
            locked_dir.chmod(stat.S_IRWXU)

    def test_parent_dirs_created_automatically(self, svc, sample_data, start_end):
        t0, t1 = start_end
        meta = svc.create_metadata(t0, t1, "A", "Test")
        path = svc.save_measurement("a/b/c/run.csv", sample_data, meta)
        assert path.exists()


# ── auto_save ─────────────────────────────────────────────────────────────────


class TestAutoSave:
    def test_returns_path_on_success(self, svc, sample_data, start_end):
        t0, t1 = start_end
        result = svc.auto_save("MySample", "A", sample_data, t0, t1)
        assert result is not None
        assert result.exists()

    def test_returns_none_on_empty_data(self, svc, start_end):
        t0, t1 = start_end
        result = svc.auto_save("X", "A", [], t0, t1)
        assert result is None

    def test_csv_content_correct(self, svc, sample_data, start_end):
        t0, t1 = start_end
        path = svc.auto_save("MySample", "A", sample_data, t0, t1)
        with open(path, newline="") as f:
            rows = list(csv.reader(f))
        assert rows == sample_data

    def test_metadata_json_written(self, svc, sample_data, start_end):
        t0, t1 = start_end
        path = svc.auto_save("MySample", "A", sample_data, t0, t1)
        meta_path = path.parent / (path.stem + "_metadata.json")
        assert meta_path.exists()
        loaded = json.load(open(meta_path))
        assert "sensors" in loaded

    def test_subterm_passed_through(self, svc, sample_data, start_end):
        t0, t1 = start_end
        path = svc.auto_save("MySample", "A", sample_data, t0, t1, subterm="Phase2")
        assert path is not None
        # folder name should contain sanitized subterm
        assert "Phase2" in str(path.parent)


# ── auto_backup ───────────────────────────────────────────────────────────────


class TestAutoBackup:
    def test_backup_file_created(self, svc, sample_data, start_end):
        t0, _ = start_end
        result = svc.auto_backup(sample_data, t0, identifier="Test", group_letter="A")
        assert result is not None
        assert result.exists()

    def test_backup_stored_in_dot_backup_subdir(self, svc, sample_data, start_end):
        t0, _ = start_end
        result = svc.auto_backup(sample_data, t0, identifier="Test", group_letter="A")
        assert result.parent == svc.base_dir / ".backup"

    def test_backup_metadata_json_created(self, svc, sample_data, start_end):
        t0, _ = start_end
        result = svc.auto_backup(sample_data, t0)
        meta = result.parent / (result.stem + "_metadata.json")
        assert meta.exists()

    def test_backup_metadata_contains_sensors(self, svc, sample_data, start_end):
        t0, _ = start_end
        result = svc.auto_backup(sample_data, t0)
        meta = result.parent / (result.stem + "_metadata.json")
        loaded = json.load(open(meta))
        assert "sensors" in loaded

    def test_backup_csv_content_correct(self, svc, sample_data, start_end):
        t0, _ = start_end
        result = svc.auto_backup(sample_data, t0)
        with open(result, newline="") as f:
            rows = list(csv.reader(f))
        assert rows == sample_data

    def test_backup_counter_increments(self, svc, sample_data, start_end):
        t0, _ = start_end
        p1 = svc.auto_backup(sample_data, t0)
        p2 = svc.auto_backup(sample_data, t0)
        assert p1 != p2

    def test_returns_none_for_header_only_data(self, svc, start_end):
        t0, _ = start_end
        header_only = [["ts_ms", "sample_angle", "detector_angle", "intensity"]]
        result = svc.auto_backup(header_only, t0)
        assert result is None

    def test_returns_none_for_empty_data(self, svc, start_end):
        t0, _ = start_end
        result = svc.auto_backup([], t0)
        assert result is None

    def test_extra_metadata_stored(self, svc, sample_data, start_end):
        t0, _ = start_end
        result = svc.auto_backup(sample_data, t0, extra_metadata={"firmware": "2.0.0"})
        meta = result.parent / (result.stem + "_metadata.json")
        loaded = json.load(open(meta))
        assert loaded["firmware"] == "2.0.0"


# ── Recovery from .backup after simulated crash ────────────────────────────────


class TestCrashRecovery:
    """
    Simulates the program exiting mid-session.  The auto_backup files in
    .backup/ must remain readable and contain all data written before the exit.
    """

    def test_backup_readable_after_service_destroyed(self, tmp_path, sample_data):
        t0 = datetime(2025, 6, 1, 9, 0, 0)
        svc = MeasurementSaveService(base_dir=tmp_path, tk_designation="TK01")
        path = svc.auto_backup(sample_data, t0, identifier="Crash", group_letter="A")
        assert path is not None

        # Simulate process exit — dereference the service
        del svc

        # The file must still exist and be valid CSV
        assert path.exists()
        with open(path, newline="") as f:
            rows = list(csv.reader(f))
        assert rows == sample_data

    def test_backup_metadata_readable_after_crash(self, tmp_path, sample_data):
        t0 = datetime(2025, 6, 1, 9, 0, 0)
        svc = MeasurementSaveService(base_dir=tmp_path, tk_designation="TK01")
        path = svc.auto_backup(sample_data, t0)
        meta_path = path.parent / (path.stem + "_metadata.json")
        del svc

        assert meta_path.exists()
        loaded = json.load(open(meta_path))
        assert "sensors" in loaded
        assert "encoder_sample" in loaded["sensors"]

    def test_multiple_backups_all_survive(self, tmp_path, sample_data):
        t0 = datetime(2025, 6, 1, 9, 0, 0)
        svc = MeasurementSaveService(base_dir=tmp_path, tk_designation="TK01")
        paths = [svc.auto_backup(sample_data, t0) for _ in range(3)]
        del svc
        for p in paths:
            assert p is not None
            assert p.exists()


# ── Backup cleanup ────────────────────────────────────────────────────────────


class TestBackupCleanup:
    def test_old_backups_removed(self, tmp_path):
        backup_dir = tmp_path / ".backup"
        backup_dir.mkdir()

        # Create a stale backup (mtime 25 h in the past)
        old_csv = backup_dir / "backup_20250601_000000_001.csv"
        old_meta = backup_dir / "backup_20250601_000000_001_metadata.json"
        old_csv.write_text("ts_ms\n1000\n")
        old_meta.write_text("{}")
        old_ts = time.time() - 25 * 3600
        import os

        os.utime(old_csv, (old_ts, old_ts))

        svc = MeasurementSaveService(base_dir=tmp_path)
        svc.cleanup_old_backups(backup_dir, max_age_hours=24)

        assert not old_csv.exists()
        assert not old_meta.exists()

    def test_recent_backups_preserved(self, tmp_path):
        backup_dir = tmp_path / ".backup"
        backup_dir.mkdir()

        recent_csv = backup_dir / "backup_20250601_120000_001.csv"
        recent_csv.write_text("ts_ms\n1000\n")

        svc = MeasurementSaveService(base_dir=tmp_path)
        svc.cleanup_old_backups(backup_dir, max_age_hours=24)

        assert recent_csv.exists()


# ── save_calibration_run ──────────────────────────────────────────────────────


class TestSaveCalibrationRun:
    def _make_data(self):
        return [
            ["ts_ms", "sample_angle", "detector_angle"],
            ["0", "0.0000", "0.0000"],
            ["100", "1.0000", "2.0000"],
        ]

    def test_file_created(self, svc, tmp_path):
        out = tmp_path / "cal_run.csv"
        result = svc.save_calibration_run(
            out, self._make_data(), firmware_version="2.0.0"
        )
        assert result == out
        assert out.exists()

    def test_firmware_version_in_header(self, svc, tmp_path):
        out = tmp_path / "cal_run.csv"
        svc.save_calibration_run(out, self._make_data(), firmware_version="2.0.0")
        content = out.read_text()
        assert "# firmware_version: 2.0.0" in content

    def test_saved_ts_in_header(self, svc, tmp_path):
        out = tmp_path / "cal_run.csv"
        svc.save_calibration_run(out, self._make_data())
        content = out.read_text()
        assert "# saved_ts:" in content

    def test_config_snapshot_entries_in_header(self, svc, tmp_path):
        out = tmp_path / "cal_run.csv"
        svc.save_calibration_run(
            out, self._make_data(), config_snapshot={"adc_gain": 8, "rate": "20SPS"}
        )
        content = out.read_text()
        assert "# config_adc_gain: 8" in content
        assert "# config_rate: 20SPS" in content

    def test_data_rows_written_after_header(self, svc, tmp_path):
        data = self._make_data()
        out = tmp_path / "cal_run.csv"
        svc.save_calibration_run(out, data)
        rows = [
            r
            for r in out.read_text().splitlines()
            if not r.startswith("#") and r.strip()
        ]
        assert rows[0] == ",".join(data[0])  # column header row
        assert rows[1] == ",".join(data[1])

    def test_empty_config_snapshot_ok(self, svc, tmp_path):
        out = tmp_path / "cal_run.csv"
        result = svc.save_calibration_run(out, self._make_data())
        assert result.exists()

    def test_parent_dirs_created(self, svc, tmp_path):
        out = tmp_path / "nested" / "cal_run.csv"
        svc.save_calibration_run(out, self._make_data())
        assert out.exists()

    def test_unwritable_raises_ioerror(self, svc, tmp_path):
        locked = tmp_path / "locked"
        locked.mkdir()
        locked.chmod(stat.S_IRUSR | stat.S_IXUSR)
        try:
            with pytest.raises(IOError):
                svc.save_calibration_run(locked / "cal.csv", self._make_data())
        finally:
            locked.chmod(stat.S_IRWXU)


# ── SENSOR_DESCRIPTIONS module constant ───────────────────────────────────────


class TestSensorDescriptionsConstant:
    """The module-level constant must fully describe all four hardware sensors."""

    def test_all_sensors_present(self):
        assert "encoder_sample" in SENSOR_DESCRIPTIONS
        assert "encoder_detector" in SENSOR_DESCRIPTIONS
        assert "adc_intensity" in SENSOR_DESCRIPTIONS
        assert "pdtia_gain" in SENSOR_DESCRIPTIONS

    def test_encoder_sample_is_as5048a(self):
        assert SENSOR_DESCRIPTIONS["encoder_sample"]["type"] == "AS5048A"

    def test_encoder_detector_is_as5048a(self):
        assert SENSOR_DESCRIPTIONS["encoder_detector"]["type"] == "AS5048A"

    def test_adc_is_ads1220(self):
        assert "ADS1220" in SENSOR_DESCRIPTIONS["adc_intensity"]["type"]

    def test_every_sensor_has_description(self):
        for key, entry in SENSOR_DESCRIPTIONS.items():
            assert "description" in entry, f"{key} missing description"
            assert len(entry["description"]) >= 50, f"{key} description too short"

    def test_encoder_channels_differ(self):
        assert SENSOR_DESCRIPTIONS["encoder_sample"]["channel"] == "A"
        assert SENSOR_DESCRIPTIONS["encoder_detector"]["channel"] == "B"

    def test_encoders_spi_interface(self):
        for key in ("encoder_sample", "encoder_detector"):
            assert "SPI" in SENSOR_DESCRIPTIONS[key]["interface"]

    def test_adc_24_bit(self):
        assert SENSOR_DESCRIPTIONS["adc_intensity"]["resolution_bits"] == 24
