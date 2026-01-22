# Copyright 2018-2019 David Conran
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Support for Hitachi A/C protocols.
## Direct translation from IRremoteESP8266 ir_Hitachi.cpp and ir_Hitachi.h
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/417
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/453
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/973
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/1056
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/1060
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/1134
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/1729
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/1757

# Supports:
#   Brand: Hitachi,  Model: RAS-35THA6 remote
#   Brand: Hitachi,  Model: LT0541-HTA remote  (HITACHI_AC1)
#   Brand: Hitachi,  Model: Series VI A/C (Circa 2007) (HITACHI_AC1)
#   Brand: Hitachi,  Model: RAR-8P2 remote (HITACHI_AC424)
#   Brand: Hitachi,  Model: RAS-AJ25H A/C (HITACHI_AC424)
#   Brand: Hitachi,  Model: PC-LH3B (HITACHI_AC3)
#   Brand: Hitachi,  Model: KAZE-312KSDP A/C (HITACHI_AC1)
#   Brand: Hitachi,  Model: R-LT0541-HTA/Y.K.1.1-1 V2.3 remote (HITACHI_AC1)
#   Brand: Hitachi,  Model: RAS-22NK A/C (HITACHI_AC344)
#   Brand: Hitachi,  Model: RF11T1 remote (HITACHI_AC344)
#   Brand: Hitachi,  Model: RAR-2P2 remote (HITACHI_AC264)
#   Brand: Hitachi,  Model: RAK-25NH5 A/C (HITACHI_AC264)
#   Brand: Hitachi,  Model: RAR-3U3 remote (HITACHI_AC296)
#   Brand: Hitachi,  Model: RAS-70YHA3 A/C (HITACHI_AC296)

from typing import List

# Constants - EXACT translation from IRremoteESP8266 ir_Hitachi.h:25-48
# & ir_Hitachi.cpp:25-48
kHitachiAcFreq = 38000  # Hz.
kHitachiAcHdrMark = 3300
kHitachiAcHdrSpace = 1700
kHitachiAc1HdrMark = 3400
kHitachiAc1HdrSpace = 3400
kHitachiAcBitMark = 400
kHitachiAcOneSpace = 1250
kHitachiAcZeroSpace = 500
kHitachiAcMinGap = 20000  # Minimum gap between messages (~20ms, real-world signals show ~30ms)

# Support for HitachiAc424 protocol (ir_Hitachi.cpp:34-40)
kHitachiAc424LdrMark = 29784  # Leader
kHitachiAc424LdrSpace = 49290  # Leader
kHitachiAc424HdrMark = 3416  # Header
kHitachiAc424HdrSpace = 1604  # Header
kHitachiAc424BitMark = 463
kHitachiAc424OneSpace = 1208
kHitachiAc424ZeroSpace = 372

# Support for HitachiAc3 protocol (ir_Hitachi.cpp:42-47)
kHitachiAc3HdrMark = 3400  # Header
kHitachiAc3HdrSpace = 1660  # Header
kHitachiAc3BitMark = 460
kHitachiAc3OneSpace = 1250
kHitachiAc3ZeroSpace = 410

# State length constants (from IRremoteESP8266.h)
kHitachiAcStateLength = 28
kHitachiAcBits = kHitachiAcStateLength * 8  # 224 bits
kHitachiAc1StateLength = 13
kHitachiAc1Bits = kHitachiAc1StateLength * 8  # 104 bits
kHitachiAc2StateLength = 53
kHitachiAc2Bits = kHitachiAc2StateLength * 8  # 424 bits
kHitachiAc424StateLength = 53
kHitachiAc424Bits = kHitachiAc424StateLength * 8  # 424 bits
kHitachiAc344StateLength = 43
kHitachiAc344Bits = kHitachiAc344StateLength * 8  # 344 bits
kHitachiAc264StateLength = 33
kHitachiAc264Bits = kHitachiAc264StateLength * 8  # 264 bits
kHitachiAc296StateLength = 37
kHitachiAc296Bits = kHitachiAc296StateLength * 8  # 296 bits
kHitachiAc3StateLength = 27
kHitachiAc3Bits = kHitachiAc3StateLength * 8  # 216 bits
kHitachiAc3MinStateLength = 15
kHitachiAc3MinBits = kHitachiAc3MinStateLength * 8  # 120 bits

# HitachiAC constants (EXACT translation from ir_Hitachi.h:76-88)
kHitachiAcAuto = 2
kHitachiAcHeat = 3
kHitachiAcCool = 4
kHitachiAcDry = 5
kHitachiAcFan = 0xC
kHitachiAcFanAuto = 1
kHitachiAcFanLow = 2
kHitachiAcFanMed = 3
kHitachiAcFanHigh = 5
kHitachiAcMinTemp = 16  # 16C
kHitachiAcMaxTemp = 32  # 32C
kHitachiAcAutoTemp = 23  # 23C

# HitachiAc424 & HitachiAc344 Button constants (EXACT translation from ir_Hitachi.h:128-140)
kHitachiAc424ButtonPowerMode = 0x13
kHitachiAc424ButtonFan = 0x42
kHitachiAc424ButtonTempDown = 0x43
kHitachiAc424ButtonTempUp = 0x44
kHitachiAc424ButtonSwingV = 0x81
kHitachiAc424ButtonSwingH = 0x8C
kHitachiAc344ButtonPowerMode = kHitachiAc424ButtonPowerMode
kHitachiAc344ButtonFan = kHitachiAc424ButtonFan
kHitachiAc344ButtonTempDown = kHitachiAc424ButtonTempDown
kHitachiAc344ButtonTempUp = kHitachiAc424ButtonTempUp
kHitachiAc344ButtonSwingV = kHitachiAc424ButtonSwingV
kHitachiAc344ButtonSwingH = kHitachiAc424ButtonSwingH

# HitachiAc424 & HitachiAc344 constants (EXACT translation from ir_Hitachi.h:142-169)
kHitachiAc424MinTemp = 16  # 16C
kHitachiAc424MaxTemp = 32  # 32C
kHitachiAc344MinTemp = kHitachiAc424MinTemp
kHitachiAc344MaxTemp = kHitachiAc424MaxTemp
kHitachiAc424FanTemp = 27  # 27C

kHitachiAc424Fan = 1
kHitachiAc424Cool = 3
kHitachiAc424Dry = 5
kHitachiAc424Heat = 6
kHitachiAc344Fan = kHitachiAc424Fan
kHitachiAc344Cool = kHitachiAc424Cool
kHitachiAc344Dry = kHitachiAc424Dry
kHitachiAc344Heat = kHitachiAc424Heat

kHitachiAc424FanMin = 1
kHitachiAc424FanLow = 2
kHitachiAc424FanMedium = 3
kHitachiAc424FanHigh = 4
kHitachiAc424FanAuto = 5
kHitachiAc424FanMax = 6
kHitachiAc424FanMaxDry = 2
kHitachiAc344FanMin = kHitachiAc424FanMin
kHitachiAc344FanLow = kHitachiAc424FanLow
kHitachiAc344FanMedium = kHitachiAc424FanMedium
kHitachiAc344FanHigh = kHitachiAc424FanHigh
kHitachiAc344FanAuto = kHitachiAc424FanAuto
kHitachiAc344FanMax = kHitachiAc424FanMax

# HitachiAc344 Horizontal Swing (EXACT translation from ir_Hitachi.h:171-176)
kHitachiAc344SwingHAuto = 0  # 0b000
kHitachiAc344SwingHRightMax = 1  # 0b001
kHitachiAc344SwingHRight = 2  # 0b010
kHitachiAc344SwingHMiddle = 3  # 0b011
kHitachiAc344SwingHLeft = 4  # 0b100
kHitachiAc344SwingHLeftMax = 5  # 0b101

# HitachiAc1 Model constants (EXACT translation from ir_Hitachi.h:218-219)
kHitachiAc1Model_A = 0b10
kHitachiAc1Model_B = 0b01

# HitachiAc1 Mode & Fan (EXACT translation from ir_Hitachi.h:222-230)
kHitachiAc1Dry = 0b0010  # 2
kHitachiAc1Fan = 0b0100  # 4
kHitachiAc1Cool = 0b0110  # 6
kHitachiAc1Heat = 0b1001  # 9
kHitachiAc1Auto = 0b1110  # 14
kHitachiAc1FanAuto = 1  # 0b0001
kHitachiAc1FanHigh = 2  # 0b0010
kHitachiAc1FanMed = 4  # 0b0100
kHitachiAc1FanLow = 8  # 0b1000

# HitachiAc1 Temp & Timer constants (EXACT translation from ir_Hitachi.h:233-237)
kHitachiAc1TempSize = 5  # Mask 0b01111100
kHitachiAc1TempDelta = 7
kHitachiAc1TempAuto = 25  # Celsius
kHitachiAc1TimerSize = 16  # Mask 0b1111111111111111

# HitachiAc1 Sleep constants (EXACT translation from ir_Hitachi.h:239-243)
kHitachiAc1SleepOff = 0b000
kHitachiAc1Sleep1 = 0b001
kHitachiAc1Sleep2 = 0b010
kHitachiAc1Sleep3 = 0b011
kHitachiAc1Sleep4 = 0b100

# HitachiAc1 Checksum (EXACT translation from ir_Hitachi.h:245)
kHitachiAc1ChecksumStartByte = 5

# HitachiAc264 constants (EXACT translation from ir_Hitachi.h:282-297)
kHitachiAc264ButtonPowerMode = kHitachiAc424ButtonPowerMode
kHitachiAc264ButtonFan = kHitachiAc424ButtonFan
kHitachiAc264ButtonTempDown = kHitachiAc424ButtonTempDown
kHitachiAc264ButtonTempUp = kHitachiAc424ButtonTempUp
kHitachiAc264ButtonSwingV = kHitachiAc424ButtonSwingV
kHitachiAc264MinTemp = kHitachiAc424MinTemp  # 16C
kHitachiAc264MaxTemp = kHitachiAc424MaxTemp  # 32C
kHitachiAc264Fan = kHitachiAc424Fan
kHitachiAc264Cool = kHitachiAc424Cool
kHitachiAc264Dry = kHitachiAc424Dry
kHitachiAc264Heat = kHitachiAc424Heat
kHitachiAc264FanMin = kHitachiAc424FanMin
kHitachiAc264FanLow = kHitachiAc424FanMin
kHitachiAc264FanMedium = kHitachiAc424FanMedium
kHitachiAc264FanHigh = kHitachiAc424FanHigh
kHitachiAc264FanAuto = kHitachiAc424FanAuto

# HitachiAc296 Mode & Fan (EXACT translation from ir_Hitachi.h:346-359)
kHitachiAc296Cool = 0b0011
kHitachiAc296DryCool = 0b0100
kHitachiAc296Dehumidify = 0b0101
kHitachiAc296Heat = 0b0110
kHitachiAc296Auto = 0b0111
kHitachiAc296AutoDehumidifying = 0b1001
kHitachiAc296QuickLaundry = 0b1010
kHitachiAc296CondensationControl = 0b1100

kHitachiAc296FanSilent = 0b001
kHitachiAc296FanLow = 0b010
kHitachiAc296FanMedium = 0b011
kHitachiAc296FanHigh = 0b100
kHitachiAc296FanAuto = 0b101

# HitachiAc296 Temperature constants (EXACT translation from ir_Hitachi.h:361-363)
kHitachiAc296TempAuto = 1  # Special value for "Auto" op mode.
kHitachiAc296MinTemp = 16
kHitachiAc296MaxTemp = 31  # Max value you can store in 5 bits.

# HitachiAc296 Power constants (EXACT translation from ir_Hitachi.h:365-366)
kHitachiAc296PowerOn = 1
kHitachiAc296PowerOff = 0

# Helper constants from IRrecv.h
kHeader = 1
kFooter = 1
kMarkExcess = 50
kUseDefTol = 0


## Bit manipulation helpers (from IRremoteESP8266 IRutils.h)
def GETBITS8(data: int, offset: int, size: int) -> int:
    """EXACT translation from IRremoteESP8266 IRutils.h"""
    mask = (1 << size) - 1
    return (data >> offset) & mask


def GETBITS16(data: int, offset: int, size: int) -> int:
    """EXACT translation from IRremoteESP8266 IRutils.h"""
    mask = (1 << size) - 1
    return (data >> offset) & mask


# Nibble constants (from IRremoteESP8266 IRutils.h)
kNibbleSize = 4
kLowNibble = 0
kHighNibble = 4


def invertBytePairs(ptr: List[int], length: int) -> None:
    """
    Invert every second byte of an array, after the fixed header.
    EXACT translation from IRremoteESP8266 IRutils.cpp:invertBytePairs
    """
    for i in range(0, length - 1, 2):
        ptr[i + 1] = ptr[i] ^ 0xFF


def checkInvertedBytePairs(ptr: List[int], length: int) -> bool:
    """
    Check if every second byte of an array is inverted to the previous byte.
    EXACT translation from IRremoteESP8266 IRutils.cpp:checkInvertedBytePairs
    """
    for i in range(0, length - 1, 2):
        if ptr[i] != (ptr[i + 1] ^ 0xFF):
            return False
    return True


## Reverse bits in a byte (or any sized value).
## EXACT translation from IRremoteESP8266 IRutils.cpp reverseBits
def reverseBits(input_val: int, nbits: int) -> int:
    """
    Reverse the order of nbits of the integer value.
    EXACT translation from IRremoteESP8266 IRutils.cpp:reverseBits

    @param[in] input_val Integer value to be reversed.
    @param[in] nbits Nr. of bits to reverse.
    @return The reversed bit integer value.
    """
    if nbits <= 1:
        return input_val  # Reversing <= 1 bits makes no change.

    output = 0
    for _ in range(nbits):
        output <<= 1
        output |= input_val & 1
        input_val >>= 1
    return output


#####################################################################
# HitachiAC (224-bit / 28-byte) Protocol
#####################################################################


## Send a Hitachi 28-byte/224-bit A/C formatted message. (HITACHI_AC)
## Status: STABLE / Working.
## EXACT translation from IRremoteESP8266 IRsend::sendHitachiAC (ir_Hitachi.cpp:68-85)
def sendHitachiAC(data: List[int], nbytes: int, repeat: int = 0) -> List[int]:
    """
    Send a Hitachi 28-byte/224-bit A/C formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendHitachiAC

    Returns timing array instead of transmitting via hardware.
    """
    if nbytes < kHitachiAcStateLength:
        return []  # Not enough bytes to send a proper message.

    # EXACT translation from ir_Hitachi.cpp:73-79
    MSBfirst = True
    if nbytes in [kHitachiAc264StateLength, kHitachiAc296StateLength, kHitachiAc344StateLength]:
        MSBfirst = False

    # Import here to avoid circular import
    from app.core.ir_protocols.ir_send import sendGeneric

    # EXACT translation from ir_Hitachi.cpp:81-84
    return sendGeneric(
        headermark=kHitachiAcHdrMark,
        headerspace=kHitachiAcHdrSpace,
        onemark=kHitachiAcBitMark,
        onespace=kHitachiAcOneSpace,
        zeromark=kHitachiAcBitMark,
        zerospace=kHitachiAcZeroSpace,
        footermark=kHitachiAcBitMark,
        gap=kHitachiAcMinGap,
        dataptr=data,
        nbytes=nbytes,
        MSBfirst=MSBfirst,
    )


## Native representation of a Hitachi 224-bit A/C message.
## EXACT translation from IRremoteESP8266 HitachiProtocol (ir_Hitachi.h:44-73)
class HitachiProtocol:
    def __init__(self):
        # The state array (28 bytes for HitachiAC)
        self.remote_state = [0] * kHitachiAcStateLength

    # Byte 10
    @property
    def Mode(self) -> int:
        return self.remote_state[10]

    @Mode.setter
    def Mode(self, value: int) -> None:
        self.remote_state[10] = value & 0xFF

    # Byte 11
    @property
    def Temp(self) -> int:
        return self.remote_state[11]

    @Temp.setter
    def Temp(self, value: int) -> None:
        self.remote_state[11] = value & 0xFF

    # Byte 13
    @property
    def Fan(self) -> int:
        return self.remote_state[13]

    @Fan.setter
    def Fan(self, value: int) -> None:
        self.remote_state[13] = value & 0xFF

    # Byte 14 - SwingV
    @property
    def SwingV(self) -> int:
        return (self.remote_state[14] >> 7) & 0x01

    @SwingV.setter
    def SwingV(self, value: bool) -> None:
        if value:
            self.remote_state[14] |= 0x80
        else:
            self.remote_state[14] &= 0x7F

    # Byte 15 - SwingH
    @property
    def SwingH(self) -> int:
        return (self.remote_state[15] >> 7) & 0x01

    @SwingH.setter
    def SwingH(self, value: bool) -> None:
        if value:
            self.remote_state[15] |= 0x80
        else:
            self.remote_state[15] &= 0x7F

    # Byte 17 - Power
    @property
    def Power(self) -> int:
        return self.remote_state[17] & 0x01

    @Power.setter
    def Power(self, value: bool) -> None:
        if value:
            self.remote_state[17] |= 0x01
        else:
            self.remote_state[17] &= 0xFE

    # Byte 27 - Sum (checksum)
    @property
    def Sum(self) -> int:
        return self.remote_state[27]

    @Sum.setter
    def Sum(self, value: int) -> None:
        self.remote_state[27] = value & 0xFF


## Class for handling detailed Hitachi 224-bit A/C messages.
## EXACT translation from IRremoteESP8266 IRHitachiAc class (ir_Hitachi.cpp:139-424)
class IRHitachiAc:
    ## Class Constructor
    ## EXACT translation from ir_Hitachi.cpp:143-145
    def __init__(self) -> None:
        self._: HitachiProtocol = HitachiProtocol()
        self._previoustemp: int = 23
        self.stateReset()

    ## Reset the internal state to a fixed known good state.
    ## EXACT translation from ir_Hitachi.cpp:148-164
    def stateReset(self) -> None:
        self._.remote_state[0] = 0x80
        self._.remote_state[1] = 0x08
        self._.remote_state[2] = 0x0C
        self._.remote_state[3] = 0x02
        self._.remote_state[4] = 0xFD
        self._.remote_state[5] = 0x80
        self._.remote_state[6] = 0x7F
        self._.remote_state[7] = 0x88
        self._.remote_state[8] = 0x48
        self._.remote_state[9] = 0x10
        for i in range(10, kHitachiAcStateLength):
            self._.remote_state[i] = 0x00
        self._.remote_state[14] = 0x60
        self._.remote_state[15] = 0x60
        self._.remote_state[24] = 0x80
        self.setTemp(23)

    ## Calculate the checksum for a given state.
    ## EXACT translation from ir_Hitachi.cpp:173-178
    @staticmethod
    def calcChecksum(state: List[int], length: int = kHitachiAcStateLength) -> int:
        sum_val = 62
        for i in range(length - 1):
            sum_val -= reverseBits(state[i], 8)
        return reverseBits(sum_val & 0xFF, 8)

    ## Calculate and set the checksum values for the internal state.
    ## EXACT translation from ir_Hitachi.cpp:182-184
    def checksum(self, length: int = kHitachiAcStateLength) -> None:
        self._.Sum = self.calcChecksum(self._.remote_state, length)

    ## Verify the checksum is valid for a given state.
    ## EXACT translation from ir_Hitachi.cpp:190-193
    @staticmethod
    def validChecksum(state: List[int], length: int = kHitachiAcStateLength) -> bool:
        if length < 2:
            return True  # Assume true for lengths that are too short.
        return state[length - 1] == IRHitachiAc.calcChecksum(state, length)

    ## Get a PTR to the internal state/code for this protocol.
    ## EXACT translation from ir_Hitachi.cpp:197-200
    def getRaw(self) -> List[int]:
        self.checksum()
        return self._.remote_state

    ## Set the internal state from a valid code for this protocol.
    ## EXACT translation from ir_Hitachi.cpp:205-207
    def setRaw(self, new_code: List[int], length: int = kHitachiAcStateLength) -> None:
        for i in range(min(length, kHitachiAcStateLength)):
            self._.remote_state[i] = new_code[i]

    ## Get the value of the current power setting.
    ## EXACT translation from ir_Hitachi.cpp:219-221
    def getPower(self) -> bool:
        return bool(self._.Power)

    ## Change the power setting.
    ## EXACT translation from ir_Hitachi.cpp:225-227
    def setPower(self, on: bool) -> None:
        self._.Power = on

    ## Change the power setting to On.
    ## EXACT translation from ir_Hitachi.cpp:230
    def on(self) -> None:
        self.setPower(True)

    ## Change the power setting to Off.
    ## EXACT translation from ir_Hitachi.cpp:233
    def off(self) -> None:
        self.setPower(False)

    ## Get the operating mode setting of the A/C.
    ## EXACT translation from ir_Hitachi.cpp:237
    def getMode(self) -> int:
        return reverseBits(self._.Mode, 8)

    ## Set the operating mode of the A/C.
    ## EXACT translation from ir_Hitachi.cpp:241-255
    def setMode(self, mode: int) -> None:
        newmode = mode
        if mode == kHitachiAcFan:
            # Fan mode sets a special temp.
            self.setTemp(64)
        elif mode in [kHitachiAcAuto, kHitachiAcHeat, kHitachiAcCool, kHitachiAcDry]:
            pass
        else:
            newmode = kHitachiAcAuto
        self._.Mode = reverseBits(newmode, 8)
        if mode != kHitachiAcFan:
            self.setTemp(self._previoustemp)
        self.setFan(self.getFan())  # Reset the fan speed after the mode change.

    ## Get the current temperature setting.
    ## EXACT translation from ir_Hitachi.cpp:259-261
    def getTemp(self) -> int:
        return reverseBits(self._.Temp, 8) >> 1

    ## Set the temperature.
    ## EXACT translation from ir_Hitachi.cpp:265-281
    def setTemp(self, celsius: int) -> None:
        if celsius != 64:
            self._previoustemp = celsius

        if celsius == 64:
            temp = celsius
        else:
            temp = min(celsius, kHitachiAcMaxTemp)
            temp = max(temp, kHitachiAcMinTemp)

        self._.Temp = reverseBits(temp << 1, 8)
        if temp == kHitachiAcMinTemp:
            self._.remote_state[9] = 0x90
        else:
            self._.remote_state[9] = 0x10

    ## Get the current fan speed setting.
    ## EXACT translation from ir_Hitachi.cpp:285
    def getFan(self) -> int:
        return reverseBits(self._.Fan, 8)

    ## Set the speed of the fan.
    ## EXACT translation from ir_Hitachi.cpp:289-304
    def setFan(self, speed: int) -> None:
        fanmin = kHitachiAcFanAuto
        fanmax = kHitachiAcFanHigh

        mode = self.getMode()
        if mode == kHitachiAcDry:
            # Only 2 x low speeds in Dry mode.
            fanmin = kHitachiAcFanLow
            fanmax = kHitachiAcFanLow + 1
        elif mode == kHitachiAcFan:
            fanmin = kHitachiAcFanLow  # No Auto in Fan mode.

        newspeed = max(speed, fanmin)
        newspeed = min(newspeed, fanmax)
        self._.Fan = reverseBits(newspeed, 8)

    ## Get the Vertical Swing setting of the A/C.
    ## EXACT translation from ir_Hitachi.cpp:308-310
    def getSwingVertical(self) -> bool:
        return bool(self._.SwingV)

    ## Set the Vertical Swing setting of the A/C.
    ## EXACT translation from ir_Hitachi.cpp:314-316
    def setSwingVertical(self, on: bool) -> None:
        self._.SwingV = on

    ## Get the Horizontal Swing setting of the A/C.
    ## EXACT translation from ir_Hitachi.cpp:320-322
    def getSwingHorizontal(self) -> bool:
        return bool(self._.SwingH)

    ## Set the Horizontal Swing setting of the A/C.
    ## EXACT translation from ir_Hitachi.cpp:326-328
    def setSwingHorizontal(self, on: bool) -> None:
        self._.SwingH = on


#####################################################################
# HitachiAC1 (104-bit / 13-byte) Protocol
#####################################################################


## Send a Hitachi 13 byte/104-bit A/C formatted message. (HITACHI_AC1)
## Status: STABLE / Confirmed Working.
## EXACT translation from IRremoteESP8266 IRsend::sendHitachiAC1 (ir_Hitachi.cpp:97-105)
def sendHitachiAC1(data: List[int], nbytes: int, repeat: int = 0) -> List[int]:
    """
    Send a Hitachi 13 byte/104-bit A/C formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendHitachiAC1

    Returns timing array instead of transmitting via hardware.
    """
    if nbytes < kHitachiAc1StateLength:
        return []  # Not enough bytes to send a proper message.

    # Import here to avoid circular import
    from app.core.ir_protocols.ir_send import sendGeneric

    # EXACT translation from ir_Hitachi.cpp:101-104
    return sendGeneric(
        headermark=kHitachiAc1HdrMark,
        headerspace=kHitachiAc1HdrSpace,
        onemark=kHitachiAcBitMark,
        onespace=kHitachiAcOneSpace,
        zeromark=kHitachiAcBitMark,
        zerospace=kHitachiAcZeroSpace,
        footermark=kHitachiAcBitMark,
        gap=kHitachiAcMinGap,
        dataptr=data,
        nbytes=nbytes,
        MSBfirst=True,
    )


## Native representation of a Hitachi 104-bit A/C message.
## EXACT translation from IRremoteESP8266 Hitachi1Protocol (ir_Hitachi.h:180-215)
class Hitachi1Protocol:
    def __init__(self):
        # The state array (13 bytes for HitachiAC1)
        self.remote_state = [0] * kHitachiAc1StateLength

    # Byte 3 - Model
    @property
    def Model(self) -> int:
        return (self.remote_state[3] >> 6) & 0x03

    @Model.setter
    def Model(self, value: int) -> None:
        self.remote_state[3] = (self.remote_state[3] & 0x3F) | ((value & 0x03) << 6)

    # Byte 5 - Mode & Fan
    @property
    def Mode(self) -> int:
        return (self.remote_state[5] >> 4) & 0x0F

    @Mode.setter
    def Mode(self, value: int) -> None:
        self.remote_state[5] = (self.remote_state[5] & 0x0F) | ((value & 0x0F) << 4)

    @property
    def Fan(self) -> int:
        return self.remote_state[5] & 0x0F

    @Fan.setter
    def Fan(self, value: int) -> None:
        self.remote_state[5] = (self.remote_state[5] & 0xF0) | (value & 0x0F)

    # Byte 6 - Temp (stored in LSB order)
    @property
    def Temp(self) -> int:
        return (self.remote_state[6] >> 2) & 0x1F

    @Temp.setter
    def Temp(self, value: int) -> None:
        self.remote_state[6] = (self.remote_state[6] & 0x83) | ((value & 0x1F) << 2)

    # Byte 7 - OffTimerLow
    @property
    def OffTimerLow(self) -> int:
        return self.remote_state[7]

    @OffTimerLow.setter
    def OffTimerLow(self, value: int) -> None:
        self.remote_state[7] = value & 0xFF

    # Byte 8 - OffTimerHigh
    @property
    def OffTimerHigh(self) -> int:
        return self.remote_state[8]

    @OffTimerHigh.setter
    def OffTimerHigh(self, value: int) -> None:
        self.remote_state[8] = value & 0xFF

    # Byte 9 - OnTimerLow
    @property
    def OnTimerLow(self) -> int:
        return self.remote_state[9]

    @OnTimerLow.setter
    def OnTimerLow(self, value: int) -> None:
        self.remote_state[9] = value & 0xFF

    # Byte 10 - OnTimerHigh
    @property
    def OnTimerHigh(self) -> int:
        return self.remote_state[10]

    @OnTimerHigh.setter
    def OnTimerHigh(self, value: int) -> None:
        self.remote_state[10] = value & 0xFF

    # Byte 11 - SwingToggle, Sleep, PowerToggle, Power, SwingV, SwingH
    @property
    def SwingToggle(self) -> int:
        return self.remote_state[11] & 0x01

    @SwingToggle.setter
    def SwingToggle(self, value: bool) -> None:
        if value:
            self.remote_state[11] |= 0x01
        else:
            self.remote_state[11] &= 0xFE

    @property
    def Sleep(self) -> int:
        return (self.remote_state[11] >> 1) & 0x07

    @Sleep.setter
    def Sleep(self, value: int) -> None:
        self.remote_state[11] = (self.remote_state[11] & 0xF1) | ((value & 0x07) << 1)

    @property
    def PowerToggle(self) -> int:
        return (self.remote_state[11] >> 4) & 0x01

    @PowerToggle.setter
    def PowerToggle(self, value: bool) -> None:
        if value:
            self.remote_state[11] |= 0x10
        else:
            self.remote_state[11] &= 0xEF

    @property
    def Power(self) -> int:
        return (self.remote_state[11] >> 5) & 0x01

    @Power.setter
    def Power(self, value: bool) -> None:
        if value:
            self.remote_state[11] |= 0x20
        else:
            self.remote_state[11] &= 0xDF

    @property
    def SwingV(self) -> int:
        return (self.remote_state[11] >> 6) & 0x01

    @SwingV.setter
    def SwingV(self, value: bool) -> None:
        if value:
            self.remote_state[11] |= 0x40
        else:
            self.remote_state[11] &= 0xBF

    @property
    def SwingH(self) -> int:
        return (self.remote_state[11] >> 7) & 0x01

    @SwingH.setter
    def SwingH(self, value: bool) -> None:
        if value:
            self.remote_state[11] |= 0x80
        else:
            self.remote_state[11] &= 0x7F

    # Byte 12 - Sum (checksum)
    @property
    def Sum(self) -> int:
        return self.remote_state[12]

    @Sum.setter
    def Sum(self, value: int) -> None:
        self.remote_state[12] = value & 0xFF


## Class for handling detailed Hitachi 104-bit A/C messages.
## EXACT translation from IRremoteESP8266 IRHitachiAc1 class (ir_Hitachi.cpp:430-837)
class IRHitachiAc1:
    ## Class Constructor
    ## EXACT translation from ir_Hitachi.cpp:430-432
    def __init__(self) -> None:
        self._: Hitachi1Protocol = Hitachi1Protocol()
        self.stateReset()

    ## Reset the internal state to a fixed known good state.
    ## EXACT translation from ir_Hitachi.cpp:435-447
    def stateReset(self) -> None:
        for i in range(kHitachiAc1StateLength):
            self._.remote_state[i] = 0x00
        # Copy in a known good state.
        self._.remote_state[0] = 0xB2
        self._.remote_state[1] = 0xAE
        self._.remote_state[2] = 0x4D
        self._.remote_state[3] = 0x91
        self._.remote_state[4] = 0xF0
        self._.remote_state[5] = 0xE1
        self._.remote_state[6] = 0xA4
        self._.remote_state[11] = 0x61
        self._.remote_state[12] = 0x24

    ## Calculate the checksum for a given state.
    ## EXACT translation from ir_Hitachi.cpp:456-466
    @staticmethod
    def calcChecksum(state: List[int], length: int = kHitachiAc1StateLength) -> int:
        sum_val = 0
        for i in range(kHitachiAc1ChecksumStartByte, length - 1):
            sum_val += reverseBits(GETBITS8(state[i], kLowNibble, kNibbleSize), kNibbleSize)
            sum_val += reverseBits(GETBITS8(state[i], kHighNibble, kNibbleSize), kNibbleSize)
        return reverseBits(sum_val & 0xFF, 8)

    ## Calculate and set the checksum values for the internal state.
    ## EXACT translation from ir_Hitachi.cpp:470-472
    def checksum(self, length: int = kHitachiAc1StateLength) -> None:
        self._.Sum = self.calcChecksum(self._.remote_state, length)

    ## Verify the checksum is valid for a given state.
    ## EXACT translation from ir_Hitachi.cpp:478-481
    @staticmethod
    def validChecksum(state: List[int], length: int = kHitachiAc1StateLength) -> bool:
        if length < 2:
            return True  # Assume true for lengths that are too short.
        return state[length - 1] == IRHitachiAc1.calcChecksum(state, length)

    ## Get a PTR to the internal state/code for this protocol.
    ## EXACT translation from ir_Hitachi.cpp:485-488
    def getRaw(self) -> List[int]:
        self.checksum()
        return self._.remote_state

    ## Set the internal state from a valid code for this protocol.
    ## EXACT translation from ir_Hitachi.cpp:493-495
    def setRaw(self, new_code: List[int], length: int = kHitachiAc1StateLength) -> None:
        for i in range(min(length, kHitachiAc1StateLength)):
            self._.remote_state[i] = new_code[i]

    ## Get/Detect the model of the A/C.
    ## EXACT translation from ir_Hitachi.cpp:510-515
    def getModel(self) -> int:
        if self._.Model == kHitachiAc1Model_B:
            return 1  # R_LT0541_HTA_B
        else:
            return 0  # R_LT0541_HTA_A

    ## Set the model of the A/C to emulate.
    ## EXACT translation from ir_Hitachi.cpp:519-529
    def setModel(self, model: int) -> None:
        if model == 1:  # R_LT0541_HTA_B
            value = kHitachiAc1Model_B
        else:
            value = kHitachiAc1Model_A  # i.e. 'A' mode.
        self._.Model = value

    ## Get the value of the current power setting.
    ## EXACT translation from ir_Hitachi.cpp:533-535
    def getPower(self) -> bool:
        return bool(self._.Power)

    ## Change the power setting.
    ## EXACT translation from ir_Hitachi.cpp:539-543
    def setPower(self, on: bool) -> None:
        # If the power changes, set the power toggle bit.
        if on != self._.Power:
            self.setPowerToggle(True)
        self._.Power = on

    ## Get the value of the current power toggle setting.
    ## EXACT translation from ir_Hitachi.cpp:547-549
    def getPowerToggle(self) -> bool:
        return bool(self._.PowerToggle)

    ## Change the power toggle setting.
    ## EXACT translation from ir_Hitachi.cpp:553-555
    def setPowerToggle(self, on: bool) -> None:
        self._.PowerToggle = on

    ## Change the power setting to On.
    ## EXACT translation from ir_Hitachi.cpp:558
    def on(self) -> None:
        self.setPower(True)

    ## Change the power setting to Off.
    ## EXACT translation from ir_Hitachi.cpp:561
    def off(self) -> None:
        self.setPower(False)

    ## Get the operating mode setting of the A/C.
    ## EXACT translation from ir_Hitachi.cpp:565-567
    def getMode(self) -> int:
        return self._.Mode

    ## Set the operating mode of the A/C.
    ## EXACT translation from ir_Hitachi.cpp:571-589
    def setMode(self, mode: int) -> None:
        if mode == kHitachiAc1Auto:
            self.setTemp(kHitachiAc1TempAuto)
            # FALL THRU
        if mode in [
            kHitachiAc1Auto,
            kHitachiAc1Fan,
            kHitachiAc1Heat,
            kHitachiAc1Cool,
            kHitachiAc1Dry,
        ]:
            self._.Mode = mode
        else:
            self.setTemp(kHitachiAc1TempAuto)
            self._.Mode = kHitachiAc1Auto
        self.setSleep(self._.Sleep)  # Correct the sleep mode if required.
        self.setFan(self._.Fan)  # Correct the fan speed if required.

    ## Get the current temperature setting.
    ## EXACT translation from ir_Hitachi.cpp:593-595
    def getTemp(self) -> int:
        return reverseBits(self._.Temp, kHitachiAc1TempSize) + kHitachiAc1TempDelta

    ## Set the temperature.
    ## EXACT translation from ir_Hitachi.cpp:599-606
    def setTemp(self, celsius: int) -> None:
        if self._.Mode == kHitachiAc1Auto:
            return  # Can't change temp in Auto mode.
        temp = min(celsius, kHitachiAcMaxTemp)
        temp = max(temp, kHitachiAcMinTemp)
        temp -= kHitachiAc1TempDelta
        temp = reverseBits(temp, kHitachiAc1TempSize)
        self._.Temp = temp

    ## Get the current fan speed setting.
    ## EXACT translation from ir_Hitachi.cpp:610-612
    def getFan(self) -> int:
        return self._.Fan

    ## Set the speed of the fan.
    ## EXACT translation from ir_Hitachi.cpp:617-642
    def setFan(self, speed: int, force: bool = False) -> None:
        # restrictions
        if self._.Mode == kHitachiAc1Dry:
            self._.Fan = kHitachiAc1FanLow  # Dry is locked to Low speed.
            return
        elif self._.Mode == kHitachiAc1Auto:
            self._.Fan = kHitachiAc1FanAuto  # Auto is locked to Auto speed.
            return
        elif self._.Mode in [kHitachiAc1Heat, kHitachiAc1Fan]:
            # Auto speed not allowed in these modes.
            if speed == kHitachiAc1FanAuto or self._.Fan == kHitachiAc1FanAuto:
                self._.Fan = kHitachiAc1FanLow
            return

        if speed in [kHitachiAc1FanAuto, kHitachiAc1FanHigh, kHitachiAc1FanMed, kHitachiAc1FanLow]:
            self._.Fan = speed
        else:
            self._.Fan = kHitachiAc1FanAuto

    ## Get the Swing Toggle setting of the A/C.
    ## EXACT translation from ir_Hitachi.cpp:646-648
    def getSwingToggle(self) -> bool:
        return bool(self._.SwingToggle)

    ## Set the Swing toggle setting of the A/C.
    ## EXACT translation from ir_Hitachi.cpp:652-654
    def setSwingToggle(self, toggle: bool) -> None:
        self._.SwingToggle = toggle

    ## Get the Vertical Swing setting of the A/C.
    ## EXACT translation from ir_Hitachi.cpp:658-660
    def getSwingV(self) -> bool:
        return bool(self._.SwingV)

    ## Set the Vertical Swing setting of the A/C.
    ## EXACT translation from ir_Hitachi.cpp:664-666
    def setSwingV(self, on: bool) -> None:
        self._.SwingV = on

    ## Get the Horizontal Swing setting of the A/C.
    ## EXACT translation from ir_Hitachi.cpp:670-672
    def getSwingH(self) -> bool:
        return bool(self._.SwingH)

    ## Set the Horizontal Swing setting of the A/C.
    ## EXACT translation from ir_Hitachi.cpp:676-678
    def setSwingH(self, on: bool) -> None:
        self._.SwingH = on

    ## Get the Sleep setting of the A/C.
    ## EXACT translation from ir_Hitachi.cpp:683-685
    def getSleep(self) -> int:
        return self._.Sleep

    ## Set the Sleep setting of the A/C.
    ## EXACT translation from ir_Hitachi.cpp:690-699
    def setSleep(self, mode: int) -> None:
        if self._.Mode in [kHitachiAc1Auto, kHitachiAc1Cool]:
            self._.Sleep = min(mode, kHitachiAc1Sleep4)
        else:
            self._.Sleep = kHitachiAc1SleepOff

    ## Set the On Timer time.
    ## EXACT translation from ir_Hitachi.cpp:703-707
    def setOnTimer(self, mins: int) -> None:
        mins_lsb = reverseBits(mins, kHitachiAc1TimerSize)
        self._.OnTimerLow = GETBITS16(mins_lsb, 8, 8)
        self._.OnTimerHigh = GETBITS16(mins_lsb, 0, 8)

    ## Get the On Timer time of the A/C.
    ## EXACT translation from ir_Hitachi.cpp:711-714
    def getOnTimer(self) -> int:
        return reverseBits((self._.OnTimerLow << 8) | self._.OnTimerHigh, kHitachiAc1TimerSize)

    ## Set the Off Timer time.
    ## EXACT translation from ir_Hitachi.cpp:718-722
    def setOffTimer(self, mins: int) -> None:
        mins_lsb = reverseBits(mins, kHitachiAc1TimerSize)
        self._.OffTimerLow = GETBITS16(mins_lsb, 8, 8)
        self._.OffTimerHigh = GETBITS16(mins_lsb, 0, 8)

    ## Get the Off Timer time of the A/C.
    ## EXACT translation from ir_Hitachi.cpp:726-729
    def getOffTimer(self) -> int:
        return reverseBits((self._.OffTimerLow << 8) | self._.OffTimerHigh, kHitachiAc1TimerSize)


#####################################################################
# HitachiAC424 (424-bit / 53-byte) Protocol
#####################################################################


## Native representation of a Hitachi 53-byte/424-bit A/C message.
## EXACT translation from IRremoteESP8266 Hitachi424Protocol (ir_Hitachi.h:91-126)
class Hitachi424Protocol:
    def __init__(self):
        # The state array (53 bytes for HitachiAC424)
        self.remote_state = [0] * kHitachiAc424StateLength

    # Byte 11 - Button
    @property
    def Button(self) -> int:
        return self.remote_state[11]

    @Button.setter
    def Button(self, value: int) -> None:
        self.remote_state[11] = value & 0xFF

    # Byte 13 - Temp (6 bits starting at bit 2)
    @property
    def Temp(self) -> int:
        return (self.remote_state[13] >> 2) & 0x3F

    @Temp.setter
    def Temp(self, value: int) -> None:
        self.remote_state[13] = (self.remote_state[13] & 0x03) | ((value & 0x3F) << 2)

    # Byte 25 - Mode (4 bits) & Fan (4 bits)
    @property
    def Mode(self) -> int:
        return self.remote_state[25] & 0x0F

    @Mode.setter
    def Mode(self, value: int) -> None:
        self.remote_state[25] = (self.remote_state[25] & 0xF0) | (value & 0x0F)

    @property
    def Fan(self) -> int:
        return (self.remote_state[25] >> 4) & 0x0F

    @Fan.setter
    def Fan(self, value: int) -> None:
        self.remote_state[25] = (self.remote_state[25] & 0x0F) | ((value & 0x0F) << 4)

    # Byte 27 - Power (bit 4)
    @property
    def Power(self) -> int:
        return (self.remote_state[27] >> 4) & 0x01

    @Power.setter
    def Power(self, value: bool) -> None:
        if value:
            self.remote_state[27] |= 0x10
        else:
            self.remote_state[27] &= 0xEF

    # Byte 35 - SwingH (3 bits)
    @property
    def SwingH(self) -> int:
        return self.remote_state[35] & 0x07

    @SwingH.setter
    def SwingH(self, value: int) -> None:
        self.remote_state[35] = (self.remote_state[35] & 0xF8) | (value & 0x07)

    # Byte 37 - SwingV (bit 5)
    @property
    def SwingV(self) -> int:
        return (self.remote_state[37] >> 5) & 0x01

    @SwingV.setter
    def SwingV(self, value: bool) -> None:
        if value:
            self.remote_state[37] |= 0x20
        else:
            self.remote_state[37] &= 0xDF


## Send a Hitachi 53 byte/424-bit A/C formatted message. (HITACHI_AC424)
## Status: STABLE / Reported as working.
## EXACT translation from IRremoteESP8266 IRsend::sendHitachiAc424 (ir_Hitachi.cpp:946-961)
def sendHitachiAc424(data: List[int], nbytes: int, repeat: int = 0) -> List[int]:
    """
    Send a Hitachi 53 byte/424-bit A/C formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendHitachiAc424

    Returns timing array instead of transmitting via hardware.
    """
    # Import here to avoid circular import
    from app.core.ir_protocols.ir_send import sendGeneric

    all_timings = []

    for r in range(repeat + 1):
        # Leader (EXACT translation from ir_Hitachi.cpp:951-952)
        all_timings.append(kHitachiAc424LdrMark)
        all_timings.append(kHitachiAc424LdrSpace)

        # Header + Data + Footer (EXACT translation from ir_Hitachi.cpp:954-959)
        msg_timings = sendGeneric(
            headermark=kHitachiAc424HdrMark,
            headerspace=kHitachiAc424HdrSpace,
            onemark=kHitachiAc424BitMark,
            onespace=kHitachiAc424OneSpace,
            zeromark=kHitachiAc424BitMark,
            zerospace=kHitachiAc424ZeroSpace,
            footermark=kHitachiAc424BitMark,
            gap=kHitachiAcMinGap,
            dataptr=data,
            nbytes=nbytes,
            MSBfirst=False,
        )
        all_timings.extend(msg_timings)

    return all_timings


## Class for handling detailed Hitachi 53-byte/424-bit A/C messages.
## EXACT translation from IRremoteESP8266 IRHitachiAc424 class (ir_Hitachi.cpp:1015-1335)
class IRHitachiAc424:
    ## Class Constructor
    ## EXACT translation from ir_Hitachi.cpp:1015-1017
    def __init__(self) -> None:
        self._: Hitachi424Protocol = Hitachi424Protocol()
        self._previoustemp: int = 23
        self.stateReset()

    ## Reset the internal state to a fixed known good state.
    ## EXACT translation from ir_Hitachi.cpp:1021-1044
    def stateReset(self) -> None:
        for i in range(kHitachiAc424StateLength):
            self._.remote_state[i] = 0x00

        self._.remote_state[0] = 0x01
        self._.remote_state[1] = 0x10
        self._.remote_state[3] = 0x40
        self._.remote_state[5] = 0xFF
        self._.remote_state[7] = 0xCC
        self._.remote_state[27] = 0xE1
        self._.remote_state[33] = 0x80
        self._.remote_state[35] = 0x03
        self._.remote_state[37] = 0x01
        self._.remote_state[39] = 0x88
        self._.remote_state[45] = 0xFF
        self._.remote_state[47] = 0xFF
        self._.remote_state[49] = 0xFF
        self._.remote_state[51] = 0xFF

        self.setTemp(23)
        self.setPower(True)
        self.setMode(kHitachiAc424Cool)
        self.setFan(kHitachiAc424FanAuto)

    ## Update the internal consistency check for the protocol.
    ## EXACT translation from ir_Hitachi.cpp:1047-1049
    def setInvertedStates(self) -> None:
        invertBytePairs(self._.remote_state[3:], kHitachiAc424StateLength - 3)

    ## Get a PTR to the internal state/code for this protocol.
    ## EXACT translation from ir_Hitachi.cpp:1056-1059
    def getRaw(self) -> List[int]:
        self.setInvertedStates()
        return self._.remote_state

    ## Set the internal state from a valid code for this protocol.
    ## EXACT translation from ir_Hitachi.cpp:1064-1066
    def setRaw(self, new_code: List[int], length: int = kHitachiAc424StateLength) -> None:
        for i in range(min(length, kHitachiAc424StateLength)):
            self._.remote_state[i] = new_code[i]

    ## Get the value of the current power setting.
    ## EXACT translation from ir_Hitachi.cpp:1078
    def getPower(self) -> bool:
        return bool(self._.Power)

    ## Change the power setting.
    ## EXACT translation from ir_Hitachi.cpp:1082-1085
    def setPower(self, on: bool) -> None:
        self._.Power = on
        self.setButton(kHitachiAc424ButtonPowerMode)

    ## Change the power setting to On.
    ## EXACT translation from ir_Hitachi.cpp:1088
    def on(self) -> None:
        self.setPower(True)

    ## Change the power setting to Off.
    ## EXACT translation from ir_Hitachi.cpp:1091
    def off(self) -> None:
        self.setPower(False)

    ## Get the operating mode setting of the A/C.
    ## EXACT translation from ir_Hitachi.cpp:1095-1097
    def getMode(self) -> int:
        return self._.Mode

    ## Set the operating mode of the A/C.
    ## EXACT translation from ir_Hitachi.cpp:1101-1115
    def setMode(self, mode: int) -> None:
        newMode = mode
        if mode == kHitachiAc424Fan:
            # Fan mode sets a special temp.
            self.setTemp(kHitachiAc424FanTemp, False)
        elif mode in [kHitachiAc424Heat, kHitachiAc424Cool, kHitachiAc424Dry]:
            pass
        else:
            newMode = kHitachiAc424Cool

        self._.Mode = newMode
        if newMode != kHitachiAc424Fan:
            self.setTemp(self._previoustemp)
        self.setFan(self._.Fan)  # Reset the fan speed after the mode change.
        self.setButton(kHitachiAc424ButtonPowerMode)

    ## Get the current temperature setting.
    ## EXACT translation from ir_Hitachi.cpp:1119-1121
    def getTemp(self) -> int:
        return self._.Temp

    ## Set the temperature.
    ## EXACT translation from ir_Hitachi.cpp:1126-1136
    def setTemp(self, celsius: int, setPrevious: bool = True) -> None:
        temp = min(celsius, kHitachiAc424MaxTemp)
        temp = max(temp, kHitachiAc424MinTemp)
        self._.Temp = temp

        if self._previoustemp > temp:
            self.setButton(kHitachiAc424ButtonTempDown)
        elif self._previoustemp < temp:
            self.setButton(kHitachiAc424ButtonTempUp)

        if setPrevious:
            self._previoustemp = temp

    ## Get the current fan speed setting.
    ## EXACT translation from ir_Hitachi.cpp:1140-1142
    def getFan(self) -> int:
        return self._.Fan

    ## Set the speed of the fan.
    ## EXACT translation from ir_Hitachi.cpp:1146-1174
    def setFan(self, speed: int) -> None:
        newSpeed = max(speed, kHitachiAc424FanMin)
        fanMax = kHitachiAc424FanMax

        # Only 2 x low speeds in Dry mode or Auto
        if self._.Mode == kHitachiAc424Dry and speed == kHitachiAc424FanAuto:
            fanMax = kHitachiAc424FanAuto
        elif self._.Mode == kHitachiAc424Dry:
            fanMax = kHitachiAc424FanMaxDry
        elif self._.Mode == kHitachiAc424Fan and speed == kHitachiAc424FanAuto:
            # Fan Mode does not have auto. Set to safe low
            newSpeed = kHitachiAc424FanMin

        newSpeed = min(newSpeed, fanMax)
        # Handle the setting the button value if we are going to change the value.
        if newSpeed != self._.Fan:
            self.setButton(kHitachiAc424ButtonFan)
        # Set the values
        self._.Fan = newSpeed
        self._.remote_state[9] = 0x92
        self._.remote_state[29] = 0x00

        # When fan is at min/max, additional bytes seem to be set
        if newSpeed == kHitachiAc424FanMin:
            self._.remote_state[9] = 0x98
        if newSpeed == kHitachiAc424FanMax:
            self._.remote_state[9] = 0xA9
            self._.remote_state[29] = 0x30

    ## Get the Button/Command setting of the A/C.
    ## EXACT translation from ir_Hitachi.cpp:1178-1180
    def getButton(self) -> int:
        return self._.Button

    ## Set the Button/Command pressed setting of the A/C.
    ## EXACT translation from ir_Hitachi.cpp:1184-1186
    def setButton(self, button: int) -> None:
        self._.Button = button

    ## Set the Vertical Swing toggle setting of the A/C.
    ## EXACT translation from ir_Hitachi.cpp:1192-1200
    def setSwingVToggle(self, on: bool) -> None:
        button = self._.Button  # Get the current button value.
        if on:
            button = kHitachiAc424ButtonSwingV  # Set the button to SwingV.
        elif button == kHitachiAc424ButtonSwingV:  # Asked to unset it
            # It was set previous, so use Power as a default
            button = kHitachiAc424ButtonPowerMode
        self.setButton(button)

    ## Get the Vertical Swing toggle setting of the A/C.
    ## EXACT translation from ir_Hitachi.cpp:1204-1206
    def getSwingVToggle(self) -> bool:
        return self._.Button == kHitachiAc424ButtonSwingV


#####################################################################
# HitachiAC3 (variable length 15-27 bytes) Protocol
#####################################################################


## Send a Hitachi(3) A/C formatted message. (HITACHI_AC3)
## Status: STABLE / Working fine.
## EXACT translation from IRremoteESP8266 IRsend::sendHitachiAc3 (ir_Hitachi.cpp:1351-1360)
def sendHitachiAc3(data: List[int], nbytes: int, repeat: int = 0) -> List[int]:
    """
    Send a Hitachi(3) A/C formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendHitachiAc3

    Returns timing array instead of transmitting via hardware.
    """
    # Import here to avoid circular import
    from app.core.ir_protocols.ir_send import sendGeneric

    # Header + Data + Footer (EXACT translation from ir_Hitachi.cpp:1354-1359)
    return sendGeneric(
        headermark=kHitachiAc3HdrMark,
        headerspace=kHitachiAc3HdrSpace,
        onemark=kHitachiAc3BitMark,
        onespace=kHitachiAc3OneSpace,
        zeromark=kHitachiAc3BitMark,
        zerospace=kHitachiAc3ZeroSpace,
        footermark=kHitachiAc3BitMark,
        gap=kHitachiAcMinGap,
        dataptr=data,
        nbytes=nbytes,
        MSBfirst=False,
    )


## Class for handling detailed Hitachi 15to27-byte/120to216-bit A/C messages.
## EXACT translation from IRremoteESP8266 IRHitachiAc3 class (ir_Hitachi.cpp:1368-1423)
class IRHitachiAc3:
    ## Class Constructor
    ## EXACT translation from ir_Hitachi.cpp:1368-1370
    def __init__(self) -> None:
        self.remote_state: List[int] = [0] * kHitachiAc3StateLength
        self.stateReset()

    ## Reset the internal state to a fixed known good state.
    ## EXACT translation from ir_Hitachi.cpp:1374-1389
    def stateReset(self) -> None:
        for i in range(kHitachiAc3StateLength):
            self.remote_state[i] = 0x00
        self.remote_state[0] = 0x01
        self.remote_state[1] = 0x10
        self.remote_state[3] = 0x40
        self.remote_state[5] = 0xFF
        self.remote_state[7] = 0xE8
        self.remote_state[9] = 0x89
        self.remote_state[11] = 0x0B
        self.remote_state[13] = 0x3F
        self.remote_state[15] = 0x15
        self.remote_state[21] = 0x4B
        self.remote_state[23] = 0x18
        self.setInvertedStates()

    ## Invert every second byte of the internal state, after the fixed header.
    ## EXACT translation from ir_Hitachi.cpp:1394-1396
    def setInvertedStates(self, length: int = kHitachiAc3StateLength) -> None:
        if length > 3:
            invertBytePairs(self.remote_state[3:], length - 3)

    ## Check if every second byte of the state, after the fixed header
    ##   is inverted to the previous byte.
    ## EXACT translation from ir_Hitachi.cpp:1403-1406
    @staticmethod
    def hasInvertedStates(state: List[int], length: int) -> bool:
        return length <= 3 or checkInvertedBytePairs(state[3:], length - 3)

    ## Get a PTR to the internal state/code for this protocol.
    ## EXACT translation from ir_Hitachi.cpp:1413-1416
    def getRaw(self) -> List[int]:
        self.setInvertedStates()
        return self.remote_state

    ## Set the internal state from a valid code for this protocol.
    ## EXACT translation from ir_Hitachi.cpp:1421-1423
    def setRaw(self, new_code: List[int], length: int = kHitachiAc3StateLength) -> None:
        for i in range(min(length, kHitachiAc3StateLength)):
            self.remote_state[i] = new_code[i]

    ## Get the operating mode setting of the A/C.
    ## @return The current operating mode setting.
    def getMode(self) -> int:
        # Byte 25 contains mode (lower 4 bits)
        if len(self.remote_state) >= 26:
            return self.remote_state[25] & 0x0F
        return 0


#####################################################################
# HitachiAC344 (344-bit / 43-byte) Protocol
#####################################################################


## Send a Hitachi A/C 43-byte/344-bit message. (HITACHI_AC344)
##  Basically the same as sendHitachiAC() except different size.
## Status: Beta / Probably works.
## EXACT translation from IRremoteESP8266 IRsend::sendHitachiAc344 (ir_Hitachi.cpp:131-136)
def sendHitachiAc344(data: List[int], nbytes: int, repeat: int = 0) -> List[int]:
    """
    Send a Hitachi A/C 43-byte/344-bit message.
    EXACT translation from IRremoteESP8266 IRsend::sendHitachiAc344
    """
    if nbytes < kHitachiAc344StateLength:
        return []  # Not enough bytes to send a proper message.
    return sendHitachiAC(data, nbytes, repeat)


## Class for handling detailed Hitachi_AC344 43 byte A/C messages.
## EXACT translation from IRremoteESP8266 IRHitachiAc344 class (ir_Hitachi.cpp:1485-1598)
class IRHitachiAc344(IRHitachiAc424):
    ## Class Constructor for handling detailed Hitachi_AC344 43 byte A/C messages.
    ## EXACT translation from ir_Hitachi.cpp:1485-1487
    def __init__(self) -> None:
        super().__init__()
        self.stateReset()

    ## Reset the internal state to auto fan, cooling, 23 Celsius
    ## EXACT translation from ir_Hitachi.cpp:1490-1494
    def stateReset(self) -> None:
        super().stateReset()
        self._.remote_state[37] = 0x00
        self._.remote_state[39] = 0x00

    ## Set the internal state from a valid code for this protocol.
    ## EXACT translation from ir_Hitachi.cpp:1507-1509
    def setRaw(self, new_code: List[int], length: int = kHitachiAc344StateLength) -> None:
        for i in range(min(length, kHitachiAc344StateLength)):
            self._.remote_state[i] = new_code[i]

    ## Control the vertical swing setting.
    ## EXACT translation from ir_Hitachi.cpp:1513-1516
    def setSwingV(self, on: bool) -> None:
        self.setSwingVToggle(on)  # Set the button value.
        self._.SwingV = on

    ## Get the current vertical swing setting.
    ## EXACT translation from ir_Hitachi.cpp:1520-1522
    def getSwingV(self) -> bool:
        return bool(self._.SwingV)

    ## Control the horizontal swing setting.
    ## EXACT translation from ir_Hitachi.cpp:1526-1532
    def setSwingH(self, position: int) -> None:
        if position > kHitachiAc344SwingHLeftMax:
            self._.SwingH = kHitachiAc344SwingHMiddle
        else:
            self._.SwingH = position
        self.setButton(kHitachiAc344ButtonSwingH)

    ## Get the current horizontal swing setting.
    ## EXACT translation from ir_Hitachi.cpp:1536-1538
    def getSwingH(self) -> int:
        return self._.SwingH


#####################################################################
# HitachiAC264 (264-bit / 33-byte) Protocol
#####################################################################


## Send a Hitachi 33-byte/264-bit A/C message (HITACHI_AC264)
## Basically the same as sendHitachiAC() except different size.
## Status: STABLE / Reported as working.
## EXACT translation from IRremoteESP8266 IRsend::sendHitachiAc264 (ir_Hitachi.cpp:1609-1614)
def sendHitachiAc264(data: List[int], nbytes: int, repeat: int = 0) -> List[int]:
    """
    Send a Hitachi 33-byte/264-bit A/C message.
    EXACT translation from IRremoteESP8266 IRsend::sendHitachiAc264
    """
    if nbytes < kHitachiAc264StateLength:
        return []  # Not enough bytes to send a proper message.
    return sendHitachiAC(data, nbytes, repeat)


## Class for handling detailed Hitachi_AC264 33 byte A/C messages.
## EXACT translation from IRremoteESP8266 IRHitachiAc264 class (ir_Hitachi.cpp:1621-1704)
class IRHitachiAc264(IRHitachiAc424):
    ## Class constructor for handling detailed Hitachi_AC264 33 byte A/C messages.
    ## EXACT translation from ir_Hitachi.cpp:1621-1623
    def __init__(self) -> None:
        super().__init__()
        self.stateReset()

    ## Reset the internal state to auto fan, cooling, 23 Celsius
    ## EXACT translation from ir_Hitachi.cpp:1626-1630
    def stateReset(self) -> None:
        super().stateReset()
        self._.remote_state[9] = 0x92
        self._.remote_state[27] = 0xC1

    ## Set the internal state from a valid code for this protocol.
    ## EXACT translation from ir_Hitachi.cpp:1643-1645
    def setRaw(self, new_code: List[int], length: int = kHitachiAc264StateLength) -> None:
        for i in range(min(length, kHitachiAc264StateLength)):
            self._.remote_state[i] = new_code[i]

    ## Set the speed of the fan.
    ## EXACT translation from ir_Hitachi.cpp:1649-1660
    def setFan(self, speed: int) -> None:
        if speed in [
            kHitachiAc264FanMin,
            kHitachiAc264FanMedium,
            kHitachiAc264FanHigh,
            kHitachiAc264FanAuto,
        ]:
            self._.Fan = speed
        else:
            self.setFan(kHitachiAc264FanAuto)


#####################################################################
# HitachiAC296 (296-bit / 37-byte) Protocol
#####################################################################


## Native representation of a HitachiAC296 37-byte/296-bit A/C message.
## EXACT translation from IRremoteESP8266 HitachiAC296Protocol (ir_Hitachi.h:300-343)
class HitachiAC296Protocol:
    def __init__(self):
        # The state array (37 bytes for HitachiAC296)
        self.remote_state = [0] * kHitachiAc296StateLength

    # Byte 13 - Temp (5 bits starting at bit 2, LSB)
    @property
    def Temp(self) -> int:
        return (self.remote_state[13] >> 2) & 0x1F

    @Temp.setter
    def Temp(self, value: int) -> None:
        self.remote_state[13] = (self.remote_state[13] & 0x83) | ((value & 0x1F) << 2)

    # Byte 25 - Mode (4 bits) & Fan (3 bits)
    @property
    def Mode(self) -> int:
        return self.remote_state[25] & 0x0F

    @Mode.setter
    def Mode(self, value: int) -> None:
        self.remote_state[25] = (self.remote_state[25] & 0xF0) | (value & 0x0F)

    @property
    def Fan(self) -> int:
        return (self.remote_state[25] >> 4) & 0x07

    @Fan.setter
    def Fan(self, value: int) -> None:
        self.remote_state[25] = (self.remote_state[25] & 0x8F) | ((value & 0x07) << 4)

    # Byte 27 - Power (bit 4)
    @property
    def Power(self) -> int:
        return (self.remote_state[27] >> 4) & 0x01

    @Power.setter
    def Power(self, value: bool) -> None:
        if value:
            self.remote_state[27] |= 0x10
        else:
            self.remote_state[27] &= 0xEF


## Send a HitachiAc 37-byte/296-bit A/C message (HITACHI_AC296)
## Status: STABLE / Working on a real device.
## EXACT translation from IRremoteESP8266 IRsend::sendHitachiAc296 (ir_Hitachi.cpp:1717-1723)
def sendHitachiAc296(data: List[int], nbytes: int, repeat: int = 0) -> List[int]:
    """
    Send a HitachiAc 37-byte/296-bit A/C message.
    EXACT translation from IRremoteESP8266 IRsend::sendHitachiAc296
    """
    if nbytes < kHitachiAc296StateLength:
        return []  # Not enough bytes to send a proper message.
    return sendHitachiAC(data, nbytes, repeat)


## Class for handling detailed Hitachi_AC296 37 byte A/C messages.
## EXACT translation from IRremoteESP8266 IRHitachiAc296 class (ir_Hitachi.cpp:1730-1964)
class IRHitachiAc296:
    ## Class Constructor for handling detailed Hitachi_AC296 37 byte A/C messages.
    ## EXACT translation from ir_Hitachi.cpp:1730-1732
    def __init__(self) -> None:
        self._: HitachiAC296Protocol = HitachiAC296Protocol()
        self.stateReset()

    ## Reset the internal state to auto fan, heating, & 24 Celsius
    ## EXACT translation from ir_Hitachi.cpp:1735-1765
    def stateReset(self) -> None:
        # Header
        self._.remote_state[0] = 0x01
        self._.remote_state[1] = 0x10
        self._.remote_state[2] = 0x00

        # Every next byte is a parity byte
        self._.remote_state[3] = 0x40
        self._.remote_state[5] = 0xFF
        self._.remote_state[7] = 0xCC
        self._.remote_state[9] = 0x92
        self._.remote_state[11] = 0x43
        # 13-14 is Temperature and parity
        self._.remote_state[15] = 0x00
        self._.remote_state[17] = 0x00  # Off timer LSB
        self._.remote_state[19] = 0x00  # Off timer cont
        self._.remote_state[21] = 0x00  # On timer LSB
        self._.remote_state[23] = 0x00  # On timer cont
        # 25-26 is Mode and fan
        self._.remote_state[27] = 0xF1  # Power on
        self._.remote_state[29] = 0x00
        self._.remote_state[31] = 0x00
        self._.remote_state[33] = 0x00
        self._.remote_state[35] = 0x03  # Humidity

        self.setTemp(24)
        self.setMode(kHitachiAc296Heat)
        self.setFan(kHitachiAc296FanAuto)

        self.setInvertedStates()

    ## Update the internal consistency check for the protocol.
    ## EXACT translation from ir_Hitachi.cpp:1768-1770
    def setInvertedStates(self) -> None:
        invertBytePairs(self._.remote_state[3:], kHitachiAc296StateLength - 3)

    ## Check if every second byte of the state, after the fixed header
    ##   is inverted to the previous byte.
    ## EXACT translation from ir_Hitachi.cpp:1777-1780
    @staticmethod
    def hasInvertedStates(state: List[int], length: int) -> bool:
        return IRHitachiAc3.hasInvertedStates(state, length)

    ## Get the value of the current power setting.
    ## EXACT translation from ir_Hitachi.cpp:1795
    def getPower(self) -> bool:
        return bool(self._.Power)

    ## Change the power setting.
    ## EXACT translation from ir_Hitachi.cpp:1799
    def setPower(self, on: bool) -> None:
        self._.Power = on

    ## Change the power setting to On.
    ## EXACT translation from ir_Hitachi.cpp:1802
    def on(self) -> None:
        self.setPower(True)

    ## Change the power setting to Off.
    ## EXACT translation from ir_Hitachi.cpp:1805
    def off(self) -> None:
        self.setPower(False)

    ## Get the operating mode setting of the A/C.
    ## EXACT translation from ir_Hitachi.cpp:1809
    def getMode(self) -> int:
        return self._.Mode

    ## Set the operating mode of the A/C.
    ## EXACT translation from ir_Hitachi.cpp:1813-1826
    def setMode(self, mode: int) -> None:
        if mode in [
            kHitachiAc296Heat,
            kHitachiAc296Cool,
            kHitachiAc296Dehumidify,
            kHitachiAc296AutoDehumidifying,
            kHitachiAc296Auto,
        ]:
            self._.Mode = mode
            self.setTemp(self.getTemp())  # Reset the temp to handle "Auto"'s special temp.
        else:
            self.setMode(kHitachiAc296Auto)

    ## Get the current temperature setting.
    ## EXACT translation from ir_Hitachi.cpp:1856
    def getTemp(self) -> int:
        return self._.Temp

    ## Set the temperature.
    ## EXACT translation from ir_Hitachi.cpp:1860-1869
    def setTemp(self, celsius: int) -> None:
        temp = celsius
        if self.getMode() == kHitachiAc296Auto:
            # Special temp for auto mode
            temp = kHitachiAc296TempAuto
        else:
            # Normal temp setting.
            temp = min(temp, kHitachiAc296MaxTemp)
            temp = max(temp, kHitachiAc296MinTemp)
        self._.Temp = temp

    ## Get the current fan speed setting.
    ## EXACT translation from ir_Hitachi.cpp:1873
    def getFan(self) -> int:
        return self._.Fan

    ## Set the speed of the fan.
    ## EXACT translation from ir_Hitachi.cpp:1877-1880
    def setFan(self, speed: int) -> None:
        newSpeed = max(speed, kHitachiAc296FanSilent)
        self._.Fan = min(newSpeed, kHitachiAc296FanAuto)

    ## Get a PTR to the internal state/code for this protocol.
    ## EXACT translation from ir_Hitachi.cpp:1911-1914
    def getRaw(self) -> List[int]:
        self.setInvertedStates()
        return self._.remote_state

    ## Set the internal state from a valid code for this protocol.
    ## EXACT translation from ir_Hitachi.cpp:1919-1921
    def setRaw(self, new_code: List[int], length: int = kHitachiAc296StateLength) -> None:
        for i in range(min(length, kHitachiAc296StateLength)):
            self._.remote_state[i] = new_code[i]


#####################################################################
# DECODE Functions
#####################################################################


## Decode the supplied Hitachi A/C message.
## Status: STABLE / Expected to work.
## EXACT translation from IRremoteESP8266 IRrecv::decodeHitachiAC (ir_Hitachi.cpp:857-933)
def decodeHitachiAC(
    results,
    offset: int = 1,
    nbits: int = kHitachiAcBits,
    strict: bool = True,
    MSBfirst: bool = True,
) -> bool:
    """
    Decode the supplied Hitachi A/C message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeHitachiAC
    """
    # Import here to avoid circular imports
    from app.core.ir_protocols.ir_recv import _matchGeneric

    k_tolerance = 25 + 5  # _tolerance + 5

    # EXACT translation from ir_Hitachi.cpp:862-873
    if strict:
        if nbits not in [
            kHitachiAcBits,
            kHitachiAc1Bits,
            kHitachiAc2Bits,
            kHitachiAc264Bits,
            kHitachiAc344Bits,
        ]:
            return False  # Not strictly a Hitachi message.

    # EXACT translation from ir_Hitachi.cpp:874-882
    if nbits == kHitachiAc1Bits:
        hmark = kHitachiAc1HdrMark
        hspace = kHitachiAc1HdrSpace
    else:
        hmark = kHitachiAcHdrMark
        hspace = kHitachiAcHdrSpace

    # Match Header + Data + Footer (EXACT translation from ir_Hitachi.cpp:884-890)
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state,
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=nbits,
        hdrmark=hmark,
        hdrspace=hspace,
        onemark=kHitachiAcBitMark,
        onespace=kHitachiAcOneSpace,
        zeromark=kHitachiAcBitMark,
        zerospace=kHitachiAcZeroSpace,
        footermark=kHitachiAcBitMark,
        footerspace=kHitachiAcMinGap,
        atleast=True,
        tolerance=k_tolerance,
        excess=kMarkExcess,
        MSBfirst=MSBfirst,
    )
    if used == 0:
        return False

    # Compliance (EXACT translation from ir_Hitachi.cpp:893-908)
    if strict:
        nbytes = nbits // 8
        if nbytes == kHitachiAcStateLength:
            if not IRHitachiAc.validChecksum(results.state, nbytes):
                return False
        elif nbytes == kHitachiAc1StateLength:
            if not IRHitachiAc1.validChecksum(results.state, nbytes):
                return False
        elif nbytes in [kHitachiAc264StateLength, kHitachiAc344StateLength]:
            if not IRHitachiAc3.hasInvertedStates(results.state, nbytes):
                return False

    # Success (EXACT translation from ir_Hitachi.cpp:911-928)
    # Use enum values for proper protocol identification
    from app.core.ir_protocols.ir_dispatcher import decode_type_t

    if nbits == kHitachiAc1Bits:
        results.decode_type = decode_type_t.HITACHI_AC1
    elif nbits == kHitachiAc2Bits:
        results.decode_type = decode_type_t.HITACHI_AC2
    elif nbits == kHitachiAc264Bits:
        results.decode_type = decode_type_t.HITACHI_AC264
    elif nbits == kHitachiAc344Bits:
        results.decode_type = decode_type_t.HITACHI_AC344
    else:
        results.decode_type = decode_type_t.HITACHI_AC

    results.bits = nbits
    return True


## Decode the supplied Hitachi 53-byte/424-bit A/C message.
## Status: STABLE / Reported as working.
## EXACT translation from IRremoteESP8266 IRrecv::decodeHitachiAc424 (ir_Hitachi.cpp:978-1008)
def decodeHitachiAc424(
    results, offset: int = 1, nbits: int = kHitachiAc424Bits, strict: bool = True
) -> bool:
    """
    Decode the supplied Hitachi 53-byte/424-bit A/C message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeHitachiAc424
    """
    # Import here to avoid circular imports
    from app.core.ir_protocols.ir_recv import matchMark, matchSpace, _matchGeneric

    # EXACT translation from ir_Hitachi.cpp:981-984
    if results.rawlen < 2 * nbits + kHeader + kHeader + kFooter - 1 + offset:
        return False  # Too short a message to match.
    if strict and nbits != kHitachiAc424Bits:
        return False

    # Leader (EXACT translation from ir_Hitachi.cpp:989-992)
    if not matchMark(results.rawbuf[offset], kHitachiAc424LdrMark):
        return False
    offset += 1
    if not matchSpace(results.rawbuf[offset], kHitachiAc424LdrSpace):
        return False
    offset += 1

    # Header + Data + Footer (EXACT translation from ir_Hitachi.cpp:995-1002)
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state,
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=nbits,
        hdrmark=kHitachiAc424HdrMark,
        hdrspace=kHitachiAc424HdrSpace,
        onemark=kHitachiAc424BitMark,
        onespace=kHitachiAc424OneSpace,
        zeromark=kHitachiAc424BitMark,
        zerospace=kHitachiAc424ZeroSpace,
        footermark=kHitachiAc424BitMark,
        footerspace=kHitachiAcMinGap,
        atleast=True,
        tolerance=kUseDefTol,
        excess=0,
        MSBfirst=False,
    )
    if used == 0:
        return False  # We failed to find any data.

    # Success (EXACT translation from ir_Hitachi.cpp:1005-1007)
    from app.core.ir_protocols.ir_dispatcher import decode_type_t

    results.decode_type = decode_type_t.HITACHI_AC424
    results.bits = nbits
    return True


## Decode the supplied Hitachi 15to27-byte/120to216-bit A/C message.
## Status: STABLE / Works fine.
## EXACT translation from IRremoteESP8266 IRrecv::decodeHitachiAc3 (ir_Hitachi.cpp:1443-1478)
def decodeHitachiAc3(
    results, offset: int = 1, nbits: int = kHitachiAc3Bits, strict: bool = True
) -> bool:
    """
    Decode the supplied Hitachi 15to27-byte/120to216-bit A/C message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeHitachiAc3
    """
    # Import here to avoid circular imports
    from app.core.ir_protocols.ir_recv import _matchGeneric

    # EXACT translation from ir_Hitachi.cpp:1446-1459
    if results.rawlen < 2 * nbits + kHeader + kFooter - 1 + offset:
        return False  # Too short a message to match.
    if strict:
        # Check the requested bit length.
        if nbits not in [
            kHitachiAc3MinBits,  # Cancel Timer (Min Size)
            kHitachiAc3MinBits + 2 * 8,  # Change Temp
            kHitachiAc3Bits - 6 * 8,  # Change Mode
            kHitachiAc3Bits - 4 * 8,  # Normal
            kHitachiAc3Bits,
        ]:  # Set Temp (Max Size)
            return False

    # Header + Data + Footer (EXACT translation from ir_Hitachi.cpp:1462-1469)
    if not _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state,
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=nbits,
        hdrmark=kHitachiAc3HdrMark,
        hdrspace=kHitachiAc3HdrSpace,
        onemark=kHitachiAc3BitMark,
        onespace=kHitachiAc3OneSpace,
        zeromark=kHitachiAc3BitMark,
        zerospace=kHitachiAc3ZeroSpace,
        footermark=kHitachiAc3BitMark,
        footerspace=kHitachiAcMinGap,
        atleast=True,
        tolerance=kUseDefTol,
        excess=0,
        MSBfirst=False,
    ):
        return False  # We failed to find any data.

    # Compliance (EXACT translation from ir_Hitachi.cpp:1472-1473)
    if strict and not IRHitachiAc3.hasInvertedStates(results.state, nbits // 8):
        return False

    # Success (EXACT translation from ir_Hitachi.cpp:1475-1477)
    from app.core.ir_protocols.ir_dispatcher import decode_type_t

    results.decode_type = decode_type_t.HITACHI_AC3
    results.bits = nbits
    return True


## Decode the supplied Hitachi 37-byte A/C message.
## Status: STABLE / Working on a real device.
## EXACT translation from IRremoteESP8266 IRrecv::decodeHitachiAc296 (ir_Hitachi.cpp:1976-1995)
def decodeHitachiAc296(
    results, offset: int = 1, nbits: int = kHitachiAc296Bits, strict: bool = True
) -> bool:
    """
    Decode the supplied Hitachi 37-byte A/C message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeHitachiAc296
    """
    # Import here to avoid circular imports
    from app.core.ir_protocols.ir_recv import _matchGeneric

    # EXACT translation from ir_Hitachi.cpp:1979-1985
    if not _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state,
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=nbits,
        hdrmark=kHitachiAcHdrMark,
        hdrspace=kHitachiAcHdrSpace,
        onemark=kHitachiAcBitMark,
        onespace=kHitachiAcOneSpace,
        zeromark=kHitachiAcBitMark,
        zerospace=kHitachiAcZeroSpace,
        footermark=kHitachiAcBitMark,
        footerspace=kHitachiAcMinGap,
        atleast=True,
        tolerance=kUseDefTol,
        excess=0,
        MSBfirst=False,
    ):
        return False

    # Compliance (EXACT translation from ir_Hitachi.cpp:1988-1989)
    if strict and not IRHitachiAc296.hasInvertedStates(results.state, nbits // 8):
        return False

    # Success (EXACT translation from ir_Hitachi.cpp:1992-1994)
    from app.core.ir_protocols.ir_dispatcher import decode_type_t

    results.decode_type = decode_type_t.HITACHI_AC296
    results.bits = nbits
    return True
