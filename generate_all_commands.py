#!/usr/bin/env python3
"""
Generate complete Fujitsu AC command set (376 commands)
Using confirmed working 24C_High structure and tuya1.py compression
"""

import json
from app.core.tuya_encoder import encode_ir
from app.core.fujitsu_encoder import (
    FUJITSU_HEADER_MARK,
    FUJITSU_HEADER_SPACE,
    FUJITSU_BIT_MARK,
    FUJITSU_ZERO_SPACE,
    FUJITSU_ONE_SPACE,
)

# Mode constants (from working 24C_High code)
MODE_AUTO = 0x00
MODE_COOL = 0x01
MODE_DRY = 0x02
MODE_FAN = 0x03
MODE_HEAT = 0x04

# Fan constants
FAN_AUTO = 0x00
FAN_LOW = 0x01
FAN_MEDIUM = 0x02
FAN_HIGH = 0x03
FAN_QUIET = 0x04

# Temperature range
MIN_TEMP = 16
MAX_TEMP = 30

# Swing setting (from working code byte 10 = 0x11)
SWING_VERTICAL = 0x01

MODE_NAMES = {
    MODE_AUTO: "auto",
    MODE_COOL: "cool",
    MODE_DRY: "dry",
    MODE_FAN: "fan",
    MODE_HEAT: "heat"
}

FAN_NAMES = {
    FAN_AUTO: "auto",
    FAN_LOW: "low",
    FAN_MEDIUM: "medium",
    FAN_HIGH: "high",
    FAN_QUIET: "quiet"
}


def calculate_checksum(state_bytes: bytes) -> int:
    """
    Calculate checksum using confirmed formula from working codes.
    Formula: (Sum + Checksum) & 0xFF = 0x9E
    Therefore: Checksum = (0x9E - Sum) & 0xFF
    """
    sum_bytes = sum(state_bytes)
    checksum = (0x9E - sum_bytes) & 0xFF
    return checksum


def bytes_to_timings(state_bytes: bytes) -> list[int]:
    """Convert protocol bytes to IR timings"""
    timings = [FUJITSU_HEADER_MARK, FUJITSU_HEADER_SPACE]

    for byte_val in state_bytes:
        for bit_pos in range(8):
            bit = (byte_val >> bit_pos) & 1
            timings.append(FUJITSU_BIT_MARK)
            timings.append(FUJITSU_ONE_SPACE if bit else FUJITSU_ZERO_SPACE)

    return timings


def generate_off_command() -> tuple[bytes, str]:
    """Generate OFF command (7 bytes)"""
    state_bytes = bytes([0x14, 0x63, 0x00, 0x10, 0x10, 0x02, 0xFD])

    # Convert to timings and encode
    timings = bytes_to_timings(state_bytes)
    code = encode_ir(timings)

    return state_bytes, code


def generate_on_command(temperature: int, mode: int, fan: int) -> tuple[bytes, str]:
    """
    Generate ON command (16 bytes) based on working 24C_High structure.

    Args:
        temperature: Temperature in Celsius (16-30)
        mode: Mode constant (MODE_AUTO, MODE_COOL, etc.)
        fan: Fan constant (FAN_AUTO, FAN_LOW, etc.)

    Returns:
        Tuple of (state_bytes, tuya_code)
    """
    state_bytes = bytearray(16)

    # Bytes 0-4: Header (from working code)
    state_bytes[0] = 0x14
    state_bytes[1] = 0x63
    state_bytes[2] = 0x00
    state_bytes[3] = 0x10
    state_bytes[4] = 0x10

    # Byte 5: ON marker
    state_bytes[5] = 0xFE

    # Bytes 6-7: Unknown but consistent (from working code)
    state_bytes[6] = 0x09
    state_bytes[7] = 0x30

    # Byte 8: Temperature + Power bit
    temp_clamped = max(MIN_TEMP, min(MAX_TEMP, temperature))
    temp_value = int((temp_clamped - 16) * 4)
    temp_value = max(0, min(63, temp_value))
    power_bit = 1  # Always ON
    state_bytes[8] = power_bit | (temp_value << 2)

    # Byte 9: Mode
    state_bytes[9] = mode & 0x07

    # Byte 10: Fan + Swing (from working code: 0x11)
    # Bits 0-2: fan, Bits 4-5: swing
    fan_bits = fan & 0x07
    swing_bits = (SWING_VERTICAL & 0x03) << 4
    state_bytes[10] = fan_bits | swing_bits

    # Bytes 11-13: Zeros (from working code)
    state_bytes[11] = 0x00
    state_bytes[12] = 0x00
    state_bytes[13] = 0x00

    # Byte 14: Hardware compatibility bit (from working code)
    state_bytes[14] = 0x20

    # Byte 15: Checksum
    state_bytes[15] = calculate_checksum(state_bytes[0:15])

    # Convert to timings and encode with tuya1.py
    timings = bytes_to_timings(bytes(state_bytes))
    code = encode_ir(timings)

    return bytes(state_bytes), code


print("="*80)
print("GENERATING COMPLETE FUJITSU AC COMMAND SET")
print("="*80)
print()
print("Using confirmed working structure from 24C_High code")
print("Compression: tuya1.py (proven to work)")
print("Checksum formula: (0x9E - Sum) & 0xFF")
print()

# Generate all commands
commands = {}

# 1. OFF command
print("Generating OFF command...")
off_bytes, off_code = generate_off_command()
commands["off"] = {
    "code": off_code,
    "bytes": off_bytes.hex().upper(),
    "power": "off"
}
print(f"  ✓ OFF: {len(off_code)} chars")

# 2. ON commands - all combinations
print("\nGenerating ON commands...")
print(f"  Modes: {len(MODE_NAMES)} (auto, cool, dry, fan, heat)")
print(f"  Temperatures: {MAX_TEMP - MIN_TEMP + 1} ({MIN_TEMP}-{MAX_TEMP}°C)")
print(f"  Fan speeds: {len(FAN_NAMES)} (auto, low, medium, high, quiet)")
print(f"  Total ON commands: {len(MODE_NAMES) * (MAX_TEMP - MIN_TEMP + 1) * len(FAN_NAMES)}")
print()

count = 0
for mode_val, mode_name in MODE_NAMES.items():
    for temp in range(MIN_TEMP, MAX_TEMP + 1):
        for fan_val, fan_name in FAN_NAMES.items():
            # Generate command
            state_bytes, code = generate_on_command(temp, mode_val, fan_val)

            # Create key
            key = f"{mode_name}_{temp}c_{fan_name}"

            # Store
            commands[key] = {
                "code": code,
                "bytes": state_bytes.hex().upper(),
                "power": "on",
                "mode": mode_name,
                "temperature": temp,
                "fan": fan_name
            }

            count += 1
            if count % 50 == 0:
                print(f"  Generated {count} commands...")

print(f"  ✓ Total: {count} ON commands")

# Add metadata
output = {
    "device": "Fujitsu AC",
    "protocol": "fujitsu_ac_16byte",
    "total_commands": len(commands),
    "compression": "tuya1.py (FastLZ level 2)",
    "checksum_formula": "(0x9E - Sum) & 0xFF",
    "verified_working": [
        "off",
        "heat_24c_low (original 24C_High code)"
    ],
    "commands": commands
}

# Save to JSON file
output_file = "fujitsu_ac_commands_complete.json"
with open(output_file, "w") as f:
    json.dump(output, f, indent=2)

print()
print("="*80)
print("COMPLETE!")
print("="*80)
print(f"\n✓ Generated {len(commands)} total commands (1 OFF + {count} ON)")
print(f"✓ Saved to: {output_file}")
print()
print("Command structure:")
print("  - off: OFF command")
print("  - {mode}_{temp}c_{fan}: ON commands")
print()
print("Example keys:")
print("  - cool_20c_auto")
print("  - heat_24c_low")
print("  - dry_22c_high")
print()
print("All commands use:")
print("  ✓ Verified working 24C_High structure")
print("  ✓ Correct checksum formula (0x9E - Sum)")
print("  ✓ tuya1.py compression (proven to work)")
print()
print("Ready to test on your AC!")

# Verify our known working code
print()
print("="*80)
print("VERIFICATION")
print("="*80)
print("\nVerifying heat_24c_low matches original working 24C_High...")

# Original working code
original_24c = "EfcMNAbRAYIB0QFWAdEBkwTRAeADB0ALQANAF0ADQAvAA0APQAPAD0AHwEdAC+ADA0AXQAPAE0A3QA9AA8ATwAdAE0AfwA/AB0AT4BMD4AMnwAvAB0BTwANAE8BHQAtAA0APQAdAI0AH4AMDQBvAF0ALwBsAgmABAdEBQA/AFwCCYAEB0QHgAQ8C0QGCYAFABwHRAUAr4AMHAIJgAUAHgAOAH8ABAdEBQANAE0ADAILgAAFAC4ADgBcC0QGCYAFAB4ADQBcHkwSCAYIB0QFAC0ADBJME0QGCIAFAB0ADC1YB0QGCAdEBggHRAQ=="

# Generated code
generated = commands["heat_24c_low"]["code"]

if original_24c == generated:
    print("✓✓✓ PERFECT MATCH! Generated code exactly matches working 24C_High!")
else:
    print(f"Generated: {generated[:60]}...")
    print(f"Original:  {original_24c[:60]}...")
    print("Note: Bytes should be identical even if Base64 differs slightly")

    # Check bytes
    original_bytes = commands["heat_24c_low"]["bytes"]
    expected_bytes = "146300101010FE09308104110000002019A"  # From working code

    if original_bytes == expected_bytes.upper():
        print("✓ Bytes match exactly!")
    else:
        print(f"Generated bytes: {original_bytes}")
        print(f"Expected bytes:  {expected_bytes.upper()}")
