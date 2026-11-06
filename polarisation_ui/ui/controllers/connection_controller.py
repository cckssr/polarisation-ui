"""Arduino connection: ports, connect / disconnect, reconnect states, encoder health and zeroing.

Owns the ``GoniometerDeviceManager`` handle and reacts to the ``DataController`` link signals
(read errors, reconnect attempts, permanent loss). It never touches widgets: the window maps
``row_state_changed`` and ``connected_changed`` to the status panel.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable

from PySide6.QtCore import QObject, Signal, Slot

from polarisation_ui.core.detector import is_adc_saturated
from polarisation_ui.infrastructure.config import AppConfig
from polarisation_ui.infrastructure.device_manager import GoniometerDeviceManager
from polarisation_ui.infrastructure.logging import Debug
from polarisation_ui.ui.controllers.data_controller import DataController
from polarisation_ui.ui.controllers.status import (
    LED_BUSY,
    LED_ERROR,
    LED_OFF,
    LED_OK,
    LED_WARN,
    ROW_ARDUINO,
    ROW_DETECTOR,
    ROW_DETECTOR_STAGE,
    ROW_SAMPLE,
    StatusHub,
)


class ConnectionController(QObject):
    """State machine of the Arduino link (encoders + ADC) and its status rows."""

    # row ("arduino"/"sample"/"detector_stage"/"detector"), LED state, text
    row_state_changed = Signal(str, str, str)
    # True once the Arduino answers, False after a disconnect or a permanent loss
    connected_changed = Signal(bool)
    # True while connect_port() is running (the window locks the port selection)
    connecting_changed = Signal(bool)
    # fires after the link is up and polling has started (gain restore, stream sources, ...)
    ready = Signal()
    # "connected" / "reconnecting" / "lost" — forwarded to the experiment tabs
    link_state_changed = Signal(str)
    # reconnect attempts exhausted: the window may offer the partial data export
    lost = Signal()
    ports_changed = Signal(list)  # list[str]
    zero_failed = Signal(str, str)  # dialog title, text
    persist_requested = Signal()

    def __init__(
        self,
        config: AppConfig,
        device_manager: GoniometerDeviceManager,
        data: DataController,
        status: StatusHub,
        fixed_ports: Iterable[str] | None = None,
        parent: QObject | None = None,
    ) -> None:
        """Wire the data controller's link signals; ``fixed_ports`` replaces the serial scan."""
        super().__init__(parent)
        self._cfg = config
        self.device_manager = device_manager
        self._data = data
        self._status = status
        self._fixed_ports = list(fixed_ports) if fixed_ports is not None else None
        self._connected = False
        self._adc_saturated = False
        self._sensor_a_ok = True
        self._sensor_b_ok = True

        data.intensity_updated.connect(self._on_intensity)
        data.poll_rate_updated.connect(self._on_poll_rate)
        data.diagnostics_updated.connect(self._on_diagnostics)
        data.error_occurred.connect(self._on_data_error)
        data.retry_connecting.connect(self._on_retry)
        data.reconnect_succeeded.connect(self._on_reconnected)
        data.connection_lost.connect(self._on_lost)

    # ---- helpers -------------------------------------------------------------------------
    def _t(self, key: str, **fmt: object) -> str:
        return self._cfg.text(f"mainwindow.{key}", **fmt)

    def _m(self, key: str, **fmt: object) -> str:
        return self._cfg.message(f"connection.{key}", **fmt)

    def _row(self, row: str, led: str, key: str, **fmt: object) -> None:
        self.row_state_changed.emit(row, led, self._t(key, **fmt))

    @property
    def is_connected(self) -> bool:
        """True while the Arduino link is up."""
        return self._connected

    @property
    def ports_missing_text(self) -> str:
        """Placeholder shown in the port selector when no port was found."""
        return self._t("ports_missing")

    # ---- ports ---------------------------------------------------------------------------
    def list_ports(self) -> list[str]:
        """Serial ports (plus registered mock ports), or the fixed simulation port."""
        if self._fixed_ports is not None:
            return list(self._fixed_ports)
        return self.device_manager.list_available_ports()

    @Slot()
    def refresh_ports(self) -> None:
        """Rescan the ports and publish them."""
        ports = self.list_ports()
        self.ports_changed.emit(ports)
        Debug.info(f"Available serial ports: {ports}")

    def publish_state(self) -> None:
        """Emit the initial (disconnected) state of every row."""
        self.refresh_ports()
        self._row(ROW_ARDUINO, LED_OFF, "status_arduino_idle")
        self._status.info(self._m("please_connect"))

    # ---- connect / disconnect ------------------------------------------------------------
    def connect_port(self, port: str) -> bool:
        """Connect to the Arduino on ``port``; returns True on success."""
        if not port or port == self.ports_missing_text:
            self._row(ROW_ARDUINO, LED_OFF, "status_arduino_idle")
            return False

        self._row(ROW_ARDUINO, LED_BUSY, "status_connecting")
        self.connecting_changed.emit(True)
        success = self.device_manager.connect_encoders(port=port)
        if not success:
            error = self.device_manager.get_encoder_status().error_message or self._m(
                "connect_failed_default"
            )
            self._row(ROW_ARDUINO, LED_ERROR, "status_error", error=error)
            self.connecting_changed.emit(False)
            self._status.error(self._m("connect_failed", error=error))
            Debug.error(f"Arduino connection failed: {error}")
            return False

        self._row(ROW_ARDUINO, LED_OK, "status_connected")
        self._connected = True
        self.connected_changed.emit(True)
        self._row(ROW_SAMPLE, LED_OK, "status_encoder_a")
        self._row(ROW_DETECTOR_STAGE, LED_OK, "status_encoder_b")
        self._row(ROW_DETECTOR, LED_OK, "status_adc")
        self._sensor_a_ok = True
        self._sensor_b_ok = True
        self._adc_saturated = False
        self._data.start_continuous_reading()
        self.link_state_changed.emit("connected")
        self.ready.emit()
        self._status.success(self._m("connected", port=port))
        Debug.info(f"Arduino connected on {port}")
        return True

    @Slot()
    def disconnect_port(self) -> None:
        """User-initiated disconnect."""
        self._data.stop_continuous_reading()
        self.device_manager.disconnect_all()
        self._reset()
        self.link_state_changed.emit("lost")
        self._status.info(self._m("disconnected"))
        Debug.info("Arduino disconnected by user")

    def _reset(self) -> None:
        """Back to the disconnected state (shared by the user path and the permanent loss)."""
        self._connected = False
        self._adc_saturated = False
        self.connected_changed.emit(False)
        self.connecting_changed.emit(False)
        self._row(ROW_ARDUINO, LED_OFF, "status_disconnected")
        self._row(ROW_SAMPLE, LED_ERROR, "status_no_signal")
        self._row(ROW_DETECTOR_STAGE, LED_ERROR, "status_no_signal")
        self._row(ROW_DETECTOR, LED_ERROR, "status_no_signal")

    def set_stream_sources(self, sources: set[str]) -> bool:
        """Configure CONF:SRC; a no-op (False) while disconnected."""
        if not self._connected:
            return False
        return self.device_manager.set_stream_sources(sources)

    def shutdown(self) -> None:
        """Stop polling and close the serial link (window close)."""
        self._data.cleanup()
        self.device_manager.disconnect_all()
        self._connected = False

    # ---- data-controller link signals ----------------------------------------------------
    @Slot(float)
    def _on_intensity(self, voltage: float) -> None:
        """Flag ADC saturation on the detector row (only on a change, to avoid LED flicker)."""
        if voltage != voltage:  # NaN
            return
        saturated = is_adc_saturated(voltage)
        if saturated != self._adc_saturated:
            self._adc_saturated = saturated
            if saturated:
                self._row(ROW_DETECTOR, LED_WARN, "status_saturated")
            else:
                self._row(ROW_DETECTOR, LED_OK, "status_adc")

    @Slot(float)
    def _on_poll_rate(self, hz: float) -> None:
        """Show the measured poll rate in the detector row while the ADC is healthy."""
        if not self._adc_saturated and self._connected:
            self.row_state_changed.emit(ROW_DETECTOR, LED_OK, self._t("status_adc_rate", hz=hz))

    @Slot(bool, str, bool, str)
    def _on_diagnostics(self, a_ok: bool, a_desc: str, b_ok: bool, b_desc: str) -> None:
        """Per-encoder diagnostics: update each LED independently, flush buffers on recovery."""
        prev_a_ok = self._sensor_a_ok
        prev_b_ok = self._sensor_b_ok
        self._encoder_health(
            a_ok, prev_a_ok, ROW_SAMPLE, "status_encoder_a", self._data.clear_sample_buffer
        )
        self._sensor_a_ok = a_ok
        self._encoder_health(
            b_ok, prev_b_ok, ROW_DETECTOR_STAGE, "status_encoder_b", self._data.clear_det_buffer
        )
        self._sensor_b_ok = b_ok

        # Status bar: only when something is wrong or both just recovered
        if not a_ok or not b_ok:
            parts = [d for ok, d in ((a_ok, a_desc), (b_ok, b_desc)) if not ok]
            self._status.warning(self._m("sensor_diag", faults=" | ".join(parts)))
        elif not prev_a_ok and not prev_b_ok:
            self._status.success(self._m("sensor_diag_ok"))

    def _encoder_health(
        self, ok: bool, prev_ok: bool, row: str, ok_key: str, clear_fn: Callable[[], None]
    ) -> None:
        if ok:
            if not prev_ok:
                clear_fn()
                self._row(row, LED_OK, ok_key)
        else:
            self._row(row, LED_WARN, "status_sensor_error")

    @Slot(str)
    def _on_data_error(self, error_msg: str) -> None:
        """First read error: mark all three sensor rows, report in the status bar."""
        Debug.error(f"Data acquisition error: {error_msg}")
        for row in (ROW_SAMPLE, ROW_DETECTOR_STAGE, ROW_DETECTOR):
            self._row(row, LED_WARN, "status_connection_error")
        self._status.error(self._m("read_error", error=error_msg))

    @Slot(int, float)
    def _on_retry(self, _attempt: int, _delay_s: float) -> None:
        self._status.warning(self._m("reconnecting"))
        self.link_state_changed.emit("reconnecting")

    @Slot()
    def _on_reconnected(self) -> None:
        """Serial link re-established: restore all status rows."""
        self._row(ROW_ARDUINO, LED_OK, "status_connected")
        self._row(ROW_SAMPLE, LED_OK, "status_encoder_a")
        self._row(ROW_DETECTOR_STAGE, LED_OK, "status_encoder_b")
        self._row(ROW_DETECTOR, LED_OK, "status_adc")
        self._adc_saturated = False
        self._status.success(self._m("reconnected"))
        self.link_state_changed.emit("connected")
        Debug.info("Reconnect: status restored")

    @Slot()
    def _on_lost(self) -> None:
        """Reconnect attempts exhausted: show the disconnected state."""
        self._reset()
        self._status.error(self._m("lost"))
        Debug.error("Connection permanently lost; user must reconnect manually")
        self.link_state_changed.emit("lost")
        self.lost.emit()

    # ---- encoder zeroing -----------------------------------------------------------------
    @Slot()
    def zero_sample(self) -> bool:
        """Zero the sample encoder at its current position."""
        if self.device_manager.zero_sample_encoder():
            self._status.success(self._m("zero_sample_ok"))
            Debug.info("Sample encoder zeroed")
            return True
        self._status.error(self._m("zero_sample_failed"))
        self.zero_failed.emit(self._m("zero_failed_title"), self._m("zero_sample_failed_text"))
        return False

    @Slot()
    def zero_detector(self) -> bool:
        """Zero the detector encoder at its current position (display 0°)."""
        return self._zero_detector(0.0, "zero_detector")

    @Slot()
    def zero_detector_at_180(self) -> bool:
        """Zero the detector encoder and apply a host-side +180° offset (display 180°)."""
        return self._zero_detector(180.0, "zero_detector_180")

    def _zero_detector(self, offset_deg: float, key: str) -> bool:
        if self.device_manager.zero_detector_encoder():
            self._data.set_detector_offset(offset_deg)
            self.persist_requested.emit()
            self._status.success(self._m(f"{key}_ok"))
            Debug.info(f"Detector encoder zeroed (offset={offset_deg:g}°)")
            return True
        self._status.error(self._m(f"{key}_failed"))
        self.zero_failed.emit(self._m("zero_failed_title"), self._m(f"{key}_failed_text"))
        return False
