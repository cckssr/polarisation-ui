#include "encoder.h"

AS5048A_SPI encA(ENC_CS_A);
AS5048A_SPI encB(ENC_CS_B);

// ── Lifecycle ─────────────────────────────────────────────────────────────

void encoderInit()
{
  encA.begin(SPI_HZ);
  encB.begin(SPI_HZ);
  // Clear any latched EF from the previous session or power-on transient.
  encA.clearErrorFlag();
  encB.clearErrorFlag();
}

// ── EF auto-recovery helpers ──────────────────────────────────────────────

static AS5048A_SPI::FrameResult readAngleRec(AS5048A_SPI &enc)
{
  AS5048A_SPI::FrameResult r = enc.readAngleRawWithDiagnostics();
  if (r.errorFlag)
  {
    enc.clearErrorFlag();
    r = enc.readAngleRawWithDiagnostics();
  }
  return r;
}

static AS5048A_SPI::FrameResult readMagnRec(AS5048A_SPI &enc)
{
  AS5048A_SPI::FrameResult r = enc.readMagnitudeRawWithDiagnostics();
  if (r.errorFlag)
  {
    enc.clearErrorFlag();
    r = enc.readMagnitudeRawWithDiagnostics();
  }
  return r;
}

static float rawToDeg(uint16_t raw14)
{
  return (raw14 & 0x3FFFu) * (360.0f / 16384.0f);
}

static bool frameOk(const AS5048A_SPI::FrameResult &r)
{
  return r.parityOk && !r.errorFlag;
}

// ── Streaming ─────────────────────────────────────────────────────────────

void encStreamAngle(char id, AS5048A_SPI &enc)
{
  Serial.print("DATA:ANGL ");
  Serial.print(id);
  Serial.print(',');

  if (appState.debug)
  {
    AS5048A_SPI::FrameResult r = readAngleRec(enc);
    ++acqStats.readAttempts;
    if (!r.parityOk)
      ++acqStats.parityErrors;
    if (r.errorFlag)
    {
      ++acqStats.efEvents;
      errorQueue.push("-300,\"Persistent EF enc " + String(id) + "\"");
      Serial.println("NAN");
      return;
    }
    ++acqStats.dataPoints;
    Serial.print(rawToDeg(r.data14), 2);
    Serial.print(',');
    Serial.println(r.data14, DEC);
  }
  else
  {
    Serial.println(enc.readAngleDeg(), 2);
  }
}

void encStreamAngles()
{
  float a = encA.readAngleDeg();
  float b = appState.encBPresent ? encB.readAngleDeg() : 0.0f;
  Serial.print("DATA:ANGL BOTH,");
  Serial.print(a, 2);
  Serial.print(',');
  Serial.println(b, 2);
}

void encStreamMagnitude(char id, AS5048A_SPI &enc)
{
  AS5048A_SPI::FrameResult r = readMagnRec(enc);
  Serial.print("DATA:MAGN ");
  Serial.print(id);
  Serial.print(',');
  if (!frameOk(r))
  {
    errorQueue.push("-300,\"Magnitude read failed enc " + String(id) + "\"");
    Serial.println("NAN");
  }
  else
  {
    Serial.println(r.data14, DEC);
  }
}

void encStreamMagnitudes()
{
  AS5048A_SPI::FrameResult rA = readMagnRec(encA);
  AS5048A_SPI::FrameResult rB = appState.encBPresent
                                    ? readMagnRec(encB)
                                    : AS5048A_SPI::FrameResult{0, 0, false, true};
  Serial.print("DATA:MAGN BOTH,");
  Serial.print(frameOk(rA) ? String(rA.data14) : "NAN");
  Serial.print(',');
  Serial.println((appState.encBPresent && frameOk(rB)) ? String(rB.data14) : "NAN");
}

void encStreamNop()
{
  auto printNop = [](char id, const AS5048A_SPI::FrameResult &r, bool newline)
  {
    Serial.print("DATA:NOP ");
    Serial.print(id);
    Serial.print(',');
    Serial.print(r.parityOk ? "OK" : "FAIL");
    Serial.print(",0x");
    if (newline)
      Serial.println(r.raw16, HEX);
    else
      Serial.print(r.raw16, HEX);
  };
  AS5048A_SPI::FrameResult rA = encA.nop();
  if (appState.encBPresent)
  {
    AS5048A_SPI::FrameResult rB = encB.nop();
    printNop('A', rA, false);
    Serial.print(' ');
    printNop('B', rB, true);
  }
  else
  {
    printNop('A', rA, true);
  }
}

// ── SCPI handlers ─────────────────────────────────────────────────────────

// Helper: resolve "A"→encA, "B"→encB, rejects unknown; pushes error + returns nullptr.
static AS5048A_SPI *resolveEncoder(const String &param)
{
  if (param == "A")
    return &encA;
  if (param == "B")
  {
    if (!appState.encBPresent)
    {
      errorQueue.push("-241,\"Hardware missing; encoder B not present\"");
      return nullptr;
    }
    return &encB;
  }
  errorQueue.push("-113,\"Undefined header; expected A or B, got: " + param + "\"");
  return nullptr;
}

void handleMeasAngl(const String &param)
{
  if (param == "BOTH" || param == "")
  {
    float a = encA.readAngleDeg();
    float b = appState.encBPresent ? encB.readAngleDeg() : 0.0f;
    Serial.print(a, 2);
    Serial.print(',');
    Serial.println(b, 2);
    return;
  }
  AS5048A_SPI *enc = resolveEncoder(param);
  if (enc)
    Serial.println(enc->readAngleDeg(), 2);
  else
    Serial.println("NAN");
}

void handleMeasMagn(const String &param)
{
  auto readMagn = [](AS5048A_SPI &e) -> String
  {
    AS5048A_SPI::FrameResult r = readMagnRec(e);
    return frameOk(r) ? String(r.data14) : "NAN";
  };

  if (param == "BOTH" || param == "")
  {
    Serial.print(readMagn(encA));
    Serial.print(',');
    Serial.println(appState.encBPresent ? readMagn(encB) : "NAN");
    return;
  }
  AS5048A_SPI *enc = resolveEncoder(param);
  if (enc)
    Serial.println(readMagn(*enc));
  else
    Serial.println("NAN");
}

void handleConfZero(const String &param)
{
  if (param == "BOTH")
  {
    encA.setSoftwareZero();
    if (appState.encBPresent)
      encB.setSoftwareZero();
    return;
  }
  AS5048A_SPI *enc = resolveEncoder(param == "" ? "A" : param);
  if (enc)
    enc->setSoftwareZero();
}

void handleConfErr(const String &param)
{
  if (param == "BOTH")
  {
    encA.clearErrorFlag();
    if (appState.encBPresent)
      encB.clearErrorFlag();
    return;
  }
  AS5048A_SPI *enc = resolveEncoder(param == "" ? "A" : param);
  if (enc)
    enc->clearErrorFlag();
}

void handleSystDiag(const String &param)
{
  AS5048A_SPI *enc = resolveEncoder(param == "" ? "A" : param);
  if (!enc)
  {
    Serial.println("NAN,NAN,NAN,NAN,NAN");
    return;
  }

  AS5048A_SPI::Diagnostics d = enc->readDiagnostics();
  Serial.print(d.compHigh);
  Serial.print(',');
  Serial.print(d.compLow);
  Serial.print(',');
  Serial.print(d.cof);
  Serial.print(',');
  Serial.print(d.ocf);
  Serial.print(',');
  Serial.println(d.agc);
}
