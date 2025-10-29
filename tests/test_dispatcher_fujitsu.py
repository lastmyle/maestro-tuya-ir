"""
Test why the dispatcher doesn't detect Fujitsu codes correctly
"""

from app.core.ir_protocols.test_codes import FUJITSU_KNOWN_GOOD_CODES
from app.core.tuya_encoder import decode_ir
from app.core.ir_protocols.ir_recv import decode_results
from app.core.ir_protocols.ir_dispatcher import decode, decode_type_t


def test_dispatcher_with_fujitsu_codes():
    """Test what the dispatcher detects for each Fujitsu code"""
    print(f"\n=== Dispatcher Detection Test ===\n")

    for name, tuya_code in FUJITSU_KNOWN_GOOD_CODES.items():
        signal = decode_ir(tuya_code)
        results = decode_results()
        results.rawbuf = signal
        results.rawlen = len(signal)

        success = decode(results, max_skip=0)

        detected_protocol = decode_type_t(results.decode_type).name if success else "NONE"
        status = "✓" if detected_protocol == "FUJITSU_AC" else "✗"

        print(f"{status} {name:20} - {len(signal):3} timings - Detected as: {detected_protocol}")
        if success:
            print(f"    Bits decoded: {results.bits}")


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v", "-s"])
