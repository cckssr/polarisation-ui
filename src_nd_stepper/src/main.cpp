// ND-filter stepper controller — ESP32 + DRV8825 driving an axial (rotary)
// variable ND filter. SCPI-style protocol over USB serial, one command per line.
//
// The host (polarisation-ui) polls MOT:BUSY? to wait for moves to finish.
// Commands produce no reply on success; failures are queued and read via
// SYST:ERR? (same convention as the encoder/ADC firmware in ../src_arduino).
//
//   *IDN?  *RST  *CLS  *OPC?
//   SYST:ERR?  SYST:VERS?
//   MOT:HOME              Seek the home switch, or zero here if PIN_HOME < 0
//   MOT:HOMED?            1 once a home/zero reference exists
//   MOT:MOVE:ABS <deg>    Absolute move (non-blocking)
//   MOT:MOVE:REL <deg>    Relative move (non-blocking)
//   MOT:STOP              Decelerate to a halt
//   MOT:ZERO              Define the current position as 0 deg
//   MOT:POS?              Position in degrees
//   MOT:BUSY?             1 while moving or homing
//   MOT:ENAB ON|OFF       Energise / release the motor (MOT:ENAB? to query)
//   DIAG:DRV?             OK | FAULT | NA — DRV8825 /FAULT pin (latched; *CLS clears)
//   DIAG:DRV:RES          Pulse DRV8825 /RESET to clear a latched fault (needs PIN_RESET)
//   DIAG:SELF?            Short out-and-back move; PASS | FAIL,<reason> | NA,NO_FAULT_PIN
//   CONF:MOT:IDLE <ms>    Release the motor this long after a move; 0 = hold (query with ?)
//   CONF:MOT:SPEED <dps>  Max speed in deg/s (query with ?)
//   CONF:MOT:ACCEL <dps2> Acceleration in deg/s^2 (query with ?)
//   CONF:MOT:LIM <min>,<max>  Software travel limits in deg (query with ?)

#include <Arduino.h>
#include <AccelStepper.h>
#include <stdlib.h>
#include "config.h"

// Shared parser — single source of truth, also unit-tested natively from ../src_arduino/test.
#include "scpi_parse.inc"

// ── State ─────────────────────────────────────────────────────────────────────

static const float STEPS_PER_DEG = (float)MOTOR_STEPS_PER_REV * MICROSTEPS * GEAR_RATIO / 360.0f;

static AccelStepper stepper(AccelStepper::DRIVER, PIN_STEP, PIN_DIR);

enum class HomePhase : uint8_t
{
  Idle,
  Seek,    // drive towards the switch until it triggers
  Release, // drive away until the switch releases
  Backoff  // travel a fixed distance further so zero is a repeatable edge
};

static HomePhase s_homePhase = HomePhase::Idle;
static long s_phaseSteps = 0; // step budget (Seek/Release) or remaining distance (Backoff)
static bool s_homed = false;
static bool s_enabled = true;
static uint32_t s_idleDisableMs = IDLE_DISABLE_MS;
static uint32_t s_lastActiveMs = 0; // last time the motor was moving or (re-)enabled
static bool s_driverFault = false;  // latched when /FAULT was seen low
static float s_speedDps = DEFAULT_SPEED_DPS;
static float s_accelDps2 = DEFAULT_ACCEL_DPS2;
static float s_limMin = DEFAULT_LIMIT_MIN_DEG;
static float s_limMax = DEFAULT_LIMIT_MAX_DEG;

static String s_errors[ERR_QUEUE_SIZE];
static uint8_t s_errCount = 0;

static void pushError(const String &e)
{
  if (s_errCount < ERR_QUEUE_SIZE)
  {
    s_errors[s_errCount++] = e;
  }
}

static String popError()
{
  if (s_errCount == 0)
    return String("0,\"No error\"");
  String e = s_errors[0];
  for (uint8_t i = 1; i < s_errCount; ++i)
    s_errors[i - 1] = s_errors[i];
  --s_errCount;
  return e;
}

// ── Motion helpers ────────────────────────────────────────────────────────────

static inline long degToSteps(float deg)
{
  const float signedDeg = DIR_INVERT ? -deg : deg;
  return lroundf(signedDeg * STEPS_PER_DEG);
}

static inline float stepsToDeg(long steps)
{
  const float deg = (float)steps / STEPS_PER_DEG;
  return DIR_INVERT ? -deg : deg;
}

static inline bool busy()
{
  return s_homePhase != HomePhase::Idle || stepper.distanceToGo() != 0;
}

static inline bool homeSwitchActive()
{
  return PIN_HOME >= 0 && digitalRead(PIN_HOME) == HOME_ACTIVE_LEVEL;
}

static void applyMotionProfile()
{
  stepper.setMaxSpeed(s_speedDps * STEPS_PER_DEG);
  stepper.setAcceleration(s_accelDps2 * STEPS_PER_DEG);
}

/** Drop any pending move and make the current position the target. */
static void haltImmediately()
{
  stepper.setCurrentPosition(stepper.currentPosition());
  s_homePhase = HomePhase::Idle;
}

/** True while the DRV8825 pulls /FAULT low (always false without PIN_FAULT). */
static inline bool faultPinLow()
{
  return PIN_FAULT >= 0 && digitalRead(PIN_FAULT) == LOW;
}

/** Latch a fault and stop at once. Called every loop iteration. */
static void serviceFault()
{
  if (PIN_FAULT < 0 || s_driverFault || !faultPinLow())
    return;
  s_driverFault = true;
  haltImmediately();
  pushError("-200,\"Execution error; DRV8825 fault (overcurrent or over-temperature)\"");
}

static void setMicrostepPins()
{
  // DRV8825 M0/M1/M2 truth table: 1 → 000, 2 → 100, 4 → 010, 8 → 110, 16 → 001, 32 → 101.
  uint8_t m0 = 0, m1 = 0, m2 = 0;
  switch (MICROSTEPS)
  {
  case 2:
    m0 = 1;
    break;
  case 4:
    m1 = 1;
    break;
  case 8:
    m0 = m1 = 1;
    break;
  case 16:
    m2 = 1;
    break;
  case 32:
    m0 = m2 = 1;
    break;
  default:
    break; // full step
  }
  digitalWrite(PIN_MS1, m0);
  digitalWrite(PIN_MS2, m1);
  digitalWrite(PIN_MS3, m2);
}

static void setEnabled(bool on)
{
  s_enabled = on;
  digitalWrite(PIN_EN, on ? LOW : HIGH); // /ENABLE is active low
  if (on)
    s_lastActiveMs = millis();
}

/** Release the motor once it has been idle for s_idleDisableMs. Call every loop iteration. */
static void serviceIdle()
{
  if (!s_enabled || s_idleDisableMs == 0)
    return;
  if (busy())
  {
    s_lastActiveMs = millis();
    return;
  }
  if (millis() - s_lastActiveMs >= s_idleDisableMs)
    setEnabled(false);
}

static void startHome()
{
  haltImmediately();
  if (s_driverFault || faultPinLow())
  {
    pushError("-200,\"Execution error; DRV8825 fault\"");
    return;
  }
  if (PIN_HOME < 0)
  {
    stepper.setCurrentPosition(0);
    s_homed = true;
    return;
  }
  setEnabled(true);
  s_homed = false;
  // Already on the switch: skip the seek and release it straight away.
  if (homeSwitchActive())
  {
    s_homePhase = HomePhase::Release;
    s_phaseSteps = lroundf(20.0f * STEPS_PER_DEG);
  }
  else
  {
    s_homePhase = HomePhase::Seek;
    s_phaseSteps = lroundf(HOME_MAX_SEEK_DEG * STEPS_PER_DEG);
  }
}

static void failHome(const char *message)
{
  haltImmediately();
  pushError(String("-200,\"Execution error; ") + message + "\"");
}

/** Advance the homing state machine; call every loop iteration while not Idle. */
static void serviceHoming()
{
  // HOME_DIRECTION is in output degrees; AccelStepper counts motor steps.
  const float towardSwitch = (float)HOME_DIRECTION * (DIR_INVERT ? -1.0f : 1.0f);
  const float speed = HOME_SEEK_DPS * STEPS_PER_DEG;

  switch (s_homePhase)
  {
  case HomePhase::Seek:
    if (homeSwitchActive())
    {
      s_homePhase = HomePhase::Release;
      s_phaseSteps = lroundf(20.0f * STEPS_PER_DEG);
      return;
    }
    stepper.setSpeed(towardSwitch * speed);
    if (stepper.runSpeed() && --s_phaseSteps <= 0)
      failHome("home switch not found");
    break;

  case HomePhase::Release:
    if (!homeSwitchActive())
    {
      s_homePhase = HomePhase::Backoff;
      s_phaseSteps = lroundf(HOME_BACKOFF_DEG * STEPS_PER_DEG);
      return;
    }
    stepper.setSpeed(-towardSwitch * speed);
    if (stepper.runSpeed() && --s_phaseSteps <= 0)
      failHome("could not release home switch");
    break;

  case HomePhase::Backoff:
    stepper.setSpeed(-towardSwitch * speed);
    if (stepper.runSpeed() && --s_phaseSteps <= 0)
    {
      stepper.setCurrentPosition(0);
      s_homed = true;
      s_homePhase = HomePhase::Idle;
    }
    break;

  case HomePhase::Idle:
    break;
  }
}

// ── SCPI dispatch ─────────────────────────────────────────────────────────────

/** Parse *param* as a finite number; queues an error and returns false otherwise. */
static bool parseNumber(const String &param, float &out)
{
  if (param.length() == 0)
  {
    pushError("-109,\"Missing parameter\"");
    return false;
  }
  char *end = nullptr;
  const double v = strtod(param.c_str(), &end);
  if (end == param.c_str() || *end != '\0' || isnan(v) || isinf(v))
  {
    pushError("-104,\"Data type error\"");
    return false;
  }
  out = (float)v;
  return true;
}

static void moveToDeg(float deg)
{
  if (s_homePhase != HomePhase::Idle)
  {
    pushError("-200,\"Execution error; homing in progress\"");
    return;
  }
  if (s_driverFault || faultPinLow())
  {
    pushError("-200,\"Execution error; DRV8825 fault\"");
    return;
  }
  if (deg < s_limMin - 1e-3f || deg > s_limMax + 1e-3f)
  {
    pushError("-222,\"Data out of range; target outside travel limits\"");
    return;
  }
  setEnabled(true);
  stepper.moveTo(degToSteps(deg));
}

/** Pulse /RESET low, then re-check /FAULT. Motion is stopped; coil phase is lost. */
static void resetDriver()
{
  if (PIN_RESET < 0)
  {
    pushError("-241,\"Hardware missing; PIN_RESET not configured\"");
    return;
  }
  haltImmediately();
  digitalWrite(PIN_RESET, LOW);
  delay(2);
  digitalWrite(PIN_RESET, HIGH);
  delay(5); // the DRV8825 needs ~1 ms to wake before accepting STEP pulses
  if (!faultPinLow())
    s_driverFault = false;
}

/** Blocking run of the pending move; returns false if /FAULT trips meanwhile. */
static bool runToTarget()
{
  while (stepper.distanceToGo() != 0)
  {
    stepper.run();
    if (faultPinLow())
    {
      s_driverFault = true;
      haltImmediately();
      return false;
    }
  }
  return true;
}

/** DIAG:SELF? — enable, move SELFTEST_DEG out and back, watch /FAULT throughout. */
static String driverSelfTest()
{
  if (busy())
    return "FAIL,BUSY";
  if (s_driverFault || faultPinLow())
    return "FAIL,FAULT_ACTIVE";
  setEnabled(true);
  delay(5); // let the driver wake up and /FAULT settle
  if (faultPinLow())
  {
    s_driverFault = true;
    return "FAIL,FAULT_AFTER_ENABLE";
  }
  const long start = stepper.currentPosition();
  const long delta = degToSteps(SELFTEST_DEG);
  stepper.moveTo(start + delta);
  if (!runToTarget())
    return "FAIL,FAULT_DURING_MOVE";
  stepper.moveTo(start);
  if (!runToTarget())
    return "FAIL,FAULT_DURING_MOVE";
  s_lastActiveMs = millis();
  return PIN_FAULT < 0 ? "NA,NO_FAULT_PIN" : "PASS";
}

static void scpiDispatch(const String &line)
{
  String header, param;
  bool isQuery = false;
  if (!scpiParse(line, header, param, isQuery))
    return;

  if (header == "*IDN" && isQuery)
  {
    Serial.println(DEVICE_MFR "," DEVICE_MODEL "," DEVICE_SERIAL "," FW_VERSION);
  }
  else if (header == "*RST")
  {
    haltImmediately();
    s_speedDps = DEFAULT_SPEED_DPS;
    s_accelDps2 = DEFAULT_ACCEL_DPS2;
    s_idleDisableMs = IDLE_DISABLE_MS;
    s_limMin = DEFAULT_LIMIT_MIN_DEG;
    s_limMax = DEFAULT_LIMIT_MAX_DEG;
    applyMotionProfile();
  }
  else if (header == "*CLS")
  {
    s_errCount = 0;
    if (!faultPinLow())
      s_driverFault = false;
  }
  else if (header == "DIAG:DRV" && isQuery)
  {
    if (PIN_FAULT < 0)
      Serial.println("NA");
    else
      Serial.println((s_driverFault || faultPinLow()) ? "FAULT" : "OK");
  }
  else if (header == "DIAG:DRV:RES" && !isQuery)
  {
    resetDriver();
  }
  else if (header == "DIAG:SELF" && isQuery)
  {
    Serial.println(driverSelfTest());
  }
  else if (header == "*OPC" && isQuery)
  {
    Serial.println(busy() ? 0 : 1);
  }
  else if (header == "SYST:ERR" && isQuery)
  {
    Serial.println(popError());
  }
  else if (header == "SYST:VERS" && isQuery)
  {
    Serial.println(FW_VERSION);
  }
  else if (header == "MOT:HOME" && !isQuery)
  {
    startHome();
  }
  else if (header == "MOT:HOMED" && isQuery)
  {
    Serial.println(s_homed ? 1 : 0);
  }
  else if (header == "MOT:MOVE:ABS" && !isQuery)
  {
    float deg;
    if (parseNumber(param, deg))
      moveToDeg(deg);
  }
  else if (header == "MOT:MOVE:REL" && !isQuery)
  {
    float delta;
    if (parseNumber(param, delta))
      moveToDeg(stepsToDeg(stepper.targetPosition()) + delta);
  }
  else if (header == "MOT:STOP" && !isQuery)
  {
    if (s_homePhase != HomePhase::Idle)
      haltImmediately();
    else
      stepper.stop(); // decelerates; AccelStepper shortens the pending move
  }
  else if (header == "MOT:ZERO" && !isQuery)
  {
    if (busy())
    {
      pushError("-200,\"Execution error; motor is moving\"");
    }
    else
    {
      stepper.setCurrentPosition(0);
      s_homed = true;
    }
  }
  else if (header == "MOT:POS" && isQuery)
  {
    Serial.println(stepsToDeg(stepper.currentPosition()), 3);
  }
  else if (header == "MOT:BUSY" && isQuery)
  {
    Serial.println(busy() ? 1 : 0);
  }
  else if (header == "MOT:ENAB")
  {
    if (isQuery)
    {
      Serial.println(s_enabled ? 1 : 0);
    }
    else if (param == "ON" || param == "1")
    {
      setEnabled(true);
    }
    else if (param == "OFF" || param == "0")
    {
      if (busy())
        pushError("-200,\"Execution error; motor is moving\"");
      else
        setEnabled(false);
    }
    else
    {
      pushError("-224,\"Illegal parameter value\"");
    }
  }
  else if (header == "CONF:MOT:SPEED")
  {
    float v;
    if (isQuery)
    {
      Serial.println(s_speedDps, 2);
    }
    else if (parseNumber(param, v))
    {
      if (v <= 0.0f || v > MAX_SPEED_DPS)
      {
        pushError("-222,\"Data out of range; speed\"");
      }
      else
      {
        s_speedDps = v;
        applyMotionProfile();
      }
    }
  }
  else if (header == "CONF:MOT:IDLE")
  {
    float v;
    if (isQuery)
    {
      Serial.println(s_idleDisableMs);
    }
    else if (parseNumber(param, v))
    {
      if (v < 0.0f || v > 600000.0f)
      {
        pushError("-222,\"Data out of range; idle time\"");
      }
      else
      {
        s_idleDisableMs = (uint32_t)v;
        s_lastActiveMs = millis();
      }
    }
  }
  else if (header == "CONF:MOT:ACCEL")
  {
    float v;
    if (isQuery)
    {
      Serial.println(s_accelDps2, 2);
    }
    else if (parseNumber(param, v))
    {
      if (v <= 0.0f)
      {
        pushError("-222,\"Data out of range; acceleration\"");
      }
      else
      {
        s_accelDps2 = v;
        applyMotionProfile();
      }
    }
  }
  else if (header == "CONF:MOT:LIM")
  {
    if (isQuery)
    {
      Serial.print(s_limMin, 2);
      Serial.print(",");
      Serial.println(s_limMax, 2);
    }
    else
    {
      const int comma = param.indexOf(',');
      float lo, hi;
      if (comma < 0)
      {
        pushError("-109,\"Missing parameter\"");
      }
      else if (parseNumber(param.substring(0, comma), lo) && parseNumber(param.substring(comma + 1), hi))
      {
        if (lo >= hi)
        {
          pushError("-222,\"Data out of range; min must be below max\"");
        }
        else
        {
          s_limMin = lo;
          s_limMax = hi;
        }
      }
    }
  }
  else
  {
    pushError("-113,\"Undefined header; " + header + "\"");
  }
}

// ── Arduino entry points ──────────────────────────────────────────────────────

void setup()
{
  Serial.begin(BAUD_RATE);

  pinMode(PIN_EN, OUTPUT);
  pinMode(PIN_MS1, OUTPUT);
  pinMode(PIN_MS2, OUTPUT);
  pinMode(PIN_MS3, OUTPUT);
  if (PIN_HOME >= 0)
    pinMode(PIN_HOME, INPUT_PULLUP);
  if (PIN_FAULT >= 0)
    pinMode(PIN_FAULT, INPUT_PULLUP);
  if (PIN_RESET >= 0)
  {
    digitalWrite(PIN_RESET, HIGH); // release before switching to output: no glitch
    pinMode(PIN_RESET, OUTPUT);
  }

  setMicrostepPins();
  setEnabled(true);
  applyMotionProfile();
  stepper.setMinPulseWidth(3); // DRV8825 needs >= 1.9 µs STEP high
  stepper.setCurrentPosition(0);

  Serial.println("DATA:INFO " DEVICE_MFR "," DEVICE_MODEL " Ready fw=" FW_VERSION);
}

static char s_lineBuf[128];
static uint16_t s_lineLen = 0;
static bool s_lineOverflowed = false;

static void processSerial()
{
  while (Serial.available())
  {
    const char c = (char)Serial.read();
    if (c == '\n' || c == '\r')
    {
      if (s_lineOverflowed)
      {
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
      s_lineLen = 0;
    }
    else if (s_lineLen < (uint16_t)(sizeof(s_lineBuf) - 1))
    {
      s_lineBuf[s_lineLen++] = c;
    }
    else
    {
      s_lineOverflowed = true;
    }
  }
}

void loop()
{
  processSerial();
  serviceFault();
  serviceIdle();
  if (s_homePhase == HomePhase::Idle)
    stepper.run();
  else
    serviceHoming();
}
