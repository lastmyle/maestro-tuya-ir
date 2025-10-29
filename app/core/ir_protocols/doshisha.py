# Copyright 2020 Christian (nikize)
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Doshisha protocol support
## Direct translation from IRremoteESP8266 ir_Doshisha.cpp
## @see https://www.doshisha-led.com/

from typing import List

# Supports:
#   Brand: Doshisha,  Model: CZ-S32D LED Light
#   Brand: Doshisha,  Model: CZ-S38D LED Light
#   Brand: Doshisha,  Model: CZ-S50D LED Light
#   Brand: Doshisha,  Model: RCZ01 remote

# Constants - Timing values (from ir_Doshisha.cpp lines 17-21)
kDoshishaHdrMark = 3412
kDoshishaHdrSpace = 1722
kDoshishaBitMark = 420
kDoshishaOneSpace = 1310
kDoshishaZeroSpace = 452

# State length constants (from IRremoteESP8266.h)
kDoshishaBits = 40

# Default message gap (from IRremoteESP8266.h - standard value)
kDefaultMessageGap = 100000

# basic structure of bits, and mask (from ir_Doshisha.cpp lines 23-27)
kRcz01SignatureMask = 0xFFFFFFFF00
kRcz01Signature = 0x800B304800
kRcz01CommandMask = 0xFE
kRcz01ChannelMask = 0x01

# Known commands - Here for documentation rather than actual usage (from ir_Doshisha.cpp lines 29-45)
kRcz01CommandSwitchChannel = 0xD2
kRcz01CommandTimmer60 = 0x52
kRcz01CommandTimmer30 = 0x92
kRcz01CommandOff = 0xA0

kRcz01CommandLevelDown = 0x2C
kRcz01CommandLevelUp = 0xCC
# below are the only ones that turns it on
kRcz01CommandLevel1 = 0xA4
kRcz01CommandLevel2 = 0x24
kRcz01CommandLevel3 = 0xC4
kRcz01CommandLevel4 = 0xD0

kRcz01CommandOn = 0xC0
kRcz01CommandNightLight = 0xC8
# end Known commands


## Send a Doshisha formatted message.
## Status: STABLE / Works on real device.
## @param[in] data The message to be sent.
## @param[in] nbits The number of bits of message to be sent.
## @param[in] repeat The number of times the command is to be repeated.
## Direct translation from IRremoteESP8266 IRsend::sendDoshisha (ir_Doshisha.cpp lines 47-60)
def sendDoshisha(data: int, nbits: int = kDoshishaBits, repeat: int = 0) -> List[int]:
    """
    Send a Doshisha formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendDoshisha

    Returns timing array instead of transmitting via hardware.
    """
    # Import here to avoid circular import
    from app.core.ir_protocols.ir_send import sendGeneric

    kDutyDefault = 50

    return sendGeneric(
        headermark=kDoshishaHdrMark,
        headerspace=kDoshishaHdrSpace,
        onemark=kDoshishaBitMark,
        onespace=kDoshishaOneSpace,
        zeromark=kDoshishaBitMark,
        zerospace=kDoshishaZeroSpace,
        footermark=kDoshishaBitMark,
        data=data,
        nbits=nbits,
        MSBfirst=True,
    )


## Encode Doshisha combining constant values with command and channel.
## Status: STABLE / Working.
## @param[in] command The command code to be sent.
## @param[in] channel The one bit channel 0 for CH1 and 1 for CH2
## @return The corresponding Doshisha code.
## Direct translation from IRremoteESP8266 IRsend::encodeDoshisha (ir_Doshisha.cpp lines 62-72)
def encodeDoshisha(command: int, channel: int) -> int:
    """
    Encode Doshisha combining constant values with command and channel.
    EXACT translation from IRremoteESP8266 IRsend::encodeDoshisha
    """
    data = kRcz01Signature | (command & kRcz01CommandMask) | (channel & kRcz01ChannelMask)
    return data


## Decode the supplied Doshisha message.
## Status: STABLE / Works on real device.
## @param[in,out] results Ptr to the data to decode & where to store the decode
##   result.
## @param[in] offset The starting index to use when attempting to decode the
##   raw data. Typically/Defaults to kStartOffset.
## @param[in] nbits The number of data bits to expect.
## @param[in] strict Flag indicating if we should perform strict matching.
## @return A boolean. True if it can decode it, false if it can't.
## Direct translation from IRremoteESP8266 IRrecv::decodeDoshisha (ir_Doshisha.cpp lines 75-124)
def decodeDoshisha(
    results, offset: int = 1, nbits: int = kDoshishaBits, strict: bool = True
) -> bool:
    """
    Decode a Doshisha IR message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeDoshisha

    This is the ACTUAL C++ decoder function, not a wrapper.
    """
    # Import here to avoid circular imports
    from app.core.ir_protocols.ir_recv import (
        kHeader,
        kFooter,
        kMarkExcess,
        kTolerance,
        _matchGeneric,
    )

    if results.rawlen < 2 * nbits + kHeader + kFooter - 1 + offset:
        return False  # Can't possibly be a valid message.
    if strict and nbits != kDoshishaBits:
        return False

    data = 0
    # Match Header + Data
    if not _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=[data],
        result_bytes_ptr=None,
        use_bits=True,
        remaining=results.rawlen - offset,
        nbits=nbits,
        hdrmark=kDoshishaHdrMark,
        hdrspace=kDoshishaHdrSpace,
        onemark=kDoshishaBitMark,
        onespace=kDoshishaOneSpace,
        zeromark=kDoshishaBitMark,
        zerospace=kDoshishaZeroSpace,
        footermark=kDoshishaBitMark,
        footerspace=0,
        atleast=False,
        tolerance=kTolerance,
        excess=kMarkExcess,
        MSBfirst=True,
    ):
        return False

    # e.g. data = 0x800B3048C0, nbits = 40

    # RCZ01 remote commands starts with a lead bit set
    if (data & kRcz01SignatureMask) != kRcz01Signature:
        # DPRINT(" decodeDoshisha data ");
        # DPRINT(uint64ToString(data, 16));
        # DPRINT(" masked ");
        # DPRINT(uint64ToString(data & kRcz01SignatureMask, 16));
        # DPRINT(" not matching ");
        # DPRINT(uint64ToString(kRcz01Signature, 16));
        # DPRINTLN(" .");
        return False  # expected lead bits not matching

    # Success
    # results.decode_type = DOSHISHA  # Would set protocol type in C++
    results.bits = nbits
    results.value = data
    results.command = data & kRcz01CommandMask
    results.address = data & kRcz01ChannelMask
    return True
