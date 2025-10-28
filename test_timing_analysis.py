#!/usr/bin/env python3
"""
Detailed timing analysis to find missing bits
"""

from app.core.tuya_encoder import decode_tuya_ir

ON_CODE = "BxoNDAbbAV8BQAMDtgGUBEAHAdsBgAcBtgGAA4APAZQE4AEP4A8TQBeAA+AFKwFfAcADgBcBlATADwLbAbYgAQFfAUADAdsBwAMBlARAD0ADAdsBwAMBlATgBwMAtuACEwG2AeADJwC2IAEBXwFAAwHbAeADAwC2IAEGXwG2AZQE22ADAV8BQAOADwFfAeADAwG2AUADQCcBXwGAAwC2IAEBXwFAAwHbAeAFAwG2AeADJ4APALYgB0AL4AEDALYgAQFfAUADAdsBwAkDQBdAA+AHG0ATQAPgExfgBx9ADwO2AZQEQDMDtgFfAYAHQA+AA4ALC18BtgGUBLYBtgG2AQ=="

timings = decode_tuya_ir(ON_CODE)

print("="*80)
print(f"Timing Analysis: {len(timings)} timings")
print("="*80)

print(f"\nHeader:")
print(f"  Mark: {timings[0]} μs")
print(f"  Space: {timings[1]} μs")

print(f"\nData timings (first 20 pairs):")
data_timings = timings[2:]
for i in range(0, min(40, len(data_timings)), 2):
    if i + 1 < len(data_timings):
        mark = data_timings[i]
        space = data_timings[i + 1]
        bit = 1 if space > 600 else 0
        print(f"  Pair {i//2}: Mark={mark:4d} Space={space:4d} → Bit={bit}")

print(f"\nLast 10 pairs:")
for i in range(max(0, len(data_timings) - 20), len(data_timings), 2):
    if i + 1 < len(data_timings):
        mark = data_timings[i]
        space = data_timings[i + 1]
        bit = 1 if space > 600 else 0
        print(f"  Pair {i//2}: Mark={mark:4d} Space={space:4d} → Bit={bit}")
    elif i < len(data_timings):
        # Orphan mark at the end?
        mark = data_timings[i]
        print(f"  Orphan: Mark={mark:4d} (no space)")

print(f"\nTotal data timing values: {len(data_timings)}")
print(f"Complete pairs: {len(data_timings) // 2}")
print(f"Orphan timing: {'Yes' if len(data_timings) % 2 else 'No'}")

# Count bits
bits = []
for i in range(0, len(data_timings), 2):
    if i + 1 < len(data_timings):
        mark = data_timings[i]
        space = data_timings[i + 1]
        bits.append(1 if space > 600 else 0)

print(f"\nTotal bits: {len(bits)}")
print(f"Complete bytes: {len(bits) // 8}")
print(f"Remaining bits: {len(bits) % 8}")
print(f"\nExpected: 128 bits (16 bytes)")
print(f"Missing: {128 - len(bits)} bits")

if len(bits) % 8 != 0:
    print(f"\nPartial last byte:")
    last_bits = bits[-(len(bits) % 8):]
    print(f"  Bits: {last_bits}")
    print(f"  Binary: {''.join(str(b) for b in last_bits)}")
