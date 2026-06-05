#pragma once

#include <Arduino.h>
#include <SPI.h>

// SPI mode 1 (CPOL=0, CPHA=1), MSB first, max ~4 MHz

static constexpr uint8_t ADS1220_CMD_RESET = 0x06;
static constexpr uint8_t ADS1220_CMD_START = 0x08;
static constexpr uint8_t ADS1220_CMD_POWERDOWN = 0x02;
static constexpr uint8_t ADS1220_CMD_RDATA = 0x10;
static constexpr uint8_t ADS1220_CMD_RREG = 0x20; // | (reg<<2) | (n-1)
static constexpr uint8_t ADS1220_CMD_WREG = 0x40; // | (reg<<2) | (n-1)

class ADS1220
{
public:
    // Config register 0, bits 7:4 — input multiplexer
    enum class Mux : uint8_t
    {
        AIN0_AIN1 = 0x00, // default
        AIN0_AIN2 = 0x10,
        AIN0_AIN3 = 0x20,
        AIN1_AIN2 = 0x30,
        AIN1_AIN3 = 0x40,
        AIN2_AIN3 = 0x50,
        AIN1_AIN0 = 0x60,
        AIN3_AIN2 = 0x70,
        AIN0_AVSS = 0x80,
        AIN1_AVSS = 0x90,
        AIN2_AVSS = 0xA0,
        AIN3_AVSS = 0xB0,
        VREF_MON = 0xC0,  // (VREFP-VREFN)/4 monitor, PGA bypassed
        AVDD_MON = 0xD0,  // (AVDD-AVSS)/4 monitor, PGA bypassed
        AVDD_HALF = 0xE0, // AINP/AINN shorted to (AVDD+AVSS)/2
    };

    // Config register 0, bits 3:1 — PGA gain
    enum class Gain : uint8_t
    {
        G1 = 0x00, // default
        G2 = 0x02,
        G4 = 0x04,
        G8 = 0x06,
        G16 = 0x08,
        G32 = 0x0A,
        G64 = 0x0C,
        G128 = 0x0E,
    };

    // Config register 1, bits 7:5 — data rate
    // Actual SPS depends on operating mode (normal/duty-cycle/turbo)
    enum class DataRate : uint8_t
    {
        DR0 = 0x00, //  20 /   5 /   40 SPS
        DR1 = 0x20, //  45 / 11.25/  90 SPS
        DR2 = 0x40, //  90 / 22.5 / 180 SPS
        DR3 = 0x60, // 175 /  44  / 350 SPS
        DR4 = 0x80, // 330 / 82.5 / 660 SPS
        DR5 = 0xA0, // 600 / 150  /1200 SPS
        DR6 = 0xC0, // 1000 / 250  /2000 SPS
    };

    // Config register 1, bits 4:3 — operating mode
    enum class OperatingMode : uint8_t
    {
        NORMAL = 0x00,     // 256-kHz modulator, default
        DUTY_CYCLE = 0x08, // 1:4 internal duty cycle
        TURBO = 0x10,      // 512-kHz modulator
    };

    // Config register 1, bit 2 — conversion mode
    enum class ConversionMode : uint8_t
    {
        SINGLE_SHOT = 0x00, // default
        CONTINUOUS = 0x04,
    };

    // Config register 2, bits 7:6 — voltage reference
    enum class VoltageRef : uint8_t
    {
        INTERNAL = 0x00,      // internal 2.048 V, default
        EXT_REFP0 = 0x40,     // external REFP0/REFN0 pins
        EXT_AIN0_AIN3 = 0x80, // external AIN0/AIN3 (REFP1/REFN1)
        AVDD_AVSS = 0xC0,     // analog supply as reference
    };

    // Config register 2, bits 5:4 — FIR filter (valid at 20 SPS normal / 5 SPS duty-cycle only)
    enum class FIRFilter : uint8_t
    {
        NONE = 0x00,    // default
        HZ50_60 = 0x10, // simultaneous 50 Hz and 60 Hz rejection
        HZ50 = 0x20,    // 50 Hz rejection only
        HZ60 = 0x30,    // 60 Hz rejection only
    };

    // Config register 2, bits 2:0 — IDAC excitation current (both IDAC1 and IDAC2)
    enum class IDACCurrent : uint8_t
    {
        OFF = 0x00, // default
        UA10 = 0x01,
        UA50 = 0x02,
        UA100 = 0x03,
        UA250 = 0x04,
        UA500 = 0x05,
        UA1000 = 0x06,
        UA1500 = 0x07,
    };

    // Config register 3, I1MUX / I2MUX bits — IDAC routing
    enum class IDACRoute : uint8_t
    {
        ROUTE_OFF = 0x00, // default (renamed: ESP32 HAL defines DISABLED as a macro)
        AIN0_REFP1 = 0x01,
        AIN1 = 0x02,
        AIN2 = 0x03,
        AIN3_REFN1 = 0x04,
        REFP0 = 0x05,
        REFN0 = 0x06,
    };

    // csPin: chip select (active low)
    // misoPin: master in slave out (input)
    // mosiPin: master out slave in (output)
    // sckPin: serial clock (output)
    // drdyPin: dedicated DRDY output (active low); pass -1 to rely on DOUT/DRDY with DRDYM=1
    ADS1220(uint8_t csPin, uint8_t misoPin, uint8_t mosiPin, uint8_t sckPin, int8_t drdyPin, SPIClass &spi = SPI);

    // Initialise pins, SPI bus, and reset the device.
    // Returns false if the initial register readback does not match expected reset values.
    bool begin(uint32_t spiFreq = 4000000UL);

    // Stand-alone command wrappers
    void reset();
    void start();
    void powerDown();

    // ---- Configuration setters (update shadow registers and write to device) ----
    void setMux(Mux mux);
    void setGain(Gain gain);
    void setPGABypass(bool bypass);

    void setDataRate(DataRate dr);
    void setOperatingMode(OperatingMode mode);
    void setConversionMode(ConversionMode mode);
    void enableTemperatureSensor(bool enable);
    void enableBurnoutCurrentSources(bool enable);

    void setVoltageReference(VoltageRef ref);
    void setFIRFilter(FIRFilter filter);
    void setLowSidePowerSwitch(bool enable);
    void setIDACCurrent(IDACCurrent current);

    void setIDAC1Route(IDACRoute route);
    void setIDAC2Route(IDACRoute route);
    // When true, DOUT/DRDY also acts as data-ready indicator (DRDYM=1)
    void setDRDYMode(bool combinedWithDOUT);

    // Write all four shadow registers to the device in one burst
    void applyConfig();

    // ---- Data ready ----
    // Returns true when DRDY (or DOUT/DRDY if drdyPin==-1) is asserted low
    bool dataReady() const;
    // Blocks until data ready or timeout (ms). Returns false on timeout.
    bool waitForDataReady(uint32_t timeoutMs = 1000);

    // ---- Reading ----
    // Read 24-bit two's complement result directly (no RDATA command).
    // Call after dataReady() returns true, or at any time in continuous mode.
    int32_t readRaw();

    // Read 24-bit result using explicit RDATA command.
    // Use when DRDY/DOUT are not monitored.
    int32_t readRawWithCommand();

    // Convert raw code to voltage. vref must match the selected reference voltage.
    float readVoltage(float vref = 2.048f);

    // Read internal temperature sensor result (must have called enableTemperatureSensor(true) first).
    // Temperature data occupies bits 23:10 of the 24-bit result (14-bit, 0.03125 °C/LSB).
    float readTemperature();

    // ---- Low-level register access ----
    void writeRegister(uint8_t reg, uint8_t value);
    uint8_t readRegister(uint8_t reg);

    // Access cached shadow register values (no SPI transaction)
    uint8_t getRegister(uint8_t reg) const { return _reg[reg & 0x03]; }

private:
    uint8_t _csPin;
    uint8_t _misoPin;
    uint8_t _mosiPin;
    uint8_t _sckPin;
    int8_t _drdyPin;
    SPIClass &_spi;
    uint32_t _spiFreq;
    uint8_t _reg[4]; // shadow copies of config registers 0–3

    void _csAssert();
    void _csRelease();
    uint8_t _transfer(uint8_t data);
    void _sendCommand(uint8_t cmd);
    uint8_t _gainValue() const;
};
