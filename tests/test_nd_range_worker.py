"""Tests for NDRangeScanWorker using mocks — no real hardware."""

import time

import pytest
from PySide6.QtCore import Qt

from polarisation_ui.core.nd_filter import NDFilterRange
from polarisation_ui.infrastructure.mocks.mock_kdc101_nd_stage import MockKDC101NDStage
from polarisation_ui.infrastructure.mocks.mock_pm400 import MockPM400

_DIRECT = Qt.ConnectionType.DirectConnection


def _make_devices():
    nd = MockKDC101NDStage()
    nd.connect("mock://nd-stage")
    pm = MockPM400(nd_mock=nd)
    pm.connect("mock://pm400")
    return nd, pm


class TestNDRangeScanWorker:
    def setup_method(self):
        import sys

        from PySide6.QtWidgets import QApplication

        self._app = QApplication.instance() or QApplication(sys.argv)

    def test_full_scan_emits_expected_point_count_and_range(self):
        from polarisation_ui.infrastructure.qt_threads import NDRangeScanWorker

        nd, pm = _make_devices()

        points: list[tuple] = []
        results: list[NDFilterRange] = []
        failures: list[str] = []

        worker = NDRangeScanWorker(
            nd=nd, pm=pm, start_mm=0.0, end_mm=50.0, n_points=11, settle_s=0.0
        )
        worker.point_scanned.connect(lambda *a: points.append(a), _DIRECT)
        worker.finished.connect(lambda r: results.append(r), _DIRECT)
        worker.failed.connect(lambda m: failures.append(m), _DIRECT)
        worker.start()
        worker.wait(10_000)

        assert not failures, f"Worker failed: {failures}"
        assert len(points) == 11
        assert len(results) == 1

        result = results[0]
        assert isinstance(result, NDFilterRange)
        # MockPM400's ND model is monotonically decreasing with position.
        assert result.pos_clear_mm == pytest.approx(0.0, abs=1e-6)
        assert result.pos_dark_mm == pytest.approx(50.0, abs=1e-6)
        assert result.monotonic is True

    def test_abort_stops_worker_cleanly(self):
        from polarisation_ui.infrastructure.qt_threads import NDRangeScanWorker

        nd, pm = _make_devices()

        failures: list[str] = []
        worker = NDRangeScanWorker(
            nd=nd, pm=pm, start_mm=0.0, end_mm=50.0, n_points=200, settle_s=0.02
        )
        worker.failed.connect(lambda m: failures.append(m), _DIRECT)
        worker.start()
        time.sleep(0.2)
        worker.abort()
        worker.wait(10_000)

        assert len(failures) == 1
        assert "abgebroch" in failures[0].lower() or "abort" in failures[0].lower()
