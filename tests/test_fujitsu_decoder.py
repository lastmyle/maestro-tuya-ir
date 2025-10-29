"""
Test Fujitsu decoder with real codes to diagnose why detection is failing
"""

from app.core.ir_protocols.test_codes import FUJITSU_KNOWN_GOOD_CODES
from app.core.tuya_encoder import decode_ir
from app.core.ir_protocols.ir_recv import decode_results, decodeFujitsuAC, kFujitsuAcBits
from app.core.ir_protocols.fujitsu import (
    kFujitsuAcHdrMark,
    kFujitsuAcHdrSpace,
    kFujitsuAcBitMark,
    kFujitsuAcOneSpace,
    kFujitsuAcZeroSpace,
    kFujitsuAcMinGap,
)


def test_fujitsu_timings_analysis():
    """Analyze the actual timings from a known Fujitsu code"""
    tuya_code = FUJITSU_KNOWN_GOOD_CODES["24C_High"]
    signal = decode_ir(tuya_code)

    print(f"\n=== Fujitsu Code Analysis ===")
    print(f"Code: 24C_High")
    print(f"Total timing values: {len(signal)}")
    print(f"\nFirst 20 timings:")
    for i, timing in enumerate(signal[:20]):
        timing_type = "MARK" if i % 2 == 0 else "SPACE"
        print(f"  [{i}] {timing_type}: {timing}µs")

    # Check header
    if len(signal) >= 2:
        header_mark = signal[0]
        header_space = signal[1]
        print(f"\n=== Header Check ===")
        print(f"Expected header mark: {kFujitsuAcHdrMark}µs")
        print(f"Actual header mark:   {header_mark}µs")
        print(f"Difference:           {abs(header_mark - kFujitsuAcHdrMark)}µs")
        print(f"Expected header space: {kFujitsuAcHdrSpace}µs")
        print(f"Actual header space:   {header_space}µs")
        print(f"Difference:            {abs(header_space - kFujitsuAcHdrSpace)}µs")

        # Calculate tolerance (25% default)
        mark_tolerance = kFujitsuAcHdrMark * 0.25
        space_tolerance = kFujitsuAcHdrSpace * 0.25

        mark_match = abs(header_mark - kFujitsuAcHdrMark) <= mark_tolerance
        space_match = abs(header_space - kFujitsuAcHdrSpace) <= space_tolerance

        print(f"\nHeader mark matches (±25%): {mark_match}")
        print(f"Header space matches (±25%): {space_match}")


def test_fujitsu_decoder_direct():
    """Test decodeFujitsuAC directly with known Fujitsu code"""
    tuya_code = FUJITSU_KNOWN_GOOD_CODES["24C_High"]
    signal = decode_ir(tuya_code)

    print(f"\n=== Direct Decoder Test ===")

    # Create results object
    results = decode_results()
    results.rawbuf = signal
    results.rawlen = len(signal)

    # Try decoding with different bit counts
    for bits in [kFujitsuAcBits, 128, 136, 144]:
        results_copy = decode_results()
        results_copy.rawbuf = signal
        results_copy.rawlen = len(signal)

        success = decodeFujitsuAC(results_copy, offset=0, nbits=bits, strict=False)
        print(f"\nTrying nbits={bits}: {'SUCCESS' if success else 'FAILED'}")
        if success:
            print(f"  Decoded {results_copy.bits} bits")
            print(f"  First 16 bytes: {bytes(results_copy.state[:16]).hex()}")


def test_all_known_codes():
    """Test all known Fujitsu codes"""
    print(f"\n=== Testing All Known Codes ===")

    for name, tuya_code in FUJITSU_KNOWN_GOOD_CODES.items():
        signal = decode_ir(tuya_code)
        results = decode_results()
        results.rawbuf = signal
        results.rawlen = len(signal)

        success = decodeFujitsuAC(results, offset=0, nbits=kFujitsuAcBits, strict=False)
        status = "✓" if success else "✗"
        print(f"{status} {name:20} - {len(signal):3} timings - {'DECODED' if success else 'FAILED'}")

        if success:
            print(f"    Bits: {results.bits}, Bytes: {results.bits // 8}")


def test_timing_statistics():
    """Analyze timing patterns across all codes"""
    print(f"\n=== Timing Statistics ===")

    all_marks = []
    all_spaces = []

    for name, tuya_code in FUJITSU_KNOWN_GOOD_CODES.items():
        signal = decode_ir(tuya_code)

        # Skip header (first 2 values)
        for i in range(2, len(signal) - 1, 2):
            mark = signal[i]
            space = signal[i + 1]

            # Ignore footer/gap values > 8000
            if mark < 8000 and space < 8000:
                all_marks.append(mark)
                all_spaces.append(space)

    if all_marks and all_spaces:
        print(f"\nMark timings (bit marks):")
        print(f"  Min: {min(all_marks)}µs")
        print(f"  Max: {max(all_marks)}µs")
        print(f"  Avg: {sum(all_marks) // len(all_marks)}µs")
        print(f"  Expected: {kFujitsuAcBitMark}µs")

        # Find common space values (likely ONE and ZERO)
        space_counts = {}
        for space in all_spaces:
            # Round to nearest 50 for grouping
            rounded = (space // 50) * 50
            space_counts[rounded] = space_counts.get(rounded, 0) + 1

        print(f"\nMost common space timings:")
        for space, count in sorted(space_counts.items(), key=lambda x: -x[1])[:5]:
            print(f"  ~{space}µs: {count} occurrences")

        print(f"\nExpected spaces:")
        print(f"  ONE:  {kFujitsuAcOneSpace}µs")
        print(f"  ZERO: {kFujitsuAcZeroSpace}µs")


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v", "-s"])
