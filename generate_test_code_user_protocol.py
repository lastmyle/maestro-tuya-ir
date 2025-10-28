#!/usr/bin/env python3
"""
Generate a test code using the user's protocol structure
Based on analysis of working OFF and ON codes
"""

from app.core.tuya_encoder import encode_tuya_ir
from app.core.fujitsu_encoder import (
    FUJITSU_HEADER_MARK,
    FUJITSU_HEADER_SPACE,
    FUJITSU_BIT_MARK,
    FUJITSU_ZERO_SPACE,
    FUJITSU_ONE_SPACE,
)

def bytes_to_timings(state_bytes: bytes) -> list[int]:
    """Convert protocol bytes to IR timings"""
    timings = [FUJITSU_HEADER_MARK, FUJITSU_HEADER_SPACE]

    for byte_val in state_bytes:
        for bit_pos in range(8):
            bit = (byte_val >> bit_pos) & 1
            timings.append(FUJITSU_BIT_MARK)
            timings.append(FUJITSU_ONE_SPACE if bit else FUJITSU_ZERO_SPACE)

    return timings


print("="*80)
print("Generating Test Code Using User's Protocol Structure")
print("="*80)

# User's working ON code bytes (first 10 bytes we're confident about):
# 14 63 00 10 10 FE 09 30 41 00 ...
#
# Let's try to generate Cool 25°C Medium:
# - Keep bytes 0-4 the same (header)
# - Byte 5: 0xFE (ON)
# - Byte 6-7: Try to encode temperature (25°C)
# - Byte 8-9: Try to encode mode (Cool) and fan (Medium)
# - Rest: Copy from working code or use zeros + checksum

# Temperature encoding (guess):
# User's code has 20°C → Bytes 6-8 = 09 30 41
# Let's try 25°C → Need to figure out the formula

# For now, let's just modify the working code slightly
# Change temperature from 20°C to 25°C

# User's 20°C: 14 63 00 10 10 FE 09 30 41 00 11 40 18 16 01
# Hypothesis: Temperature might be in byte 7 or 8
# Byte 7 = 0x30 (48 decimal) - could this be related to temp?
# Byte 8 = 0x41 (65 decimal)

# Using IRremoteESP8266 formula for byte 8:
# temp_value = (temp - 16) * 4
# For 20°C: (20 - 16) * 4 = 16 = 0x10
# But byte 8 = 0x41, and bits 2-7 = 010000 = 16 ✓

# So byte 8 encodes temperature in bits 2-7
# For 25°C: (25 - 16) * 4 = 36 = 0x24 (in bits 2-7)
# New byte 8 = 0x01 (power on) | (0x24 << 2) = 0x01 | 0x90 = 0x91

test_codes = []

# Test 1: Cool 25°C Auto
print("\n1. Cool 25°C Auto (Modified from working code)")
print("-" * 80)
# Start with working code structure
state_bytes_25c = bytes([
    0x14, 0x63, 0x00, 0x10, 0x10,  # Header
    0xFE,  # ON marker
    0x09,  # Byte 6 (unknown)
    0x30,  # Byte 7 (unknown)
    0x91,  # Byte 8 - Changed: 25°C = (25-16)*4 = 36 → bits 2-7 = 100100 → 0x01 | (36<<2) = 0x91
    0x01,  # Byte 9 - Changed: Cool = 0x01 (guess)
    0x11, 0x40, 0x18, 0x16, 0x01,  # Bytes 10-14 (copy from working)
    0x00,  # Byte 15 - Checksum placeholder
])
print(f"Bytes: {' '.join(f'{b:02X}' for b in state_bytes_25c)}")
timings_25c = bytes_to_timings(state_bytes_25c)
code_25c = encode_tuya_ir(timings_25c)
print(f"Tuya code: {code_25c}")
test_codes.append(("Cool 25°C Auto", code_25c))

# Test 2: Cool 18°C Auto (coldest setting)
print("\n2. Cool 18°C Auto (Coldest)")
print("-" * 80)
# 18°C: (18-16)*4 = 8 → bits 2-7 = 001000 → 0x01 | (8<<2) = 0x21
state_bytes_18c = bytes([
    0x14, 0x63, 0x00, 0x10, 0x10,
    0xFE,
    0x09, 0x30,
    0x21,  # 18°C
    0x01,  # Cool
    0x11, 0x40, 0x18, 0x16, 0x01,
    0x00,
])
print(f"Bytes: {' '.join(f'{b:02X}' for b in state_bytes_18c)}")
timings_18c = bytes_to_timings(state_bytes_18c)
code_18c = encode_tuya_ir(timings_18c)
print(f"Tuya code: {code_18c}")
test_codes.append(("Cool 18°C Auto", code_18c))

# Test 3: Cool 20°C Auto (should match working code if our theory is correct)
print("\n3. Cool 20°C Auto (Verification - should match original if byte 9 = Cool)")
print("-" * 80)
# 20°C: (20-16)*4 = 16 → bits 2-7 = 010000 → 0x01 | (16<<2) = 0x41
state_bytes_20c_cool = bytes([
    0x14, 0x63, 0x00, 0x10, 0x10,
    0xFE,
    0x09, 0x30,
    0x41,  # 20°C (matches working code)
    0x01,  # Cool (changed from 0x00 in working code)
    0x11, 0x40, 0x18, 0x16, 0x01,
    0x00,
])
print(f"Bytes: {' '.join(f'{b:02X}' for b in state_bytes_20c_cool)}")
timings_20c_cool = bytes_to_timings(state_bytes_20c_cool)
code_20c_cool = encode_tuya_ir(timings_20c_cool)
print(f"Tuya code: {code_20c_cool}")
test_codes.append(("Cool 20°C Auto", code_20c_cool))

print("\n" + "="*80)
print("Test Codes Generated")
print("="*80)
print("\nThese codes are based on reverse-engineering your working codes.")
print("They use the same protocol structure as your working ON command.")
print("\nPlease test them on your AC:")
for name, code in test_codes:
    print(f"\n{name}:")
    print(f"  {code}")

print("\n" + "="*80)
print("Important Notes:")
print("="*80)
print("1. These codes start with 'B' like your working codes")
print("2. They use byte 5 = 0xFE for ON (like your working code)")
print("3. Temperature is encoded in byte 8, bits 2-7")
print("4. Mode might be in byte 9 (Cool = 0x01, Auto = 0x00)")
print("5. Checksum byte 15 is set to 0x00 (may need correction)")
print("\nIf these work, we can generate the full command set.")
print("If not, we need more working codes to analyze.")
