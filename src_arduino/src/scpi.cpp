#include "scpi.h"
#include "encoder.h"
#include "ads_session.h"
#include <math.h>

// ── Parser ────────────────────────────────────────────────────────────────────

bool scpiParse(const String &line, String &header, String &param, bool &isQuery)
{
  if (line.length() == 0)
    return false;

  int sp = line.indexOf(' ');
  if (sp >= 0)
  {
    header = line.substring(0, sp);
    param = line.substring(sp + 1);
    param.trim();
  }
  else
  {
    header = line;
    param = "";
  }

  isQuery = header.endsWith("?");
  if (isQuery)
    header = header.substring(0, header.length() - 1);

  header.toUpperCase();
  param.toUpperCase();
  return true;
}

// ── Error helpers ─────────────────────────────────────────────────────────────

static void errQueryOnly(const String &h)
{
  errorQueue.push("-113,\"Undefined header; " + h + " is query-only\"");
}
static void errCmdOnly(const String &h)
{
  errorQueue.push("-113,\"Undefined header; " + h + " is command-only\"");
}
static void errNoAdc()
{
  errorQueue.push("-241,\"Hardware missing; ADS1220 not present\"");
}

// ── DATA:FRAME emitter ────────────────────────────────────────────────────────

// Monotonic frame sequence counter — wraps at 2^32 (~49 days at 1 kHz).
static uint32_t s_frameSeq = 0;

void emitDataFrame()
{
  const uint8_t src = appState.stream.sources;
  uint8_t stat = 0;

  Serial.print("DATA:FRAME seq=");
  Serial.print(++s_frameSeq);
  Serial.print(",tsMs=");
  Serial.print(millis());

  if (src & SRC_ENC_A)
  {
    AS5048A_SPI::FrameResult r = encReadAngle(encA);
    if (!r.parityOk)
      stat |= 0x01;
    if (r.errorFlag)
      stat |= 0x04;
    // Apply software zero so the streamed angle matches MEAS:ENC:ANGL? A.
    Serial.print(",angA=");
    Serial.print(frameOk(r) ? encA.applyZero(r.data14) : NAN, 2);
    if (appState.debug && !r.parityOk)
      ++acqStats.parityErrors;
    if (appState.debug && r.errorFlag)
      ++acqStats.efEvents;
    if (src & SRC_DIAG)
    {
      AS5048A_SPI::Diagnostics d = encA.readDiagnostics();
      Serial.print(",agcA=");
      Serial.print(d.agc);
      // dstatA bits: 3=compHigh, 2=compLow, 1=cof, 0=ocf
      uint8_t ds = (d.compHigh ? 0x08u : 0u) | (d.compLow ? 0x04u : 0u) | (d.cof ? 0x02u : 0u) | (d.ocf ? 0x01u : 0u);
      Serial.print(",dstatA=");
      Serial.print(ds);
    }
  }

  if (src & SRC_ENC_B)
  {
    float angB = NAN;
    if (appState.encBPresent)
    {
      AS5048A_SPI::FrameResult r = encReadAngle(encB);
      if (!r.parityOk)
        stat |= 0x02;
      if (r.errorFlag)
        stat |= 0x08;
      angB = frameOk(r) ? encB.applyZero(r.data14) : NAN;
      Serial.print(",angB=");
      Serial.print(angB, 2);
      if (src & SRC_DIAG)
      {
        AS5048A_SPI::Diagnostics d = encB.readDiagnostics();
        Serial.print(",agcB=");
        Serial.print(d.agc);
        uint8_t ds = (d.compHigh ? 0x08u : 0u) | (d.compLow ? 0x04u : 0u) | (d.cof ? 0x02u : 0u) | (d.ocf ? 0x01u : 0u);
        Serial.print(",dstatB=");
        Serial.print(ds);
      }
    }
    else
    {
      Serial.print(",angB=");
      Serial.print(angB, 2);
    }
  }

  if (src & SRC_ADC)
  {
    Serial.print(",adcV=");
    if (adsSession.adcPresent())
      Serial.print(adsSession.takeVoltageReading(), 6);
    else
      Serial.print("nan");
  }

  if (src & SRC_ADC_T)
  {
    Serial.print(",adcT=");
    if (adsSession.adcPresent())
    {
      // Blocking temperature interleave (adds ~50 ms at 20 SPS default).
      float t = adsSession.takeTemperatureReading(200);
      Serial.print(isnan(t) ? NAN : t, 2);
    }
    else
    {
      Serial.print("nan");
    }
  }

  if (src & SRC_PDTIA)
  {
    Serial.print(",pdGain=");
    Serial.print(adsSession.pdGainStage());
  }

  Serial.print(",stat=");
  Serial.println(stat);

  ++acqStats.dataPoints;
}

// ── IEEE 488.2 common commands ────────────────────────────────────────────────

static void handleIDN()
{
  Serial.println(DEVICE_MFR "," DEVICE_MODEL "," DEVICE_SERIAL "," FW_VERSION);
}

static void handleRST()
{
  if (appState.debug && appState.streaming)
  {
    acqStats.endMs = millis();
    acqStats.print();
  }
  appState.streaming = false;
  appState.singleShot = false;
  appState.stream = StreamConfig{}; // reset to defaults
  appState.debug = false;
  errorQueue.clear();
  acqStats.reset();
  adsSession.reset();
}

static void handleCLS() { errorQueue.clear(); }
static void handleTST() { Serial.println(0); }
static void handleOPCQ() { Serial.println(1); }

// ── MEASure subsystem ─────────────────────────────────────────────────────────

static void handleMeasEncAngl(const String &param)
{
  String p = (param == "") ? "BOTH" : param;

  if (p == "BOTH")
  {
    // Use encReadAngle() for EF recovery + parity check on both paths.
    AS5048A_SPI::FrameResult rA = encReadAngle(encA);
    float a = frameOk(rA) ? encA.applyZero(rA.data14) : NAN;
    float b = NAN;
    if (appState.encBPresent)
    {
      AS5048A_SPI::FrameResult rB = encReadAngle(encB);
      b = frameOk(rB) ? encB.applyZero(rB.data14) : NAN;
    }
    Serial.print(a, 4);
    Serial.print(',');
    Serial.println(b, 4);
  }
  else if (p == "A")
  {
    AS5048A_SPI::FrameResult r = encReadAngle(encA);
    Serial.println(frameOk(r) ? encA.applyZero(r.data14) : NAN, 4);
  }
  else if (p == "B")
  {
    if (!appState.encBPresent)
    {
      errorQueue.push("-241,\"Hardware missing; encoder B not present\"");
      Serial.println("nan");
    }
    else
    {
      AS5048A_SPI::FrameResult r = encReadAngle(encB);
      Serial.println(frameOk(r) ? encB.applyZero(r.data14) : NAN, 4);
    }
  }
  else
  {
    errorQueue.push("-113,\"Undefined header; expected A, B, or BOTH\"");
    Serial.println("nan");
  }
}

static void handleMeasEncMagn(const String &param)
{
  String p = (param == "") ? "BOTH" : param;

  auto readMagn = [](AS5048A_SPI &e) -> String
  {
    AS5048A_SPI::FrameResult r = encReadMagn(e);
    return frameOk(r) ? String(r.data14) : "nan";
  };

  if (p == "BOTH")
  {
    Serial.print(readMagn(encA));
    Serial.print(',');
    Serial.println(appState.encBPresent ? readMagn(encB) : "nan");
  }
  else if (p == "A")
  {
    Serial.println(readMagn(encA));
  }
  else if (p == "B")
  {
    if (!appState.encBPresent)
    {
      errorQueue.push("-241,\"Hardware missing; encoder B not present\"");
      Serial.println("nan");
    }
    else
    {
      Serial.println(readMagn(encB));
    }
  }
  else
  {
    errorQueue.push("-113,\"Undefined header; expected A, B, or BOTH\"");
    Serial.println("nan");
  }
}

static void handleMeasAdcVolt()
{
  if (!adsSession.adcPresent())
  {
    errNoAdc();
    Serial.println("nan");
    return;
  }
  Serial.println(adsSession.takeVoltageReading(), 6);
}

static void handleMeasAdcTemp()
{
  if (!adsSession.adcPresent())
  {
    errNoAdc();
    Serial.println("nan");
    return;
  }
  float t = adsSession.takeTemperatureReading(500);
  if (isnan(t))
  {
    errorQueue.push("-310,\"Measurement timeout; ADS1220 temperature conversion\"");
    Serial.println("nan");
  }
  else
  {
    Serial.println(t, 3);
  }
}

static void handleMeasAll()
{
  // Use encReadAngle() on all paths for EF recovery + parity check.
  AS5048A_SPI::FrameResult angRA = encReadAngle(encA);
  float angA = frameOk(angRA) ? encA.applyZero(angRA.data14) : NAN;

  float angB = NAN;
  AS5048A_SPI::FrameResult angRB{};
  if (appState.encBPresent)
  {
    angRB = encReadAngle(encB);
    angB = frameOk(angRB) ? encB.applyZero(angRB.data14) : NAN;
  }

  AS5048A_SPI::FrameResult magA = encReadMagn(encA);
  AS5048A_SPI::FrameResult magB{};
  if (appState.encBPresent)
    magB = encReadMagn(encB);

  float volt = adsSession.adcPresent() ? adsSession.takeVoltageReading() : NAN;

  Serial.print(millis());
  Serial.print(',');
  Serial.print(angA, 4);
  Serial.print(',');
  Serial.print(angB, 4);
  Serial.print(',');
  Serial.print(frameOk(magA) ? String(magA.data14) : "nan");
  Serial.print(',');
  Serial.print(appState.encBPresent && frameOk(magB) ? String(magB.data14) : "nan");
  Serial.print(',');
  Serial.println(volt, 6);
}

// ── CONFigure subsystem ───────────────────────────────────────────────────────

static void handleConfEncZero(const String &param)
{
  String p = (param == "") ? "A" : param;
  if (p == "BOTH")
  {
    encA.setSoftwareZero();
    if (appState.encBPresent)
      encB.setSoftwareZero();
  }
  else if (p == "A")
  {
    encA.setSoftwareZero();
  }
  else if (p == "B")
  {
    if (!appState.encBPresent)
    {
      errorQueue.push("-241,\"Hardware missing; encoder B not present\"");
    }
    else
    {
      encB.setSoftwareZero();
    }
  }
  else
  {
    errorQueue.push("-113,\"Undefined header; expected A, B, or BOTH\"");
  }
}

static void handleConfEncErr(const String &param)
{
  String p = (param == "") ? "A" : param;
  if (p == "BOTH")
  {
    encA.clearErrorFlag();
    if (appState.encBPresent)
      encB.clearErrorFlag();
  }
  else if (p == "A")
  {
    encA.clearErrorFlag();
  }
  else if (p == "B")
  {
    if (!appState.encBPresent)
    {
      errorQueue.push("-241,\"Hardware missing; encoder B not present\"");
    }
    else
    {
      encB.clearErrorFlag();
    }
  }
  else
  {
    errorQueue.push("-113,\"Undefined header; expected A, B, or BOTH\"");
  }
}

// ── ADC mux token → enum ──────────────────────────────────────────────────────

static bool parseMux(const String &tok, ADS1220::Mux &out)
{
  if (tok == "DIFF01")
  {
    out = ADS1220::Mux::AIN0_AIN1;
    return true;
  }
  if (tok == "AIN0_AIN2")
  {
    out = ADS1220::Mux::AIN0_AIN2;
    return true;
  }
  if (tok == "AIN0_AIN3")
  {
    out = ADS1220::Mux::AIN0_AIN3;
    return true;
  }
  if (tok == "AIN1_AIN2")
  {
    out = ADS1220::Mux::AIN1_AIN2;
    return true;
  }
  if (tok == "AIN1_AIN3")
  {
    out = ADS1220::Mux::AIN1_AIN3;
    return true;
  }
  if (tok == "DIFF23")
  {
    out = ADS1220::Mux::AIN2_AIN3;
    return true;
  }
  if (tok == "AIN1_AIN0")
  {
    out = ADS1220::Mux::AIN1_AIN0;
    return true;
  }
  if (tok == "AIN3_AIN2")
  {
    out = ADS1220::Mux::AIN3_AIN2;
    return true;
  }
  if (tok == "CH0")
  {
    out = ADS1220::Mux::AIN0_AVSS;
    return true;
  }
  if (tok == "CH1")
  {
    out = ADS1220::Mux::AIN1_AVSS;
    return true;
  }
  if (tok == "CH2")
  {
    out = ADS1220::Mux::AIN2_AVSS;
    return true;
  }
  if (tok == "CH3")
  {
    out = ADS1220::Mux::AIN3_AVSS;
    return true;
  }
  return false;
}

static void handleConfAdcMux(const String &param)
{
  if (!adsSession.adcPresent())
  {
    errNoAdc();
    return;
  }
  ADS1220::Mux mux;
  if (parseMux(param, mux))
    adsSession.setMux(mux);
  else
    errorQueue.push("-113,\"Undefined header; unknown MUX: " + param + "\"");
}

static void handleConfAdcGain(const String &param)
{
  if (!adsSession.adcPresent())
  {
    errNoAdc();
    return;
  }
  static const struct
  {
    int val;
    ADS1220::Gain g;
  } kTable[] = {
      {1, ADS1220::Gain::G1},
      {2, ADS1220::Gain::G2},
      {4, ADS1220::Gain::G4},
      {8, ADS1220::Gain::G8},
      {16, ADS1220::Gain::G16},
      {32, ADS1220::Gain::G32},
      {64, ADS1220::Gain::G64},
      {128, ADS1220::Gain::G128},
  };
  int v = param.toInt();
  for (auto &e : kTable)
  {
    if (e.val == v)
    {
      adsSession.setGain(e.g);
      return;
    }
  }
  errorQueue.push("-222,\"Data out of range; gain must be 1|2|4|8|16|32|64|128\"");
}

static void handleConfAdcRate(const String &param)
{
  if (!adsSession.adcPresent())
  {
    errNoAdc();
    return;
  }
  static const struct
  {
    int sps;
    ADS1220::DataRate dr;
  } kTable[] = {
      {20, ADS1220::DataRate::DR0},
      {45, ADS1220::DataRate::DR1},
      {90, ADS1220::DataRate::DR2},
      {175, ADS1220::DataRate::DR3},
      {330, ADS1220::DataRate::DR4},
      {600, ADS1220::DataRate::DR5},
      {1000, ADS1220::DataRate::DR6},
  };
  int v = param.toInt();
  for (auto &e : kTable)
  {
    if (e.sps == v)
    {
      adsSession.setDataRate(e.dr);
      return;
    }
  }
  errorQueue.push("-222,\"Data out of range; rate must be 20|45|90|175|330|600|1000\"");
}

static void handleConfAdcMode(const String &param)
{
  if (!adsSession.adcPresent())
  {
    errNoAdc();
    return;
  }
  if (param == "NORM")
    adsSession.setOperatingMode(ADS1220::OperatingMode::NORMAL);
  else if (param == "TURBO")
    adsSession.setOperatingMode(ADS1220::OperatingMode::TURBO);
  else
    errorQueue.push("-113,\"Undefined header; expected NORM or TURBO\"");
}

static void handleConfAdcFir(const String &param)
{
  if (!adsSession.adcPresent())
  {
    errNoAdc();
    return;
  }
  if (param == "OFF")
    adsSession.setFIRFilter(ADS1220::FIRFilter::NONE);
  else if (param == "50")
    adsSession.setFIRFilter(ADS1220::FIRFilter::HZ50);
  else if (param == "60")
    adsSession.setFIRFilter(ADS1220::FIRFilter::HZ60);
  else if (param == "BOTH")
    adsSession.setFIRFilter(ADS1220::FIRFilter::HZ50_60);
  else
    errorQueue.push("-113,\"Undefined header; expected OFF|50|60|BOTH\"");
}

static void handleConfAdcVref(const String &param)
{
  if (!adsSession.adcPresent())
  {
    errNoAdc();
    return;
  }
  if (param == "INT")
    adsSession.setVoltageRef(ADS1220::VoltageRef::INTERNAL, 2.048f);
  else if (param == "EXT")
    adsSession.setVoltageRef(ADS1220::VoltageRef::EXT_REFP0, 2.5f);
  else if (param == "AVDD")
    adsSession.setVoltageRef(ADS1220::VoltageRef::AVDD_AVSS, 3.3f);
  else
    errorQueue.push("-113,\"Undefined header; expected INT|EXT|AVDD\"");
}

static void handleConfAdcTemp(const String &param)
{
  if (!adsSession.adcPresent())
  {
    errNoAdc();
    return;
  }
  if (param == "ON")
    adsSession.enableTemperature(true);
  else if (param == "OFF")
    adsSession.enableTemperature(false);
  else
    errorQueue.push("-113,\"Undefined header; expected ON or OFF\"");
}

static void handleConfAdcPwr(bool isQuery, const String &param)
{
  if (isQuery)
  {
    Serial.println(adsSession.adcPoweredDown() ? "OFF" : "ON");
    return;
  }
  if (param == "OFF")
    adsSession.powerDown();
  else if (param == "ON")
    adsSession.powerUp();
  else
    errorQueue.push("-113,\"Undefined header; expected ON or OFF\"");
}

static void handleConfPdtiaGain(bool isQuery, const String &param)
{
  if (isQuery)
  {
    Serial.print(adsSession.pdGainStage());
    Serial.print(",0b");
    uint8_t pat = adsSession.pdGainPattern();
    // Print 4-bit binary manually for clarity.
    Serial.print((pat >> 3) & 1);
    Serial.print((pat >> 2) & 1);
    Serial.print((pat >> 1) & 1);
    Serial.println(pat & 1);
    return;
  }
  int stage = param.toInt();
  if (stage < 0 || !adsSession.setPdGainStage((uint8_t)stage))
    errorQueue.push("-222,\"Data out of range; stage must be 0.." + String(PDTIA_NUM_STAGES - 1) + "\"");
}

// ── CONF:SRC — streaming source set ──────────────────────────────────────────

static void handleConfSrc(const String &param)
{
  uint8_t newSrc = SRC_NONE;
  String p = param;
  int start = 0;

  while (start <= (int)p.length())
  {
    int comma = p.indexOf(',', start);
    String tok;
    if (comma < 0)
    {
      tok = p.substring(start);
      start = (int)p.length() + 1;
    }
    else
    {
      tok = p.substring(start, comma);
      start = comma + 1;
    }
    tok.trim();
    if (tok == "ENC:A")
      newSrc |= SRC_ENC_A;
    else if (tok == "ENC:B")
    {
      if (!appState.encBPresent)
      {
        errorQueue.push("-241,\"Hardware missing; encoder B not present\"");
        return;
      }
      newSrc |= SRC_ENC_B;
    }
    else if (tok == "ENC:BOTH")
    {
      if (!appState.encBPresent)
      {
        errorQueue.push("-241,\"Hardware missing; encoder B not present\"");
        return;
      }
      newSrc |= SRC_ENC_A | SRC_ENC_B;
    }
    else if (tok == "ADC")
      newSrc |= SRC_ADC;
    else if (tok == "ADC:T")
      newSrc |= SRC_ADC_T;
    else if (tok == "PDTIA")
      newSrc |= SRC_PDTIA;
    else if (tok == "DIAG")
      newSrc |= SRC_DIAG;
    else if (tok.length() > 0)
    {
      errorQueue.push("-113,\"Undefined header; unknown source: " + tok + "\"");
      return;
    }
  }
  appState.stream.sources = newSrc;
}

// ── CONF:RATE — streaming rate (Hz) ──────────────────────────────────────────

static void handleConfRate(bool isQuery, const String &param)
{
  if (isQuery)
  {
    Serial.println(appState.stream.rateHz);
    return;
  }
  int hz = param.toInt();
  if (hz < 1 || hz > 1000)
  {
    errorQueue.push("-222,\"Data out of range; rate must be 1-1000 Hz\"");
    return;
  }
  appState.stream.setRate((uint16_t)hz);
}

// ── SENSe — query current config ─────────────────────────────────────────────

static uint8_t adcGainValue()
{
  static const uint8_t kT[8] = {1, 2, 4, 8, 16, 32, 64, 128};
  return kT[(adsSession.adcRef().getRegister(0) >> 1) & 0x07];
}

static uint16_t adcRateValue()
{
  static const uint16_t kT[7] = {20, 45, 90, 175, 330, 600, 1000};
  uint8_t idx = (adsSession.adcRef().getRegister(1) >> 5) & 0x07;
  return (idx < 7) ? kT[idx] : 20;
}

static void handleSensAdcMux() { Serial.println(adsSession.muxName()); }
static void handleSensAdcGain() { Serial.println(adcGainValue()); }
static void handleSensAdcRate() { Serial.println(adcRateValue()); }
static void handleSensAdcMode()
{
  uint8_t m = (adsSession.adcRef().getRegister(1) >> 3) & 0x03;
  Serial.println(m == 0 ? "NORM" : (m == 2 ? "TURBO" : "DUTY"));
}
static void handleSensAdcFir()
{
  uint8_t f = (adsSession.adcRef().getRegister(2) >> 4) & 0x03;
  const char *names[] = {"OFF", "BOTH", "50", "60"};
  Serial.println(names[f]);
}
static void handleSensAdcVref()
{
  uint8_t r = (adsSession.adcRef().getRegister(2) >> 6) & 0x03;
  const char *names[] = {"INT", "EXT", "EXT_AIN", "AVDD"};
  Serial.println(names[r]);
}
static void handleSensAdcTemp()
{
  Serial.println((adsSession.adcRef().getRegister(1) & 0x02) ? "ON" : "OFF");
}
static void handleSensPdtiaGain()
{
  Serial.print(adsSession.pdGainStage());
  Serial.print(",0b");
  uint8_t pat = adsSession.pdGainPattern();
  Serial.print((pat >> 3) & 1);
  Serial.print((pat >> 2) & 1);
  Serial.print((pat >> 1) & 1);
  Serial.println(pat & 1);
}
static void handleSensSrc()
{
  const uint8_t src = appState.stream.sources;
  String s;
  if (src & SRC_ENC_A)
    s += "ENC:A,";
  if (src & SRC_ENC_B)
    s += "ENC:B,";
  if (src & SRC_ADC)
    s += "ADC,";
  if (src & SRC_ADC_T)
    s += "ADC:T,";
  if (src & SRC_PDTIA)
    s += "PDTIA,";
  if (src & SRC_DIAG)
    s += "DIAG,";
  if (s.length() > 0)
    s.remove(s.length() - 1);
  else
    s = "NONE";
  Serial.println(s);
}
static void handleSensRate() { Serial.println(appState.stream.rateHz); }

// ── INITiate / ABORt ──────────────────────────────────────────────────────────

static void stopStream()
{
  if (appState.debug && appState.streaming)
  {
    acqStats.endMs = millis();
    acqStats.print();
  }
  appState.streaming = false;
  appState.singleShot = false;
}

static void handleInitCont(bool isQuery, const String &param)
{
  if (isQuery)
  {
    Serial.println(appState.streaming ? 1 : 0);
    return;
  }
  if (param == "ON")
  {
    appState.streaming = true;
    appState.lastPollMs = millis();
    if (appState.debug)
    {
      acqStats.reset();
      acqStats.startMs = millis();
    }
  }
  else if (param == "OFF")
  {
    stopStream();
  }
  else
  {
    errorQueue.push("-102,\"Syntax error; expected: INIT:CONT ON|OFF\"");
  }
}

static void handleInit()
{
  // Single-shot: emit one frame on the next loop() tick.
  appState.singleShot = true;
}

static void handleAbor() { stopStream(); }

// ── FETCh — return last cached values ────────────────────────────────────────
// For Phase 2, FETCh commands do a fresh one-shot read (same as MEAS).
// Phase 3 can refine to true cached-only semantics.

static void handleFetcEncAngl(const String &param) { handleMeasEncAngl(param); }
static void handleFetcAdcVolt() { handleMeasAdcVolt(); }
static void handleFetcAll() { handleMeasAll(); }

// ── READ? — arm + fetch ───────────────────────────────────────────────────────

static void handleRead(const String &param)
{
  if (param == "ADC" || param == "ADC:VOLT")
  {
    handleMeasAdcVolt();
  }
  else if (param == "ADC:T" || param == "ADC:TEMP")
  {
    handleMeasAdcTemp();
  }
  else
  {
    handleMeasAll();
  }
}

// ── SYSTem subsystem ──────────────────────────────────────────────────────────

static void handleSystErr() { Serial.println(errorQueue.pop()); }
static void handleSystVers() { Serial.println(FW_VERSION); }
static void handleSystUptime() { Serial.println(millis()); }

static void handleSystDeb(bool isQuery, const String &param)
{
  if (isQuery)
  {
    Serial.println(appState.debug ? 1 : 0);
    return;
  }
  if (param == "ON" || param == "1")
    appState.debug = true;
  else if (param == "OFF" || param == "0")
    appState.debug = false;
  else
    errorQueue.push("-102,\"Syntax error; use ON, OFF, 1, or 0\"");
}

static void handleSystHelp()
{
  Serial.println("=== SCPI 2.0.0 Command Reference ===");
  Serial.println("Common: *IDN? *RST *CLS *TST? *OPC? *OPC *WAI");
  Serial.println("");
  Serial.println("MEASure (one-shot):");
  Serial.println("  MEAS:ENC:ANGL? [A|B|BOTH]    angle in deg");
  Serial.println("  MEAS:ENC:MAGN? [A|B|BOTH]    raw 14-bit magnitude");
  Serial.println("  MEAS:ADC:VOLT?               voltage (V)");
  Serial.println("  MEAS:ADC:TEMP?               temperature (degC)");
  Serial.println("  MEAS:ALL?                    tsMs,angA,angB,magA,magB,volt");
  Serial.println("");
  Serial.println("CONFigure/Query:");
  Serial.println("  CONF:ENC:ZERO A|B|BOTH       set software zero");
  Serial.println("  CONF:ENC:ERR  A|B|BOTH       clear error flag");
  Serial.println("  CONF:ADC:MUX  DIFF01|CH0|CH1|CH2|CH3|...");
  Serial.println("  CONF:ADC:MUX?                query current MUX setting");
  Serial.println("  CONF:ADC:GAIN 1|2|4|8|16|32|64|128");
  Serial.println("  CONF:ADC:GAIN?               query current gain");
  Serial.println("  CONF:ADC:RATE 20|45|90|175|330|600|1000");
  Serial.println("  CONF:ADC:RATE?               query current rate (SPS)");
  Serial.println("  CONF:ADC:MODE NORM|TURBO");
  Serial.println("  CONF:ADC:MODE?               query current mode");
  Serial.println("  CONF:ADC:FIR  OFF|50|60|BOTH");
  Serial.println("  CONF:ADC:FIR?                query current FIR filter");
  Serial.println("  CONF:ADC:VREF INT|EXT|AVDD");
  Serial.println("  CONF:ADC:VREF?               query current voltage ref");
  Serial.println("  CONF:ADC:TEMP ON|OFF");
  Serial.println("  CONF:ADC:TEMP?               query temp measurement state");
  Serial.println("  CONF:ADC:PWR  ON|OFF         hardware power-down | up (inhibits auto-recovery)");
  Serial.println("  CONF:ADC:PWR?                ON|OFF");
  Serial.println("  CONF:PDTIA:GAIN <stage>");
  Serial.println("  CONF:PDTIA:GAIN?             stage,0b<bits>");
  Serial.println("  CONF:SRC ENC:A|ENC:B|ENC:BOTH|ADC|ADC:T|PDTIA|DIAG");
  Serial.println("  CONF:SRC?                    query active sources");
  Serial.println("  CONF:RATE <hz>               stream rate 1-1000 Hz");
  Serial.println("  CONF:RATE?                   query current rate");
  Serial.println("");
  Serial.println("INITiate/ABORt:");
  Serial.println("  INIT:CONT ON|OFF  INIT:CONT?  INIT  ABOR");
  Serial.println("");
  Serial.println("FETCh (cached reads):");
  Serial.println("  FETC:ENC:ANGL? [A|B|BOTH]");
  Serial.println("  FETC:ADC:VOLT?");
  Serial.println("  FETC:ALL?");
  Serial.println("");
  Serial.println("READ? (one-shot reads):");
  Serial.println("  READ? [ADC|ADC:T]");
  Serial.println("");
  Serial.println("Streaming:");
  Serial.println("  DATA:FRAME seq=..,tsMs=..,angA=..,angB=..,adcV=..,adcT=..,pdGain=..,agcA=..,dstatA=..,agcB=..,dstatB=..,stat=..");
  Serial.println("  (DIAG adds agcA/agcB/dstatA/dstatB to each DATA:FRAME)");
  Serial.println("");
  Serial.println("SYSTem:");
  Serial.println("  SYST:ERR?      next queued error");
  Serial.println("  SYST:VERS?     firmware version");
  Serial.println("  SYST:UPTIME?   milliseconds since boot");
  Serial.println("  SYST:DEB ON|OFF|?");
  Serial.println("  SYST:HELP?     this message");
  Serial.println("");
  Serial.println("DIAGnostic:");
  Serial.println("  DIAG:ENC? [A|B|BOTH]");
  Serial.println("  DIAG:ADC?");
  Serial.println("  DIAG:PDTIA?");
  Serial.println("  DIAG:SELF?");
  Serial.println("====================================");
}

// ── DIAGnostic subsystem ──────────────────────────────────────────────────────

static void printDiagLine(const AS5048A_SPI::Diagnostics &d)
{
  Serial.print("compH=");
  Serial.print(d.compHigh);
  Serial.print(",compL=");
  Serial.print(d.compLow);
  Serial.print(",cof=");
  Serial.print(d.cof);
  Serial.print(",ocf=");
  Serial.print(d.ocf);
  Serial.print(",agc=");
  Serial.println(d.agc);
}

static void handleDiagEnc(const String &param)
{
  String p = (param == "") ? "A" : param;

  if (p == "BOTH")
  {
    // Single response line with A and B fields interleaved for easy parsing.
    AS5048A_SPI::Diagnostics dA = encA.readDiagnostics();
    Serial.print("compHA=");
    Serial.print(dA.compHigh);
    Serial.print(",compLA=");
    Serial.print(dA.compLow);
    Serial.print(",cofA=");
    Serial.print(dA.cof);
    Serial.print(",ocfA=");
    Serial.print(dA.ocf);
    Serial.print(",agcA=");
    Serial.print(dA.agc);
    if (appState.encBPresent)
    {
      AS5048A_SPI::Diagnostics dB = encB.readDiagnostics();
      Serial.print(",compHB=");
      Serial.print(dB.compHigh);
      Serial.print(",compLB=");
      Serial.print(dB.compLow);
      Serial.print(",cofB=");
      Serial.print(dB.cof);
      Serial.print(",ocfB=");
      Serial.print(dB.ocf);
      Serial.print(",agcB=");
      Serial.println(dB.agc);
    }
    else
    {
      Serial.println(",encB=absent");
    }
    return;
  }

  AS5048A_SPI *enc = nullptr;
  if (p == "A")
    enc = &encA;
  else if (p == "B")
  {
    if (!appState.encBPresent)
    {
      errorQueue.push("-241,\"Hardware missing; encoder B not present\"");
      Serial.println("nan");
      return;
    }
    enc = &encB;
  }
  else
  {
    errorQueue.push("-113,\"Undefined header; expected A, B, or BOTH\"");
    Serial.println("nan");
    return;
  }
  printDiagLine(enc->readDiagnostics());
}

static void handleDiagAdc()
{
  if (!adsSession.adcPresent())
  {
    errNoAdc();
    Serial.println("ABSENT");
    return;
  }
  const ADS1220 &adc = adsSession.adcRef();
  Serial.print("reg0=0x");
  Serial.print(adc.getRegister(0), HEX);
  Serial.print(",reg1=0x");
  Serial.print(adc.getRegister(1), HEX);
  Serial.print(",reg2=0x");
  Serial.print(adc.getRegister(2), HEX);
  Serial.print(",reg3=0x");
  Serial.print(adc.getRegister(3), HEX);
  Serial.print(",drdy=");
  Serial.print(adsSession.ready() ? 1 : 0);
  Serial.print(",last_raw=0x");
  Serial.println((uint32_t)adsSession.lastRaw(), HEX);
}

static void handleDiagPdtia()
{
  Serial.print("stage=");
  Serial.print(adsSession.pdGainStage());
  Serial.print(",pattern=0b");
  uint8_t pat = adsSession.pdGainPattern();
  Serial.print((pat >> 3) & 1);
  Serial.print((pat >> 2) & 1);
  Serial.print((pat >> 1) & 1);
  Serial.println(pat & 1);
}

static void handleDiagSelf()
{
  // ENC A
  {
    AS5048A_SPI::FrameResult r = encReadAngle(encA);
    Serial.print("DIAG:SELF ENC:A,");
    Serial.println(frameOk(r) ? "PASS" : "FAIL");
  }
  // ENC B
  if (appState.encBPresent)
  {
    AS5048A_SPI::FrameResult r = encReadAngle(encB);
    Serial.print("DIAG:SELF ENC:B,");
    Serial.println(frameOk(r) ? "PASS" : "FAIL");
  }
  else
  {
    Serial.println("DIAG:SELF ENC:B,ABSENT");
  }
  // ADC
  Serial.print("DIAG:SELF ADC,");
  Serial.println(adsSession.adcPresent() ? "PASS" : "ABSENT");
  // PDTIA (GPIOs are always present — just verify they're outputs by attempting a write)
  adsSession.setPdGainStage(adsSession.pdGainStage()); // re-apply, no-op if OK
  Serial.println("DIAG:SELF PDTIA,PASS");
}

// ── Main dispatcher ───────────────────────────────────────────────────────────

void scpiDispatch(const String &line)
{
  String header, param;
  bool isQuery;
  if (!scpiParse(line, header, param, isQuery))
    return;

  // ── IEEE 488.2 ─────────────────────────────────────────────────────────────
  if (header == "*IDN")
  {
    isQuery ? handleIDN() : errQueryOnly(header);
  }
  else if (header == "*RST")
  {
    !isQuery ? handleRST() : errCmdOnly(header);
  }
  else if (header == "*CLS")
  {
    !isQuery ? handleCLS() : errCmdOnly(header);
  }
  else if (header == "*TST")
  {
    isQuery ? handleTST() : errQueryOnly(header);
  }
  else if (header == "*OPC")
  {
    if (isQuery)
      handleOPCQ(); /* else: no-op (sync device) */
  }
  else if (header == "*WAI")
  {
    /* no-op */

    // ── MEASure ────────────────────────────────────────────────────────────────
  }
  else if (header == "MEAS:ENC:ANGL")
  {
    isQuery ? handleMeasEncAngl(param) : errQueryOnly(header);
  }
  else if (header == "MEAS:ENC:MAGN")
  {
    isQuery ? handleMeasEncMagn(param) : errQueryOnly(header);
  }
  else if (header == "MEAS:ADC:VOLT")
  {
    isQuery ? handleMeasAdcVolt() : errQueryOnly(header);
  }
  else if (header == "MEAS:ADC:TEMP")
  {
    isQuery ? handleMeasAdcTemp() : errQueryOnly(header);
  }
  else if (header == "MEAS:ALL")
  {
    isQuery ? handleMeasAll() : errQueryOnly(header);

    // ── CONFigure ──────────────────────────────────────────────────────────────
  }
  else if (header == "CONF:ENC:ZERO")
  {
    !isQuery ? handleConfEncZero(param) : errCmdOnly(header);
  }
  else if (header == "CONF:ENC:ERR")
  {
    !isQuery ? handleConfEncErr(param) : errCmdOnly(header);
  }
  else if (header == "CONF:ADC:MUX")
  {
    isQuery ? handleSensAdcMux() : handleConfAdcMux(param);
  }
  else if (header == "CONF:ADC:GAIN")
  {
    isQuery ? handleSensAdcGain() : handleConfAdcGain(param);
  }
  else if (header == "CONF:ADC:RATE")
  {
    isQuery ? handleSensAdcRate() : handleConfAdcRate(param);
  }
  else if (header == "CONF:ADC:MODE")
  {
    isQuery ? handleSensAdcMode() : handleConfAdcMode(param);
  }
  else if (header == "CONF:ADC:FIR")
  {
    isQuery ? handleSensAdcFir() : handleConfAdcFir(param);
  }
  else if (header == "CONF:ADC:VREF")
  {
    isQuery ? handleSensAdcVref() : handleConfAdcVref(param);
  }
  else if (header == "CONF:ADC:TEMP")
  {
    isQuery ? handleSensAdcTemp() : handleConfAdcTemp(param);
  }
  else if (header == "CONF:ADC:PWR")
  {
    handleConfAdcPwr(isQuery, param);
  }
  else if (header == "CONF:PDTIA:GAIN")
  {
    isQuery ? handleSensPdtiaGain() : handleConfPdtiaGain(isQuery, param);
  }
  else if (header == "CONF:SRC")
  {
    isQuery ? handleSensSrc() : handleConfSrc(param);
  }
  else if (header == "CONF:RATE")
  {
    handleConfRate(isQuery, param);

    // ── INITiate / ABORt – consolidated under CONF:*

    // ── INITiate / ABORt ───────────────────────────────────────────────────────
  }
  else if (header == "INIT:CONT")
  {
    handleInitCont(isQuery, param);
  }
  else if (header == "INIT")
  {
    !isQuery ? handleInit() : errCmdOnly(header);
  }
  else if (header == "ABOR")
  {
    !isQuery ? handleAbor() : errCmdOnly(header);

    // ── FETCh ──────────────────────────────────────────────────────────────────
  }
  else if (header == "FETC:ENC:ANGL")
  {
    isQuery ? handleFetcEncAngl(param) : errQueryOnly(header);
  }
  else if (header == "FETC:ADC:VOLT")
  {
    isQuery ? handleFetcAdcVolt() : errQueryOnly(header);
  }
  else if (header == "FETC:ALL")
  {
    isQuery ? handleFetcAll() : errQueryOnly(header);

    // ── READ ───────────────────────────────────────────────────────────────────
  }
  else if (header == "READ")
  {
    isQuery ? handleRead(param) : errQueryOnly(header);

    // ── SYSTem ─────────────────────────────────────────────────────────────────
  }
  else if (header == "SYST:ERR")
  {
    isQuery ? handleSystErr() : errQueryOnly(header);
  }
  else if (header == "SYST:VERS")
  {
    isQuery ? handleSystVers() : errQueryOnly(header);
  }
  else if (header == "SYST:UPTIME")
  {
    isQuery ? handleSystUptime() : errQueryOnly(header);
  }
  else if (header == "SYST:DEB")
  {
    handleSystDeb(isQuery, param);
  }
  else if (header == "SYST:HELP")
  {
    isQuery ? handleSystHelp() : errQueryOnly(header);

    // ── DIAGnostic ─────────────────────────────────────────────────────────────
  }
  else if (header == "DIAG:ENC")
  {
    isQuery ? handleDiagEnc(param) : errQueryOnly(header);
  }
  else if (header == "DIAG:ADC")
  {
    isQuery ? handleDiagAdc() : errQueryOnly(header);
  }
  else if (header == "DIAG:PDTIA")
  {
    isQuery ? handleDiagPdtia() : errQueryOnly(header);
  }
  else if (header == "DIAG:SELF")
  {
    isQuery ? handleDiagSelf() : errQueryOnly(header);
  }
  else
  {
    errorQueue.push("-113,\"Undefined header: " + header + "\"");
  }
}
