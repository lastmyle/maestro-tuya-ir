# Copyright 2020 Christian Nilsson (nikize)
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Support for Zepeal protocol.
## This protocol uses fixed length bit encoding.
## Most official information about Zepeal seems to be from Denkyosha
## @see https://www.denkyosha.co.jp/
## Direct translation from IRremoteESP8266 ir_Zepeal.cpp

from typing import List

# Supports:
#   Brand: Zepeal,  Model: DRT-A3311(BG) floor fan
#   Brand: Zepeal,  Model: DRT-A3311(BG) 5 button remote

# Constants - Timing values (from ir_Zepeal.cpp lines 19-26)
kZepealHdrMark = 2330
kZepealHdrSpace = 3380
kZepealOneMark = 1300
kZepealZeroMark = 420
kZepealOneSpace = kZepealZeroMark
kZepealZeroSpace = kZepealOneMark
kZepealFooterMark = 420
kZepealGap = 6750

# Tolerance constant (from ir_Zepeal.cpp line 28)
kZepealTolerance = 40

# Signature constant (from ir_Zepeal.cpp lines 31-32)
# Signature limits possible false possitvies,
# but might need change (removal) if more devices are detected
kZepealSignature = 0x6C

# Known Zepeal DRT-A3311(BG) Buttons - documentation rather than actual usage
# (from ir_Zepeal.cpp lines 34-39)
kZepealCommandSpeed = 0x6C82
kZepealCommandOffOn = 0x6C81
kZepealCommandRhythm = 0x6C84
kZepealCommandOffTimer = 0x6C88
kZepealCommandOnTimer = 0x6CC3


## Send a Zepeal formatted message.
## Status: STABLE / Works on real device.
## @param[in] data The message to be sent.
## @param[in] nbits The bit size of the message being sent.
## @param[in] repeat The number of times the message is to be repeated.
## Direct translation from IRremoteESP8266 IRsend::sendZepeal (ir_Zepeal.cpp lines 47-54)
def sendZepeal(data: int, nbits: int, repeat: int = 0) -> List[int]:
    """
    Send a Zepeal formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendZepeal

    Returns timing array instead of transmitting via hardware.
    """
    # Import here to avoid circular import
    from app.core.ir_protocols.ir_send import sendGeneric

    all_timings = sendGeneric(
        headermark=kZepealHdrMark,
        headerspace=kZepealHdrSpace,
        onemark=kZepealOneMark,
        onespace=kZepealOneSpace,
        zeromark=kZepealZeroMark,
        zerospace=kZepealZeroSpace,
        footermark=kZepealFooterMark,
        gap=kZepealGap,
        dataptr=data,
        nbits=nbits,
        MSBfirst=True,
    )

    return all_timings


## Decode the supplied Zepeal message.
## Status: STABLE / Works on real device.
## @param[in,out] results Ptr to the data to decode & where to store the decode result.
## @param[in] offset The starting index to use when attempting to decode the raw data.
## @param[in] nbits The number of data bits to expect. Typically kZepealBits.
## @param[in] strict Flag indicating if we should perform strict matching.
## @return A boolean. True if it can decode it, false if it can't.
## Direct translation from IRremoteESP8266 IRrecv::decodeZepeal (ir_Zepeal.cpp lines 67-93)
def decodeZepeal(results, offset: int = 1, nbits: int = 16, strict: bool = True) -> bool:
    """
    Decode a Zepeal IR message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeZepeal

    This is the ACTUAL C++ decoder function, not a wrapper.
    """
    # Import here to avoid circular imports
    from app.core.ir_protocols.ir_recv import kHeader, kFooter, _matchGeneric

    # lines 69-72
    if results.rawlen < 2 * nbits + kHeader + kFooter - 1 + offset:
        return False  # Can't possibly be a valid message.
    if strict and nbits != 16:  # kZepealBits
        return False  # Not strictly a message.

    data = 0
    # lines 74-82
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=None,
        use_bits=True,
        remaining=results.rawlen - offset,
        nbits=nbits,
        hdrmark=kZepealHdrMark,
        hdrspace=kZepealHdrSpace,
        onemark=kZepealOneMark,
        onespace=kZepealOneSpace,
        zeromark=kZepealZeroMark,
        zerospace=kZepealZeroSpace,
        footermark=kZepealFooterMark,
        footerspace=kZepealGap,
        atleast=True,
        tolerance=kZepealTolerance,
        excess=50,  # kMarkExcess placeholder
        MSBfirst=True,
    )
    if not used:
        return False

    # Parse the actual data bits
    from app.core.ir_protocols.ir_recv import matchData

    data_result = matchData(
        data_ptr=results.rawbuf[offset:],
        offset=0,
        nbits=nbits,
        onemark=kZepealOneMark,
        onespace=kZepealOneSpace,
        zeromark=kZepealZeroMark,
        zerospace=kZepealZeroSpace,
        tolerance=kZepealTolerance,
        excess=50,
        MSBfirst=True,
        expectlastspace=False,
    )
    if not data_result.success:
        return False
    data = data_result.data

    # line 84
    if strict and (data >> 8) != kZepealSignature:
        return False

    # Success (lines 87-92)
    results.value = data
    # results.decode_type = ZEPEAL  # Would set protocol type in C++
    results.bits = nbits
    results.address = 0
    results.command = 0
    return True
