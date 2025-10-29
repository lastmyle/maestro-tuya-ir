# Copyright 2020 Chandrashekar Shetty (iamDshetty)
# Copyright 2020 crankyoldgit
# Copyright 2021 siriuslzx
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Support for Transcold A/C protocols.
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/1256
## @see https://docs.google.com/spreadsheets/d/1qdoyB0FyJm85HPP9oXcfui0n4ztXBFlik6kiNlkO2IM/edit?usp=sharing
## Direct translation from IRremoteESP8266 ir_Transcold.cpp and ir_Transcold.h

from typing import List

# Supports:
#   Brand: Transcold,  Model: M1-F-NO-6 A/C

# Constants - Timing values (from ir_Transcold.cpp lines 21-25)
kTranscoldHdrMark = 5944  # uSeconds.
kTranscoldBitMark = 555  # uSeconds.
kTranscoldHdrSpace = 7563  # uSeconds.
kTranscoldOneSpace = 3556  # uSeconds.
kTranscoldZeroSpace = 1526  # uSeconds.

# Mode constants (from ir_Transcold.h lines 87-91)
kTranscoldCool = 0b0110
kTranscoldDry = 0b1100
kTranscoldAuto = 0b1110
kTranscoldHeat = 0b1010
kTranscoldFan = 0b0010

# Fan Control constants (from ir_Transcold.h lines 94-100)
kTranscoldFanMin = 0b1001
kTranscoldFanMed = 0b1101
kTranscoldFanMax = 0b1011
kTranscoldFanAuto = 0b1111
kTranscoldFanAuto0 = 0b0110
kTranscoldFanZoneFollow = 0b0000
kTranscoldFanFixed = 0b1100

# Temperature constants (from ir_Transcold.h lines 103-106)
kTranscoldTempMin = 18  # Celsius
kTranscoldTempMax = 30  # Celsius
kTranscoldFanTempCode = 0b1111  # Part of Fan Mode.
kTranscoldTempSize = 4

# Special state constants (from ir_Transcold.h lines 108-114)
kTranscoldPrefix = 0b0000
kTranscoldUnknown = 0xFF
kTranscoldOff = 0b111011110111100101010100
kTranscoldSwing = 0b111001110110000101010100
kTranscoldSwingH = 0b111101110110000101010100  # NA
kTranscoldSwingV = 0b111001110110000101010100  # NA
kTranscoldCmdFan = 0b111011110110000101010100  # NA

kTranscoldKnownGoodState = 0xE96554


## Native representation of a Transcold A/C message.
## Direct translation from C++ union/struct (ir_Transcold.h lines 73-83)
class TranscoldProtocol:
    def __init__(self):
        # The state as raw 32-bit value
        self.raw = 0

    # Byte 1 - Temp (4 bits at bit position 8-11)
    @property
    def Temp(self) -> int:
        return (self.raw >> 8) & 0x0F

    @Temp.setter
    def Temp(self, value: int) -> None:
        self.raw = (self.raw & 0xFFFFF0FF) | ((value & 0x0F) << 8)

    # Byte 1 - Mode (4 bits at bit position 12-15)
    @property
    def Mode(self) -> int:
        return (self.raw >> 12) & 0x0F

    @Mode.setter
    def Mode(self, value: int) -> None:
        self.raw = (self.raw & 0xFFFF0FFF) | ((value & 0x0F) << 12)

    # Byte 2 - Fan (4 bits at bit position 16-19)
    @property
    def Fan(self) -> int:
        return (self.raw >> 16) & 0x0F

    @Fan.setter
    def Fan(self, value: int) -> None:
        self.raw = (self.raw & 0xFFF0FFFF) | ((value & 0x0F) << 16)


## Send a Transcold message
## Status: STABLE / Confirmed Working.
## @param[in] data The message to be sent.
## @param[in] nbits The number of bits of message to be sent.
## @param[in] repeat The number of times the command is to be repeated.
## Direct translation from IRremoteESP8266 IRsend::sendTranscold (ir_Transcold.cpp lines 40-67)
def sendTranscold(data: int, nbits: int, repeat: int = 0) -> List[int]:
    """
    Send a Transcold message.
    EXACT translation from IRremoteESP8266 IRsend::sendTranscold

    Returns timing array instead of transmitting via hardware.
    """
    if nbits % 8 != 0:
        return []  # nbits is required to be a multiple of 8.

    # Import here to avoid circular import
    from app.core.ir_protocols.ir_send import sendData

    all_timings = []

    for r in range(repeat + 1):
        # Header (lines 47-48)
        all_timings.append(kTranscoldHdrMark)
        all_timings.append(kTranscoldHdrSpace)

        # Data (lines 49-60)
        # Break data into byte segments, starting at the Most Significant
        # Byte. Each byte then being sent normal, then followed inverted.
        for i in range(8, nbits + 1, 8):
            # Grab a bytes worth of data. (line 54)
            # uint8_t segment = GETBITS64(data, nbits - i, 8);
            segment = (data >> (nbits - i)) & 0xFF

            # Normal + Inverted (lines 56-59)
            both = (segment << 8) | (~segment & 0xFF)
            segment_timings = sendData(
                onemark=kTranscoldBitMark,
                onespace=kTranscoldOneSpace,
                zeromark=kTranscoldBitMark,
                zerospace=kTranscoldZeroSpace,
                data=both,
                nbits=16,
                MSBfirst=True,
            )
            all_timings.extend(segment_timings)

        # Footer (lines 61-65)
        all_timings.append(kTranscoldBitMark)
        all_timings.append(kTranscoldHdrSpace)
        all_timings.append(kTranscoldBitMark)
        # kDefaultMessageGap placeholder - using standard gap
        all_timings.append(100000)

    return all_timings


## Class for handling detailed Transcold A/C messages.
## Direct translation from C++ IRTranscoldAc class (ir_Transcold.h lines 120-172)
class IRTranscoldAc:
    ## Class Constructor
    ## @param[in] pin GPIO to be used when sending. (Not used in Python)
    ## @param[in] inverted Is the output signal to be inverted? (Not used in Python)
    ## @param[in] use_modulation Is frequency modulation to be used? (Not used in Python)
    ## Direct translation from ir_Transcold.cpp lines 74-76
    def __init__(self) -> None:
        self._: TranscoldProtocol = TranscoldProtocol()
        # internal state (from ir_Transcold.h lines 164-166)
        self.swingFlag: bool = False
        self.swingHFlag: bool = False
        self.swingVFlag: bool = False
        # special state (from ir_Transcold.h line 169)
        self.special_state: int = kTranscoldOff
        self.stateReset()

    ## Reset the internal state to a fixed known good state.
    ## Direct translation from ir_Transcold.cpp lines 79-85
    def stateReset(self) -> None:
        self.setRaw(kTranscoldKnownGoodState)
        self.special_state = kTranscoldOff
        self.swingFlag = False
        self.swingHFlag = False
        self.swingVFlag = False

    ## Get a copy of the internal state as a valid code for this protocol.
    ## @return A valid code for this protocol based on the current internal state.
    ## Direct translation from ir_Transcold.cpp lines 105-110
    def getRaw(self) -> int:
        if self.isSpecialState():
            return self.special_state
        return self._.raw

    ## Set the internal state from a valid code for this protocol.
    ## @param[in] new_code A valid code for this protocol.
    ## Direct translation from ir_Transcold.cpp lines 114-128
    def setRaw(self, new_code: int) -> None:
        if self.handleSpecialState(new_code):
            self.special_state = new_code
            self._.raw = kTranscoldKnownGoodState
        else:
            # must be a command changing Temp|Mode|Fan
            # it is safe to just copy to remote var
            self._.raw = new_code
            self.special_state = kTranscoldKnownGoodState
            # it isn`t special so might affect Temp|mode|Fan
            if new_code == kTranscoldCmdFan:
                self.setMode(kTranscoldFan)

    ## Is the current state is a special state?
    ## @return true, if it is. false if it isn't.
    ## Direct translation from ir_Transcold.cpp lines 132-138
    def isSpecialState(self) -> bool:
        if self.special_state in [kTranscoldOff, kTranscoldSwing]:
            return True
        return False

    ## Adjust any internal settings based on the type of special state we are
    ##   supplied. Does nothing if it isn't a special state.
    ## @param[in] data The state we need to act upon.
    ## @note Special state means commands that are not affecting
    ## Temperature/Mode/Fan
    ## @return true, if it is a special state. false if it isn't.
    ## Direct translation from ir_Transcold.cpp lines 146-157
    def handleSpecialState(self, data: int) -> bool:
        if data == kTranscoldOff:
            pass
        elif data == kTranscoldSwing:
            self.swingFlag = not self.swingFlag
        else:
            return False
        return True

    ## Set the temperature.
    ## @param[in] desired The temperature in degrees celsius.
    ## Direct translation from ir_Transcold.cpp lines 161-167
    def setTemp(self, desired: int) -> None:
        # Range check.
        temp = min(desired, kTranscoldTempMax)
        temp = max(temp, kTranscoldTempMin) - kTranscoldTempMin + 1
        # Import here to avoid circular dependency
        from app.core.ir_protocols.ir_recv import reverseBits, invertBits

        self._.Temp = reverseBits(invertBits(temp, kTranscoldTempSize), kTranscoldTempSize)

    ## Get the current temperature setting.
    ## @return The current setting for temp. in degrees celsius.
    ## Direct translation from ir_Transcold.cpp lines 171-174
    def getTemp(self) -> int:
        # Import here to avoid circular dependency
        from app.core.ir_protocols.ir_recv import reverseBits, invertBits

        return (
            reverseBits(invertBits(self._.Temp, kTranscoldTempSize), kTranscoldTempSize)
            + kTranscoldTempMin
            - 1
        )

    ## Get the value of the current power setting.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Transcold.cpp lines 178-181
    def getPower(self) -> bool:
        # There is only an off state. Everything else is "on".
        return self.special_state != kTranscoldOff

    ## Change the power setting.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Transcold.cpp lines 185-191
    def setPower(self, on: bool) -> None:
        if not on:
            self.special_state = kTranscoldOff
        else:
            self.special_state = kTranscoldKnownGoodState

    ## Change the power setting to On.
    ## Direct translation from ir_Transcold.cpp line 194
    def on(self) -> None:
        self.setPower(True)

    ## Change the power setting to Off.
    ## Direct translation from ir_Transcold.cpp line 197
    def off(self) -> None:
        self.setPower(False)

    ## Get the Swing setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Transcold.cpp line 201
    def getSwing(self) -> bool:
        return self.swingFlag

    ## Toggle the Swing mode of the A/C.
    ## Direct translation from ir_Transcold.cpp lines 204-209
    def setSwing(self) -> None:
        # Assumes that repeated sending "swing" toggles the action on the device.
        # if not, the variable "swingFlag" can be removed.
        self.special_state = kTranscoldSwing
        self.swingFlag = not self.swingFlag

    ## Set the operating mode of the A/C.
    ## @param[in] mode The desired operating mode.
    ## Direct translation from ir_Transcold.cpp lines 213-236
    def setMode(self, mode: int) -> None:
        actualmode = mode
        if actualmode == kTranscoldAuto or actualmode == kTranscoldDry:
            self._.Fan = kTranscoldFanAuto0
        elif actualmode in [kTranscoldCool, kTranscoldHeat, kTranscoldFan]:
            self._.Fan = kTranscoldFanAuto
        else:  # Anything else, go with Auto mode.
            actualmode = kTranscoldAuto
            self._.Fan = kTranscoldFanAuto0

        self.setTemp(self.getTemp())
        # Fan mode is a special case of Dry.
        if actualmode == kTranscoldFan:
            actualmode = kTranscoldDry
            self._.Temp = kTranscoldFanTempCode
        self._.Mode = actualmode

    ## Get the operating mode setting of the A/C.
    ## @return The current operating mode setting.
    ## Direct translation from ir_Transcold.cpp lines 240-245
    def getMode(self) -> int:
        mode = self._.Mode
        if mode == kTranscoldDry:
            if self._.Temp == kTranscoldFanTempCode:
                return kTranscoldFan
        return mode

    ## Get the current fan speed setting.
    ## @return The current fan speed.
    ## Direct translation from ir_Transcold.cpp lines 249-251
    def getFan(self) -> int:
        return self._.Fan

    ## Set the speed of the fan.
    ## @param[in] speed The desired setting.
    ## @param[in] modecheck Do we enforce any mode limitations before setting?
    ## Direct translation from ir_Transcold.cpp lines 256-284
    def setFan(self, speed: int, modecheck: bool = True) -> None:
        newspeed = speed
        if modecheck:
            mode = self.getMode()
            if mode in [kTranscoldAuto, kTranscoldDry]:  # Dry & Auto mode can't have speed Auto.
                if speed == kTranscoldFanAuto:
                    newspeed = kTranscoldFanAuto0
            else:  # Only Dry & Auto mode can have speed Auto0.
                if speed == kTranscoldFanAuto0:
                    newspeed = kTranscoldFanAuto

        if speed in [
            kTranscoldFanAuto,
            kTranscoldFanAuto0,
            kTranscoldFanMin,
            kTranscoldFanMed,
            kTranscoldFanMax,
            kTranscoldFanZoneFollow,
            kTranscoldFanFixed,
        ]:
            pass
        else:  # Unknown speed requested.
            newspeed = kTranscoldFanAuto

        self._.Fan = newspeed


## Decode the supplied Transcold A/C message.
## Status: STABLE / Known Working.
## @param[in,out] results Ptr to the data to decode & where to store the decode result.
## @param[in] offset The starting index to use when attempting to decode the raw data.
## @param[in] nbits The number of data bits to expect.
## @param[in] strict Flag indicating if we should perform strict matching.
## @return A boolean. True if it can decode it, false if it can't.
## Direct translation from IRremoteESP8266 IRrecv::decodeTranscold (ir_Transcold.cpp lines 441-499)
def decodeTranscold(results, offset: int = 1, nbits: int = 24, strict: bool = True) -> bool:
    """
    Decode a Transcold A/C IR message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeTranscold

    This is the ACTUAL C++ decoder function, not a wrapper.
    """
    # Import here to avoid circular imports
    from app.core.ir_protocols.ir_recv import (
        kHeader,
        kFooter,
        matchMark,
        matchSpace,
        matchAtLeast,
        invertBits,
    )

    # The protocol sends the data normal + inverted, alternating on
    # each byte. Hence twice the number of expected data bits. (lines 445-448)
    if results.rawlen <= 2 * 2 * nbits + kHeader + kFooter - 1 + offset:
        return False
    if strict and nbits != 24:  # kTranscoldBits
        return False
    if nbits % 8 != 0:
        return False

    data = 0
    inverted = 0

    # lines 453-454
    if nbits > 64:
        return False  # We can't possibly capture a Transcold packet that big.

    # Header (lines 457-458)
    if not matchMark(results.rawbuf[offset], kTranscoldHdrMark):
        return False
    offset += 1
    if not matchSpace(results.rawbuf[offset], kTranscoldHdrSpace):
        return False
    offset += 1

    # Data (lines 461-479)
    # Twice as many bits as there are normal plus inverted bits.
    for i in range(nbits * 2):
        flip = (i // 8) % 2
        if not matchMark(results.rawbuf[offset], kTranscoldBitMark):
            return False
        offset += 1
        if matchSpace(results.rawbuf[offset], kTranscoldOneSpace):
            if flip:
                inverted = (inverted << 1) | 1
            else:
                data = (data << 1) | 1
        elif matchSpace(results.rawbuf[offset], kTranscoldZeroSpace):
            if flip:
                inverted <<= 1
            else:
                data <<= 1
        else:
            return False
        offset += 1

    # Footer (lines 482-487)
    if not matchMark(results.rawbuf[offset], kTranscoldBitMark):
        return False
    offset += 1
    if not matchSpace(results.rawbuf[offset], kTranscoldHdrSpace):
        return False
    offset += 1
    if not matchMark(results.rawbuf[offset], kTranscoldBitMark):
        return False
    offset += 1
    if offset < results.rawlen and not matchAtLeast(
        results.rawbuf[offset], 100000
    ):  # kDefaultMessageGap placeholder
        return False

    # Compliance (line 490)
    if strict and inverted != invertBits(data, nbits):
        return False

    # Success (lines 493-498)
    # results.decode_type = TRANSCOLD  # Would set protocol type in C++
    results.bits = nbits
    results.value = data
    results.address = 0
    results.command = 0
    return True
