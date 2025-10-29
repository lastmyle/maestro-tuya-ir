"""
Show the exact problem: Fujitsu dispatcher only tries 128 bits
"""

from app.core.ir_protocols.test_codes import FUJITSU_KNOWN_GOOD_CODES
from app.core.tuya_encoder import decode_ir
from app.core.ir_protocols.ir_recv import decode_results, decodeFujitsuAC, kFujitsuAcBits


def test_show_problem():
    """Show that the dispatcher approach fails for short codes"""
    print(f"\n=== The Problem ===\n")

    for name, tuya_code in FUJITSU_KNOWN_GOOD_CODES.items():
        signal = decode_ir(tuya_code)
        results = decode_results()
        results.rawbuf = signal
        results.rawlen = len(signal)

        # This is what the dispatcher does (line 434):
        # if decodeFujitsuAC(results, offset, kFujitsuAcBits, strict=False):
        dispatcher_approach = decodeFujitsuAC(results, 0, kFujitsuAcBits, strict=False)

        # But we should try both short and long formats:
        results_short = decode_results()
        results_short.rawbuf = signal
        results_short.rawlen = len(signal)
        short_format = decodeFujitsuAC(results_short, 0, 56, strict=False)

        results_long = decode_results()
        results_long.rawbuf = signal
        results_long.rawlen = len(signal)
        long_format = decodeFujitsuAC(results_long, 0, 128, strict=False)

        print(f"\n{name}:")
        print(f"  Signal length: {len(signal)} timings")
        print(f"  Dispatcher approach (128 bits only): {'✓ SUCCESS' if dispatcher_approach else '✗ FAILED'}")
        print(f"  Try 56 bits:  {'✓ SUCCESS' if short_format else '✗ FAILED'} {f'(decoded {results_short.bits} bits)' if short_format else ''}")
        print(f"  Try 128 bits: {'✓ SUCCESS' if long_format else '✗ FAILED'} {f'(decoded {results_long.bits} bits)' if long_format else ''}")

        if short_format or long_format:
            print(f"  ✓ Code IS Fujitsu (but dispatcher misses short format!)")
        else:
            print(f"  ✗ Code NOT Fujitsu")


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v", "-s"])
