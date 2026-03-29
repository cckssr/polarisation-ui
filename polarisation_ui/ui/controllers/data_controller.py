"""
Data controller for continuous sensor reading.

Manages threaded data acquisition from encoder devices and
emits signals for UI updates. Separates data collection from UI rendering.
"""

from PySide6.QtCore import QObject, QTimer, Signal, Slot
from typing import Optional

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

    # Error signals
    error_occurred = Signal(str)  # error_message

    # Measurement signals
    measurement_started = Signal()
    measurement_stopped = Signal()

    # Default polling interval (milliseconds)
    DEFAULT_POLL_INTERVAL = 100  # 10 Hz

    # Delay before each reconnection attempt (milliseconds)
    RETRY_DELAY_MS = 3000

    # Signal emitted when a reconnection attempt begins
    retry_connecting = Signal()

    def __init__(
        self, device_manager: GoniometerDeviceManager, parent: Optional[QObject] = None
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

        # State tracking
        self._is_measuring = False
        self._error_count = 0
        self._max_errors = 10  # Stop after this many consecutive errors

        Debug.debug("Data controller initialized")

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
        Debug.info("Continuous reading started")
        return True

    def stop_continuous_reading(self) -> None:
        """Stop continuous sensor polling."""
        if self.poll_timer.isActive():
            self.poll_timer.stop()
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

            # Reset error counter on successful read
            self._error_count = 0

            # Emit updated values
            self.angles_updated.emit(sample_angle, detector_angle)

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
        else:
            self._retry_timer.start(self.RETRY_DELAY_MS)

    @Slot()
    def _attempt_reconnect(self) -> None:
        """Try to resume polling after a connection error."""
        self.retry_connecting.emit()
        Debug.info(f"Reconnect attempt {self._error_count}/{self._max_errors}...")

        try:
            angles = self.device_manager.read_angles()
            if angles is not None:
                self._error_count = 0
                self.poll_timer.start(self.poll_interval)
                sample_angle, detector_angle = angles
                self.angles_updated.emit(sample_angle, detector_angle)
                Debug.info("Reconnected successfully")
            else:
                self._handle_read_error("Failed to read angles")
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

    # ==================== Cleanup ====================

    def cleanup(self) -> None:
        """Clean up resources."""
        self._retry_timer.stop()
        self.stop_continuous_reading()

        if self._is_measuring:
            self.stop_measurement()

        Debug.debug("Data controller cleaned up")
