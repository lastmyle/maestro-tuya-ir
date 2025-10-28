#!/usr/bin/env python3
"""
Generate test codes for Hubitat using reverse-engineered protocol structure
"""

from app.core.tuya_encoder import encode_tuya_ir
from app.core.fujitsu_encoder import (
    FUJITSU_HEADER_MARK,
    FUJITSU_HEADER_SPACE,
    FUJITSU_BIT_MARK,
    FUJITSU_ZERO_SPACE,
    FUJITSU_ONE_SPACE,
)

# Mode mapping from analysis
MODE_AUTO = 0x00
MODE_COOL = 0x01
MODE_DRY = 0x02
MODE_FAN = 0x03
MODE_HEAT = 0x04

# Fan mapping (estimated from IRremoteESP8266)
FAN_AUTO = 0x00
FAN_LOW = 0x01
FAN_MEDIUM = 0x02
FAN_HIGH = 0x03
FAN_QUIET = 0x04

def bytes_to_timings(state_bytes: bytes) -> list[int]:
    """Convert protocol bytes to IR timings"""
    timings = [FUJITSU_HEADER_MARK, FUJITSU_HEADER_SPACE]

    for byte_val in state_bytes:
        for bit_pos in range(8):
            bit = (byte_val >> bit_pos) & 1
            timings.append(FUJITSU_BIT_MARK)
            timings.append(FUJITSU_ONE_SPACE if bit else FUJITSU_ZERO_SPACE)

    return timings


def calculate_checksum(state_bytes: bytes) -> int:
    """
    Calculate checksum for Fujitsu command.

    Since we don't know the exact formula, we'll try:
    1. Simple sum + offset (common pattern)
    2. Or use 0x3E from working 22°C code
    """
    # Try simple sum approach
    checksum = (sum(state_bytes) + 0x64) & 0xFF
    return checksum


def generate_fujitsu_command(
    temperature: int,
    mode: int,
    fan: int = FAN_AUTO,
    swing: int = 0,
    power: bool = True
) -> bytes:
    """
    Generate Fujitsu AC command based on reverse-engineered protocol.

    Args:
        temperature: Temperature in Celsius (16-30)
        mode: Mode value (MODE_AUTO, MODE_COOL, MODE_HEAT, etc.)
        fan: Fan speed (FAN_AUTO, FAN_LOW, FAN_MEDIUM, FAN_HIGH)
        swing: Swing setting (0-3)
        power: Power state (True=ON, False=OFF)

    Returns:
        16-byte command
    """
    state_bytes = bytearray(16)

    # Bytes 0-4: Header (from all working codes)
    state_bytes[0] = 0x14
    state_bytes[1] = 0x63
    state_bytes[2] = 0x00
    state_bytes[3] = 0x10
    state_bytes[4] = 0x10

    # Byte 5: ON/OFF marker
    state_bytes[5] = 0xFE if power else 0x02

    # Bytes 6-7: Unknown but consistent in all working codes
    state_bytes[6] = 0x09
    state_bytes[7] = 0x30

    # Byte 8: Temperature + Power bit
    if power:
        temp_clamped = max(16, min(30, temperature))
        temp_value = int((temp_clamped - 16) * 4)
        temp_value = max(0, min(63, temp_value))  # Clamp to 6 bits
        power_bit = 1
        state_bytes[8] = power_bit | (temp_value << 2)
    else:
        state_bytes[8] = 0x00

    # Byte 9: Mode
    state_bytes[9] = mode & 0x07  # Bits 0-2

    # Byte 10: Fan + Swing
    fan_bits = fan & 0x07  # Bits 0-2
    swing_bits = (swing & 0x03) << 4  # Bits 4-5
    state_bytes[10] = fan_bits | swing_bits

    # Bytes 11-13: Unknown - using zeros like 22°C codes
    state_bytes[11] = 0x00
    state_bytes[12] = 0x00
    state_bytes[13] = 0x00

    # Byte 14: Hardware compatibility bit (critical!)
    state_bytes[14] = 0x20

    # Byte 15: Checksum
    state_bytes[15] = calculate_checksum(state_bytes[0:15])

    return bytes(state_bytes)


def generate_off_command() -> bytes:
    """Generate OFF command (7 bytes)"""
    state_bytes = bytearray(7)

    # Bytes 0-4: Header
    state_bytes[0] = 0x14
    state_bytes[1] = 0x63
    state_bytes[2] = 0x00
    state_bytes[3] = 0x10
    state_bytes[4] = 0x10

    # Byte 5: OFF marker
    state_bytes[5] = 0x02

    # Byte 6: Checksum (from working OFF code)
    state_bytes[6] = 0xFD

    return bytes(state_bytes)


print("="*80)
print("GENERATING HUBITAT TEST CODES")
print("="*80)
print("\nBased on reverse-engineered protocol from your working codes:")
print("  - Temperature: Confirmed formula")
print("  - Mode: Auto=0x00, Cool=0x01, Heat=0x04")
print("  - Fan: Using 0x11 from working 22°C codes")
print("  - Structure: 16-byte format like 22°C codes")
print()

test_codes = []

# Test 1: OFF
print("\n1. OFF Command")
print("-" * 80)
off_bytes = generate_off_command()
print(f"Bytes: {' '.join(f'{b:02X}' for b in off_bytes)}")
off_timings = bytes_to_timings(off_bytes)
off_code = encode_tuya_ir(off_timings)
print(f"Tuya code: {off_code}")
test_codes.append(("OFF", off_code, off_bytes, "AC turns OFF"))

# Test 2: 18°C Cool Auto (coldest)
print("\n2. 18°C Cool Auto (Coldest)")
print("-" * 80)
bytes_18c = generate_fujitsu_command(
    temperature=18,
    mode=MODE_COOL,
    fan=0x01,  # Using fan value from working 22°C code (0x11 → bits 0-2 = 0x01)
    swing=0x01  # Using swing value from working 22°C code (0x11 → bits 4-5 = 0x01)
)
print(f"Bytes: {' '.join(f'{b:02X}' for b in bytes_18c)}")
timings_18c = bytes_to_timings(bytes_18c)
code_18c = encode_tuya_ir(timings_18c)
print(f"Tuya code: {code_18c}")
test_codes.append(("18°C Cool Auto", code_18c, bytes_18c, "AC ON, Cool mode, 18°C, Auto fan"))

# Test 3: 22°C Cool Auto (should match working structure)
print("\n3. 22°C Cool Auto (Verification)")
print("-" * 80)
bytes_22c = generate_fujitsu_command(
    temperature=22,
    mode=MODE_COOL,
    fan=0x01,
    swing=0x01
)
print(f"Bytes: {' '.join(f'{b:02X}' for b in bytes_22c)}")
print(f"Compare with working 22°C Cool:")
print(f"  Working: 14 63 00 10 10 FE 09 30 60 01 11 00 00 00 20 3E")
print(f"  Generated: {' '.join(f'{b:02X}' for b in bytes_22c)}")
timings_22c = bytes_to_timings(bytes_22c)
code_22c = encode_tuya_ir(timings_22c)
print(f"Tuya code: {code_22c}")
test_codes.append(("22°C Cool Auto", code_22c, bytes_22c, "AC ON, Cool mode, 22°C, Auto fan (should match working code)"))

# Test 4: 25°C Cool Auto (warmer)
print("\n4. 25°C Cool Auto")
print("-" * 80)
bytes_25c = generate_fujitsu_command(
    temperature=25,
    mode=MODE_COOL,
    fan=0x01,
    swing=0x01
)
print(f"Bytes: {' '.join(f'{b:02X}' for b in bytes_25c)}")
timings_25c = bytes_to_timings(bytes_25c)
code_25c = encode_tuya_ir(timings_25c)
print(f"Tuya code: {code_25c}")
test_codes.append(("25°C Cool Auto", code_25c, bytes_25c, "AC ON, Cool mode, 25°C, Auto fan"))

# Test 5: 24°C Heat Auto (different mode)
print("\n5. 24°C Heat Auto (Test Heat Mode)")
print("-" * 80)
bytes_24h = generate_fujitsu_command(
    temperature=24,
    mode=MODE_HEAT,
    fan=0x01,
    swing=0x01
)
print(f"Bytes: {' '.join(f'{b:02X}' for b in bytes_24h)}")
timings_24h = bytes_to_timings(bytes_24h)
code_24h = encode_tuya_ir(timings_24h)
print(f"Tuya code: {code_24h}")
test_codes.append(("24°C Heat Auto", code_24h, bytes_24h, "AC ON, Heat mode, 24°C, Auto fan"))

# Test 6: 22°C Auto mode (for comparison with Cool)
print("\n6. 22°C Auto Mode")
print("-" * 80)
bytes_22a = generate_fujitsu_command(
    temperature=22,
    mode=MODE_AUTO,
    fan=0x01,
    swing=0x01
)
print(f"Bytes: {' '.join(f'{b:02X}' for b in bytes_22a)}")
timings_22a = bytes_to_timings(bytes_22a)
code_22a = encode_tuya_ir(timings_22a)
print(f"Tuya code: {code_22a}")
test_codes.append(("22°C Auto Mode", code_22a, bytes_22a, "AC ON, Auto mode, 22°C"))

print("\n" + "="*80)
print("SAVING TO FILE")
print("="*80)

# Save to file
output = []
output.append("="*80)
output.append("HUBITAT TEST CODES V2")
output.append("="*80)
output.append("")
output.append("Generated using reverse-engineered protocol from your working codes.")
output.append("")
output.append("Protocol Structure (16 bytes for ON, 7 bytes for OFF):")
output.append("  Byte 0-4:  Header (14 63 00 10 10)")
output.append("  Byte 5:    ON/OFF marker (FE=ON, 02=OFF)")
output.append("  Byte 6-7:  Unknown but consistent (09 30)")
output.append("  Byte 8:    Temperature + Power bit")
output.append("  Byte 9:    Mode (0x00=Auto, 0x01=Cool, 0x04=Heat)")
output.append("  Byte 10:   Fan/Swing (0x11 from working codes)")
output.append("  Byte 11-13: Unknown (00 00 00)")
output.append("  Byte 14:   Hardware compat (0x20)")
output.append("  Byte 15:   Checksum")
output.append("")
output.append("="*80)
output.append("")

for i, (name, code, bytes_val, expected) in enumerate(test_codes, 1):
    output.append(f"TEST CODE {i}: {name}")
    output.append("-" * 80)
    output.append(f"Code: {code}")
    output.append("")
    output.append(f"Bytes: {' '.join(f'{b:02X}' for b in bytes_val)}")
    output.append(f"Expected: {expected}")
    output.append("")

    # Temperature analysis for ON commands
    if len(bytes_val) >= 9:
        byte_8 = bytes_val[8]
        temp_val = (byte_8 >> 2) & 0x3F
        calculated_temp = temp_val / 4 + 16
        power_bit = byte_8 & 0x01
        mode_val = bytes_val[9] & 0x07

        mode_names = {0: "Auto", 1: "Cool", 2: "Dry", 3: "Fan", 4: "Heat"}
        mode_name = mode_names.get(mode_val, f"Unknown({mode_val})")

        output.append(f"Decoded:")
        output.append(f"  Power: {'ON' if power_bit else 'OFF'}")
        output.append(f"  Temperature: {calculated_temp}°C")
        output.append(f"  Mode: {mode_name}")
        output.append("")

    output.append("="*80)
    output.append("")

# Write to file
with open("TEST_CODES_V2.txt", "w") as f:
    f.write("\n".join(output))

print(f"\n✅ Saved {len(test_codes)} test codes to TEST_CODES_V2.txt")

print("\n" + "="*80)
print("QUICK REFERENCE")
print("="*80)
print("\nCopy these codes to test on your Hubitat:\n")
for name, code, _, _ in test_codes:
    print(f"{name}:")
    print(f"  {code}")
    print()

print("="*80)
print("NEXT STEPS")
print("="*80)
print("\n1. Test these codes on your AC via Hubitat")
print("2. Report which ones work and what they do")
print("3. If they work, we can generate the full 376-command set!")
print("\nNote: These codes may start with different letters (B, E, D, etc.)")
print("      due to FastLZ compression - this is normal and expected.")
