"""
Encoder + ADS1220 Debug Dialog.

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

from datetime import datetime

from PySide6.QtCore import QTimer, Slot
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLCDNumber,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

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

    def __init__(
        self,
        device_manager: GoniometerDeviceManager,
        sample_inverted: bool = False,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.ui = Ui_EncoderDebugDialog()
        self.ui.setupUi(self)

        self._dm = device_manager
        self._sample_inverted = sample_inverted

        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._refresh)

        self._connect_signals()
        self._init_leds()
        self._load_system_info()

        self._build_ads_tab()

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
        # ADS LEDs are instance vars created in _build_ads_tab — set after that call.

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
        self._update_adc_tab(device)

    def _set_disconnected_state(self) -> None:
        self.ui.ledConnA.setStyleSheet(LED_RED)
        self.ui.ledConnB.setStyleSheet(LED_RED)
        for suffix in ("A", "B"):
            for led in ("ledCompH", "ledCompL", "ledCof", "ledOcf", "ledError"):
                getattr(self.ui, f"{led}{suffix}").setStyleSheet(LED_GRAY)
        if hasattr(self, "_led_adc_present"):
            self._led_adc_present.setStyleSheet(LED_RED)
            self._led_adc_drdy.setStyleSheet(LED_GRAY)

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

        # CONF:RATE? returns Hz; display as ms
        raw_rate = device.send_query("CONF:RATE?")
        if raw_rate:
            try:
                hz = int(raw_rate.strip())
                if hz > 0:
                    self.ui.spbPollInterval.setValue(round(1000 / hz))
            except ValueError:
                pass

        # SYST:DEB? — block signals to avoid triggering the toggle slot
        raw_deb = device.send_query("SYST:DEB?")
        if raw_deb is not None:
            self.ui.cbDebugMode.blockSignals(True)
            self.ui.cbDebugMode.setChecked(raw_deb.strip() == "1")
            self.ui.cbDebugMode.blockSignals(False)

        # Sample stage inverted flag — read-only, derived from hardware config
        lbl = QLabel("Probe invertiert:", self.ui.gbSysInfo)
        cb = QCheckBox(self.ui.gbSysInfo)
        cb.setChecked(self._sample_inverted)
        cb.setEnabled(False)
        self.ui.formSysInfo.addRow(lbl, cb)

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

    # ==================== ADS1220 Tab ====================

    def _build_ads_tab(self) -> None:
        """Create the ADS1220 / PD-TIA diagnostic tab programmatically."""
        tab = QWidget()
        vl = QVBoxLayout(tab)

        # ── Live readings ────────────────────────────────────────────────────
        gb_live = QGroupBox("Live-Messwerte")
        form_live = QFormLayout(gb_live)

        self._led_adc_present = QFrame()
        self._led_adc_present.setMinimumSize(20, 20)
        self._led_adc_present.setMaximumSize(20, 20)
        self._led_adc_present.setFrameShape(QFrame.Shape.Box)
        self._led_adc_present.setStyleSheet(LED_GRAY)
        form_live.addRow("ADS1220 vorhanden:", self._led_adc_present)

        self._lcd_adc_voltage = QLCDNumber()
        self._lcd_adc_voltage.setDigitCount(10)
        self._lcd_adc_voltage.setSmallDecimalPoint(True)
        self._lcd_adc_voltage.setMinimumSize(180, 50)
        self._lcd_adc_voltage.setToolTip("MEAS:ADC:VOLT? (V)")
        form_live.addRow("Spannung (V):", self._lcd_adc_voltage)

        self._led_adc_drdy = QFrame()
        self._led_adc_drdy.setMinimumSize(20, 20)
        self._led_adc_drdy.setMaximumSize(20, 20)
        self._led_adc_drdy.setFrameShape(QFrame.Shape.Box)
        self._led_adc_drdy.setStyleSheet(LED_GRAY)
        self._led_adc_drdy.setToolTip("Zeitbasierte Bereitschaft (DRDY-Pin nicht angeschlossen)")
        form_live.addRow("Bereit (zeitbasiert):", self._led_adc_drdy)

        vl.addWidget(gb_live)

        # ── Registers + Config side by side ──────────────────────────────────
        hl_mid = QHBoxLayout()

        gb_regs = QGroupBox("Register (DIAG:ADC?)")
        form_regs = QFormLayout(gb_regs)
        self._le_adc_reg: dict[int, QLineEdit] = {}
        for i in range(4):
            le = QLineEdit()
            le.setReadOnly(True)
            le.setPlaceholderText("–")
            self._le_adc_reg[i] = le
            form_regs.addRow(f"REG{i}:", le)
        self._le_adc_last_raw = QLineEdit()
        self._le_adc_last_raw.setReadOnly(True)
        self._le_adc_last_raw.setPlaceholderText("–")
        form_regs.addRow("Last Raw:", self._le_adc_last_raw)
        hl_mid.addWidget(gb_regs)

        gb_cfg = QGroupBox("Konfiguration (CONF:ADC:*?)")
        form_cfg = QFormLayout(gb_cfg)
        self._le_adc_mux = QLineEdit(); self._le_adc_mux.setReadOnly(True); self._le_adc_mux.setPlaceholderText("–")
        self._le_adc_gain = QLineEdit(); self._le_adc_gain.setReadOnly(True); self._le_adc_gain.setPlaceholderText("–")
        self._le_adc_rate = QLineEdit(); self._le_adc_rate.setReadOnly(True); self._le_adc_rate.setPlaceholderText("–")
        self._le_adc_mode = QLineEdit(); self._le_adc_mode.setReadOnly(True); self._le_adc_mode.setPlaceholderText("–")
        self._le_adc_fir = QLineEdit(); self._le_adc_fir.setReadOnly(True); self._le_adc_fir.setPlaceholderText("–")
        self._le_adc_vref = QLineEdit(); self._le_adc_vref.setReadOnly(True); self._le_adc_vref.setPlaceholderText("–")
        form_cfg.addRow("MUX:", self._le_adc_mux)
        form_cfg.addRow("Gain:", self._le_adc_gain)
        form_cfg.addRow("Rate (SPS):", self._le_adc_rate)
        form_cfg.addRow("Mode:", self._le_adc_mode)
        form_cfg.addRow("FIR Filter:", self._le_adc_fir)
        form_cfg.addRow("Spannungsref.:", self._le_adc_vref)
        btn_read_cfg = QPushButton("Konfiguration lesen")
        btn_read_cfg.clicked.connect(self._read_adc_config)
        form_cfg.addRow("", btn_read_cfg)
        hl_mid.addWidget(gb_cfg)

        vl.addLayout(hl_mid)

        # ── PD-TIA ───────────────────────────────────────────────────────────
        gb_pdtia = QGroupBox("PD-TIA Verstärkung (DIAG:PDTIA?)")
        form_pdtia = QFormLayout(gb_pdtia)
        self._le_pdtia_stage = QLineEdit(); self._le_pdtia_stage.setReadOnly(True); self._le_pdtia_stage.setPlaceholderText("–")
        self._le_pdtia_pattern = QLineEdit(); self._le_pdtia_pattern.setReadOnly(True); self._le_pdtia_pattern.setPlaceholderText("–")
        form_pdtia.addRow("Stufe:", self._le_pdtia_stage)
        form_pdtia.addRow("GPIO Muster:", self._le_pdtia_pattern)
        vl.addWidget(gb_pdtia)

        vl.addItem(QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.ui.tabWidget.addTab(tab, "ADS1220")

    def _update_adc_tab(self, device: "DualEncoderArduino") -> None:
        # Live voltage
        voltage = device.adc.read_voltage()
        if voltage is not None:
            self._lcd_adc_voltage.display(voltage)

        # ADC diagnostics (registers + drdy)
        adc_diag = device.get_adc_diagnostics()
        if adc_diag is not None:
            if adc_diag.get("absent"):
                self._led_adc_present.setStyleSheet(LED_RED)
                self._led_adc_drdy.setStyleSheet(LED_GRAY)
            else:
                self._led_adc_present.setStyleSheet(LED_GREEN)
                drdy = bool(adc_diag.get("drdy", False))
                self._led_adc_drdy.setStyleSheet(LED_GREEN if drdy else LED_YELLOW)
                for i in range(4):
                    self._le_adc_reg[i].setText(f"0x{adc_diag.get(f'reg{i}', 0):02X}")
                self._le_adc_last_raw.setText(f"0x{adc_diag.get('last_raw', 0):06X}")

        # PD-TIA
        pdtia = device.get_pdtia_diagnostics()
        if pdtia is not None:
            self._le_pdtia_stage.setText(str(pdtia.get("stage", "–")))
            self._le_pdtia_pattern.setText(pdtia.get("pattern", "–"))

    @Slot()
    def _read_adc_config(self) -> None:
        device = self._device()
        if device is None:
            return
        cfg = device.get_adc_config()
        self._le_adc_mux.setText(cfg.get("mux", "–"))
        self._le_adc_gain.setText(cfg.get("gain", "–"))
        self._le_adc_rate.setText(cfg.get("rate", "–"))
        self._le_adc_mode.setText(cfg.get("mode", "–"))
        self._le_adc_fir.setText(cfg.get("fir", "–"))
        self._le_adc_vref.setText(cfg.get("vref", "–"))

    # ==================== Lifecycle ====================

    def closeEvent(self, event) -> None:  # type: ignore[override]
        self._refresh_timer.stop()
        super().closeEvent(event)
