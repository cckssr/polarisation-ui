"""In-memory mock of NDStepperStage for headless worker/UI tests."""

from polarisation_ui.core.exceptions import NDStageError
from polarisation_ui.infrastructure.devices.nd_stepper import MAX_ANGLE_DEG, MIN_ANGLE_DEG


class MockNDStage:
    """Simulated NDStepperStage.

    ``move_to_deg()`` updates the position instantly (clamped to
    ``[MIN_ANGLE_DEG, MAX_ANGLE_DEG]``); ``home()`` resets to 0°. No serial port needed.
    For protocol-level tests use ``MockNDStepperFirmware`` instead.
    """

    def __init__(self) -> None:
        """Start disconnected at position 0°."""
        self._position_deg: float = 0.0
        self._connected: bool = False
        self._homed: bool = False
        self.stop_called: int = 0

    def connect(self, port: str) -> None:
        """Mark the mock as connected (port is accepted but ignored)."""
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

    def zero(self) -> None:
        """Define the current position as 0°."""
        self._require_connected()
        self._position_deg = 0.0
        self._homed = True

    def move_to_deg(self, angle_deg: float, wait: bool = True, timeout: float = 60.0) -> None:
        """Set the simulated position instantly, clamped to range (wait/timeout are ignored)."""
        self._require_connected()
        self._position_deg = max(MIN_ANGLE_DEG, min(MAX_ANGLE_DEG, angle_deg))

    def jog_deg(self, delta_deg: float, wait: bool = True, timeout: float = 60.0) -> None:
        """Shift the simulated position by *delta_deg*, clamped to range."""
        self._require_connected()
        self._position_deg = max(MIN_ANGLE_DEG, min(MAX_ANGLE_DEG, self._position_deg + delta_deg))

    def get_position_deg(self) -> float:
        """Return the current simulated position in degrees."""
        self._require_connected()
        return self._position_deg

    def get_position_deg_nowait(self) -> float:
        """Mirror NDStepperStage.get_position_deg_nowait() (the mock has no lock contention)."""
        return self.get_position_deg()

    def get_driver_status(self) -> str:
        """Return ``"OK"`` — the mock driver never faults."""
        self._require_connected()
        return "OK"

    def reset_driver(self) -> str:
        """Return ``"OK"`` — nothing to reset in the mock."""
        self._require_connected()
        return "OK"

    def self_test(self) -> tuple[bool, str]:
        """Return a passing self-test result."""
        self._require_connected()
        return True, "PASS"

    def is_homed(self) -> bool:
        """Return whether home()/zero() has been called since construction."""
        return self._homed

    def stop(self, immediate: bool = True) -> None:
        """No-op — the mock has no in-flight move to interrupt."""
        self.stop_called += 1

    def enable(self, state: bool) -> None:
        """No-op — the mock has no motor-enable state to simulate."""
        self._require_connected()

    @staticmethod
    def list_devices() -> list[tuple[str, str]]:
        """Return a single fixed fake device (port, description) pair."""
        return [("mock://nd-stage", "Mock ND stepper (ESP32 + DRV8825)")]

    def _require_connected(self) -> None:
        if not self._connected:
            raise NDStageError("MockNDStage: not connected")
