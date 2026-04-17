#include "ads_session.h"
#include "state.h"

// ── PD-TIA gain stage lookup table ────────────────────────────────────────────
// Indexed by stage number.  Each entry is a 4-bit GPIO pattern:
//   bit 0 → PDTIA_PIN_0 … bit 3 → PDTIA_PIN_3
// Adjust this table to match your physical hardware wiring.
static const uint8_t kPdGainPatterns[PDTIA_NUM_STAGES] = {
    0b0000, // stage 0 — lowest gain (all GPIO low)
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

AdsSession::AdsSession()
    : _adc(ADC_CS_PIN, ADC_DRDY_PIN)
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

  // Start in continuous conversion mode at default rate (20 SPS).
  _adc.setConversionMode(ADS1220::ConversionMode::CONTINUOUS);
  _adc.start();
  _present = true;
  return true;
}

void AdsSession::reset()
{
  if (!_present)
    return;
  _adc.reset();
  _adc.setConversionMode(ADS1220::ConversionMode::CONTINUOUS);
  _adc.start();
  _lastVoltage = 0.0f;
  _lastTemperature = NAN;
  _lastRaw = 0;
  _vrefVolts = 2.048f;
  setPdGainStage(0);
}

// ── Continuous ADC polling ────────────────────────────────────────────────────

bool AdsSession::ready() const
{
  return _present && _adc.dataReady();
}

void AdsSession::pollAdc()
{
  if (!_present)
    return;
  _lastRaw = _adc.readRaw();
  _lastVoltage = _computeVoltage(_lastRaw);
}

// ── One-shot reads ────────────────────────────────────────────────────────────

float AdsSession::takeVoltageReading()
{
  if (!_present)
    return NAN;
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
  // In continuous mode the next conversion will use the temperature sensor mux.
  if (!_adc.waitForDataReady(timeoutMs))
  {
    _adc.enableTemperatureSensor(false);
    return NAN;
  }
  float temp = _adc.readTemperature();
  _lastTemperature = temp;
  _adc.enableTemperatureSensor(false);
  return temp;
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
