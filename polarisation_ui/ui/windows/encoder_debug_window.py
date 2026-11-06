"""Encoder + ADS1220 Debug Dialog.

Provides a comprehensive live view of:
  - AS5048A encoder angles, magnitudes, and diagnostics (DIAG:ENC?)
  - ADS1220 live voltage, register dump (DIAG:ADC?), PD-TIA state (DIAG:PDTIA?)
  - ADC configuration (CONF:ADC:*?)
  - SCPI error queue (SYST:ERR?)
  - System info: IDN, streaming rate, debug mode
  - SCPI terminal for arbitrary commands

Architecture note: accesses DualEncoderArduino directly via
GoniometerDeviceManager.get_encoder_device() — acceptable for a debug-only
dialog that lives entirely inside the UI layer.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from PySide6.QtCore import QTimer, Slot
from PySide6.QtWidgets import QDialog, QLineEdit

from polarisation_ui.core.models import Frame
from polarisation_ui.infrastructure.config import AppConfig, default_config
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
from polarisation_ui.ui.i18n import apply_strings

if TYPE_CHECKING:
    from polarisation_ui.infrastructure.devices.pm400 import PM400PowerMeter
    from polarisation_ui.ui.controllers.data_controller import DataController


# ─── LED colour semantics ───────────────────────────────────────────────────
# COMP_H / COMP_L  — False = OK (green),  True = warning (yellow)
# COF              — False = OK (green),  True = error   (red)
# OCF              — True  = ready (green), False = not ready (yellow)
# Error Flag       — False = OK (green),  True = error   (red)
# Conn             — connected = green,   disconnected = red
# ────────────────────────────────────────────────────────────────────────────

_ENCODER_LABELS = ["A", "B", "BOTH"]


class EncoderDebugDialog(QDialog):
    """Live debug view for the dual AS5048A encoder system.

    Opens non-modally so the main window remains usable while monitoring.
    All data is polled via the existing GoniometerDeviceManager — no extra
    serial connections are opened.
    """

    def __init__(
        self,
        device_manager: GoniometerDeviceManager,
        sample_inverted: bool = False,
        data_controller: DataController | None = None,
        parent=None,
        standalone: bool = False,
        pm400: PM400PowerMeter | None = None,
        config: AppConfig | None = None,
    ) -> None:
        """Wire up the Designer form and polling against the shared device manager.

        ``pm400`` is accepted because the main window passes it along; the dialog has no
        power-meter diagnostics yet, so it is only stored.
        """
        super().__init__(parent)
        self.config = config or default_config()
        self.ui = Ui_EncoderDebugDialog()
        self.ui.setupUi(self)
        apply_strings(self, self.config.section("ui").get("encoder_debug", {}))

        self._dm = device_manager
        self._sample_inverted = sample_inverted
        self._data_controller = data_controller
        self._standalone = standalone
        self._pm400 = pm400
        self._adc_reg_edits: tuple[QLineEdit, ...] = (
            self.ui.editReg0,
            self.ui.editReg1,
            self.ui.editReg2,
            self.ui.editReg3,
        )

        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._refresh)

        self._apply_code_texts()
        self._setup_connection_group()
        self._setup_raw_stream_tab()
        self.ui.checkSampleInverted.setChecked(sample_inverted)

        self._connect_signals()
        self._init_leds()

        if device_manager.is_encoder_connected():
            self._load_system_info()
        else:
            self._set_tabs_enabled(False)

        if not standalone and self.ui.checkAutoRefresh.isChecked():
            self._refresh_timer.start(self.ui.spinRefreshInterval.value())

        # Speed up DataController diagnostic polling while this dialog is open.
        if self._data_controller is not None:
            self._data_controller.set_diag_interval(500)

    # ==================== Setup ====================

    def _msg(self, key: str, **fmt: object) -> str:
        """Message text ``messages.encoder_debug.<key>``."""
        return self.config.message(f"encoder_debug.{key}", **fmt)

    def _apply_code_texts(self) -> None:
        """Set the texts that are not plain object-name keys: tab titles and combo items."""
        tabs = self.ui.tabWidget
        for page, key in (
            (self.ui.tabMeasurements, "tab_title_measurements"),
            (self.ui.tabSystem, "tab_title_system"),
            (self.ui.tabTerminal, "tab_title_terminal"),
            (self.ui.tabAds, "tab_title_ads"),
            (self.ui.tabRawStream, "tab_title_raw_stream"),
            (self.ui.tabSelfTest, "tab_title_self_test"),
        ):
            tabs.setTabText(tabs.indexOf(page), self.config.text(f"encoder_debug.{key}"))
        items = self.config.get("ui.encoder_debug.combo_encoder_items", [])
        combo = self.ui.comboEncoderSelect
        for index, text in enumerate(items[: combo.count()]):
            combo.setItemText(index, str(text))

    def _setup_connection_group(self) -> None:
        """Show the port-selector bar in standalone (--debug-only) mode, hide it otherwise."""
        self.ui.groupConnection.setVisible(self._standalone)
        if not self._standalone:
            return
        self.setWindowTitle(self.config.text("encoder_debug.title_standalone"))
        self.ui.valueConnectionStatus.setText(self._msg("not_connected"))
        self._populate_standalone_ports()

    def _setup_raw_stream_tab(self) -> None:
        """Show the DATA:FRAME log when a DataController feeds it, else the notice label."""
        has_controller = self._data_controller is not None
        self.ui.labelRawStreamNotice.setVisible(not has_controller)
        self.ui.editRawStream.setVisible(has_controller)
        self.ui.buttonClearRawStream.setVisible(has_controller)
        if self._data_controller is None:
            return
        # Enable the signal when the dialog opens, disable it again on close (see closeEvent).
        self._data_controller.raw_frame.connect(self._on_raw_frame)
        self._data_controller.enable_raw_frame_signal(True)
        Debug.debug("Raw Stream tab connected to DataController.raw_frame")

    def _populate_standalone_ports(self) -> None:
        """Refresh the port combo from the device manager's port list."""
        ports = self._dm.list_available_ports()
        self.ui.comboPort.clear()
        if ports:
            self.ui.comboPort.addItems(ports)
        else:
            self.ui.comboPort.addItem(self._msg("no_ports"))

    @Slot()
    def _standalone_connect(self) -> None:
        """Connect to (or disconnect from) the selected port in standalone mode."""
        if self._dm.is_encoder_connected():
            self._refresh_timer.stop()
            self._dm.disconnect_all()
            self.ui.buttonConnect.setText(self.config.text("encoder_debug.text_connect"))
            self.ui.valueConnectionStatus.setText(self._msg("standalone_disconnected"))
            self._set_tabs_enabled(False)
            return

        port = self.ui.comboPort.currentText()
        self.ui.valueConnectionStatus.setText(self._msg("standalone_connecting"))
        self.ui.buttonConnect.setEnabled(False)

        success = self._dm.connect_encoders(port=port)
        self.ui.buttonConnect.setEnabled(True)

        if success:
            self.ui.valueConnectionStatus.setText(self._msg("standalone_connected", port=port))
            self.ui.buttonConnect.setText(self.config.text("encoder_debug.text_disconnect"))
            self._set_tabs_enabled(True)
            self._load_system_info()
            if self.ui.checkAutoRefresh.isChecked():
                self._refresh_timer.start(self.ui.spinRefreshInterval.value())
            Debug.info(f"Standalone debug: connected to {port}")
        else:
            self.ui.valueConnectionStatus.setText(self._msg("standalone_failed"))
            Debug.error(f"Standalone debug: connection to {port} failed")

    def _set_tabs_enabled(self, enabled: bool) -> None:
        """Enable or disable the diagnostic tabs and the refresh controls."""
        self.ui.tabWidget.setEnabled(enabled)
        self.ui.groupControl.setEnabled(enabled)

    def _connect_signals(self) -> None:
        self.ui.buttonRefreshPorts.clicked.connect(self._populate_standalone_ports)
        self.ui.buttonConnect.clicked.connect(self._standalone_connect)

        self.ui.buttonRefresh.clicked.connect(self._refresh)
        self.ui.checkAutoRefresh.toggled.connect(self._on_auto_refresh_toggled)
        self.ui.spinRefreshInterval.valueChanged.connect(self._on_interval_changed)

        self.ui.buttonZeroEncoder.clicked.connect(self._zero_encoder)
        self.ui.buttonClearErrorFlag.clicked.connect(self._clear_error_flag)

        self.ui.buttonSendCommand.clicked.connect(self._send_terminal_command)
        self.ui.editCommandInput.returnPressed.connect(self._send_terminal_command)
        self.ui.buttonClearLog.clicked.connect(self.ui.editTerminalLog.clear)

        self.ui.buttonReadScpiErrors.clicked.connect(self._read_scpi_error_queue)
        self.ui.buttonClearScpiErrors.clicked.connect(self._clear_scpi_error_queue)

        self.ui.checkDebugMode.toggled.connect(self._on_debug_mode_toggled)

        self.ui.buttonReadAdcConfig.clicked.connect(self._read_adc_config)
        self.ui.buttonClearRawStream.clicked.connect(self.ui.editRawStream.clear)
        self.ui.buttonRunSelfTest.clicked.connect(self._run_self_test)

        # The button box's rejected() -> reject() connection is declared in the .ui file.

        # When DataController is available, subscribe to its signals for live
        # angles, intensity, and stat bitmask so we display the same processed
        # values as the main window (inversion, averaging, spike filter applied)
        # without competing on the serial port.
        if self._data_controller is not None:
            self._data_controller.angles_updated.connect(self._on_angles_updated)
            self._data_controller.intensity_updated.connect(self._on_intensity_updated)
            self._data_controller.frame_ready.connect(self._on_frame_ready)

    def _init_leds(self) -> None:
        """Reset all LEDs to gray until the first successful read."""
        for name in (
            "ledConnA",
            "ledConnB",
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
            "ledAdcPresent",
            "ledAdcDrdy",
        ):
            getattr(self.ui, name).setStyleSheet(LED_GRAY)

    # ==================== DataController Signal Receivers ====================

    @Slot(float, float)
    def _on_angles_updated(self, sample_angle: float, detector_angle: float) -> None:
        """Update angle displays at 10 Hz from DataController (same values as main window)."""
        self.ui.lcdAngleA.display(round(sample_angle, 4))
        self.ui.ledConnA.setStyleSheet(LED_GREEN)
        self.ui.lcdAngleB.display(round(detector_angle, 4))
        self.ui.ledConnB.setStyleSheet(LED_GREEN)

    @Slot(float)
    def _on_intensity_updated(self, intensity: float) -> None:
        """Update ADC voltage display at 10 Hz from DataController."""
        self.ui.lcdAdcVoltage.display(intensity)

    @Slot(object)
    def _on_frame_ready(self, frame: Frame) -> None:
        """Drive error-flag LEDs from Frame.stat bits 2/3.

        In polling mode ``stat`` is always 0 (the firmware only exposes the error
        flag in streaming ``DATA:FRAME`` packets), so both LEDs appear green —
        meaning "no error detected via this path".  When streaming mode is used
        in the future, bits 2/3 will reflect the hardware self-latching error flag.
        """
        err_a = bool(frame.stat & 0x04)  # bit 2 — encoder A persistent error flag
        err_b = bool(frame.stat & 0x08)  # bit 3 — encoder B persistent error flag
        self.ui.ledErrorA.setStyleSheet(LED_RED if err_a else LED_GREEN)
        self.ui.ledErrorB.setStyleSheet(LED_RED if err_b else LED_GREEN)

    # ==================== Device Access ====================

    def _device(self) -> DualEncoderArduino | None:
        return self._dm.get_encoder_device()

    def _selected_encoder_id(self) -> str:
        """Return 'A', 'B', or 'BOTH' from the encoder selector combo."""
        return _ENCODER_LABELS[self.ui.comboEncoderSelect.currentIndex()]

    # ==================== Refresh ====================

    @Slot()
    def _refresh(self) -> None:
        device = self._device()
        if device is None:
            self._set_disconnected_state()
            return
        if self._data_controller is None:
            # Standalone: no shared serial port owner — do all reads directly.
            self._update_measurements(device)
            self._update_diagnostics(device)
            self._update_adc_tab(device)
        else:
            # DataController present: angles and voltage arrive via signals.
            # Remaining debug reads (magnitude, diagnostic flags, ADC registers,
            # PDTIA) are done here with the poll timer paused to prevent
            # interleaving on the serial port.
            self._update_debug_reads(device)

    def _update_debug_reads(self, device: DualEncoderArduino) -> None:
        """Magnitude, encoder diagnostics, ADC registers, PDTIA — pause poll timer."""
        poll_timer = self._data_controller.poll_timer
        was_active = poll_timer.isActive()
        if was_active:
            poll_timer.stop()
        try:
            mag_a = device.read_magnitude(EncoderID.A)
            if mag_a is not None:
                self.ui.lcdMagnitudeA.display(mag_a)
                self.ui.progressMagnitudeA.setValue(mag_a)
            mag_b = device.read_magnitude(EncoderID.B)
            if mag_b is not None:
                self.ui.lcdMagnitudeB.display(mag_b)
                self.ui.progressMagnitudeB.setValue(mag_b)

            diag_a, diag_b = device.query_diagnostics("BOTH")
            if diag_a:
                self._apply_diagnostics(diag_a, "A")
            if diag_b:
                self._apply_diagnostics(diag_b, "B")

            self._update_adc_diagnostics(device)
        finally:
            if was_active:
                poll_timer.start(self._data_controller.poll_interval)

    def _set_disconnected_state(self) -> None:
        self.ui.ledConnA.setStyleSheet(LED_RED)
        self.ui.ledConnB.setStyleSheet(LED_RED)
        for suffix in ("A", "B"):
            for led in ("ledCompH", "ledCompL", "ledCof", "ledOcf", "ledError"):
                getattr(self.ui, f"{led}{suffix}").setStyleSheet(LED_GRAY)
        self.ui.ledAdcPresent.setStyleSheet(LED_RED)
        self.ui.ledAdcDrdy.setStyleSheet(LED_GRAY)

    # ──── Measurements (Angle + Magnitude) ──────────────────────────────────

    def _update_measurements(self, device: DualEncoderArduino) -> None:
        # Encoder A — angle
        val_a = device.read_angle(EncoderID.A)
        if val_a is not None:
            self.ui.lcdAngleA.display(round(val_a.angle_deg, 4))
            self.ui.ledConnA.setStyleSheet(LED_GREEN)
        else:
            self.ui.ledConnA.setStyleSheet(LED_RED)

        # Encoder B — angle
        val_b = device.read_angle(EncoderID.B)
        if val_b is not None:
            self.ui.lcdAngleB.display(round(val_b.angle_deg, 4))
            self.ui.ledConnB.setStyleSheet(LED_GREEN)
        else:
            self.ui.ledConnB.setStyleSheet(LED_RED)

        # Encoder A — magnitude
        mag_a = device.read_magnitude(EncoderID.A)
        if mag_a is not None:
            self.ui.lcdMagnitudeA.display(mag_a)
            self.ui.progressMagnitudeA.setValue(mag_a)

        # Encoder B — magnitude
        mag_b = device.read_magnitude(EncoderID.B)
        if mag_b is not None:
            self.ui.lcdMagnitudeB.display(mag_b)
            self.ui.progressMagnitudeB.setValue(mag_b)

    # ──── Diagnostics ────────────────────────────────────────────────────────

    def _update_diagnostics(self, device: DualEncoderArduino) -> None:
        diag_a, diag_b = device.query_diagnostics("BOTH")
        if diag_a:
            self._apply_diagnostics(diag_a, "A")
        if diag_b:
            self._apply_diagnostics(diag_b, "B")

    def _apply_diagnostics(self, diag: dict, suffix: str) -> None:
        # COMP_H: weak-field warning
        comp_h = bool(diag.get("compHigh"))
        getattr(self.ui, f"ledCompH{suffix}").setStyleSheet(LED_YELLOW if comp_h else LED_GREEN)

        # COMP_L: strong-field warning
        comp_l = bool(diag.get("compLow"))
        getattr(self.ui, f"ledCompL{suffix}").setStyleSheet(LED_YELLOW if comp_l else LED_GREEN)

        # COF: CORDIC overflow — critical error
        cof = bool(diag.get("cof"))
        getattr(self.ui, f"ledCof{suffix}").setStyleSheet(LED_RED if cof else LED_GREEN)

        # OCF: offset compensation finished — must be True for valid readings
        ocf = bool(diag.get("ocf"))
        getattr(self.ui, f"ledOcf{suffix}").setStyleSheet(LED_GREEN if ocf else LED_YELLOW)

        # Note: ledError{suffix} is driven from Frame.stat bits 2/3 via
        # _on_frame_ready; DIAG:ENC? does not expose the error flag.

        # AGC — always an int (0–255) after the bug-fix in dual_encoder.py
        agc = int(diag.get("agc", 0))
        getattr(self.ui, f"spinAgc{suffix}").setValue(agc)
        getattr(self.ui, f"progressAgc{suffix}").setValue(agc)

    # ==================== System Info ====================

    def _load_system_info(self) -> None:
        """Populate the System tab with static device information."""
        device = self._device()
        if device is None:
            self.ui.editIdn.setText(self._msg("not_connected"))
            return

        # *IDN?
        idn = device.query_idn()
        self.ui.editIdn.setText(idn if idn else "–")

        # CONF:RATE? returns Hz; display as ms
        raw_rate = device.send_query("CONF:RATE?")
        if raw_rate:
            try:
                hz = int(raw_rate.strip())
                if hz > 0:
                    self.ui.spinPollInterval.setValue(round(1000 / hz))
            except ValueError:
                pass

        # SYST:DEB? — block signals to avoid triggering the toggle slot
        raw_deb = device.send_query("SYST:DEB?")
        if raw_deb is not None:
            self.ui.checkDebugMode.blockSignals(True)
            self.ui.checkDebugMode.setChecked(raw_deb.strip() == "1")
            self.ui.checkDebugMode.blockSignals(False)

    # ==================== Controls ====================

    @Slot()
    def _zero_encoder(self) -> None:
        device = self._device()
        if device is None:
            return
        enc = self._selected_encoder_id()
        target = EncoderID.A if enc == "A" else EncoderID.B if enc == "B" else "BOTH"
        device.zero(target)
        Debug.info(f"Zero set for encoder {enc} from debug dialog")

    @Slot()
    def _clear_error_flag(self) -> None:
        device = self._device()
        if device is None:
            return
        enc = self._selected_encoder_id()
        target = EncoderID.A if enc == "A" else EncoderID.B if enc == "B" else "BOTH"
        device.clear_error(target)
        Debug.info(f"Error flag cleared for encoder {enc} from debug dialog")

    # ==================== SCPI Error Queue ====================

    @Slot()
    def _read_scpi_error_queue(self) -> None:
        device = self._device()
        if device is None:
            self.ui.editScpiErrors.setPlainText(self._msg("not_connected"))
            return

        entries: list[str] = []
        for _ in range(20):  # safety limit
            entry = device.query_last_error()
            if entry is None:
                break
            entries.append(entry)
            if entry.startswith("0,"):  # "0,No error" — queue drained
                break

        self.ui.editScpiErrors.setPlainText("\n".join(entries) if entries else "–")

    @Slot()
    def _clear_scpi_error_queue(self) -> None:
        device = self._device()
        if device is None:
            return
        device.send_query("*CLS")
        self.ui.editScpiErrors.clear()
        Debug.info("SCPI error queue cleared (*CLS)")

    # ==================== SCPI Terminal ====================

    @Slot()
    def _send_terminal_command(self) -> None:
        cmd = self.ui.editCommandInput.text().strip()
        if not cmd:
            return

        timestamp = datetime.now().strftime("%H:%M:%S")
        self._log(f"[{timestamp}] >>> {cmd}")

        device = self._device()
        if device is None:
            self._log(f"            <<< {self._msg('terminal_not_connected')}")
            self.ui.editCommandInput.clear()
            return

        if cmd.endswith("?"):
            # Query command — expect a response lineSeparatorA
            response = device.send_query(cmd)
            reply = response if response is not None else self._msg("terminal_timeout")
            self._log(f"            <<< {reply}")
        else:
            # Control command — no response from firmware
            ok = device.send_control_command(cmd)
            reply = "OK" if ok else self._msg("terminal_send_failed")
            self._log(f"            <<< {reply}")

        self.ui.editCommandInput.clear()

    def _log(self, text: str) -> None:
        self.ui.editTerminalLog.append(text)

    # ==================== Auto-refresh & Interval ====================

    @Slot(bool)
    def _on_auto_refresh_toggled(self, enabled: bool) -> None:
        if enabled:
            self._refresh_timer.start(self.ui.spinRefreshInterval.value())
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

    # ==================== ADS1220 Tab ====================

    def _update_adc_tab(self, device: DualEncoderArduino) -> None:
        voltage = device.adc.read_voltage()
        if voltage is not None:
            self.ui.lcdAdcVoltage.display(voltage)
        self._update_adc_diagnostics(device)

    def _update_adc_diagnostics(self, device: DualEncoderArduino) -> None:
        """ADC registers, DRDY and PD-TIA state (DIAG:ADC? / DIAG:PDTIA?)."""
        adc_diag = device.query_adc_diagnostics()
        if adc_diag is not None:
            if adc_diag.get("absent"):
                self.ui.ledAdcPresent.setStyleSheet(LED_RED)
                self.ui.ledAdcDrdy.setStyleSheet(LED_GRAY)
            else:
                self.ui.ledAdcPresent.setStyleSheet(LED_GREEN)
                drdy = bool(adc_diag.get("drdy", False))
                self.ui.ledAdcDrdy.setStyleSheet(LED_GREEN if drdy else LED_YELLOW)
                for i, edit in enumerate(self._adc_reg_edits):
                    edit.setText(f"0x{adc_diag.get(f'reg{i}', 0):02X}")
                self.ui.editLastRaw.setText(f"0x{adc_diag.get('last_raw', 0):06X}")

        pdtia = device.query_pdtia_diagnostics()
        if pdtia is not None:
            self.ui.editPdtiaStage.setText(str(pdtia.get("stage", "–")))
            self.ui.editPdtiaPattern.setText(pdtia.get("pattern", "–"))

    @Slot()
    def _read_adc_config(self) -> None:
        device = self._device()
        if device is None:
            return
        cfg = device.query_adc_config()
        self.ui.editMux.setText(cfg.get("mux", "–"))
        self.ui.editGain.setText(cfg.get("gain", "–"))
        self.ui.editRate.setText(cfg.get("rate", "–"))
        self.ui.editMode.setText(cfg.get("mode", "–"))
        self.ui.editFir.setText(cfg.get("fir", "–"))
        self.ui.editVref.setText(cfg.get("vref", "–"))

    # ==================== Raw Stream Tab ====================

    @Slot(str)
    def _on_raw_frame(self, frame_str: str) -> None:
        """Append one DATA:FRAME line to the raw stream log."""
        ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.ui.editRawStream.appendPlainText(f"[{ts}] {frame_str}")

    # ==================== Self-Test Tab ====================

    @Slot()
    def _run_self_test(self) -> None:
        """Send DIAG:SELF? and display the multi-line result."""
        device = self._device()
        if device is None:
            self.ui.editSelfTest.setPlainText(self._msg("self_test_not_connected"))
            return

        ts = datetime.now().strftime("%H:%M:%S")
        self.ui.editSelfTest.appendPlainText(f"\n[{ts}] DIAG:SELF? …")

        lines = device.query_self_test()
        if not lines:
            self.ui.editSelfTest.appendPlainText(f"  {self._msg('self_test_timeout')}")
            return

        for entry in lines:
            upper = entry.upper()
            status = "✓" if "PASS" in upper else ("✗" if "FAIL" in upper else " ")
            self.ui.editSelfTest.appendPlainText(f"  {status} {entry}")

        Debug.info(f"DIAG:SELF? response: {lines!r}")

    # ==================== Lifecycle ====================

    def closeEvent(self, event) -> None:  # type: ignore[override]
        """Stop polling and detach from the shared DataController before closing."""
        self._refresh_timer.stop()
        if self._data_controller is not None:
            self._data_controller.angles_updated.disconnect(self._on_angles_updated)
            self._data_controller.intensity_updated.disconnect(self._on_intensity_updated)
            self._data_controller.frame_ready.disconnect(self._on_frame_ready)
            self._data_controller.raw_frame.disconnect(self._on_raw_frame)
            self._data_controller.enable_raw_frame_signal(False)
            # Restore diagnostic polling to the background rate.
            self._data_controller.set_diag_interval(5000)
        super().closeEvent(event)
