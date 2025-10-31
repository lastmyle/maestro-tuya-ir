# Copyright 2018-2022 David Conran
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Carrier protocols.
## @see CarrierAc https://github.com/crankyoldgit/IRremoteESP8266/issues/385
## @see CarrierAc64 https://github.com/crankyoldgit/IRremoteESP8266/issues/1127
## @see CarrierAc128 https://github.com/crankyoldgit/IRremoteESP8266/issues/1797
## Direct translation from IRremoteESP8266 ir_Carrier.cpp and ir_Carrier.h

from typing import List

# Supports:
#   Brand: Carrier/Surrey,  Model: 42QG5A55970 remote
#   Brand: Carrier/Surrey,  Model: 619EGX0090E0 A/C
#   Brand: Carrier/Surrey,  Model: 619EGX0120E0 A/C
#   Brand: Carrier/Surrey,  Model: 619EGX0180E0 A/C
#   Brand: Carrier/Surrey,  Model: 619EGX0220E0 A/C
#   Brand: Carrier/Surrey,  Model: 53NGK009/012 Inverter
#   Brand: Carrier,  Model: 40GKX0E2006 remote (CARRIER_AC128)
#   Brand: Carrier,  Model: 3021203 RR03-S-Remote (CARRIER_AC84)
#   Brand: Carrier,  Model: 342WM100CT A/C (CARRIER_AC84)

# Constants
# EXACT translation from IRremoteESP8266 ir_Carrier.cpp:25-67
kCarrierAcHdrMark = 8532
kCarrierAcHdrSpace = 4228
kCarrierAcBitMark = 628
kCarrierAcOneSpace = 1320
kCarrierAcZeroSpace = 532
kCarrierAcGap = 20000
kCarrierAcFreq = 38  # kHz. (An educated guess)

kCarrierAc40HdrMark = 8402
kCarrierAc40HdrSpace = 4166
kCarrierAc40BitMark = 547
kCarrierAc40OneSpace = 1540
kCarrierAc40ZeroSpace = 497
kCarrierAc40Gap = 150000
# @see https://github.com/crankyoldgit/IRremoteESP8266/issues/1190#issuecomment-643380155

kCarrierAc64HdrMark = 8940
kCarrierAc64HdrSpace = 4556
kCarrierAc64BitMark = 503
kCarrierAc64OneSpace = 1736
kCarrierAc64ZeroSpace = 615
kCarrierAc64Gap = 100000  # kDefaultMessageGap - A guess.

# @see: https://github.com/crankyoldgit/IRremoteESP8266/issues/1943#issue-1519570772
kCarrierAc84HdrMark = 5850
kCarrierAc84Zero = 1175
kCarrierAc84One = 430
kCarrierAc84HdrSpace = kCarrierAc84Zero
kCarrierAc84Gap = 100000  # kDefaultMessageGap - A guess.
kCarrierAc84ExtraBits = 4
kCarrierAc84ExtraTolerance = 5

kCarrierAc128HdrMark = 4600
kCarrierAc128HdrSpace = 2600
kCarrierAc128Hdr2Mark = 9300
kCarrierAc128Hdr2Space = 5000
kCarrierAc128BitMark = 340
kCarrierAc128OneSpace = 1000
kCarrierAc128ZeroSpace = 400
kCarrierAc128SectionGap = 20600
kCarrierAc128InterSpace = 6700
kCarrierAc128SectionBits = 64  # kCarrierAc128Bits / 2

# EXACT translation from IRremoteESP8266 ir_Carrier.h:70-84
# CARRIER_AC64
kCarrierAc64ChecksumOffset = 16
kCarrierAc64ChecksumSize = 4
kCarrierAc64Heat = 0b01  # 1
kCarrierAc64Cool = 0b10  # 2
kCarrierAc64Fan = 0b11  # 3
kCarrierAc64FanAuto = 0b00  # 0
kCarrierAc64FanLow = 0b01  # 1
kCarrierAc64FanMedium = 0b10  # 2
kCarrierAc64FanHigh = 0b11  # 3
kCarrierAc64MinTemp = 16  # Celsius
kCarrierAc64MaxTemp = 30  # Celsius
kCarrierAc64TimerMax = 9  # Hours.
kCarrierAc64TimerMin = 1  # Hours.

# State length constants (from IRremoteESP8266.h)
kCarrierAcBits = 32
kCarrierAc40Bits = 40
kCarrierAc64Bits = 64
kCarrierAc84Bits = 84
kCarrierAc128Bits = 128
kCarrierAc128StateLength = 16


## Send a Carrier HVAC formatted message.
## Status: STABLE / Works on real devices.
## @param[in] data The message to be sent.
## @param[in] nbits The number of bits of message to be sent.
## @param[in] repeat The number of times the command is to be repeated.
## EXACT translation from IRremoteESP8266 ir_Carrier.cpp:69-88
def sendCarrierAC(data: int, nbits: int = kCarrierAcBits, repeat: int = 0) -> List[int]:
    """
    Send a Carrier HVAC formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendCarrierAC (ir_Carrier.cpp:75-87)

    Returns timing array instead of transmitting via hardware.
    """
    from app.core.ir_protocols.ir_send import sendGeneric, sendGenericUint64

    def invertBits(data, nbits):
        """Invert bits in data"""
        result = 0
        for i in range(nbits):
            result <<= 1
            result |= (data & 1) ^ 1
            data >>= 1
        return result

    all_timings = []

    for r in range(repeat + 1):
        temp_data = data
        # Carrier sends the data block three times. normal + inverted + normal.
        for i in range(3):
            timings = sendGenericUint64(
                headermark=kCarrierAcHdrMark,
                headerspace=kCarrierAcHdrSpace,
                onemark=kCarrierAcBitMark,
                onespace=kCarrierAcOneSpace,
                zeromark=kCarrierAcBitMark,
                zerospace=kCarrierAcZeroSpace,
                footermark=kCarrierAcBitMark,
                gap=kCarrierAcGap,
                dataint=temp_data,
                nbits=nbits,
                MSBfirst=True,
            )
            all_timings.extend(timings)
            temp_data = invertBits(temp_data, nbits)

    return all_timings


## Decode the supplied Carrier HVAC message.
## @note Carrier HVAC messages contain only 32 bits, but it is sent three(3)
##   times. i.e. normal + inverted + normal
## Status: BETA / Probably works.
## @param[in,out] results Ptr to the data to decode & where to store the decode
##   result.
## @param[in] offset The starting index to use when attempting to decode the
##   raw data. Typically/Defaults to kStartOffset.
## @param[in] nbits The number of data bits to expect.
## @param[in] strict Flag indicating if we should perform strict matching.
## @return A boolean. True if it can decode it, false if it can't.
## EXACT translation from IRremoteESP8266 ir_Carrier.cpp:90-139
def decodeCarrierAC(
    results, offset: int = 1, nbits: int = kCarrierAcBits, strict: bool = True
) -> bool:
    """
    Decode the supplied Carrier HVAC message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeCarrierAC (ir_Carrier.cpp:102-138)
    """
    from app.core.ir_protocols.ir_recv import _matchGeneric, kHeader, kFooter

    def invertBits(data, nbits):
        """Invert bits in data"""
        result = 0
        for i in range(nbits):
            result <<= 1
            result |= (data & 1) ^ 1
            data >>= 1
        return result

    if results.rawlen < ((2 * nbits + kHeader + kFooter) * 3) - 1 + offset:
        return False  # Can't possibly be a valid Carrier message.
    if strict and nbits != kCarrierAcBits:
        return False  # We expect Carrier to be 32 bits of message.

    data = 0
    prev_data = 0

    for i in range(3):
        prev_data = data
        # Match Header + Data + Footer
        data = _matchGeneric(
            data_ptr=results.rawbuf[offset:],
            result_bits_ptr=None,
            result_bytes_ptr=None,
            use_bits=True,
            remaining=results.rawlen - offset,
            nbits=nbits,
            hdrmark=kCarrierAcHdrMark,
            hdrspace=kCarrierAcHdrSpace,
            onemark=kCarrierAcBitMark,
            onespace=kCarrierAcOneSpace,
            zeromark=kCarrierAcBitMark,
            zerospace=kCarrierAcZeroSpace,
            footermark=kCarrierAcBitMark,
            footerspace=kCarrierAcGap,
            atleast=True,
            tolerance=25,
            excess=50,
            MSBfirst=True,
        )
        if not data:
            return False
        offset += _matchGeneric(  # Get the actual offset used
            data_ptr=results.rawbuf[offset:],
            result_bits_ptr=None,
            result_bytes_ptr=None,
            use_bits=False,
            remaining=results.rawlen - offset,
            nbits=nbits,
            hdrmark=kCarrierAcHdrMark,
            hdrspace=kCarrierAcHdrSpace,
            onemark=kCarrierAcBitMark,
            onespace=kCarrierAcOneSpace,
            zeromark=kCarrierAcBitMark,
            zerospace=kCarrierAcZeroSpace,
            footermark=kCarrierAcBitMark,
            footerspace=kCarrierAcGap,
            atleast=True,
            tolerance=25,
            excess=50,
            MSBfirst=True,
        )
        # Compliance.
        if strict:
            # Check if the data is an inverted copy of the previous data.
            if i > 0 and prev_data != invertBits(data, nbits):
                return False

    # Success
    results.bits = nbits
    results.value = data
    # results.decode_type = CARRIER_AC
    results.address = data >> 16
    results.command = data & 0xFFFF
    return True


## Send a Carrier 40bit HVAC formatted message.
## Status: STABLE / Tested against a real device.
## @param[in] data The message to be sent.
## @param[in] nbits The bit size of the message being sent.
## @param[in] repeat The number of times the message is to be repeated.
## EXACT translation from IRremoteESP8266 ir_Carrier.cpp:141-154
def sendCarrierAC40(data: int, nbits: int = kCarrierAc40Bits, repeat: int = 0) -> List[int]:
    """
    Send a Carrier 40bit HVAC formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendCarrierAC40 (ir_Carrier.cpp:147-153)

    Returns timing array instead of transmitting via hardware.
    """
    from app.core.ir_protocols.ir_send import sendGeneric, sendGenericUint64

    return sendGenericUint64(
        headermark=kCarrierAc40HdrMark,
        headerspace=kCarrierAc40HdrSpace,
        onemark=kCarrierAc40BitMark,
        onespace=kCarrierAc40OneSpace,
        zeromark=kCarrierAc40BitMark,
        zerospace=kCarrierAc40ZeroSpace,
        footermark=kCarrierAc40BitMark,
        gap=kCarrierAc40Gap,
        dataint=data,
        nbits=nbits,
        MSBfirst=True,
    )


## Decode the supplied Carrier 40-bit HVAC message.
## Carrier HVAC messages contain only 40 bits, but it is sent three(3) times.
## Status: STABLE / Tested against a real device.
## @param[in,out] results Ptr to the data to decode & where to store the decode
##   result.
## @param[in] offset The starting index to use when attempting to decode the
##   raw data. Typically/Defaults to kStartOffset.
## @param[in] nbits The number of data bits to expect.
## @param[in] strict Flag indicating if we should perform strict matching.
## @return A boolean. True if it can decode it, false if it can't.
## EXACT translation from IRremoteESP8266 ir_Carrier.cpp:156-188
def decodeCarrierAC40(
    results, offset: int = 1, nbits: int = kCarrierAc40Bits, strict: bool = True
) -> bool:
    """
    Decode the supplied Carrier 40-bit HVAC message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeCarrierAC40 (ir_Carrier.cpp:167-187)
    """
    from app.core.ir_protocols.ir_recv import _matchGeneric, kHeader, kFooter

    if results.rawlen < 2 * nbits + kHeader + kFooter - 1 + offset:
        return False  # Can't possibly be a valid Carrier message.
    if strict and nbits != kCarrierAc40Bits:
        return False  # We expect Carrier to be 40 bits of message.

    value = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=None,
        use_bits=True,
        remaining=results.rawlen - offset,
        nbits=nbits,
        hdrmark=kCarrierAc40HdrMark,
        hdrspace=kCarrierAc40HdrSpace,
        onemark=kCarrierAc40BitMark,
        onespace=kCarrierAc40OneSpace,
        zeromark=kCarrierAc40BitMark,
        zerospace=kCarrierAc40ZeroSpace,
        footermark=kCarrierAc40BitMark,
        footerspace=kCarrierAc40Gap,
        atleast=True,
        tolerance=25,
        excess=50,
        MSBfirst=True,
    )
    if not value:
        return False

    # Success
    results.bits = nbits
    results.value = value
    # results.decode_type = CARRIER_AC40
    results.address = 0
    results.command = 0
    return True


## Send a Carrier 64bit HVAC formatted message.
## Status: STABLE / Known to be working.
## @param[in] data The message to be sent.
## @param[in] nbits The bit size of the message being sent.
## @param[in] repeat The number of times the message is to be repeated.
## EXACT translation from IRremoteESP8266 ir_Carrier.cpp:190-203
def sendCarrierAC64(data: int, nbits: int = kCarrierAc64Bits, repeat: int = 0) -> List[int]:
    """
    Send a Carrier 64bit HVAC formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendCarrierAC64 (ir_Carrier.cpp:196-202)

    Returns timing array instead of transmitting via hardware.
    """
    from app.core.ir_protocols.ir_send import sendGeneric, sendGenericUint64

    return sendGenericUint64(
        headermark=kCarrierAc64HdrMark,
        headerspace=kCarrierAc64HdrSpace,
        onemark=kCarrierAc64BitMark,
        onespace=kCarrierAc64OneSpace,
        zeromark=kCarrierAc64BitMark,
        zerospace=kCarrierAc64ZeroSpace,
        footermark=kCarrierAc64BitMark,
        gap=kCarrierAc64Gap,
        dataint=data,
        nbits=nbits,
        MSBfirst=False,
    )


## Decode the supplied Carrier 64-bit HVAC message.
## Status: STABLE / Known to be working.
## @param[in,out] results Ptr to the data to decode & where to store the decode
##   result.
## @param[in] offset The starting index to use when attempting to decode the
##   raw data. Typically/Defaults to kStartOffset.
## @param[in] nbits The number of data bits to expect.
## @param[in] strict Flag indicating if we should perform strict matching.
## @return A boolean. True if it can decode it, false if it can't.
## EXACT translation from IRremoteESP8266 ir_Carrier.cpp:205-240
def decodeCarrierAC64(
    results, offset: int = 1, nbits: int = kCarrierAc64Bits, strict: bool = True
) -> bool:
    """
    Decode the supplied Carrier 64-bit HVAC message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeCarrierAC64 (ir_Carrier.cpp:215-239)
    """
    from app.core.ir_protocols.ir_recv import _matchGeneric, kHeader, kFooter

    if results.rawlen < 2 * nbits + kHeader + kFooter - 1 + offset:
        return False  # Can't possibly be a valid Carrier message.
    if strict and nbits != kCarrierAc64Bits:
        return False  # We expect Carrier to be 64 bits of message.

    value = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=None,
        use_bits=True,
        remaining=results.rawlen - offset,
        nbits=nbits,
        hdrmark=kCarrierAc64HdrMark,
        hdrspace=kCarrierAc64HdrSpace,
        onemark=kCarrierAc64BitMark,
        onespace=kCarrierAc64OneSpace,
        zeromark=kCarrierAc64BitMark,
        zerospace=kCarrierAc64ZeroSpace,
        footermark=kCarrierAc64BitMark,
        footerspace=kCarrierAc64Gap,
        atleast=True,
        tolerance=25,
        excess=50,
        MSBfirst=False,
    )
    if not value:
        return False

    # Compliance
    if strict and not IRCarrierAc64.validChecksum(value):
        return False

    # Success
    results.bits = nbits
    results.value = value
    # results.decode_type = CARRIER_AC64
    results.address = 0
    results.command = 0
    return True


## Native representation of a Carrier A/C message.
## EXACT translation from IRremoteESP8266 ir_Carrier.h:35-66
class CarrierProtocol:
    def __init__(self):
        self.raw = 0  # The state of the IR remote (64-bit).

    # Byte 2
    @property
    def Sum(self) -> int:
        return (self.raw >> 16) & 0x0F

    @Sum.setter
    def Sum(self, value: int) -> None:
        self.raw = (self.raw & 0xFFFFFFFFFFF0FFFF) | ((value & 0x0F) << 16)

    @property
    def Mode(self) -> int:
        return (self.raw >> 20) & 0x03

    @Mode.setter
    def Mode(self, value: int) -> None:
        self.raw = (self.raw & 0xFFFFFFFFFFCFFFFF) | ((value & 0x03) << 20)

    @property
    def Fan(self) -> int:
        return (self.raw >> 22) & 0x03

    @Fan.setter
    def Fan(self, value: int) -> None:
        self.raw = (self.raw & 0xFFFFFFFFFF3FFFFF) | ((value & 0x03) << 22)

    # Byte 3
    @property
    def Temp(self) -> int:
        return (self.raw >> 24) & 0x0F

    @Temp.setter
    def Temp(self, value: int) -> None:
        self.raw = (self.raw & 0xFFFFFFFFF0FFFFFF) | ((value & 0x0F) << 24)

    @property
    def SwingV(self) -> int:
        return (self.raw >> 29) & 0x01

    @SwingV.setter
    def SwingV(self, value: bool) -> None:
        if value:
            self.raw |= 1 << 29
        else:
            self.raw &= ~(1 << 29)

    # Byte 4
    @property
    def Power(self) -> int:
        return (self.raw >> 36) & 0x01

    @Power.setter
    def Power(self, value: bool) -> None:
        if value:
            self.raw |= 1 << 36
        else:
            self.raw &= ~(1 << 36)

    @property
    def OffTimerEnable(self) -> int:
        return (self.raw >> 37) & 0x01

    @OffTimerEnable.setter
    def OffTimerEnable(self, value: bool) -> None:
        if value:
            self.raw |= 1 << 37
        else:
            self.raw &= ~(1 << 37)

    @property
    def OnTimerEnable(self) -> int:
        return (self.raw >> 38) & 0x01

    @OnTimerEnable.setter
    def OnTimerEnable(self, value: bool) -> None:
        if value:
            self.raw |= 1 << 38
        else:
            self.raw &= ~(1 << 38)

    @property
    def Sleep(self) -> int:
        return (self.raw >> 39) & 0x01

    @Sleep.setter
    def Sleep(self, value: bool) -> None:
        if value:
            self.raw |= 1 << 39
        else:
            self.raw &= ~(1 << 39)

    # Byte 6
    @property
    def OnTimer(self) -> int:
        return (self.raw >> 52) & 0x0F

    @OnTimer.setter
    def OnTimer(self, value: int) -> None:
        self.raw = (self.raw & 0xFFFFFFF0FFFFFFFF) | ((value & 0x0F) << 52)

    # Byte 7
    @property
    def OffTimer(self) -> int:
        return (self.raw >> 60) & 0x0F

    @OffTimer.setter
    def OffTimer(self, value: int) -> None:
        self.raw = (self.raw & 0xF0FFFFFFFFFFFFFF) | ((value & 0x0F) << 60)


## Class for handling detailed Carrier 64 bit A/C messages.
## EXACT translation from IRremoteESP8266 ir_Carrier.h and ir_Carrier.cpp
class IRCarrierAc64:
    ## Class Constructor
    ## EXACT translation from IRremoteESP8266 ir_Carrier.cpp:242-248
    def __init__(self) -> None:
        self._: CarrierProtocol = CarrierProtocol()
        self.stateReset()

    ## Reset the internal state to a fixed known good state.
    ## @note The state is powered off.
    ## EXACT translation from IRremoteESP8266 ir_Carrier.cpp:250-252
    def stateReset(self) -> None:
        self._.raw = 0x109000002C2A5584

    ## Calculate the checksum for a given state.
    ## @param[in] state The value to calc the checksum of.
    ## @return The 4-bit checksum stored in a uint_8.
    ## EXACT translation from IRremoteESP8266 ir_Carrier.cpp:254-265
    @staticmethod
    def calcChecksum(state: int) -> int:
        data = (state >> (kCarrierAc64ChecksumOffset + kCarrierAc64ChecksumSize)) & (
            (1 << (kCarrierAc64Bits - (kCarrierAc64ChecksumOffset + kCarrierAc64ChecksumSize))) - 1
        )
        result = 0
        while data:
            result += data & 0xF
            data >>= 4
        return result & 0xF

    ## Verify the checksum is valid for a given state.
    ## @param[in] state The array to verify the checksum of.
    ## @return true, if the state has a valid checksum. Otherwise, false.
    ## EXACT translation from IRremoteESP8266 ir_Carrier.cpp:267-274
    @staticmethod
    def validChecksum(state: int) -> bool:
        # Validate the checksum of the given state.
        return ((state >> kCarrierAc64ChecksumOffset) & 0x0F) == IRCarrierAc64.calcChecksum(state)

    ## Calculate and set the checksum values for the internal state.
    ## EXACT translation from IRremoteESP8266 ir_Carrier.cpp:276-279
    def checksum(self) -> None:
        self._.Sum = self.calcChecksum(self._.raw)

    ## Get a copy of the internal state as a valid code for this protocol.
    ## @return A valid code for this protocol based on the current internal state.
    ## EXACT translation from IRremoteESP8266 ir_Carrier.cpp:292-297
    def getRaw(self) -> int:
        self.checksum()  # Ensure correct settings before sending.
        return self._.raw

    ## Set the internal state from a valid code for this protocol.
    ## @param[in] state A valid code for this protocol.
    ## EXACT translation from IRremoteESP8266 ir_Carrier.cpp:299-301
    def setRaw(self, state: int) -> None:
        self._.raw = state

    ## Set the temp in deg C.
    ## @param[in] temp The desired temperature in Celsius.
    ## EXACT translation from IRremoteESP8266 ir_Carrier.cpp:303-309
    def setTemp(self, temp: int) -> None:
        degrees = max(temp, kCarrierAc64MinTemp)
        degrees = min(degrees, kCarrierAc64MaxTemp)
        self._.Temp = degrees - kCarrierAc64MinTemp

    ## Get the current temperature from the internal state.
    ## @return The current temperature in Celsius.
    ## EXACT translation from IRremoteESP8266 ir_Carrier.cpp:311-315
    def getTemp(self) -> int:
        return self._.Temp + kCarrierAc64MinTemp

    ## Change the power setting.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## EXACT translation from IRremoteESP8266 ir_Carrier.cpp:317-321
    def setPower(self, on: bool) -> None:
        self._.Power = on

    ## Get the value of the current power setting.
    ## @return true, the setting is on. false, the setting is off.
    ## EXACT translation from IRremoteESP8266 ir_Carrier.cpp:323-327
    def getPower(self) -> bool:
        return bool(self._.Power)

    ## Change the power setting to On.
    ## EXACT translation from IRremoteESP8266 ir_Carrier.cpp:329-330
    def on(self) -> None:
        self.setPower(True)

    ## Change the power setting to Off.
    ## EXACT translation from IRremoteESP8266 ir_Carrier.cpp:332-333
    def off(self) -> None:
        self.setPower(False)

    ## Get the operating mode setting of the A/C.
    ## @return The current operating mode setting.
    ## EXACT translation from IRremoteESP8266 ir_Carrier.cpp:335-339
    def getMode(self) -> int:
        return self._.Mode

    ## Set the operating mode of the A/C.
    ## @param[in] mode The desired operating mode.
    ## EXACT translation from IRremoteESP8266 ir_Carrier.cpp:341-353
    def setMode(self, mode: int) -> None:
        if mode in [kCarrierAc64Heat, kCarrierAc64Cool, kCarrierAc64Fan]:
            self._.Mode = mode
            return
        self._.Mode = kCarrierAc64Cool

    ## Get the current fan speed setting.
    ## @return The current fan speed.
    ## EXACT translation from IRremoteESP8266 ir_Carrier.cpp:377-381
    def getFan(self) -> int:
        return self._.Fan

    ## Set the speed of the fan.
    ## @param[in] speed The desired setting.
    ## EXACT translation from IRremoteESP8266 ir_Carrier.cpp:383-390
    def setFan(self, speed: int) -> None:
        if speed > kCarrierAc64FanHigh:
            self._.Fan = kCarrierAc64FanAuto
        else:
            self._.Fan = speed

    ## Set the Vertical Swing mode of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## EXACT translation from IRremoteESP8266 ir_Carrier.cpp:418-422
    def setSwingV(self, on: bool) -> None:
        self._.SwingV = on

    ## Get the Vertical Swing mode of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## EXACT translation from IRremoteESP8266 ir_Carrier.cpp:424-428
    def getSwingV(self) -> bool:
        return bool(self._.SwingV)

    ## Set the Sleep mode of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## EXACT translation from IRremoteESP8266 ir_Carrier.cpp:430-441
    def setSleep(self, on: bool) -> None:
        if on:
            # Sleep sets a default value in the Off timer, and disables both timers.
            self.setOffTimer(2 * 60)
            # Clear the enable bits for each timer.
            self._cancelOnTimer()
            self._cancelOffTimer()
        self._.Sleep = on

    ## Get the Sleep mode of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## EXACT translation from IRremoteESP8266 ir_Carrier.cpp:443-447
    def getSleep(self) -> bool:
        return bool(self._.Sleep)

    ## Clear the On Timer enable bit.
    ## EXACT translation from IRremoteESP8266 ir_Carrier.cpp:449-452
    def _cancelOnTimer(self) -> None:
        self._.OnTimerEnable = False

    ## Get the current On Timer time.
    ## @return The number of minutes it is set for. 0 means it's off.
    ## @note The A/C protocol only supports one hour increments.
    ## EXACT translation from IRremoteESP8266 ir_Carrier.cpp:454-462
    def getOnTimer(self) -> int:
        if self._.OnTimerEnable:
            return self._.OnTimer * 60
        else:
            return 0

    ## Set the On Timer time.
    ## @param[in] nr_of_mins Number of minutes to set the timer to.
    ##  (< 60 is disable).
    ## @note The A/C protocol only supports one hour increments.
    ## EXACT translation from IRremoteESP8266 ir_Carrier.cpp:464-476
    def setOnTimer(self, nr_of_mins: int) -> None:
        hours = min(nr_of_mins // 60, kCarrierAc64TimerMax)
        self._.OnTimerEnable = bool(hours)  # Enable
        self._.OnTimer = max(kCarrierAc64TimerMin, hours)  # Hours
        if hours:  # If enabled, disable the Off Timer & Sleep mode.
            self._cancelOffTimer()
            self.setSleep(False)

    ## Clear the Off Timer enable bit.
    ## EXACT translation from IRremoteESP8266 ir_Carrier.cpp:478-481
    def _cancelOffTimer(self) -> None:
        self._.OffTimerEnable = False

    ## Get the current Off Timer time.
    ## @return The number of minutes it is set for. 0 means it's off.
    ## @note The A/C protocol only supports one hour increments.
    ## EXACT translation from IRremoteESP8266 ir_Carrier.cpp:483-491
    def getOffTimer(self) -> int:
        if self._.OffTimerEnable:
            return self._.OffTimer * 60
        else:
            return 0

    ## Set the Off Timer time.
    ## @param[in] nr_of_mins Number of minutes to set the timer to.
    ##  (< 60 is disable).
    ## @note The A/C protocol only supports one hour increments.
    ## EXACT translation from IRremoteESP8266 ir_Carrier.cpp:493-506
    def setOffTimer(self, nr_of_mins: int) -> None:
        hours = min(nr_of_mins // 60, kCarrierAc64TimerMax)
        # The time can be changed in sleep mode, but doesn't set the flag.
        self._.OffTimerEnable = hours > 0 and not self._.Sleep
        self._.OffTimer = max(kCarrierAc64TimerMin, hours)  # Hours
        if hours:  # If enabled, disable the On Timer & Sleep mode.
            self._cancelOnTimer()
            self.setSleep(False)


## Send a Carrier 128bit HVAC formatted message.
## Status: BETA / Seems to work with tests. Needs testing agaisnt real devices.
## @param[in] data The message to be sent.
## @param[in] nbytes The byte size of the message being sent.
## @param[in] repeat The number of times the message is to be repeated.
## EXACT translation from IRremoteESP8266 ir_Carrier.cpp:557-594
def sendCarrierAC128(data: List[int], nbytes: int, repeat: int = 0) -> List[int]:
    """
    Send a Carrier 128bit HVAC formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendCarrierAC128 (ir_Carrier.cpp:563-593)

    Returns timing array instead of transmitting via hardware.
    """
    from app.core.ir_protocols.ir_send import sendGeneric, sendGenericUint64

    # Min length check.
    if nbytes <= kCarrierAc128StateLength // 2:
        return []

    all_timings = []

    # Handle repeats.
    for r in range(repeat + 1):
        # First part of the message.
        # Headers + Data + SectionGap
        part1_timings = sendGeneric(
            headermark=kCarrierAc128HdrMark,
            headerspace=kCarrierAc128HdrSpace,
            onemark=kCarrierAc128BitMark,
            onespace=kCarrierAc128OneSpace,
            zeromark=kCarrierAc128BitMark,
            zerospace=kCarrierAc128ZeroSpace,
            footermark=kCarrierAc128BitMark,
            gap=kCarrierAc128SectionGap,
            dataptr=data,
            nbytes=nbytes // 2,
            MSBfirst=False,
        )
        all_timings.extend(part1_timings)

        # Inter-message markers
        all_timings.append(kCarrierAc128HdrMark)
        all_timings.append(kCarrierAc128InterSpace)

        # Second part of the message
        # Headers + Data + SectionGap
        part2_timings = sendGeneric(
            headermark=kCarrierAc128Hdr2Mark,
            headerspace=kCarrierAc128Hdr2Space,
            onemark=kCarrierAc128BitMark,
            onespace=kCarrierAc128OneSpace,
            zeromark=kCarrierAc128BitMark,
            zerospace=kCarrierAc128ZeroSpace,
            footermark=kCarrierAc128BitMark,
            gap=kCarrierAc128SectionGap,
            dataptr=data[nbytes // 2 :],
            nbytes=nbytes // 2,
            MSBfirst=False,
        )
        all_timings.extend(part2_timings)

        # Footer
        all_timings.append(kCarrierAc128HdrMark)
        all_timings.append(100000)  # kDefaultMessageGap

    return all_timings


## Decode the supplied Carrier 128-bit HVAC message.
## Status: STABLE / Expected to work.
## @param[in,out] results Ptr to the data to decode & where to store the decode
##   result.
## @param[in] offset The starting index to use when attempting to decode the
##   raw data. Typically/Defaults to kStartOffset.
## @param[in] nbits The number of data bits to expect.
## @param[in] strict Flag indicating if we should perform strict matching.
## @return A boolean. True if it can decode it, false if it can't.
## EXACT translation from IRremoteESP8266 ir_Carrier.cpp:596-656
def decodeCarrierAC128(
    results, offset: int = 1, nbits: int = kCarrierAc128Bits, strict: bool = True
) -> bool:
    """
    Decode the supplied Carrier 128-bit HVAC message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeCarrierAC128 (ir_Carrier.cpp:606-655)
    """
    from app.core.ir_protocols.ir_recv import (
        _matchGeneric,
        matchMark,
        matchSpace,
        matchAtLeast,
        kHeader,
        kFooter,
    )

    if results.rawlen < 2 * (nbits + 2 * kHeader + kFooter) - 1 + offset:
        return False  # Can't possibly be a valid Carrier message.
    if strict and nbits != kCarrierAc128Bits:
        return False  # We expect Carrier to be 128 bits of message.

    pos = 0
    sectionbits = nbits // 2

    # Match the first section.
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state,
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=sectionbits,
        hdrmark=kCarrierAc128HdrMark,
        hdrspace=kCarrierAc128HdrSpace,
        onemark=kCarrierAc128BitMark,
        onespace=kCarrierAc128OneSpace,
        zeromark=kCarrierAc128BitMark,
        zerospace=kCarrierAc128ZeroSpace,
        footermark=kCarrierAc128BitMark,
        footerspace=kCarrierAc128SectionGap,
        atleast=True,
        tolerance=25,
        excess=50,
        MSBfirst=False,
    )
    if used == 0:
        return False  # No match.
    offset += used
    pos += sectionbits // 8

    # Look for the inter-message markers.
    if not matchMark(results.rawbuf[offset], kCarrierAc128HdrMark, 25, 50):
        return False
    offset += 1
    if not matchSpace(results.rawbuf[offset], kCarrierAc128InterSpace, 25, 50):
        return False
    offset += 1

    # Now look for the second section.
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state[pos:],
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=sectionbits,
        hdrmark=kCarrierAc128Hdr2Mark,
        hdrspace=kCarrierAc128Hdr2Space,
        onemark=kCarrierAc128BitMark,
        onespace=kCarrierAc128OneSpace,
        zeromark=kCarrierAc128BitMark,
        zerospace=kCarrierAc128ZeroSpace,
        footermark=kCarrierAc128BitMark,
        footerspace=kCarrierAc128SectionGap,
        atleast=True,
        tolerance=25,
        excess=50,
        MSBfirst=False,
    )
    if used == 0:
        return False  # No match.
    offset += used

    # Now check for the Footer.
    if not matchMark(results.rawbuf[offset], kCarrierAc128HdrMark, 25, 50):
        return False
    offset += 1
    if offset < results.rawlen and not matchAtLeast(
        results.rawbuf[offset], 100000
    ):  # kDefaultMessageGap
        return False

    # Compliance
    # if (strict && !IRCarrierAc128::validChecksum(results->value)) return false;

    # Success
    results.bits = nbits
    # results.decode_type = CARRIER_AC128
    return True


## Send a Carroer A/C 84 Bit formatted message.
## Status: BETA / Untested but probably works.
## @param[in] data The message to be sent.
## @param[in] nbytes The byte size of the message being sent.
## @param[in] repeat The number of times the command is to be repeated.
## EXACT translation from IRremoteESP8266 ir_Carrier.cpp:658-686
def sendCarrierAC84(data: List[int], nbytes: int, repeat: int = 0) -> List[int]:
    """
    Send a Carroer A/C 84 Bit formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendCarrierAC84 (ir_Carrier.cpp:664-685)

    Returns timing array instead of transmitting via hardware.
    """
    from app.core.ir_protocols.ir_send import sendGeneric, sendGenericUint64

    all_timings = []

    # Protocol uses a constant bit time encoding.
    for r in range(repeat + 1):
        if nbytes:
            # The least significant `kCarrierAc84ExtraBits` bits of the first byte
            part1_timings = sendGenericUint64(
                headermark=kCarrierAc84HdrMark,
                headerspace=kCarrierAc84HdrSpace,  # Header
                onemark=kCarrierAc84Zero,
                onespace=kCarrierAc84One,  # Data
                zeromark=kCarrierAc84One,
                zerospace=kCarrierAc84Zero,
                footermark=0,
                gap=0,  # No footer
                dataint=data[0] & 0x0F,  # GETBITS64(data[0], 0, kCarrierAc84ExtraBits)
                nbits=kCarrierAc84ExtraBits,
                MSBfirst=False,
            )
            all_timings.extend(part1_timings)

            # The rest of the data.
            part2_timings = sendGeneric(
                headermark=0,
                headerspace=0,  # No Header
                onemark=kCarrierAc84Zero,
                onespace=kCarrierAc84One,  # Data
                zeromark=kCarrierAc84One,
                zerospace=kCarrierAc84Zero,
                footermark=kCarrierAc84Zero,
                gap=100000,  # kDefaultMessageGap - Footer
                dataptr=data[1:],
                nbytes=nbytes - 1,
                MSBfirst=False,
            )
            all_timings.extend(part2_timings)

    return all_timings


## Decode the supplied Carroer A/C 84 Bit formatted message.
## Status: STABLE / Confirmed Working.
## @param[in,out] results Ptr to the data to decode & where to store the decode
##   result.
## @param[in] offset The starting index to use when attempting to decode the
##   raw data. Typically/Defaults to kStartOffset.
## @param[in] nbits The number of data bits to expect.
## @param[in] strict Flag indicating if we should perform strict matching.
## @return A boolean. True if it can decode it, false if it can't.
## EXACT translation from IRremoteESP8266 ir_Carrier.cpp:688-747
def decodeCarrierAC84(
    results, offset: int = 1, nbits: int = kCarrierAc84Bits, strict: bool = True
) -> bool:
    """
    Decode the supplied Carroer A/C 84 Bit formatted message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeCarrierAC84 (ir_Carrier.cpp:698-746)
    """
    from app.core.ir_protocols.ir_recv import _matchGeneric, matchGenericConstBitTime, kHeader, kFooter, kMarkExcess

    # Check if we have enough data to even possibly match.
    if results.rawlen < 2 * nbits + kHeader + kFooter - 1 + offset:
        return False  # Can't possibly be a valid Carrier message.
    # Compliance check.
    if strict and nbits != kCarrierAc84Bits:
        return False

    # This decoder expects to decode an unusual number of bits. Check before we
    # start.
    if nbits % 8 != kCarrierAc84ExtraBits:
        return False

    data = [0]  # Will hold first 4 bits

    # Header + Data (kCarrierAc84ExtraBits only)
    # C++: matchGenericConstBitTime(..., kCarrierAc84ExtraBits, kCarrierAc84HdrMark, kCarrierAc84HdrSpace,
    #                                kCarrierAc84Zero, kCarrierAc84One, 0, 0, false, _tolerance + kCarrierAc84ExtraTolerance, ...)
    used = matchGenericConstBitTime(
        data_ptr=results.rawbuf[offset:],
        result_ptr=data,
        remaining=results.rawlen - offset,
        nbits=kCarrierAc84ExtraBits,
        hdrmark=kCarrierAc84HdrMark,
        hdrspace=kCarrierAc84HdrSpace,  # Header
        one=kCarrierAc84Zero,  # Note: One and Zero are swapped in constant bit time
        zero=kCarrierAc84One,
        footermark=0,
        footerspace=0,  # No Footer
        atleast=False,
        tolerance=25 + kCarrierAc84ExtraTolerance,  # _tolerance + kCarrierAc84ExtraTolerance
        excess=kMarkExcess,
        MSBfirst=False,
    )
    if not used:
        return False

    # Stuff the captured data so far into the first byte of the state.
    results.state[0] = data[0]
    offset += used

    # Capture the rest of the data as normal as we should be on a byte boundary.
    # Data + Footer
    # C++: matchGeneric(results->rawbuf + offset, results->state + 1, results->rawlen - offset,
    #                   nbits - kCarrierAc84ExtraBits, 0, 0, kCarrierAc84Zero, kCarrierAc84One, ...)
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state[1:],
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=nbits - kCarrierAc84ExtraBits,
        hdrmark=0,
        hdrspace=0,  # No Header
        onemark=kCarrierAc84Zero,
        onespace=kCarrierAc84One,  # Data
        zeromark=kCarrierAc84One,
        zerospace=kCarrierAc84Zero,
        footermark=kCarrierAc84Zero,
        footerspace=kCarrierAc84Gap,
        atleast=True,
        tolerance=25 + kCarrierAc84ExtraTolerance,
        excess=kMarkExcess,
        MSBfirst=False,
    )
    if used == 0:
        return False

    # Success
    results.bits = nbits
    # results.decode_type = CARRIER_AC84
    results.repeat = False
    return True
