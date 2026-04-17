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

  if (!adsSession.begin()) {
    Serial.println("DATA:WARN ADS1220 not detected; ADC commands unavailable");
  }
}

void loop()
{
  // ── Process incoming SCPI commands (one line per call) ─────────────────────
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    line.trim();
    line.toUpperCase();
    scpiDispatch(line);
  }

  // ── Poll ADS1220 whenever DRDY asserts (decoupled from stream rate) ─────────
  if (adsSession.ready()) {
    adsSession.pollAdc();
  }

  // ── Single-shot INIT frame ─────────────────────────────────────────────────
  if (appState.singleShot) {
    appState.singleShot = false;
    emitDataFrame();
  }

  // ── Continuous streaming at configured rate ────────────────────────────────
  if (appState.streaming) {
    unsigned long now = millis();
    if (now - appState.lastPollMs >= appState.stream.intervalMs) {
      appState.lastPollMs = now;
      emitDataFrame();
    }
  }
}
