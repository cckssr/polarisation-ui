"""
Encoder Debug Dialog.

Provides a comprehensive live view of all AS5048A encoder parameters:
  - Angles (MEAS:ANGL? A/B)
  - Raw magnitudes (MEAS:MAGN? A/B)
  - Diagnostics: COMP_H, COMP_L, COF, OCF, AGC (SYST:DIAG? A/B)
  - SCPI error queue (SYST:ERR?)
  - System info: IDN, poll interval, debug mode
  - SCPI terminal for arbitrary commands

Architecture note: accesses DualEncoderArduino directly via
GoniometerDeviceManager.get_encoder_device() — acceptable for a debug-only
dialog that lives entirely inside the UI layer.
"""

from datetime import datetime

from PySide6.QtCore import QTimer, Slot
from PySide6.QtWidgets import QDialog

from polarisation_ui.infrastructure.device_manager import GoniometerDeviceManager
from polarisation_ui.infrastructure.devices.dual_encoder import (
    DualEncoderArduino,
    EncoderID,
)
from polarisation_ui.infrastructure.logging import Debug
from polarisation_ui.pyqt.ui_encoder_debug import Ui_EncoderDebugDialog
from polarisation_ui.ui.common.status_led import (
    LED_GRAY,
    LED_GREEN,
    LED_RED,
    LED_YELLOW,
)


# ─── LED colour semantics ───────────────────────────────────────────────────
# COMP_H / COMP_L  — False = OK (green),  True = warning (yellow)
# COF              — False = OK (green),  True = error   (red)
# OCF              — True  = ready (green), False = not ready (yellow)
# Error Flag       — False = OK (green),  True = error   (red)
# Conn             — connected = green,   disconnected = red
# ────────────────────────────────────────────────────────────────────────────

_ENCODER_LABELS = ["A", "B", "BOTH"]


class EncoderDebugDialog(QDialog):
    """
    Live debug view for the dual AS5048A encoder system.

    Opens non-modally so the main window remains usable while monitoring.
    All data is polled via the existing GoniometerDeviceManager — no extra
    serial connections are opened.
    """

    def __init__(self, device_manager: GoniometerDeviceManager, parent=None) -> None:
        super().__init__(parent)
        self.ui = Ui_EncoderDebugDialog()
        self.ui.setupUi(self)

        self._dm = device_manager

        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._refresh)

        self._connect_signals()
        self._init_leds()
        self._load_system_info()

        if self.ui.cbAutoRefresh.isChecked():
            self._refresh_timer.start(self.ui.spbRefreshInterval.value())

    # ==================== Setup ====================

    def _connect_signals(self) -> None:
        self.ui.btnRefresh.clicked.connect(self._refresh)
        self.ui.cbAutoRefresh.toggled.connect(self._on_auto_refresh_toggled)
        self.ui.spbRefreshInterval.valueChanged.connect(self._on_interval_changed)

        self.ui.btnZeroEncoder.clicked.connect(self._zero_encoder)
        self.ui.btnClearErrorFlag.clicked.connect(self._clear_error_flag)

        self.ui.btnSendCommand.clicked.connect(self._send_terminal_command)
        self.ui.leCommandInput.returnPressed.connect(self._send_terminal_command)
        self.ui.btnClearLog.clicked.connect(self.ui.teTerminalLog.clear)

        self.ui.btnReadScpiErrors.clicked.connect(self._read_scpi_error_queue)
        self.ui.btnClearScpiErrors.clicked.connect(self._clear_scpi_error_queue)

        self.ui.cbDebugMode.toggled.connect(self._on_debug_mode_toggled)

        self.ui.buttonBox.rejected.connect(self.reject)

    def _init_leds(self) -> None:
        """Reset all LEDs to gray until the first successful read."""
        _conn_leds = ["ledConnA", "ledConnB"]
        _diag_leds = [
            "ledCompHA",
            "ledCompLA",
            "ledCofA",
            "ledOcfA",
            "ledErrorA",
            "ledCompHB",
            "ledCompLB",
            "ledCofB",
            "ledOcfB",
            "ledErrorB",
        ]
        for name in _conn_leds + _diag_leds:
            getattr(self.ui, name).setStyleSheet(LED_GRAY)

    # ==================== Device Access ====================

    def _device(self) -> "DualEncoderArduino | None":
        return self._dm.get_encoder_device()

    def _selected_encoder_id(self) -> str:
        """Return 'A', 'B', or 'BOTH' from the encoder selector combo."""
        return _ENCODER_LABELS[self.ui.cbEncoderSelect.currentIndex()]

    # ==================== Refresh ====================

    @Slot()
    def _refresh(self) -> None:
        device = self._device()
        if device is None:
            self._set_disconnected_state()
            return
        self._update_measurements(device)
        self._update_diagnostics(device)

    def _set_disconnected_state(self) -> None:
        self.ui.ledConnA.setStyleSheet(LED_RED)
        self.ui.ledConnB.setStyleSheet(LED_RED)
        for suffix in ("A", "B"):
            for led in ("ledCompH", "ledCompL", "ledCof", "ledOcf", "ledError"):
                getattr(self.ui, f"{led}{suffix}").setStyleSheet(LED_GRAY)

    # ──── Measurements (Angle + Magnitude) ──────────────────────────────────

    def _update_measurements(self, device: "DualEncoderArduino") -> None:
        # Encoder A — angle
        angle_a = device.read_encoder_a()
        if angle_a is not None:
            self.ui.lcdAngleA.display(round(angle_a, 4))
            self.ui.ledConnA.setStyleSheet(LED_GREEN)
        else:
            self.ui.ledConnA.setStyleSheet(LED_RED)

        # Encoder B — angle
        angle_b = device.read_encoder_b()
        if angle_b is not None:
            self.ui.lcdAngleB.display(round(angle_b, 4))
            self.ui.ledConnB.setStyleSheet(LED_GREEN)
        else:
            self.ui.ledConnB.setStyleSheet(LED_RED)

        # Encoder A — magnitude
        mag_a = device.read_magnitude(EncoderID.A)
        if mag_a is not None:
            self.ui.lcdMagnitudeA.display(mag_a)
            self.ui.pbarMagnitudeA.setValue(mag_a)

        # Encoder B — magnitude
        mag_b = device.read_magnitude(EncoderID.B)
        if mag_b is not None:
            self.ui.lcdMagnitudeB.display(mag_b)
            self.ui.pbarMagnitudeB.setValue(mag_b)

    # ──── Diagnostics ────────────────────────────────────────────────────────

    def _update_diagnostics(self, device: "DualEncoderArduino") -> None:
        diag_a = device.get_diagnostics_a()
        if diag_a:
            self._apply_diagnostics(diag_a, "A")

        diag_b = device.get_diagnostics_b()
        if diag_b:
            self._apply_diagnostics(diag_b, "B")

    def _apply_diagnostics(self, diag: dict, suffix: str) -> None:
        # COMP_H: weak-field warning
        comp_h = bool(diag.get("compHigh"))
        getattr(self.ui, f"ledCompH{suffix}").setStyleSheet(
            LED_YELLOW if comp_h else LED_GREEN
        )

        # COMP_L: strong-field warning
        comp_l = bool(diag.get("compLow"))
        getattr(self.ui, f"ledCompL{suffix}").setStyleSheet(
            LED_YELLOW if comp_l else LED_GREEN
        )

        # COF: CORDIC overflow — critical error
        cof = bool(diag.get("cof"))
        getattr(self.ui, f"ledCof{suffix}").setStyleSheet(LED_RED if cof else LED_GREEN)

        # OCF: offset compensation finished — must be True for valid readings
        ocf = bool(diag.get("ocf"))
        getattr(self.ui, f"ledOcf{suffix}").setStyleSheet(
            LED_GREEN if ocf else LED_YELLOW
        )

        # Error Flag: hardware self-latching error
        # SYST:DIAG? does not expose the error flag directly; rely on the
        # dedicated error-flag read via btnClearErrorFlag / _refresh_error_flags.
        # Leave that LED unchanged here.

        # AGC — always an int (0–255) after the bug-fix in dual_encoder.py
        agc = int(diag.get("agc", 0))
        getattr(self.ui, f"spbAgc{suffix}").setValue(agc)
        getattr(self.ui, f"pbarAgc{suffix}").setValue(agc)

    # ==================== System Info ====================

    def _load_system_info(self) -> None:
        """Populate the System tab with static device information."""
        device = self._device()
        if device is None:
            self.ui.leIdn.setText("Nicht verbunden")
            return

        # *IDN?
        idn = device.identify()
        self.ui.leIdn.setText(idn if idn else "–")

        # SENS:INT?
        raw_interval = device.send_query("SENS:INT?")
        if raw_interval:
            try:
                self.ui.spbPollInterval.setValue(int(raw_interval.strip()))
            except ValueError:
                pass

        # SYST:DEB? — block signals to avoid triggering the toggle slot
        raw_deb = device.send_query("SYST:DEB?")
        if raw_deb is not None:
            self.ui.cbDebugMode.blockSignals(True)
            self.ui.cbDebugMode.setChecked(raw_deb.strip() == "1")
            self.ui.cbDebugMode.blockSignals(False)

    # ==================== Controls ====================

    @Slot()
    def _zero_encoder(self) -> None:
        device = self._device()
        if device is None:
            return
        enc = self._selected_encoder_id()
        if enc == "A":
            device.reset_zero_a()
        elif enc == "B":
            device.reset_zero_b()
        else:
            device.reset_zero_both()
        Debug.info(f"Zero set for encoder {enc} from debug dialog")

    @Slot()
    def _clear_error_flag(self) -> None:
        device = self._device()
        if device is None:
            return
        enc = self._selected_encoder_id()
        if enc == "A":
            device.clear_error_flag_a()
        elif enc == "B":
            device.clear_error_flag_b()
        else:
            device.clear_error_flag_both()
        Debug.info(f"Error flag cleared for encoder {enc} from debug dialog")

    # ==================== SCPI Error Queue ====================

    @Slot()
    def _read_scpi_error_queue(self) -> None:
        device = self._device()
        if device is None:
            self.ui.teScpiErrors.setPlainText("Nicht verbunden")
            return

        entries: list[str] = []
        for _ in range(20):  # safety limit
            entry = device.query_error()
            if entry is None:
                break
            entries.append(entry)
            if entry.startswith("0,"):  # "0,No error" — queue drained
                break

        self.ui.teScpiErrors.setPlainText("\n".join(entries) if entries else "–")

    @Slot()
    def _clear_scpi_error_queue(self) -> None:
        device = self._device()
        if device is None:
            return
        device.send_query("*CLS")
        self.ui.teScpiErrors.clear()
        Debug.info("SCPI error queue cleared (*CLS)")

    # ==================== SCPI Terminal ====================

    @Slot()
    def _send_terminal_command(self) -> None:
        cmd = self.ui.leCommandInput.text().strip()
        if not cmd:
            return

        timestamp = datetime.now().strftime("%H:%M:%S")
        self._log(f"[{timestamp}] >>> {cmd}")

        device = self._device()
        if device is None:
            self._log("            <<< [Nicht verbunden]")
            self.ui.leCommandInput.clear()
            return

        if cmd.endswith("?"):
            # Query command — expect a response line
            response = device.send_query(cmd)
            self._log(
                f"            <<< {response if response is not None else '[Timeout]'}"
            )
        else:
            # Control command — no response from firmware
            ok = device._send_command_no_response(cmd)  # noqa: SLF001
            self._log(
                "            <<< OK" if ok else "            <<< [Fehler beim Senden]"
            )

        self.ui.leCommandInput.clear()

    def _log(self, text: str) -> None:
        self.ui.teTerminalLog.append(text)

    # ==================== Auto-refresh & Interval ====================

    @Slot(bool)
    def _on_auto_refresh_toggled(self, enabled: bool) -> None:
        if enabled:
            self._refresh_timer.start(self.ui.spbRefreshInterval.value())
        else:
            self._refresh_timer.stop()

    @Slot(int)
    def _on_interval_changed(self, value: int) -> None:
        if self._refresh_timer.isActive():
            self._refresh_timer.setInterval(value)

    # ==================== Debug Mode Toggle ====================

    @Slot(bool)
    def _on_debug_mode_toggled(self, enabled: bool) -> None:
        device = self._device()
        if device is None:
            return
        cmd = "SYST:DEB ON" if enabled else "SYST:DEB OFF"
        device.send_query(cmd)
        Debug.info(f"Arduino debug mode {'enabled' if enabled else 'disabled'}")

    # ==================== Lifecycle ====================

    def closeEvent(self, event) -> None:  # type: ignore[override]
        self._refresh_timer.stop()
        super().closeEvent(event)
