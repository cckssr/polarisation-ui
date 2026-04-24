#include "AS5048A.h"

AS5048A_SPI::AS5048A_SPI(uint8_t csPin, SPIClass &spi)
    : _cs(csPin), _spi(&spi), _settings(1000000, MSBFIRST, SPI_MODE1) {}

void AS5048A_SPI::begin(uint32_t spiHz)
{
    pinMode(_cs, OUTPUT);
    digitalWrite(_cs, HIGH);

    _settings = SPISettings(spiHz, MSBFIRST, SPI_MODE1);
    _spi->begin();
}

void AS5048A_SPI::csLow() { digitalWrite(_cs, LOW); }
void AS5048A_SPI::csHigh() { digitalWrite(_cs, HIGH); }

bool AS5048A_SPI::evenParity16(uint16_t word)
{
    // true if total number of 1-bits in 'word' is even
#if defined(__GNUC__)
    return (__builtin_popcount((unsigned)word) % 2) == 0;
#else
    uint16_t x = word;
    x ^= x >> 8;
    x ^= x >> 4;
    x ^= x >> 2;
    x ^= x >> 1;
    return (x & 1u) == 0;
#endif
}

uint16_t AS5048A_SPI::buildCommandFrame(bool read, uint16_t addr14) const
{
    // Command frame format: [15]=PAR (even), [14]=RWn (1=read), [13:0]=ADDR
    uint16_t frame = (read ? 0x4000 : 0x0000) | (addr14 & 0x3FFF);

    // parity bit makes total 16-bit word even parity
    // Set bit15 such that evenParity16(frame_with_parity) == true.
    // Start with parity bit cleared:
    frame &= 0x7FFF;
    if (!evenParity16(frame))
        frame |= 0x8000;
    return frame;
}

uint16_t AS5048A_SPI::buildDataFrame(uint16_t data14) const
{
    // Data frame format: [15]=PAR (even), [14]=R (must be 0), [13:0]=DATA
    uint16_t frame = (data14 & 0x3FFF); // bit14 stays 0
    frame &= 0x7FFF;
    if (!evenParity16(frame))
        frame |= 0x8000;
    return frame;
}

AS5048A_SPI::FrameResult AS5048A_SPI::transfer16(uint16_t tx)
{
    _spi->beginTransaction(_settings);
    csLow();
    uint16_t rx = _spi->transfer16(tx);
    csHigh();
    _spi->endTransaction();

    // Small inter-frame gap; datasheet requires CSn high time >= 350ns and timing margins.
    // 1us is conservative and avoids edge cases on slow GPIO.
    delayMicroseconds(1);

    FrameResult r;
    r.raw16 = rx;
    r.errorFlag = (rx & 0x4000) != 0; // bit14 = EF
    r.data14 = (rx & 0x3FFF);
    r.parityOk = evenParity16(rx); // total even parity expected
    return r;
}

AS5048A_SPI::FrameResult AS5048A_SPI::doReadPipelined(uint16_t addr14)
{
    // Datasheet: response to command N appears in transmission N+1 (pipeline).  [oai_citation:3‡AS5048_DS000298_4_00.pdf](sediment://file_0000000026cc71f49cd598e988add4a7)
    const uint16_t cmd = buildCommandFrame(true, addr14);

    // Transmission N: send READ command (response is previous command's data, ignore)
    (void)transfer16(cmd);

    // Transmission N+1: send NOP (or next command), read desired register response now
    return transfer16(buildCommandFrame(true, REG_NOP)); // using READ NOP is fine; NOP also defined.
}

AS5048A_SPI::FrameResult AS5048A_SPI::doWriteTwoFrame(uint16_t addr14, uint16_t data14)
{
    // WRITE takes two transmissions: first the write command (RWn=0 + addr),
    // then the data frame. The response to the write command is old register content.  [oai_citation:4‡AS5048_DS000298_4_00.pdf](sediment://file_0000000026cc71f49cd598e988add4a7)
    const uint16_t cmd = buildCommandFrame(false, addr14);
    const uint16_t data = buildDataFrame(data14);

    (void)transfer16(cmd);            // Transmission N: issue WRITE command
    FrameResult r = transfer16(data); // Transmission N+1: send data, receive old content
    return r;
}

AS5048A_SPI::FrameResult AS5048A_SPI::readRegister(uint16_t addr14)
{
    return doReadPipelined(addr14 & 0x3FFF);
}

AS5048A_SPI::FrameResult AS5048A_SPI::writeRegister(uint16_t addr14, uint16_t data14)
{
    return doWriteTwoFrame(addr14 & 0x3FFF, data14 & 0x3FFF);
}

uint16_t AS5048A_SPI::read14(uint16_t addr14)
{
    return readRegister(addr14).data14;
}

uint16_t AS5048A_SPI::write14(uint16_t addr14, uint16_t data14)
{
    return writeRegister(addr14, data14).data14; // returns old content (per datasheet)
}

AS5048A_SPI::FrameResult AS5048A_SPI::nop()
{
    // NOP command is address 0x0000; chip's response is 0x0000 per datasheet.  [oai_citation:5‡AS5048_DS000298_4_00.pdf](sediment://file_0000000026cc71f49cd598e988add4a7)
    (void)transfer16(buildCommandFrame(true, REG_NOP));
    return transfer16(buildCommandFrame(true, REG_NOP));
}

uint16_t AS5048A_SPI::readAngleRaw()
{
    return read14(REG_ANGLE);
}

float AS5048A_SPI::readAngleDeg()
{
    const uint16_t raw = readAngleRaw();
    uint16_t corrected = raw;
    if (_swZeroEnabled)
    {
        corrected = (uint16_t)((raw + 16384u - _swZeroOffset) & 0x3FFF);
    }
    return (corrected * 360.0f) / 16384.0f;
}

uint16_t AS5048A_SPI::readMagnitudeRaw()
{
    return read14(REG_MAG);
}

AS5048A_SPI::FrameResult AS5048A_SPI::readAngleRawWithDiagnostics()
{
    return readRegister(REG_ANGLE);
}

AS5048A_SPI::FrameResult AS5048A_SPI::readMagnitudeRawWithDiagnostics()
{
    return readRegister(REG_MAG);
}

AS5048A_SPI::Diagnostics AS5048A_SPI::readDiagnostics()
{
    const uint16_t v = read14(REG_DIAG_AGC);

    Diagnostics d;
    d.raw14 = v;
    d.compHigh = (v & (1u << 11)) != 0;
    d.compLow = (v & (1u << 10)) != 0;
    d.cof = (v & (1u << 9)) != 0;
    d.ocf = (v & (1u << 8)) != 0;
    d.agc = (uint8_t)(v & 0x00FF);
    return d;
}

AS5048A_SPI::FrameResult AS5048A_SPI::clearErrorFlag()
{
    // Clear Error Flag is implemented as READ to address 0x0001.  [oai_citation:6‡AS5048_DS000298_4_00.pdf](sediment://file_0000000026cc71f49cd598e988add4a7)
    return readRegister(REG_CLR_ERR);
}

// -------------------- Software-zero --------------------

void AS5048A_SPI::setSoftwareZero()
{
    _swZeroOffset = readAngleRaw();
    _swZeroEnabled = true;
}

void AS5048A_SPI::clearSoftwareZero()
{
    _swZeroEnabled = false;
    _swZeroOffset = 0;
}

uint16_t AS5048A_SPI::getSoftwareZeroOffset() const
{
    return _swZeroOffset;
}

float AS5048A_SPI::readAngleDegSoftwareZeroed()
{
    const uint16_t raw = readAngleRaw();
    uint16_t corrected = raw;
    if (_swZeroEnabled)
    {
        corrected = (uint16_t)((raw + 16384u - _swZeroOffset) & 0x3FFF);
    }
    return (corrected * 360.0f) / 16384.0f;
}

// -------------------- Chip zero-position registers --------------------

uint16_t AS5048A_SPI::readZeroPosition()
{
    // ZPOS is split:
    // ZPOS_HI holds bits [13:6] in its low bits (datasheet calls it "high byte"),
    // ZPOS_LO holds bits [5:0] in its low bits.  [oai_citation:7‡AS5048_DS000298_4_00.pdf](sediment://file_0000000026cc71f49cd598e988add4a7)
    const uint16_t hi = read14(REG_ZPOS_HI) & 0x00FF; // bits [7:0] map to ZPOS[13:6]
    const uint16_t lo = read14(REG_ZPOS_LO) & 0x003F; // bits [5:0] map to ZPOS[5:0]
    return (uint16_t)((hi << 6) | lo);
}

bool AS5048A_SPI::setZeroPositionVolatile()
{
    // Datasheet programming sequence (without OTP burn):
    // 1) write 0 to ZPOS regs
    // 2) read ANGLE
    // 3) write that ANGLE into ZPOS regs
    // This sets zero such that ANGLE becomes ~0 at this mechanical position.  [oai_citation:8‡AS5048_DS000298_4_00.pdf](sediment://file_0000000026cc71f49cd598e988add4a7)

    // 1) clear
    (void)writeRegister(REG_ZPOS_HI, 0);
    (void)writeRegister(REG_ZPOS_LO, 0);

    // 2) read current angle (chip-corrected angle)
    const uint16_t a = readAngleRaw();

    // 3) write back as new ZPOS
    const uint16_t hi = (a >> 6) & 0x00FF; // ZPOS[13:6]
    const uint16_t lo = (a >> 0) & 0x003F; // ZPOS[5:0]

    (void)writeRegister(REG_ZPOS_HI, hi);
    (void)writeRegister(REG_ZPOS_LO, lo);

    // Optional sanity check: angle should now read near 0
    const uint16_t a2 = readAngleRaw();
    return (a2 <= 5u) || (a2 >= (16384u - 5u));
}

bool AS5048A_SPI::burnZeroPositionToOTP()
{
    // WARNING: one-time, irreversible (OTP).
    // Datasheet sequence:
    // 4) set PROG_EN
    // 5) set BURN (starts automatic programming)
    // 6) read angle (equals 0)
    // 7) set VERIFY (reload OTP into internal regs)
    // 8) read angle (equals 0)  [oai_citation:9‡AS5048_DS000298_4_00.pdf](sediment://file_0000000026cc71f49cd598e988add4a7)

    // Enable programming
    (void)writeRegister(REG_PROG_CTRL, PROG_EN);

    // Start burn
    (void)writeRegister(REG_PROG_CTRL, (uint16_t)(PROG_EN | PROG_BURN));

    // Give the chip a moment; datasheet doesn’t give a concrete burn time here.
    // Keep it conservative.
    delay(20);

    // Read angle; should be 0 if the current mechanical position equals newly set ZPOS.
    const uint16_t a1 = readAngleRaw();

    // Verify
    (void)writeRegister(REG_PROG_CTRL, (uint16_t)(PROG_EN | PROG_VRFY));
    delay(5);

    const uint16_t a2 = readAngleRaw();

    // Disable programming (good practice)
    (void)writeRegister(REG_PROG_CTRL, 0);

    // Expect ~0
    const bool ok1 = (a1 <= 5u) || (a1 >= (16384u - 5u));
    const bool ok2 = (a2 <= 5u) || (a2 >= (16384u - 5u));
    return ok1 && ok2;
}