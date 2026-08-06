#pragma once
#include <AS5048A.h>
#include "state.h"

// ── Hardware instances (defined in encoder.cpp) ────────────────────────────────
extern AS5048A_SPI encA;
extern AS5048A_SPI encB;

// ── Lifecycle ─────────────────────────────────────────────────────────────────
void encoderInit();

// ── EF-recovery read helpers (used by scpi.cpp) ───────────────────────────────
// Re-reads once on errorFlag and clears the flag; returns the second result.
AS5048A_SPI::FrameResult encReadAngle(AS5048A_SPI &enc);
AS5048A_SPI::FrameResult encReadMagn(AS5048A_SPI &enc);

// Utility
bool frameOk(const AS5048A_SPI::FrameResult &r);
