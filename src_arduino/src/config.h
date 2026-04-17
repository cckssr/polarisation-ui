#pragma once

// ── Encoder SPI ───────────────────────────────────────────────────────────────
#define ENC_CS_A 9
#define ENC_CS_B 10
#define SPI_HZ 100000UL

// ── ADS1220 ADC ───────────────────────────────────────────────────────────────
#define ADC_CS_PIN 5   // chip select  (active low)
#define ADC_DRDY_PIN 4 // DRDY output  (active low)
#define ADC_SPI_HZ 4000000UL

// ── PD-TIA discrete gain select (4 GPIO lines, active HIGH) ──────────────────
// Bit 0 of the gain pattern maps to PIN_0, bit 3 to PIN_3.
#define PDTIA_PIN_0 6
#define PDTIA_PIN_1 7
#define PDTIA_PIN_2 8
#define PDTIA_PIN_3 3
// Number of gain stages.  The actual 4-bit patterns live in ads_session.cpp.
#define PDTIA_NUM_STAGES 5

// ── Serial ────────────────────────────────────────────────────────────────────
#define BAUD_RATE 115200

// ── Firmware identity (*IDN?) ─────────────────────────────────────────────────
#define DEVICE_MFR "ams OSRAM"
#define DEVICE_MODEL "AS5048A-dual-ADS1220"
#define DEVICE_SERIAL "0"
#define FW_VERSION "2.0.0"

// ── Streaming defaults ────────────────────────────────────────────────────────
#define DEFAULT_STREAM_RATE_HZ 20   // 50 ms per frame
#define DEFAULT_STREAM_SOURCES 0x03 // SRC_ENC_A | SRC_ENC_B

// ── Error queue capacity ──────────────────────────────────────────────────────
#define ERR_QUEUE_SIZE 10
