# Copyright 2018 David Conran
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Support for Whirlpool protocols.
## Direct translation from IRremoteESP8266 ir_Whirlpool.cpp and ir_Whirlpool.h

from typing import List

# Ref: https://github.com/crankyoldgit/IRremoteESP8266/issues/509
# Note: Smart, iFeel, AroundU, PowerSave, & Silent modes are unsupported.
#   Advanced 6thSense, Dehumidify, & Sleep modes are not supported.
# Note: Dim == !Light, Jet == Super == Turbo

# Constants
kWhirlpoolAcHdrMark = 8950
kWhirlpoolAcHdrSpace = 4484
kWhirlpoolAcBitMark = 597
kWhirlpoolAcOneSpace = 1649
kWhirlpoolAcZeroSpace = 533
kWhirlpoolAcGap = 7920
kWhirlpoolAcMinGap = 43000  # kDefaultMessageGap - Just a guess.
kWhirlpoolAcSections = 3
kWhirlpoolAcStateLength = 21
kWhirlpoolAcBits = kWhirlpoolAcStateLength * 8

kWhirlpoolAcChecksumByte1 = 13
kWhirlpoolAcChecksumByte2 = kWhirlpoolAcStateLength - 1

# Mode constants
kWhirlpoolAcHeat = 0
kWhirlpoolAcAuto = 1
kWhirlpoolAcCool = 2
kWhirlpoolAcDry = 3
kWhirlpoolAcFan = 4

# Fan constants
kWhirlpoolAcFanAuto = 0
kWhirlpoolAcFanHigh = 1
kWhirlpoolAcFanMedium = 2
kWhirlpoolAcFanLow = 3

# Temperature constants
kWhirlpoolAcMinTemp = 18  # 18C (DG11J1-3A), 16C (DG11J1-91)
kWhirlpoolAcMaxTemp = 32  # 32C (DG11J1-3A), 30C (DG11J1-91)
kWhirlpoolAcAutoTemp = 23  # 23C

# Command constants
kWhirlpoolAcCommandLight = 0x00
kWhirlpoolAcCommandPower = 0x01
kWhirlpoolAcCommandTemp = 0x02
kWhirlpoolAcCommandSleep = 0x03
kWhirlpoolAcCommandSuper = 0x04
kWhirlpoolAcCommandOnTimer = 0x05
kWhirlpoolAcCommandMode = 0x06
kWhirlpoolAcCommandSwing = 0x07
kWhirlpoolAcCommandIFeel = 0x0D
kWhirlpoolAcCommandFanSpeed = 0x11
kWhirlpoolAcCommand6thSense = 0x17
kWhirlpoolAcCommandOffTimer = 0x1D

# Model enums
WHIRLPOOL_DG11J13A = 0
WHIRLPOOL_DG11J191 = 1


# Macros for time handling
def GETTIME_HOURS(state: List[int], prefix: str) -> int:
    """Get hours from timer state"""
    if prefix == "Clock":
        return state[6] & 0x1F
    elif prefix == "Off":
        return state[8] & 0x1F
    elif prefix == "On":
        return state[10] & 0x1F
    return 0


def GETTIME_MINS(state: List[int], prefix: str) -> int:
    """Get minutes from timer state"""
    if prefix == "Clock":
        return state[7] & 0x3F
    elif prefix == "Off":
        return state[9] & 0x3F
    elif prefix == "On":
        return state[11] & 0x3F
    return 0


def GETTIME(state: List[int], prefix: str) -> int:
    """Get total minutes from timer state"""
    return GETTIME_HOURS(state, prefix) * 60 + GETTIME_MINS(state, prefix)


def SETTIME_HOURS(state: List[int], prefix: str, value: int) -> None:
    """Set hours in timer state"""
    if prefix == "Clock":
        state[6] = (state[6] & 0xE0) | (value & 0x1F)
    elif prefix == "Off":
        state[8] = (state[8] & 0xE0) | (value & 0x1F)
    elif prefix == "On":
        state[10] = (state[10] & 0xE0) | (value & 0x1F)


def SETTIME_MINS(state: List[int], prefix: str, value: int) -> None:
    """Set minutes in timer state"""
    if prefix == "Clock":
        state[7] = (state[7] & 0xC0) | (value & 0x3F)
    elif prefix == "Off":
        state[9] = (state[9] & 0xC0) | (value & 0x3F)
    elif prefix == "On":
        state[11] = (state[11] & 0xC0) | (value & 0x3F)


def SETTIME(state: List[int], prefix: str, mins: int) -> None:
    """Set time from total minutes"""
    SETTIME_HOURS(state, prefix, (mins // 60) % 24)
    SETTIME_MINS(state, prefix, mins % 60)


def xorBytes(data: List[int], length: int) -> int:
    """XOR bytes in data array starting from index 0"""
    result = 0
    for i in range(length):
        result ^= data[i]
    return result


## Native representation of a Whirlpool A/C message.
## This is a direct translation of the C++ union/struct
class WhirlpoolProtocol:
    def __init__(self):
        # The state array (21 bytes for Whirlpool AC)
        self.raw = [0] * kWhirlpoolAcStateLength

    # Byte 2
    @property
    def Fan(self) -> int:
        return self.raw[2] & 0x03

    @Fan.setter
    def Fan(self, value: int) -> None:
        self.raw[2] = (self.raw[2] & 0xFC) | (value & 0x03)

    @property
    def Power(self) -> int:
        return (self.raw[2] >> 2) & 0x01

    @Power.setter
    def Power(self, value: bool) -> None:
        if value:
            self.raw[2] |= 0x04
        else:
            self.raw[2] &= 0xFB

    @property
    def Sleep(self) -> int:
        return (self.raw[2] >> 3) & 0x01

    @Sleep.setter
    def Sleep(self, value: bool) -> None:
        if value:
            self.raw[2] |= 0x08
        else:
            self.raw[2] &= 0xF7

    @property
    def Swing1(self) -> int:
        return (self.raw[2] >> 7) & 0x01

    @Swing1.setter
    def Swing1(self, value: bool) -> None:
        if value:
            self.raw[2] |= 0x80
        else:
            self.raw[2] &= 0x7F

    # Byte 3
    @property
    def Mode(self) -> int:
        return self.raw[3] & 0x07

    @Mode.setter
    def Mode(self, value: int) -> None:
        self.raw[3] = (self.raw[3] & 0xF8) | (value & 0x07)

    @property
    def Temp(self) -> int:
        return (self.raw[3] >> 4) & 0x0F

    @Temp.setter
    def Temp(self, value: int) -> None:
        self.raw[3] = (self.raw[3] & 0x0F) | ((value & 0x0F) << 4)

    # Byte 5
    @property
    def Super1(self) -> int:
        return (self.raw[5] >> 4) & 0x01

    @Super1.setter
    def Super1(self, value: bool) -> None:
        if value:
            self.raw[5] |= 0x10
        else:
            self.raw[5] &= 0xEF

    @property
    def Super2(self) -> int:
        return (self.raw[5] >> 7) & 0x01

    @Super2.setter
    def Super2(self, value: bool) -> None:
        if value:
            self.raw[5] |= 0x80
        else:
            self.raw[5] &= 0x7F

    # Byte 6
    @property
    def ClockHours(self) -> int:
        return self.raw[6] & 0x1F

    @ClockHours.setter
    def ClockHours(self, value: int) -> None:
        self.raw[6] = (self.raw[6] & 0xE0) | (value & 0x1F)

    @property
    def LightOff(self) -> int:
        return (self.raw[6] >> 5) & 0x01

    @LightOff.setter
    def LightOff(self, value: bool) -> None:
        if value:
            self.raw[6] |= 0x20
        else:
            self.raw[6] &= 0xDF

    # Byte 7
    @property
    def ClockMins(self) -> int:
        return self.raw[7] & 0x3F

    @ClockMins.setter
    def ClockMins(self, value: int) -> None:
        self.raw[7] = (self.raw[7] & 0xC0) | (value & 0x3F)

    @property
    def OffTimerEnabled(self) -> int:
        return (self.raw[7] >> 7) & 0x01

    @OffTimerEnabled.setter
    def OffTimerEnabled(self, value: bool) -> None:
        if value:
            self.raw[7] |= 0x80
        else:
            self.raw[7] &= 0x7F

    # Byte 8
    @property
    def OffHours(self) -> int:
        return self.raw[8] & 0x1F

    @OffHours.setter
    def OffHours(self, value: int) -> None:
        self.raw[8] = (self.raw[8] & 0xE0) | (value & 0x1F)

    @property
    def Swing2(self) -> int:
        return (self.raw[8] >> 6) & 0x01

    @Swing2.setter
    def Swing2(self, value: bool) -> None:
        if value:
            self.raw[8] |= 0x40
        else:
            self.raw[8] &= 0xBF

    # Byte 9
    @property
    def OffMins(self) -> int:
        return self.raw[9] & 0x3F

    @OffMins.setter
    def OffMins(self, value: int) -> None:
        self.raw[9] = (self.raw[9] & 0xC0) | (value & 0x3F)

    @property
    def OnTimerEnabled(self) -> int:
        return (self.raw[9] >> 7) & 0x01

    @OnTimerEnabled.setter
    def OnTimerEnabled(self, value: bool) -> None:
        if value:
            self.raw[9] |= 0x80
        else:
            self.raw[9] &= 0x7F

    # Byte 10
    @property
    def OnHours(self) -> int:
        return self.raw[10] & 0x1F

    @OnHours.setter
    def OnHours(self, value: int) -> None:
        self.raw[10] = (self.raw[10] & 0xE0) | (value & 0x1F)

    # Byte 11
    @property
    def OnMins(self) -> int:
        return self.raw[11] & 0x3F

    @OnMins.setter
    def OnMins(self, value: int) -> None:
        self.raw[11] = (self.raw[11] & 0xC0) | (value & 0x3F)

    # Byte 13
    @property
    def Sum1(self) -> int:
        return self.raw[13]

    @Sum1.setter
    def Sum1(self, value: int) -> None:
        self.raw[13] = value & 0xFF

    # Byte 15
    @property
    def Cmd(self) -> int:
        return self.raw[15]

    @Cmd.setter
    def Cmd(self, value: int) -> None:
        self.raw[15] = value & 0xFF

    # Byte 18
    @property
    def J191(self) -> int:
        return (self.raw[18] >> 3) & 0x01

    @J191.setter
    def J191(self, value: bool) -> None:
        if value:
            self.raw[18] |= 0x08
        else:
            self.raw[18] &= 0xF7

    # Byte 20
    @property
    def Sum2(self) -> int:
        return self.raw[20]

    @Sum2.setter
    def Sum2(self, value: int) -> None:
        self.raw[20] = value & 0xFF


## Send a Whirlpool A/C message.
## Status: BETA / Probably works.
## EXACT translation from IRremoteESP8266 IRsend::sendWhirlpoolAC (ir_Whirlpool.cpp lines 55-80)
def sendWhirlpoolAC(
    data: List[int], nbytes: int = kWhirlpoolAcStateLength, repeat: int = 0
) -> List[int]:
    """
    Send a Whirlpool A/C message.
    EXACT translation from IRremoteESP8266 IRsend::sendWhirlpoolAC

    Returns timing array instead of transmitting via hardware.
    """
    if nbytes < kWhirlpoolAcStateLength:
        return []  # Not enough bytes to send a proper message.

    from app.core.ir_protocols.ir_send import sendGeneric

    all_timings = []

    for r in range(repeat + 1):
        # Section 1
        section1_timings = sendGeneric(
            headermark=kWhirlpoolAcHdrMark,
            headerspace=kWhirlpoolAcHdrSpace,
            onemark=kWhirlpoolAcBitMark,
            onespace=kWhirlpoolAcOneSpace,
            zeromark=kWhirlpoolAcBitMark,
            zerospace=kWhirlpoolAcZeroSpace,
            footermark=kWhirlpoolAcBitMark,
            dataptr=data,
            nbytes=6,  # 6 bytes == 48 bits
            MSBfirst=False,
        )
        all_timings.extend(section1_timings)

        # Section 2
        section2_timings = sendGeneric(
            headermark=0,
            headerspace=0,
            onemark=kWhirlpoolAcBitMark,
            onespace=kWhirlpoolAcOneSpace,
            zeromark=kWhirlpoolAcBitMark,
            zerospace=kWhirlpoolAcZeroSpace,
            footermark=kWhirlpoolAcBitMark,
            dataptr=data[6:],
            nbytes=8,  # 8 bytes == 64 bits
            MSBfirst=False,
        )
        all_timings.extend(section2_timings)

        # Section 3
        section3_timings = sendGeneric(
            headermark=0,
            headerspace=0,
            onemark=kWhirlpoolAcBitMark,
            onespace=kWhirlpoolAcOneSpace,
            zeromark=kWhirlpoolAcBitMark,
            zerospace=kWhirlpoolAcZeroSpace,
            footermark=kWhirlpoolAcBitMark,
            dataptr=data[14:],
            nbytes=7,  # 7 bytes == 56 bits
            MSBfirst=False,
        )
        all_timings.extend(section3_timings)

    return all_timings


## Verify the checksum is valid for a given state.
## EXACT translation from IRremoteESP8266 IRWhirlpoolAc::validChecksum (ir_Whirlpool.cpp lines 109-126)
def validChecksumWhirlpoolAc(state: List[int], length: int = kWhirlpoolAcStateLength) -> bool:
    """
    Verify the checksum is valid for a given state.
    EXACT translation from IRremoteESP8266 IRWhirlpoolAc::validChecksum
    """
    if length > kWhirlpoolAcChecksumByte1:
        if state[kWhirlpoolAcChecksumByte1] != xorBytes(
            state[2:kWhirlpoolAcChecksumByte1], kWhirlpoolAcChecksumByte1 - 1 - 2
        ):
            return False

    if length > kWhirlpoolAcChecksumByte2:
        if state[kWhirlpoolAcChecksumByte2] != xorBytes(
            state[kWhirlpoolAcChecksumByte1 + 1 : kWhirlpoolAcChecksumByte2],
            kWhirlpoolAcChecksumByte2 - kWhirlpoolAcChecksumByte1 - 1,
        ):
            return False

    # State is too short to have a checksum or everything checked out.
    return True


## Class for handling detailed Whirlpool A/C messages.
## Direct translation from C++ IRWhirlpoolAc class
class IRWhirlpoolAc:
    ## Class Constructor
    def __init__(self, model: int = WHIRLPOOL_DG11J13A) -> None:
        self._: WhirlpoolProtocol = WhirlpoolProtocol()
        self._desiredtemp: int = kWhirlpoolAcAutoTemp
        self.stateReset()
        self.setModel(model)

    ## Reset the internal state to a fixed known good state.
    ## EXACT translation from ir_Whirlpool.cpp lines 94-100
    def stateReset(self) -> None:
        for i in range(2, kWhirlpoolAcStateLength):
            self._.raw[i] = 0x0
        self._.raw[0] = 0x83
        self._.raw[1] = 0x06
        self._.raw[6] = 0x80
        self._setTemp(kWhirlpoolAcAutoTemp)  # Default to a sane value.

    ## Calculate & set the checksum for the current internal state of the remote.
    ## EXACT translation from ir_Whirlpool.cpp lines 130-136
    def checksum(self, length: int = kWhirlpoolAcStateLength) -> None:
        if length >= kWhirlpoolAcChecksumByte1:
            self._.Sum1 = xorBytes(
                self._.raw[2:kWhirlpoolAcChecksumByte1], kWhirlpoolAcChecksumByte1 - 1 - 2
            )
        if length >= kWhirlpoolAcChecksumByte2:
            self._.Sum2 = xorBytes(
                self._.raw[kWhirlpoolAcChecksumByte1 + 1 : kWhirlpoolAcChecksumByte2],
                kWhirlpoolAcChecksumByte2 - kWhirlpoolAcChecksumByte1 - 1,
            )

    ## Get a copy of the internal state/code for this protocol.
    ## EXACT translation from ir_Whirlpool.cpp lines 151-154
    def getRaw(self, calcchecksum: bool = True) -> List[int]:
        if calcchecksum:
            self.checksum()
        return self._.raw

    ## Set the internal state from a valid code for this protocol.
    ## EXACT translation from ir_Whirlpool.cpp lines 159-161
    def setRaw(self, new_code: List[int], length: int = kWhirlpoolAcStateLength) -> None:
        for i in range(min(length, kWhirlpoolAcStateLength)):
            self._.raw[i] = new_code[i]

    ## Get/Detect the model of the A/C.
    ## EXACT translation from ir_Whirlpool.cpp lines 165-170
    def getModel(self) -> int:
        if self._.J191:
            return WHIRLPOOL_DG11J191
        else:
            return WHIRLPOOL_DG11J13A

    ## Set the model of the A/C to emulate.
    ## EXACT translation from ir_Whirlpool.cpp lines 174-185
    def setModel(self, model: int) -> None:
        if model == WHIRLPOOL_DG11J191:
            self._.J191 = True
        else:
            self._.J191 = False
        self._setTemp(self._desiredtemp)  # Different models have different temp values.

    ## Calculate the temp. offset in deg C for the current model.
    ## EXACT translation from ir_Whirlpool.cpp lines 189-194
    def getTempOffset(self) -> int:
        if self.getModel() == WHIRLPOOL_DG11J191:
            return -2
        else:
            return 0

    ## Set the temperature.
    ## EXACT translation from ir_Whirlpool.cpp lines 200-206
    def _setTemp(self, temp: int, remember: bool = True) -> None:
        if remember:
            self._desiredtemp = temp
        offset = self.getTempOffset()  # Cache the min temp for the model.
        newtemp = max(kWhirlpoolAcMinTemp + offset, temp)
        newtemp = min(kWhirlpoolAcMaxTemp + offset, newtemp)
        self._.Temp = newtemp - (kWhirlpoolAcMinTemp + offset)

    ## Set the temperature.
    ## EXACT translation from ir_Whirlpool.cpp lines 210-214
    def setTemp(self, temp: int) -> None:
        self._setTemp(temp)
        self.setSuper(False)  # Changing temp cancels Super/Jet mode.
        self._.Cmd = kWhirlpoolAcCommandTemp

    ## Get the current temperature setting.
    ## EXACT translation from ir_Whirlpool.cpp lines 218-220
    def getTemp(self) -> int:
        return self._.Temp + kWhirlpoolAcMinTemp + self.getTempOffset()

    ## Set the operating mode of the A/C.
    ## EXACT translation from ir_Whirlpool.cpp lines 225-243
    def _setMode(self, mode: int) -> None:
        if mode == kWhirlpoolAcAuto:
            self.setFan(kWhirlpoolAcFanAuto)
            self._setTemp(kWhirlpoolAcAutoTemp, False)
            self.setSleep(False)  # Cancel sleep mode when in auto/6thsense mode.
            self._.Mode = mode
        elif mode in [kWhirlpoolAcHeat, kWhirlpoolAcCool, kWhirlpoolAcDry, kWhirlpoolAcFan]:
            self._.Mode = mode
        else:
            return

        self._.Cmd = kWhirlpoolAcCommandMode
        if mode == kWhirlpoolAcAuto:
            self._.Cmd = kWhirlpoolAcCommand6thSense

    ## Set the operating mode of the A/C.
    ## EXACT translation from ir_Whirlpool.cpp lines 247-250
    def setMode(self, mode: int) -> None:
        self.setSuper(False)  # Changing mode cancels Super/Jet mode.
        self._setMode(mode)

    ## Get the operating mode setting of the A/C.
    ## EXACT translation from ir_Whirlpool.cpp lines 254-256
    def getMode(self) -> int:
        return self._.Mode

    ## Set the speed of the fan.
    ## EXACT translation from ir_Whirlpool.cpp lines 260-271
    def setFan(self, speed: int) -> None:
        if speed in [
            kWhirlpoolAcFanAuto,
            kWhirlpoolAcFanLow,
            kWhirlpoolAcFanMedium,
            kWhirlpoolAcFanHigh,
        ]:
            self._.Fan = speed
            self.setSuper(False)  # Changing fan speed cancels Super/Jet mode.
            self._.Cmd = kWhirlpoolAcCommandFanSpeed

    ## Get the current fan speed setting.
    ## EXACT translation from ir_Whirlpool.cpp lines 275-277
    def getFan(self) -> int:
        return self._.Fan

    ## Set the (vertical) swing setting of the A/C.
    ## EXACT translation from ir_Whirlpool.cpp lines 281-285
    def setSwing(self, on: bool) -> None:
        self._.Swing1 = on
        self._.Swing2 = on
        self._.Cmd = kWhirlpoolAcCommandSwing

    ## Get the (vertical) swing setting of the A/C.
    ## EXACT translation from ir_Whirlpool.cpp lines 289-291
    def getSwing(self) -> bool:
        return bool(self._.Swing1 and self._.Swing2)

    ## Set the Light (Display/LED) setting of the A/C.
    ## EXACT translation from ir_Whirlpool.cpp lines 295-298
    def setLight(self, on: bool) -> None:
        # Cleared when on.
        self._.LightOff = not on

    ## Get the Light (Display/LED) setting of the A/C.
    ## EXACT translation from ir_Whirlpool.cpp lines 302-304
    def getLight(self) -> bool:
        return not bool(self._.LightOff)

    ## Set the clock time in nr. of minutes past midnight.
    ## EXACT translation from ir_Whirlpool.cpp lines 308-310
    def setClock(self, minspastmidnight: int) -> None:
        SETTIME(self._.raw, "Clock", minspastmidnight)

    ## Get the clock time in nr. of minutes past midnight.
    ## EXACT translation from ir_Whirlpool.cpp lines 314-316
    def getClock(self) -> int:
        return GETTIME(self._.raw, "Clock")

    ## Set the Off Timer time.
    ## EXACT translation from ir_Whirlpool.cpp lines 320-322
    def setOffTimer(self, minspastmidnight: int) -> None:
        SETTIME(self._.raw, "Off", minspastmidnight)

    ## Get the Off Timer time.
    ## EXACT translation from ir_Whirlpool.cpp lines 326-328
    def getOffTimer(self) -> int:
        return GETTIME(self._.raw, "Off")

    ## Is the Off timer enabled?
    ## EXACT translation from ir_Whirlpool.cpp lines 332-334
    def isOffTimerEnabled(self) -> bool:
        return bool(self._.OffTimerEnabled)

    ## Enable the Off Timer.
    ## EXACT translation from ir_Whirlpool.cpp lines 338-341
    def enableOffTimer(self, on: bool) -> None:
        self._.OffTimerEnabled = on
        self._.Cmd = kWhirlpoolAcCommandOffTimer

    ## Set the On Timer time.
    ## EXACT translation from ir_Whirlpool.cpp lines 345-347
    def setOnTimer(self, minspastmidnight: int) -> None:
        SETTIME(self._.raw, "On", minspastmidnight)

    ## Get the On Timer time.
    ## EXACT translation from ir_Whirlpool.cpp lines 351-353
    def getOnTimer(self) -> int:
        return GETTIME(self._.raw, "On")

    ## Is the On timer enabled?
    ## EXACT translation from ir_Whirlpool.cpp lines 357-359
    def isOnTimerEnabled(self) -> bool:
        return bool(self._.OnTimerEnabled)

    ## Enable the On Timer.
    ## EXACT translation from ir_Whirlpool.cpp lines 363-366
    def enableOnTimer(self, on: bool) -> None:
        self._.OnTimerEnabled = on
        self._.Cmd = kWhirlpoolAcCommandOnTimer

    ## Change the power toggle setting.
    ## EXACT translation from ir_Whirlpool.cpp lines 370-374
    def setPowerToggle(self, on: bool) -> None:
        self._.Power = on
        self.setSuper(False)  # Changing power cancels Super/Jet mode.
        self._.Cmd = kWhirlpoolAcCommandPower

    ## Get the value of the current power toggle setting.
    ## EXACT translation from ir_Whirlpool.cpp lines 378-380
    def getPowerToggle(self) -> bool:
        return bool(self._.Power)

    ## Get the Command (Button) setting of the A/C.
    ## EXACT translation from ir_Whirlpool.cpp lines 384-386
    def getCommand(self) -> int:
        return self._.Cmd

    ## Set the Sleep setting of the A/C.
    ## EXACT translation from ir_Whirlpool.cpp lines 390-394
    def setSleep(self, on: bool) -> None:
        self._.Sleep = on
        if on:
            self.setFan(kWhirlpoolAcFanLow)
        self._.Cmd = kWhirlpoolAcCommandSleep

    ## Get the Sleep setting of the A/C.
    ## EXACT translation from ir_Whirlpool.cpp lines 398-400
    def getSleep(self) -> bool:
        return bool(self._.Sleep)

    ## Set the Super (Turbo/Jet) setting of the A/C.
    ## EXACT translation from ir_Whirlpool.cpp lines 404-424
    def setSuper(self, on: bool) -> None:
        if on:
            self.setFan(kWhirlpoolAcFanHigh)
            if self._.Mode == kWhirlpoolAcHeat:
                self.setTemp(kWhirlpoolAcMaxTemp + self.getTempOffset())
            else:
                self.setTemp(kWhirlpoolAcMinTemp + self.getTempOffset())
                self.setMode(kWhirlpoolAcCool)

            self._.Super1 = 1
            self._.Super2 = 1
        else:
            self._.Super1 = 0
            self._.Super2 = 0

        self._.Cmd = kWhirlpoolAcCommandSuper

    ## Get the Super (Turbo/Jet) setting of the A/C.
    ## EXACT translation from ir_Whirlpool.cpp lines 428-430
    def getSuper(self) -> bool:
        return bool(self._.Super1 and self._.Super2)

    ## Set the Command (Button) setting of the A/C.
    ## EXACT translation from ir_Whirlpool.cpp lines 434-436
    def setCommand(self, code: int) -> None:
        self._.Cmd = code


## Decode the supplied Whirlpool A/C message.
## Status: STABLE / Working as intended.
## EXACT translation from IRremoteESP8266 IRrecv::decodeWhirlpoolAC (ir_Whirlpool.cpp lines 607-656)
def decodeWhirlpoolAC(
    results, offset: int = 1, nbits: int = kWhirlpoolAcBits, strict: bool = True
) -> bool:
    """
    Decode the supplied Whirlpool A/C message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeWhirlpoolAC
    """
    from app.core.ir_protocols.ir_recv import (
        kHeader,
        kFooter,
        kMarkExcess,
        matchMark,
        matchSpace,
        _matchGeneric,
    )

    if results.rawlen < 2 * nbits + 4 + kHeader + kFooter - 1 + offset:
        return False  # Can't possibly be a valid Whirlpool A/C message.

    if strict:
        if nbits != kWhirlpoolAcBits:
            return False

    sectionSize = [6, 8, 7]

    # Header
    if not matchMark(results.rawbuf[offset], kWhirlpoolAcHdrMark):
        return False
    offset += 1
    if not matchSpace(results.rawbuf[offset], kWhirlpoolAcHdrSpace):
        return False
    offset += 1

    # Data Sections
    pos = 0
    for section in range(kWhirlpoolAcSections):
        # Section Data
        used = _matchGeneric(
            data_ptr=results.rawbuf[offset:],
            result_bits_ptr=None,
            result_bytes_ptr=results.state[pos:],
            use_bits=False,
            remaining=results.rawlen - offset,
            nbits=sectionSize[section] * 8,
            hdrmark=0,
            hdrspace=0,
            onemark=kWhirlpoolAcBitMark,
            onespace=kWhirlpoolAcOneSpace,
            zeromark=kWhirlpoolAcBitMark,
            zerospace=kWhirlpoolAcZeroSpace,
            footermark=kWhirlpoolAcBitMark,
            footerspace=kWhirlpoolAcGap,
            atleast=(section >= kWhirlpoolAcSections - 1),
            tolerance=25,
            excess=kMarkExcess,
            MSBfirst=False,
        )
        if used == 0:
            return False
        offset += used
        pos += sectionSize[section]

    # Compliance
    if strict:
        # Re-check we got the correct size/length due to the way we read the data.
        if pos * 8 != nbits:
            return False
        if not validChecksumWhirlpoolAc(results.state, nbits // 8):
            return False

    # Success
    results.decode_type = "WHIRLPOOL_AC"
    results.bits = nbits
    # No need to record the state as we stored it as we decoded it.
    return True
