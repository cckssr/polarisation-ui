"""Hardware-free bench for ``--simulate`` and the UI tests.

Bundles the existing in-memory / PTY mocks: a ``MockArduino`` behind a PTY port (talks SCPI to the
real ``DualEncoderArduino`` client), a ``MockKDC101Polariser`` and a ``MockPM400`` whose power
follows the polariser angle (Malus's law).
"""

from __future__ import annotations

import threading

from polarisation_ui.infrastructure.logging import Debug
from polarisation_ui.infrastructure.mocks.mock_arduino import MockArduino
from polarisation_ui.infrastructure.mocks.mock_kdc101_polariser import MockKDC101Polariser
from polarisation_ui.infrastructure.mocks.mock_pm400 import MockPM400


class _PolariserAngle:
    """Angle source for the PM400 mock that reads 0° while the KDC101 mock is not connected.

    ``MockKDC101Polariser.get_position_deg()`` raises when disconnected, which would make the
    simulated PM400 report a lost connection as soon as it is connected before the stage.
    """

    def __init__(self, kdc: MockKDC101Polariser) -> None:
        """Wrap the polariser mock."""
        self._kdc = kdc

    def get_position_deg(self) -> float:
        """Return the stage angle, or 0.0 while the stage is not connected."""
        return self._kdc.get_position_deg() if self._kdc.is_connected() else 0.0


class SimulatedBench:
    """A complete simulated polarisation bench (Arduino PTY, KDC101 polariser, PM400)."""

    DRIFT_INTERVAL_S = 0.05

    def __init__(self, poll_interval_ms: int = 20, drift: bool = True) -> None:
        """Start the mock Arduino; the KDC101 and PM400 mocks are created disconnected.

        With ``drift`` the two encoders keep turning (at the mock's configured speeds) so the angle
        displays and the Malus-law intensity of the simulated ADC change on their own — the mock
        only advances its angles while it streams frames, which the UI does not request.
        """
        self.arduino = MockArduino(poll_interval_ms=poll_interval_ms)
        self.port: str = self.arduino.start()
        self.kdc = MockKDC101Polariser()
        self.pm400 = MockPM400(kdc_mock=_PolariserAngle(self.kdc))
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        if drift:
            self._thread = threading.Thread(target=self._drift, name="sim-drift", daemon=True)
            self._thread.start()
        Debug.info(f"Simulated bench ready (Arduino PTY {self.port})")

    def _drift(self) -> None:
        a, b = self.arduino.encoder_a, self.arduino.encoder_b
        while not self._stop.wait(self.DRIFT_INTERVAL_S):
            a.current_angle = (a.current_angle + self.arduino.encoder_a_speed) % 360.0
            b.current_angle = (b.current_angle + self.arduino.encoder_b_speed) % 360.0

    def stop(self) -> None:
        """Stop the drift thread and the mock Arduino, releasing its PTY port."""
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=1.0)
        self.arduino.stop()
