#!/usr/bin/env python3
"""
Test if GitHub FastLZ preserves timings and protocol bytes correctly
even though Base64 doesn't match
"""

import io
import base64
from struct import pack, unpack
import sys
sys.path.insert(0, '/Users/rhyswilliams/Documents/lastmyle/maestro-tuya-ir')

from app.core.ac_decoders import decode_fujitsu_ac

# GitHub repo's implementation (same as before)
def decompress(inf: io.FileIO) -> bytes:
    out = bytearray()
    while (header := inf.read(1)):
        L, D = header[0] >> 5, header[0] & 0b11111
        if not L:
            L = D + 1
            data = inf.read(L)
            assert len(data) == L
        else:
            if L == 7:
                L += inf.read(1)[0]
            L += 2
            D = (D << 8 | inf.read(1)[0]) + 1
            data = bytearray()
            while len(data) < L:
                data.extend(out[-D:][:L-len(data)])
        out.extend(data)
    return bytes(out)

def emit_literal_blocks(out: io.FileIO, data: bytes):
    for i in range(0, len(data), 32):
        emit_literal_block(out, data[i:i+32])

def emit_literal_block(out: io.FileIO, data: bytes):
    length = len(data) - 1
    assert 0 <= length < (1 << 5)
    out.write(bytes([length]))
    out.write(data)

def emit_distance_block(out: io.FileIO, length: int, distance: int):
    distance -= 1
    assert 0 <= distance < (1 << 13)
    length -= 2
    assert length > 0
    block = bytearray()
    if length >= 7:
        assert length - 7 < (1 << 8)
        block.append(length - 7)
        length = 7
    block.insert(0, length << 5 | distance >> 8)
    block.append(distance & 0xFF)
    out.write(block)

def compress(out: io.FileIO, data: bytes, level=2):
    if level == 0:
        return emit_literal_blocks(out, data)

    W = 2**13
    L = 255 + 9
    distance_candidates = lambda: range(1, min(pos, W) + 1)

    def find_length_for_distance(start: int) -> int:
        length = 0
        limit = min(L, len(data) - pos)
        while length < limit and data[pos + length] == data[start + length]:
            length += 1
        return length

    def find_length_max():
        return max(
            ((find_length_for_distance(pos - d), d) for d in distance_candidates()),
            key=lambda c: (c[0], -c[1]),
            default=None
        )

    pos = 0
    block_start = 0
    while pos < len(data):
        c = find_length_max()
        if c and c[0] >= 3:
            emit_literal_blocks(out, data[block_start:pos])
            emit_distance_block(out, c[0], c[1])
            pos += c[0]
            block_start = pos
        else:
            pos += 1
    emit_literal_blocks(out, data[block_start:pos])

def decode_ir(code: str) -> list[int]:
    payload = base64.decodebytes(code.encode('ascii'))
    payload = decompress(io.BytesIO(payload))
    signal = []
    while payload:
        assert len(payload) >= 2, f'garbage in decompressed payload: {payload.hex()}'
        signal.append(unpack('<H', payload[:2])[0])
        payload = payload[2:]
    return signal

def encode_ir(signal: list[int], compression_level=2) -> str:
    signal = [min(t, 65535) for t in signal]
    payload = b''.join(pack('<H', t) for t in signal)
    compress(out := io.BytesIO(), payload, compression_level)
    payload = out.getvalue()
    return base64.encodebytes(payload).decode('ascii').replace('\n', '')

def timings_to_protocol_bytes(timings: list[int]) -> bytes:
    """Convert timings to protocol bytes"""
    # Skip header (first 2 timings)
    data_timings = timings[2:]

    # Convert timings to bits
    bits = []
    for i in range(0, len(data_timings), 2):
        if i + 1 < len(data_timings):
            mark = data_timings[i]
            space = data_timings[i + 1]

            # Bit decision: space > 600 = 1, else 0
            if space > 600:
                bits.append(1)
            else:
                bits.append(0)

    # Convert bits to bytes (LSB first)
    state_bytes = []
    for i in range(0, len(bits), 8):
        if i + 8 <= len(bits):
            byte_bits = bits[i:i+8]
            byte_val = 0
            for j, bit in enumerate(byte_bits):
                byte_val |= (bit << j)
            state_bytes.append(byte_val)

    return bytes(state_bytes)

# Test codes
OFF_CODE = "BvQMFwbeAb4gARFdAb4BlQTeAV0B3gGVBL4BXQFAAwHeAUADAZUEQANAD0ADAd4BQAMBlQRAA+ABD0ATAV0BQA/AA0APwAPAE0AHBd4BlQTeAUAHAL4gAQFdAUADAd4B4AMDAZUEQBNAAwHeAYADAb4B4AkTQBsBvgFAAwGVBEALAd4BQAcBlQSADwuVBN4BlQS+AZUE3gE="
ON_CODE = "BxoNDAbbAV8BQAMDtgGUBEAHAdsBgAcBtgGAA4APAZQE4AEP4A8TQBeAA+AFKwFfAcADgBcBlATADwLbAbYgAQFfAUADAdsBwAMBlARAD0ADAdsBwAMBlATgBwMAtuACEwG2AeADJwC2IAEBXwFAAwHbAeADAwC2IAEGXwG2AZQE22ADAV8BQAOADwFfAeADAwG2AUADQCcBXwGAAwC2IAEBXwFAAwHbAeAFAwG2AeADJ4APALYgB0AL4AEDALYgAQFfAUADAdsBwAkDQBdAA+AHG0ATQAPgExfgBx9ADwO2AZQEQDMDtgFfAYAHQA+AA4ALC18BtgGUBLYBtgG2AQ=="

print("="*80)
print("Testing Round-Trip Accuracy (Timings & Protocol Bytes)")
print("="*80)

def test_code(name: str, code: str):
    print(f"\n{name}")
    print("-" * 80)

    # Decode original
    original_timings = decode_ir(code)
    original_bytes = timings_to_protocol_bytes(original_timings)

    print(f"Original timings: {len(original_timings)} values")
    print(f"Original bytes: {original_bytes.hex().upper()}")

    # Try to decode with Fujitsu decoder
    try:
        original_state = decode_fujitsu_ac(original_bytes)
        print(f"Original state: {original_state}")
    except Exception as e:
        print(f"Original decode error: {e}")
        original_state = None

    # Re-encode with level 2 (most common)
    reencoded = encode_ir(original_timings, compression_level=2)

    # Decode the re-encoded version
    reencoded_timings = decode_ir(reencoded)
    reencoded_bytes = timings_to_protocol_bytes(reencoded_timings)

    print(f"\nRe-encoded timings: {len(reencoded_timings)} values")
    print(f"Re-encoded bytes: {reencoded_bytes.hex().upper()}")

    # Try to decode with Fujitsu decoder
    try:
        reencoded_state = decode_fujitsu_ac(reencoded_bytes)
        print(f"Re-encoded state: {reencoded_state}")
    except Exception as e:
        print(f"Re-encoded decode error: {e}")
        reencoded_state = None

    # Compare
    print("\n" + "─" * 80)
    timings_match = original_timings == reencoded_timings
    bytes_match = original_bytes == reencoded_bytes
    state_match = original_state == reencoded_state if (original_state and reencoded_state) else False

    print(f"Timings match: {'✅ YES' if timings_match else '❌ NO'}")
    print(f"Bytes match: {'✅ YES' if bytes_match else '❌ NO'}")
    print(f"State match: {'✅ YES' if state_match else '❌ NO'}")

    if not timings_match:
        print("\nTiming differences:")
        for i, (orig, reenc) in enumerate(zip(original_timings, reencoded_timings)):
            if orig != reenc:
                print(f"  Position {i}: {orig} → {reenc}")
                if i > 10:
                    print("  ...")
                    break

    if not bytes_match:
        print("\nByte differences:")
        for i, (orig, reenc) in enumerate(zip(original_bytes, reencoded_bytes)):
            if orig != reenc:
                print(f"  Byte {i}: 0x{orig:02X} → 0x{reenc:02X}")

test_code("OFF Command", OFF_CODE)
test_code("ON Command", ON_CODE)

print("\n" + "="*80)
print("Conclusion:")
print("="*80)
print("If timings and bytes match, GitHub's FastLZ is functionally correct.")
print("The Base64 difference is just due to different compression heuristics.")
print("Your AC should accept codes with different Base64 but identical timings.")
