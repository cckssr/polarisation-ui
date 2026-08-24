"""Mock PM400PowerMeter for headless tests.

Simulates power from either a MockKDC101Polariser's current angle (Malus's
law) or a MockKDC101NDStage's current position (exponential wedge
transmission) so that the full calibration worker can run without any real
hardware.
"""

import math
import random

from polarisation_ui.core.exceptions import PM400Error
from polarisation_ui.infrastructure.devices.kdc101_nd_stage import TRAVEL_MM


class MockPM400:
    """Simulated PM400PowerMeter.

    *kdc_mock* is a MockKDC101Polariser (or any object with ``get_position_deg()``);
    when given, power follows Malus's law:

        P = P_max * cos²(θ) * 10^(-attenuation_dB/10) + noise

    *nd_mock* is a MockKDC101NDStage (or any object with ``get_position_mm()``);
    when given instead, power follows an exponential gradient-ND-filter model:

        P = P_max * 10^(-OD_max * x / TRAVEL_MM) * 10^(-attenuation_dB/10) + noise

    where x is the current ND-stage position (mm). Passing both is not a
    supported configuration; *nd_mock* takes precedence if both are given.
    P_max = 1 µW, noise is Gaussian with the same magnitude in both models.
    """

    _P_MAX_W: float = 1e-6
    _NOISE_W: float = 5e-10
    _OD_MAX: float = 3.0
    """Maximum optical density of the simulated gradient ND filter (3 OD ≈ 30 dB)."""

    def __init__(self, kdc_mock: object | None = None, nd_mock: object | None = None) -> None:
        """Set up the mock, optionally linked to an angle- or position-driven power source."""
        self._kdc = kdc_mock
        self._nd = nd_mock
        self._connected: bool = False
        self._wavelength_nm: float = 633.0
        self._attenuation_dB: float = 0.0
        self._averaging: int = 1

    # ── Connection ────────────────────────────────────────────────────────────

    def connect(self, visa_resource: str) -> None:
        """Mark the mock as connected (visa_resource is accepted but ignored)."""
        self._connected = True

    def disconnect(self) -> None:
        """Mark the mock as disconnected."""
        self._connected = False

    def is_connected(self) -> bool:
        """Return whether the mock is currently connected."""
        return self._connected

    # ── Measurement ───────────────────────────────────────────────────────────

    def read_power_W(self) -> float:
        """Return a simulated power reading (W) from whichever intensity source is linked."""
        self._require_connected()
        att_factor = 10.0 ** (-self._attenuation_dB / 10.0)
        if self._nd is not None:
            position_mm = self._nd.get_position_mm()
            transmission = 10.0 ** (-self._OD_MAX * position_mm / TRAVEL_MM)
            power = self._P_MAX_W * transmission * att_factor
        else:
            angle_deg = self._kdc.get_position_deg() if self._kdc is not None else 0.0
            cos2 = math.cos(math.radians(angle_deg)) ** 2
            power = self._P_MAX_W * cos2 * att_factor
        power += random.gauss(0.0, self._NOISE_W)
        return max(0.0, power)

    # ── Configuration ─────────────────────────────────────────────────────────

    def set_wavelength_nm(self, nm: float) -> None:
        """Store the configured sensor wavelength (nm); does not affect the simulated power."""
        self._wavelength_nm = nm

    def get_wavelength_nm(self) -> float:
        """Return the configured sensor wavelength (nm)."""
        return self._wavelength_nm

    def set_attenuation_dB(self, db: float) -> None:
        """Set the beamsplitter attenuation (dB) applied to the simulated power."""
        self._attenuation_dB = db

    def get_attenuation_dB(self) -> float:
        """Return the configured beamsplitter attenuation (dB)."""
        return self._attenuation_dB

    def set_averaging(self, n: int) -> None:
        """Store the averaging count; the mock ignores it (no real averaging)."""
        self._averaging = n

    def zero(self) -> None:
        """No-op — the mock has no zero-offset to calibrate."""

    def sensor_info(self) -> list:
        """Return a fixed fake sensor identification tuple."""
        return ["S120C", "MOCK0001", "Mock sensor", "PHOT", "PHOT", "0"]

    # ── Discovery ─────────────────────────────────────────────────────────────

    @staticmethod
    def list_resources() -> list[str]:
        """Return a single fixed fake VISA resource string."""
        return ["USB0::0x1313::0x8078::MOCK00001::INSTR"]

    # ── Internal ──────────────────────────────────────────────────────────────

    def _require_connected(self) -> None:
        if not self._connected:
            raise PM400Error("MockPM400: not connected")
