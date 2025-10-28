# Copyright 2022 Daniele Gobbetti
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Support for the York AC protocol (remote GRYLH2A)
## Direct translation from IRremoteESP8266 ir_York.cpp and ir_York.h

from typing import List, Optional

# Supports:
#   Brand: York,  Model: MHH07P17 A/C
#   Brand: York,  Model: GRYLH2A remote

# Constants - Timing values (from ir_York.cpp lines 34-39)
kYorkHdrMark = 4887
kYorkBitMark = 612
kYorkHdrSpace = 2267
kYorkOneSpace = 1778
kYorkZeroSpace = 579
kYorkFreq = 38000  # Hz. (Guessing the most common frequency.)

# State length constants (from IRremoteESP8266.h)
kYorkStateLength = 17
kYorkBits = kYorkStateLength * 8  # 136 bits

# Temperature constants (from ir_York.h lines 74-75)
kYorkMinTemp = 18  # Celsius
kYorkMaxTemp = 32  # Celsius

# Fan constants (from ir_York.h lines 77-80)
kYorkFanLow = 1
kYorkFanMedium = 2
kYorkFanHigh = 3
kYorkFanAuto = 8

# Mode constants (from ir_York.h lines 82-86)
kYorkHeat = 1
kYorkCool = 2
kYorkDry = 3
kYorkFan = 4
kYorkAuto = 8

# Known good state (from ir_York.h lines 67-71)
kYorkKnownGoodState = [
    0x08, 0x10, 0x07, 0x02, 0x40, 0x08,
    0x03, 0x18, 0x01, 0x60, 0x00, 0x00, 0x00, 0x00,
    0xEC,
    0xF5, 0xF2  # Mode "Heat", Fan Speed "auto", Temp: 24, Power: on
]


## Native representation of a York A/C message.
## This is a direct translation of the C++ union/struct (from ir_York.h lines 26-64)
class YorkProtocol:
    def __init__(self):
        # The state array (17 bytes for York)
        self.raw = [0] * kYorkStateLength

    # byte 0-5 - preamble (from ir_York.h line 30)
    # unknown, fixed 0x08, 0x10, 0x07, 0x02, 0x40, 0x08

    # byte 6 (from ir_York.h lines 32-36)
    @property
    def Key1(self) -> int:
        return self.raw[6] & 0x0F

    @Key1.setter
    def Key1(self, value: int) -> None:
        self.raw[6] = (self.raw[6] & 0xF0) | (value & 0x0F)

    @property
    def Key2(self) -> int:
        return (self.raw[6] >> 4) & 0x0F

    @Key2.setter
    def Key2(self, value: int) -> None:
        self.raw[6] = (self.raw[6] & 0x0F) | ((value & 0x0F) << 4)

    # byte 7 (from ir_York.h lines 38-40)
    @property
    def Fan(self) -> int:
        return self.raw[7] & 0x0F

    @Fan.setter
    def Fan(self, value: int) -> None:
        self.raw[7] = (self.raw[7] & 0xF0) | (value & 0x0F)

    @property
    def Power(self) -> int:
        return (self.raw[7] >> 4) & 0x01

    @Power.setter
    def Power(self, value: bool) -> None:
        if value:
            self.raw[7] |= 0x10
        else:
            self.raw[7] &= 0xEF

    # byte 8 (from ir_York.h lines 42-43)
    @property
    def Mode(self) -> int:
        return self.raw[8] & 0x0F

    @Mode.setter
    def Mode(self, value: int) -> None:
        self.raw[8] = (self.raw[8] & 0xF0) | (value & 0x0F)

    # byte 9 (from ir_York.h lines 46-47)
    @property
    def Temp(self) -> int:
        return (self.raw[9] >> 2) & 0x3F

    @Temp.setter
    def Temp(self, value: int) -> None:
        self.raw[9] = (self.raw[9] & 0x03) | ((value & 0x3F) << 2)

    # byte 10 (from ir_York.h lines 48-49)
    @property
    def OffTimer(self) -> int:
        return self.raw[10] & 0xFF

    @OffTimer.setter
    def OffTimer(self, value: int) -> None:
        self.raw[10] = value & 0xFF

    # byte 11 (from ir_York.h lines 50-51)
    @property
    def OnTimer(self) -> int:
        return self.raw[11] & 0xFF

    @OnTimer.setter
    def OnTimer(self, value: int) -> None:
        self.raw[11] = value & 0xFF

    # byte 13 (from ir_York.h lines 56-57)
    @property
    def SwingV(self) -> int:
        return self.raw[13] & 0x01

    @SwingV.setter
    def SwingV(self, value: bool) -> None:
        if value:
            self.raw[13] |= 0x01
        else:
            self.raw[13] &= 0xFE

    # byte 15-16 (from ir_York.h lines 61-62)
    @property
    def Chk1(self) -> int:
        return self.raw[15] & 0xFF

    @Chk1.setter
    def Chk1(self, value: int) -> None:
        self.raw[15] = value & 0xFF

    @property
    def Chk2(self) -> int:
        return self.raw[16] & 0xFF

    @Chk2.setter
    def Chk2(self, value: int) -> None:
        self.raw[16] = value & 0xFF


## Send a York A/C message.
## Status: ALPHA / Untested.
## @param[in] data An array of bytes containing the IR command.
## @param[in] nbytes Nr. of bytes of data in the array. (>=kStateLength)
## @param[in] repeat Nr. of times the message is to be repeated.
## Direct translation from IRremoteESP8266 IRsend::sendYork (ir_York.cpp lines 42-57)
def sendYork(data: List[int], nbytes: int, repeat: int = 0) -> List[int]:
    """
    Send a York A/C message.
    EXACT translation from IRremoteESP8266 IRsend::sendYork

    Returns timing array instead of transmitting via hardware.
    """
    if nbytes < kYorkStateLength:
        return []

    # Import here to avoid circular import
    from app.core.ir_protocols.ir_send import sendGeneric

    all_timings = []

    for r in range(repeat + 1):
        timings = sendGeneric(
            headermark=kYorkHdrMark,
            headerspace=kYorkHdrSpace,
            onemark=kYorkBitMark,
            onespace=kYorkOneSpace,
            zeromark=kYorkBitMark,
            zerospace=kYorkZeroSpace,
            footermark=kYorkBitMark,
            gap=0,  # kDefaultMessageGap
            dataptr=data,
            nbytes=nbytes,
            frequency=kYorkFreq,
            MSBfirst=False,  # LSB first
            repeat=0,
            dutycycle=50
        )
        all_timings.extend(timings)

    return all_timings


## Decode the supplied York message.
## Status: ALPHA / Tested, some values still are not mapped to the internal state of AC
## @param[in,out] results Ptr to the data to decode & where to store the decode
## @param[in] offset The starting index to use when attempting to decode the
##   raw data. Typically/Defaults to kStartOffset.
## @param[in] nbits The number of data bits to expect.
## @param[in] strict Flag indicating if we should perform strict matching.
## @return A boolean. True if it can decode it, false if it can't.
## Direct translation from IRremoteESP8266 IRrecv::decodeYork (ir_York.cpp lines 60-92)
def decodeYork(results, offset: int = 1, nbits: int = kYorkBits, strict: bool = True,
               _tolerance: int = 25) -> bool:
    """
    Decode a York HVAC IR message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeYork

    This is the ACTUAL C++ decoder function, not a wrapper.
    """
    # Import here to avoid circular imports
    from app.core.ir_protocols.ir_recv import kMarkExcess, _matchGeneric

    if strict and nbits != kYorkBits:
        return False

    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state,
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=nbits,
        hdrmark=kYorkHdrMark,
        hdrspace=kYorkHdrSpace,
        onemark=kYorkBitMark,
        onespace=kYorkOneSpace,
        zeromark=kYorkBitMark,
        zerospace=kYorkZeroSpace,
        footermark=kYorkBitMark,
        footerspace=0,  # kDefaultMessageGap
        atleast=False,
        tolerance=_tolerance,
        excess=kMarkExcess,
        MSBfirst=False
    )
    if used == 0:
        return False  # We failed to find any data.

    # Success
    # results.decode_type = YORK
    results.bits = nbits

    return True


## CRC16-16 (a.k.a. CRC-16-IBM)
## Direct translation from ir_York.cpp lines 286-302
def calcChecksum(data: List[int]) -> tuple:
    """
    Calculate CRC16-16 checksum for York protocol.
    EXACT translation from IRremoteESP8266 IRYorkAc::calcChecksum

    Returns (Chk1, Chk2) tuple
    """
    length = 14
    reg_crc = 0x0000
    data_idx = 0
    while length > 0:
        reg_crc ^= data[data_idx]
        data_idx += 1
        for index in range(8):
            if reg_crc & 0x01:
                reg_crc = (reg_crc >> 1) ^ 0xA001
            else:
                reg_crc = reg_crc >> 1
        length -= 1

    chk1 = reg_crc & 0xff
    chk2 = (reg_crc >> 8) & 0x00ff
    return (chk1, chk2)


## Class for handling detailed York A/C messages.
## Direct translation from C++ IRYorkAc class (ir_York.h lines 90-136, ir_York.cpp lines 95-357)
class IRYorkAc:
    ## Class Constructor
    ## @param[in] pin GPIO to be used when sending.
    ## @param[in] inverted Is the output signal to be inverted?
    ## @param[in] use_modulation Is frequency modulation to be used?
    ## Direct translation from ir_York.cpp lines 97-105
    def __init__(self) -> None:
        self._: YorkProtocol = YorkProtocol()
        self.stateReset()

    ## Reset the internal state to a fixed known good state.
    ## Direct translation from ir_York.cpp lines 107-111
    def stateReset(self) -> None:
        # This resets to a known-good state.
        self.setRaw(kYorkKnownGoodState)

    ## Get the raw state of the object, suitable to be sent with the appropriate
    ## IRsend object method.
    ## @return A copy of the internal state.
    ## Direct translation from ir_York.cpp lines 116-122
    def getRaw(self) -> List[int]:
        self.calcChecksum()
        return self._.raw

    ## Set the internal state from a valid code for this protocol.
    ## @param[in] new_code A valid code for this protocol.
    ## @param[in] length Length of the code in bytes.
    ## Direct translation from ir_York.cpp lines 124-129
    def setRaw(self, new_code: List[int], length: int = kYorkStateLength) -> None:
        for i in range(min(length, len(self._.raw))):
            self._.raw[i] = new_code[i]

    ## Get the current operation mode setting.
    ## @return The current operation mode.
    ## Direct translation from ir_York.cpp lines 139-143
    def getMode(self) -> int:
        return self._.Mode

    ## Set the desired operation mode.
    ## @param[in] mode The desired operation mode.
    ## Direct translation from ir_York.cpp lines 145-159
    def setMode(self, mode: int) -> None:
        if mode in [kYorkFan, kYorkCool, kYorkHeat, kYorkDry]:
            self._.Mode = mode
        else:
            self._.Mode = kYorkAuto
        self.setFan(self.getFan())  # Ensure the fan is at the correct speed for the new mode.

    ## Convert a stdAc::opmode_t enum into its native mode.
    ## @param[in] mode The enum to be converted.
    ## @return The native equivalent of the enum.
    ## Direct translation from ir_York.cpp lines 161-172
    @staticmethod
    def convertMode(mode: str) -> int:
        """Convert common mode to York mode"""
        if mode == 'cool':
            return kYorkCool
        elif mode == 'heat':
            return kYorkHeat
        elif mode == 'dry':
            return kYorkDry
        elif mode == 'fan':
            return kYorkFan
        else:
            return kYorkAuto

    ## Convert a native mode into its stdAc equivalent.
    ## @param[in] mode The native setting to be converted.
    ## @return The stdAc equivalent of the native setting.
    ## Direct translation from ir_York.cpp lines 174-185
    @staticmethod
    def toCommonMode(mode: int) -> str:
        """Convert York mode to common mode"""
        if mode == kYorkCool:
            return 'cool'
        elif mode == kYorkHeat:
            return 'heat'
        elif mode == kYorkDry:
            return 'dry'
        elif mode == kYorkFan:
            return 'fan'
        else:
            return 'auto'

    ## Set the speed of the fan.
    ## @param[in] speed The desired setting.
    ## @note The fan speed is locked to Low when in Dry mode, to auto when in auto
    ## mode. "Fan" mode has no support for "auto" speed.
    ## Direct translation from ir_York.cpp lines 187-205
    def setFan(self, speed: int) -> None:
        mode = self.getMode()
        if mode == kYorkDry:
            self._.Fan = kYorkFanLow
        elif mode == kYorkFan:
            self._.Fan = min(speed, kYorkFanHigh)
        elif mode == kYorkAuto:
            self._.Fan = kYorkFanAuto
        else:
            self._.Fan = min(speed, kYorkFanAuto)

    ## Get the current fan speed setting.
    ## @return The current fan speed.
    ## Direct translation from ir_York.cpp lines 207-211
    def getFan(self) -> int:
        return self._.Fan

    ## Convert a stdAc::fanspeed_t enum into it's native speed.
    ## @param[in] speed The enum to be converted.
    ## @return The native equivalent of the enum.
    ## Direct translation from ir_York.cpp lines 213-229
    @staticmethod
    def convertFan(speed: str) -> int:
        """Convert common fan speed to York fan speed"""
        if speed in ['min', 'low']:
            return kYorkFanLow
        elif speed == 'medium':
            return kYorkFanMedium
        elif speed in ['high', 'max']:
            return kYorkFanHigh
        else:
            return kYorkFanAuto

    ## Convert a native fan speed into its stdAc equivalent.
    ## @param[in] speed The native setting to be converted.
    ## @return The stdAc equivalent of the native setting.
    ## Direct translation from ir_York.cpp lines 231-241
    @staticmethod
    def toCommonFanSpeed(speed: int) -> str:
        """Convert York fan speed to common fan speed"""
        if speed == kYorkFanHigh:
            return 'max'
        elif speed == kYorkFanMedium:
            return 'medium'
        elif speed == kYorkFanLow:
            return 'min'
        else:
            return 'auto'

    ## Set the temperature.
    ## @param[in] degrees The temperature in degrees celsius.
    ## Direct translation from ir_York.cpp lines 243-247
    def setTemp(self, degrees: int) -> None:
        temp = max(kYorkMinTemp, min(kYorkMaxTemp, degrees))
        self._.Temp = temp

    ## Get the current temperature setting.
    ## @return Get current setting for temp. in degrees celsius.
    ## Direct translation from ir_York.cpp lines 249-253
    def getTemp(self) -> int:
        return self._.Temp

    ## Set the On Timer value of the A/C.
    ## @param[in] nr_of_mins The number of minutes the timer should be.
    ## @note The timer time only has a resolution of 10 mins.
    ## @note Setting the On Timer active will cancel the Sleep timer/setting.
    ## Direct translation from ir_York.cpp lines 255-261
    def setOnTimer(self, nr_of_mins: int) -> None:
        self._.OnTimer = nr_of_mins // 10

    ## Set the Off Timer value of the A/C.
    ## @param[in] nr_of_mins The number of minutes the timer should be.
    ## @note The timer time only has a resolution of 10 mins.
    ## @note Setting the Off Timer active will cancel the Sleep timer/setting.
    ## Direct translation from ir_York.cpp lines 263-269
    def setOffTimer(self, nr_of_mins: int) -> None:
        self._.OffTimer = nr_of_mins // 10

    ## Get the On Timer setting of the A/C.
    ## @return The Nr. of minutes the On Timer is set for.
    ## Direct translation from ir_York.cpp lines 272-276
    def getOnTimer(self) -> int:
        return self._.OnTimer * 10

    ## Get the Off Timer setting of the A/C.
    ## @return The Nr. of minutes the Off Timer is set for.
    ## @note Sleep & Off Timer share the same timer.
    ## Direct translation from ir_York.cpp lines 278-283
    def getOffTimer(self) -> int:
        return self._.OffTimer * 10

    ## CRC16-16 (a.k.a. CRC-16-IBM)
    ## Direct translation from ir_York.cpp lines 285-302
    def calcChecksum(self) -> None:
        """Calculate and set the checksum for the internal state"""
        chk1, chk2 = calcChecksum(self._.raw)
        self._.Chk1 = chk1
        self._.Chk2 = chk2

    ## Convert the current internal state into its stdAc::state_t equivalent.
    ## @param[in] prev Ptr to the previous state if required.
    ## @return The stdAc equivalent of the native settings.
    ## Direct translation from ir_York.cpp lines 304-337
    def toCommon(self, prev: Optional[dict] = None) -> dict:
        """Convert to common A/C state format"""
        result = {}
        # Start with the previous state if given it.
        if prev is not None:
            result = prev.copy()
        else:
            # Set defaults for non-zero values that are not implicitly set for when
            # there is no previous state.
            # e.g. Any setting that toggles should probably go here.
            result['power'] = False

        result['protocol'] = 'YORK'
        result['mode'] = self.toCommonMode(self._.Mode)
        result['celsius'] = True
        result['degrees'] = self.getTemp()
        result['fanspeed'] = self.toCommonFanSpeed(self._.Fan)
        result['swingv'] = 'auto' if self._.SwingV else 'off'
        result['sleep'] = self.getOffTimer()
        # Not supported.
        result['model'] = -1
        result['turbo'] = False
        result['swingh'] = 'off'
        result['light'] = False
        result['filter'] = False
        result['econo'] = False
        result['quiet'] = False
        result['clean'] = False
        result['beep'] = False
        result['clock'] = -1
        return result

    ## Convert the current internal state into a human readable string.
    ## @return A human readable string.
    ## Direct translation from ir_York.cpp lines 339-357
    def toString(self) -> str:
        """Convert current state to human readable string"""
        result = ""
        result += f"Power: {bool(self._.Power)}, "
        result += f"Mode: {self.toCommonMode(self._.Mode)}, "
        result += f"Fan: {self.toCommonFanSpeed(self._.Fan)}, "
        result += f"Temp: {self.getTemp()}C, "
        result += f"SwingV: {bool(self._.SwingV)}, "
        result += f"OnTimer: {self.getOnTimer()} mins, "
        result += f"OffTimer: {self.getOffTimer()} mins"
        return result
