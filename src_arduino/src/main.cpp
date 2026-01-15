#include <Arduino.h>
#include <AS5048A.h>

// ============================================================================
// CONFIGURATION
// ============================================================================

// SPI CS pins for encoders
#define ENCODER_A_CS_PIN 10
#define ENCODER_B_CS_PIN 9

// Baud rate for USB communication
#define SERIAL_BAUDRATE 115200

// Default polling interval in continuous mode (ms)
#define DEFAULT_POLL_INTERVAL 50
#define SPI_CLOCK_HZ 100000 // 100 kHz

// Debugging output
bool debugOutput = false;

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
    float durationSec = durationMs / 1000.0f;

    Serial.println("\n=== CONTINUOUS MODE STATISTICS ===");
    Serial.print("Duration: ");
    Serial.print(durationMs);
    Serial.println(" ms");

    Serial.print("Data points: ");
    Serial.println(dataPoints);

    if (dataPoints > 0)
    {
      float avgTimePerPoint = durationMs / (float)dataPoints;
      Serial.print("Avg time per point: ");
      Serial.print(avgTimePerPoint, 2);
      Serial.print(" ms (normal: ");
      Serial.print(DEFAULT_POLL_INTERVAL);
      Serial.println(" ms)");
    }

    Serial.print("Total read attempts: ");
    Serial.println(totalReadAttempts);

    if (totalReadAttempts > 0)
    {
      float parityErrorRate = (parityErrors * 100.0f) / totalReadAttempts;
      float errorFlagRate = (errorFlagErrors * 100.0f) / totalReadAttempts;

      Serial.print("Parity errors: ");
      Serial.print(parityErrors);
      Serial.print(" (");
      Serial.print(parityErrorRate, 1);
      Serial.println("%)");

      Serial.print("Error flag errors: ");
      Serial.print(errorFlagErrors);
      Serial.print(" (");
      Serial.print(errorFlagRate, 1);
      Serial.println("%)");
    }

    Serial.println("==================================\n");
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
  bool encoderBPresent = false; // Auto-detect or manual config
};

AppState appState;

// ============================================================================
// INITIALIZATION
// ============================================================================

void initEncoders()
{
  // Initialize Encoder A (always present)
  encoderA.begin(SPI_CLOCK_HZ);

  // Try to initialize Encoder B (optional)
  // You can change logic here for auto-detection
  encoderB.begin(SPI_CLOCK_HZ);
  appState.encoderBPresent = false; // Assume present for now

  Serial.println("INFO:Encoders initialized");
}

void setup()
{
  Serial.begin(SERIAL_BAUDRATE);
  delay(500); // Allow serial port to stabilize

  Serial.println("INFO:AS5048A Dual Encoder System Ready");
  Serial.println("INFO:Send commands: C_A1|C_A0|C_B1|C_B0|C_BOTH1|C_BOTH0|C_MAG1|C_MAG0|R_A|R_B|R_BOTH|M_A|M_B|M_BOTH|Z_A|Z_B|Z_BOTH|P:100");

  initEncoders();
}

// ============================================================================
// PRINTING AND DATA CONVERSION
// ============================================================================

enum DataType
{
  ANGLE,
  MAGNITUDE,
  NOP_TEST
};

float convertRawToDegrees(uint16_t raw)
{
  // Convert 14-bit raw value to angular degrees
  return (raw & 0x3FFF) * 360.0 / 16384.0;
}

// Unified output function for encoder frame data
// Format: <dataType>,<encoderId>,<parity>,<errorFlag>,<angle_deg>,<raw>
// Error flag only printed if debugOutput is true
void printFrameResult(const char *dataType, char encoderId, const AS5048A_SPI::FrameResult &result, float degreesValue = -1.0)
{
  Serial.print(dataType);
  Serial.print(",");
  Serial.print(encoderId);
  Serial.print(",");
  Serial.print(result.parityOk ? "OK" : "NO");

  // Only include error flag if debug mode is enabled
  if (debugOutput)
  {
    Serial.print(",");
    Serial.print(result.errorFlag ? "SET" : "OK");
  }

  Serial.print(",");

  // If degrees value provided (for angle data), print it
  if (degreesValue >= 0.0)
  {
    Serial.print(degreesValue, 2);
    Serial.print(",");
    Serial.println(result.data14, DEC);
  }
  else
  {
    // For magnitude or NOP, just print raw
    Serial.println(result.data14, DEC);
  }
}

// ============================================================================
// UNIFIED ENCODER READ & SEND OPERATIONS
// ============================================================================

// Read angle from single encoder and send formatted output
// Debug ON: raw value + parity check + deg calculation
// Debug OFF: direct deg read (respects zero position)
void readAndSendAngle(char encoderId, AS5048A_SPI &encoder)
{
  if (debugOutput)
  {
    // Debug mode: read raw with diagnostics
    AS5048A_SPI::FrameResult result = encoder.readAngleRawWithDiagnostics();

    // Collect statistics
    if (appState.mode == MODE_CONTINUOUS_A || appState.mode == MODE_CONTINUOUS_B)
    {
      stats.totalReadAttempts++;
      if (!result.parityOk)
        stats.parityErrors++;
      if (result.errorFlag)
        stats.errorFlagErrors++;
    }

    float angleDeg = convertRawToDegrees(result.data14);
    printFrameResult("DATA", encoderId, result, angleDeg);

    // Only count successful reads
    if (result.parityOk && !result.errorFlag &&
        (appState.mode == MODE_CONTINUOUS_A || appState.mode == MODE_CONTINUOUS_B))
    {
      stats.dataPoints++;
    }
  }
  else
  {
    // Normal mode: read deg directly (respects zero position)
    float angleDeg = encoder.readAngleDeg();

    // Simple output without parity/error flags
    Serial.print("DATA,");
    Serial.print(encoderId);
    Serial.print(",");
    Serial.println(angleDeg, 2);
  }
}

// Read angles from both encoders and send
void readAndSendAngles()
{
  if (debugOutput)
  {
    // Debug mode: raw values with diagnostics
    AS5048A_SPI::FrameResult resultA = encoderA.readAngleRawWithDiagnostics();
    AS5048A_SPI::FrameResult resultB = appState.encoderBPresent ? encoderB.readAngleRawWithDiagnostics() : AS5048A_SPI::FrameResult{0, 0, false, true};

    // Check parity and error flags
    if (!resultA.parityOk)
    {
      Serial.println("ERRO,A,Parity check failed");
      return;
    }
    if (resultA.errorFlag)
    {
      Serial.println("ERRO,A,Error flag set");
      return;
    }

    if (appState.encoderBPresent)
    {
      if (!resultB.parityOk)
      {
        Serial.println("ERRO,B,Parity check failed");
        return;
      }
      if (resultB.errorFlag)
      {
        Serial.println("ERRO,B,Error flag set");
        return;
      }
    }

    float angleA = convertRawToDegrees(resultA.data14);
    float angleB = appState.encoderBPresent ? convertRawToDegrees(resultB.data14) : 0.0;

    // Format: DATA_BOTH,angle_a,angle_b
    Serial.print("DATA_BOTH,");
    Serial.print(angleA, 2);
    Serial.print(",");
    Serial.println(angleB, 2);
  }
  else
  {
    // Normal mode: direct deg read (respects zero position)
    float angleA = encoderA.readAngleDeg();
    float angleB = appState.encoderBPresent ? encoderB.readAngleDeg() : 0.0;

    // Format: DATA_BOTH,angle_a,angle_b
    Serial.print("DATA_BOTH,");
    Serial.print(angleA, 2);
    Serial.print(",");
    Serial.println(angleB, 2);
  }
}

// Read magnitude from single encoder
void readAndSendMagnitude(char encoderId, AS5048A_SPI &encoder)
{
  AS5048A_SPI::FrameResult result = encoder.readMagnitudeRawWithDiagnostics();

  if (!result.parityOk || result.errorFlag)
  {
    Serial.print("ERRO,");
    Serial.print(encoderId);
    Serial.println(",Magnitude read failed");
  }
  else
  {
    printFrameResult("MAG", encoderId, result);
  }
}

// Read magnitudes from both encoders
void readAndSendMagnitudes()
{
  AS5048A_SPI::FrameResult resultA = encoderA.readMagnitudeRawWithDiagnostics();
  AS5048A_SPI::FrameResult resultB = appState.encoderBPresent ? encoderB.readMagnitudeRawWithDiagnostics() : AS5048A_SPI::FrameResult{0, 0, false, true};

  // Check parity and error flags for both encoders
  if (!resultA.parityOk || resultA.errorFlag)
  {
    Serial.println("ERRO,A,Magnitude read failed");
    return;
  }
  if (appState.encoderBPresent && (!resultB.parityOk || resultB.errorFlag))
  {
    Serial.println("ERRO,B,Magnitude read failed");
    return;
  }

  Serial.print("MAG_BOTH,");
  Serial.print(resultA.data14);
  Serial.print(",");
  Serial.println(resultB.data14);
}

// Send continuous NOP to check signal quality
void sendContinuousNOP()
{
  AS5048A_SPI::FrameResult resultA = encoderA.nop();
  AS5048A_SPI::FrameResult resultB = appState.encoderBPresent ? encoderB.nop() : AS5048A_SPI::FrameResult{0, 0, false, true};

  Serial.print("NOP,A,");
  Serial.print(resultA.parityOk ? "OK" : "FAIL");
  Serial.print(",");
  Serial.print(resultA.errorFlag ? "SET" : "OK");
  Serial.print(",0x");
  Serial.print(resultA.raw16, HEX);

  if (appState.encoderBPresent)
  {
    Serial.print(" | B,");
    Serial.print(resultB.parityOk ? "OK" : "FAIL");
    Serial.print(",");
    Serial.print(resultB.errorFlag ? "SET" : "OK");
    Serial.print(",0x");
    Serial.println(resultB.raw16, HEX);
  }
  else
  {
    Serial.println();
  }
}

// ============================================================================
// COMMAND PROCESSING
// ============================================================================
void printHelp()
{
  Serial.println("\n=== AS5048A Command Reference ===");
  Serial.println("Mode Control:");
  Serial.println("  C_A1       - Start continuous reading encoder A");
  Serial.println("  C_A0       - Stop continuous reading encoder A");
  Serial.println("  C_B1       - Start continuous reading encoder B");
  Serial.println("  C_B0       - Stop continuous reading encoder B");
  Serial.println("  C_BOTH1    - Start continuous reading both");
  Serial.println("  C_BOTH0    - Stop continuous reading");
  Serial.println("Single Read:");
  Serial.println("  R_A        - Read encoder A once");
  Serial.println("  R_B        - Read encoder B once");
  Serial.println("  R_BOTH     - Read both encoders once");
  Serial.println("  M_A        - Read magnitude encoder A once");
  Serial.println("  M_B        - Read magnitude encoder B once");
  Serial.println("  M_BOTH     - Read magnitude of both once");
  Serial.println("Zero Position:");
  Serial.println("  Z_A        - Set zero for encoder A");
  Serial.println("  Z_B        - Set zero for encoder B");
  Serial.println("  Z_BOTH     - Set zero for both");
  Serial.println("Settings:");
  Serial.println("  P:100      - Set poll interval to 100 ms");
  Serial.println("  DEBUG:1    - Enable debug output & statistics");
  Serial.println("  DEBUG:0    - Disable debug output");
  Serial.println("Diagnostics:");
  Serial.println("  DIAG_A     - Read diagnostics for encoder A");
  Serial.println("  DIAG_B     - Read diagnostics for encoder B");
  Serial.println("Continuous Magnitude:");
  Serial.println("  C_MAG1     - Start continuous magnitude (both)");
  Serial.println("  C_MAG0     - Stop continuous magnitude");
  Serial.println("Signal Quality:");
  Serial.println("  C_NOP1     - Start continuous NOP (signal test)");
  Serial.println("  C_NOP0     - Stop continuous NOP");
  Serial.println("=====================================\n");
}

void handleCommand(String cmd)
{
  cmd.trim();
  cmd.toUpperCase();

  // Mode control: Enable continuous reading
  if (cmd == "C_A1")
  {
    appState.mode = MODE_CONTINUOUS_A;
    appState.lastPoll = millis();
    if (debugOutput)
    {
      stats.reset();
      stats.startTime = millis();
    }
    Serial.println("OK:Mode continuous A");
  }
  else if (cmd == "C_A0")
  {
    if (debugOutput && appState.mode == MODE_CONTINUOUS_A)
    {
      stats.endTime = millis();
      stats.print();
    }
    appState.mode = MODE_IDLE;
    Serial.println("OK:Mode idle");
  }
  else if (cmd == "C_B1" && appState.encoderBPresent)
  {
    appState.mode = MODE_CONTINUOUS_B;
    appState.lastPoll = millis();
    if (debugOutput)
    {
      stats.reset();
      stats.startTime = millis();
    }
    Serial.println("OK:Mode continuous B");
  }
  else if (cmd == "C_B0")
  {
    if (debugOutput && appState.mode == MODE_CONTINUOUS_B)
    {
      stats.endTime = millis();
      stats.print();
    }
    appState.mode = MODE_IDLE;
    Serial.println("OK:Mode idle");
  }
  else if (cmd == "C_BOTH1" && appState.encoderBPresent)
  {
    appState.mode = MODE_CONTINUOUS_BOTH;
    appState.lastPoll = millis();
    Serial.println("OK:Mode continuous both");
  }
  else if (cmd == "C_BOTH0")
  {
    appState.mode = MODE_IDLE;
    Serial.println("OK:Mode idle");
  }
  else if (cmd == "C_MAG1")
  {
    appState.mode = MODE_CONTINUOUS_MAG;
    appState.lastPoll = millis();
    Serial.println("OK:Mode continuous magnitude");
  }
  else if (cmd == "C_MAG0")
  {
    appState.mode = MODE_IDLE;
    Serial.println("OK:Mode idle");
  }
  else if (cmd == "C_NOP1")
  {
    appState.mode = MODE_CONTINUOUS_NOP;
    appState.lastPoll = millis();
    Serial.println("OK:Mode continuous NOP (signal quality test)");
  }
  else if (cmd == "C_NOP0")
  {
    appState.mode = MODE_IDLE;
    Serial.println("OK:Mode idle");
  }

  // Single read commands
  else if (cmd == "R_A")
  {
    readAndSendAngle('A', encoderA);
  }
  else if (cmd == "R_B" && appState.encoderBPresent)
  {
    readAndSendAngle('B', encoderB);
  }
  else if (cmd == "R_BOTH")
  {
    readAndSendAngles();
  }
  else if (cmd == "M_A")
  {
    readAndSendMagnitude('A', encoderA);
  }
  else if (cmd == "M_B" && appState.encoderBPresent)
  {
    readAndSendMagnitude('B', encoderB);
  }
  else if (cmd == "M_BOTH")
  {
    readAndSendMagnitudes();
  }

  // Zero position commands
  else if (cmd == "Z_A")
  {
    encoderA.setSoftwareZero();
    Serial.println("OK:Zero set for encoder A");
  }
  else if (cmd == "Z_B" && appState.encoderBPresent)
  {
    encoderB.setSoftwareZero();
    Serial.println("OK:Zero set for encoder B");
  }
  else if (cmd == "Z_BOTH" && appState.encoderBPresent)
  {
    encoderA.setSoftwareZero();
    encoderB.setSoftwareZero();
    Serial.println("OK:Zero set for both encoders");
  }

  // Poll interval adjustment (e.g., "P:100")
  else if (cmd.startsWith("P:"))
  {
    int interval = cmd.substring(2).toInt();
    if (interval > 0 && interval < 10000)
    {
      appState.pollInterval = interval;
      Serial.print("OK:Poll interval set to ");
      Serial.print(interval);
      Serial.println(" ms");
    }
    else
    {
      Serial.println("ERROR:Invalid poll interval");
    }
  }

  // Debug output control
  else if (cmd.startsWith("DEBUG:"))
  {
    int debugVal = cmd.substring(6).toInt();
    if (debugVal == 1 || debugVal == 0)
    {
      debugOutput = (debugVal == 1);
      Serial.print("OK:Debug output ");
      Serial.println(debugOutput ? "enabled" : "disabled");
    }
    else
    {
      Serial.println("ERROR:Use DEBUG:0 or DEBUG:1");
    }
  }

  // Diagnostics
  else if (cmd == "DIAG_A")
  {
    AS5048A_SPI::Diagnostics diag = encoderA.readDiagnostics();
    Serial.print("DIAG_A,compHigh:");
    Serial.print(diag.compHigh);
    Serial.print(",compLow:");
    Serial.print(diag.compLow);
    Serial.print(",cof:");
    Serial.print(diag.cof);
    Serial.print(",ocf:");
    Serial.print(diag.ocf);
    Serial.print(",agc:");
    Serial.println(diag.agc);
  }
  else if (cmd == "DIAG_B" && appState.encoderBPresent)
  {
    AS5048A_SPI::Diagnostics diag = encoderB.readDiagnostics();
    Serial.print("DIAG_B,compHigh:");
    Serial.print(diag.compHigh);
    Serial.print(",compLow:");
    Serial.print(diag.compLow);
    Serial.print(",cof:");
    Serial.print(diag.cof);
    Serial.print(",ocf:");
    Serial.print(diag.ocf);
    Serial.print(",agc:");
    Serial.println(diag.agc);
  }

  // Help
  else if (cmd == "?" || cmd == "HELP")
  {
    printHelp();
  }

  else
  {
    Serial.println("ERROR:Unknown command");
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