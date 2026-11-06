"""Owns the main window and rebuilds it when the user switches the profile."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from PySide6.QtCore import QObject, QTimer
from PySide6.QtWidgets import QApplication

from polarisation_ui.infrastructure.config import load_config
from polarisation_ui.infrastructure.logging import Debug
from polarisation_ui.ui.windows.main_window import MainWindow


@dataclass(frozen=True)
class _DeviceState:
    """What was connected in the window that is about to be replaced."""

    simulate: bool
    arduino_port: str | None
    kdc_id: str | None
    pm400_resource: str | None

    @classmethod
    def of(cls, window: MainWindow) -> _DeviceState:
        ctx, ui = window.ctx, window.ui
        kdc_id = ui.kdcPanel.ui.comboDevice.currentData()
        return cls(
            simulate=ctx.simulation is not None,
            arduino_port=ui.arduinoPanel.current_port() if ctx.connection.is_connected else None,
            kdc_id=str(kdc_id) if ctx.kdc.is_connected and kdc_id else None,
            pm400_resource=ctx.pm400.resource if ctx.pm400.is_connected else None,
        )


class Launcher(QObject):
    """Creates the main window for a profile and swaps it for another one on request.

    A switch closes the old window (which stops measurement and workers and releases the
    devices), builds the new one from ``load_config(profile=...)`` and reconnects the devices
    that were connected (on the new simulated bench if the old window simulated). The window
    state (full screen, maximised) is kept. Nothing is switched while a measurement, sweep,
    zero search or calibration worker runs.
    """

    def __init__(
        self,
        profile: str | None = None,
        window_mode: str | None = None,
        simulate: bool = False,
        persist: bool = True,
        overrides: dict[str, Any] | None = None,
        parent: QObject | None = None,
    ) -> None:
        """``profile`` None means ``application.profile``; ``overrides`` are merged last."""
        super().__init__(parent)
        self._profile = profile
        self._window_mode = window_mode
        self._simulate = simulate
        self._persist = persist
        self._overrides = overrides
        self.window: MainWindow | None = None

    def start(self) -> MainWindow:
        """Build and show the first window."""
        return self._open(self._profile, self._window_mode, self._simulate, None)

    def _open(
        self,
        profile: str | None,
        window_mode: str | None,
        simulate: bool,
        reconnect: _DeviceState | None,
    ) -> MainWindow:
        config = load_config(profile=profile, overrides=self._overrides)
        window = MainWindow(config, simulate=simulate, persist=self._persist)
        title = config.text("main_window.self@title")
        window.setWindowTitle(f"{title} {config.get('version', '')}".rstrip())
        window.profile_switch_requested.connect(self._on_switch_requested)
        window.show_initial(window_mode or config.get("application.window_mode", "maximized"))
        self.window = window
        Debug.info(f"Profile {config.profile} active (simulate={simulate})")
        if reconnect is not None:
            self._reconnect(window, reconnect)
        return window

    @staticmethod
    def _reconnect(window: MainWindow, state: _DeviceState) -> None:
        """Connect what the old window had connected; a simulated bench has new ports."""
        ctx, ui = window.ctx, window.ui
        if state.arduino_port is not None:
            port = ui.arduinoPanel.current_port() if state.simulate else state.arduino_port
            ctx.connection.connect_port(port)
        if state.kdc_id is not None:
            kdc_id = ui.kdcPanel.ui.comboDevice.currentData() if state.simulate else state.kdc_id
            ctx.kdc.connect_device(kdc_id)
        if state.pm400_resource is not None:
            resource = (
                ui.detectorPanel.current_pm400_resource()
                if state.simulate
                else state.pm400_resource
            )
            ctx.pm400.connect_resource(resource)

    def _on_switch_requested(self, profile: str) -> None:
        # not inside the slot of the window that is about to be destroyed
        QTimer.singleShot(0, lambda: self.switch_to(profile))

    def switch_to(self, profile: str) -> MainWindow | None:
        """Replace the window by one for ``profile``; returns the window that is now active.

        A no-op (the current window is returned) for the active profile and while the window
        is busy.
        """
        old = self.window
        if old is None or old.config.profile == profile or old.is_busy():
            return old
        state = _DeviceState.of(old)
        mode = (
            "fullscreen" if old.isFullScreen() else "maximized" if old.isMaximized() else "normal"
        )
        app = QApplication.instance()
        if isinstance(app, QApplication):
            app.setQuitOnLastWindowClosed(False)  # closing the old window must not quit
        try:
            old.close()  # saves the layout, stops measurement and workers, releases the devices
            old.deleteLater()
            return self._open(profile, mode, state.simulate, state)
        finally:
            if isinstance(app, QApplication):
                app.setQuitOnLastWindowClosed(True)
