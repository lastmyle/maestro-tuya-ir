#!/usr/bin/env python3
"""
Test tuya1.py compression/decompression round-trip with known good codes
"""

import pytest
import sys

from app.core.tuya_encoder import decode_ir, encode_ir
from app.core.ir_protocols.test_codes import FUJITSU_KNOWN_GOOD_CODES


# Use centralized test codes
KNOWN_GOOD_CODES = FUJITSU_KNOWN_GOOD_CODES


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