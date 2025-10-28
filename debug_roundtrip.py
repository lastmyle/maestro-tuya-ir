#!/usr/bin/env python3
"""
Debug: Why does round-trip produce a shorter code?
"""

from app.core.ir_protocols.fujitsu import IRFujitsuAC, sendFujitsuAC
from app.core.ir_protocols.ir_recv import decode_results, decodeFujitsuAC, kFujitsuAcBits
from app.core.ir_protocols.test_codes import FUJITSU_KNOWN_GOOD_CODES
from app.core.tuya_encoder import decode_ir, encode_ir


def analyze_roundtrip():
    original = FUJITSU_KNOWN_GOOD_CODES["24C_High"]

    print("=" * 80)
    print("ROUND-TRIP ANALYSIS")
    print("=" * 80)

    # Step 1: Decode original Tuya code to timings
    print("\n1. DECODE ORIGINAL TUYA CODE")
    signal = decode_ir(original)
    print(f"   Original Tuya code length: {len(original)} chars")
    print(f"   Decoded to: {len(signal)} timings")
    print(f"   First 10 timings: {signal[:10]}")
    print(f"   These are REAL DEVICE TIMINGS (with natural variations)")

    # Step 2: Decode timings to bytes using EXACT C++ translation
    print("\n2. DECODE TIMINGS TO BYTES")
    results = decode_results()
    results.rawbuf = signal
    results.rawlen = len(signal)
    success = decodeFujitsuAC(results, offset=0, nbits=kFujitsuAcBits, strict=False)
    assert success
    bytes_array = results.state[:results.bits // 8]
    print(f"   Decoded to: {len(bytes_array)} bytes")
    print(f"   Bytes: {' '.join(f'{b:02x}' for b in bytes_array)}")

    # Step 3: Parse into IRFujitsuAC
    print("\n3. PARSE INTO IRFujitsuAC")
    command = IRFujitsuAC()
    command.setRaw(bytes_array, len(bytes_array))
    print(f"   Model: {command.getModel()}")
    print(f"   Temp: {command.getTemp()}°C")
    print(f"   Mode: {command.getMode()}")

    # Step 4: Get bytes back (THIS CALLS checkSum() which may modify!)
    print("\n4. GET BYTES BACK FROM IRFujitsuAC")
    new_bytes = command.getRaw()
    print(f"   Returned: {len(new_bytes)} bytes")
    print(f"   Bytes: {' '.join(f'{b:02x}' for b in new_bytes)}")

    # Compare bytes
    if bytes_array == new_bytes:
        print(f"   ✓ Bytes MATCH (no changes)")
    else:
        print(f"   ✗ Bytes DIFFER!")
        for i, (old, new) in enumerate(zip(bytes_array, new_bytes)):
            if old != new:
                print(f"      Byte {i}: 0x{old:02x} → 0x{new:02x}")

    # Step 5: Encode bytes to timings (GENERATES IDEAL TIMINGS!)
    print("\n5. ENCODE BYTES TO TIMINGS")
    new_signal = sendFujitsuAC(new_bytes, len(new_bytes), repeat=0)
    print(f"   Generated: {len(new_signal)} timings")
    print(f"   First 10 timings: {new_signal[:10]}")
    print(f"   ⚠️  These are IDEAL PROTOCOL TIMINGS (from constants)")

    # Step 6: Compare timing patterns
    print("\n6. COMPARE TIMING PATTERNS")
    print(f"   Original timings (real device):")
    print(f"      {signal[:20]}")
    print(f"   Generated timings (ideal protocol):")
    print(f"      {new_signal[:20]}")
    print(f"\n   Notice: Values are similar but NOT identical")
    print(f"           Real device: 3294, 1602, 424, 372...")
    print(f"           Ideal spec:  3324, 1574, 448, 390...")

    # Step 7: Encode to Tuya
    print("\n7. ENCODE TO TUYA FORMAT")
    new_command = encode_ir(new_signal)
    print(f"   New Tuya code length: {len(new_command)} chars")
    print(f"   Original: {len(original)} chars")
    print(f"   Difference: {len(original) - len(new_command)} chars shorter")

    print(f"\n   Original: {original[:60]}...")
    print(f"   New:      {new_command[:60]}...")

    # Explain the compression difference
    print("\n8. WHY IS IT SHORTER?")
    print("   Tuya uses LZ77-style compression:")
    print("   - Real device timings have natural variations")
    print("   - Ideal timings are perfectly regular")
    print("   - Regular patterns compress MUCH better")
    print("   - Hence: shorter compressed code")

    print("\n9. WHY DOESN'T IT WORK ON THE DEVICE?")
    print("   The IR receiver on your device might be:")
    print("   - Too strict about timing tolerances")
    print("   - Expecting the exact timing variations it was trained on")
    print("   - Using a decoder that doesn't match the Fujitsu spec exactly")

    return original, new_command, bytes_array, new_bytes


def test_direct_byte_roundtrip():
    """Test that bytes round-trip correctly (without IRFujitsuAC)"""
    print("\n" + "=" * 80)
    print("TEST: DIRECT BYTE ROUND-TRIP (Without IRFujitsuAC)")
    print("=" * 80)

    original = FUJITSU_KNOWN_GOOD_CODES["24C_High"]

    # Decode
    signal1 = decode_ir(original)
    results1 = decode_results()
    results1.rawbuf = signal1
    results1.rawlen = len(signal1)
    success1 = decodeFujitsuAC(results1, offset=0, nbits=kFujitsuAcBits, strict=False)
    assert success1
    bytes1 = results1.state[:results1.bits // 8]

    # Encode (skipping IRFujitsuAC)
    signal2 = sendFujitsuAC(bytes1, len(bytes1), repeat=0)
    new_code = encode_ir(signal2)

    # Decode again
    signal3 = decode_ir(new_code)
    results2 = decode_results()
    results2.rawbuf = signal3
    results2.rawlen = len(signal3)
    success2 = decodeFujitsuAC(results2, offset=0, nbits=kFujitsuAcBits, strict=False)
    assert success2
    bytes2 = results2.state[:results2.bits // 8]

    print(f"\nOriginal bytes: {' '.join(f'{b:02x}' for b in bytes1)}")
    print(f"Final bytes:    {' '.join(f'{b:02x}' for b in bytes2)}")

    if bytes1 == bytes2:
        print("\n✓ Bytes match perfectly!")
        print("  The encoder/decoder work correctly.")
        print("  The issue is the timing differences.")
    else:
        print("\n✗ Bytes differ!")


def show_solution():
    """Show the correct way to modify commands"""
    print("\n" + "=" * 80)
    print("SOLUTION: How to modify commands correctly")
    print("=" * 80)

    print("\n❌ WRONG WAY (doesn't work):")
    print("   1. Decode Tuya → Timings → Bytes")
    print("   2. Parse into IRFujitsuAC")
    print("   3. Get bytes back")
    print("   4. Encode Bytes → Timings → Tuya")
    print("   Problem: Generates ideal timings that device doesn't recognize")

    print("\n✓ RIGHT WAY (preserves original timings):")
    print("   1. Store the ORIGINAL captured code")
    print("   2. Parse it to read settings: temp, mode, fan, etc.")
    print("   3. DON'T re-encode if you want exact same timing pattern")

    print("\n✓ ALTERNATIVE (if you must generate new codes):")
    print("   1. Create IRFujitsuAC from scratch")
    print("   2. Set desired settings: temp, mode, fan")
    print("   3. Get bytes and encode")
    print("   4. Test on device - may need timing adjustments")
    print("   5. If it works, capture it and use that as reference")


if __name__ == "__main__":
    print("\nWHY IS THE RE-ENCODED COMMAND SHORTER?")
    print("=" * 80)

    original, new_command, bytes_array, new_bytes = analyze_roundtrip()
    test_direct_byte_roundtrip()
    show_solution()

    print("\n" + "=" * 80)
    print("SUMMARY:")
    print("  - Original code has real device timings (with variations)")
    print("  - Re-encoded code has ideal protocol timings (perfectly regular)")
    print("  - Ideal timings compress better → shorter code")
    print("  - But device may not recognize ideal timings")
    print("  - Solution: Use original captured codes, don't re-encode")
    print("=" * 80)
