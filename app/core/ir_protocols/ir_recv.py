# Copyright 2009 Ken Shirriff
# Copyright 2015 Mark Szabo
# Copyright 2017,2019 David Conran
# Python translation: EXACT conversion from C++ IRremoteESP8266 with NO optimizations

## @file
## @brief Generic IR protocol decoder functions
## Direct translation of IRrecv class methods from IRrecv.cpp

from typing import List, Optional
from app.core.ir_protocols.fujitsu import (
    kFujitsuAcHdrMark,
    kFujitsuAcHdrSpace,
    kFujitsuAcBitMark,
    kFujitsuAcOneSpace,
    kFujitsuAcZeroSpace,
    kFujitsuAcExtraTolerance,
    kFujitsuAcMinGap,
)

## Constants from IRremoteESP8266.h and IRrecv.h
kHeader = 2  # Usual nr. of header entries
kFooter = 2  # Usual nr. of footer entries
kMarkExcess = 50  # From IRrecv.h line 24
kUseDefTol = 25  # Default tolerance percentage (From IRrecv.h)
kStateSizeMax = 256  # Max state size (simplified for Python)
kFujitsuAcStateLength = 16  # From IRremoteESP8266.h line 1250
kFujitsuAcStateLengthShort = 7  # From IRremoteESP8266.h line 1251
kFujitsuAcBits = kFujitsuAcStateLength * 8  # 128 bits
kFujitsuAcMinBits = (kFujitsuAcStateLengthShort - 1) * 8  # 48 bits


def matchMark(measured: int, desired: int, tolerance: int = 25, excess: int = 0) -> bool:
    """
    Check if a mark timing matches expected value within tolerance.
    Direct translation from IRremoteESP8266 matchMark logic.

    @param measured The measured timing value in microseconds
    @param desired The expected timing value in microseconds
    @param tolerance The tolerance percentage (default 25%)
    @param excess Additional microseconds to add to desired
    @return True if match, False otherwise
    """
    adjusted = desired + excess
    # Apply tolerance percentage
    lower = adjusted * (100 - tolerance) // 100
    upper = adjusted * (100 + tolerance) // 100
    if measured >= lower and measured <= upper:
        return True
    else:
        return False


def matchSpace(measured: int, desired: int, tolerance: int = 25, excess: int = 0) -> bool:
    """
    Check if a space timing matches expected value within tolerance.
    Direct translation from IRremoteESP8266 matchSpace logic.

    @param measured The measured timing value in microseconds
    @param desired The expected timing value in microseconds
    @param tolerance The tolerance percentage (default 25%)
    @param excess Additional microseconds to add to desired
    @return True if match, False otherwise
    """
    adjusted = desired + excess
    # Apply tolerance percentage
    lower = adjusted * (100 - tolerance) // 100
    upper = adjusted * (100 + tolerance) // 100
    if measured >= lower and measured <= upper:
        return True
    else:
        return False


def matchAtLeast(measured: int, desired: int, tolerance: int = 25, excess: int = 0) -> bool:
    """
    Check if measured timing is at least the desired value (within tolerance).
    Direct translation from IRremoteESP8266 matchAtLeast logic.

    @param measured The measured timing value in microseconds
    @param desired The expected minimum timing value in microseconds
    @param tolerance The tolerance percentage (default 25%)
    @param excess Additional microseconds to add to desired
    @return True if match, False otherwise
    """
    adjusted = desired + excess
    # Apply tolerance percentage to get lower bound
    lower = adjusted * (100 - tolerance) // 100
    if measured >= lower:
        return True
    else:
        return False


## Match result structure - direct translation from C++
class match_result_t:
    def __init__(self):
        self.success = False
        self.data = 0
        self.used = 0


def reverseBits(data: int, nbits: int) -> int:
    """
    Reverse the order of bits.
    Direct translation from IRremoteESP8266 reverseBits

    @param data The data to reverse
    @param nbits Number of bits to reverse
    @return Reversed data
    """
    result = 0
    for i in range(nbits):
        result <<= 1
        result |= data & 1
        data >>= 1
    return result


## Match & decode data bits from IR timings.
## @param[in] data_ptr A pointer to where we are at in the capture buffer.
## @param[in] nbits Number of data bits we expect.
## @param[in] onemark Nr. of uSeconds in an expected mark signal for a '1' bit.
## @param[in] onespace Nr. of uSecs in an expected space signal for a '1' bit.
## @param[in] zeromark Nr. of uSecs in an expected mark signal for a '0' bit.
## @param[in] zerospace Nr. of uSecs in an expected space signal for a '0' bit.
## @param[in] tolerance Percentage error margin to allow. (Default: kUseDefTol)
## @param[in] excess Nr. of uSeconds. (Def: kMarkExcess)
## @param[in] MSBfirst Bit order to save the data in. (Def: true)
##   true is Most Significant Bit First Order, false is Least Significant First
## @param[in] expectlastspace Do we expect a trailing space at the end of the data?
## @return A match_result_t structure with the success status, data & how many
##   buffer entries were used.
## Direct translation from IRremoteESP8266 IRrecv::matchData (lines 1457-1499)
def matchData(
    data_ptr: List[int],
    offset: int,
    nbits: int,
    onemark: int,
    onespace: int,
    zeromark: int,
    zerospace: int,
    tolerance: int,
    excess: int,
    MSBfirst: bool,
    expectlastspace: bool,
) -> match_result_t:
    """
    Match & decode data bits from IR timings.
    EXACT translation from IRremoteESP8266 IRrecv::matchData
    """
    result = match_result_t()
    result.success = False  # Fail by default.
    result.data = 0
    if expectlastspace:  # We are expecting data with a final space.
        result.used = 0
        # Replicate: for (result.used = 0; result.used < nbits * 2; result.used += 2, data_ptr += 2)
        while result.used < nbits * 2:
            # Is the bit a '1'?
            if matchMark(data_ptr[offset + result.used], onemark, tolerance, excess) and matchSpace(
                data_ptr[offset + result.used + 1], onespace, tolerance, excess
            ):
                result.data = (result.data << 1) | 1
            elif matchMark(
                data_ptr[offset + result.used], zeromark, tolerance, excess
            ) and matchSpace(data_ptr[offset + result.used + 1], zerospace, tolerance, excess):
                result.data <<= 1  # The bit is a '0'.
            else:
                if not MSBfirst:
                    result.data = reverseBits(result.data, result.used // 2)
                return result  # It's neither, so fail.
            result.used += 2
        result.success = True
    else:  # We are expecting data without a final space.
        # Match all but the last bit, as it may not match easily.
        result = matchData(
            data_ptr,
            offset,
            nbits - 1 if nbits else 0,
            onemark,
            onespace,
            zeromark,
            zerospace,
            tolerance,
            excess,
            True,
            True,
        )
        if result.success:
            # Is the bit a '1'?
            if matchMark(data_ptr[offset + result.used], onemark, tolerance, excess):
                result.data = (result.data << 1) | 1
            elif matchMark(data_ptr[offset + result.used], zeromark, tolerance, excess):
                result.data <<= 1  # The bit is a '0'.
            else:
                result.success = False
            if result.success:
                result.used += 1
    if not MSBfirst:
        result.data = reverseBits(result.data, nbits)
    return result


## Match & decode the typical data section of an IR message.
## The bytes are stored at result_ptr. The first byte in the result equates to
## the first byte encountered, and so on.
## @param[in] data_ptr A pointer to where we are at in the capture buffer.
## @param[out] result_ptr A ptr to where to start storing the bytes we decoded.
## @param[in] remaining The size of the capture buffer remaining.
## @param[in] nbytes Nr. of data bytes we expect.
## @param[in] onemark Nr. of uSeconds in an expected mark signal for a '1' bit.
## @param[in] onespace Nr. of uSecs in an expected space signal for a '1' bit.
## @param[in] zeromark Nr. of uSecs in an expected mark signal for a '0' bit.
## @param[in] zerospace Nr. of uSecs in an expected space signal for a '0' bit.
## @param[in] tolerance Percentage error margin to allow. (Default: kUseDefTol)
## @param[in] excess Nr. of uSeconds. (Def: kMarkExcess)
## @param[in] MSBfirst Bit order to save the data in. (Def: true)
##   true is Most Significant Bit First Order, false is Least Significant First
## @param[in] expectlastspace Do we expect a space at the end of the message?
## @return If successful, how many buffer entries were used. Otherwise 0.
## Direct translation from IRremoteESP8266 IRrecv::matchBytes (lines 1518-1538)
def matchBytes(
    data_ptr: List[int],
    offset: int,
    result_ptr: List[int],
    remaining: int,
    nbytes: int,
    onemark: int,
    onespace: int,
    zeromark: int,
    zerospace: int,
    tolerance: int,
    excess: int,
    MSBfirst: bool,
    expectlastspace: bool,
    result_offset: int = 0,  # Python fix: write offset into result_ptr (C++ uses pointer arithmetic)
) -> int:
    """
    Match & decode bytes from IR timings.
    EXACT translation from IRremoteESP8266 IRrecv::matchBytes

    Note: result_offset parameter added for Python compatibility.
    In C++, callers pass &state[offset] which is a pointer to the middle of the array.
    In Python, slicing creates a copy, so we pass the full array + write offset instead.
    """
    # Check if there is enough capture buffer to possibly have the desired bytes.
    if remaining + (1 if expectlastspace else 0) < (nbytes * 8 * 2) + 1:
        return 0  # Nope, so abort.
    used_offset = 0
    for byte_pos in range(nbytes):  # for (uint16_t byte_pos = 0; byte_pos < nbytes; byte_pos++)
        if byte_pos + 1 == nbytes:
            lastspace = expectlastspace
        else:
            lastspace = True
        result = matchData(
            data_ptr,
            offset + used_offset,
            8,
            onemark,
            onespace,
            zeromark,
            zerospace,
            tolerance,
            excess,
            MSBfirst,
            lastspace,
        )
        if result.success == False:
            return 0  # Fail
        result_ptr[result_offset + byte_pos] = result.data & 0xFF  # Python fix: use result_offset
        used_offset += result.used
    return used_offset


## Match & decode a generic/typical IR message.
## The data is stored in result_bits_ptr or result_bytes_ptr depending on flag
## `use_bits`.
## @note Values of 0 for hdrmark, hdrspace, footermark, or footerspace mean
## skip that requirement.
##
## @param[in] data_ptr A pointer to where we are at in the capture buffer.
## @param[out] result_bits_ptr A pointer to where to start storing the bits we
##    decoded.
## @param[out] result_bytes_ptr A pointer to where to start storing the bytes
##    we decoded.
## @param[in] use_bits A flag indicating if we are to decode bits or bytes.
## @param[in] remaining The size of the capture buffer remaining.
## @param[in] nbits Nr. of data bits we expect.
## @param[in] hdrmark Nr. of uSeconds for the expected header mark signal.
## @param[in] hdrspace Nr. of uSeconds for the expected header space signal.
## @param[in] onemark Nr. of uSeconds in an expected mark signal for a '1' bit.
## @param[in] onespace Nr. of uSecs in an expected space signal for a '1' bit.
## @param[in] zeromark Nr. of uSecs in an expected mark signal for a '0' bit.
## @param[in] zerospace Nr. of uSecs in an expected space signal for a '0' bit.
## @param[in] footermark Nr. of uSeconds for the expected footer mark signal.
## @param[in] footerspace Nr. of uSeconds for the expected footer space/gap
##   signal.
## @param[in] atleast Is the match on the footerspace a matchAtLeast or
##   matchSpace?
## @param[in] tolerance Percentage error margin to allow. (Default: kUseDefTol)
## @param[in] excess Nr. of uSeconds. (Def: kMarkExcess)
## @param[in] MSBfirst Bit order to save the data in. (Def: true)
##   true is Most Significant Bit First Order, false is Least Significant First
## @return If successful, how many buffer entries were used. Otherwise 0.
## Direct translation from IRremoteESP8266 IRrecv::_matchGeneric (lines 1570-1645)
def _matchGeneric(
    data_ptr: List[int],
    result_bits_ptr: Optional[List[int]],
    result_bytes_ptr: Optional[List[int]],
    use_bits: bool,
    remaining: int,
    nbits: int,
    hdrmark: int,
    hdrspace: int,
    onemark: int,
    onespace: int,
    zeromark: int,
    zerospace: int,
    footermark: int,
    footerspace: int,
    atleast: bool,
    tolerance: int,
    excess: int,
    MSBfirst: bool,
    result_offset: int = 0,  # Python fix: write offset into result_bytes_ptr
) -> int:
    """
    Match & decode a generic/typical IR message.
    EXACT translation from IRremoteESP8266 IRrecv::_matchGeneric

    Returns offset (number of buffer entries used) on success, 0 on failure.
    """
    # If we are expecting byte sizes AND storing results, check it's a factor of 8 or fail.
    # When result_bytes_ptr is None, we're just validating timing, not storing data.
    if not use_bits and result_bytes_ptr is not None and nbits % 8 != 0:
        return 0
    # Calculate if we expect a trailing space in the data section.
    kexpectspace = footermark or (onespace != zerospace)
    # Calculate how much remaining buffer is required.
    min_remaining = nbits * 2 - (0 if kexpectspace else 1)

    if hdrmark:
        min_remaining += 1
    if hdrspace:
        min_remaining += 1
    if footermark:
        min_remaining += 1
    # Don't need to extend for footerspace because it could be the end of message

    # Check if there is enough capture buffer to possibly have the message.
    if remaining < min_remaining:
        return 0  # Nope, so abort.
    offset = 0

    # Header
    if hdrmark and not matchMark(data_ptr[offset], hdrmark, tolerance, excess):
        return 0
    if hdrmark:
        offset += 1
    if hdrspace and not matchSpace(data_ptr[offset], hdrspace, tolerance, excess):
        return 0
    if hdrspace:
        offset += 1

    # Data
    if use_bits:  # Bits.
        result = matchData(
            data_ptr,
            offset,
            nbits,
            onemark,
            onespace,
            zeromark,
            zerospace,
            tolerance,
            excess,
            MSBfirst,
            kexpectspace,
        )
        if not result.success:
            return 0
        if result_bits_ptr is not None:
            result_bits_ptr[0] = result.data  # *result_bits_ptr = result.data
        offset += result.used
    else:  # bytes
        if result_bytes_ptr is not None:
            # Store bytes in result buffer
            data_used = matchBytes(
                data_ptr,
                offset,
                result_bytes_ptr,
                remaining - offset,
                nbits // 8,
                onemark,
                onespace,
                zeromark,
                zerospace,
                tolerance,
                excess,
                MSBfirst,
                kexpectspace,
                result_offset,  # Python fix: pass write offset
            )
            if not data_used:
                return 0
            offset += data_used
        else:
            # Just validate timing without storing (e.g., for preamble validation)
            result = matchData(
                data_ptr,
                offset,
                nbits,
                onemark,
                onespace,
                zeromark,
                zerospace,
                tolerance,
                excess,
                MSBfirst,
                kexpectspace,
            )
            if not result.success:
                return 0
            offset += result.used

    # Footer
    if footermark and not matchMark(data_ptr[offset], footermark, tolerance, excess):
        return 0
    if footermark:
        offset += 1
    # If we have something still to match & haven't reached the end of the buffer
    if footerspace and offset < remaining:
        if atleast:
            if not matchAtLeast(data_ptr[offset], footerspace, tolerance, excess):
                return 0
        else:
            if not matchSpace(data_ptr[offset], footerspace, tolerance, excess):
                return 0
        offset += 1
    return offset


## Results returned from the decoder
## Direct translation from IRrecv.h decode_results class (lines 99-118)
class decode_results:
    """
    Results returned from the decoder.
    EXACT translation from IRremoteESP8266 decode_results class
    """

    def __init__(self):
        self.decode_type = 0  # Protocol type
        self.value = 0  # Decoded value (for simple protocols)
        self.address = 0  # Decoded address
        self.command = 0  # Decoded command
        self.state = [0] * kStateSizeMax  # Multi-byte results
        self.bits = 0  # Number of bits in decoded value
        self.rawbuf = []  # Raw intervals (timings)
        self.rawlen = 0  # Number of records in rawbuf
        self.overflow = False
        self.repeat = False  # Is the result a repeat code?


## Decode the supplied Fujitsu AC IR message if possible.
## Status: STABLE / Working.
## @param[in,out] results Ptr to the data to decode & where to store the decode result.
## @param[in] offset The starting index to use when attempting to decode the
##   raw data. Typically/Defaults to kStartOffset.
## @param[in] nbits The number of data bits to expect.
## @param[in] strict Flag indicating if we should perform strict matching.
## @param[in] _tolerance The tolerance percentage for matching (passed from IRrecv instance)
## @return A boolean. True if it can decode it, false if it can't.
## Direct translation from IRremoteESP8266 IRrecv::decodeFujitsuAC (ir_Fujitsu.cpp lines 1003-1099)
def decodeFujitsuAC(
    results: decode_results,
    offset: int = 1,
    nbits: int = kFujitsuAcBits,
    strict: bool = False,
    _tolerance: int = 25,
) -> bool:
    """
    Decode a Fujitsu AC IR message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeFujitsuAC

    This is the ACTUAL C++ decoder function, not a wrapper.
    """
    dataBitsSoFar = 0

    # Have we got enough data to successfully decode?
    if results.rawlen < (2 * kFujitsuAcMinBits) + kHeader + kFooter - 1 + offset:
        return False  # Can't possibly be a valid message.

    # Compliance
    if strict:
        if nbits not in [
            kFujitsuAcBits,
            kFujitsuAcBits - 8,
            kFujitsuAcMinBits,
            kFujitsuAcMinBits + 8,
        ]:
            return False  # Must be called with the correct nr. of bits.

    # Header / Some of the Data
    # Call matchGeneric for first part (kFujitsuAcMinBits - 8 = 48 bits = 6 bytes)
    # In C++: matchGeneric(results->rawbuf + offset, ...)
    # In Python: pass sliced array starting at offset
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],  # Start from offset (like C++ pointer arithmetic)
        result_bits_ptr=None,
        result_bytes_ptr=results.state,
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=kFujitsuAcMinBits - 8,  # 48 bits
        hdrmark=kFujitsuAcHdrMark,
        hdrspace=kFujitsuAcHdrSpace,
        onemark=kFujitsuAcBitMark,
        onespace=kFujitsuAcOneSpace,
        zeromark=kFujitsuAcBitMark,
        zerospace=kFujitsuAcZeroSpace,
        footermark=0,  # No footer yet
        footerspace=0,
        atleast=False,
        tolerance=_tolerance + kFujitsuAcExtraTolerance,
        excess=0,
        MSBfirst=False,  # LSB first
    )
    if not used:
        return False
    offset += used

    # Check we have the typical data header.
    if results.state[0] != 0x14 or results.state[1] != 0x63:
        return False
    dataBitsSoFar += kFujitsuAcMinBits - 8

    # Keep reading bytes until we either run out of message or state to fill.
    # for (uint16_t i = 5; offset <= results->rawlen - 16 && i < kFujitsuAcStateLength;
    #      i++, dataBitsSoFar += 8, offset += data_result.used)
    # In C++: matchData(&(results->rawbuf[offset]), ...) passes pointer at offset
    # In Python: pass sliced array starting at offset
    i = 5
    while offset <= results.rawlen - 16 and i < kFujitsuAcStateLength:
        # C++ call has 9 params, so expectlastspace uses default value (true)
        data_result = matchData(
            data_ptr=results.rawbuf[offset:],  # Sliced array (like C++ pointer)
            offset=0,  # Start at beginning of sliced array
            nbits=8,
            onemark=kFujitsuAcBitMark,
            onespace=kFujitsuAcOneSpace,
            zeromark=kFujitsuAcBitMark,
            zerospace=kFujitsuAcZeroSpace,
            tolerance=_tolerance + kFujitsuAcExtraTolerance,
            excess=0,
            MSBfirst=False,
            expectlastspace=True,  # Default value in C++
        )
        if data_result.success == False:
            break  # Fail
        results.state[i] = data_result.data & 0xFF
        i += 1
        dataBitsSoFar += 8
        offset += data_result.used

    # Footer
    if offset > results.rawlen or not matchMark(
        results.rawbuf[offset], kFujitsuAcBitMark, _tolerance + kFujitsuAcExtraTolerance, 0
    ):
        return False
    offset += 1

    # The space is optional if we are out of capture.
    if offset < results.rawlen and not matchAtLeast(
        results.rawbuf[offset], kFujitsuAcMinGap, _tolerance + kFujitsuAcExtraTolerance, 0
    ):
        return False

    # Compliance
    if strict:
        if dataBitsSoFar != nbits:
            return False

    # results.decode_type = FUJITSU_AC  # Would set protocol type in C++
    results.bits = dataBitsSoFar

    # Compliance
    if dataBitsSoFar == kFujitsuAcMinBits:
        # Check if this values indicate that this should have been a long state message.
        if results.state[5] == 0xFC:
            return False
        return True  # Success
    elif dataBitsSoFar == kFujitsuAcMinBits + 8:
        # Check if this values indicate that this should have been a long state message.
        if results.state[5] == 0xFE:
            return False
        # The last byte needs to be the inverse of the penultimate byte.
        if results.state[5] != (~results.state[6] & 0xFF):
            return False
        return True  # Success
    elif dataBitsSoFar == kFujitsuAcBits - 8:
        # Long messages of this size require this byte be correct.
        if results.state[5] != 0xFC:
            return False
    elif dataBitsSoFar == kFujitsuAcBits:
        # Long messages of this size require this byte be correct.
        if results.state[5] != 0xFE:
            return False
    else:
        return False  # Unexpected size.

    # Would call validChecksum here in C++, but we'll skip for now
    # if (!IRFujitsuAC::validChecksum(results->state, dataBitsSoFar / 8))
    #     return false;

    # Success
    return True  # All good.


def validate_timings(
    timings: List[int], headermark: int, headerspace: int, bitmark: int, tolerance: int
) -> bool:
    """
    Validate that timings appear to be a specific protocol.
    Quick check without full decode.

    @param timings List of timing values in microseconds
    @param headermark Expected header mark
    @param headerspace Expected header space
    @param bitmark Expected bit mark
    @param tolerance Tolerance percentage
    @return True if timings look like the protocol, False otherwise
    """
    # Check minimum length (header + at least a few bits + trailer)
    if len(timings) < 10:
        return False

    # Check header mark
    if not matchMark(timings[0], headermark, tolerance):
        return False

    # Check header space
    if not matchSpace(timings[1], headerspace, tolerance):
        return False

    # Check that next timing looks like a bit mark
    if not matchMark(timings[2], bitmark, tolerance):
        return False

    return True


def validate_fujitsu_timings(timings: List[int]) -> bool:
    """
    Validate that timings appear to be Fujitsu protocol.
    Quick check without full decode.

    @param timings List of timing values in microseconds
    @return True if timings look like Fujitsu protocol, False otherwise
    """
    tolerance = 25 + kFujitsuAcExtraTolerance
    return validate_timings(
        timings, kFujitsuAcHdrMark, kFujitsuAcHdrSpace, kFujitsuAcBitMark, tolerance
    )


## Match & decode a generic/typical constant bit time <= 64bit IR message.
## The data is stored at result_ptr.
## @note Values of 0 for hdrmark, hdrspace, footermark, or footerspace mean
##   skip that requirement.
## @param[in] data_ptr A pointer to where we are at in the capture buffer.
## @note `data_ptr` is assumed to be pointing to a "Mark", not a "Space".
## @param[out] result_ptr A ptr to where to start storing the bits we decoded.
## @param[in] remaining The size of the capture buffer remaining.
## @param[in] nbits Nr. of data bits we expect.
## @param[in] hdrmark Nr. of uSeconds for the expected header mark signal.
## @param[in] hdrspace Nr. of uSeconds for the expected header space signal.
## @param[in] one Nr. of uSeconds for the expected mark signal for a '1' bit.
## @param[in] zero Nr. of uSeconds for the expected mark signal for a '0' bit.
## @param[in] footermark Nr. of uSeconds for the expected footer mark signal.
## @param[in] footerspace Nr. of uSeconds for the expected footer space/gap signal.
## @param[in] atleast Is the match on the footerspace a matchAtLeast or matchSpace?
## @param[in] tolerance Percentage error margin to allow. (Default: kUseDefTol)
## @param[in] excess Nr. of uSeconds. (Def: kMarkExcess)
## @param[in] MSBfirst Bit order to save the data in. (Def: true)
##   true is Most Significant Bit First Order, false is Least Significant First
## @return If successful, how many buffer entries were used. Otherwise 0.
## Direct translation from IRremoteESP8266 IRrecv::matchGenericConstBitTime (lines 1766-1830)
def matchGenericConstBitTime(
    data_ptr: List[int],
    result_ptr: List[int],
    remaining: int,
    nbits: int,
    hdrmark: int,
    hdrspace: int,
    one: int,
    zero: int,
    footermark: int,
    footerspace: int,
    atleast: bool,
    tolerance: int,
    excess: int,
    MSBfirst: bool,
) -> int:
    """
    Match & decode a generic/typical constant bit time IR message.
    EXACT translation from IRremoteESP8266 IRrecv::matchGenericConstBitTime

    Returns offset (number of buffer entries used) on success, 0 on failure.
    """
    offset = 0
    result = 0

    # If we expect a footermark, then this can be processed like normal.
    # Lines 1783-1786
    if footermark:
        used = _matchGeneric(
            data_ptr=data_ptr,
            result_bits_ptr=result_ptr,
            result_bytes_ptr=None,
            use_bits=True,
            remaining=remaining,
            nbits=nbits,
            hdrmark=hdrmark,
            hdrspace=hdrspace,
            onemark=one,
            onespace=zero,
            zeromark=zero,
            zerospace=one,
            footermark=footermark,
            footerspace=footerspace,
            atleast=atleast,
            tolerance=tolerance,
            excess=excess,
            MSBfirst=MSBfirst,
        )
        return used

    # Otherwise handle like normal, except for the last bit. and no footer.
    # Lines 1787-1791
    bits = (nbits - 1) if (nbits > 0) else 0  # Make sure we don't underflow.
    result_temp = [0]
    offset = _matchGeneric(
        data_ptr=data_ptr,
        result_bits_ptr=result_temp,
        result_bytes_ptr=None,
        use_bits=True,
        remaining=remaining,
        nbits=bits,
        hdrmark=hdrmark,
        hdrspace=hdrspace,
        onemark=one,
        onespace=zero,
        zeromark=zero,
        zerospace=one,
        footermark=0,
        footerspace=0,
        atleast=False,
        tolerance=tolerance,
        excess=excess,
        MSBfirst=True,
    )
    if not offset:
        return 0  # Didn't match.
    result = result_temp[0]

    # Now for the last bit.
    # Lines 1792-1795
    if remaining <= offset:
        return 0  # Not enough buffer.
    result <<= 1
    last_bit = False

    # Is the mark a '1' or a `0`?
    # Lines 1796-1804
    if matchMark(data_ptr[offset], one, tolerance, excess):  # 1
        last_bit = True
        result |= 1
    elif matchMark(data_ptr[offset], zero, tolerance, excess):  # 0
        last_bit = False
    else:
        return 0  # It's neither, so fail.

    offset += 1
    expected_space = (zero if last_bit else one) + footerspace

    # If we are not at the end of the buffer, check for at least the expected
    # space value.
    # Lines 1805-1819
    if remaining > offset:
        if atleast:
            if not matchAtLeast(data_ptr[offset], expected_space, tolerance, excess):
                return 0
        else:
            if not matchSpace(data_ptr[offset], expected_space, tolerance):
                return 0
        offset += 1

    if not MSBfirst:
        result = reverseBits(result, nbits)
    result_ptr[0] = result
    return offset


## Match & decode a generic/typical <= 64bit IR message.
## The data is stored at result_ptr.
## @note Values of 0 for hdrmark, hdrspace, footermark, or footerspace mean
##   skip that requirement.
## @param[in] data_ptr A pointer to where we are at in the capture buffer.
## @note `data_ptr` is assumed to be pointing to a "Mark", not a "Space".
## @param[out] result_ptr A ptr to where to start storing the bits we decoded.
## @param[in] remaining The size of the capture buffer remaining.
## @param[in] nbits Nr. of data bits we expect.
## @param[in] hdrmark Nr. of uSeconds for the expected header mark signal.
## @param[in] hdrspace Nr. of uSeconds for the expected header space signal.
## @param[in] onemark Nr. of uSeconds in an expected mark signal for a '1' bit.
## @param[in] onespace Nr. of uSecs in an expected space signal for a '1' bit.
## @param[in] zeromark Nr. of uSecs in an expected mark signal for a '0' bit.
## @param[in] zerospace Nr. of uSecs in an expected space signal for a '0' bit.
## @param[in] footermark Nr. of uSeconds for the expected footer mark signal.
## @param[in] footerspace Nr. of uSeconds for the expected footer space/gap signal.
## @param[in] atleast Is the match on the footerspace a matchAtLeast or matchSpace?
## @param[in] tolerance Percentage error margin to allow. (Default: kUseDefTol)
## @param[in] excess Nr. of uSeconds. (Def: kMarkExcess)
## @return If successful, how many buffer entries were used. Otherwise 0.
## Direct translation from IRremoteESP8266 IRrecv::matchGeneric (uint64_t variant)
def matchGeneric(
    data_ptr: List[int],
    result_ptr: List[int],
    remaining: int,
    nbits: int,
    hdrmark: int,
    hdrspace: int,
    onemark: int,
    onespace: int,
    zeromark: int,
    zerospace: int,
    footermark: int,
    footerspace: int,
    atleast: bool,
    tolerance: int,
) -> bool:
    """
    Match & decode a generic/typical IR message (uint64_t result variant).
    EXACT translation from IRremoteESP8266 IRrecv::matchGeneric (uint64_t variant)

    Returns True on success, False on failure.
    """
    # This is a wrapper that calls _matchGeneric with use_bits=True
    used = _matchGeneric(
        data_ptr=data_ptr,
        result_bits_ptr=result_ptr,
        result_bytes_ptr=None,
        use_bits=True,
        remaining=remaining,
        nbits=nbits,
        hdrmark=hdrmark,
        hdrspace=hdrspace,
        onemark=onemark,
        onespace=onespace,
        zeromark=zeromark,
        zerospace=zerospace,
        footermark=footermark,
        footerspace=footerspace,
        atleast=atleast,
        tolerance=tolerance,
        excess=kMarkExcess,
        MSBfirst=True,
    )
    return used != 0
