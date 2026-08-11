"""Mock KDC101Polariser for headless tests."""


class MockKDC101Polariser:
    """Simulated KDC101Polariser.

    move_to() updates the internal position instantly; home() resets to 0°.
    No real hardware or pylablib needed.
    """

    def __init__(self) -> None:
        """Start disconnected at position 0°."""
        self._position_deg: float = 0.0
        self._connected: bool = False
        self._zero_offset_deg: float = 0.0
        self._homed: bool = False
        self.stop_called: int = 0

    def connect(self, conn_id: str) -> None:
        """Mark the mock as connected (conn_id is accepted but ignored)."""
        self._connected = True

    def disconnect(self) -> None:
        """Mark the mock as disconnected."""
        self._connected = False

    def is_connected(self) -> bool:
        """Return whether the mock is currently connected."""
        return self._connected

    def home(self, wait: bool = True, timeout: float = 120.0) -> None:
        """Reset the simulated position to 0° instantly (wait/timeout are ignored)."""
        self._require_connected()
        self._position_deg = 0.0
        self._homed = True

    def move_to(self, angle_deg: float, wait: bool = True, timeout: float = 60.0) -> None:
        """Set the simulated position instantly (wait/timeout are ignored)."""
        self._require_connected()
        self._position_deg = angle_deg

    def move_to_logical(self, angle_deg: float, wait: bool = True, timeout: float = 60.0) -> None:
        """Move to *angle_deg* relative to the current zero offset, like the real driver."""
        self.move_to((self._zero_offset_deg + angle_deg) % 360.0, wait=wait, timeout=timeout)

    def get_position_deg(self) -> float:
        """Return the current simulated position in degrees."""
        self._require_connected()
        return self._position_deg

    def is_homed(self) -> bool:
        """Return whether home() has been called since construction."""
        return self._homed

    def stop(self, immediate: bool = True) -> None:
        """No-op — the mock has no in-flight move to interrupt."""
        self.stop_called += 1

    @property
    def zero_offset_deg(self) -> float:
        """Host-side logical-zero offset in degrees (0.0 until set)."""
        return self._zero_offset_deg

    def set_zero_offset_deg(self, offset_deg: float) -> None:
        """Set the logical-zero offset, normalised to [0, 360)."""
        self._zero_offset_deg = offset_deg % 360.0

    def get_position_deg_nowait(self) -> float:
        """Mirror KDC101Polariser.get_position_deg_nowait().

        The mock has no lock contention to simulate, so it always succeeds
        like get_position_deg().
        """
        return self.get_position_deg()

    def enable(self, state: bool) -> None:
        """No-op — the mock has no motor-enable state to simulate."""
        self._require_connected()

    @staticmethod
    def list_devices() -> list[tuple[str, str]]:
        """Return a single fixed fake device (connection id, description) pair."""
        return [("mock://kdc101", "Mock KDC101 (PRM1-Z8)")]

    def _require_connected(self) -> None:
        if not self._connected:
            raise RuntimeError("MockKDC101Polariser: not connected")
