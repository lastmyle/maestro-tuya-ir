# Copyright 2019-2021 David Conran
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Support for Electra A/C protocols.
## Direct translation from IRremoteESP8266 ir_Electra.cpp and ir_Electra.h

from typing import List

# Ref: https://github.com/ToniA/arduino-heatpumpir/blob/master/AUXHeatpumpIR.cpp

# Constants - Timing values (from ir_Electra.cpp lines 17-23)
kElectraAcHdrMark = 9166
kElectraAcBitMark = 646
kElectraAcHdrSpace = 4470
kElectraAcOneSpace = 1647
kElectraAcZeroSpace = 547
kElectraAcMessageGap = 100000  # kDefaultMessageGap - just a guess

# State length constants (from IRremoteESP8266.h)
kElectraAcStateLength = 13
kElectraAcBits = kElectraAcStateLength * 8  # 104 bits

# Temperature constants (from ir_Electra.h lines 82-84)
kElectraAcMinTemp = 16   # 16C
kElectraAcMaxTemp = 32   # 32C
kElectraAcTempDelta = 8

# Swing constants (from ir_Electra.h lines 85-86)
kElectraAcSwingOn = 0b000
kElectraAcSwingOff = 0b111

# Fan speed constants (from ir_Electra.h lines 88-91)
kElectraAcFanAuto = 0b101
kElectraAcFanLow = 0b011
kElectraAcFanMed = 0b010
kElectraAcFanHigh = 0b001

# Mode constants (from ir_Electra.h lines 93-97)
kElectraAcAuto = 0b000
kElectraAcCool = 0b001
kElectraAcDry = 0b010
kElectraAcHeat = 0b100
kElectraAcFan = 0b110

# Light toggle constants (from ir_Electra.h lines 99-105)
kElectraAcLightToggleOn = 0x15
# Light has known ON values of 0x15 (0b00010101) or 0x19 (0b00011001)
#   Thus common bits ON are: 0b00010001 (0x11)
# We will use this for the getLightToggle() test.
kElectraAcLightToggleMask = 0x11
# and known OFF values of 0x08 (0b00001000) & 0x05 (0x00000101)
kElectraAcLightToggleOff = 0x08

# Sensor temp constants (from ir_Electra.h lines 108-111)
# Re: Byte[7]. Or Delta == 0xA and Temperature are stored in last 6 bits,
# and bit 7 stores Unknown flag
kElectraAcSensorTempDelta = 0x4A
kElectraAcSensorMinTemp = 0    # 0C
kElectraAcSensorMaxTemp = 50   # 50C


## Helper function for checksum calculation
def sumBytes(data: List[int], length: int) -> int:
    """Sum all bytes in the array (used for checksum)"""
    return sum(data[:length]) & 0xFF


## Native representation of an Electra A/C message.
## This is a direct translation of the C++ union/struct (ir_Electra.h lines 35-79)
class ElectraProtocol:
    def __init__(self):
        # The state array (13 bytes for Electra)
        self.remote_state = [0] * 13

    # Byte 1
    @property
    def SwingV(self) -> int:
        return self.remote_state[1] & 0x07

    @SwingV.setter
    def SwingV(self, value: int) -> None:
        self.remote_state[1] = (self.remote_state[1] & 0xF8) | (value & 0x07)

    @property
    def Temp(self) -> int:
        return (self.remote_state[1] >> 3) & 0x1F

    @Temp.setter
    def Temp(self, value: int) -> None:
        self.remote_state[1] = (self.remote_state[1] & 0x07) | ((value & 0x1F) << 3)

    # Byte 2
    @property
    def SwingH(self) -> int:
        return (self.remote_state[2] >> 5) & 0x07

    @SwingH.setter
    def SwingH(self, value: int) -> None:
        self.remote_state[2] = (self.remote_state[2] & 0x1F) | ((value & 0x07) << 5)

    # Byte 3
    @property
    def SensorUpdate(self) -> int:
        return (self.remote_state[3] >> 6) & 0x01

    @SensorUpdate.setter
    def SensorUpdate(self, value: bool) -> None:
        if value:
            self.remote_state[3] |= 0x40
        else:
            self.remote_state[3] &= 0xBF

    # Byte 4
    @property
    def Fan(self) -> int:
        return (self.remote_state[4] >> 5) & 0x07

    @Fan.setter
    def Fan(self, value: int) -> None:
        self.remote_state[4] = (self.remote_state[4] & 0x1F) | ((value & 0x07) << 5)

    # Byte 5
    @property
    def Turbo(self) -> int:
        return (self.remote_state[5] >> 6) & 0x01

    @Turbo.setter
    def Turbo(self, value: bool) -> None:
        if value:
            self.remote_state[5] |= 0x40
        else:
            self.remote_state[5] &= 0xBF

    @property
    def Quiet(self) -> int:
        return (self.remote_state[5] >> 7) & 0x01

    @Quiet.setter
    def Quiet(self, value: bool) -> None:
        if value:
            self.remote_state[5] |= 0x80
        else:
            self.remote_state[5] &= 0x7F

    # Byte 6
    @property
    def IFeel(self) -> int:
        return (self.remote_state[6] >> 3) & 0x01

    @IFeel.setter
    def IFeel(self, value: bool) -> None:
        if value:
            self.remote_state[6] |= 0x08
        else:
            self.remote_state[6] &= 0xF7

    @property
    def Mode(self) -> int:
        return (self.remote_state[6] >> 5) & 0x07

    @Mode.setter
    def Mode(self, value: int) -> None:
        self.remote_state[6] = (self.remote_state[6] & 0x1F) | ((value & 0x07) << 5)

    # Byte 7
    @property
    def SensorTemp(self) -> int:
        return self.remote_state[7] & 0xFF

    @SensorTemp.setter
    def SensorTemp(self, value: int) -> None:
        self.remote_state[7] = value & 0xFF

    # Byte 9
    @property
    def Clean(self) -> int:
        return (self.remote_state[9] >> 2) & 0x01

    @Clean.setter
    def Clean(self, value: bool) -> None:
        if value:
            self.remote_state[9] |= 0x04
        else:
            self.remote_state[9] &= 0xFB

    @property
    def Power(self) -> int:
        return (self.remote_state[9] >> 5) & 0x01

    @Power.setter
    def Power(self, value: bool) -> None:
        if value:
            self.remote_state[9] |= 0x20
        else:
            self.remote_state[9] &= 0xDF

    # Byte 11
    @property
    def LightToggle(self) -> int:
        return self.remote_state[11] & 0xFF

    @LightToggle.setter
    def LightToggle(self, value: int) -> None:
        self.remote_state[11] = value & 0xFF

    # Byte 12
    @property
    def Sum(self) -> int:
        return self.remote_state[12] & 0xFF

    @Sum.setter
    def Sum(self, value: int) -> None:
        self.remote_state[12] = value & 0xFF


## Send an Electra A/C formatted message.
## Status: Alpha / Needs testing against a real device.
## @param[in] data The message to be sent.
## @param[in] nbytes The number of bytes of message to be sent.
## @param[in] repeat The number of times the command is to be repeated.
## Direct translation from IRremoteESP8266 IRsend::sendElectraAC (ir_Electra.cpp lines 40-49)
def sendElectraAC(data: List[int], nbytes: int, repeat: int = 0) -> List[int]:
    """
    Send an Electra A/C formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendElectraAC

    Returns timing array instead of transmitting via hardware.
    """
    # Import here to avoid circular import
    from app.core.ir_protocols.ir_send import sendGeneric

    all_timings = []

    for r in range(repeat + 1):
        timings = sendGeneric(
            headermark=kElectraAcHdrMark,
            headerspace=kElectraAcHdrSpace,
            onemark=kElectraAcBitMark,
            onespace=kElectraAcOneSpace,
            zeromark=kElectraAcBitMark,
            zerospace=kElectraAcZeroSpace,
            footermark=kElectraAcBitMark,
            gap=kElectraAcMessageGap,
            dataptr=data,
            nbytes=nbytes,
            frequency=38000,  # Complete guess of the modulation frequency
            MSBfirst=False,  # Send data in LSB order per byte
            repeat=0,
            dutycycle=50
        )
        all_timings.extend(timings)

    return all_timings


## Class for handling detailed Electra A/C messages.
## Direct translation from C++ IRElectraAc class
class IRElectraAc:
    ## Class Constructor
    def __init__(self) -> None:
        self._: ElectraProtocol = ElectraProtocol()
        self.stateReset()

    ## Reset the internal state to a fixed known good state.
    ## Direct translation from ir_Electra.cpp lines 63-68
    def stateReset(self) -> None:
        for i in range(1, kElectraAcStateLength - 2):
            self._.remote_state[i] = 0
        self._.remote_state[0] = 0xC3
        self._.LightToggle = kElectraAcLightToggleOff
        # [12] is the checksum.

    ## Calculate the checksum for a given state.
    ## @param[in] state The value to calc the checksum of.
    ## @param[in] length The length of the state array.
    ## @return The calculated checksum stored in a uint_8.
    ## Direct translation from ir_Electra.cpp lines 77-81
    @staticmethod
    def calcChecksum(state: List[int], length: int = kElectraAcStateLength) -> int:
        if length == 0:
            return state[0]
        return sumBytes(state, length - 1)

    ## Verify the checksum is valid for a given state.
    ## @param[in] state The state to verify the checksum of.
    ## @param[in] length The length of the state array.
    ## @return true, if the state has a valid checksum. Otherwise, false.
    ## Direct translation from ir_Electra.cpp lines 87-91
    @staticmethod
    def validChecksum(state: List[int], length: int = kElectraAcStateLength) -> bool:
        if length < 2:
            return True  # No checksum to compare with. Assume okay.
        return state[length - 1] == IRElectraAc.calcChecksum(state, length)

    ## Calculate and set the checksum values for the internal state.
    ## @param[in] length The length of the state array.
    ## Direct translation from ir_Electra.cpp lines 95-98
    def checksum(self, length: int = kElectraAcStateLength) -> None:
        if length < 2:
            return
        self._.Sum = IRElectraAc.calcChecksum(self._.remote_state, length)

    ## Change the power setting to On.
    ## Direct translation from ir_Electra.cpp line 123
    def on(self) -> None:
        self.setPower(True)

    ## Change the power setting to Off.
    ## Direct translation from ir_Electra.cpp line 126
    def off(self) -> None:
        self.setPower(False)

    ## Change the power setting.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Electra.cpp lines 130-132
    def setPower(self, on: bool) -> None:
        self._.Power = on

    ## Get the value of the current power setting.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Electra.cpp lines 136-138
    def getPower(self) -> bool:
        return bool(self._.Power)

    ## Set the operating mode of the A/C.
    ## @param[in] mode The desired operating mode.
    ## Direct translation from ir_Electra.cpp lines 142-155
    def setMode(self, mode: int) -> None:
        if mode in [kElectraAcAuto, kElectraAcDry, kElectraAcCool,
                   kElectraAcHeat, kElectraAcFan]:
            self._.Mode = mode
        else:
            # If we get an unexpected mode, default to AUTO.
            self._.Mode = kElectraAcAuto

    ## Get the operating mode setting of the A/C.
    ## @return The current operating mode setting.
    ## Direct translation from ir_Electra.cpp lines 159-161
    def getMode(self) -> int:
        return self._.Mode

    ## Set the temperature.
    ## @param[in] temp The temperature in degrees celsius.
    ## Direct translation from ir_Electra.cpp lines 191-195
    def setTemp(self, temp: int) -> None:
        newtemp = max(kElectraAcMinTemp, temp)
        newtemp = min(kElectraAcMaxTemp, newtemp) - kElectraAcTempDelta
        self._.Temp = newtemp

    ## Get the current temperature setting.
    ## @return The current setting for temp. in degrees celsius.
    ## Direct translation from ir_Electra.cpp lines 199-201
    def getTemp(self) -> int:
        return self._.Temp + kElectraAcTempDelta

    ## Set the speed of the fan.
    ## @param[in] speed The desired setting.
    ## @note 0 is auto, 1-3 is the speed
    ## Direct translation from ir_Electra.cpp lines 206-218
    def setFan(self, speed: int) -> None:
        if speed in [kElectraAcFanAuto, kElectraAcFanHigh,
                    kElectraAcFanMed, kElectraAcFanLow]:
            self._.Fan = speed
        else:
            # If we get an unexpected speed, default to Auto.
            self._.Fan = kElectraAcFanAuto

    ## Get the current fan speed setting.
    ## @return The current fan speed.
    ## Direct translation from ir_Electra.cpp lines 222-224
    def getFan(self) -> int:
        return self._.Fan

    ## Set the Vertical Swing mode of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Electra.cpp lines 254-256
    def setSwingV(self, on: bool) -> None:
        self._.SwingV = (kElectraAcSwingOn if on else kElectraAcSwingOff)

    ## Get the Vertical Swing mode of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Electra.cpp lines 260-262
    def getSwingV(self) -> bool:
        return not self._.SwingV

    ## Set the Horizontal Swing mode of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Electra.cpp lines 266-268
    def setSwingH(self, on: bool) -> None:
        self._.SwingH = (kElectraAcSwingOn if on else kElectraAcSwingOff)

    ## Get the Horizontal Swing mode of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Electra.cpp lines 272-274
    def getSwingH(self) -> bool:
        return not self._.SwingH

    ## Set the Light (LED) Toggle mode of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Electra.cpp lines 278-280
    def setLightToggle(self, on: bool) -> None:
        self._.LightToggle = (kElectraAcLightToggleOn if on else kElectraAcLightToggleOff)

    ## Get the Light (LED) Toggle mode of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Electra.cpp lines 284-287
    def getLightToggle(self) -> bool:
        return (self._.LightToggle & kElectraAcLightToggleMask) == kElectraAcLightToggleMask

    ## Set the Clean mode of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Electra.cpp lines 291-293
    def setClean(self, on: bool) -> None:
        self._.Clean = on

    ## Get the Clean mode of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Electra.cpp lines 297-299
    def getClean(self) -> bool:
        return bool(self._.Clean)

    ## Set the Turbo mode of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Electra.cpp lines 303-305
    def setTurbo(self, on: bool) -> None:
        self._.Turbo = on

    ## Get the Turbo mode of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Electra.cpp lines 309-311
    def getTurbo(self) -> bool:
        return bool(self._.Turbo)

    ## Set the Quiet/Silent mode of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Electra.cpp lines 315-317
    def setQuiet(self, on: bool) -> None:
        self._.Quiet = on

    ## Get the Quiet/Silent mode of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Electra.cpp lines 321-323
    def getQuiet(self) -> bool:
        return bool(self._.Quiet)

    ## Get the IFeel mode of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Electra.cpp line 327
    def getIFeel(self) -> bool:
        return bool(self._.IFeel)

    ## Set the IFeel mode of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Electra.cpp lines 331-339
    def setIFeel(self, on: bool) -> None:
        self._.IFeel = on
        if self._.IFeel:
            # Make sure there is a reasonable value in _.SensorTemp
            self.setSensorTemp(self.getSensorTemp())
        else:
            # Clear any previous stored temp..
            self._.SensorTemp = kElectraAcSensorMinTemp

    ## Get the silent Sensor Update setting of the message.
    ## i.e. Is this _just_ a sensor temp update message from the remote?
    ## @note The A/C just takes the sensor temp value from the message and
    ## will not follow any of the other settings in the message.
    ## @return true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Electra.cpp line 346
    def getSensorUpdate(self) -> bool:
        return bool(self._.SensorUpdate)

    ## Set the silent Sensor Update setting of the message.
    ## i.e. Is this _just_ a sensor temp update message from the remote?
    ## @note The A/C will just take the sensor temp value from the message and
    ## will not follow any of the other settings in the message. If set, the A/C
    ## unit will also not beep in response to the message.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## Direct translation from ir_Electra.cpp line 354
    def setSensorUpdate(self, on: bool) -> None:
        self._.SensorUpdate = on

    ## Set the Sensor temperature for the IFeel mode.
    ## @param[in] temp The temperature in degrees celsius.
    ## Direct translation from ir_Electra.cpp lines 358-362
    def setSensorTemp(self, temp: int) -> None:
        self._.SensorTemp = min(kElectraAcSensorMaxTemp,
                                max(kElectraAcSensorMinTemp, temp)) + \
                            kElectraAcSensorTempDelta

    ## Get the current sensor temperature setting for the IFeel mode.
    ## @return The current setting for temp. in degrees celsius.
    ## Direct translation from ir_Electra.cpp lines 366-369
    def getSensorTemp(self) -> int:
        return max(kElectraAcSensorTempDelta, self._.SensorTemp) - \
               kElectraAcSensorTempDelta

    ## Get a PTR to the internal state/code for this protocol.
    ## @return PTR to a code for this protocol based on the current internal state.
    ## Direct translation from ir_Electra.cpp lines 110-113
    def getRaw(self) -> List[int]:
        self.checksum()
        return self._.remote_state

    ## Set the internal state from a valid code for this protocol.
    ## @param[in] new_code A valid code for this protocol.
    ## @param[in] length The length of the code array.
    ## Direct translation from ir_Electra.cpp lines 118-120
    def setRaw(self, new_code: List[int], length: int = kElectraAcStateLength) -> None:
        for i in range(min(length, kElectraAcStateLength)):
            self._.remote_state[i] = new_code[i]


## Decode the supplied Electra A/C message.
## Status: STABLE / Known working.
## @param[in,out] results Ptr to the data to decode & where to store the decode result.
## @param[in] offset The starting index to use when attempting to decode the raw data.
## @param[in] nbits The number of data bits to expect.
## @param[in] strict Flag indicating if we should perform strict matching.
## @return A boolean. True if it can decode it, false if it can't.
## Direct translation from IRremoteESP8266 IRrecv::decodeElectraAC (ir_Electra.cpp lines 439-469)
def decodeElectraAC(results, offset: int = 1, nbits: int = kElectraAcBits,
                    strict: bool = True) -> bool:
    """
    Decode an Electra A/C IR message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeElectraAC

    This is the ACTUAL C++ decoder function, not a wrapper.
    """
    # Import here to avoid circular imports
    from app.core.ir_protocols.ir_recv import matchGeneric

    if strict:
        if nbits != kElectraAcBits:
            return False  # Not strictly a ELECTRA_AC message.

    # Match Header + Data + Footer
    if not matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_ptr=results.state,
        remaining=results.rawlen - offset,
        nbits=nbits,
        hdrmark=kElectraAcHdrMark,
        hdrspace=kElectraAcHdrSpace,
        onemark=kElectraAcBitMark,
        onespace=kElectraAcOneSpace,
        zeromark=kElectraAcBitMark,
        zerospace=kElectraAcZeroSpace,
        footermark=kElectraAcBitMark,
        footerspace=kElectraAcMessageGap,
        atleast=True,
        tolerance=25,
        excess=0,
        MSBfirst=False
    ):
        return False

    # Compliance
    if strict:
        # Verify the checksum.
        if not IRElectraAc.validChecksum(results.state):
            return False

    # Success
    # results.decode_type = ELECTRA_AC  # Would set protocol type in C++
    results.bits = nbits
    # No need to record the state as we stored it as we decoded it.
    # As we use result->state, we don't record value, address, or command as it
    # is a union data type.
    return True
