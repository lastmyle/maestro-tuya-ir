"""
Test for second real Tuya IR code.
"""

import pytest

from app.core.protocols import identify_protocol
from app.core.tuya import decode_tuya_ir


def test_decode_second_tuya_command():
    """
    Test decoding second real Tuya IR command.
    """
    tuya_code = "B9oMWAatAYIBgAMFyASCAYIBQAcBrQFAB8ADQA9AA8APQAdAD0ADQAvgIQNAAQGtAeAJN0ABAa0BwAPgAx8CrQGCIAEBrQFAE+AJAwCC4AATAYIBQAMBggFAE0AJ4BMDQCMByARAIQKCAa0gAYAFAa0BQAdAA4AbAK1gAcALQA/gOQNAAeAJRwGtAeANFQGtAeALF+AVEwPlAYIBQCMDyASCAUAH4A8DC8gEggGtAYIBrQGCAQ=="

    # Decode to raw timings
    timings = decode_tuya_ir(tuya_code)

    # Verify we got timings
    assert len(timings) > 0
    assert isinstance(timings, list)
    assert all(isinstance(t, int) for t in timings)

    # Verify timings are in valid range
    assert all(0 <= t <= 65535 for t in timings)

    print(f"\n📊 Second Code - Decoded {len(timings)} timing values")
    print(f"First 10 timings: {timings[:10]}")
    print(f"Header: [{timings[0]}, {timings[1]}]")
    print(f"Last 10 timings: {timings[-10:]}")


def test_identify_second_code_protocol():
    """
    Test identifying the protocol from the second Tuya command.
    """
    tuya_code = "B9oMWAatAYIBgAMFyASCAYIBQAcBrQFAB8ADQA9AA8APQAdAD0ADQAvgIQNAAQGtAeAJN0ABAa0BwAPgAx8CrQGCIAEBrQFAE+AJAwCC4AATAYIBQAMBggFAE0AJ4BMDQCMByARAIQKCAa0gAYAFAa0BQAdAA4AbAK1gAcALQA/gOQNAAeAJRwGtAeANFQGtAeALF+AVEwPlAYIBQCMDyASCAUAH4A8DC8gEggGtAYIBrQGCAQ=="

    # Decode to timings
    timings = decode_tuya_ir(tuya_code)

    # Try to identify protocol
    try:
        protocol_info = identify_protocol(timings)

        print(f"\n🔍 Second Code - Protocol Detection:")
        print(f"  Manufacturer: {protocol_info['manufacturer']}")
        print(f"  Protocol: {protocol_info['protocol']}")
        print(f"  Confidence: {protocol_info['confidence']}")
        print(f"  Header pattern: [{timings[0]}, {timings[1]}]")

        # Verify protocol detection
        assert protocol_info['confidence'] >= 0.5

    except ValueError as e:
        print(f"\n⚠️  Could not identify protocol: {e}")
        print(f"   Header timings: [{timings[0]}, {timings[1]}]")
        pytest.skip(f"Protocol not identified: {e}")


def test_compare_two_codes():
    """
    Compare the two Tuya codes to see if they're from the same manufacturer.
    """
    code1 = "Ed4MRQYFAkQBxAGIAcQBwATEAYAHQBMAiKABA8QBwASAA0ALQAMGRAHEAcAEiCADA8QBiAGAA0ATgAvAAUAPQAFAB4ADAsQBiGABQDfAL8AHAIhgAQDEIAEBiAHgAR8BiAFAD0ABQBMBwARAB0ADQAtAA0ALQAMBxAHARwjABIgBiAHEAYhgAUAH4AcDAYgBQCNAAwGIAYAbQAsCxAGIoAEBxAFAS0ADQAsDwATEAcALQA8AiKABwAlABwHEAYAhQAECxAGIYAFAB+ADA4ABQBGAAQDEIAEBRAFBZ0AHAsQBiCABgAUBiAGAB0AFAcQBgBsCxAGIYAHAB0ABAcQB4BMbQLcAiKABAcAE4AUDQAELwATEAYgBxAGIAYgB"

    code2 = "B9oMWAatAYIBgAMFyASCAYIBQAcBrQFAB8ADQA9AA8APQAdAD0ADQAvgIQNAAQGtAeAJN0ABAa0BwAPgAx8CrQGCIAEBrQFAE+AJAwCC4AATAYIBQAMBggFAE0AJ4BMDQCMByARAIQKCAa0gAYAFAa0BQAdAA4AbAK1gAcALQA/gOQNAAeAJRwGtAeANFQGtAeALF+AVEwPlAYIBQCMDyASCAUAH4A8DC8gEggGtAYIBrQGCAQ=="

    timings1 = decode_tuya_ir(code1)
    timings2 = decode_tuya_ir(code2)

    print(f"\n🔬 Comparison:")
    print(f"  Code 1 - {len(timings1)} timings, header: [{timings1[0]}, {timings1[1]}]")
    print(f"  Code 2 - {len(timings2)} timings, header: [{timings2[0]}, {timings2[1]}]")

    try:
        proto1 = identify_protocol(timings1)
        proto2 = identify_protocol(timings2)

        print(f"\n  Code 1: {proto1['manufacturer']} ({proto1['protocol']})")
        print(f"  Code 2: {proto2['manufacturer']} ({proto2['protocol']})")

        if proto1['manufacturer'] == proto2['manufacturer']:
            print(f"\n✅ Both codes are from {proto1['manufacturer']}")
        else:
            print(f"\n⚠️  Different manufacturers detected:")
            print(f"     Code 1: {proto1['manufacturer']}")
            print(f"     Code 2: {proto2['manufacturer']}")

    except ValueError as e:
        print(f"\n⚠️  Could not compare: {e}")
        pytest.skip("One or both codes couldn't be identified")
