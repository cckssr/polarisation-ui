# SCPI Command Reference — Firmware 2.0.0

**Source of truth**: `src_arduino/src/scpi.cpp`  
**Protocol**: ASCII over USB serial, 115200 baud, LF-terminated lines  
**Breaking change from 1.x**: all 1.x commands removed; clients must check `SYST:VERS?` and refuse `< 2.0.0`.

---

## Conventions

| Symbol    | Meaning                                          |
| --------- | ------------------------------------------------ |
| `<ch>`    | `A` or `B` (encoder channel)                     |
| `[…]`     | optional parameter; default shown in description |
| `\|`      | choose one                                       |
| Responses | ASCII, comma-separated, LF-terminated            |
| `nan`     | IEEE NaN — sensor absent or read failed          |

---

## ADS1220 ADC Behavior

- **Temperature sensor**: Disabled by default to avoid interfering with voltage measurements (the internal temperature sensor input can corrupt the analog signal path). Enable on-demand via `CONF:ADC:TEMP ON` to read temperature briefly, then disable it afterward.
- **Stale data on power-up**: After power-on or `*RST`, the first ADC conversion is discarded automatically to clear any stale output buffer data.
- **DRDY pin**: Not wired on this board; polling uses software timing (50 ms at 20 SPS default, configurable via `CONF:ADC:RATE`).

---

## IEEE 488.2 Common Commands

| Command | Description                                                          |
| ------- | -------------------------------------------------------------------- |
| `*IDN?` | Identification: `MFR,MODEL,SN,FW`                                    |
| `*RST`  | Reset to defaults; stop streaming; reset ADC config and PD-TIA stage |
| `*CLS`  | Clear error queue                                                    |
| `*TST?` | Self-test — returns `0` (pass)                                       |
| `*OPC?` | Returns `1` (synchronous device, always complete)                    |
| `*OPC`  | No-op                                                                |
| `*WAI`  | No-op                                                                |

---

## MEASure — One-Shot Reads

All MEAS commands trigger a fresh hardware read.

| Command                       | Response                                    | Notes                                                                                      |
| ----------------------------- | ------------------------------------------- | ------------------------------------------------------------------------------------------ |
| `MEAS:ENC:ANGL? [A\|B\|BOTH]` | `<deg>` or `<degA>,<degB>`                  | default `BOTH`                                                                             |
| `MEAS:ENC:MAGN? [A\|B\|BOTH]` | `<raw14>` or `<raw14A>,<raw14B>`            | 14-bit unsigned                                                                            |
| `MEAS:ADC:VOLT?`              | `<volts>`                                   | uses current MUX and gain; 6 decimal places; disables temp sensor to avoid data corruption |
| `MEAS:ADC:TEMP?`              | `<degC>`                                    | enables temp sensor briefly (~50 ms at 20 SPS), then disables it                           |
| `MEAS:ALL?`                   | `<tsMs>,<angA>,<angB>,<magA>,<magB>,<volt>` | single-line snapshot                                                                       |

---
CONF:ENC:ERR BOTH
MEAS:ENC:MAGN? BOTH

## CONFigure — Setup Commands

### Encoder

| Command                    | Notes                                            |
| -------------------------- | ------------------------------------------------ |
| `CONF:ENC:ZERO A\|B\|BOTH` | Set software zero at current angle (default `A`) |
| `CONF:ENC:ERR  A\|B\|BOTH` | Clear latched error flag (default `A`)           |

### ADC (ADS1220)

| Command                          | Values                                                                                                            | Default  | Notes                                                                                              |
| -------------------------------- | ----------------------------------------------------------------------------------------------------------------- | -------- | -------------------------------------------------------------------------------------------------- |
| `CONF:ADC:MUX <mux>`             | `DIFF01` `DIFF23` `CH0` `CH1` `CH2` `CH3` `AIN0_AIN2` `AIN0_AIN3` `AIN1_AIN2` `AIN1_AIN3` `AIN1_AIN0` `AIN3_AIN2` | `DIFF01` | ADS1220 input multiplexer                                                                          |
| `CONF:ADC:GAIN <n>`              | `1 2 4 8 16 32 64 128`                                                                                            | `1`      | ADS1220 internal PGA gain                                                                          |
| `CONF:ADC:RATE <sps>`            | `20 45 90 175 330 600 1000`                                                                                       | `20`     | Sample rate (SPS)                                                                                  |
| `CONF:ADC:MODE NORM\|TURBO`      | —                                                                                                                 | `NORM`   | Normal = 256 kHz, Turbo = 512 kHz modulator                                                        |
| `CONF:ADC:FIR OFF\|50\|60\|BOTH` | —                                                                                                                 | `OFF`    | FIR filter (effective at 20 SPS only)                                                              |
| `CONF:ADC:VREF INT\|EXT\|AVDD`   | —                                                                                                                 | `INT`    | `INT`=2.048 V internal; `EXT`=REFP0/REFN0 (2.5 V nominal); `AVDD`=3.3 V nominal                    |
| `CONF:ADC:TEMP ON\|OFF`          | —                                                                                                                 | `OFF`    | Enable temperature sensor on-demand (OFF by default to prevent interference with voltage readings) |

### PD-TIA Discrete Gain

| Command                   | Response           | Notes                                                                   |
| ------------------------- | ------------------ | ----------------------------------------------------------------------- |
| `CONF:PDTIA:GAIN <stage>` | —                  | Integer `0` to `PDTIA_NUM_STAGES-1` (currently 0–4); writes 4 GPIO pins |
| `CONF:PDTIA:GAIN?`        | `<stage>,0b<bits>` | Returns current stage and the 4-bit GPIO pattern                        |

### Streaming Sources and Rate

| Command                     | Notes                                                                                                            |
| --------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| `CONF:SRC <src>[,<src>...]` | Set streaming source set. Valid tokens: `ENC:A` `ENC:B` `ENC:BOTH` `ADC` `ADC:T` `PDTIA`. Default: `ENC:A,ENC:B` |
| `CONF:RATE <hz>`            | Streaming rate 1–1000 Hz. Default: 20 Hz                                                                         |

---

## SENSe — Query Current Configuration

All `SENS:*` commands are query-only.

| Query              | Returns                                                |
| ------------------ | ------------------------------------------------------ |
| `SENS:ADC:MUX?`    | Current MUX token (e.g. `DIFF01`)                      |
| `SENS:ADC:GAIN?`   | Gain integer (e.g. `8`)                                |
| `SENS:ADC:RATE?`   | Rate in SPS (e.g. `90`)                                |
| `SENS:ADC:MODE?`   | `NORM` or `TURBO`                                      |
| `SENS:ADC:FIR?`    | `OFF`, `50`, `60`, or `BOTH`                           |
| `SENS:ADC:VREF?`   | `INT`, `EXT`, or `AVDD`                                |
| `SENS:ADC:TEMP?`   | `ON` or `OFF`                                          |
| `SENS:PDTIA:GAIN?` | `<stage>,0b<bits>`                                     |
| `SENS:SRC?`        | Comma-separated active sources, e.g. `ENC:A,ENC:B,ADC` |
| `SENS:RATE?`       | Stream rate in Hz                                      |

---

## INITiate / ABORt — Stream Control

| Command         | Notes                                                    |
| --------------- | -------------------------------------------------------- |
| `INIT:CONT ON`  | Start continuous streaming                               |
| `INIT:CONT OFF` | Stop continuous streaming                                |
| `INIT:CONT?`    | Returns `1` (streaming) or `0` (idle)                    |
| `INIT`          | Single-shot: emit one `DATA:FRAME` on the next loop tick |
| `ABOR`          | Stop streaming (alias for `INIT:CONT OFF`)               |

---

## FETCh — Return Last Cached Values

`FETC:*` returns the last internally cached value without triggering a new hardware read.  
_(Phase 2: implemented as a fresh read; Phase 3 Python client will use true cached semantics.)_

| Command                       | Response                                    |
| ----------------------------- | ------------------------------------------- |
| `FETC:ENC:ANGL? [A\|B\|BOTH]` | Last cached angle(s) in degrees             |
| `FETC:ADC:VOLT?`              | Last cached ADC voltage                     |
| `FETC:ALL?`                   | `<tsMs>,<angA>,<angB>,<magA>,<magB>,<volt>` |

---

## READ? — Arm and Fetch

`READ?` triggers a fresh conversion for the specified source and returns it.

| Command       | Notes                          |
| ------------- | ------------------------------ |
| `READ?`       | Equivalent to `MEAS:ALL?`      |
| `READ? ADC`   | Equivalent to `MEAS:ADC:VOLT?` |
| `READ? ADC:T` | Equivalent to `MEAS:ADC:TEMP?` |

---

## Streaming Frame

Emitted each interval when `INIT:CONT ON` is active, or once on `INIT`.

```
DATA:FRAME tsMs=<ms>,angA=<deg>,angB=<deg>,adcV=<V>,adcT=<C>,pdGain=<stage>,stat=<flags>
```

- Fields are **only included** for sources enabled via `CONF:SRC`.
- `tsMs` and `stat` are **always** present.
- Parsers must ignore unknown keys (forward compatibility).

### `stat` bitmask

| Bit | Meaning                         |
| --- | ------------------------------- |
| 0   | Encoder A parity error          |
| 1   | Encoder B parity error          |
| 2   | Encoder A persistent error flag |
| 3   | Encoder B persistent error flag |

### Example

```
CONF:SRC ENC:BOTH,ADC
CONF:RATE 20
INIT:CONT ON

DATA:FRAME tsMs=1234,angA=90.12,angB=180.24,adcV=1.234567,stat=0
DATA:FRAME tsMs=1284,angA=90.14,angB=180.28,adcV=1.234231,stat=0
```

---

## SYSTem

| Command            | Returns          | Notes                                                |
| ------------------ | ---------------- | ---------------------------------------------------- |
| `SYST:ERR?`        | `<code>,"<msg>"` | Pop oldest error from queue; `0,"No error"` if empty |
| `SYST:VERS?`       | `2.0.0`          | Firmware version string                              |
| `SYST:UPTIME?`     | `<ms>`           | Milliseconds since power-on                          |
| `SYST:HELP?`       | Multi-line text  | Full command summary                                 |
| `SYST:DEB ON\|OFF` | —                | Enable/disable verbose debug output                  |
| `SYST:DEB?`        | `0` or `1`       | Query debug state                                    |

---

## DIAGnostic

| Command            | Returns                                                            | Notes                               |
| ------------------ | ------------------------------------------------------------------ | ----------------------------------- |
| `DIAG:ENC? [A\|B]` | `compH=<0/1>,compL=<0/1>,cof=<0/1>,ocf=<0/1>,agc=<0-255>`          | AS5048A diagnostics register        |
| `DIAG:ADC?`        | `reg0=0x..,reg1=0x..,reg2=0x..,reg3=0x..,drdy=<0/1>,last_raw=0x..` | ADS1220 shadow register dump        |
| `DIAG:PDTIA?`      | `stage=<n>,pattern=0b<bits>`                                       | Current gain stage and GPIO pattern |
| `DIAG:SELF?`       | Multi-line `DIAG:SELF <subsystem>,PASS\|FAIL\|ABSENT`              | Cross-checks all subsystems         |

---

## Error Codes

| Code | Meaning                       |
| ---- | ----------------------------- |
| 0    | No error                      |
| -102 | Syntax error                  |
| -113 | Undefined header              |
| -222 | Data out of range             |
| -241 | Hardware missing              |
| -300 | Persistent encoder error flag |
| -310 | Measurement timeout           |

---

## Pin Assignments (configurable in `config.h`)

| Function          | Default pin |
| ----------------- | ----------- |
| Encoder A CS      | 9           |
| Encoder B CS      | 10          |
| ADS1220 CS        | 5           |
| ADS1220 DRDY      | 4           |
| PD-TIA gain bit 0 | 6           |
| PD-TIA gain bit 1 | 7           |
| PD-TIA gain bit 2 | 8           |
| PD-TIA gain bit 3 | 3           |

All SPI devices share the hardware SPI bus (MOSI/MISO/SCK). The ADS1220 operates at 4 MHz (SPI mode 1); the AS5048A at 100 kHz (SPI mode 1). `SPISettings` + `beginTransaction` prevent conflicts.

---

_Generated by Phase 2 of the polarisation-ui SCPI redesign. Regenerate after firmware changes._
