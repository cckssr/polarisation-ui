"""Tests for infrastructure.qt_threads worker QThreads.

Uses qtbot.waitSignal to synchronise with each worker's background thread
instead of polling, since these are real QThread.start() runs (not run()
called directly), matching how MainWindow/tabs actually use them.
"""

from unittest.mock import MagicMock

from polarisation_ui.core.exceptions import KDC101Error
from polarisation_ui.infrastructure.qt_threads import (
    KDC101HomeWorker,
    MalusSweepWorker,
    ReconnectWorker,
)


class TestReconnectWorker:
    def test_emits_succeeded_on_success(self, qtbot):
        dm = MagicMock()
        dm.reconnect_encoders.return_value = True
        worker = ReconnectWorker(dm)

        with qtbot.waitSignal(worker.succeeded, timeout=2000, raising=True):
            worker.start()

        worker.wait(2000)

    def test_emits_failed_when_reconnect_returns_false(self, qtbot):
        dm = MagicMock()
        dm.reconnect_encoders.return_value = False
        worker = ReconnectWorker(dm)

        with qtbot.waitSignal(worker.failed, timeout=2000, raising=True):
            worker.start()

        worker.wait(2000)

    def test_emits_failed_on_exception(self, qtbot):
        dm = MagicMock()
        dm.reconnect_encoders.side_effect = RuntimeError("usb gone")
        worker = ReconnectWorker(dm)

        with qtbot.waitSignal(worker.failed, timeout=2000, raising=True):
            worker.start()

        worker.wait(2000)


class TestKDC101HomeWorker:
    def test_emits_done_on_success(self, qtbot):
        kdc = MagicMock()
        worker = KDC101HomeWorker(kdc)

        with qtbot.waitSignal(worker.done, timeout=2000, raising=True):
            worker.start()

        worker.wait(2000)
        kdc.home.assert_called_once()

    def test_emits_error_on_kdc101error(self, qtbot):
        kdc = MagicMock()
        kdc.home.side_effect = KDC101Error("stage jammed")
        worker = KDC101HomeWorker(kdc)

        with qtbot.waitSignal(worker.error, timeout=2000, raising=True) as blocker:
            worker.start()

        worker.wait(2000)
        assert "stage jammed" in blocker.args[0]


class TestMalusSweepWorker:
    def test_waveplate_mode_sweeps_and_emits_points(self, qtbot):
        """mode='waveplate' skips the auto-zero search (home == zero)."""
        kdc = MagicMock()
        kdc.get_position_deg.return_value = 0.0
        read_average = MagicMock(return_value=(0.5, None))

        worker = MalusSweepWorker(
            kdc=kdc,
            read_average=read_average,
            start_deg=0.0,
            end_deg=10.0,
            step_deg=5.0,
            mode="waveplate",
            settle_ms=1,
        )

        points = []
        worker.point_scanned.connect(lambda angle, pos, i: points.append((angle, pos, i)))

        with qtbot.waitSignal(worker.finished, timeout=5000, raising=True):
            worker.start()

        worker.wait(2000)
        kdc.home.assert_called_once()
        assert len(points) == 3  # 0, 5, 10 deg
        assert [p[0] for p in points] == [0.0, 5.0, 10.0]

    def test_abort_before_sweep_emits_failed(self, qtbot):
        kdc = MagicMock()
        read_average = MagicMock(return_value=(0.5, None))

        worker = MalusSweepWorker(
            kdc=kdc,
            read_average=read_average,
            start_deg=0.0,
            end_deg=10.0,
            step_deg=5.0,
            mode="waveplate",
            settle_ms=1,
        )
        worker.abort()

        with qtbot.waitSignal(worker.failed, timeout=2000, raising=True):
            worker.start()

        worker.wait(2000)
        read_average.assert_not_called()

    def test_malus_mode_runs_auto_zero_search(self, qtbot):
        """mode='malus' (default) runs the coarse+fine auto-zero search first."""
        kdc = MagicMock()
        kdc.get_position_deg.return_value = 0.0
        read_average = MagicMock(return_value=(0.5, None))

        worker = MalusSweepWorker(
            kdc=kdc,
            read_average=read_average,
            start_deg=0.0,
            end_deg=5.0,
            step_deg=5.0,
            mode="malus",
            settle_ms=1,
        )

        with qtbot.waitSignal(worker.finished, timeout=10000, raising=True):
            worker.start()

        worker.wait(2000)
        kdc.home.assert_called_once()
        # Coarse pass alone moves the stage 37 times (0..180 in 5 deg steps);
        # confirms the auto-zero search actually ran for mode="malus".
        assert kdc.move_to.call_count > 37
