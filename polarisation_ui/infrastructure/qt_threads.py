"""!/usr/bin/env python
Qt threading module for background measurement collection.

This module provides Qt thread implementations for asynchronous data collection
and measurement processing. Threads communicate with the main UI via Qt signals,
ensuring thread-safe updates to the user interface while keeping measurement
logic separated from UI code.

Features:
    - Generic measurement collection in background threads
    - Signal-based communication between threads and UI
    - Data validation and filtering with pluggable validators
    - Automatic error handling and connection monitoring
    - Thread-safe resource cleanup

Classes:
    MeasurementCollectorThread: Generic thread for collecting measurements
                                and emitting them to the UI.

Usage:
    Create and start a measurement collection thread:

    >>> from PySide6.QtCore import QThread
    >>> collector = MeasurementCollectorThread(data_source)
    >>> collector.measurement_collected.connect(on_measurement)
    >>> collector.start()
    >>> # When done:
    >>> collector.stop()
    >>> collector.wait()

    The thread emits measurement_collected signal with a MeasurementPoint
    whenever a complete measurement is acquired and validated.

Dependencies:
    - PySide6 (Qt framework)
    - polarisation_ui.core.models (MeasurementPoint dataclass)
"""

import time
from typing import Optional, Callable, Any
from datetime import datetime
from PySide6.QtCore import QThread, Signal  # pylint: disable=no-name-in-module

from polarisation_ui.core.models import MeasurementPoint
from .logging import Debug


class MeasurementCollectorThread(QThread):
    """
    Generic measurement collection thread for asynchronous data acquisition.

    Collects measurements from a data source and emits them via Qt signals.
    Validates measurements using pluggable validators before emission.
    Runs independently from the main UI thread, allowing long-running
    measurements without blocking user interaction.
    """

    # Signals emitted by this thread
    measurement_collected = Signal(object)  # Emits MeasurementPoint
    error_occurred = Signal(str)  # Emits error message
    collection_started = Signal()  # Emitted when collection begins
    collection_stopped = Signal()  # Emitted when collection ends

    def __init__(
        self,
        data_source: Any,
        validator: Optional[Callable[[MeasurementPoint], bool]] = None,
        auto_timestamp: bool = True,
    ) -> None:
        """
        Initialize the measurement collector thread.

        The thread collects measurements from a data source and validates them
        before emission. Validators are optional and can be swapped at runtime.

        Args:
            data_source: Object with methods to read encoder and photodiode data.
                        Expected to have: read_sample_angle(), read_detector_angle(),
                        read_photodiode_voltage() methods or similar.
            validator: Optional callable that validates MeasurementPoint objects.
                      Returns True if valid, False otherwise. Default None (no validation).
            auto_timestamp: If True, automatically set measurement timestamp.
                           Default True.
        """
        super().__init__()
        self.data_source = data_source
        self.validator = validator
        self.auto_timestamp = auto_timestamp
        self._running = False
        self._measurement_count = 0
        self._error_count = 0

    def validate_measurement(self, measurement: MeasurementPoint) -> bool:
        """
        Validate a measurement using the configured validator.

        Args:
            measurement: MeasurementPoint to validate.

        Returns:
            bool: True if measurement passes validation or no validator configured,
                  False otherwise.
        """
        if self.validator is None:
            return True

        try:
            is_valid = self.validator(measurement)
            if not is_valid:
                Debug.debug(f"Measurement failed validation: {measurement}")
            return is_valid
        except Exception as e:
            Debug.error(f"Error in measurement validator: {e}", exc_info=True)
            return False

    def collect_measurement(self) -> Optional[MeasurementPoint]:
        """
        Collect a single measurement from the data source.

        This method must be overridden by subclasses to implement
        specific data collection logic.

        Returns:
            MeasurementPoint if successfully collected, None otherwise.
        """
        # This is a template method that subclasses override
        raise NotImplementedError("Subclasses must implement collect_measurement()")

    def run(self):
        """
        Main thread loop for continuous measurement collection.

        Acquires measurements, validates them, and emits valid measurements.
        """
        Debug.info("Measurement collection thread started")
        self._running = True
        self._measurement_count = 0
        self._error_count = 0

        self.collection_started.emit()

        try:
            while self._running:
                try:
                    # Collect a measurement
                    measurement = self.collect_measurement()

                    if measurement is None:
                        # No measurement available, wait briefly
                        time.sleep(0.01)
                        continue

                    # Set timestamp if configured
                    if self.auto_timestamp and measurement.timestamp is None:
                        measurement.timestamp = datetime.now()

                    # Validate measurement
                    if not self.validate_measurement(measurement):
                        self._error_count += 1
                        self.error_occurred.emit(
                            f"Measurement validation failed (error #{self._error_count})"
                        )
                        continue

                    # Emit valid measurement
                    self._measurement_count += 1
                    Debug.debug(f"Collected measurement #{self._measurement_count}")
                    self.measurement_collected.emit(measurement)

                except Exception as e:
                    Debug.error(f"Error collecting measurement: {e}", exc_info=True)
                    self._error_count += 1
                    self.error_occurred.emit(str(e))
                    time.sleep(0.1)

        finally:
            Debug.info(
                f"Measurement collection thread stopped "
                f"(collected: {self._measurement_count}, errors: {self._error_count})"
            )
            self.collection_stopped.emit()

    def stop(self):
        """
        Stop the measurement collection thread.

        Gracefully stops the thread and waits for it to finish.
        """
        self._running = False
        self.requestInterruption()
        Debug.info("Stopping measurement collection thread")

        # Wait for thread to finish (max 2 seconds)
        if not self.wait(2000):
            Debug.warning("Thread did not stop within timeout, terminating...")
            self.terminate()
            self.wait()

    def set_validator(
        self, validator: Optional[Callable[[MeasurementPoint], bool]]
    ) -> None:
        """
        Set or replace the measurement validator.

        Args:
            validator: Callable that validates MeasurementPoint, or None to disable validation.
        """
        self.validator = validator
        Debug.debug(f"Validator updated: {validator.__name__ if validator else 'None'}")
