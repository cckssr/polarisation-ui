#pragma once
#include <Arduino.h>
#include "config.h"
#include "../../lib/ADS1220/ADS1220.h"

// ── AdsSession ────────────────────────────────────────────────────────────────
// Owns the ADS1220 ADC instance and the PD-TIA discrete gain selector.
// Keeps last-cached voltage/temperature for streaming frames.
// Thread model: all methods called from the Arduino main loop (no ISR).

class AdsSession
{
public:
  AdsSession();

  // Initialise ADS1220 and PD-TIA GPIO pins.
  // Returns true if the ADS1220 responds correctly (register readback OK).
  bool begin();

  // Reset ADC to power-on defaults and restart continuous conversion.
  void reset();

  // Send hardware POWERDOWN command and inhibit auto-recovery until powerUp().
  void powerDown();

  // Clear the power-down inhibit and attempt to re-initialise the ADC.
  void powerUp();

  // ── Continuous ADC polling ────────────────────────────────────────────────
  // Call from loop() when ready() returns true. Never blocks.
  void pollAdc();

  // True when DRDY pin is asserted (data ready for a new conversion result).
  bool ready() const;

  // Non-blocking temperature refresh: call unconditionally every loop() tick.
  // Internally a no-op unless ADC:T is an active stream source and a refresh
  // is due; maintains lastTemperature() via a start/wait/read state machine
  // instead of the delay()-based synchronous conversion used by
  // takeTemperatureReading(). Never blocks. Pauses pollAdc()'s normal voltage
  // polling while a conversion is in flight, since the ADS1220 can only
  // digitize one mux input (external channel vs. internal temp sensor) at a
  // time.
  void pollTemperature();

  // ── One-shot reads (synchronous, used by MEAS: commands) ─────────────────
  // Reads the last completed conversion result via RDATA command (no DRDY wait).
  // Updates and returns _lastVoltage.
  float takeVoltageReading();

  // Switches to temperature mode, waits for one conversion, switches back.
  // Returns NAN on timeout.
  float takeTemperatureReading(uint32_t timeoutMs = 200);

  // ── PD-TIA gain stage ─────────────────────────────────────────────────────
  // Returns false if stage >= PDTIA_NUM_STAGES.
  bool setPdGainStage(uint8_t stage);
  uint8_t pdGainStage() const { return _pdGainStage; }
  uint8_t pdGainPattern() const; // 4-bit GPIO pattern for current stage

  // ── Configuration setters (mirror CONF:ADC:* commands) ───────────────────
  void setMux(ADS1220::Mux mux);
  void setGain(ADS1220::Gain gain);
  void setDataRate(ADS1220::DataRate dr);
  void setOperatingMode(ADS1220::OperatingMode mode);
  void setFIRFilter(ADS1220::FIRFilter filter);
  void setVoltageRef(ADS1220::VoltageRef ref, float vrefVolts);
  void enableTemperature(bool on);

  // ── Cached state (used in streaming frames) ───────────────────────────────
  float lastVoltage() const { return _lastVoltage; }
  float lastTemperature() const { return _lastTemperature; }
  int32_t lastRaw() const { return _lastRaw; }
  bool adcPresent() const { return _present; }
  bool adcPoweredDown() const { return _inhibitRecovery; }

  // Read-only access to shadow registers (for SENS:ADC:* and DIAG:ADC?).
  const ADS1220 &adcRef() const { return _adc; }

  // String representation of current mux config (for SENS:ADC:MUX?).
  const char *muxName() const;

private:
  ADS1220 _adc;
  bool _present = false;
  bool _inhibitRecovery = false;
  uint8_t _pdGainStage = 0;
  float _lastVoltage = 0.0f;
  float _lastTemperature = NAN;
  int32_t _lastRaw = 0;
  float _vrefVolts = 2.5f;           // external reference voltage
  uint32_t _conversionPeriodMs = 50; // 1000 / data_rate_sps
  uint32_t _nextConversionMs = 0;
  uint32_t _nextRecoveryAttemptMs = 0;

  // Non-blocking recovery state: true between a successful _adc.begin() and
  // the deferred discard-read of its stale first conversion completing.
  // While true, pollAdc() skips normal voltage polling.
  bool _recovering = false;
  uint32_t _recoveryDiscardDeadlineMs = 0;

  // Non-blocking temperature state: true while a background conversion
  // (started by pollTemperature()) is in flight. While true, pollAdc() skips
  // normal voltage polling, since the mux is pointed at the internal sensor.
  bool _tempConverting = false;
  uint32_t _tempConversionDeadlineMs = 0;
  uint32_t _nextTempConversionMs = 0;

  // Applies the 4-bit pattern for _pdGainStage to the four GPIO pins.
  void _applyPdGainGpio(uint8_t pattern);

  // Convert a raw 24-bit ADC code to voltage using current vref and gain.
  float _computeVoltage(int32_t raw) const;

  // Block for one conversion period and discard the stale result. Used at
  // setup()/reset() time and by the synchronous one-shot recovery path,
  // where blocking briefly is acceptable. The runtime streaming path
  // (pollAdc()) uses the non-blocking _recovering state instead.
  void _waitForFirstConversion();

  // Apply the desired ADC configuration and remember expected register bytes.
  void _applyDefaultConfig();

  // Verify device registers match the expected configuration. Returns true
  // when device appears correctly configured and present.
  bool _verifyConfiguration();

  // Attempt to recover the ADC when it is not present (power or connection
  // loss). Returns true on successful re-init and reconfiguration.
  // blockingDiscard selects between the synchronous one-shot path (blocks
  // for the stale first conversion, used by takeVoltageReading()) and the
  // non-blocking streaming path (defers the discard to pollAdc() via
  // _recovering, used by pollAdc() itself).
  bool _attemptRecovery(bool blockingDiscard);

  // Expected configuration snapshot (copied from ADS1220 shadow registers
  // after applying configuration). Used to detect a hardware reset.
  uint8_t _expectedReg[4] = {0, 0, 0, 0};

  // Apply the firmware's default ADC configuration (gain, vref, mode,
  // conversion period) and start continuous conversions.
  void _configureAdcDefaults();

  // Schedule the next recovery attempt after a failed probe.
  void _scheduleRecoveryRetry();
};

extern AdsSession adsSession;
