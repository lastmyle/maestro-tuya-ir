#!/usr/bin/env python3
"""
Test the EXACT C++ translations in fujitsu_timings.py
"""

from app.core.ir_protocols.fujitsu import sendFujitsuAC
from app.core.ir_protocols.ir_recv import decode_results, decodeFujitsuAC, kFujitsuAcBits
from app.core.ir_protocols.test_codes import FUJITSU_KNOWN_GOOD_CODES
from app.core.tuya_encoder import decode_ir, encode_ir

def test_off_code():
    """Test the OFF code - should be 7 bytes (short format)"""
    print("=" * 80)
    print("Testing OFF code (short 7-byte format)")
    print("=" * 80)

    code = FUJITSU_KNOWN_GOOD_CODES['OFF']
    print(f"\nOriginal Tuya code: {code[:60]}...")

    # Decode: Tuya → Timings
    timings = decode_ir(code)
    print(f"Decoded to {len(timings)} timings")
    print(f"First 10 timings: {timings[:10]}")

    # Decode: Timings → Bytes using EXACT C++ translation
    results = decode_results()
    results.rawbuf = timings
    results.rawlen = len(timings)
    success = decodeFujitsuAC(results, offset=0, nbits=kFujitsuAcBits, strict=False)
    if not success:
        print("❌ FAILED: decodeFujitsuAC returned False")
        return False
    bytes_decoded = results.state[:results.bits // 8]

    print(f"\nDecoded to {len(bytes_decoded)} bytes")
    print(f"Bytes (hex): {' '.join(f'{b:02x}' for b in bytes_decoded)}")

    # Check header
    if bytes_decoded[0] == 0x14 and bytes_decoded[1] == 0x63:
        print("✓ Fujitsu header bytes correct (0x14 0x63)")
    else:
        print(f"✗ Invalid header: {bytes_decoded[0]:02x} {bytes_decoded[1]:02x}")

    # Encode: Bytes → Timings
    timings_encoded = sendFujitsuAC(bytes_decoded, len(bytes_decoded), repeat=0)
    print(f"\nEncoded to {len(timings_encoded)} timings")
    print(f"First 10 timings: {timings_encoded[:10]}")

    # Encode: Timings → Tuya
    code_encoded = encode_ir(timings_encoded)
    print(f"\nRe-encoded Tuya code: {code_encoded[:60]}...")

    # Compare round-trip
    print(f"\n{'='*80}")
    print("Round-trip validation:")
    print(f"Original timings count: {len(timings)}")
    print(f"Re-encoded timings count: {len(timings_encoded)}")

    # Timings may differ slightly due to gap/footer handling
    if len(timings) == len(timings_encoded):
        print("✓ Timing counts match")
    else:
        print(f"⚠ Timing counts differ (this may be OK due to gap handling)")

    # Check if codes decode to same bytes
    timings2 = decode_ir(code_encoded)
    results2 = decode_results()
    results2.rawbuf = timings2
    results2.rawlen = len(timings2)
    success2 = decodeFujitsuAC(results2, offset=0, nbits=kFujitsuAcBits, strict=False)
    assert success2
    bytes_decoded2 = results2.state[:results2.bits // 8]

    if bytes_decoded == bytes_decoded2:
        print("✓ Round-trip successful: Bytes match perfectly")
        return True
    else:
        print("✗ Round-trip failed: Bytes differ")
        print(f"  Original: {' '.join(f'{b:02x}' for b in bytes_decoded[:10])}...")
        print(f"  After RT: {' '.join(f'{b:02x}' for b in bytes_decoded2[:10])}...")
        return False


def test_24c_high_code():
    """Test the 24C_High code - should be 16 bytes (long format)"""
    print("\n" + "=" * 80)
    print("Testing 24C_High code (long 16-byte format)")
    print("=" * 80)

    code = FUJITSU_KNOWN_GOOD_CODES['24C_High']
    print(f"\nOriginal Tuya code: {code[:60]}...")

    # Decode: Tuya → Timings
    timings = decode_ir(code)
    print(f"Decoded to {len(timings)} timings")
    print(f"First 10 timings: {timings[:10]}")

    # Decode: Timings → Bytes using EXACT C++ translation
    results = decode_results()
    results.rawbuf = timings
    results.rawlen = len(timings)
    success = decodeFujitsuAC(results, offset=0, nbits=kFujitsuAcBits, strict=False)
    if not success:
        print("❌ FAILED: decodeFujitsuAC returned False")
        return False
    bytes_decoded = results.state[:results.bits // 8]

    print(f"\nDecoded to {len(bytes_decoded)} bytes")
    print(f"Bytes (hex): {' '.join(f'{b:02x}' for b in bytes_decoded)}")

    # Check header
    if bytes_decoded[0] == 0x14 and bytes_decoded[1] == 0x63:
        print("✓ Fujitsu header bytes correct (0x14 0x63)")
    else:
        print(f"✗ Invalid header: {bytes_decoded[0]:02x} {bytes_decoded[1]:02x}")

    # Encode: Bytes → Timings
    timings_encoded = sendFujitsuAC(bytes_decoded, len(bytes_decoded), repeat=0)
    print(f"\nEncoded to {len(timings_encoded)} timings")
    print(f"First 10 timings: {timings_encoded[:10]}")

    # Encode: Timings → Tuya
    code_encoded = encode_ir(timings_encoded)
    print(f"\nRe-encoded Tuya code: {code_encoded[:60]}...")

    # Compare round-trip
    print(f"\n{'='*80}")
    print("Round-trip validation:")
    print(f"Original timings count: {len(timings)}")
    print(f"Re-encoded timings count: {len(timings_encoded)}")

    # Check if codes decode to same bytes
    timings2 = decode_ir(code_encoded)
    results2 = decode_results()
    results2.rawbuf = timings2
    results2.rawlen = len(timings2)
    success2 = decodeFujitsuAC(results2, offset=0, nbits=kFujitsuAcBits, strict=False)
    assert success2
    bytes_decoded2 = results2.state[:results2.bits // 8]

    if bytes_decoded == bytes_decoded2:
        print("✓ Round-trip successful: Bytes match perfectly")
        return True
    else:
        print("✗ Round-trip failed: Bytes differ")
        print(f"  Original: {' '.join(f'{b:02x}' for b in bytes_decoded[:10])}...")
        print(f"  After RT: {' '.join(f'{b:02x}' for b in bytes_decoded2[:10])}...")
        return False


if __name__ == "__main__":
    print("\nTesting EXACT C++ translations from IRremoteESP8266")
    print("Functions tested: sendData, sendGeneric, matchData, matchBytes")
    print("=" * 80)

    success = True
    success &= test_off_code()
    success &= test_24c_high_code()

    print("\n" + "=" * 80)
    if success:
        print("✓ ALL TESTS PASSED - EXACT translations work correctly!")
    else:
        print("✗ SOME TESTS FAILED - Check output above")
    print("=" * 80)
