#include <Arduino.h>
#include "config.h"
#include "state.h"
#include "encoder.h"
#include "ads_session.h"
#include "scpi.h"

void setup()
{
  Serial.begin(BAUD_RATE);
  delay(500);
  Serial.println("DATA:INFO " DEVICE_MFR "," DEVICE_MODEL " Ready fw=" FW_VERSION);
  Serial.println("DATA:INFO Send SYST:HELP? for command reference");

  encoderInit();

  if (!adsSession.begin())
  {
    Serial.println("DATA:WARN ADS1220 not detected; ADC commands unavailable");
  }
}

// ── Non-blocking line accumulator ─────────────────────────────────────────────
// Drains only bytes already in the UART FIFO on each loop() tick so streaming
// frames are never stalled by a slow or incomplete host command.
static char s_lineBuf[256];
static uint16_t s_lineLen = 0;
static bool s_lineOverflowed = false; // true while discarding a too-long line

static void processSerial()
{
  while (Serial.available())
  {
    char c = (char)Serial.read();
    if (c == '\n' || c == '\r')
    {
      if (s_lineOverflowed)
      {
        // The line that just ended was >255 chars — it was never a complete,
        // trustworthy command, so drop it entirely instead of dispatching
        // whatever fit in the buffer (which would silently run a truncated,
        // and likely wrong, command).
        s_lineOverflowed = false;
      }
      else if (s_lineLen > 0)
      {
        s_lineBuf[s_lineLen] = '\0';
        String line = String(s_lineBuf);
        line.trim();
        line.toUpperCase();
        scpiDispatch(line);
      }
      // Ignore bare CR / lone LF — CRLF line endings handled transparently.
      s_lineLen = 0;
    }
    else if (s_lineLen < (uint16_t)(sizeof(s_lineBuf) - 1))
    {
      s_lineBuf[s_lineLen++] = c;
    }
    else
    {
      // Buffer full without a line ending — discard the rest of this line
      // once the terminator finally arrives, rather than dispatching a
      // truncated command.
      s_lineOverflowed = true;
    }
  }
}

void loop()
{
  // ── Process incoming SCPI commands (non-blocking) ───────────────────────────
  processSerial();

  // ── Poll ADS1220 whenever DRDY asserts (decoupled from stream rate) ─────────
  if (adsSession.ready())
  {
    adsSession.pollAdc();
  }

  // ── Non-blocking background temperature refresh (see ads_session.h) ────────
  adsSession.pollTemperature();

  // ── Single-shot INIT frame ─────────────────────────────────────────────────
  if (appState.singleShot)
  {
    appState.singleShot = false;
    emitDataFrame();
  }

  // ── Continuous streaming at configured rate ────────────────────────────────
  if (appState.streaming)
  {
    unsigned long now = millis();
    if (now - appState.lastPollMs >= appState.stream.intervalMs)
    {
      appState.lastPollMs = now;
      emitDataFrame();
    }
  }
}
