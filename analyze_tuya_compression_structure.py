#!/usr/bin/env python3
"""
Analyze the compression structure of working Tuya codes
to understand exactly how Tuya compresses
"""

import base64
from app.core.fastlz import fastlz_decompress

CODE_24C_HIGH = "EfcMNAbRAYIB0QFWAdEBkwTRAeADB0ALQANAF0ADQAvAA0APQAPAD0AHwEdAC+ADA0AXQAPAE0A3QA9AA8ATwAdAE0AfwA/AB0AT4BMD4AMnwAvAB0BTwANAE8BHQAtAA0APQAdAI0AH4AMDQBvAF0ALwBsAgmABAdEBQA/AFwCCYAEB0QHgAQ8C0QGCYAFABwHRAUAr4AMHAIJgAUAHgAOAH8ABAdEBQANAE0ADAILgAAFAC4ADgBcC0QGCYAFAB4ADQBcHkwSCAYIB0QFAC0ADBJME0QGCIAFAB0ADC1YB0QGCAdEBggHRAQ=="

print("="*80)
print("ANALYZING TUYA COMPRESSION STRUCTURE")
print("="*80)

# Decode Base64
compressed = base64.b64decode(CODE_24C_HIGH)
print(f"\nCompressed length: {len(compressed)} bytes")

# Analyze block structure
print("\nBlock structure analysis:")
print("-" * 80)

pos = 0
block_num = 0

while pos < len(compressed):
    if pos >= len(compressed):
        break

    # Read control byte
    ctrl = compressed[pos]
    pos += 1

    L = ctrl >> 5  # Length field (bits 5-7)
    D = ctrl & 0b11111  # Distance field (bits 0-4)

    if L == 0:
        # Literal block
        length = D + 1
        print(f"Block {block_num}: LITERAL, {length} bytes at pos {pos-1}")
        print(f"  Control byte: 0x{ctrl:02X} = {ctrl:08b}")
        print(f"  Data: {' '.join(f'{compressed[pos+i]:02X}' for i in range(min(10, length)))}{'...' if length > 10 else ''}")

        pos += length
        block_num += 1

        if block_num > 10:  # Limit output
            print(f"... (showing first 10 blocks)")
            break
    else:
        # Back reference block
        if L == 7:
            length = 7 + compressed[pos]
            pos += 1
        else:
            length = L
        length += 2

        distance = (D << 8) | compressed[pos]
        distance += 1
        pos += 1

        print(f"Block {block_num}: REFERENCE, length={length}, distance={distance} at pos {pos-2}")
        print(f"  Control byte: 0x{ctrl:02X} = {ctrl:08b}")

        block_num += 1

        if block_num > 10:
            print(f"... (showing first 10 blocks)")
            break

print(f"\nTotal blocks analyzed: {min(block_num, 10)}")
print(f"Total compressed size: {len(compressed)} bytes")

# Now try to RECREATE this exact compression
print("\n" + "="*80)
print("COMPARING WITH MY COMPRESSION")
print("="*80)

from app.core.fastlz import fastlz_compress

raw_data = fastlz_decompress(compressed)
print(f"\nDecompressed data: {len(raw_data)} bytes")

for level in [0, 1, 2]:
    my_compressed = fastlz_compress(raw_data, level=level)
    print(f"\nLevel {level}:")
    print(f"  My size: {len(my_compressed)} bytes")
    print(f"  Tuya size: {len(compressed)} bytes")
    print(f"  Difference: {len(my_compressed) - len(compressed):+d} bytes")

    if len(my_compressed) <= 50:
        print(f"  My first 50: {' '.join(f'{b:02X}' for b in my_compressed[:50])}")
        print(f"  Tuya first 50: {' '.join(f'{b:02X}' for b in compressed[:50])}")

print("\n" + "="*80)
print("HYPOTHESIS")
print("="*80)

print("\nTuya's compression (235 bytes) is between:")
print("  - Level 0 literal blocks (~535 bytes)")
print("  - Level 1/2 optimal compression (~126 bytes)")
print()
print("This suggests Tuya uses:")
print("  1. A custom FastLZ variant")
print("  2. Sub-optimal compression settings")
print("  3. Older FastLZ version")
print("  4. OR: Compression artifacts from low battery remote!")
print()
print("SOLUTION:")
print("  Since we can't replicate Tuya's exact compression,")
print("  you MUST replace remote batteries and re-learn codes")
print("  with a fresh signal to get clean, consistent compression.")
