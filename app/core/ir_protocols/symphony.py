# Copyright 2020 David Conran
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Support for Symphony protocols.
## Direct translation from IRremoteESP8266 ir_Symphony.cpp and IRremoteESP8266.h
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/1057
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/1105
## @see https://www.alldatasheet.com/datasheet-pdf/pdf/124369/ANALOGICTECH/SM5021B.html

# Supports:
#   Brand: Symphony,  Model: Air Cooler 3Di
#   Brand: SamHop,    Model: SM3015 Fan Remote Control
#   Brand: SamHop,    Model: SM5021 Encoder chip
#   Brand: SamHop,    Model: SM5032 Decoder chip
#   Brand: Blyss,     Model: Owen-SW-5 3 Fan
#   Brand: Blyss,     Model: WP-YK8 090218 remote
#   Brand: Westinghouse,  Model: Ceiling fan
#   Brand: Westinghouse,  Model: 78095 Remote
#   Brand: Satellite Electronic,  Model: ID6 Remote
#   Brand: Satellite Electronic,  Model: JY199I Fan driver
#   Brand: Satellite Electronic,  Model: JY199I-L Fan driver
#   Brand: SilverCrest,  Model: SSVS 85 A1 Fan

# Known Codes:
#   SilverCrest SSVS 85 A1 Fan:
#     0x581 - On/Off
#     0x582 - Speed
#     0x584 - Mist
#     0x588 - Timer
#     0x590 - OSC

from typing import List

# Constants - From ir_Symphony.cpp lines 38-43
kSymphonyZeroMark = 400
kSymphonyZeroSpace = 1250
kSymphonyOneMark = kSymphonyZeroSpace
kSymphonyOneSpace = kSymphonyZeroMark
kSymphonyFooterGap = 4 * (kSymphonyZeroMark + kSymphonyZeroSpace)

# Constants - From IRremoteESP8266.h lines 1397-1398
kSymphonyBits = 12
kSymphonyDefaultRepeat = 3


## Send a Symphony packet.
## Status:  STABLE / Should be working.
## @param[in] data The message to be sent.
## @param[in] nbits The number of bits of message to be sent.
## @param[in] repeat The number of times the command is to be repeated.
## Direct translation from IRremoteESP8266 IRsend::sendSymphony (ir_Symphony.cpp lines 46-57)
def sendSymphony(data: int, nbits: int = kSymphonyBits, repeat: int = kSymphonyDefaultRepeat) -> List[int]:
    """
    Send a Symphony packet.
    EXACT translation from IRremoteESP8266 IRsend::sendSymphony

    Returns timing array instead of transmitting via hardware.
    """
    # Import here to avoid circular import
    from app.core.ir_protocols.ir_send import sendGenericUint64

    return sendGenericUint64(
        headermark=0,
        headerspace=0,
        onemark=kSymphonyOneMark,
        onespace=kSymphonyOneSpace,
        zeromark=kSymphonyZeroMark,
        zerospace=kSymphonyZeroSpace,
        footermark=0,
        gap=kSymphonyFooterGap,
        data=data,
        nbits=nbits,
        frequency=38,
        MSBfirst=True,
        repeat=repeat,
        dutycycle=50
    )


## Decode the supplied Symphony packet/message.
## Status: STABLE / Should be working.
## @param[in,out] results Ptr to the data to decode & where to store the result
## @param[in] offset The starting index to use when attempting to decode the
##   raw data. Typically/Defaults to kStartOffset.
## @param[in] nbits The number of data bits to expect.
## @param[in] strict Flag indicating if we should perform strict matching.
## @param[in] _tolerance The tolerance percentage for matching (default 25%)
## @return True if it can decode it, false if it can't.
## Direct translation from IRremoteESP8266 IRrecv::decodeSymphony (ir_Symphony.cpp lines 60-94)
def decodeSymphony(results, offset: int = 1, nbits: int = kSymphonyBits,
                   strict: bool = True, _tolerance: int = 25) -> bool:
    """
    Decode the supplied Symphony packet/message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeSymphony

    This is the ACTUAL C++ decoder function, not a wrapper.
    """
    # Import here to avoid circular imports
    from app.core.ir_protocols.ir_recv import matchGenericConstBitTime

    # Line 73: if (results->rawlen < 2 * nbits + offset - 1)
    if results.rawlen < 2 * nbits + offset - 1:
        return False  # Not enough entries to ever be SYMPHONY.

    # Compliance
    # Line 76: if (strict && nbits != kSymphonyBits) return false;
    if strict and nbits != kSymphonyBits:
        return False

    # Lines 78-85
    data = [0]  # Will hold result
    used = matchGenericConstBitTime(
        data_ptr=results.rawbuf[offset:],
        result_ptr=data,
        remaining=results.rawlen - offset,
        nbits=nbits,
        hdrmark=0,
        hdrspace=0,  # No Header
        one=kSymphonyOneMark,
        zero=kSymphonyZeroMark,
        footermark=0,
        footerspace=kSymphonyFooterGap,
        atleast=True,
        tolerance=_tolerance,
        excess=0,
        MSBfirst=True
    )
    if used == 0:
        return False

    # Success
    # Lines 88-93
    results.value = data[0]
    results.decode_type = "SYMPHONY"  # decode_type_t::SYMPHONY
    results.bits = nbits
    results.address = 0
    results.command = 0
    return True
