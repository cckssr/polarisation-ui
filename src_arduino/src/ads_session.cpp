#include "ads_session.h"
#include "state.h"

// ── PD-TIA gain stage lookup table ────────────────────────────────────────────
// Indexed by stage number.  Each entry is a 4-bit GPIO pattern:
//   bit 0 → PDTIA_PIN_0 … bit 3 → PDTIA_PIN_3
// Adjust this table to match your physical hardware wiring.
static const uint8_t kPdGainPatterns[PDTIA_NUM_STAGES] = {
    0b0001, // stage 1
    0b0010, // stage 2
    0b0100, // stage 3
    0b1000, // stage 4 — highest gain
};

// MUX token table — index matches bits 7:4 of ADS1220 config register 0.
static const char *const kMuxNames[15] = {
    "DIFF01", // AIN0-AIN1  (default)
    "AIN0_AIN2",
    "AIN0_AIN3",
    "AIN1_AIN2",
    "AIN1_AIN3",
    "DIFF23", // AIN2-AIN3
    "AIN1_AIN0",
    "AIN3_AIN2",
    "CH0", // AIN0-AVSS
    "CH1", // AIN1-AVSS
    "CH2", // AIN2-AVSS
    "CH3", // AIN3-AVSS
    "VREF_MON",
    "AVDD_MON",
    "AVDD_HALF",
};

// ── Constructor / global instance ─────────────────────────────────────────────

// ADS1220 uses the second SPI bus (HSPI) to avoid contention with the AS5048A encoders on SPI.
static SPIClass sAdcSpi(HSPI);

AdsSession::AdsSession()
    : _adc(ADC_CS_PIN, ADC_MISO_PIN, ADC_MOSI_PIN, ADC_SCK_PIN, ADC_DRDY_PIN, sAdcSpi)
{
}

AdsSession adsSession;

// ── Lifecycle ─────────────────────────────────────────────────────────────────

bool AdsSession::begin()
{
  // Configure PD-TIA GPIO pins as outputs and apply the default (stage 0) pattern.
  pinMode(PDTIA_PIN_0, OUTPUT);
  pinMode(PDTIA_PIN_1, OUTPUT);
  pinMode(PDTIA_PIN_2, OUTPUT);
  pinMode(PDTIA_PIN_3, OUTPUT);
  _applyPdGainGpio(kPdGainPatterns[0]);
  _pdGainStage = 0;

  // Init ADS1220.  begin() resets the device and verifies register readback.
  if (!_adc.begin(ADC_SPI_HZ))
  {
    _present = false;
    return false;
  }

  // Apply required configuration: gain=1, external reference (REFP0/REFN0, 2.5 V),
  // 20 SPS, differential AIN0-AIN1.
  // Temperature sensor left OFF by default; enable on-demand via CONF:ADC:TEMP ON
  _adc.setGain(ADS1220::Gain::G1);
  _adc.setVoltageReference(ADS1220::VoltageRef::EXT_REFP0);
  _vrefVolts = 2.5f;
  _conversionPeriodMs = 50; // 20 SPS default
  _nextConversionMs = 0;

  // Start in continuous conversion mode.
  // Configure ADC defaults and snapshot expected config.
  _configureAdcDefaults();
  _present = true;

  // Wait for and discard the first conversion to clear stale output buffer data.
  _waitForFirstConversion();
  _nextConversionMs = millis() + _conversionPeriodMs;

  return true;
}

void AdsSession::_applyDefaultConfig()
{
  // After configuration calls, capture the ADS1220 shadow registers as the
  // expected device state. This lets us detect a device reset/power loss.
  for (uint8_t i = 0; i < 4; i++)
  {
    _expectedReg[i] = _adc.getRegister(i);
  }
}

bool AdsSession::_verifyConfiguration()
{
  // Read back device registers and compare to expected snapshot.
  for (uint8_t i = 0; i < 4; i++)
  {
    uint8_t val = _adc.readRegister(i);
    if (val != _expectedReg[i])
    {
      return false;
    }
  }
  return true;
}

bool AdsSession::_attemptRecovery()
{
  // Try to re-initialize the ADS1220 (useful after power/connection loss).
  if (_adc.begin(ADC_SPI_HZ))
  {
    // Re-apply default ADC configuration.
    _configureAdcDefaults();

    // Re-apply PD-TIA GPIO stage to ensure detector front-end is known state.
    _applyPdGainGpio(kPdGainPatterns[_pdGainStage]);

    // Discard first conversion and resync timing.
    _waitForFirstConversion();
    _nextConversionMs = millis() + _conversionPeriodMs;
    _nextRecoveryAttemptMs = 0;
    _present = true;
    return true;
  }
  return false;
}

void AdsSession::_configureAdcDefaults()
{
  // Apply required configuration: gain=1, external reference (REFP0/REFN0, 2.5 V),
  // 20 SPS, differential AIN0-AIN1. Keep conversion period in sync.
  _adc.setGain(ADS1220::Gain::G1);
  _adc.setVoltageReference(ADS1220::VoltageRef::EXT_REFP0);
  _vrefVolts = 2.5f;
  _conversionPeriodMs = 50; // 20 SPS default
  _nextConversionMs = 0;

  // DRDYM=1: DOUT/DRDY acts as standard SPI MISO (only driven while CS is low).
  // Without this, DRDYM=0 default drives MISO LOW on conversion-complete even
  // when CS is high, corrupting encoder reads on the shared SPI bus.
  _adc.setDRDYMode(true);

  _adc.setConversionMode(ADS1220::ConversionMode::CONTINUOUS);
  _adc.start();

  // Snapshot expected config and mark present.
  _applyDefaultConfig();
  _nextRecoveryAttemptMs = 0;
}

void AdsSession::reset()
{
  _inhibitRecovery = false;
  if (!_present)
    return;
  _adc.reset();

  // Re-apply required configuration after reset.
  _configureAdcDefaults();
  _lastVoltage = 0.0f;
  _lastTemperature = NAN;
  _lastRaw = 0;
  setPdGainStage(0);

  _waitForFirstConversion();
  _nextConversionMs = millis() + _conversionPeriodMs;
}

void AdsSession::powerDown()
{
  _inhibitRecovery = true;
  if (_present)
    _adc.powerDown();
  _present = false;
}

void AdsSession::powerUp()
{
  _inhibitRecovery = false;
  _scheduleRecoveryRetry(); // triggers _attemptRecovery() on the next pollAdc() tick
}

// ── Continuous ADC polling ────────────────────────────────────────────────────

bool AdsSession::ready() const
{
  // DRDY is not connected; use time-based polling at the configured data rate.
  // When the ADC is absent, keep waking the loop periodically so recovery can
  // still be attempted.
  if (_present)
    return millis() >= _nextConversionMs;
  return millis() >= _nextRecoveryAttemptMs;
}

void AdsSession::pollAdc()
{
  // If ADC not present, try to recover (power/connection may have returned),
  // unless a deliberate power-down is in effect.
  if (!_present)
  {
    if (_inhibitRecovery || millis() < _nextRecoveryAttemptMs)
      return;
    if (!_attemptRecovery())
    {
      _scheduleRecoveryRetry();
      return;
    }
  }

  // Verify the ADC still matches the expected configuration. If not, mark
  // as not present and let recovery logic in subsequent polls re-init it.
  if (!_verifyConfiguration())
  {
    _present = false;
    _scheduleRecoveryRetry();
    return;
  }

  _lastRaw = _adc.readRawWithCommand();
  _lastVoltage = _computeVoltage(_lastRaw);
  _nextConversionMs = millis() + _conversionPeriodMs;
}

// ── One-shot reads ────────────────────────────────────────────────────────────

float AdsSession::takeVoltageReading()
{
  if (!_present)
  {
    if (_inhibitRecovery || millis() < _nextRecoveryAttemptMs)
      return NAN;

    // Try to recover once for synchronous one-shot reads.
    if (!_attemptRecovery())
    {
      _scheduleRecoveryRetry();
      return NAN;
    }
  }
  // RDATA command returns the last completed result without a DRDY wait.
  _lastRaw = _adc.readRawWithCommand();
  _lastVoltage = _computeVoltage(_lastRaw);
  return _lastVoltage;
}

float AdsSession::takeTemperatureReading(uint32_t timeoutMs)
{
  if (!_present)
    return NAN;

  _adc.enableTemperatureSensor(true);
  // DRDY is not connected; wait one conversion period plus a safety margin.
  // Cap the wait to the caller-supplied timeoutMs.
  uint32_t waitMs = min(_conversionPeriodMs + 10, timeoutMs);
  delay(waitMs);
  float temp = _adc.readTemperature();
  _lastTemperature = temp;
  _adc.enableTemperatureSensor(false);
  return temp;
}

void AdsSession::_scheduleRecoveryRetry()
{
  // Retry at a modest cadence so we can recover after a replug without
  // hammering the SPI bus every loop iteration.
  _nextRecoveryAttemptMs = millis() + 1000;
}

// ── PD-TIA gain stage ─────────────────────────────────────────────────────────

bool AdsSession::setPdGainStage(uint8_t stage)
{
  if (stage >= PDTIA_NUM_STAGES)
    return false;
  _pdGainStage = stage;
  _applyPdGainGpio(kPdGainPatterns[stage]);
  return true;
}

uint8_t AdsSession::pdGainPattern() const
{
  return (_pdGainStage < PDTIA_NUM_STAGES) ? kPdGainPatterns[_pdGainStage] : 0;
}

void AdsSession::_applyPdGainGpio(uint8_t pattern)
{
  digitalWrite(PDTIA_PIN_0, (pattern >> 0) & 1);
  digitalWrite(PDTIA_PIN_1, (pattern >> 1) & 1);
  digitalWrite(PDTIA_PIN_2, (pattern >> 2) & 1);
  digitalWrite(PDTIA_PIN_3, (pattern >> 3) & 1);
}

// ── Configuration setters ─────────────────────────────────────────────────────

void AdsSession::setMux(ADS1220::Mux mux)
{
  if (!_present)
    return;
  _adc.setMux(mux);
}

void AdsSession::setGain(ADS1220::Gain gain)
{
  if (!_present)
    return;
  _adc.setGain(gain);
}

void AdsSession::setDataRate(ADS1220::DataRate dr)
{
  if (!_present)
    return;
  _adc.setDataRate(dr);
  // Keep conversion period in sync for time-based ready() polling.
  static const uint16_t kSps[7] = {20, 45, 90, 175, 330, 600, 1000};
  uint8_t idx = static_cast<uint8_t>(dr);
  _conversionPeriodMs = (idx < 7) ? (1000u / kSps[idx]) : 50u;
}

void AdsSession::setOperatingMode(ADS1220::OperatingMode mode)
{
  if (!_present)
    return;
  _adc.setOperatingMode(mode);
}

void AdsSession::setFIRFilter(ADS1220::FIRFilter filter)
{
  if (!_present)
    return;
  _adc.setFIRFilter(filter);
}

void AdsSession::setVoltageRef(ADS1220::VoltageRef ref, float vrefVolts)
{
  if (!_present)
    return;
  _adc.setVoltageReference(ref);
  _vrefVolts = vrefVolts;
}

void AdsSession::enableTemperature(bool on)
{
  if (!_present)
    return;
  _adc.enableTemperatureSensor(on);
}

// ── Helpers ───────────────────────────────────────────────────────────────────

void AdsSession::_waitForFirstConversion()
{
  // DRDY is not connected; wait 2× the conversion period and discard.
  delay(_conversionPeriodMs * 2);
  _adc.readRawWithCommand();
}

float AdsSession::_computeVoltage(int32_t raw) const
{
  // ADS1220: gain bits 3:1 of register 0.
  static const uint8_t kGainTable[8] = {1, 2, 4, 8, 16, 32, 64, 128};
  const float gain = static_cast<float>(kGainTable[(_adc.getRegister(0) >> 1) & 0x07]);
  return static_cast<float>(raw) * _vrefVolts / (gain * 8388608.0f);
}

const char *AdsSession::muxName() const
{
  uint8_t idx = (_adc.getRegister(0) >> 4) & 0x0F;
  if (idx < 15)
    return kMuxNames[idx];
  return "?";
}
