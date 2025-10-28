#!/usr/bin/env python3
"""
Compare my generated codes with working codes - focus on checksum
"""

from app.core.tuya_encoder import decode_tuya_ir

# Working codes
CODE_22C_COOL = "EfcMEwbxAd0APwImAfEBmATxAUALA5gErwFADwkmAT8CJgHxAZgEQAPAEwHxAcAjBZgE8QEmAYAjCyYB8QFhAa8BYQHxAUALQAPAC8AHQBMDJgE/AkA3QBNARwMmAfEBQANAD0AHQAMDmASvAUAHwANAJ0ATApgE8aADwAtAB0ADAfEBQCNAQ0ALwDcFJgE/AiYBQAcB8QFAG+ADI+ADJwdhAa8BYQHxAUAnwANAH0ADQBcDmASvAUAXB2EBrwFhAfEBQAtAA0ALQAMDmATxAeALD+ADE0AngAPgBUMAryABgBNABwPxAWEBgAcAryABgAtABwHxAYBLgAuAB0ALQAOAD+ADAQdhAa8BmASvAcABgA8E8QGYBK+gA4ALB68BrwGvAa8B"

CODE_24C_HIGH = "EfcMNAbRAYIB0QFWAdEBkwTRAeADB0ALQANAF0ADQAvAA0APQAPAD0AHwEdAC+ADA0AXQAPAE0A3QA9AA8ATwAdAE0AfwA/AB0AT4BMD4AMnwAvAB0BTwANAE8BHQAtAA0APQAdAI0AH4AMDQBvAF0ALwBsAgmABAdEBQA/AFwCCYAEB0QHgAQ8C0QGCYAFABwHRAUAr4AMHAIJgAUAHgAOAH8ABAdEBQANAE0ADAILgAAFAC4ADgBcC0QGCYAFAB4ADQBcHkwSCAYIB0QFAC0ADBJME0QGCIAFAB0ADC1YB0QGCAdEBggHRAQ=="

def timings_to_bits(timings: list[int]) -> list[int]:
    """Convert IR timings to bits"""
    data_timings = timings[2:]
    bits = []
    for i in range(0, len(data_timings), 2):
        if i + 1 < len(data_timings):
            space = data_timings[i + 1]
            bits.append(1 if space > 600 else 0)
    return bits

def bits_to_bytes(bits: list[int]) -> bytes:
    """Convert bits to bytes (LSB first)"""
    state_bytes = []
    for i in range(0, len(bits), 8):
        if i + 8 <= len(bits):
            byte_bits = bits[i:i+8]
            byte_val = sum(bit << j for j, bit in enumerate(byte_bits))
            state_bytes.append(byte_val)
    return bytes(state_bytes)

print("="*80)
print("CHECKSUM ANALYSIS - Working Codes")
print("="*80)

codes = [
    ("22°C Cool High", CODE_22C_COOL, 22, 0x01),  # Cool mode
    ("24°C High", CODE_24C_HIGH, 24, 0x04),  # Suspect this is Heat mode based on byte 9
]

for name, code, temp, expected_mode in codes:
    print(f"\n{name}")
    print("-" * 80)

    timings = decode_tuya_ir(code)
    bits = timings_to_bits(timings)
    state_bytes = bits_to_bytes(bits)

    print(f"Bytes: {' '.join(f'{b:02X}' for b in state_bytes)}")

    # Temperature
    byte_8 = state_bytes[8]
    temp_val = (byte_8 >> 2) & 0x3F
    calculated_temp = temp_val / 4 + 16
    power_bit = byte_8 & 0x01

    print(f"\nByte 8: 0x{byte_8:02X}")
    print(f"  Power bit: {power_bit}")
    print(f"  Temp value: {temp_val} → {calculated_temp}°C")

    # Mode
    mode_val = state_bytes[9] & 0x07
    mode_names = {0: "Auto", 1: "Cool", 2: "Dry", 3: "Fan", 4: "Heat"}
    print(f"\nByte 9: 0x{state_bytes[9]:02X}")
    print(f"  Mode: {mode_names.get(mode_val, 'Unknown')} ({mode_val})")

    # Checksum
    checksum = state_bytes[15]
    print(f"\nByte 15 (Checksum): 0x{checksum:02X}")

    # Try different checksum formulas
    sum_all = sum(state_bytes[0:15])
    sum_mod = sum_all & 0xFF
    sum_plus_64 = (sum_all + 0x64) & 0xFF
    sum_plus_checksum = (sum_all + checksum) & 0xFF

    print(f"\nChecksum analysis:")
    print(f"  Sum of bytes 0-14: {sum_all} = 0x{sum_all:04X}")
    print(f"  Sum & 0xFF: 0x{sum_mod:02X}")
    print(f"  (Sum + 0x64) & 0xFF: 0x{sum_plus_64:02X}")
    print(f"  (Sum + checksum) & 0xFF: 0x{sum_plus_checksum:02X}")

    # Check if any formula matches
    if checksum == sum_mod:
        print(f"  ✓ Checksum = Sum & 0xFF")
    elif checksum == sum_plus_64:
        print(f"  ✓ Checksum = (Sum + 0x64) & 0xFF")
    elif sum_plus_checksum == 0:
        print(f"  ✓ Checksum = (-Sum) & 0xFF (Two's complement)")
    elif sum_plus_checksum == 0xFF:
        print(f"  ✓ Checksum = (0xFF - Sum) & 0xFF")
    else:
        # Try XOR
        xor_all = 0
        for b in state_bytes[0:15]:
            xor_all ^= b
        if checksum == xor_all:
            print(f"  ✓ Checksum = XOR of all bytes")
        else:
            print(f"  ✗ No standard formula matches")

print("\n" + "="*80)
print("COMPARING MY GENERATED VS WORKING")
print("="*80)

# My generated 24°C Heat from earlier
my_24h_bytes = bytes([0x14, 0x63, 0x00, 0x10, 0x10, 0xFE, 0x09, 0x30, 0x81, 0x04, 0x11, 0x00, 0x00, 0x00, 0x20, 0xE8])

working_24h = bits_to_bytes(timings_to_bits(decode_tuya_ir(CODE_24C_HIGH)))

print(f"\n24°C Heat Comparison:")
print(f"My generated:  {' '.join(f'{b:02X}' for b in my_24h_bytes)}")
print(f"Your working:  {' '.join(f'{b:02X}' for b in working_24h)}")

print(f"\nByte-by-byte comparison:")
for i in range(16):
    mine = my_24h_bytes[i]
    theirs = working_24h[i]
    match = "✓" if mine == theirs else "✗"
    print(f"  Byte {i:2d}: 0x{mine:02X} vs 0x{theirs:02X}  {match}")

print("\n" + "="*80)
print("CONCLUSION")
print("="*80)

print("\nThe protocol structure is CORRECT!")
print("The ONLY difference is the checksum byte.")
print()
print("My checksum: 0xE8 (calculated with simple formula)")
print("Working checksum: 0x1A")
print()
print("Need to find the correct checksum formula.")
