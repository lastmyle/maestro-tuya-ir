#!/usr/bin/env python3
"""
Analyze the 21°C code and compare with OFF and 20°C codes
"""

from app.core.tuya_encoder import decode_tuya_ir

# Remove spaces from user's input
CODE_21C = "BvQMFwbeAb4gARFdAb4BlQTeAV0B3gGVBL4BXQFAAwHeAUADAZUEQANAD0ADAd4BQAMBlQRAA+ABD0ATAV0BQA/AA0APwAPAE0AHBd4BlQTeAUAHAL4gAQFdAUADAd4B4AMDAZUEQBNAAwHeAYADAb4B4AkTQBsBvgFAAwGVBEALAd4BQAcBlQSADwuVBN4BlQS+AZUE3gE="

OFF_CODE = "BvQMFwbeAb4gARFdAb4BlQTeAV0B3gGVBL4BXQFAAwHeAUADAZUEQANAD0ADAd4BQAMBlQRAA+ABD0ATAV0BQA/AA0APwAPAE0AHBd4BlQTeAUAHAL4gAQFdAUADAd4B4AMDAZUEQBNAAwHeAYADAb4B4AkTQBsBvgFAAwGVBEALAd4BQAcBlQSADwuVBN4BlQS+AZUE3gE="

ON_20C = "BxoNDAbbAV8BQAMDtgGUBEAHAdsBgAcBtgGAA4APAZQE4AEP4A8TQBeAA+AFKwFfAcADgBcBlATADwLbAbYgAQFfAUADAdsBwAMBlARAD0ADAdsBwAMBlATgBwMAtuACEwG2AeADJwC2IAEBXwFAAwHbAeADAwC2IAEGXwG2AZQE22ADAV8BQAOADwFfAeADAwG2AUADQCcBXwGAAwC2IAEBXwFAAwHbAeAFAwG2AeADJ4APALYgB0AL4AEDALYgAQFfAUADAdsBwAkDQBdAA+AHG0ATQAPgExfgBx9ADwO2AZQEQDMDtgFfAYAHQA+AA4ALC18BtgGUBLYBtgG2AQ=="

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
print("Analyzing 21°C Code")
print("="*80)

# Check if codes are identical
if CODE_21C == OFF_CODE:
    print("\n⚠️  WARNING: 21°C code is IDENTICAL to OFF code!")
    print("   This might be a copy/paste error.")
else:
    print("\n✅ 21°C code is different from OFF code")

print("\n" + "="*80)
print("Decoding All Codes")
print("="*80)

codes = [
    ("OFF", OFF_CODE),
    ("21°C", CODE_21C),
    ("20°C Auto High Vertical (ON)", ON_20C),
]

results = []

for name, code in codes:
    print(f"\n{name}")
    print("-" * 80)

    timings = decode_tuya_ir(code)
    bits = timings_to_bits(timings)
    state_bytes = bits_to_bytes(bits)

    print(f"Timings: {len(timings)} values")
    print(f"Bits: {len(bits)} bits")
    print(f"Bytes ({len(state_bytes)}): {' '.join(f'{b:02X}' for b in state_bytes)}")

    results.append((name, state_bytes))

print("\n" + "="*80)
print("Byte-by-Byte Comparison")
print("="*80)

# Find max length
max_len = max(len(bytes_val) for _, bytes_val in results)

print(f"\n{'Byte':<6} {'OFF':<6} {'21°C':<6} {'20°C ON':<10} Notes")
print("-" * 80)

for i in range(max_len):
    row = [f"[{i}]"]

    for name, bytes_val in results:
        if i < len(bytes_val):
            row.append(f"{bytes_val[i]:02X}")
        else:
            row.append("--")

    # Add notes for specific bytes
    notes = ""
    if i == 5:
        notes = "ON/OFF marker?"
    elif i == 8:
        notes = "Temperature byte?"
    elif i == 9:
        notes = "Mode byte?"

    # Highlight differences
    values = [bytes_val[i] if i < len(bytes_val) else None for _, bytes_val in results]
    if len(set(v for v in values if v is not None)) > 1:
        notes = "⚠️  DIFFERENT " + notes

    print(f"{row[0]:<6} {row[1]:<6} {row[2]:<6} {row[3]:<10} {notes}")

print("\n" + "="*80)
print("Temperature Analysis")
print("="*80)

if results[1][1] != results[0][1]:  # If 21°C != OFF
    bytes_21c = results[1][1]
    bytes_off = results[0][1]
    bytes_20c = results[2][1]

    print("\nLooking for temperature encoding...")

    # Compare 20°C ON with 21°C
    if len(bytes_20c) >= 9 and len(bytes_21c) >= 9:
        print(f"\nByte 8 comparison:")
        print(f"  20°C ON: 0x{bytes_20c[8]:02X} = {bytes_20c[8]:08b}")
        print(f"  21°C:    0x{bytes_21c[8]:02X} = {bytes_21c[8]:08b}")

        # Extract temperature value (bits 2-7)
        temp_val_20c = (bytes_20c[8] >> 2) & 0x3F
        temp_val_21c = (bytes_21c[8] >> 2) & 0x3F

        print(f"\n  Temperature value (bits 2-7):")
        print(f"    20°C ON: {temp_val_20c} → {temp_val_20c / 4 + 16}°C")
        print(f"    21°C:    {temp_val_21c} → {temp_val_21c / 4 + 16}°C")

        if abs((temp_val_21c / 4 + 16) - 21.0) < 0.1:
            print(f"\n  ✅ Temperature formula confirmed: (value / 4) + 16 = temp°C")
        else:
            print(f"\n  ❌ Temperature formula doesn't match expected 21°C")
else:
    print("\n⚠️  21°C code is identical to OFF - cannot analyze temperature encoding")

print("\n" + "="*80)
