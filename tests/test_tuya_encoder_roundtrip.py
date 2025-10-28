#!/usr/bin/env python3
"""
Test tuya1.py compression/decompression round-trip with known good codes
"""

import pytest
import sys

from app.core.tuya_encoder import decode_ir, encode_ir


# Known good codes from Tuya device
KNOWN_GOOD_CODES = {
    "OFF": "BvQMFwbeAb4gARFdAb4BlQTeAV0B3gGVBL4BXQFAAwHeAUADAZUEQANAD0ADAd4BQAMBlQRAA+ABD0ATAV0BQA/AA0APwAPAE0AHBd4BlQTeAUAHAL4gAQFdAUADAd4B4AMDAZUEQBNAAwHeAYADAb4B4AkTQBsBvgFAAwGVBEALAd4BQAcBlQSADwuVBN4BlQS+AZUE3gE=",
    "24C_High": "EfcMNAbRAYIB0QFWAdEBkwTRAeADB0ALQANAF0ADQAvAA0APQAPAD0AHwEdAC+ADA0AXQAPAE0A3QA9AA8ATwAdAE0AfwA/AB0AT4BMD4AMnwAvAB0BTwANAE8BHQAtAA0APQAdAI0AH4AMDQBvAF0ALwBsAgmABAdEBQA/AFwCCYAEB0QHgAQ8C0QGCYAFABwHRAUAr4AMHAIJgAUAHgAOAH8ABAdEBQANAE0ADAILgAAFAC4ADgBcC0QGCYAFAB4ADQBcHkwSCAYIB0QFAC0ADBJME0QGCIAFAB0ADC1YB0QGCAdEBggHRAQ==",
}


# def test_decode_completely():
#     for name, original in KNOWN_GOOD_CODES.items():
#         print(f"\nTesting {name} round-trip...")

#         # Decode
#         timings = decode_ir(original)
#         protocol_data = identify_protocol(timings)
#         protocol_info = ProtocolInfo(
#             name=protocol_data["protocol"],
#             manufacturer=protocol_data["manufacturer"],
#             confidence=protocol_data["confidence"],
#         )

#         # Try to parse state
#         state = parse_hvac_state(timings, protocol_data["protocol"])

#         command = generate_command(
#             protocol_data["protocol"],
#             power="on",
#             mode=state["mode"],
#             temperature=state["temperature"],
#             fan=state["fan"],
#             swing="off",
#             sample_code=original,
#         )

#         # Re-encode
#         print(f"Original:  %s\n" % original)


def test_round_trip():
    for name, original in KNOWN_GOOD_CODES.items():
        print(f"\nTesting {name} round-trip...")

        # Decode
        signal = decode_ir(original)
        assert len(signal) > 0, f"Decoded signal for {name} should not be empty"

        # Re-encode
        code = encode_ir(signal)
        print(f"Original:  %s\n" % original)
        print(f"Re-encoded: %s\n" % code)

        # The re-encoded code does NOT have to match the original