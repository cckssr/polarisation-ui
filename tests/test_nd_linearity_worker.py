"""Tests for NDLinearityScanWorker using mocks — no real hardware."""

import sys

import pytest
from PySide6.QtCore import Qt

from polarisation_ui.core.nd_linearity import BACKWARD, FORWARD, NDLinearityScan
from polarisation_ui.infrastructure.mocks.mock_nd_stage import MockNDStage
from polarisation_ui.infrastructure.mocks.mock_pm400 import MockPM400

_DIRECT = Qt.ConnectionType.DirectConnection


def _make_devices():
    nd = MockNDStage()
    nd.connect("mock://nd-stage")
    pm = MockPM400(nd_mock=nd)
    pm.connect("mock://pm400")
    return nd, pm


class TestNDLinearityScanWorker:
    def setup_method(self):
        from PySide6.QtWidgets import QApplication

        self._app = QApplication.instance() or QApplication(sys.argv)

    def _run(self, **kwargs):
        from polarisation_ui.infrastructure.qt_threads import NDLinearityScanWorker

        nd, pm = _make_devices()
        scans: list[NDLinearityScan] = []
        finished: list[list[NDLinearityScan]] = []
        failures: list[str] = []
        points: list[tuple] = []
        worker = NDLinearityScanWorker(nd=nd, pm=pm, settle_s=0.0, **kwargs)
        worker.scan_finished.connect(scans.append, _DIRECT)
        worker.finished.connect(finished.append, _DIRECT)
        worker.failed.connect(failures.append, _DIRECT)
        worker.point_scanned.connect(lambda *a: points.append(a), _DIRECT)
        worker.start()
        worker.wait(10_000)
        return scans, finished, failures, points

    def test_alternating_scans_cover_the_same_grid_in_opposite_directions(self):
        scans, finished, failures, points = self._run(
            start_deg=0.0, end_deg=100.0, n_points=6, n_scans=3, alternate=True
        )
        assert not failures
        assert [s.direction for s in scans] == [FORWARD, BACKWARD, FORWARD]
        assert [s.index for s in scans] == [0, 1, 2]
        assert len(points) == 18
        fwd = [p for p, _ in scans[0].points]
        bwd = [p for p, _ in scans[1].points]
        assert bwd == pytest.approx(list(reversed(fwd)))
        assert len(finished) == 1 and finished[0] == scans

    def test_without_alternation_all_scans_run_forward(self):
        scans, _, failures, _ = self._run(
            start_deg=0.0, end_deg=100.0, n_points=4, n_scans=2, alternate=False
        )
        assert not failures
        assert {s.direction for s in scans} == {FORWARD}

    def test_first_index_continues_numbering(self):
        scans, _, _, _ = self._run(
            start_deg=0.0, end_deg=50.0, n_points=4, n_scans=2, first_index=5
        )
        assert [s.index for s in scans] == [5, 6]

    def test_negative_angles_can_be_scanned(self):
        scans, _, failures, _ = self._run(start_deg=-60.0, end_deg=0.0, n_points=4, n_scans=1)
        assert not failures
        assert [p for p, _ in scans[0].points][0] == pytest.approx(-60.0)

    def test_abort_keeps_completed_scans(self):
        from polarisation_ui.infrastructure.qt_threads import NDLinearityScanWorker

        nd, pm = _make_devices()
        scans: list[NDLinearityScan] = []
        failures: list[str] = []
        worker = NDLinearityScanWorker(
            nd=nd, pm=pm, start_deg=0.0, end_deg=100.0, n_points=4, settle_s=0.0, n_scans=3
        )
        # Abort as soon as the first scan has been delivered.
        worker.scan_finished.connect(scans.append, _DIRECT)
        worker.scan_finished.connect(lambda _s: worker.abort(), _DIRECT)
        worker.failed.connect(failures.append, _DIRECT)
        worker.start()
        worker.wait(10_000)
        assert len(scans) == 1
        assert failures == ["Abgebrochen"]
