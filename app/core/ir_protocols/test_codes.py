"""
Known Good IR Codes for Testing
These are validated Tuya IR codes captured from real devices
"""

# Fujitsu AC test codes
FUJITSU_KNOWN_GOOD_CODES = {
    "OFF": "BvQMFwbeAb4gARFdAb4BlQTeAV0B3gGVBL4BXQFAAwHeAUADAZUEQANAD0ADAd4BQAMBlQRAA+ABD0ATAV0BQA/AA0APwAPAE0AHBd4BlQTeAUAHAL4gAQFdAUADAd4B4AMDAZUEQBNAAwHeAYADAb4B4AkTQBsBvgFAAwGVBEALAd4BQAcBlQSADwuVBN4BlQS+AZUE3gE=",
    "24C_High": "B94MQgaoAXQBgAMDrwSoAUABQAfAE0ABQA9AA8ATQAdAD0ADQAtAAUAHQAPgAwFAD8AD4AMBQDfAAUAf4AMBQA/gAx9AAcATQBfgDwNAAcAnQAcFdAHkAXQBQAcAqOAAAUALQAPAQ0ALQAMBrwTgBStAE8ADwBtAAQOvBKgBwBcBdAGAM8ABAXQB4A0DQAHgCRuAOwF0AeABA0ABQA8BqAFAG0ADAagBQAPAAUAL4AcD4AMBwBvAAcCrQAFAC0ADQAHgAwcHdAGoAagBqAE=",
}

# Samsung AC test codes (add when available)
SAMSUNG_KNOWN_GOOD_CODES = {
    # "COOL_24C": "...",
    # "HEAT_22C": "...",
}

# Daikin AC test codes (add when available)
DAIKIN_KNOWN_GOOD_CODES = {
    # "COOL_24C": "...",
    # "HEAT_22C": "...",
}

# Mitsubishi AC test codes (add when available)
MITSUBISHI_KNOWN_GOOD_CODES = {
    # "COOL_24C": "...",
    # "HEAT_22C": "...",
}

# Panasonic AC test codes (add when available)
PANASONIC_KNOWN_GOOD_CODES = {
    # "COOL_24C": "...",
    # "HEAT_22C": "...",
}

# LG AC test codes (add when available)
LG_KNOWN_GOOD_CODES = {
    # "COOL_24C": "...",
    # "HEAT_22C": "...",
}

# Carrier AC test codes (add when available)
CARRIER_KNOWN_GOOD_CODES = {
    # "COOL_24C": "...",
    # "HEAT_22C": "...",
}

# Haier AC test codes (add when available)
HAIER_KNOWN_GOOD_CODES = {
    # "COOL_24C": "...",
    # "HEAT_22C": "...",
}

# Hitachi AC test codes (add when available)
HITACHI_KNOWN_GOOD_CODES = {
    # "COOL_24C": "...",
    # "HEAT_22C": "...",
}

# Sharp AC test codes (add when available)
SHARP_KNOWN_GOOD_CODES = {
    # "COOL_24C": "...",
    # "HEAT_22C": "...",
}

# Toshiba AC test codes (add when available)
TOSHIBA_KNOWN_GOOD_CODES = {
    # "COOL_24C": "...",
    # "HEAT_22C": "...",
}

# Vestel AC test codes (add when available)
VESTEL_KNOWN_GOOD_CODES = {
    # "COOL_24C": "...",
    # "HEAT_22C": "...",
}

# Whirlpool AC test codes (add when available)
WHIRLPOOL_KNOWN_GOOD_CODES = {
    # "COOL_24C": "...",
    # "HEAT_22C": "...",
}

# Electra AC test codes (add when available)
ELECTRA_KNOWN_GOOD_CODES = {
    # "COOL_24C": "...",
    # "HEAT_22C": "...",
}

# Delonghi AC test codes (add when available)
DELONGHI_KNOWN_GOOD_CODES = {
    # "COOL_24C": "...",
    # "HEAT_22C": "...",
}

# Corona AC test codes (add when available)
CORONA_KNOWN_GOOD_CODES = {
    # "COOL_24C": "...",
    # "HEAT_22C": "...",
}


# Master collection of all known good codes by protocol
ALL_KNOWN_GOOD_CODES = {
    "fujitsu": FUJITSU_KNOWN_GOOD_CODES,
    "samsung": SAMSUNG_KNOWN_GOOD_CODES,
    "daikin": DAIKIN_KNOWN_GOOD_CODES,
    "mitsubishi": MITSUBISHI_KNOWN_GOOD_CODES,
    "panasonic": PANASONIC_KNOWN_GOOD_CODES,
    "lg": LG_KNOWN_GOOD_CODES,
    "carrier": CARRIER_KNOWN_GOOD_CODES,
    "haier": HAIER_KNOWN_GOOD_CODES,
    "hitachi": HITACHI_KNOWN_GOOD_CODES,
    "sharp": SHARP_KNOWN_GOOD_CODES,
    "toshiba": TOSHIBA_KNOWN_GOOD_CODES,
    "vestel": VESTEL_KNOWN_GOOD_CODES,
    "whirlpool": WHIRLPOOL_KNOWN_GOOD_CODES,
    "electra": ELECTRA_KNOWN_GOOD_CODES,
    "delonghi": DELONGHI_KNOWN_GOOD_CODES,
    "corona": CORONA_KNOWN_GOOD_CODES,
}


def get_test_codes(protocol: str) -> dict:
    """
    Get known good test codes for a specific protocol.

    Args:
        protocol: Protocol name (e.g., "fujitsu", "samsung")

    Returns:
        Dictionary of test codes for the protocol
    """
    return ALL_KNOWN_GOOD_CODES.get(protocol.lower(), {})


def add_test_code(protocol: str, name: str, code: str) -> None:
    """
    Add a new test code to the collection.

    Args:
        protocol: Protocol name
        name: Test code name (e.g., "COOL_24C")
        code: Base64 encoded Tuya IR code
    """
    protocol_key = protocol.lower()
    if protocol_key in ALL_KNOWN_GOOD_CODES:
        ALL_KNOWN_GOOD_CODES[protocol_key][name] = code
    else:
        ALL_KNOWN_GOOD_CODES[protocol_key] = {name: code}


def list_protocols() -> list:
    """Get list of protocols with available test codes."""
    return [protocol for protocol, codes in ALL_KNOWN_GOOD_CODES.items() if codes]


def list_test_codes(protocol: str) -> list:
    """Get list of test code names for a protocol."""
    codes = get_test_codes(protocol)
    return list(codes.keys())
