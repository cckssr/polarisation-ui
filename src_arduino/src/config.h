#pragma once

// ── Hardware ──────────────────────────────────────────────────────────────
#define ENC_CS_A       9
#define ENC_CS_B       10
#define SPI_HZ         100000UL
#define BAUD_RATE      115200

// ── Firmware identity (used in *IDN?) ─────────────────────────────────────
#define DEVICE_MFR     "ams OSRAM"
#define DEVICE_MODEL   "AS5048A-dual"
#define DEVICE_SERIAL  "0"
#define FW_VERSION     "1.1"

// ── Acquisition defaults ──────────────────────────────────────────────────
#define DEFAULT_POLL_MS  50

// ── Error queue capacity ──────────────────────────────────────────────────
#define ERR_QUEUE_SIZE  10
