"""KDC101 polariser stage: connection, position poll, homing and extinction-angle zero-find.

Owns the stage object, its 250 ms position timer and the home / zero-find workers, and registers
the stage in the ``ModuleRegistry`` so that tabs requiring ``kdc101`` appear. It never touches
widgets; the window mirrors its signals.
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QObject, QTimer, Signal, Slot

from polarisation_ui.core.exceptions import KDC101Error
from polarisation_ui.core.formatting import fmt_angle
from polarisation_ui.core.models import Frame
from polarisation_ui.infrastructure.config import AppConfig
from polarisation_ui.infrastructure.devices.kdc101_polariser import KDC101Polariser
from polarisation_ui.infrastructure.logging import Debug
from polarisation_ui.infrastructure.modules import ModuleRegistry
from polarisation_ui.infrastructure.modules.kdc101_adapter import KDC101ModuleAdapter
from polarisation_ui.infrastructure.qt_threads import KDC101HomeWorker, KDCZeroFindWorker
from polarisation_ui.ui.controllers.data_controller import DataController
from polarisation_ui.ui.controllers.detector_controller import DetectorController
from polarisation_ui.ui.controllers.status import LED_BUSY, LED_ERROR, LED_OFF, LED_OK, StatusHub

# Consecutive failed position reads (at 250 ms/poll, ~1 s) before the stage counts as unplugged
# rather than a transient communication glitch.
DISCONNECT_THRESHOLD = 4
POSITION_POLL_MS = 250


class KdcController(QObject):
    """State and actions of the KDC101 polariser stage."""

    state_changed = Signal(str, str)  # LED state, text
    connected_changed = Signal(bool)
    # connect, home, zero, reset-offset buttons enabled
    controls_changed = Signal(bool, bool, bool, bool)
    position_changed = Signal(object)  # float degrees, or None when unknown
    offset_changed = Signal(float)  # logical-zero offset in degrees (0.0 = none)
    devices_changed = Signal(list)  # list[tuple[str, str]] (connection id, description)
    modules_changed = Signal()  # the ModuleRegistry changed: tabs must be re-evaluated
    notice = Signal(str, str)  # dialog title, text
    persist_requested = Signal()

    def __init__(
        self,
        config: AppConfig,
        data: DataController,
        detector: DetectorController,
        status: StatusHub,
        kdc: KDC101Polariser | None = None,
        list_devices: Callable[[], list[tuple[str, str]]] = KDC101Polariser.list_devices,
        parent: QObject | None = None,
    ) -> None:
        """Take the stage object (a real or mock polariser) and the device-listing function."""
        super().__init__(parent)
        self._cfg = config
        self._data = data
        self._detector = detector
        self._status = status
        self.kdc = kdc if kdc is not None else KDC101Polariser()
        self._list_devices = list_devices

        self._home_worker: KDC101HomeWorker | None = None
        self._zero_worker: KDCZeroFindWorker | None = None
        self._read_failures = 0
        self._registered = False
        self._connect_enabled = True
        self._actions_enabled = (False, False, False)  # home, zero, reset
        # Most recent Frame — the thread-safe read used by the zero-find worker.
        self._last_frame: Frame | None = None
        # Gain stage to restore after the zero-find if it fails partway through.
        self._gain_before_zero_find = 0

        self._position_timer = QTimer(self)
        self._position_timer.setInterval(POSITION_POLL_MS)
        self._position_timer.timeout.connect(self.poll_position)
        data.frame_ready.connect(self._on_frame)

    # ---- helpers -------------------------------------------------------------------------
    def _t(self, key: str, **fmt: object) -> str:
        return self._cfg.text(f"main_window.{key}", **fmt)

    def _m(self, key: str, **fmt: object) -> str:
        return self._cfg.message(f"kdc.{key}", **fmt)

    def _set_controls(
        self,
        connect: bool | None = None,
        home: bool | None = None,
        zero: bool | None = None,
        reset: bool | None = None,
    ) -> None:
        if connect is not None:
            self._connect_enabled = connect
        h, z, r = self._actions_enabled
        self._actions_enabled = (
            h if home is None else home,
            z if zero is None else zero,
            r if reset is None else reset,
        )
        self.controls_changed.emit(self._connect_enabled, *self._actions_enabled)

    @property
    def is_connected(self) -> bool:
        """True while the stage is connected."""
        return self.kdc.is_connected()

    @property
    def zero_offset_deg(self) -> float:
        """Host-side logical-zero offset of the stage in degrees."""
        return self.kdc.zero_offset_deg

    @property
    def zero_find_running(self) -> bool:
        """True while the extinction-angle search is running."""
        return self._zero_worker is not None

    def publish_state(self) -> None:
        """Emit the initial (disconnected) state."""
        self.refresh_devices()
        self.state_changed.emit(LED_OFF, self._t("status_not_connected"))
        self._set_controls(connect=True, home=False, zero=False, reset=False)
        self.position_changed.emit(None)
        self.offset_changed.emit(self.kdc.zero_offset_deg)

    # ---- devices / connection ------------------------------------------------------------
    @Slot()
    def refresh_devices(self) -> None:
        """Rescan for KDC101 devices."""
        devices = self._list_devices()
        self.devices_changed.emit(devices)
        Debug.info(f"KDC101 devices found: {devices}")

    def connect_device(self, conn_id: str | None = None) -> bool:
        """Connect to the stage ``conn_id`` (None = nothing selected)."""
        if not conn_id:
            self.notice.emit(self._m("title"), self._m("no_device"))
            return False
        self.state_changed.emit(LED_BUSY, self._t("status_connecting_dots"))
        try:
            self.kdc.connect(conn_id)
        except KDC101Error as exc:
            self.state_changed.emit(LED_ERROR, self._t("status_error", error=exc))
            self._status.error(self._m("connect_error", error=exc))
            return False
        ModuleRegistry.register(KDC101ModuleAdapter(self.kdc))
        self._registered = True
        self.modules_changed.emit()
        self.state_changed.emit(LED_OK, self._t("status_connected_named", id=conn_id))
        self.connected_changed.emit(True)
        self._set_controls(home=True, zero=True, reset=True)
        self.offset_changed.emit(self.kdc.zero_offset_deg)
        self._position_timer.start()
        self._status.success(self._m("connected", id=conn_id))
        Debug.info(f"KDC101 connected: {conn_id}")
        return True

    @Slot()
    def disconnect_device(self) -> None:
        """User-initiated disconnect."""
        self._teardown()
        self._status.info(self._m("disconnected"))

    def _teardown(self) -> None:
        """Back to the disconnected state (user disconnect and auto-detected unplug)."""
        if self._zero_worker is not None:
            self._zero_worker.abort()
        self._position_timer.stop()
        self._read_failures = 0
        self.kdc.disconnect()
        ModuleRegistry.unregister("kdc101")
        self._registered = False
        self.modules_changed.emit()
        self.state_changed.emit(LED_OFF, self._t("status_not_connected"))
        self.connected_changed.emit(False)
        self._set_controls(home=False, zero=False, reset=False)
        self.position_changed.emit(None)

    def _on_connection_lost(self) -> None:
        Debug.warning(
            "KDC101: connection lost after repeated read failures — treating as disconnected"
        )
        self._teardown()
        self._status.error(self._m("lost"))

    @Slot()
    def poll_position(self) -> None:
        """Read the position without blocking; repeated failures mean the stage was unplugged.

        ``None`` means the stage was busy serving a sweep or home worker, not a failure.
        """
        try:
            pos = self.kdc.get_position_deg_nowait()
        except KDC101Error:
            self._read_failures += 1
            if self._read_failures >= DISCONNECT_THRESHOLD:
                self._on_connection_lost()
            return
        self._read_failures = 0
        if pos is not None:
            self.position_changed.emit(pos)

    # ---- homing --------------------------------------------------------------------------
    @Slot()
    def home(self) -> None:
        """Home the stage off the main thread."""
        if not self.kdc.is_connected():
            return
        self._set_controls(connect=False, home=False)
        self._home_worker = KDC101HomeWorker(self.kdc, parent=self)
        self._home_worker.done.connect(self._on_home_done)
        self._home_worker.error.connect(self._on_home_error)
        self._home_worker.start()
        self._status.info(self._m("home_running"))

    @Slot()
    def _on_home_done(self) -> None:
        self._set_controls(connect=True, home=True)
        self._status.success(self._m("home_done"))

    @Slot(str)
    def _on_home_error(self, msg: str) -> None:
        self._set_controls(connect=True, home=True)
        self._status.error(self._m("home_failed", error=msg))

    # ---- zero offset ---------------------------------------------------------------------
    @Slot(object)
    def _on_frame(self, frame: Frame) -> None:
        self._last_frame = frame

    def set_zero_offset(self, offset_deg: float) -> None:
        """Set the logical-zero offset (session restore, zero-find result, reset)."""
        self.kdc.set_zero_offset_deg(offset_deg)
        self.offset_changed.emit(self.kdc.zero_offset_deg)

    @Slot()
    def reset_offset(self) -> None:
        """Reset the logical-zero offset to 0°."""
        self.set_zero_offset(0.0)
        self.persist_requested.emit()
        self._status.info(self._m("offset_reset"))

    @Slot()
    def start_zero_find(self) -> None:
        """Start the two-stage (coarse gain 1 / fine gain 3) extinction-angle search."""
        if not self.kdc.is_connected() or self._zero_worker is not None:
            return
        if not self._data.is_reading():
            self._status.error(self._m("zero_no_data"))
            return
        self._gain_before_zero_find = self._data.pdtia_gain or 1
        self._detector.gain_auto_suspended = True
        self._set_controls(connect=False, home=False, zero=False, reset=False)
        worker = KDCZeroFindWorker(kdc=self.kdc, read_latest=lambda: self._last_frame, parent=self)
        self._zero_worker = worker
        worker.gain_requested.connect(self._on_zero_gain_requested)
        worker.finished.connect(self._on_zero_finished)
        worker.failed.connect(self._on_zero_failed)
        worker.log.connect(self._status.info)
        worker.start()
        self._status.info(self._m("zero_running"))

    @Slot(int)
    def _on_zero_gain_requested(self, stage: int) -> None:
        """Apply a PD-TIA gain change requested by the worker (main thread only)."""
        self._detector.apply_gain(stage)

    @Slot(float)
    def _on_zero_finished(self, offset_deg: float) -> None:
        self._zero_worker = None
        self._detector.gain_auto_suspended = False
        self.set_zero_offset(offset_deg)
        self._set_controls(connect=True, home=True, zero=True, reset=True)
        self.persist_requested.emit()
        self._status.success(self._m("zero_done", offset=fmt_angle(offset_deg)))

    @Slot(str)
    def _on_zero_failed(self, msg: str) -> None:
        self._zero_worker = None
        self._detector.gain_auto_suspended = False
        # Best-effort: put the gain back the way the user had it before tuning.
        self._detector.apply_gain(self._gain_before_zero_find)
        self._set_controls(connect=True, home=True, zero=True, reset=True)
        self._status.error(self._m("zero_failed", error=msg))

    def shutdown(self) -> None:
        """Stop the poll timer and workers, release the stage (window close)."""
        self._position_timer.stop()
        for worker in (self._zero_worker, self._home_worker):
            if worker is not None and worker.isRunning():
                if worker is self._zero_worker:
                    worker.abort()
                worker.wait(3000)
        if self.kdc.is_connected():
            self.kdc.disconnect()
        if self._registered:
            ModuleRegistry.unregister("kdc101")
            self._registered = False
