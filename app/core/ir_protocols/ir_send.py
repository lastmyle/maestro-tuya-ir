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
def sendData(onemark: int, onespace: int, zeromark: int, zerospace: int,
             data: int, nbits: int, MSBfirst: bool) -> List[int]:
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
## @param[in] headermark Nr. of usecs for the led to be pulsed for the header
##   mark. A value of 0 means no header mark.
## @param[in] headerspace Nr. of usecs for the led to be off after the header
##   mark. A value of 0 means no header space.
## @param[in] onemark Nr. of usecs for the led to be pulsed for a '1' bit.
## @param[in] onespace Nr. of usecs for the led to be fully off for a '1' bit.
## @param[in] zeromark Nr. of usecs for the led to be pulsed for a '0' bit.
## @param[in] zerospace Nr. of usecs for the led to be fully off for a '0' bit.
## @param[in] footermark Nr. of usecs for the led to be pulsed for the footer
##   mark. A value of 0 means no footer mark.
## @param[in] gap Nr. of usecs for the led to be off after the footer mark.
##   This is effectively the gap between messages.
##   A value of 0 means no gap space.
## @param[in] dataptr Pointer to the data to be transmitted.
## @param[in] nbytes Nr. of bytes of data to be sent.
## @param[in] frequency The frequency we want to modulate at. (Hz/kHz)
## @param[in] MSBfirst Flag for bit transmission order.
##   Defaults to MSB->LSB order.
## @param[in] repeat Nr. of extra times the message will be sent.
##   e.g. 0 = 1 message sent, 1 = 1 initial + 1 repeat = 2 messages
## @param[in] dutycycle Percentage duty cycle of the LED.
##   e.g. 25 = 25% = 1/4 on, 3/4 off.
##   If you are not sure, try 50 percent.
## @note Assumes a frequency < 1000 means kHz otherwise it is in Hz.
##   Most common value is 38000 or 38, for 38kHz.
## Direct translation from IRremoteESP8266 IRsend::sendGeneric (lines 411-435)
def sendGeneric(headermark: int, headerspace: int, onemark: int, onespace: int,
                zeromark: int, zerospace: int, footermark: int, gap: int,
                dataptr: List[int], nbytes: int, frequency: int, MSBfirst: bool,
                repeat: int, dutycycle: int) -> List[int]:
    """
    Encode byte array into IR protocol timings with header and footer.
    EXACT translation from IRremoteESP8266 IRsend::sendGeneric

    Note: In Python we return timings instead of transmitting via hardware.
    The repeat parameter generates multiple copies of the message.
    """
    all_timings = []
    # Setup
    # enableIROut(frequency, dutycycle);  # Not applicable in Python
    # We always send a message, even for repeat=0, hence '<= repeat'.
    for r in range(repeat + 1):  # for (uint16_t r = 0; r <= repeat; r++)
        # Header
        if headermark:
            all_timings.append(headermark)  # mark(headermark)
        if headerspace:
            all_timings.append(headerspace)  # space(headerspace)

        # Data
        for i in range(nbytes):  # for (uint16_t i = 0; i < nbytes; i++)
            byte_timings = sendData(onemark, onespace, zeromark, zerospace,
                                   dataptr[i], 8, MSBfirst)  # *(dataptr + i)
            all_timings.extend(byte_timings)

        # Footer
        if footermark:
            all_timings.append(footermark)  # mark(footermark)
        all_timings.append(gap)  # space(gap)
    return all_timings


## Generic method for sending simple protocol messages (uint64_t data variant).
## Will send leading or trailing 0's if the nbits is larger than the number
## of bits in data.
## @param[in] headermark Nr. of usecs for the led to be pulsed for the header
##   mark. A value of 0 means no header mark.
## @param[in] headerspace Nr. of usecs for the led to be off after the header
##   mark. A value of 0 means no header space.
## @param[in] onemark Nr. of usecs for the led to be pulsed for a '1' bit.
## @param[in] onespace Nr. of usecs for the led to be fully off for a '1' bit.
## @param[in] zeromark Nr. of usecs for the led to be pulsed for a '0' bit.
## @param[in] zerospace Nr. of usecs for the led to be fully off for a '0' bit.
## @param[in] footermark Nr. of usecs for the led to be pulsed for the footer
##   mark. A value of 0 means no footer mark.
## @param[in] gap Nr. of usecs for the led to be off after the footer mark.
##   This is effectively the gap between messages.
##   A value of 0 means no gap space.
## @param[in] data The data to be transmitted.
## @param[in] nbits Nr. of bits of data to be sent.
## @param[in] frequency The frequency we want to modulate at. (Hz/kHz)
## @param[in] MSBfirst Flag for bit transmission order.
##   Defaults to MSB->LSB order.
## @param[in] repeat Nr. of extra times the message will be sent.
##   e.g. 0 = 1 message sent, 1 = 1 initial + 1 repeat = 2 messages
## @param[in] dutycycle Percentage duty cycle of the LED.
##   e.g. 25 = 25% = 1/4 on, 3/4 off.
##   If you are not sure, try 50 percent.
## @note Assumes a frequency < 1000 means kHz otherwise it is in Hz.
##   Most common value is 38000 or 38, for 38kHz.
## Direct translation from IRremoteESP8266 IRsend::sendGeneric (uint64_t variant)
def sendGenericUint64(headermark: int, headerspace: int, onemark: int, onespace: int,
                      zeromark: int, zerospace: int, footermark: int, gap: int,
                      data: int, nbits: int, frequency: int, MSBfirst: bool,
                      repeat: int, dutycycle: int) -> List[int]:
    """
    Encode uint64_t data into IR protocol timings with header and footer.
    EXACT translation from IRremoteESP8266 IRsend::sendGeneric (uint64_t variant)

    Note: In Python we return timings instead of transmitting via hardware.
    The repeat parameter generates multiple copies of the message.
    """
    all_timings = []
    # Setup
    # enableIROut(frequency, dutycycle);  # Not applicable in Python
    # We always send a message, even for repeat=0, hence '<= repeat'.
    for r in range(repeat + 1):  # for (uint16_t r = 0; r <= repeat; r++)
        # Header
        if headermark:
            all_timings.append(headermark)  # mark(headermark)
        if headerspace:
            all_timings.append(headerspace)  # space(headerspace)

        # Data
        data_timings = sendData(onemark, onespace, zeromark, zerospace,
                               data, nbits, MSBfirst)
        all_timings.extend(data_timings)

        # Footer
        if footermark:
            all_timings.append(footermark)  # mark(footermark)
        all_timings.append(gap)  # space(gap)
    return all_timings
