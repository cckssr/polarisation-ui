"""
Data controller for continuous sensor reading.

Manages threaded data acquisition from encoder devices and
emits signals for UI updates. Separates data collection from UI rendering.
"""

import math
import random
import time
from collections import deque
from typing import Optional

from PySide6.QtCore import QObject, QTimer, Signal, Slot
from polarisation_ui.core.models import AcquisitionSettings, Frame
from polarisation_ui.core.power_calibration import PowerCalibrationProfile
from polarisation_ui.core.utils import circular_mean_deg
from polarisation_ui.infrastructure.config import import_config
from polarisation_ui.infrastructure.device_manager import GoniometerDeviceManager
from polarisation_ui.infrastructure.logging import Debug
from polarisation_ui.infrastructure.qt_threads import ReconnectWorker
from polarisation_ui.infrastructure.session_journal import SessionJournal

CONFIG = import_config()


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


def _circular_delta(a: float, b: float) -> float:
    """Smallest absolute angular difference between two angles in [0, 360)."""
    diff = abs(a - b) % 360.0
    return min(diff, 360.0 - diff)


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
    frame_ready = Signal(Frame)  # consolidated per-sample frame
    # Per-encoder diagnostic results: (a_ok, a_desc, b_ok, b_desc)
    diagnostics_updated = Signal(bool, str, bool, str)
    # Opt-in debug signal — raw DATA:FRAME string (off by default for perf).
    # Enable via enable_raw_frame_signal(True) before opening the Raw Stream tab.
    raw_frame = Signal(str)
    # Emitted every poll with the computed optical power in watts, or NaN when
    # no calibration profile is loaded or the current gain has no calibration data.
    power_updated = Signal(float)
    # Measured polling rate in Hz (emitted after each successful frame once
    # enough samples are available for a stable estimate).
    poll_rate_updated = Signal(float)

    # Error signals
    error_occurred = Signal(str)  # error_message

    # Measurement signals
    measurement_started = Signal()
    measurement_stopped = Signal()

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

        # Load tunable parameters from config so nothing is hardcoded here.
        _timers = CONFIG.get("timers", {})
        _conn = CONFIG.get("connection", {})
        _acq_cfg = CONFIG.get("acquisition", {})

        # Polling timer
        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self._poll_sensors)
        self.poll_interval: int = int(_timers.get("acquisition_timer_interval", 100))

        # Retry timer — fires once per backoff step when connection is lost
        self._retry_timer = QTimer(self)
        self._retry_timer.setSingleShot(True)
        self._retry_timer.timeout.connect(self._attempt_reconnect)

        # Diagnostic timer — periodically sends DIAG:ENC? to both encoders
        self._diag_timer = QTimer(self)
        self._diag_timer.timeout.connect(self._check_diagnostics)
        self._diag_interval_ms: int = int(_timers.get("diag_interval_ms", 5000))

        # State tracking
        self._is_measuring = False
        self._error_count = 0
        self._max_errors: int = int(_conn.get("max_retry_attempts", 10))
        self._backoff_delays_ms: list[int] = list(
            _conn.get("backoff_delays_ms", [1000, 2000, 4000, 8000, 15000])
        )
        self._backoff_attempt = 0

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

        # Spike filter: last accepted angles for derivative check.
        self._last_sample_angle: Optional[float] = None
        self._last_det_angle: Optional[float] = None
        # Consecutive spike rejections; reference is cleared after this many in a row.
        self._spike_reject_streak: int = 0
        self._spike_reset_after: int = int(_acq_cfg.get("spike_reset_after", 5))

        # Poll-rate measurement: ring buffer of raw-read (pre-spike-filter) timestamps.
        self._poll_ts_deque: deque[float] = deque(maxlen=20)

        # When True, fall back to Gaussian simulation instead of querying ADC.
        # Set to True in unit tests that don't have a mock device attached.
        self._use_mock_intensity = use_mock_intensity

        # Current PDTIA gain stage (1–4; 0 = not set).
        self._current_pdtia_gain: int = 0

        # Active detector calibration profile; None when not loaded.
        self._calibration_profile: Optional[PowerCalibrationProfile] = None

        # When True, the raw_frame signal is emitted with the DATA:FRAME string
        # on every poll.  Disabled by default — only enabled when the Raw Stream
        # tab in the debug dialog is open, to avoid unnecessary string formatting.
        self._raw_frame_enabled: bool = False

        # Last seen DATA:FRAME sequence number — used to detect gaps in the stream.
        self._last_frame_seq: Optional[int] = None

        # Active session journal — created on start_measurement(), closed/finalized
        # when the user explicitly exports or stops. Preserved across reconnects.
        self._journal: Optional[SessionJournal] = None

        # Current ReconnectWorker instance — kept as attribute to prevent GC while running.
        self._reconnect_worker: Optional[ReconnectWorker] = None

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
            f"inverted={settings.sample_stage_inverted}, "
            f"spike_filter={settings.spike_filter_enabled} "
            f"(max_delta={settings.spike_max_delta_deg}°)"
        )

    def clear_sample_buffer(self) -> None:
        """Flush the sample-angle averaging buffer (e.g. on sensor recovery)."""
        self._sample_buffer.clear()
        self._last_sample_angle = None
        self._spike_reject_streak = 0

    def clear_det_buffer(self) -> None:
        """Flush the detector-angle averaging buffer (e.g. on sensor recovery)."""
        self._det_buffer.clear()
        self._last_det_angle = None
        self._spike_reject_streak = 0

    # ==================== Polling Control ====================

    def enable_raw_frame_signal(self, enabled: bool) -> None:
        """
        Enable or disable the opt-in ``raw_frame`` debug signal.

        When *enabled* is True, each poll emits ``raw_frame(str)`` with a
        synthetic ``DATA:FRAME`` string built from the latest sensor readings.
        Disable when the Raw Stream debug tab is closed to avoid the overhead
        of string formatting on every 100 ms tick.
        """
        self._raw_frame_enabled = enabled
        Debug.debug(f"raw_frame signal {'enabled' if enabled else 'disabled'}")

    def set_diag_interval(self, interval_ms: int) -> None:
        """Change the periodic diagnostic poll rate (ms). Call 500 when debug dialog opens."""
        self._diag_interval_ms = interval_ms
        if self._diag_timer.isActive():
            self._diag_timer.setInterval(interval_ms)

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
        self._backoff_attempt = 0
        self.poll_timer.start(self.poll_interval)
        self._diag_timer.start(self._diag_interval_ms)
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

        Continuous reading must already be active (started on device connect).
        Returns False if a measurement is already running.
        """
        if self._is_measuring:
            Debug.warning("Measurement already in progress")
            return False

        if not self.device_manager.is_encoder_connected():
            Debug.warning("Cannot start measurement: device not connected")
            return False

        self._is_measuring = True
        self._start_journal()
        self.measurement_started.emit()
        Debug.info("Measurement session started")
        return True

    def stop_measurement(self) -> None:
        """Stop measurement session. Continuous reading keeps running. Journal closed but not finalized."""
        if not self._is_measuring:
            return

        self._is_measuring = False
        if self._journal is not None and self._journal.is_active:
            self._journal.close()
        self.measurement_stopped.emit()
        Debug.info("Measurement session stopped")

    @property
    def current_journal(self) -> Optional[SessionJournal]:
        """The active (or most-recently closed) session journal, or None."""
        return self._journal

    def is_measuring(self) -> bool:
        """Check if measurement is active."""
        return self._is_measuring

    # ==================== PDTIA Gain Control ====================

    def set_pdtia_gain(self, stage: int) -> bool:
        """
        Set PDTIA discrete gain stage (1–4).

        Pauses polling for the duration of the SCPI exchange (same pattern as
        _check_diagnostics) so commands don't interleave with ongoing reads.
        Updates the internal gain tracker used to annotate emitted Frames.
        """
        was_polling = self.poll_timer.isActive()
        if was_polling:
            self.poll_timer.stop()
        try:
            ok = self.device_manager.set_pdtia_gain(stage)
        finally:
            if was_polling:
                self.poll_timer.start(self.poll_interval)
        if ok:
            self._current_pdtia_gain = stage
            Debug.info(f"DataController: PDTIA gain updated to stage {stage}")
        return ok

    def update_calibration_profile(
        self, profile: Optional[PowerCalibrationProfile]
    ) -> None:
        """Set the detector calibration profile used to convert voltage → watts."""
        self._calibration_profile = profile
        Debug.info(
            f"Calibration profile updated: {profile.name if profile else 'None'}"
        )

    @property
    def pdtia_gain(self) -> int:
        """Currently active PDTIA gain stage (0 = not set)."""
        return self._current_pdtia_gain

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

            # Track raw poll rate here, before the spike filter, so the displayed
            # Hz reflects the true timer rate rather than the acceptance rate.
            now = time.monotonic()
            self._poll_ts_deque.append(now)
            if len(self._poll_ts_deque) >= 2:
                span = self._poll_ts_deque[-1] - self._poll_ts_deque[0]
                if span > 0:
                    hz = (len(self._poll_ts_deque) - 1) / span
                    self.poll_rate_updated.emit(hz)

            # Spike filter: reject frames where either angle jumps too far.
            # After spike_reset_after consecutive rejects the reference is cleared
            # so a bad initial reading cannot permanently lock out all future frames.
            if self._acq_settings.spike_filter_enabled:
                threshold = self._acq_settings.spike_max_delta_deg
                sample_spike = (
                    self._last_sample_angle is not None
                    and _circular_delta(sample_angle, self._last_sample_angle)
                    > threshold
                )
                det_spike = (
                    self._last_det_angle is not None
                    and _circular_delta(detector_angle, self._last_det_angle)
                    > threshold
                )
                if sample_spike or det_spike:
                    self._spike_reject_streak += 1
                    if sample_spike:
                        Debug.debug(
                            f"Spike rejected: sample Δ="
                            f"{_circular_delta(sample_angle, self._last_sample_angle):.1f}°"  # type: ignore[arg-type]
                        )
                    else:
                        Debug.debug(
                            f"Spike rejected: detector Δ="
                            f"{_circular_delta(detector_angle, self._last_det_angle):.1f}°"  # type: ignore[arg-type]
                        )
                    if self._spike_reject_streak >= self._spike_reset_after:
                        Debug.info(
                            f"Spike filter: {self._spike_reject_streak} consecutive "
                            "rejects — resetting reference angles"
                        )
                        self._last_sample_angle = None
                        self._last_det_angle = None
                        self._spike_reject_streak = 0
                    return
                self._spike_reject_streak = 0

            self._last_sample_angle = sample_angle
            self._last_det_angle = detector_angle

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

            intensity = self._read_intensity(detector_angle)
            self.intensity_updated.emit(intensity)
            self.angles_updated.emit(display_sample, display_det)
            # Compute optical power from calibration profile (if loaded).
            conv_factor: Optional[float] = None
            power_W: Optional[float] = None
            if self._calibration_profile is not None:
                conv_factor = self._calibration_profile.conversion_factor(
                    self._current_pdtia_gain
                )
                if conv_factor is not None:
                    power_W = intensity * conv_factor

            self.power_updated.emit(power_W if power_W is not None else float("nan"))

            frame = Frame(
                ts_ms=int(time.monotonic() * 1000),
                sample_angle=display_sample,
                detector_angle=display_det,
                intensity=intensity,
                pdtia_gain=self._current_pdtia_gain,
                power_W=power_W,
                conv_factor_W_per_V=conv_factor,
            )
            self.frame_ready.emit(frame)
            if self._raw_frame_enabled:
                self._last_frame_seq = (self._last_frame_seq or 0) + 1
                raw = (
                    f"DATA:FRAME seq={self._last_frame_seq},"
                    f"tsMs={frame.ts_ms},"
                    f"angA={frame.sample_angle:.4f},"
                    f"angB={frame.detector_angle:.4f},"
                    f"adcV={frame.intensity:.6f}"
                )
                self.raw_frame.emit(raw)
            if self._is_measuring and self._journal is not None:
                self._journal.append_frame(frame)

        except Exception as e:
            self._handle_read_error(f"Exception during sensor poll: {e}")

    def _handle_read_error(self, error_msg: str) -> None:
        """Pause polling and schedule a reconnect with exponential backoff."""
        self._error_count += 1
        Debug.error(f"Read error ({self._error_count}/{self._max_errors}): {error_msg}")
        self.error_occurred.emit(error_msg)
        self.poll_timer.stop()

        if self._error_count >= self._max_errors:
            Debug.error("Max reconnect attempts exhausted — declaring connection lost")
            # Close the journal (not finalized — stays recoverable)
            if self._journal is not None and self._journal.is_active:
                self._journal.close()
            self.connection_lost.emit()
        else:
            delay_ms = self._backoff_delays_ms[
                min(self._backoff_attempt, len(self._backoff_delays_ms) - 1)
            ]
            self._backoff_attempt += 1
            Debug.info(
                f"Scheduling reconnect in {delay_ms} ms (attempt {self._backoff_attempt})"
            )
            self._retry_timer.start(delay_ms)

    @Slot()
    def _attempt_reconnect(self) -> None:
        """Start a ReconnectWorker to re-establish the serial connection off the main thread."""
        self.retry_connecting.emit()
        Debug.info(f"Reconnect attempt {self._error_count}/{self._max_errors}...")

        # Clean up any previous worker that has already finished
        if self._reconnect_worker is not None:
            self._reconnect_worker.deleteLater()

        worker = ReconnectWorker(self.device_manager, parent=self)
        worker.succeeded.connect(self._on_reconnect_success)
        worker.failed.connect(self._on_reconnect_failed)
        # Auto-cleanup: delete QThread object once it finishes
        worker.finished.connect(worker.deleteLater)
        self._reconnect_worker = worker
        worker.start()

    @Slot()
    def _on_reconnect_success(self) -> None:
        """Called on the main thread when ReconnectWorker reports success."""
        self._reconnect_worker = None
        self._error_count = 0
        self._backoff_attempt = 0
        # Buffers are intentionally preserved — data continuity across gaps.
        # Write a gap marker so consumers can show a discontinuity on plots.
        if self._journal is not None and self._journal.is_active:
            self._journal.append_gap()
        self.poll_timer.start(self.poll_interval)
        self._diag_timer.start(self._diag_interval_ms)
        self.reconnect_succeeded.emit()
        Debug.info("Reconnected successfully")

    @Slot()
    def _on_reconnect_failed(self) -> None:
        """Called on the main thread when ReconnectWorker reports failure."""
        self._reconnect_worker = None
        self._handle_read_error("Reconnect failed")

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

    # ==================== Journal Helpers ====================

    def _start_journal(self) -> None:
        """Create and start a new session journal for the current measurement."""
        firmware = self.device_manager.get_firmware_version()
        config = self.device_manager.get_desired_state().as_config_snapshot()
        self._journal = SessionJournal(
            firmware_version=firmware, config_snapshot=config
        )
        try:
            self._journal.start()
        except OSError as e:
            Debug.error(f"Failed to start session journal: {e}")
            self._journal = None

    # ==================== Cleanup ====================

    def cleanup(self) -> None:
        """Clean up resources."""
        self._retry_timer.stop()
        self._diag_timer.stop()
        self.stop_continuous_reading()

        if self._reconnect_worker is not None and self._reconnect_worker.isRunning():
            self._reconnect_worker.quit()
            self._reconnect_worker.wait(3000)

        if self._is_measuring:
            self.stop_measurement()
        elif self._journal is not None and self._journal.is_active:
            self._journal.close()

        Debug.debug("Data controller cleaned up")
