#!/usr/bin/env python3
"""
Analyze the working 24°C High code to find the real protocol structure
"""

from app.core.tuya_encoder import decode_tuya_ir

# Remove spaces from user's input
CODE_24C_HIGH = "EfcMNAbRAYIB0QFWAdEBkwTRAeADB0ALQANAF0ADQAvAA0APQAPAD0AHwEdAC+ADA0AXQAPAE0A3QA9AA8ATwAdAE0AfwA/AB0AT4BMD4AMnwAvAB0BTwANAE8BHQAtAA0APQAdAI0AH4AMDQBvAF0ALwBsAgmABAdEBQA/AFwCCYAEB0QHgAQ8C0QGCYAFABwHRAUAr4AMHAIJgAUAHgAOAH8ABAdEBQANAE0ADAILgAAFAC4ADgBcC0QGCYAFAB4ADQBcHkwSCAYIB0QFAC0ADBJME0QGCIAFAB0ADC1YB0QGCAdEBggHRAQ=="

CODE_22C_COOL_HIGH = "EfcMEwbxAd0APwImAfEBmATxAUALA5gErwFADwkmAT8CJgHxAZgEQAPAEwHxAcAjBZgE8QEmAYAjCyYB8QFhAa8BYQHxAUALQAPAC8AHQBMDJgE/AkA3QBNARwMmAfEBQANAD0AHQAMDmASvAUAHwANAJ0ATApgE8aADwAtAB0ADAfEBQCNAQ0ALwDcFJgE/AiYBQAcB8QFAG+ADI+ADJwdhAa8BYQHxAUAnwANAH0ADQBcDmASvAUAXB2EBrwFhAfEBQAtAA0ALQAMDmATxAeALD+ADE0AngAPgBUMAryABgBNABwPxAWEBgAcAryABgAtABwHxAYBLgAuAB0ALQAOAD+ADAQdhAa8BmASvAcABgA8E8QGYBK+gA4ALB68BrwGvAa8B"

OFF_CODE = "BvQMFwbeAb4gARFdAb4BlQTeAV0B3gGVBL4BXQFAAwHeAUADAZUEQANAD0ADAd4BQAMBlQRAA+ABD0ATAV0BQA/AA0APwAPAE0AHBd4BlQTeAUAHAL4gAQFdAUADAd4B4AMDAZUEQBNAAwHeAYADAb4B4AkTQBsBvgFAAwGVBEALAd4BQAcBlQSADwuVBN4BlQS+AZUE3gE="

def timings_to_bits(timings: list[int]) -> list[int]:
    """Convert IR timings to bits"""
    data_timings = timings[2:]  # Skip header
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
print("ANALYZING 24°C HIGH CODE (WORKING)")
print("="*80)

codes = [
    ("OFF (7 bytes)", OFF_CODE),
    ("22°C Cool High (earlier)", CODE_22C_COOL_HIGH),
    ("24°C High (NEW)", CODE_24C_HIGH),
]

results = []

for name, code in codes:
    print(f"\n{name}")
    print("-" * 80)

    timings = decode_tuya_ir(code)
    bits = timings_to_bits(timings)
    state_bytes = bits_to_bytes(bits)

    print(f"Base64 length: {len(code)} characters")
    print(f"Timings: {len(timings)} values")
    print(f"Bits: {len(bits)} bits")
    print(f"Bytes: {len(state_bytes)} bytes")
    print(f"First 20 bytes: {' '.join(f'{b:02X}' for b in state_bytes[:20])}")

    if len(state_bytes) > 20:
        print(f"... (showing first 20 of {len(state_bytes)} total)")
        print(f"Last 10 bytes: {' '.join(f'{b:02X}' for b in state_bytes[-10:])}")

    results.append((name, state_bytes, len(code)))

print("\n" + "="*80)
print("LENGTH COMPARISON")
print("="*80)

for name, bytes_val, base64_len in results:
    print(f"{name}:")
    print(f"  Base64: {base64_len} chars")
    print(f"  Bytes: {len(bytes_val)} bytes")
    print(f"  Bits: {len(bytes_val) * 8} bits")

print("\n" + "="*80)
print("CRITICAL FINDING")
print("="*80)

off_bytes = results[0][1]
code_24c_bytes = results[2][1]

print(f"\nOFF command: {len(off_bytes)} bytes")
print(f"24°C High command: {len(code_24c_bytes)} bytes")
print(f"\nRatio: {len(code_24c_bytes) / len(off_bytes):.1f}x longer!")

print("\n" + "="*80)
print("TEMPERATURE ANALYSIS")
print("="*80)

# Look for temperature encoding in various byte positions
print(f"\n24°C High command - searching for temperature encoding:")
print(f"Looking for value 32 (which would give (32/4)+16 = 24°C)")
print()

for i in range(min(50, len(code_24c_bytes))):
    byte_val = code_24c_bytes[i]

    # Check if this could be temperature byte
    temp_val = (byte_val >> 2) & 0x3F
    calculated_temp = temp_val / 4 + 16

    if 23.5 <= calculated_temp <= 24.5:
        print(f"Byte [{i}]: 0x{byte_val:02X} = {byte_val:08b}")
        print(f"  → Temperature value (bits 2-7): {temp_val} → {calculated_temp}°C ✓")
        print(f"  → Power bit (bit 0): {byte_val & 0x01}")

print("\n" + "="*80)
print("FIRST 30 BYTES DETAILED")
print("="*80)

print(f"\n24°C High command:")
for i in range(min(30, len(code_24c_bytes))):
    byte_val = code_24c_bytes[i]
    print(f"Byte [{i:2d}]: 0x{byte_val:02X} = {byte_val:08b} = {byte_val:3d}")

print("\n" + "="*80)
print("COMPARISON WITH MY SHORT CODES")
print("="*80)

print(f"\nMy generated codes: ~90 Base64 chars → ~16 bytes")
print(f"Your working codes: ~264 Base64 chars → ~{len(code_24c_bytes)} bytes")
print(f"\nConclusion: I've been generating the WRONG PROTOCOL!")
print(f"The real protocol is {len(code_24c_bytes) // 16}x longer than I thought.")
