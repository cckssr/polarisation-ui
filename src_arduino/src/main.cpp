#include <Arduino.h>
#include <AS5048A.h>

// ============================================================================
// CONFIGURATION
// ============================================================================

// SPI CS pins for encoders
#define ENCODER_A_CS_PIN 9
#define ENCODER_B_CS_PIN 10

// Baud rate for USB communication
#define SERIAL_BAUDRATE 115200

// Default polling interval in continuous mode (ms)
#define DEFAULT_POLL_INTERVAL 50
#define SPI_CLOCK_HZ 100000 // 100 kHz

#define IDN_STRING "Polarisation-UI,AS5048A-DualEncoder,0,1.0"
#define MAX_ERRORS 10

// ============================================================================
// ERROR QUEUE (SCPI SYST:ERR?)
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
// STATISTICS STRUCTURE
// ============================================================================

struct ContinuousStats
{
  unsigned long startTime = 0;
  unsigned long endTime = 0;
  unsigned long dataPoints = 0;
  unsigned long parityErrors = 0;
  unsigned long errorFlagErrors = 0;
  unsigned long totalReadAttempts = 0;

  void reset()
  {
    startTime = 0;
    endTime = 0;
    dataPoints = 0;
    parityErrors = 0;
    errorFlagErrors = 0;
    totalReadAttempts = 0;
  }

  void print()
  {
    unsigned long durationMs = endTime - startTime;
    Serial.println("DATA:STAT DUR," + String(durationMs));
    Serial.println("DATA:STAT NPTS," + String(dataPoints));
    Serial.println("DATA:STAT PERR," + String(parityErrors));
    Serial.println("DATA:STAT EERR," + String(errorFlagErrors));
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
  bool encoderBPresent = false;
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
  appState.encoderBPresent = true;
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
// DATA CONVERSION
// ============================================================================

float convertRawToDegrees(uint16_t raw)
{
  return (raw & 0x3FFF) * 360.0 / 16384.0;
}

// ============================================================================
// ENCODER READ & SEND OPERATIONS
// ============================================================================

// Streaming output for single encoder angle
// Format: DATA:ANGL <id>,<deg>[,<raw>]
void readAndSendAngle(char encoderId, AS5048A_SPI &encoder)
{
  if (appState.debugOutput)
  {
    AS5048A_SPI::FrameResult result = encoder.readAngleRawWithDiagnostics();
    stats.totalReadAttempts++;
    if (!result.parityOk)
      stats.parityErrors++;
    if (result.errorFlag)
      stats.errorFlagErrors++;

    if (result.parityOk && !result.errorFlag)
    {
      stats.dataPoints++;
      float deg = convertRawToDegrees(result.data14);
      Serial.print("DATA:ANGL ");
      Serial.print(encoderId);
      Serial.print(",");
      Serial.print(deg, 2);
      Serial.print(",");
      Serial.println(result.data14, DEC);
    }
    else
    {
      errorQueue.push("-300,\"Hardware error encoder " + String(encoderId) + "\"");
      Serial.print("DATA:ANGL ");
      Serial.print(encoderId);
      Serial.println(",NAN");
    }
  }
  else
  {
    float deg = encoder.readAngleDeg();
    Serial.print("DATA:ANGL ");
    Serial.print(encoderId);
    Serial.print(",");
    Serial.println(deg, 2);
  }
}

// Streaming output for both encoders
// Format: DATA:ANGL BOTH,<deg_a>,<deg_b>
void readAndSendAngles()
{
  float angleA = encoderA.readAngleDeg();
  float angleB = appState.encoderBPresent ? encoderB.readAngleDeg() : 0.0;
  Serial.print("DATA:ANGL BOTH,");
  Serial.print(angleA, 2);
  Serial.print(",");
  Serial.println(angleB, 2);
}

// Streaming output for single encoder magnitude
// Format: DATA:MAGN <id>,<value>
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

// Streaming output for both magnitudes
// Format: DATA:MAGN BOTH,<val_a>,<val_b>
void readAndSendMagnitudes()
{
  AS5048A_SPI::FrameResult resultA = encoderA.readMagnitudeRawWithDiagnostics();
  AS5048A_SPI::FrameResult resultB = appState.encoderBPresent
                                         ? encoderB.readMagnitudeRawWithDiagnostics()
                                         : AS5048A_SPI::FrameResult{0, 0, false, true};

  Serial.print("DATA:MAGN BOTH,");
  Serial.print((!resultA.parityOk || resultA.errorFlag) ? "NAN" : String(resultA.data14));
  Serial.print(",");
  Serial.println((appState.encoderBPresent && (!resultB.parityOk || resultB.errorFlag)) ? "NAN" : String(resultB.data14));
}

// Streaming NOP signal quality test
// Format: DATA:NOP A,<parity>,0x<raw>[,B,<parity>,0x<raw>]
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

// *IDN?
void handleIDN()
{
  Serial.println(IDN_STRING);
}

// *RST
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

// *CLS
void handleCLS()
{
  errorQueue.clear();
}

// MEAS:ANGL? [A|B|BOTH]
// Response: <deg>  or  <deg_a>,<deg_b>
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

// MEAS:MAGN? [A|B|BOTH]
// Response: <raw>  or  <raw_a>,<raw_b>
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

// CONF:ZERO [A|B|BOTH]
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

// INIT ON,<target>  |  INIT OFF
void handleInit(const String &param)
{
  if (param.startsWith("ON"))
  {
    String target = "A";
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
  else if (param == "OFF" || param == "0")
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
    errorQueue.push("-102,\"Syntax error; expected ON,<target> or OFF\"");
  }
}

// ABOR - stop continuous mode
void handleAbor()
{
  if (appState.debugOutput && appState.mode != MODE_IDLE)
  {
    stats.endTime = millis();
    stats.print();
  }
  appState.mode = MODE_IDLE;
}

// SENS:INT <ms>  |  SENS:INT?
void handleSensInt(bool isQuery, const String &param)
{
  if (isQuery)
  {
    Serial.println(appState.pollInterval);
  }
  else
  {
    int interval = param.toInt();
    if (interval > 0 && interval < 10000)
    {
      appState.pollInterval = (unsigned long)interval;
    }
    else
    {
      errorQueue.push("-222,\"Data out of range; interval must be 1-9999 ms\"");
    }
  }
}

// SYST:ERR?
void handleSystErr()
{
  Serial.println(errorQueue.pop());
}

// SYST:DIAG? [A|B]
// Response: <compHigh>,<compLow>,<cof>,<ocf>,<agc>
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

// SYST:DEB ON|OFF|1|0  |  SYST:DEB?
void handleSystDeb(bool isQuery, const String &param)
{
  if (isQuery)
  {
    Serial.println(appState.debugOutput ? "1" : "0");
  }
  else
  {
    if (param == "ON" || param == "1")
      appState.debugOutput = true;
    else if (param == "OFF" || param == "0")
      appState.debugOutput = false;
    else
      errorQueue.push("-102,\"Syntax error; use ON, OFF, 1, or 0\"");
  }
}

// SYST:HELP?
void printHelp()
{
  Serial.println("=== AS5048A SCPI Command Reference ===");
  Serial.println("Common:");
  Serial.println("  *IDN?                  Identification string");
  Serial.println("  *RST                   Reset to defaults (stops streaming)");
  Serial.println("  *CLS                   Clear error queue");
  Serial.println("Measure (single read):");
  Serial.println("  MEAS:ANGL? A|B|BOTH    Read angle in degrees");
  Serial.println("  MEAS:MAGN? A|B|BOTH    Read raw magnitude (14-bit)");
  Serial.println("Configure:");
  Serial.println("  CONF:ZERO A|B|BOTH     Set current position as zero");
  Serial.println("Continuous streaming:");
  Serial.println("  INIT ON,A|B|BOTH       Start angle streaming");
  Serial.println("  INIT ON,MAG            Start magnitude streaming");
  Serial.println("  INIT ON,NOP            Start NOP signal quality test");
  Serial.println("  INIT OFF               Stop streaming (= ABOR)");
  Serial.println("  ABOR                   Abort streaming");
  Serial.println("Sense (settings):");
  Serial.println("  SENS:INT <ms>          Set poll interval (1-9999 ms)");
  Serial.println("  SENS:INT?              Query poll interval");
  Serial.println("System:");
  Serial.println("  SYST:ERR?              Query next error from queue");
  Serial.println("  SYST:DIAG? A|B         Read encoder diagnostics");
  Serial.println("  SYST:DEB ON|OFF        Enable/disable debug output");
  Serial.println("  SYST:DEB?              Query debug state");
  Serial.println("  SYST:HELP?             This help text");
  Serial.println("Streaming data format:");
  Serial.println("  DATA:ANGL A,<deg>      Single encoder angle");
  Serial.println("  DATA:ANGL BOTH,<a>,<b> Both encoder angles");
  Serial.println("  DATA:MAGN A,<raw>      Single encoder magnitude");
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

  // Split into header and parameter at first space
  String header = cmd;
  String param = "";
  int space = cmd.indexOf(' ');
  if (space >= 0)
  {
    header = cmd.substring(0, space);
    param = cmd.substring(space + 1);
    param.trim();
  }
  
  bool isQuery = header.endsWith("?");
  if (isQuery)
    header = header.substring(0, header.length() - 1);

  // Serial.println("DATA:INFO Received command: " + cmd);
  // Serial.println("DATA:INFO Parsed header: " + header + ", parameter: " + param + ", isQuery: " + String(isQuery ? "Yes" : "No"));
  
  // --- Common IEEE 488.2 commands ---
  if (header == "*IDN")
  {
    if (isQuery)
      handleIDN();
    else
      errorQueue.push("-113,\"Undefined header; *IDN is query-only\"");
  }
  else if (header == "*RST")
  {
    if (!isQuery)
      handleRST();
    else
      errorQueue.push("-113,\"Undefined header; *RST is command-only\"");
  }
  else if (header == "*CLS")
  {
    if (!isQuery)
      handleCLS();
    else
      errorQueue.push("-113,\"Undefined header; *CLS is command-only\"");
  }

  // --- MEASure subsystem ---
  else if (header == "MEAS:ANGL" || header == "MEASURE:ANGLE")
  {
    if (isQuery)
      handleMeasAngl(param);
    else
      errorQueue.push("-113,\"Undefined header; MEAS:ANGL is query-only\"");
  }
  else if (header == "MEAS:MAGN" || header == "MEASURE:MAGNITUDE")
  {
    if (isQuery)
      handleMeasMagn(param);
    else
      errorQueue.push("-113,\"Undefined header; MEAS:MAGN is query-only\"");
  }

  // --- CONFigure subsystem ---
  else if (header == "CONF:ZERO" || header == "CONFIGURE:ZERO")
  {
    if (!isQuery)
      handleConfZero(param);
    else
      errorQueue.push("-113,\"Undefined header; CONF:ZERO is command-only\"");
  }

  // --- INITiate ---
  else if (header == "INIT" || header == "INITIATE")
  {
    if (!isQuery)
      handleInit(param);
    else
      errorQueue.push("-113,\"Undefined header; INIT is command-only\"");
  }

  // --- ABORt ---
  else if (header == "ABOR" || header == "ABORT")
  {
    if (!isQuery)
      handleAbor();
    else
      errorQueue.push("-113,\"Undefined header; ABOR is command-only\"");
  }

  // --- SENSe subsystem ---
  else if (header == "SENS:INT" || header == "SENSE:INTERVAL")
  {
    handleSensInt(isQuery, param);
  }

  // --- SYSTem subsystem ---
  else if (header == "SYST:ERR" || header == "SYSTEM:ERROR")
  {
    if (isQuery)
      handleSystErr();
    else
      errorQueue.push("-113,\"Undefined header; SYST:ERR is query-only\"");
  }
  else if (header == "SYST:DIAG" || header == "SYSTEM:DIAGNOSTIC")
  {
    if (isQuery)
      handleSystDiag(param);
    else
      errorQueue.push("-113,\"Undefined header; SYST:DIAG is query-only\"");
  }
  else if (header == "SYST:DEB" || header == "SYSTEM:DEBUG")
  {
    handleSystDeb(isQuery, param);
  }
  else if (header == "SYST:HELP" || header == "SYSTEM:HELP")
  {
    if (isQuery)
      printHelp();
    else
      errorQueue.push("-113,\"Undefined header; SYST:HELP is query-only\"");
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
  // Handle incoming serial commands
  if (Serial.available())
  {
    String cmd = Serial.readStringUntil('\n');
    handleCommand(cmd);
  }

  // Continuous mode: poll at specified interval
  unsigned long now = millis();
  if (appState.mode != MODE_IDLE &&
      (now - appState.lastPoll >= appState.pollInterval))
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
