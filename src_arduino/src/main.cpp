#include <Arduino.h>
#include <AS5048A.h>

// ============================================================================
// CONFIGURATION
// ============================================================================

#define ENCODER_A_CS_PIN 9
#define ENCODER_B_CS_PIN 10
#define SERIAL_BAUDRATE 115200
#define DEFAULT_POLL_INTERVAL 50
#define SPI_CLOCK_HZ 100000 // 100 kHz

#define IDN_STRING "Polarisation-UI,AS5048A-DualEncoder,0,1.0"
#define MAX_ERRORS 10

// ============================================================================
// ERROR QUEUE  (SYST:ERR?)
// ============================================================================

struct ErrorQueue
{
  String messages[MAX_ERRORS];
  int count = 0;

  void push(const String &msg)
  {
    if (count < MAX_ERRORS)
      messages[count++] = msg;
  }

  String pop()
  {
    if (count == 0)
      return "0,\"No error\"";
    String e = messages[0];
    for (int i = 1; i < count; i++)
      messages[i - 1] = messages[i];
    count--;
    return e;
  }

  void clear() { count = 0; }
};

ErrorQueue errorQueue;

// ============================================================================
// STATISTICS
// ============================================================================

struct ContinuousStats
{
  unsigned long startTime = 0;
  unsigned long endTime = 0;
  unsigned long dataPoints = 0;
  unsigned long parityErrors = 0;
  unsigned long errorFlagEvents = 0; // times EF was set (auto-cleared)
  unsigned long totalReadAttempts = 0;

  void reset()
  {
    startTime = endTime = dataPoints = parityErrors = errorFlagEvents = totalReadAttempts = 0;
  }

  void print()
  {
    unsigned long durationMs = endTime - startTime;
    Serial.println("DATA:STAT DUR," + String(durationMs));
    Serial.println("DATA:STAT NPTS," + String(dataPoints));
    Serial.println("DATA:STAT PERR," + String(parityErrors));
    Serial.println("DATA:STAT EERR," + String(errorFlagEvents));
  }
};

ContinuousStats stats;

// ============================================================================
// GLOBAL STATE
// ============================================================================

AS5048A_SPI encoderA(ENCODER_A_CS_PIN);
AS5048A_SPI encoderB(ENCODER_B_CS_PIN);

enum OperationMode
{
  MODE_IDLE,
  MODE_CONTINUOUS_A,
  MODE_CONTINUOUS_B,
  MODE_CONTINUOUS_BOTH,
  MODE_CONTINUOUS_MAG,
  MODE_CONTINUOUS_NOP
};

struct AppState
{
  OperationMode mode = MODE_IDLE;
  unsigned long lastPoll = 0;
  unsigned long pollInterval = DEFAULT_POLL_INTERVAL;
  bool encoderBPresent = true;
  bool debugOutput = false;
};

AppState appState;

// ============================================================================
// INITIALIZATION
// ============================================================================

void initEncoders()
{
  encoderA.begin(SPI_CLOCK_HZ);
  encoderB.begin(SPI_CLOCK_HZ);
}

void setup()
{
  Serial.begin(SERIAL_BAUDRATE);
  delay(500);
  Serial.println("DATA:INFO " IDN_STRING " Ready");
  Serial.println("DATA:INFO Send SYST:HELP? for command reference");
  initEncoders();
}

// ============================================================================
// HELPERS
// ============================================================================

float convertRawToDegrees(uint16_t raw)
{
  return (raw & 0x3FFF) * 360.0 / 16384.0;
}

// Read angle with automatic error-flag recovery.
// If EF is set, clears it via clearErrorFlag() and retries once.
// Returns {raw16=0, data14=0, errorFlag=true, parityOk=false} on persistent failure.
AS5048A_SPI::FrameResult readAngleWithRecovery(AS5048A_SPI &encoder)
{
  AS5048A_SPI::FrameResult result = encoder.readAngleRawWithDiagnostics();

  if (result.errorFlag)
  {
    // AS5048A: reading REG_CLR_ERR (0x0001) clears the EF bit for subsequent reads.
    encoder.clearErrorFlag();
    result = encoder.readAngleRawWithDiagnostics(); // single retry
  }

  return result;
}

// ============================================================================
// STREAMING READ & SEND
// ============================================================================

// Streaming: DATA:ANGL <id>,<deg>[,<raw14>]
void readAndSendAngle(char encoderId, AS5048A_SPI &encoder)
{
  Serial.print("DATA:ANGL ");
  Serial.print(encoderId);
  Serial.print(",");

  if (appState.debugOutput)
  {
    AS5048A_SPI::FrameResult result = readAngleWithRecovery(encoder);
    stats.totalReadAttempts++;

    if (!result.parityOk)
      stats.parityErrors++;

    if (result.errorFlag)
    {
      // Persistent failure even after auto-clear
      stats.errorFlagEvents++;
      errorQueue.push("-300,\"Persistent EF encoder " + String(encoderId) + "\"");
      Serial.println("NAN");
      return;
    }

    stats.dataPoints++;
    float deg = convertRawToDegrees(result.data14);
    Serial.print(deg, 2);
    Serial.print(",");
    Serial.println(result.data14, DEC);
  }
  else
  {
    Serial.println(encoder.readAngleDeg(), 2);
  }
}

// Streaming: DATA:ANGL BOTH,<deg_a>,<deg_b>
void readAndSendAngles()
{
  float angleA = encoderA.readAngleDeg();
  float angleB = appState.encoderBPresent ? encoderB.readAngleDeg() : 0.0;
  Serial.print("DATA:ANGL BOTH,");
  Serial.print(angleA, 2);
  Serial.print(",");
  Serial.println(angleB, 2);
}

// Streaming: DATA:MAGN <id>,<raw14>
void readAndSendMagnitude(char encoderId, AS5048A_SPI &encoder)
{
  AS5048A_SPI::FrameResult result = encoder.readMagnitudeRawWithDiagnostics();
  Serial.print("DATA:MAGN ");
  Serial.print(encoderId);
  Serial.print(",");
  if (!result.parityOk || result.errorFlag)
  {
    errorQueue.push("-300,\"Magnitude read failed encoder " + String(encoderId) + "\"");
    Serial.println("NAN");
  }
  else
  {
    Serial.println(result.data14, DEC);
  }
}

// Streaming: DATA:MAGN BOTH,<raw_a>,<raw_b>
void readAndSendMagnitudes()
{
  AS5048A_SPI::FrameResult rA = encoderA.readMagnitudeRawWithDiagnostics();
  AS5048A_SPI::FrameResult rB = appState.encoderBPresent
                                    ? encoderB.readMagnitudeRawWithDiagnostics()
                                    : AS5048A_SPI::FrameResult{0, 0, false, true};
  Serial.print("DATA:MAGN BOTH,");
  Serial.print((!rA.parityOk || rA.errorFlag) ? "NAN" : String(rA.data14));
  Serial.print(",");
  Serial.println((appState.encoderBPresent && (!rB.parityOk || rB.errorFlag)) ? "NAN" : String(rB.data14));
}

// Streaming: DATA:NOP A,<OK|FAIL>,0x<raw>[,B,<OK|FAIL>,0x<raw>]
void sendContinuousNOP()
{
  AS5048A_SPI::FrameResult rA = encoderA.nop();
  Serial.print("DATA:NOP A,");
  Serial.print(rA.parityOk ? "OK" : "FAIL");
  Serial.print(",0x");
  Serial.print(rA.raw16, HEX);

  if (appState.encoderBPresent)
  {
    AS5048A_SPI::FrameResult rB = encoderB.nop();
    Serial.print(",B,");
    Serial.print(rB.parityOk ? "OK" : "FAIL");
    Serial.print(",0x");
    Serial.println(rB.raw16, HEX);
  }
  else
  {
    Serial.println();
  }
}

// ============================================================================
// SCPI COMMAND HANDLERS
// ============================================================================

// *IDN?  →  <manufacturer>,<model>,<serial>,<fw>
void handleIDN()
{
  Serial.println(IDN_STRING);
}

// *RST  —  stop streaming, restore defaults, clear error queue
void handleRST()
{
  if (appState.debugOutput && appState.mode != MODE_IDLE)
  {
    stats.endTime = millis();
    stats.print();
  }
  appState.mode = MODE_IDLE;
  appState.pollInterval = DEFAULT_POLL_INTERVAL;
  appState.debugOutput = false;
  errorQueue.clear();
  stats.reset();
}

// *CLS  —  clear SCPI error queue
void handleCLS()
{
  errorQueue.clear();
}

// MEAS:ANGL? A|B|BOTH
// Query-only. Response: <deg>  or  <deg_a>,<deg_b>
void handleMeasAngl(const String &param)
{
  if (param == "A" || param == "")
  {
    Serial.println(encoderA.readAngleDeg(), 2);
  }
  else if (param == "B")
  {
    if (!appState.encoderBPresent)
    {
      errorQueue.push("-241,\"Hardware missing; encoder B not present\"");
      Serial.println("NAN");
      return;
    }
    Serial.println(encoderB.readAngleDeg(), 2);
  }
  else if (param == "BOTH")
  {
    float degA = encoderA.readAngleDeg();
    float degB = appState.encoderBPresent ? encoderB.readAngleDeg() : 0.0;
    Serial.print(degA, 2);
    Serial.print(",");
    Serial.println(degB, 2);
  }
  else
  {
    errorQueue.push("-113,\"Undefined header; unknown encoder: " + param + "\"");
    Serial.println("NAN");
  }
}

// MEAS:MAGN? A|B|BOTH
// Query-only. Response: <raw14>  or  <raw_a>,<raw_b>
// Always returns bare integer values regardless of debug mode.
void handleMeasMagn(const String &param)
{
  auto readMagn = [](AS5048A_SPI &enc) -> String
  {
    AS5048A_SPI::FrameResult r = enc.readMagnitudeRawWithDiagnostics();
    return (r.parityOk && !r.errorFlag) ? String(r.data14) : "NAN";
  };

  if (param == "A" || param == "")
  {
    Serial.println(readMagn(encoderA));
  }
  else if (param == "B")
  {
    if (!appState.encoderBPresent)
    {
      errorQueue.push("-241,\"Hardware missing; encoder B not present\"");
      Serial.println("NAN");
      return;
    }
    Serial.println(readMagn(encoderB));
  }
  else if (param == "BOTH")
  {
    Serial.print(readMagn(encoderA));
    Serial.print(",");
    Serial.println(appState.encoderBPresent ? readMagn(encoderB) : "NAN");
  }
  else
  {
    errorQueue.push("-113,\"Undefined header; unknown encoder: " + param + "\"");
    Serial.println("NAN");
  }
}

// CONF:ZERO A|B|BOTH
// Command-only. Sets current position as software zero (no chip write).
void handleConfZero(const String &param)
{
  if (param == "A" || param == "")
  {
    encoderA.setSoftwareZero();
  }
  else if (param == "B")
  {
    if (!appState.encoderBPresent)
    {
      errorQueue.push("-241,\"Hardware missing; encoder B not present\"");
      return;
    }
    encoderB.setSoftwareZero();
  }
  else if (param == "BOTH")
  {
    encoderA.setSoftwareZero();
    if (appState.encoderBPresent)
      encoderB.setSoftwareZero();
  }
  else
  {
    errorQueue.push("-113,\"Undefined header; unknown encoder: " + param + "\"");
  }
}

// CONF:ERR A|B|BOTH
// Command-only. Clears the AS5048A hardware Error Flag (EF) by reading REG_CLR_ERR (0x0001).
// The EF is self-latching — once set it stays set until explicitly cleared.
// This command is rarely needed: reads in debug mode auto-clear EF and retry.
void handleConfErr(const String &param)
{
  if (param == "A" || param == "")
  {
    encoderA.clearErrorFlag();
  }
  else if (param == "B")
  {
    if (!appState.encoderBPresent)
    {
      errorQueue.push("-241,\"Hardware missing; encoder B not present\"");
      return;
    }
    encoderB.clearErrorFlag();
  }
  else if (param == "BOTH")
  {
    encoderA.clearErrorFlag();
    if (appState.encoderBPresent)
      encoderB.clearErrorFlag();
  }
  else
  {
    errorQueue.push("-113,\"Undefined header; unknown encoder: " + param + "\"");
  }
}

// INIT ON,<A|B|BOTH|MAG|NOP>  |  INIT OFF
// Command-only. Starts / stops continuous streaming.
void handleInit(const String &param)
{
  if (param.startsWith("ON"))
  {
    String target = "BOTH"; // sensible default: both encoders
    int comma = param.indexOf(',');
    if (comma >= 0)
    {
      target = param.substring(comma + 1);
      target.trim();
    }

    if (target == "A")
    {
      appState.mode = MODE_CONTINUOUS_A;
    }
    else if (target == "B")
    {
      if (!appState.encoderBPresent)
      {
        errorQueue.push("-241,\"Hardware missing; encoder B not present\"");
        return;
      }
      appState.mode = MODE_CONTINUOUS_B;
    }
    else if (target == "BOTH")
    {
      if (!appState.encoderBPresent)
      {
        errorQueue.push("-241,\"Hardware missing; encoder B not present\"");
        return;
      }
      appState.mode = MODE_CONTINUOUS_BOTH;
    }
    else if (target == "MAG")
    {
      appState.mode = MODE_CONTINUOUS_MAG;
    }
    else if (target == "NOP")
    {
      appState.mode = MODE_CONTINUOUS_NOP;
    }
    else
    {
      errorQueue.push("-113,\"Undefined header; unknown target: " + target + "\"");
      return;
    }

    appState.lastPoll = millis();
    if (appState.debugOutput)
    {
      stats.reset();
      stats.startTime = millis();
    }
  }
  else if (param == "OFF")
  {
    if (appState.debugOutput && appState.mode != MODE_IDLE)
    {
      stats.endTime = millis();
      stats.print();
    }
    appState.mode = MODE_IDLE;
  }
  else
  {
    errorQueue.push("-102,\"Syntax error; expected: INIT ON,<A|B|BOTH|MAG|NOP> or INIT OFF\"");
  }
}

// ABOR  —  stop any active streaming (alias for INIT OFF)
// Command-only.
void handleAbor()
{
  if (appState.debugOutput && appState.mode != MODE_IDLE)
  {
    stats.endTime = millis();
    stats.print();
  }
  appState.mode = MODE_IDLE;
}

// SENS:INT <ms>   Set poll interval (command)
// SENS:INT?       Query poll interval (query)
void handleSensInt(bool isQuery, const String &param)
{
  if (isQuery)
  {
    Serial.println(appState.pollInterval);
    return;
  }
  int interval = param.toInt();
  if (interval >= 1 && interval <= 9999)
    appState.pollInterval = (unsigned long)interval;
  else
    errorQueue.push("-222,\"Data out of range; interval must be 1-9999 ms\"");
}

// SYST:ERR?  →  <code>,\"<message>\"
// Query-only. Pops and returns the oldest error from the queue.
void handleSystErr()
{
  Serial.println(errorQueue.pop());
}

// SYST:DIAG? A|B
// Query-only. Response: <compHigh>,<compLow>,<cof>,<ocf>,<agc>
void handleSystDiag(const String &param)
{
  AS5048A_SPI *enc = nullptr;
  if (param == "A" || param == "")
  {
    enc = &encoderA;
  }
  else if (param == "B")
  {
    if (!appState.encoderBPresent)
    {
      errorQueue.push("-241,\"Hardware missing; encoder B not present\"");
      Serial.println("NAN,NAN,NAN,NAN,NAN");
      return;
    }
    enc = &encoderB;
  }
  else
  {
    errorQueue.push("-113,\"Undefined header; unknown encoder: " + param + "\"");
    Serial.println("NAN,NAN,NAN,NAN,NAN");
    return;
  }

  AS5048A_SPI::Diagnostics diag = enc->readDiagnostics();
  Serial.print(diag.compHigh);
  Serial.print(",");
  Serial.print(diag.compLow);
  Serial.print(",");
  Serial.print(diag.cof);
  Serial.print(",");
  Serial.print(diag.ocf);
  Serial.print(",");
  Serial.println(diag.agc);
}

// SYST:DEB ON|OFF   Enable/disable debug mode (command)
// SYST:DEB?         Query debug state: 0 or 1 (query)
void handleSystDeb(bool isQuery, const String &param)
{
  if (isQuery)
  {
    Serial.println(appState.debugOutput ? "1" : "0");
    return;
  }
  if (param == "ON" || param == "1")
    appState.debugOutput = true;
  else if (param == "OFF" || param == "0")
    appState.debugOutput = false;
  else
    errorQueue.push("-102,\"Syntax error; use ON, OFF, 1, or 0\"");
}

// SYST:HELP?
// Query-only.
void printHelp()
{
  Serial.println("=== AS5048A SCPI Command Reference ===");
  Serial.println("IEEE 488.2 Common Commands:");
  Serial.println("  *IDN?                  Identification string (query)");
  Serial.println("  *RST                   Reset: stop streaming, restore defaults");
  Serial.println("  *CLS                   Clear SCPI error queue");
  Serial.println("MEASure — single reads (queries only):");
  Serial.println("  MEAS:ANGL? A|B|BOTH    Angle in degrees");
  Serial.println("  MEAS:MAGN? A|B|BOTH    Raw magnitude (14-bit integer)");
  Serial.println("CONFigure — hardware settings (commands only):");
  Serial.println("  CONF:ZERO A|B|BOTH     Set current position as software zero");
  Serial.println("  CONF:ERR  A|B|BOTH     Clear hardware Error Flag (EF) on sensor");
  Serial.println("                         (auto-cleared in debug mode; rarely needed)");
  Serial.println("INITiate / ABORt — streaming control (commands only):");
  Serial.println("  INIT ON,A|B|BOTH       Start angle streaming");
  Serial.println("  INIT ON,MAG            Start magnitude streaming");
  Serial.println("  INIT ON,NOP            Start NOP signal-quality test");
  Serial.println("  INIT OFF               Stop streaming");
  Serial.println("  ABOR                   Abort streaming (= INIT OFF)");
  Serial.println("SENSe — acquisition settings (command + query):");
  Serial.println("  SENS:INT <ms>          Set poll interval (1-9999 ms)");
  Serial.println("  SENS:INT?              Query poll interval");
  Serial.println("SYSTem — diagnostics (mostly queries):");
  Serial.println("  SYST:ERR?              Pop oldest error: <code>,\"<msg>\"");
  Serial.println("  SYST:DIAG? A|B         Diagnostics: compH,compL,cof,ocf,agc");
  Serial.println("  SYST:DEB ON|OFF        Enable/disable debug output");
  Serial.println("  SYST:DEB?              Query debug state (0 or 1)");
  Serial.println("  SYST:HELP?             This help text");
  Serial.println("Streaming output format:");
  Serial.println("  DATA:ANGL A,<deg>             Single encoder angle");
  Serial.println("  DATA:ANGL A,<deg>,<raw14>      ...with raw value (debug)");
  Serial.println("  DATA:ANGL BOTH,<deg_a>,<deg_b> Both encoders");
  Serial.println("  DATA:MAGN A,<raw14>            Single encoder magnitude");
  Serial.println("  DATA:MAGN BOTH,<a>,<b>         Both encoders magnitude");
  Serial.println("  DATA:NOP A,<OK|FAIL>,0x<raw>   NOP signal test");
  Serial.println("  DATA:STAT ...                  Statistics after ABOR/INIT OFF (debug)");
  Serial.println("  DATA:INFO ...                  Informational messages");
  Serial.println("======================================");
}

// ============================================================================
// MAIN COMMAND DISPATCHER
// ============================================================================

void handleCommand(String cmd)
{
  cmd.trim();
  if (cmd.length() == 0)
    return;

  cmd.toUpperCase(); // SCPI is case-insensitive

  // Split into header (first word) and parameter (remainder)
  String header = cmd;
  String param = "";
  int space = cmd.indexOf(' ');
  if (space >= 0)
  {
    header = cmd.substring(0, space);
    param = cmd.substring(space + 1);
    param.trim();
  }

  // '?' must be attached to the header, not the parameter.
  // E.g.: "MEAS:ANGL? A"  → header="MEAS:ANGL?", param="A"
  //        "SENS:INT?"     → header="SENS:INT?",   param=""
  bool isQuery = header.endsWith("?");
  if (isQuery)
    header = header.substring(0, header.length() - 1);

  // ── IEEE 488.2 Common Commands ─────────────────────────────────────────────
  if (header == "*IDN")
  {
    if (isQuery) handleIDN();
    else errorQueue.push("-113,\"Undefined header; *IDN is query-only\"");
  }
  else if (header == "*RST")
  {
    if (!isQuery) handleRST();
    else errorQueue.push("-113,\"Undefined header; *RST is command-only\"");
  }
  else if (header == "*CLS")
  {
    if (!isQuery) handleCLS();
    else errorQueue.push("-113,\"Undefined header; *CLS is command-only\"");
  }

  // ── MEASure subsystem ──────────────────────────────────────────────────────
  else if (header == "MEAS:ANGL")
  {
    if (isQuery) handleMeasAngl(param);
    else errorQueue.push("-113,\"Undefined header; MEAS:ANGL is query-only\"");
  }
  else if (header == "MEAS:MAGN")
  {
    if (isQuery) handleMeasMagn(param);
    else errorQueue.push("-113,\"Undefined header; MEAS:MAGN is query-only\"");
  }

  // ── CONFigure subsystem ────────────────────────────────────────────────────
  else if (header == "CONF:ZERO")
  {
    if (!isQuery) handleConfZero(param);
    else errorQueue.push("-113,\"Undefined header; CONF:ZERO is command-only\"");
  }
  else if (header == "CONF:ERR")
  {
    if (!isQuery) handleConfErr(param);
    else errorQueue.push("-113,\"Undefined header; CONF:ERR is command-only\"");
  }

  // ── INITiate ───────────────────────────────────────────────────────────────
  else if (header == "INIT")
  {
    if (!isQuery) handleInit(param);
    else errorQueue.push("-113,\"Undefined header; INIT is command-only\"");
  }

  // ── ABORt ─────────────────────────────────────────────────────────────────
  else if (header == "ABOR")
  {
    if (!isQuery) handleAbor();
    else errorQueue.push("-113,\"Undefined header; ABOR is command-only\"");
  }

  // ── SENSe subsystem ────────────────────────────────────────────────────────
  else if (header == "SENS:INT")
  {
    handleSensInt(isQuery, param);
  }

  // ── SYSTem subsystem ───────────────────────────────────────────────────────
  else if (header == "SYST:ERR")
  {
    if (isQuery) handleSystErr();
    else errorQueue.push("-113,\"Undefined header; SYST:ERR is query-only\"");
  }
  else if (header == "SYST:DIAG")
  {
    if (isQuery) handleSystDiag(param);
    else errorQueue.push("-113,\"Undefined header; SYST:DIAG is query-only\"");
  }
  else if (header == "SYST:DEB")
  {
    handleSystDeb(isQuery, param);
  }
  else if (header == "SYST:HELP")
  {
    if (isQuery) printHelp();
    else errorQueue.push("-113,\"Undefined header; SYST:HELP is query-only\"");
  }

  else
  {
    errorQueue.push("-113,\"Undefined header: " + header + "\"");
  }
}

// ============================================================================
// MAIN LOOP
// ============================================================================

void loop()
{
  if (Serial.available())
  {
    String cmd = Serial.readStringUntil('\n');
    handleCommand(cmd);
  }

  unsigned long now = millis();
  if (appState.mode != MODE_IDLE && (now - appState.lastPoll >= appState.pollInterval))
  {
    appState.lastPoll = now;
    switch (appState.mode)
    {
    case MODE_CONTINUOUS_A:
      readAndSendAngle('A', encoderA);
      break;
    case MODE_CONTINUOUS_B:
      readAndSendAngle('B', encoderB);
      break;
    case MODE_CONTINUOUS_BOTH:
      readAndSendAngles();
      break;
    case MODE_CONTINUOUS_MAG:
      readAndSendMagnitudes();
      break;
    case MODE_CONTINUOUS_NOP:
      sendContinuousNOP();
      break;
    default:
      break;
    }
  }
}
