"""
Simple test to check if dispatcher tries Fujitsu before Carrier
"""

from app.core.ir_protocols.test_codes import FUJITSU_KNOWN_GOOD_CODES
from app.core.tuya_encoder import decode_ir
from app.core.ir_protocols.ir_recv import decode_results, decodeFujitsuAC, kFujitsuAcBits
from app.core.ir_protocols.carrier import decodeCarrierAC84
from app.core.ir_protocols.ir_dispatcher import decode_type_t


def test_order_matters():
    """Test if Fujitsu detects before Carrier"""
    print(f"\n=== Testing Decode Order ===\n")

    for name, tuya_code in FUJITSU_KNOWN_GOOD_CODES.items():
        signal = decode_ir(tuya_code)

        # Test with offset=0 (what we expect)
        results_fujitsu_0 = decode_results()
        results_fujitsu_0.rawbuf = signal
        results_fujitsu_0.rawlen = len(signal)
        fujitsu_match_0 = decodeFujitsuAC(results_fujitsu_0, 0, kFujitsuAcBits, strict=False)

        results_carrier_0 = decode_results()
        results_carrier_0.rawbuf = signal
        results_carrier_0.rawlen = len(signal)
        carrier_match_0 = decodeCarrierAC84(results_carrier_0, 0)

        # Test with offset=1 (what dispatcher actually uses!)
        results_fujitsu_1 = decode_results()
        results_fujitsu_1.rawbuf = signal
        results_fujitsu_1.rawlen = len(signal)
        fujitsu_match_1 = decodeFujitsuAC(results_fujitsu_1, 1, kFujitsuAcBits, strict=False)

        results_carrier_1 = decode_results()
        results_carrier_1.rawbuf = signal
        results_carrier_1.rawlen = len(signal)
        carrier_match_1 = decodeCarrierAC84(results_carrier_1, 1)

        print(f"{name}:")
        print(f"  Offset=0: Fujitsu={fujitsu_match_0}, Carrier={carrier_match_0}")
        print(f"  Offset=1: Fujitsu={fujitsu_match_1}, Carrier={carrier_match_1}")
        print(f"  Dispatcher uses offset=1 (kStartOffset=1, max_skip=0)\n")


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v", "-s"])
