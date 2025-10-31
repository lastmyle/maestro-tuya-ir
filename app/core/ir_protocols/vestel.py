# Copyright 2018 Erdem U. Altinyurt
# Copyright 2019 David Conran
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Support for Vestel protocols.
## Vestel added by Erdem U. Altinyurt
## Direct translation from IRremoteESP8266 ir_Vestel.cpp and ir_Vestel.h

# Supports:
#   Brand: Vestel,  Model: BIOX CXP-9 A/C (9K BTU)

from typing import List

# Ref: None. Totally reverse engineered.

# Constants (from ir_Vestel.h lines 64-92)
kVestelAcHdrMark = 3110
kVestelAcHdrSpace = 9066
kVestelAcBitMark = 520
kVestelAcOneSpace = 1535
kVestelAcZeroSpace = 480
kVestelAcTolerance = 30

# State length constant (from IRremoteESP8266.h line 1432)
kVestelAcBits = 56

# Temperature constants (from ir_Vestel.h lines 71-73)
kVestelAcMinTempH = 16
kVestelAcMinTempC = 18
kVestelAcMaxTemp = 30

# Mode constants (from ir_Vestel.h lines 75-79)
kVestelAcAuto = 0
kVestelAcCool = 1
kVestelAcDry = 2
kVestelAcFan = 3
kVestelAcHeat = 4

# Fan speed constants (from ir_Vestel.h lines 81-86)
kVestelAcFanAuto = 1
kVestelAcFanLow = 5
kVestelAcFanMed = 9
kVestelAcFanHigh = 0xB
kVestelAcFanAutoCool = 0xC
kVestelAcFanAutoHot = 0xD

# Special constants (from ir_Vestel.h lines 88-92)
kVestelAcNormal = 1
kVestelAcSleep = 3
kVestelAcTurbo = 7
kVestelAcIon = 4
kVestelAcSwing = 0xA

# Default states (from ir_Vestel.h lines 94-96)
kVestelAcStateDefault = 0x0F00D9001FEF201
kVestelAcTimeStateDefault = 0x201


## Helper function to extract bits from uint64
## Direct translation from IRremoteESP8266 GETBITS64 macro
def GETBITS64(data: int, offset: int, nbits: int) -> int:
    """Extract bits from uint64. EXACT translation from IRremoteESP8266."""
    mask = (1 << nbits) - 1
    return (data >> offset) & mask


## Helper function for counting bits
## Direct translation from IRutils.cpp countBits (lines 497-506)
def countBits(data: int, length: int, ones: bool = True, init: int = 0) -> int:
    """
    Count the number of bits of a given type (1s or 0s) in an integer.
    EXACT translation from IRremoteESP8266 countBits
    """
    count = init
    bitsSoFar = length
    remainder = data

    while remainder and bitsSoFar:
        if ones:
            if remainder & 1:
                count += 1
        else:
            if not (remainder & 1):
                count += 1
        remainder >>= 1
        bitsSoFar -= 1

    if not ones:
        count += bitsSoFar

    return count


## Native representation of a Vestel A/C message.
## Direct translation of the C++ union/struct (ir_Vestel.h lines 26-61)
class VestelProtocol:
    def __init__(self):
        # The state in IR code form (64-bit value)
        self.cmdState = 0
        self.timeState = 0

    # Command state properties
    # Signature (bits 0-11) - from ir_Vestel.h line 33
    @property
    def Signature(self) -> int:
        return GETBITS64(self.cmdState, 0, 12)

    @Signature.setter
    def Signature(self, value: int) -> None:
        self.cmdState = (self.cmdState & ~0xFFF) | (value & 0xFFF)

    # CmdSum (bits 12-19) - from ir_Vestel.h line 34
    @property
    def CmdSum(self) -> int:
        return GETBITS64(self.cmdState, 12, 8)

    @CmdSum.setter
    def CmdSum(self, value: int) -> None:
        self.cmdState = (self.cmdState & ~(0xFF << 12)) | ((value & 0xFF) << 12)

    # Swing (bits 20-23) - from ir_Vestel.h line 35
    @property
    def Swing(self) -> int:
        return GETBITS64(self.cmdState, 20, 4)

    @Swing.setter
    def Swing(self, value: int) -> None:
        self.cmdState = (self.cmdState & ~(0xF << 20)) | ((value & 0xF) << 20)

    # TurboSleep (bits 24-27) - from ir_Vestel.h line 36
    @property
    def TurboSleep(self) -> int:
        return GETBITS64(self.cmdState, 24, 4)

    @TurboSleep.setter
    def TurboSleep(self, value: int) -> None:
        self.cmdState = (self.cmdState & ~(0xF << 24)) | ((value & 0xF) << 24)

    # Temp (bits 36-39) - from ir_Vestel.h line 38
    @property
    def Temp(self) -> int:
        return GETBITS64(self.cmdState, 36, 4)

    @Temp.setter
    def Temp(self, value: int) -> None:
        self.cmdState = (self.cmdState & ~(0xF << 36)) | ((value & 0xF) << 36)

    # Fan (bits 40-43) - from ir_Vestel.h line 39
    @property
    def Fan(self) -> int:
        return GETBITS64(self.cmdState, 40, 4)

    @Fan.setter
    def Fan(self, value: int) -> None:
        self.cmdState = (self.cmdState & ~(0xF << 40)) | ((value & 0xF) << 40)

    # Mode (bits 44-46) - from ir_Vestel.h line 40
    @property
    def Mode(self) -> int:
        return GETBITS64(self.cmdState, 44, 3)

    @Mode.setter
    def Mode(self, value: int) -> None:
        self.cmdState = (self.cmdState & ~(0x7 << 44)) | ((value & 0x7) << 44)

    # Ion (bit 50) - from ir_Vestel.h line 42
    @property
    def Ion(self) -> int:
        return GETBITS64(self.cmdState, 50, 1)

    @Ion.setter
    def Ion(self, value: bool) -> None:
        if value:
            self.cmdState |= 1 << 50
        else:
            self.cmdState &= ~(1 << 50)

    # Power (bits 52-53) - from ir_Vestel.h line 44
    @property
    def Power(self) -> int:
        return GETBITS64(self.cmdState, 52, 2)

    @Power.setter
    def Power(self, value: int) -> None:
        self.cmdState = (self.cmdState & ~(0x3 << 52)) | ((value & 0x3) << 52)

    # UseCmd (bit 54) - from ir_Vestel.h line 45
    @property
    def UseCmd(self) -> int:
        return GETBITS64(self.cmdState, 54, 1)

    @UseCmd.setter
    def UseCmd(self, value: bool) -> None:
        if value:
            self.cmdState |= 1 << 54
        else:
            self.cmdState &= ~(1 << 54)

    # Time state properties
    # TimeSum (bits 12-19) - from ir_Vestel.h line 49
    @property
    def TimeSum(self) -> int:
        return GETBITS64(self.timeState, 12, 8)

    @TimeSum.setter
    def TimeSum(self, value: int) -> None:
        self.timeState = (self.timeState & ~(0xFF << 12)) | ((value & 0xFF) << 12)

    # OffTenMins (bits 20-22) - from ir_Vestel.h line 50
    @property
    def OffTenMins(self) -> int:
        return GETBITS64(self.timeState, 20, 3)

    @OffTenMins.setter
    def OffTenMins(self, value: int) -> None:
        self.timeState = (self.timeState & ~(0x7 << 20)) | ((value & 0x7) << 20)

    # OffHours (bits 23-27) - from ir_Vestel.h line 51
    @property
    def OffHours(self) -> int:
        return GETBITS64(self.timeState, 23, 5)

    @OffHours.setter
    def OffHours(self, value: int) -> None:
        self.timeState = (self.timeState & ~(0x1F << 23)) | ((value & 0x1F) << 23)

    # OnTenMins (bits 28-30) - from ir_Vestel.h line 52
    @property
    def OnTenMins(self) -> int:
        return GETBITS64(self.timeState, 28, 3)

    @OnTenMins.setter
    def OnTenMins(self, value: int) -> None:
        self.timeState = (self.timeState & ~(0x7 << 28)) | ((value & 0x7) << 28)

    # OnHours (bits 31-35) - from ir_Vestel.h line 53
    @property
    def OnHours(self) -> int:
        return GETBITS64(self.timeState, 31, 5)

    @OnHours.setter
    def OnHours(self, value: int) -> None:
        self.timeState = (self.timeState & ~(0x1F << 31)) | ((value & 0x1F) << 31)

    # Hours (bits 36-40) - from ir_Vestel.h line 54
    @property
    def Hours(self) -> int:
        return GETBITS64(self.timeState, 36, 5)

    @Hours.setter
    def Hours(self, value: int) -> None:
        self.timeState = (self.timeState & ~(0x1F << 36)) | ((value & 0x1F) << 36)

    # OnTimer (bit 41) - from ir_Vestel.h line 55
    @property
    def OnTimer(self) -> int:
        return GETBITS64(self.timeState, 41, 1)

    @OnTimer.setter
    def OnTimer(self, value: bool) -> None:
        if value:
            self.timeState |= 1 << 41
        else:
            self.timeState &= ~(1 << 41)

    # OffTimer (bit 42) - from ir_Vestel.h line 56
    @property
    def OffTimer(self) -> int:
        return GETBITS64(self.timeState, 42, 1)

    @OffTimer.setter
    def OffTimer(self, value: bool) -> None:
        if value:
            self.timeState |= 1 << 42
        else:
            self.timeState &= ~(1 << 42)

    # Timer (bit 43) - from ir_Vestel.h line 57
    @property
    def Timer(self) -> int:
        return GETBITS64(self.timeState, 43, 1)

    @Timer.setter
    def Timer(self, value: bool) -> None:
        if value:
            self.timeState |= 1 << 43
        else:
            self.timeState &= ~(1 << 43)

    # Minutes (bits 44-51) - from ir_Vestel.h line 58
    @property
    def Minutes(self) -> int:
        return GETBITS64(self.timeState, 44, 8)

    @Minutes.setter
    def Minutes(self, value: int) -> None:
        self.timeState = (self.timeState & ~(0xFF << 44)) | ((value & 0xFF) << 44)


## Send a Vestel message
## Status: STABLE / Working.
## @param[in] data The message to be sent.
## @param[in] nbits The number of bits of message to be sent.
## @param[in] repeat The number of times the command is to be repeated.
## Direct translation from IRremoteESP8266 IRsend::sendVestelAc (ir_Vestel.cpp lines 30-46)
def sendVestelAc(data: int, nbits: int = kVestelAcBits, repeat: int = 0) -> List[int]:
    """
    Send a Vestel formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendVestelAc

    Returns timing array instead of transmitting via hardware.
    """
    if nbits % 8 != 0:
        return []  # nbits is required to be a multiple of 8

    from app.core.ir_protocols.ir_send import sendGeneric

    # Convert uint64 to byte array for sendGeneric
    dataptr = []
    for i in range(nbits // 8):
        dataptr.append((data >> (i * 8)) & 0xFF)

    return sendGeneric(
        headermark=kVestelAcHdrMark,
        headerspace=kVestelAcHdrSpace,
        onemark=kVestelAcBitMark,
        onespace=kVestelAcOneSpace,
        zeromark=kVestelAcBitMark,
        zerospace=kVestelAcZeroSpace,
        footermark=kVestelAcBitMark,
        gap=100000  # Footer + repeat gap,
        dataptr=dataptr,
        nbytes=nbits // 8,
        MSBfirst=False,
    )


## Class for handling detailed Vestel A/C messages.
## Direct translation from C++ IRVestelAc class (ir_Vestel.h lines 100-170)
class IRVestelAc:
    ## Class Constructor
    def __init__(self) -> None:
        self._: VestelProtocol = VestelProtocol()
        self.stateReset()

    ## Reset the state of the remote to a known good state/sequence.
    ## @note Power On, Mode Auto, Fan Auto, Temp = 25C/77F
    ## Direct translation from ir_Vestel.cpp lines 56-61
    def stateReset(self) -> None:
        self._.cmdState = kVestelAcStateDefault
        self._.timeState = kVestelAcTimeStateDefault

    ## Calculate the checksum for a given state.
    ## @param[in] state The state to calc the checksum of.
    ## @return The calculated checksum value.
    ## Direct translation from ir_Vestel.cpp lines 360-366
    @staticmethod
    def calcChecksum(state: int) -> int:
        # Just counts the set bits +1 on stream and take inverse after mask
        return 0xFF - countBits(GETBITS64(state, 20, 44), 44, True, 2)

    ## Calculate & set the checksum for the current internal state of the remote.
    ## Direct translation from ir_Vestel.cpp lines 377-382
    def checksum(self) -> None:
        # Stored the checksum value in the last byte.
        self._.CmdSum = self.calcChecksum(self._.cmdState)
        self._.TimeSum = self.calcChecksum(self._.timeState)

    ## Verify the checksum is valid for a given state.
    ## @param[in] state The state to verify the checksum of.
    ## @return true, if the state has a valid checksum. Otherwise, false.
    ## Direct translation from ir_Vestel.cpp lines 368-375
    @staticmethod
    def validChecksum(state: int) -> bool:
        vp = VestelProtocol()
        vp.cmdState = state
        return vp.CmdSum == IRVestelAc.calcChecksum(state)

    ## Get a copy of the internal state/code for this protocol.
    ## @return A code for this protocol based on the current internal state.
    ## Direct translation from ir_Vestel.cpp lines 74-80
    def getRaw(self) -> int:
        self.checksum()
        if not self._.UseCmd:
            return self._.timeState
        return self._.cmdState

    ## Set the internal state from a valid code for this protocol.
    ## @param[in] newState A valid code for this protocol.
    ## Direct translation from ir_Vestel.cpp lines 82-102
    def setRaw(self, newState: int) -> None:
        self._.cmdState = newState
        self._.timeState = newState
        if self.isTimeCommand():
            self._.cmdState = kVestelAcStateDefault
            self._.UseCmd = False
        else:
            self._.timeState = kVestelAcTimeStateDefault

    ## Is the current state a time command?
    ## @return true, if the state is a time message. Otherwise, false.
    ## Direct translation from ir_Vestel.cpp lines 384-388
    def isTimeCommand(self) -> bool:
        return not bool(self._.UseCmd)

    ## Set the requested power state of the A/C to on.
    ## Direct translation from ir_Vestel.cpp line 105
    def on(self) -> None:
        self.setPower(True)

    ## Set the requested power state of the A/C to off.
    ## Direct translation from ir_Vestel.cpp line 108
    def off(self) -> None:
        self.setPower(False)

    ## Change the power setting.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Vestel.cpp lines 110-115
    def setPower(self, on: bool) -> None:
        self._.Power = 0b11 if on else 0b00
        self._.UseCmd = True

    ## Get the value of the current power setting.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Vestel.cpp lines 117-121
    def getPower(self) -> bool:
        return bool(self._.Power)

    ## Set the temperature.
    ## @param[in] temp The temperature in degrees celsius.
    ## Direct translation from ir_Vestel.cpp lines 123-130
    def setTemp(self, temp: int) -> None:
        new_temp = max(kVestelAcMinTempC, temp)
        new_temp = min(kVestelAcMaxTemp, new_temp)
        self._.Temp = new_temp - kVestelAcMinTempH
        self._.UseCmd = True

    ## Get the current temperature setting.
    ## @return The current setting for temp. in degrees celsius.
    ## Direct translation from ir_Vestel.cpp lines 132-136
    def getTemp(self) -> int:
        return self._.Temp + kVestelAcMinTempH

    ## Set the speed of the fan.
    ## @param[in] fan The desired setting.
    ## Direct translation from ir_Vestel.cpp lines 138-154
    def setFan(self, fan: int) -> None:
        if fan in [
            kVestelAcFanLow,
            kVestelAcFanMed,
            kVestelAcFanHigh,
            kVestelAcFanAutoCool,
            kVestelAcFanAutoHot,
            kVestelAcFanAuto,
        ]:
            self._.Fan = fan
        else:
            self._.Fan = kVestelAcFanAuto
        self._.UseCmd = True

    ## Get the current fan speed setting.
    ## @return The current fan speed/mode.
    ## Direct translation from ir_Vestel.cpp lines 156-160
    def getFan(self) -> int:
        return self._.Fan

    ## Get the operating mode setting of the A/C.
    ## @return The current operating mode setting.
    ## Direct translation from ir_Vestel.cpp lines 162-166
    def getMode(self) -> int:
        return self._.Mode

    ## Set the operating mode of the A/C.
    ## @param[in] mode The desired operating mode.
    ## @note If we get an unexpected mode, default to AUTO.
    ## Direct translation from ir_Vestel.cpp lines 168-184
    def setMode(self, mode: int) -> None:
        if mode in [kVestelAcAuto, kVestelAcCool, kVestelAcHeat, kVestelAcDry, kVestelAcFan]:
            self._.Mode = mode
        else:
            self._.Mode = kVestelAcAuto
        self._.UseCmd = True

    ## Set Auto mode/level of the A/C.
    ## @param[in] autoLevel The auto mode/level setting.
    ## Direct translation from ir_Vestel.cpp lines 186-202
    def setAuto(self, autoLevel: int) -> None:
        if autoLevel < -2 or autoLevel > 2:
            return
        self._.Mode = kVestelAcAuto
        self._.Fan = kVestelAcFanAutoCool if autoLevel < 0 else kVestelAcFanAutoHot
        if autoLevel == 2:
            self.setTemp(30)
        elif autoLevel == 1:
            self.setTemp(31)
        elif autoLevel == 0:
            self.setTemp(25)
        elif autoLevel == -1:
            self.setTemp(16)
        elif autoLevel == -2:
            self.setTemp(17)

    ## Set the timer to be active on the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Vestel.cpp lines 204-209
    def setTimerActive(self, on: bool) -> None:
        self._.Timer = on
        self._.UseCmd = False

    ## Get if the Timer is active on the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Vestel.cpp lines 211-215
    def isTimerActive(self) -> bool:
        return bool(self._.Timer)

    ## Set Timer option of A/C.
    ## @param[in] minutes Nr of minutes the timer is to be set for.
    ## @note Valid arguments are 0, 0.5, 1, 2, 3 and 5 hours (in minutes).
    ##   0 disables the timer.
    ## Direct translation from ir_Vestel.cpp lines 217-232
    def setTimer(self, minutes: int) -> None:
        # Clear both On & Off timers.
        self._.OnHours = 0
        self._.OnTenMins = 0
        # Set the "Off" time with the nr of minutes before we turn off.
        self._.OffHours = minutes // 60
        self._.OffTenMins = (minutes % 60) // 10
        self.setOffTimerActive(False)
        # Yes. On Timer instead of Off timer active.
        self.setOnTimerActive(minutes != 0)
        self.setTimerActive(minutes != 0)

    ## Get the Timer time of A/C.
    ## @return The number of minutes of time on the timer.
    ## Direct translation from ir_Vestel.cpp line 236
    def getTimer(self) -> int:
        return self.getOffTimer()

    ## Set the A/C's internal clock.
    ## @param[in] minutes The time expressed in nr. of minutes past midnight.
    ## Direct translation from ir_Vestel.cpp lines 238-244
    def setTime(self, minutes: int) -> None:
        self._.Hours = minutes // 60
        self._.Minutes = minutes % 60
        self._.UseCmd = False

    ## Get the A/C's internal clock's time.
    ## @return The time expressed in nr. of minutes past midnight.
    ## Direct translation from ir_Vestel.cpp lines 246-250
    def getTime(self) -> int:
        return self._.Hours * 60 + self._.Minutes

    ## Set the On timer to be active on the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Vestel.cpp lines 252-257
    def setOnTimerActive(self, on: bool) -> None:
        self._.OnTimer = on
        self._.UseCmd = False

    ## Get if the On Timer is active on the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Vestel.cpp lines 259-263
    def isOnTimerActive(self) -> bool:
        return bool(self._.OnTimer)

    ## Set the On timer time on the A/C.
    ## @param[in] minutes Time in nr. of minutes.
    ## Direct translation from ir_Vestel.cpp lines 265-272
    def setOnTimer(self, minutes: int) -> None:
        self.setOnTimerActive(bool(minutes))
        self._.OnHours = minutes // 60
        self._.OnTenMins = (minutes % 60) // 10
        self.setTimerActive(False)

    ## Get the A/C's On Timer time.
    ## @return The time expressed in nr. of minutes.
    ## Direct translation from ir_Vestel.cpp lines 274-278
    def getOnTimer(self) -> int:
        return self._.OnHours * 60 + self._.OnTenMins * 10

    ## Set the Off timer to be active on the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Vestel.cpp lines 280-285
    def setOffTimerActive(self, on: bool) -> None:
        self._.OffTimer = on
        self._.UseCmd = False

    ## Get if the Off Timer is active on the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Vestel.cpp lines 287-291
    def isOffTimerActive(self) -> bool:
        return bool(self._.OffTimer)

    ## Set the Off timer time on the A/C.
    ## @param[in] minutes Time in nr. of minutes.
    ## Direct translation from ir_Vestel.cpp lines 293-300
    def setOffTimer(self, minutes: int) -> None:
        self.setOffTimerActive(bool(minutes))
        self._.OffHours = minutes // 60
        self._.OffTenMins = (minutes % 60) // 10
        self.setTimerActive(False)

    ## Get the A/C's Off Timer time.
    ## @return The time expressed in nr. of minutes.
    ## Direct translation from ir_Vestel.cpp lines 302-306
    def getOffTimer(self) -> int:
        return self._.OffHours * 60 + self._.OffTenMins * 10

    ## Set the Sleep setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Vestel.cpp lines 308-313
    def setSleep(self, on: bool) -> None:
        self._.TurboSleep = kVestelAcSleep if on else kVestelAcNormal
        self._.UseCmd = True

    ## Get the Sleep setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Vestel.cpp lines 315-319
    def getSleep(self) -> bool:
        return self._.TurboSleep == kVestelAcSleep

    ## Set the Turbo setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Vestel.cpp lines 321-326
    def setTurbo(self, on: bool) -> None:
        self._.TurboSleep = kVestelAcTurbo if on else kVestelAcNormal
        self._.UseCmd = True

    ## Get the Turbo setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Vestel.cpp lines 328-332
    def getTurbo(self) -> bool:
        return self._.TurboSleep == kVestelAcTurbo

    ## Set the Ion (Filter) setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Vestel.cpp lines 334-339
    def setIon(self, on: bool) -> None:
        self._.Ion = on
        self._.UseCmd = True

    ## Get the Ion (Filter) setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Vestel.cpp lines 341-345
    def getIon(self) -> bool:
        return bool(self._.Ion)

    ## Set the Swing Roaming setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Vestel.cpp lines 347-352
    def setSwing(self, on: bool) -> None:
        self._.Swing = kVestelAcSwing if on else 0xF
        self._.UseCmd = True

    ## Get the Swing Roaming setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Vestel.cpp lines 354-358
    def getSwing(self) -> bool:
        return self._.Swing == kVestelAcSwing


## Decode the supplied Vestel message.
## Status: Alpha / Needs testing against a real device.
## @param[in,out] results Ptr to the data to decode & where to store the result
## @param[in] offset The starting index to use when attempting to decode the
##   raw data. Typically/Defaults to kStartOffset.
## @param[in] nbits The number of data bits to expect.
## @param[in] strict Flag indicating if we should perform strict matching.
## @return True if it can decode it, false if it can't.
## Direct translation from IRremoteESP8266 IRrecv::decodeVestelAc (ir_Vestel.cpp lines 528-572)
def decodeVestelAc(
    results, offset: int = 1, nbits: int = kVestelAcBits, strict: bool = True
) -> bool:
    """
    Decode a Vestel AC IR message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeVestelAc
    """
    # Import here to avoid circular imports
    from app.core.ir_protocols.ir_recv import kMarkExcess, _matchGeneric

    if nbits % 8 != 0:  # nbits has to be a multiple of nr. of bits in a byte.
        return False

    if strict:
        if nbits != kVestelAcBits:
            return False  # Not strictly a Vestel AC message.

    data = 0

    if nbits > 64:
        return False  # We can't possibly capture a Vestel packet that big.

    # Match Header + Data + Footer
    data_result = [data]
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=data_result,
        result_bytes_ptr=None,
        use_bits=True,
        remaining=results.rawlen - offset,
        nbits=nbits,
        hdrmark=kVestelAcHdrMark,
        hdrspace=kVestelAcHdrSpace,
        onemark=kVestelAcBitMark,
        onespace=kVestelAcOneSpace,
        zeromark=kVestelAcBitMark,
        zerospace=kVestelAcZeroSpace,
        footermark=kVestelAcBitMark,
        footerspace=0,
        atleast=False,
        tolerance=kVestelAcTolerance,
        excess=kMarkExcess,
        MSBfirst=False,
    )

    if not used:
        return False

    data = data_result[0]

    # Compliance
    if strict:
        if not IRVestelAc.validChecksum(data):
            return False

    # Success
    # results.decode_type = VESTEL_AC  # Would set protocol type in C++
    results.bits = nbits
    results.value = data
    results.address = 0
    results.command = 0

    return True
