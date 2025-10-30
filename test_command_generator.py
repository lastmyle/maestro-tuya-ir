#!/usr/bin/env python3
"""
Test script to verify the command generator service works for all protocols
"""

import requests
import json

# Test codes for different protocols
TEST_CODES = {
    "Panasonic": "DYYNvAbdAa4B3QExBd0BQAeAA4ABQA3gAQHADUAHAd0B4AEvQAEB3QGAA8ABAd0BQB/AA0APQAMIMQWuAa4B3QGuYAFAB0ADQAFAB8ADAa4BQAmAAUAJwANAAeABCwDdIAFABYADQAHgCwvgARMCMQXdYAMAruAAAUALQAMDrgFnKOEDBwGuAeABAUAfQAPgDQFAGeAFL8ABQBmAAUAfgAPAEwrdATEFrgGuAd0BruAAAUALQAPAAUALwAMBrgFACUABATEFgAkBMQVAA0ALgAMDMQWuAYABgAtADwkxBd0BrgHdATEFQAUAriABQAVAA+AHAUATAd0BQCcBrgFABwLdAa7gAAEB3QFADwMxBa4BQAEEMQXdAa4gAUAFAzEFrgFABwGuAUAFQAMBrgGABeABAUAPwAMBrgFACQGuAUA3wANAEcADwAFAD8ABQAvAK0AHQAFAE+ADAUAPwAPgAwHgCxPAQ0ABwB/AB0AbwAvgAwHAE0AHQAFAB+ADA+ADAUBDQANAH0AHQAMLrgGuATEFrgExBa4B",
    # Add other protocol test codes here when available
}

API_URL = "http://localhost:8002/api/identify"


def test_protocol(protocol_name: str, tuya_code: str):
    """Test a single protocol"""
    print(f"\n{'='*60}")
    print(f"Testing {protocol_name}")
    print(f"{'='*60}")

    try:
        response = requests.post(
            API_URL,
            json={"tuya_code": tuya_code},
            headers={"accept": "application/json", "Content-Type": "application/json"},
        )

        if response.status_code != 200:
            print(f"❌ FAILED: HTTP {response.status_code}")
            print(f"   {response.text}")
            return False

        data = response.json()

        # Print results
        print(f"✓ Protocol detected: {data['protocol']}")
        print(f"✓ Manufacturer: {data['manufacturer']}")
        print(f"✓ Commands generated: {len(data['commands'])}")
        print(f"✓ Temperature range: {data['min_temperature']}-{data['max_temperature']}°C")
        print(f"✓ Operation modes: {', '.join(data['operation_modes'])}")
        print(f"✓ Fan modes: {', '.join(data['fan_modes'])}")
        print(f"✓ Notes: {data['notes']}")

        # Show sample commands
        if len(data["commands"]) > 0:
            print(f"\n  Sample commands:")
            for cmd in data["commands"][:3]:
                print(f"    • {cmd['name']}: {cmd['description']}")
            if len(data["commands"]) > 6:
                print(f"    ... and {len(data['commands']) - 3} more")

        print(f"\n✅ {protocol_name} test PASSED")
        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all protocol tests"""
    print("=" * 60)
    print("Command Generator Service Test Suite")
    print("=" * 60)

    results = {}
    for protocol_name, tuya_code in TEST_CODES.items():
        results[protocol_name] = test_protocol(protocol_name, tuya_code)

    # Summary
    print(f"\n{'='*60}")
    print("Test Summary")
    print(f"{'='*60}")

    passed = sum(1 for r in results.values() if r)
    total = len(results)

    for protocol, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status}: {protocol}")

    print(f"\nTotal: {passed}/{total} protocols passed")

    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(main())
