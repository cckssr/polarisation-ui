"""Mock KDC101NDStage for headless tests."""

from polarisation_ui.infrastructure.devices.kdc101_nd_stage import TRAVEL_MM


class MockKDC101NDStage:
    """Simulated KDC101NDStage.

    move_to_mm() updates the internal position instantly (clamped to
    ``[0, TRAVEL_MM]``); home() resets to 0 mm. No real hardware or pylablib
    needed.
    """

    def __init__(self) -> None:
        """Start disconnected at position 0 mm."""
        self._position_mm: float = 0.0
        self._connected: bool = False
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
        """Reset the simulated position to 0 mm instantly (wait/timeout are ignored)."""
        self._require_connected()
        self._position_mm = 0.0
        self._homed = True

    def move_to_mm(self, position_mm: float, wait: bool = True, timeout: float = 60.0) -> None:
        """Set the simulated position instantly, clamped to travel (wait/timeout are ignored)."""
        self._require_connected()
        self._position_mm = max(0.0, min(TRAVEL_MM, position_mm))

    def get_position_mm(self) -> float:
        """Return the current simulated position in millimetres."""
        self._require_connected()
        return self._position_mm

    def get_position_mm_nowait(self) -> float:
        """Mirror KDC101NDStage.get_position_mm_nowait().

        The mock has no lock contention to simulate, so it always succeeds
        like get_position_mm().
        """
        return self.get_position_mm()

    def is_homed(self) -> bool:
        """Return whether home() has been called since construction."""
        return self._homed

    def stop(self, immediate: bool = True) -> None:
        """No-op — the mock has no in-flight move to interrupt."""
        self.stop_called += 1

    def enable(self, state: bool) -> None:
        """No-op — the mock has no motor-enable state to simulate."""
        self._require_connected()

    @staticmethod
    def list_devices() -> list[tuple[str, str]]:
        """Return a single fixed fake device (connection id, description) pair."""
        return [("mock://nd-stage", "Mock KDC101 (MTS50/M-Z8)")]

    def _require_connected(self) -> None:
        if not self._connected:
            raise RuntimeError("MockKDC101NDStage: not connected")
