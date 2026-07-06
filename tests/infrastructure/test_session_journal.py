"""Tests for SessionJournal — append-only crash-safe autosave.

Run with: .venv/bin/pytest tests/infrastructure/test_session_journal.py
"""

import csv
import os

import pytest

from polarisation_ui.core.models import Frame
from polarisation_ui.infrastructure.session_journal import (
    SessionJournal,
)


@pytest.fixture
def tmp_journal_base(tmp_path, monkeypatch):
    """Redirect JOURNAL_BASE to a temp directory so tests don't touch ~/.polarisation-ui."""
    import polarisation_ui.infrastructure.session_journal as sj_mod

    monkeypatch.setattr(sj_mod, "JOURNAL_BASE", tmp_path / "sessions")
    return tmp_path / "sessions"


def _make_frame(
    ts_ms: int = 1000, sa: float = 10.0, da: float = 20.0, inten: float = 500.0
) -> Frame:
    return Frame(ts_ms=ts_ms, sample_angle=sa, detector_angle=da, intensity=inten)


# ── Creation and basic I/O ────────────────────────────────────────────────────


class TestJournalBasics:
    def test_start_creates_file(self, tmp_journal_base):
        j = SessionJournal(firmware_version="2.0.0")
        j.start()
        assert j.journal_path.exists()
        j.close()

    def test_is_active_after_start(self, tmp_journal_base):
        j = SessionJournal()
        j.start()
        assert j.is_active
        j.close()

    def test_is_inactive_after_close(self, tmp_journal_base):
        j = SessionJournal()
        j.start()
        j.close()
        assert not j.is_active

    def test_row_count_increments(self, tmp_journal_base):
        j = SessionJournal()
        j.start()
        for i in range(5):
            j.append_frame(_make_frame(ts_ms=i))
        assert j.row_count == 5
        j.close()

    def test_firmware_version_in_header(self, tmp_journal_base):
        j = SessionJournal(firmware_version="2.0.0")
        j.start()
        j.close()
        content = j.journal_path.read_text()
        assert "firmware_version: 2.0.0" in content

    def test_config_snapshot_in_header(self, tmp_journal_base):
        j = SessionJournal(config_snapshot={"adc_gain": 8, "adc_vref": "EXT"})
        j.start()
        j.close()
        content = j.journal_path.read_text()
        assert "config_adc_gain: 8" in content
        assert "config_adc_vref: EXT" in content


# ── Data rows ─────────────────────────────────────────────────────────────────


class TestDataRows:
    def test_frame_values_written(self, tmp_journal_base):
        j = SessionJournal()
        j.start()
        j.append_frame(Frame(ts_ms=12345, sample_angle=45.0, detector_angle=90.0, intensity=800.0))
        j.close()

        rows = list(
            csv.reader(
                line for line in j.journal_path.read_text().splitlines() if not line.startswith("#")
            )
        )
        # rows[0] = header, rows[1] = data
        assert len(rows) == 2
        assert rows[1][0] == "12345"
        assert float(rows[1][1]) == pytest.approx(45.0, abs=1e-3)
        assert float(rows[1][2]) == pytest.approx(90.0, abs=1e-3)
        assert float(rows[1][3]) == pytest.approx(800.0, abs=1e-4)
        assert rows[1][4] == ""  # not a gap

    def test_gap_marker_written(self, tmp_journal_base):
        j = SessionJournal()
        j.start()
        j.append_frame(_make_frame())
        j.append_gap()
        j.append_frame(_make_frame())
        j.close()

        rows = list(
            csv.reader(
                line for line in j.journal_path.read_text().splitlines() if not line.startswith("#")
            )
        )
        data_rows = rows[1:]  # skip header
        gap_rows = [r for r in data_rows if len(r) >= 5 and r[4] == "1"]
        assert len(gap_rows) == 1

    def test_gap_marker_uses_wall_clock_not_monotonic(self, tmp_journal_base):
        """Regression test: append_gap() used to write time.monotonic()*1000
        into the same ts_ms column that append_frame() fills with the
        firmware's device-uptime clock.  monotonic()'s epoch is arbitrary
        (often since boot) so the two clock domains were not comparable.
        The fixed version uses wall-clock ms, which must land within a wide
        tolerance of time.time()*1000 sampled around the call.
        """
        import time

        j = SessionJournal()
        j.start()
        before_ms = time.time() * 1000
        j.append_gap()
        after_ms = time.time() * 1000
        j.close()

        rows = list(
            csv.reader(
                line for line in j.journal_path.read_text().splitlines() if not line.startswith("#")
            )
        )
        gap_row = rows[1]  # header, then the single gap row
        gap_ts_ms = int(gap_row[0])
        assert before_ms - 1000 <= gap_ts_ms <= after_ms + 1000


# ── Finalized marker ──────────────────────────────────────────────────────────


class TestFinalization:
    def test_finalize_creates_marker(self, tmp_journal_base):
        j = SessionJournal()
        j.start()
        j.finalize()
        assert (j.session_dir / "finalized").exists()

    def test_close_does_not_create_marker(self, tmp_journal_base):
        j = SessionJournal()
        j.start()
        j.close()
        assert not (j.session_dir / "finalized").exists()


# ── Export ────────────────────────────────────────────────────────────────────


class TestExport:
    def test_export_excludes_gaps(self, tmp_journal_base, tmp_path):
        j = SessionJournal()
        j.start()
        j.append_frame(_make_frame(ts_ms=1))
        j.append_gap()
        j.append_frame(_make_frame(ts_ms=2))
        j.close()

        out = tmp_path / "out.csv"
        rows = j.export_to_csv(out, finalize=False)
        assert rows == 2

        with open(out, newline="") as f:
            exported = list(csv.reader(f))
        assert exported[0] == ["ts_ms", "sample_angle", "detector_angle", "intensity"]
        assert len(exported) == 3  # header + 2 data rows

    def test_export_finalize_flag(self, tmp_journal_base, tmp_path):
        j = SessionJournal()
        j.start()
        j.append_frame(_make_frame())
        j.close()

        out = tmp_path / "out.csv"
        j.export_to_csv(out, finalize=True)
        assert (j.session_dir / "finalized").exists()

    def test_export_no_finalize(self, tmp_journal_base, tmp_path):
        j = SessionJournal()
        j.start()
        j.append_frame(_make_frame())
        j.close()

        out = tmp_path / "out.csv"
        j.export_to_csv(out, finalize=False)
        assert not (j.session_dir / "finalized").exists()

    def test_export_while_still_active_closes_write_handle_first(self, tmp_journal_base, tmp_path):
        """Regression test: export_to_csv() used to open a second read handle
        via _copy_data_rows() while the write handle was still open, risking
        a sharing violation on Windows.  Calling export without a prior
        close() must still succeed and must leave the journal inactive
        afterwards (proving the write handle was closed before the read pass).
        """
        j = SessionJournal()
        j.start()
        j.append_frame(_make_frame(ts_ms=1))
        j.append_frame(_make_frame(ts_ms=2))
        assert j.is_active

        out = tmp_path / "out.csv"
        rows = j.export_to_csv(out, finalize=False)

        assert rows == 2
        assert not j.is_active


# ── Orphan detection ──────────────────────────────────────────────────────────


class TestOrphanDetection:
    def test_no_orphans_initially(self, tmp_journal_base):
        assert SessionJournal.find_orphans() == []

    def test_closed_journal_is_orphan(self, tmp_journal_base):
        j = SessionJournal()
        j.start()
        j.append_frame(_make_frame())
        j.close()
        orphans = SessionJournal.find_orphans()
        assert len(orphans) == 1
        assert orphans[0] == j.session_dir

    def test_finalized_journal_not_orphan(self, tmp_journal_base):
        j = SessionJournal()
        j.start()
        j.append_frame(_make_frame())
        j.finalize()
        assert SessionJournal.find_orphans() == []

    def test_multiple_orphans(self, tmp_journal_base):
        for _ in range(3):
            j = SessionJournal()
            j.start()
            j.append_frame(_make_frame())
            j.close()
        assert len(SessionJournal.find_orphans()) == 3

    def test_export_orphan_finalizes(self, tmp_journal_base, tmp_path):
        j = SessionJournal()
        j.start()
        j.append_frame(_make_frame(ts_ms=42))
        j.close()

        out = tmp_path / "recovered.csv"
        rows = SessionJournal.export_orphan(j.session_dir, out)
        assert rows == 1
        assert (j.session_dir / "finalized").exists()
        assert out.exists()


# ── Crash simulation ──────────────────────────────────────────────────────────


class TestCrashResilience:
    def test_data_survives_simulated_crash(self, tmp_journal_base, tmp_path):
        """Simulate kill -9: write frames, flush, then close the fd without finalize."""
        j = SessionJournal()
        j.start()
        for i in range(10):
            j.append_frame(_make_frame(ts_ms=i))
        # Manually flush + fsync without calling finalize
        j._file.flush()
        os.fsync(j._file.fileno())
        j._file.close()
        j._file = None
        j._writer = None

        # Journal should be an orphan
        orphans = SessionJournal.find_orphans()
        assert len(orphans) == 1

        # Export recovers all 10 rows
        out = tmp_path / "crash_recovery.csv"
        rows = SessionJournal.export_orphan(orphans[0], out)
        assert rows == 10
