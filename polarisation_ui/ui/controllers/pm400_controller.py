"""PM400 power meter: connection, zeroing and wavelength.

While connected the PM400 takes precedence over the PD-TIA as the active detector — the hand-over
itself is done by ``DataController.set_pm400`` / ``clear_pm400``. The controller never touches
widgets; the window mirrors its signals.
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QObject, Signal, Slot

from polarisation_ui.core.exceptions import PM400Error
from polarisation_ui.infrastructure.config import AppConfig
from polarisation_ui.infrastructure.devices.pm400 import PM400PowerMeter
from polarisation_ui.infrastructure.logging import Debug
from polarisation_ui.infrastructure.modules import ModuleRegistry
from polarisation_ui.infrastructure.modules.pm400_adapter import PM400ModuleAdapter
from polarisation_ui.ui.controllers.data_controller import DataController
from polarisation_ui.ui.controllers.status import LED_BUSY, LED_ERROR, LED_OFF, LED_OK, StatusHub

DEFAULT_WAVELENGTH_NM = 633.0


class PM400Controller(QObject):
    """State and actions of the PM400 power meter."""

    state_changed = Signal(str, str)  # LED state, text
    connected_changed = Signal(bool)
    resources_changed = Signal(list)  # list[str] of VISA resources found
    resource_selected = Signal(str)  # a restored resource that is currently listed
    wavelength_changed = Signal(float)  # wavelength changed from outside the spin box
    modules_changed = Signal()  # the ModuleRegistry changed: tabs must be re-evaluated
    notice = Signal(str, str)  # dialog title, text
    persist_requested = Signal()

    def __init__(
        self,
        config: AppConfig,
        data: DataController,
        status: StatusHub,
        pm400: PM400PowerMeter | None = None,
        list_resources: Callable[[], list[str]] = PM400PowerMeter.list_resources,
        preferred_resource: str = "",
        wavelength_nm: float = DEFAULT_WAVELENGTH_NM,
        parent: QObject | None = None,
    ) -> None:
        """Take the meter object (real or mock), the resource scan and the remembered settings."""
        super().__init__(parent)
        self._cfg = config
        self._data = data
        self._status = status
        self.pm400 = pm400 if pm400 is not None else PM400PowerMeter()
        self._list_resources = list_resources
        self.preferred_resource = preferred_resource
        self._resource = preferred_resource
        self._resources: list[str] = []
        self._wavelength_nm = wavelength_nm
        self._registered = False
        data.pm400_connection_lost.connect(self._on_connection_lost)

    # ---- helpers -------------------------------------------------------------------------
    def _t(self, key: str, **fmt: object) -> str:
        return self._cfg.text(f"main_window.{key}", **fmt)

    def _m(self, key: str, **fmt: object) -> str:
        return self._cfg.message(f"pm400.{key}", **fmt)

    @property
    def is_connected(self) -> bool:
        """True while the meter is connected."""
        return self.pm400.is_connected()

    @property
    def resource(self) -> str:
        """The VISA resource currently selected (or last connected)."""
        return self._resource

    @property
    def wavelength_nm(self) -> float:
        """Sensor wavelength in nm used for the spectral correction."""
        return self._wavelength_nm

    def publish_state(self) -> None:
        """Emit the initial (disconnected) state."""
        self.refresh_resources()
        self.state_changed.emit(LED_OFF, self._t("status_not_connected"))
        self.wavelength_changed.emit(self._wavelength_nm)

    # ---- resources / connection ----------------------------------------------------------
    @Slot()
    def refresh_resources(self) -> None:
        """Rescan for VISA resources."""
        self._resources = self._list_resources()
        self.resources_changed.emit(self._resources)
        Debug.info(f"PM400 VISA resources found: {self._resources}")

    def set_resource(self, resource: str) -> None:
        """Remember the resource shown in the selector."""
        self._resource = resource.strip()

    def select_resource(self, resource: str) -> None:
        """Select a remembered resource if it is currently listed (session restore)."""
        if resource in self._resources:
            self._resource = resource
            self.resource_selected.emit(resource)

    def connect_resource(self, resource: str) -> bool:
        """Connect to the PM400 at ``resource`` and make it the active detector."""
        resource = resource.strip()
        if not resource:
            self.notice.emit(self._m("title"), self._m("no_resource"))
            return False
        self.state_changed.emit(LED_BUSY, self._t("status_connecting_dots"))
        try:
            self.pm400.connect(resource)
            self.pm400.set_wavelength_nm(self._wavelength_nm)
        except PM400Error as exc:
            self.state_changed.emit(LED_ERROR, self._t("status_error", error=exc))
            self._status.error(self._m("connect_error", error=exc))
            return False
        self._resource = resource
        ModuleRegistry.register(PM400ModuleAdapter(self.pm400))
        self._registered = True
        self.modules_changed.emit()
        info = self.pm400.sensor_info()
        sensor = " | ".join(str(x) for x in info[:2]) if info else self._t("status_connected")
        self.state_changed.emit(LED_OK, sensor)
        self.connected_changed.emit(True)
        # Precedence takes effect immediately: every Frame now reports PM400 power.
        self._data.set_pm400(self.pm400)
        self.persist_requested.emit()
        self._status.success(self._m("connected", resource=resource))
        Debug.info(f"PM400 connected: {resource}")
        return True

    @Slot()
    def disconnect_device(self) -> None:
        """User-initiated disconnect (falls back to the PD-TIA)."""
        self._data.clear_pm400()
        self._teardown()
        self._status.info(self._m("disconnected"))
        Debug.info("PM400 disconnected by user")

    def _teardown(self) -> None:
        """Back to the disconnected state; leaves the DataController alone (see callers)."""
        self.pm400.disconnect()
        ModuleRegistry.unregister("pm400")
        self._registered = False
        self.modules_changed.emit()
        self.state_changed.emit(LED_OFF, self._t("status_not_connected"))
        self.connected_changed.emit(False)

    @Slot(str)
    def _on_connection_lost(self, msg: str) -> None:
        """The poll worker gave up after repeated read failures — treat as unplugged.

        The DataController has already fallen back to the PD-TIA and stopped a running
        measurement before emitting its signal.
        """
        self._teardown()
        self._status.error(self._m("lost", error=msg))
        Debug.error(f"PM400 connection lost: {msg}")

    # ---- actions -------------------------------------------------------------------------
    @Slot()
    def zero(self) -> None:
        """Start the meter's dark-current zero adjustment."""
        if not self.pm400.is_connected():
            return
        try:
            self.pm400.zero()
            self._status.info(self._m("zero_started"))
        except PM400Error as exc:
            self._status.error(self._m("error", error=exc))

    @Slot(float)
    def set_wavelength(self, nm: float) -> None:
        """Store the wavelength and push it to a connected meter."""
        changed = nm != self._wavelength_nm
        self._wavelength_nm = nm
        if self.pm400.is_connected():
            try:
                self.pm400.set_wavelength_nm(nm)
            except PM400Error as exc:
                self._status.error(self._m("wavelength_failed", error=exc))
        if changed:
            self.wavelength_changed.emit(nm)
        self.persist_requested.emit()

    def shutdown(self) -> None:
        """Release the meter (window close); the DataController stops its poll worker itself."""
        if self.pm400.is_connected():
            self.pm400.disconnect()
        if self._registered:
            ModuleRegistry.unregister("pm400")
            self._registered = False
