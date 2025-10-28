#!/usr/bin/env python3
"""
Compare 22°C codes to identify Mode and Fan bytes
"""

from app.core.tuya_encoder import decode_tuya_ir

# Remove spaces from user's input
CODE_22C_COOL_HIGH = "EfcMEwbxAd0APwImAfEBmATxAUALA5gErwFADwkmAT8CJgHxAZgEQAPAEwHxAcAjBZgE8QEmAYAjCyYB8QFhAa8BYQHxAUALQAPAC8AHQBMDJgE/AkA3QBNARwMmAfEBQANAD0AHQAMDmASvAUAHwANAJ0ATApgE8aADwAtAB0ADAfEBQCNAQ0ALwDcFJgE/AiYBQAcB8QFAG+ADI+ADJwdhAa8BYQHxAUAnwANAH0ADQBcDmASvAUAXB2EBrwFhAfEBQAtAA0ALQAMDmATxAeALD+ADE0AngAPgBUMAryABgBNABwPxAWEBgAcAryABgAtABwHxAYBLgAuAB0ALQAOAD+ADAQdhAa8BmASvAcABgA8E8QGYBK+gA4ALB68BrwGvAa8B"

CODE_22C = "EQoNGwbPAcoACgItAQoCmgTPAeABB4ALBS0BCgKaBEADgA8A/OACK+ADEwdsAc8BygCWAkAvwCNAC+ALA+ADN+AHH0A74AMfQA9AI0AT4BMDA8oACgLAJ0AHwANAl0ALwEcDLQHPAcBHAS0BQA+AAwBsoAdADwNsAc8B4AMjQDsDbAEKAkAbQAMDbAHPAUAHQAMDbAEKAkArQAeADwHPAUAPAy0BzwFAC0ADAy0BCgJAB0ADAS0BQAPgAQ9AE+APAwEtAYAD4AsfQBvgCxfAE0CD4AMLQA/gBwMHLQHPAWwBzwE="

ON_20C = "BxoNDAbbAV8BQAMDtgGUBEAHAdsBgAcBtgGAA4APAZQE4AEP4A8TQBeAA+AFKwFfAcADgBcBlATADwLbAbYgAQFfAUADAdsBwAMBlARAD0ADAdsBwAMBlATgBwMAtuACEwG2AeADJwC2IAEBXwFAAwHbAeADAwC2IAEGXwG2AZQE22ADAV8BQAOADwFfAeADAwG2AUADQCcBXwGAAwC2IAEBXwFAAwHbAeAFAwG2AeADJ4APALYgB0AL4AEDALYgAQFfAUADAdsBwAkDQBdAA+AHG0ATQAPgExfgBx9ADwO2AZQEQDMDtgFfAYAHQA+AA4ALC18BtgGUBLYBtgG2AQ=="

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
print("22°C CODE COMPARISON - Finding Mode and Fan Bytes")
print("="*80)

codes = [
    ("OFF", OFF_CODE),
    ("20°C Auto (from earlier)", ON_20C),
    ("22°C (previous)", CODE_22C),
    ("22°C Cool High", CODE_22C_COOL_HIGH),
]

results = []

for name, code in codes:
    print(f"\n{name}")
    print("-" * 80)

    timings = decode_tuya_ir(code)
    bits = timings_to_bits(timings)
    state_bytes = bits_to_bytes(bits)

    print(f"Base64: {code[:20]}...")
    print(f"Timings: {len(timings)}, Bits: {len(bits)}, Bytes: {len(state_bytes)}")
    print(f"Bytes: {' '.join(f'{b:02X}' for b in state_bytes)}")

    # Temperature analysis
    if len(state_bytes) >= 9:
        byte_8 = state_bytes[8]
        temp_val = (byte_8 >> 2) & 0x3F
        calculated_temp = temp_val / 4 + 16
        power_bit = byte_8 & 0x01
        print(f"  → Byte 8: 0x{byte_8:02X}, Power: {power_bit}, Temp: {calculated_temp}°C")

    results.append((name, state_bytes))

print("\n" + "="*80)
print("BYTE-BY-BYTE COMPARISON")
print("="*80)

max_len = max(len(bytes_val) for _, bytes_val in results)

print(f"\n{'Byte':<6} {'OFF':<6} {'20°C':<6} {'22°C-1':<8} {'22°C-2':<8} {'Notes'}")
print("-" * 90)

for i in range(max_len):
    row = [f"[{i}]"]

    for name, bytes_val in results:
        if i < len(bytes_val):
            row.append(f"{bytes_val[i]:02X}")
        else:
            row.append("--")

    # Add notes
    notes = ""
    if i == 0:
        notes = "Header"
    elif i == 5:
        notes = "ON/OFF (02=OFF, FE=ON)"
    elif i == 8:
        notes = "Temperature"
    elif i == 9:
        notes = "Mode byte?"
    elif i == 10:
        notes = "Fan byte?"
    elif i == 14:
        notes = "Hardware compat bit"
    elif i == 15:
        notes = "Checksum"

    # Compare 22°C codes specifically
    if len(results) >= 4:
        val_22c_1 = results[2][1][i] if i < len(results[2][1]) else None
        val_22c_2 = results[3][1][i] if i < len(results[3][1]) else None

        if val_22c_1 is not None and val_22c_2 is not None:
            if val_22c_1 != val_22c_2:
                notes = "⚠️  22°C DIFFER! " + notes

    print(f"{row[0]:<6} {row[1]:<6} {row[2]:<6} {row[3]:<8} {row[4]:<8} {notes}")

print("\n" + "="*80)
print("MODE AND FAN ANALYSIS (comparing 22°C codes)")
print("="*80)

if len(results) >= 4:
    bytes_22c_1 = results[2][1]  # 22°C previous
    bytes_22c_2 = results[3][1]  # 22°C Cool High

    print("\nBoth codes are 22°C, so temperature byte should be identical:")
    print(f"  22°C-1 byte 8: 0x{bytes_22c_1[8]:02X}")
    print(f"  22°C-2 byte 8: 0x{bytes_22c_2[8]:02X}")

    if bytes_22c_1[8] == bytes_22c_2[8]:
        print("  ✅ Temperature bytes match!")
    else:
        print("  ⚠️  Temperature bytes differ - might indicate mode/fan in byte 8")

    print("\nLooking for mode/fan differences:")

    # Check byte 9 (suspected mode)
    print(f"\nByte 9 (suspected Mode):")
    print(f"  22°C-1: 0x{bytes_22c_1[9]:02X} = {bytes_22c_1[9]:08b}")
    print(f"  22°C-2: 0x{bytes_22c_2[9]:02X} = {bytes_22c_2[9]:08b}")
    if bytes_22c_1[9] != bytes_22c_2[9]:
        print(f"  ⚠️  DIFFERENT! Bits 0-2: {bytes_22c_1[9] & 0x07} vs {bytes_22c_2[9] & 0x07}")
        print(f"     22°C-1 might be: Auto (0x{bytes_22c_1[9] & 0x07:02X})")
        print(f"     22°C-2 might be: Cool (0x{bytes_22c_2[9] & 0x07:02X})")
    else:
        print(f"  ✅ Same - both might be same mode")

    # Check byte 10 (suspected fan)
    print(f"\nByte 10 (suspected Fan/Swing):")
    print(f"  22°C-1: 0x{bytes_22c_1[10]:02X} = {bytes_22c_1[10]:08b}")
    print(f"  22°C-2: 0x{bytes_22c_2[10]:02X} = {bytes_22c_2[10]:08b}")
    if bytes_22c_1[10] != bytes_22c_2[10]:
        fan_1 = bytes_22c_1[10] & 0x07
        fan_2 = bytes_22c_2[10] & 0x07
        swing_1 = (bytes_22c_1[10] >> 4) & 0x03
        swing_2 = (bytes_22c_2[10] >> 4) & 0x03
        print(f"  ⚠️  DIFFERENT!")
        print(f"     22°C-1: Fan bits 0-2: {fan_1}, Swing bits 4-5: {swing_1}")
        print(f"     22°C-2: Fan bits 0-2: {fan_2}, Swing bits 4-5: {swing_2}")
        print(f"     If 22°C-2 is 'High', then High fan = {fan_2}")
    else:
        print(f"  ✅ Same - both might have same fan/swing")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)

print("\nKnown protocol structure:")
print("  Byte 0-4:  Header (14 63 00 10 10)")
print("  Byte 5:    ON/OFF (FE=ON, 02=OFF)")
print("  Byte 8:    Temperature + Power bit")
print("  Byte 9:    Mode (needs more codes to confirm mapping)")
print("  Byte 10:   Fan/Swing (needs more codes to confirm mapping)")
print("  Byte 14:   Hardware compat (0x20)")
print("  Byte 15:   Checksum")

print("\nTo complete protocol reverse-engineering, we need:")
print("  - Codes with different modes: Heat, Cool, Dry, Fan, Auto")
print("  - Codes with different fan speeds: Low, Medium, High, Auto")
print("  - Codes with swing on/off")
