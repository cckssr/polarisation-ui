#!/usr/bin/env python3
"""
AS5048A SPI Response Parser

Parses 16-bit hex words from AS5048A encoder:
  Bit 15: PAR (Parity - even parity over all 16 bits)
  Bit 14: EF (Error Flag)
  Bits 13-0: DATA (14-bit value)

Usage:
  python as5048a_parser.py 0x3D5E
  python as5048a_parser.py 0xABCD
  python as5048a_parser.py 15701  (decimal)
"""

import sys


def even_parity(value):
    """Check if value has even parity (even number of 1-bits)."""
    count = 0
    while value:
        count += value & 1
        value >>= 1
    return count % 2 == 0


def parse_as5048a_word(hex_word):
    """
    Parse a 16-bit word from AS5048A.

    Args:
        hex_word: 16-bit integer (0x0000 - 0xFFFF)

    Returns:
        dict with parsed components
    """
    # Ensure 16-bit
    hex_word = hex_word & 0xFFFF

    # Extract components
    parity_bit = (hex_word >> 15) & 1
    error_flag = (hex_word >> 14) & 1
    data_14bit = hex_word & 0x3FFF

    # Verify parity (even parity over all 16 bits)
    parity_ok = even_parity(hex_word)

    return {
        "raw_16bit": hex_word,
        "parity_bit": parity_bit,
        "error_flag": error_flag,
        "data_14bit": data_14bit,
        "parity_ok": parity_ok,
        "parity_status": "✓ OK" if parity_ok else "✗ FAIL",
    }


def data_to_degrees(data_14bit):
    """Convert 14-bit angle data to degrees."""
    return (data_14bit * 360.0) / 16384.0


def data_to_magnitude_pct(data_14bit):
    """Convert 14-bit magnitude to percentage (0-100%)."""
    return (data_14bit * 100.0) / 16384.0


def print_parsed(parsed, show_degrees=True, show_magnitude=False):
    """Pretty-print parsed AS5048A word."""
    print(f"\n{'=' * 60}")
    print(f"  Raw 16-bit value: 0x{parsed['raw_16bit']:04X} ({parsed['raw_16bit']})")
    print(f"{'=' * 60}")

    print(f"\n  Bit 15 (PAR):   {parsed['parity_bit']} (Parity bit)")
    print(f"  Bit 14 (EF):    {parsed['error_flag']} (Error Flag)")
    print(
        f"  Bits 13-0:      0x{parsed['data_14bit']:04X} ({parsed['data_14bit']}) (14-bit DATA)"
    )

    print(f"\n  Parity Check:   {parsed['parity_status']}")

    if parsed["error_flag"]:
        print(f"  ⚠️  ERROR FLAG SET - Data may be invalid!")

    if show_degrees:
        angle = data_to_degrees(parsed["data_14bit"])
        print(f"\n  As Angle:       {angle:.2f}° (0-360°)")

    if show_magnitude:
        magnitude = data_to_magnitude_pct(parsed["data_14bit"])
        print(f"  As Magnitude:   {magnitude:.1f}% (0-100%)")

    print(f"\n{'=' * 60}\n")


def main():
    """Main console interface."""
    if len(sys.argv) > 1:
        # Parse command-line argument
        hex_input = sys.argv[1]
        try:
            # Try hex format (0xABCD or ABCD)
            if hex_input.startswith("0x") or hex_input.startswith("0X"):
                value = int(hex_input, 16)
            else:
                # Try decimal first, then hex
                try:
                    value = int(hex_input, 10)
                except ValueError:
                    value = int(hex_input, 16)

            parsed = parse_as5048a_word(value)
            print_parsed(parsed, show_degrees=True, show_magnitude=False)
        except ValueError as e:
            print(f"Error: Invalid input '{hex_input}': {e}")
            sys.exit(1)
    else:
        # Interactive mode
        print("AS5048A 16-bit Word Parser")
        print("=" * 60)
        print("Enter 16-bit hex words (0xABCD or ABCD format)")
        print("Type 'exit' to quit\n")

        while True:
            try:
                user_input = input("Enter hex word (or 'exit'): ").strip()

                if user_input.lower() in ("exit", "quit", "q"):
                    print("Goodbye!")
                    break

                if not user_input:
                    continue

                # Parse input
                if user_input.startswith("0x") or user_input.startswith("0X"):
                    value = int(user_input, 16)
                else:
                    try:
                        value = int(user_input, 10)
                    except ValueError:
                        value = int(user_input, 16)

                parsed = parse_as5048a_word(value)
                print_parsed(parsed, show_degrees=True, show_magnitude=False)

            except ValueError:
                print("Invalid input. Use hex (0xABCD) or decimal format.\n")
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}\n")


if __name__ == "__main__":
    main()
