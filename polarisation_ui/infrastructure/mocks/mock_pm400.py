"""Mock PM400PowerMeter for headless tests.

Simulates Malus-law power from the MockKDC101Polariser's current angle so
that the full calibration worker can run without any real hardware.
"""

import math
import random
from typing import Optional


class MockPM400:
    """Simulated PM400PowerMeter.

    *kdc_mock* is a MockKDC101Polariser (or any object with ``get_position_deg()``).
    Power is computed as:

        P = P_max * cos²(θ) * 10^(-attenuation_dB/10) + noise

    where θ is the current KDC position, P_max = 1 µW, and noise is ±0.5 nW.
    """

    _P_MAX_W: float = 1e-6
    _NOISE_W: float = 5e-10

    def __init__(self, kdc_mock: Optional[object] = None) -> None:
        self._kdc = kdc_mock
        self._connected: bool = False
        self._wavelength_nm: float = 633.0
        self._attenuation_dB: float = 0.0
        self._averaging: int = 1

    # ── Connection ────────────────────────────────────────────────────────────

    def connect(self, visa_resource: str) -> None:
        self._connected = True

    def disconnect(self) -> None:
        self._connected = False

    def is_connected(self) -> bool:
        return self._connected

    # ── Measurement ───────────────────────────────────────────────────────────

    def read_power_W(self) -> float:
        self._require_connected()
        angle_deg = self._kdc.get_position_deg() if self._kdc is not None else 0.0
        cos2 = math.cos(math.radians(angle_deg)) ** 2
        att_factor = 10.0 ** (-self._attenuation_dB / 10.0)
        power = self._P_MAX_W * cos2 * att_factor
        power += random.gauss(0.0, self._NOISE_W)
        return max(0.0, power)

    # ── Configuration ─────────────────────────────────────────────────────────

    def set_wavelength_nm(self, nm: float) -> None:
        self._wavelength_nm = nm

    def get_wavelength_nm(self) -> float:
        return self._wavelength_nm

    def set_attenuation_dB(self, db: float) -> None:
        self._attenuation_dB = db

    def get_attenuation_dB(self) -> float:
        return self._attenuation_dB

    def set_averaging(self, n: int) -> None:
        self._averaging = n

    def zero(self) -> None:
        pass

    def sensor_info(self) -> list:
        return ["S120C", "MOCK0001", "Mock sensor", "PHOT", "PHOT", "0"]

    # ── Discovery ─────────────────────────────────────────────────────────────

    @staticmethod
    def list_resources() -> list[str]:
        return ["USB0::0x1313::0x8078::MOCK00001::INSTR"]

    # ── Internal ──────────────────────────────────────────────────────────────

    def _require_connected(self) -> None:
        if not self._connected:
            raise RuntimeError("MockPM400: not connected")
