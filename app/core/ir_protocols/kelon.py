# Copyright 2021 Davide Depau
# Copyright 2022 David Conran
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Support for Kelon AC protocol.
## Direct translation from IRremoteESP8266 ir_Kelon.cpp and ir_Kelon.h
## Both sending and decoding should be functional for models of series
## KELON ON/OFF 9000-12000.
## All features of the standard remote are implemented.
##
## @note Unsupported:
##    - Explicit on/off due to AC unit limitations
##    - Explicit swing position due to AC unit limitations
##    - Fahrenheit.
##
## For KELON168:
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/1745

from typing import List, Optional

# Supports:
#   Brand: Kelon,  Model: ON/OFF 9000-12000 (KELON)
#   Brand: Kelon,  Model: DG11R2-01 remote (KELON168)
#   Brand: Kelon,  Model: AST-09UW4RVETG00A A/C (KELON168)
#   Brand: Hisense,  Model: AST-09UW4RVETG00A A/C (KELON168)

# Constants - Timing values (from ir_Kelon.cpp lines 36-42)
kKelonHdrMark = 9000
kKelonHdrSpace = 4600
kKelonBitMark = 560
kKelonOneSpace = 1680
kKelonZeroSpace = 600
kKelonGap = 2 * 100000  # 2 * kDefaultMessageGap
kKelonFreq = 38000

# KELON168 constants (from ir_Kelon.cpp lines 44-47)
kKelon168FooterSpace = 8000
kKelon168Section1Size = 6
kKelon168Section2Size = 8
kKelon168Section3Size = 7

# State length constants (from IRremoteESP8266.h)
kKelonBits = 48  # 6 bytes
kKelon168StateLength = 21  # kKelon168Section1Size + kKelon168Section2Size + kKelon168Section3Size
kKelon168Bits = kKelon168StateLength * 8  # 168 bits

# Mode constants (from ir_Kelon.h lines 58-62)
kKelonModeHeat = 0
kKelonModeSmart = 1  # (temp = 26C, but not shown)
kKelonModeCool = 2
kKelonModeDry = 3  # (temp = 25C, but not shown)
kKelonModeFan = 4  # (temp = 25C, but not shown)

# Fan speed constants (from ir_Kelon.h lines 63-69)
# Note! Kelon fan speeds are actually 0:AUTO, 1:MAX, 2:MED, 3:MIN
# Since this is insane, I decided to invert them in the public API, they are
# converted back in setFan/getFan
kKelonFanAuto = 0
kKelonFanMin = 1
kKelonFanMedium = 2
kKelonFanMax = 3

# Dry grade constants (from ir_Kelon.h lines 71-72)
kKelonDryGradeMin = -2
kKelonDryGradeMax = +2

# Temperature constants (from ir_Kelon.h lines 73-74)
kKelonMinTemp = 18
kKelonMaxTemp = 32


## Native representation of a Kelon A/C message.
## This is a direct translation of the C++ union/struct (from ir_Kelon.h lines 34-55)
class KelonProtocol:
    def __init__(self):
        # 64-bit raw value
        self.raw = 0

    # Helper to get/set bytes in raw
    def _get_byte(self, idx: int) -> int:
        return (self.raw >> (idx * 8)) & 0xFF

    def _set_byte(self, idx: int, value: int) -> None:
        mask = 0xFF << (idx * 8)
        self.raw = (self.raw & ~mask) | ((value & 0xFF) << (idx * 8))

    # preamble[0] - byte 0 (from ir_Kelon.h line 38)
    @property
    def preamble0(self) -> int:
        return self._get_byte(0)

    @preamble0.setter
    def preamble0(self, value: int) -> None:
        self._set_byte(0, value)

    # preamble[1] - byte 1 (from ir_Kelon.h line 38)
    @property
    def preamble1(self) -> int:
        return self._get_byte(1)

    @preamble1.setter
    def preamble1(self, value: int) -> None:
        self._set_byte(1, value)

    # byte 2 (from ir_Kelon.h lines 39-44)
    @property
    def Fan(self) -> int:
        return (self._get_byte(2) >> 0) & 0x03

    @Fan.setter
    def Fan(self, value: int) -> None:
        byte = self._get_byte(2)
        byte = (byte & 0xFC) | ((value & 0x03) << 0)
        self._set_byte(2, byte)

    @property
    def PowerToggle(self) -> int:
        return (self._get_byte(2) >> 2) & 0x01

    @PowerToggle.setter
    def PowerToggle(self, value: bool) -> None:
        byte = self._get_byte(2)
        if value:
            byte |= 1 << 2
        else:
            byte &= ~(1 << 2)
        self._set_byte(2, byte)

    @property
    def SleepEnabled(self) -> int:
        return (self._get_byte(2) >> 3) & 0x01

    @SleepEnabled.setter
    def SleepEnabled(self, value: bool) -> None:
        byte = self._get_byte(2)
        if value:
            byte |= 1 << 3
        else:
            byte &= ~(1 << 3)
        self._set_byte(2, byte)

    @property
    def DehumidifierGrade(self) -> int:
        return (self._get_byte(2) >> 4) & 0x07

    @DehumidifierGrade.setter
    def DehumidifierGrade(self, value: int) -> None:
        byte = self._get_byte(2)
        byte = (byte & 0x8F) | ((value & 0x07) << 4)
        self._set_byte(2, byte)

    @property
    def SwingVToggle(self) -> int:
        return (self._get_byte(2) >> 7) & 0x01

    @SwingVToggle.setter
    def SwingVToggle(self, value: bool) -> None:
        byte = self._get_byte(2)
        if value:
            byte |= 1 << 7
        else:
            byte &= ~(1 << 7)
        self._set_byte(2, byte)

    # byte 3 (from ir_Kelon.h lines 45-47)
    @property
    def Mode(self) -> int:
        return (self._get_byte(3) >> 0) & 0x07

    @Mode.setter
    def Mode(self, value: int) -> None:
        byte = self._get_byte(3)
        byte = (byte & 0xF8) | ((value & 0x07) << 0)
        self._set_byte(3, byte)

    @property
    def TimerEnabled(self) -> int:
        return (self._get_byte(3) >> 3) & 0x01

    @TimerEnabled.setter
    def TimerEnabled(self, value: bool) -> None:
        byte = self._get_byte(3)
        if value:
            byte |= 1 << 3
        else:
            byte &= ~(1 << 3)
        self._set_byte(3, byte)

    @property
    def Temperature(self) -> int:
        return (self._get_byte(3) >> 4) & 0x0F

    @Temperature.setter
    def Temperature(self, value: int) -> None:
        byte = self._get_byte(3)
        byte = (byte & 0x0F) | ((value & 0x0F) << 4)
        self._set_byte(3, byte)

    # byte 4 (from ir_Kelon.h lines 48-50)
    @property
    def TimerHalfHour(self) -> int:
        return (self._get_byte(4) >> 0) & 0x01

    @TimerHalfHour.setter
    def TimerHalfHour(self, value: bool) -> None:
        byte = self._get_byte(4)
        if value:
            byte |= 1 << 0
        else:
            byte &= ~(1 << 0)
        self._set_byte(4, byte)

    @property
    def TimerHours(self) -> int:
        return (self._get_byte(4) >> 1) & 0x3F

    @TimerHours.setter
    def TimerHours(self, value: int) -> None:
        byte = self._get_byte(4)
        byte = (byte & 0x81) | ((value & 0x3F) << 1)
        self._set_byte(4, byte)

    @property
    def SmartModeEnabled(self) -> int:
        return (self._get_byte(4) >> 7) & 0x01

    @SmartModeEnabled.setter
    def SmartModeEnabled(self, value: bool) -> None:
        byte = self._get_byte(4)
        if value:
            byte |= 1 << 7
        else:
            byte &= ~(1 << 7)
        self._set_byte(4, byte)

    # byte 5 (from ir_Kelon.h lines 51-54)
    @property
    def SuperCoolEnabled1(self) -> int:
        return (self._get_byte(5) >> 4) & 0x01

    @SuperCoolEnabled1.setter
    def SuperCoolEnabled1(self, value: bool) -> None:
        byte = self._get_byte(5)
        if value:
            byte |= 1 << 4
        else:
            byte &= ~(1 << 4)
        self._set_byte(5, byte)

    @property
    def SuperCoolEnabled2(self) -> int:
        return (self._get_byte(5) >> 7) & 0x01

    @SuperCoolEnabled2.setter
    def SuperCoolEnabled2(self, value: bool) -> None:
        byte = self._get_byte(5)
        if value:
            byte |= 1 << 7
        else:
            byte &= ~(1 << 7)
        self._set_byte(5, byte)


## Send a Kelon 48-bit message.
## Status: STABLE / Working.
## @param[in] data The data to be transmitted.
## @param[in] nbits Nr. of bits of data to be sent.
## @param[in] repeat The number of times the command is to be repeated.
## Direct translation from IRremoteESP8266 IRsend::sendKelon (ir_Kelon.cpp lines 49-63)
def sendKelon(data: int, nbits: int = kKelonBits, repeat: int = 0) -> List[int]:
    """
    Send a Kelon 48-bit message.
    EXACT translation from IRremoteESP8266 IRsend::sendKelon

    Returns timing array instead of transmitting via hardware.
    """
    # Import here to avoid circular import
    from app.core.ir_protocols.ir_send import sendGeneric64

    return sendGeneric64(
        headermark=kKelonHdrMark,
        headerspace=kKelonHdrSpace,
        onemark=kKelonBitMark,
        onespace=kKelonOneSpace,
        zeromark=kKelonBitMark,
        zerospace=kKelonZeroSpace,
        footermark=kKelonBitMark,
        gap=kKelonGap,
        data=data,
        nbits=nbits,
        frequency=kKelonFreq,
        MSBfirst=False,  # LSB First
        repeat=repeat,
        dutycycle=50,
    )


## Decode the supplied Kelon 48-bit message.
## Status: STABLE / Working.
## @param[in,out] results Ptr to the data to decode & where to store the result
## @param[in] offset The starting index to use when attempting to decode the
##   raw data. Typically/Defaults to kStartOffset.
## @param[in] nbits The number of data bits to expect.
## @param[in] strict Flag indicating if we should perform strict matching.
## @return True if it can decode it, false if it can't.
## Direct translation from IRremoteESP8266 IRrecv::decodeKelon (ir_Kelon.cpp lines 66-92)
def decodeKelon(
    results, offset: int = 1, nbits: int = kKelonBits, strict: bool = True, _tolerance: int = 25
) -> bool:
    """
    Decode a Kelon 48-bit HVAC IR message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeKelon

    This is the ACTUAL C++ decoder function, not a wrapper.
    """
    # Import here to avoid circular imports
    from app.core.ir_protocols.ir_recv import kMarkExcess, _matchGeneric

    if strict and nbits != kKelonBits:
        return False

    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=results.value,
        result_bytes_ptr=None,
        use_bits=True,
        remaining=results.rawlen - offset,
        nbits=nbits,
        hdrmark=kKelonHdrMark,
        hdrspace=kKelonHdrSpace,
        onemark=kKelonBitMark,
        onespace=kKelonOneSpace,
        zeromark=kKelonBitMark,
        zerospace=kKelonZeroSpace,
        footermark=kKelonBitMark,
        footerspace=kKelonGap,
        atleast=True,
        tolerance=_tolerance,
        excess=kMarkExcess,
        MSBfirst=False,
    )
    if used == 0:
        return False

    # Success
    # results.decode_type = KELON
    results.address = 0
    results.command = 0
    results.bits = nbits
    return True


## Send a Kelon 168 bit / 21 byte message.
## Status: BETA / Probably works.
## @param[in] data The data to be transmitted.
## @param[in] nbytes Nr. of bytes of data to be sent.
## @param[in] repeat The number of times the command is to be repeated.
## Direct translation from IRremoteESP8266 IRsend::sendKelon168 (ir_Kelon.cpp lines 452-494)
def sendKelon168(data: List[int], nbytes: int, repeat: int = 0) -> List[int]:
    """
    Send a Kelon 168 bit / 21 byte message.
    EXACT translation from IRremoteESP8266 IRsend::sendKelon168

    Returns timing array instead of transmitting via hardware.
    """
    # Enough bytes to send a proper message?
    if nbytes < kKelon168StateLength:
        return []

    # Import here to avoid circular import
    from app.core.ir_protocols.ir_send import sendGeneric

    all_timings = []

    for r in range(repeat + 1):
        # Section #1 (48 bits)
        section1 = sendGeneric(
            headermark=kKelonHdrMark,
            headerspace=kKelonHdrSpace,
            onemark=kKelonBitMark,
            onespace=kKelonOneSpace,
            zeromark=kKelonBitMark,
            zerospace=kKelonZeroSpace,
            footermark=kKelonBitMark,
            gap=kKelon168FooterSpace,
            dataptr=data[0:kKelon168Section1Size],
            nbytes=kKelon168Section1Size,
            frequency=kKelonFreq,
            MSBfirst=False,  # LSB First
            repeat=0,
            dutycycle=50,
        )
        all_timings.extend(section1)

        # Section #2 (64 bits)
        section2 = sendGeneric(
            headermark=0,
            headerspace=0,
            onemark=kKelonBitMark,
            onespace=kKelonOneSpace,
            zeromark=kKelonBitMark,
            zerospace=kKelonZeroSpace,
            footermark=kKelonBitMark,
            gap=kKelon168FooterSpace,
            dataptr=data[kKelon168Section1Size : kKelon168Section1Size + kKelon168Section2Size],
            nbytes=kKelon168Section2Size,
            frequency=kKelonFreq,
            MSBfirst=False,  # LSB First
            repeat=0,
            dutycycle=50,
        )
        all_timings.extend(section2)

        # Section #3 (56 bits)
        section3 = sendGeneric(
            headermark=0,
            headerspace=0,
            onemark=kKelonBitMark,
            onespace=kKelonOneSpace,
            zeromark=kKelonBitMark,
            zerospace=kKelonZeroSpace,
            footermark=kKelonBitMark,
            gap=kKelonGap,
            dataptr=data[kKelon168Section1Size + kKelon168Section2Size :],
            nbytes=nbytes - (kKelon168Section1Size + kKelon168Section2Size),
            frequency=kKelonFreq,
            MSBfirst=False,  # LSB First
            repeat=0,
            dutycycle=50,
        )
        all_timings.extend(section3)

    return all_timings


## Decode the supplied Kelon 168 bit / 21 byte message.
## Status: BETA / Probably Working.
## @param[in,out] results Ptr to the data to decode & where to store the result
## @param[in] offset The starting index to use when attempting to decode the
##   raw data. Typically/Defaults to kStartOffset.
## @param[in] nbits The number of data bits to expect.
## @param[in] strict Flag indicating if we should perform strict matching.
## @return True if it can decode it, false if it can't.
## Direct translation from IRremoteESP8266 IRrecv::decodeKelon168 (ir_Kelon.cpp lines 497-552)
def decodeKelon168(
    results, offset: int = 1, nbits: int = kKelon168Bits, strict: bool = True, _tolerance: int = 25
) -> bool:
    """
    Decode a Kelon 168 bit HVAC IR message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeKelon168

    This is the ACTUAL C++ decoder function, not a wrapper.
    """
    # Import here to avoid circular imports
    from app.core.ir_protocols.ir_recv import kHeader, kFooter, kMarkExcess, _matchGeneric

    if strict and nbits != kKelon168Bits:
        return False
    if results.rawlen <= 2 * nbits + kHeader + kFooter * 2 - 1 + offset:
        return False  # Can't possibly be a valid Kelon 168 bit message.

    # Section 1
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state[0:kKelon168Section1Size],
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=kKelon168Section1Size * 8,
        hdrmark=kKelonHdrMark,
        hdrspace=kKelonHdrSpace,
        onemark=kKelonBitMark,
        onespace=kKelonOneSpace,
        zeromark=kKelonBitMark,
        zerospace=kKelonZeroSpace,
        footermark=kKelonBitMark,
        footerspace=kKelon168FooterSpace,
        atleast=False,
        tolerance=_tolerance,
        excess=kMarkExcess,
        MSBfirst=False,
    )
    if not used:
        return False  # Failed to match.
    offset += used

    # Section 2
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state[
            kKelon168Section1Size : kKelon168Section1Size + kKelon168Section2Size
        ],
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=kKelon168Section2Size * 8,
        hdrmark=0,
        hdrspace=0,
        onemark=kKelonBitMark,
        onespace=kKelonOneSpace,
        zeromark=kKelonBitMark,
        zerospace=kKelonZeroSpace,
        footermark=kKelonBitMark,
        footerspace=kKelon168FooterSpace,
        atleast=False,
        tolerance=_tolerance,
        excess=kMarkExcess,
        MSBfirst=False,
    )
    if not used:
        return False  # Failed to match.
    offset += used

    # Section 3
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state[kKelon168Section1Size + kKelon168Section2Size :],
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=nbits - (kKelon168Section1Size + kKelon168Section2Size) * 8,
        hdrmark=0,
        hdrspace=0,
        onemark=kKelonBitMark,
        onespace=kKelonOneSpace,
        zeromark=kKelonBitMark,
        zerospace=kKelonZeroSpace,
        footermark=kKelonBitMark,
        footerspace=kKelonGap,
        atleast=True,
        tolerance=_tolerance,
        excess=kMarkExcess,
        MSBfirst=False,
    )
    if not used:
        return False  # Failed to match.

    # Success
    # results.decode_type = KELON168
    results.bits = nbits
    return True


## Class for handling detailed Kelon A/C messages.
## Direct translation from C++ IRKelonAc class (ir_Kelon.h lines 77-141, ir_Kelon.cpp lines 95-450)
class IRKelonAc:
    ## Class Constructor
    ## @param[in] pin GPIO to be used when sending.
    ## @param[in] inverted Is the output signal to be inverted?
    ## @param[in] use_modulation Is frequency modulation to be used?
    ## Direct translation from ir_Kelon.cpp lines 95-101
    def __init__(self) -> None:
        self._: KelonProtocol = KelonProtocol()
        # Used when exiting supercool mode (from ir_Kelon.h lines 137-140)
        self._previousMode = 0
        self._previousTemp = kKelonMinTemp
        self._previousFan = kKelonFanAuto
        self.stateReset()

    ## Reset the internals of the object to a known good state.
    ## Direct translation from ir_Kelon.cpp lines 103-108
    def stateReset(self) -> None:
        self._.raw = 0
        self._.preamble0 = 0b10000011
        self._.preamble1 = 0b00000110

    ## Request toggling power - will be reset to false after sending
    ## @param[in] toggle Whether to toggle the power state
    ## Direct translation from ir_Kelon.cpp lines 159-160
    def setTogglePower(self, toggle: bool) -> None:
        self._.PowerToggle = toggle

    ## Get whether toggling power will be requested
    ## @return The power toggle state
    ## Direct translation from ir_Kelon.cpp lines 162-164
    def getTogglePower(self) -> bool:
        return bool(self._.PowerToggle)

    ## Set the temperature setting.
    ## @param[in] degrees The temperature in degrees celsius.
    ## Direct translation from ir_Kelon.cpp lines 166-173
    def setTemp(self, degrees: int) -> None:
        temp = max(kKelonMinTemp, degrees)
        temp = min(kKelonMaxTemp, temp)
        self._previousTemp = self._.Temperature
        self._.Temperature = temp - kKelonMinTemp

    ## Get the current temperature setting.
    ## @return Get current setting for temp. in degrees celsius.
    ## Direct translation from ir_Kelon.cpp lines 175-177
    def getTemp(self) -> int:
        return self._.Temperature + kKelonMinTemp

    ## Set the speed of the fan.
    ## @param[in] speed 0 is auto, 1-5 is the speed
    ## Direct translation from ir_Kelon.cpp lines 179-188
    def setFan(self, speed: int) -> None:
        fan = min(speed, kKelonFanMax)

        self._previousFan = self._.Fan
        # Note: Kelon fan speeds are backwards! This code maps the range 0,1:3 to
        # 0,3:1 to save the API's user's sanity.
        self._.Fan = ((fan - 4) * -1) % 4

    ## Get the current fan speed setting.
    ## @return The current fan speed.
    ## Direct translation from ir_Kelon.cpp lines 190-194
    def getFan(self) -> int:
        return ((self._.Fan - 4) * -1) % 4

    ## Set the dehumidification intensity.
    ## @param[in] grade has to be in the range [-2 : +2]
    ## Direct translation from ir_Kelon.cpp lines 196-209
    def setDryGrade(self, grade: int) -> None:
        drygrade = max(kKelonDryGradeMin, grade)
        drygrade = min(kKelonDryGradeMax, drygrade)

        # Two's complement is clearly too bleeding edge for this manufacturer
        if drygrade < 0:
            outval = 0b100 | ((-drygrade) & 0b011)
        else:
            outval = drygrade & 0b011
        self._.DehumidifierGrade = outval

    ## Get the current dehumidification intensity setting. In smart mode, this
    ## controls the temperature adjustment.
    ## @return The current dehumidification intensity.
    ## Direct translation from ir_Kelon.cpp lines 211-217
    def getDryGrade(self) -> int:
        val = (self._.DehumidifierGrade & 0b011) * (-1 if (self._.DehumidifierGrade & 0b100) else 1)
        return val

    ## Set the desired operation mode.
    ## @param[in] mode The desired operation mode.
    ## Direct translation from ir_Kelon.cpp lines 219-252
    def setMode(self, mode: int) -> None:
        if (
            self._.Mode == kKelonModeSmart
            or self._.Mode == kKelonModeFan
            or self._.Mode == kKelonModeDry
        ):
            self._.Temperature = self._previousTemp

        if self._.SuperCoolEnabled1:
            # Cancel supercool
            self._.SuperCoolEnabled1 = False
            self._.SuperCoolEnabled2 = False
            self._.Temperature = self._previousTemp
            self._.Fan = self._previousFan

        self._previousMode = self._.Mode

        if mode == kKelonModeSmart:
            self.setTemp(26)
            self._.SmartModeEnabled = True
            self._.Mode = mode
        elif mode in [kKelonModeDry, kKelonModeFan]:
            self.setTemp(25)
            # fallthrough
            self._.Mode = mode
            self._.SmartModeEnabled = False
        elif mode in [kKelonModeCool, kKelonModeHeat]:
            self._.Mode = mode
            # fallthrough
            self._.SmartModeEnabled = False
        else:
            self._.SmartModeEnabled = False

    ## Get the current operation mode setting.
    ## @return The current operation mode.
    ## Direct translation from ir_Kelon.cpp lines 254-256
    def getMode(self) -> int:
        return self._.Mode

    ## Request toggling the vertical swing - will be reset to false after sending
    ## @param[in] toggle If true, the swing mode will be toggled when sent.
    ## Direct translation from ir_Kelon.cpp lines 258-262
    def setToggleSwingVertical(self, toggle: bool) -> None:
        self._.SwingVToggle = toggle

    ## Get whether the swing mode is set to be toggled
    ## @return Whether the toggle bit is set
    ## Direct translation from ir_Kelon.cpp lines 264-266
    def getToggleSwingVertical(self) -> bool:
        return bool(self._.SwingVToggle)

    ## Control the current sleep (quiet) setting.
    ## @param[in] on The desired setting.
    ## Direct translation from ir_Kelon.cpp lines 268-270
    def setSleep(self, on: bool) -> None:
        self._.SleepEnabled = on

    ## Is the sleep setting on?
    ## @return The current value.
    ## Direct translation from ir_Kelon.cpp lines 272-274
    def getSleep(self) -> bool:
        return bool(self._.SleepEnabled)

    ## Control the current super cool mode setting.
    ## @param[in] on The desired setting.
    ## Direct translation from ir_Kelon.cpp lines 276-289
    def setSupercool(self, on: bool) -> None:
        if on:
            self.setTemp(kKelonMinTemp)
            self.setMode(kKelonModeCool)
            self.setFan(kKelonFanMax)
        else:
            # All reverts to previous are handled by setMode as needed
            self.setMode(self._previousMode)
        self._.SuperCoolEnabled1 = on
        self._.SuperCoolEnabled2 = on

    ## Is the super cool mode setting on?
    ## @return The current value.
    ## Direct translation from ir_Kelon.cpp lines 291-293
    def getSupercool(self) -> bool:
        return bool(self._.SuperCoolEnabled1)

    ## Set the timer time and enable it. Timer is an off timer if the unit is on,
    ## it is an on timer if the unit is off.
    ## Only multiples of 30m are supported for < 10h, then only multiples of 60m
    ## @param[in] mins Nr. of minutes
    ## Direct translation from ir_Kelon.cpp lines 295-312
    def setTimer(self, mins: int) -> None:
        minutes = min(mins, 24 * 60)

        if minutes // 60 >= 10:
            hours = minutes // 60 + 10
            self._.TimerHalfHour = hours & 1
            self._.TimerHours = hours >> 1
        else:
            self._.TimerHalfHour = 1 if (minutes % 60) >= 30 else 0
            self._.TimerHours = minutes // 60

        self.setTimerEnabled(True)

    ## Get the set timer. Timer set time is deleted once the command is sent, so
    ## calling this after send() will return 0.
    ## The AC unit will continue keeping track of the remaining time unless it is
    ## later disabled.
    ## @return The timer set minutes
    ## Direct translation from ir_Kelon.cpp lines 314-324
    def getTimer(self) -> int:
        if self._.TimerHours >= 10:
            return ((self._.TimerHours << 1) | self._.TimerHalfHour - 10) * 60
        return self._.TimerHours * 60 + (30 if self._.TimerHalfHour else 0)

    ## Enable or disable the timer. Note that in order to enable the timer the
    ## minutes must be set with setTimer().
    ## @param[in] on Whether to enable or disable the timer
    ## Direct translation from ir_Kelon.cpp lines 326-329
    def setTimerEnabled(self, on: bool) -> None:
        self._.TimerEnabled = on

    ## Get the current timer status
    ## @return Whether the timer is enabled.
    ## Direct translation from ir_Kelon.cpp lines 331-333
    def getTimerEnabled(self) -> bool:
        return bool(self._.TimerEnabled)

    ## Get the raw state of the object, suitable to be sent with the appropriate
    ## IRsend object method.
    ## @return A PTR to the internal state.
    ## Direct translation from ir_Kelon.cpp lines 335-338
    def getRaw(self) -> int:
        return self._.raw

    ## Set the raw state of the object.
    ## @param[in] new_code The raw state from the native IR message.
    ## Direct translation from ir_Kelon.cpp lines 340-342
    def setRaw(self, new_code: int) -> None:
        self._.raw = new_code

    ## Convert a standard A/C mode (stdAc::opmode_t) into it a native mode.
    ## @param[in] mode A stdAc::opmode_t operation mode.
    ## @return The native mode equivalent.
    ## Direct translation from ir_Kelon.cpp lines 344-355
    @staticmethod
    def convertMode(mode: str) -> int:
        """Convert common mode to Kelon mode"""
        if mode == "cool":
            return kKelonModeCool
        elif mode == "heat":
            return kKelonModeHeat
        elif mode == "dry":
            return kKelonModeDry
        elif mode == "fan":
            return kKelonModeFan
        else:
            return kKelonModeSmart  # aka Auto

    ## Convert a standard A/C fan speed (stdAc::fanspeed_t) into it a native speed.
    ## @param[in] fan A stdAc::fanspeed_t fan speed
    ## @return The native speed equivalent.
    ## Direct translation from ir_Kelon.cpp lines 357-369
    @staticmethod
    def convertFan(fan: str) -> int:
        """Convert common fan speed to Kelon fan speed"""
        if fan in ["min", "low"]:
            return kKelonFanMin
        elif fan == "medium":
            return kKelonFanMedium
        elif fan in ["high", "max"]:
            return kKelonFanMax
        else:
            return kKelonFanAuto

    ## Convert a native mode to it's stdAc::opmode_t equivalent.
    ## @param[in] mode A native operating mode value.
    ## @return The stdAc::opmode_t equivalent.
    ## Direct translation from ir_Kelon.cpp lines 371-382
    @staticmethod
    def toCommonMode(mode: int) -> str:
        """Convert Kelon mode to common mode"""
        if mode == kKelonModeCool:
            return "cool"
        elif mode == kKelonModeHeat:
            return "heat"
        elif mode == kKelonModeDry:
            return "dry"
        elif mode == kKelonModeFan:
            return "fan"
        else:
            return "auto"

    ## Convert a native fan speed to it's stdAc::fanspeed_t equivalent.
    ## @param[in] speed A native fan speed value.
    ## @return The stdAc::fanspeed_t equivalent.
    ## Direct translation from ir_Kelon.cpp lines 384-394
    @staticmethod
    def toCommonFanSpeed(speed: int) -> str:
        """Convert Kelon fan speed to common fan speed"""
        if speed == kKelonFanMin:
            return "low"
        elif speed == kKelonFanMedium:
            return "medium"
        elif speed == kKelonFanMax:
            return "high"
        else:
            return "auto"

    ## Convert the internal A/C object state to it's stdAc::state_t equivalent.
    ## @return A stdAc::state_t containing the current settings.
    ## Direct translation from ir_Kelon.cpp lines 396-425
    def toCommon(self, prev: Optional[dict] = None) -> dict:
        """Convert to common A/C state format"""
        result = {}
        result["protocol"] = "KELON"
        result["model"] = -1  # Unused.
        # AC only supports toggling it
        result["power"] = (prev is None or prev.get("power", True)) ^ bool(self._.PowerToggle)
        result["mode"] = self.toCommonMode(self.getMode())
        result["celsius"] = True
        result["degrees"] = self.getTemp()
        result["fanspeed"] = self.toCommonFanSpeed(self.getFan())
        # AC only supports toggling it
        result["swingv"] = "auto"
        if prev is not None and (prev.get("swingv") != "auto") ^ bool(self._.SwingVToggle):
            result["swingv"] = "off"
        result["turbo"] = self.getSupercool()
        result["sleep"] = 0 if self.getSleep() else -1
        # Not supported.
        result["swingh"] = "off"
        result["light"] = True
        result["beep"] = True
        result["quiet"] = False
        result["filter"] = False
        result["clean"] = False
        result["econo"] = False
        result["clock"] = -1
        return result

    ## Convert the internal settings into a human readable string.
    ## @return A String.
    ## Direct translation from ir_Kelon.cpp lines 427-450
    def toString(self) -> str:
        """Convert current state to human readable string"""
        result = ""
        result += f"Temp: {self.getTemp()}C, "
        result += f"Mode: {self.toCommonMode(self._.Mode)}, "
        result += f"Fan: {self.toCommonFanSpeed(self._.Fan)}, "
        result += f"Sleep: {self._.SleepEnabled}, "
        result += f"DryGrade: {self.getDryGrade()}, "
        timer_str = "On" if self.getTimer() > 0 else "Off"
        if self.getTimerEnabled():
            timer_str = f"{self.getTimer()} mins"
        result += f"Timer: {timer_str}, "
        result += f"Turbo: {self.getSupercool()}"
        if self.getTogglePower():
            result += ", PowerToggle: True"
        if self.getToggleSwingVertical():
            result += ", SwingVToggle: True"
        return result
