"""Tests for infrastructure.serial_device.SerialDevice against a raw PTY pair.

Unlike the MockArduino-based tests (which exercise the SCPI command layer),
these drive SerialDevice directly against a bare PTY so send_command()/
read_value()/flush_input_buffer() are tested in isolation from any protocol.
"""

import os
import pty
import select
import sys
import threading
import time
import tty

import pytest

from polarisation_ui.infrastructure.serial_device import SerialDevice

pytestmark = pytest.mark.skipif(sys.platform == "win32", reason="PTY not available on Windows")


class _MasterReader:
    """Continuously drains the PTY master side in a background thread.

    SerialDevice.send_command() calls pyserial's flush(), which calls
    termios.tcdrain() — on macOS this blocks until the bytes are actually
    read from the master side, not just written into the kernel buffer.
    Without an active reader, send_command() hangs forever. MockArduino
    avoids this the same way: a background thread continuously reading
    the master fd via select()+os.read().
    """

    def __init__(self, master_fd: int) -> None:
        self._fd = master_fd
        self._buffer = bytearray()
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                r, _, _ = select.select([self._fd], [], [], 0.05)
            except (OSError, ValueError):
                return
            if not r:
                continue
            try:
                chunk = os.read(self._fd, 4096)
            except OSError:
                return
            if not chunk:
                return
            with self._lock:
                self._buffer.extend(chunk)

    def wait_for_bytes(self, min_len: int, timeout: float = 2.0) -> bytes:
        """Block until at least *min_len* bytes have been drained, then return them."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            with self._lock:
                if len(self._buffer) >= min_len:
                    data = bytes(self._buffer)
                    self._buffer.clear()
                    return data
            time.sleep(0.01)
        with self._lock:
            data = bytes(self._buffer)
            self._buffer.clear()
        return data

    def stop(self) -> None:
        self._stop.set()
        self._thread.join(timeout=1.0)


@pytest.fixture
def pty_pair():
    master_fd, slave_fd = pty.openpty()
    # Without this, the pty stays in canonical (cooked) mode, where the line
    # discipline buffers/processes data (echo, newline translation) instead of
    # passing bytes straight through.
    tty.setraw(master_fd)
    slave_path = os.ttyname(slave_fd)
    reader = _MasterReader(master_fd)
    yield master_fd, slave_path, reader
    reader.stop()
    try:
        os.close(master_fd)
    except OSError:
        pass


@pytest.fixture
def device(pty_pair):
    _master_fd, slave_path, _reader = pty_pair
    dev = SerialDevice(port=slave_path, timeout=0.5)
    assert dev.reconnect()
    yield dev
    dev.close()


class TestReconnect:
    def test_reconnect_succeeds_and_sets_connected(self, pty_pair):
        _master_fd, slave_path, _reader = pty_pair
        dev = SerialDevice(port=slave_path, timeout=0.5)
        assert dev.reconnect() is True
        assert dev.connected is True
        dev.close()

    def test_reconnect_on_bad_port_raises(self):
        dev = SerialDevice(port="/dev/ttys_does_not_exist_9999", timeout=0.5)
        with pytest.raises(Exception):  # noqa: B017 - serial.SerialException subclass
            dev.reconnect()
        assert dev.connected is False


class TestClose:
    def test_close_marks_disconnected(self, device):
        device.close()
        assert device.connected is False

    def test_close_is_safe_when_never_connected(self):
        dev = SerialDevice(port="/dev/nonexistent")
        dev.close()  # must not raise
        assert dev.connected is False


class TestSendCommand:
    def test_send_command_writes_bytes_to_peer(self, pty_pair, device):
        _master_fd, _slave_path, reader = pty_pair
        assert device.send_command("PING", add_newline=True)
        assert reader.wait_for_bytes(5) == b"PING\n"

    def test_send_command_does_not_duplicate_newline(self, pty_pair, device):
        _master_fd, _slave_path, reader = pty_pair
        assert device.send_command("PING\n", add_newline=True)
        assert reader.wait_for_bytes(5) == b"PING\n"

    def test_send_command_without_newline_flag(self, pty_pair, device):
        _master_fd, _slave_path, reader = pty_pair
        assert device.send_command("PING", add_newline=False)
        assert reader.wait_for_bytes(4) == b"PING"

    def test_send_command_fails_when_not_connected(self):
        dev = SerialDevice(port="/dev/nonexistent")
        assert dev.send_command("PING") is False


class TestReadValue:
    def test_read_value_returns_string(self, pty_pair, device):
        master_fd, _slave_path, _reader = pty_pair
        os.write(master_fd, b"42.5\n")
        value = device.read_value(timeout=1.0, return_type="str")
        assert value == "42.5"

    def test_read_value_strips_whitespace_by_default(self, pty_pair, device):
        master_fd, _slave_path, _reader = pty_pair
        os.write(master_fd, b"  42.5  \n")
        value = device.read_value(timeout=1.0, return_type="str")
        assert value == "42.5"

    def test_read_value_bytes_return_type(self, pty_pair, device):
        master_fd, _slave_path, _reader = pty_pair
        os.write(master_fd, b"raw\n")
        value = device.read_value(timeout=1.0, return_type="bytes")
        assert value == b"raw\n"

    def test_read_value_timeout_returns_none(self, device):
        value = device.read_value(timeout=0.05, return_type="str")
        assert value is None

    def test_read_value_when_not_connected_returns_none(self):
        dev = SerialDevice(port="/dev/nonexistent")
        assert dev.read_value(timeout=0.05) is None

    def test_read_value_treats_literal_invalid_as_none(self, pty_pair, device):
        master_fd, _slave_path, _reader = pty_pair
        os.write(master_fd, b"invalid\n")
        value = device.read_value(timeout=1.0, return_type="str")
        assert value is None


class TestFlushInputBuffer:
    def test_flush_discards_pending_data(self, pty_pair, device):
        master_fd, _slave_path, _reader = pty_pair
        os.write(master_fd, b"stale_data\n")
        time.sleep(0.05)  # let the bytes actually arrive at the slave side

        assert device.flush_input_buffer() is True

        os.write(master_fd, b"fresh\n")
        value = device.read_value(timeout=1.0, return_type="str")
        assert value == "fresh"

    def test_flush_when_not_connected_returns_false(self):
        dev = SerialDevice(port="/dev/nonexistent")
        assert dev.flush_input_buffer() is False
