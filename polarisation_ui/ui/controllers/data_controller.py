"""
Data controller for continuous sensor reading.

Manages threaded data acquisition from encoder devices and
emits signals for UI updates. Separates data collection from UI rendering.
"""

import math
import random
from collections import deque

from PySide6.QtCore import QObject, QTimer, Signal, Slot
from typing import Optional


def _evaluate_encoder(diag: Optional[dict], label: str) -> tuple[bool, str]:
    """
    Evaluate one encoder's SYST:DIAG? dict.

    Returns (ok, description) — description is "<label>: OK" when healthy or
    "<label>: <fault list>" when one or more flags are set.
    """
    if diag is None:
        return False, f"{label}: keine Antwort"
    faults: list[str] = []
    if diag.get("compHigh"):
        faults.append("Magnet zu weit (COMP_H)")
    if diag.get("compLow"):
        faults.append("Magnet zu nah (COMP_L)")
    if diag.get("cof"):
        faults.append("CORDIC-Überlauf (COF)")
    if not diag.get("ocf", True):
        faults.append("Kalibrierung ausstehend (OCF)")
    ok = len(faults) == 0
    return ok, f"{label}: {'; '.join(faults) if faults else 'OK'}"


from polarisation_ui.core.models import AcquisitionSettings
from polarisation_ui.core.utils import circular_mean_deg
from polarisation_ui.infrastructure.device_manager import GoniometerDeviceManager
from polarisation_ui.infrastructure.logging import Debug


class DataController(QObject):
    """
    Controller for managing continuous data acquisition.

    Responsibilities:
        - Poll encoders at regular intervals
        - Process readings and emit signals
        - Manage measurement sessions
        - Handle errors gracefully

    Signals:
        angles_updated: Emitted with (sample_angle, detector_angle)
        error_occurred: Emitted when read error occurs
        measurement_started: Emitted when measurement begins
        measurement_stopped: Emitted when measurement ends
    """

    # Data signals
    angles_updated = Signal(float, float)  # sample_angle, detector_angle
    intensity_updated = Signal(float)  # photodiode / ADC reading (a.u.)
    # Per-encoder diagnostic results: (a_ok, a_desc, b_ok, b_desc)
    diagnostics_updated = Signal(bool, str, bool, str)

    # Error signals
    error_occurred = Signal(str)  # error_message

    # Measurement signals
    measurement_started = Signal()
    measurement_stopped = Signal()

    # Default polling interval (milliseconds)
    DEFAULT_POLL_INTERVAL = 100  # 10 Hz

    # Delay before each reconnection attempt (milliseconds)
    RETRY_DELAY_MS = 3000

    # How often to run SYST:DIAG? checks (milliseconds)
    DIAG_INTERVAL_MS = 5000  # every 5 s

    # --- Mock intensity parameters -------------------------------------------
    # Replace _read_intensity() body with a real ADC read when hardware is ready.
    _MOCK_PEAK_ANGLE: float = 90.0  # degrees — centre of simulated Gaussian
    _MOCK_SIGMA: float = 20.0  # width (degrees)
    _MOCK_AMPLITUDE: float = 1000.0  # peak intensity (a.u.)
    _MOCK_NOISE: float = 15.0  # Gaussian noise amplitude
    # -------------------------------------------------------------------------

    # Signal emitted when a reconnection attempt begins
    retry_connecting = Signal()
    # Signal emitted when the connection is re-established after errors
    reconnect_succeeded = Signal()
    # Signal emitted when max errors are reached and we stop trying
    connection_lost = Signal()

    def __init__(
        self,
        device_manager: GoniometerDeviceManager,
        parent: Optional[QObject] = None,
        use_mock_intensity: bool = False,
    ):
        """
        Initialize data controller.

        Args:
            device_manager: Device manager instance
            parent: Parent QObject
        """
        super().__init__(parent)

        self.device_manager = device_manager

        # Polling timer
        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self._poll_sensors)
        self.poll_interval = self.DEFAULT_POLL_INTERVAL

        # Retry timer — fires once after RETRY_DELAY_MS when connection is lost
        self._retry_timer = QTimer(self)
        self._retry_timer.setSingleShot(True)
        self._retry_timer.timeout.connect(self._attempt_reconnect)

        # Diagnostic timer — periodically sends SYST:DIAG? to both encoders
        self._diag_timer = QTimer(self)
        self._diag_timer.timeout.connect(self._check_diagnostics)

        # State tracking
        self._is_measuring = False
        self._error_count = 0
        self._max_errors = 10  # Stop after this many consecutive errors

        # When True, sample angle is corrected as (360 - raw) % 360 to account
        # for the diametrically flipped magnet on the sample stage.
        self.sample_inverted: bool = False

        # Acquisition settings and rolling-average buffers.
        # Populated with defaults here; call update_acq_settings() from MainWindow
        # at startup and whenever the settings dialog is accepted.
        self._acq_settings: AcquisitionSettings = AcquisitionSettings()
        self._sample_buffer: deque[float] = deque(
            maxlen=self._acq_settings.samp_averages
        )
        self._det_buffer: deque[float] = deque(maxlen=self._acq_settings.det_averages)

        # When True, fall back to Gaussian simulation instead of querying ADC.
        # Set to True in unit tests that don't have a mock device attached.
        self._use_mock_intensity = use_mock_intensity

        Debug.debug("Data controller initialized")

    # ==================== Polling Control ====================

    # ==================== Acquisition Settings ====================

    def update_acq_settings(self, settings: AcquisitionSettings) -> None:
        """
        Apply new acquisition settings.

        Recreates the averaging buffers (discarding old samples) and syncs
        the sample-inversion flag.  Call at startup and whenever the settings
        dialog is accepted.
        """
        self._acq_settings = settings
        self._sample_buffer = deque(maxlen=settings.samp_averages)
        self._det_buffer = deque(maxlen=settings.det_averages)
        self.sample_inverted = settings.sample_stage_inverted
        Debug.info(
            f"Acq settings updated: "
            f"samp={settings.samp_averages}× (on={settings.samp_average_on}), "
            f"det={settings.det_averages}× (on={settings.det_average_on}), "
            f"inverted={settings.sample_stage_inverted}"
        )

    def clear_sample_buffer(self) -> None:
        """Flush the sample-angle averaging buffer (e.g. on sensor recovery)."""
        self._sample_buffer.clear()

    def clear_det_buffer(self) -> None:
        """Flush the detector-angle averaging buffer (e.g. on sensor recovery)."""
        self._det_buffer.clear()

    # ==================== Polling Control ====================

    def set_poll_interval(self, interval_ms: int) -> None:
        """
        Set polling interval.

        Args:
            interval_ms: Interval in milliseconds
        """
        self.poll_interval = max(10, interval_ms)  # Minimum 10ms

        if self.poll_timer.isActive():
            self.poll_timer.setInterval(self.poll_interval)

        Debug.debug(f"Poll interval set to {self.poll_interval}ms")

    def start_continuous_reading(self) -> bool:
        """
        Start continuous sensor polling.

        Returns:
            bool: True if started successfully
        """
        if not self.device_manager.is_encoder_connected():
            Debug.warning("Cannot start reading: encoders not connected")
            return False

        if self.poll_timer.isActive():
            Debug.warning("Polling already active")
            return True

        self._error_count = 0
        self.poll_timer.start(self.poll_interval)
        self._diag_timer.start(self.DIAG_INTERVAL_MS)
        Debug.info("Continuous reading started")
        return True

    def stop_continuous_reading(self) -> None:
        """Stop continuous sensor polling."""
        if self.poll_timer.isActive():
            self.poll_timer.stop()
            self._diag_timer.stop()
            Debug.info("Continuous reading stopped")

    def is_reading(self) -> bool:
        """Check if continuous reading is active."""
        return self.poll_timer.isActive()

    # ==================== Measurement Control ====================

    def start_measurement(self) -> bool:
        """
        Start measurement session.

        Returns:
            bool: True if started successfully
        """
        if self._is_measuring:
            Debug.warning("Measurement already in progress")
            return False

        if not self.start_continuous_reading():
            return False

        self._is_measuring = True
        self.measurement_started.emit()
        Debug.info("Measurement session started")
        return True

    def stop_measurement(self) -> None:
        """Stop measurement session."""
        if not self._is_measuring:
            return

        self.stop_continuous_reading()
        self._is_measuring = False
        self.measurement_stopped.emit()
        Debug.info("Measurement session stopped")

    def is_measuring(self) -> bool:
        """Check if measurement is active."""
        return self._is_measuring

    # ==================== Intensity Reading ====================

    def _read_intensity(self, detector_angle: float) -> float:
        """
        Return the current photodiode intensity (a.u.).

        Reads real ADC voltage via MEAS:ADC:VOLT?.  Falls back to a Gaussian
        simulation when use_mock_intensity=True (tests without hardware).
        """
        if self._use_mock_intensity:
            diff = detector_angle - self._MOCK_PEAK_ANGLE
            signal = self._MOCK_AMPLITUDE * math.exp(
                -(diff**2) / (2.0 * self._MOCK_SIGMA**2)
            )
            return signal + random.gauss(0.0, self._MOCK_NOISE)

        voltage = self.device_manager.read_adc_voltage()
        if voltage is None:
            return 0.0
        return voltage

    # ==================== Data Acquisition ====================

    @Slot()
    def _poll_sensors(self) -> None:
        """
        Poll sensors and emit updated data.

        Called by timer at regular intervals.
        """
        try:
            # Read both encoders
            angles = self.device_manager.read_angles()

            if angles is None:
                self._handle_read_error("Failed to read angles")
                return

            sample_angle, detector_angle = angles

            # Correct for diametrically flipped magnet on sample stage
            if self.sample_inverted:
                sample_angle = (360.0 - sample_angle) % 360.0

            # Reset error counter on successful read
            self._error_count = 0

            # Apply rolling circular averaging before emitting so that
            # consumers receive display-ready values.
            self._sample_buffer.append(sample_angle)
            self._det_buffer.append(detector_angle)

            display_sample = (
                circular_mean_deg(self._sample_buffer)
                if self._acq_settings.samp_average_on and self._sample_buffer
                else sample_angle
            )
            display_det = (
                circular_mean_deg(self._det_buffer)
                if self._acq_settings.det_average_on and self._det_buffer
                else detector_angle
            )

            # Emit intensity first so MainWindow has a fresh value when
            # angles_updated is processed (direct-connection ordering).
            self.intensity_updated.emit(self._read_intensity(detector_angle))
            self.angles_updated.emit(display_sample, display_det)

        except Exception as e:
            self._handle_read_error(f"Exception during sensor poll: {e}")

    def _handle_read_error(self, error_msg: str) -> None:
        """
        Handle sensor read errors.

        Args:
            error_msg: Error message
        """
        self._error_count += 1

        Debug.error(f"Read error ({self._error_count}/{self._max_errors}): {error_msg}")

        # Emit error signal
        self.error_occurred.emit(error_msg)

        # Pause polling and schedule a delayed reconnect attempt
        self.poll_timer.stop()

        if self._error_count >= self._max_errors:
            Debug.error("Too many consecutive errors, giving up")
            if self._is_measuring:
                self.stop_measurement()
            self.connection_lost.emit()
        else:
            self._retry_timer.start(self.RETRY_DELAY_MS)

    @Slot()
    def _attempt_reconnect(self) -> None:
        """Try to re-establish the serial connection and resume polling."""
        self.retry_connecting.emit()
        Debug.info(f"Reconnect attempt {self._error_count}/{self._max_errors}...")

        try:
            success = self.device_manager.reconnect_encoders()
            if success:
                self._error_count = 0
                self._sample_buffer.clear()
                self._det_buffer.clear()
                self.poll_timer.start(self.poll_interval)
                self._diag_timer.start(self.DIAG_INTERVAL_MS)
                self.reconnect_succeeded.emit()
                Debug.info("Reconnected successfully")
            else:
                self._handle_read_error("Reconnect failed")
        except Exception as e:
            self._handle_read_error(f"Exception during reconnect: {e}")

    # ==================== Manual Reading ====================

    def read_once(self) -> Optional[tuple[float, float]]:
        """
        Perform single sensor read without starting continuous polling.

        Returns:
            Tuple of (sample_angle, detector_angle) or None on error
        """
        if not self.device_manager.is_encoder_connected():
            Debug.warning("Cannot read: encoders not connected")
            return None

        try:
            angles = self.device_manager.read_angles()

            if angles is not None:
                sample_angle, detector_angle = angles
                self.angles_updated.emit(sample_angle, detector_angle)
                return angles

            return None

        except Exception as e:
            Debug.error(f"Error during manual read: {e}")
            self.error_occurred.emit(str(e))
            return None

    # ==================== Diagnostics ====================

    @Slot()
    def _check_diagnostics(self) -> None:
        """
        Run SYST:DIAG? on both encoders and emit diagnostics_updated.

        The angle-polling timer is paused for the duration of the SCPI
        exchange so that serial commands do not interleave.
        """
        was_polling = self.poll_timer.isActive()
        if was_polling:
            self.poll_timer.stop()

        try:
            result = self.device_manager.read_diagnostics_both()
        finally:
            if was_polling:
                self.poll_timer.start(self.poll_interval)

        if result is None:
            return  # not connected — nothing to report

        a_ok, a_desc = _evaluate_encoder(result[0], "Enc A")
        b_ok, b_desc = _evaluate_encoder(result[1], "Enc B")
        self.diagnostics_updated.emit(a_ok, a_desc, b_ok, b_desc)
        if not a_ok or not b_ok:
            Debug.warning(f"Sensor diagnostics: {a_desc} | {b_desc}")
        else:
            Debug.debug(f"Sensor diagnostics OK: {a_desc} | {b_desc}")

    # ==================== Cleanup ====================

    def cleanup(self) -> None:
        """Clean up resources."""
        self._retry_timer.stop()
        self._diag_timer.stop()
        self.stop_continuous_reading()

        if self._is_measuring:
            self.stop_measurement()

        Debug.debug("Data controller cleaned up")
