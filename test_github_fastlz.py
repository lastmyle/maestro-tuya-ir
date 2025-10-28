#!/usr/bin/env python3
"""
Test GitHub repo's FastLZ compress/decompress with user's working codes
"""

import io
import base64
from struct import pack, unpack

# GitHub repo's implementation
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
    signal = [min(t, 65535) for t in signal]  # clamp any timing over 65535
    payload = b''.join(pack('<H', t) for t in signal)
    compress(out := io.BytesIO(), payload, compression_level)
    payload = out.getvalue()
    return base64.encodebytes(payload).decode('ascii').replace('\n', '')


# Test with user's working codes
OFF_CODE = "BvQMFwbeAb4gARFdAb4BlQTeAV0B3gGVBL4BXQFAAwHeAUADAZUEQANAD0ADAd4BQAMBlQRAA+ABD0ATAV0BQA/AA0APwAPAE0AHBd4BlQTeAUAHAL4gAQFdAUADAd4B4AMDAZUEQBNAAwHeAYADAb4B4AkTQBsBvgFAAwGVBEALAd4BQAcBlQSADwuVBN4BlQS+AZUE3gE="
ON_CODE = "BxoNDAbbAV8BQAMDtgGUBEAHAdsBgAcBtgGAA4APAZQE4AEP4A8TQBeAA+AFKwFfAcADgBcBlATADwLbAbYgAQFfAUADAdsBwAMBlARAD0ADAdsBwAMBlATgBwMAtuACEwG2AeADJwC2IAEBXwFAAwHbAeADAwC2IAEGXwG2AZQE22ADAV8BQAOADwFfAeADAwG2AUADQCcBXwGAAwC2IAEBXwFAAwHbAeAFAwG2AeADJ4APALYgB0AL4AEDALYgAQFfAUADAdsBwAkDQBdAA+AHG0ATQAPgExfgBx9ADwO2AZQEQDMDtgFfAYAHQA+AA4ALC18BtgGUBLYBtgG2AQ=="

print("="*80)
print("Testing GitHub repo's FastLZ with user's working codes")
print("="*80)

# Test OFF command
print("\n1. OFF Command - Decode and Re-encode")
print("-" * 80)
try:
    decoded = decode_ir(OFF_CODE)
    print(f"✅ Decoded successfully: {len(decoded)} timings")
    print(f"   First 10 timings: {decoded[:10]}")

    # Test with compression level 2 (default)
    reencoded_level2 = encode_ir(decoded, compression_level=2)
    match2 = "✅ MATCH" if reencoded_level2 == OFF_CODE else "❌ MISMATCH"
    print(f"\n   Level 2: {match2}")
    print(f"   Original:  {OFF_CODE[:60]}...")
    print(f"   Re-encoded: {reencoded_level2[:60]}...")

    # Test with compression level 1
    reencoded_level1 = encode_ir(decoded, compression_level=1)
    match1 = "✅ MATCH" if reencoded_level1 == OFF_CODE else "❌ MISMATCH"
    print(f"\n   Level 1: {match1}")
    print(f"   Original:  {OFF_CODE[:60]}...")
    print(f"   Re-encoded: {reencoded_level1[:60]}...")

    # Test with compression level 0 (no compression)
    reencoded_level0 = encode_ir(decoded, compression_level=0)
    match0 = "✅ MATCH" if reencoded_level0 == OFF_CODE else "❌ MISMATCH"
    print(f"\n   Level 0: {match0}")
    print(f"   Original:  {OFF_CODE[:60]}...")
    print(f"   Re-encoded: {reencoded_level0[:60]}...")

except Exception as e:
    print(f"❌ Error: {e}")

# Test ON command
print("\n\n2. ON Command - Decode and Re-encode")
print("-" * 80)
try:
    decoded = decode_ir(ON_CODE)
    print(f"✅ Decoded successfully: {len(decoded)} timings")
    print(f"   First 10 timings: {decoded[:10]}")

    # Test with compression level 2 (default)
    reencoded_level2 = encode_ir(decoded, compression_level=2)
    match2 = "✅ MATCH" if reencoded_level2 == ON_CODE else "❌ MISMATCH"
    print(f"\n   Level 2: {match2}")
    print(f"   Original:  {ON_CODE[:60]}...")
    print(f"   Re-encoded: {reencoded_level2[:60]}...")

    # Test with compression level 1
    reencoded_level1 = encode_ir(decoded, compression_level=1)
    match1 = "✅ MATCH" if reencoded_level1 == ON_CODE else "❌ MISMATCH"
    print(f"\n   Level 1: {match1}")
    print(f"   Original:  {ON_CODE[:60]}...")
    print(f"   Re-encoded: {reencoded_level1[:60]}...")

    # Test with compression level 0 (no compression)
    reencoded_level0 = encode_ir(decoded, compression_level=0)
    match0 = "✅ MATCH" if reencoded_level0 == ON_CODE else "❌ MISMATCH"
    print(f"\n   Level 0: {match0}")
    print(f"   Original:  {ON_CODE[:60]}...")
    print(f"   Re-encoded: {reencoded_level0[:60]}...")

except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*80)
print("Summary:")
print("="*80)
print("If any level matches, we can use that compression level for generating codes.")
print("If none match exactly, we need to test if AC accepts codes with different")
print("Base64 encoding but identical decompressed timings.")
