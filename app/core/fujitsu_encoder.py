"""
Fujitsu AC IR code encoder.

Creates proper Fujitsu HVAC IR commands that match real hardware.
Based on IRremoteESP8266 Fujitsu AC implementation.
"""

from typing import List

# Import constants from decoder
from app.core.ac_decoders import (
    FUJITSU_MODE_AUTO,
    FUJITSU_MODE_COOL,
    FUJITSU_MODE_DRY,
    FUJITSU_MODE_FAN,
    FUJITSU_MODE_HEAT,
    FUJITSU_FAN_AUTO,
    FUJITSU_FAN_HIGH,
    FUJITSU_FAN_LOW,
    FUJITSU_FAN_MED,
    FUJITSU_FAN_QUIET,
    FUJITSU_CMD_TURN_OFF,
    FUJITSU_MIN_TEMP_C,
    FUJITSU_MAX_TEMP_C,
)

# Fujitsu protocol constants
FUJITSU_HEADER_MARK = 3300
FUJITSU_HEADER_SPACE = 1600
FUJITSU_BIT_MARK = 400
FUJITSU_ZERO_SPACE = 400
FUJITSU_ONE_SPACE = 1200


def calculate_checksum(state_bytes: List[int]) -> int:
    """
    Calculate Fujitsu checksum.

    Formula: (sum of bytes + 0x64) & 0xFF
    The 0x64 constant is part of the Fujitsu protocol specification.
    """
    checksum = (sum(state_bytes) + 0x64) & 0xFF
    return checksum


def encode_fujitsu_off() -> List[int]:
    """
    Encode Fujitsu OFF command (7 bytes).

    Returns real Fujitsu OFF command matching hardware behavior.
    """
    # Create 7-byte OFF command
    state_bytes = [
        0x14,  # Byte 0: Header
        0x63,  # Byte 1: Header
        0x00,  # Byte 2: Length/type indicator
        0x10,  # Byte 3: Command type
        0x10,  # Byte 4: Command type
        0x02,  # Byte 5: OFF command
        0x00,  # Byte 6: Checksum (will be calculated)
    ]

    # Calculate and set checksum
    state_bytes[6] = calculate_checksum(state_bytes[:6])

    # Convert to IR timings
    return bytes_to_ir_timings(state_bytes)


def encode_fujitsu_state(
    power: str = "on",
    mode: str = "cool",
    temperature: int = 24,
    fan: str = "auto",
    swing: str = "off",
) -> List[int]:
    """
    Encode full Fujitsu AC state command (16 bytes).

    Args:
        power: "on" or "off"
        mode: "cool", "heat", "dry", "fan", "auto"
        temperature: 16-30°C
        fan: "auto", "low", "medium", "high", "quiet"
        swing: "off", "vertical", "horizontal", "both"

    Returns:
        IR timing array
    """
    # If power is off, use short OFF command
    if power == "off":
        return encode_fujitsu_off()

    # Create 16-byte state command
    state_bytes = [
        0x14,  # Byte 0: Header
        0x63,  # Byte 1: Header
        0x00,  # Byte 2: Length indicator
        0x10,  # Byte 3: Command type
        0x10,  # Byte 4: Command type
        0xFE,  # Byte 5: State command (0xFE = set state)
        0x09,  # Byte 6: Length
        0x30,  # Byte 7: Type
        0x00,  # Byte 8: Temperature + power bit
        0x00,  # Byte 9: Mode
        0x00,  # Byte 10: Fan + swing
        0x00,  # Byte 11: Extra
        0x00,  # Byte 12: Extra
        0x00,  # Byte 13: Extra
        0x00,  # Byte 14: Extra
        0x00,  # Byte 15: Checksum
    ]

    # Encode mode
    mode_map = {
        "auto": FUJITSU_MODE_AUTO,
        "cool": FUJITSU_MODE_COOL,
        "dry": FUJITSU_MODE_DRY,
        "fan": FUJITSU_MODE_FAN,
        "heat": FUJITSU_MODE_HEAT,
    }
    mode_val = mode_map.get(mode.lower(), FUJITSU_MODE_COOL)
    state_bytes[9] = mode_val & 0x07

    # Encode temperature
    # Temperature encoding: (temp - offset) * 2 - 1
    # Stored in byte 8 bits 0-6, with power bit in bit 7
    temp_clamped = max(FUJITSU_MIN_TEMP_C, min(FUJITSU_MAX_TEMP_C, temperature))
    temp_encoded = (temp_clamped - FUJITSU_MIN_TEMP_C) * 2 - 1
    if temp_encoded < 0:
        temp_encoded = 0
    state_bytes[8] = (temp_encoded & 0x7F) | 0x80  # Set power bit (bit 7)

    # Encode fan speed
    fan_map = {
        "auto": FUJITSU_FAN_AUTO,
        "low": FUJITSU_FAN_LOW,
        "medium": FUJITSU_FAN_MED,
        "high": FUJITSU_FAN_HIGH,
        "quiet": FUJITSU_FAN_QUIET,
    }
    fan_val = fan_map.get(fan.lower(), FUJITSU_FAN_AUTO)

    # Encode swing (simplified - just off for now)
    swing_val = 0x00  # Off

    # Combine fan and swing in byte 10
    state_bytes[10] = (fan_val & 0x07) | ((swing_val & 0x03) << 4)

    # Calculate and set checksum
    state_bytes[15] = calculate_checksum(state_bytes[:15])

    # Convert to IR timings
    return bytes_to_ir_timings(state_bytes)


def bytes_to_bits(state_bytes: List[int]) -> List[int]:
    """
    Convert byte array to bit array (LSB first per byte).

    Args:
        state_bytes: List of bytes

    Returns:
        List of bits (0s and 1s)
    """
    bits = []
    for byte_val in state_bytes:
        # Extract bits LSB first
        for i in range(8):
            bit = (byte_val >> i) & 0x01
            bits.append(bit)
    return bits


def bytes_to_ir_timings(state_bytes: List[int]) -> List[int]:
    """
    Convert Fujitsu state bytes to IR timing array.

    Uses space encoding:
    - Short space (~400μs) = 0
    - Long space (~1200μs) = 1
    - Marks are constant (~400μs)

    Args:
        state_bytes: Fujitsu state byte array

    Returns:
        IR timing array (microseconds)
    """
    timings = []

    # Add header
    timings.append(FUJITSU_HEADER_MARK)
    timings.append(FUJITSU_HEADER_SPACE)

    # Convert bytes to bits (LSB first per byte)
    bits = bytes_to_bits(state_bytes)

    # Encode each bit as mark + space
    for bit in bits:
        timings.append(FUJITSU_BIT_MARK)
        if bit == 1:
            timings.append(FUJITSU_ONE_SPACE)
        else:
            timings.append(FUJITSU_ZERO_SPACE)

    # Add footer mark
    timings.append(FUJITSU_BIT_MARK)

    return timings


def generate_fujitsu_command(
    power: str = "on",
    mode: str = "cool",
    temperature: int = 24,
    fan: str = "auto",
    swing: str = "off",
) -> List[int]:
    """
    Generate Fujitsu AC command as IR timings.

    Args:
        power: "on" or "off"
        mode: "cool", "heat", "dry", "fan", "auto"
        temperature: 16-30°C
        fan: "auto", "low", "medium", "high", "quiet"
        swing: "off" (others not yet implemented)

    Returns:
        IR timing array
    """
    return encode_fujitsu_state(power, mode, temperature, fan, swing)
