"""Tests for DetectorCrossCheckWorker using mocks — no real hardware."""

import time

import pytest
from PySide6.QtCore import Qt

from polarisation_ui.core.detector_crosscheck import DetectorComparisonResult
from polarisation_ui.infrastructure.mocks.mock_kdc101_nd_stage import MockKDC101NDStage
from polarisation_ui.infrastructure.mocks.mock_pm400 import MockPM400

_DIRECT = Qt.ConnectionType.DirectConnection


class TestDetectorCrossCheckWorker:
    def setup_method(self):
        import sys

        from PySide6.QtWidgets import QApplication

        self._app = QApplication.instance() or QApplication(sys.argv)

    def test_identical_meters_pass(self):
        from polarisation_ui.infrastructure.qt_threads import DetectorCrossCheckWorker

        nd = MockKDC101NDStage()
        nd.connect("mock://nd-stage")
        # Both meters driven by the same ND mock -> identical readings.
        pm_a = MockPM400(nd_mock=nd)
        pm_a.connect("mock://pm400a")
        pm_b = MockPM400(nd_mock=nd)
        pm_b.connect("mock://pm400b")

        points: list[tuple] = []
        results: list[DetectorComparisonResult] = []
        failures: list[str] = []

        # Stay well above the mock's noise floor (pos_dark_mm=50 would put the
        # signal within ~1x the noise amplitude, where two independently
        # noisy meters legitimately disagree by more than typical tolerances).
        worker = DetectorCrossCheckWorker(
            nd=nd,
            pm_a=pm_a,
            pm_b=pm_b,
            pos_clear_mm=0.0,
            pos_dark_mm=20.0,
            n_points=9,
            settle_s=0.0,
            tolerance_pct=10.0,
        )
        worker.point_recorded.connect(lambda *a: points.append(a), _DIRECT)
        worker.finished.connect(lambda r: results.append(r), _DIRECT)
        worker.failed.connect(lambda m: failures.append(m), _DIRECT)
        worker.start()
        worker.wait(10_000)

        assert not failures, f"Worker failed: {failures}"
        assert len(points) == 9
        assert len(results) == 1
        result = results[0]
        # Independent Gaussian noise on each mock keeps this near, not exactly, 1.0.
        assert result.mean_ratio == pytest.approx(1.0, abs=0.05)
        assert result.passed is True

    def test_abort_stops_worker_cleanly(self):
        from polarisation_ui.infrastructure.qt_threads import DetectorCrossCheckWorker

        nd = MockKDC101NDStage()
        nd.connect("mock://nd-stage")
        pm_a = MockPM400(nd_mock=nd)
        pm_a.connect("mock://pm400a")
        pm_b = MockPM400(nd_mock=nd)
        pm_b.connect("mock://pm400b")

        failures: list[str] = []
        worker = DetectorCrossCheckWorker(
            nd=nd,
            pm_a=pm_a,
            pm_b=pm_b,
            pos_clear_mm=0.0,
            pos_dark_mm=50.0,
            n_points=200,
            settle_s=0.02,
        )
        worker.failed.connect(lambda m: failures.append(m), _DIRECT)
        worker.start()
        time.sleep(0.2)
        worker.abort()
        worker.wait(10_000)

        assert len(failures) == 1
        assert "abgebroch" in failures[0].lower() or "abort" in failures[0].lower()
