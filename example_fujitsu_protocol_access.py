#!/usr/bin/env python3
"""
Example: Accessing FujitsuProtocol directly

Shows how to access the low-level FujitsuProtocol object
from an IRFujitsuAC instance.
"""

from app.core.ir_protocols.fujitsu import IRFujitsuAC, FujitsuProtocol, ARRAH2E
from app.core.ir_protocols.ir_recv import decode_results, decodeFujitsuAC, kFujitsuAcBits
from app.core.ir_protocols.test_codes import FUJITSU_KNOWN_GOOD_CODES
from app.core.tuya_encoder import decode_ir


def access_protocol_object():
    """Show how to access the FujitsuProtocol object"""
    print("=" * 80)
    print("Accessing FujitsuProtocol Object")
    print("=" * 80)

    # Create an IRFujitsuAC instance
    ac = IRFujitsuAC(model=ARRAH2E)

    # Access the FujitsuProtocol instance via the ._ attribute
    protocol: FujitsuProtocol = ac._

    print(f"\n1. The protocol object is: {type(protocol)}")
    print(f"   IRFujitsuAC has a ._ attribute that holds the FujitsuProtocol")

    # Access raw byte arrays
    print(f"\n2. Access raw byte arrays:")
    print(f"   protocol.longcode:  {protocol.longcode[:10]}... (16 bytes total)")
    print(f"   protocol.shortcode: {protocol.shortcode[:7]} (7 bytes total)")

    # Access protocol fields via properties
    print(f"\n3. Access protocol fields (via properties):")
    print(f"   protocol.Cmd:       0x{protocol.Cmd:02x}")
    print(f"   protocol.Temp:      {protocol.Temp}")
    print(f"   protocol.Mode:      {protocol.Mode}")
    print(f"   protocol.Fan:       {protocol.Fan}")
    print(f"   protocol.Swing:     {protocol.Swing}")
    print(f"   protocol.Power:     {protocol.Power}")
    print(f"   protocol.Clean:     {protocol.Clean}")
    print(f"   protocol.Filter:    {protocol.Filter}")

    # Modify via properties
    print(f"\n4. Modify via properties:")
    print(f"   Before: protocol.Temp = {protocol.Temp}")
    protocol.Temp = 0x20  # Set raw temperature value
    print(f"   After:  protocol.Temp = {protocol.Temp}")


def parse_and_access_protocol():
    """Parse a real code and access the protocol object"""
    print("\n" + "=" * 80)
    print("Parse Real Code and Access Protocol")
    print("=" * 80)

    # Parse a real Fujitsu code using EXACT C++ translation
    tuya_code = FUJITSU_KNOWN_GOOD_CODES["24C_High"]
    timings = decode_ir(tuya_code)
    results = decode_results()
    results.rawbuf = timings
    results.rawlen = len(timings)
    success = decodeFujitsuAC(results, offset=0, nbits=kFujitsuAcBits, strict=False)
    assert success
    bytes_array = results.state[: results.bits // 8]

    print(f"\nParsed bytes: {' '.join(f'{b:02x}' for b in bytes_array)}")

    # Create AC object and parse
    ac = IRFujitsuAC()
    ac.setRaw(bytes_array, len(bytes_array))

    # Access the protocol object
    protocol = ac._

    print(f"\nProtocol object after parsing:")
    print(f"  protocol.longcode: {' '.join(f'{b:02x}' for b in protocol.longcode)}")
    print(f"\nDecoded fields:")
    print(
        f"  Header:      0x{protocol.longcode[0]:02x} 0x{protocol.longcode[1]:02x} (should be 0x14 0x63)"
    )
    print(f"  Cmd:         0x{protocol.Cmd:02x}")
    print(f"  RestLength:  {protocol.RestLength}")
    print(f"  Protocol:    0x{protocol.Protocol:02x}")
    print(f"  Temp (raw):  {protocol.Temp}")
    print(f"  Mode:        {protocol.Mode}")
    print(f"  Fan:         {protocol.Fan}")
    print(f"  Swing:       {protocol.Swing}")
    print(f"  Power:       {protocol.Power}")
    print(f"  Fahrenheit:  {protocol.Fahrenheit}")


def direct_byte_manipulation():
    """Show how to directly manipulate bytes"""
    print("\n" + "=" * 80)
    print("Direct Byte Manipulation")
    print("=" * 80)

    ac = IRFujitsuAC()
    protocol = ac._

    print(f"\n1. Direct array access:")
    print(f"   protocol.longcode[0] = 0x{protocol.longcode[0]:02x} (header byte 1)")
    print(f"   protocol.longcode[1] = 0x{protocol.longcode[1]:02x} (header byte 2)")
    print(f"   protocol.longcode[5] = 0x{protocol.longcode[5]:02x} (command byte)")

    print(f"\n2. Modify bytes directly:")
    print(f"   Before: protocol.longcode[5] = 0x{protocol.longcode[5]:02x}")
    protocol.longcode[5] = 0xFE  # Set command to long format
    print(f"   After:  protocol.longcode[5] = 0x{protocol.longcode[5]:02x}")

    print(f"\n3. Property access updates the same bytes:")
    print(f"   Before: protocol.Cmd = 0x{protocol.Cmd:02x}")
    protocol.Cmd = 0x02  # Set command via property
    print(f"   After:  protocol.Cmd = 0x{protocol.Cmd:02x}")
    print(f"   Verify: protocol.longcode[5] = 0x{protocol.longcode[5]:02x} (same byte!)")


def create_standalone_protocol():
    """Create a FujitsuProtocol without IRFujitsuAC"""
    print("\n" + "=" * 80)
    print("Create Standalone FujitsuProtocol")
    print("=" * 80)

    # You can create a FujitsuProtocol directly
    protocol = FujitsuProtocol()

    print(f"\nCreated standalone protocol object:")
    print(f"  Type: {type(protocol)}")
    print(f"  longcode initialized: {protocol.longcode[:10]}...")
    print(f"  shortcode initialized: {protocol.shortcode}")

    # Set some values
    protocol.longcode[0] = 0x14
    protocol.longcode[1] = 0x63
    protocol.Cmd = 0xFE
    protocol.Temp = 0x20
    protocol.Mode = 4
    protocol.Fan = 1

    print(f"\nAfter setting values:")
    print(f"  Header: 0x{protocol.longcode[0]:02x} 0x{protocol.longcode[1]:02x}")
    print(f"  Cmd:    0x{protocol.Cmd:02x}")
    print(f"  Temp:   {protocol.Temp}")
    print(f"  Mode:   {protocol.Mode}")
    print(f"  Fan:    {protocol.Fan}")


if __name__ == "__main__":
    print("\nFujitsuProtocol Access Examples")
    print("=" * 80)
    print("The FujitsuProtocol is accessed via: ac._")
    print("=" * 80)

    access_protocol_object()
    parse_and_access_protocol()
    direct_byte_manipulation()
    create_standalone_protocol()

    print("\n" + "=" * 80)
    print("Summary:")
    print("  IRFujitsuAC._ → FujitsuProtocol instance")
    print("  protocol.longcode → List[int] with 16 bytes")
    print("  protocol.shortcode → List[int] with 7 bytes")
    print("  protocol.Cmd, protocol.Temp, etc. → Properties for bit fields")
    print("=" * 80)
