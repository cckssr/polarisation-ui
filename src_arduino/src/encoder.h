#pragma once
#include <AS5048A.h>
#include "state.h"

// ── Hardware instances (defined in encoder.cpp) ────────────────────────────
extern AS5048A_SPI encA;
extern AS5048A_SPI encB;

// ── Lifecycle ─────────────────────────────────────────────────────────────
void encoderInit();

// ── Streaming (called from loop()) ────────────────────────────────────────
void encStreamAngle(char id, AS5048A_SPI &enc);
void encStreamAngles();
void encStreamMagnitude(char id, AS5048A_SPI &enc);
void encStreamMagnitudes();
void encStreamNop();

// ── SCPI handlers ─────────────────────────────────────────────────────────
// MEASure subsystem (query-only)
void handleMeasAngl(const String &param);   // MEAS:ANGL? A|B|BOTH
void handleMeasMagn(const String &param);   // MEAS:MAGN? A|B|BOTH

// CONFigure subsystem (command-only)
void handleConfZero(const String &param);   // CONF:ZERO A|B|BOTH
void handleConfErr (const String &param);   // CONF:ERR  A|B|BOTH

// SYSTem:DIAGnostic subsystem (query-only)
void handleSystDiag(const String &param);   // SYST:DIAG? A|B
