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
  MODE_CONTINUOUS_BOTH
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
  encoderA.begin(1000000); // 1 MHz SPI clock

  // Try to initialize Encoder B (optional)
  // You can change logic here for auto-detection
  encoderB.begin(1000000);
  appState.encoderBPresent = true; // Assume present for now

  Serial.println("INFO:Encoders initialized");
}

void setup()
{
  Serial.begin(SERIAL_BAUDRATE);
  delay(500); // Allow serial port to stabilize

  Serial.println("INFO:AS5048A Dual Encoder System Ready");
  Serial.println("INFO:Send commands: C_A1|C_A0|C_B1|C_B0|C_BOTH1|C_BOTH0|R_A|R_B|Z_A|Z_B|P:100");

  initEncoders();
}

// ============================================================================
// ENCODER READ OPERATIONS
// ============================================================================

void readAndSendEncoder(char encoderId, AS5048A_SPI &encoder)
{
  float angleDeg = encoder.readAngleDeg();
  uint16_t angleRaw = encoder.readAngleRaw();

  // Format: ENCODER,A,angle_deg,angle_raw
  Serial.print("DATA,");
  Serial.print(encoderId);
  Serial.print(",");
  Serial.print(angleDeg, 2); // 2 decimal places
  Serial.print(",");
  Serial.println(angleRaw);
}

void readAndSendBoth()
{
  float angleA = encoderA.readAngleDeg();
  float angleB = appState.encoderBPresent ? encoderB.readAngleDeg() : 0.0;

  // Format: DATA_BOTH,angle_a,angle_b
  Serial.print("DATA_BOTH,");
  Serial.print(angleA, 2);
  Serial.print(",");
  Serial.println(angleB, 2);
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
  Serial.println("Zero Position:");
  Serial.println("  Z_A        - Set zero for encoder A");
  Serial.println("  Z_B        - Set zero for encoder B");
  Serial.println("  Z_BOTH     - Set zero for both");
  Serial.println("Settings:");
  Serial.println("  P:100      - Set poll interval to 100 ms");
  Serial.println("Diagnostics:");
  Serial.println("  DIAG_A     - Read diagnostics for encoder A");
  Serial.println("  DIAG_B     - Read diagnostics for encoder B");
  Serial.println("=====================================\n");
}


void handleCommand(String cmd)
{
  cmd.trim();

  // Mode control: Enable continuous reading
  if (cmd == "C_A1")
  {
    appState.mode = MODE_CONTINUOUS_A;
    appState.lastPoll = millis();
    Serial.println("OK:Mode continuous A");
  }
  else if (cmd == "C_A0")
  {
    appState.mode = MODE_IDLE;
    Serial.println("OK:Mode idle");
  }
  else if (cmd == "C_B1" && appState.encoderBPresent)
  {
    appState.mode = MODE_CONTINUOUS_B;
    appState.lastPoll = millis();
    Serial.println("OK:Mode continuous B");
  }
  else if (cmd == "C_B0")
  {
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

  // Single read commands
  else if (cmd == "R_A")
  {
    readAndSendEncoder('A', encoderA);
  }
  else if (cmd == "R_B" && appState.encoderBPresent)
  {
    readAndSendEncoder('B', encoderB);
  }
  else if (cmd == "R_BOTH" && appState.encoderBPresent)
  {
    readAndSendBoth();
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
      readAndSendEncoder('A', encoderA);
      break;
    case MODE_CONTINUOUS_B:
      readAndSendEncoder('B', encoderB);
      break;
    case MODE_CONTINUOUS_BOTH:
      readAndSendBoth();
      break;
    default:
      break;
    }
  }
}