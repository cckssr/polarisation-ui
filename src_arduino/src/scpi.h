#pragma once
#include <Arduino.h>
#include "state.h"

// Parse one SCPI command line.
// Strips trailing '?' from header into isQuery.
// Returns false if line is empty.
bool scpiParse(const String &line, String &header, String &param, bool &isQuery);

// Route a parsed command line to the correct handler.
void scpiDispatch(const String &line);

// Emit a single DATA:FRAME line for all enabled stream sources.
// Called from loop() when the stream timer fires, and for single-shot INIT.
void emitDataFrame();
