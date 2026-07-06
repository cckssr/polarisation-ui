# AS5048A Encoder Debugging Guide

Complete hardware and software debugging reference for the dual-encoder goniometer bench.
Covers the AS5048A magnetic rotary encoder on SPI, the firmware SCPI interface, and the Python UI stack.

---

## 1. How the AS5048A works (and fails)

The AS5048A is a 14-bit Hall-effect magnetic rotary encoder. It measures the direction of a magnetic field using a CORDIC algorithm and reports an angle with 0.022° resolution.

### Internal signal chain

```shell
Magnet field → Hall array → Analog front-end → CORDIC → 14-bit angle register
                                    ↑
                            AGC (Automatic Gain Control)
```

Every step can introduce errors:

| Stage               | Failure mode                 | Observable symptom                              |
| ------------------- | ---------------------------- | ----------------------------------------------- |
| Magnet field        | Too weak (far away)          | `compHigh=1`, `agc < 30`, angle jitter          |
| Magnet field        | Too strong (close)           | `compLow=1`, `agc > 230`, saturation            |
| Magnet field        | Off-axis tilt                | `cof=1` (CORDIC overflow), angle = 0 or garbage |
| Hall array          | Magnet not centred over chip | Large eccentricity error, non-linearity         |
| CORDIC              | Overflow during computation  | `cof=1`                                         |
| Offset compensation | Not finished after power-on  | `ocf=0`, unreliable angle                       |
| SPI framing         | Parity error or wrong mode   | `parityOk=false`, bad read not detected         |
| SPI noise           | Glitches on shared bus       | Occasional spikes, parity errors                |

### Diagnostic register (0x3FFD)

This is the single most important register for diagnosing problems.

| Field      | Bit(s) | Meaning when set                                                |
| ---------- | ------ | --------------------------------------------------------------- |
| `compHigh` | 11     | AGC at maximum — field too **weak** (magnet too far)            |
| `compLow`  | 10     | AGC at minimum — field too **strong** (magnet too close)        |
| `cof`      | 9      | CORDIC overflow — angle is **invalid**                          |
| `ocf`      | 8      | Offset compensation finished — **must be 1** for valid readings |
| `agc`      | 7:0    | Current AGC value: 0 = max gain (weak), 255 = min gain (strong) |

**Target AGC range: 50–200.** Values near 0 or 255 indicate marginal field strength.

---

## 2. SCPI diagnostic commands

All commands below work in a serial terminal (`pio device monitor` at 115200 baud) or in the SCPI terminal tab of the debug dialog (`Ctrl+D`).

### 2.1 Immediate health check

```shell
DIAG:SELF?
```

Expected output (all subsystems healthy):

```shell
DIAG:SELF ENC:A,PASS
DIAG:SELF ENC:B,PASS
DIAG:SELF ADC,PASS
DIAG:SELF PDTIA,PASS
```

### 2.2 Full diagnostics — both encoders in one call

```shell
DIAG:ENC? BOTH
```

Example response:

```shell
compHA=0,compLA=0,cofA=0,ocfA=1,agcA=143,compHB=0,compLB=0,cofB=0,ocfB=1,agcB=167
```

Fields `*A` = encoder A (sample stage), `*B` = encoder B (detector arm).

### 2.3 Per-encoder diagnostics

```shell
DIAG:ENC? A
DIAG:ENC? B
```

Response format: `compH=N,compL=N,cof=N,ocf=N,agc=N`

### 2.4 Live diagnostic stream

Continuously stream angle + diagnostic registers for both encoders at 2 Hz:

```shell
CONF:SRC ENC:BOTH,DIAG
CONF:RATE 2
INIT:CONT ON
```

Example frame:

```shell
DATA:FRAME seq=1,tsMs=1234,angA=45.23,agcA=143,dstatA=1,angB=90.51,agcB=167,dstatB=1,stat=0
```

**`dstatX` bitmask** (decimal):

| Value | Meaning                                      |
| ----- | -------------------------------------------- |
| `1`   | OCF set — **normal operation**               |
| `3`   | OCF + COF — CORDIC overflow, angle invalid   |
| `5`   | OCF + compLow — magnet too close             |
| `9`   | OCF + compHigh — magnet too far              |
| `0`   | OCF not set — offset compensation incomplete |

Stop stream: `ABOR`

### 2.5 Parity and error-flag statistics

Enable debug mode before streaming to count errors:

```shell
SYST:DEB ON
INIT:CONT ON
```

On `ABOR` or `*RST`, the firmware prints:

```shell
DATA:STAT DUR,30000        ← elapsed ms
DATA:STAT NPTS,600         ← frames emitted
DATA:STAT PERR,0           ← SPI parity errors
DATA:STAT EERR,0           ← error-flag events
```

Any non-zero `PERR` or `EERR` count indicates a hardware problem.

### 2.6 Check zero-position registers (read current SW zero)

The software zero is applied transparently by the firmware after `CONF:ENC:ZERO A|B|BOTH`. Angles in the stream and in `MEAS:ENC:ANGL?` are both zero-referenced consistently. To clear:

```shell
*RST           ← resets zero offsets (volatile) and all config
```

### 2.7 Clear latched error flags

If the encoder latches an error flag (e.g. after a power glitch), clear it:

```shell
CONF:ENC:ERR A
CONF:ENC:ERR B
CONF:ENC:ERR BOTH
```

Then re-read to confirm the flag is gone:

```shell
DIAG:ENC? BOTH
```

---

## 3. Hardware debugging procedure

Work through these steps in order. Stop when the problem is identified.

### Step 1 — Read the diagnostic register (30 seconds)

Connect via serial terminal or debug dialog and run:

```shell
DIAG:ENC? BOTH
```

**If `ocf=0`:** The chip has not finished internal calibration. Power-cycle the Arduino and wait 500 ms before querying again.

**If `compHigh=1` (agc ≈ 0–30):** The magnetic field is too weak.  
→ See §3.1 — Magnet placement: weak field.

**If `compLow=1` (agc ≈ 230–255):** The magnetic field is too strong.  
→ See §3.2 — Magnet placement: strong field.

**If `cof=1`:** CORDIC overflow — angle is completely invalid.  
→ See §3.3 — CORDIC overflow (magnet off-axis).

**If all flags clear and agc ≈ 50–200:** Field strength is fine. Jump to §3.4 (SPI integrity).

---

### 3.1 Magnet placement: weak field

`compHigh=1` means the AGC is at maximum gain and still cannot see the field. The magnet is either too far away, the wrong polarity, or missing.

**Checklist:**

1. **Distance:** The AS5048A datasheet specifies a nominal air gap of 0.5–3 mm depending on magnet diameter and magnetisation. Use a feeler gauge; anything beyond 3 mm will be unreliable.
2. **Magnet polarity:** The magnet must be magnetised axially (pole faces towards the chip), not diametrically. Check with a compass or Hall probe — the field must be perpendicular to the chip surface, not parallel to it.
3. **Magnet diameter:** Smaller diameter magnets produce weaker fields at the same distance. Use at minimum a Ø6 mm × 2.5 mm N52 diametrically (axially) magnetised magnet.
4. **Magnet centring:** The chip must be within 0.25 mm of the magnet's rotation axis. Eccentricity degrades both field strength and linearity.

**Live test:** While watching `agcA` in the stream (`CONF:SRC ENC:BOTH,DIAG` + `INIT:CONT ON`), slowly move the magnet closer in 0.5 mm steps. Stop when `agcA` is in the 100–180 range.

---

### 3.2 Magnet placement: strong field

`compLow=1` means the field is saturating the Hall array. The magnet is too close or too strong.

**Fix:** Increase air gap in 0.5 mm increments while watching `agcX` in the live stream. Target 100–180.

If you cannot increase the gap (mechanical constraint), use a weaker magnet grade (N35 instead of N52) or a smaller diameter.

---

### 3.3 CORDIC overflow

`cof=1` means the AS5048A cannot compute a valid angle. This happens when the magnetic field vector is severely tilted relative to the chip plane.

**Causes and fixes:**

| Cause                                                                        | Fix                                                                                                                    |
| ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Magnet tilted (not parallel to chip surface)                                 | Re-seat magnet on a flat face perpendicular to the rotation axis                                                       |
| Magnet off-centre laterally by > 1 mm                                        | Reposition on axis                                                                                                     |
| Two magnets too close (cross-talk)                                           | Increase separation between sample-stage and detector-arm magnet assemblies; add a soft-iron shield if geometry allows |
| Wrong magnet type (diametrically magnetised disc used as axially magnetised) | Replace with correct magnet                                                                                            |

**Oscilloscope test:** With `cof=1`, the AGC loop is saturated and the MISO line from the encoder will show the same data pattern on every read — a stuck value. A scope on MISO (with CS_A or CS_B as trigger) will confirm this: the 14-bit DATA field repeats identically instead of varying.

---

### 3.4 SPI signal integrity

If the diagnostic flags are clean but angles are unstable, the problem is in the SPI bus.

**Setup:** Enable SYST:DEB ON, stream at 20 Hz for 60 seconds, read stats on ABOR.

```shell
SYST:DEB ON
CONF:SRC ENC:BOTH
CONF:RATE 20
INIT:CONT ON
```

(wait 60 s)

```shell
ABOR
```

Expected: `PERR=0`, `EERR=0`.

**If PERR > 0 (parity errors):**

The SPI master received a corrupted frame from the encoder. This is almost always a wiring problem at 1 MHz.

Checklist:

- **Wire length:** Keep SPI wires < 20 cm on a breadboard. At 1 MHz, capacitive loading on long wires causes ringing on MISO.
- **Ground:** Confirm Arduino GND and encoder GND are on the same node with a low-resistance path (< 1 Ω).
- **Decoupling:** Place a 100 nF ceramic capacitor from VCC to GND directly at each AS5048A pin 1 (VDD3.3) and pin 8 (GND).
- **CS crosstalk:** CS_A (pin 10) and CS_B (pin 9) are adjacent GPIO pins on the shared encoder SPI bus. ADC_CS (pin 4) is on the ADS1220's separate HSPI bus, so it cannot crosstalk with the encoder CS lines electrically, but a shared breadboard rail can still couple noise between them. If removing SRC_ADC from the stream eliminates parity errors, suspect rail/ground coupling from the ADC transactions. Add a 33 Ω series resistor on each CS line.
- **SPI mode:** The AS5048A uses SPI Mode 1 (CPOL=0, CPHA=1). Confirm with a logic analyser — data samples on the falling edge of SCLK.

**Oscilloscope probe points (per CS):**

| Signal        | Where             | What to check                                                             |
| ------------- | ----------------- | ------------------------------------------------------------------------- |
| CS_A (pin D10) | Arduino → encoder | Low during transaction, no glitches while CS_B or ADC_CS switches         |
| SCLK          | Shared bus        | Clean edges, no ringing >10% of amplitude between transitions             |
| MISO          | Encoder → Arduino | Stable during clock pulses; goes high-Z (or holds last bit) after CS high |
| MOSI          | Arduino → encoder | Stable during clock pulses                                                |

**Probing during streaming:** The scope will show rapid CS toggling as ENC_A, ENC_B, and ADC are read in sequence. This is normal. Trigger on CS_A and check only the MISO data for encoder A's transactions.

**If EERR > 0 (error-flag events):**

The AS5048A internally set its error flag during normal operation. This means the chip itself detected an error (e.g. field temporarily out of range, power-supply glitch, or temperature spike). Run for longer and check if it correlates with:

- Physical vibration of the setup (field disturbance)
- Other USB devices connecting/disconnecting (power supply noise on 3.3 V rail)
- ADS1220 SPI transactions (if CS_ADC glitches)

---

### 3.5 Power supply

The AS5048A requires a stable 3.3 V supply. The Arduino Nano ESP32's 3.3 V LDO is shared with the ESP32 chip, which has significant current spikes during WiFi/BT radio activity (even if unused). These can inject noise into the 3.3 V rail.

**Measurement:** Scope the AS5048A VDD pin (directly at the chip) with 10 mV/div. Any spikes > 50 mV that correlate with error events indicate a power integrity problem.

**Fix:** Add a 10 µF electrolytic + 100 nF ceramic in parallel directly at each encoder's VDD/GND pins.

---

### 3.6 Thermal effects

The AS5048A AGC value changes with temperature because the magnet's field strength changes (NdFeB magnets lose ~0.1% of their field per °C). If the bench runs for hours and angles drift, check if the AGC value has shifted.

Monitor AGC over time with the diagnostic stream. A drift of ±10 in AGC over an hour is normal; more than ±30 suggests the magnet is heating up (from a nearby motor or power supply) and the field is leaving the COMP range.

---

## 4. Software debugging procedure

### 4.1 Verify stream values match expected angles

With the stage physically at 0°, zero both encoders:

```shell
CONF:ENC:ZERO BOTH
```

Then stream and read:

```shell
CONF:SRC ENC:BOTH
INIT:CONT ON
```

Both `angA` and `angB` should be ~0.00° after zeroing. If they're not zero in the stream but `MEAS:ENC:ANGL? BOTH` returns 0, the firmware had the SW-zero bug — this is fixed in the current firmware (v2.1.0).

### 4.2 Verify parity + EF checking is active

Send a bad command to trigger an error flag, then stream:

```shell
CONF:SRC ENC:BOTH,DIAG
INIT:CONT ON
```

Introduce a loose connection on MISO (touch and release). Frames with bad parity will show `stat=1` (ENC_A parity error) or `stat=2` (ENC_B). Without the fix, bad frames would have silently passed through `readAngleDeg()`.

### 4.3 Interpret the `stat` field

The `stat` byte in each `DATA:FRAME` is a bitmask:

| Bit | Mask   | Meaning                   |
| --- | ------ | ------------------------- |
| 0   | `0x01` | Encoder A parity error    |
| 1   | `0x02` | Encoder B parity error    |
| 2   | `0x04` | Encoder A error flag (EF) |
| 3   | `0x08` | Encoder B error flag (EF) |

A frame with `stat≠0` delivers `angX=nan`. The UI spike filter will reject it.

### 4.4 Interpret the `dstatX` field

`dstatA` and `dstatB` are only present when `CONF:SRC` includes `DIAG`.

| Bit | Mask   | Meaning                                       |
| --- | ------ | --------------------------------------------- |
| 0   | `0x01` | OCF — offset compensation finished (want = 1) |
| 1   | `0x02` | COF — CORDIC overflow (bad)                   |
| 2   | `0x04` | compLow — strong field (magnet too close)     |
| 3   | `0x08` | compHigh — weak field (magnet too far)        |

Healthy frame: `dstatA=1` (only OCF set). Any other bit set indicates a hardware issue.

### 4.5 UI: check the debug dialog

Open the debug dialog (`Ctrl+D` in the main window):

1. **Messwerte tab** — select encoder A / B / Both from the combo box; LEDs for COMP_H, COMP_L, COF, OCF update every 500 ms while the dialog is open (faster than the background 5 s poll). AGC is shown on a 0–255 progress bar.
2. **ADS1220 tab** — ADC register dump, voltage/temperature readouts, and PD-TIA gain-stage control.
3. **Raw Stream tab** — live `DATA:FRAME` log. Verify `angA`, `angB` change smoothly and `stat=0` on every frame.
4. **Selbsttest tab** — click "Selbsttest ausführen (DIAG:SELF?)" to run the full self-test; each subsystem line is shown PASS/FAIL/ABSENT.
5. **System tab** — firmware version, uptime, error queue.
6. **SCPI Terminal tab** — run arbitrary commands from the UI.

### 4.6 Check the spike filter is not masking bad readings

If the UI displays stable angles but they are wrong, check whether the spike filter is suppressing large jumps. The default threshold is in the acquisition settings dialog. If the magnet placement produces occasional 180° jumps (common with off-axis placement), the spike filter catches them but the underlying problem is still the magnet.

Set `SYST:DEB ON` and check `DATA:STAT EERR` after a streaming run. If EERR > 0, the encoder is experiencing real hardware errors, not just UI filtering artefacts.

### 4.7 Verify serial timing is not causing gaps

With the non-blocking serial accumulator now in the firmware, commands typed during streaming should not stall frames. To verify:

1. Start streaming: `CONF:RATE 20`, `INIT:CONT ON`
2. Send several SCPI commands quickly in the terminal
3. Check `seq=` values in the Raw Stream tab — gaps larger than 1 indicate missed frames

---

## 5. Oscilloscope procedures

### 5.1 Setup

- Probe ground clip at Arduino GND (not the USB connector shield).
- Use ×10 probes if cable is long; at 1 MHz this reduces capacitive loading.
- Trigger: falling edge of CS_A (D10) or CS_B (D9).

### 5.2 Normal SPI transaction (pipelined read)

One `encReadAngle()` call produces two 16-bit SPI transactions:

```shell
Transaction 1: CS low → 16 SCLK pulses → CS high   (sends READ ANGLE command)
1 µs gap
Transaction 2: CS low → 16 SCLK pulses → CS high   (sends NOP, receives ANGLE data)
```

At 1 MHz: each 16-bit transaction takes 16 µs. Total per read: ~34 µs.  
At 100 kHz (old setting): each took 160 µs. Total: ~322 µs.

**What to look for:** CS_A goes low cleanly (no pre-ringing), SCLK is stable, MISO is valid during sampling edges (falling edge of SCLK in Mode 1). After CS goes high, MISO holds the last bit value — it should not float.

### 5.3 Detecting parity errors on the scope

Set the scope to capture MISO at 16 bit resolution and manually count bits. The AS5048A response frame is:

```shell
[PAR][EF][DATA13..DATA0]
```

- Bit 15 (first received): even parity over all 16 bits
- Bit 14: Error Flag (1 = error latched)
- Bits 13–0: 14-bit angle

If the PAR bit does not make the total count of 1-bits even, the firmware will set `stat |= 0x01`. You can confirm this by counting manually on the scope and comparing to what the firmware reports.

### 5.4 Isolating cross-talk between CS lines

Probe CS_A while triggering on a falling edge of CS_B. Any pulse visible on CS_A during a CS_B transaction is cross-talk. Similarly probe CS_B while triggering on CS_A.

On a breadboard, pins D9/D10 (the two encoder CS lines) are adjacent. Add 33 Ω series resistors on both CS lines (between Arduino pin and wire-to-sensor) to dampen capacitive coupling.

### 5.5 Checking for floating MISO

When no CS is asserted, MISO should be either driven by the last-selected device or tristated (depending on the AS5048A's output driver). If MISO floats (random oscillation around mid-rail), another SPI device's unrelated CS assertion can couple into MISO and look like a false parity check. To confirm:

- Disconnect the ADS1220 CS (hold ADC_CS high permanently) and re-run the parity error stats test.
- If `PERR` drops to zero, the ADC is interfering with the encoder MISO.
- Fix: add a pull-up resistor (10 kΩ) on MISO between the last encoder in the daisy chain and the Arduino.

---

## 6. Quick-reference card

```shell
# --- Instant health check (copy-paste into pio device monitor) ---

DIAG:ENC? BOTH
# Look for: cofA=0, compHA=0, compLA=0, ocfA=1, agcA=50..200
# Same for B.

# --- Live AGC monitoring while moving magnet ---

CONF:SRC ENC:BOTH,DIAG
CONF:RATE 5
INIT:CONT ON
# Move magnet, watch agcA/agcB until both ≈ 100..180, dstatA=1, dstatB=1
ABOR

# --- Check for SPI errors over 60 s ---

SYST:DEB ON
CONF:SRC ENC:BOTH
CONF:RATE 20
INIT:CONT ON
# wait 60 seconds
ABOR
# Should print: DATA:STAT PERR,0 and DATA:STAT EERR,0

# --- Zero both encoders after mechanical positioning ---

CONF:ENC:ZERO BOTH

# --- Clear latched error flags ---

CONF:ENC:ERR BOTH
```

---

## 7. Fault decision tree

```shell
DIAG:ENC? BOTH
│
├─ ocf=0 → power-cycle, wait 500 ms, re-query
│
├─ compHigh=1 or agc < 30
│    → magnet too far or wrong polarity
│    → reduce air gap in 0.5 mm steps until agc ≈ 100–180
│
├─ compLow=1 or agc > 230
│    → magnet too close or too strong
│    → increase air gap
│
├─ cof=1
│    → magnet off-axis or tilted
│    → reposition magnet, ensure it rotates on axis
│
└─ all flags clear, agc ≈ 50–200
     │
     ├─ angles still unstable → run SYST:DEB ON + 60 s stream
     │    ├─ PERR > 0 → SPI wiring fault (length, capacitance, CS crosstalk)
     │    ├─ EERR > 0 → power supply noise or environmental vibration
     │    └─ PERR=0, EERR=0 → scope CS lines for crosstalk (§5.4)
     │
     └─ angles stable but wrong value
          → check software zero: CONF:ENC:ZERO BOTH, verify angA≈0 after
          → check sample_inverted flag in acquisition settings dialog
```
