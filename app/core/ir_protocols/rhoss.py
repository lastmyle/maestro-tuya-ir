# Copyright 2021 Tom Rosenback
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Support for Rhoss A/C protocol
## Direct translation from IRremoteESP8266 ir_Rhoss.cpp and ir_Rhoss.h

# Supports:
#   Brand: Rhoss, Model: Idrowall MPCV 20-30-35-40

from typing import List

# Constants - Timing values (from ir_Rhoss.cpp lines 14-20)
kRhossHdrMark = 3042
kRhossHdrSpace = 4248
kRhossBitMark = 648
kRhossOneSpace = 1545
kRhossZeroSpace = 457
kRhossGap = 100000  # kDefaultMessageGap
kRhossFreq = 38

# Constants from IRremoteESP8266.h lines 1442-1444
kRhossStateLength = 12
kRhossBits = kRhossStateLength * 8
kRhossDefaultRepeat = 0

# Fan Control (from ir_Rhoss.h lines 62-65)
kRhossFanAuto = 0b00
kRhossFanMin = 0b01
kRhossFanMed = 0b10
kRhossFanMax = 0b11

# Modes (from ir_Rhoss.h lines 67-71)
kRhossModeHeat = 0b0001
kRhossModeCool = 0b0010
kRhossModeDry = 0b0011
kRhossModeFan = 0b0100
kRhossModeAuto = 0b0101

# Temperature (from ir_Rhoss.h lines 74-75)
kRhossTempMin = 16  # Celsius
kRhossTempMax = 30  # Celsius

# Power (from ir_Rhoss.h lines 78-79)
kRhossPowerOn = 0b10  # 0x2
kRhossPowerOff = 0b01  # 0x1

# Swing (from ir_Rhoss.h lines 82-83)
kRhossSwingOn = 0b1  # 0x1
kRhossSwingOff = 0b0  # 0x0

# Defaults (from ir_Rhoss.h lines 85-89)
kRhossDefaultFan = kRhossFanAuto
kRhossDefaultMode = kRhossModeCool
kRhossDefaultTemp = 21  # Celsius
kRhossDefaultPower = False
kRhossDefaultSwing = False


## Native representation of a Rhoss A/C message.
## Direct translation of the C++ union/struct (from ir_Rhoss.h lines 24-57)
class RhossProtocol:
    def __init__(self):
        # The state array (12 bytes for Rhoss)
        self.raw = [0] * kRhossStateLength

    # Byte 1 (from ir_Rhoss.h lines 30-31)
    @property
    def Temp(self) -> int:
        return self.raw[1] & 0x0F

    @Temp.setter
    def Temp(self, value: int) -> None:
        self.raw[1] = (self.raw[1] & 0xF0) | (value & 0x0F)

    # Byte 4 (from ir_Rhoss.h lines 37-39)
    @property
    def Fan(self) -> int:
        return self.raw[4] & 0x03

    @Fan.setter
    def Fan(self, value: int) -> None:
        self.raw[4] = (self.raw[4] & 0xFC) | (value & 0x03)

    @property
    def Mode(self) -> int:
        return (self.raw[4] >> 4) & 0x0F

    @Mode.setter
    def Mode(self, value: int) -> None:
        self.raw[4] = (self.raw[4] & 0x0F) | ((value & 0x0F) << 4)

    # Byte 5 (from ir_Rhoss.h lines 41-43)
    @property
    def Swing(self) -> int:
        return self.raw[5] & 0x01

    @Swing.setter
    def Swing(self, value: int) -> None:
        if value:
            self.raw[5] |= 0x01
        else:
            self.raw[5] &= 0xFE

    @property
    def Power(self) -> int:
        return (self.raw[5] >> 6) & 0x03

    @Power.setter
    def Power(self, value: int) -> None:
        self.raw[5] = (self.raw[5] & 0x3F) | ((value & 0x03) << 6)

    # Byte 11 (from ir_Rhoss.h line 55)
    @property
    def Sum(self) -> int:
        return self.raw[11]

    @Sum.setter
    def Sum(self, value: int) -> None:
        self.raw[11] = value & 0xFF


## Send a Rhoss HVAC formatted message.
## Status: STABLE / Reported as working.
## @param[in] data The message to be sent.
## @param[in] nbytes The number of bytes of message to be sent.
## @param[in] repeat The number of times the command is to be repeated.
## Direct translation from IRremoteESP8266 IRsend::sendRhoss (ir_Rhoss.cpp lines 33-48)
def sendRhoss(data: List[int], nbytes: int, repeat: int = kRhossDefaultRepeat) -> List[int]:
    """
    Send a Rhoss HVAC formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendRhoss

    Returns timing array instead of transmitting via hardware.
    """
    # Check if we have enough bytes to send a proper message. (ir_Rhoss.cpp line 36)
    if nbytes < kRhossStateLength:
        return []

    # Import here to avoid circular import
    from app.core.ir_protocols.ir_send import sendGeneric

    all_timings = []

    # We always send a message, even for repeat=0, hence '<= repeat'. (ir_Rhoss.cpp line 39)
    for r in range(repeat + 1):
        # Direct translation from ir_Rhoss.cpp lines 40-43
        block_timings = sendGeneric(
            headermark=kRhossHdrMark,
            headerspace=kRhossHdrSpace,
            onemark=kRhossBitMark,
            onespace=kRhossOneSpace,
            zeromark=kRhossBitMark,
            zerospace=kRhossZeroSpace,
            footermark=kRhossBitMark,
            gap=kRhossZeroSpace,
            dataptr=data,
            nbytes=nbytes,
            MSBfirst=False,
        )
        all_timings.extend(block_timings)
        # mark(kRhossBitMark); (ir_Rhoss.cpp line 44)
        all_timings.append(kRhossBitMark)
        # Gap (ir_Rhoss.cpp lines 45-46)
        all_timings.append(kRhossGap)

    return all_timings


## Calculate the checksum for the supplied state.
## @param[in] state The source state to generate the checksum from.
## @param[in] length Length of the supplied state to checksum.
## @return The checksum value.
## Direct translation from IRremoteESP8266 IRRhossAc::calcChecksum (ir_Rhoss.cpp lines 126-128)
def calcChecksum(state: List[int], length: int = kRhossStateLength) -> int:
    """
    Calculate checksum for Rhoss protocol.
    EXACT translation from IRremoteESP8266 IRRhossAc::calcChecksum
    """
    # sumBytes helper function - direct translation
    return sum(state[: length - 1]) & 0xFF


## Verify the checksum is valid for a given state.
## @param[in] state The array to verify the checksum of.
## @param[in] length The size of the state.
## @return A boolean indicating if it's checksum is valid.
## Direct translation from IRremoteESP8266 IRRhossAc::validChecksum (ir_Rhoss.cpp lines 134-136)
def validChecksum(state: List[int], length: int = kRhossStateLength) -> bool:
    """
    Verify checksum is valid for a given state.
    EXACT translation from IRremoteESP8266 IRRhossAc::validChecksum
    """
    return state[length - 1] == calcChecksum(state, length)


## Decode the supplied Rhoss formatted message.
## Status: STABLE / Known working.
## @param[in,out] results Ptr to the data to decode & where to store the result
## @param[in] offset The starting index to use when attempting to decode the
##   raw data. Typically/Defaults to kStartOffset.
## @param[in] nbits The number of data bits to expect.
## @param[in] strict Flag indicating if we should perform strict matching.
## Direct translation from IRremoteESP8266 IRrecv::decodeRhoss (ir_Rhoss.cpp lines 59-99)
def decodeRhoss(results, offset: int = 1, nbits: int = kRhossBits, strict: bool = True) -> bool:
    """
    Decode a Rhoss HVAC IR message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeRhoss

    This is the ACTUAL C++ decoder function, not a wrapper.
    """
    # Import here to avoid circular imports
    from app.core.ir_protocols.ir_recv import (
        kHeader,
        kFooter,
        kMarkExcess,
        _matchGeneric,
        matchMark,
        matchAtLeast,
    )

    # Direct translation from ir_Rhoss.cpp line 61
    if strict and nbits != kRhossBits:
        return False

    # Direct translation from ir_Rhoss.cpp lines 63-65
    if results.rawlen <= 2 * nbits + kHeader + kFooter - 1 + offset:
        return False  # Can't possibly be a valid Rhoss message.

    # Header + Data Block (96 bits) + Footer (ir_Rhoss.cpp lines 68-75)
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state,
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=kRhossBits,
        hdrmark=kRhossHdrMark,
        hdrspace=kRhossHdrSpace,
        onemark=kRhossBitMark,
        onespace=kRhossOneSpace,
        zeromark=kRhossBitMark,
        zerospace=kRhossZeroSpace,
        footermark=kRhossBitMark,
        footerspace=kRhossZeroSpace,
        atleast=False,
        tolerance=25,
        excess=kMarkExcess,
        MSBfirst=False,
    )

    # Direct translation from ir_Rhoss.cpp lines 77-78
    if not used:
        return False
    offset += used

    # Footer (Part 2) (ir_Rhoss.cpp lines 81-83)
    if not matchMark(results.rawbuf[offset], kRhossBitMark):
        offset += 1
    else:
        offset += 1

    # Direct translation from ir_Rhoss.cpp lines 85-88
    if offset < results.rawlen and not matchAtLeast(results.rawbuf[offset], kRhossGap):
        return False

    # Direct translation from ir_Rhoss.cpp line 90
    if strict and not validChecksum(results.state):
        return False

    # Success (ir_Rhoss.cpp lines 92-98)
    # results.decode_type = RHOSS  # Would set protocol type in C++
    results.bits = nbits
    # No need to record the state as we stored it as we decoded it.
    # As we use result->state, we don't record value, address, or command as it
    # is a union data type.
    return True


## Class for handling detailed Rhoss A/C messages.
## Direct translation from C++ IRRhossAc class (ir_Rhoss.h lines 94-144)
class IRRhossAc:
    ## Class Constructor
    ## @param[in] pin GPIO to be used when sending.
    ## @param[in] inverted Is the output signal to be inverted?
    ## @param[in] use_modulation Is frequency modulation to be used?
    ## Direct translation from ir_Rhoss.cpp lines 107-109
    def __init__(self) -> None:
        self._: RhossProtocol = RhossProtocol()
        self.stateReset()

    ## Reset the internals of the object to a known good state.
    ## Direct translation from ir_Rhoss.cpp lines 145-155
    def stateReset(self) -> None:
        # for (uint8_t i = 1; i < kRhossStateLength; i++) _.raw[i] = 0x0;
        for i in range(1, kRhossStateLength):
            self._.raw[i] = 0x0
        self._.raw[0] = 0xAA
        self._.raw[2] = 0x60
        self._.raw[6] = 0x54
        self._.Power = kRhossDefaultPower
        self._.Fan = kRhossDefaultFan
        self._.Mode = kRhossDefaultMode
        self._.Swing = kRhossDefaultSwing
        self._.Temp = kRhossDefaultTemp - kRhossTempMin

    ## Update the checksum value for the internal state.
    ## Direct translation from ir_Rhoss.cpp lines 139-142
    def checksum(self) -> None:
        self._.Sum = calcChecksum(self._.raw, kRhossStateLength)
        self._.raw[kRhossStateLength - 1] = self._.Sum

    ## Get the raw state of the object, suitable to be sent with the appropriate
    ## IRsend object method.
    ## @return A PTR to the internal state.
    ## Direct translation from ir_Rhoss.cpp lines 160-163
    def getRaw(self) -> List[int]:
        self.checksum()  # Ensure correct bit array before returning
        return self._.raw

    ## Set the raw state of the object.
    ## @param[state] state The raw state from the native IR message.
    ## Direct translation from ir_Rhoss.cpp lines 167-169
    def setRaw(self, state: List[int]) -> None:
        for i in range(min(len(state), kRhossStateLength)):
            self._.raw[i] = state[i]

    ## Set the internal state to have the power on.
    ## Direct translation from ir_Rhoss.cpp line 172
    def on(self) -> None:
        self.setPower(True)

    ## Set the internal state to have the power off.
    ## Direct translation from ir_Rhoss.cpp line 175
    def off(self) -> None:
        self.setPower(False)

    ## Set the internal state to have the desired power.
    ## @param[in] on The desired power state.
    ## Direct translation from ir_Rhoss.cpp lines 179-181
    def setPower(self, on: bool) -> None:
        self._.Power = kRhossPowerOn if on else kRhossPowerOff

    ## Get the power setting from the internal state.
    ## @return A boolean indicating the power setting.
    ## Direct translation from ir_Rhoss.cpp lines 185-187
    def getPower(self) -> bool:
        return self._.Power == kRhossPowerOn

    ## Set the temperature.
    ## @param[in] degrees The temperature in degrees celsius.
    ## Direct translation from ir_Rhoss.cpp lines 191-194
    def setTemp(self, degrees: int) -> None:
        temp = max(kRhossTempMin, degrees)
        self._.Temp = min(kRhossTempMax, temp) - kRhossTempMin

    ## Get the current temperature setting.
    ## @return Get current setting for temp. in degrees celsius.
    ## Direct translation from ir_Rhoss.cpp lines 198-200
    def getTemp(self) -> int:
        return self._.Temp + kRhossTempMin

    ## Set the speed of the fan.
    ## @param[in] speed The desired setting.
    ## Direct translation from ir_Rhoss.cpp lines 204-215
    def setFan(self, speed: int) -> None:
        if speed in [kRhossFanAuto, kRhossFanMin, kRhossFanMed, kRhossFanMax]:
            self._.Fan = speed
        else:
            self._.Fan = kRhossFanAuto

    ## Get the current fan speed setting.
    ## @return The current fan speed.
    ## Direct translation from ir_Rhoss.cpp lines 219-221
    def getFan(self) -> int:
        return self._.Fan

    ## Set the Vertical Swing mode of the A/C.
    ## @param[in] state true, the Swing is on. false, the Swing is off.
    ## Direct translation from ir_Rhoss.cpp lines 225-227
    def setSwing(self, state: bool) -> None:
        self._.Swing = state

    ## Get the Vertical Swing speed of the A/C.
    ## @return The native swing speed setting.
    ## Direct translation from ir_Rhoss.cpp lines 231-233
    def getSwing(self) -> int:
        return self._.Swing

    ## Get the current operation mode setting.
    ## @return The current operation mode.
    ## Direct translation from ir_Rhoss.cpp lines 237-239
    def getMode(self) -> int:
        return self._.Mode

    ## Set the desired operation mode.
    ## @param[in] mode The desired operation mode.
    ## Direct translation from ir_Rhoss.cpp lines 243-256
    def setMode(self, mode: int) -> None:
        if mode in [kRhossModeFan, kRhossModeCool, kRhossModeDry, kRhossModeHeat, kRhossModeAuto]:
            self._.Mode = mode
            return
        else:
            self._.Mode = kRhossDefaultMode

    ## Convert a stdAc::opmode_t enum into its native mode.
    ## @param[in] mode The enum to be converted.
    ## @return The native equivalent of the enum.
    ## Direct translation from ir_Rhoss.cpp lines 261-276
    @staticmethod
    def convertMode(mode: str) -> int:
        """
        Convert common mode to Rhoss native mode.
        mode: 'cool', 'heat', 'dry', 'fan', 'auto'
        """
        if mode == "cool":
            return kRhossModeCool
        elif mode == "heat":
            return kRhossModeHeat
        elif mode == "dry":
            return kRhossModeDry
        elif mode == "fan":
            return kRhossModeFan
        elif mode == "auto":
            return kRhossModeAuto
        else:
            return kRhossDefaultMode

    ## Convert a stdAc::fanspeed_t enum into it's native speed.
    ## @param[in] speed The enum to be converted.
    ## @return The native equivalent of the enum.
    ## Direct translation from ir_Rhoss.cpp lines 281-294
    @staticmethod
    def convertFan(speed: str) -> int:
        """
        Convert common fan speed to Rhoss native fan speed.
        speed: 'min', 'low', 'medium', 'high', 'max', 'auto'
        """
        if speed in ["min", "low"]:
            return kRhossFanMin
        elif speed == "medium":
            return kRhossFanMed
        elif speed in ["high", "max"]:
            return kRhossFanMax
        else:
            return kRhossDefaultFan

    ## Convert a native mode into its stdAc equivalent.
    ## @param[in] mode The native setting to be converted.
    ## @return The stdAc equivalent of the native setting.
    ## Direct translation from ir_Rhoss.cpp lines 299-308
    @staticmethod
    def toCommonMode(mode: int) -> str:
        """
        Convert Rhoss native mode to common mode string.
        """
        if mode == kRhossModeCool:
            return "cool"
        elif mode == kRhossModeHeat:
            return "heat"
        elif mode == kRhossModeDry:
            return "dry"
        elif mode == kRhossModeFan:
            return "fan"
        elif mode == kRhossModeAuto:
            return "auto"
        else:
            return "auto"

    ## Convert a native fan speed into its stdAc equivalent.
    ## @param[in] speed The native setting to be converted.
    ## @return The stdAc equivalent of the native setting.
    ## Direct translation from ir_Rhoss.cpp lines 313-322
    @staticmethod
    def toCommonFanSpeed(speed: int) -> str:
        """
        Convert Rhoss native fan speed to common fan speed string.
        """
        if speed == kRhossFanMax:
            return "max"
        elif speed == kRhossFanMed:
            return "medium"
        elif speed == kRhossFanMin:
            return "min"
        elif speed == kRhossFanAuto:
            return "auto"
        else:
            return "auto"
