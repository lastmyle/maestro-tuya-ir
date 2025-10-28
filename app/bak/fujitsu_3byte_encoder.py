"""
Fujitsu AC IR code encoder - 3-byte repeating pattern variant.

This encoder is for Fujitsu AC units that use a 3-byte repeating pattern protocol.
Based on analysis of real Fujitsu AC IR codes (12 bytes = 4x repetitions of 3-byte pattern).

Protocol structure:
- 12 bytes total (3-byte pattern repeated 4 times)
- Byte 0: Power bit (bit 0) + Temperature encoding (bits 1-7)
- Byte 1: Temp LSB (bit 0) + Fan speed (bits 1-3) + Mode (bits 4-7)
- Byte 2: Checksum = ((byte1 & 0x0F) << 4) | (byte0 >> 4)

This is NOT the IRremoteESP8266 FUJITSU_AC protocol (which uses 16-byte state commands).
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
)

# Fujitsu 3-byte protocol constants
FUJITSU_HEADER_MARK = 3300
FUJITSU_HEADER_SPACE = 1600
FUJITSU_BIT_MARK = 600
FUJITSU_ZERO_SPACE = 540
FUJITSU_ONE_SPACE = 1600

# Mode encoding (upper nibble of byte 1)
MODE_MAP_3BYTE = {
    "cool": 0x1,
    "heat": 0x9,
    "dry": 0x5,
    "fan": 0xD,
    "auto": 0x1,  # Auto uses cool mode
}

# Fan speed encoding (bits 1-3 of byte 1)
FAN_MAP_3BYTE = {
    "auto": 0,
    "quiet": 0,  # Same as auto
    "medium": 1,
    "low": 2,
    "high": 3,
}

# Temperature encoding lookup (byte 0 bits 1-7)
# Maps (temp-16)//2 to the encoded value
TEMP_ENCODING_MAP = {
    2: 0x20,  # 20-21°C
    3: 0x60,  # 22-23°C
    4: 0x10,  # 24-25°C
    5: 0x50,  # 26-27°C
    6: 0x90,  # 28-29°C
    7: 0x30,  # 30°C
}


def calculate_checksum_3byte(byte0: int, byte1: int) -> int:
    """
    Calculate checksum for 3-byte Fujitsu protocol.

    Formula: Take lower nibble of byte1 as upper nibble of checksum,
             and upper nibble of byte0 as lower nibble of checksum.
    """
    checksum = ((byte1 & 0x0F) << 4) | (byte0 >> 4)
    return checksum


def encode_fujitsu_3byte_off() -> List[int]:
    """
    Encode Fujitsu OFF command (3-byte pattern repeated 4 times = 12 bytes).

    Returns real Fujitsu OFF command matching hardware behavior.
    """
    # OFF pattern: 0x20 0x00 0x02
    byte0 = 0x20  # Power bit = 0
    byte1 = 0x00  # No mode, no fan, no temp
    byte2 = calculate_checksum_3byte(byte0, byte1)

    # Repeat pattern 4 times
    state_bytes = [byte0, byte1, byte2] * 4

    # Convert to IR timings
    return bytes_to_ir_timings(state_bytes)


def encode_fujitsu_3byte_state(
    power: str = "on",
    mode: str = "cool",
    temperature: int = 24,
    fan: str = "auto",
    swing: str = "off",
) -> List[int]:
    """
    Encode Fujitsu AC state command (3-byte pattern repeated 4 times = 12 bytes).

    Args:
        power: "on" or "off"
        mode: "cool", "heat", "dry", "fan", "auto"
        temperature: 16-30°C
        fan: "auto", "low", "medium", "high", "quiet"
        swing: "off" (swing not supported in this protocol variant)

    Returns:
        IR timing array
    """
    # If power is off, use OFF command
    if power == "off":
        return encode_fujitsu_3byte_off()

    # Encode mode (upper nibble of byte 1)
    mode_val = MODE_MAP_3BYTE.get(mode.lower(), MODE_MAP_3BYTE["cool"])

    # Encode fan speed (bits 1-3 of byte 1)
    fan_val = FAN_MAP_3BYTE.get(fan.lower(), FAN_MAP_3BYTE["auto"])

    # Encode temperature
    # Clamp temperature to valid range
    temp_clamped = max(16, min(30, temperature))

    # Get temperature encoding
    temp_idx = (temp_clamped - 16) // 2
    if temp_idx not in TEMP_ENCODING_MAP:
        # Use closest valid temperature
        temp_idx = min(TEMP_ENCODING_MAP.keys(), key=lambda x: abs(x - temp_idx))

    temp_encoded = TEMP_ENCODING_MAP[temp_idx]
    temp_lsb = (temp_clamped - 16) & 0x01  # Odd/even bit

    # Build byte 0: power bit (bit 0) + temperature encoding + mode bits (bits 2-3)
    # Temperature encoding is stored in upper bits, shift left by 1
    # Mode bits 2-3 are also encoded in byte 0 bits 2-3
    byte0 = (temp_encoded << 1) | (mode_val & 0x0C) | 0x01  # Temp + mode bits + power bit

    # Build byte 1: temp LSB (bit 0) + fan (bits 1-3) + mode (bits 4-7)
    byte1 = temp_lsb | (fan_val << 1) | (mode_val << 4)

    # Calculate checksum
    byte2 = calculate_checksum_3byte(byte0, byte1)

    # Repeat pattern 4 times
    state_bytes = [byte0, byte1, byte2] * 4

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
    Convert Fujitsu 3-byte state to IR timing array.

    Uses space encoding:
    - Short space (~540μs) = 0
    - Long space (~1600μs) = 1
    - Marks are constant (~600μs)

    Args:
        state_bytes: Fujitsu state byte array (12 bytes)

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


def generate_fujitsu_3byte_command(
    power: str = "on",
    mode: str = "cool",
    temperature: int = 24,
    fan: str = "auto",
    swing: str = "off",
) -> List[int]:
    """
    Generate Fujitsu AC command as IR timings (3-byte protocol variant).

    Args:
        power: "on" or "off"
        mode: "cool", "heat", "dry", "fan", "auto"
        temperature: 16-30°C
        fan: "auto", "low", "medium", "high", "quiet"
        swing: "off" (not supported)

    Returns:
        IR timing array
    """
    return encode_fujitsu_3byte_state(power, mode, temperature, fan, swing)
