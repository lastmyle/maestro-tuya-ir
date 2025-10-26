"""
FastLZ compression/decompression implementation for Tuya IR codes.

Note: This is a pure Python implementation based on:
https://gist.github.com/mildsunrise/1d576669b63a260d2cff35fda63ec0b5

Alternative: pyfastlz (https://pypi.org/project/pyfastlz/) is a C-based implementation
that offers better performance, but has limited platform support (no ARM64 macOS).

If pyfastlz is available and works on your platform, you can install it with:
    uv add pyfastlz

And update this module to use it:
    import pyfastlz
    fastlz_decompress = pyfastlz.decompress
    fastlz_compress = pyfastlz.compress
"""


def fastlz_decompress(data: bytes) -> bytes:
    """
    Decompress FastLZ compressed data.
    Tuya uses FastLZ for IR code compression.

    Args:
        data: Compressed bytes

    Returns:
        Decompressed bytes

    Raises:
        ValueError: If data is corrupted or invalid
    """
    if not data:
        return b""

    output = bytearray()
    ip = 0  # input pointer

    while ip < len(data):
        ctrl = data[ip]
        ip += 1

        if ctrl < 32:
            # Literal run
            ctrl += 1
            if ip + ctrl > len(data):
                raise ValueError("Corrupted data: literal run exceeds input")
            output.extend(data[ip : ip + ctrl])
            ip += ctrl
        else:
            # Back reference
            length = ctrl >> 5
            if length == 7:
                if ip >= len(data):
                    raise ValueError("Corrupted data: extended length byte missing")
                length += data[ip]
                ip += 1
            length += 2

            if ip >= len(data):
                raise ValueError("Corrupted data: reference offset byte missing")

            ref = (ctrl & 31) << 8
            ref += data[ip]
            ip += 1

            # Copy from reference
            ref_pos = len(output) - ref - 1
            if ref_pos < 0:
                raise ValueError("Corrupted data: invalid back reference")

            for _ in range(length):
                if ref_pos >= len(output):
                    raise ValueError("Corrupted data: reference position out of bounds")
                output.append(output[ref_pos])
                ref_pos += 1

    return bytes(output)


def fastlz_compress(data: bytes) -> bytes:
    """
    Compress data using FastLZ algorithm.
    Tuya uses FastLZ for IR code compression.

    Args:
        data: Raw bytes to compress

    Returns:
        Compressed bytes

    Note:
        This is a simplified implementation focusing on decompression compatibility.
        For production use, consider using a more optimized C-based implementation.
    """
    if not data:
        return b""

    output = bytearray()
    ip = 0  # input pointer
    anchor = 0  # anchor for literal run

    # Hash table for finding matches (simple implementation)
    hash_table = {}

    while ip < len(data):
        # Try to find a match
        best_match_len = 0
        best_match_dist = 0

        if ip + 3 <= len(data):
            # Create hash of current position
            hash_val = (data[ip] << 16) | (data[ip + 1] << 8) | data[ip + 2]

            if hash_val in hash_table:
                match_pos = hash_table[hash_val]
                # Check if match is within reference distance (8192 bytes)
                if ip - match_pos < 8192:
                    # Calculate match length
                    match_len = 0
                    max_len = min(len(data) - ip, 264)  # Max match length
                    while (
                        match_len < max_len
                        and match_pos + match_len < ip
                        and data[match_pos + match_len] == data[ip + match_len]
                    ):
                        match_len += 1

                    if match_len >= 3:
                        best_match_len = match_len
                        best_match_dist = ip - match_pos - 1

            hash_table[hash_val] = ip

        if best_match_len >= 3:
            # Output literal run if any
            literal_len = ip - anchor
            if literal_len > 0:
                while literal_len > 0:
                    run = min(literal_len, 32)
                    output.append(run - 1)
                    output.extend(data[anchor : anchor + run])
                    anchor += run
                    literal_len -= run

            # Output back reference
            length = best_match_len - 2
            if length < 7:
                ctrl = (length << 5) | ((best_match_dist >> 8) & 31)
                output.append(ctrl)
                output.append(best_match_dist & 255)
            else:
                ctrl = (7 << 5) | ((best_match_dist >> 8) & 31)
                output.append(ctrl)
                output.append(length - 7)
                output.append(best_match_dist & 255)

            ip += best_match_len
            anchor = ip
        else:
            ip += 1

    # Output remaining literal run
    literal_len = len(data) - anchor
    while literal_len > 0:
        run = min(literal_len, 32)
        output.append(run - 1)
        output.extend(data[anchor : anchor + run])
        anchor += run
        literal_len -= run

    return bytes(output)
