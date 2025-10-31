# Copyright 2017 stufisher
# Copyright 2019 crankyoldgit
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Support for Trotec protocols.
## Direct translation from IRremoteESP8266 ir_Trotec.cpp and ir_Trotec.h
## Includes both Trotec and Trotec3550 variants

from typing import List

# Constants - Trotec Timing values
kTrotecHdrMark = 5952
kTrotecHdrSpace = 7364
kTrotecBitMark = 592
kTrotecOneSpace = 1560
kTrotecZeroSpace = 592
kTrotecGap = 6184
kTrotecGapEnd = 1500  # made up value

# Constants - Trotec3550 Timing values
kTrotec3550HdrMark = 12000
kTrotec3550HdrSpace = 5130
kTrotec3550BitMark = 550
kTrotec3550OneSpace = 1950
kTrotec3550ZeroSpace = 500

# State length constants
kTrotecStateLength = 9
kTrotecBits = kTrotecStateLength * 8  # 72 bits

# Trotec intro/header constants
kTrotecIntro1 = 0x12
kTrotecIntro2 = 0x34

# Mode constants (shared by both variants)
kTrotecAuto = 0
kTrotecCool = 1
kTrotecDry = 2
kTrotecFan = 3

# Fan speed constants (shared by both variants)
kTrotecFanLow = 1
kTrotecFanMed = 2
kTrotecFanHigh = 3

# Temperature constants - Trotec
kTrotecMinTemp = 18  # Celsius
kTrotecDefTemp = 25  # Celsius
kTrotecMaxTemp = 32  # Celsius
kTrotecMaxTimer = 23  # Hours

# Temperature constants - Trotec3550
kTrotec3550MinTempC = 16  # Celsius
kTrotec3550MaxTempC = 30  # Celsius
kTrotec3550MinTempF = 59  # Fahrenheit
kTrotec3550MaxTempF = 86  # Fahrenheit
kTrotec3550TimerMax = 8 * 60  # 8 hours in Minutes


## Helper functions for temperature conversion
def celsiusToFahrenheit(temp: float) -> int:
    """Convert Celsius to Fahrenheit"""
    return int(temp * 1.8 + 32.0)


def fahrenheitToCelsius(temp: float) -> int:
    """Convert Fahrenheit to Celsius"""
    return int((temp - 32.0) / 1.8)


## Native representation of a Trotec A/C message.
## This is a direct translation of the C++ union/struct
class TrotecProtocol:
    def __init__(self):
        # The state array (9 bytes for Trotec)
        self.raw = [0] * kTrotecStateLength

    # Byte 0
    @property
    def Intro1(self) -> int:
        return self.raw[0]

    @Intro1.setter
    def Intro1(self, value: int) -> None:
        self.raw[0] = value & 0xFF

    # Byte 1
    @property
    def Intro2(self) -> int:
        return self.raw[1]

    @Intro2.setter
    def Intro2(self, value: int) -> None:
        self.raw[1] = value & 0xFF

    # Byte 2
    @property
    def Mode(self) -> int:
        return self.raw[2] & 0x03

    @Mode.setter
    def Mode(self, value: int) -> None:
        self.raw[2] = (self.raw[2] & 0xFC) | (value & 0x03)

    @property
    def Power(self) -> int:
        return (self.raw[2] >> 3) & 0x01

    @Power.setter
    def Power(self, value: bool) -> None:
        if value:
            self.raw[2] |= 0x08
        else:
            self.raw[2] &= 0xF7

    @property
    def Fan(self) -> int:
        return (self.raw[2] >> 4) & 0x03

    @Fan.setter
    def Fan(self, value: int) -> None:
        self.raw[2] = (self.raw[2] & 0xCF) | ((value & 0x03) << 4)

    # Byte 3
    @property
    def Temp(self) -> int:
        return self.raw[3] & 0x0F

    @Temp.setter
    def Temp(self, value: int) -> None:
        self.raw[3] = (self.raw[3] & 0xF0) | (value & 0x0F)

    @property
    def Sleep(self) -> int:
        return (self.raw[3] >> 7) & 0x01

    @Sleep.setter
    def Sleep(self, value: bool) -> None:
        if value:
            self.raw[3] |= 0x80
        else:
            self.raw[3] &= 0x7F

    # Byte 5
    @property
    def Timer(self) -> int:
        return (self.raw[5] >> 6) & 0x01

    @Timer.setter
    def Timer(self, value: bool) -> None:
        if value:
            self.raw[5] |= 0x40
        else:
            self.raw[5] &= 0xBF

    # Byte 6
    @property
    def Hours(self) -> int:
        return self.raw[6]

    @Hours.setter
    def Hours(self, value: int) -> None:
        self.raw[6] = value & 0xFF

    # Byte 8
    @property
    def Sum(self) -> int:
        return self.raw[8]

    @Sum.setter
    def Sum(self, value: int) -> None:
        self.raw[8] = value & 0xFF


## Native representation of a Trotec 3550 A/C message.
## This is a direct translation of the C++ union/struct
class Trotec3550Protocol:
    def __init__(self):
        # The state array (9 bytes for Trotec3550)
        self.raw = [0] * kTrotecStateLength

    # Byte 0
    @property
    def Intro(self) -> int:
        return self.raw[0]

    @Intro.setter
    def Intro(self, value: int) -> None:
        self.raw[0] = value & 0xFF

    # Byte 1
    @property
    def SwingV(self) -> int:
        return self.raw[1] & 0x01

    @SwingV.setter
    def SwingV(self, value: bool) -> None:
        if value:
            self.raw[1] |= 0x01
        else:
            self.raw[1] &= 0xFE

    @property
    def Power(self) -> int:
        return (self.raw[1] >> 1) & 0x01

    @Power.setter
    def Power(self, value: bool) -> None:
        if value:
            self.raw[1] |= 0x02
        else:
            self.raw[1] &= 0xFD

    @property
    def TimerSet(self) -> int:
        return (self.raw[1] >> 3) & 0x01

    @TimerSet.setter
    def TimerSet(self, value: bool) -> None:
        if value:
            self.raw[1] |= 0x08
        else:
            self.raw[1] &= 0xF7

    @property
    def TempC(self) -> int:
        return (self.raw[1] >> 4) & 0x0F

    @TempC.setter
    def TempC(self, value: int) -> None:
        self.raw[1] = (self.raw[1] & 0x0F) | ((value & 0x0F) << 4)

    # Byte 2
    @property
    def TimerHrs(self) -> int:
        return self.raw[2] & 0x0F

    @TimerHrs.setter
    def TimerHrs(self, value: int) -> None:
        self.raw[2] = (self.raw[2] & 0xF0) | (value & 0x0F)

    # Byte 3
    @property
    def TempF(self) -> int:
        return self.raw[3] & 0x1F

    @TempF.setter
    def TempF(self, value: int) -> None:
        self.raw[3] = (self.raw[3] & 0xE0) | (value & 0x1F)

    # Byte 6
    @property
    def Mode(self) -> int:
        return self.raw[6] & 0x03

    @Mode.setter
    def Mode(self, value: int) -> None:
        self.raw[6] = (self.raw[6] & 0xFC) | (value & 0x03)

    @property
    def Fan(self) -> int:
        return (self.raw[6] >> 4) & 0x03

    @Fan.setter
    def Fan(self, value: int) -> None:
        self.raw[6] = (self.raw[6] & 0xCF) | ((value & 0x03) << 4)

    # Byte 7
    @property
    def Celsius(self) -> int:
        return (self.raw[7] >> 7) & 0x01

    @Celsius.setter
    def Celsius(self, value: bool) -> None:
        if value:
            self.raw[7] |= 0x80
        else:
            self.raw[7] &= 0x7F

    # Byte 8
    @property
    def Sum(self) -> int:
        return self.raw[8]

    @Sum.setter
    def Sum(self, value: int) -> None:
        self.raw[8] = value & 0xFF


## Calculate the checksum for a given state (Trotec).
## EXACT translation from IRremoteESP8266 IRTrotecESP::calcChecksum (ir_Trotec.cpp lines 91-94)
def calcChecksumTrotec(state: List[int], length: int = kTrotecStateLength) -> int:
    """
    Calculate checksum for Trotec protocol.
    EXACT translation from IRremoteESP8266 IRTrotecESP::calcChecksum
    """
    from app.core.ir_protocols.ir_recv import sumBytes

    return sumBytes(state, 2, length - 3)


## Verify the checksum is valid for a given state (Trotec).
## EXACT translation from IRremoteESP8266 IRTrotecESP::validChecksum (ir_Trotec.cpp lines 100-102)
def validChecksumTrotec(state: List[int], length: int = kTrotecStateLength) -> bool:
    """
    Verify the checksum is valid for a given state (Trotec).
    EXACT translation from IRremoteESP8266 IRTrotecESP::validChecksum
    """
    return state[length - 1] == calcChecksumTrotec(state, length)


## Calculate the checksum for a given state (Trotec3550).
## EXACT translation from IRremoteESP8266 IRTrotec3550::calcChecksum (ir_Trotec.cpp lines 423-426)
def calcChecksumTrotec3550(state: List[int], length: int = kTrotecStateLength) -> int:
    """
    Calculate checksum for Trotec3550 protocol.
    EXACT translation from IRremoteESP8266 IRTrotec3550::calcChecksum
    """
    if length == 0:
        return 0
    from app.core.ir_protocols.ir_recv import sumBytes

    return sumBytes(state, 0, length - 1)


## Verify the checksum is valid for a given state (Trotec3550).
## EXACT translation from IRremoteESP8266 IRTrotec3550::validChecksum (ir_Trotec.cpp lines 432-434)
def validChecksumTrotec3550(state: List[int], length: int = kTrotecStateLength) -> bool:
    """
    Verify the checksum is valid for a given state (Trotec3550).
    EXACT translation from IRremoteESP8266 IRTrotec3550::validChecksum
    """
    return state[length - 1] == calcChecksumTrotec3550(state, length)


## Send a Trotec message.
## Status: Beta / Probably Working.
## EXACT translation from IRremoteESP8266 IRsend::sendTrotec (ir_Trotec.cpp lines 50-65)
def sendTrotec(data: List[int], nbytes: int, repeat: int = 0) -> List[int]:
    """
    Send a Trotec formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendTrotec

    Returns timing array instead of transmitting via hardware.
    """
    if nbytes < kTrotecStateLength:
        return []

    # Import here to avoid circular import
    from app.core.ir_protocols.ir_send import sendGeneric

    all_timings = []

    for r in range(repeat + 1):
        # Main message
        msg_timings = sendGeneric(
            headermark=kTrotecHdrMark,
            headerspace=kTrotecHdrSpace,
            onemark=kTrotecBitMark,
            onespace=kTrotecOneSpace,
            zeromark=kTrotecBitMark,
            zerospace=kTrotecZeroSpace,
            footermark=kTrotecBitMark,
            gap=kTrotecGap,
            dataptr=data,
            nbytes=nbytes,
            MSBfirst=False,
        )
        all_timings.extend(msg_timings)

        # More footer
        all_timings.append(kTrotecBitMark)
        all_timings.append(kTrotecGapEnd)

    return all_timings


## Send a Trotec 3550 message.
## Status: STABLE / Known to be working.
## EXACT translation from IRremoteESP8266 IRsend::sendTrotec3550 (ir_Trotec.cpp lines 357-364)
def sendTrotec3550(data: List[int], nbytes: int, repeat: int = 0) -> List[int]:
    """
    Send a Trotec3550 formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendTrotec3550

    Returns timing array instead of transmitting via hardware.
    """
    # Import here to avoid circular import
    from app.core.ir_protocols.ir_send import sendGeneric

    return sendGeneric(
        headermark=kTrotec3550HdrMark,
        headerspace=kTrotec3550HdrSpace,
        onemark=kTrotec3550BitMark,
        onespace=kTrotec3550OneSpace,
        zeromark=kTrotec3550BitMark,
        zerospace=kTrotec3550ZeroSpace,
        footermark=kTrotec3550BitMark,
        gap=100000,  # kDefaultMessageGap
        dataptr=data,
        nbytes=nbytes,
        MSBfirst=True,
    )


## Class for handling detailed Trotec A/C messages.
## Direct translation from C++ IRTrotecESP class
class IRTrotecESP:
    ## Class Constructor
    def __init__(self) -> None:
        self._: TrotecProtocol = TrotecProtocol()
        self.stateReset()

    ## Reset the state of the remote to a known good state/sequence.
    ## Direct translation from ir_Trotec.cpp lines 110-120
    def stateReset(self) -> None:
        for i in range(2, kTrotecStateLength):
            self._.raw[i] = 0x0

        self._.Intro1 = kTrotecIntro1
        self._.Intro2 = kTrotecIntro2

        self._.Power = False
        self.setTemp(kTrotecDefTemp)
        self._.Fan = kTrotecFanMed
        self._.Mode = kTrotecAuto

    ## Calculate & set the checksum for the current internal state of the remote.
    ## Direct translation from ir_Trotec.cpp lines 105-107
    def checksum(self) -> None:
        self._.Sum = calcChecksumTrotec(self._.raw, kTrotecStateLength)

    ## Get a PTR to the internal state/code for this protocol.
    ## Direct translation from ir_Trotec.cpp lines 124-127
    def getRaw(self) -> List[int]:
        self.checksum()
        return self._.raw

    ## Set the internal state from a valid code for this protocol.
    ## Direct translation from ir_Trotec.cpp lines 131-133
    def setRaw(self, state: List[int]) -> None:
        for i in range(min(len(state), kTrotecStateLength)):
            self._.raw[i] = state[i]

    ## Set the requested power state of the A/C to on.
    ## Direct translation from ir_Trotec.cpp line 136
    def on(self) -> None:
        self.setPower(True)

    ## Set the requested power state of the A/C to off.
    ## Direct translation from ir_Trotec.cpp line 139
    def off(self) -> None:
        self.setPower(False)

    ## Change the power setting.
    ## Direct translation from ir_Trotec.cpp lines 143-145
    def setPower(self, on: bool) -> None:
        self._.Power = on

    ## Get the value of the current power setting.
    ## Direct translation from ir_Trotec.cpp lines 149-151
    def getPower(self) -> bool:
        return bool(self._.Power)

    ## Set the speed of the fan.
    ## Direct translation from ir_Trotec.cpp lines 155-158
    def setSpeed(self, fan: int) -> None:
        speed = min(fan, kTrotecFanHigh)
        self._.Fan = speed

    ## Get the current fan speed setting.
    ## Direct translation from ir_Trotec.cpp lines 162-164
    def getSpeed(self) -> int:
        return self._.Fan

    ## Set the operating mode of the A/C.
    ## Direct translation from ir_Trotec.cpp lines 168-170
    def setMode(self, mode: int) -> None:
        self._.Mode = kTrotecAuto if mode > kTrotecFan else mode

    ## Get the operating mode setting of the A/C.
    ## Direct translation from ir_Trotec.cpp lines 174-176
    def getMode(self) -> int:
        return self._.Mode

    ## Set the temperature.
    ## Direct translation from ir_Trotec.cpp lines 180-184
    def setTemp(self, celsius: int) -> None:
        temp = max(celsius, kTrotecMinTemp)
        temp = min(temp, kTrotecMaxTemp)
        self._.Temp = temp - kTrotecMinTemp

    ## Get the current temperature setting.
    ## Direct translation from ir_Trotec.cpp lines 188-190
    def getTemp(self) -> int:
        return self._.Temp + kTrotecMinTemp

    ## Set the Sleep setting of the A/C.
    ## Direct translation from ir_Trotec.cpp lines 194-196
    def setSleep(self, on: bool) -> None:
        self._.Sleep = on

    ## Get the Sleep setting of the A/C.
    ## Direct translation from ir_Trotec.cpp lines 200-202
    def getSleep(self) -> bool:
        return bool(self._.Sleep)

    ## Set the timer time in nr. of Hours.
    ## Direct translation from ir_Trotec.cpp lines 206-209
    def setTimer(self, timer: int) -> None:
        self._.Timer = timer > 0
        self._.Hours = min(timer, kTrotecMaxTimer) if timer > kTrotecMaxTimer else timer

    ## Get the timer time in nr. of Hours.
    ## Direct translation from ir_Trotec.cpp line 213
    def getTimer(self) -> int:
        return self._.Hours


## Class for handling detailed Trotec 3550 A/C messages.
## Direct translation from C++ IRTrotec3550 class
class IRTrotec3550:
    ## Class Constructor
    def __init__(self) -> None:
        self._: Trotec3550Protocol = Trotec3550Protocol()
        self.stateReset()

    ## Reset the state of the remote to a known good state/sequence.
    ## Direct translation from ir_Trotec.cpp lines 440-444
    def stateReset(self) -> None:
        kReset = [0x55, 0x60, 0x00, 0x0D, 0x00, 0x00, 0x10, 0x88, 0x5A]
        for i in range(min(len(kReset), kTrotecStateLength)):
            self._.raw[i] = kReset[i]

    ## Calculate & set the checksum for the current internal state of the remote.
    ## Direct translation from ir_Trotec.cpp line 437
    def checksum(self) -> None:
        self._.Sum = calcChecksumTrotec3550(self._.raw, kTrotecStateLength)

    ## Get a PTR to the internal state/code for this protocol.
    ## Direct translation from ir_Trotec.cpp lines 448-451
    def getRaw(self) -> List[int]:
        self.checksum()
        return self._.raw

    ## Set the internal state from a valid code for this protocol.
    ## Direct translation from ir_Trotec.cpp lines 455-457
    def setRaw(self, state: List[int]) -> None:
        for i in range(min(len(state), kTrotecStateLength)):
            self._.raw[i] = state[i]

    ## Set the requested power state of the A/C to on.
    ## Direct translation from ir_Trotec.cpp line 460
    def on(self) -> None:
        self.setPower(True)

    ## Set the requested power state of the A/C to off.
    ## Direct translation from ir_Trotec.cpp line 463
    def off(self) -> None:
        self.setPower(False)

    ## Change the power setting.
    ## Direct translation from ir_Trotec.cpp line 467
    def setPower(self, on: bool) -> None:
        self._.Power = on

    ## Get the value of the current power setting.
    ## Direct translation from ir_Trotec.cpp line 471
    def getPower(self) -> bool:
        return bool(self._.Power)

    ## Set the speed of the fan.
    ## Direct translation from ir_Trotec.cpp lines 475-478
    def setFan(self, fan: int) -> None:
        speed = min(fan, kTrotecFanHigh)
        self._.Fan = speed

    ## Get the current fan speed setting.
    ## Direct translation from ir_Trotec.cpp line 482
    def getFan(self) -> int:
        return self._.Fan

    ## Set the operating mode of the A/C.
    ## Direct translation from ir_Trotec.cpp lines 486-488
    def setMode(self, mode: int) -> None:
        self._.Mode = kTrotecAuto if mode > kTrotecFan else mode

    ## Get the operating mode setting of the A/C.
    ## Direct translation from ir_Trotec.cpp line 492
    def getMode(self) -> int:
        return self._.Mode

    ## Set the temperature.
    ## Direct translation from ir_Trotec.cpp lines 497-514
    def setTemp(self, degrees: int, celsius: bool = True) -> None:
        self.setTempUnit(celsius)
        minTemp = kTrotec3550MinTempC if celsius else kTrotec3550MinTempF
        maxTemp = kTrotec3550MaxTempC if celsius else kTrotec3550MaxTempF
        temp = max(degrees, minTemp)
        temp = min(temp, maxTemp)
        if celsius:
            self._.TempC = temp - minTemp
            self._.TempF = celsiusToFahrenheit(temp) - kTrotec3550MinTempF
        else:
            self._.TempF = temp - minTemp
            self._.TempC = fahrenheitToCelsius(temp) - kTrotec3550MinTempC

    ## Get the current temperature setting.
    ## Direct translation from ir_Trotec.cpp lines 518-521
    def getTemp(self) -> int:
        if self.getTempUnit():
            return self._.TempC + kTrotec3550MinTempC
        else:
            return self._.TempF + kTrotec3550MinTempF

    ## Set the temperature unit that the A/C will use..
    ## Direct translation from ir_Trotec.cpp line 525
    def setTempUnit(self, celsius: bool) -> None:
        self._.Celsius = celsius

    ## Get the current temperature unit setting.
    ## Direct translation from ir_Trotec.cpp line 529
    def getTempUnit(self) -> bool:
        return bool(self._.Celsius)

    ## Change the Vertical Swing setting.
    ## Direct translation from ir_Trotec.cpp line 533
    def setSwingV(self, on: bool) -> None:
        self._.SwingV = on

    ## Get the value of the current Vertical Swing setting.
    ## Direct translation from ir_Trotec.cpp line 537
    def getSwingV(self) -> bool:
        return bool(self._.SwingV)

    ## Get the number of minutes of the Timer setting.
    ## Direct translation from ir_Trotec.cpp line 541
    def getTimer(self) -> int:
        return self._.TimerHrs * 60

    ## Set the number of minutes of the Timer setting.
    ## Direct translation from ir_Trotec.cpp lines 545-548
    def setTimer(self, mins: int) -> None:
        self._.TimerSet = mins > 0
        self._.TimerHrs = min(mins, kTrotec3550TimerMax) // 60


## Decode the supplied Trotec message.
## Status: STABLE / Works. Untested on real devices.
## EXACT translation from IRremoteESP8266 IRrecv::decodeTrotec (ir_Trotec.cpp lines 316-348)
def decodeTrotec(results, offset: int = 1, nbits: int = kTrotecBits, strict: bool = True) -> bool:
    """
    Decode a Trotec HVAC IR message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeTrotec

    This is the ACTUAL C++ decoder function, not a wrapper.
    """
    # Import here to avoid circular imports
    from app.core.ir_protocols.ir_recv import (
        kHeader,
        kFooter,
        _matchGeneric,
        matchMark,
        matchAtLeast,
    )

    if results.rawlen <= 2 * nbits + kHeader + 2 * kFooter - 1 + offset:
        return False  # Can't possibly be a valid Trotec A/C message.
    if strict and nbits != kTrotecBits:
        return False

    # Header + Data + Footer #1
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state,
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=nbits,
        hdrmark=kTrotecHdrMark,
        hdrspace=kTrotecHdrSpace,
        onemark=kTrotecBitMark,
        onespace=kTrotecOneSpace,
        zeromark=kTrotecBitMark,
        zerospace=kTrotecZeroSpace,
        footermark=kTrotecBitMark,
        footerspace=kTrotecGap,
        atleast=True,
        tolerance=25,
        excess=0,
        MSBfirst=False,
    )
    if used == 0:
        return False
    offset += used

    # Footer #2
    if not matchMark(results.rawbuf[offset], kTrotecBitMark):
        return False
    offset += 1
    if offset <= results.rawlen and not matchAtLeast(results.rawbuf[offset], kTrotecGapEnd):
        return False

    # Compliance
    # Verify we got a valid checksum.
    if strict and not validChecksumTrotec(results.state, kTrotecStateLength):
        return False

    # Success
    results.bits = nbits
    # No need to record the state as we stored it as we decoded it.
    # As we use result->state, we don't record value, address, or command as it
    # is a union data type.
    return True


## Decode the supplied Trotec 3550 message.
## Status: STABLE / Known to be working.
## EXACT translation from IRremoteESP8266 IRrecv::decodeTrotec3550 (ir_Trotec.cpp lines 376-397)
def decodeTrotec3550(
    results, offset: int = 1, nbits: int = kTrotecBits, strict: bool = True
) -> bool:
    """
    Decode a Trotec3550 HVAC IR message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeTrotec3550

    This is the ACTUAL C++ decoder function, not a wrapper.
    """
    # Import here to avoid circular imports
    from app.core.ir_protocols.ir_recv import _matchGeneric

    if strict and nbits != kTrotecBits:
        return False

    # Header + Data + Footer
    if not _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state,
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=nbits,
        hdrmark=kTrotec3550HdrMark,
        hdrspace=kTrotec3550HdrSpace,
        onemark=kTrotec3550BitMark,
        onespace=kTrotec3550OneSpace,
        zeromark=kTrotec3550BitMark,
        zerospace=kTrotec3550ZeroSpace,
        footermark=kTrotec3550BitMark,
        footerspace=100000,  # kDefaultMessageGap
        atleast=False,
        tolerance=25,
        excess=0,
        MSBfirst=True,
    ):
        return False

    # Compliance
    if strict and not validChecksumTrotec3550(results.state, nbits // 8):
        return False

    # Success
    results.bits = nbits
    # No need to record the state as we stored it as we decoded it.
    # As we use result->state, we don't record value, address, or command as it
    # is a union data type.
    return True
