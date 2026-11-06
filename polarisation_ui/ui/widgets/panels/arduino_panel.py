"""Arduino connection panel: serial port, connect / disconnect, link status."""

from __future__ import annotations

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QGroupBox, QWidget

from polarisation_ui.infrastructure.config import AppConfig, default_config
from polarisation_ui.pyqt.ui_arduino_panel import Ui_ArduinoPanel
from polarisation_ui.ui.common.status_led import set_led_state
from polarisation_ui.ui.i18n import apply_strings


class ArduinoPanel(QGroupBox):
    """Port selection and connect button; the owner connects the intent signals to a controller."""

    connect_requested = Signal(str)  # the selected port
    disconnect_requested = Signal()
    refresh_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build the form; texts come from :meth:`apply_config` (the form carries the defaults)."""
        super().__init__(parent)
        self.ui = Ui_ArduinoPanel()
        self.ui.setupUi(self)
        self._config: AppConfig = default_config()
        self._connected = False
        self.ui.buttonRefreshPorts.clicked.connect(self.refresh_requested)
        self.ui.buttonConnect.clicked.connect(self._on_connect_clicked)

    def apply_config(self, config: AppConfig) -> None:
        """Apply the ``ui.arduino_panel`` strings."""
        self._config = config
        apply_strings(self, config.section("ui").get("arduino_panel", {}))
        self.set_connected(self._connected)

    # ---- setters (driven by the controller) -----------------------------------------------
    @Slot(list)
    def set_ports(self, ports: list[str], missing_text: str = "") -> None:
        """Replace the port list; ``missing_text`` is shown as the only entry when it is empty."""
        self.ui.comboPort.clear()
        self.ui.comboPort.addItems(ports)
        if not ports:
            self.ui.comboPort.addItem(missing_text)

    def set_state(self, led: str, text: str) -> None:
        """Show the link status (``led`` is a controller LED state such as ``ok`` or ``off``)."""
        set_led_state(self.ui.ledStatus, self.ui.valueStatus, text, led)

    @Slot(bool)
    def set_connected(self, connected: bool) -> None:
        """The button disconnects while connected and connects otherwise."""
        self._connected = connected
        key = "text_disconnect" if connected else "text_connect"
        self.ui.buttonConnect.setText(self._config.text(f"arduino_panel.{key}"))

    @Slot(bool)
    def set_connecting(self, connecting: bool) -> None:
        """No port change while a connect attempt runs."""
        self.ui.comboPort.setEnabled(not connecting)
        self.ui.buttonRefreshPorts.setEnabled(not connecting)

    # ---- internals ------------------------------------------------------------------------
    def current_port(self) -> str:
        """The selected port ("" when there is none)."""
        return self.ui.comboPort.currentText()

    def _on_connect_clicked(self) -> None:
        if self._connected:
            self.disconnect_requested.emit()
        else:
            self.connect_requested.emit(self.current_port())
