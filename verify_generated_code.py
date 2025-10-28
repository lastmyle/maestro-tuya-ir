#!/usr/bin/env python3
"""
Verify the generated heat_24c_low code matches the working 24C_High
"""

from app.core.tuya_encoder import decode_ir, encode_ir

# Original working code
WORKING_24C_HIGH = "EfcMNAbRAYIB0QFWAdEBkwTRAeADB0ALQANAF0ADQAvAA0APQAPAD0AHwEdAC+ADA0AXQAPAE0A3QA9AA8ATwAdAE0AfwA/AB0AT4BMD4AMnwAvAB0BTwANAE8BHQAtAA0APQAdAI0AH4AMDQBvAF0ALwBsAgmABAdEBQA/AFwCCYAEB0QHgAQ8C0QGCYAFABwHRAUAr4AMHAIJgAUAHgAOAH8ABAdEBQANAE0ADAILgAAFAC4ADgBcC0QGCYAFAB4ADQBcHkwSCAYIB0QFAC0ADBJME0QGCIAFAB0ADC1YB0QGCAdEBggHRAQ=="

print("="*80)
print("VERIFYING GENERATED CODE")
print("="*80)

# Decode working code to get bytes
signal = decode_ir(WORKING_24C_HIGH)
print(f"\nWorking 24C_High:")
print(f"  Timings: {len(signal)}")
print(f"  First 10 timings: {signal[:10]}")

# Convert timings to bytes
def timings_to_bits(timings: list[int]) -> list[int]:
    data_timings = timings[2:]  # Skip header
    bits = []
    for i in range(0, len(data_timings), 2):
        if i + 1 < len(data_timings):
            space = data_timings[i + 1]
            bits.append(1 if space > 600 else 0)
    return bits

def bits_to_bytes(bits: list[int]) -> bytes:
    state_bytes = []
    for i in range(0, len(bits), 8):
        if i + 8 <= len(bits):
            byte_bits = bits[i:i+8]
            byte_val = sum(bit << j for j, bit in enumerate(byte_bits))
            state_bytes.append(byte_val)
    return bytes(state_bytes)

bits = timings_to_bits(signal)
working_bytes = bits_to_bytes(bits)

print(f"\nWorking bytes: {working_bytes.hex().upper()}")
print(f"  Length: {len(working_bytes)} bytes")
print(f"  Byte 8 (temp): 0x{working_bytes[8]:02X} = {((working_bytes[8]>>2)&0x3F)/4 + 16}°C")
print(f"  Byte 9 (mode): 0x{working_bytes[9]:02X} = {'Heat' if working_bytes[9]==4 else 'Unknown'}")
print(f"  Byte 15 (checksum): 0x{working_bytes[15]:02X}")

# Verify checksum
checksum_check = (sum(working_bytes[:15]) + working_bytes[15]) & 0xFF
print(f"  Checksum verify: (sum + checksum) & 0xFF = 0x{checksum_check:02X} {'✓' if checksum_check == 0x9E else '✗'}")

# Re-encode to verify round-trip
reencoded = encode_ir(signal)
print(f"\nRe-encoded code:")
print(f"  {reencoded}")
print(f"  Length: {len(reencoded)} chars")

if reencoded == WORKING_24C_HIGH:
    print(f"\n✓✓✓ PERFECT MATCH! Re-encoded code exactly matches original!")
else:
    print(f"\nCodes differ:")
    print(f"  Original:  {WORKING_24C_HIGH[:80]}...")
    print(f"  Generated: {reencoded[:80]}...")

    # Check if timings match
    signal2 = decode_ir(reencoded)
    if signal == signal2:
        print(f"\n✓ Timings match! Difference is just compression variation.")
    else:
        print(f"\n✗ Timings differ! Something is wrong.")

print("\n" + "="*80)
print("LOADING GENERATED COMMANDS FILE")
print("="*80)

import json
with open("fujitsu_ac_commands_complete.json", "r") as f:
    data = json.load(f)

generated_code = data["commands"]["heat_24c_low"]["code"]
generated_bytes = bytes.fromhex(data["commands"]["heat_24c_low"]["bytes"])

print(f"\nGenerated heat_24c_low:")
print(f"  Code: {generated_code}")
print(f"  Bytes: {generated_bytes.hex().upper()}")

if generated_bytes == working_bytes:
    print(f"\n✓✓✓ BYTES MATCH EXACTLY!")
else:
    print(f"\nByte differences:")
    for i in range(min(len(generated_bytes), len(working_bytes))):
        if generated_bytes[i] != working_bytes[i]:
            print(f"  Byte {i}: 0x{generated_bytes[i]:02X} vs 0x{working_bytes[i]:02X}")

# Test if generated code produces same timings
print("\n" + "="*80)
print("FINAL VERIFICATION")
print("="*80)

generated_signal = decode_ir(generated_code)

if generated_signal == signal:
    print(f"\n✓✓✓ SUCCESS! Generated code produces identical timings!")
    print(f"    The generated command will work on your AC!")
else:
    print(f"\n✗ Timings differ!")
    print(f"  Working timings: {len(signal)}")
    print(f"  Generated timings: {len(generated_signal)}")
