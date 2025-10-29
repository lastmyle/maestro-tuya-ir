# Copyright 2022 Nico Thien
# Copyright 2022 David Conran
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Support for Bosch A/C protocol
## Direct translation from IRremoteESP8266 ir_Bosch.cpp and ir_Bosch.h

from typing import List

# Supports:
#   Brand: Bosch,  Model: CL3000i-Set 26 E A/C
#   Brand: Bosch,  Model: RG10A(G2S)BGEF remote

# Ref: https://github.com/crankyoldgit/IRremoteESP8266/issues/1787

# Constants - Timing values (from ir_Bosch.h lines 31-37)
kBoschHdrMark = 4366
kBoschBitMark = 502
kBoschHdrSpace = 4415
kBoschOneSpace = 1645
kBoschZeroSpace = 571
kBoschFooterSpace = 5235
kBoschFreq = 38000  # Hz. (Guessing the most common frequency.)

# Section constants (from ir_Bosch.h lines 38-39)
kBosch144NrOfSections = 3
kBosch144BytesPerSection = 6

# State length constants
kBosch144StateLength = 18  # 3 sections * 6 bytes per section

# Modes - Bit[0] to Section 3    Bit[1-2] to Section 1 (from ir_Bosch.h lines 50-56)
#                    ModeS3                   ModeS1
kBosch144Cool = 0b000
kBosch144Dry = 0b011
kBosch144Auto = 0b101
kBosch144Heat = 0b110
kBosch144Fan = 0b010

# Fan Control - Bit[0-5] to Section 3    Bit[6-8] to Section 1 (from ir_Bosch.h lines 58-66)
#                         FanS3                    FanS1
kBosch144Fan20 = 0b111001010
kBosch144Fan40 = 0b100010100
kBosch144Fan60 = 0b010011110
kBosch144Fan80 = 0b001101000
kBosch144Fan100 = 0b001110010
kBosch144FanAuto = 0b101110011
kBosch144FanAuto0 = 0b000110011

# Temperature (from ir_Bosch.h lines 68-88)
kBosch144TempMin = 16  # Celsius
kBosch144TempMax = 30  # Celsius
kBosch144TempRange = kBosch144TempMax - kBosch144TempMin + 1
kBosch144TempMap = [
    0b00001,  # 16C      # Bit[0] to Section 3    Bit[1-4] to Section 1
    0b00000,  # 17C      #           TempS3                   TempS1
    0b00010,  # 18c
    0b00110,  # 19C
    0b00100,  # 20C
    0b01100,  # 21C
    0b01110,  # 22C
    0b01010,  # 23C
    0b01000,  # 24C
    0b11000,  # 25C
    0b11010,  # 26C
    0b10010,  # 27C
    0b10000,  # 28C
    0b10100,  # 29C
    0b10110,  # 30C
]

# "OFF" is a 96bit-message    the same as Coolix protocol (from ir_Bosch.h lines 90-92)
kBosch144Off = [0xB2, 0x4D, 0x7B, 0x84, 0xE0, 0x1F, 0xB2, 0x4D, 0x7B, 0x84, 0xE0, 0x1F]

# On, 25C, Mode: Auto (from ir_Bosch.h lines 94-98)
kBosch144DefaultState = [
    0xB2,
    0x4D,
    0x1F,
    0xE0,
    0xC8,
    0x37,
    0xB2,
    0x4D,
    0x1F,
    0xE0,
    0xC8,
    0x37,
    0xD5,
    0x65,
    0x00,
    0x00,
    0x00,
    0x3A,
]


def sumBytes(data: List[int], length: int) -> int:
    """
    Sum all bytes in the array up to length.
    Helper function for checksum calculation.
    """
    result = 0
    for i in range(length):
        result += data[i]
    return result & 0xFF


## Native representation of a Bosch 144 A/C message.
## This is a direct translation of the C++ union/struct (from ir_Bosch.h lines 100-135)
class Bosch144Protocol:
    def __init__(self):
        # The state array (18 bytes for Bosch144)
        self.raw = [0] * kBosch144StateLength

    # Section 1 = Section 2 (bytes 0-5)
    # Byte 0 - Fixed value 0b10110010 / 0xB2.

    # Byte 1
    @property
    def InnvertS1_1(self) -> int:
        return self.raw[1]

    @InnvertS1_1.setter
    def InnvertS1_1(self, value: int) -> None:
        self.raw[1] = value & 0xFF

    # Byte 2
    @property
    def FanS1(self) -> int:
        return (self.raw[2] >> 5) & 0x07

    @FanS1.setter
    def FanS1(self, value: int) -> None:
        self.raw[2] = (self.raw[2] & 0x1F) | ((value & 0x07) << 5)

    # Byte 3
    @property
    def InnvertS1_2(self) -> int:
        return self.raw[3]

    @InnvertS1_2.setter
    def InnvertS1_2(self, value: int) -> None:
        self.raw[3] = value & 0xFF

    # Byte 4
    @property
    def ModeS1(self) -> int:
        return (self.raw[4] >> 2) & 0x03

    @ModeS1.setter
    def ModeS1(self, value: int) -> None:
        self.raw[4] = (self.raw[4] & 0xF3) | ((value & 0x03) << 2)

    @property
    def TempS1(self) -> int:
        return (self.raw[4] >> 4) & 0x0F

    @TempS1.setter
    def TempS1(self, value: int) -> None:
        self.raw[4] = (self.raw[4] & 0x0F) | ((value & 0x0F) << 4)

    # Byte 5
    @property
    def InnvertS1_3(self) -> int:
        return self.raw[5]

    @InnvertS1_3.setter
    def InnvertS1_3(self, value: int) -> None:
        self.raw[5] = value & 0xFF

    # Section 2 = Section 1 (bytes 6-11)
    # Byte 6 - Fixed value 0b10110010 / 0xB2.

    # Byte 7
    @property
    def InnvertS2_1(self) -> int:
        return self.raw[7]

    @InnvertS2_1.setter
    def InnvertS2_1(self, value: int) -> None:
        self.raw[7] = value & 0xFF

    # Byte 8
    @property
    def FanS2(self) -> int:
        return (self.raw[8] >> 5) & 0x07

    @FanS2.setter
    def FanS2(self, value: int) -> None:
        self.raw[8] = (self.raw[8] & 0x1F) | ((value & 0x07) << 5)

    # Byte 9
    @property
    def InnvertS2_2(self) -> int:
        return self.raw[9]

    @InnvertS2_2.setter
    def InnvertS2_2(self, value: int) -> None:
        self.raw[9] = value & 0xFF

    # Byte 10
    @property
    def ModeS2(self) -> int:
        return (self.raw[10] >> 2) & 0x03

    @ModeS2.setter
    def ModeS2(self, value: int) -> None:
        self.raw[10] = (self.raw[10] & 0xF3) | ((value & 0x03) << 2)

    @property
    def TempS2(self) -> int:
        return (self.raw[10] >> 4) & 0x0F

    @TempS2.setter
    def TempS2(self, value: int) -> None:
        self.raw[10] = (self.raw[10] & 0x0F) | ((value & 0x0F) << 4)

    # Byte 11
    @property
    def InnvertS2_3(self) -> int:
        return self.raw[11]

    @InnvertS2_3.setter
    def InnvertS2_3(self, value: int) -> None:
        self.raw[11] = value & 0xFF

    # Section 3 (bytes 12-17)
    # Byte 12 - Fixed value 0b11010101 / 0xD5

    # Byte 13
    @property
    def ModeS3(self) -> int:
        return self.raw[13] & 0x01

    @ModeS3.setter
    def ModeS3(self, value: int) -> None:
        self.raw[13] = (self.raw[13] & 0xFE) | (value & 0x01)

    @property
    def FanS3(self) -> int:
        return (self.raw[13] >> 1) & 0x3F

    @FanS3.setter
    def FanS3(self, value: int) -> None:
        self.raw[13] = (self.raw[13] & 0x81) | ((value & 0x3F) << 1)

    # Byte 14
    @property
    def Quiet(self) -> int:
        return (self.raw[14] >> 7) & 0x01

    @Quiet.setter
    def Quiet(self, value: bool) -> None:
        if value:
            self.raw[14] |= 0x80
        else:
            self.raw[14] &= 0x7F

    # Byte 15
    @property
    def TempS3(self) -> int:
        return (self.raw[15] >> 4) & 0x01

    @TempS3.setter
    def TempS3(self, value: int) -> None:
        self.raw[15] = (self.raw[15] & 0xEF) | ((value & 0x01) << 4)

    # Byte 16 - Unknown

    # Byte 17
    @property
    def ChecksumS3(self) -> int:
        return self.raw[17]

    @ChecksumS3.setter
    def ChecksumS3(self, value: int) -> None:
        self.raw[17] = value & 0xFF


## Send a Bosch 144-bit / 18-byte message (96-bit message are also possible)
## Status: BETA / Probably Working.
## @param[in] data The message to be sent.
## @param[in] nbytes The number of bytes of message to be sent.
## @param[in] repeat The number of times the command is to be repeated.
## Direct translation from IRremoteESP8266 IRsend::sendBosch144 (ir_Bosch.cpp lines 11-34)
def sendBosch144(data: List[int], nbytes: int, repeat: int = 0) -> List[int]:
    """
    Send a Bosch 144-bit / 18-byte message (96-bit message are also possible)
    EXACT translation from IRremoteESP8266 IRsend::sendBosch144

    Returns timing array instead of transmitting via hardware.
    """
    # nbytes is required to be a multiple of kBosch144BytesPerSection. (from ir_Bosch.cpp line 18)
    if nbytes % kBosch144BytesPerSection != 0:
        return []

    # Import here to avoid circular import
    from app.core.ir_protocols.ir_send import sendGeneric

    all_timings = []

    for r in range(repeat + 1):
        for offset in range(0, nbytes, kBosch144BytesPerSection):
            # Section Header + Data + Footer (from ir_Bosch.cpp lines 25-31)
            section_timings = sendGeneric(
                headermark=kBoschHdrMark,
                headerspace=kBoschHdrSpace,
                onemark=kBoschBitMark,
                onespace=kBoschOneSpace,
                zeromark=kBoschBitMark,
                zerospace=kBoschZeroSpace,
                footermark=kBoschBitMark,
                gap=kBoschFooterSpace,
                dataptr=data[offset : offset + kBosch144BytesPerSection],
                nbytes=kBosch144BytesPerSection,
                frequency=kBoschFreq,
                MSBfirst=True,
                repeat=0,
                dutycycle=50,
            )
            all_timings.extend(section_timings)
        # space(kDefaultMessageGap);  // Complete guess (from ir_Bosch.cpp line 32)

    return all_timings


## Class for handling detailed Bosch144 A/C messages.
## Direct translation from C++ IRBosch144AC class (from ir_Bosch.h lines 140-191)
class IRBosch144AC:
    ## Class Constructor
    ## @param[in] pin GPIO to be used when sending. (Not used in Python)
    ## @param[in] inverted Is the output signal to be inverted? (Not used in Python)
    ## @param[in] use_modulation Is frequency modulation to be used? (Not used in Python)
    ## Direct translation from ir_Bosch.cpp lines 38-44
    def __init__(self) -> None:
        self._: Bosch144Protocol = Bosch144Protocol()
        self.powerFlag: bool = False
        self.stateReset()

    ## Reset the internal state to a fixed known good state.
    ## Direct translation from ir_Bosch.cpp lines 46-50
    def stateReset(self) -> None:
        self.setRaw(kBosch144DefaultState, kBosch144StateLength)
        self.setPower(True)

    ## Get a copy of the internal state as a valid code for this protocol.
    ## @return A valid code for this protocol based on the current internal state.
    ## Direct translation from ir_Bosch.cpp lines 67-73
    def getRaw(self) -> List[int]:
        self.setInvertBytes()
        self.setCheckSumS3()
        return self._.raw

    ## Set the internal state from a valid code for this protocol.
    ## @param[in] new_code A valid code for this protocol.
    ## @param[in] length Size of the array being passed in in bytes.
    ## Direct translation from ir_Bosch.cpp lines 75-87
    def setRaw(self, new_code: List[int], length: int = kBosch144StateLength) -> None:
        len_copy = min(length, kBosch144StateLength)
        lenOff = len(kBosch144Off)
        # Is it an off message? (from ir_Bosch.cpp lines 81-82)
        if new_code[: min(lenOff, len_copy)] == kBosch144Off[: min(lenOff, len_copy)]:
            self.setPower(False)  # It is.
        else:
            self.setPower(True)
        for i in range(len_copy):
            self._.raw[i] = new_code[i]

    ## Set the power setting.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Bosch.cpp lines 89-91
    def setPower(self, on: bool) -> None:
        self.powerFlag = on

    ## Get the value of the current power setting.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Bosch.cpp lines 93-95
    def getPower(self) -> bool:
        return self.powerFlag

    ## Set the temperature raw value.
    ## @param[in] code The raw temperature code.
    ## Direct translation from ir_Bosch.cpp lines 97-100
    def setTempRaw(self, code: int) -> None:
        self._.TempS1 = self._.TempS2 = code >> 1  # save 4 bits in S1 and S2
        self._.TempS3 = code & 1  # save 1 bit in Section3

    ## Set the temperature.
    ## @param[in] degrees The temperature in degrees celsius.
    ## Direct translation from ir_Bosch.cpp lines 102-108
    def setTemp(self, degrees: int) -> None:
        temp = max(kBosch144TempMin, degrees)
        temp = min(kBosch144TempMax, temp)
        self.setTempRaw(kBosch144TempMap[temp - kBosch144TempMin])

    ## Get the current temperature setting.
    ## @return The current setting for temp. in degrees celsius.
    ## Direct translation from ir_Bosch.cpp lines 110-119
    def getTemp(self) -> int:
        temp = (self._.TempS1 << 1) + self._.TempS3
        retemp = 25
        for i in range(kBosch144TempRange):
            if temp == kBosch144TempMap[i]:
                retemp = kBosch144TempMin + i
        return retemp

    ## Set the speed of the fan.
    ## @param[in] speed The desired setting.
    ## Direct translation from ir_Bosch.cpp lines 121-126
    def setFan(self, speed: int) -> None:
        self._.FanS1 = self._.FanS2 = speed >> 6  # save 3 bits in S1 and S2
        self._.FanS3 = speed & 0b111111  # save 6 bits in Section3

    ## Get the current fan speed setting.
    ## @return The current fan speed.
    ## Direct translation from ir_Bosch.cpp lines 128-130
    def getFan(self) -> int:
        return (self._.FanS1 << 6) + self._.FanS3

    ## Set the desired operation mode.
    ## @param[in] mode The desired operation mode.
    ## Direct translation from ir_Bosch.cpp lines 132-141
    def setMode(self, mode: int) -> None:
        self._.ModeS1 = self._.ModeS2 = mode >> 1  # save 2 bits in S1 and S2
        self._.ModeS3 = mode & 0b1  # save 1 bit in Section3
        if mode == kBosch144Auto or mode == kBosch144Dry:
            self._.FanS1 = self._.FanS2 = 0b000  # save 3 bits in S1 and S2
            self._.FanS3 = kBosch144FanAuto0  # save 6 bits in Section3

    ## Get the operating mode setting of the A/C.
    ## @return The current operating mode setting.
    ## Direct translation from ir_Bosch.cpp lines 143-145
    def getMode(self) -> int:
        return (self._.ModeS1 << 1) + self._.ModeS3

    ## Set the Quiet mode of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Bosch.cpp lines 147-152
    def setQuiet(self, on: bool) -> None:
        self._.Quiet = on  # save 1 bit in Section3
        self.setFan(kBosch144FanAuto)  # set Fan -> Auto

    ## Get the Quiet mode of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Bosch.cpp line 156
    def getQuiet(self) -> bool:
        return bool(self._.Quiet)

    ## Convert a stdAc::opmode_t enum into its native mode.
    ## @param[in] mode The enum to be converted.
    ## @return The native equivalent of the enum.
    ## Direct translation from ir_Bosch.cpp lines 158-174
    @staticmethod
    def convertMode(mode: int) -> int:
        # stdAc::opmode_t values (approximated):
        # kCool = 1, kHeat = 2, kDry = 3, kFan = 4, kAuto = 0
        if mode == 1:  # kCool
            return kBosch144Cool
        elif mode == 2:  # kHeat
            return kBosch144Heat
        elif mode == 3:  # kDry
            return kBosch144Dry
        elif mode == 4:  # kFan
            return kBosch144Fan
        else:
            return kBosch144Auto

    ## Convert a stdAc::fanspeed_t enum into it's native speed.
    ## @param[in] speed The enum to be converted.
    ## @return The native equivalent of the enum.
    ## Direct translation from ir_Bosch.cpp lines 176-194
    @staticmethod
    def convertFan(speed: int) -> int:
        # stdAc::fanspeed_t values (approximated):
        # kMin = 1, kLow = 2, kMedium = 3, kHigh = 4, kMax = 5, kAuto = 0
        if speed == 1:  # kMin
            return kBosch144Fan20
        elif speed == 2:  # kLow
            return kBosch144Fan40
        elif speed == 3:  # kMedium
            return kBosch144Fan60
        elif speed == 4:  # kHigh
            return kBosch144Fan80
        elif speed == 5:  # kMax
            return kBosch144Fan100
        else:
            return kBosch144FanAuto

    ## Convert a native mode into its stdAc equivalent.
    ## @param[in] mode The native setting to be converted.
    ## @return The stdAc equivalent of the native setting.
    ## Direct translation from ir_Bosch.cpp lines 196-207
    @staticmethod
    def toCommonMode(mode: int) -> int:
        if mode == kBosch144Cool:
            return 1  # stdAc::opmode_t::kCool
        elif mode == kBosch144Heat:
            return 2  # stdAc::opmode_t::kHeat
        elif mode == kBosch144Dry:
            return 3  # stdAc::opmode_t::kDry
        elif mode == kBosch144Fan:
            return 4  # stdAc::opmode_t::kFan
        else:
            return 0  # stdAc::opmode_t::kAuto

    ## Convert a native fan speed into its stdAc equivalent.
    ## @param[in] speed The native setting to be converted.
    ## @return The stdAc equivalent of the native setting.
    ## Direct translation from ir_Bosch.cpp lines 209-221
    @staticmethod
    def toCommonFanSpeed(speed: int) -> int:
        if speed == kBosch144Fan100:
            return 5  # stdAc::fanspeed_t::kMax
        elif speed == kBosch144Fan80:
            return 4  # stdAc::fanspeed_t::kHigh
        elif speed == kBosch144Fan60:
            return 3  # stdAc::fanspeed_t::kMedium
        elif speed == kBosch144Fan40:
            return 2  # stdAc::fanspeed_t::kLow
        elif speed == kBosch144Fan20:
            return 1  # stdAc::fanspeed_t::kMin
        else:
            return 0  # stdAc::fanspeed_t::kAuto

    ## Convert the current internal state into its stdAc::state_t equivalent.
    ## @return The stdAc equivalent of the native settings.
    ## Direct translation from ir_Bosch.cpp lines 223-247
    def toCommon(self) -> dict:
        result = {}
        result["protocol"] = "BOSCH144"
        result["power"] = self.getPower()
        result["mode"] = self.toCommonMode(self.getMode())
        result["celsius"] = True
        result["degrees"] = self.getTemp()
        result["fanspeed"] = self.toCommonFanSpeed(self.getFan())
        result["quiet"] = self.getQuiet()
        # Not supported.
        result["model"] = -1
        result["turbo"] = False
        result["swingv"] = 0  # stdAc::swingv_t::kOff
        result["swingh"] = 0  # stdAc::swingh_t::kOff
        result["light"] = False
        result["filter"] = False
        result["econo"] = False
        result["clean"] = False
        result["beep"] = False
        result["clock"] = -1
        result["sleep"] = -1
        return result

    ## Convert the current internal state into a human readable string.
    ## @return A human readable string.
    ## Direct translation from ir_Bosch.cpp lines 249-267
    def toString(self) -> str:
        mode = self.getMode()
        fan = self.toCommonFanSpeed(self.getFan())
        result = ""
        result += "Power: " + ("On" if self.getPower() else "Off") + ", "
        result += "Mode: " + str(mode) + ", "
        result += "Fan: " + str(fan) + ", "
        result += "Temp: " + str(self.getTemp()) + "C, "
        result += "Quiet: " + ("On" if self._.Quiet else "Off")
        return result

    ## Set invert bytes for sections 1 and 2.
    ## Direct translation from ir_Bosch.cpp lines 269-273
    def setInvertBytes(self) -> None:
        for i in range(0, 11, 2):
            self._.raw[i + 1] = ~self._.raw[i] & 0xFF

    ## Calculate and set the checksum for section 3.
    ## Direct translation from ir_Bosch.cpp lines 275-277
    def setCheckSumS3(self) -> None:
        self._.ChecksumS3 = sumBytes(self._.raw[12:], 5)


## Decode the supplied Bosch 144-bit / 18-byte A/C message.
## Status: STABLE / Confirmed Working.
## @param[in,out] results Ptr to the data to decode & where to store the decode result.
## @param[in] offset The starting index to use when attempting to decode the raw data.
## @param[in] nbits The number of data bits to expect.
## @param[in] strict Flag indicating if we should perform strict matching.
## @return A boolean. True if it can decode it, false if it can't.
## Direct translation from IRremoteESP8266 IRrecv::decodeBosch144 (ir_Bosch.cpp lines 279-332)
def decodeBosch144(results, offset: int = 1, nbits: int = 144, strict: bool = True) -> bool:
    """
    Decode a Bosch 144-bit / 18-byte A/C IR message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeBosch144

    This is the ACTUAL C++ decoder function, not a wrapper.
    """
    # Import here to avoid circular imports
    from app.core.ir_protocols.ir_recv import kHeader, kFooter, kMarkExcess, _matchGeneric

    # Can't possibly be a valid BOSCH144 message. (from ir_Bosch.cpp lines 291-293)
    if results.rawlen < 2 * nbits + kBosch144NrOfSections * (kHeader + kFooter) - 1 + offset:
        return False
    if strict and nbits != 144:  # kBosch144Bits
        return False
    if (
        nbits % 8 != 0
    ):  # nbits has to be a multiple of nr. of bits in a byte. (from ir_Bosch.cpp lines 297-298)
        return False
    if nbits % kBosch144NrOfSections != 0:  # (from ir_Bosch.cpp lines 299-300)
        return False

    kSectionBits = nbits // kBosch144NrOfSections
    kSectionBytes = kSectionBits // 8
    kNBytes = kSectionBytes * kBosch144NrOfSections

    # Capture each section individually (from ir_Bosch.cpp lines 304-320)
    for pos in range(0, kNBytes, kSectionBytes):
        section = pos // kSectionBytes
        # Section Header + Section Data + Section Footer (from ir_Bosch.cpp lines 309-317)
        used = _matchGeneric(
            data_ptr=results.rawbuf[offset:],
            result_bits_ptr=None,
            result_bytes_ptr=results.state[pos:],
            use_bits=False,
            remaining=results.rawlen - offset,
            nbits=kSectionBits,
            hdrmark=kBoschHdrMark,
            hdrspace=kBoschHdrSpace,
            onemark=kBoschBitMark,
            onespace=kBoschOneSpace,
            zeromark=kBoschBitMark,
            zerospace=kBoschZeroSpace,
            footermark=kBoschBitMark,
            footerspace=kBoschFooterSpace,
            atleast=section >= kBosch144NrOfSections - 1,
            tolerance=25,
            excess=kMarkExcess,
            MSBfirst=True,
        )
        if not used:
            return False  # Didn't match.
        offset += used

    # Compliance (from ir_Bosch.cpp line 322)

    # Success (from ir_Bosch.cpp lines 324-329)
    # results.decode_type = decode_type_t::BOSCH144;
    results.bits = nbits
    # No need to record the state as we stored it as we decoded it.
    # As we use result->state, we don't record value, address, or command as it
    # is a union data type.
    return True
