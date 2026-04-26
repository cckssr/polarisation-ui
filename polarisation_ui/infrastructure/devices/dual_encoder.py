"""
Dual AS5048A Encoder + ADS1220 ADC interface via SCPI 2.0.0.

SCPI 2.0.0 command subset used by this client:

    *IDN?                               Identification (version check on connect)
    *RST / *CLS                         Reset / clear errors
    MEAS:ENC:ANGL? A|B|BOTH             One-shot encoder angle (degrees)
    MEAS:ENC:MAGN? A|B|BOTH             One-shot encoder magnitude (raw 14-bit)
    MEAS:ADC:VOLT? [CH]                 One-shot ADC voltage (V)
    MEAS:ADC:TEMP?                      Internal temperature (°C)
    CONF:ENC:ZERO A|B|BOTH              Set zero position
    CONF:ENC:ERR  A|B|BOTH              Clear encoder error flag
    CONF:ADC:GAIN 1|2|4|8|16|32|64|128 ADS1220 PGA gain
    CONF:ADC:MUX  <ch>                  Input mux channel
    CONF:ADC:RATE <sps>                 ADC sample rate
    CONF:ADC:MODE NORM|TURBO            ADC operating mode
    CONF:ADC:FIR  OFF|50|60|BOTH        FIR filter
    CONF:ADC:VREF INT|EXT|AVDD          Reference source
    CONF:ADC:TEMP ON|OFF                Enable temperature channel
    CONF:PDTIA:GAIN <stage>             PD-TIA discrete gain stage
    CONF:PDTIA:GAIN?                    Query current stage + GPIO bit pattern
    CONF:SRC <src>[,<src>...]           Streaming source set (e.g. ENC:BOTH,ADC)
    CONF:RATE <hz>                      Streaming rate
    INIT:CONT ON|OFF                    Arm / disarm streaming
    ABOR                                Stop streaming
    DIAG:ENC? A|B                       AS5048A diagnostics
    SYST:ERR?                           Error queue
    SYST:VERS?                          Firmware version string

Firmware < 2.0.0 is rejected with IncompatibleFirmwareError.

Architecture: pure Python — no PySide6, no serial imports beyond pyserial.
"""

from typing import Any, Optional
from dataclasses import dataclass
from enum import Enum

import serial

from polarisation_ui.core.exceptions import IncompatibleFirmwareError
from polarisation_ui.infrastructure.serial_device import SerialDevice
from polarisation_ui.infrastructure.logging import Debug


class EncoderID(Enum):
    """Identifier for encoders; used in commands and responses."""

    A = "A"
    B = "B"


@dataclass
class EncoderValue:
    """Represents a single encoder reading with optional raw magnitude."""

    encoder_id: EncoderID
    angle_deg: float
    angle_raw: Optional[int] = None

    def __repr__(self) -> str:
        raw_str = f", raw={self.angle_raw}" if self.angle_raw is not None else ""
        return f"EncoderValue({self.encoder_id.value}, {self.angle_deg}°{raw_str})"


@dataclass
class DualEncoderValue:
    """Represents simultaneous readings from both encoders."""

    angle_a: float
    angle_b: float

    def __repr__(self) -> str:
        return f"DualEncoderValue(A={self.angle_a}°, B={self.angle_b}°)"


@dataclass
class DesiredState:
    """
    Snapshot of CONF:ADC:* and CONF:PDTIA:* settings.

    Stored by GoniometerDeviceManager and reapplied automatically after every
    successful reconnect so the Arduino config is never lost across a USB drop.
    """

    adc_gain: int = 1
    adc_mux: str = "DIFF01"
    adc_rate: int = 20
    adc_mode: str = "NORM"
    adc_fir: str = "OFF"
    adc_vref: str = "EXT"
    adc_temp: bool = False
    pdtia_gain: int = 0

    def as_config_snapshot(self) -> dict:
        """Return a dict suitable for the SessionJournal config header."""
        return {
            "adc_gain": self.adc_gain,
            "adc_mux": self.adc_mux,
            "adc_rate": self.adc_rate,
            "adc_mode": self.adc_mode,
            "adc_fir": self.adc_fir,
            "adc_vref": self.adc_vref,
            "adc_temp": self.adc_temp,
            "pdtia_gain": self.pdtia_gain,
        }


# ── ADC client facet ──────────────────────────────────────────────────────────
class ADCClient:
    """
    ADC sub-interface of DualEncoderArduino.

    Exposes CONF:ADC:*, CONF:PDTIA:*, MEAS:ADC:* commands as typed methods.
    Accessed via the parent's `.adc` attribute::

        dev.adc.configure(gain=8)
        voltage = dev.adc.read_voltage()
    """

    def __init__(self, parent: "DualEncoderArduino") -> None:
        self._dev = parent

    def configure(
        self,
        gain: int = 1,
        mux: str = "DIFF01",
        rate: int = 20,
        mode: str = "NORM",
        fir: str = "OFF",
        vref: str = "EXT",
        temp: bool = False,
    ) -> bool:
        """Send a batch of CONF:ADC:* commands; returns True if all succeeded."""
        cmds = [
            f"CONF:ADC:GAIN {gain}",
            f"CONF:ADC:MUX {mux}",
            f"CONF:ADC:RATE {rate}",
            f"CONF:ADC:MODE {mode}",
            f"CONF:ADC:FIR {fir}",
            f"CONF:ADC:VREF {vref}",
            f"CONF:ADC:TEMP {'ON' if temp else 'OFF'}",
        ]
        return all(self._dev._send_command_no_response(c) for c in cmds)

    def set_gain(self, gain: int) -> bool:
        """Set ADS1220 PGA gain (1,2,4,8,16,32,64,128)."""
        return self._dev._send_command_no_response(f"CONF:ADC:GAIN {gain}")

    def set_pdtia_gain(self, stage: int) -> bool:
        """Set PD-TIA discrete gain stage (integer; mapped to GPIO pattern in firmware)."""
        return self._dev._send_command_no_response(f"CONF:PDTIA:GAIN {stage}")

    def get_pdtia_gain(self) -> Optional[str]:
        """Query current PD-TIA stage; returns '<stage>,0b<bits>' or None."""
        if not self._dev._device.send_command("CONF:PDTIA:GAIN?", add_newline=True):
            return None
        return self._dev._device.read_value(
            timeout=self._dev.timeout, return_type="str"
        )

    def read_voltage(self, channel: str = "DIFF01") -> Optional[float]:
        """One-shot ADC voltage read via MEAS:ADC:VOLT?; returns volts or None."""
        cmd = f"MEAS:ADC:VOLT? {channel}"
        if not self._dev._device.send_command(cmd, add_newline=True):
            Debug.error(f"Failed to send: {cmd}")
            return None
        response = self._dev._device.read_value(
            timeout=self._dev.timeout, return_type="str"
        )
        if not response:
            Debug.error("No response for MEAS:ADC:VOLT?")
            return None
        try:
            return float(response.strip())
        except ValueError:
            Debug.error(f"Failed to parse ADC voltage: '{response}'")
            return None

    def read_temperature(self) -> Optional[float]:
        """One-shot internal temperature read via MEAS:ADC:TEMP?; returns °C or None."""
        if not self._dev._device.send_command("MEAS:ADC:TEMP?", add_newline=True):
            Debug.error("Failed to send: MEAS:ADC:TEMP?")
            return None
        response = self._dev._device.read_value(
            timeout=self._dev.timeout, return_type="str"
        )
        if not response:
            Debug.error("No response for MEAS:ADC:TEMP?")
            return None
        try:
            return float(response.strip())
        except ValueError:
            Debug.error(f"Failed to parse ADC temperature: '{response}'")
            return None


# ── Main device class ─────────────────────────────────────────────────────────


class DualEncoderArduino:
    """
    High-level SCPI 2.0.0 interface for dual AS5048A encoders + ADS1220 ADC.

    Raises IncompatibleFirmwareError on connect() when the firmware reports
    a version older than 2.0.0.

    Attributes:
        adc: ADCClient — sub-interface for all ADC / PD-TIA operations.
    """

    DEFAULT_TIMEOUT = 1.0
    DEFAULT_POLL_INTERVAL_MS = 50

    def __init__(
        self,
        port: str,
        baudrate: int = 115200,
        timeout: float = DEFAULT_TIMEOUT,
        encoder_b_present: bool = True,
    ) -> None:
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.encoder_b_present = encoder_b_present

        self._device = SerialDevice(port, baudrate, timeout)
        self.adc = ADCClient(self)
        self._firmware_version: str = "unknown"

    @property
    def firmware_version(self) -> str:
        return self._firmware_version

    # ── Connection ────────────────────────────────────────────────────────────

    def connect(self) -> bool:
        """
        Connect and verify firmware version.

        Raises:
            IncompatibleFirmwareError: if firmware < 2.0.0.

        Returns:
            True on success, False on serial error.
        """
        try:
            self._device.reconnect()
            if not self._device.connected:
                return False
            idn = self.identify()
            if idn:
                self._check_firmware_version(idn)
                self._firmware_version = self._parse_version(idn)
            # Apply required ADC configuration: gain=1, external vref (2.5 V), temp off.
            self.adc.configure(gain=1, vref="EXT", temp=False)
            Debug.info(f"DualEncoderArduino connected to {self.port}")
            return True
        except IncompatibleFirmwareError:
            self._device.close()
            raise
        except serial.SerialException as e:
            Debug.error(f"Failed to connect to encoder Arduino: {e}")
            return False

    def disconnect(self) -> None:
        self._device.close()
        Debug.info(f"DualEncoderArduino disconnected from {self.port}")

    def is_connected(self) -> bool:
        return self._device.connected and self._device.serial is not None

    # ── Encoder reads ─────────────────────────────────────────────────────────

    def read_encoder_a(self) -> Optional[float]:
        v = self.read_single(EncoderID.A)
        return v.angle_deg if v else None

    def read_encoder_b(self) -> Optional[float]:
        if not self.encoder_b_present:
            Debug.warning("Encoder B not present")
            return None
        v = self.read_single(EncoderID.B)
        return v.angle_deg if v else None

    def read_single(self, encoder_id: EncoderID) -> Optional[EncoderValue]:
        """MEAS:ENC:ANGL? A|B → EncoderValue."""
        if encoder_id == EncoderID.B and not self.encoder_b_present:
            Debug.warning("Encoder B not available")
            return None

        cmd = f"MEAS:ENC:ANGL? {encoder_id.value}"
        if not self._device.send_command(cmd, add_newline=True):
            Debug.error(f"Failed to send: {cmd}")
            return None

        response = self._device.read_value(timeout=self.timeout, return_type="str")
        if not response:
            Debug.error(f"No response from encoder {encoder_id.value}")
            self._query_and_log_error()
            return None

        return self._parse_single_response(response, encoder_id)

    def read_both(self) -> Optional[DualEncoderValue]:
        """MEAS:ENC:ANGL? BOTH → DualEncoderValue."""
        if not self.encoder_b_present:
            Debug.warning("Encoder B not present")
            return None

        cmd = "MEAS:ENC:ANGL? BOTH"
        if not self._device.send_command(cmd, add_newline=True):
            Debug.error(f"Failed to send: {cmd}")
            return None

        response = self._device.read_value(timeout=self.timeout, return_type="str")
        if not response:
            Debug.error("No response for MEAS:ENC:ANGL? BOTH")
            self._query_and_log_error()
            return None

        return self._parse_both_response(response)

    def read_magnitude(self, encoder_id: EncoderID) -> Optional[int]:
        """MEAS:ENC:MAGN? A|B → raw 14-bit magnitude or None."""
        if encoder_id == EncoderID.B and not self.encoder_b_present:
            Debug.warning("Encoder B not available")
            return None

        cmd = f"MEAS:ENC:MAGN? {encoder_id.value}"
        if not self._device.send_command(cmd, add_newline=True):
            Debug.error(f"Failed to send: {cmd}")
            return None

        response = self._device.read_value(timeout=self.timeout, return_type="str")
        if not response:
            Debug.error(f"No response for {cmd}")
            return None

        try:
            return int(response.strip())
        except ValueError as e:
            Debug.error(f"Failed to parse magnitude: '{response}' ({e})")
            return None

    # ── Continuous streaming ──────────────────────────────────────────────────

    def start_continuous_a(self) -> bool:
        """Configure source ENC:A and arm streaming."""
        return self._send_command_no_response(
            "CONF:SRC ENC:A"
        ) and self._send_command_no_response("INIT:CONT ON")

    def start_continuous_b(self) -> bool:
        """Configure source ENC:B and arm streaming."""
        if not self.encoder_b_present:
            Debug.warning("Encoder B not present")
            return False
        return self._send_command_no_response(
            "CONF:SRC ENC:B"
        ) and self._send_command_no_response("INIT:CONT ON")

    def start_continuous_both(self) -> bool:
        """Configure source ENC:BOTH,ADC and arm streaming."""
        if not self.encoder_b_present:
            Debug.warning("Encoder B not present")
            return False
        return self._send_command_no_response(
            "CONF:SRC ENC:BOTH,ADC"
        ) and self._send_command_no_response("INIT:CONT ON")

    def stop_continuous_a(self) -> bool:
        return self._send_command_no_response("ABOR")

    def stop_continuous_b(self) -> bool:
        return self._send_command_no_response("ABOR")

    def stop_continuous_both(self) -> bool:
        return self._send_command_no_response("ABOR")

    def abort(self) -> bool:
        return self._send_command_no_response("ABOR")

    # ── Zero / error-flag ─────────────────────────────────────────────────────

    def reset_zero_a(self) -> bool:
        return self._send_command_no_response("CONF:ENC:ZERO A")

    def reset_zero_b(self) -> bool:
        if not self.encoder_b_present:
            Debug.warning("Encoder B not present")
            return False
        return self._send_command_no_response("CONF:ENC:ZERO B")

    def reset_zero_both(self) -> bool:
        if not self.encoder_b_present:
            Debug.warning("Encoder B not present")
            return False
        return self._send_command_no_response("CONF:ENC:ZERO BOTH")

    def clear_error_flag_a(self) -> bool:
        return self._send_command_no_response("CONF:ENC:ERR A")

    def clear_error_flag_b(self) -> bool:
        if not self.encoder_b_present:
            Debug.warning("Encoder B not present")
            return False
        return self._send_command_no_response("CONF:ENC:ERR B")

    def clear_error_flag_both(self) -> bool:
        if not self.encoder_b_present:
            Debug.warning("Encoder B not present")
            return False
        return self._send_command_no_response("CONF:ENC:ERR BOTH")

    # ── Poll rate ─────────────────────────────────────────────────────────────

    def set_poll_interval(self, interval_ms: int) -> bool:
        """
        Set the streaming poll interval.

        Converts milliseconds to Hz and sends CONF:RATE.  Valid range: 1–9999 ms.
        """
        if interval_ms < 1 or interval_ms > 9999:
            Debug.error(f"Invalid poll interval: {interval_ms} ms")
            return False
        hz = max(1, round(1000 / interval_ms))
        return self._send_command_no_response(f"CONF:RATE {hz}")

    # ── Diagnostics ───────────────────────────────────────────────────────────

    def get_diagnostics_a(self) -> Optional[dict[str, Any]]:
        return self.get_diagnostics(EncoderID.A)

    def get_diagnostics_b(self) -> Optional[dict[str, Any]]:
        if not self.encoder_b_present:
            Debug.warning("Encoder B not present")
            return None
        return self.get_diagnostics(EncoderID.B)

    def get_diagnostics(self, encoder_id: EncoderID) -> Optional[dict[str, Any]]:
        """DIAG:ENC? A|B → dict with compHigh, compLow, cof, ocf (bool), agc (int)."""
        if encoder_id == EncoderID.B and not self.encoder_b_present:
            Debug.warning("Encoder B not present")
            return None

        cmd = f"DIAG:ENC? {encoder_id.value}"
        if not self._device.send_command(cmd, add_newline=True):
            Debug.error(f"Failed to send: {cmd}")
            return None

        response = self._device.read_value(timeout=self.timeout, return_type="str")
        if not response:
            Debug.error("No response for diagnostics command")
            return None

        return self._parse_diagnostics_response(response, encoder_id)

    def get_adc_diagnostics(self) -> Optional[dict[str, Any]]:
        """DIAG:ADC? → dict(reg0-reg3: int, drdy: bool, last_raw: int, absent: bool)."""
        cmd = "DIAG:ADC?"
        if not self._device.send_command(cmd, add_newline=True):
            Debug.error(f"Failed to send: {cmd}")
            return None
        response = self._device.read_value(timeout=self.timeout, return_type="str")
        if not response:
            Debug.error("No response for DIAG:ADC?")
            return None
        if response.strip() == "ABSENT":
            return {"absent": True}
        try:
            kv: dict[str, str] = {}
            for token in response.strip().split(","):
                if "=" in token:
                    k, _, v = token.partition("=")
                    kv[k.strip()] = v.strip()
            return {
                "absent": False,
                "reg0": int(kv.get("reg0", "0x0"), 16),
                "reg1": int(kv.get("reg1", "0x0"), 16),
                "reg2": int(kv.get("reg2", "0x0"), 16),
                "reg3": int(kv.get("reg3", "0x0"), 16),
                "drdy": bool(int(kv.get("drdy", "0"))),
                "last_raw": int(kv.get("last_raw", "0x0"), 16),
            }
        except (ValueError, KeyError) as e:
            Debug.error(f"Failed to parse DIAG:ADC? response: '{response}' ({e})")
            return None

    def get_pdtia_diagnostics(self) -> Optional[dict[str, Any]]:
        """DIAG:PDTIA? → dict(stage: int, pattern: str like '0b1010')."""
        cmd = "DIAG:PDTIA?"
        if not self._device.send_command(cmd, add_newline=True):
            Debug.error(f"Failed to send: {cmd}")
            return None
        response = self._device.read_value(timeout=self.timeout, return_type="str")
        if not response:
            Debug.error("No response for DIAG:PDTIA?")
            return None
        try:
            kv: dict[str, str] = {}
            for token in response.strip().split(","):
                if "=" in token:
                    k, _, v = token.partition("=")
                    kv[k.strip()] = v.strip()
            return {
                "stage": int(kv.get("stage", "0")),
                "pattern": kv.get("pattern", "0b0000"),
            }
        except (ValueError, KeyError) as e:
            Debug.error(f"Failed to parse DIAG:PDTIA? response: '{response}' ({e})")
            return None

    def get_adc_config(self) -> dict[str, str]:
        """Query all current ADC config settings via CONF:ADC:*? commands."""
        config: dict[str, str] = {}
        for key, cmd in [
            ("mux", "CONF:ADC:MUX?"),
            ("gain", "CONF:ADC:GAIN?"),
            ("rate", "CONF:ADC:RATE?"),
            ("mode", "CONF:ADC:MODE?"),
            ("fir", "CONF:ADC:FIR?"),
            ("vref", "CONF:ADC:VREF?"),
        ]:
            val = self.send_query(cmd)
            config[key] = val.strip() if val else "–"
        return config

    # ── Misc ──────────────────────────────────────────────────────────────────

    def query_error(self) -> Optional[str]:
        if not self._device.send_command("SYST:ERR?", add_newline=True):
            return None
        return self._device.read_value(timeout=self.timeout, return_type="str")

    def identify(self) -> Optional[str]:
        if not self._device.send_command("*IDN?", add_newline=True):
            return None
        return self._device.read_value(timeout=self.timeout, return_type="str")

    def reset(self) -> bool:
        return self._send_command_no_response("*RST")

    def flush_buffer(self) -> bool:
        return self._device.flush_input_buffer()

    def send_query(self, command: str) -> Optional[str]:
        """Send an arbitrary SCPI command and return the response (debug terminal use)."""
        if not self._device.send_command(command, add_newline=True):
            Debug.error(f"Failed to send raw query: {command}")
            return None
        return self._device.read_value(timeout=self.timeout, return_type="str")

    def reapply_desired_state(self, state: "DesiredState") -> bool:
        """
        Reapply a DesiredState snapshot after reconnect.

        Called by GoniometerDeviceManager immediately after a successful
        reconnect so the Arduino retains the last-known CONF:ADC:* / PDTIA
        settings without requiring the user to reconfigure.
        """
        ok = self.adc.configure(
            gain=state.adc_gain,
            mux=state.adc_mux,
            rate=state.adc_rate,
            mode=state.adc_mode,
            fir=state.adc_fir,
            vref=state.adc_vref,
            temp=state.adc_temp,
        )
        if state.pdtia_gain != 0:
            ok = self.adc.set_pdtia_gain(state.pdtia_gain) and ok
        Debug.info(f"DesiredState reapplied (ok={ok}): {state}")
        return ok

    # ── Internal helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _parse_version(idn: str) -> str:
        """Extract the version field from an IDN string, or 'unknown'."""
        parts = idn.strip().split(",")
        return parts[3].strip() if len(parts) >= 4 else "unknown"

    def _check_firmware_version(self, idn: str) -> None:
        """Raise IncompatibleFirmwareError if firmware version is < 2.0.0."""
        version = self._parse_version(idn)
        if version == "unknown":
            return
        try:
            major, minor, *_rest = version.split(".")
            if (int(major), int(minor)) < (2, 0):
                raise IncompatibleFirmwareError(
                    f"Firmware {version} is incompatible; requires >= 2.0.0. "
                    "Please flash the latest firmware."
                )
        except ValueError:
            return  # non-semver version string — skip check

    def _query_and_log_error(self) -> None:
        self._device.flush_input_buffer()
        error = self.query_error()
        if error is None:
            Debug.error("SYST:ERR? query failed (no response)")
        elif error.startswith("0,"):
            Debug.debug(f"SYST:ERR? → {error} (no device error)")
        else:
            Debug.error(f"SYST:ERR? → {error}")

    def _send_command_no_response(self, command: str) -> bool:
        if not self._device.send_command(command, add_newline=True):
            Debug.error(f"Failed to send command: {command}")
            return False
        Debug.debug(f"Command sent: {command}")
        return True

    @staticmethod
    def _parse_data_frame(line: str) -> dict[str, str]:
        """Parse a DATA:FRAME key=value line; unknown keys are silently included."""
        if not line.startswith("DATA:FRAME "):
            return {}
        payload = line[len("DATA:FRAME ") :]
        result: dict[str, str] = {}
        for part in payload.split(","):
            if "=" in part:
                k, _, v = part.partition("=")
                result[k.strip()] = v.strip()
        return result

    def _parse_single_response(
        self, response: str, encoder_id: EncoderID
    ) -> Optional[EncoderValue]:
        try:
            angle_deg = float(response.strip())
            Debug.debug(f"Encoder {encoder_id.value}: {angle_deg}°")
            return EncoderValue(encoder_id, angle_deg)
        except ValueError as e:
            Debug.error(f"Failed to parse encoder response: '{response}' ({e})")
            return None

    def _parse_both_response(self, response: str) -> Optional[DualEncoderValue]:
        try:
            parts = response.strip().split(",")
            if len(parts) < 2:
                Debug.error(f"Invalid dual encoder response: '{response}'")
                return None
            angle_a = float(parts[0])
            angle_b = float(parts[1])
            Debug.debug(f"Both encoders: A={angle_a}°, B={angle_b}°")
            return DualEncoderValue(angle_a, angle_b)
        except (IndexError, ValueError) as e:
            Debug.error(f"Failed to parse dual encoder response: '{response}' ({e})")
            return None

    def _parse_diagnostics_response(
        self, response: str, encoder_id: EncoderID
    ) -> Optional[dict[str, Any]]:
        """DIAG:ENC? → 'compH=N,compL=N,cof=N,ocf=N,agc=N' → typed dict."""
        try:
            kv: dict[str, str] = {}
            for token in response.strip().split(","):
                if "=" in token:
                    k, _, v = token.partition("=")
                    kv[k.strip()] = v.strip()
            if len(kv) < 5:
                Debug.error(f"Invalid diagnostics response: '{response}'")
                return None
            diag: dict[str, Any] = {
                "compHigh": bool(int(kv.get("compH", "0"))),
                "compLow": bool(int(kv.get("compL", "0"))),
                "cof": bool(int(kv.get("cof", "0"))),
                "ocf": bool(int(kv.get("ocf", "0"))),
                "agc": int(kv.get("agc", "0")),
            }
            Debug.debug(f"Diagnostics {encoder_id.value}: {diag}")
            return diag
        except (IndexError, ValueError) as e:
            Debug.error(f"Failed to parse diagnostics: '{response}' ({e})")
            return None
