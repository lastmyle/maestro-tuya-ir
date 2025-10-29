# Copyright 2019 David Conran
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Amcor A/C protocol.
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/834
## @remark Kudos to ldellus; For the breakdown and mapping of the bit values.
# Supports:
#   Brand: Amcor,  Model: ADR-853H A/C
#   Brand: Amcor,  Model: TAC-495 remote
#   Brand: Amcor,  Model: TAC-444 remote
## Direct translation from IRremoteESP8266 ir_Amcor.cpp and ir_Amcor.h

from typing import List

# Constants - Timing values (ir_Amcor.cpp lines 17-25)
kAmcorHdrMark = 8200
kAmcorHdrSpace = 4200
kAmcorOneMark = 1500
kAmcorZeroMark = 600
kAmcorOneSpace = kAmcorZeroMark
kAmcorZeroSpace = kAmcorOneMark
kAmcorFooterMark = 1900
kAmcorGap = 34300
kAmcorTolerance = 40

# State length constants (IRremoteESP8266.h)
kAmcorStateLength = 8
kAmcorBits = kAmcorStateLength * 8  # 64 bits
kAmcorDefaultRepeat = 0  # kSingleRepeat

# Fan Control (ir_Amcor.h lines 61-64)
kAmcorFanMin = 0b001
kAmcorFanMed = 0b010
kAmcorFanMax = 0b011
kAmcorFanAuto = 0b100

# Modes (ir_Amcor.h lines 66-70)
kAmcorCool = 0b001
kAmcorHeat = 0b010
kAmcorFan = 0b011  # Aka "Vent"
kAmcorDry = 0b100
kAmcorAuto = 0b101

# Temperature (ir_Amcor.h lines 73-74)
kAmcorMinTemp = 12  # Celsius
kAmcorMaxTemp = 32  # Celsius

# Power (ir_Amcor.h lines 77-78)
kAmcorPowerOn = 0b0011  # 0x3
kAmcorPowerOff = 0b1100  # 0xC

# Max Mode (aka "Lo" in Cool and "Hi" in Heat) (ir_Amcor.h line 81)
kAmcorMax = 0b11

# "Vent" Mode (ir_Amcor.h line 84)
kAmcorVentOn = 0b11


## Native representation of a Amcor A/C message.
## This is a direct translation of the C++ union/struct (ir_Amcor.h lines 28-56)
class AmcorProtocol:
    def __init__(self):
        # The state array (8 bytes for Amcor)
        self.raw = [0] * kAmcorStateLength

    # Byte 1 (ir_Amcor.h lines 34-37)
    @property
    def Mode(self) -> int:
        return self.raw[1] & 0x07

    @Mode.setter
    def Mode(self, value: int) -> None:
        self.raw[1] = (self.raw[1] & 0xF8) | (value & 0x07)

    @property
    def Fan(self) -> int:
        return (self.raw[1] >> 4) & 0x07

    @Fan.setter
    def Fan(self, value: int) -> None:
        self.raw[1] = (self.raw[1] & 0x8F) | ((value & 0x07) << 4)

    # Byte 2 (ir_Amcor.h lines 39-41)
    @property
    def Temp(self) -> int:
        return (self.raw[2] >> 1) & 0x3F

    @Temp.setter
    def Temp(self, value: int) -> None:
        self.raw[2] = (self.raw[2] & 0x81) | ((value & 0x3F) << 1)

    # Byte 5 (ir_Amcor.h lines 47-48)
    @property
    def Power(self) -> int:
        return (self.raw[5] >> 4) & 0x0F

    @Power.setter
    def Power(self, value: int) -> None:
        self.raw[5] = (self.raw[5] & 0x0F) | ((value & 0x0F) << 4)

    # Byte 6 (ir_Amcor.h lines 50-52)
    @property
    def Max(self) -> int:
        return self.raw[6] & 0x03

    @Max.setter
    def Max(self, value: int) -> None:
        self.raw[6] = (self.raw[6] & 0xFC) | (value & 0x03)

    @property
    def Vent(self) -> int:
        return (self.raw[6] >> 6) & 0x03

    @Vent.setter
    def Vent(self, value: int) -> None:
        self.raw[6] = (self.raw[6] & 0x3F) | ((value & 0x03) << 6)

    # Byte 7 (ir_Amcor.h line 54)
    @property
    def Sum(self) -> int:
        return self.raw[7]

    @Sum.setter
    def Sum(self, value: int) -> None:
        self.raw[7] = value & 0xFF


## Calculate the checksum for the supplied state.
## @param[in] state The source state to generate the checksum from.
## @param[in] length Length of the supplied state to checksum.
## @return The checksum value.
## Direct translation from ir_Amcor.cpp lines 110-116
def calcChecksumAmcor(state: List[int], length: int = kAmcorStateLength) -> int:
    """
    Calculate checksum for Amcor protocol.
    EXACT translation from IRremoteESP8266 IRAmcorAc::calcChecksum
    """
    # Uses irutils::sumNibbles - sum lower and upper nibbles
    result = 0
    for i in range(length - 1):
        result += state[i] & 0x0F  # Lower nibble
        result += state[i] >> 4  # Upper nibble
    return result & 0xFF


## Verify the checksum is valid for a given state.
## @param[in] state The array to verify the checksum of.
## @param[in] length The size of the state.
## @return A boolean indicating if it's checksum is valid.
## Direct translation from ir_Amcor.cpp lines 118-124
def validChecksumAmcor(state: List[int], length: int = kAmcorStateLength) -> bool:
    """
    Verify the checksum is valid for a given state.
    EXACT translation from IRremoteESP8266 IRAmcorAc::validChecksum
    """
    return state[length - 1] == calcChecksumAmcor(state, length)


## Send a Amcor HVAC formatted message.
## Status: STABLE / Reported as working.
## @param[in] data The message to be sent.
## @param[in] nbytes The number of bytes of message to be sent.
## @param[in] repeat The number of times the command is to be repeated.
## Direct translation from ir_Amcor.cpp lines 32-45
def sendAmcor(
    data: List[int], nbytes: int = kAmcorStateLength, repeat: int = kAmcorDefaultRepeat
) -> List[int]:
    """
    Send a Amcor HVAC formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendAmcor

    Returns timing array instead of transmitting via hardware.
    """
    # Check if we have enough bytes to send a proper message.
    if nbytes < kAmcorStateLength:
        return []

    from app.core.ir_protocols.ir_send import sendGeneric

    all_timings = []

    for r in range(repeat + 1):
        timings = sendGeneric(
            headermark=kAmcorHdrMark,
            headerspace=kAmcorHdrSpace,
            onemark=kAmcorOneMark,
            onespace=kAmcorOneSpace,
            zeromark=kAmcorZeroMark,
            zerospace=kAmcorZeroSpace,
            footermark=kAmcorFooterMark,
            gap=kAmcorGap,
            dataptr=data,
            nbytes=nbytes,
            frequency=38,
            MSBfirst=False,
            repeat=0,
            dutycycle=50,  # kDutyDefault
        )
        all_timings.extend(timings)

    return all_timings


## Decode the supplied Amcor HVAC message.
## Status: STABLE / Reported as working.
## @param[in,out] results Ptr to the data to decode & where to store the decode result.
## @param[in] offset The starting index to use when attempting to decode the raw data.
## @param[in] nbits The number of data bits to expect.
## @param[in] strict Flag indicating if we should perform strict matching.
## @return A boolean. True if it can decode it, false if it can't.
## Direct translation from ir_Amcor.cpp lines 48-89
def decodeAmcor(results, offset: int = 1, nbits: int = kAmcorBits, strict: bool = True) -> bool:
    """
    Decode the supplied Amcor HVAC message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeAmcor
    """
    from app.core.ir_protocols.ir_recv import kHeader, _matchGeneric

    if results.rawlen <= 2 * nbits + kHeader - 1 + offset:
        return False  # Can't possibly be a valid Amcor message.
    if strict and nbits != kAmcorBits:
        return False  # We expect Amcor to be 64 bits of message.

    # Header + Data Block (64 bits) + Footer
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state,
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=64,
        hdrmark=kAmcorHdrMark,
        hdrspace=kAmcorHdrSpace,
        onemark=kAmcorOneMark,
        onespace=kAmcorOneSpace,
        zeromark=kAmcorZeroMark,
        zerospace=kAmcorZeroSpace,
        footermark=kAmcorFooterMark,
        footerspace=kAmcorGap,
        atleast=True,
        tolerance=kAmcorTolerance,
        excess=0,  # kMarkExcess
        MSBfirst=False,
    )
    if not used:
        return False
    offset += used

    if strict:
        if not validChecksumAmcor(results.state):
            return False

    # Success
    results.bits = nbits
    results.decode_type = "AMCOR"
    # No need to record the state as we stored it as we decoded it.
    # As we use result->state, we don't record value, address, or command as it
    # is a union data type.
    return True


## Class for handling detailed Amcor A/C messages.
## Direct translation from C++ IRAmcorAc class (ir_Amcor.h lines 90-140, ir_Amcor.cpp)
class IRAmcorAc:
    ## Class Constructor
    ## @param[in] pin GPIO to be used when sending.
    ## @param[in] inverted Is the output signal to be inverted?
    ## @param[in] use_modulation Is frequency modulation to be used?
    ## Direct translation from ir_Amcor.cpp lines 91-97
    def __init__(self) -> None:
        self._: AmcorProtocol = AmcorProtocol()
        self.stateReset()

    ## Reset the internals of the object to a known good state.
    ## Direct translation from ir_Amcor.cpp lines 132-138
    def stateReset(self) -> None:
        for i in range(1, kAmcorStateLength):
            self._.raw[i] = 0x0
        self._.raw[0] = 0x01
        self._.Fan = kAmcorFanAuto
        self._.Mode = kAmcorAuto
        self._.Temp = 25  # 25C

    ## Update the checksum value for the internal state.
    ## Direct translation from ir_Amcor.cpp lines 127-129
    def checksum(self) -> None:
        self._.Sum = calcChecksumAmcor(self._.raw, kAmcorStateLength)

    ## Get the raw state of the object, suitable to be sent with the appropriate
    ## IRsend object method.
    ## @return A PTR to the internal state.
    ## Direct translation from ir_Amcor.cpp lines 140-146
    def getRaw(self) -> List[int]:
        self.checksum()  # Ensure correct bit array before returning
        return self._.raw

    ## Set the raw state of the object.
    ## @param[in] state The raw state from the native IR message.
    ## Direct translation from ir_Amcor.cpp lines 148-152
    def setRaw(self, state: List[int]) -> None:
        for i in range(min(len(state), kAmcorStateLength)):
            self._.raw[i] = state[i]

    ## Set the internal state to have the power on.
    ## Direct translation from ir_Amcor.cpp line 155
    def on(self) -> None:
        self.setPower(True)

    ## Set the internal state to have the power off.
    ## Direct translation from ir_Amcor.cpp line 158
    def off(self) -> None:
        self.setPower(False)

    ## Set the internal state to have the desired power.
    ## @param[in] on The desired power state.
    ## Direct translation from ir_Amcor.cpp lines 160-164
    def setPower(self, on: bool) -> None:
        self._.Power = kAmcorPowerOn if on else kAmcorPowerOff

    ## Get the power setting from the internal state.
    ## @return A boolean indicating the power setting.
    ## Direct translation from ir_Amcor.cpp lines 166-170
    def getPower(self) -> bool:
        return self._.Power == kAmcorPowerOn

    ## Set the temperature.
    ## @param[in] degrees The temperature in degrees celsius.
    ## Direct translation from ir_Amcor.cpp lines 172-178
    def setTemp(self, degrees: int) -> None:
        temp = max(kAmcorMinTemp, degrees)
        temp = min(kAmcorMaxTemp, temp)
        self._.Temp = temp

    ## Get the current temperature setting.
    ## @return Get current setting for temp. in degrees celsius.
    ## Direct translation from ir_Amcor.cpp lines 180-184
    def getTemp(self) -> int:
        return self._.Temp

    ## Control the current Maximum Cooling or Heating setting. (i.e. Turbo)
    ## @note Only allowed in Cool or Heat mode.
    ## @param[in] on The desired setting.
    ## Direct translation from ir_Amcor.cpp lines 186-199
    def setMax(self, on: bool) -> None:
        if on:
            if self._.Mode == kAmcorCool:
                self._.Temp = kAmcorMinTemp
            elif self._.Mode == kAmcorHeat:
                self._.Temp = kAmcorMaxTemp
            else:
                # Not allowed in all other operating modes.
                return
        self._.Max = kAmcorMax if on else 0

    ## Is the Maximum Cooling or Heating setting (i.e. Turbo) setting on?
    ## @return The current value.
    ## Direct translation from ir_Amcor.cpp lines 201-205
    def getMax(self) -> bool:
        return self._.Max == kAmcorMax

    ## Set the speed of the fan.
    ## @param[in] speed The desired setting.
    ## Direct translation from ir_Amcor.cpp lines 207-220
    def setFan(self, speed: int) -> None:
        if speed in [kAmcorFanAuto, kAmcorFanMin, kAmcorFanMed, kAmcorFanMax]:
            self._.Fan = speed
        else:
            self._.Fan = kAmcorFanAuto

    ## Get the current fan speed setting.
    ## @return The current fan speed.
    ## Direct translation from ir_Amcor.cpp lines 222-226
    def getFan(self) -> int:
        return self._.Fan

    ## Get the current operation mode setting.
    ## @return The current operation mode.
    ## Direct translation from ir_Amcor.cpp lines 228-232
    def getMode(self) -> int:
        return self._.Mode

    ## Set the desired operation mode.
    ## @param[in] mode The desired operation mode.
    ## Direct translation from ir_Amcor.cpp lines 234-251
    def setMode(self, mode: int) -> None:
        if mode in [kAmcorFan, kAmcorCool, kAmcorHeat, kAmcorDry, kAmcorAuto]:
            self._.Vent = kAmcorVentOn if mode == kAmcorFan else 0
            self._.Mode = mode
            return
        else:
            self._.Vent = 0
            self._.Mode = kAmcorAuto

    ## Convert a stdAc::opmode_t enum into its native mode.
    ## @param[in] mode The enum to be converted.
    ## @return The native equivalent of the enum.
    ## Direct translation from ir_Amcor.cpp lines 253-269
    @staticmethod
    def convertMode(mode: str) -> int:
        """Convert common mode to native mode"""
        if mode == "cool":
            return kAmcorCool
        elif mode == "heat":
            return kAmcorHeat
        elif mode == "dry":
            return kAmcorDry
        elif mode == "fan":
            return kAmcorFan
        else:
            return kAmcorAuto

    ## Convert a stdAc::fanspeed_t enum into it's native speed.
    ## @param[in] speed The enum to be converted.
    ## @return The native equivalent of the enum.
    ## Direct translation from ir_Amcor.cpp lines 271-287
    @staticmethod
    def convertFan(speed: str) -> int:
        """Convert common fan speed to native fan speed"""
        if speed in ["min", "low"]:
            return kAmcorFanMin
        elif speed == "medium":
            return kAmcorFanMed
        elif speed in ["high", "max"]:
            return kAmcorFanMax
        else:
            return kAmcorFanAuto

    ## Convert a native mode into its stdAc equivalent.
    ## @param[in] mode The native setting to be converted.
    ## @return The stdAc equivalent of the native setting.
    ## Direct translation from ir_Amcor.cpp lines 289-300
    @staticmethod
    def toCommonMode(mode: int) -> str:
        """Convert native mode to common mode"""
        if mode == kAmcorCool:
            return "cool"
        elif mode == kAmcorHeat:
            return "heat"
        elif mode == kAmcorDry:
            return "dry"
        elif mode == kAmcorFan:
            return "fan"
        else:
            return "auto"

    ## Convert a native fan speed into its stdAc equivalent.
    ## @param[in] speed The native setting to be converted.
    ## @return The stdAc equivalent of the native setting.
    ## Direct translation from ir_Amcor.cpp lines 302-312
    @staticmethod
    def toCommonFanSpeed(speed: int) -> str:
        """Convert native fan speed to common fan speed"""
        if speed == kAmcorFanMax:
            return "max"
        elif speed == kAmcorFanMed:
            return "medium"
        elif speed == kAmcorFanMin:
            return "min"
        else:
            return "auto"

    ## Convert the current internal state into its stdAc::state_t equivalent.
    ## @return The stdAc equivalent of the native settings.
    ## Direct translation from ir_Amcor.cpp lines 314-338
    def toCommon(self) -> dict:
        """Convert the internal state to common A/C state"""
        result = {}
        result["protocol"] = "AMCOR"
        result["power"] = self.getPower()
        result["mode"] = self.toCommonMode(self._.Mode)
        result["celsius"] = True
        result["degrees"] = self._.Temp
        result["fanspeed"] = self.toCommonFanSpeed(self._.Fan)
        # Not supported.
        result["model"] = -1
        result["turbo"] = False
        result["swingv"] = "off"
        result["swingh"] = "off"
        result["light"] = False
        result["filter"] = False
        result["econo"] = False
        result["quiet"] = False
        result["clean"] = False
        result["beep"] = False
        result["sleep"] = -1
        result["clock"] = -1
        return result

    ## Convert the current internal state into a human readable string.
    ## @return A human readable string.
    ## Direct translation from ir_Amcor.cpp lines 340-354
    def toString(self) -> str:
        """Convert the internal state to a human readable string"""
        result = ""
        result += "Power: "
        result += "On" if self.getPower() else "Off"
        result += ", Mode: "
        result += str(self._.Mode)
        result += ", Fan: "
        result += str(self._.Fan)
        result += ", Temp: "
        result += str(self._.Temp) + "C"
        result += ", Max: "
        result += "On" if self.getMax() else "Off"
        return result
