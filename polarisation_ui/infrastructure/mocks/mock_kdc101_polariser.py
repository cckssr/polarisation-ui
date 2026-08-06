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

    def move_to(self, angle_deg: float, wait: bool = True, timeout: float = 60.0) -> None:
        """Set the simulated position instantly (wait/timeout are ignored)."""
        self._require_connected()
        self._position_deg = angle_deg

    def get_position_deg(self) -> float:
        """Return the current simulated position in degrees."""
        self._require_connected()
        return self._position_deg

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
