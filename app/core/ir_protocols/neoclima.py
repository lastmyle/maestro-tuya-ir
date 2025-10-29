# Copyright 2019-2020 David Conran
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Support for Neoclima protocols.
## Analysis by crankyoldgit, AndreyShpilevoy, & griffisc306
## Code by crankyoldgit
## Direct translation from IRremoteESP8266 ir_Neoclima.cpp and ir_Neoclima.h

from typing import List

# Constants - Timing values
kNeoclimaHdrMark = 6112
kNeoclimaHdrSpace = 7391
kNeoclimaBitMark = 537
kNeoclimaOneSpace = 1651
kNeoclimaZeroSpace = 571
kNeoclimaMinGap = 100000  # kDefaultMessageGap

# State length constants (from IRremoteESP8266.h)
kNeoclimaStateLength = 12
kNeoclimaBits = kNeoclimaStateLength * 8  # 96 bits

# Button/Command constants
kNeoclimaButtonPower = 0x00
kNeoclimaButtonMode = 0x01
kNeoclimaButtonTempUp = 0x02
kNeoclimaButtonTempDown = 0x03
kNeoclimaButtonSwing = 0x04
kNeoclimaButtonFanSpeed = 0x05
kNeoclimaButtonAirFlow = 0x07
kNeoclimaButtonHold = 0x08
kNeoclimaButtonSleep = 0x09
kNeoclimaButtonTurbo = 0x0A
kNeoclimaButtonLight = 0x0B
kNeoclimaButtonEcono = 0x0D
kNeoclimaButtonEye = 0x0E
kNeoclimaButtonFollow = 0x13
kNeoclimaButtonIon = 0x14
kNeoclimaButtonFresh = 0x15
kNeoclimaButton8CHeat = 0x1D
kNeoclimaButtonTempUnit = 0x1E

# Swing constants
kNeoclimaSwingVOn = 0b01
kNeoclimaSwingVOff = 0b10

# Fan speed constants
kNeoclimaFanAuto = 0b00
kNeoclimaFanHigh = 0b01
kNeoclimaFanMed = 0b10
kNeoclimaFanLow = 0b11

# Follow Me constant
kNeoclimaFollowMe = 0x5D  # Also 0x5F

# Temperature constants
kNeoclimaMinTempC = 16  # Celsius
kNeoclimaMaxTempC = 32  # Celsius
kNeoclimaMinTempF = 61  # Fahrenheit
kNeoclimaMaxTempF = 90  # Fahrenheit

# Mode constants
kNeoclimaAuto = 0b000
kNeoclimaCool = 0b001
kNeoclimaDry = 0b010
kNeoclimaFan = 0b011
kNeoclimaHeat = 0b100


## Native representation of a Neoclima A/C message.
## This is a direct translation of the C++ union/struct
class NeoclimaProtocol:
    def __init__(self):
        # The state array (12 bytes for Neoclima)
        self.raw = [0] * kNeoclimaStateLength

    # Byte 1
    @property
    def CHeat(self) -> int:
        return (self.raw[1] >> 1) & 0x01

    @CHeat.setter
    def CHeat(self, value: bool) -> None:
        if value:
            self.raw[1] |= 0x02
        else:
            self.raw[1] &= 0xFD

    @property
    def Ion(self) -> int:
        return (self.raw[1] >> 2) & 0x01

    @Ion.setter
    def Ion(self, value: bool) -> None:
        if value:
            self.raw[1] |= 0x04
        else:
            self.raw[1] &= 0xFB

    # Byte 3
    @property
    def Light(self) -> int:
        return self.raw[3] & 0x01

    @Light.setter
    def Light(self, value: bool) -> None:
        if value:
            self.raw[3] |= 0x01
        else:
            self.raw[3] &= 0xFE

    @property
    def Hold(self) -> int:
        return (self.raw[3] >> 2) & 0x01

    @Hold.setter
    def Hold(self, value: bool) -> None:
        if value:
            self.raw[3] |= 0x04
        else:
            self.raw[3] &= 0xFB

    @property
    def Turbo(self) -> int:
        return (self.raw[3] >> 3) & 0x01

    @Turbo.setter
    def Turbo(self, value: bool) -> None:
        if value:
            self.raw[3] |= 0x08
        else:
            self.raw[3] &= 0xF7

    @property
    def Econo(self) -> int:
        return (self.raw[3] >> 4) & 0x01

    @Econo.setter
    def Econo(self, value: bool) -> None:
        if value:
            self.raw[3] |= 0x10
        else:
            self.raw[3] &= 0xEF

    @property
    def Eye(self) -> int:
        return (self.raw[3] >> 6) & 0x01

    @Eye.setter
    def Eye(self, value: bool) -> None:
        if value:
            self.raw[3] |= 0x40
        else:
            self.raw[3] &= 0xBF

    # Byte 5
    @property
    def Button(self) -> int:
        return self.raw[5] & 0x1F

    @Button.setter
    def Button(self, value: int) -> None:
        self.raw[5] = (self.raw[5] & 0xE0) | (value & 0x1F)

    @property
    def Fresh(self) -> int:
        return (self.raw[5] >> 7) & 0x01

    @Fresh.setter
    def Fresh(self, value: bool) -> None:
        if value:
            self.raw[5] |= 0x80
        else:
            self.raw[5] &= 0x7F

    # Byte 7
    @property
    def Sleep(self) -> int:
        return self.raw[7] & 0x01

    @Sleep.setter
    def Sleep(self, value: bool) -> None:
        if value:
            self.raw[7] |= 0x01
        else:
            self.raw[7] &= 0xFE

    @property
    def Power(self) -> int:
        return (self.raw[7] >> 1) & 0x01

    @Power.setter
    def Power(self, value: bool) -> None:
        if value:
            self.raw[7] |= 0x02
        else:
            self.raw[7] &= 0xFD

    @property
    def SwingV(self) -> int:
        return (self.raw[7] >> 2) & 0x03

    @SwingV.setter
    def SwingV(self, value: int) -> None:
        self.raw[7] = (self.raw[7] & 0xF3) | ((value & 0x03) << 2)

    @property
    def SwingH(self) -> int:
        return (self.raw[7] >> 4) & 0x01

    @SwingH.setter
    def SwingH(self, value: bool) -> None:
        if value:
            self.raw[7] |= 0x10
        else:
            self.raw[7] &= 0xEF

    @property
    def Fan(self) -> int:
        return (self.raw[7] >> 5) & 0x03

    @Fan.setter
    def Fan(self, value: int) -> None:
        self.raw[7] = (self.raw[7] & 0x9F) | ((value & 0x03) << 5)

    @property
    def UseFah(self) -> int:
        return (self.raw[7] >> 7) & 0x01

    @UseFah.setter
    def UseFah(self, value: bool) -> None:
        if value:
            self.raw[7] |= 0x80
        else:
            self.raw[7] &= 0x7F

    # Byte 8
    @property
    def Follow(self) -> int:
        return self.raw[8]

    @Follow.setter
    def Follow(self, value: int) -> None:
        self.raw[8] = value & 0xFF

    # Byte 9
    @property
    def Temp(self) -> int:
        return self.raw[9] & 0x1F

    @Temp.setter
    def Temp(self, value: int) -> None:
        self.raw[9] = (self.raw[9] & 0xE0) | (value & 0x1F)

    @property
    def Mode(self) -> int:
        return (self.raw[9] >> 5) & 0x07

    @Mode.setter
    def Mode(self, value: int) -> None:
        self.raw[9] = (self.raw[9] & 0x1F) | ((value & 0x07) << 5)

    # Byte 11
    @property
    def Sum(self) -> int:
        return self.raw[11]

    @Sum.setter
    def Sum(self, value: int) -> None:
        self.raw[11] = value & 0xFF


## Calculate the checksum for a given state.
## EXACT translation from IRremoteESP8266 IRNeoclimaAc::calcChecksum (ir_Neoclima.cpp lines 83-87)
def calcChecksum(state: List[int], length: int = kNeoclimaStateLength) -> int:
    """
    Calculate checksum for Neoclima protocol.
    EXACT translation from IRremoteESP8266 IRNeoclimaAc::calcChecksum
    """
    if length == 0:
        return state[0]
    # Import here to avoid circular import
    from app.core.ir_protocols.ir_recv import sumBytes

    return sumBytes(state, length - 1)


## Verify the checksum is valid for a given state.
## EXACT translation from IRremoteESP8266 IRNeoclimaAc::validChecksum (ir_Neoclima.cpp lines 93-97)
def validChecksum(state: List[int], length: int = kNeoclimaStateLength) -> bool:
    """
    Verify the checksum is valid for a given state.
    EXACT translation from IRremoteESP8266 IRNeoclimaAc::validChecksum
    """
    if length < 2:
        return True  # No checksum to compare with. Assume okay.
    return state[length - 1] == calcChecksum(state, length)


## Send a Neoclima message.
## Status: STABLE / Known to be working.
## EXACT translation from IRremoteESP8266 IRsend::sendNeoclima (ir_Neoclima.cpp lines 40-56)
def sendNeoclima(data: List[int], nbytes: int, repeat: int = 0) -> List[int]:
    """
    Send a Neoclima Heat Pump formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendNeoclima

    Returns timing array instead of transmitting via hardware.
    """
    # Import here to avoid circular import
    from app.core.ir_protocols.ir_send import sendGeneric

    all_timings = []

    for r in range(repeat + 1):
        # Main message
        msg_timings = sendGeneric(
            headermark=kNeoclimaHdrMark,
            headerspace=kNeoclimaHdrSpace,
            onemark=kNeoclimaBitMark,
            onespace=kNeoclimaOneSpace,
            zeromark=kNeoclimaBitMark,
            zerospace=kNeoclimaZeroSpace,
            footermark=kNeoclimaBitMark,
            dataptr=data,
            nbytes=nbytes,
            MSBfirst=False,
        )
        all_timings.extend(msg_timings)

        # Extra footer
        all_timings.append(kNeoclimaBitMark)
        all_timings.append(kNeoclimaMinGap)

    return all_timings


## Class for handling detailed Neoclima A/C messages.
## Direct translation from C++ IRNeoclimaAc class
class IRNeoclimaAc:
    ## Class Constructor
    def __init__(self) -> None:
        self._: NeoclimaProtocol = NeoclimaProtocol()
        self.stateReset()

    ## Reset the state of the remote to a known good state/sequence.
    ## Direct translation from ir_Neoclima.cpp lines 70-74
    def stateReset(self) -> None:
        kReset = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x6A, 0x00, 0x2A, 0xA5, 0x00]
        self.setRaw(kReset)

    ## Calculate & update the checksum for the internal state.
    ## Direct translation from ir_Neoclima.cpp lines 101-104
    def checksum(self, length: int = kNeoclimaStateLength) -> None:
        if length < 2:
            return
        self._.Sum = calcChecksum(self._.raw, length)

    ## Get a PTR to the internal state/code for this protocol.
    ## Direct translation from ir_Neoclima.cpp lines 116-119
    def getRaw(self) -> List[int]:
        self.checksum()
        return self._.raw

    ## Set the internal state from a valid code for this protocol.
    ## Direct translation from ir_Neoclima.cpp lines 124-126
    def setRaw(self, new_code: List[int], length: int = kNeoclimaStateLength) -> None:
        for i in range(min(len(new_code), length)):
            self._.raw[i] = new_code[i]

    ## Set the Button/Command pressed setting of the A/C.
    ## Direct translation from ir_Neoclima.cpp lines 130-155
    def setButton(self, button: int) -> None:
        if button in [
            kNeoclimaButtonPower,
            kNeoclimaButtonMode,
            kNeoclimaButtonTempUp,
            kNeoclimaButtonTempDown,
            kNeoclimaButtonSwing,
            kNeoclimaButtonFanSpeed,
            kNeoclimaButtonAirFlow,
            kNeoclimaButtonHold,
            kNeoclimaButtonSleep,
            kNeoclimaButtonLight,
            kNeoclimaButtonEye,
            kNeoclimaButtonFollow,
            kNeoclimaButtonIon,
            kNeoclimaButtonFresh,
            kNeoclimaButton8CHeat,
            kNeoclimaButtonTurbo,
            kNeoclimaButtonEcono,
            kNeoclimaButtonTempUnit,
        ]:
            self._.Button = button
        else:
            self._.Button = kNeoclimaButtonPower

    ## Get the Button/Command setting of the A/C.
    ## Direct translation from ir_Neoclima.cpp lines 159-161
    def getButton(self) -> int:
        return self._.Button

    ## Set the requested power state of the A/C to on.
    ## Direct translation from ir_Neoclima.cpp line 164
    def on(self) -> None:
        self.setPower(True)

    ## Set the requested power state of the A/C to off.
    ## Direct translation from ir_Neoclima.cpp line 167
    def off(self) -> None:
        self.setPower(False)

    ## Change the power setting.
    ## Direct translation from ir_Neoclima.cpp lines 171-174
    def setPower(self, on: bool) -> None:
        self._.Button = kNeoclimaButtonPower
        self._.Power = on

    ## Get the value of the current power setting.
    ## Direct translation from ir_Neoclima.cpp lines 178-180
    def getPower(self) -> bool:
        return bool(self._.Power)

    ## Set the operating mode of the A/C.
    ## Direct translation from ir_Neoclima.cpp lines 184-202
    def setMode(self, mode: int) -> None:
        if mode == kNeoclimaDry:
            # In this mode fan speed always LOW
            self.setFan(kNeoclimaFanLow)
            # FALL THRU
            self._.Mode = mode
            self._.Button = kNeoclimaButtonMode
        elif mode in [kNeoclimaAuto, kNeoclimaCool, kNeoclimaFan, kNeoclimaHeat]:
            self._.Mode = mode
            self._.Button = kNeoclimaButtonMode
        else:
            # If we get an unexpected mode, default to AUTO.
            self._.Mode = kNeoclimaAuto
            self._.Button = kNeoclimaButtonMode

    ## Get the operating mode setting of the A/C.
    ## Direct translation from ir_Neoclima.cpp lines 206-208
    def getMode(self) -> int:
        return self._.Mode

    ## Set the temperature.
    ## Direct translation from ir_Neoclima.cpp lines 239-250
    def setTemp(self, temp: int, celsius: bool = True) -> None:
        oldtemp = self.getTemp()
        self._.UseFah = not celsius
        min_temp = kNeoclimaMinTempC if celsius else kNeoclimaMinTempF
        max_temp = kNeoclimaMaxTempC if celsius else kNeoclimaMaxTempF
        newtemp = min(max_temp, max(min_temp, temp))
        if oldtemp > newtemp:
            self._.Button = kNeoclimaButtonTempDown
        elif newtemp > oldtemp:
            self._.Button = kNeoclimaButtonTempUp
        self._.Temp = newtemp - min_temp

    ## Get the current temperature setting.
    ## Direct translation from ir_Neoclima.cpp lines 255-259
    def getTemp(self) -> int:
        min_temp = kNeoclimaMinTempC if self.getTempUnits() else kNeoclimaMinTempF
        return self._.Temp + min_temp

    ## Set the speed of the fan.
    ## Direct translation from ir_Neoclima.cpp lines 263-280
    def setFan(self, speed: int) -> None:
        self._.Button = kNeoclimaButtonFanSpeed
        if self._.Mode == kNeoclimaDry:  # Dry mode only allows low speed.
            self._.Fan = kNeoclimaFanLow
            return
        if speed in [kNeoclimaFanAuto, kNeoclimaFanHigh, kNeoclimaFanMed, kNeoclimaFanLow]:
            self._.Fan = speed
        else:
            # If we get an unexpected speed, default to Auto.
            self._.Fan = kNeoclimaFanAuto

    ## Get the current fan speed setting.
    ## Direct translation from ir_Neoclima.cpp lines 284-286
    def getFan(self) -> int:
        return self._.Fan

    ## Set the Sleep setting of the A/C.
    ## Direct translation from ir_Neoclima.cpp lines 316-319
    def setSleep(self, on: bool) -> None:
        self._.Button = kNeoclimaButtonSleep
        self._.Sleep = on

    ## Get the Sleep setting of the A/C.
    ## Direct translation from ir_Neoclima.cpp lines 323-325
    def getSleep(self) -> bool:
        return bool(self._.Sleep)

    ## Set the vertical swing setting of the A/C.
    ## Direct translation from ir_Neoclima.cpp lines 329-332
    def setSwingV(self, on: bool) -> None:
        self._.Button = kNeoclimaButtonSwing
        self._.SwingV = kNeoclimaSwingVOn if on else kNeoclimaSwingVOff

    ## Get the vertical swing setting of the A/C.
    ## Direct translation from ir_Neoclima.cpp lines 336-338
    def getSwingV(self) -> bool:
        return self._.SwingV == kNeoclimaSwingVOn

    ## Set the horizontal swing setting of the A/C.
    ## Direct translation from ir_Neoclima.cpp lines 342-345
    def setSwingH(self, on: bool) -> None:
        self._.Button = kNeoclimaButtonAirFlow
        self._.SwingH = not on  # Cleared when `on`

    ## Get the horizontal swing (Air Flow) setting of the A/C.
    ## Direct translation from ir_Neoclima.cpp lines 349-351
    def getSwingH(self) -> bool:
        return not bool(self._.SwingH)

    ## Set the Turbo setting of the A/C.
    ## Direct translation from ir_Neoclima.cpp lines 355-358
    def setTurbo(self, on: bool) -> None:
        self._.Button = kNeoclimaButtonTurbo
        self._.Turbo = on

    ## Get the Turbo setting of the A/C.
    ## Direct translation from ir_Neoclima.cpp lines 362-364
    def getTurbo(self) -> bool:
        return bool(self._.Turbo)

    ## Set the Economy (Energy Saver) setting of the A/C.
    ## Direct translation from ir_Neoclima.cpp lines 368-371
    def setEcono(self, on: bool) -> None:
        self._.Button = kNeoclimaButtonEcono
        self._.Econo = on

    ## Get the Economy (Energy Saver) setting of the A/C.
    ## Direct translation from ir_Neoclima.cpp lines 375-377
    def getEcono(self) -> bool:
        return bool(self._.Econo)

    ## Set the Fresh (air) setting of the A/C.
    ## Direct translation from ir_Neoclima.cpp lines 381-384
    def setFresh(self, on: bool) -> None:
        self._.Button = kNeoclimaButtonFresh
        self._.Fresh = on

    ## Get the Fresh (air) setting of the A/C.
    ## Direct translation from ir_Neoclima.cpp lines 388-390
    def getFresh(self) -> bool:
        return bool(self._.Fresh)

    ## Set the Hold setting of the A/C.
    ## Direct translation from ir_Neoclima.cpp lines 394-397
    def setHold(self, on: bool) -> None:
        self._.Button = kNeoclimaButtonHold
        self._.Hold = on

    ## Get the Hold setting of the A/C.
    ## Direct translation from ir_Neoclima.cpp lines 401-403
    def getHold(self) -> bool:
        return bool(self._.Hold)

    ## Set the Ion (filter) setting of the A/C.
    ## Direct translation from ir_Neoclima.cpp lines 407-410
    def setIon(self, on: bool) -> None:
        self._.Button = kNeoclimaButtonIon
        self._.Ion = on

    ## Get the Ion (filter) setting of the A/C.
    ## Direct translation from ir_Neoclima.cpp lines 414-416
    def getIon(self) -> bool:
        return bool(self._.Ion)

    ## Set the Light(LED display) setting of the A/C.
    ## Direct translation from ir_Neoclima.cpp lines 420-423
    def setLight(self, on: bool) -> None:
        self._.Button = kNeoclimaButtonLight
        self._.Light = on

    ## Get the Light (LED display) setting of the A/C.
    ## Direct translation from ir_Neoclima.cpp lines 427-429
    def getLight(self) -> bool:
        return bool(self._.Light)

    ## Set the 8°C Heat setting of the A/C.
    ## Direct translation from ir_Neoclima.cpp lines 437-440
    def set8CHeat(self, on: bool) -> None:
        self._.Button = kNeoclimaButton8CHeat
        self._.CHeat = on

    ## Get the 8°C Heat setting of the A/C.
    ## Direct translation from ir_Neoclima.cpp lines 444-446
    def get8CHeat(self) -> bool:
        return bool(self._.CHeat)

    ## Set the Eye (Sensor) setting of the A/C.
    ## Direct translation from ir_Neoclima.cpp lines 450-453
    def setEye(self, on: bool) -> None:
        self._.Button = kNeoclimaButtonEye
        self._.Eye = on

    ## Get the Eye (Sensor) setting of the A/C.
    ## Direct translation from ir_Neoclima.cpp lines 457-459
    def getEye(self) -> bool:
        return bool(self._.Eye)

    ## Is the A/C unit using Fahrenheit or Celsius for temperature units.
    ## Direct translation from ir_Neoclima.cpp lines 463-465
    def getTempUnits(self) -> bool:
        return not bool(self._.UseFah)

    ## Get the Follow Me setting of the A/C.
    ## Direct translation from ir_Neoclima.cpp lines 480-482
    def getFollow(self) -> bool:
        return (self._.Follow & kNeoclimaFollowMe) == kNeoclimaFollowMe


## Decode the supplied Neoclima message.
## Status: STABLE / Known working
## EXACT translation from IRremoteESP8266 IRrecv::decodeNeoclima (ir_Neoclima.cpp lines 571-607)
def decodeNeoclima(
    results, offset: int = 1, nbits: int = kNeoclimaBits, strict: bool = True
) -> bool:
    """
    Decode a Neoclima HVAC IR message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeNeoclima

    This is the ACTUAL C++ decoder function, not a wrapper.
    """
    # Import here to avoid circular imports
    from app.core.ir_protocols.ir_recv import kHeader, kFooter, _matchGeneric

    # Compliance
    if strict and nbits != kNeoclimaBits:
        return False  # Incorrect nr. of bits per spec.

    # Match Main Header + Data + Footer
    used = _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state,
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=nbits,
        hdrmark=kNeoclimaHdrMark,
        hdrspace=kNeoclimaHdrSpace,
        onemark=kNeoclimaBitMark,
        onespace=kNeoclimaOneSpace,
        zeromark=kNeoclimaBitMark,
        zerospace=kNeoclimaZeroSpace,
        footermark=kNeoclimaBitMark,
        footerspace=kNeoclimaHdrSpace,
        atleast=False,
        tolerance=25,
        excess=0,
        MSBfirst=False,
    )
    if not used:
        return False
    offset += used

    # Extra footer
    from app.core.ir_protocols.ir_recv import matchGeneric

    if not matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=None,
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=0,
        hdrmark=0,
        hdrspace=0,
        onemark=0,
        onespace=0,
        zeromark=0,
        zerospace=0,
        footermark=kNeoclimaBitMark,
        footerspace=kNeoclimaHdrSpace,
        atleast=True,
        tolerance=25,
        excess=0,
        MSBfirst=False,
    ):
        return False

    # Compliance
    if strict:
        # Check we got a valid checksum.
        if not validChecksum(results.state, nbits // 8):
            return False

    # Success
    results.bits = nbits
    # No need to record the state as we stored it as we decoded it.
    # As we use result->state, we don't record value, address, or command as it
    # is a union data type.
    return True
