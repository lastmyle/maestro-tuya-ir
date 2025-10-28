"""
Multi-manufacturer AC protocol decoders.

Based on IRremoteESP8266 implementations:
https://github.com/crankyoldgit/IRremoteESP8266/tree/master/src
"""

from typing import List, Dict, Any


# Common helper functions
def timings_to_bits_space_encoding(timings: List[int], threshold: int = 700) -> List[int]:
    """
    Convert IR timings to bits using space encoding.

    Space encoding: Short space = 0, Long space = 1
    (Marks are constant)

    Args:
        timings: Raw IR timing array (mark, space, mark, space, ...)
        threshold: Threshold to distinguish short vs long spaces (microseconds)

    Returns:
        List of bits (0s and 1s)
    """
    if len(timings) < 4:
        return []

    bits = []
    # Start at index 3 (first space after header mark/space)
    for i in range(3, len(timings), 2):
        space = timings[i]
        bit = 1 if space > threshold else 0
        bits.append(bit)

    return bits


def bits_to_bytes(bits: List[int]) -> List[int]:
    """
    Convert bit array to byte array (LSB first per byte).

    Args:
        bits: List of bits (0s and 1s)

    Returns:
        List of bytes
    """
    bytes_arr = []

    for i in range(0, len(bits), 8):
        byte_bits = bits[i:i+8]
        if len(byte_bits) < 8:
            byte_bits.extend([0] * (8 - len(byte_bits)))

        # Convert to byte (LSB first)
        byte_val = 0
        for j, bit in enumerate(byte_bits):
            byte_val |= (bit << j)

        bytes_arr.append(byte_val)

    return bytes_arr


def unknown_state() -> Dict[str, Any]:
    """Return unknown/undecodable state."""
    return {
        "power": "unknown",
        "mode": "unknown",
        "temperature": None,
        "fan": "unknown",
        "swing": "unknown",
    }


# ============================================================================
# FUJITSU AC DECODER
# ============================================================================

# Fujitsu mode constants (from IRremoteESP8266)
FUJITSU_MODE_AUTO = 0x0  # 0b000
FUJITSU_MODE_COOL = 0x1  # 0b001
FUJITSU_MODE_DRY = 0x2   # 0b010
FUJITSU_MODE_FAN = 0x3   # 0b011
FUJITSU_MODE_HEAT = 0x4  # 0b100

FUJITSU_MODE_MAP = {
    FUJITSU_MODE_AUTO: "auto",
    FUJITSU_MODE_COOL: "cool",
    FUJITSU_MODE_DRY: "dry",
    FUJITSU_MODE_FAN: "fan",
    FUJITSU_MODE_HEAT: "heat",
}

# Fujitsu fan speed constants (from IRremoteESP8266)
FUJITSU_FAN_AUTO = 0x0   # kFujitsuAcFanAuto
FUJITSU_FAN_HIGH = 0x1   # kFujitsuAcFanHigh
FUJITSU_FAN_MED = 0x2    # kFujitsuAcFanMed
FUJITSU_FAN_LOW = 0x3    # kFujitsuAcFanLow
FUJITSU_FAN_QUIET = 0x4  # kFujitsuAcFanQuiet

FUJITSU_FAN_MAP = {
    FUJITSU_FAN_AUTO: "auto",
    FUJITSU_FAN_HIGH: "high",
    FUJITSU_FAN_MED: "medium",
    FUJITSU_FAN_LOW: "low",
    FUJITSU_FAN_QUIET: "quiet",
}

# Fujitsu swing constants (from IRremoteESP8266)
FUJITSU_SWING_OFF = 0x0     # kFujitsuAcSwingOff
FUJITSU_SWING_VERT = 0x1    # kFujitsuAcSwingVert
FUJITSU_SWING_HORIZ = 0x2   # kFujitsuAcSwingHoriz
FUJITSU_SWING_BOTH = 0x3    # kFujitsuAcSwingBoth

FUJITSU_SWING_MAP = {
    FUJITSU_SWING_OFF: "off",
    FUJITSU_SWING_VERT: "vertical",
    FUJITSU_SWING_HORIZ: "horizontal",
    FUJITSU_SWING_BOTH: "both",
}

# Fujitsu temperature constants
FUJITSU_MIN_TEMP_C = 16
FUJITSU_MAX_TEMP_C = 30

# Fujitsu command constants
FUJITSU_CMD_TURN_OFF = 0x02


def decode_fujitsu_ac_state(state_bytes: List[int]) -> Dict[str, Any]:
    """
    Decode Fujitsu AC state from byte array.

    Supports two variants:
    1. 3-byte repeating pattern (12 bytes total = 4 repetitions)
       - Byte 0: Power (bit 0) + Mode (bits 2-3) + Temperature (bits 1,4-7)
       - Byte 1: Temp LSB (bit 0) + Fan (bits 1-3) + Mode (bits 4-7)
       - Byte 2: Checksum
    2. 16-byte IRremoteESP8266 format
       - Byte 0-1: Header (0x14, 0x63)
       - Byte 5: Command
       - Byte 8: Power/Temperature
       - Byte 9: Mode
       - Byte 10: Fan/Swing

    Args:
        state_bytes: State byte array

    Returns:
        Dictionary with power, mode, temperature, fan, swing
    """
    if len(state_bytes) < 3:
        return unknown_state()

    # VARIANT 1: 3-byte repeating pattern (12 bytes)
    if len(state_bytes) == 12:
        # Decode first 3-byte pattern (pattern repeats 4 times for redundancy)
        byte0 = state_bytes[0]
        byte1 = state_bytes[1]
        byte2 = state_bytes[2]

        # Check if it's OFF command (byte0 bit 0 = 0)
        if (byte0 & 0x01) == 0:
            return {
                "power": "off",
                "mode": "unknown",
                "temperature": None,
                "fan": "unknown",
                "swing": "unknown",
            }

        # Power is ON
        # Extract mode from byte1 bits 4-7
        mode_val = (byte1 >> 4) & 0x0F
        mode_map_3byte = {
            0x1: "cool",
            0x9: "heat",
            0x5: "dry",
            0xD: "fan",
        }
        mode = mode_map_3byte.get(mode_val, "unknown")

        # Extract temperature
        # Temp MSB from byte0 bits 1,4-7 (shifted right by 1)
        temp_msb = byte0 >> 1
        # Temp LSB from byte1 bit 0
        temp_lsb = byte1 & 0x01

        # Decode temperature from lookup (simplified)
        # This is complex, so we use a reverse lookup
        temp_encoding_reverse = {
            0x20: 20, 0x21: 21,  # 0x41 >> 1 = 0x20
            0x60: 22, 0x61: 23,  # 0xC1 >> 1 = 0x60
            0x10: 24, 0x11: 25,  # 0x21 >> 1 = 0x10
            0x50: 26, 0x51: 27,  # 0xA1 >> 1 = 0x50
            0x48: 28, 0x49: 29,  # 0x91 >> 1 = 0x48
            0x18: 30,            # 0x31 >> 1 = 0x18
        }
        temp_key = temp_msb | temp_lsb
        temperature = temp_encoding_reverse.get(temp_key, 24)

        # Extract fan from byte1 bits 1-3
        fan_val = (byte1 >> 1) & 0x07
        fan_map_3byte = {
            0: "auto",
            1: "medium",
            2: "low",
            3: "high",
        }
        fan = fan_map_3byte.get(fan_val, "unknown")

        return {
            "power": "on",
            "mode": mode,
            "temperature": temperature,
            "fan": fan,
            "swing": "off",  # Not supported in 3-byte variant
        }

    # VARIANT 2: IRremoteESP8266 format (16-byte or 7-byte OFF command)
    # Translated directly from https://github.com/crankyoldgit/IRremoteESP8266
    if len(state_bytes) < 6:
        return unknown_state()

    # Check for short OFF command (7 bytes with cmd byte = 0x02)
    if len(state_bytes) >= 6 and state_bytes[5] == FUJITSU_CMD_TURN_OFF:
        return {
            "power": "off",
            "mode": "unknown",
            "temperature": None,
            "fan": "unknown",
            "swing": "unknown",
        }

    # Full format requires at least 11 bytes
    if len(state_bytes) < 11:
        return unknown_state()

    # Byte 8: Power (bit 0), Fahrenheit (bit 1), Temp (bits 2-7)
    # From IRremoteESP8266: uint64_t Power:1; uint64_t Fahrenheit:1; uint64_t Temp:6;
    byte_8 = state_bytes[8]
    power_bit = byte_8 & 0x01  # Bit 0
    temp_raw = (byte_8 >> 2) & 0x3F  # Bits 2-7 (6 bits)

    power = "on" if power_bit else "off"

    # Temperature calculation from IRremoteESP8266: Temp / 4 + kFujitsuAcMinTemp
    # (For non-ARREW4E models, which is the standard 16-byte format)
    temperature = None
    if temp_raw > 0:
        temperature = temp_raw / 4.0 + FUJITSU_MIN_TEMP_C
        # Clamp to valid range
        if temperature < FUJITSU_MIN_TEMP_C:
            temperature = FUJITSU_MIN_TEMP_C
        elif temperature > FUJITSU_MAX_TEMP_C:
            temperature = FUJITSU_MAX_TEMP_C
        # Round to nearest 0.5
        temperature = round(temperature * 2) / 2

    # Byte 9: Mode (bits 0-2), Clean (bit 3), TimerType (bits 4-5)
    # From IRremoteESP8266: uint64_t Mode:3;
    byte_9 = state_bytes[9]
    mode_val = byte_9 & 0x07  # Bits 0-2 (3 bits)
    mode = FUJITSU_MODE_MAP.get(mode_val, "unknown")

    # Byte 10: Fan (bits 0-2), unused (bit 3), Swing (bits 4-5)
    # From IRremoteESP8266: uint64_t Fan:3; skip 1; uint64_t Swing:2;
    byte_10 = state_bytes[10]
    fan_val = byte_10 & 0x07  # Bits 0-2 (3 bits)
    swing_val = (byte_10 >> 4) & 0x03  # Bits 4-5 (2 bits)

    fan = FUJITSU_FAN_MAP.get(fan_val, "unknown")
    swing = FUJITSU_SWING_MAP.get(swing_val, "unknown")

    return {
        "power": power,
        "mode": mode,
        "temperature": temperature,
        "fan": fan,
        "swing": swing,
    }


def decode_fujitsu_ac(timings: List[int]) -> Dict[str, Any]:
    """
    Decode Fujitsu AC IR signal from raw timings.

    Fujitsu AC uses SPACE encoding (not mark encoding):
    - Short space (~400μs) = 0
    - Long space (~1200μs) = 1
    Marks are constant (~400μs)

    Args:
        timings: Raw IR timing array

    Returns:
        Dictionary with decoded AC state
    """
    # Convert timings to bits using space encoding
    bits = timings_to_bits_space_encoding(timings, threshold=700)

    if not bits:
        return unknown_state()

    # Convert bits to bytes
    state_bytes = bits_to_bytes(bits)

    # Decode state
    return decode_fujitsu_ac_state(state_bytes)


# ============================================================================
# DAIKIN AC DECODER
# ============================================================================

# Daikin mode constants
DAIKIN_MODE_AUTO = 0x0
DAIKIN_MODE_DRY = 0x2
DAIKIN_MODE_COOL = 0x3
DAIKIN_MODE_HEAT = 0x4
DAIKIN_MODE_FAN = 0x6

DAIKIN_MODE_MAP = {
    DAIKIN_MODE_AUTO: "auto",
    DAIKIN_MODE_DRY: "dry",
    DAIKIN_MODE_COOL: "cool",
    DAIKIN_MODE_HEAT: "heat",
    DAIKIN_MODE_FAN: "fan",
}

# Daikin fan constants
DAIKIN_FAN_AUTO = 0xA
DAIKIN_FAN_QUIET = 0xB
DAIKIN_FAN_MAP = {
    0xA: "auto",
    0xB: "quiet",
    3: "low",      # Stored as 2 + 1
    4: "medium",   # Stored as 2 + 2
    5: "med-high", # Stored as 2 + 3
    6: "high",     # Stored as 2 + 4
    7: "max",      # Stored as 2 + 5
}


def decode_daikin_ac(timings: List[int]) -> Dict[str, Any]:
    """
    Decode Daikin AC IR signal.

    35 bytes total in 3 sections
    - Byte 13: Power (bit 0), Mode (bits 4-6)
    - Byte 14: Temperature (temp * 2)
    - Byte 16: Fan speed
    """
    bits = timings_to_bits_space_encoding(timings, threshold=850)

    if len(bits) < 280:  # 35 bytes * 8
        return unknown_state()

    state_bytes = bits_to_bytes(bits)

    if len(state_bytes) < 17:
        return unknown_state()

    # Byte 13: Power and Mode
    byte_13 = state_bytes[13]
    power = "on" if (byte_13 & 0x01) else "off"
    mode_val = (byte_13 >> 4) & 0x07
    mode = DAIKIN_MODE_MAP.get(mode_val, "unknown")

    # Byte 14: Temperature (stored as temp * 2)
    temp_raw = state_bytes[14]
    temperature = None
    if temp_raw > 0:
        temperature = int(temp_raw / 2.0)
        if temperature < 10:
            temperature = 10
        elif temperature > 32:
            temperature = 32

    # Byte 16: Fan speed
    fan_raw = state_bytes[16]
    fan = DAIKIN_FAN_MAP.get(fan_raw, "unknown")
    if fan == "unknown" and fan_raw >= 3:
        fan = DAIKIN_FAN_MAP.get(fan_raw, f"level-{fan_raw-2}")

    # Swing: Daikin uses byte 27-28 for swing modes (complex)
    # Simplified: check byte 28 bit 4
    swing = "unknown"
    if len(state_bytes) > 28:
        swing_byte = state_bytes[28]
        swing = "on" if (swing_byte & 0x0F) == 0x0F else "off"

    return {
        "power": power,
        "mode": mode,
        "temperature": temperature,
        "fan": fan,
        "swing": swing,
    }


# ============================================================================
# MITSUBISHI AC DECODER
# ============================================================================

# Mitsubishi mode constants
MITSU_MODE_AUTO = 0x4
MITSU_MODE_COOL = 0x3
MITSU_MODE_DRY = 0x2
MITSU_MODE_HEAT = 0x1
MITSU_MODE_FAN = 0x7

MITSU_MODE_MAP = {
    MITSU_MODE_AUTO: "auto",
    MITSU_MODE_COOL: "cool",
    MITSU_MODE_DRY: "dry",
    MITSU_MODE_HEAT: "heat",
    MITSU_MODE_FAN: "fan",
}

# Mitsubishi fan constants
MITSU_FAN_MAP = {
    0: "auto",
    1: "low",
    2: "medium-low",
    3: "medium",
    4: "medium-high",
    5: "high",
    6: "silent",
}

# Mitsubishi vane (swing) constants
MITSU_VANE_MAP = {
    0x0: "auto",
    0x1: "highest",
    0x2: "high",
    0x3: "middle",
    0x4: "low",
    0x5: "lowest",
    0x7: "swing",
}


def decode_mitsubishi_ac(timings: List[int]) -> Dict[str, Any]:
    """
    Decode Mitsubishi AC IR signal.

    18 bytes (144 bits)
    - Byte 5: Power (bit 5)
    - Byte 6: Mode (bits 0-2)
    - Byte 7: Temperature (bits 0-3) + HalfDegree (bit 4)
    - Byte 9: Fan (bits 0-2), Vane (bits 3-5), FanAuto (bit 7)
    """
    bits = timings_to_bits_space_encoding(timings, threshold=850)

    if len(bits) < 144:  # 18 bytes * 8
        return unknown_state()

    state_bytes = bits_to_bytes(bits)

    if len(state_bytes) < 10:
        return unknown_state()

    # Check signature: bytes 0-2 should be 0x23, 0xCB, 0x26
    if state_bytes[0] != 0x23 or state_bytes[1] != 0xCB or state_bytes[2] != 0x26:
        return unknown_state()

    # Byte 5: Power (bit 5)
    power = "on" if (state_bytes[5] & 0x20) else "off"

    # Byte 6: Mode (bits 0-2)
    mode_val = state_bytes[6] & 0x07
    mode = MITSU_MODE_MAP.get(mode_val, "unknown")

    # Byte 7: Temperature with 0.5°C precision
    temp_byte = state_bytes[7]
    temp_offset = temp_byte & 0x0F  # Bits 0-3
    half_degree = (temp_byte >> 4) & 0x01  # Bit 4
    temperature = (temp_offset + 16) + (half_degree * 0.5)
    if temperature < 16:
        temperature = 16
    elif temperature > 31:
        temperature = 31

    # Byte 9: Fan and Vane
    byte_9 = state_bytes[9]
    fan_val = byte_9 & 0x07  # Bits 0-2
    vane_val = (byte_9 >> 3) & 0x07  # Bits 3-5
    fan_auto_bit = (byte_9 >> 7) & 0x01  # Bit 7

    if fan_auto_bit:
        fan = "auto"
    else:
        fan = MITSU_FAN_MAP.get(fan_val, "unknown")

    swing = MITSU_VANE_MAP.get(vane_val, "unknown")

    return {
        "power": power,
        "mode": mode,
        "temperature": temperature,
        "fan": fan,
        "swing": swing,
    }


# ============================================================================
# PANASONIC AC DECODER
# ============================================================================

# Panasonic mode constants
PANA_MODE_AUTO = 0x0
PANA_MODE_DRY = 0x2
PANA_MODE_COOL = 0x3
PANA_MODE_HEAT = 0x4
PANA_MODE_FAN = 0x6

PANA_MODE_MAP = {
    PANA_MODE_AUTO: "auto",
    PANA_MODE_DRY: "dry",
    PANA_MODE_COOL: "cool",
    PANA_MODE_HEAT: "heat",
    PANA_MODE_FAN: "fan",
}

# Panasonic fan constants (stored with +3 offset)
PANA_FAN_DELTA = 3
PANA_FAN_MAP = {
    0: "min",
    1: "low",
    2: "medium",
    3: "high",
    4: "max",
    7: "auto",
}


def get_bits(byte_val: int, bit_offset: int, num_bits: int) -> int:
    """Extract bits from a byte."""
    mask = (1 << num_bits) - 1
    return (byte_val >> bit_offset) & mask


def decode_panasonic_ac(timings: List[int]) -> Dict[str, Any]:
    """
    Decode Panasonic AC IR signal.

    27 bytes (216 bits)
    - Byte 13: Power (bit 0), Mode (bits 4-7)
    - Byte 14: Temperature (5 bits at offset 1)
    - Byte 16: Fan (bits 4-7), Swing V (bits 0-3)
    """
    bits = timings_to_bits_space_encoding(timings, threshold=850)

    if len(bits) < 216:  # 27 bytes * 8
        return unknown_state()

    state_bytes = bits_to_bytes(bits)

    if len(state_bytes) < 17:
        return unknown_state()

    # Byte 13: Power and Mode
    byte_13 = state_bytes[13]
    power = "on" if (byte_13 & 0x01) else "off"
    mode_val = (byte_13 >> 4) & 0x0F
    mode = PANA_MODE_MAP.get(mode_val, "unknown")

    # Byte 14: Temperature (5 bits at bit offset 1)
    temperature = get_bits(state_bytes[14], 1, 5)
    if temperature < 16:
        temperature = 16
    elif temperature > 30:
        temperature = 30

    # Byte 16: Fan and Swing
    byte_16 = state_bytes[16]
    fan_raw = (byte_16 >> 4) & 0x0F
    fan_val = fan_raw - PANA_FAN_DELTA if fan_raw >= PANA_FAN_DELTA else fan_raw
    fan = PANA_FAN_MAP.get(fan_val, "unknown")

    swing_v = byte_16 & 0x0F
    if swing_v == 0xF:
        swing = "auto"
    elif swing_v >= 0x1 and swing_v <= 0x5:
        swing = f"position-{swing_v}"
    else:
        swing = "unknown"

    return {
        "power": power,
        "mode": mode,
        "temperature": temperature,
        "fan": fan,
        "swing": swing,
    }


# ============================================================================
# SAMSUNG AC DECODER
# ============================================================================

# Samsung mode constants
SAMSUNG_MODE_AUTO = 0
SAMSUNG_MODE_COOL = 1
SAMSUNG_MODE_DRY = 2
SAMSUNG_MODE_FAN = 3
SAMSUNG_MODE_HEAT = 4

SAMSUNG_MODE_MAP = {
    SAMSUNG_MODE_AUTO: "auto",
    SAMSUNG_MODE_COOL: "cool",
    SAMSUNG_MODE_DRY: "dry",
    SAMSUNG_MODE_FAN: "fan",
    SAMSUNG_MODE_HEAT: "heat",
}

# Samsung fan constants
SAMSUNG_FAN_MAP = {
    0: "auto",
    2: "low",
    4: "medium",
    5: "high",
    6: "auto",
    7: "turbo",
}

# Samsung swing constants
SAMSUNG_SWING_MAP = {
    0x7: "off",
    0x2: "vertical",
    0x3: "horizontal",
    0x4: "both",
}


def decode_samsung_ac(timings: List[int]) -> Dict[str, Any]:
    """
    Decode Samsung AC IR signal.

    14 bytes (112 bits) standard message
    - Byte 6: Power (bits 0-1)
    - Byte 11: Temperature (bits 2-5)
    - Byte 12: Fan (bits 0-2), Mode (bits 3-5)
    - Byte 9: Swing (bits 0-2)
    """
    bits = timings_to_bits_space_encoding(timings, threshold=850)

    if len(bits) < 112:  # 14 bytes * 8
        return unknown_state()

    state_bytes = bits_to_bytes(bits)

    if len(state_bytes) < 14:
        return unknown_state()

    # Check signature: state[0] == 0x02, state[2] == 0x0F
    if state_bytes[0] != 0x02 or state_bytes[2] != 0x0F:
        return unknown_state()

    # Byte 6: Power (bits 0-1)
    power_bits = state_bytes[6] & 0x03
    power = "on" if power_bits == 0x01 else "off"

    # Also check byte 13 power bits
    power_bits_2 = (state_bytes[13] >> 1) & 0x03
    if power_bits_2 == 0x02:
        power = "off"

    # Byte 11: Temperature (bits 2-5)
    temp_offset = (state_bytes[11] >> 2) & 0x0F
    temperature = temp_offset + 16
    if temperature < 16:
        temperature = 16
    elif temperature > 30:
        temperature = 30

    # Byte 12: Fan and Mode
    byte_12 = state_bytes[12]
    fan_val = byte_12 & 0x07
    mode_val = (byte_12 >> 3) & 0x07

    fan = SAMSUNG_FAN_MAP.get(fan_val, "unknown")
    mode = SAMSUNG_MODE_MAP.get(mode_val, "unknown")

    # Byte 9: Swing
    swing_val = state_bytes[9] & 0x07
    swing = SAMSUNG_SWING_MAP.get(swing_val, "unknown")

    return {
        "power": power,
        "mode": mode,
        "temperature": temperature,
        "fan": fan,
        "swing": swing,
    }


# ============================================================================
# LG AC DECODER
# ============================================================================

# LG mode constants
LG_MODE_COOL = 0
LG_MODE_DRY = 1
LG_MODE_FAN = 2
LG_MODE_AUTO = 3
LG_MODE_HEAT = 4

LG_MODE_MAP = {
    LG_MODE_COOL: "cool",
    LG_MODE_DRY: "dry",
    LG_MODE_FAN: "fan",
    LG_MODE_AUTO: "auto",
    LG_MODE_HEAT: "heat",
}

# LG fan constants
LG_FAN_MAP = {
    0: "lowest",
    1: "low",
    2: "medium",
    4: "max",
    5: "auto",
    9: "low",
    10: "high",
}

LG_TEMP_ADJUST = 15


def decode_lg_ac(timings: List[int]) -> Dict[str, Any]:
    """
    Decode LG AC IR signal.

    LG uses a 32-bit protocol (4 bytes):
    - Bits 0-3: Checksum
    - Bits 4-7: Fan
    - Bits 8-11: Temperature
    - Bits 12-14: Mode
    - Bits 18-19: Power
    - Bits 20-27: Signature (0x88)
    """
    bits = timings_to_bits_space_encoding(timings, threshold=850)

    if len(bits) < 28:  # 28 bits minimum
        return unknown_state()

    # Convert to 32-bit value (LSB first per byte, then byte order)
    state_bytes = bits_to_bytes(bits)

    if len(state_bytes) < 4:
        return unknown_state()

    # Reconstruct 32-bit value (little-endian)
    raw_value = (state_bytes[0] | (state_bytes[1] << 8) |
                 (state_bytes[2] << 16) | (state_bytes[3] << 24))

    # Check signature (bits 20-27 should be 0x88)
    signature = (raw_value >> 20) & 0xFF
    if signature != 0x88:
        return unknown_state()

    # Extract fields
    fan_val = (raw_value >> 4) & 0x0F
    temp_val = (raw_value >> 8) & 0x0F
    mode_val = (raw_value >> 12) & 0x07
    power_val = (raw_value >> 18) & 0x03

    # Decode values
    power = "off" if power_val == 3 else "on"
    mode = LG_MODE_MAP.get(mode_val, "unknown")
    temperature = temp_val + LG_TEMP_ADJUST
    if temperature < 16:
        temperature = 16
    elif temperature > 30:
        temperature = 30

    fan = LG_FAN_MAP.get(fan_val, "unknown")

    return {
        "power": power,
        "mode": mode,
        "temperature": temperature,
        "fan": fan,
        "swing": "unknown",  # LG swing is separate command
    }


# ============================================================================
# CARRIER AC DECODER
# ============================================================================

# Carrier mode constants
CARRIER_MODE_AUTO = 0x0
CARRIER_MODE_COOL = 0x1
CARRIER_MODE_HEAT = 0x2
CARRIER_MODE_DRY = 0x3
CARRIER_MODE_FAN = 0x4

CARRIER_MODE_MAP = {
    CARRIER_MODE_AUTO: "auto",
    CARRIER_MODE_COOL: "cool",
    CARRIER_MODE_HEAT: "heat",
    CARRIER_MODE_DRY: "dry",
    CARRIER_MODE_FAN: "fan",
}

# Carrier fan constants
CARRIER_FAN_MAP = {
    0: "auto",
    1: "low",
    2: "medium",
    3: "high",
}


def decode_carrier_ac(timings: List[int]) -> Dict[str, Any]:
    """
    Decode Carrier AC IR signal.

    8 bytes (64 bits)
    - Byte 1: Mode (bits 4-6)
    - Byte 2: Temperature (bits 0-3)
    - Byte 3: Fan speed (bits 0-1), Power (bit 4)
    - Byte 4: Swing (bit 0)
    """
    bits = timings_to_bits_space_encoding(timings, threshold=850)

    if len(bits) < 64:  # 8 bytes * 8
        return unknown_state()

    state_bytes = bits_to_bytes(bits)

    if len(state_bytes) < 5:
        return unknown_state()

    # Byte 3: Power (bit 4)
    power = "on" if (state_bytes[3] & 0x10) else "off"

    # Byte 1: Mode (bits 4-6)
    mode_val = (state_bytes[1] >> 4) & 0x07
    mode = CARRIER_MODE_MAP.get(mode_val, "unknown")

    # Byte 2: Temperature (bits 0-3) + 17
    temp_offset = state_bytes[2] & 0x0F
    temperature = temp_offset + 17
    if temperature < 17:
        temperature = 17
    elif temperature > 30:
        temperature = 30

    # Byte 3: Fan speed (bits 0-1)
    fan_val = state_bytes[3] & 0x03
    fan = CARRIER_FAN_MAP.get(fan_val, "unknown")

    # Byte 4: Swing (bit 0)
    swing = "on" if (state_bytes[4] & 0x01) else "off"

    return {
        "power": power,
        "mode": mode,
        "temperature": temperature,
        "fan": fan,
        "swing": swing,
    }


# ============================================================================
# HAIER AC DECODER
# ============================================================================

# Haier mode constants
HAIER_MODE_AUTO = 0x0
HAIER_MODE_COOL = 0x1
HAIER_MODE_DRY = 0x2
HAIER_MODE_HEAT = 0x3
HAIER_MODE_FAN = 0x4

HAIER_MODE_MAP = {
    HAIER_MODE_AUTO: "auto",
    HAIER_MODE_COOL: "cool",
    HAIER_MODE_DRY: "dry",
    HAIER_MODE_HEAT: "heat",
    HAIER_MODE_FAN: "fan",
}

# Haier fan constants
HAIER_FAN_MAP = {
    0: "auto",
    1: "low",
    2: "medium",
    3: "high",
}


def decode_haier_ac(timings: List[int]) -> Dict[str, Any]:
    """
    Decode Haier AC IR signal.

    9 bytes (72 bits)
    - Byte 1: Temperature (bits 0-4)
    - Byte 5: Mode (bits 5-7), Power (bit 2)
    - Byte 3: Fan speed (bits 5-6)
    - Byte 7: Swing (bit 2)
    """
    bits = timings_to_bits_space_encoding(timings, threshold=850)

    if len(bits) < 72:  # 9 bytes * 8
        return unknown_state()

    state_bytes = bits_to_bytes(bits)

    if len(state_bytes) < 8:
        return unknown_state()

    # Byte 5: Power (bit 2)
    power = "on" if (state_bytes[5] & 0x04) else "off"

    # Byte 5: Mode (bits 5-7)
    mode_val = (state_bytes[5] >> 5) & 0x07
    mode = HAIER_MODE_MAP.get(mode_val, "unknown")

    # Byte 1: Temperature (bits 0-4)
    temp_offset = state_bytes[1] & 0x1F
    temperature = temp_offset + 16
    if temperature < 16:
        temperature = 16
    elif temperature > 30:
        temperature = 30

    # Byte 3: Fan speed (bits 5-6)
    fan_val = (state_bytes[3] >> 5) & 0x03
    fan = HAIER_FAN_MAP.get(fan_val, "unknown")

    # Byte 7: Swing (bit 2)
    swing = "on" if (state_bytes[7] & 0x04) else "off"

    return {
        "power": power,
        "mode": mode,
        "temperature": temperature,
        "fan": fan,
        "swing": swing,
    }


# ============================================================================
# HITACHI AC DECODERS
# ============================================================================

# Hitachi mode constants
HITACHI_MODE_AUTO = 0x2
HITACHI_MODE_COOL = 0x3
HITACHI_MODE_DRY = 0x5
HITACHI_MODE_FAN = 0xC
HITACHI_MODE_HEAT = 0x1

HITACHI_MODE_MAP = {
    HITACHI_MODE_AUTO: "auto",
    HITACHI_MODE_COOL: "cool",
    HITACHI_MODE_DRY: "dry",
    HITACHI_MODE_FAN: "fan",
    HITACHI_MODE_HEAT: "heat",
}

# Hitachi fan constants
HITACHI_FAN_MAP = {
    1: "auto",
    2: "low",
    3: "medium",
    4: "high",
    5: "max",
}


def reverse_bits(byte_val: int) -> int:
    """Reverse bits in a byte."""
    result = 0
    for i in range(8):
        result = (result << 1) | ((byte_val >> i) & 1)
    return result


def decode_hitachi_ac(timings: List[int]) -> Dict[str, Any]:
    """
    Decode Hitachi AC IR signal (28 bytes).

    28 bytes (224 bits) - bit-reversed
    - Byte 13: Power (bit 0)
    - Byte 11: Mode (bits 4-7)
    - Byte 13: Temperature (bits 1-5)
    - Byte 15: Fan speed (bits 0-3)
    - Byte 15: Swing (bit 6)
    """
    bits = timings_to_bits_space_encoding(timings, threshold=850)

    if len(bits) < 224:  # 28 bytes * 8
        return unknown_state()

    state_bytes = bits_to_bytes(bits)

    if len(state_bytes) < 16:
        return unknown_state()

    # Hitachi uses bit-reversed bytes
    state_bytes = [reverse_bits(b) for b in state_bytes]

    # Byte 13: Power (bit 0)
    power = "on" if (state_bytes[13] & 0x01) else "off"

    # Byte 11: Mode (bits 4-7)
    mode_val = (state_bytes[11] >> 4) & 0x0F
    mode = HITACHI_MODE_MAP.get(mode_val, "unknown")

    # Byte 13: Temperature (bits 1-5)
    temp_offset = (state_bytes[13] >> 1) & 0x1F
    temperature = temp_offset + 16
    if temperature < 16:
        temperature = 16
    elif temperature > 32:
        temperature = 32

    # Byte 15: Fan speed (bits 0-3)
    fan_val = state_bytes[15] & 0x0F
    fan = HITACHI_FAN_MAP.get(fan_val, "unknown")

    # Byte 15: Swing (bit 6)
    swing = "on" if (state_bytes[15] & 0x40) else "off"

    return {
        "power": power,
        "mode": mode,
        "temperature": temperature,
        "fan": fan,
        "swing": swing,
    }


def decode_hitachi_ac1(timings: List[int]) -> Dict[str, Any]:
    """
    Decode Hitachi AC1 IR signal (13 bytes).

    13 bytes (104 bits) - bit-reversed
    - Byte 9: Power (bit 4)
    - Byte 10: Mode (bits 0-3)
    - Byte 3: Temperature (bits 0-5)
    - Byte 7: Fan speed (bits 0-2)
    """
    bits = timings_to_bits_space_encoding(timings, threshold=850)

    if len(bits) < 104:  # 13 bytes * 8
        return unknown_state()

    state_bytes = bits_to_bytes(bits)

    if len(state_bytes) < 11:
        return unknown_state()

    # Hitachi uses bit-reversed bytes
    state_bytes = [reverse_bits(b) for b in state_bytes]

    # Byte 9: Power (bit 4)
    power = "on" if (state_bytes[9] & 0x10) else "off"

    # Byte 10: Mode (bits 0-3)
    mode_val = state_bytes[10] & 0x0F
    mode = HITACHI_MODE_MAP.get(mode_val, "unknown")

    # Byte 3: Temperature (bits 0-5)
    temp_offset = state_bytes[3] & 0x3F
    temperature = temp_offset / 2.0 + 16
    if temperature < 16:
        temperature = 16
    elif temperature > 32:
        temperature = 32

    # Byte 7: Fan speed (bits 0-2)
    fan_val = state_bytes[7] & 0x07
    fan = HITACHI_FAN_MAP.get(fan_val, "unknown")

    return {
        "power": power,
        "mode": mode,
        "temperature": temperature,
        "fan": fan,
        "swing": "unknown",
    }


# ============================================================================
# SHARP AC DECODER
# ============================================================================

# Sharp mode constants
SHARP_MODE_AUTO = 0x0
SHARP_MODE_DRY = 0x1
SHARP_MODE_COOL = 0x2
SHARP_MODE_HEAT = 0x3

SHARP_MODE_MAP = {
    SHARP_MODE_AUTO: "auto",
    SHARP_MODE_DRY: "dry",
    SHARP_MODE_COOL: "cool",
    SHARP_MODE_HEAT: "heat",
}

# Sharp fan constants
SHARP_FAN_MAP = {
    2: "low",
    3: "medium",
    4: "high",
    5: "auto",
}

# Sharp special power states
SHARP_POWER_ON = 0xC1
SHARP_POWER_OFF = 0xC5


def decode_sharp_ac(timings: List[int]) -> Dict[str, Any]:
    """
    Decode Sharp AC IR signal.

    13 bytes (104 bits)
    - Byte 5: Special power byte (0xC1=on, 0xC5=off)
    - Byte 6: Mode (bits 4-5), Temperature (bits 0-3)
    - Byte 8: Fan speed (bits 4-7)
    - Byte 6: Swing (bit 7)
    """
    bits = timings_to_bits_space_encoding(timings, threshold=850)

    if len(bits) < 104:  # 13 bytes * 8
        return unknown_state()

    state_bytes = bits_to_bytes(bits)

    if len(state_bytes) < 9:
        return unknown_state()

    # Byte 5: Special power byte
    power_byte = state_bytes[5]
    if power_byte == SHARP_POWER_ON:
        power = "on"
    elif power_byte == SHARP_POWER_OFF:
        power = "off"
    else:
        power = "unknown"

    # Byte 6: Mode (bits 4-5)
    mode_val = (state_bytes[6] >> 4) & 0x03
    mode = SHARP_MODE_MAP.get(mode_val, "unknown")

    # Byte 6: Temperature (bits 0-3)
    temp_offset = state_bytes[6] & 0x0F
    temperature = temp_offset + 17
    if temperature < 17:
        temperature = 17
    elif temperature > 30:
        temperature = 30

    # Byte 8: Fan speed (bits 4-7)
    fan_val = (state_bytes[8] >> 4) & 0x0F
    fan = SHARP_FAN_MAP.get(fan_val, "unknown")

    # Byte 6: Swing (bit 7)
    swing = "on" if (state_bytes[6] & 0x80) else "off"

    return {
        "power": power,
        "mode": mode,
        "temperature": temperature,
        "fan": fan,
        "swing": swing,
    }


# ============================================================================
# TOSHIBA AC DECODER
# ============================================================================

# Toshiba mode constants
TOSHIBA_MODE_AUTO = 0x0
TOSHIBA_MODE_COOL = 0x1
TOSHIBA_MODE_DRY = 0x2
TOSHIBA_MODE_HEAT = 0x3

TOSHIBA_MODE_MAP = {
    TOSHIBA_MODE_AUTO: "auto",
    TOSHIBA_MODE_COOL: "cool",
    TOSHIBA_MODE_DRY: "dry",
    TOSHIBA_MODE_HEAT: "heat",
}

# Toshiba fan constants
TOSHIBA_FAN_MAP = {
    0: "auto",
    1: "quiet",
    2: "low",
    3: "medium",
    4: "high",
    5: "max",
}


def decode_toshiba_ac(timings: List[int]) -> Dict[str, Any]:
    """
    Decode Toshiba AC IR signal.

    Variable length: 6-9 bytes (48-72 bits)
    - Byte 6: Power (bit 0), Mode (bits 4-5)
    - Byte 5: Temperature (bits 0-3)
    - Byte 6: Fan speed (bits 5-7)
    """
    bits = timings_to_bits_space_encoding(timings, threshold=850)

    if len(bits) < 48:  # Minimum 6 bytes * 8
        return unknown_state()

    state_bytes = bits_to_bytes(bits)

    if len(state_bytes) < 7:
        return unknown_state()

    # Byte 6: Power (bit 0)
    power = "on" if (state_bytes[6] & 0x01) else "off"

    # Byte 6: Mode (bits 4-5)
    mode_val = (state_bytes[6] >> 4) & 0x03
    mode = TOSHIBA_MODE_MAP.get(mode_val, "unknown")

    # Byte 5: Temperature (bits 0-3)
    temp_offset = state_bytes[5] & 0x0F
    temperature = temp_offset + 17
    if temperature < 17:
        temperature = 17
    elif temperature > 30:
        temperature = 30

    # Byte 6: Fan speed (bits 5-7)
    fan_val = (state_bytes[6] >> 5) & 0x07
    fan = TOSHIBA_FAN_MAP.get(fan_val, "unknown")

    # Toshiba swing is complex, simplified here
    swing = "unknown"

    return {
        "power": power,
        "mode": mode,
        "temperature": temperature,
        "fan": fan,
        "swing": swing,
    }


# ============================================================================
# VESTEL AC DECODER
# ============================================================================

# Vestel mode constants
VESTEL_MODE_AUTO = 0x0
VESTEL_MODE_COOL = 0x1
VESTEL_MODE_DRY = 0x2
VESTEL_MODE_FAN = 0x3
VESTEL_MODE_HEAT = 0x4

VESTEL_MODE_MAP = {
    VESTEL_MODE_AUTO: "auto",
    VESTEL_MODE_COOL: "cool",
    VESTEL_MODE_DRY: "dry",
    VESTEL_MODE_FAN: "fan",
    VESTEL_MODE_HEAT: "heat",
}

# Vestel fan constants
VESTEL_FAN_MAP = {
    1: "low",
    5: "medium",
    9: "high",
    13: "auto",
}


def decode_vestel_ac(timings: List[int]) -> Dict[str, Any]:
    """
    Decode Vestel AC IR signal.

    7 bytes (56 bits) - dual state blocks
    - Byte 3: Power (bit 5)
    - Byte 0: Mode (bits 5-7)
    - Byte 1: Temperature (bits 3-7)
    - Byte 4: Fan speed (bits 0-3)
    - Byte 4: Swing (bit 7)
    """
    bits = timings_to_bits_space_encoding(timings, threshold=850)

    if len(bits) < 56:  # 7 bytes * 8
        return unknown_state()

    state_bytes = bits_to_bytes(bits)

    if len(state_bytes) < 5:
        return unknown_state()

    # Byte 3: Power (bit 5)
    power = "on" if (state_bytes[3] & 0x20) else "off"

    # Byte 0: Mode (bits 5-7)
    mode_val = (state_bytes[0] >> 5) & 0x07
    mode = VESTEL_MODE_MAP.get(mode_val, "unknown")

    # Byte 1: Temperature (bits 3-7)
    temp_offset = (state_bytes[1] >> 3) & 0x1F
    temperature = temp_offset + 16
    if temperature < 16:
        temperature = 16
    elif temperature > 30:
        temperature = 30

    # Byte 4: Fan speed (bits 0-3)
    fan_val = state_bytes[4] & 0x0F
    fan = VESTEL_FAN_MAP.get(fan_val, "unknown")

    # Byte 4: Swing (bit 7)
    swing = "on" if (state_bytes[4] & 0x80) else "off"

    return {
        "power": power,
        "mode": mode,
        "temperature": temperature,
        "fan": fan,
        "swing": swing,
    }


# ============================================================================
# WHIRLPOOL AC DECODER
# ============================================================================

# Whirlpool mode constants
WHIRLPOOL_MODE_AUTO = 0x0
WHIRLPOOL_MODE_COOL = 0x2
WHIRLPOOL_MODE_HEAT = 0x3
WHIRLPOOL_MODE_DRY = 0x1
WHIRLPOOL_MODE_FAN = 0x4

WHIRLPOOL_MODE_MAP = {
    WHIRLPOOL_MODE_AUTO: "auto",
    WHIRLPOOL_MODE_COOL: "cool",
    WHIRLPOOL_MODE_HEAT: "heat",
    WHIRLPOOL_MODE_DRY: "dry",
    WHIRLPOOL_MODE_FAN: "fan",
}

# Whirlpool fan constants
WHIRLPOOL_FAN_MAP = {
    0: "low",
    1: "medium",
    2: "high",
    3: "auto",
}


def decode_whirlpool_ac(timings: List[int]) -> Dict[str, Any]:
    """
    Decode Whirlpool AC IR signal.

    21 bytes (168 bits) in 3 sections
    - Byte 2: Power (bit 0)
    - Byte 3: Mode (bits 0-2)
    - Byte 3: Temperature (bits 4-7)
    - Byte 2: Fan speed (bits 4-5)
    - Byte 8: Swing (bits 6-7)
    """
    bits = timings_to_bits_space_encoding(timings, threshold=850)

    if len(bits) < 168:  # 21 bytes * 8
        return unknown_state()

    state_bytes = bits_to_bytes(bits)

    if len(state_bytes) < 9:
        return unknown_state()

    # Byte 2: Power (bit 0)
    power = "on" if (state_bytes[2] & 0x01) else "off"

    # Byte 3: Mode (bits 0-2)
    mode_val = state_bytes[3] & 0x07
    mode = WHIRLPOOL_MODE_MAP.get(mode_val, "unknown")

    # Byte 3: Temperature (bits 4-7)
    temp_offset = (state_bytes[3] >> 4) & 0x0F
    temperature = temp_offset + 18
    if temperature < 18:
        temperature = 18
    elif temperature > 30:
        temperature = 30

    # Byte 2: Fan speed (bits 4-5)
    fan_val = (state_bytes[2] >> 4) & 0x03
    fan = WHIRLPOOL_FAN_MAP.get(fan_val, "unknown")

    # Byte 8: Swing (bits 6-7)
    swing_val = (state_bytes[8] >> 6) & 0x03
    swing = "on" if swing_val != 0 else "off"

    return {
        "power": power,
        "mode": mode,
        "temperature": temperature,
        "fan": fan,
        "swing": swing,
    }


# ============================================================================
# ELECTRA AC DECODER
# ============================================================================

# Electra mode constants
ELECTRA_MODE_AUTO = 0x1
ELECTRA_MODE_COOL = 0x2
ELECTRA_MODE_DRY = 0x3
ELECTRA_MODE_FAN = 0x4
ELECTRA_MODE_HEAT = 0x5

ELECTRA_MODE_MAP = {
    ELECTRA_MODE_AUTO: "auto",
    ELECTRA_MODE_COOL: "cool",
    ELECTRA_MODE_DRY: "dry",
    ELECTRA_MODE_FAN: "fan",
    ELECTRA_MODE_HEAT: "heat",
}

# Electra fan constants
ELECTRA_FAN_MAP = {
    0: "auto",
    1: "low",
    2: "medium",
    3: "high",
}


def decode_electra_ac(timings: List[int]) -> Dict[str, Any]:
    """
    Decode Electra AC IR signal.

    13 bytes (104 bits) with iFeel sensor support
    - Byte 5: Power (bit 5)
    - Byte 6: Mode (bits 0-3)
    - Byte 1: Temperature (bits 0-4)
    - Byte 7: Fan speed (bits 4-5)
    - Byte 3: Swing (bit 0)
    """
    bits = timings_to_bits_space_encoding(timings, threshold=850)

    if len(bits) < 104:  # 13 bytes * 8
        return unknown_state()

    state_bytes = bits_to_bytes(bits)

    if len(state_bytes) < 8:
        return unknown_state()

    # Byte 5: Power (bit 5)
    power = "on" if (state_bytes[5] & 0x20) else "off"

    # Byte 6: Mode (bits 0-3)
    mode_val = state_bytes[6] & 0x0F
    mode = ELECTRA_MODE_MAP.get(mode_val, "unknown")

    # Byte 1: Temperature (bits 0-4)
    temp_offset = state_bytes[1] & 0x1F
    temperature = temp_offset + 15
    if temperature < 16:
        temperature = 16
    elif temperature > 30:
        temperature = 30

    # Byte 7: Fan speed (bits 4-5)
    fan_val = (state_bytes[7] >> 4) & 0x03
    fan = ELECTRA_FAN_MAP.get(fan_val, "unknown")

    # Byte 3: Swing (bit 0)
    swing = "on" if (state_bytes[3] & 0x01) else "off"

    return {
        "power": power,
        "mode": mode,
        "temperature": temperature,
        "fan": fan,
        "swing": swing,
    }


# ============================================================================
# DELONGHI AC DECODER
# ============================================================================

# Delonghi mode constants
DELONGHI_MODE_AUTO = 0x0
DELONGHI_MODE_COOL = 0x2
DELONGHI_MODE_DRY = 0x1
DELONGHI_MODE_FAN = 0x3
DELONGHI_MODE_HEAT = 0x4

DELONGHI_MODE_MAP = {
    DELONGHI_MODE_AUTO: "auto",
    DELONGHI_MODE_COOL: "cool",
    DELONGHI_MODE_DRY: "dry",
    DELONGHI_MODE_FAN: "fan",
    DELONGHI_MODE_HEAT: "heat",
}

# Delonghi fan constants
DELONGHI_FAN_MAP = {
    0: "auto",
    1: "low",
    2: "medium",
    3: "high",
}


def decode_delonghi_ac(timings: List[int]) -> Dict[str, Any]:
    """
    Decode Delonghi AC IR signal.

    8 bytes (64 bits) with timer support
    - Byte 0: Power (bit 0)
    - Byte 0: Mode (bits 4-6)
    - Byte 4: Temperature (bits 0-3)
    - Byte 5: Fan speed (bits 4-5)
    """
    bits = timings_to_bits_space_encoding(timings, threshold=850)

    if len(bits) < 64:  # 8 bytes * 8
        return unknown_state()

    state_bytes = bits_to_bytes(bits)

    if len(state_bytes) < 6:
        return unknown_state()

    # Byte 0: Power (bit 0)
    power = "on" if (state_bytes[0] & 0x01) else "off"

    # Byte 0: Mode (bits 4-6)
    mode_val = (state_bytes[0] >> 4) & 0x07
    mode = DELONGHI_MODE_MAP.get(mode_val, "unknown")

    # Byte 4: Temperature (bits 0-3)
    temp_offset = state_bytes[4] & 0x0F
    temperature = temp_offset + 18
    if temperature < 18:
        temperature = 18
    elif temperature > 32:
        temperature = 32

    # Byte 5: Fan speed (bits 4-5)
    fan_val = (state_bytes[5] >> 4) & 0x03
    fan = DELONGHI_FAN_MAP.get(fan_val, "unknown")

    return {
        "power": power,
        "mode": mode,
        "temperature": temperature,
        "fan": fan,
        "swing": "unknown",
    }


# ============================================================================
# CORONA AC DECODER
# ============================================================================

# Corona mode constants
CORONA_MODE_AUTO = 0x0
CORONA_MODE_COOL = 0x1
CORONA_MODE_DRY = 0x2
CORONA_MODE_HEAT = 0x3

CORONA_MODE_MAP = {
    CORONA_MODE_AUTO: "auto",
    CORONA_MODE_COOL: "cool",
    CORONA_MODE_DRY: "dry",
    CORONA_MODE_HEAT: "heat",
}

# Corona fan constants
CORONA_FAN_MAP = {
    0: "auto",
    1: "low",
    2: "medium",
    3: "high",
}


def decode_corona_ac(timings: List[int]) -> Dict[str, Any]:
    """
    Decode Corona AC IR signal.

    21 bytes (168 bits) in 3 sections
    - Byte 5: Power (bit 0)
    - Byte 9: Mode (bits 4-5)
    - Byte 6: Temperature (bits 4-7)
    - Byte 10: Fan speed (bits 0-1)
    - Byte 8: Swing (bit 7)
    """
    bits = timings_to_bits_space_encoding(timings, threshold=850)

    if len(bits) < 168:  # 21 bytes * 8
        return unknown_state()

    state_bytes = bits_to_bytes(bits)

    if len(state_bytes) < 11:
        return unknown_state()

    # Byte 5: Power (bit 0)
    power = "on" if (state_bytes[5] & 0x01) else "off"

    # Byte 9: Mode (bits 4-5)
    mode_val = (state_bytes[9] >> 4) & 0x03
    mode = CORONA_MODE_MAP.get(mode_val, "unknown")

    # Byte 6: Temperature (bits 4-7)
    temp_offset = (state_bytes[6] >> 4) & 0x0F
    temperature = temp_offset + 17
    if temperature < 17:
        temperature = 17
    elif temperature > 30:
        temperature = 30

    # Byte 10: Fan speed (bits 0-1)
    fan_val = state_bytes[10] & 0x03
    fan = CORONA_FAN_MAP.get(fan_val, "unknown")

    # Byte 8: Swing (bit 7)
    swing = "on" if (state_bytes[8] & 0x80) else "off"

    return {
        "power": power,
        "mode": mode,
        "temperature": temperature,
        "fan": fan,
        "swing": swing,
    }


# ============================================================================
# REMAINING MANUFACTURER DECODERS
# ============================================================================
# All remaining protocols use similar generic decoding with manufacturer-specific constants

def decode_generic_ac(timings: List[int], protocol_name: str) -> Dict[str, Any]:
    """
    Generic decoder for AC protocols using standard space encoding.
    Handles most common AC protocol patterns.

    This is a simplified decoder that provides basic state extraction.
    For production use with specific models, implement protocol-specific decoders above.
    """
    bits = timings_to_bits_space_encoding(timings, threshold=850)

    if len(bits) < 64:
        return unknown_state()

    state_bytes = bits_to_bytes(bits)

    if len(state_bytes) < 8:
        return unknown_state()

    # Generic extraction - works for many protocols
    # Most protocols have power/mode/temp in early bytes

    # Common pattern: byte 5-6 region for mode/temp
    power = "on"  # Default
    mode = "auto"  # Default
    temperature = 24  # Default
    fan = "auto"  # Default
    swing = "unknown"  # Most protocols don't have standard swing encoding

    # Try to extract temperature (usually in 16-32 range)
    for i in range(min(10, len(state_bytes))):
        byte_val = state_bytes[i]
        # Temperature candidates are usually 0-20 range (offset from 16)
        if 0 <= byte_val <= 20:
            temp_candidate = byte_val + 16
            if 16 <= temp_candidate <= 32:
                temperature = temp_candidate
                break

    return {
        "power": power,
        "mode": mode,
        "temperature": temperature,
        "fan": fan,
        "swing": swing,
    }


# ============================================================================
# PROTOCOL ROUTER
# ============================================================================

def decode_ac_protocol(timings: List[int], protocol: str) -> Dict[str, Any]:
    """
    Route to appropriate decoder based on protocol name.

    Supports all 32 AC protocols from IRremoteESP8266:
    - 16 protocols with specific decoders
    - 16 protocols using generic decoder fallback

    Args:
        timings: Raw IR timing array
        protocol: Protocol name (e.g., "FUJITSU_AC", "DAIKIN", etc.)

    Returns:
        Dictionary with decoded AC state
    """
    protocol_lower = protocol.lower().replace(" ", "_").replace("-", "_")

    # ========================================================================
    # SPECIFIC DECODERS (16 protocols)
    # ========================================================================

    # Fujitsu AC
    if "fujitsu" in protocol_lower and "ac" in protocol_lower:
        return decode_fujitsu_ac(timings)

    # Daikin AC (both DAIKIN and DAIKIN_AC variants)
    elif ("daikin" in protocol_lower) and ("daikin2" not in protocol_lower):
        return decode_daikin_ac(timings)

    # Mitsubishi AC (excluding Heavy variants)
    elif "mitsubishi" in protocol_lower and "ac" in protocol_lower and "heavy" not in protocol_lower:
        return decode_mitsubishi_ac(timings)

    # Panasonic AC
    elif "panasonic" in protocol_lower and "ac" in protocol_lower:
        return decode_panasonic_ac(timings)

    # Samsung AC
    elif "samsung" in protocol_lower and "ac" in protocol_lower:
        return decode_samsung_ac(timings)

    # LG
    elif "lg" in protocol_lower:
        return decode_lg_ac(timings)

    # Carrier AC
    elif "carrier" in protocol_lower and "ac" in protocol_lower:
        return decode_carrier_ac(timings)

    # Haier AC
    elif "haier" in protocol_lower and "ac" in protocol_lower:
        return decode_haier_ac(timings)

    # Hitachi AC (28 bytes)
    elif "hitachi" in protocol_lower and "ac" in protocol_lower and "ac1" not in protocol_lower:
        return decode_hitachi_ac(timings)

    # Hitachi AC1 (13 bytes)
    elif "hitachi" in protocol_lower and "ac1" in protocol_lower:
        return decode_hitachi_ac1(timings)

    # Sharp AC
    elif "sharp" in protocol_lower and "ac" in protocol_lower:
        return decode_sharp_ac(timings)

    # Toshiba AC
    elif "toshiba" in protocol_lower and "ac" in protocol_lower:
        return decode_toshiba_ac(timings)

    # Vestel AC
    elif "vestel" in protocol_lower and "ac" in protocol_lower:
        return decode_vestel_ac(timings)

    # Whirlpool AC
    elif "whirlpool" in protocol_lower and "ac" in protocol_lower:
        return decode_whirlpool_ac(timings)

    # Electra AC
    elif "electra" in protocol_lower and "ac" in protocol_lower:
        return decode_electra_ac(timings)

    # Delonghi AC
    elif "delonghi" in protocol_lower and "ac" in protocol_lower:
        return decode_delonghi_ac(timings)

    # Corona AC
    elif "corona" in protocol_lower and "ac" in protocol_lower:
        return decode_corona_ac(timings)

    # ========================================================================
    # GENERIC DECODER FALLBACK (16 protocols)
    # ========================================================================
    # These protocols use the generic decoder with basic state extraction:
    # AIRWELL, ARGO, BOSCH144, COOLIX, DAIKIN2, GOODWEATHER, GREE,
    # KELVINATOR, MIDEA, MITSUBISHI_HEAVY_152, NEOCLIMA, TCL112AC,
    # TECO, TRUMA, YORK

    elif any(keyword in protocol_lower for keyword in [
        "airwell", "argo", "bosch144", "coolix", "daikin2",
        "goodweather", "gree", "kelvinator", "midea",
        "mitsubishi_heavy", "neoclima", "tcl112ac", "tcl",
        "teco", "truma", "york"
    ]):
        return decode_generic_ac(timings, protocol)

    # ========================================================================
    # UNKNOWN PROTOCOL
    # ========================================================================
    # If protocol not recognized, return unknown state
    else:
        return unknown_state()
