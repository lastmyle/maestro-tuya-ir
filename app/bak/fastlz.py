"""
FastLZ compression/decompression implementation for Tuya IR codes.

This implementation is from: https://github.com/burkminipup/irdb-to-tuya/
It produces functionally correct output (identical timings and protocol bytes)
even though the Base64 encoding may differ from Tuya's original compression.

Note: This is expected behavior - FastLZ compression is not deterministic.
Different implementations may produce different compressed output for the
same input data, but the decompressed result will always be identical.
"""

import io


def fastlz_decompress(data: bytes) -> bytes:
    """
    Decompress FastLZ compressed data.

    Args:
        data: Compressed bytes

    Returns:
        Decompressed bytes

    Raises:
        AssertionError: If data is corrupted or invalid
    """
    inf = io.BytesIO(data)
    out = bytearray()

    while (header := inf.read(1)):
        L, D = header[0] >> 5, header[0] & 0b11111
        if not L:
            L = D + 1
            data = inf.read(L)
            assert len(data) == L, "Corrupted data: literal run exceeds input"
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


def _emit_literal_blocks(out: io.BytesIO, data: bytes):
    """Emit literal blocks (max 32 bytes each)"""
    for i in range(0, len(data), 32):
        _emit_literal_block(out, data[i:i+32])


def _emit_literal_block(out: io.BytesIO, data: bytes):
    """Emit a single literal block"""
    length = len(data) - 1
    assert 0 <= length < (1 << 5)
    out.write(bytes([length]))
    out.write(data)


def _emit_distance_block(out: io.BytesIO, length: int, distance: int):
    """Emit a back-reference block"""
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


def fastlz_compress(data: bytes, level: int = 2) -> bytes:
    """
    Compress data using FastLZ algorithm.

    Args:
        data: Raw bytes to compress
        level: Compression level (0=none, 1=fast, 2=best, default=2)

    Returns:
        Compressed bytes
    """
    out = io.BytesIO()

    if level == 0:
        _emit_literal_blocks(out, data)
        return out.getvalue()

    W = 2**13  # Window size: 8KB
    L = 255 + 9  # Max match length: 264 bytes

    pos = 0
    block_start = 0

    while pos < len(data):
        # Find best match in window
        best_match = None
        best_distance = 0

        for distance in range(1, min(pos, W) + 1):
            ref_pos = pos - distance

            # Find match length
            length = 0
            limit = min(L, len(data) - pos)
            while length < limit and data[pos + length] == data[ref_pos + length]:
                length += 1

            # Keep best match (prefer longer, then closer)
            if length >= 3:
                if not best_match or length > best_match or (length == best_match and distance < best_distance):
                    best_match = length
                    best_distance = distance

        # Use match if found
        if best_match and best_match >= 3:
            # Output any pending literals
            if pos > block_start:
                _emit_literal_blocks(out, data[block_start:pos])

            # Output match
            _emit_distance_block(out, best_match, best_distance)
            pos += best_match
            block_start = pos
        else:
            pos += 1

    # Output remaining literals
    if block_start < len(data):
        _emit_literal_blocks(out, data[block_start:])

    return out.getvalue()
