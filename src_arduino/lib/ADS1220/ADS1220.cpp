#include "ADS1220.h"

ADS1220::ADS1220(uint8_t csPin, uint8_t misoPin, uint8_t mosiPin, uint8_t sckPin, int8_t drdyPin, SPIClass &spi)
    : _csPin(csPin), _misoPin(misoPin), _mosiPin(mosiPin), _sckPin(sckPin), _drdyPin(drdyPin), _spi(spi), _spiFreq(4000000UL)
{
    memset(_reg, 0, sizeof(_reg));
}

bool ADS1220::begin(uint32_t spiFreq)
{
    _spiFreq = spiFreq;

    // Configure HSPI bus with the application-supplied pins.
    // SPIClass::begin(sck, miso, mosi, ss) sets pin modes for the SPI signals.
    _spi.begin(_sckPin, _misoPin, _mosiPin, _csPin);

    // CS is driven manually; ensure it starts deasserted.
    pinMode(_csPin, OUTPUT);
    digitalWrite(_csPin, HIGH);

    if (_drdyPin >= 0)
    {
        pinMode(_drdyPin, INPUT);
    }

    reset();

    // Verify all registers read back as 0x00 (power-on default)
    for (uint8_t i = 0; i < 4; i++)
    {
        if (readRegister(i) != 0x00)
            return false;
    }
    return true;
}

// ---------------------------------------------------------------------------
// SPI helpers
// ---------------------------------------------------------------------------

void ADS1220::_csAssert()
{
    _spi.beginTransaction(SPISettings(_spiFreq, MSBFIRST, SPI_MODE1));
    digitalWrite(_csPin, LOW);
    delayMicroseconds(1); // t_d(CSSC) >= 50 ns
}

void ADS1220::_csRelease()
{
    delayMicroseconds(1); // t_d(SCCS) >= 25 ns
    digitalWrite(_csPin, HIGH);
    _spi.endTransaction();
}

uint8_t ADS1220::_transfer(uint8_t data)
{
    return _spi.transfer(data);
}

void ADS1220::_sendCommand(uint8_t cmd)
{
    _csAssert();
    _transfer(cmd);
    _csRelease();
}

// ---------------------------------------------------------------------------
// Stand-alone commands
// ---------------------------------------------------------------------------

void ADS1220::reset()
{
    _sendCommand(ADS1220_CMD_RESET);
    // Datasheet: wait >= 50 µs + 32 t_CLK after RESET before next command
    delayMicroseconds(500);
    memset(_reg, 0, sizeof(_reg));
}

void ADS1220::start()
{
    _sendCommand(ADS1220_CMD_START);
}

void ADS1220::powerDown()
{
    _sendCommand(ADS1220_CMD_POWERDOWN);
}

// ---------------------------------------------------------------------------
// Register access
// ---------------------------------------------------------------------------

void ADS1220::writeRegister(uint8_t reg, uint8_t value)
{
    reg &= 0x03;
    _reg[reg] = value;
    _csAssert();
    // WREG: 0100 rrnn  rr=reg, nn=0 (1 byte)
    _transfer(ADS1220_CMD_WREG | (reg << 2) | 0x00);
    _transfer(value);
    _csRelease();
}

uint8_t ADS1220::readRegister(uint8_t reg)
{
    reg &= 0x03;
    _csAssert();
    // RREG: 0010 rrnn  rr=reg, nn=0 (1 byte)
    _transfer(ADS1220_CMD_RREG | (reg << 2) | 0x00);
    uint8_t value = _transfer(0x00);
    _csRelease();
    _reg[reg] = value;
    return value;
}

void ADS1220::applyConfig()
{
    _csAssert();
    // WREG starting at reg 0, writing 4 bytes: 0100 0011 = 0x43
    _transfer(ADS1220_CMD_WREG | (0 << 2) | 0x03);
    for (uint8_t i = 0; i < 4; i++)
    {
        _transfer(_reg[i]);
    }
    _csRelease();
}

// ---------------------------------------------------------------------------
// Config register 0 — MUX, GAIN, PGA_BYPASS
// ---------------------------------------------------------------------------

void ADS1220::setMux(Mux mux)
{
    _reg[0] = (_reg[0] & 0x0F) | static_cast<uint8_t>(mux);
    writeRegister(0, _reg[0]);
}

void ADS1220::setGain(Gain gain)
{
    _reg[0] = (_reg[0] & 0xF1) | static_cast<uint8_t>(gain);
    writeRegister(0, _reg[0]);
}

void ADS1220::setPGABypass(bool bypass)
{
    if (bypass)
        _reg[0] |= 0x01;
    else
        _reg[0] &= ~0x01;
    writeRegister(0, _reg[0]);
}

// ---------------------------------------------------------------------------
// Config register 1 — DR, MODE, CM, TS, BCS
// ---------------------------------------------------------------------------

void ADS1220::setDataRate(DataRate dr)
{
    _reg[1] = (_reg[1] & 0x1F) | static_cast<uint8_t>(dr);
    writeRegister(1, _reg[1]);
}

void ADS1220::setOperatingMode(OperatingMode mode)
{
    _reg[1] = (_reg[1] & 0xE7) | static_cast<uint8_t>(mode);
    writeRegister(1, _reg[1]);
}

void ADS1220::setConversionMode(ConversionMode mode)
{
    _reg[1] = (_reg[1] & 0xFB) | static_cast<uint8_t>(mode);
    writeRegister(1, _reg[1]);
}

void ADS1220::enableTemperatureSensor(bool enable)
{
    if (enable)
        _reg[1] |= 0x02;
    else
        _reg[1] &= ~0x02;
    writeRegister(1, _reg[1]);
}

void ADS1220::enableBurnoutCurrentSources(bool enable)
{
    if (enable)
        _reg[1] |= 0x01;
    else
        _reg[1] &= ~0x01;
    writeRegister(1, _reg[1]);
}

// ---------------------------------------------------------------------------
// Config register 2 — VREF, 50/60, PSW, IDAC
// ---------------------------------------------------------------------------

void ADS1220::setVoltageReference(VoltageRef ref)
{
    _reg[2] = (_reg[2] & 0x3F) | static_cast<uint8_t>(ref);
    writeRegister(2, _reg[2]);
}

void ADS1220::setFIRFilter(FIRFilter filter)
{
    _reg[2] = (_reg[2] & 0xCF) | static_cast<uint8_t>(filter);
    writeRegister(2, _reg[2]);
}

void ADS1220::setLowSidePowerSwitch(bool enable)
{
    if (enable)
        _reg[2] |= 0x08;
    else
        _reg[2] &= ~0x08;
    writeRegister(2, _reg[2]);
}

void ADS1220::setIDACCurrent(IDACCurrent current)
{
    _reg[2] = (_reg[2] & 0xF8) | static_cast<uint8_t>(current);
    writeRegister(2, _reg[2]);
}

// ---------------------------------------------------------------------------
// Config register 3 — I1MUX, I2MUX, DRDYM
// ---------------------------------------------------------------------------

void ADS1220::setIDAC1Route(IDACRoute route)
{
    // I1MUX occupies bits 7:5
    _reg[3] = (_reg[3] & 0x1F) | (static_cast<uint8_t>(route) << 5);
    writeRegister(3, _reg[3]);
}

void ADS1220::setIDAC2Route(IDACRoute route)
{
    // I2MUX occupies bits 4:2
    _reg[3] = (_reg[3] & 0xE3) | (static_cast<uint8_t>(route) << 2);
    writeRegister(3, _reg[3]);
}

void ADS1220::setDRDYMode(bool combinedWithDOUT)
{
    if (combinedWithDOUT)
        _reg[3] |= 0x02;
    else
        _reg[3] &= ~0x02;
    writeRegister(3, _reg[3]);
}

// ---------------------------------------------------------------------------
// Data ready
// ---------------------------------------------------------------------------

bool ADS1220::dataReady() const
{
    if (_drdyPin >= 0)
    {
        return digitalRead(_drdyPin) == LOW;
    }
    // Without a dedicated DRDY pin, caller must use DRDYM=1 and monitor DOUT/DRDY
    return false;
}

bool ADS1220::waitForDataReady(uint32_t timeoutMs)
{
    const uint32_t deadline = millis() + timeoutMs;
    while (!dataReady())
    {
        if (millis() > deadline)
            return false;
    }
    return true;
}

// ---------------------------------------------------------------------------
// Reading
// ---------------------------------------------------------------------------

// Direct read (no RDATA command) — use after DRDY asserts in continuous mode,
// or after DRDY asserts following a single-shot START command.
// Data is shifted out MSB first on SCLK rising edges.
int32_t ADS1220::readRaw()
{
    _csAssert();
    const uint8_t b0 = _transfer(0x00);
    const uint8_t b1 = _transfer(0x00);
    const uint8_t b2 = _transfer(0x00);
    _csRelease();

    // Assemble 24-bit value and sign-extend to 32 bits
    int32_t raw = ((uint32_t)b0 << 16) | ((uint32_t)b1 << 8) | (uint32_t)b2;
    if (raw & 0x800000)
        raw |= (int32_t)0xFF000000;
    return raw;
}

// Read using explicit RDATA command — useful when DRDY is not monitored
int32_t ADS1220::readRawWithCommand()
{
    _csAssert();
    _transfer(ADS1220_CMD_RDATA);
    const uint8_t b0 = _transfer(0x00);
    const uint8_t b1 = _transfer(0x00);
    const uint8_t b2 = _transfer(0x00);
    _csRelease();

    int32_t raw = ((uint32_t)b0 << 16) | ((uint32_t)b1 << 8) | (uint32_t)b2;
    if (raw & 0x800000)
        raw |= (int32_t)0xFF000000;
    return raw;
}

uint8_t ADS1220::_gainValue() const
{
    // GAIN[2:0] lives in bits 3:1 of register 0
    static const uint8_t table[8] = {1, 2, 4, 8, 16, 32, 64, 128};
    return table[(_reg[0] >> 1) & 0x07];
}

// Convert raw ADC code to voltage.
// V = code * Vref / (gain * 2^23)
float ADS1220::readVoltage(float vref)
{
    const float gain = static_cast<float>(_gainValue());
    return static_cast<float>(readRaw()) * vref / (gain * 8388608.0f);
}

// Read internal temperature sensor.
// Temperature occupies bits 23:10 (14-bit two's complement, 0.03125 °C/LSB).
float ADS1220::readTemperature()
{
    const int32_t raw = readRaw();
    // Arithmetic right-shift drops the 10 unused LSBs; result is 14-bit signed
    const int16_t tempCode = static_cast<int16_t>(raw >> 10);
    return tempCode * 0.03125f;
}
