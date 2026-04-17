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

  // ── Continuous ADC polling ────────────────────────────────────────────────
  // Call from loop() when ready() returns true.
  void pollAdc();

  // True when DRDY pin is asserted (data ready for a new conversion result).
  bool ready() const;

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

  // Read-only access to shadow registers (for SENS:ADC:* and DIAG:ADC?).
  const ADS1220 &adcRef() const { return _adc; }

  // String representation of current mux config (for SENS:ADC:MUX?).
  const char *muxName() const;

private:
  ADS1220 _adc;
  bool _present = false;
  uint8_t _pdGainStage = 0;
  float _lastVoltage = 0.0f;
  float _lastTemperature = NAN;
  int32_t _lastRaw = 0;
  float _vrefVolts = 2.048f; // matches ADS1220 internal reference default

  // Applies the 4-bit pattern for _pdGainStage to the four GPIO pins.
  void _applyPdGainGpio(uint8_t pattern);

  // Convert a raw 24-bit ADC code to voltage using current vref and gain.
  float _computeVoltage(int32_t raw) const;
};

extern AdsSession adsSession;
