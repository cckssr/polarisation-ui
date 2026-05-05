#include "encoder.h"

AS5048A_SPI encA(ENC_CS_A);
AS5048A_SPI encB(ENC_CS_B);

// ── Lifecycle ─────────────────────────────────────────────────────────────────

void encoderInit()
{
  encA.begin(SPI_HZ);
  encB.begin(SPI_HZ);
  // Clear any latched EF from the previous session or power-on transient.
  encA.clearErrorFlag();
  encB.clearErrorFlag();
}

// ── EF-recovery read helpers ──────────────────────────────────────────────────

AS5048A_SPI::FrameResult encReadAngle(AS5048A_SPI &enc)
{
  AS5048A_SPI::FrameResult r = enc.readAngleRawWithDiagnostics();
  if (r.errorFlag)
  {
    enc.clearErrorFlag();
    r = enc.readAngleRawWithDiagnostics();
  }
  return r;
}

AS5048A_SPI::FrameResult encReadMagn(AS5048A_SPI &enc)
{
  AS5048A_SPI::FrameResult r = enc.readMagnitudeRawWithDiagnostics();
  if (r.errorFlag)
  {
    enc.clearErrorFlag();
    r = enc.readMagnitudeRawWithDiagnostics();
  }
  return r;
}

// ── Utilities ─────────────────────────────────────────────────────────────────

float rawToDeg(uint16_t raw14)
{
  return (raw14 & 0x3FFFu) * (360.0f / 16384.0f);
}

bool frameOk(const AS5048A_SPI::FrameResult &r)
{
  return r.parityOk && !r.errorFlag;
}
