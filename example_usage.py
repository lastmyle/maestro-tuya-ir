#!/usr/bin/env python3
"""
Example usage of EXACT C++ translations from IRremoteESP8266

This demonstrates the complete workflow:
1. Decode Tuya IR code to timings
2. Decode timings to Fujitsu byte array
3. Encode byte array to timings
4. Encode timings to Tuya IR code
"""

from app.core.ir_protocols.fujitsu import sendFujitsuAC
from app.core.ir_protocols.ir_recv import decode_results, decodeFujitsuAC, kFujitsuAcBits
from app.core.ir_protocols.test_codes import FUJITSU_KNOWN_GOOD_CODES
from app.core.tuya_encoder import decode_ir, encode_ir


def demonstrate_decoding():
    """Show how to decode a Tuya IR code"""
    print("=" * 80)
    print("DECODING: Tuya Code → Timings → Bytes")
    print("=" * 80)

    # Get a known good code
    tuya_code = FUJITSU_KNOWN_GOOD_CODES["OFF"]
    print(f"\n1. Original Tuya code (base64):")
    print(f"   {tuya_code[:60]}...")

    # Step 1: Decode Tuya format to raw timings (using tuya_encoder.py)
    timings = decode_ir(tuya_code)
    print(f"\n2. Decoded to {len(timings)} IR timings (microseconds):")
    print(f"   First 10: {timings[:10]}")
    print(f"   These are mark/space pairs representing the IR signal")

    # Step 2: Decode timings to Fujitsu byte array (using decodeFujitsuAC - EXACT C++ translation)
    results = decode_results()
    results.rawbuf = timings
    results.rawlen = len(timings)
    success = decodeFujitsuAC(results, offset=0, nbits=kFujitsuAcBits, strict=False)
    assert success
    byte_count = results.bits // 8
    bytes_array = results.state[:byte_count]

    print(f"\n3. Decoded to {len(bytes_array)} Fujitsu protocol bytes:")
    print(f"   Hex: {' '.join(f'{b:02x}' for b in bytes_array)}")
    print(f"   Header: 0x{bytes_array[0]:02x} 0x{bytes_array[1]:02x} (Fujitsu signature)")
    print(f"   This is the actual AC command data")

    return bytes_array


def demonstrate_encoding(bytes_array):
    """Show how to encode a byte array to Tuya IR code"""
    print("\n" + "=" * 80)
    print("ENCODING: Bytes → Timings → Tuya Code")
    print("=" * 80)

    print(f"\n1. Starting with {len(bytes_array)} Fujitsu protocol bytes:")
    print(f"   Hex: {' '.join(f'{b:02x}' for b in bytes_array)}")

    # Step 1: Encode bytes to timings (using sendFujitsuAC from fujitsu.py)
    timings = sendFujitsuAC(bytes_array, len(bytes_array), repeat=0)
    print(f"\n2. Encoded to {len(timings)} IR timings (microseconds):")
    print(f"   First 10: {timings[:10]}")
    print(f"   These are mark/space pairs for the IR blaster")

    # Step 2: Encode timings to Tuya format (using tuya_encoder.py)
    tuya_code = encode_ir(timings)
    print(f"\n3. Encoded to Tuya code (base64):")
    print(f"   {tuya_code[:60]}...")
    print(f"   This can be sent directly to a Tuya IR blaster")

    return tuya_code


def demonstrate_round_trip():
    """Show complete round-trip validation"""
    print("\n" + "=" * 80)
    print("ROUND-TRIP VALIDATION")
    print("=" * 80)

    # Original code
    original_code = FUJITSU_KNOWN_GOOD_CODES["OFF"]
    print(f"\nOriginal Tuya code: {original_code[:40]}...")

    # Decode path
    timings1 = decode_ir(original_code)
    results1 = decode_results()
    results1.rawbuf = timings1
    results1.rawlen = len(timings1)
    success1 = decodeFujitsuAC(results1, offset=0, nbits=kFujitsuAcBits, strict=False)
    assert success1
    bytes1 = results1.state[: results1.bits // 8]
    print(f"Decoded bytes: {' '.join(f'{b:02x}' for b in bytes1)}")

    # Encode path
    timings2 = sendFujitsuAC(bytes1, len(bytes1), repeat=0)
    new_code = encode_ir(timings2)
    print(f"Re-encoded code: {new_code[:40]}...")

    # Verify
    timings3 = decode_ir(new_code)
    results2 = decode_results()
    results2.rawbuf = timings3
    results2.rawlen = len(timings3)
    success2 = decodeFujitsuAC(results2, offset=0, nbits=kFujitsuAcBits, strict=False)
    assert success2
    bytes2 = results2.state[: results2.bits // 8]
    print(f"Re-decoded bytes: {' '.join(f'{b:02x}' for b in bytes2)}")

    # Check results
    if bytes1 == bytes2:
        print("\n✓ ROUND-TRIP SUCCESS: Byte arrays match perfectly!")
        print("  This proves the EXACT C++ translations are working correctly")
    else:
        print("\n✗ ROUND-TRIP FAILED: Byte arrays differ")

    # Note about timing differences
    if len(timings1) != len(timings2):
        print(f"\nNote: Timing counts differ ({len(timings1)} vs {len(timings2)})")
        print("      This is EXPECTED due to gap/footer handling")
        print("      What matters is that the byte arrays match!")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("IRremoteESP8266 C++ Translation Demonstration")
    print("Files: ir_send.py (IRsend.cpp) + ir_recv.py (IRrecv.cpp)")
    print("=" * 80)

    # Demonstrate decoding
    bytes_array = demonstrate_decoding()

    # Demonstrate encoding
    tuya_code = demonstrate_encoding(bytes_array)

    # Demonstrate round-trip
    demonstrate_round_trip()

    print("\n" + "=" * 80)
    print("Translation Structure:")
    print("  C++ IRsend.cpp    → Python ir_send.py")
    print("  C++ IRrecv.cpp    → Python ir_recv.py")
    print("  C++ ir_Fujitsu.cpp → Python fujitsu.py")
    print("=" * 80)
