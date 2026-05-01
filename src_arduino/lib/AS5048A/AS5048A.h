#pragma once
#include <Arduino.h>
#include <SPI.h>

class AS5048A_SPI
{
public:
    struct FrameResult
    {
        uint16_t raw16;  // full 16-bit frame returned by chip (PAR|EF|DATA)
        uint16_t data14; // DATA[13:0]
        bool errorFlag;  // EF bit (bit14)
        bool parityOk;   // even parity check on raw16
    };

    // Diagnostics register (0x3FFD) interpretation
    struct Diagnostics
    {
        bool compHigh; // weak field
        bool compLow;  // strong field
        bool cof;      // CORDIC overflow
        bool ocf;      // offset compensation finished
        uint8_t agc;   // automatic gain control value
        uint16_t raw14;
    };

    // ---- Ctor ----
    explicit AS5048A_SPI(uint8_t csPin, SPIClass &spi = SPI);

    // ---- Init ----
    // spiHz: safe default 1MHz. Datasheet allows much higher (TCLK min 100ns => 10MHz),
    // but keep it conservative unless wiring is perfect.
    void begin(uint32_t spiHz = 1000000);

    // ---- Low-level register access ----
    FrameResult readRegister(uint16_t addr14);
    FrameResult writeRegister(uint16_t addr14, uint16_t data14);

    // Convenience: get 14-bit data without extra struct
    uint16_t read14(uint16_t addr14);
    uint16_t write14(uint16_t addr14, uint16_t data14);

    // ---- Common readouts ----
    uint16_t readAngleRaw(); // 0..16383, already includes chip zero-position correction
    float readAngleDeg();    // 0..360
    uint16_t readMagnitudeRaw();
    Diagnostics readDiagnostics();

    // ---- Common readouts with diagnostics ----
    // Returns FrameResult with parity check and error flag
    FrameResult readAngleRawWithDiagnostics();
    FrameResult readMagnitudeRawWithDiagnostics();

    // ---- Error handling ----
    // Clear Error Flag is implemented as READ from address 0x0001.
    // Returns error register content in DATA[13:0] (see datasheet), and clears EF for subsequent reads.
    FrameResult clearErrorFlag();

    // Optionally read NOP response (should return 0x0000 as per datasheet)
    FrameResult nop();

    // ---- Zero handling ----
    // A) "Software zero" (no chip writes): just stores current angle as offset in this object.
    void setSoftwareZero();
    void clearSoftwareZero();
    uint16_t getSoftwareZeroOffset() const;
    float readAngleDegSoftwareZeroed(); // uses stored SW offset

    // B) Set chip zero position registers (volatile, not OTP-burned):
    // Datasheet programming sequence: write 0 to ZPOS regs, read ANGLE, write ANGLE to ZPOS regs.
    // This sets the internal zero position so that ANGLE becomes ~0 at this mechanical position.
    bool setZeroPositionVolatile();

    // C) Permanently burn current ZPOS into OTP and verify (ONE-TIME).
    // Sequence (datasheet): enable prog, burn, read angle (0), verify, read angle (0).
    // WARNING: irreversible.
    bool burnZeroPositionToOTP();

    // Read current zero position registers (as stored in ZPOS shadow/OTP regs)
    uint16_t readZeroPosition();

    // Apply the stored software-zero offset to an already-read raw14 value and
    // convert to degrees.  Use in streaming paths where readAngleDeg() cannot
    // be called again (it would issue a second SPI transaction).
    float applyZero(uint16_t raw14) const;

private:
    // ---- Registers (14-bit addresses) ----
    static constexpr uint16_t REG_NOP = 0x0000;
    static constexpr uint16_t REG_CLR_ERR = 0x0001;
    static constexpr uint16_t REG_PROG_CTRL = 0x0003;
    static constexpr uint16_t REG_ZPOS_HI = 0x0016;
    static constexpr uint16_t REG_ZPOS_LO = 0x0017;
    static constexpr uint16_t REG_DIAG_AGC = 0x3FFD;
    static constexpr uint16_t REG_MAG = 0x3FFE;
    static constexpr uint16_t REG_ANGLE = 0x3FFF;

    // Programming Control bits (REG_PROG_CTRL)
    // From register map: bit0=Programming Enable, bit3=Burn, bit6=Verify.  [oai_citation:1‡AS5048_DS000298_4_00.pdf](sediment://file_0000000026cc71f49cd598e988add4a7)
    static constexpr uint16_t PROG_EN = (1u << 0);
    static constexpr uint16_t PROG_BURN = (1u << 3);
    static constexpr uint16_t PROG_VRFY = (1u << 6);

    uint8_t _cs;
    SPIClass *_spi;
    SPISettings _settings;

    // software-zero offset (raw 14-bit angle)
    bool _swZeroEnabled = false;
    uint16_t _swZeroOffset = 0;

    // ---- SPI helpers ----
    uint16_t buildCommandFrame(bool read, uint16_t addr14) const;
    uint16_t buildDataFrame(uint16_t data14) const;

    FrameResult transfer16(uint16_t tx);
    FrameResult doReadPipelined(uint16_t addr14);
    FrameResult doWriteTwoFrame(uint16_t addr14, uint16_t data14);

    static bool evenParity16(uint16_t word);
    static uint16_t mask14(uint16_t x) { return x & 0x3FFF; }

    // respects minimum CS high time etc.; keep simple + robust
    void csLow();
    void csHigh();
};