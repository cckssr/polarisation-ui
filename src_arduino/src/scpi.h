#pragma once
#include <Arduino.h>
#include "state.h"

// Parse one command line.
// Strips trailing '?' from header into isQuery.
// Returns false if line is empty.
bool scpiParse(const String &line, String &header, String &param, bool &isQuery);

// Main dispatcher. Routes to sensor-specific modules.
void scpiDispatch(const String &line);
