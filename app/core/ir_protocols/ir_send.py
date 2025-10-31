# Copyright 2009 Ken Shirriff
# Copyright 2015 Mark Szabo
# Copyright 2017,2019 David Conran
# Python translation: EXACT conversion from C++ IRremoteESP8266 with NO optimizations

## @file
## @brief Generic IR protocol encoder functions
## Direct translation of IRsend class methods from IRsend.cpp

from typing import List


## Generic method for sending data that is common to most protocols.
## Will send leading or trailing 0's if the nbits is larger than the number
## of bits in data.
## @param[in] onemark Nr. of usecs for the led to be pulsed for a '1' bit.
## @param[in] onespace Nr. of usecs for the led to be fully off for a '1' bit.
## @param[in] zeromark Nr. of usecs for the led to be pulsed for a '0' bit.
## @param[in] zerospace Nr. of usecs for the led to be fully off for a '0' bit.
## @param[in] data The data to be transmitted.
## @param[in] nbits Nr. of bits of data to be sent.
## @param[in] MSBfirst Flag for bit transmission order.
##   Defaults to MSB->LSB order.
## Direct translation from IRremoteESP8266 IRsend::sendData (lines 248-279)
def sendData(
    onemark: int,
    onespace: int,
    zeromark: int,
    zerospace: int,
    data: int,
    nbits: int,
    MSBfirst: bool,
) -> List[int]:
    """
    Encode data bits into IR timings.
    EXACT translation from IRremoteESP8266 IRsend::sendData
    """
    timings = []
    if nbits == 0:  # If we are asked to send nothing, just return.
        return timings
    if MSBfirst:  # Send the MSB first.
        # Send 0's until we get down to a bit size we can actually manage.
        while nbits > 64:  # sizeof(data) * 8
            timings.append(zeromark)
            timings.append(zerospace)
            nbits -= 1
        # Send the supplied data.
        mask = 1 << (nbits - 1)  # 1ULL << (nbits - 1)
        while mask:  # for (uint64_t mask = 1ULL << (nbits - 1); mask; mask >>= 1)
            if data & mask:  # Send a 1
                timings.append(onemark)
                timings.append(onespace)
            else:  # Send a 0
                timings.append(zeromark)
                timings.append(zerospace)
            mask >>= 1
    else:  # Send the Least Significant Bit (LSB) first / MSB last.
        for bit in range(nbits):  # for (uint16_t bit = 0; bit < nbits; bit++, data >>= 1)
            if data & 1:  # Send a 1
                timings.append(onemark)
                timings.append(onespace)
            else:  # Send a 0
                timings.append(zeromark)
                timings.append(zerospace)
            data >>= 1
    return timings


## Generic method for sending simple protocol messages.
## @param[in] headermark Nr. of usecs for the header mark. 0 means no header mark.
## @param[in] headerspace Nr. of usecs for the header space. 0 means no header space.
## @param[in] onemark Nr. of usecs for a '1' bit mark.
## @param[in] onespace Nr. of usecs for a '1' bit space.
## @param[in] zeromark Nr. of usecs for a '0' bit mark.
## @param[in] zerospace Nr. of usecs for a '0' bit space.
## @param[in] footermark Nr. of usecs for the footer mark. 0 means no footer mark.
## @param[in] gap Nr. of usecs for the gap between repeated messages. 0 means no gap.
##   NOTE: Gap is only added BETWEEN messages when repeat > 0, NOT after the final message.
## @param[in] dataptr Byte array of data to encode.
## @param[in] nbytes Number of bytes in dataptr.
## @param[in] MSBfirst True for MSB-first bit order, False for LSB-first.
## @param[in] repeat Number of extra times to send the message. 0 = send once only.
## Adapted from IRremoteESP8266 IRsend::sendGeneric
def sendGeneric(
    headermark: int,
    headerspace: int,
    onemark: int,
    onespace: int,
    zeromark: int,
    zerospace: int,
    footermark: int,
    gap: int = 0,
    dataptr: List[int] = None,
    nbytes: int = 0,
    MSBfirst: bool = True,
    repeat: int = 0,
) -> List[int]:
    """
    Encode byte array into IR protocol timing array.
    Adapted from IRremoteESP8266 IRsend::sendGeneric.

    Args:
        gap: Space in microseconds between repeated messages. NOT added after final message.
        repeat: Number of extra transmissions. 0 = send once, 1 = send twice, etc.

    Returns:
        List of timing values in microseconds (mark/space pairs).
    """
    if dataptr is None:
        return []

    all_timings = []

    # Send message (repeat + 1) times
    for r in range(repeat + 1):
        # Header
        if headermark:
            all_timings.append(headermark)
        if headerspace:
            all_timings.append(headerspace)

        # Data
        for i in range(nbytes):
            byte_timings = sendData(
                onemark, onespace, zeromark, zerospace, dataptr[i], 8, MSBfirst
            )
            all_timings.extend(byte_timings)

        # Footer
        if footermark:
            all_timings.append(footermark)

        # Gap - added after each message in the loop
        # For Panasonic: gap is used for section separator (always added)
        # For others with repeat: gap is inter-message spacing
        # If this is the last message AND gap is for inter-message only, skip it
        if gap:
            # Only skip gap if this is the last repetition AND we're repeating
            # (i.e., don't skip for single messages where gap is structural like Panasonic)
            if repeat > 0 and r == repeat:
                # This is the last of multiple repeats, skip the gap
                pass
            else:
                # Add gap: either structural (repeat=0) or between messages (repeat>0, not last)
                all_timings.append(gap)

    return all_timings


## Generic method for sending simple protocol messages (uint64_t data variant).
## @param[in] headermark Nr. of usecs for the header mark. 0 means no header mark.
## @param[in] headerspace Nr. of usecs for the header space. 0 means no header space.
## @param[in] onemark Nr. of usecs for a '1' bit mark.
## @param[in] onespace Nr. of usecs for a '1' bit space.
## @param[in] zeromark Nr. of usecs for a '0' bit mark.
## @param[in] zerospace Nr. of usecs for a '0' bit space.
## @param[in] footermark Nr. of usecs for the footer mark. 0 means no footer mark.
## @param[in] gap Nr. of usecs for the gap between repeated messages. 0 means no gap.
##   NOTE: Gap is only added BETWEEN messages when repeat > 0, NOT after the final message.
## @param[in] data Integer data to encode.
## @param[in] nbits Number of bits to encode from data.
## @param[in] MSBfirst True for MSB-first bit order, False for LSB-first.
## @param[in] repeat Number of extra times to send the message. 0 = send once only.
## Adapted from IRremoteESP8266 IRsend::sendGeneric (uint64_t variant)
def sendGenericUint64(
    headermark: int,
    headerspace: int,
    onemark: int,
    onespace: int,
    zeromark: int,
    zerospace: int,
    footermark: int,
    gap: int = 0,
    data_uint64: int = 0,
    nbits: int = 0,
    MSBfirst: bool = True,
    repeat: int = 0,
) -> List[int]:
    """
    Encode integer data into IR protocol timing array.
    Adapted from IRremoteESP8266 IRsend::sendGeneric.

    Args:
        gap: Space in microseconds between repeated messages. NOT added after final message.
        repeat: Number of extra transmissions. 0 = send once, 1 = send twice, etc.
        data_uint64: Integer data to encode (renamed from 'data' to avoid conflicts).

    Returns:
        List of timing values in microseconds (mark/space pairs).
    """
    all_timings = []

    # Send message (repeat + 1) times
    for r in range(repeat + 1):
        # Header
        if headermark:
            all_timings.append(headermark)
        if headerspace:
            all_timings.append(headerspace)

        # Data
        data_timings = sendData(onemark, onespace, zeromark, zerospace, data_uint64, nbits, MSBfirst)
        all_timings.extend(data_timings)

        # Footer
        if footermark:
            all_timings.append(footermark)

        # Gap - same logic as sendGeneric
        if gap:
            if repeat > 0 and r == repeat:
                pass  # Skip gap after last repetition
            else:
                all_timings.append(gap)

    return all_timings
