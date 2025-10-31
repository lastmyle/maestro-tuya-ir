# Copyright 2020 Christian Nilsson
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Corona A/C protocol
## @note Unsupported:
##    - Auto/Max button press (special format)
# Supports:
#   Brand: Corona,  Model: CSH-N2211 A/C
#   Brand: Corona,  Model: CSH-N2511 A/C
#   Brand: Corona,  Model: CSH-N2811 A/C
#   Brand: Corona,  Model: CSH-N4011 A/C
#   Brand: Corona,  Model: AR-01 remote
#
# Ref: https://docs.google.com/spreadsheets/d/1zzDEUQ52y7MZ7_xCU3pdjdqbRXOwZLsbTGvKWcicqCI/
# Ref: https://www.corona.co.jp/box/download.php?id=145060636229
## Direct translation from IRremoteESP8266 ir_Corona.cpp and ir_Corona.h

from typing import List

# Constants - Timing values (ir_Corona.cpp lines 26-35)
kCoronaAcHdrMark = 3500
kCoronaAcHdrSpace = 1680
kCoronaAcBitMark = 450
kCoronaAcOneSpace = 1270
kCoronaAcZeroSpace = 420
kCoronaAcSpaceGap = 10800
kCoronaAcFreq = 38000  # Hz.
kCoronaAcOverheadShort = 3
kCoronaAcOverhead = 11  # full message
kCoronaTolerance = 5  # +5%

# State length constants (IRremoteESP8266.h)
kCoronaAcSectionBytes = 7  # kCoronaAcStateLengthShort
kCoronaAcSections = 3
kCoronaAcStateLength = kCoronaAcSectionBytes * 3  # 21 bytes
kCoronaAcBitsShort = kCoronaAcSectionBytes * 8  # 56 bits
kCoronaAcBits = kCoronaAcStateLength * 8  # 168 bits

# Section header constants (ir_Corona.h lines 75-78)
kCoronaAcSectionHeader0 = 0x28
kCoronaAcSectionHeader1 = 0x61
kCoronaAcSectionLabelBase = 0x0D  # 0b1101
kCoronaAcSectionData0Base = 0x10  # D0 Pos 4 always on

# Fan constants (ir_Corona.h lines 80-83)
kCoronaAcFanAuto = 0b00  # 0
kCoronaAcFanLow = 0b01  # 1
kCoronaAcFanMedium = 0b10  # 2
kCoronaAcFanHigh = 0b11  # 3

# Temperature constants (ir_Corona.h lines 89-90)
kCoronaAcMinTemp = 17  # Celsius = 0b0001
kCoronaAcMaxTemp = 30  # Celsius = 0b1110

# Mode constants (ir_Corona.h lines 91-94)
kCoronaAcModeHeat = 0b00  # 0
kCoronaAcModeDry = 0b01  # 1
kCoronaAcModeCool = 0b10  # 2
kCoronaAcModeFan = 0b11  # 3

# Section constants (ir_Corona.h lines 96-98)
kCoronaAcSettingsSection = 0
kCoronaAcOnTimerSection = 1
kCoronaAcOffTimerSection = 2

# Timer constants (ir_Corona.h lines 99-102)
kCoronaAcTimerMax = 12 * 60  # 12H in Minutes
# Min value on remote is 1 hour, actual sent value can be 2 secs
kCoronaAcTimerOff = 0xFFFF
kCoronaAcTimerUnitsPerMin = 30  # 30 units = 1 minute

# Nibble positions
kHighNibble = 4
kNibbleSize = 4


def setBits(data: List[int], idx: int, offset: int, nbits: int, value: int) -> None:
    """Set bits in a byte array"""
    if idx >= len(data):
        return
    mask = ((1 << nbits) - 1) << offset
    data[idx] = (data[idx] & ~mask) | ((value << offset) & mask)


## Native representation of a Corona A/C message.
## This is a direct translation of the C++ union/struct (ir_Corona.h lines 29-69)
class CoronaProtocol:
    def __init__(self):
        # The state array (21 bytes for Corona AC = 3 sections of 7 bytes)
        self.raw = [0] * kCoronaAcStateLength

    # Byte 3 (ir_Corona.h lines 54-60)
    @property
    def Fan(self) -> int:
        return self.raw[3] & 0x03

    @Fan.setter
    def Fan(self, value: int) -> None:
        self.raw[3] = (self.raw[3] & 0xFC) | (value & 0x03)

    @property
    def Econo(self) -> int:
        return (self.raw[3] >> 3) & 0x01

    @Econo.setter
    def Econo(self, value: bool) -> None:
        if value:
            self.raw[3] |= 0x08
        else:
            self.raw[3] &= 0xF7

    @property
    def SwingVToggle(self) -> int:
        return (self.raw[3] >> 6) & 0x01

    @SwingVToggle.setter
    def SwingVToggle(self, value: bool) -> None:
        if value:
            self.raw[3] |= 0x40
        else:
            self.raw[3] &= 0xBF

    # Byte 5 (ir_Corona.h lines 64-67)
    @property
    def Temp(self) -> int:
        return self.raw[5] & 0x0F

    @Temp.setter
    def Temp(self, value: int) -> None:
        self.raw[5] = (self.raw[5] & 0xF0) | (value & 0x0F)

    @property
    def Power(self) -> int:
        return (self.raw[5] >> 4) & 0x01

    @Power.setter
    def Power(self, value: bool) -> None:
        if value:
            self.raw[5] |= 0x10
        else:
            self.raw[5] &= 0xEF

    @property
    def PowerButton(self) -> int:
        return (self.raw[5] >> 5) & 0x01

    @PowerButton.setter
    def PowerButton(self, value: bool) -> None:
        if value:
            self.raw[5] |= 0x20
        else:
            self.raw[5] &= 0xDF

    @property
    def Mode(self) -> int:
        return (self.raw[5] >> 6) & 0x03

    @Mode.setter
    def Mode(self, value: int) -> None:
        self.raw[5] = (self.raw[5] & 0x3F) | ((value & 0x03) << 6)


## Get the byte that identifies the section
## @param[in] section Index of the section 0-2,
##            3 and above is used as the special case for short message
## @return The byte used for the section
## Direct translation from ir_Corona.cpp lines 167-179
def getSectionByte(section: int) -> int:
    """
    Get the byte that identifies the section.
    EXACT translation from IRremoteESP8266 IRCoronaAc::getSectionByte
    """
    # base byte
    b = kCoronaAcSectionLabelBase
    # 2 enabled bits shifted 0-2 bits depending on section
    if section >= 3:
        return 0b10010000 | b
    setBits([0], 0, kHighNibble, kNibbleSize, 0b11 << section)
    b |= (0b11 << section) << kHighNibble
    return b


## Check that a CoronaAc Section part is valid with section byte and inverted
## @param[in] state An array of bytes containing the section
## @param[in] pos Where to start in the state array
## @param[in] section Which section to work with
##            Used to get the section byte, and is validated against pos
## @return true if section is valid, otherwise false
## Direct translation from ir_Corona.cpp lines 181-236
def validSectionCorona(state: List[int], pos: int, section: int) -> bool:
    """
    Check that a Corona Section is valid.
    EXACT translation from IRremoteESP8266 IRCoronaAc::validSection
    """
    # sanity check, pos must match section, section 4 is at pos 0
    if (section % kCoronaAcSections) * kCoronaAcSectionBytes != pos:
        return False

    # all individual sections has the same prefix
    # Check Header0
    if state[pos] != kCoronaAcSectionHeader0:
        return False
    # Check Header1
    if state[pos + 1] != kCoronaAcSectionHeader1:
        return False

    # checking section byte
    if state[pos + 2] != getSectionByte(section):
        return False

    # checking inverts
    d0invinv = (~state[pos + 4]) & 0xFF
    if state[pos + 3] != d0invinv:
        return False
    d1invinv = (~state[pos + 6]) & 0xFF
    if state[pos + 5] != d1invinv:
        return False
    return True


## Calculate and set the check values for the internal state.
## @param[in,out] data The array to be modified
## Direct translation from ir_Corona.cpp lines 238-249
def checksumCorona(data: List[int]) -> None:
    """
    Calculate and set the checksum for Corona protocol.
    EXACT translation from IRremoteESP8266 IRCoronaAc::checksum
    """
    for i in range(kCoronaAcSections):
        pos = i * kCoronaAcSectionBytes
        data[pos] = kCoronaAcSectionHeader0
        data[pos + 1] = kCoronaAcSectionHeader1
        data[pos + 2] = getSectionByte(i)
        data[pos + 4] = (~data[pos + 3]) & 0xFF
        data[pos + 6] = (~data[pos + 5]) & 0xFF


## Send a CoronaAc formatted message.
## Status: STABLE / Working on real device.
## @param[in] data An array of bytes containing the IR command.
## @param[in] nbytes Nr. of bytes of data in the array.
## @param[in] repeat Nr. of times the message is to be repeated.
## Direct translation from ir_Corona.cpp lines 37-77
def sendCoronaAc(data: List[int], nbytes: int = kCoronaAcStateLength, repeat: int = 0) -> List[int]:
    """
    Send a Corona AC formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendCoronaAc

    Returns timing array instead of transmitting via hardware.
    """
    if nbytes < kCoronaAcSectionBytes:
        return []
    if kCoronaAcSectionBytes < nbytes < kCoronaAcStateLength:
        return []

    from app.core.ir_protocols.ir_send import sendGeneric

    all_timings = []

    for r in range(repeat + 1):
        pos = 0
        # Data Section #1 - 3 loop
        # e.g.
        #   bits = 56; bytes = 7;
        # #1  *(data + pos) = {0x28, 0x61, 0x3D, 0x19, 0xE6, 0x37, 0xC8};
        # #2  *(data + pos) = {0x28, 0x61, 0x6D, 0xFF, 0x00, 0xFF, 0x00};
        # #3  *(data + pos) = {0x28, 0x61, 0xCD, 0xFF, 0x00, 0xFF, 0x00};
        for section in range(kCoronaAcSections):
            section_timings = sendGeneric(
                headermark=kCoronaAcHdrMark,
                headerspace=kCoronaAcHdrSpace,
                onemark=kCoronaAcBitMark,
                onespace=kCoronaAcOneSpace,
                zeromark=kCoronaAcBitMark,
                zerospace=kCoronaAcZeroSpace,
                footermark=kCoronaAcBitMark,
                gap=kCoronaAcSpaceGap,
                dataptr=data[pos:],
                nbytes=kCoronaAcSectionBytes,
                MSBfirst=False,
            )
            all_timings.extend(section_timings)
            pos += kCoronaAcSectionBytes  # Adjust by how many bytes was sent
            # don't send more data then what we have
            if nbytes <= pos:
                break

    return all_timings


## Decode the supplied CoronaAc message.
## Status: STABLE / Appears to be working.
## @param[in,out] results Ptr to the data to decode & where to store it
## @param[in] offset The starting index to use when attempting to decode the raw data.
## @param[in] nbits The number of data bits to expect.
## @param[in] strict Flag indicating if we should perform strict matching.
## @return A boolean. True if it can decode it, false if it can't.
## Direct translation from ir_Corona.cpp lines 79-142
def decodeCoronaAc(
    results, offset: int = 1, nbits: int = kCoronaAcBits, strict: bool = True
) -> bool:
    """
    Decode the supplied Corona AC message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeCoronaAc
    """
    from app.core.ir_protocols.ir_recv import _matchGeneric

    isLong = results.rawlen >= kCoronaAcBits * 2
    if (
        results.rawlen
        < 2 * nbits + (kCoronaAcOverhead if isLong else kCoronaAcOverheadShort) - offset
    ):
        return False  # Too short a message to match.
    if strict and nbits != kCoronaAcBits and nbits != kCoronaAcBitsShort:
        return False

    pos = 0
    used = 0

    # Data Section #1 - 3 loop
    # e.g.
    #   bits = 56; bytes = 7;
    # #1  *(results->state + pos) = {0x28, 0x61, 0x3D, 0x19, 0xE6, 0x37, 0xC8};
    # #2  *(results->state + pos) = {0x28, 0x61, 0x6D, 0xFF, 0x00, 0xFF, 0x00};
    # #3  *(results->state + pos) = {0x28, 0x61, 0xCD, 0xFF, 0x00, 0xFF, 0x00};
    for section in range(kCoronaAcSections):
        used = _matchGeneric(
            data_ptr=results.rawbuf[offset:],
            result_bits_ptr=None,
            result_bytes_ptr=results.state[pos:],
            use_bits=False,
            remaining=results.rawlen - offset,
            nbits=kCoronaAcBitsShort,
            hdrmark=kCoronaAcHdrMark,
            hdrspace=kCoronaAcHdrSpace,
            onemark=kCoronaAcBitMark,
            onespace=kCoronaAcOneSpace,
            zeromark=kCoronaAcBitMark,
            zerospace=kCoronaAcZeroSpace,
            footermark=kCoronaAcBitMark,
            footerspace=kCoronaAcSpaceGap,
            atleast=True,
            tolerance=kCoronaTolerance,
            excess=0,  # kMarkExcess
            MSBfirst=False,
        )
        if used == 0:
            return False  # We failed to find any data.
        # short versions section 0 is special
        if strict and not validSectionCorona(results.state, pos, 3 if not isLong else section):
            return False
        offset += used  # Adjust for how much of the message we read.
        pos += kCoronaAcSectionBytes  # Adjust by how many bytes of data was read
        # don't read more data then what we have
        if results.rawlen <= offset:
            break

    # Re-check we got the correct size/length due to the way we read the data.
    if strict and pos * 8 != kCoronaAcBits and pos * 8 != kCoronaAcBitsShort:
        return False

    # Success
    results.decode_type = "CORONA_AC"
    results.bits = pos * 8
    # No need to record the state as we stored it as we decoded it.
    # As we use result->state, we don't record value, address, or command as it
    # is a union data type.
    return True


## Class for handling detailed Corona A/C messages.
## Direct translation from C++ IRCoronaAc class (ir_Corona.h lines 107-167, ir_Corona.cpp)
class IRCoronaAc:
    ## Class Constructor
    ## @param[in] pin GPIO to be used when sending.
    ## @param[in] inverted Is the output signal to be inverted?
    ## @param[in] use_modulation Is frequency modulation to be used?
    ## Direct translation from ir_Corona.cpp lines 144-150
    def __init__(self) -> None:
        self._: CoronaProtocol = CoronaProtocol()
        self.stateReset()

    ## Reset the internal state to a fixed known good state.
    ## @note The state is powered off.
    ## Direct translation from ir_Corona.cpp lines 152-165
    def stateReset(self) -> None:
        # known good state
        section_pos = kCoronaAcSettingsSection * kCoronaAcSectionBytes
        self._.raw[section_pos + 3] = kCoronaAcSectionData0Base
        self._.raw[section_pos + 5] = 0x00  # ensure no unset mem
        self.setPowerButton(True)  # we default to this on, any timer removes it
        self.setTemp(kCoronaAcMinTemp)
        self.setMode(kCoronaAcModeCool)
        self.setFan(kCoronaAcFanAuto)
        self.setOnTimer(kCoronaAcTimerOff)
        self.setOffTimer(kCoronaAcTimerOff)
        # headers and checks are fixed in getRaw by checksum(_.raw)

    ## Get a copy of the internal state as a valid code for this protocol.
    ## @return A Ptr to a valid code for this protocol based on the current
    ##   internal state.
    ## @note To get stable AC state, if no timers, send once
    ##   without PowerButton set, and once with
    ## Direct translation from ir_Corona.cpp lines 269-277
    def getRaw(self) -> List[int]:
        checksumCorona(self._.raw)  # Ensure correct check bits before sending.
        return self._.raw

    ## Set the internal state from a valid code for this protocol.
    ## @param[in] new_code A valid state for this protocol.
    ## @param[in] length of the new_code array.
    ## Direct translation from ir_Corona.cpp lines 279-284
    def setRaw(self, new_code: List[int], length: int = kCoronaAcStateLength) -> None:
        for i in range(min(length, kCoronaAcStateLength)):
            self._.raw[i] = new_code[i]

    ## Set the temp in deg C.
    ## @param[in] temp The desired temperature in Celsius.
    ## Direct translation from ir_Corona.cpp lines 286-292
    def setTemp(self, temp: int) -> None:
        degrees = max(temp, kCoronaAcMinTemp)
        degrees = min(degrees, kCoronaAcMaxTemp)
        self._.Temp = degrees - kCoronaAcMinTemp + 1

    ## Get the current temperature from the internal state.
    ## @return The current temperature in Celsius.
    ## Direct translation from ir_Corona.cpp lines 294-298
    def getTemp(self) -> int:
        return self._.Temp + kCoronaAcMinTemp - 1

    ## Change the power setting. (in practice Standby, remote power)
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## @note If changed, setPowerButton is also needed,
    ##       unless timer is or was active
    ## Direct translation from ir_Corona.cpp lines 300-311
    def setPower(self, on: bool) -> None:
        self._.Power = on
        # setting power state resets timers that would cause the state
        if on:
            self.setOnTimer(kCoronaAcTimerOff)
        else:
            self.setOffTimer(kCoronaAcTimerOff)

    ## Get the current power setting. (in practice Standby, remote power)
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Corona.cpp lines 313-317
    def getPower(self) -> bool:
        return bool(self._.Power)

    ## Change the power button setting.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## @note this sets that the AC should set power,
    ##   use setPower to define if the AC should end up as on or off
    ##   When no timer is active, the below is a truth table
    ##   With AC On, a command with setPower and setPowerButton gives nothing
    ##   With AC On, a command with setPower but not setPowerButton is ok
    ##   With AC Off, a command with setPower but not setPowerButton gives nothing
    ##   With AC Off, a command with setPower and setPowerButton is ok
    ## Direct translation from ir_Corona.cpp lines 319-330
    def setPowerButton(self, on: bool) -> None:
        self._.PowerButton = on

    ## Get the value of the current power button setting.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Corona.cpp lines 332-336
    def getPowerButton(self) -> bool:
        return bool(self._.PowerButton)

    ## Change the power setting to On.
    ## Direct translation from ir_Corona.cpp line 339
    def on(self) -> None:
        self.setPower(True)

    ## Change the power setting to Off.
    ## Direct translation from ir_Corona.cpp line 342
    def off(self) -> None:
        self.setPower(False)

    ## Get the operating mode setting of the A/C.
    ## @return The current operating mode setting.
    ## Direct translation from ir_Corona.cpp lines 344-348
    def getMode(self) -> int:
        return self._.Mode

    ## Set the operating mode of the A/C.
    ## @param[in] mode The desired operating mode.
    ## Direct translation from ir_Corona.cpp lines 350-363
    def setMode(self, mode: int) -> None:
        if mode in [kCoronaAcModeCool, kCoronaAcModeDry, kCoronaAcModeFan, kCoronaAcModeHeat]:
            self._.Mode = mode
            return
        else:
            self._.Mode = kCoronaAcModeCool

    ## Convert a standard A/C mode into its native mode.
    ## @param[in] mode A stdAc::opmode_t mode to be
    ##   converted to it's native equivalent
    ## @return The corresponding native mode.
    ## Direct translation from ir_Corona.cpp lines 365-376
    @staticmethod
    def convertMode(mode: str) -> int:
        """Convert common mode to native mode"""
        if mode == "fan":
            return kCoronaAcModeFan
        elif mode == "dry":
            return kCoronaAcModeDry
        elif mode == "heat":
            return kCoronaAcModeHeat
        else:
            return kCoronaAcModeCool

    ## Convert a native mode to it's common stdAc::opmode_t equivalent.
    ## @param[in] mode A native operation mode to be converted.
    ## @return The corresponding common stdAc::opmode_t mode.
    ## Direct translation from ir_Corona.cpp lines 378-388
    @staticmethod
    def toCommonMode(mode: int) -> str:
        """Convert native mode to common mode"""
        if mode == kCoronaAcModeFan:
            return "fan"
        elif mode == kCoronaAcModeDry:
            return "dry"
        elif mode == kCoronaAcModeHeat:
            return "heat"
        else:
            return "cool"

    ## Get the operating speed of the A/C Fan
    ## @return The current operating fan speed setting
    ## Direct translation from ir_Corona.cpp lines 390-394
    def getFan(self) -> int:
        return self._.Fan

    ## Set the operating speed of the A/C Fan
    ## @param[in] speed The desired fan speed
    ## Direct translation from ir_Corona.cpp lines 396-403
    def setFan(self, speed: int) -> None:
        if speed > kCoronaAcFanHigh:
            self._.Fan = kCoronaAcFanAuto
        else:
            self._.Fan = speed

    ## Change the powersave setting.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Corona.cpp lines 405-409
    def setEcono(self, on: bool) -> None:
        self._.Econo = on

    ## Get the value of the current powersave setting.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Corona.cpp lines 411-415
    def getEcono(self) -> bool:
        return bool(self._.Econo)

    ## Convert a standard A/C Fan speed into its native fan speed.
    ## @param[in] speed The desired stdAc::fanspeed_t fan speed
    ## @return The given fan speed in native format
    ## Direct translation from ir_Corona.cpp lines 417-429
    @staticmethod
    def convertFan(speed: str) -> int:
        """Convert common fan speed to native fan speed"""
        if speed in ["min", "low"]:
            return kCoronaAcFanLow
        elif speed == "medium":
            return kCoronaAcFanMedium
        elif speed in ["high", "max"]:
            return kCoronaAcFanHigh
        else:
            return kCoronaAcFanAuto

    ## Convert a native fan speed to it's common equivalent.
    ## @param[in] speed The desired native fan speed
    ## @return The given fan speed in stdAc::fanspeed_t format
    ## Direct translation from ir_Corona.cpp lines 431-441
    @staticmethod
    def toCommonFanSpeed(speed: int) -> str:
        """Convert native fan speed to common fan speed"""
        if speed == kCoronaAcFanHigh:
            return "high"
        elif speed == kCoronaAcFanMedium:
            return "medium"
        elif speed == kCoronaAcFanLow:
            return "low"
        else:
            return "auto"

    ## Set the Vertical Swing toggle setting
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## @note This is a button press, and not a state
    ##       after sending it once you should turn it off
    ## Direct translation from ir_Corona.cpp lines 443-449
    def setSwingVToggle(self, on: bool) -> None:
        self._.SwingVToggle = on

    ## Get the Vertical Swing toggle setting
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Corona.cpp lines 451-455
    def getSwingVToggle(self) -> bool:
        return bool(self._.SwingVToggle)

    ## Set the Timer time
    ## @param[in] section index of section, used for offset.
    ## @param[in] nr_of_mins Number of minutes to set the timer to.
    ##   (non in range value is disable).
    ##   Valid is from 1 minute to 12 hours
    ## Direct translation from ir_Corona.cpp lines 457-477
    def _setTimer(self, section: int, nr_of_mins: int) -> None:
        # default to off
        hsecs = kCoronaAcTimerOff
        if 1 <= nr_of_mins <= kCoronaAcTimerMax:
            hsecs = nr_of_mins * kCoronaAcTimerUnitsPerMin

        # convert 16 bit value to separate 8 bit parts
        section_pos = section * kCoronaAcSectionBytes
        self._.raw[section_pos + 5] = hsecs >> 8
        self._.raw[section_pos + 3] = hsecs & 0xFF

        # if any timer is enabled, then (remote) ac must be on (Standby)
        if hsecs != kCoronaAcTimerOff:
            self._.Power = True
            self.setPowerButton(False)

    ## Get the current Timer time
    ## @return The number of minutes it is set for. 0 means it's off.
    ## @note The A/C protocol supports 2 second increments
    ## Direct translation from ir_Corona.cpp lines 479-491
    def _getTimer(self, section: int) -> int:
        # combine separate 8 bit parts to 16 bit value
        section_pos = section * kCoronaAcSectionBytes
        hsecs = (self._.raw[section_pos + 5] << 8) | self._.raw[section_pos + 3]

        if hsecs == kCoronaAcTimerOff:
            return 0

        return hsecs // kCoronaAcTimerUnitsPerMin

    ## Get the current On Timer time
    ## @return The number of minutes it is set for. 0 means it's off.
    ## Direct translation from ir_Corona.cpp lines 493-497
    def getOnTimer(self) -> int:
        return self._getTimer(kCoronaAcOnTimerSection)

    ## Set the On Timer time
    ## @param[in] nr_of_mins Number of minutes to set the timer to.
    ##   (0 or kCoronaAcTimerOff is disable).
    ## Direct translation from ir_Corona.cpp lines 499-507
    def setOnTimer(self, nr_of_mins: int) -> None:
        self._setTimer(kCoronaAcOnTimerSection, nr_of_mins)
        # if we set a timer value, clear the other timer
        if self.getOnTimer():
            self.setOffTimer(kCoronaAcTimerOff)

    ## Get the current Off Timer time
    ## @return The number of minutes it is set for. 0 means it's off.
    ## Direct translation from ir_Corona.cpp lines 509-513
    def getOffTimer(self) -> int:
        return self._getTimer(kCoronaAcOffTimerSection)

    ## Set the Off Timer time
    ## @param[in] nr_of_mins Number of minutes to set the timer to.
    ##   (0 or kCoronaAcTimerOff is disable).
    ## Direct translation from ir_Corona.cpp lines 515-523
    def setOffTimer(self, nr_of_mins: int) -> None:
        self._setTimer(kCoronaAcOffTimerSection, nr_of_mins)
        # if we set a timer value, clear the other timer
        if self.getOffTimer():
            self.setOnTimer(kCoronaAcTimerOff)

    ## Convert the internal state into a human readable string.
    ## @return The current internal state expressed as a human readable String.
    ## Direct translation from ir_Corona.cpp lines 525-548
    def toString(self) -> str:
        """Convert the internal state to a human readable string"""
        result = ""
        result += "Power: "
        result += "On" if self._.Power else "Off"
        result += ", PowerButton: "
        result += "On" if self._.PowerButton else "Off"
        result += ", Mode: "
        result += str(self._.Mode)
        result += ", Temp: "
        result += str(self.getTemp()) + "C"
        result += ", Fan: "
        result += str(self._.Fan)
        result += ", SwingVToggle: "
        result += "On" if self._.SwingVToggle else "Off"
        result += ", Econo: "
        result += "On" if self._.Econo else "Off"
        result += ", OnTimer: "
        result += str(self.getOnTimer()) + "m" if self.getOnTimer() else "Off"
        result += ", OffTimer: "
        result += str(self.getOffTimer()) + "m" if self.getOffTimer() else "Off"
        return result

    ## Convert the A/C state to it's common stdAc::state_t equivalent.
    ## @return A stdAc::state_t state.
    ## Direct translation from ir_Corona.cpp lines 550-575
    def toCommon(self) -> dict:
        """Convert the internal state to common A/C state"""
        result = {}
        result["protocol"] = "CORONA_AC"
        result["model"] = -1  # No models used.
        result["power"] = bool(self._.Power)
        result["mode"] = self.toCommonMode(self._.Mode)
        result["celsius"] = True
        result["degrees"] = self.getTemp()
        result["fanspeed"] = self.toCommonFanSpeed(self._.Fan)
        result["swingv"] = "auto" if self._.SwingVToggle else "off"
        result["econo"] = bool(self._.Econo)
        # Not supported.
        result["sleep"] = -1
        result["swingh"] = "off"
        result["turbo"] = False
        result["quiet"] = False
        result["clean"] = False
        result["filter"] = False
        result["beep"] = False
        result["light"] = False
        result["clock"] = -1
        return result
