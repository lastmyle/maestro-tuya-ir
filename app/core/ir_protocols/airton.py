# Copyright 2021 David Conran (crankyoldgit)
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Support for Airton protocol
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/1670
## Direct translation from IRremoteESP8266 ir_Airton.cpp and ir_Airton.h

from typing import List

# Supports:
#   Brand: Airton,  Model: SMVH09B-2A2A3NH ref. 409730 A/C
#   Brand: Airton,  Model: RD1A1 remote

# Constants - Timing values (from ir_Airton.cpp lines 13-18)
kAirtonHdrMark = 6630
kAirtonBitMark = 400
kAirtonHdrSpace = 3350
kAirtonOneSpace = 1260
kAirtonZeroSpace = 430
kAirtonFreq = 38000  # Hz. (Just a guess)

# State length constants (from IRremoteESP8266.h)
kAirtonBits = 56
kAirtonDefaultRepeat = 0  # kNoRepeat

# Mode constants (from ir_Airton.h lines 57-61)
kAirtonAuto = 0b000  # 0
kAirtonCool = 0b001  # 1
kAirtonDry = 0b010  # 2
kAirtonFan = 0b011  # 3
kAirtonHeat = 0b100  # 4

# Fan speed constants (from ir_Airton.h lines 63-68)
kAirtonFanAuto = 0b000  # 0
kAirtonFanMin = 0b001  # 1
kAirtonFanLow = 0b010  # 2
kAirtonFanMed = 0b011  # 3
kAirtonFanHigh = 0b100  # 4
kAirtonFanMax = 0b101  # 5

# Temperature constants (from ir_Airton.h lines 70-71)
kAirtonMinTemp = 16  # 16C
kAirtonMaxTemp = 31  # 31C


## Helper function for sumBytes
## EXACT translation from IRremoteESP8266 IRutils.cpp sumBytes
def sumBytes(data: int, length: int, init: int = 0) -> int:
    """
    Sum all the bytes together in an integer.
    EXACT translation from IRremoteESP8266 IRutils.cpp sumBytes
    """
    checksum = init
    copy = data
    for i in range(length):
        checksum += copy & 0xFF
        copy >>= 8
    return checksum & 0xFF


## Native representation of an Airton 56-bit A/C message.
## This is a direct translation of the C++ union/struct
## @see https://docs.google.com/spreadsheets/d/1Kpq7WCkh85heLnTQGlwUfCR6eeu_vfBHvhii8wtP4LU/edit?usp=sharing
class AirtonProtocol:
    def __init__(self):
        # The raw state as a 64-bit integer
        self.raw = 0

    # Byte 1 & 0 (LSB) (from ir_Airton.h lines 30)
    @property
    def Header(self) -> int:
        return self.raw & 0xFFFF

    @Header.setter
    def Header(self, value: int) -> None:
        self.raw = (self.raw & 0xFFFFFFFFFFFF0000) | (value & 0xFFFF)

    # Byte 2 (from ir_Airton.h lines 32-35)
    @property
    def Mode(self) -> int:
        return (self.raw >> 16) & 0x07

    @Mode.setter
    def Mode(self, value: int) -> None:
        self.raw = (self.raw & 0xFFFFFFFFFFF8FFFF) | ((value & 0x07) << 16)

    @property
    def Power(self) -> int:
        return (self.raw >> 19) & 0x01

    @Power.setter
    def Power(self, value: bool) -> None:
        if value:
            self.raw |= 1 << 19
        else:
            self.raw &= ~(1 << 19)

    @property
    def Fan(self) -> int:
        return (self.raw >> 20) & 0x07

    @Fan.setter
    def Fan(self, value: int) -> None:
        self.raw = (self.raw & 0xFFFFFFFFFF8FFFFF) | ((value & 0x07) << 20)

    @property
    def Turbo(self) -> int:
        return (self.raw >> 23) & 0x01

    @Turbo.setter
    def Turbo(self, value: bool) -> None:
        if value:
            self.raw |= 1 << 23
        else:
            self.raw &= ~(1 << 23)

    # Byte 3 (from ir_Airton.h lines 37-38)
    @property
    def Temp(self) -> int:
        return (self.raw >> 24) & 0x0F

    @Temp.setter
    def Temp(self, value: int) -> None:
        self.raw = (self.raw & 0xFFFFFFFFF0FFFFFF) | ((value & 0x0F) << 24)

    # Byte 4 (from ir_Airton.h lines 40-41)
    @property
    def SwingV(self) -> int:
        return (self.raw >> 32) & 0x01

    @SwingV.setter
    def SwingV(self, value: bool) -> None:
        if value:
            self.raw |= 1 << 32
        else:
            self.raw &= ~(1 << 32)

    # Byte 5 (from ir_Airton.h lines 43-50)
    @property
    def Econo(self) -> int:
        return (self.raw >> 40) & 0x01

    @Econo.setter
    def Econo(self, value: bool) -> None:
        if value:
            self.raw |= 1 << 40
        else:
            self.raw &= ~(1 << 40)

    @property
    def Sleep(self) -> int:
        return (self.raw >> 41) & 0x01

    @Sleep.setter
    def Sleep(self, value: bool) -> None:
        if value:
            self.raw |= 1 << 41
        else:
            self.raw &= ~(1 << 41)

    @property
    def NotAutoOn(self) -> int:
        return (self.raw >> 42) & 0x01

    @NotAutoOn.setter
    def NotAutoOn(self, value: bool) -> None:
        if value:
            self.raw |= 1 << 42
        else:
            self.raw &= ~(1 << 42)

    @property
    def HeatOn(self) -> int:
        return (self.raw >> 44) & 0x01

    @HeatOn.setter
    def HeatOn(self, value: bool) -> None:
        if value:
            self.raw |= 1 << 44
        else:
            self.raw &= ~(1 << 44)

    @property
    def Health(self) -> int:
        return (self.raw >> 46) & 0x01

    @Health.setter
    def Health(self, value: bool) -> None:
        if value:
            self.raw |= 1 << 46
        else:
            self.raw &= ~(1 << 46)

    @property
    def Light(self) -> int:
        return (self.raw >> 47) & 0x01

    @Light.setter
    def Light(self, value: bool) -> None:
        if value:
            self.raw |= 1 << 47
        else:
            self.raw &= ~(1 << 47)

    # Byte 6 (from ir_Airton.h line 52)
    @property
    def Sum(self) -> int:
        return (self.raw >> 48) & 0xFF

    @Sum.setter
    def Sum(self, value: int) -> None:
        self.raw = (self.raw & 0xFF00FFFFFFFFFFFF) | ((value & 0xFF) << 48)


## Function should be safe up to 64 bits.
## Send a Airton formatted message.
## Status: STABLE / Confirmed working.
## @param[in] data containing the IR command.
## @param[in] nbits Nr. of bits to send. usually kAirtonBits
## @param[in] repeat Nr. of times the message is to be repeated.
## Direct translation from IRremoteESP8266 IRsend::sendAirton (ir_Airton.cpp lines 28-40)
def sendAirton(
    data: int, nbits: int = kAirtonBits, repeat: int = kAirtonDefaultRepeat
) -> List[int]:
    """
    Send a Airton formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendAirton

    Returns timing array instead of transmitting via hardware.
    """
    # Import here to avoid circular import
    from app.core.ir_protocols.ir_send import sendGeneric

    return sendGeneric(
        headermark=kAirtonHdrMark,
        headerspace=kAirtonHdrSpace,
        onemark=kAirtonBitMark,
        onespace=kAirtonOneSpace,
        zeromark=kAirtonBitMark,
        zerospace=kAirtonZeroSpace,
        footermark=kAirtonBitMark,
        data=data,
        nbits=nbits,
        MSBfirst=False,
    )


## Decode the supplied Airton message.
## Status: STABLE / Confirmed working. LSBF ordering confirmed via temperature.
## @param[in,out] results Ptr to the data to decode & where to store the decode
## @param[in] offset The starting index to use when attempting to decode the
##   raw data. Typically/Defaults to kStartOffset.
## @param[in] nbits The number of data bits to expect.
## @param[in] strict Flag indicating if we should perform strict matching.
## @return A boolean. True if it can decode it, false if it can't.
## Direct translation from IRremoteESP8266 IRrecv::decodeAirton (ir_Airton.cpp lines 44-76)
def decodeAirton(results, offset: int = 1, nbits: int = kAirtonBits, strict: bool = True) -> bool:
    """
    Decode a Airton HVAC IR message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeAirton

    This is the ACTUAL C++ decoder function, not a wrapper.
    """
    # Import here to avoid circular imports
    from app.core.ir_protocols.ir_recv import kHeader, kFooter, matchGeneric

    if results.rawlen < 2 * nbits + kHeader + kFooter - offset:
        return False  # Too short a message to match.
    if strict and nbits != kAirtonBits:
        return False

    # Header + Data + Footer
    if not matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_ptr=None,
        remaining=results.rawlen - offset,
        nbits=nbits,
        hdrmark=kAirtonHdrMark,
        hdrspace=kAirtonHdrSpace,
        onemark=kAirtonBitMark,
        onespace=kAirtonOneSpace,
        zeromark=kAirtonBitMark,
        zerospace=kAirtonZeroSpace,
        footermark=kAirtonBitMark,
        footerspace=20000,  # kDefaultMessageGap
        atleast=True,
        tolerance=25,  # kUseDefTol
        excess=50,  # kMarkExcess
        MSBfirst=False,
    ):
        return False

    # Compliance
    if strict and not IRAirtonAc.validChecksum(results.value):
        return False

    # Success
    results.decode_type = "AIRTON"
    results.bits = nbits
    results.command = 0
    results.address = 0
    return True


## Class for handling detailed Airton A/C messages.
## Direct translation from C++ IRAirtonAc class
class IRAirtonAc:
    ## Class constructor
    ## @param[in] pin GPIO to be used when sending.
    ## @param[in] inverted Is the output signal to be inverted?
    ## @param[in] use_modulation Is frequency modulation to be used?
    ## Direct translation from ir_Airton.cpp lines 78-84
    def __init__(self) -> None:
        self._: AirtonProtocol = AirtonProtocol()
        self.stateReset()

    ## Reset the internals of the object to a known good state.
    ## Direct translation from ir_Airton.cpp line 117
    def stateReset(self) -> None:
        self.setRaw(0x11D3)

    ## Get the raw state of the object, suitable to be sent with the appropriate
    ## IRsend object method.
    ## @return A copy to the internal state.
    ## Direct translation from ir_Airton.cpp lines 119-125
    def getRaw(self) -> int:
        self.checksum()  # Ensure correct bit array before returning
        return self._.raw

    ## Set the raw state of the object.
    ## @param[in] state The raw state from the native IR message.
    ## Direct translation from ir_Airton.cpp lines 127-129
    def setRaw(self, state: int) -> None:
        self._.raw = state

    ## Set the internal state to have the power on.
    ## Direct translation from ir_Airton.cpp line 133
    def on(self) -> None:
        self.setPower(True)

    ## Set the internal state to have the power off.
    ## Direct translation from ir_Airton.cpp line 136
    def off(self) -> None:
        self.setPower(False)

    ## Set the internal state to have the desired power.
    ## @param[in] on The desired power state.
    ## Direct translation from ir_Airton.cpp lines 139-143
    def setPower(self, on: bool) -> None:
        self._.Power = on
        self.setMode(self.getMode())  # Re-do the mode incase we need to do something special.

    ## Get the power setting from the internal state.
    ## @return A boolean indicating the power setting.
    ## Direct translation from ir_Airton.cpp line 147
    def getPower(self) -> bool:
        return bool(self._.Power)

    ## Get the current operation mode setting.
    ## @return The current operation mode.
    ## Direct translation from ir_Airton.cpp line 151
    def getMode(self) -> int:
        return self._.Mode

    ## Set the desired operation mode.
    ## @param[in] mode The desired operation mode.
    ## Direct translation from ir_Airton.cpp lines 154-175
    def setMode(self, mode: int) -> None:
        # Changing the mode always removes the sleep setting.
        if mode != self._.Mode:
            self.setSleep(False)
        # Set the actual mode.
        self._.Mode = kAirtonAuto if mode > kAirtonHeat else mode
        # Handle special settings for each mode.
        if self._.Mode == kAirtonAuto:
            self.setTemp(25)  # Auto has a fixed temp.
            self._.NotAutoOn = not self.getPower()
        elif self._.Mode == kAirtonHeat:
            # When powered on and in Heat mode, set a special bit.
            self._.HeatOn = self.getPower()
            # FALL-THRU
            self._.NotAutoOn = True
        else:
            self._.NotAutoOn = True
        # Reset the economy setting if we need to.
        self.setEcono(self.getEcono())

    ## Convert a stdAc::opmode_t enum into its native mode.
    ## @param[in] mode The enum to be converted.
    ## @return The native equivalent of the enum.
    ## Direct translation from ir_Airton.cpp lines 177-188
    @staticmethod
    def convertMode(mode: str) -> int:
        # mode is stdAc::opmode_t equivalent (string)
        if mode == "kCool":
            return kAirtonCool
        elif mode == "kHeat":
            return kAirtonHeat
        elif mode == "kDry":
            return kAirtonDry
        elif mode == "kFan":
            return kAirtonFan
        else:
            return kAirtonAuto

    ## Convert a native mode into its stdAc equivalent.
    ## @param[in] mode The native setting to be converted.
    ## @return The stdAc equivalent of the native setting.
    ## Direct translation from ir_Airton.cpp lines 190-201
    @staticmethod
    def toCommonMode(mode: int) -> str:
        # Returns stdAc::opmode_t equivalent (string)
        if mode == kAirtonCool:
            return "kCool"
        elif mode == kAirtonHeat:
            return "kHeat"
        elif mode == kAirtonDry:
            return "kDry"
        elif mode == kAirtonFan:
            return "kFan"
        else:
            return "kAuto"

    ## Set the temperature.
    ## @param[in] degrees The temperature in degrees celsius.
    ## Direct translation from ir_Airton.cpp lines 203-210
    def setTemp(self, degrees: int) -> None:
        temp = max(kAirtonMinTemp, degrees)
        temp = min(kAirtonMaxTemp, temp)
        if self._.Mode == kAirtonAuto:
            temp = kAirtonMaxTemp  # Auto has a fixed temp.
        self._.Temp = temp - kAirtonMinTemp

    ## Get the current temperature setting.
    ## @return Get current setting for temp. in degrees celsius.
    ## Direct translation from ir_Airton.cpp line 214
    def getTemp(self) -> int:
        return self._.Temp + kAirtonMinTemp

    ## Set the speed of the fan.
    ## @param[in] speed The desired setting.
    ## Direct translation from ir_Airton.cpp lines 217-221
    def setFan(self, speed: int) -> None:
        self._.Fan = kAirtonFanAuto if speed > kAirtonFanMax else speed

    ## Get the current fan speed setting.
    ## @return The current fan speed.
    ## Direct translation from ir_Airton.cpp line 225
    def getFan(self) -> int:
        return self._.Fan

    ## Convert a stdAc::fanspeed_t enum into it's native speed.
    ## @param[in] speed The enum to be converted.
    ## @return The native equivalent of the enum.
    ## Direct translation from ir_Airton.cpp lines 227-239
    @staticmethod
    def convertFan(speed: str) -> int:
        # speed is stdAc::fanspeed_t equivalent (string)
        if speed == "kMin":
            return kAirtonFanMin
        elif speed == "kLow":
            return kAirtonFanLow
        elif speed == "kMedium":
            return kAirtonFanMed
        elif speed == "kHigh":
            return kAirtonFanHigh
        elif speed == "kMax":
            return kAirtonFanMax
        else:
            return kAirtonFanAuto

    ## Convert a native fan speed into its stdAc equivalent.
    ## @param[in] speed The native setting to be converted.
    ## @return The stdAc equivalent of the native setting.
    ## Direct translation from ir_Airton.cpp lines 241-253
    @staticmethod
    def toCommonFanSpeed(speed: int) -> str:
        # Returns stdAc::fanspeed_t equivalent (string)
        if speed == kAirtonFanMax:
            return "kMax"
        elif speed == kAirtonFanHigh:
            return "kHigh"
        elif speed == kAirtonFanMed:
            return "kMedium"
        elif speed == kAirtonFanLow:
            return "kLow"
        elif speed == kAirtonFanMin:
            return "kMin"
        else:
            return "kAuto"

    ## Set the Vertical Swing setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Airton.cpp line 257
    def setSwingV(self, on: bool) -> None:
        self._.SwingV = on

    ## Get the Vertical Swing setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Airton.cpp line 261
    def getSwingV(self) -> bool:
        return bool(self._.SwingV)

    ## Set the Light/LED/Display setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Airton.cpp line 265
    def setLight(self, on: bool) -> None:
        self._.Light = on

    ## Get the Light/LED/Display setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Airton.cpp line 269
    def getLight(self) -> bool:
        return bool(self._.Light)

    ## Set the Economy setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## @note Only available in Cool mode.
    ## Direct translation from ir_Airton.cpp lines 271-276
    def setEcono(self, on: bool) -> None:
        self._.Econo = on and (self.getMode() == kAirtonCool)

    ## Get the Economy setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Airton.cpp line 280
    def getEcono(self) -> bool:
        return bool(self._.Econo)

    ## Set the Turbo setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Airton.cpp lines 282-288
    def setTurbo(self, on: bool) -> None:
        self._.Turbo = on
        # Pressing the turbo button sets the fan to max as well.
        if on:
            self.setFan(kAirtonFanMax)

    ## Get the Turbo setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Airton.cpp line 292
    def getTurbo(self) -> bool:
        return bool(self._.Turbo)

    ## Set the Sleep setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## @note Sleep not available in fan or auto mode.
    ## Direct translation from ir_Airton.cpp lines 294-303
    def setSleep(self, on: bool) -> None:
        mode = self.getMode()
        if mode == kAirtonAuto or mode == kAirtonFan:
            self._.Sleep = False
        else:
            self._.Sleep = on

    ## Get the Sleep setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Airton.cpp line 307
    def getSleep(self) -> bool:
        return bool(self._.Sleep)

    ## Set the Health/Filter setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Airton.cpp line 311
    def setHealth(self, on: bool) -> None:
        self._.Health = on

    ## Get the Health/Filter setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Airton.cpp line 315
    def getHealth(self) -> bool:
        return bool(self._.Health)

    ## Calculate the checksum for the supplied state.
    ## @param[in] state The source state to generate the checksum from.
    ## @return The checksum value.
    ## Direct translation from ir_Airton.cpp lines 97-102
    @staticmethod
    def calcChecksum(state: int) -> int:
        return (0x7F - sumBytes(state, 6)) ^ 0x2C

    ## Verify the checksum is valid for a given state.
    ## @param[in] state The value to verify the checksum of.
    ## @return A boolean indicating if it's checksum is valid.
    ## Direct translation from ir_Airton.cpp lines 104-111
    @staticmethod
    def validChecksum(state: int) -> bool:
        p = AirtonProtocol()
        p.raw = state
        return p.Sum == IRAirtonAc.calcChecksum(state)

    ## Update the checksum value for the internal state.
    ## Direct translation from ir_Airton.cpp line 114
    def checksum(self) -> None:
        self._.Sum = IRAirtonAc.calcChecksum(self._.raw)
