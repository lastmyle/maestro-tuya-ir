#!/usr/bin/env python3
"""
Test the updated FastLZ implementation with user's working codes
"""

from app.core.tuya_encoder import decode_tuya_ir, encode_tuya_ir

# Test with user's working codes
OFF_CODE = "BvQMFwbeAb4gARFdAb4BlQTeAV0B3gGVBL4BXQFAAwHeAUADAZUEQANAD0ADAd4BQAMBlQRAA+ABD0ATAV0BQA/AA0APwAPAE0AHBd4BlQTeAUAHAL4gAQFdAUADAd4B4AMDAZUEQBNAAwHeAYADAb4B4AkTQBsBvgFAAwGVBEALAd4BQAcBlQSADwuVBN4BlQS+AZUE3gE="
ON_CODE = "BxoNDAbbAV8BQAMDtgGUBEAHAdsBgAcBtgGAA4APAZQE4AEP4A8TQBeAA+AFKwFfAcADgBcBlATADwLbAbYgAQFfAUADAdsBwAMBlARAD0ADAdsBwAMBlATgBwMAtuACEwG2AeADJwC2IAEBXwFAAwHbAeADAwC2IAEGXwG2AZQE22ADAV8BQAOADwFfAeADAwG2AUADQCcBXwGAAwC2IAEBXwFAAwHbAeAFAwG2AeADJ4APALYgB0AL4AEDALYgAQFfAUADAdsBwAkDQBdAA+AHG0ATQAPgExfgBx9ADwO2AZQEQDMDtgFfAYAHQA+AA4ALC18BtgGUBLYBtgG2AQ=="

print("="*80)
print("Testing Updated FastLZ Implementation")
print("="*80)

def test_round_trip(name: str, code: str):
    print(f"\n{name}")
    print("-" * 80)

    try:
        # Decode
        timings = decode_tuya_ir(code)
        print(f"✅ Decoded: {len(timings)} timings")
        print(f"   First 10: {timings[:10]}")

        # Re-encode
        reencoded = encode_tuya_ir(timings)
        print(f"✅ Re-encoded: {len(reencoded)} chars")

        # Decode again to verify
        timings2 = decode_tuya_ir(reencoded)

        # Compare
        if timings == timings2:
            print(f"✅ Round-trip successful: Timings match perfectly!")
        else:
            print(f"❌ Round-trip failed: Timings differ")
            for i, (t1, t2) in enumerate(zip(timings, timings2)):
                if t1 != t2:
                    print(f"   Position {i}: {t1} → {t2}")
                    if i > 5:
                        print("   ...")
                        break

        # Check Base64 match
        if code == reencoded:
            print(f"✅ Base64 matches Tuya original (unexpected but great!)")
        else:
            print(f"ℹ️  Base64 differs (expected - compression not deterministic)")
            print(f"   Original:    {code[:50]}...")
            print(f"   Re-encoded:  {reencoded[:50]}...")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

test_round_trip("OFF Command", OFF_CODE)
test_round_trip("ON Command", ON_CODE)

print("\n" + "="*80)
print("Result:")
print("="*80)
print("If round-trip is successful, the FastLZ implementation is working correctly.")
print("Base64 difference is normal - AC hardware only cares about the timings.")
