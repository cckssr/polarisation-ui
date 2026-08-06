#pragma once

// ── Encoder SPI ───────────────────────────────────────────────────────────────
#define ENC_CS_A 10     // chip select for sample stage encoder
#define ENC_CS_B 9      // chip select for detector stage encoder
#define SPI_HZ 1000000UL

// ── ADS1220 ADC ───────────────────────────────────────────────────────────────
// Uses second SPI peripheral (HSPI) on the ESP32, with dedicated GPIO pins.
#define ADC_MISO_PIN 5
#define ADC_MOSI_PIN 6
#define ADC_SCK_PIN 7
#define ADC_CS_PIN 4    // chip select  (active low)
#define ADC_DRDY_PIN -1 // DRDY not wired; time-based polling used instead
#define ADC_SPI_HZ 4000000UL

// ── PD-TIA discrete gain select (4 GPIO lines, active HIGH) ──────────────────
// Bit 0 of the gain pattern maps to PIN_0, bit 3 to PIN_3.
#define PDTIA_PIN_0 A4
#define PDTIA_PIN_1 A5
#define PDTIA_PIN_2 A6
#define PDTIA_PIN_3 A7
// Number of gain stages.  The actual 4-bit patterns live in ads_session.cpp.
#define PDTIA_NUM_STAGES 4

// ── Serial ────────────────────────────────────────────────────────────────────
#define BAUD_RATE 115200

// ── Firmware identity (*IDN?) ─────────────────────────────────────────────────
#define DEVICE_MFR "Custom Arduino Nano ESP32"
#define DEVICE_MODEL "Dual_AS5048A-ADS1220"
#define DEVICE_SERIAL "0"
#define FW_VERSION "2.1.0"

// ── Streaming defaults ────────────────────────────────────────────────────────
#define DEFAULT_STREAM_RATE_HZ 20   // 50 ms per frame
#define DEFAULT_STREAM_SOURCES 0x03 // SRC_ENC_A | SRC_ENC_B

// ── Error queue capacity ──────────────────────────────────────────────────────
#define ERR_QUEUE_SIZE 10
