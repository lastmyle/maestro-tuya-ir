#!/usr/bin/env python3
"""
Example: Parse bytes into Fujitsu object

Shows how to:
1. Decode Tuya IR code to bytes
2. Parse bytes into IRFujitsuAC object
3. Read AC state (temp, mode, fan, etc.)
"""

from app.core.ir_protocols.ir_recv import decode_results, decodeFujitsuAC, kFujitsuAcBits
from app.core.ir_protocols.fujitsu import IRFujitsuAC, ARRAH2E
from app.core.ir_protocols.test_codes import FUJITSU_KNOWN_GOOD_CODES
from app.core.tuya_encoder import decode_ir


def parse_off_command():
    """Example: Parse OFF command"""
    print("=" * 80)
    print("Example 1: Parse OFF command")
    print("=" * 80)

    # Step 1: Get Tuya code and decode to bytes using EXACT C++ translation
    tuya_code = FUJITSU_KNOWN_GOOD_CODES['OFF']
    timings = decode_ir(tuya_code)
    results = decode_results()
    results.rawbuf = timings
    results.rawlen = len(timings)
    success = decodeFujitsuAC(results, offset=0, nbits=kFujitsuAcBits, strict=False)
    assert success
    bytes_array = results.state[:results.bits // 8]

    print(f"\nBytes (hex): {' '.join(f'{b:02x}' for b in bytes_array)}")
    print(f"Length: {len(bytes_array)} bytes (short format)")

    # Step 2: Create Fujitsu object
    ac = IRFujitsuAC(model=ARRAH2E)

    # Step 3: Parse bytes into object using setRaw()
    success = ac.setRaw(bytes_array, len(bytes_array))

    if not success:
        print("✗ Failed to parse bytes")
        return

    print("\n✓ Successfully parsed bytes into Fujitsu object")

    # Step 4: Read AC state
    print("\nAC State:")
    print(f"  Model: {ac.getModel()} (0=ARRAH2E, 1=ARDB1, 2=ARREB1E, etc.)")
    print(f"  Power: {'ON' if ac.getPower() else 'OFF'}")
    print(f"  Command: 0x{ac.getCmd():02x}")
    print(f"  Temperature: {ac.getTemp()}°C")
    print(f"  Mode: {ac.getMode()} (0=Auto, 1=Cool, 2=Dry, 3=Fan, 4=Heat)")
    print(f"  Fan Speed: {ac.getFanSpeed()} (0=Auto, 1=High, 2=Med, 3=Low, 4=Quiet)")
    print(f"  Swing: {ac.getSwing()} (0=Off, 1=Vert, 2=Horiz, 3=Both)")

    return ac


def parse_24c_high_command():
    """Example: Parse 24C High command"""
    print("\n" + "=" * 80)
    print("Example 2: Parse 24C High command")
    print("=" * 80)

    # Step 1: Get Tuya code and decode to bytes using EXACT C++ translation
    tuya_code = FUJITSU_KNOWN_GOOD_CODES['24C_High']
    timings = decode_ir(tuya_code)
    results = decode_results()
    results.rawbuf = timings
    results.rawlen = len(timings)
    success = decodeFujitsuAC(results, offset=0, nbits=kFujitsuAcBits, strict=False)
    assert success
    bytes_array = results.state[:results.bits // 8]

    print(f"\nBytes (hex): {' '.join(f'{b:02x}' for b in bytes_array)}")
    print(f"Length: {len(bytes_array)} bytes (long format)")

    # Step 2: Create Fujitsu object
    ac = IRFujitsuAC()  # Will auto-detect model from bytes

    # Step 3: Parse bytes into object
    success = ac.setRaw(bytes_array, len(bytes_array))

    if not success:
        print("✗ Failed to parse bytes")
        return

    print("\n✓ Successfully parsed bytes into Fujitsu object")

    # Step 4: Read detailed AC state
    print("\nAC State:")
    print(f"  Model: {ac.getModel()} (auto-detected from bytes)")
    print(f"  Power: {'ON' if ac.getPower() else 'OFF'}")
    print(f"  Command: 0x{ac.getCmd():02x}")
    print(f"  Temperature: {ac.getTemp()}°C")
    print(f"  Mode: {ac.getMode()} (0=Auto, 1=Cool, 2=Dry, 3=Fan, 4=Heat)")
    print(f"  Fan Speed: {ac.getFanSpeed()} (0=Auto, 1=High, 2=Med, 3=Low, 4=Quiet)")
    print(f"  Swing: {ac.getSwing()} (0=Off, 1=Vert, 2=Horiz, 3=Both)")
    print(f"  Clean: {'ON' if ac.getClean() else 'OFF'}")
    print(f"  Filter: {'ON' if ac.getFilter() else 'OFF'}")
    print(f"  Outside Quiet: {'ON' if ac.getOutsideQuiet() else 'OFF'}")
    print(f"  Timer Type: {ac.getTimerType()} (0=Stop, 1=Sleep, 2=Off, 3=On)")
    print(f"  On Timer: {ac.getOnTimer()} minutes")
    print(f"  Off/Sleep Timer: {ac.getOffSleepTimer()} minutes")

    return ac


def modify_and_encode_example():
    """Example: Parse bytes, modify settings, encode back to Tuya"""
    print("\n" + "=" * 80)
    print("Example 3: Parse → Modify → Encode back to Tuya")
    print("=" * 80)

    # Parse existing command
    tuya_code = FUJITSU_KNOWN_GOOD_CODES['24C_High']
    timings = decode_ir(tuya_code)
    results = decode_results()
    results.rawbuf = timings
    results.rawlen = len(timings)
    success = decodeFujitsuAC(results, offset=0, nbits=kFujitsuAcBits, strict=False)
    assert success
    bytes_array = results.state[:results.bits // 8]

    ac = IRFujitsuAC()
    ac.setRaw(bytes_array, len(bytes_array))

    print(f"\nOriginal settings:")
    print(f"  Temperature: {ac.getTemp()}°C")
    print(f"  Fan Speed: {ac.getFanSpeed()}")

    # Modify settings
    ac.setTemp(22)  # Change to 22°C
    ac.setFanSpeed(2)  # Change to medium fan

    print(f"\nModified settings:")
    print(f"  Temperature: {ac.getTemp()}°C")
    print(f"  Fan Speed: {ac.getFanSpeed()}")

    # Get modified bytes
    modified_bytes = ac.getRaw()
    print(f"\nModified bytes (hex): {' '.join(f'{b:02x}' for b in modified_bytes)}")

    # Encode back to Tuya (if needed)
    from app.core.ir_protocols.fujitsu import sendFujitsuAC
    from app.core.tuya_encoder import encode_ir

    modified_timings = sendFujitsuAC(modified_bytes, len(modified_bytes), repeat=0)
    modified_tuya = encode_ir(modified_timings)
    print(f"\nModified Tuya code: {modified_tuya[:60]}...")
    print("This can now be sent to your IR blaster!")


if __name__ == "__main__":
    print("\nFujitsu Byte Parsing Examples")
    print("Using setRaw() method from IRFujitsuAC class")
    print("=" * 80)

    # Example 1: Parse OFF command (short format)
    ac1 = parse_off_command()

    # Example 2: Parse 24C High command (long format)
    ac2 = parse_24c_high_command()

    # Example 3: Parse, modify, encode
    modify_and_encode_example()

    print("\n" + "=" * 80)
    print("Key method: ac.setRaw(bytes_array, len(bytes_array))")
    print("  - Returns True if successful")
    print("  - Auto-detects model from bytes")
    print("  - Populates all AC state properties")
    print("  - Then use getter methods: getTemp(), getMode(), getFanSpeed(), etc.")
    print("=" * 80)
