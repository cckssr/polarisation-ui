"""KDC101 polariser-stage panel: device, status, position, optic zeroing."""

from __future__ import annotations

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QGroupBox, QWidget

from polarisation_ui.core.formatting import fmt_angle
from polarisation_ui.infrastructure.config import AppConfig, default_config
from polarisation_ui.pyqt.ui_kdc_panel import Ui_KdcPanel
from polarisation_ui.ui.common.status_led import set_led_state
from polarisation_ui.ui.i18n import apply_strings


class KdcPanel(QGroupBox):
    """Connection, homing and zero-offset controls of the Thorlabs KDC101."""

    refresh_requested = Signal()
    connect_requested = Signal(object)  # selected connection id (str), None when none is listed
    disconnect_requested = Signal()
    home_requested = Signal()
    zero_requested = Signal()
    offset_reset_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        """Build the form; texts come from :meth:`apply_config`."""
        super().__init__(parent)
        self.ui = Ui_KdcPanel()
        self.ui.setupUi(self)
        self._config: AppConfig = default_config()
        self._connected = False
        self.ui.buttonRefresh.clicked.connect(self.refresh_requested)
        self.ui.buttonConnect.clicked.connect(self._on_connect_clicked)
        self.ui.buttonHome.clicked.connect(self.home_requested)
        self.ui.buttonZero.clicked.connect(self.zero_requested)
        self.ui.buttonOffsetReset.clicked.connect(self.offset_reset_requested)

    def apply_config(self, config: AppConfig) -> None:
        """Apply the ``ui.kdc_panel`` strings."""
        self._config = config
        apply_strings(self, config.section("ui").get("kdc_panel", {}))
        self.set_connected(self._connected)
        self.set_position(None)
        self.set_offset(0.0)

    def _t(self, key: str) -> str:
        return self._config.text(f"kdc_panel.{key}")

    # ---- setters (driven by the controller) -----------------------------------------------
    @Slot(list)
    def set_devices(self, devices: list[tuple[str, str]]) -> None:
        """Replace the device list (``(connection id, description)``), keeping the selection."""
        combo = self.ui.comboDevice
        current = combo.currentText()
        combo.clear()
        for conn_id, _ in devices:
            combo.addItem(f"{conn_id}", userData=conn_id)
        if not devices:
            combo.addItem(self._t("text_no_device"))
        index = combo.findText(current) if current else -1
        if index >= 0:
            combo.setCurrentIndex(index)

    @Slot(str, str)
    def set_state(self, led: str, text: str) -> None:
        """Show the device status (``led`` is a controller LED state)."""
        set_led_state(self.ui.ledStatus, self.ui.valueStatus, text, led)

    @Slot(bool)
    def set_connected(self, connected: bool) -> None:
        """The connect button disconnects while connected."""
        self._connected = connected
        self.ui.buttonConnect.setText(self._t("text_disconnect" if connected else "text_connect"))

    @Slot(bool, bool, bool, bool)
    def set_controls(self, connect: bool, home: bool, zero: bool, reset: bool) -> None:
        """Enable the buttons (connect, home, find zero, reset offset)."""
        self.ui.buttonConnect.setEnabled(connect)
        self.ui.buttonHome.setEnabled(home)
        self.ui.buttonZero.setEnabled(zero)
        self.ui.buttonOffsetReset.setEnabled(reset)

    @Slot(object)
    def set_position(self, position: float | None) -> None:
        """Show the raw stage angle, a dash when unknown."""
        self.ui.valuePosition.setText(
            self._t("text_none") if position is None else f"{fmt_angle(position)}°"
        )

    @Slot(float)
    def set_offset(self, offset_deg: float) -> None:
        """Show the zero offset, a dash when none is set."""
        self.ui.valueOffset.setText(
            self._t("text_none") if offset_deg == 0.0 else f"{fmt_angle(offset_deg)}°"
        )

    def _on_connect_clicked(self) -> None:
        if self._connected:
            self.disconnect_requested.emit()
        else:
            self.connect_requested.emit(self.ui.comboDevice.currentData())
