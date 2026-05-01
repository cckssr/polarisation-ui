"""
Qt worker threads for infrastructure-layer blocking operations.

Qt is allowed in this module only. All other infrastructure modules must remain
free of PySide6 imports.
"""

from PySide6.QtCore import QThread, Signal

from polarisation_ui.infrastructure.device_manager import GoniometerDeviceManager
from polarisation_ui.infrastructure.logging import Debug


class ReconnectWorker(QThread):
    """
    Off-main-thread reconnection worker.

    Calls ``device_manager.reconnect_encoders()`` (which contains blocking
    ``sleep()`` calls) on a dedicated QThread so the Qt event loop — and the
    UI — stay responsive during every backoff window.

    Signals are delivered to the main thread via Qt's automatic queued-connection
    mechanism because the receiver objects live on the main thread.
    """

    succeeded = Signal()
    failed = Signal()

    def __init__(
        self,
        device_manager: GoniometerDeviceManager,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._device_manager = device_manager

    def run(self) -> None:
        Debug.info("ReconnectWorker: attempting reconnect on worker thread")
        try:
            success = self._device_manager.reconnect_encoders()
        except Exception as exc:
            Debug.error(f"ReconnectWorker: exception during reconnect: {exc}")
            self.failed.emit()
            return

        if success:
            Debug.info("ReconnectWorker: reconnect succeeded")
            self.succeeded.emit()
        else:
            Debug.info("ReconnectWorker: reconnect failed")
            self.failed.emit()
