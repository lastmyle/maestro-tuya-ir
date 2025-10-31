# Copyright 2009 Ken Shirriff
# Copyright 2016 marcosamarinho
# Copyright 2017-2021 David Conran
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Support for Sanyo protocols.
## Sanyo LC7461 support originally by marcosamarinho
## Sanyo SA 8650B originally added from
##   https://github.com/shirriff/Arduino-IRremote/
## @see https://github.com/z3t0/Arduino-IRremote/blob/master/ir_Sanyo.cpp
## @see http://pdf.datasheetcatalog.com/datasheet/sanyo/LC7461.pdf
## @see https://github.com/marcosamarinho/IRremoteESP8266/blob/master/ir_Sanyo.cpp
## @see http://slydiman.narod.ru/scr/kb/sanyo.htm
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/1211
## @see https://docs.google.com/spreadsheets/d/1dYfLsnYvpjV-SgO8pdinpfuBIpSzm8Q1R5SabrLeskw/edit?usp=sharing
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/1503
## @see https://docs.google.com/spreadsheets/d/1weUmGAsEpfX38gg5rlDN69Uchnbr6gQl9FqHffLBIRk/edit#gid=0
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/1826

from typing import List, Optional

# Supports:
#   Brand: Sanyo,  Model: SA 8650B - disabled
#   Brand: Sanyo,  Model: LC7461 transmitter IC (SANYO_LC7461)
#   Brand: Sanyo,  Model: SAP-K121AHA A/C (SANYO_AC)
#   Brand: Sanyo,  Model: RCS-2HS4E remote (SANYO_AC)
#   Brand: Sanyo,  Model: SAP-K242AH A/C (SANYO_AC)
#   Brand: Sanyo,  Model: RCS-2S4E remote (SANYO_AC)
#   Brand: Sanyo,  Model: RCS-4MHVPIS4EE remote (SANYO_AC152)
#   Brand: Sanyo,  Model: SAP-KMRV124EHE A/C (SANYO_AC152)

# Constants - Sanyo SA 8650B
# ir_Sanyo.cpp:38-44
kSanyoSa8650bHdrMark = 3500  # seen range 3500
kSanyoSa8650bHdrSpace = 950  # seen 950
kSanyoSa8650bOneMark = 2400  # seen 2400
kSanyoSa8650bZeroMark = 700  # seen 700
# usually see 713 - not using ticks as get number wrapround
kSanyoSa8650bDoubleSpaceUsecs = 800
kSanyoSa8650bRptLength = 45000

# Sanyo LC7461
# ir_Sanyo.cpp:46-61
kSanyoLC7461AddressBits = 13
kSanyoLC7461CommandBits = 8
kSanyoLC7461Bits = 42
kSanyoLc7461AddressMask = (1 << kSanyoLC7461AddressBits) - 1
kSanyoLc7461CommandMask = (1 << kSanyoLC7461CommandBits) - 1
kSanyoLc7461HdrMark = 9000
kSanyoLc7461HdrSpace = 4500
kSanyoLc7461BitMark = 560  # 1T
kSanyoLc7461OneSpace = 1690  # 3T
kSanyoLc7461ZeroSpace = 560  # 1T
kSanyoLc7461MinCommandLength = 108000

kSanyoLc7461MinGap = kSanyoLc7461MinCommandLength - (
    kSanyoLc7461HdrMark
    + kSanyoLc7461HdrSpace
    + kSanyoLC7461Bits * (kSanyoLc7461BitMark + (kSanyoLc7461OneSpace + kSanyoLc7461ZeroSpace) // 2)
    + kSanyoLc7461BitMark
)

# Sanyo AC
# ir_Sanyo.cpp:63-69
kSanyoAcStateLength = 9
kSanyoAcBits = kSanyoAcStateLength * 8
kSanyoAcHdrMark = 8500  # uSeconds
kSanyoAcHdrSpace = 4200  # uSeconds
kSanyoAcBitMark = 500  # uSeconds
kSanyoAcOneSpace = 1600  # uSeconds
kSanyoAcZeroSpace = 550  # uSeconds
kSanyoAcGap = 100000  # kDefaultMessageGap uSeconds (Guess only)
kSanyoAcFreq = 38000  # Hz. (Guess only)

# Sanyo AC 88-bit
# ir_Sanyo.cpp:71-78
kSanyoAc88StateLength = 11
kSanyoAc88Bits = kSanyoAc88StateLength * 8
kSanyoAc88HdrMark = 5400  # uSeconds
kSanyoAc88HdrSpace = 2000  # uSeconds
kSanyoAc88BitMark = 500  # uSeconds
kSanyoAc88OneSpace = 1500  # uSeconds
kSanyoAc88ZeroSpace = 750  # uSeconds
kSanyoAc88Gap = 3675  # uSeconds
kSanyoAc88Freq = 38000  # Hz. (Guess only)
kSanyoAc88ExtraTolerance = 5  # (%) Extra tolerance to use.
kSanyoAc88MinRepeat = 1  # Minimum number of repeats required

# Sanyo AC 152-bit
# ir_Sanyo.cpp:80-86
kSanyoAc152StateLength = 19
kSanyoAc152Bits = kSanyoAc152StateLength * 8
kSanyoAc152HdrMark = 3300  # uSeconds
kSanyoAc152BitMark = 440  # uSeconds
kSanyoAc152HdrSpace = 1725  # uSeconds
kSanyoAc152OneSpace = 1290  # uSeconds
kSanyoAc152ZeroSpace = 405  # uSeconds
kSanyoAc152Freq = 38000  # Hz. (Guess only)
kSanyoAc152ExtraTolerance = 13  # (%) Extra tolerance to use.

# Sanyo AC constants
# ir_Sanyo.h:83-107
kSanyoAcTempMin = 16  # Celsius
kSanyoAcTempMax = 30  # Celsius
kSanyoAcTempDelta = 4  # Celsius to Native Temp difference.

kSanyoAcHourMax = 15  # 0b1111

kSanyoAcHeat = 1  # 0b001
kSanyoAcCool = 2  # 0b010
kSanyoAcDry = 3  # 0b011
kSanyoAcAuto = 4  # 0b100
kSanyoAcFanAuto = 0  # 0b00
kSanyoAcFanHigh = 1  # 0b01
kSanyoAcFanLow = 2  # 0b10
kSanyoAcFanMedium = 3  # 0b11

# const uint8_t kSanyoAcPowerStandby = 0b00;  # Standby?
kSanyoAcPowerOff = 0b01  # Off
kSanyoAcPowerOn = 0b10  # On
kSanyoAcSwingVAuto = 0  # 0b000
kSanyoAcSwingVLowest = 2  # 0b010
kSanyoAcSwingVLow = 3  # 0b011
kSanyoAcSwingVLowerMiddle = 4  # 0b100
kSanyoAcSwingVUpperMiddle = 5  # 0b101
kSanyoAcSwingVHigh = 6  # 0b110
kSanyoAcSwingVHighest = 7  # 0b111

# Sanyo AC88 constants
# ir_Sanyo.h:174-187
kSanyoAc88Auto = 0  # 0b000
kSanyoAc88FeelCool = 1  # 0b001
kSanyoAc88Cool = 2  # 0b010
kSanyoAc88FeelHeat = 3  # 0b011
kSanyoAc88Heat = 4  # 0b100
kSanyoAc88Fan = 5  # 0b101

kSanyoAc88TempMin = 10  # Celsius
kSanyoAc88TempMax = 30  # Celsius

kSanyoAc88FanAuto = 0  # 0b00
kSanyoAc88FanLow = 1  # 0b01
kSanyoAc88FanMedium = 2  # 0b10
kSanyoAc88FanHigh = 3  # 0b11


## Construct a Sanyo LC7461 message.
## @param[in] address The 13 bit value of the address(Custom) portion of the protocol.
## @param[in] command The 8 bit value of the command(Key) portion of the protocol.
## @return An int with the encoded raw 42 bit Sanyo LC7461 data value.
## @note This protocol uses the NEC protocol timings. However, data is
##  formatted as : address(13 bits), !address, command(8 bits), !command.
##  According with LIRC, this protocol is used on Sanyo, Aiwa and Chinon
## ir_Sanyo.cpp:98-114
def encodeSanyoLC7461(address: int, command: int) -> int:
    # Mask our input values to ensure the correct bit sizes.
    address &= kSanyoLc7461AddressMask
    command &= kSanyoLc7461CommandMask

    data = address
    address ^= kSanyoLc7461AddressMask  # Invert the 13 LSBs.
    # Append the now inverted address.
    data = (data << kSanyoLC7461AddressBits) | address
    # Append the command.
    data = (data << kSanyoLC7461CommandBits) | command
    command ^= kSanyoLc7461CommandMask  # Invert the command.
    # Append the now inverted command.
    data = (data << kSanyoLC7461CommandBits) | command

    return data


## Send a Sanyo LC7461 message.
## Status: BETA / Probably works.
## @param[in] data The message to be sent.
## @param[in] nbits The number of bits of message to be sent.
## @param[in] repeat The number of times the command is to be repeated.
## @note Based on @marcosamarinho's work.
##   This protocol uses the NEC protocol timings. However, data is
##   formatted as : address(13 bits), !address, command (8 bits), !command.
##   According with LIRC, this protocol is used on Sanyo, Aiwa and Chinon
##   Information for this protocol is available at the Sanyo LC7461 datasheet.
##   Repeats are performed similar to the NEC method of sending a special
##   repeat message, rather than duplicating the entire message.
## @see https://github.com/marcosamarinho/IRremoteESP8266/blob/master/ir_Sanyo.cpp
## @see http://pdf.datasheetcatalog.com/datasheet/sanyo/LC7461.pdf
## ir_Sanyo.cpp:130-134
def sendSanyoLC7461(data: int, nbits: int = kSanyoLC7461Bits, repeat: int = 0) -> List[int]:
    # This protocol appears to be another 42-bit variant of the NEC protocol.
    from app.core.ir_protocols.ir_send import sendNEC

    return sendNEC(data, nbits, repeat)


## Decode the supplied SANYO LC7461 message.
## Status: BETA / Probably works.
## @param[in,out] results Ptr to the data to decode & where to store the result
## @param[in] offset The starting index to use when attempting to decode the
##   raw data. Typically/Defaults to kStartOffset.
## @param[in] nbits The number of data bits to expect.
## @param[in] strict Flag indicating if we should perform strict matching.
## @return True if it can decode it, false if it can't.
## @note Based on @marcosamarinho's work.
##   This protocol uses the NEC protocol. However, data is
##   formatted as : address(13 bits), !address, command (8 bits), !command.
##   According with LIRC, this protocol is used on Sanyo, Aiwa and Chinon
##   Information for this protocol is available at the Sanyo LC7461 datasheet.
## @see http://slydiman.narod.ru/scr/kb/sanyo.htm
## @see https://github.com/marcosamarinho/IRremoteESP8266/blob/master/ir_Sanyo.cpp
## @see http://pdf.datasheetcatalog.com/datasheet/sanyo/LC7461.pdf
## ir_Sanyo.cpp:154-188
def decodeSanyoLC7461(
    results, offset: int = 1, nbits: int = kSanyoLC7461Bits, strict: bool = True
) -> bool:
    from app.core.ir_protocols.ir_recv import decodeNEC

    if strict and nbits != kSanyoLC7461Bits:
        return False  # Not strictly in spec.
    # This protocol is basically a 42-bit variant of the NEC protocol.
    if not decodeNEC(results, offset, nbits, False):
        return False  # Didn't match a NEC format (without strict)

    # Bits 30 to 42+.
    address = results.value >> (kSanyoLC7461Bits - kSanyoLC7461AddressBits)
    # Bits 9 to 16.
    command = (results.value >> kSanyoLC7461CommandBits) & kSanyoLc7461CommandMask
    # Compliance
    if strict:
        if results.bits != nbits:
            return False
        # Bits 17 to 29.
        inverted_address = (
            results.value >> (kSanyoLC7461CommandBits * 2)
        ) & kSanyoLc7461AddressMask
        # Bits 1-8.
        inverted_command = results.value & kSanyoLc7461CommandMask
        if (address ^ kSanyoLc7461AddressMask) != inverted_address:
            return False  # Address integrity check failed.
        if (command ^ kSanyoLc7461CommandMask) != inverted_command:
            return False  # Command integrity check failed.

    # Success
    results.decode_type = "SANYO_LC7461"
    results.address = address
    results.command = command
    return True


## Send a SanyoAc formatted message.
## Status: STABLE / Reported as working.
## @param[in] data An array of bytes containing the IR command.
## @param[in] nbytes Nr. of bytes of data in the array.
## @param[in] repeat Nr. of times the message is to be repeated.
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/1211
## ir_Sanyo.cpp:270-278
def sendSanyoAc(data: List[int], nbytes: int = kSanyoAcStateLength, repeat: int = 0) -> List[int]:
    from app.core.ir_protocols.ir_send import sendGeneric

    # Header + Data + Footer
    return sendGeneric(
        headermark=kSanyoAcHdrMark,
        headerspace=kSanyoAcHdrSpace,
        onemark=kSanyoAcBitMark,
        onespace=kSanyoAcOneSpace,
        zeromark=kSanyoAcBitMark,
        zerospace=kSanyoAcZeroSpace,
        footermark=kSanyoAcBitMark,
        gap=kSanyoAcGap,
        dataptr=data,
        nbytes=nbytes,
        MSBfirst=False,
    )


## Decode the supplied SanyoAc message.
## Status: STABLE / Reported as working.
## @param[in,out] results Ptr to the data to decode & where to store the decode
## @param[in] offset The starting index to use when attempting to decode the
##   raw data. Typically/Defaults to kStartOffset.
## @param[in] nbits The number of data bits to expect.
## @param[in] strict Flag indicating if we should perform strict matching.
## @return A boolean. True if it can decode it, false if it can't.
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/1211
## ir_Sanyo.cpp:291-315
def decodeSanyoAc(results, offset: int = 1, nbits: int = kSanyoAcBits, strict: bool = True) -> bool:
    from app.core.ir_protocols.ir_recv import matchGeneric, kUseDefTol, kMarkExcess

    if strict and nbits != kSanyoAcBits:
        return False

    # Header + Data + Footer
    if not matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_ptr=results.state,
        remaining=results.rawlen - offset,
        nbits=nbits,
        hdrmark=kSanyoAcHdrMark,
        hdrspace=kSanyoAcHdrSpace,
        onemark=kSanyoAcBitMark,
        onespace=kSanyoAcOneSpace,
        zeromark=kSanyoAcBitMark,
        zerospace=kSanyoAcZeroSpace,
        footermark=kSanyoAcBitMark,
        footerspace=kSanyoAcGap,
        atleast=True,
        tolerance=kUseDefTol,
        excess=kMarkExcess,
        MSBfirst=False,
    ):
        return False
    # Compliance
    if strict:
        if not IRSanyoAc.validChecksum(results.state, nbits // 8):
            return False

    # Success
    results.decode_type = "SANYO_AC"
    results.bits = nbits
    # No need to record the state as we stored it as we decoded it.
    # As we use result->state, we don't record value, address, or command as it
    # is a union data type.
    return True


## Native representation of a Sanyo A/C message.
## Direct translation from C++ union SanyoProtocol
## ir_Sanyo.h:43-79
class SanyoProtocol:
    def __init__(self):
        # The state array (9 bytes for Sanyo AC)
        self.raw = [0] * kSanyoAcStateLength

    # Byte 0
    # Fixed value 0x6A

    # Byte 1
    @property
    def Temp(self) -> int:
        return self.raw[1] & 0x1F

    @Temp.setter
    def Temp(self, value: int) -> None:
        self.raw[1] = (self.raw[1] & 0xE0) | (value & 0x1F)

    # Byte 2
    @property
    def SensorTemp(self) -> int:
        return self.raw[2] & 0x1F

    @SensorTemp.setter
    def SensorTemp(self, value: int) -> None:
        self.raw[2] = (self.raw[2] & 0xE0) | (value & 0x1F)

    @property
    def Sensor(self) -> int:
        return (self.raw[2] >> 5) & 0x01

    @Sensor.setter
    def Sensor(self, value: bool) -> None:
        if value:
            self.raw[2] |= 0x20
        else:
            self.raw[2] &= 0xDF

    @property
    def Beep(self) -> int:
        return (self.raw[2] >> 6) & 0x01

    @Beep.setter
    def Beep(self, value: bool) -> None:
        if value:
            self.raw[2] |= 0x40
        else:
            self.raw[2] &= 0xBF

    # Byte 3
    @property
    def OffHour(self) -> int:
        return self.raw[3] & 0x0F

    @OffHour.setter
    def OffHour(self, value: int) -> None:
        self.raw[3] = (self.raw[3] & 0xF0) | (value & 0x0F)

    # Byte 4
    @property
    def Fan(self) -> int:
        return self.raw[4] & 0x03

    @Fan.setter
    def Fan(self, value: int) -> None:
        self.raw[4] = (self.raw[4] & 0xFC) | (value & 0x03)

    @property
    def OffTimer(self) -> int:
        return (self.raw[4] >> 2) & 0x01

    @OffTimer.setter
    def OffTimer(self, value: bool) -> None:
        if value:
            self.raw[4] |= 0x04
        else:
            self.raw[4] &= 0xFB

    @property
    def Mode(self) -> int:
        return (self.raw[4] >> 4) & 0x07

    @Mode.setter
    def Mode(self, value: int) -> None:
        self.raw[4] = (self.raw[4] & 0x8F) | ((value & 0x07) << 4)

    # Byte 5
    @property
    def SwingV(self) -> int:
        return self.raw[5] & 0x07

    @SwingV.setter
    def SwingV(self, value: int) -> None:
        self.raw[5] = (self.raw[5] & 0xF8) | (value & 0x07)

    @property
    def Power(self) -> int:
        return (self.raw[5] >> 6) & 0x03

    @Power.setter
    def Power(self, value: int) -> None:
        self.raw[5] = (self.raw[5] & 0x3F) | ((value & 0x03) << 6)

    # Byte 6
    @property
    def Sleep(self) -> int:
        return (self.raw[6] >> 3) & 0x01

    @Sleep.setter
    def Sleep(self, value: bool) -> None:
        if value:
            self.raw[6] |= 0x08
        else:
            self.raw[6] &= 0xF7

    # Byte 7
    # Unused

    # Byte 8
    @property
    def Sum(self) -> int:
        return self.raw[8]

    @Sum.setter
    def Sum(self, value: int) -> None:
        self.raw[8] = value & 0xFF


## Class for handling detailed Sanyo A/C messages.
## Direct translation from C++ IRSanyoAc class
## ir_Sanyo.h:111-172
class IRSanyoAc:
    ## Class Constructor
    ## ir_Sanyo.cpp:322-324
    def __init__(self) -> None:
        self._: SanyoProtocol = SanyoProtocol()
        self.stateReset()

    ## Reset the state of the remote to a known  state/sequence.
    ## ir_Sanyo.cpp:327-331
    def stateReset(self) -> None:
        kReset = [0x6A, 0x6D, 0x51, 0x00, 0x10, 0x45, 0x00, 0x00, 0x33]
        self._.raw = kReset.copy()

    ## Calculate the checksum for a given state.
    ## @param[in] state The array to calc the checksum of.
    ## @param[in] length The length/size of the array.
    ## @return The calculated checksum value.
    ## ir_Sanyo.cpp:362-365
    @staticmethod
    def calcChecksum(state: List[int], length: int = kSanyoAcStateLength) -> int:
        from app.core.ir_protocols.ir_utils import sumNibbles

        return sumNibbles(state, length - 1) if length else 0

    ## Verify the checksum is valid for a given state.
    ## @param[in] state The array to verify the checksum of.
    ## @param[in] length The length/size of the array.
    ## @return true, if the state has a valid checksum. Otherwise, false.
    ## ir_Sanyo.cpp:371-373
    @staticmethod
    def validChecksum(state: List[int], length: int = kSanyoAcStateLength) -> bool:
        return length and state[length - 1] == IRSanyoAc.calcChecksum(state, length)

    ## Calculate & set the checksum for the current internal state of the remote.
    ## ir_Sanyo.cpp:376-379
    def checksum(self) -> None:
        # Stored the checksum value in the last byte.
        self._.Sum = IRSanyoAc.calcChecksum(self._.raw)

    ## Set the requested power state of the A/C to on.
    ## ir_Sanyo.cpp:383
    def on(self) -> None:
        self.setPower(True)

    ## Set the requested power state of the A/C to off.
    ## ir_Sanyo.cpp:386
    def off(self) -> None:
        self.setPower(False)

    ## Change the power setting.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## ir_Sanyo.cpp:390-392
    def setPower(self, on: bool) -> None:
        self._.Power = kSanyoAcPowerOn if on else kSanyoAcPowerOff

    ## Get the value of the current power setting.
    ## @return true, the setting is on. false, the setting is off.
    ## ir_Sanyo.cpp:396-398
    def getPower(self) -> bool:
        return self._.Power == kSanyoAcPowerOn

    ## Get the operating mode setting of the A/C.
    ## @return The current operating mode setting.
    ## ir_Sanyo.cpp:402-404
    def getMode(self) -> int:
        return self._.Mode

    ## Set the operating mode of the A/C.
    ## @param[in] mode The desired operating mode.
    ## @note If we get an unexpected mode, default to AUTO.
    ## ir_Sanyo.cpp:409-419
    def setMode(self, mode: int) -> None:
        if mode in [kSanyoAcAuto, kSanyoAcCool, kSanyoAcDry, kSanyoAcHeat]:
            self._.Mode = mode
        else:
            self._.Mode = kSanyoAcAuto

    ## Convert a stdAc::opmode_t enum into its native mode.
    ## @param[in] mode The enum to be converted.
    ## @return The native equivalent of the enum.
    ## ir_Sanyo.cpp:424-431
    @staticmethod
    def convertMode(mode: str) -> int:
        if mode == "cool":
            return kSanyoAcCool
        elif mode == "heat":
            return kSanyoAcHeat
        elif mode == "dry":
            return kSanyoAcDry
        else:
            return kSanyoAcAuto

    ## Convert a native mode into its stdAc equivalent.
    ## @param[in] mode The native setting to be converted.
    ## @return The stdAc equivalent of the native setting.
    ## ir_Sanyo.cpp:436-443
    @staticmethod
    def toCommonMode(mode: int) -> str:
        if mode == kSanyoAcCool:
            return "cool"
        elif mode == kSanyoAcHeat:
            return "heat"
        elif mode == kSanyoAcDry:
            return "dry"
        else:
            return "auto"

    ## Set the desired temperature.
    ## @param[in] degrees The temperature in degrees celsius.
    ## ir_Sanyo.cpp:447-451
    def setTemp(self, degrees: int) -> None:
        temp = max(kSanyoAcTempMin, degrees)
        temp = min(kSanyoAcTempMax, temp)
        self._.Temp = temp - kSanyoAcTempDelta

    ## Get the current desired temperature setting.
    ## @return The current setting for temp. in degrees celsius.
    ## ir_Sanyo.cpp:455-457
    def getTemp(self) -> int:
        return self._.Temp + kSanyoAcTempDelta

    ## Set the sensor temperature.
    ## @param[in] degrees The temperature in degrees celsius.
    ## ir_Sanyo.cpp:461-465
    def setSensorTemp(self, degrees: int) -> None:
        temp = max(kSanyoAcTempMin, degrees)
        temp = min(kSanyoAcTempMax, temp)
        self._.SensorTemp = temp - kSanyoAcTempDelta

    ## Get the current sensor temperature setting.
    ## @return The current setting for temp. in degrees celsius.
    ## ir_Sanyo.cpp:469-471
    def getSensorTemp(self) -> int:
        return self._.SensorTemp + kSanyoAcTempDelta

    ## Set the speed of the fan.
    ## @param[in] speed The desired setting.
    ## ir_Sanyo.cpp:475-477
    def setFan(self, speed: int) -> None:
        self._.Fan = speed

    ## Get the current fan speed setting.
    ## @return The current fan speed/mode.
    ## ir_Sanyo.cpp:481-483
    def getFan(self) -> int:
        return self._.Fan

    ## Convert a stdAc::fanspeed_t enum into it's native speed.
    ## @param[in] speed The enum to be converted.
    ## @return The native equivalent of the enum.
    ## ir_Sanyo.cpp:488-497
    @staticmethod
    def convertFan(speed: str) -> int:
        if speed in ["min", "low"]:
            return kSanyoAcFanLow
        elif speed == "medium":
            return kSanyoAcFanMedium
        elif speed in ["high", "max"]:
            return kSanyoAcFanHigh
        else:
            return kSanyoAcFanAuto

    ## Convert a native fan speed into its stdAc equivalent.
    ## @param[in] spd The native setting to be converted.
    ## @return The stdAc equivalent of the native setting.
    ## ir_Sanyo.cpp:502-509
    @staticmethod
    def toCommonFanSpeed(spd: int) -> str:
        if spd == kSanyoAcFanHigh:
            return "high"
        elif spd == kSanyoAcFanMedium:
            return "medium"
        elif spd == kSanyoAcFanLow:
            return "low"
        else:
            return "auto"

    ## Get the vertical swing setting of the A/C.
    ## @return The current swing mode setting.
    ## ir_Sanyo.cpp:513-515
    def getSwingV(self) -> int:
        return self._.SwingV

    ## Set the vertical swing setting of the A/C.
    ## @param[in] setting The value of the desired setting.
    ## ir_Sanyo.cpp:519-525
    def setSwingV(self, setting: int) -> None:
        if setting == kSanyoAcSwingVAuto or (
            setting >= kSanyoAcSwingVLowest and setting <= kSanyoAcSwingVHighest
        ):
            self._.SwingV = setting
        else:
            self._.SwingV = kSanyoAcSwingVAuto

    ## Convert a stdAc::swingv_t enum into it's native setting.
    ## @param[in] position The enum to be converted.
    ## @return The native equivalent of the enum.
    ## ir_Sanyo.cpp:530-539
    @staticmethod
    def convertSwingV(position: str) -> int:
        if position == "highest":
            return kSanyoAcSwingVHighest
        elif position == "high":
            return kSanyoAcSwingVHigh
        elif position == "middle":
            return kSanyoAcSwingVUpperMiddle
        elif position == "low":
            return kSanyoAcSwingVLow
        elif position == "lowest":
            return kSanyoAcSwingVLowest
        else:
            return kSanyoAcSwingVAuto

    ## Convert a native vertical swing postion to it's common equivalent.
    ## @param[in] setting A native position to convert.
    ## @return The common vertical swing position.
    ## ir_Sanyo.cpp:544-554
    @staticmethod
    def toCommonSwingV(setting: int) -> str:
        if setting == kSanyoAcSwingVHighest:
            return "highest"
        elif setting == kSanyoAcSwingVHigh:
            return "high"
        elif setting in [kSanyoAcSwingVUpperMiddle, kSanyoAcSwingVLowerMiddle]:
            return "middle"
        elif setting == kSanyoAcSwingVLow:
            return "low"
        elif setting == kSanyoAcSwingVLowest:
            return "lowest"
        else:
            return "auto"

    ## Set the Sleep (Night Setback) setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## ir_Sanyo.cpp:558-560
    def setSleep(self, on: bool) -> None:
        self._.Sleep = on

    ## Get the Sleep (Night Setback) setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## ir_Sanyo.cpp:564-566
    def getSleep(self) -> bool:
        return bool(self._.Sleep)

    ## Set the Sensor Location setting of the A/C.
    ## i.e. Where the ambient temperature is measured.
    ## @param[in] location true is Unit/Wall, false is Remote/Room.
    ## ir_Sanyo.cpp:571-573
    def setSensor(self, location: bool) -> None:
        self._.Sensor = location

    ## Get the Sensor Location setting of the A/C.
    ## i.e. Where the ambient temperature is measured.
    ## @return true is Unit/Wall, false is Remote/Room.
    ## ir_Sanyo.cpp:578-580
    def getSensor(self) -> bool:
        return bool(self._.Sensor)

    ## Set the Beep setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## ir_Sanyo.cpp:584-586
    def setBeep(self, on: bool) -> None:
        self._.Beep = on

    ## Get the Beep setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## ir_Sanyo.cpp:590-592
    def getBeep(self) -> bool:
        return bool(self._.Beep)

    ## Get the nr of minutes the Off Timer is set to.
    ## @return The timer time expressed as the number of minutes.
    ##   A value of 0 means the Off Timer is off/disabled.
    ## @note The internal precission has a resolution of 1 hour.
    ## ir_Sanyo.cpp:598-603
    def getOffTimer(self) -> int:
        if self._.OffTimer:
            return self._.OffHour * 60
        else:
            return 0

    ## Set the nr of minutes for the Off Timer.
    ## @param[in] mins The timer time expressed as nr. of minutes.
    ##   A value of 0 means the Off Timer is off/disabled.
    ## @note The internal precission has a resolution of 1 hour.
    ## ir_Sanyo.cpp:609-613
    def setOffTimer(self, mins: int) -> None:
        hours = min(mins // 60, kSanyoAcHourMax)
        self._.OffTimer = hours > 0
        self._.OffHour = hours

    ## Get a PTR to the internal state/code for this protocol with all integrity
    ##   checks passing.
    ## @return PTR to a code for this protocol based on the current internal state.
    ## ir_Sanyo.cpp:347-350
    def getRaw(self) -> List[int]:
        self.checksum()
        return self._.raw

    ## Set the internal state from a valid code for this protocol.
    ## @param[in] newState A valid code for this protocol.
    ## ir_Sanyo.cpp:354-356
    def setRaw(self, newState: List[int]) -> None:
        self._.raw = newState[:kSanyoAcStateLength].copy()

    ## Convert the current internal state into its stdAc::state_t equivalent.
    ## @return The stdAc equivalent of the native settings.
    ## ir_Sanyo.cpp:617-641
    def toCommon(self) -> dict:
        result = {}
        result["protocol"] = "SANYO_AC"
        result["model"] = -1  # Not supported.
        result["power"] = self.getPower()
        result["mode"] = IRSanyoAc.toCommonMode(self._.Mode)
        result["celsius"] = True
        result["degrees"] = self.getTemp()
        result["sensorTemperature"] = self.getSensorTemp()
        result["fanspeed"] = IRSanyoAc.toCommonFanSpeed(self._.Fan)
        result["sleep"] = 0 if self._.Sleep else -1
        result["swingv"] = IRSanyoAc.toCommonSwingV(self._.SwingV)
        result["beep"] = bool(self._.Beep)
        result["iFeel"] = not self.getSensor()
        # Not supported.
        result["swingh"] = "off"
        result["turbo"] = False
        result["econo"] = False
        result["light"] = False
        result["filter"] = False
        result["quiet"] = False
        result["clean"] = False
        result["clock"] = -1
        return result

    ## Convert the current internal state into a human readable string.
    ## @return A human readable string.
    ## ir_Sanyo.cpp:645-677
    def toString(self) -> str:
        result = ""
        result += f"Power: {'On' if self.getPower() else 'Off'}, "
        result += f"Mode: {IRSanyoAc.toCommonMode(self._.Mode)}, "
        result += f"Temp: {self.getTemp()}C, "
        result += f"Fan: {IRSanyoAc.toCommonFanSpeed(self._.Fan)}, "
        result += f"Swing(V): {IRSanyoAc.toCommonSwingV(self._.SwingV)}, "
        result += f"Sleep: {'On' if self._.Sleep else 'Off'}, "
        result += f"Beep: {'On' if self._.Beep else 'Off'}, "
        result += f"Sensor: {'Wall' if self._.Sensor else 'Room'}, "
        result += f"Sensor Temp: {self.getSensorTemp()}C, "
        offtime = self.getOffTimer()
        result += f"Off Timer: {'Off' if offtime == 0 else f'{offtime} mins'}"
        return result


## Native representation of a Sanyo 88-bit A/C message.
## Direct translation from C++ union SanyoAc88Protocol
## ir_Sanyo.h:190-225
class SanyoAc88Protocol:
    def __init__(self):
        # The state array (11 bytes for Sanyo AC88)
        self.raw = [0] * kSanyoAc88StateLength

    # Byte 0-1
    # Fixed values 0xAA, 0x55

    # Byte 2
    @property
    def Fan(self) -> int:
        return self.raw[2] & 0x03

    @Fan.setter
    def Fan(self, value: int) -> None:
        self.raw[2] = (self.raw[2] & 0xFC) | (value & 0x03)

    @property
    def Mode(self) -> int:
        return (self.raw[2] >> 4) & 0x07

    @Mode.setter
    def Mode(self, value: int) -> None:
        self.raw[2] = (self.raw[2] & 0x8F) | ((value & 0x07) << 4)

    @property
    def Power(self) -> int:
        return (self.raw[2] >> 7) & 0x01

    @Power.setter
    def Power(self, value: bool) -> None:
        if value:
            self.raw[2] |= 0x80
        else:
            self.raw[2] &= 0x7F

    # Byte 3
    @property
    def Temp(self) -> int:
        return self.raw[3] & 0x1F

    @Temp.setter
    def Temp(self, value: int) -> None:
        self.raw[3] = (self.raw[3] & 0xE0) | (value & 0x1F)

    @property
    def Filter(self) -> int:
        return (self.raw[3] >> 5) & 0x01

    @Filter.setter
    def Filter(self, value: bool) -> None:
        if value:
            self.raw[3] |= 0x20
        else:
            self.raw[3] &= 0xDF

    @property
    def SwingV(self) -> int:
        return (self.raw[3] >> 6) & 0x01

    @SwingV.setter
    def SwingV(self, value: bool) -> None:
        if value:
            self.raw[3] |= 0x40
        else:
            self.raw[3] &= 0xBF

    # Byte 4
    @property
    def ClockSecs(self) -> int:
        return self.raw[4]

    @ClockSecs.setter
    def ClockSecs(self, value: int) -> None:
        self.raw[4] = value & 0xFF

    # Byte 5
    @property
    def ClockMins(self) -> int:
        return self.raw[5]

    @ClockMins.setter
    def ClockMins(self, value: int) -> None:
        self.raw[5] = value & 0xFF

    # Byte 6
    @property
    def ClockHrs(self) -> int:
        return self.raw[6]

    @ClockHrs.setter
    def ClockHrs(self, value: int) -> None:
        self.raw[6] = value & 0xFF

    # Byte 7-9  (Timer times?)
    # Unused

    # Byte 10
    @property
    def Turbo(self) -> int:
        return (self.raw[10] >> 3) & 0x01

    @Turbo.setter
    def Turbo(self, value: bool) -> None:
        if value:
            self.raw[10] |= 0x08
        else:
            self.raw[10] &= 0xF7

    @property
    def EnableStartTimer(self) -> int:
        return (self.raw[10] >> 4) & 0x01

    @EnableStartTimer.setter
    def EnableStartTimer(self, value: bool) -> None:
        if value:
            self.raw[10] |= 0x10
        else:
            self.raw[10] &= 0xEF

    @property
    def EnableStopTimer(self) -> int:
        return (self.raw[10] >> 5) & 0x01

    @EnableStopTimer.setter
    def EnableStopTimer(self, value: bool) -> None:
        if value:
            self.raw[10] |= 0x20
        else:
            self.raw[10] &= 0xDF

    @property
    def Sleep(self) -> int:
        return (self.raw[10] >> 6) & 0x01

    @Sleep.setter
    def Sleep(self, value: bool) -> None:
        if value:
            self.raw[10] |= 0x40
        else:
            self.raw[10] &= 0xBF


## Send a SanyoAc88 formatted message.
## Status: ALPHA / Completely untested.
## @param[in] data An array of bytes containing the IR command.
## @warning data's bit order may change. It is not yet confirmed.
## @param[in] nbytes Nr. of bytes of data in the array.
## @param[in] repeat Nr. of times the message is to be repeated.
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/1503
## ir_Sanyo.cpp:687-696
def sendSanyoAc88(
    data: List[int], nbytes: int = kSanyoAc88StateLength, repeat: int = kSanyoAc88MinRepeat
) -> List[int]:
    from app.core.ir_protocols.ir_send import sendGeneric

    all_timings = []
    # (Header + Data + Footer) per repeat
    for r in range(repeat + 1):
        timings = sendGeneric(
            headermark=kSanyoAc88HdrMark,
            headerspace=kSanyoAc88HdrSpace,
            onemark=kSanyoAc88BitMark,
            onespace=kSanyoAc88OneSpace,
            zeromark=kSanyoAc88BitMark,
            zerospace=kSanyoAc88ZeroSpace,
            footermark=kSanyoAc88BitMark,
            gap=kSanyoAc88Gap,
            dataptr=data,
            nbytes=nbytes,
            MSBfirst=False,
        )
        all_timings.extend(timings)
        if r < repeat:
            all_timings.append(100000)  # kDefaultMessageGap

    all_timings.append(100000)  # Make a guess at a post message gap.
    return all_timings


## Decode the supplied SanyoAc88 message.
## Status: ALPHA / Untested.
## @param[in,out] results Ptr to the data to decode & where to store the decode
## @warning data's bit order may change. It is not yet confirmed.
## @param[in] offset The starting index to use when attempting to decode the
##   raw data. Typically/Defaults to kStartOffset.
## @param[in] nbits The number of data bits to expect.
## @param[in] strict Flag indicating if we should perform strict matching.
## @return A boolean. True if it can decode it, false if it can't.
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/1503
## ir_Sanyo.cpp:710-745
def decodeSanyoAc88(
    results, offset: int = 1, nbits: int = kSanyoAc88Bits, strict: bool = True
) -> bool:
    from app.core.ir_protocols.ir_recv import matchGeneric, kMarkExcess

    if strict and nbits != kSanyoAc88Bits:
        return False

    used = 0
    # Compliance
    expected_repeats = kSanyoAc88MinRepeat if strict else 0

    # Handle the expected nr of repeats.
    for r in range(expected_repeats + 1):
        # Header + Data + Footer
        used = matchGeneric(
            data_ptr=results.rawbuf[offset:],
            result_ptr=results.state,
            remaining=results.rawlen - offset,
            nbits=nbits,
            hdrmark=kSanyoAc88HdrMark,
            hdrspace=kSanyoAc88HdrSpace,
            onemark=kSanyoAc88BitMark,
            onespace=kSanyoAc88OneSpace,
            zeromark=kSanyoAc88BitMark,
            zerospace=kSanyoAc88ZeroSpace,
            footermark=kSanyoAc88BitMark,
            # Expect an inter-message gap, or just the end of msg?
            footerspace=kSanyoAc88Gap if r < expected_repeats else 100000,
            atleast=(r == expected_repeats),
            tolerance=25 + kSanyoAc88ExtraTolerance,
            excess=kMarkExcess,
            MSBfirst=False,
        )
        if not used:
            return False  # No match!
        offset += used

    # Success
    results.decode_type = "SANYO_AC88"
    results.bits = nbits
    # No need to record the state as we stored it as we decoded it.
    # As we use result->state, we don't record value, address, or command as it
    # is a union data type.
    return True


## Class for handling detailed Sanyo A/C 88-bit messages.
## Direct translation from C++ IRSanyoAc88 class
## ir_Sanyo.h:229-284
class IRSanyoAc88:
    ## Class Constructor
    ## ir_Sanyo.cpp:752-754
    def __init__(self) -> None:
        self._: SanyoAc88Protocol = SanyoAc88Protocol()
        self.stateReset()

    ## Reset the state of the remote to a known good state/sequence.
    ## @see https://docs.google.com/spreadsheets/d/1dYfLsnYvpjV-SgO8pdinpfuBIpSzm8Q1R5SabrLeskw/edit?ts=5f0190a5#gid=1050142776&range=A2:B2
    ## ir_Sanyo.cpp:758-762
    def stateReset(self) -> None:
        kReset = [0xAA, 0x55, 0xA0, 0x16, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x10]
        self._.raw = kReset.copy()

    ## Get a PTR to the internal state/code for this protocol with all integrity
    ##   checks passing.
    ## @return PTR to a code for this protocol based on the current internal state.
    ## ir_Sanyo.cpp:778-780
    def getRaw(self) -> List[int]:
        return self._.raw

    ## Set the internal state from a valid code for this protocol.
    ## @param[in] newState A valid code for this protocol.
    ## ir_Sanyo.cpp:784-786
    def setRaw(self, newState: List[int]) -> None:
        self._.raw = newState[:kSanyoAc88StateLength].copy()

    ## Set the requested power state of the A/C to on.
    ## ir_Sanyo.cpp:789
    def on(self) -> None:
        self.setPower(True)

    ## Set the requested power state of the A/C to off.
    ## ir_Sanyo.cpp:792
    def off(self) -> None:
        self.setPower(False)

    ## Change the power setting.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## ir_Sanyo.cpp:796
    def setPower(self, on: bool) -> None:
        self._.Power = on

    ## Get the value of the current power setting.
    ## @return true, the setting is on. false, the setting is off.
    ## ir_Sanyo.cpp:800
    def getPower(self) -> bool:
        return bool(self._.Power)

    ## Get the operating mode setting of the A/C.
    ## @return The current operating mode setting.
    ## ir_Sanyo.cpp:804
    def getMode(self) -> int:
        return self._.Mode

    ## Set the operating mode of the A/C.
    ## @param[in] mode The desired operating mode.
    ## @note If we get an unexpected mode, default to AUTO.
    ## ir_Sanyo.cpp:809-821
    def setMode(self, mode: int) -> None:
        if mode in [
            kSanyoAc88Auto,
            kSanyoAc88FeelCool,
            kSanyoAc88Cool,
            kSanyoAc88FeelHeat,
            kSanyoAc88Heat,
            kSanyoAc88Fan,
        ]:
            self._.Mode = mode
        else:
            self._.Mode = kSanyoAc88Auto

    ## Convert a stdAc::opmode_t enum into its native mode.
    ## @param[in] mode The enum to be converted.
    ## @return The native equivalent of the enum.
    ## ir_Sanyo.cpp:826-833
    @staticmethod
    def convertMode(mode: str) -> int:
        if mode == "cool":
            return kSanyoAc88Cool
        elif mode == "heat":
            return kSanyoAc88Heat
        elif mode == "fan":
            return kSanyoAc88Fan
        else:
            return kSanyoAc88Auto

    ## Convert a native mode into its stdAc equivalent.
    ## @param[in] mode The native setting to be converted.
    ## @return The stdAc equivalent of the native setting.
    ## ir_Sanyo.cpp:838-851
    @staticmethod
    def toCommonMode(mode: int) -> str:
        if mode in [kSanyoAc88FeelCool, kSanyoAc88Cool]:
            return "cool"
        elif mode in [kSanyoAc88FeelHeat, kSanyoAc88Heat]:
            return "heat"
        elif mode == kSanyoAc88Fan:
            return "fan"
        else:
            return "auto"

    ## Set the desired temperature.
    ## @param[in] degrees The temperature in degrees celsius.
    ## ir_Sanyo.cpp:855-858
    def setTemp(self, degrees: int) -> None:
        temp = max(kSanyoAc88TempMin, degrees)
        self._.Temp = min(kSanyoAc88TempMax, temp)

    ## Get the current desired temperature setting.
    ## @return The current setting for temp. in degrees celsius.
    ## ir_Sanyo.cpp:862
    def getTemp(self) -> int:
        return self._.Temp

    ## Set the speed of the fan.
    ## @param[in] speed The desired setting.
    ## ir_Sanyo.cpp:866
    def setFan(self, speed: int) -> None:
        self._.Fan = speed

    ## Get the current fan speed setting.
    ## @return The current fan speed/mode.
    ## ir_Sanyo.cpp:870
    def getFan(self) -> int:
        return self._.Fan

    ## Convert a stdAc::fanspeed_t enum into it's native speed.
    ## @param[in] speed The enum to be converted.
    ## @return The native equivalent of the enum.
    ## ir_Sanyo.cpp:875-884
    @staticmethod
    def convertFan(speed: str) -> int:
        if speed in ["min", "low"]:
            return kSanyoAc88FanLow
        elif speed == "medium":
            return kSanyoAc88FanMedium
        elif speed in ["high", "max"]:
            return kSanyoAc88FanHigh
        else:
            return kSanyoAc88FanAuto

    ## Get the current clock time.
    ## @return The time as the nr. of minutes past midnight.
    ## ir_Sanyo.cpp:888-890
    def getClock(self) -> int:
        return self._.ClockHrs * 60 + self._.ClockMins

    ## Set the current clock time.
    ## @param[in] mins_since_midnight The time as nr. of minutes past midnight.
    ## ir_Sanyo.cpp:894-900
    def setClock(self, mins_since_midnight: int) -> None:
        mins = min(mins_since_midnight, 23 * 60 + 59)
        self._.ClockMins = mins % 60
        self._.ClockHrs = mins // 60
        self._.ClockSecs = 0

    ## Convert a native fan speed into its stdAc equivalent.
    ## @param[in] spd The native setting to be converted.
    ## @return The stdAc equivalent of the native setting.
    ## ir_Sanyo.cpp:905-912
    @staticmethod
    def toCommonFanSpeed(spd: int) -> str:
        if spd == kSanyoAc88FanHigh:
            return "high"
        elif spd == kSanyoAc88FanMedium:
            return "medium"
        elif spd == kSanyoAc88FanLow:
            return "low"
        else:
            return "auto"

    ## Change the SwingV setting.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## ir_Sanyo.cpp:916
    def setSwingV(self, on: bool) -> None:
        self._.SwingV = on

    ## Get the value of the current SwingV setting.
    ## @return true, the setting is on. false, the setting is off.
    ## ir_Sanyo.cpp:920
    def getSwingV(self) -> bool:
        return bool(self._.SwingV)

    ## Change the Turbo setting.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## ir_Sanyo.cpp:924
    def setTurbo(self, on: bool) -> None:
        self._.Turbo = on

    ## Get the value of the current Turbo setting.
    ## @return true, the setting is on. false, the setting is off.
    ## ir_Sanyo.cpp:928
    def getTurbo(self) -> bool:
        return bool(self._.Turbo)

    ## Change the Filter setting.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## ir_Sanyo.cpp:932
    def setFilter(self, on: bool) -> None:
        self._.Filter = on

    ## Get the value of the current Filter setting.
    ## @return true, the setting is on. false, the setting is off.
    ## ir_Sanyo.cpp:936
    def getFilter(self) -> bool:
        return bool(self._.Filter)

    ## Change the Sleep setting.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## ir_Sanyo.cpp:940
    def setSleep(self, on: bool) -> None:
        self._.Sleep = on

    ## Get the value of the current Sleep setting.
    ## @return true, the setting is on. false, the setting is off.
    ## ir_Sanyo.cpp:944
    def getSleep(self) -> bool:
        return bool(self._.Sleep)

    ## Convert the current internal state into its stdAc::state_t equivalent.
    ## @return The stdAc equivalent of the native settings.
    ## ir_Sanyo.cpp:948-970
    def toCommon(self) -> dict:
        result = {}
        result["protocol"] = "SANYO_AC88"
        result["model"] = -1  # Not supported.
        result["power"] = self.getPower()
        result["mode"] = IRSanyoAc88.toCommonMode(self._.Mode)
        result["celsius"] = True
        result["degrees"] = self.getTemp()
        result["fanspeed"] = IRSanyoAc88.toCommonFanSpeed(self._.Fan)
        result["swingv"] = "auto" if self._.SwingV else "off"
        result["filter"] = bool(self._.Filter)
        result["turbo"] = bool(self._.Turbo)
        result["sleep"] = 0 if self._.Sleep else -1
        result["clock"] = self.getClock()
        # Not supported.
        result["swingh"] = "off"
        result["econo"] = False
        result["light"] = False
        result["quiet"] = False
        result["beep"] = False
        result["clean"] = False
        return result

    ## Convert the current internal state into a human readable string.
    ## @return A human readable string.
    ## ir_Sanyo.cpp:974-989
    def toString(self) -> str:
        result = ""
        result += f"Power: {'On' if self.getPower() else 'Off'}, "
        result += f"Mode: {IRSanyoAc88.toCommonMode(self._.Mode)}, "
        result += f"Temp: {self.getTemp()}C, "
        result += f"Fan: {IRSanyoAc88.toCommonFanSpeed(self._.Fan)}, "
        result += f"Swing(V): {'On' if self._.SwingV else 'Off'}, "
        result += f"Turbo: {'On' if self._.Turbo else 'Off'}, "
        result += f"Sleep: {'On' if self._.Sleep else 'Off'}, "
        result += f"Clock: {self.getClock() // 60:02d}:{self.getClock() % 60:02d}"
        return result


## Send a SanyoAc152 formatted message.
## Status: BETA / Probably works.
## @param[in] data An array of bytes containing the IR command.
## @warning data's bit order may change. It is not yet confirmed.
## @param[in] nbytes Nr. of bytes of data in the array.
## @param[in] repeat Nr. of times the message is to be repeated.
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/1826
## ir_Sanyo.cpp:999-1008
def sendSanyoAc152(
    data: List[int], nbytes: int = kSanyoAc152StateLength, repeat: int = 0
) -> List[int]:
    from app.core.ir_protocols.ir_send import sendGeneric

    all_timings = []
    # (Header + Data + Footer) per repeat
    for r in range(repeat + 1):
        timings = sendGeneric(
            headermark=kSanyoAc152HdrMark,
            headerspace=kSanyoAc152HdrSpace,
            onemark=kSanyoAc152BitMark,
            onespace=kSanyoAc152OneSpace,
            zeromark=kSanyoAc152BitMark,
            zerospace=kSanyoAc152ZeroSpace,
            footermark=kSanyoAc152BitMark,
            gap=100000,  # kDefaultMessageGap
            dataptr=data,
            nbytes=nbytes,
            MSBfirst=False,
        )
        all_timings.extend(timings)

    all_timings.append(100000)  # Make a guess at a post message gap.
    return all_timings


## Decode the supplied SanyoAc152 message.
## Status: BETA / Probably works.
## @param[in,out] results Ptr to the data to decode & where to store the decode
## @warning data's bit order may change. It is not yet confirmed.
## @param[in] offset The starting index to use when attempting to decode the
##   raw data. Typically/Defaults to kStartOffset.
## @param[in] nbits The number of data bits to expect.
## @param[in] strict Flag indicating if we should perform strict matching.
## @return A boolean. True if it can decode it, false if it can't.
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/1503
## ir_Sanyo.cpp:1022-1046
def decodeSanyoAc152(
    results, offset: int = 1, nbits: int = kSanyoAc152Bits, strict: bool = True
) -> bool:
    from app.core.ir_protocols.ir_recv import matchGeneric, kMarkExcess

    if strict and nbits != kSanyoAc152Bits:
        return False

    # Header + Data + Footer
    if not matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_ptr=results.state,
        remaining=results.rawlen - offset,
        nbits=nbits,
        hdrmark=kSanyoAc152HdrMark,
        hdrspace=kSanyoAc152HdrSpace,
        onemark=kSanyoAc152BitMark,
        onespace=kSanyoAc152OneSpace,
        zeromark=kSanyoAc152BitMark,
        zerospace=kSanyoAc152ZeroSpace,
        footermark=kSanyoAc152BitMark,
        footerspace=100000,  # Just a guess.
        atleast=False,
        tolerance=25 + kSanyoAc152ExtraTolerance,
        excess=kMarkExcess,
        MSBfirst=False,
    ):
        return False  # No match!

    # Success
    results.decode_type = "SANYO_AC152"
    results.bits = nbits
    # No need to record the state as we stored it as we decoded it.
    # As we use result->state, we don't record value, address, or command as it
    # is a union data type.
    return True
