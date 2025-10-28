#!/usr/bin/env python3
"""
Test decoding of user's working codes to understand the protocol
"""

from app.core.tuya_encoder import decode_tuya_ir
from app.core.ac_decoders import decode_fujitsu_ac


def timings_to_bits(timings: list[int]) -> list[int]:
    """Convert IR timings to bits"""
    # Skip header (first 2 timings)
    data_timings = timings[2:]

    bits = []
    for i in range(0, len(data_timings), 2):
        if i + 1 < len(data_timings):
            mark = data_timings[i]
            space = data_timings[i + 1]
            # Bit decision: space > 600 = 1, else 0
            bits.append(1 if space > 600 else 0)

    return bits


def bits_to_bytes(bits: list[int]) -> bytes:
    """Convert bits to bytes (LSB first)"""
    state_bytes = []
    for i in range(0, len(bits), 8):
        if i + 8 <= len(bits):
            byte_bits = bits[i:i+8]
            byte_val = 0
            for j, bit in enumerate(byte_bits):
                byte_val |= (bit << j)
            state_bytes.append(byte_val)
    return bytes(state_bytes)

# Test with user's working codes
OFF_CODE = "BvQMFwbeAb4gARFdAb4BlQTeAV0B3gGVBL4BXQFAAwHeAUADAZUEQANAD0ADAd4BQAMBlQRAA+ABD0ATAV0BQA/AA0APwAPAE0AHBd4BlQTeAUAHAL4gAQFdAUADAd4B4AMDAZUEQBNAAwHeAYADAb4B4AkTQBsBvgFAAwGVBEALAd4BQAcBlQSADwuVBN4BlQS+AZUE3gE="
ON_CODE = "BxoNDAbbAV8BQAMDtgGUBEAHAdsBgAcBtgGAA4APAZQE4AEP4A8TQBeAA+AFKwFfAcADgBcBlATADwLbAbYgAQFfAUADAdsBwAMBlARAD0ADAdsBwAMBlATgBwMAtuACEwG2AeADJwC2IAEBXwFAAwHbAeADAwC2IAEGXwG2AZQE22ADAV8BQAOADwFfAeADAwG2AUADQCcBXwGAAwC2IAEBXwFAAwHbAeAFAwG2AeADJ4APALYgB0AL4AEDALYgAQFfAUADAdsBwAkDQBdAA+AHG0ATQAPgExfgBx9ADwO2AZQEQDMDtgFfAYAHQA+AA4ALC18BtgGUBLYBtgG2AQ=="

print("="*80)
print("Decoding User's Working Codes")
print("="*80)

def analyze_code(name: str, code: str):
    print(f"\n{name}")
    print("-" * 80)

    # Decode Tuya to timings
    timings = decode_tuya_ir(code)
    print(f"Timings: {len(timings)} values")
    print(f"  First 10: {timings[:10]}")

    # Convert to bits
    bits = timings_to_bits(timings)
    print(f"\nBits: {len(bits)} bits")

    # Convert to bytes
    state_bytes = bits_to_bytes(bits)
    print(f"Bytes ({len(state_bytes)}): {' '.join(f'{b:02X}' for b in state_bytes)}")

    # Decode with Fujitsu decoder
    try:
        state = decode_fujitsu_ac(state_bytes)
        print(f"\nDecoded State:")
        for key, value in state.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"\n❌ Decode error: {e}")
        import traceback
        traceback.print_exc()

    # Manual byte analysis
    print(f"\nManual Byte Analysis:")
    if len(state_bytes) >= 16:
        print(f"  Byte 8 (Power/Temp): 0x{state_bytes[8]:02X} = {state_bytes[8]:08b}")
        print(f"    - Bit 0 (Power): {state_bytes[8] & 0x01}")
        print(f"    - Bits 2-7 (Temp): {(state_bytes[8] >> 2) & 0x3F} → {((state_bytes[8] >> 2) & 0x3F) / 4 + 16}°C")
        print(f"  Byte 9 (Mode): 0x{state_bytes[9]:02X} = {state_bytes[9]:08b}")
        print(f"    - Bits 0-2 (Mode): {state_bytes[9] & 0x07}")
        print(f"  Byte 10 (Fan/Swing): 0x{state_bytes[10]:02X} = {state_bytes[10]:08b}")
        print(f"    - Bits 0-2 (Fan): {state_bytes[10] & 0x07}")
        print(f"    - Bits 4-5 (Swing): {(state_bytes[10] >> 4) & 0x03}")
        print(f"  Byte 14: 0x{state_bytes[14]:02X}")
        print(f"  Byte 15 (Checksum): 0x{state_bytes[15]:02X}")
    elif len(state_bytes) >= 7:
        print(f"  7-byte OFF command")
        print(f"  Byte 0: 0x{state_bytes[0]:02X}")
        print(f"  Byte 1: 0x{state_bytes[1]:02X}")
        print(f"  Byte 6 (Checksum): 0x{state_bytes[6]:02X}")

analyze_code("OFF Command", OFF_CODE)
analyze_code("ON Command (Auto 20°C High Vertical)", ON_CODE)

print("\n" + "="*80)
