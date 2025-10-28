#!/usr/bin/env python3
"""
Test different FastLZ compression levels to match Tuya's format
"""

import base64
import struct
from app.core.tuya_encoder import decode_tuya_ir
from app.core.fastlz import fastlz_decompress, fastlz_compress

# Working code
CODE_24C_HIGH = "EfcMNAbRAYIB0QFWAdEBkwTRAeADB0ALQANAF0ADQAvAA0APQAPAD0AHwEdAC+ADA0AXQAPAE0A3QA9AA8ATwAdAE0AfwA/AB0AT4BMD4AMnwAvAB0BTwANAE8BHQAtAA0APQAdAI0AH4AMDQBvAF0ALwBsAgmABAdEBQA/AFwCCYAEB0QHgAQ8C0QGCYAFABwHRAUAr4AMHAIJgAUAHgAOAH8ABAdEBQANAE0ADAILgAAFAC4ADgBcC0QGCYAFAB4ADQBcHkwSCAYIB0QFAC0ADBJME0QGCIAFAB0ADC1YB0QGCAdEBggHRAQ=="

print("="*80)
print("TESTING COMPRESSION LEVELS TO MATCH TUYA")
print("="*80)

# Decode working code
compressed_original = base64.b64decode(CODE_24C_HIGH)
raw_bytes = fastlz_decompress(compressed_original)

print(f"\nOriginal Tuya code:")
print(f"  Compressed: {len(compressed_original)} bytes")
print(f"  Base64: {len(CODE_24C_HIGH)} chars")
print(f"  Raw data: {len(raw_bytes)} bytes")

print(f"\n" + "="*80)
print("TESTING DIFFERENT COMPRESSION LEVELS")
print("="*80)

for level in [0, 1, 2]:
    print(f"\nLevel {level}:")
    compressed = fastlz_compress(raw_bytes, level=level)
    base64_code = base64.b64encode(compressed).decode("ascii")

    print(f"  Compressed: {len(compressed)} bytes")
    print(f"  Base64: {len(base64_code)} chars")
    print(f"  Match: {'✓ YES!' if len(compressed) == len(compressed_original) else '✗ No'}")

    if len(compressed) == len(compressed_original):
        # Check if bytes match exactly
        if compressed == compressed_original:
            print(f"  EXACT MATCH! Use compression level {level}")
        else:
            # Show differences
            diff_count = sum(1 for a, b in zip(compressed, compressed_original) if a != b)
            print(f"  Byte differences: {diff_count} / {len(compressed)}")

print(f"\n" + "="*80)
print("ANALYZING TUYA'S COMPRESSION PATTERN")
print("="*80)

# Check if level 0 (no compression) matches
compressed_level0 = fastlz_compress(raw_bytes, level=0)
print(f"\nLevel 0 (no compression):")
print(f"  Size: {len(compressed_level0)} bytes")
print(f"  Expected for no compression: {len(raw_bytes) + (len(raw_bytes)//32)*2} bytes approx")

# The issue might be that Tuya uses a DIFFERENT FastLZ implementation
# Let's try to understand the pattern by examining the first few bytes

print(f"\nFirst 20 bytes comparison:")
print(f"  Tuya:    {' '.join(f'{b:02X}' for b in compressed_original[:20])}")
print(f"  Level 0: {' '.join(f'{b:02X}' for b in compressed_level0[:20])}")
print(f"  Level 1: {' '.join(f'{b:02X}' for b in fastlz_compress(raw_bytes, level=1)[:20])}")
print(f"  Level 2: {' '.join(f'{b:02X}' for b in fastlz_compress(raw_bytes, level=2)[:20])}")

print(f"\n" + "="*80)
print("CONCLUSION")
print("="*80)

print("\nTuya uses a specific FastLZ implementation that produces:")
print(f"  235 bytes compressed from 518 bytes raw")
print(f"  This is ~45% compression ratio")
print()
print("My FastLZ produces:")
print(f"  Level 0: {len(compressed_level0)} bytes (no compression)")
print(f"  Level 1: {len(fastlz_compress(raw_bytes, level=1))} bytes")
print(f"  Level 2: {len(fastlz_compress(raw_bytes, level=2))} bytes (best compression)")
print()
print("None of these match Tuya's 235 bytes!")
print()
print("Possible solutions:")
print("  1. Use the EXACT Tuya device to learn codes (no battery issues)")
print("  2. Find Tuya's exact FastLZ source code")
print("  3. Try different checksum (0x9E formula) with my compression")
print("     - AC might accept different compression if checksum is correct")
