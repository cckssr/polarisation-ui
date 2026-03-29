#include <Arduino.h>
#include "config.h"
#include "state.h"
#include "encoder.h"
#include "scpi.h"

void setup()
{
  Serial.begin(BAUD_RATE);
  delay(500);
  Serial.println("DATA:INFO " DEVICE_MFR "," DEVICE_MODEL " Ready");
  Serial.println("DATA:INFO Send SYST:HELP? for command reference");
  encoderInit();
}

void loop()
{
  // Process incoming SCPI commands (one per line)
  if (Serial.available())
  {
    String line = Serial.readStringUntil('\n');
    line.trim();
    line.toUpperCase();
    scpiDispatch(line);
  }

  // Continuous acquisition
  unsigned long now = millis();
  if (appState.mode != AcqMode::Idle && (now - appState.lastPollMs >= appState.pollMs))
  {
    appState.lastPollMs = now;
    switch (appState.mode)
    {
    case AcqMode::AngleA:
      encStreamAngle('A', encA);
      break;
    case AcqMode::AngleB:
      encStreamAngle('B', encB);
      break;
    case AcqMode::AngleBoth:
      encStreamAngles();
      break;
    case AcqMode::Magnitude:
      encStreamMagnitudes();
      break;
    case AcqMode::Nop:
      encStreamNop();
      break;
    default:
      break;
    }
  }
}
