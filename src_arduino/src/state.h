#pragma once
#include <Arduino.h>
#include "config.h"

// ── Error queue (SYST:ERR?) ───────────────────────────────────────────────
struct ErrorQueue
{
  String  msgs[ERR_QUEUE_SIZE];
  uint8_t count = 0;

  void push(const String &msg)
  {
    if (count < ERR_QUEUE_SIZE)
      msgs[count++] = msg;
  }

  String pop()
  {
    if (count == 0)
      return F("0,\"No error\"");
    String e = msgs[0];
    for (uint8_t i = 1; i < count; ++i)
      msgs[i - 1] = msgs[i];
    --count;
    return e;
  }

  void clear() { count = 0; }
};

// ── Acquisition statistics ─────────────────────────────────────────────────
struct AcqStats
{
  unsigned long startMs       = 0;
  unsigned long endMs         = 0;
  unsigned long dataPoints    = 0;
  unsigned long parityErrors  = 0;
  unsigned long efEvents      = 0;   // auto-cleared EF occurrences
  unsigned long readAttempts  = 0;

  void reset()
  {
    startMs = endMs = dataPoints = parityErrors = efEvents = readAttempts = 0;
  }

  void print() const
  {
    Serial.println("DATA:STAT DUR,"  + String(endMs - startMs));
    Serial.println("DATA:STAT NPTS," + String(dataPoints));
    Serial.println("DATA:STAT PERR," + String(parityErrors));
    Serial.println("DATA:STAT EERR," + String(efEvents));
  }
};

// ── Acquisition mode ───────────────────────────────────────────────────────
enum class AcqMode : uint8_t
{
  Idle,
  AngleA,
  AngleB,
  AngleBoth,
  Magnitude,
  Nop
};

// ── Application state ──────────────────────────────────────────────────────
struct AppState
{
  AcqMode       mode        = AcqMode::Idle;
  unsigned long lastPollMs  = 0;
  unsigned long pollMs      = DEFAULT_POLL_MS;
  bool          encBPresent = true;
  bool          debug       = false;
};

// ── Global instances (defined in state.cpp) ────────────────────────────────
extern ErrorQueue  errorQueue;
extern AcqStats    acqStats;
extern AppState    appState;
