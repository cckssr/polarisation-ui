#pragma once
#include <Arduino.h>
#include "config.h"

// ── Error queue (SYST:ERR?) ───────────────────────────────────────────────────
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

// ── Acquisition statistics (emitted on stream stop in debug mode) ─────────────
struct AcqStats
{
  unsigned long startMs      = 0;
  unsigned long endMs        = 0;
  unsigned long dataPoints   = 0;   // frames emitted
  unsigned long parityErrors = 0;
  unsigned long efEvents     = 0;

  void reset()
  {
    startMs = endMs = dataPoints = parityErrors = efEvents = 0;
  }

  void print() const
  {
    Serial.println("DATA:STAT DUR,"  + String(endMs - startMs));
    Serial.println("DATA:STAT NPTS," + String(dataPoints));
    Serial.println("DATA:STAT PERR," + String(parityErrors));
    Serial.println("DATA:STAT EERR," + String(efEvents));
  }
};

// ── Stream source bitmask (CONF:SRC) ──────────────────────────────────────────
enum StreamSource : uint8_t
{
  SRC_NONE   = 0x00,
  SRC_ENC_A  = 0x01,
  SRC_ENC_B  = 0x02,
  SRC_ADC    = 0x04,
  SRC_ADC_T  = 0x08,
  SRC_PDTIA  = 0x10,
};

// ── Stream configuration (CONF:SRC / CONF:RATE) ───────────────────────────────
struct StreamConfig
{
  uint8_t       sources    = DEFAULT_STREAM_SOURCES;
  uint16_t      rateHz     = DEFAULT_STREAM_RATE_HZ;
  unsigned long intervalMs = 1000UL / DEFAULT_STREAM_RATE_HZ;

  void setRate(uint16_t hz)
  {
    rateHz     = hz;
    intervalMs = (hz > 0) ? (1000UL / hz) : 50UL;
  }
};

// ── Application state ─────────────────────────────────────────────────────────
struct AppState
{
  bool          streaming   = false;
  bool          singleShot  = false;   // INIT — one frame on next tick
  unsigned long lastPollMs  = 0;
  StreamConfig  stream;
  bool          encBPresent = true;
  bool          debug       = false;
};

// ── Global instances (defined in state.cpp) ───────────────────────────────────
extern ErrorQueue  errorQueue;
extern AcqStats    acqStats;
extern AppState    appState;
