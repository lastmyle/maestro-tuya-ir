# Copyright 2019, 2021 David Conran
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Support for TCL protocols (TCL112AC and TCL96AC).
## Direct translation from IRremoteESP8266 ir_Tcl.cpp and ir_Tcl.h

# Supports:
#   Brand: Leberg,  Model: LBS-TOR07 A/C (TAC09CHSD)
#   Brand: TCL,  Model: TAC-09CHSD/XA31I A/C (TAC09CHSD)
#   Brand: Teknopoint,  Model: Allegro SSA-09H A/C (GZ055BE1)
#   Brand: Teknopoint,  Model: GZ-055B-E1 remote (GZ055BE1)
#   Brand: Daewoo,  Model: DSB-F0934ELH-V A/C
#   Brand: Daewoo,  Model: GYKQ-52E remote
#   Brand: TCL,  Model: GYKQ-58(XM) remote (TCL96AC)
#   Brand: Electrolux,  Model: EACM CL/N3 series remote

from typing import List, Optional

# Constants for TCL112AC (from ir_Tcl.h lines 86-123)
kTcl112AcHdrMark = 3000
kTcl112AcHdrSpace = 1650
kTcl112AcBitMark = 500
kTcl112AcOneSpace = 1050
kTcl112AcZeroSpace = 325
kTcl112AcGap = 100000  # kDefaultMessageGap - Just a guess
kTcl112AcHdrMarkTolerance = 6  # Total tolerance percentage to use for matching the header mark
kTcl112AcTolerance = 5  # Extra Percentage for the rest

# State length constants (from IRremoteESP8266.h line 1402-1403)
kTcl112AcStateLength = 14
kTcl112AcBits = kTcl112AcStateLength * 8  # 112 bits

# Timer constants (from ir_Tcl.cpp lines 17-18)
kTcl112AcTimerResolution = 20  # Minutes
kTcl112AcTimerMax = 720  # Minutes (12 hrs)

# Mode constants (from ir_Tcl.h lines 96-100)
kTcl112AcHeat = 1
kTcl112AcDry = 2
kTcl112AcCool = 3
kTcl112AcFan = 7
kTcl112AcAuto = 8

# Fan speed constants (from ir_Tcl.h lines 102-108)
kTcl112AcFanAuto = 0b000
kTcl112AcFanMin = 0b001  # Aka. "Night"
kTcl112AcFanLow = 0b010
kTcl112AcFanMed = 0b011
kTcl112AcFanHigh = 0b101
kTcl112AcFanNight = kTcl112AcFanMin
kTcl112AcFanQuiet = kTcl112AcFanMin

# Temperature constants (from ir_Tcl.h lines 110-111)
kTcl112AcTempMax = 31.0
kTcl112AcTempMin = 16.0

# Swing constants (from ir_Tcl.h lines 113-119)
kTcl112AcSwingVOff = 0b000
kTcl112AcSwingVHighest = 0b001
kTcl112AcSwingVHigh = 0b010
kTcl112AcSwingVMiddle = 0b011
kTcl112AcSwingVLow = 0b100
kTcl112AcSwingVLowest = 0b101
kTcl112AcSwingVOn = 0b111

# MsgType constants (from ir_Tcl.h lines 121-122)
kTcl112AcNormal = 0b01
kTcl112AcSpecial = 0b10

# Constants for TCL96AC (from ir_Tcl.cpp lines 20-28)
kTcl96AcHdrMark = 1056  # uSeconds
kTcl96AcHdrSpace = 550  # uSeconds
kTcl96AcBitMark = 600  # uSeconds
kTcl96AcGap = 100000  # kDefaultMessageGap - Just a guess
kTcl96AcSpaceCount = 4
kTcl96AcBitSpaces = [360, 838, 2182, 1444]  # 0b00, 0b01, 0b10, 0b11

# State length constants (from IRremoteESP8266.h lines 1399-1400)
kTcl96AcStateLength = 12
kTcl96AcBits = kTcl96AcStateLength * 8  # 96 bits


## Helper function for summing bytes (used for checksum calculation)
## Direct translation from IRutils.cpp sumBytes
def sumBytes(start: List[int], length: int, init: int = 0) -> int:
    """Sum all bytes in the array (used for checksum). EXACT translation from IRremoteESP8266."""
    return (init + sum(start[:length])) & 0xFF


## Helper function to extract bits from uint8
## Direct translation from IRremoteESP8266 GETBITS8 macro
def GETBITS8(data: int, offset: int, size: int) -> int:
    """Extract bits from uint8. EXACT translation from IRremoteESP8266."""
    mask = (1 << size) - 1
    return (data >> offset) & mask


## Native representation of a TCL 112 A/C message.
## Direct translation of the C++ union/struct (ir_Tcl.h lines 30-83)
class Tcl112Protocol:
    def __init__(self):
        # The state array (14 bytes for TCL112AC)
        self.raw = [0] * 14

    # Byte 3 (from ir_Tcl.h lines 38-39)
    @property
    def MsgType(self) -> int:
        return self.raw[3] & 0x03

    @MsgType.setter
    def MsgType(self, value: int) -> None:
        self.raw[3] = (self.raw[3] & 0xFC) | (value & 0x03)

    # Byte 5 (from ir_Tcl.h lines 42-49)
    @property
    def Power(self) -> int:
        return (self.raw[5] >> 2) & 0x01

    @Power.setter
    def Power(self, value: bool) -> None:
        if value:
            self.raw[5] |= 0x04
        else:
            self.raw[5] &= 0xFB

    @property
    def OffTimerEnabled(self) -> int:
        return (self.raw[5] >> 3) & 0x01

    @OffTimerEnabled.setter
    def OffTimerEnabled(self, value: bool) -> None:
        if value:
            self.raw[5] |= 0x08
        else:
            self.raw[5] &= 0xF7

    @property
    def OnTimerEnabled(self) -> int:
        return (self.raw[5] >> 4) & 0x01

    @OnTimerEnabled.setter
    def OnTimerEnabled(self, value: bool) -> None:
        if value:
            self.raw[5] |= 0x10
        else:
            self.raw[5] &= 0xEF

    @property
    def Quiet(self) -> int:
        return (self.raw[5] >> 5) & 0x01

    @Quiet.setter
    def Quiet(self, value: bool) -> None:
        if value:
            self.raw[5] |= 0x20
        else:
            self.raw[5] &= 0xDF

    @property
    def Light(self) -> int:
        return (self.raw[5] >> 6) & 0x01

    @Light.setter
    def Light(self, value: bool) -> None:
        if value:
            self.raw[5] |= 0x40
        else:
            self.raw[5] &= 0xBF

    @property
    def Econo(self) -> int:
        return (self.raw[5] >> 7) & 0x01

    @Econo.setter
    def Econo(self, value: bool) -> None:
        if value:
            self.raw[5] |= 0x80
        else:
            self.raw[5] &= 0x7F

    # Byte 6 (from ir_Tcl.h lines 51-54)
    @property
    def Mode(self) -> int:
        return self.raw[6] & 0x0F

    @Mode.setter
    def Mode(self, value: int) -> None:
        self.raw[6] = (self.raw[6] & 0xF0) | (value & 0x0F)

    @property
    def Health(self) -> int:
        return (self.raw[6] >> 4) & 0x01

    @Health.setter
    def Health(self, value: bool) -> None:
        if value:
            self.raw[6] |= 0x10
        else:
            self.raw[6] &= 0xEF

    @property
    def Turbo(self) -> int:
        return (self.raw[6] >> 5) & 0x01

    @Turbo.setter
    def Turbo(self, value: bool) -> None:
        if value:
            self.raw[6] |= 0x20
        else:
            self.raw[6] &= 0xDF

    # Byte 7 (from ir_Tcl.h lines 56-57)
    @property
    def Temp(self) -> int:
        return self.raw[7] & 0x0F

    @Temp.setter
    def Temp(self, value: int) -> None:
        self.raw[7] = (self.raw[7] & 0xF0) | (value & 0x0F)

    # Byte 8 (from ir_Tcl.h lines 59-62)
    @property
    def Fan(self) -> int:
        return self.raw[8] & 0x07

    @Fan.setter
    def Fan(self, value: int) -> None:
        self.raw[8] = (self.raw[8] & 0xF8) | (value & 0x07)

    @property
    def SwingV(self) -> int:
        return (self.raw[8] >> 3) & 0x07

    @SwingV.setter
    def SwingV(self, value: int) -> None:
        self.raw[8] = (self.raw[8] & 0xC7) | ((value & 0x07) << 3)

    @property
    def TimerIndicator(self) -> int:
        return (self.raw[8] >> 6) & 0x01

    @TimerIndicator.setter
    def TimerIndicator(self, value: bool) -> None:
        if value:
            self.raw[8] |= 0x40
        else:
            self.raw[8] &= 0xBF

    # Byte 9 (from ir_Tcl.h lines 64-66)
    @property
    def OffTimer(self) -> int:
        return (self.raw[9] >> 1) & 0x3F

    @OffTimer.setter
    def OffTimer(self, value: int) -> None:
        self.raw[9] = (self.raw[9] & 0x81) | ((value & 0x3F) << 1)

    # Byte 10 (from ir_Tcl.h lines 68-70)
    @property
    def OnTimer(self) -> int:
        return (self.raw[10] >> 1) & 0x3F

    @OnTimer.setter
    def OnTimer(self, value: int) -> None:
        self.raw[10] = (self.raw[10] & 0x81) | ((value & 0x3F) << 1)

    # Byte 12 (from ir_Tcl.h lines 74-79)
    @property
    def SwingH(self) -> int:
        return (self.raw[12] >> 3) & 0x01

    @SwingH.setter
    def SwingH(self, value: bool) -> None:
        if value:
            self.raw[12] |= 0x08
        else:
            self.raw[12] &= 0xF7

    @property
    def HalfDegree(self) -> int:
        return (self.raw[12] >> 5) & 0x01

    @HalfDegree.setter
    def HalfDegree(self, value: bool) -> None:
        if value:
            self.raw[12] |= 0x20
        else:
            self.raw[12] &= 0xDF

    @property
    def isTcl(self) -> int:
        return (self.raw[12] >> 7) & 0x01

    @isTcl.setter
    def isTcl(self, value: bool) -> None:
        if value:
            self.raw[12] |= 0x80
        else:
            self.raw[12] &= 0x7F

    # Byte 13 (from ir_Tcl.h line 81)
    @property
    def Sum(self) -> int:
        return self.raw[13] & 0xFF

    @Sum.setter
    def Sum(self, value: int) -> None:
        self.raw[13] = value & 0xFF


## Send a TCL 112-bit A/C message.
## Status: Beta / Probably working.
## @param[in] data The message to be sent.
## @param[in] nbytes The number of bytes of message to be sent.
## @param[in] repeat The number of times the command is to be repeated.
## Direct translation from IRremoteESP8266 IRsend::sendTcl112Ac (ir_Tcl.cpp lines 40-53)
def sendTcl112Ac(data: List[int], nbytes: int, repeat: int = 0) -> List[int]:
    """
    Send a TCL 112-bit A/C message.
    EXACT translation from IRremoteESP8266 IRsend::sendTcl112Ac

    Returns timing array instead of transmitting via hardware.
    """
    from app.core.ir_protocols.ir_send import sendGeneric

    return sendGeneric(
        headermark=kTcl112AcHdrMark,
        headerspace=kTcl112AcHdrSpace,
        onemark=kTcl112AcBitMark,
        onespace=kTcl112AcOneSpace,
        zeromark=kTcl112AcBitMark,
        zerospace=kTcl112AcZeroSpace,
        footermark=kTcl112AcBitMark,
        dataptr=data,
        nbytes=nbytes,
        MSBfirst=False,
    )


## Class for handling detailed TCL 112 A/C messages.
## Direct translation from C++ IRTcl112Ac class (ir_Tcl.h lines 126-200)
class IRTcl112Ac:
    ## Class Constructor
    def __init__(self) -> None:
        self._: Tcl112Protocol = Tcl112Protocol()
        self._quiet_prev: bool = False
        self._quiet: bool = False
        self._quiet_explictly_set: bool = False
        self.stateReset()

    ## Reset the internal state of the emulation. (On, Cool, 24C)
    ## Direct translation from ir_Tcl.cpp lines 141-150
    def stateReset(self) -> None:
        # A known good state. (On, Cool, 24C)
        reset = [0x23, 0xCB, 0x26, 0x01, 0x00, 0x24, 0x03, 0x07, 0x40, 0x00, 0x00, 0x00, 0x00, 0x03]
        for i in range(len(reset)):
            self._.raw[i] = reset[i]
        self._quiet = False
        self._quiet_prev = False
        self._quiet_explictly_set = False

    ## Calculate the checksum for a given state.
    ## @param[in] state The array to calc the checksum of.
    ## @param[in] length The length/size of the array.
    ## @return The calculated checksum value.
    ## Direct translation from ir_Tcl.cpp lines 97-111
    @staticmethod
    def calcChecksum(state: List[int], length: int = kTcl112AcStateLength) -> int:
        if length:
            if length > 4 and state[3] == 0x02:  # Special message?
                return sumBytes(state, length - 1, 0xF)  # Checksum needs an offset
            else:
                return sumBytes(state, length - 1)
        else:
            return 0

    ## Calculate & set the checksum for the current internal state of the remote.
    ## @param[in] length The length/size of the internal array to checksum.
    ## Direct translation from ir_Tcl.cpp lines 114-119
    def checksum(self, length: int = kTcl112AcStateLength) -> None:
        # Stored the checksum value in the last byte.
        if length > 1:
            self._.Sum = self.calcChecksum(self._.raw, length)

    ## Verify the checksum is valid for a given state.
    ## @param[in] state The array to verify the checksum of.
    ## @param[in] length The length/size of the array.
    ## @return true, if the state has a valid checksum. Otherwise, false.
    ## Direct translation from ir_Tcl.cpp lines 121-127
    @staticmethod
    def validChecksum(state: List[int], length: int = kTcl112AcStateLength) -> bool:
        return length > 1 and state[length - 1] == IRTcl112Ac.calcChecksum(state, length)

    ## Check the supplied state looks like a TCL112AC message.
    ## @param[in] state The array to verify the checksum of.
    ## @note Assumes the state is the correct size.
    ## @return true, if the state looks like a TCL112AC message. Otherwise, false.
    ## @warning This is just a guess.
    ## Direct translation from ir_Tcl.cpp lines 129-138
    @staticmethod
    def isTcl(state: List[int]) -> bool:
        mesg = Tcl112Protocol()
        for i in range(min(len(state), len(mesg.raw))):
            mesg.raw[i] = state[i]
        return (mesg.MsgType != kTcl112AcNormal) or bool(mesg.isTcl)

    ## Get/Detect the model of the A/C.
    ## @return The enum of the compatible model.
    ## Direct translation from ir_Tcl.cpp lines 152-157
    def getModel(self) -> int:
        # tcl_ac_remote_model_t::TAC09CHSD = 0
        # tcl_ac_remote_model_t::GZ055BE1 = 1
        return 0 if self.isTcl(self._.raw) else 1

    ## Set the model of the A/C to emulate.
    ## @param[in] model The enum of the appropriate model.
    ## Direct translation from ir_Tcl.cpp lines 159-163
    def setModel(self, model: int) -> None:
        # tcl_ac_remote_model_t::GZ055BE1 = 1
        self._.isTcl = model != 1

    ## Get a PTR to the internal state/code for this protocol.
    ## @return PTR to a code for this protocol based on the current internal state.
    ## Direct translation from ir_Tcl.cpp lines 165-170
    def getRaw(self) -> List[int]:
        self.checksum()
        return self._.raw

    ## Set the internal state from a valid code for this protocol.
    ## @param[in] new_code A valid code for this protocol.
    ## @param[in] length The length/size of the new_code array.
    ## Direct translation from ir_Tcl.cpp lines 172-177
    def setRaw(self, new_code: List[int], length: int = kTcl112AcStateLength) -> None:
        for i in range(min(length, kTcl112AcStateLength)):
            self._.raw[i] = new_code[i]

    ## Set the requested power state of the A/C to on.
    ## Direct translation from ir_Tcl.cpp line 180
    def on(self) -> None:
        self.setPower(True)

    ## Set the requested power state of the A/C to off.
    ## Direct translation from ir_Tcl.cpp line 183
    def off(self) -> None:
        self.setPower(False)

    ## Change the power setting.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Tcl.cpp line 187
    def setPower(self, on: bool) -> None:
        self._.Power = on

    ## Get the value of the current power setting.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Tcl.cpp line 191
    def getPower(self) -> bool:
        return bool(self._.Power)

    ## Get the operating mode setting of the A/C.
    ## @return The current operating mode setting.
    ## Direct translation from ir_Tcl.cpp line 195
    def getMode(self) -> int:
        return self._.Mode

    ## Set the operating mode of the A/C.
    ## @param[in] mode The desired operating mode.
    ## @note Fan/Ventilation mode sets the fan speed to high.
    ##   Unknown values default to Auto.
    ## Direct translation from ir_Tcl.cpp lines 197-216
    def setMode(self, mode: int) -> None:
        # If we get an unexpected mode, default to AUTO.
        if mode == kTcl112AcFan:
            self.setFan(kTcl112AcFanHigh)
            # FALLTHRU
        if mode in [kTcl112AcFan, kTcl112AcAuto, kTcl112AcCool, kTcl112AcHeat, kTcl112AcDry]:
            self._.Mode = mode
        else:
            self._.Mode = kTcl112AcAuto

    ## Set the temperature.
    ## @param[in] celsius The temperature in degrees celsius.
    ## @note The temperature resolution is 0.5 of a degree.
    ## Direct translation from ir_Tcl.cpp lines 218-230
    def setTemp(self, celsius: float) -> None:
        # Make sure we have desired temp in the correct range.
        safecelsius = max(celsius, kTcl112AcTempMin)
        safecelsius = min(safecelsius, kTcl112AcTempMax)
        # Convert to integer nr. of half degrees.
        nrHalfDegrees = int(safecelsius * 2)
        # Do we have a half degree celsius?
        self._.HalfDegree = bool(nrHalfDegrees & 1)
        self._.Temp = int(kTcl112AcTempMax - nrHalfDegrees / 2)

    ## Get the current temperature setting.
    ## @return The current setting for temp. in degrees celsius.
    ## @note The temperature resolution is 0.5 of a degree.
    ## Direct translation from ir_Tcl.cpp lines 232-239
    def getTemp(self) -> float:
        result = kTcl112AcTempMax - self._.Temp
        if self._.HalfDegree:
            result += 0.5
        return result

    ## Set the speed of the fan.
    ## @param[in] speed The desired setting.
    ## @note Unknown speeds will default to Auto.
    ## Direct translation from ir_Tcl.cpp lines 241-256
    def setFan(self, speed: int) -> None:
        if speed in [
            kTcl112AcFanAuto,
            kTcl112AcFanMin,
            kTcl112AcFanLow,
            kTcl112AcFanMed,
            kTcl112AcFanHigh,
        ]:
            self._.Fan = speed
        else:
            self._.Fan = kTcl112AcFanAuto

    ## Get the current fan speed setting.
    ## @return The current fan speed/mode.
    ## Direct translation from ir_Tcl.cpp line 260
    def getFan(self) -> int:
        return self._.Fan

    ## Set the economy setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Tcl.cpp line 264
    def setEcono(self, on: bool) -> None:
        self._.Econo = on

    ## Get the economy setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Tcl.cpp line 268
    def getEcono(self) -> bool:
        return bool(self._.Econo)

    ## Set the Health (Filter) setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Tcl.cpp line 272
    def setHealth(self, on: bool) -> None:
        self._.Health = on

    ## Get the Health (Filter) setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Tcl.cpp line 276
    def getHealth(self) -> bool:
        return bool(self._.Health)

    ## Set the Light (LED/Display) setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Tcl.cpp line 280
    def setLight(self, on: bool) -> None:
        self._.Light = not on  # Cleared when on

    ## Get the Light (LED/Display) setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Tcl.cpp line 284
    def getLight(self) -> bool:
        return not bool(self._.Light)

    ## Set the horizontal swing setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Tcl.cpp line 288
    def setSwingHorizontal(self, on: bool) -> None:
        self._.SwingH = on

    ## Get the horizontal swing setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Tcl.cpp line 292
    def getSwingHorizontal(self) -> bool:
        return bool(self._.SwingH)

    ## Set the vertical swing setting of the A/C.
    ## @param[in] setting The value of the desired setting.
    ## Direct translation from ir_Tcl.cpp lines 294-307
    def setSwingVertical(self, setting: int) -> None:
        if setting in [
            kTcl112AcSwingVOff,
            kTcl112AcSwingVHighest,
            kTcl112AcSwingVHigh,
            kTcl112AcSwingVMiddle,
            kTcl112AcSwingVLow,
            kTcl112AcSwingVLowest,
            kTcl112AcSwingVOn,
        ]:
            self._.SwingV = setting

    ## Get the vertical swing setting of the A/C.
    ## @return The current setting.
    ## Direct translation from ir_Tcl.cpp line 311
    def getSwingVertical(self) -> int:
        return self._.SwingV

    ## Set the Turbo setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Tcl.cpp lines 313-321
    def setTurbo(self, on: bool) -> None:
        self._.Turbo = on
        if on:
            self._.Fan = kTcl112AcFanHigh
            self._.SwingV = kTcl112AcSwingVOn

    ## Get the Turbo setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Tcl.cpp line 325
    def getTurbo(self) -> bool:
        return bool(self._.Turbo)

    ## Set the Quiet setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Tcl.cpp lines 327-333
    def setQuiet(self, on: bool) -> None:
        self._quiet_explictly_set = True
        self._quiet = on
        if self._.MsgType == kTcl112AcSpecial:
            self._.Quiet = on

    ## Get the Quiet setting of the A/C.
    ## @param[in] def_ The default value to use if we are not sure.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Tcl.cpp lines 335-343
    def getQuiet(self, def_: bool = False) -> bool:
        if self._.MsgType == kTcl112AcSpecial:
            return bool(self._.Quiet)
        else:
            return self._quiet if self._quiet_explictly_set else def_

    ## Get how long the On Timer is set for, in minutes.
    ## @return The time in nr of minutes.
    ## Direct translation from ir_Tcl.cpp lines 345-349
    def getOnTimer(self) -> int:
        return self._.OnTimer * kTcl112AcTimerResolution

    ## Set or cancel the On Timer function.
    ## @param[in] mins Nr. of minutes the timer is to be set to.
    ## @note Rounds down to 20 min increments. (max: 720 mins (12h), 0 is Off)
    ## Direct translation from ir_Tcl.cpp lines 351-358
    def setOnTimer(self, mins: int) -> None:
        self._.OnTimer = min(mins, kTcl112AcTimerMax) // kTcl112AcTimerResolution
        self._.OnTimerEnabled = self._.OnTimer > 0
        self._.TimerIndicator = bool(self._.OnTimerEnabled or self._.OffTimerEnabled)

    ## Get how long the Off Timer is set for, in minutes.
    ## @return The time in nr of minutes.
    ## Direct translation from ir_Tcl.cpp lines 360-364
    def getOffTimer(self) -> int:
        return self._.OffTimer * kTcl112AcTimerResolution

    ## Set or cancel the Off Timer function.
    ## @param[in] mins Nr. of minutes the timer is to be set to.
    ## @note Rounds down to 20 min increments. (max: 720 mins (12h), 0 is Off)
    ## Direct translation from ir_Tcl.cpp lines 366-373
    def setOffTimer(self, mins: int) -> None:
        self._.OffTimer = min(mins, kTcl112AcTimerMax) // kTcl112AcTimerResolution
        self._.OffTimerEnabled = self._.OffTimer > 0
        self._.TimerIndicator = bool(self._.OnTimerEnabled or self._.OffTimerEnabled)


## Decode the supplied Tcl112Ac message.
## @note There is no `decodeTcl112Ac()`.
##   It's the same as `decodeMitsubishi112()`. A shared routine is used.
##   You can find it in: ir_Mitsubishi.cpp
## Direct translation from ir_Tcl.cpp lines 533-538
def decodeTcl112Ac(
    results, offset: int = 1, nbits: int = kTcl112AcBits, strict: bool = True
) -> bool:
    """
    Decode a TCL 112-bit A/C IR message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeTcl112Ac

    Note: The actual decoder is the same as Mitsubishi112.
    """
    # Import here to avoid circular imports
    from app.core.ir_protocols.mitsubishi import decodeMitsubishi112

    # Use the shared Mitsubishi112 decoder
    return decodeMitsubishi112(results, offset, nbits, strict)


## Send a TCL 96-bit A/C message.
## Status: BETA / Untested on a real device working.
## @param[in] data The message to be sent.
## @param[in] nbytes The number of bytes of message to be sent.
## @param[in] repeat The number of times the command is to be repeated.
## Direct translation from IRremoteESP8266 IRsend::sendTcl96Ac (ir_Tcl.cpp lines 540-567)
def sendTcl96Ac(data: List[int], nbytes: int, repeat: int = 0) -> List[int]:
    """
    Send a TCL 96-bit A/C message.
    EXACT translation from IRremoteESP8266 IRsend::sendTcl96Ac

    Returns timing array instead of transmitting via hardware.
    """
    all_timings = []

    for r in range(repeat + 1):
        # Header
        all_timings.append(kTcl96AcHdrMark)
        all_timings.append(kTcl96AcHdrSpace)

        # Data
        for pos in range(nbytes):
            databyte = data[pos]
            for bits in range(0, 8, 2):
                all_timings.append(kTcl96AcBitMark)
                # Extract 2 bits at a time from MSB
                two_bits = GETBITS8(databyte, 8 - 2, 2)
                all_timings.append(kTcl96AcBitSpaces[two_bits])
                databyte <<= 2

        # Footer
        all_timings.append(kTcl96AcBitMark)
        all_timings.append(kTcl96AcGap)

    return all_timings


## Decode the supplied Tcl96Ac message.
## Status: ALPHA / Experimental.
## @param[in,out] results Ptr to the data to decode & where to store the result
## @param[in] offset The starting index to use when attempting to decode the
##   raw data. Typically/Defaults to kStartOffset.
## @param[in] nbits The number of data bits to expect.
## @param[in] strict Flag indicating if we should perform strict matching.
## @return True if it can decode it, false if it can't.
## Direct translation from IRremoteESP8266 IRrecv::decodeTcl96Ac (ir_Tcl.cpp lines 569-616)
def decodeTcl96Ac(results, offset: int = 1, nbits: int = kTcl96AcBits, strict: bool = True) -> bool:
    """
    Decode a TCL 96-bit A/C IR message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeTcl96Ac
    """
    # Import here to avoid circular imports
    from app.core.ir_protocols.ir_recv import kHeader, kFooter, matchMark, matchSpace, matchAtLeast

    if results.rawlen < nbits + kHeader + kFooter - 1 + offset:
        return False  # Message is smaller than we expected
    if strict and nbits != kTcl96AcBits:
        return False  # Not strictly a TCL96AC message

    data = 0

    # Header
    if not matchMark(results.rawbuf[offset], kTcl96AcHdrMark):
        return False
    offset += 1
    if not matchSpace(results.rawbuf[offset], kTcl96AcHdrSpace):
        return False
    offset += 1

    # Data (2 bits at a time)
    bits_so_far = 0
    while bits_so_far < nbits:
        if bits_so_far % 8:
            data <<= 2  # Make space for the new data bits
        else:
            data = 0

        if not matchMark(results.rawbuf[offset], kTcl96AcBitMark):
            return False
        offset += 1

        value = 0
        while value < kTcl96AcSpaceCount:
            if matchSpace(results.rawbuf[offset], kTcl96AcBitSpaces[value]):
                data += value
                break
            value += 1

        if value >= kTcl96AcSpaceCount:
            return False  # No matches
        offset += 1
        results.state[bits_so_far // 8] = data
        bits_so_far += 2

    # Footer
    if not matchMark(results.rawbuf[offset], kTcl96AcBitMark):
        return False
    offset += 1

    if offset < results.rawlen:
        if not matchAtLeast(results.rawbuf[offset], kTcl96AcGap):
            return False

    # Success
    # results.decode_type = TCL96AC  # Would set protocol type in C++
    results.bits = nbits
    return True
