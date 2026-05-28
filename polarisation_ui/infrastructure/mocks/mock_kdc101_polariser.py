"""Mock KDC101Polariser for headless tests."""

import math
from typing import Optional


class MockKDC101Polariser:
    """Simulated KDC101Polariser.

    move_to() updates the internal position instantly; home() resets to 0°.
    No real hardware or pylablib needed.
    """

    def __init__(self) -> None:
        self._position_deg: float = 0.0
        self._connected: bool = False

    def connect(self, conn_id: str) -> None:
        self._connected = True

    def disconnect(self) -> None:
        self._connected = False

    def is_connected(self) -> bool:
        return self._connected

    def home(self, wait: bool = True, timeout: float = 120.0) -> None:
        self._require_connected()
        self._position_deg = 0.0

    def move_to(
        self, angle_deg: float, wait: bool = True, timeout: float = 60.0
    ) -> None:
        self._require_connected()
        self._position_deg = angle_deg

    def get_position_deg(self) -> float:
        self._require_connected()
        return self._position_deg

    def enable(self, state: bool) -> None:
        self._require_connected()

    @staticmethod
    def list_devices() -> list[tuple[str, str]]:
        return [("mock://kdc101", "Mock KDC101 (PRM1-Z8)")]

    def _require_connected(self) -> None:
        if not self._connected:
            raise RuntimeError("MockKDC101Polariser: not connected")
