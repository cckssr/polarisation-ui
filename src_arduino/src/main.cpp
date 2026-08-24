#include <Arduino.h>
#include "config.h"
#include "state.h"
#include "encoder.h"
#include "ads_session.h"
#include "scpi.h"

/**
 * @brief Arduino setup function.
 *
 * The function initializes the serial communication, prints device information,
 * initializes the encoder, and checks for the presence of the ADS1220 ADC.
 * If the ADC is not detected, a warning message is printed.
 *
 * @return void
 */
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

static char s_lineBuf[256];           // data buffer
static uint16_t s_lineLen = 0;        // current data length
static bool s_lineOverflowed = false; // true while discarding a too-long line

/**
 * @brief Pre-process serial buffer for SCPI commands.
 *
 * Checks for available data on the serial port, reads it character by
 * character, and processes complete lines as SCPI commands. Lines are
 * terminated by either a newline or carriage return. If a line exceeds the
 * buffer size, it is discarded until the next line ending.
 *
 * @return void
 */
static void processSerial()
{
  while (Serial.available())
  {
    char c = (char)Serial.read();
    if (c == '\n' || c == '\r')
    {
      if (s_lineOverflowed)
      {
        // Buffer overflowed, discard line
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
      // Ignore bare CR / lone LF
      s_lineLen = 0;
    }
    else if (s_lineLen < (uint16_t)(sizeof(s_lineBuf) - 1))
    {
      s_lineBuf[s_lineLen++] = c;
    }
    else
    {
      // If buffer full, discard next until line ending
      s_lineOverflowed = true;
    }
  }
}

/**
 * Main arduino loop function.
 *
 * In the main loop the serial input from the master is processed,
 * The PD-TIA ADC is read through the ADS,
 * A one-time measurement is sent back to master or
 * Continous streaming is enabled.
 *
 * @return void
 */
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
