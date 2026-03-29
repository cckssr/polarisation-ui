#include "scpi.h"
#include "encoder.h"

// ── Parser ─────────────────────────────────────────────────────────────────

bool scpiParse(const String &line, String &header, String &param, bool &isQuery)
{
  if (line.length() == 0)
    return false;

  // Split at first space → header + param
  int sp = line.indexOf(' ');
  if (sp >= 0)
  {
    header = line.substring(0, sp);
    param = line.substring(sp + 1);
    param.trim();
  }
  else
  {
    header = line;
    param = "";
  }

  // '?' is part of the header (not the param): "MEAS:ANGL? A" → header="MEAS:ANGL?"
  isQuery = header.endsWith("?");
  if (isQuery)
    header = header.substring(0, header.length() - 1);

  return true;
}

// ── Helpers ────────────────────────────────────────────────────────────────

static void errQueryOnly(const String &h)
{
  errorQueue.push("-113,\"Undefined header; " + h + " is query-only\"");
}
static void errCmdOnly(const String &h)
{
  errorQueue.push("-113,\"Undefined header; " + h + " is command-only\"");
}

// ── IEEE 488.2 common commands ─────────────────────────────────────────────

static void handleIDN()
{
  Serial.println(DEVICE_MFR "," DEVICE_MODEL "," DEVICE_SERIAL "," FW_VERSION);
}

static void handleRST()
{
  if (appState.debug && appState.mode != AcqMode::Idle)
  {
    acqStats.endMs = millis();
    acqStats.print();
  }
  appState.mode = AcqMode::Idle;
  appState.pollMs = DEFAULT_POLL_MS;
  appState.debug = false;
  errorQueue.clear();
  acqStats.reset();
}

static void handleCLS()
{
  errorQueue.clear();
}

// *TST? — self-test: returns 0 (pass) always; hardware test not implemented.
static void handleTST()
{
  Serial.println(0);
}

// *OPC? — returns 1 (operation complete) because this device is synchronous.
static void handleOPCQuery()
{
  Serial.println(1);
}

// ── INIT:CONT subsystem ────────────────────────────────────────────────────
// Syntax:
//   INIT:CONT ON[,A|B|BOTH|MAG|NOP]  — start continuous acquisition
//   INIT:CONT OFF                     — stop continuous acquisition
//   INIT:CONT?                        — query streaming state (0|1)

static void stopAcq()
{
  if (appState.debug && appState.mode != AcqMode::Idle)
  {
    acqStats.endMs = millis();
    acqStats.print();
  }
  appState.mode = AcqMode::Idle;
}

static void handleInitCont(bool isQuery, const String &param)
{
  if (isQuery)
  {
    Serial.println(appState.mode != AcqMode::Idle ? 1 : 0);
    return;
  }

  if (param.startsWith("ON"))
  {
    String target = "BOTH"; // default: both encoders angle
    int comma = param.indexOf(',');
    if (comma >= 0)
    {
      target = param.substring(comma + 1);
      target.trim();
    }

    AcqMode next;
    if (target == "A")
      next = AcqMode::AngleA;
    else if (target == "B")
      next = AcqMode::AngleB;
    else if (target == "BOTH")
      next = AcqMode::AngleBoth;
    else if (target == "MAG")
      next = AcqMode::Magnitude;
    else if (target == "NOP")
      next = AcqMode::Nop;
    else
    {
      errorQueue.push("-113,\"Undefined header; unknown target: " + target + "\"");
      return;
    }

    if ((next == AcqMode::AngleB || next == AcqMode::AngleBoth) && !appState.encBPresent)
    {
      errorQueue.push("-241,\"Hardware missing; encoder B not present\"");
      return;
    }

    appState.mode = next;
    appState.lastPollMs = millis();
    if (appState.debug)
    {
      acqStats.reset();
      acqStats.startMs = millis();
    }
  }
  else if (param == "OFF")
  {
    stopAcq();
  }
  else
  {
    errorQueue.push("-102,\"Syntax error; expected: INIT:CONT ON[,A|B|BOTH|MAG|NOP] or OFF\"");
  }
}

// ── ABOR ──────────────────────────────────────────────────────────────────
static void handleAbor()
{
  stopAcq();
}

// ── SENS:INT subsystem ─────────────────────────────────────────────────────
static void handleSensInt(bool isQuery, const String &param)
{
  if (isQuery)
  {
    Serial.println(appState.pollMs);
    return;
  }
  int ms = param.toInt();
  if (ms >= 1 && ms <= 9999)
    appState.pollMs = (unsigned long)ms;
  else
    errorQueue.push("-222,\"Data out of range; interval must be 1-9999 ms\"");
}

// ── SYST subsystem ─────────────────────────────────────────────────────────

static void handleSystErr()
{
  Serial.println(errorQueue.pop());
}

static void handleSystDeb(bool isQuery, const String &param)
{
  if (isQuery)
  {
    Serial.println(appState.debug ? 1 : 0);
    return;
  }
  if (param == "ON" || param == "1")
    appState.debug = true;
  else if (param == "OFF" || param == "0")
    appState.debug = false;
  else
    errorQueue.push("-102,\"Syntax error; use ON, OFF, 1, or 0\"");
}

static void handleSystHelp()
{
  Serial.println("=== SCPI Command Reference (IEC 60488-2) ===");
  Serial.println("Common commands:");
  Serial.println("  *IDN?                 Identification: MFR,MODEL,SN,FW");
  Serial.println("  *RST                  Reset to defaults, stop streaming");
  Serial.println("  *CLS                  Clear error queue");
  Serial.println("  *TST?                 Self-test (returns 0=pass)");
  Serial.println("  *OPC?                 Returns 1 (always complete)");
  Serial.println("  *OPC  *WAI            No-op (synchronous device)");
  Serial.println("MEASure — single-shot queries:");
  Serial.println("  MEAS:ANGL? A|B|BOTH   Angle in degrees");
  Serial.println("  MEAS:MAGN? A|B|BOTH   Raw magnitude (14-bit)");
  Serial.println("CONFigure — hardware config commands:");
  Serial.println("  CONF:ZERO A|B|BOTH    Set software zero position");
  Serial.println("  CONF:ERR  A|B|BOTH    Clear hardware Error Flag");
  Serial.println("INITiate:CONTinuous — streaming control:");
  Serial.println("  INIT:CONT ON[,A|B|BOTH|MAG|NOP]  Start streaming");
  Serial.println("  INIT:CONT OFF                     Stop streaming");
  Serial.println("  INIT:CONT?                        Query streaming state");
  Serial.println("ABORt:");
  Serial.println("  ABOR                  Stop streaming (= INIT:CONT OFF)");
  Serial.println("SENSe — acquisition settings:");
  Serial.println("  SENS:INT <ms>         Set poll interval (1-9999 ms)");
  Serial.println("  SENS:INT?             Query poll interval");
  Serial.println("SYSTem:");
  Serial.println("  SYST:ERR?             Pop oldest error: <code>,\"<msg>\"");
  Serial.println("  SYST:DIAG? A|B        Diagnostics: compH,compL,cof,ocf,agc");
  Serial.println("  SYST:DEB ON|OFF       Enable/disable verbose debug output");
  Serial.println("  SYST:DEB?             Query debug state (0 or 1)");
  Serial.println("  SYST:HELP?            This help text");
  Serial.println("Streaming output (INIT:CONT):");
  Serial.println("  DATA:ANGL A,<deg>              Single angle");
  Serial.println("  DATA:ANGL A,<deg>,<raw14>       + raw value (debug mode)");
  Serial.println("  DATA:ANGL BOTH,<deg_a>,<deg_b>  Both angles");
  Serial.println("  DATA:MAGN A|BOTH,<raw14>...     Magnitude");
  Serial.println("  DATA:NOP A[,B],<OK|FAIL>,0x...  SPI signal test");
  Serial.println("  DATA:STAT ...         Statistics on stream stop (debug)");
  Serial.println("============================================");
}

// ── Main dispatcher ────────────────────────────────────────────────────────

void scpiDispatch(const String &line)
{
  String header, param;
  bool isQuery;
  if (!scpiParse(line, header, param, isQuery))
    return;

  // ── IEEE 488.2 common commands ──────────────────────────────────────────
  if (header == "*IDN")
  {
    if (isQuery)
      handleIDN();
    else
      errQueryOnly(header);
  }
  else if (header == "*RST")
  {
    if (!isQuery)
      handleRST();
    else
      errCmdOnly(header);
  }
  else if (header == "*CLS")
  {
    if (!isQuery)
      handleCLS();
    else
      errCmdOnly(header);
  }
  else if (header == "*TST")
  {
    if (isQuery)
      handleTST();
    else
      errQueryOnly(header);
  }
  else if (header == "*OPC")
  {
    if (isQuery)
      handleOPCQuery(); /* else: no-op */
  }
  else if (header == "*WAI")
  { /* no-op — synchronous device */
  }

  // ── MEASure subsystem ───────────────────────────────────────────────────
  else if (header == "MEAS:ANGL")
  {
    if (isQuery)
      handleMeasAngl(param);
    else
      errQueryOnly(header);
  }
  else if (header == "MEAS:MAGN")
  {
    if (isQuery)
      handleMeasMagn(param);
    else
      errQueryOnly(header);
  }

  // ── CONFigure subsystem ─────────────────────────────────────────────────
  else if (header == "CONF:ZERO")
  {
    if (!isQuery)
      handleConfZero(param);
    else
      errCmdOnly(header);
  }
  else if (header == "CONF:ERR")
  {
    if (!isQuery)
      handleConfErr(param);
    else
      errCmdOnly(header);
  }

  // ── INITiate:CONTinuous subsystem ───────────────────────────────────────
  else if (header == "INIT:CONT")
  {
    handleInitCont(isQuery, param);
  }

  // ── ABORt ───────────────────────────────────────────────────────────────
  else if (header == "ABOR")
  {
    if (!isQuery)
      handleAbor();
    else
      errCmdOnly(header);
  }

  // ── SENSe subsystem ─────────────────────────────────────────────────────
  else if (header == "SENS:INT")
  {
    handleSensInt(isQuery, param);
  }

  // ── SYSTem subsystem ────────────────────────────────────────────────────
  else if (header == "SYST:ERR")
  {
    if (isQuery)
      handleSystErr();
    else
      errQueryOnly(header);
  }
  else if (header == "SYST:DIAG")
  {
    if (isQuery)
      handleSystDiag(param);
    else
      errQueryOnly(header);
  }
  else if (header == "SYST:DEB")
  {
    handleSystDeb(isQuery, param);
  }
  else if (header == "SYST:HELP")
  {
    if (isQuery)
      handleSystHelp();
    else
      errQueryOnly(header);
  }

  else
  {
    errorQueue.push("-113,\"Undefined header: " + header + "\"");
  }
}
