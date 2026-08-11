"""Tests for infrastructure.qt_threads worker QThreads.

Uses qtbot.waitSignal to synchronise with each worker's background thread
instead of polling, since these are real QThread.start() runs (not run()
called directly), matching how MainWindow/tabs actually use them.
"""

import time
from unittest.mock import MagicMock

from PySide6.QtCore import Qt

from polarisation_ui.core.exceptions import KDC101Error
from polarisation_ui.core.models import Frame
from polarisation_ui.infrastructure.qt_threads import (
    KDC101HomeWorker,
    KDCSweepWorker,
    KDCZeroFindWorker,
    ReconnectWorker,
)

# Cross-thread signals carrying Python objects (e.g. a Frame) must be connected
# with an explicit DirectConnection when the receiver is a bare callable rather
# than a QObject slot — AutoConnection's queued delivery to a callable with no
# Qt-tracked lifetime can outlive the test's local objects and crash on
# delivery. Same workaround already used in test_auto_power_calibration_worker.py.
_DIRECT = Qt.ConnectionType.DirectConnection


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


class TestKDCSweepWorker:
    def test_sweeps_and_emits_points(self, qtbot):
        kdc = MagicMock()
        kdc.is_homed.return_value = False
        kdc.get_position_deg.return_value = 0.0
        read_average = MagicMock(return_value=(0.5, None))

        worker = KDCSweepWorker(
            kdc=kdc,
            read_average=read_average,
            start_deg=0.0,
            end_deg=10.0,
            step_deg=5.0,
            settle_ms=1,
        )

        points = []
        worker.point_scanned.connect(
            lambda angle, pos, i, frame: points.append((angle, pos, i)), _DIRECT
        )

        with qtbot.waitSignal(worker.finished, timeout=5000, raising=True):
            worker.start()

        worker.wait(2000)
        kdc.home.assert_called_once()
        assert len(points) == 3  # 0, 5, 10 deg
        assert [p[0] for p in points] == [0.0, 5.0, 10.0]

    def test_skips_home_when_already_homed(self, qtbot):
        kdc = MagicMock()
        kdc.is_homed.return_value = True
        kdc.get_position_deg.return_value = 0.0
        read_average = MagicMock(return_value=(0.5, None))

        worker = KDCSweepWorker(
            kdc=kdc,
            read_average=read_average,
            start_deg=0.0,
            end_deg=10.0,
            step_deg=5.0,
            settle_ms=1,
        )

        with qtbot.waitSignal(worker.finished, timeout=5000, raising=True):
            worker.start()

        worker.wait(2000)
        kdc.home.assert_not_called()

    def test_uses_move_to_logical_so_offset_is_applied(self, qtbot):
        """Sweep steps must go through move_to_logical(), not raw move_to()."""
        kdc = MagicMock()
        kdc.is_homed.return_value = True
        kdc.get_position_deg.return_value = 0.0
        read_average = MagicMock(return_value=(0.5, None))

        worker = KDCSweepWorker(
            kdc=kdc,
            read_average=read_average,
            start_deg=0.0,
            end_deg=5.0,
            step_deg=5.0,
            settle_ms=1,
        )

        with qtbot.waitSignal(worker.finished, timeout=5000, raising=True):
            worker.start()

        worker.wait(2000)
        kdc.move_to_logical.assert_any_call(0.0)
        kdc.move_to_logical.assert_any_call(5.0)
        kdc.move_to.assert_not_called()

    def test_abort_before_sweep_emits_failed(self, qtbot):
        kdc = MagicMock()
        kdc.is_homed.return_value = True
        read_average = MagicMock(return_value=(0.5, None))

        worker = KDCSweepWorker(
            kdc=kdc,
            read_average=read_average,
            start_deg=0.0,
            end_deg=10.0,
            step_deg=5.0,
            settle_ms=1,
        )
        worker.abort()

        with qtbot.waitSignal(worker.failed, timeout=2000, raising=True):
            worker.start()

        worker.wait(2000)
        read_average.assert_not_called()

    def test_point_scanned_carries_frame_for_gain_and_power(self, qtbot):
        kdc = MagicMock()
        kdc.is_homed.return_value = True
        kdc.get_position_deg.return_value = 0.0
        frame = Frame(
            ts_ms=0,
            sample_angle=0.0,
            detector_angle=0.0,
            intensity=0.5,
            pdtia_gain=2,
            power_W=1.5e-6,
            conv_factor_W_per_V=3e-6,
        )
        read_average = MagicMock(return_value=(0.5, frame))

        worker = KDCSweepWorker(
            kdc=kdc,
            read_average=read_average,
            start_deg=0.0,
            end_deg=5.0,
            step_deg=10.0,  # step > range -> linear_angle_grid still yields exactly 2 points
            settle_ms=1,
        )

        points = []
        worker.point_scanned.connect(lambda angle, pos, i, fr: points.append(fr), _DIRECT)

        with qtbot.waitSignal(worker.finished, timeout=5000, raising=True):
            worker.start()

        worker.wait(2000)
        assert len(points) == 2
        assert points[0] is frame
        assert points[0].pdtia_gain == 2


class _FakeZeroFindKDC:
    """Simulates a KDC101 travelling at a constant rate for KDCZeroFindWorker tests.

    ``move_to(angle, wait=False)`` starts a time-based ramp so
    ``get_position_deg()`` reports a realistic in-flight position while the
    worker polls, letting the timestamp-correlation logic be exercised for
    real instead of jumping instantly to the target.
    """

    def __init__(self, homed: bool = True, rate_deg_per_s: float = 90.0) -> None:
        self.homed = homed
        self.home_called = 0
        self.stopped = False
        self._pos = 0.0
        self._rate = rate_deg_per_s
        self._ramp_start_pos: float | None = None
        self._ramp_target: float | None = None
        self._ramp_t0: float | None = None

    def is_homed(self) -> bool:
        return self.homed

    def home(self) -> None:
        self.home_called += 1
        self.homed = True
        self._pos = 0.0

    def move_to(self, angle: float, wait: bool = True) -> None:
        if wait:
            self._pos = angle
            self._ramp_t0 = None
        else:
            self._ramp_start_pos = self._pos
            self._ramp_target = angle
            self._ramp_t0 = time.monotonic()

    def get_position_deg(self) -> float:
        if self._ramp_t0 is None:
            return self._pos
        elapsed = time.monotonic() - self._ramp_t0
        direction = 1.0 if self._ramp_target >= self._ramp_start_pos else -1.0
        pos = self._ramp_start_pos + direction * self._rate * elapsed
        pos = max(pos, self._ramp_target) if direction < 0 else min(pos, self._ramp_target)
        self._pos = pos
        return pos

    def stop(self) -> None:
        self.stopped = True
        self._ramp_t0 = None


class _FrameSource:
    """Synthesises Frames whose intensity dips to a minimum at a known angle,
    tracking the gain KDCZeroFindWorker last requested via gain_requested."""

    def __init__(self, kdc: _FakeZeroFindKDC, minimum_angle: float) -> None:
        self._kdc = kdc
        self._minimum_angle = minimum_angle
        self.gain = 1

    def set_gain(self, stage: int) -> None:
        self.gain = stage

    def read_latest(self) -> Frame:
        angle = self._kdc.get_position_deg()
        intensity = 0.01 + 0.001 * abs(angle - self._minimum_angle)
        return Frame(
            ts_ms=int(time.monotonic() * 1000),
            sample_angle=0.0,
            detector_angle=0.0,
            intensity=intensity,
            pdtia_gain=self.gain,
        )


class TestKDCZeroFindWorker:
    def test_finds_minimum_and_cycles_gain(self, qtbot):
        kdc = _FakeZeroFindKDC(homed=True)
        source = _FrameSource(kdc, minimum_angle=60.0)

        worker = KDCZeroFindWorker(kdc=kdc, read_latest=source.read_latest)
        worker.gain_requested.connect(source.set_gain, _DIRECT)
        gains: list[int] = []
        worker.gain_requested.connect(gains.append, _DIRECT)

        with qtbot.waitSignal(worker.finished, timeout=15000, raising=True) as blocker:
            worker.start()

        worker.wait(2000)
        offset = blocker.args[0]
        assert abs(offset - 60.0) <= 1.0
        assert gains == [1, 3, 1]

    def test_skips_home_when_already_homed(self, qtbot):
        kdc = _FakeZeroFindKDC(homed=True)
        source = _FrameSource(kdc, minimum_angle=90.0)

        worker = KDCZeroFindWorker(kdc=kdc, read_latest=source.read_latest)
        worker.gain_requested.connect(source.set_gain, _DIRECT)

        with qtbot.waitSignal(worker.finished, timeout=15000, raising=True):
            worker.start()

        worker.wait(2000)
        assert kdc.home_called == 0

    def test_abort_emits_failed(self, qtbot):
        kdc = _FakeZeroFindKDC(homed=True)
        source = _FrameSource(kdc, minimum_angle=90.0)

        worker = KDCZeroFindWorker(kdc=kdc, read_latest=source.read_latest)
        worker.gain_requested.connect(source.set_gain, _DIRECT)
        worker.abort()

        with qtbot.waitSignal(worker.failed, timeout=2000, raising=True):
            worker.start()

        worker.wait(2000)
