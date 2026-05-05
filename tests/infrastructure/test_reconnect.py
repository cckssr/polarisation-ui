"""
Tests for DataController reconnect resilience.

Verifies exponential backoff, buffer preservation across reconnects,
gap markers in the session journal, and DesiredState reapplication.

Run with: .venv/bin/pytest tests/infrastructure/test_reconnect.py
"""

import time
from collections import deque
from unittest.mock import MagicMock, patch, call
from pathlib import Path

import pytest

from polarisation_ui.infrastructure.devices.dual_encoder import DesiredState
from polarisation_ui.infrastructure.session_journal import SessionJournal
from polarisation_ui.core.models import Frame

# ── Helpers ───────────────────────────────────────────────────────────────────


def _make_device_manager(
    connected: bool = True, reconnect_result: bool = True
) -> MagicMock:
    dm = MagicMock()
    dm.is_encoder_connected.return_value = connected
    dm.reconnect_encoders.return_value = reconnect_result
    dm.get_firmware_version.return_value = "2.0.0"
    dm.get_desired_state.return_value = DesiredState()
    return dm


# ── DesiredState ──────────────────────────────────────────────────────────────


class TestDesiredState:

    def test_default_state(self):
        s = DesiredState()
        assert s.adc_gain == 1
        assert s.adc_vref == "EXT"
        assert s.adc_temp is False
        assert s.pdtia_gain == 0

    def test_as_config_snapshot(self):
        s = DesiredState(adc_gain=8, pdtia_gain=2)
        snap = s.as_config_snapshot()
        assert snap["adc_gain"] == 8
        assert snap["pdtia_gain"] == 2

    def test_reapply_desired_state(self):
        from polarisation_ui.infrastructure.devices.dual_encoder import (
            DualEncoderArduino,
        )

        dev = MagicMock(spec=DualEncoderArduino)
        dev.adc = MagicMock()
        dev.adc.configure.return_value = True
        dev.adc.set_pdtia_gain.return_value = True

        state = DesiredState(adc_gain=4, pdtia_gain=1)
        # Call the actual method on the real class but with a mock device
        DualEncoderArduino.reapply_desired_state(dev, state)

        dev.adc.configure.assert_called_once_with(
            gain=4,
            mux="DIFF01",
            rate=20,
            mode="NORM",
            fir="OFF",
            vref="EXT",
            temp=False,
        )
        dev.adc.set_pdtia_gain.assert_called_once_with(1)

    def test_reapply_skips_pdtia_when_zero(self):
        from polarisation_ui.infrastructure.devices.dual_encoder import (
            DualEncoderArduino,
        )

        dev = MagicMock(spec=DualEncoderArduino)
        dev.adc = MagicMock()
        dev.adc.configure.return_value = True

        state = DesiredState(pdtia_gain=0)
        DualEncoderArduino.reapply_desired_state(dev, state)
        dev.adc.set_pdtia_gain.assert_not_called()


# ── DeviceManager reconnect with DesiredState ─────────────────────────────────


class TestDeviceManagerReconnect:

    def test_reconnect_calls_reapply(self, tmp_path):
        from polarisation_ui.infrastructure.device_manager import (
            GoniometerDeviceManager,
        )

        dm = GoniometerDeviceManager.__new__(GoniometerDeviceManager)
        dm.use_mock = False
        dm._encoder_device = None
        dm._encoder_status = MagicMock()
        dm._encoder_status.port = "/dev/fake"
        dm._encoder_status.baudrate = 115200
        dm._desired_state = DesiredState(adc_gain=8)

        mock_device = MagicMock()
        mock_device.adc = MagicMock()
        mock_device.adc.configure.return_value = True
        mock_device.firmware_version = "2.0.0"

        with (
            patch.object(dm, "disconnect_encoders"),
            patch.object(dm, "connect_encoders", return_value=True) as mock_connect,
        ):
            dm._encoder_device = mock_device
            result = dm.reconnect_encoders()

        assert result is True
        mock_device.reapply_desired_state.assert_called_once_with(dm._desired_state)


# ── Backoff delay computation ─────────────────────────────────────────────────


class TestBackoffDelays:

    def test_backoff_sequence(self):
        from polarisation_ui.infrastructure.config import import_config

        delays = (
            import_config()
            .get("connection", {})
            .get("backoff_delays_ms", [1000, 2000, 4000, 8000, 15000])
        )
        # Must be monotonically increasing up to the cap
        for i in range(len(delays) - 1):
            assert delays[i] <= delays[i + 1]
        # First delay must be 1 s
        assert delays[0] == 1000
        # Cap must be at most 15 s
        assert delays[-1] <= 15000

    def test_backoff_attempt_advances(self):
        """Each failed reconnect uses a longer delay."""
        from PySide6.QtWidgets import QApplication
        import sys

        app = QApplication.instance() or QApplication(sys.argv)

        dm = _make_device_manager(connected=True)
        dm.read_angles.return_value = None  # trigger errors

        from polarisation_ui.ui.controllers.data_controller import DataController

        dc = DataController(dm, use_mock_intensity=True)

        delays_used: list[int] = []
        original_start = dc._retry_timer.start

        def capture_start(delay):
            delays_used.append(delay)
            original_start(delay)

        dc._retry_timer.start = capture_start
        dc._retry_timer.stop()  # prevent actual timer from firing

        # Simulate 4 consecutive errors
        dc._error_count = 0
        dc._backoff_attempt = 0
        for _ in range(4):
            dc._handle_read_error("simulated error")
            dc._error_count -= 1  # prevent hitting max_errors

        assert delays_used[0] < delays_used[1] < delays_used[2]
        dc.cleanup()


# ── Buffer preservation ───────────────────────────────────────────────────────


class TestBufferPreservation:

    def test_buffers_preserved_after_reconnect(self):
        """Ring buffers must NOT be cleared when a reconnect succeeds."""
        from PySide6.QtWidgets import QApplication
        import sys

        app = QApplication.instance() or QApplication(sys.argv)

        dm = _make_device_manager(connected=True, reconnect_result=True)

        from polarisation_ui.ui.controllers.data_controller import DataController

        dc = DataController(dm, use_mock_intensity=True)

        # Pre-populate both buffers
        dc._sample_buffer.extend([10.0, 11.0, 12.0])
        dc._det_buffer.extend([20.0, 21.0, 22.0])

        sample_before = list(dc._sample_buffer)
        det_before = list(dc._det_buffer)

        # Simulate a successful reconnect (now runs on a QThread worker)
        dc._attempt_reconnect()
        if dc._reconnect_worker is not None:
            dc._reconnect_worker.wait()  # block until worker thread finishes
        app.processEvents()  # deliver the succeeded/failed signal to main thread

        assert list(dc._sample_buffer) == sample_before
        assert list(dc._det_buffer) == det_before
        dc.cleanup()


# ── Journal gap markers ───────────────────────────────────────────────────────


class TestJournalGapMarker:

    def test_gap_written_on_reconnect(self, tmp_path):
        """A gap row must appear in the journal after a successful reconnect."""
        from PySide6.QtWidgets import QApplication
        import sys

        app = QApplication.instance() or QApplication(sys.argv)

        import polarisation_ui.infrastructure.session_journal as sj_mod

        original_base = sj_mod.JOURNAL_BASE
        sj_mod.JOURNAL_BASE = tmp_path / "sessions"

        try:
            dm = _make_device_manager(connected=True, reconnect_result=True)

            from polarisation_ui.ui.controllers.data_controller import DataController

            dc = DataController(dm, use_mock_intensity=True)

            # Start a journal manually (simulating start_measurement)
            dc._is_measuring = True
            dc._start_journal()
            assert dc._journal is not None

            frame = Frame(
                ts_ms=100, sample_angle=10.0, detector_angle=20.0, intensity=500.0
            )
            dc._journal.append_frame(frame)

            # Simulate reconnect (runs on a QThread worker)
            dc._attempt_reconnect()
            if dc._reconnect_worker is not None:
                dc._reconnect_worker.wait()  # block until worker thread finishes
            app.processEvents()  # deliver the succeeded signal to main thread

            # Journal should have a gap row
            dc._journal.close()
            content = dc._journal.journal_path.read_text()
            lines = [l for l in content.splitlines() if not l.startswith("#")]
            # header + 1 data row + 1 gap row
            assert len(lines) >= 3
            # Last data line (gap) should have "1" in column 5
            import csv

            rows = list(csv.reader(lines[1:]))  # skip header
            gap_rows = [r for r in rows if len(r) >= 5 and r[4] == "1"]
            assert len(gap_rows) == 1
        finally:
            sj_mod.JOURNAL_BASE = original_base
            dc.cleanup()
